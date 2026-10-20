from langchain_openai import ChatOpenAI
from common.env_util import get_value_from_env

def get_llm():

    # 搞出 ChatOpenAI 这个类的对象： 目的就是拿到 ai  llm = large language model
    llm = ChatOpenAI(
            api_key=get_value_from_env("DEEPSEEK_API_KEY"),
            model=get_value_from_env("DEEPSEEK_MODEL"),
            base_url=get_value_from_env("DEEPSEEK_BASE_URL"),
        )
    return llm

if __name__ == '__main__':
    model = get_llm()
    print(model.invoke("你是什么模型?"))