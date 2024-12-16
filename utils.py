"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：utils.py.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午3:59
@Contact  ：king.songtao@gmail.com
"""
import traceback
from datetime import date, time
from docx.shared import Pt
import re
import streamlit as st
import sqlite3
import pandas as pd


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
    """前端制作流式输出效果"""
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


def connect_db():
    return sqlite3.connect(r"./work_orders.db")


def insert_data_to_db(register_time, notes, work_time, address, project, dispatcher, confirmed, registered, dispatched, dispatch_price, final_price, receipt_or_invoice, sent_or_not):
    conn = connect_db()
    if not conn:
        st.error("数据库连接失败！")
        return

    cursor = conn.cursor()
    try:
        # 打印所有参数，检查是否有异常值
        print("参数列表：",
            register_time, notes, work_time, address, project,
            dispatcher, confirmed, registered, dispatched,
            dispatch_price, final_price, receipt_or_invoice, sent_or_not
        )

        cursor.execute(
            """
            INSERT INTO work_orders (
                register_time, notes, work_time, address, project, 
                dispatcher, confirmed, registered, dispatched, 
                dispatch_price, final_price, receipt_or_invoice, sent_or_not
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                register_time, notes, work_time, address, project,
                dispatcher, confirmed, registered, dispatched,
                dispatch_price, final_price, receipt_or_invoice, sent_or_not
            )
        )
        conn.commit()
        st.success("工单创建成功！", icon="✅")
    except Exception as e:
        conn.rollback()
        st.error(f"添加失败，错误原因：{e}")
        print(f"详细错误信息：{traceback.format_exc()}")
    finally:
        cursor.close()
        conn.close()


# 显示工单数据
def display_all_orders():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM work_orders", conn)
    conn.close()

    st.dataframe(df, hide_index=True)
