import json
from typing import Dict, List
from datetime import datetime
import os
import requests
from requests.exceptions import HTTPError


def _handle_response(response: requests.Response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        # 尝试解析错误详情
        try:
            error_info = response.json()
            raise FinanceAPIError(
                f"API request failed: {error_info.get('message', 'Unknown error')}",
                status_code=response.status_code,
                detail=error_info
            ) from e
        except ValueError:
            raise FinanceAPIError(
                f"API request failed with status {response.status_code}",
                status_code=response.status_code
            ) from e
    return response.json().get('result')


class ModelClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get_rule_info(self, rule_id: str) -> Dict:
        """获取规则详情"""
        url = f"{self.base_url}/finance/model-sys/outapi/rule/{rule_id}"
        response = self.session.get(url, timeout=self.timeout)
        return _handle_response(response)

    def list_rules(self) -> List[Dict]:
        """获取已发布规则列表"""
        url = f"{self.base_url}/finance/model-sys/outapi/rule/list"
        response = self.session.get(url, timeout=self.timeout)
        return _handle_response(response)

    def get_model_info(self, model_id: str) -> Dict:
        """获取模型详情"""
        url = f"{self.base_url}/finance/model-sys/outapi/model/{model_id}"
        response = self.session.get(url, timeout=self.timeout)
        return _handle_response(response)

    def list_models(self) -> List[Dict]:
        """获取所有模型列表"""
        url = f"{self.base_url}/finance/model-sys/outapi/model/list"
        response = self.session.get(url, timeout=self.timeout)
        return _handle_response(response)

    def get_task_info(self, task_id: str) -> Dict:
        """获取任务详情"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/{task_id}"
        response = self.session.get(url, timeout=self.timeout)
        return _handle_response(response)

    def stop_task(self, task_id: str) -> None:
        """终止任务"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/stop/{task_id}"
        response = self.session.get(url, timeout=self.timeout)
        _handle_response(response)

    # 以下方法处理协议相关接口
    def get_rule_protocol(self, rule_id: str) -> Dict:
        """根据ruleId获取规则执行协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/rule/{rule_id}/protocol"
        response = self.session.post(url, timeout=self.timeout)
        return _handle_response(response)

    def get_rule_protocol_by_code(self, rule_code: str) -> Dict:
        """根据ruleCode获取规则执行协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/rule/{rule_code}/getRuleProtocolByCode"
        response = self.session.post(url, timeout=self.timeout)
        return _handle_response(response)

    def get_all_rule_protocol(self) -> Dict:
        """获取所有规则执行协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/rule/getAllRuleProtocol"
        response = self.session.post(url, timeout=self.timeout)
        return _handle_response(response)

    def save_rule_protocol_to_file(self, path: str, rule_code: str) -> str:
        """将规则执行协议生成json文件并保存到指定目录"""
        protocol_data = self.get_rule_protocol_by_code(rule_code)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{rule_code}_{timestamp}.json"
        full_path = os.path.join(path, filename)
        os.makedirs(path, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(protocol_data, f, ensure_ascii=False, indent=4)
        return full_path

    def save_all_rule_protocol_to_file(self, path: str) -> List[str]:
        """
        将全部规则执行协议生成多个JSON文件并保存到指定目录
        返回成功保存的文件路径列表
        """
        saved_files = []
        all_protocols = self.get_all_rule_protocol()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        os.makedirs(path, exist_ok=True)
        for protocol in all_protocols:
            rules = protocol.get("rules")
            first_rule = rules[0]
            rule_code = first_rule.get("ruleId")
            filename = f"{rule_code}_{timestamp}.json"
            full_path = os.path.join(path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(protocol, f, ensure_ascii=False, indent=4)
            saved_files.append(full_path)
        return saved_files

    def execute_rule_protocol(self, protocol_data: Dict) -> str:
        """执行规则协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/rule/execute"
        response = self.session.post(url, json=protocol_data, timeout=self.timeout)
        return _handle_response(response)

    def get_model_protocol(self, model_id: str) -> Dict:
        """根据modelId获取模型执行协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/model/{model_id}/protocol"
        response = self.session.post(url, timeout=self.timeout)
        return _handle_response(response)

    def get_model_protocol_by_code(self, model_code: str) -> Dict:
        """根据modelCode获取模型执行协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/model/{model_code}/getModelProtocolByCode"
        response = self.session.post(url, timeout=self.timeout)
        return _handle_response(response)

    def get_all_model_protocol(self) -> Dict:
        """获取所有模型执行协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/model/getAllModelProtocol"
        response = self.session.post(url, timeout=self.timeout)
        return _handle_response(response)

    def save_model_protocol_to_file(self, path: str, model_code: str) -> str:
        """将模型执行协议生成json文件并保存到指定目录"""
        protocol_data = self.get_model_protocol_by_code(model_code)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{model_code}_{timestamp}.json"
        full_path = os.path.join(path, filename)
        os.makedirs(path, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(protocol_data, f, ensure_ascii=False, indent=4)
        return full_path

    def save_all_model_protocol_to_file(self, path: str) -> List[str]:
        """
        将全部模型执行协议生成多个JSON文件并保存到指定目录
        返回成功保存的文件路径列表
        """
        saved_files = []
        all_protocols = self.get_all_model_protocol()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        os.makedirs(path, exist_ok=True)
        for protocol in all_protocols:
            models = protocol.get("modelInfos")
            first_model = models[0]
            model_code = first_model.get("modelId")
            filename = f"{model_code}_{timestamp}.json"
            full_path = os.path.join(path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(protocol, f, ensure_ascii=False, indent=4)
            saved_files.append(full_path)
        return saved_files

    def execute_model_protocol(self, protocol_data: Dict) -> str:
        """执行模型协议"""
        url = f"{self.base_url}/finance/model-sys/outapi/task/model/execute"
        response = self.session.post(url, json=protocol_data, timeout=self.timeout)
        return _handle_response(response)


class FinanceAPIError(Exception):
    """自定义API异常"""

    def __init__(self, message: str, status_code: int = None, detail: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
