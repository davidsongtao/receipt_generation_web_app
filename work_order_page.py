"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：work_order_page.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午4:48
@Contact  ：king.songtao@gmail.com
"""
import streamlit

from utils import *
import streamlit as st
from utils import delete_work_order


def work_tracking_page():
    st.title('➡️工单追踪')
    st.divider()
    from utils import get_total_sale
    total_sale = get_total_sale()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write(f"当前工单数金额: ", )
        if total_sale == None:
            total_sale_value = 0
        else:
            total_sale_value = total_sale
        st.subheader(f"$ {total_sale_value}")
    with col2:
        st.write(f"当前佣金: ", )
        if total_sale == None:
            total_commission = 0
        else:
            total_commission = round(total_sale * 0.024, 2)
        st.subheader(f"$ {total_commission}")
    st.divider()

    with st.expander("🔍工单预览", expanded=True):
        from utils import display_preview_data
        display_preview_data()
    extender_detail = st.expander("📝工单详情", expanded=False)
    with extender_detail:
        from utils import get_all_addresses
        order_info = st.selectbox('请选择您要查看的工单：', options=get_all_addresses(), placeholder="请选择...", index=None)
        if order_info:
            extender_detail.expander = True
            from utils import get_order_by_address
            order = get_order_by_address(order_info)
            with st.form("edit_form"):
                if order:
                    address = st.text_input('地址', value=order['address'][0])
                    notes = st.text_area('备注', value=order['notes'][0], height=200)
                    if order['basic_plan'][0] == '1B1B':
                        index_value = 0
                    elif order['basic_plan'][0] == '1B1B(None-Steam)':
                        index_value = 1
                    elif order['basic_plan'][0] == '2B1B':
                        index_value = 2
                    elif order['basic_plan'][0] == '2B1B(None-Steam)':
                        index_value = 3
                    elif order['basic_plan'][0] == '2B2B':
                        index_value = 4
                    elif order['basic_plan'][0] == '2B2B(None-Steam)':
                        index_value = 5
                    elif order['basic_plan'][0] == '3B1B':
                        index_value = 6
                    elif order['basic_plan'][0] == '3B1B(None-Steam)':
                        index_value = 7
                    elif order['basic_plan'][0] == '3B2B':
                        index_value = 8
                    elif order['basic_plan'][0] == '3B2B(None-Steam)':
                        index_value = 9
                    elif order['basic_plan'][0] == 'House':
                        index_value = 10
                    else:
                        index_value = None
                    project = st.selectbox('工作项目', options=['1B1B', '1B1B(None-Steam)', '2B1B', '2B1B(None-Steam)', '2B2B', '2B2B(None-Steam)', '3B1B', '3B1B(None-Steam)', '3B2B', '3B2B(None-Steam)', 'House'], placeholder="请选择...", index=index_value)
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        register_time = st.date_input('登记时间', value=order['record_time'][0])
                        work_time = st.date_input('工作时间', value=order['record_time'][0])
                        if order['receipt'][0] == '0':
                            index_paper = 0
                        elif order['receipt'][0] == '1':
                            index_paper = 1
                        elif order['receipt'][0] == '2':
                            index_paper = 2
                        else:
                            index_paper = None
                        receipt_or_invoice = st.selectbox('票据种类', options=['收据（R）- 已发', '收据（R）- 未发', '发票（I）'], index=index_paper)
                    with col2:
                        if order['dispatcher'][0] == '小鱼组':
                            index_dis = 0
                        elif order['dispatcher'][0] == 'Kitty组':
                            index_dis = 1
                        elif order['dispatcher'][0] == '李姨组':
                            index_dis = 2
                        elif order['dispatcher'][0] == '海叔组':
                            index_dis = 3
                        elif order['dispatcher'][0] == '娟姐组':
                            index_dis = 4
                        else:
                            index_dis = None
                        dispatcher = st.selectbox('派单阿姨', options=['小鱼组', 'Kitty组', '李姨组', '海叔组', '娟姐组'], index=index_dis)
                        final_price = st.number_input('成交价格', min_value=0, value=int(order["final_price"][0]) if order["final_price"][0] is not None else 0)
                        dispatch_price = st.number_input('派单价格', min_value=0, value=int(order["sales_price"][0]) if order["sales_price"][0] is not None else 0)
                    with col3:
                        if order["confirmed"][0] == 0:
                            confirmed_index = 0
                        else:
                            confirmed_index = 1
                        confirmed = st.selectbox('已确认', options=['✅', '❌'], index=confirmed_index)
                        if order["registered"][0] == 0:
                            registered_index = 0
                        else:
                            registered_index = 1
                        registered = st.selectbox('已登记表格', options=['✅', '❌'], index=registered_index)
                        if order["dispatched"][0] == 0:
                            dispatched_index = 0
                        else:
                            dispatched_index = 1
                        dispatched = st.selectbox('已派单', options=['✅', '❌'], index=dispatched_index)
                submitted = st.form_submit_button('✏️确认修改', disabled=False, type='primary', use_container_width=True)
                delete_button = st.form_submit_button('❌删除工单', disabled=False, use_container_width=True)
                col1, col2 = st.columns([5, 5])
                with col2:
                    confirm_delete = st.checkbox('我确认我想要删除这个工单！')
                with col1:
                    confirm_edit = st.checkbox('确认修改订单内容！')
                if delete_button and not confirm_delete:
                    st.error("请勾选确认删除按钮！该操作不可逆，请谨慎操作！")
                if delete_button and confirm_delete:
                    from utils import delete_work_order
                    delete_work_order(address)
                if submitted and not confirm_edit:
                    st.error("请勾选确认修改按钮！该操作不可逆，请谨慎操作！")
                if submitted and confirm_edit:
                    from utils import edit_work_order_page
                    confirmed_info = 0 if confirmed == "✅" else 1
                    registered_info = 0 if registered == "✅" else 1
                    dispatched_info = 0 if dispatched == "✅" else 1
                    receipt_or_invoice_info = 0 if receipt_or_invoice == '收据（R）- 已发' else (1 if receipt_or_invoice == '收据（R）- 未发' else 2)
                    edit_work_order_page(register_time, notes, work_time, address, project, dispatcher, confirmed_info, registered_info, dispatched_info, dispatch_price, final_price, receipt_or_invoice_info)

    with st.expander("➕新建工单", expanded=False):
        with st.form("my_form"):
            address = st.text_input('地址')
            notes = st.text_area('备注', height=200)
            project = st.selectbox('工作项目', options=['1B1B', '1B1B(None-Steam)', '2B1B', '2B1B(None-Steam)', '2B2B', '2B2B(None-Steam)', '3B1B', '3B1B(None-Steam)', '3B2B', '3B2B(None-Steam)', 'House'], placeholder="请选择...", index=None)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                register_time = st.date_input('登记时间', value=None)
                work_time = st.date_input('工作时间', value=None)
                receipt_or_invoice = st.selectbox('票据种类', options=['收据（R）- 已发', '收据（R）- 未发', '发票（I）'], placeholder="Choose an option...", index=None)

            with col2:
                dispatcher = st.selectbox('派单阿姨', options=['小鱼组', 'Kitty组', '李姨组', '海叔组', '娟姐组'], placeholder="Choose an option...", index=None)
                final_price = st.number_input('成交价格', min_value=0, value=None)
                dispatch_price = st.number_input('派单价格', min_value=0, value=None)
            with col3:
                confirmed = st.selectbox('已确认', options=['✅', '❌'], placeholder="Choose an option...", index=None)
                registered = st.selectbox('已登记表格', options=['✅', '❌'], placeholder="Choose an option...", index=None)
                dispatched = st.selectbox('已派单', options=['✅', '❌'], placeholder="Choose an option...", index=None)

            submitted = st.form_submit_button('提交工单信息', disabled=False, type='primary', use_container_width=True)
            if submitted:
                try:
                    if address == "":
                        st.error("您必须填写地址！", icon="⚠️")
                    elif work_time == None:
                        st.error("您必须填写工作时间！", icon="⚠️")
                    elif dispatcher == None:
                        st.error("您必须填写派单阿姨！", icon="⚠️")
                    else:
                        from utils import insert_data_to_db
                        confirmed_value = 0 if confirmed == '✅' else 1
                        registered_value = 0 if registered == '✅' else 1
                        dispatched_value = 0 if dispatched == '✅' else 1
                        receipt_or_invoice_value = 0 if receipt_or_invoice == '收据（R）- 已发' else 1 if receipt_or_invoice == '收据（R）- 未发' else 2
                        insert_data_to_db(register_time, notes, work_time, address, project, dispatcher, confirmed_value, registered_value, dispatched_value, dispatch_price, final_price, receipt_or_invoice_value)
                except Exception as e:
                    st.error("您输入的信息有误！请重新检查！", icon="⚠️")

        css = r'''
            <style>
                [data-testid="stForm"] {border: 0px}
            </style>
        '''

        st.markdown(css, unsafe_allow_html=True)
