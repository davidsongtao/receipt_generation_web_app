"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：receipt_preview_page.py.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午4:03
@Contact  ：king.songtao@gmail.com
"""
import mammoth
from utils import *
import io


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
