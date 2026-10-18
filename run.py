import os
import subprocess
import sys
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
  
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Đang khởi động Uvicorn Server cho ứng dụng mô phỏng chứng khoán...")
    
    
    Timer(1.5, open_browser).start()
    
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload"], check=True)
    except KeyboardInterrupt:
        print("\nĐã tắt server thành công!")