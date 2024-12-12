import time

import streamlit as st
from docx import Document
import io
import os
from datetime import date
from docx.shared import Pt
from openai import OpenAI
from st_copy_to_clipboard import st_copy_to_clipboard

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
    " the clean of floor board",
    " steam cleaning of carpet, clean of"
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
        time.sleep(0.05)


def receipt_preview_page(output_doc, receipt_filename):
    """
    收据预览页面
    """
    st.title('🧾ATM Receipt')
    st.success(f"收据创建成功！", icon="✅")
    st.info('点击"下载收据"按钮即可下载Word收据')

    # 将文档保存到内存
    output_buffer = io.BytesIO()
    output_doc.save(output_buffer)
    output_buffer.seek(0)

    # 下载Word收据
    st.download_button(
        label="下载收据",
        data=output_buffer,
        file_name=receipt_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        type="primary"  # 添加主要按钮样式
    )

    # 返回按钮
    if st.button('返回主页', use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()


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

    selected_template = st.selectbox('收据模板', templates, index=1)
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

    # 生成收据按钮 - 宽度与输入框一致
    if st.button('生成收据', use_container_width=True, type="primary"):
        # 输入验证
        if not address:
            st.warning("请填写地址")
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
        receipt_filename = f"receipt.{address}.docx"

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

    welcome_message = st.chat_message("assistant")
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
                prompt = "请根据以下需求，帮我书写一段宣传文案，字数不少于50个中文字符，不超过80个中文字符:\n" + user_requirement + "\n生成的结果中不要包含用户输入的内容，也不要包含需要替换的内容。"
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
    自动化报价页面
    """
    st.title('自动化报价')
    st.warning('页面正在开发中')


def main():
    st.set_page_config(page_title='ATM Assistant', page_icon='🤖')
    # # 设置页面导航
    # st.sidebar.title('导航菜单')


    #
    # # 创建列以均匀分布按钮
    # col1, col2, col3 = st.sidebar.columns(3)
    st.sidebar.title("🏠ATM Cleaning Service")
    st.sidebar.divider()
    #
    # with col1:
    receipt_button = st.sidebar.button('🧾创建收据', use_container_width=True, type='primary')
    # with col2:
    writing_button = st.sidebar.button('🤖撰写文案', use_container_width=True, type='primary')
    # with col3:
    # quotation_button = st.button('出报价', use_container_width=True)

    st.sidebar.divider()
    st.sidebar.write("版本：V 0.1.0", )

    # 使用按钮状态控制页面展示
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '收据生成'

    # 根据按钮点击更新页面
    if receipt_button:
        st.session_state.current_page = '收据生成'
    elif writing_button:
        st.session_state.current_page = '文案撰写'
    # elif quotation_button:
    #     st.session_state.current_page = '自动化报价'

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

    # elif st.session_state.current_page == '自动化报价':
    #     quotation_page()


if __name__ == "__main__":
    main()
