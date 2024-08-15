import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler

# 设置环境变量
BASE_URL = 'https://api.xty.app/v1'
os.environ['OPENAI_API_KEY'] = '7'
os.environ['OPENAI_API_BASE'] = BASE_URL


# 创建一个回调处理器来处理流式输出
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


# 初始化ChatOpenAI模型
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0, streaming=True)

# 设置页面标题
st.title("LangChain 聊天机器人")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful assistant.")
    ]

# 显示聊天历史
for message in st.session_state.messages[1:]:  # 跳过系统消息
    if isinstance(message, HumanMessage):
        st.chat_message("user").write(message.content)
    elif isinstance(message, AIMessage):
        st.chat_message("assistant").write(message.content)

# 获取用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 添加用户消息到历史
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)

    # 创建一个空的容器来存放AI的响应
    ai_response_container = st.empty()

    # 创建StreamHandler实例
    stream_handler = StreamHandler(ai_response_container)

    # 获取AI响应（流式）
    with st.chat_message("assistant"):
        response = model(st.session_state.messages, callbacks=[stream_handler])

    # 添加AI响应到历史
    st.session_state.messages.append(AIMessage(content=response.content))
