import requests
import os
import json

def main():
    # 确保基础 URL 末尾没有斜杠，然后拼接路径
    api_endpoint = "https://api.notionhub.app/get-data"

    # 构建查询参数
    params = {'url':f"https://github.com/{os.getenv('REPOSITORY')}"}
    # 发送 GET 请求
    response = requests.get(api_endpoint, params=params, headers={'Accept': 'application/json'}, timeout=30) # 设置 30 秒超时

    # 检查请求是否成功 (状态码 2xx)
    response.raise_for_status() # 如果状态码不是 2xx，则会抛出 HTTPError

    # 解析 JSON 响应
    api_data = response.json()

    # 检查 API 返回的业务逻辑是否成功
    if api_data.get('success') and 'data' in api_data:
        retrieved_data = api_data['data']
        notion_data = retrieved_data.get('notion')
        weread_data = retrieved_data.get('weread')

        # 设置 NOTION 环境变量 (如果存在)
        if notion_data:
            # 将 Python 对象转换为 JSON 字符串
            notion_json_str = json.dumps(notion_data, ensure_ascii=False) # ensure_ascii=False 保留非 ASCII 字符
            os.environ['NOTION'] = notion_json_str
            print("✅ 环境变量 'NOTION' 已设置。")
        else:
            print("⚠️ 在 API 响应中未找到 Notion 数据或数据为 null。")
            # 根据需要，您可以选择设置为空字符串或不设置
            # os.environ['NOTION'] = ''

        # 设置 WEREAD 环境变量 (如果存在)
        if weread_data:
            # 将 Python 对象转换为 JSON 字符串
            weread_json_str = json.dumps(weread_data, ensure_ascii=False)
            os.environ['WEREAD'] = weread_json_str
            print("✅ 环境变量 'WEREAD' 已设置。")
        else:
            print("⚠️ 在 API 响应中未找到 Weread 数据或数据为 null。")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 调用主函数
    main()