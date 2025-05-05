from typing import Union
import uuid
import requests
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from agentcp.log import log_info, logger
import os

class AuthClient:
    def __init__(self, agent_id: str, server_url: str,app_path: str):
        """认证客户端类
        Args:
            agent_id: 代理ID
            server_url: 服务器URL
        """
        self.agent_id = agent_id
        self.server_url = server_url
        self.signature = None
        self.aid_path = os.path.join(app_path, 'aid')

    def sign_in(self) -> Union[dict, None]:
        """登录方法"""
        try:
            hb_url = self.server_url + "/sign_in"
            log_info(f"Sign in: {hb_url}")
            request_id = uuid.uuid4().hex
            data = {
                "agent_id": self.agent_id,
                "request_id": request_id,
            }
            
            response = requests.post(hb_url, json=data, verify=False)
            if response.status_code == 200:
                logger.debug(f"Sign in url: {hb_url}, response: {response.json()}")
                aid_path = os.path.join(self.aid_path,self.agent_id,'private',self.agent_id+".key")
                with open(aid_path, "rb") as f:
                    private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                aid_path = os.path.join(self.aid_path,self.agent_id,'private',self.agent_id+".crt")
                with open(aid_path, "rb") as f:
                    certificate_pem = f.read().decode('utf-8')
                cert = x509.load_pem_x509_certificate(certificate_pem.encode('utf-8'))
                public_key = cert.public_key()
                public_key_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                if "nonce" in response.json():
                    nonce = response.json()["nonce"]
                    if nonce:
                        signature = private_key.sign(
                            nonce.encode('utf-8'),
                            ec.ECDSA(hashes.SHA256())
                        )
                        data = {
                            "agent_id": self.agent_id,
                            "request_id": request_id,
                            "nonce": nonce,
                            "public_key": public_key_pem,
                            "cert": certificate_pem,
                            "signature": signature.hex(),
                        }
                        response = requests.post(hb_url, json=data, verify=False)
                        if response.status_code == 200:
                            data =  response.json()
                            self.signature = data.get("signature")
                            return data
                        else:
                            logger.error(f"Sign in FAILED: {response.status_code} - {response.json().get('error', '')}")
            else:
                logger.error(f"Sign in failed: {response.status_code} - {response.json().get('error', '')}")
        except Exception as e:
            logger.exception("Sign in exception")

    def sign_out(self) -> None:
        """登出方法"""
        try:
            if self.signature is None:
                return
            hb_url = self.server_url + "/sign_out"
            data = {
                "agent_id": self.agent_id,
                "signature": self.signature,
            }
            response = requests.post(hb_url, json=data, verify=False)
            if response.status_code == 200:
                logger.debug(f"Sign out OK: {response.json()}")
            else:
                logger.error(f"Sign out failed: {response.json()}")
        except Exception as e:
            logger.exception("Sign out exception")
