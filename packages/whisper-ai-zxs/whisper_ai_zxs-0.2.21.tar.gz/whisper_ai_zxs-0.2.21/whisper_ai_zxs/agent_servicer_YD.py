from .agent_servicer import AgentServicer
import logging
logger = logging.getLogger("whisper_ai")

class Agent_YD(AgentServicer):
    def call(self, name, *args, **kwargs):
        """
        调用注册的函数
        :param name: 需要调用的函数名称
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 返回调用结果
        """
        if name not in self._functions:
            #raise KeyError(f"RPA流程 '{name}' 未注册")
            return "未注册"

        # 将 args 转换为字典
        arg_dict = {str(i): v for i, v in enumerate(args)}
        arg_dict.update(kwargs)  # 合并 kwargs
        p_arg = {
            "arg" : arg_dict,
            "result" : ""
        }
        self._functions[name].main(p_arg)
        #result = json.dumps(p_arg["result"])
        return p_arg["result"]
        #return self._functions[name](*args, **kwargs)
        #return run_module({ "module_path": self._functions[name] }, "main", SZEnv['rpa'], *args, **kwargs) 


"""
    def register_all_function(self):
        from .import process1
        from .import process2
        from .import process3
        from .import process4
        from .import process5
        from .import process6
        from .import process8
        from .import process9
        from .import process12
        from .import process13
        from .import process14
        from .import process15
        from .import process16
        from .import process17
        from .import process18
        from .import process19
        from .import process20
        from .import process21
        from .import process22
        from .import process23
        from .import process25
        from .import process26
        from .import process28
        from .import process30

        self.register("activate", process28)
        self.register("collect_info", process30)
        self.register("start", process1)
        # self.register("start", process25)  #多开版
        self.register("stop", process2)
        # self.register("stop", process26)   #多开版
        self.register("reply", process3)
        self.register("get_customers_waiting", process4)
        self.register("get_new_chats", process5)
        self.register("close_chat", process6)
        self.register("transfer_to_customer_care", process8)
        self.register("get_recently_order", process9)
        self.register("specify_logistic", process12)
        self.register("recommend_product", process13)
        self.register("modify_notes", process16)
        self.register("modify_address", process22)
        self.register("contact_old_user", process23)

                
        #self.register("report_logistic_error", process14)
        #self.register("report_delivery_error", process15)
        #self.register("report_modify_address_sended", process18)
        #self.register("report_product_error", process19)
        #self.register("goto_rest", process20)
        #self.register("get_production_date", process17)
        #self.register("get_selling_product", process21)
        pass



"""