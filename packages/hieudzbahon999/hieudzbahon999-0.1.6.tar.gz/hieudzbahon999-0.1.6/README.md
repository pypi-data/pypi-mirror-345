**A Python library**  
Thư viện hỗ trợ toán học do Nguyễn Mạnh Hiếu (Học Sinh Trường THCS & THPT BA HÒN ) phát triển, giúp xử lý thông tin nhanh chóng, hỗ trợ lập trình hiệu quả.

```bash
pip install hieudzbahon999 ( chọn 1 trong 2 nếu lỗi ) 
Usage
python

import hieudz
HOW TO USE : hieudz.funcion() ( example : hieudz.help() , hieudz.songuyento(n,m) )
# Tìm số nguyên tố từ 1 đến 10
print(hieudz.songuyento(1, 10))  # Output: [2, 3, 5, 7]

# Tách chữ số
m = []
print(hieudz.tachds(345, m))  # Output: [3, 4, 5]

# Chuẩn hóa chuỗi
print(hieudz.dinhgiang(" ( Hoc , hoc nua , hoc mai ) "))  # Output: (Hoc, hoc nua, hoc mai)

# Xem danh sách hàm
import hdz<help
hieudz.help()  # In danh sách hàm

# Xem mã nguồn hàm
import hdz<code
hieudz.code("dinhgiang")  # In mã nguồn hàm dinhgiang
Functions
songuyento(n, m): Trả về danh sách các số nguyên tố từ n đến m.

tachds(n, m): Tách từng chữ số của n vào danh sách m.

uocchung(n, m): Tìm các ước chung của n và m.

boichung(n, m): Tìm các bội chung của n và m.

uoclonnhat(n): Tìm ước lớn nhất của n.

nguyento(n): Kiểm tra xem n có phải số nguyên tố không.

sohoanhao(n): Kiểm tra xem n có phải số hoàn hảo không.

phantich(n): Phân tích n thành các thừa số nguyên tố.

daonguoc(n): Đảo ngược số n.

tamgiac(a, b, c): Kiểm tra ba cạnh có tạo thành tam giác hợp lệ không.

dinhgiang(n): Chuẩn hóa chuỗi n.

hieudz.help(): Liệt kê tất cả các hàm.

hieudz.code("func_name"): Hiển thị mã nguồn của một hàm.

License
MIT License