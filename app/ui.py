import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .storage import save_config, import_audio_to_app, get_data_dir
import os

def _basename(p: str) -> str:
    import os
    return os.path.basename(p) if p else ""

class AppUI:
    def __init__(self, root, cfg: dict, on_config_changed):
        self.root = root
        self.cfg = cfg
        self.on_config_changed = on_config_changed

        root.title("Bell SMKN 1 Maja - Configurator")
        root.geometry("1000x600")

        # --- Tabel Jadwal ---
        cols = ("label","start","end","a_start","a_end")
        self.tree = ttk.Treeview(root, columns=cols, show="headings")
        
        self.tree.heading("label", text="Nama Kegiatan")
        self.tree.heading("start", text="Mulai")
        self.tree.heading("end", text="Selesai")
        self.tree.heading("a_start", text="Audio Mulai")
        self.tree.heading("a_end", text="Audio Selesai")

        self.tree.column("label", width=200)
        self.tree.column("start", width=80, anchor="center")
        self.tree.column("end", width=80, anchor="center")
        self.tree.column("a_start", width=250)
        self.tree.column("a_end", width=250)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Tombol Aksi ---
        btns = tk.Frame(root)
        btns.pack(fill="x", padx=10, pady=10)

        tk.Button(btns, text="Edit Waktu", command=self.edit_time, bg="#e1f5fe").pack(side="left", padx=5)
        tk.Button(btns, text="Set Audio Mulai", command=lambda: self.set_audio("audio_start"), bg="#e8f5e9").pack(side="left", padx=5)
        tk.Button(btns, text="Set Audio Selesai", command=lambda: self.set_audio("audio_end"), bg="#ffebee").pack(side="left", padx=5)

        tk.Frame(btns, width=30).pack(side="left") # Spacer

        tk.Button(btns, text="Folder Musik Istirahat", command=self.set_break_folder).pack(side="left", padx=5)
        tk.Button(btns, text="Buka Folder Audio", command=self.open_audio_folder).pack(side="left", padx=5)

        tk.Button(btns, text="SIMPAN & TERAPKAN", command=self.save, bg="#4caf50", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=5)

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for ev in self.cfg.get("events", []):
            self.tree.insert("", "end", iid=ev["id"], values=(
                ev["label"],
                ev["start"],
                ev["end"],
                _basename(ev.get("audio_start","")),
                _basename(ev.get("audio_end",""))
            ))

    def _get_selected_event(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Pilih Baris", "Silakan klik salah satu jadwal di tabel dulu.")
            return None
        ev_id = sel[0]
        # Cari event di list
        for ev in self.cfg["events"]:
            if ev["id"] == ev_id:
                return ev
        return None

    def edit_time(self):
        ev = self._get_selected_event()
        if not ev: return

        w = tk.Toplevel(self.root)
        w.title(f"Edit: {ev['label']}")
        w.geometry("300x180")

        tk.Label(w, text="Jam Mulai (HH:MM):").pack(pady=(15,5))
        e1 = tk.Entry(w, justify="center"); e1.insert(0, ev["start"]); e1.pack()

        tk.Label(w, text="Jam Selesai (HH:MM) / '-' jika tidak ada:").pack(pady=(10,5))
        e2 = tk.Entry(w, justify="center"); e2.insert(0, ev["end"]); e2.pack()

        def ok():
            ev["start"] = e1.get().strip()
            ev["end"] = e2.get().strip()
            self.refresh()
            w.destroy()

        tk.Button(w, text="OK Update", command=ok, width=15).pack(pady=20)

    def set_audio(self, key):
        ev = self._get_selected_event()
        if not ev: return
        
        # Validasi: Jangan set audio selesai untuk item yg end="-"
        if key == "audio_end" and ev["end"] == "-":
            messagebox.showinfo("Info", "Kegiatan ini tidak memiliki jam selesai, jadi tidak butuh audio selesai.")
            return

        path = filedialog.askopenfilename(filetypes=[("Audio File","*.mp3 *.wav *.ogg")])
        if not path: return
        
        copied = import_audio_to_app(path)
        ev[key] = copied
        self.refresh()

    def set_break_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.cfg.setdefault("break_music", {})
        self.cfg["break_music"]["folder"] = folder
        messagebox.showinfo("Sukses", "Folder musik istirahat telah dipilih.")

    def open_audio_folder(self):
        folder = get_data_dir() / "audio"
        os.startfile(folder)

    def save(self):
        save_config(self.cfg)
        self.on_config_changed(self.cfg)
        messagebox.showinfo("Berhasil", "Jadwal berhasil disimpan dan diterapkan!")
