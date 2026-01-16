import sys
import os

# Versi Produksi: Tanpa print/input console untuk menghindari crash di mode Windowed (-w)

def main_entry():
    try:
        # Pengecekan aset dasar sebelum start
        # Catatan: Saat di-freeze (EXE), path aset ditangani oleh PyInstaller (_MEIPASS)
        # Jadi pengecekan manual os.path.exists("assets") di sini tidak selalu valid untuk EXE onefile.
        # Kita percayakan pada logic di main.py.
        
        from app.main import main
        main()
        
    except Exception as e:
        # Jika terjadi error fatal, tampilkan popup pesan error
        # agar user/admin tahu apa yang salah.
        import tkinter as tk
        from tkinter import messagebox
        import traceback
        
        # Buat root window sementara untuk menampilkan messagebox
        root = tk.Tk()
        root.withdraw() # Sembunyikan window utama, cuma butuh popupnya
        
        error_msg = traceback.format_exc()
        messagebox.showerror("Gagal Memulai AutoBell", f"Terjadi kesalahan fatal:\n\n{error_msg}")
        
        # Hancurkan root dan keluar
        root.destroy()
        sys.exit(1)

if __name__ == '__main__':
    main_entry()
