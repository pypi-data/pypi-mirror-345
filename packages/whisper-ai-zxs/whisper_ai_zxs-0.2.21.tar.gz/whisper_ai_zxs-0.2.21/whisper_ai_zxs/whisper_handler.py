from typing_extensions import override
import os
from openai import AzureOpenAI
from openai import AssistantEventHandler
from .whisper_db import WhisperDB
from .whisper_function import AIFunctionRegistry
from .whisper_tools import WhisperTools_ChatRecord, WhisperTools_Qywx
from datetime import datetime, timezone

import logging
logger = logging.getLogger("whisper_ai")

import json
import re
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.


# 设置OpenAI客户端
client = AzureOpenAI(
  api_key=os.environ["AZURE_OPENAI_API_KEY"],
  azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
  api_version="2024-05-01-preview",
)

class EventHandler(AssistantEventHandler):
  shared_fail_times = 0  # 类变量，在所有实例间共享

  def __init__(self, reg):
    super().__init__()  # 调用父类的 __init__ 方法
    self._registry = reg

  def set_userName(self, userName):
    self.userName = userName
  def set_transferFlag(self, flag):
    self.transferFlag = flag
  def set_transferReason(self, reason):
    self.transferReason = reason

  @override
  def on_text_created(self, text) -> None:
    #print(f"\nassistant > {text}", end="", flush=True)
    self.replyText = ""
      
  @override
  def on_text_delta(self, delta, snapshot):
    #print(delta.value, end="", flush=True)
    logger.info("信息输出：" + delta.value)
    self.replyText = self.replyText + delta.value

  @override
  def on_text_done(self, text):
    #print(f"\nassistant > {text}", end="", flush=True)
    
    # Using regular expressions to identify the URL and its text
    pattern = r"【\d+:\d+†([^【】]+)】"
    msgContent = re.sub(pattern, '', self.replyText)

    WhisperTools_ChatRecord.record_chatGPT_action(self._registry.get_kf_name(), self.userName, "reply", self.replyText)
    self._registry.call("reply", self.userName, msgContent)
      
  @override
  def on_event(self, event):
    #print("recieved a event.")
    #print(event.event)
    # Retrieve events that are denoted with 'requires_action'
    # since these will have our tool_calls
    if event.event == 'thread.run.requires_action':
      run_id = event.data.id  # Retrieve the run ID from the event data
      self.handle_requires_action(event.data, run_id)
    elif event.event == 'thread.run.failed':
      logger.warning(f"thread.run.failed.{event}")

      EventHandler.shared_fail_times = EventHandler.shared_fail_times + 1
      if EventHandler.shared_fail_times < 2 :
        logger.warning("重新尝试！")
        pro_event_handler = EventHandler(self._registry)
        pro_event_handler.set_userName(self.userName)
        pro_event_handler.set_transferFlag(False)
        pro_event_handler.set_transferReason("")
        
        with client.beta.threads.runs.stream(
            thread_id=self.current_run.thread_id,
            assistant_id=self.current_run.assistant_id,
            event_handler=pro_event_handler,
        ) as stream:
            stream.until_done()
            pro_event_handler.proEnd()

      else:
        logger.warning("thread.run.failed 三次后，删除用户threadID，并转接给人工客服。")
        myDB = WhisperDB()
        query = f"DELETE FROM `openai_user_list` WHERE `ThreadID`= '{self.current_run.thread_id}'"
        myDB.query(query)
        myDB.commit()
        myDB.close()

        self._registry.call("reply", self.userName, "抱歉，我这边有点问题，我暂时给您转其他人处理了。")
        pro_result = self._registry.call("transfer_to_customer_care", self.userName, self._registry.get_human_kf_name(), "服务器异常")
        if (pro_result != "success"):
          self._registry.call("reply", self.userName, pro_result)
        EventHandler.shared_fail_times = 0;

  def handle_requires_action(self, data, run_id):
    tool_outputs = []
      
    for tool in data.required_action.submit_tool_outputs.tool_calls:
      logger.info("收到openai调用："+tool.function.name)
      logger.info("收到openai调用（参数）："+tool.function.arguments)
      WhisperTools_ChatRecord.record_chatGPT_action(self._registry.get_kf_name(), self.userName, tool.function.name, json.dumps(tool.function.arguments))

      result = ""
      try:
        result = self.process_function(tool.function.name, tool.function.arguments)
      except Exception as e:
        logger.warning(f"函数处理错误！{e}，做第二次尝试！")
        try:
          result = self.process_function(tool.function.name, tool.function.arguments)
        except Exception as e:
          logger.error(f"第二次还是错误！{e}")
          logger.error(f"错误类型: {type(e).__name__}")
          logger.error(f"异常发生在: {e.__traceback__.tb_lineno} 行")
          WhisperTools_Qywx.send_to_error_robot(f"{self._registry.get_kf_name()}的{tool.function.name}函数处理出现问题。")
          result = f"函数处理错误！{e}"

      # 当前时间，带 UTC 时区
      now_utc = datetime.now(timezone.utc)

      # 返回给调用方的数据
      return_result = {
          "result": result,
          "timestamp": now_utc.isoformat(),  # 标准格式输出
          "ttl_seconds": 600  #有效时间10分钟
      }

      tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(return_result)})
      WhisperTools_ChatRecord.record_chatGPT_action(self._registry.get_kf_name(), self.userName, "return", json.dumps(result))
      
    # Submit all tool_outputs at the same time
    self.submit_tool_outputs(tool_outputs, run_id)

  def proEnd(self):
    if (self.transferFlag):
      WhisperTools_ChatRecord.record_chatGPT_action(self._registry.get_kf_name(), self.userName, "proEnd", json.dumps(self.transferReason))
      pro_result = self._registry.call("transfer_to_customer_care", self.userName, self._registry.get_human_kf_name(), self.transferReason)
      WhisperTools_ChatRecord.record_chatGPT_action(self._registry.get_kf_name(), self.userName, "return", json.dumps(pro_result))
      if (pro_result != "success"):
        WhisperTools_ChatRecord.record_chatGPT_action(self._registry.get_kf_name(), self.userName, "reply", pro_result)
        self._registry.call("reply", self.userName, pro_result)
        self._registry.report_transfer_fail(self.userName, self.transferReason)

  def submit_tool_outputs(self, tool_outputs, run_id):
    pro_event_handler = EventHandler(self._registry)
    pro_event_handler.set_userName(self.userName)
    pro_event_handler.set_transferFlag(self.transferFlag)
    pro_event_handler.set_transferReason(self.transferReason)
    # Use the submit_tool_outputs_stream helper
    with client.beta.threads.runs.submit_tool_outputs_stream(
      thread_id=self.current_run.thread_id,
      run_id=self.current_run.id,
      tool_outputs=tool_outputs,
      event_handler=pro_event_handler,
    ) as stream:
      for text in stream.text_deltas:
        print(text, end="", flush=True)
      print()
      self.set_transferFlag(pro_event_handler.transferFlag)
      self.set_transferReason(pro_event_handler.transferReason)

  def process_function(self, name, arguments):
    # 转移客服为特殊处理，需要全部对话完成后转移。
    if name == "transfer_to_customer_care":
      # 将 arguments 解析为字典
      arguments_dict = json.loads(arguments)
      self.set_transferFlag(True)
      self.set_transferReason(arguments_dict['reason'])
      result = "ok"
      return json.dumps(result)
    
    elif name == "multi_tool_use":
      logger.warning("还不支持multi_tool_use，请单独调用各个函数！")
      result = json.dumps("还不支持multi_tool_use，请单独调用各个函数！")
      return result      # 将 arguments 解析为字典
      arguments_dict = json.loads(arguments)
      tools = arguments_dict['tool_uses']
      tool_outputs = []
        
      for tool in tools:
        result = self.process_function(tool.recipient_name, json.dumps(tool.parameters))
        tool_outputs.append({"tool_call_id": tool.id, "output": result})
      
      result = json.dumps(tool_outputs)
      return result
    else:
      cls = AIFunctionRegistry.registry.get(name, None)
      if cls:
        instance = cls()
        return instance.call(self.userName, arguments, self._registry)
      else:
        WhisperTools_Qywx.send_to_error_robot(f"{self._registry.get_kf_name()}的{name}函数还未实现。")
        return json.dumps(f"'{name}'函数还未实现！")
