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


def extract_date_from_html(html_content):
    """
    提取 HTML 内容中的日期
    假设日期格式为 "16th Dec. 2024"（可以根据需要调整正则表达式）
    """
    # 用正则表达式匹配日期
    date_pattern = r"\d{1,2}[a-zA-Z]{2}\s[A-Za-z]+\.\s\d{4}"
    match = re.search(date_pattern, html_content)

    if match:
        return match.group(0)  # 返回匹配到的日期
    return None


def receipt_preview_page(output_doc, receipt_filename):
    """
    收据预览页面
    """
    safe_filename = receipt_filename.replace('/', '.')
    st.title('🧾ATM Receipt')
    st.success(f"收据 >>>{safe_filename}<<< 创建成功！", icon="✅")
    st.info('点击"下载收据"按钮，即可下载Word收据。', icon="ℹ️")

    st.divider()
    # 发票预览模块
    # 自定义 CSS，设置字体为 Arial
    custom_css = """
        <style>
        body {
            font-family: Arial, sans-serif; /* 全局设置字体为 Arial */
        }
        .date-right {
            text-align: right;
            margin-bottom: 10px;
            font-family: Arial, sans-serif; /* 确保日期部分也使用 Arial */
        }
        .other-content {
            text-align: left;
            font-family: Arial, sans-serif; /* Word 内容字体设置为 Arial */
        }
        </style>
        """

    # 使用 mammoth 转换 Word 文档内容为 HTML
    with io.BytesIO() as buffer:
        output_doc.save(buffer)
        buffer.seek(0)
        result = mammoth.convert_to_html(buffer)
        html_content = result.value

    # 提取文档中的日期
    extracted_date = extract_date_from_html(html_content)

    # 如果找到了日期，渲染右对齐的日期
    if extracted_date:
        date_html = f'<div class="date-right">{extracted_date}</div>'
    else:
        date_html = ""  # 如果没有日期则不显示

    # 删除 HTML 中的日期内容（如果有的话）
    html_content = html_content.replace(extracted_date, "") if extracted_date else html_content

    # 将 mammoth 转换的 HTML 包裹在 "other-content" 样式中
    html_content_wrapped = f'<div class="other-content">{html_content}</div>'

    # 渲染自定义 CSS、日期和 Word 文档内容
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown(date_html, unsafe_allow_html=True)  # 日期单独渲染，右对齐
    st.markdown(html_content_wrapped, unsafe_allow_html=True)  # 其他内容左对齐

    st.divider()

    # 将文档保存到内存
    output_buffer = io.BytesIO()
    output_doc.save(output_buffer)
    output_buffer.seek(0)

    # 下载Word收据
    st.download_button(
        label="下载Word格式收据",
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
        return False, "地址只能包含英文字符、数字和符号(.,- #/)。请检查是否含有中文逗号！"

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


def price_page():
    st.title('⌨️Auto Quotation')
    st.divider()
    pricing_address = st.text_input("期望服务地址：")
    wanted_date = format_date(st.date_input("期望服务日期：", min_value="today"))
    generate_button_disabled = True
    # 实时验证地址
    if pricing_address:
        is_valid, error_message = validate_address(pricing_address)
        if not is_valid:
            st.error(error_message)
            generate_button_disabled = True
        else:
            generate_button_disabled = False
    st.info("请选择您要报价的基础套餐并确认最终报价", icon="ℹ️")

    # 1. 定义套餐和默认价格
    basic_plans = {
        "1b1b(洗地毯)": 275,
        "1b1b(不蒸汽洗地毯)": 220,
        "2b1b(蒸汽洗地毯)": 320,
        "2b1b(不蒸汽洗地毯)": 280,
        "2b2b(蒸汽洗地毯)": 350,
        "2b2b(不蒸汽洗地毯)": 300,
        "3b1b(蒸汽洗地毯)": 405,
        "3b1b(不蒸汽洗地毯)": 350,
        "3b2b(蒸汽洗地毯)": 445,
        "3b2b(不蒸汽洗地毯)": 400
    }

    add_ons = {
        "冰箱": 50,
        "微波炉": 20,
        "烤箱": 50,
        "洗碗机": 25,
        "洗衣机": 25,
        "干衣机": 25,
        "单独洗衣房（三室以上）": 30,
        "单列玻璃": 8,
        "空调（外表加滤网）": 25,
        "洗床垫": 80,
        "蒸汽洗沙发": 40,
        "擦家具": 50,
        "擦墙(现场估价)": 10,
        "阳台+三面推拉门玻璃": 80,
        "地毯吸尘(单独房间)": 20,
        "地板吸尘拖地(单独房间)": 20,
        "除宠物毛发(每个房间)": 40,
        "整理物品+扔垃圾": 0,
        "额外卫生间": 70,
        "额外厨房": 130,
        "油烟机": 50,
    }

    # 3. 让用户选择套餐
    basic_plan_selected = st.selectbox("基础套餐：", options=list(basic_plans.keys()))

    # 4. 获取用户选择的套餐对应的默认价格
    default_price = basic_plans[basic_plan_selected]

    # 5. 显示并允许用户修改价格
    basic_plan_price = st.number_input(f"基础套餐 -> {basic_plan_selected} 的最终价格：", min_value=0, value=default_price)

    st.info("请选择您要报价的基础套餐并确认最终报价", icon="ℹ️")

    selected_add_ons = st.multiselect("请选择附加服务（可选择多个或不选择）", options=list(add_ons.keys()))
    add_ons_price = 0
    modified_add_ons = {}

    for add_on in selected_add_ons:
        # 允许用户修改附加服务的价格
        modified_price = st.number_input(f"{add_on} 的最终报价", min_value=0, value=add_ons[add_on])
        modified_add_ons[add_on] = modified_price
        add_ons_price += modified_price

    # 8. 计算总价格
    total_price = basic_plan_price + add_ons_price

    st.warning("请认真核对您所选择的所有服务内容及对应报价，如有错误请及时修改", icon="⚠️")

    if selected_add_ons:
        st.write(f"您选择的附加服务是: {', '.join(selected_add_ons)}")
        for add_on, price in modified_add_ons.items():
            st.write(f"{add_on}的修改后的价格: $ {price}")
    else:
        st.write("您没有选择任何附加服务")

    # 10. 显示最终的总价格
    st.write(f"最终总价格为: $ {total_price}")

    # pricing_button = st.button('生成最终报价邮件', use_container_width=True, type='primary')
    #
    # if pricing_button:
    #     st.session_state.current_page = '报价邮件'

    if st.button('生成最终报价邮件', use_container_width=True, type='primary', disabled=generate_button_disabled):
        email_subject = pricing_address
        email_body = f"""尊敬的客户，\n\n感谢您选择我们的服务！根据您的选择，以下是您的定制报价单：\n\n服务地址：{pricing_address}\n期望服务日期：{wanted_date}\n\n基础套餐: {basic_plan_selected}\n基础套餐价格: $ {basic_plan_price}\n选择的附加服务: {', '.join(selected_add_ons) if selected_add_ons else '无附加服务'}\n附加服务价格明细:\n"""
        for add_on, price in modified_add_ons.items():
            email_body += f"{add_on}: $ {price}\n"

        email_body += f"\n总价格: $ {total_price}\n\n如有任何问题，请随时联系我们。\n\n此致，\n\nATM Cleaning Service"

        st.success(f"报价单 >>>{pricing_address}<<< 创建成功！", icon="✅")
        st.divider()
        st.write("Email Subject:")
        st.code(email_subject)
        st.write("Email Body:")
        st.code(email_body)

        # col1, col2 = st.columns(2)
        # with col1:
        #     st_copy_to_clipboard(email_subject, before_copy_label="复制邮件主题", after_copy_label="✅主题已复制")
        # with col2:
        #     st_copy_to_clipboard(email_body, before_copy_label="复制邮件内容", after_copy_label="✅内容已复制")
        if st.button('重新修改报价内容', use_container_width=True):
            st.session_state.page = 'main'
            st.rerun()


def main():
    st.set_page_config(page_title='ATM Assistant', page_icon='🤖')
    st.sidebar.title("🏠JF Personal Assistant")
    st.sidebar.divider()

    receipt_button = st.sidebar.button('🧾创建收据', use_container_width=True, type='primary')

    writing_button = st.sidebar.button('🤖撰写文案', use_container_width=True, type='primary')

    price_button = st.sidebar.button('💰自动报价', use_container_width=True, type='primary')
    quotation_button = st.sidebar.button('🚀课程总结', use_container_width=True, type='primary')

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
    elif price_button:
        st.session_state.current_page = '报价生成'

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
    elif st.session_state.current_page == '报价生成':
        price_page()


if __name__ == "__main__":
    main()
