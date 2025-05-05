from .core import (
    songuyento, tachds, uocchung, boichung, uoclonnhat, nguyento,
    sohoanhao, phantich, daonguoc, tamgiac, dinhgiang, chatai
)
import inspect

# Danh sách các hàm và mô tả
FUNCTIONS = {
    "songuyento": {"desc": "Tìm tất cả số nguyên tố từ n đến m", "func": songuyento},
    "tachds": {"desc": "Tách các chữ số của n và đưa vào danh sách m", "func": tachds},
    "uocchung": {"desc": "Tìm các ước chung của n và m", "func": uocchung},
    "boichung": {"desc": "Tìm các bội chung của n và m", "func": boichung},
    "uoclonnhat": {"desc": "Tìm ước lớn nhất của n", "func": uoclonnhat},
    "nguyento": {"desc": "Kiểm tra n có phải số nguyên tố không", "func": nguyento},
    "sohoanhao": {"desc": "Kiểm tra n có phải số hoàn hảo không", "func": sohoanhao},
    "phantich": {"desc": "Phân tích n ra thừa số nguyên tố", "func": phantich},
    "daonguoc": {"desc": "Đảo ngược số n", "func": daonguoc},
    "tamgiac": {"desc": "Kiểm tra tam giác hợp lệ", "func": tamgiac},
    "dinhgiang": {"desc": "Chuẩn hóa chuỗi văn bản", "func": dinhgiang},
    "chatai": {"desc": "Gửi tin nhắn đến Gemini AI và nhận phản hồi", "func": chatai},
}

def help() -> None:
    """Hiển thị danh sách tất cả hàm trong thư viện."""
    print("Danh sách các hàm trong thư viện hieudzbahon:")
    for name, info in FUNCTIONS.items():
        print(f"- {name}: {info['desc']}")

def code(func_name: str) -> None:
    """Hiển thị mã nguồn của hàm được chỉ định."""
    if func_name not in FUNCTIONS:
        print(f"Hàm '{func_name}' không tồn tại. Dùng 'hieudzbahon.help()' để xem danh sách hàm.")
        return
    source = inspect.getsource(FUNCTIONS[func_name]["func"])
    print(source)

# Export tất cả hàm
__all__ = [
    "songuyento", "tachds", "uocchung", "boichung", "uoclonnhat", "nguyento",
    "sohoanhao", "phantich", "daonguoc", "tamgiac", "dinhgiang", "help", "code", "chatai"
]