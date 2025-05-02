# 移除或注释掉原来的导入
#: code: utf-8

from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from agentcp.agentcp import AgentCP
from agentcp.log import logger

__version__ = "1.0.0"

__all__ = ["VERSION", "AgentCP" "logger"]
