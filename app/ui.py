import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .storage import save_config, import_audio_to_app

class AppUI:
    def __init__(self, root, cfg: dict, on_config_changed):
        self.root = root
        self.cfg = cfg
        self.on_config_changed = on_config_changed

        root.title("AutoBell - Bel Sekolah Otomatis")
        root.geometry("980x540")

        self.tree = ttk.Treeview(root, columns=("label","type","start","end","a_start","a_end"), show="headings")
        for c, t in [("label","Label"),("type","Type"),("start","Mulai"),("end","Selesai"),("a_start","Audio Mulai"),("a_end","Audio Selesai")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=140 if c in ("label","a_start","a_end") else 90)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btns = tk.Frame(root); btns.pack(fill="x", padx=10, pady=6)

        tk.Button(btns, text="Edit waktu", command=self.edit_time).pack(side="left")
        tk.Button(btns, text="Set audio mulai", command=lambda: self.set_audio("audio_start")).pack(side="left", padx=6)
        tk.Button(btns, text="Set audio selesai", command=lambda: self.set_audio("audio_end")).pack(side="left")

        tk.Button(btns, text="Indonesia Raya (10:00)", command=self.set_indonesia_raya).pack(side="left", padx=18)
        tk.Button(btns, text="Folder musik istirahat", command=self.set_break_folder).pack(side="left")

        tk.Button(btns, text="Simpan", command=self.save).pack(side="right")

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ev in self.cfg["events"]:
            self.tree.insert("", "end", iid=ev["id"], values=(
                ev["label"], ev["type"], ev["start"], ev["end"],
                _basename(ev.get("audio_start","")),
                _basename(ev.get("audio_end",""))
            ))

    def _get_selected_event(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Pilih dulu", "Pilih salah satu baris jadwal.")
            return None
        ev_id = sel[0]
        for ev in self.cfg["events"]:
            if ev["id"] == ev_id:
                return ev
        return None

    def edit_time(self):
        ev = self._get_selected_event()
        if not ev: return

        w = tk.Toplevel(self.root); w.title("Edit waktu")
        tk.Label(w, text=f"{ev['label']}").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        tk.Label(w, text="Mulai (HH:MM)").grid(row=1, column=0, sticky="w", padx=10)
        e1 = tk.Entry(w); e1.insert(0, ev["start"]); e1.grid(row=1, column=1, padx=10, pady=6)

        tk.Label(w, text="Selesai (HH:MM)").grid(row=2, column=0, sticky="w", padx=10)
        e2 = tk.Entry(w); e2.insert(0, ev["end"]); e2.grid(row=2, column=1, padx=10, pady=6)

        def ok():
            ev["start"] = e1.get().strip()
            ev["end"] = e2.get().strip()
            w.destroy()
            self.refresh()

        tk.Button(w, text="OK", command=ok).grid(row=3, column=0, columnspan=2, pady=10)

    def set_audio(self, key):
        ev = self._get_selected_event()
        if not ev: return
        path = filedialog.askopenfilename(filetypes=[("Audio","*.mp3 *.wav *.ogg")])
        if not path: return
        copied = import_audio_to_app(path)
        ev[key] = copied
        self.refresh()

    def set_break_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.cfg.setdefault("break_music", {})
        self.cfg["break_music"]["folder"] = folder
        messagebox.showinfo("OK", "Folder musik istirahat diset. Simpan untuk menerapkan.")

    def set_indonesia_raya(self):
        path = filedialog.askopenfilename(filetypes=[("Audio","*.mp3 *.wav *.ogg")])
        if not path: return
        copied = import_audio_to_app(path)
        self.cfg.setdefault("indonesia_raya", {})
        self.cfg["indonesia_raya"]["time"] = "10:00"
        self.cfg["indonesia_raya"]["audio"] = copied
        messagebox.showinfo("OK", "Indonesia Raya diset jam 10:00. Simpan untuk menerapkan.")

    def save(self):
        save_config(self.cfg)
        self.on_config_changed(self.cfg)
        messagebox.showinfo("Tersimpan", "Konfigurasi tersimpan dan jadwal diterapkan.")

def _basename(p: str) -> str:
    import os
    return os.path.basename(p) if p else ""
