import os
import sys
import subprocess
import glob

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Đang cài đặt thư viện cần thiết (PyMuPDF)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
    import fitz

def find_ghostscript():
    """
    Tìm đường dẫn thực thi của Ghostscript trên Windows.
    """
    # Thử lệnh trực tiếp (nếu đã có trong PATH)
    try:
        subprocess.run(["gs", "--version"], capture_output=True, check=True)
        return "gs"
    except:
        pass

    # Tìm trong các thư mục cài đặt mặc định trên Windows
    possible_paths = [
        "C:\\Program Files\\gs\\gs*\\bin\\gswin64c.exe",
        "C:\\Program Files (x86)\\gs\\gs*\\bin\\gswin32c.exe"
    ]
    
    for path in possible_paths:
        matches = glob.glob(path)
        if matches:
            # Lấy bản mới nhất (thường là cái cuối cùng trong danh sách đã sort)
            return sorted(matches)[-1]
            
    return None

def compress_pdf_ghostscript(input_path, output_path, power=4):
    """
    Sử dụng Ghostscript để nén PDF xuống mức cực thấp.
    power: 4 là mức 'screen' (72 dpi) - nhỏ nhất có thể.
    """
    gs_executable = find_ghostscript()
    
    if not gs_executable:
        print("Lỗi: Không tìm thấy Ghostscript. Hãy đảm bảo bạn đã cài đặt nó.")
        return None

    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }
    
    print(f"--- Đang nén bằng Ghostscript: {gs_executable} ---")
    print(f"--- Chế độ nén: {quality[power]} ---")
    
    gs_command = [
        gs_executable, 
        "-sDEVICE=pdfwrite", 
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality[power]}",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]
    
    try:
        subprocess.run(gs_command, check=True)
        if os.path.exists(output_path):
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"Thành công! Dung lượng file sau nén: {final_size:.2f} MB")
            return final_size
    except Exception as e:
        print(f"Lỗi khi chạy Ghostscript: {e}")
        return None

if __name__ == "__main__":
    # Đảm bảo tên file đúng với thực tế của bạn
    input_file = "nen 2.pdf" 
    if not os.path.exists(input_file) and os.path.exists("nen 1"):
        input_file = "nen 2"
        
    output_file = "nen_2_ket_qua_cuoi.pdf"

    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file '{input_file}' trong thư mục này.")
        print("Danh sách file đang có:", os.listdir("."))
        sys.exit(1)

    # Chạy nén bằng Ghostscript trực tiếp (Bỏ qua nén ảnh bằng Python vì GS hiệu quả hơn)
    print(f"Bắt đầu nén file: {input_file} (Dung lượng gốc: {os.path.getsize(input_file)/(1024*1024):.2f} MB)")
    
    # Ưu tiên mức nén cực mạnh (power=4)
    result_size = compress_pdf_ghostscript(input_file, output_file, power=4)
    
    if result_size:
        print(f"\nXong! Bạn hãy kiểm tra file: {output_file}")
        if result_size > 5:
            print("Cảnh báo: File vẫn trên 5MB. Có thể do nội dung gốc quá phức tạp.")
    else:
        print("\nNén thất bại. Vui lòng kiểm tra lại đường dẫn cài đặt Ghostscript.")
import os
import sys
import subprocess

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Đang cài đặt thư viện PyMuPDF...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
    import fitz

def split_pdf_into_parts(input_path, num_parts=3):
    """
    Cắt file PDF thành số phần chỉ định.
    """
    if not os.path.exists(input_path):
        # Kiểm tra nếu file không có đuôi .pdf
        if os.path.exists("nen 1"):
            input_path = "nen 1"
        else:
            print(f"Lỗi: Không tìm thấy file {input_path}")
            return

    print(f"--- Đang bắt đầu cắt file: {input_path} ---")
    
    try:
        # Mở file gốc
        doc = fitz.open(input_path)
        total_pages = len(doc)
        
        if total_pages < num_parts:
            print("Lỗi: Số trang ít hơn số phần muốn cắt.")
            return

        # Tính toán số trang cho mỗi phần
        pages_per_part = total_pages // num_parts
        
        for i in range(num_parts):
            start_page = i * pages_per_part
            # Phần cuối cùng sẽ lấy hết các trang còn lại
            if i == num_parts - 1:
                end_page = total_pages
            else:
                end_page = (i + 1) * pages_per_part
            
            # Tạo file mới cho từng phần
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)
            
            output_filename = f"nen_1_phân_phần_{i+1}.pdf"
            new_doc.save(output_filename, garbage=4, deflate=True)
            new_doc.close()
            
            size_mb = os.path.getsize(output_filename) / (1024 * 1024)
            print(f"Đã tạo: {output_filename} | Trang {start_page+1}-{end_page} | Dung lượng: {size_mb:.2f} MB")

        doc.close()
        print("\n--- Hoàn thành! Sếp sẽ hài lòng với 3 file này ---")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    # Tên file của bạn
    file_name = "nen 1.pdf"
    split_pdf_into_parts(file_name, num_parts=3)