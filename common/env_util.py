from dotenv import load_dotenv
import os
# 加载 .env 文件中的环境变量
load_dotenv()


def get_value_from_env(key):
    # 读取环境变量
    value = os.getenv(key)
    return value


if __name__ == '__main__':
    print(get_value_from_env("DEEPSEEK_MODEL"))