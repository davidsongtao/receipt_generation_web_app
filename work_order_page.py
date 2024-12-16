"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：work_order_page.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午4:48
@Contact  ：king.songtao@gmail.com
"""
from utils import *


def new_work_order_page():
    with st.form(key='new_work_order'):
        address = st.text_input('地址')
        notes = st.text_input('备注')
        project = st.text_input('工作项目')
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            register_time = str(st.date_input('登记时间'))
            work_time = str(st.date_input('工作时间'))
            receipt_or_invoice = str(st.selectbox('票据种类', options=['收据（R）- 已发', '收据（R）- 未发', '发票（I）']))

        with col2:
            dispatcher = st.selectbox('派单阿姨', options=['A', 'B', 'C', 'D', 'E'])
            final_price = st.number_input('成交价格', min_value=0, value=0)
            dispatch_price = st.number_input('派单价格', min_value=0, value=0)
        with col3:
            confirmed = st.selectbox('已确认', options=['1', '2'])
            registered = st.selectbox('已登记表格', options=['1', '2'])
            dispatched = st.selectbox('已派单', options=['1', '2'])
            sent_or_not = "1" if receipt_or_invoice == '收据（R）- 已发' else "2"

        if st.form_submit_button('确认创建工单', type='primary', use_container_width=True):
            print("表单数据：",
                  register_time,
                  notes,
                  work_time,
                  address,
                  project,
                  dispatcher,
                  confirmed,
                  registered,
                  dispatched,
                  dispatch_price,
                  final_price,
                  receipt_or_invoice,
                  sent_or_not
                  )
            try:
                insert_data_to_db(register_time, notes, work_time, address, project, dispatcher, confirmed, registered, dispatched, dispatch_price, final_price, receipt_or_invoice, sent_or_not)
                st.success("工单创建成功！", icon="✅")
            except Exception as e:
                st.error(f"工单创建失败，请检查输入信息是否正确。\n{e}", icon="❌")


def work_tracking_page():
    st.title('➡️工单追踪')
    st.divider()

    if st.button('➕新建工单', type='primary'):
        new_work_order_page()

    display_all_orders()
