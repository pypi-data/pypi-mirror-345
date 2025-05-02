import abc
import requests


class IClient(abc.ABC):
    @abc.abstractmethod
    def sign_in(self) -> bool:
        pass
    
    @abc.abstractmethod
    def sign_out(self):
        pass


    def get_request(self,url: str, params: dict = None, headers: dict = None,is_retry=True) -> requests.Response:
        """
        发送GET请求的通用方法   
        Args:
            url (str): 请求的URL
            params (dict, optional): 请求参数. Defaults to None.
            headers (dict, optional): 请求头. Defaults to None. 
        Returns:
            requests.Response: 响应对象
        """
        try:
            response = requests.get(url, params=params, headers=headers,verify=False)
            response.raise_for_status()
            if response.status_code == 200:
                return response
            else:
                print(f"请求失败，状态码: {response.status_code}")
                error = response.json().get("error", "")
                if "please sign in first." in error and is_retry:
                    print("尝试重新登录...")
                    if self.sign_in():
                        return self.get_request(url, params=params, headers=headers, is_retry=False)
                return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            raise


    def post_request(self, url: str, data: dict = None, json: dict = None, headers: dict = None, is_retry=True) -> requests.Response:
        """
        发送POST请求的通用方法
    
        Args:
            url (str): 请求的URL
            data (dict, optional): 表单数据. Defaults to None.
            json (dict, optional): JSON数据. Defaults to None.
            headers (dict, optional): 请求头. Defaults to None.
            is_retry (bool, optional): 是否重试. Defaults to True.
    
        Returns:
            requests.Response: 响应对象
        """
        try:
            response = requests.post(url, data=data, json=json, headers=headers, verify=False)
            response.raise_for_status()
            if response.status_code == 200:
                print("请求成功")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                error = response.json().get("error", "")
                if "please sign in first." in error and is_retry:
                    print("尝试重新登录...")
                    if self.sign_in():
                        return self.post_request(url, data=data, json=json, headers=headers, is_retry=False)
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            raise
    
    
