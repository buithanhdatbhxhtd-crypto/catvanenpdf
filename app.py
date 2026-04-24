import streamlit as st
import fitz  # PyMuPDF
import os
import io
import zipfile

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Phần mềm xử lý PDF - Mr Đạt", page_icon="📄", layout="centered")

# --- PHẦN THÔNG TIN BẢN QUYỀN (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=100)
st.sidebar.title("Thông tin tác giả")
st.sidebar.info(
    """
    **Mr Đạt**
    - 📞 Hotline: **0986.053.006**
    - 🏢 Chức vụ: Chuyên viên BHXH Thuận An
    - 🛠️ Công cụ: Nén & Cắt PDF chuyên nghiệp
    """
)

st.title("📄 Công Cụ Xử Lý PDF Chuyên Nghiệp")
st.markdown("---")

# --- GIAO DIỆN CHỌN CHỨC NĂNG ---
option = st.selectbox(
    "Chọn tính năng bạn muốn sử dụng:",
    ("Nén PDF (Giảm dung lượng)", "Cắt PDF (Chia nhỏ file)")
)

# --- HÀM XỬ LÝ NÉN ---
def compress_pdf_logic(input_bytes, dpi=72):
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    out_doc = fitz.open()
    
    for page in doc:
        rect = page.rect
        new_page = out_doc.new_page(width=rect.width, height=rect.height)
        # Rasterize trang với DPI thấp để nén mạnh
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72)) 
        new_page.insert_image(rect, pixmap=pix)
        
    output_buffer = io.BytesIO()
    out_doc.save(output_buffer, garbage=4, deflate=True, clean=True)
    out_doc.close()
    doc.close()
    return output_buffer.getvalue()

# --- HÀM XỬ LÝ CẮT ---
def split_pdf_logic(input_bytes, num_parts=3):
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    total_pages = len(doc)
    pages_per_part = total_pages // num_parts
    
    output_files = []
    for i in range(num_parts):
        start_page = i * pages_per_part
        end_page = total_pages if i == num_parts - 1 else (i + 1) * pages_per_part
        
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)
        
        part_buffer = io.BytesIO()
        new_doc.save(part_buffer, garbage=4, deflate=True)
        new_doc.close()
        
        output_files.append((f"phan_{i+1}.pdf", part_buffer.getvalue()))
    
    doc.close()
    return output_files

# --- GIAO DIỆN CHI TIẾT ---
uploaded_file = st.file_uploader("Kéo thả hoặc chọn file PDF tại đây", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    st.write(f"📁 Tên file: `{uploaded_file.name}`")
    st.write(f"⚖️ Dung lượng gốc: `{file_size_mb:.2f} MB`")

    if option == "Nén PDF (Giảm dung lượng)":
        st.subheader("Cấu hình nén")
        quality = st.slider("Chọn chất lượng (DPI thấp = File nhỏ hơn)", 50, 150, 72)
        
        if st.button("Bắt đầu nén ngay"):
            with st.spinner("Đang nén... Vui lòng đợi trong giây lát..."):
                result = compress_pdf_logic(file_bytes, quality)
                new_size = len(result) / (1024 * 1024)
                
                st.success(f"Nén thành công! Dung lượng mới: {new_size:.2f} MB")
                st.download_button(
                    label="📥 Tải file đã nén về máy",
                    data=result,
                    file_name=f"compressed_{uploaded_file.name}",
                    mime="application/pdf"
                )

    elif option == "Cắt PDF (Chia nhỏ file)":
        st.subheader("Cấu hình cắt file")
        num_parts = st.number_input("Bạn muốn cắt thành mấy phần?", min_value=2, max_value=10, value=3)
        
        if st.button("Bắt đầu cắt file"):
            with st.spinner("Đang xử lý cắt file..."):
                parts = split_pdf_logic(file_bytes, num_parts)
                
                # Tạo file ZIP để tải tất cả các phần về một lúc
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for filename, data in parts:
                        zip_file.writestr(filename, data)
                
                st.success(f"Đã cắt thành công {num_parts} phần!")
                st.download_button(
                    label="📥 Tải tất cả các phần (File .ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="pdf_parts_mr_dat.zip",
                    mime="application/zip"
                )

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Bản quyền © 2024 thuộc về <b>Mr Đạt - 0986.053.006</b><br>
        <i>Chuyên viên BHXH Thuận An - Hỗ trợ xử lý hồ sơ nhanh chóng</i>
    </div>
    """, 
    unsafe_allow_html=True
)
