import time
from docx import Document
from config import *
from receipt_preview_page import *
from writing_page import *
from quotation_page import *
import streamlit as st
from work_order_page import *


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
    st.set_page_config(page_title='ATM Assistant', page_icon='🤖', layout='wide', initial_sidebar_state="auto")
    st.sidebar.title("🏠ATM Cleaning Assistant")
    st.sidebar.divider()

    work_tracking = st.sidebar.button('📊工单追踪', use_container_width=True, type='primary', key='work_tracking')

    receipt_button = st.sidebar.button('🧾创建收据', use_container_width=True, type='primary', key='receipt')

    writing_button = st.sidebar.button('🤖撰写文案', use_container_width=True, type='primary', key='writing')

    price_button = st.sidebar.button('💰自动报价', use_container_width=True, type='primary', key='price')

    st.sidebar.divider()
    st.sidebar.title("👤Personal Assistant")
    quotation_button = st.sidebar.button('🚀课程总结', use_container_width=True, type='primary')

    st.sidebar.divider()
    st.sidebar.write("版本：V 0.2.1", )

    # 使用按钮状态控制页面展示
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '工单追踪'

    # 根据按钮点击更新页面
    if receipt_button:
        st.session_state.current_page = '收据生成'
    elif writing_button:
        st.session_state.current_page = '文案撰写'
    elif quotation_button:
        st.session_state.current_page = '课程总结'
    elif price_button:
        st.session_state.current_page = '报价生成'
    elif work_tracking:
        st.session_state.current_page = '工单追踪'

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
    elif st.session_state.current_page == '工单追踪':
        work_tracking_page()


if __name__ == "__main__":
    main()
