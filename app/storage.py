import json
import os
import shutil
import time
from pathlib import Path

APP_NAME = "AutoBell"

def get_data_dir() -> Path:
    """
    Mengembalikan path folder penyimpanan data (config & audio).
    Menggunakan folder lokal 'data_store' di dalam project (Mode Portable)
    agar mudah dicek dan tidak tersasar ke AppData C:.
    """
    # Menggunakan path relatif terhadap lokasi script yang dijalankan
    base = Path(".").resolve() / "data_store"
    
    d = base
    d.mkdir(parents=True, exist_ok=True)
    (d / "audio").mkdir(parents=True, exist_ok=True)
    return d

def get_config_path() -> Path:
    return get_data_dir() / "config.json"

def load_or_init_config(default_config_path: Path) -> dict:
    cfg_path = get_config_path()
    if not cfg_path.exists():
        # Jika belum ada config user, copy dari default aset
        try:
            shutil.copy2(default_config_path, cfg_path)
        except Exception as e:
            print(f"[WARN] Gagal init config: {e}")
            # Return kosong dulu jika gagal, nanti akan disave ulang
            return json.loads(default_config_path.read_text(encoding="utf-8"))
            
    return json.loads(cfg_path.read_text(encoding="utf-8"))

def save_config(cfg: dict) -> None:
    try:
        get_config_path().write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan config: {e}")

def import_audio_to_app(file_path: str) -> str:
    """
    Copy file ke folder audio aplikasi agar path tidak putus saat dipindah.
    Menangani kasus jika file sudah ada atau sedang terkunci (Permission Denied).
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    src = Path(file_path)
    dst_folder = get_data_dir() / "audio"
    dst = dst_folder / src.name

    # 1. Jika file sumber dan tujuan sama (user pilih file yg sudah ada di folder data)
    try:
        if src.resolve() == dst.resolve():
            return str(dst)
    except OSError:
        pass # Lanjut saja jika resolve gagal

    # 2. Coba copy dengan penanganan error
    try:
        shutil.copy2(src, dst)
    except PermissionError:
        # Jika gagal overwrite (file sedang dipakai/locked), buat nama baru pakai timestamp
        # Contoh: bel1.wav -> bel1_170543221.wav
        timestamp = int(time.time())
        new_name = f"{src.stem}_{timestamp}{src.suffix}"
        dst = dst_folder / new_name
        
        try:
            shutil.copy2(src, dst)
            print(f"[INFO] File terkunci, disalin sebagai: {new_name}")
        except Exception as e:
            print(f"[ERROR] Gagal copy file audio alternatif: {e}")
            # Jika tetap gagal, pakai file aslinya saja (tanpa copy)
            return str(src)
            
    except Exception as e:
        print(f"[ERROR] Gagal copy file audio: {e}")
        return str(src)

    return str(dst)
