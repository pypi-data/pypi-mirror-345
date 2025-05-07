import requests
import os
import json
# load_dotenv 在 GitHub Actions 中不是必需的，因为 REPOSITORY 通常由 GHA 自动提供
# from dotenv import load_dotenv
# load_dotenv() # 如果您在本地测试并且 .env 文件中有 REPOSITORY，可以保留

def main():
    # 确保基础 URL 末尾没有斜杠，然后拼接路径
    api_endpoint = "https://api.notionhub.app/get-data" # 根据您的实际 Worker URL 修改

    github_repo_env = os.getenv('GITHUB_REPOSITORY') # GITHUB_REPOSITORY 是 Actions 提供的标准环境变量
    if not github_repo_env:
        print("::error::GITHUB_REPOSITORY 环境变量未设置。请确保在 GitHub Actions 环境中运行。")
        # 如果您在本地测试，并且希望使用 .env 中的 REPOSITORY，可以取消注释 load_dotenv() 并使用 os.getenv('REPOSITORY')
        # 或者直接在这里硬编码一个用于测试的仓库名
        # github_repo_env = "your_user/your_repo" # 例如
        if not os.getenv('REPOSITORY'): # 后备到您原先的 REPOSITORY 变量
            print("::error::REPOSITORY 环境变量也未设置。无法确定 GitHub 仓库。")
            return # 或者 sys.exit(1)
        github_repo_env = os.getenv('REPOSITORY')


    # 构建查询参数 (您的接口似乎期望 POST JSON body)
    body = {'url': f"https://github.com/{github_repo_env}"}

    print(f"[*] 正在调用 API: {api_endpoint}")
    print(f"[*] 请求体: {json.dumps(body)}")

    try:
        # 发送 POST 请求
        response = requests.post(api_endpoint, json=body, timeout=30)
        print(f"[*] API 响应状态码: {response.status_code}")
        print(f"[*] API 响应内容 (前500字符): {response.text[:500]}")

        # 检查请求是否成功 (状态码 2xx)
        response.raise_for_status() # 如果状态码不是 2xx，则会抛出 HTTPError

        # 解析 JSON 响应
        api_data = response.json()

        # 检查 API 返回的业务逻辑是否成功
        if api_data.get('success') and 'data' in api_data:
            retrieved_data = api_data['data']
            notion_data = retrieved_data.get('notion')
            weread_data = retrieved_data.get('weread')

            # 获取 GITHUB_ENV 文件的路径
            github_env_file = os.getenv('GITHUB_ENV')
            variables_set_for_gha = False

            if not github_env_file:
                print("::warning::未找到 GITHUB_ENV 文件路径。环境变量将仅在当前 Python 进程中通过 os.environ 设置 (不会传递给 GHA 后续步骤)。")
            else:
                print(f"[*] 准备将环境变量写入到 $GITHUB_ENV 文件: {github_env_file}")

            # 设置 NOTION 环境变量
            if notion_data:
                notion_json_str = json.dumps(notion_data, ensure_ascii=False)
                if github_env_file:
                    with open(github_env_file, "a") as f:
                        # 对于可能包含特殊字符或换行的 JSON，使用 heredoc 格式更安全
                        # 但对于单行 JSON 字符串，直接 KEY=VALUE 也可以
                        f.write(f"NOTION<<EOF_NOTION_DATA\n{notion_json_str}\nEOF_NOTION_DATA\n")
                    print("✅ 环境变量 'NOTION' 已写入 $GITHUB_ENV，可用于后续步骤。")
                    variables_set_for_gha = True
                else: # 后备到 os.environ，用于本地测试或 GITHUB_ENV 不可用的情况
                    os.environ['NOTION'] = notion_json_str
                    print("✅ (os.environ) 'NOTION' 已设置。")
            else:
                print("⚠️ 在 API 响应中未找到 Notion 数据或数据为 null。")
                if github_env_file: # 即使数据为空，也可能需要显式设置为空字符串以覆盖旧值
                    with open(github_env_file, "a") as f:
                        f.write("NOTION=\n") # 设置为空
                    print("::notice::'NOTION' 在 $GITHUB_ENV 中设置为空。")


            # 设置 WEREAD 环境变量
            if weread_data:
                weread_json_str = json.dumps(weread_data, ensure_ascii=False)
                if github_env_file:
                    with open(github_env_file, "a") as f:
                        f.write(f"WEREAD<<EOF_WEREAD_DATA\n{weread_json_str}\nEOF_WEREAD_DATA\n")
                    print("✅ 环境变量 'WEREAD' 已写入 $GITHUB_ENV，可用于后续步骤。")
                    variables_set_for_gha = True
                else:
                    os.environ['WEREAD'] = weread_json_str
                    print("✅ (os.environ) 'WEREAD' 已设置。")
            else:
                print("⚠️ 在 API 响应中未找到 Weread 数据或数据为 null。")
                if github_env_file:
                    with open(github_env_file, "a") as f:
                        f.write("WEREAD=\n")
                    print("::notice::'WEREAD' 在 $GITHUB_ENV 中设置为空。")

            if variables_set_for_gha:
                print("\n[*] GitHub Actions 的环境变量已准备就绪。")

        else:
            error_message = api_data.get('error', 'API 调用成功但响应中 success 不为 true 或缺少 data 字段。')
            print(f"::error::API 业务逻辑错误: {error_message}")
            # 根据需要决定是否 sys.exit(1)

    except requests.exceptions.HTTPError as errh:
        print(f"::error::HTTP 错误: {errh}")
        print(f"   状态码: {errh.response.status_code}")
        try:
            error_details = errh.response.json()
            print(f"   响应详情: {error_details}")
        except json.JSONDecodeError:
            print(f"   响应内容 (非 JSON): {errh.response.text}")
        # 在 GHA 中，通常让 action 失败
        # sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"::error::请求错误: {err}")
        # sys.exit(1)
    except json.JSONDecodeError as errj:
        print(f"::error::JSON 解析错误: {errj}")
        if 'response' in locals():
             print(f"   收到的响应文本 (前500字符): {response.text[:500]}")
        # sys.exit(1)
    except Exception as e:
        print(f"::error::发生意外错误: {e}")
        # import traceback
        # traceback.print_exc()
        # sys.exit(1)

# --- 主程序入口 ---
if __name__ == "__main__":
    main()