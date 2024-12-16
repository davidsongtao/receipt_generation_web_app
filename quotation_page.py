"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：quotation_page.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午4:05
@Contact  ：king.songtao@gmail.com
"""
from utils import *
from openai import OpenAI


def quotation_page():
    """
    课程总结页面
    """
    st.title('💰Money Maker')
    st.divider()
    st.info("请输入课程相关信息。", icon="ℹ️")
    class_date = st.date_input("授课日期：")
    class_name = st.text_input("课程名称：")
    st.info("请将通义听悟中的章节概览粘贴到下面的输入框中。", icon="ℹ️")
    section_review = st.text_area("章节概览：")

    if st.button('👉生成课程总结', use_container_width=True, type='primary'):

        system_prompt = "你现在是一个拥有三十年教学经验的初中英语老师，你刚刚完成一节英语课的授课，以下是记录的课堂授课内容章节速览：\n\n"
        class_date_label = f"授课日期：{class_date}\n"
        class_name_label = f"课程：{class_name}\n"
        sub_title = f"授课日期：{class_date}\n课程：{class_name}\n"
        content = f"{section_review}\n\n"
        end = "请帮我进行润色，丰富内容，形成一篇专业且内容丰富的课堂总结。总结包括两部分主要内容：课程概述/总结与建议。请按照1234等要点对课堂概述进行提炼。主要总结课堂上讲授了什么知识，其他无关紧要的不要总结。总结不要分太多级。"
        prompt = system_prompt + class_date_label + class_name_label + content + end
        # st.markdown(prompt)
        #
        # col1, col2 = st.columns(2)
        # with col1:
        #     st_copy_to_clipboard(prompt, before_copy_label="📋复制完整提示词", after_copy_label="✅已复制到剪贴板")
        # with col2:
        #     st_copy_to_clipboard(sub_title, before_copy_label="📋复制标题块", after_copy_label="✅已复制到剪贴板")
        # st.link_button("👉前往ChatGPT.com生成课程总结", "https://chatgpt.com/?model=auto", use_container_width=True, type='primary')

        client = OpenAI(api_key="sk-2f91e64612a141d9a88e6e6b995e5151", base_url="https://api.deepseek.com")

        # 显示加载中
        with st.spinner('正在努力生成课程总结...请稍后...'):
            try:
                response = (client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                ))
                response_message = st.chat_message("ai")
                response_message.write(stream_res(response.choices[0].message.content))
                import st_copy_to_clipboard
                st_copy_to_clipboard(response.choices[0].message.content, before_copy_label="📋复制课程总结", after_copy_label="✅已复制到剪贴板")

            except Exception as e:
                st.error(f"发生未知错误！错误代码：{e}")
