import os
import requests

BASE_API = os.environ.get("BASE_API", "http://localhost:8080")


def get_previous_submodel(submodel_no: str):
    """获取前置模型建模结果"""
    url = f"{BASE_API}/submodel/{submodel_no}"
    response = requests.get(url)
    res = response.json()
    if res.get("status") == 200:
        return res["data"]
    raise ValueError(f"请求失败: {res}")


def get_submodel_meta(submodel_no: str):
    """获取模型元数据"""
    url = f"{BASE_API}/submodelMeta/{submodel_no}"
    response = requests.get(url)
    res = response.json()
    if res.get("status") == 200:
        data = res["data"]
        exclude_keys = {"id", "createdAt", "updatedAt", "previous", "next"}
        filtered_data = {k: v for k, v in data.items() if k not in exclude_keys}
        return filtered_data
    raise ValueError(f"请求失败: {res}")






