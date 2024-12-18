"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：writing_page.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午4:04
@Contact  ：king.songtao@gmail.com
"""
from openai import OpenAI
from st_copy_to_clipboard import st_copy_to_clipboard
from utils import *


def writing_page():
    """
    文案撰写页面，使用OpenAI API生成文案
    """
    st.title('🤖ATM Assistant')

    st.divider()

    # 初始化session state中的生成文案
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = ''

    client = OpenAI(api_key="sk-2f91e64612a141d9a88e6e6b995e5151", base_url="https://api.deepseek.com")

    welcome_message = st.chat_message("ai")
    welcome_message.write("您好👋~我是您的文案助手，请告诉我您对文案的需求：")

    # 文案需求输入
    user_requirement = st.text_input(
        '',
        placeholder='例如：今天保洁工作已完成。'
    )

    # 生成文案按钮
    generate_button = st.button('生成文案', use_container_width=True, type='primary')

    # 生成文案
    if generate_button and not user_requirement:
        st.error("请输入文案需求！")
    elif generate_button and user_requirement:
        # 显示加载中
        with st.spinner('正在生成文案...'):
            try:
                prompt = "请根据以下需求，帮我书写一段宣传文案，字数不少于90个中文字符:\n" + user_requirement + "\n生成的结果中不要包含用户输入的内容，也不要包含需要替换的内容。语言风格不要太机械生硬。"
                # 调用OpenAI/DeepSeek API生成文案
                response = (client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个清洁公司的广告宣传文案生成器。\n"},
                        {"role": "user", "content": prompt}
                    ]
                ))

                # 保存生成的文案到session state
                st.session_state.generated_content = response.choices[0].message.content
            except Exception as e:
                st.error(f"发生未知错误！错误代码：{e}")

        # 始终显示生成的文案（如果有）
        if st.session_state.generated_content:
            st.divider()
            show_message = st.chat_message("assistant")
            show_message.write(stream_res(st.session_state.generated_content))
            st_copy_to_clipboard(st.session_state.generated_content, before_copy_label="📋复制文案", after_copy_label="✅已复制到剪贴板")
            st.info("再次点击“生成文案”可以重新生成哦~", icon="ℹ️")
