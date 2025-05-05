import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv
import json
from Crypto.Cipher import AES
from Crypto.Util import Counter
import base64
from typing import Dict

# 初始化mcp server
mcp = FastMCP("mcp server")

# 城市ID映射
cityIdMapping = {
    "大理市": 640100
}

# 模型映射
modulesNameMapping = {
    "游客兴趣爱好" : 2,
    "游客品牌偏好" : 7,
    "游客迁入/迁出方式": 6,
    "游客停留时长" : 5,
    "游客画像": 4,
    "聚客点" : 3,
    "游客停留天数" : 45,
    "景区潜客吸引力" : 50,
    "潜客用户画像" : 51
}



@mcp.tool(
    name="查询游客大数据",
    description="""
    查询文旅城市、景区游客大数据信息
    1、 支持以下数据模型:
    * 游客兴趣爱好
    * 游客品牌偏好
    * 游客迁入/迁出方式
    * 游客画像
    * 游客停留时长
    * 聚客点
    * 游客停留天数

    2、 支持以下城市：
    * 大理市
    * 丽江市
    """
)
def query_bigdata(moduleName: str, cityName: str):
    if cityName not in cityIdMapping:
        return "暂不支持该城市"
    if moduleName not in modulesNameMapping:
        return "暂不支持改模型"
    # 请求http
    body = requestHttp(modulesNameMapping[moduleName], cityIdMapping[cityName])
    #解密
    body = decrypt(os.getenv("AES_KEY"), os.getenv("AES_IV"), body)
    return format2markdown(body)


def requestHttp(queryId: int, blockId: int) -> str|Dict:
    url = "https://query.dali-ai.com/api/access?instance_id=%s&params=[{\"name\": \"block_id\", \"value\": \"%s\"}]&dbname=yunnan_baidu&method=sql"%(queryId, blockId)
    try:
        body = requests.get(url, headers = {
            'Content-Type': 'application/json',
            "mer-id": os.getenv("API_KEY")
        })
    except:
        return "请求失败"
    data = json.loads(body.text)
    if data["code"] != 200:
        return "请求失败"
    return data['data']


# 解密
def decrypt(key: str, iv: str, encrypted_data: str) -> Dict:
    """
    使用AES-128-CTR模式解密数据
    :param key: 16字节的密钥
    :param iv: 16字节的初始化向量（IV）
    :param encrypted_data: 加密后的数据（字节类型）
    :return: 解密后的数据（字节类型）
    """
    # 创建计数器对象
    counter = Counter.new(128, initial_value=int.from_bytes(iv.encode("utf-8"), byteorder='big'))
    # 创建AES解密器
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CTR, counter=counter)
    # 解密数据
    decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
    return json.loads(decrypted_data)['result']


# 格式化成markdown
def format2markdown(body: Dict) -> str:
    if not body:
        return ""
    # 打印标题行
    line = "| "
    for key in body[0]:
        line += f"{key} | "
    line += "\n"

    # 打印分隔行
    line += "| "
    for _ in body[0]:
        line += "-- | "
    line += "\n"

    # 打印主体行
    for item in body:
        line += "| "
        for key in item:
            line += f"{item[key]} | "
        line += "\n"
    return line


def main():
    load_dotenv()
    print("MCP server start!")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
