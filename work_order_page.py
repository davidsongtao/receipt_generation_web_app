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
        st.subheader (f"$ {total_sale}")
    with col2:
        st.write(f"当前佣金: ", )
        total_commission = round(total_sale*0.024, 2)
        st.subheader(f"$ {total_commission}")
    st.divider()

    # if st.button('➕新建工单', type='primary'):
    # print("点击了新建工单按钮")
    with st.expander("➕创建新工单", expanded=False):
        with st.form("my_form"):
            address = st.text_input('地址')
            notes = st.text_input('备注')
            project = st.text_input('工作项目')
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                register_time = st.date_input('登记时间')
                work_time = st.date_input('工作时间')
                receipt_or_invoice = st.selectbox('票据种类', options=['收据（R）- 已发', '收据（R）- 未发', '发票（I）'])

            with col2:
                dispatcher = st.selectbox('派单阿姨', options=['小鱼', 'Kitty', '李姨', '海叔', '娟姐'])
                final_price = st.number_input('成交价格', min_value=0, value=0)
                dispatch_price = st.number_input('派单价格', min_value=0, value=0)
            with col3:
                confirmed = st.selectbox('已确认', options=['✅', '❌'])
                registered = st.selectbox('已登记表格', options=['✅', '❌'])
                dispatched = st.selectbox('已派单', options=['✅', '❌'])
                sent_or_not = "✅" if receipt_or_invoice == '收据（R）- 已发' else "❌"

            submitted = st.form_submit_button('提交工单信息', disabled=False, type='primary', use_container_width=True)
            if submitted:
                from utils import insert_data_to_db
                insert_data_to_db(register_time, notes, work_time, address, project, dispatcher, confirmed, registered, dispatched, dispatch_price, final_price, receipt_or_invoice, sent_or_not)
                st.write("工单创建成功！", icon="✅")

        css = r'''
            <style>
                [data-testid="stForm"] {border: 0px}
            </style>
        '''

        st.markdown(css, unsafe_allow_html=True)

    with st.expander("🔍工单预览", expanded=True):
        from utils import display_preview_data
        display_preview_data()

    with st.expander("📝工单详情", expanded=False):
        from utils import get_all_addresses
        address = st.selectbox('请选择您要查看的工单：', options=get_all_addresses(), placeholder="请选择您要修改的工单...", index=None)
        if address:
            from utils import get_order_by_address
            order = get_order_by_address(address)
            with st.form("edit_form"):
                if order:
                    address = st.text_input('地址', value=order[0][4])
                    notes = st.text_input('备注', value=order[0][2])
                    project = st.text_input('工作项目', value=order[0][5])
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        register_time = st.date_input('登记时间', value=order[0][1])
                        work_time = st.date_input('工作时间', value=order[0][3])
                        if order[0][12] == '收据（R）- 已发':
                            index_paper = 0
                        elif order[0][12] == '收据（R）- 未发':
                            index_paper = 1
                        elif order[0][12] == '发票（I）':
                            index_paper = 2
                        else:
                            index_paper = None
                        receipt_or_invoice = st.selectbox('票据种类', options=['收据（R）- 已发', '收据（R）- 未发', '发票（I）'], index=index_paper)
                    with col2:
                        if order[0][6] == '小鱼':
                            index_dis = 0
                        elif order[0][6] == 'Kitty':
                            index_dis = 1
                        elif order[0][6] == '李姨':
                            index_dis = 2
                        elif order[0][6] == '海叔':
                            index_dis = 3
                        elif order[0][6] == '娟姐':
                            index_dis = 4
                        else:
                            index_dis = None
                        dispatcher = st.selectbox('派单阿姨', options=['小鱼', 'Kitty', '李姨', '海叔', '娟姐'], index=index_dis)
                        final_price = st.number_input('成交价格', min_value=0, value=int(order[0][11]) if order[0][11] is not None else 0)
                        dispatch_price = st.number_input('派单价格', min_value=0, value=int(order[0][10]) if order[0][10] is not None else 0)
                    with col3:
                        confirmed = st.selectbox('已确认', options=['✅', '❌'], index=0)
                        registered = st.selectbox('已登记表格', options=['✅', '❌'], index=0)
                        dispatched = st.selectbox('已派单', options=['✅', '❌'])
                        sent_or_not = "✅" if receipt_or_invoice == '收据（R）- 已发' else "❌"
                submitted = st.form_submit_button('✏️确认修改', disabled=False, type='primary', use_container_width=True)
                if submitted:
                    from utils import edit_work_order_page
                    edit_work_order_page(register_time, notes, work_time, address, project, dispatcher, confirmed, registered, dispatched, dispatch_price, final_price, receipt_or_invoice, sent_or_not)