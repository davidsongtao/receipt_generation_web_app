import time

import streamlit as st
from docx import Document
import io
import os
import re
from datetime import date
from docx.shared import Pt
from openai import OpenAI
from st_copy_to_clipboard import st_copy_to_clipboard
import mammoth

# 常量定义（保持不变）
TEMPLATE_DIR = 'templates'
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# 电器选项
ELECTRICAL_APPLIANCES = [
    "fridge", "microwave", "oven", "dish washer", "washing machine", "dryer", "air conditioner", "kitchen hood"
]

# 房间选项
ROOMS = ["bedroom", "kitchen", "bathroom"]

# 其他服务选项
OTHER_SERVICES = [
    "window glasses", "walls", "mattress",
    "balcony", "laundry room", "sofa",
    "extra kitchen", "extra bathroom", "extra clean of floor board",
    "extra clean of carpet"
]

# AWA服务选项
AWA_SERVICES = [
    "garbage removal", "furniture wipe off",
    "mold removal", "pet hair removal"
]

# 基础服务选项
BASIC_SERVICES = [
    " the clean of floor board,",
    " steam cleaning of carpet, the clean of"
]


def format_date(input_date):
    """
    自定义日期格式化
    将 2024-12-11 格式化为 11th Dec. 2024
    """
    day = input_date.day
    month_abbr = input_date.strftime('%b')
    year = input_date.year

    # 添加日期后缀
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    return f"{day}{suffix} {month_abbr}. {year}"


def replace_placeholders(doc, data_dict):
    """
    替换文档中的占位符并统一字体
    """
    # 替换段落中的文本
    for paragraph in doc.paragraphs:
        for key, value in data_dict.items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, str(value))

        # 统一段落字体和大小
        for run in paragraph.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(10)

    # 替换表格中的文本
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in data_dict.items():
                    if key in cell.text:
                        cell.text = cell.text.replace(key, str(value))

                # 统一单元格内段落的字体和大小
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = 'Arial'
                        run.font.size = Pt(10)

    return doc


def stream_res(res):
    for char in res:
        yield char
        time.sleep(0.02)


def receipt_preview_page(output_doc, receipt_filename):
    """
    收据预览页面
    """
    safe_filename = receipt_filename.replace('/', '.')
    st.title('🧾ATM Receipt')
    st.success(f"收据 >>>{safe_filename}<<< 创建成功！", icon="✅")
    st.info('点击"下载收据"按钮，即可下载Word收据。', icon="ℹ️")

    st.divider()

    # 将 Word 文档转换为 HTML
    with io.BytesIO() as buffer:
        output_doc.save(buffer)
        buffer.seek(0)

        # 使用 mammoth 转换
        result = mammoth.convert_to_html(buffer, style_map=["p[style-name='Right Aligned'] => div.text-right",])
        html_content = result.value

    # 在 Streamlit 中渲染 HTML
    st.markdown(html_content, unsafe_allow_html=True)

    # 将文档保存到内存
    output_buffer = io.BytesIO()
    output_doc.save(output_buffer)
    output_buffer.seek(0)

    st.divider()

    # 下载Word收据
    st.download_button(
        label="下载收据",
        data=output_buffer,
        file_name=safe_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        type="primary"  # 添加主要按钮样式
    )

    # 返回按钮
    if st.button('返回主页', use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()


def validate_address(address):
    """
    验证地址是否只包含英文字符、数字和常见标点符号
    """
    # 增加 / 到允许的字符中
    pattern = r'^[a-zA-Z0-9\s\.\,\-\#\/]+$'

    if not address:
        return False, "地址不能为空"

    if not re.match(pattern, address):
        return False, "地址只能包含英文字符、数字和符号(.,- #/)"

    return True, ""


def main_page():
    """
    主页面
    """
    st.title('🧾ATM Receipt')

    st.divider()

    # 模板选择
    templates = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.docx')]

    if not templates:
        st.error('未找到模板文件，请在templates文件夹中添加.docx文件')
        return None

    selected_template = st.selectbox('收据模板', templates)
    template_path = os.path.join(TEMPLATE_DIR, selected_template)

    # 读取模板
    doc = Document(template_path)

    # 输入区域
    col1, col2 = st.columns(2)

    with col1:
        # 日期选择
        selected_date = st.date_input('收据日期', date.today())

        # 地址输入
        address = st.text_input('客户地址')

        # 地址验证标志
        address_valid = True

        # 实时验证地址
        if address:
            is_valid, error_message = validate_address(address)
            if not is_valid:
                st.error(error_message)
                address_valid = False
            else:
                address_valid = True

        # 金额输入 - 修改为每次加减1
        amount = st.number_input('订单金额', min_value=0.0, step=1.0, format='%f')

        # 基础服务选择
        basic_service = st.selectbox('基础服务', BASIC_SERVICES, placeholder="请选择基础服务...")

    with col2:
        # 电器多选
        electrical_appliances = st.multiselect(
            'Electrical Appliances',
            ELECTRICAL_APPLIANCES,
            placeholder="请选择电器..."
        )

        # 房间多选
        rooms = st.multiselect(
            'Rooms',
            ROOMS,
            placeholder="请选择房间..."
        )

        # 其他服务多选
        other_services = st.multiselect(
            'Other Services',
            OTHER_SERVICES,
            placeholder="请选择其他服务..."
        )

    # AWA服务多选
    awa_services = st.multiselect(
        'AWS Services',
        AWA_SERVICES,
        placeholder="请选择AWA服务..."
    )

    # 处理AWA相关逻辑
    awa = " as well as" if awa_services else ""

    # 处理未选择的电器
    excluded_ele = ", ".join(
        [ele for ele in ELECTRICAL_APPLIANCES if ele not in electrical_appliances]
    )

    generate_receipt_disabled = not (address and address_valid)

    # 生成收据按钮 - 宽度与输入框一致
    if st.button('生成收据', use_container_width=True, type="primary", disabled=generate_receipt_disabled):
        is_valid, error_message = validate_address(address)
        # 输入验证
        if not is_valid:
            st.error(error_message, icon="⚠️")
            return None

        # 准备替换字典
        replace_dict = {
            '$date$': format_date(selected_date),
            '$address$': address,
            '$amount$': f"{amount:.2f}",
            '$basic_service$': basic_service,
            '$electrical_appliances$': ", ".join(electrical_appliances),
            '$rooms$': ", ".join(rooms),
            '$other_services$': ", ".join(other_services),
            '$awa$': awa,
            '$awa_services$': ", ".join(awa_services),
            '$excluded_ele$': excluded_ele
        }

        # 替换占位符
        output_doc = replace_placeholders(doc, replace_dict)

        # 生成文件名，不使用下划线替换空格
        receipt_filename = f"Receipt.{address}.docx"

        return output_doc, receipt_filename

    return None


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
    if generate_button:
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
                st_copy_to_clipboard(response.choices[0].message.content, before_copy_label="📋复制课程总结", after_copy_label="✅已复制到剪贴板")

            except Exception as e:
                st.error(f"发生未知错误！错误代码：{e}")


def window_paper_page():
    st.title('🪟Window Order')
    st.divider()
    st.warning("该功能正在开发中，敬请期待...", icon="⚠️")


def main():
    st.set_page_config(page_title='ATM Assistant', page_icon='🤖')
    # # 设置页面导航
    # st.sidebar.title('导航菜单')

    #
    # # 创建列以均匀分布按钮
    # col1, col2, col3 = st.sidebar.columns(3)
    st.sidebar.title("🏠JF Personal Assistant")
    st.sidebar.divider()
    #
    # with col1:
    receipt_button = st.sidebar.button('🧾创建收据', use_container_width=True, type='primary')
    # with col2:
    writing_button = st.sidebar.button('🤖撰写文案', use_container_width=True, type='primary')
    # with col3:
    # quotation_button = st.button('出报价', use_container_width=True)
    quotation_button = st.sidebar.button('🚀课程总结', use_container_width=True, type='primary')

    window_paper_button = st.sidebar.button('📄窗户委托', use_container_width=True, type='primary')

    st.sidebar.divider()
    st.sidebar.write("版本：V 0.2.1", )

    # 使用按钮状态控制页面展示
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '收据生成'

    # 根据按钮点击更新页面
    if receipt_button:
        st.session_state.current_page = '收据生成'
    elif writing_button:
        st.session_state.current_page = '文案撰写'
    elif quotation_button:
        st.session_state.current_page = '课程总结'
    elif window_paper_button:
        st.session_state.current_page = '窗户委托'

    # 根据导航选择页面
    if st.session_state.current_page == '收据生成':
        if 'page' not in st.session_state:
            st.session_state.page = 'main'

        if st.session_state.page == 'main':
            result = main_page()
            if result:
                st.session_state.output_doc, st.session_state.receipt_filename = result
                st.session_state.page = 'preview'
                st.rerun()

        elif st.session_state.page == 'preview':
            receipt_preview_page(
                st.session_state.output_doc,
                st.session_state.receipt_filename
            )

    elif st.session_state.current_page == '文案撰写':
        writing_page()

    elif st.session_state.current_page == '课程总结':
        quotation_page()
    elif st.session_state.current_page == '窗户委托':
        window_paper_page()


if __name__ == "__main__":
    main()
