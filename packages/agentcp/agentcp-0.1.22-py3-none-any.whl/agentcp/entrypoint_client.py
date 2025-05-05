# Removed unused import
from agentcp.log import log_debug, log_error, log_exception, log_info, logger
from agentcp.client import IClient
from agentcp.auth_client import AuthClient

class EntrypointClient(IClient):

    def __init__(self, agent_id: str, server_url: str,app_path: str):
        self.agent_id = agent_id
        self.heartbeat_server = ""
        self.message_server = ""
        self.server_url = f"{server_url}"+"/api/entrypoint"
        self.app_path = app_path
        self.auth_client = AuthClient(agent_id, self.server_url,self.app_path)  # 使用AuthClient

    def initialize(self):
        self.auth_client.sign_in()
        self.get_entrypoint_config()
        
    def sign_in(self)->bool:
        return self.auth_client.sign_in() is not None 

    def sign_out(self):
        """登出方法""" 
        self.auth_client.sign_out()

    def post_public_data(self,json_path):
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            url = self.server_url + "/post_agent_public_data"
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
                "data": json.dumps(json_data),
            }
            response = self.post_request(url,json=data)
            if response.status_code == 200:
                logger.debug(f"post_public_data ok:{response.json()}")
                return True
            else:
                logger.error(f"post_public_data failed:{response.json()}")
                return False
        except Exception as e:
            logger.exception(f"Post public data exception occurred: {e}")
            return False

    def post_private_data(self, data):
        try:
            ep_url = self.server_url + "/post_agent_private_data"
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
                "data": data,
            }
            response = self.post_request(ep_url,json=data)
            if response.status_code == 200:
                logger.debug(f"post_private_data ok:{response.json()}")
                return response.json()["data"]
            else:
                logger.error(f"post_private_data failed:{response.json()}")
                return None
        except Exception as e:
            logger.exception(f"Post private data exception occurred: {e}")
            return None

    def get_all_public_data(self,is_retry:bool=True):
        try:
            ep_url = self.server_url + "/get_all_public_data"
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
            }
            response = self.post_request(ep_url,json=data)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                log_error(f"get_all_public_data failed:{response.json()}")
                return []
        except Exception as e:
            log_error(f"get_all_public_data exception:")
            log_exception(e)
            return []

    def get_agent_list(self):
        try:
            ep_url = self.server_url + "/get_agent_list"
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
            }
            response = self.post_request(ep_url,json=data)
            if response.status_code == 200:
                log_info(f"get_all_public_data ok:{response.json()}")
                return response.json()["data"]
            else:
                log_error(f"get_all_public_data failed:{response.json()}")
                return None
        except Exception as e:
            log_exception(f"Get all public data exception occurred: {e}")

    def get_entrypoint_config(self):
        try:
            ep_url = self.server_url + "/get_entrypoint_config"
            log_debug(f"Get server config: {ep_url}")
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
            }
            response = self.post_request(ep_url,json=data)
            if response.status_code == 200:
                try:
                    config = response.json()
                    if isinstance(config.get('config'), str):  # 处理config是字符串的情况
                        import json
                        config['config'] = json.loads(config['config'])
                    if 'config' in config:
                        if 'heartbeat_server' in config['config']:
                            self.heartbeat_server = config['config']['heartbeat_server']
                            log_debug(f"Set heartbeat server to: {self.heartbeat_server}")
                        if 'message_server' in config['config']:
                            self.message_server = config['config']['message_server']
                            log_debug(f"Set message server to: {self.message_server}")

                except (ValueError, AttributeError) as e:
                    log_exception(
                        f"Failed to parse JSON. Response content: {response.text[:500]}. Error: {e}"
                    )
            else:
                log_error(f"Get entrypoint config {ep_url} failed:{response.json()}")

        except Exception as e:
            logger.exception(f"Get entrypoint config exception occurred: {e}")

    def get_agent_public_data(self):
        try:
            ep_url = self.server_url + "/get_agent_public_data"
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
            }
            response = self.post_request(ep_url,json=data)
            if response.status_code == 200:
                log_debug(f"get_agent_public_data ok:{response.json()}")
                return response.json()["data"]  # Return the data if it exists, else return None or handle it as you like
            else:
                log_error(f"get_agent_public_data failed:{response.json()}")
                return None
        except Exception as e:
            log_exception(f"Get agent public data exception occurred: {e}")
            return None

    def get_agent_private_data(self):
        try:
            ep_url = self.server_url + "/get_agent_private_data"
            data = {
                "agent_id": f"{self.agent_id}",
                "signature": self.auth_client.signature,
            }
            response = self.post_request(ep_url,json=data)
            if response.status_code == 200:
                log_debug(f"Get_agent_private_data ok:{response.json()}")
                return response.json()["data"]
            else:
                log_error(f"Get_agent_private_data failed:{response.json()}")
                return None
        except Exception as e:
            log_exception(f"Get agent private data exception occurred: {e}")
            return None

    def get_heartbeat_server(self):
        return self.heartbeat_server

    def get_message_server(self):
        return self.message_server
