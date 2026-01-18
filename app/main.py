import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
import sys
import os

# Library tambahan untuk Tray Icon
from PIL import Image
import pystray

from .storage import load_or_init_config
from .audio import AudioEngine
from .scheduler import BellScheduler
from .ui import AppUI

# --- Helper Path ---
def resource_path(rel: str) -> Path:
    # Fungsi ini penting agar aplikasi bisa menemukan file aset (gambar/config)
    # baik saat dijalankan sebagai script python biasa maupun saat sudah jadi EXE.
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / rel
    return Path(os.path.abspath(".")) / rel

class BellApp:
    def __init__(self):
        # 1. Init Core System (Config, Audio, Scheduler)
        # Load config default dari aset jika user belum punya config
        self.cfg = load_or_init_config(resource_path("assets/config_default.json"))
        
        self.audio = AudioEngine()
        self.bell = BellScheduler(self.cfg, self.audio)
        self.bell.start() # Mulai scheduler di background

        # 2. Init GUI (Tkinter)
        self.root = tk.Tk()
        # Saat config berubah di UI, reload scheduler agar jadwal update realtime
        self.ui = AppUI(self.root, self.cfg, on_config_changed=lambda new_cfg: self.bell.reload(new_cfg))
        
        # Override tombol Close (X) di pojok kanan atas jendela
        # Agar aplikasi tidak mati total, tapi cuma sembunyi ke tray.
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # 3. Init System Tray
        self.tray_icon = None
        self.init_tray()

    def init_tray(self):
        # Cari file gambar ikon
        icon_path = resource_path("assets/app_icon.png")
        
        # Jika file ikon ketemu, pakai. Jika tidak, pakai kotak merah (darurat).
        if icon_path.exists():
            image = Image.open(icon_path)
        else:
            # Fallback icon: Kotak merah 64x64
            image = Image.new('RGB', (64, 64), color=(255, 0, 0))

        # Buat Menu Klik Kanan pada Ikon Tray
        menu = pystray.Menu(
            pystray.MenuItem("Buka Aplikasi", self.show_window, default=True),
            pystray.MenuItem("Keluar (Matikan Bel)", self.quit_app)
        )

        # Buat objek ikon tray (tapi belum dijalankan)
        self.tray_icon = pystray.Icon("AutoBell", image, "Bell SMKN 1 Maja", menu)

    def run_tray(self):
        # Menjalankan loop ikon tray. Fungsi ini blocking, jadi harus di thread terpisah.
        self.tray_icon.run()

    def hide_window(self):
        # Sembunyikan jendela GUI
        self.root.withdraw() 
        
        # Kirim notifikasi balon (Toast) agar user tahu aplikasi masih hidup
        if self.tray_icon:
            self.tray_icon.notify("Aplikasi berjalan di latar belakang.", "Bell SMKN 1 Maja")

    def show_window(self, icon=None, item=None):
        # Tampilkan kembali jendela GUI
        self.root.after(0, self.root.deiconify) 
        self.root.after(0, self.root.lift) # Angkat ke paling depan layar

    def quit_app(self, icon=None, item=None):
        # Fungsi untuk benar-benar menutup aplikasi (Kill process)
        
        # 1. Matikan Scheduler & Audio
        self.bell.shutdown()
        self.audio.stop()
        
        # 2. Matikan Tray Icon
        self.tray_icon.stop()
        
        # 3. Matikan GUI Tkinter
        self.root.quit()
        
        # 4. Paksa berhenti proses Python
        sys.exit(0)

    def start(self):
        # Langkah 1: Jalankan Tray Icon di thread terpisah (daemon=True agar mati jika program utama mati)
        tray_thread = threading.Thread(target=self.run_tray, daemon=True)
        tray_thread.start()
        
        # Langkah 2: Jalankan loop utama GUI (Main Thread)
        # Tkinter wajib jalan di main thread.
        self.root.mainloop()

def main():
    app = BellApp()
    app.start()

if __name__ == "__main__":
    main()
