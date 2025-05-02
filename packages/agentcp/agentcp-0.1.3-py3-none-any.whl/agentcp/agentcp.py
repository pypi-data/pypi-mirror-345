import abc
from contextlib import AbstractAsyncContextManager, asynccontextmanager
import json
import asyncio

from dataclasses import dataclass
import time
from typing import Any, AsyncIterator, Callable, Literal, Optional, Union, Dict, List
import typing
import signal
import threading
import requests

from agentcp.log import logger
from agentcp.entrypoint_client import EntrypointClient
from agentcp.heartbeat_client import HeartbeatClient
from agentcp.db.db_mananger import DBManager
from agentcp.message import AssistantMessageBlock
from agentcp.group_manager import GroupManager, Group
from agentcp.ca_client import CAClient
import os


class _AgentCP(abc.ABC):
    """
    AgentCP类的抽象基类
    """
    def __init__(self):
        self.shutdown_flag = threading.Event()  # 初始化信号量
        self.exit_hook_func = None
        
    def register_signal_handler(self, exit_hook_func=None):
        """
        注册信号处理函数
        
        """
        signal.signal(signal.SIGTERM, self.signal_handle)
        signal.signal(signal.SIGINT, self.signal_handle)
        self.exit_hook_func = exit_hook_func
        
    def serve_forever(self):
        """ """
        logger.info(f"agentid client[{self.id}] serve forever")
        while not self.shutdown_flag.is_set():
            time.sleep(1)

    def signal_handle(self, signum, frame):
        """
        信号处理函数
        :param signum: 信号编号
        :param frame: 当前栈帧
        """
        logger.info(f"recvied signal: {signum}, program exiting...")
        logger.info(f"agentid client[{self.id}] exited")
        self.shutdown_flag.set()  # 设置关闭标志
        if self.exit_hook_func:
            self.exit_hook_func(signum, frame)

class AgentCP(_AgentCP):
    
    
    def __init__(self, folder = "agentcp"):
        super().__init__()       
        import os
        self.app_path = os.path.join(os.getenv('APPDATA'), folder)
        print("应用访问路径", self.app_path)  # 输出路径
        self.id = None
        self.name = ""
        self.avaUrl = ""
        self.description = ""
        self.ca_client = None
        self.ep_url = None
        self.message_handlers = []  # 添加消息监听器属性
        self.message_handlers_map = {}  # 添加消息监听器属性
        self.heartbeat_client = None
        self.db_manager = DBManager(db_path = self.app_path)
        
    def get_app_path(self):
        return self.app_path

    def online(self):
        logger.debug("initialzing entrypoint server")
        self.entry_client = EntrypointClient(self.id, self.ep_url,self.app_path)
        self.entry_client.initialize()

        logger.debug("initialzing heartbeat server")
        self.heartbeat_client = HeartbeatClient(
            self.id, self.entry_client.get_heartbeat_server(),self.app_path
        )
        self.heartbeat_client.initialize()

        self.group_manager = GroupManager(
            self.id, self.entry_client.get_message_server()
        )
        self.db_manager.set_aid(self.id)
        self.connect()

    def set_avaUrl(self,avaUrl):
        self.avaUrl = avaUrl
        return self

    def set_name(self,name):
        self.name = name
        return self

    def set_description(self,description):
        self.description = description
        return self

    def get_agentid_info(self):
        return {
            'aid':self.id,
            'name':self.name,
            'description':self.description,
            'avaUrl':self.avaUrl,
            'ep_aid':self.ep_aid,
            'ep_url':self.ep_url,
        }

    def get_message_list(self,session_id,page=1, page_size=10):
        return self.db_manager.get_message_list(self.id,session_id,page,page_size)

    def add_message_handler(
        self, handler: typing.Callable[[dict], typing.Awaitable[None]],session_id:str=""
    ):
        """消息监听器装饰器"""
        logger.debug("add message handler")
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("监听器必须是异步函数(async def)")
        if session_id == "":
            self.message_handlers.append(handler)
        else:
            self.message_handlers_map[session_id] = handler
    def remove_message_handler(self, handler: typing.Callable[[dict], typing.Awaitable[None]],session_id:str=""):
        """移除消息监听器"""
        if session_id == "":
            if handler in self.message_handlers:
                self.message_handlers.remove(handler)
        else:
            self.message_handlers_map.pop(session_id, None)
        print(len(self.message_handlers_map))

    def create_chat_group(self, name, subject, *, type='public'):
        """创建与多个agent的会话
        :param name: 群组名称
        :param subject: 群组主题
        :param to_aid_list: 目标agent ID列表
        :return: 会话ID或None
        """
        logger.debug(f"create group: {name}, subject: {subject}, type: {type}")
        group = self.group_manager.create_group(name, subject, type)
        group.set_on_message_receive(self.__agentid_message_listener)
        group.set_on_invite_ack(self.__on_invite_ack)
        group.set_on_member_list_receive(self.__on_member_list_receive)
        self.__insert_group_chat(self.id, group.session_id, group.identifying_code, name)
        return group.session_id

    def invite_member(self, session_id, to_aid):
        to_aid = self.__build_id(to_aid)
        if self.group_manager.invite_member(session_id, to_aid):
            self.db_manager.invite_member(self.id, session_id, to_aid)
        else:
            logger.error(f"failed to invite: {to_aid} -> {session_id}")

    def get_online_status(self,aids):
        return self.heartbeat_client.get_online_status(aids)

    def get_conversation_list(self,aid,main_aid,page,page_size):
        return self.db_manager.get_conversation_list(aid,main_aid,page,page_size)
    
    async def create_stream(self,session_id,receiver, content_type: str = "text/event-stream", ref_msg_id : str = ""):
        return await self.group_manager.create_stream(session_id,receiver, content_type, ref_msg_id)
        
    def close_stream(self,session_id, stream_url):
        self.group_manager.close_stream(session_id, stream_url)
    
    def send_chunk_to_stream(self,session_id, stream_url, chunk):
        self.group_manager.send_chunk_to_stream(session_id, stream_url, chunk)
        

    def send_message(self, to_aid_list: list, sessionId: str, message: Union[AssistantMessageBlock, list[AssistantMessageBlock], dict],ref_msg_id: str="",message_id:str=""):
        # 处理对象转换为字典
        if isinstance(message, (AssistantMessageBlock, dict)):
            message_data = message.__dict__ if hasattr(message, '__dict__') else message
        elif isinstance(message, list):
            message_data = [msg.__dict__ if hasattr(msg, '__dict__') else msg for msg in message]
        if message_id == "" or message_id is None:
            message_id = str(int(time.time() * 1000))
            
        self.db_manager.insert_message(
            "user",
            self.id,
            sessionId,
            self.id,
            "",
            ",".join(to_aid_list),
            json.dumps(message_data),
            "text",
            "sent",
            message_id
        )
        self.group_manager.send_msg(sessionId ,json.dumps(message_data), ";".join(to_aid_list), ref_msg_id,message_id)

    def post_public_data(self,json_path):
        """
        发送数据到接入点服务器
        :param json_path: JSON文件路径
        :return: 响应内容或None
        """
        self.entry_client.post_public_data(json_path)

    def add_friend_agent(self,aid,name,description,avaUrl):
        self.db_manager.add_friend_agent(self.id,aid,name,description,avaUrl)

    def get_friend_agent_list(self):
        return self.db_manager.get_friend_agent_list(self.id)

    def __on_heartbeat_invite_message(self, invite_req):
        group: Group = self.group_manager.join_group(invite_req)
        group.set_on_message_receive(self.__agentid_message_listener)

    def run_message_listeners(self, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            session_id = data["session_id"]
            if session_id in self.message_handlers_map:
                tasks = [self._safe_call(self.message_handlers_map[session_id], data)]
                loop.run_until_complete(asyncio.gather(*tasks))
            else:
                tasks = [self._safe_call(func, data) for func in self.message_handlers]
                loop.run_until_complete(asyncio.gather(*tasks))
        finally:
            loop.close()

    async def _safe_call(self, func, data):
        try:
            await func(data)
        except Exception as e:
            logger.exception(f"message_listener_func: 异步消息处理异常: {e}")
    
    def __on_member_list_receive(self,data):
        print("__on_member_list_receive",data)

    def __fetch_stream_data(self, pull_url,save_message_list,data,message_list):
        """通过 HTTPS 请求拉取流式数据"""
        try:
            session_id = data["session_id"]
            message_id = data["message_id"]
            ref_msg_id = data["ref_msg_id"]
            sender = data["sender"]
            receiver = data["receiver"]
            message = message_list[0]
            message["type"] = "content"
            message["extra"] = pull_url
            message["content"] = ""
            if save_message_list is None or len(save_message_list) == 0:
                self.db_manager.insert_message("assistant",self.id,session_id,sender, ref_msg_id, receiver, json.dumps(message_list), "text", "success",message_id)
            save_message_list = self.db_manager.get_message_by_id(self.id,session_id,message_id)
            if save_message_list is None or len(save_message_list) == 0:
                logger.error(f"插入消息失败: {pull_url}")
                return
            print(save_message_list[0])
            msg_block = json.loads(save_message_list[0]["content"])[0]
            pull_url = pull_url+"&agent_id="+self.id
            logger.info("开始拉取流式数据...1："+pull_url)
            pull_url = pull_url.replace("https://agentunion.cn","https://ts.agentunion.cn")
            try:
                response = requests.get(pull_url, stream=True, verify=False, timeout=(5, 30))  # 连接超时5秒，读取超时30秒
                logger.info("开始拉取流式数据...2："+pull_url)
                response.raise_for_status()  # 检查HTTP状态码
                content_text = ""
                for line in response.iter_lines():
                    if line is None:
                        continue
                    decoded_line = line.decode('utf-8')
                    print(f"Received: {decoded_line}")
                    if not decoded_line.startswith("data:") and not decoded_line.startswith("event:"):
                        print("接收到的消息不是有效的 SSE 格式")
                        print(decoded_line)
                        continue
                    key, value = decoded_line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == 'event' and value == "done":
                        print("接收到的消息仅为 'done'")
                        msg_block["status"] = "success"
                    else:
                        content_text = content_text+value
                        msg_block["content"] = content_text
                        # save_message_list[0]["content"] = message
                    message_list = []
                    message_list.append(msg_block)
                    save_message_list[0]["content"] = json.dumps(message_list)
                    self.db_manager.update_message(self.id,save_message_list[0])
                print(content_text)
                logger.info("结束拉取流式数据...3："+pull_url)
            except requests.exceptions.Timeout:
                logger.error(f"请求超时: {pull_url}")
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败: {pull_url}, 错误: {str(e)}")
        except Exception as e:
            import traceback
            print(f"拉取流式数据时发生错误: {str(e)}\n{traceback.format_exc()}")

    def __on_invite_ack(self,data):
        status = int(data["status_code"])
        session_id = data["session_id"]
        message = data["message"]
        acceptor_id = data["acceptor_id"]
        if status == 404:
            message_list = []
            msg_block = {
                "type":"error",
                "status":"success",
                "timestamp":int(time.time() * 1000),  # 使用毫秒时间戳
                "content":"该Agent不在线",
                "extra":""
            }
            message_list.append(msg_block)
            message_id = self.db_manager.insert_message("assistant",self.id,session_id,acceptor_id, "", self.id, json.dumps(message_list), "text", "success","")
            message_data = {
                "session_id":session_id,
                "message_id":message_id,
                "ref_msg_id":"",
                "sender":acceptor_id,
                "receiver":self.id,
                "message":json.dumps(message_list)
            }
            thread = threading.Thread(target=self.run_message_listeners, args=(message_data,))
            thread.start()

    def __agentid_message_listener(self, data):
        logger.debug(f"received a message: {data}")
        session_id = data["session_id"]
        message_id = data["message_id"]
        ref_msg_id = data["ref_msg_id"]
        sender = data["sender"]
        receiver = data["receiver"]
        message = json.loads(data["message"])
        message_list = []  # 修改变量名避免与内置list冲突
        message_temp = None
        if isinstance(message, list):
            message_list = message
            message_temp = message_list[0] if isinstance(message_list[0], dict) else json.loads(message_list[0])
        else:
            message_list.append(message)
            message_temp = message
            #self.__insert_group_chat(self.id,session_id,"","")
        save_message_list = self.db_manager.get_message_by_id(self.id,session_id,message_id)
        if "text/event-stream" == message_temp.get("type", ""):
            pull_url = message_temp.get("content","")
            print("pull_url:"+pull_url)
            if pull_url == "":
                return            
            threading.Thread(target=self.__fetch_stream_data, args=(pull_url,save_message_list,data,message_list,)).start()
            return
        
        if save_message_list is None or len(save_message_list) == 0:
            self.db_manager.insert_message("assistant",self.id,session_id,sender, ref_msg_id, receiver, json.dumps(message_list), "text", "success",message_id)
        else:
            save_message = save_message_list[0]
            content = save_message["content"]
            if isinstance(content, list):
                #self.__insert_group_chat(self.id,session_id,"","")
                content.append(message_list)
            elif isinstance(content, str):
                content_list = json.loads(content)
                content_list.append(message_list)                
            save_message["content"] = json.dumps(content_list)
            self.db_manager.update_message(self.id,save_message)
            
        thread = threading.Thread(target=self.run_message_listeners, args=(data,))
        thread.start()

    def __insert_group_chat(self,aid,session_id,identifying_code,name):
        conversation =  self.db_manager.get_conversation_by_id(aid,session_id)
        if conversation is None:
            # identifying_code,name, type,to_aid_list
            self.db_manager.create_conversation(aid,session_id,identifying_code,name,"public",[])
        return

    def can_invite_member(self,session_id):
        group = self.group_manager.get(session_id)
        if group:
            return group.can_invite_member(session_id)
        else:
            chat = self.db_manager.get_conversation_by_id(self.id,session_id)
            if chat.identifying_code == "" or chat.identifying_code == None:
                return False
            else:
                return True

    def connect(self):
        if not hasattr(self, '_heartbeat_thread') or not self._heartbeat_thread.is_alive():
            self._heartbeat_thread = threading.Thread(target=self.heartbeat_client.online)
            self._heartbeat_thread.start()
        self.heartbeat_client.set_on_recv_invite(self.__on_heartbeat_invite_message)
        logger.info(f'agentid {self.id} is ready!')

    def offline(self):
        """离线状态"""
        if self.heartbeat_client:
            self.heartbeat_client.offline()
            self.heartbeat_client.sign_out()
        if self.entry_client:
            self.entry_client.sign_out()

    def get_agent_list(self):
        """获取所有agentid列表"""
        return self.entry_client.get_agent_list()

    def get_all_public_data(self):
        """获取所有agentid列表"""
        return self.entry_client.get_all_public_data()

    def get_session_member_list(self,session_id):
        return self.db_manager.get_session_member_list(self.id,session_id)

    def __build_id(self, id):
        ep = self.ep_url.split('.')
        end_str = f'{ep[-2]}.{ep[-1]}'
        if id.endswith(end_str):
            return id

        return f'{id}.{ep[-2]}.{ep[-1]}'
    
    def __build_url(self, aid):
        aid_array = aid.split('.')
        if len(aid_array) < 3:
            raise RuntimeError("加载aid错误,请检查传入aid")
        end_str = f'{aid_array[-2]}.{aid_array[-1]}'
        self.ca_client = CAClient("https://ca."+end_str,self.app_path)
        self.ep_url = "https://ep."+end_str

    def load_aid(self, agent_id: str) -> bool:
        self.id = agent_id
        self.__build_url(agent_id)
        try:
            logger.debug(f"load agentid: {self.id}")  # 调试用
            result = self.db_manager.load_aid(self.id)
            if result[0] is None:  # 检查返回结果是否有效
                logger.error(f"未找到agent_id: {self.id} 或数据不完整: {result}")
                return

            ep_aid, ep_url = result[0], result[1]  # 安全获取前两个值
            avaUrl = result[2] if len(result) > 2 else ""
            name = result[3] if len(result) > 3 else ""
            description = result[4] if len(result) > 4 else ""

            if ep_aid and ep_url:
                return self

            ep_url = self.ca_client.resign_csr(self.id)
            logger.debug(f"resign: {ep_url}")  # 调试用
            if ep_url:
                self.db_manager.update_aid(self.id, "ep_aid", ep_url)
                self.set_avaUrl(avaUrl)
                self.set_name(name)
                self.set_description(description)
                return self

        except Exception as e:
            logger.exception(f"加载和验证密钥对时出错: {e}")  # 调试用
            return False

    def create_aid(self, ep_url: str,agent_id: str):
        self.ca_client = CAClient("https://ca."+ep_url,self.app_path)
        self.ep_url = "https://ep."+ep_url
        self.id = self.__build_id(agent_id)
        
        # 确保证书目录存在
        cert_dir = os.path.join(self.app_path, 'aid', self.id)
        os.makedirs(cert_dir, exist_ok=True)
        
        logger.debug(f"create agentid: {self.id}")
        result = self.ca_client.send_csr_to_server(self.id)
        if result == True:
            self.db_manager.create_aid(self.id)
            return self.id
        raise RuntimeError(result)

    def get_agentid_list(self):
        list = self.db_manager.get_agentid_list()
        return list

    def get_agentid(self, id):
        id = self.__build_id(id)
        agents = [_id for _id in self.db_manager.get_agentid_list() if _id == id]
        return agents[0] if agents else None

    def update_aid_info(self, aid, avaUrl, name, description):
        self.db_manager.update_aid_info(aid, avaUrl, name, description)
        return True

    def message_handler(self, name: str|None = None):
        def wrapper(fn):
            # 动态获取 client 属性名
            self.add_message_handler(fn)
            return fn
        return wrapper

    def __repr__(self):
        return f"AgentId(aid={self.id})"
    
    def get_sender_from_message(self, message):
        if isinstance(message, dict):
            return message.get("sender")
        return None  # 如果不是字典，返回None或抛出异常，取决于你的需求

    def get_receiver_from_message(self, message):
        if isinstance(message, dict):
            return message.get("receiver")
        return None  # 如果不是字典，返回None或抛出异常，取决于你的需求
    
    
    # 尝试解析 content 为 JSON 格式 
    def get_content_array_from_message(self, message):
        #消息数组
        message_content = message.get("message","")
        message_array = []
        if isinstance(message_content, str):
            try:
                if message_content.strip():  # 检查内容是否非空
                    llm_content_json_array = json.loads(message_content)
                    if isinstance(llm_content_json_array, list) and len(llm_content_json_array) > 0:
                        return llm_content_json_array  # 返回整个数组而不是第一个元素的 conten
                    else:
                        message_array.append(llm_content_json_array)
                        return message_array
                else:
                    print("收到空消息内容")
                    return []
            except json.JSONDecodeError:
                print(f"无法解析的消息内容: {message_content}")
                return []
        elif isinstance(message_content, list) and len(message_content) > 0:
            return message_content
        else:
            print("无效的消息格式")
            return []
                
        message_array.append(llm_content_json)
        return message_array
