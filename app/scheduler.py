from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
import os

def _parse_hhmm(s: str):
    h, m = s.split(":")
    return int(h), int(m)

def list_audio_files(folder: str) -> list[str]:
    if not folder or not os.path.isdir(folder):
        return []
    exts = {".mp3", ".wav", ".ogg"}
    out = []
    for name in os.listdir(folder):
        p = Path(folder) / name
        if p.is_file() and p.suffix.lower() in exts:
            out.append(str(p))
    return sorted(out)

class BellScheduler:
    def __init__(self, cfg: dict, audio_engine):
        self.cfg = cfg
        self.audio = audio_engine
        self.sched = BackgroundScheduler(timezone=None)

    def start(self):
        self._register_jobs()
        self.sched.start()

    def shutdown(self):
        self.sched.shutdown(wait=False)

    def reload(self, cfg: dict):
        self.cfg = cfg
        self.sched.remove_all_jobs()
        self._register_jobs()

    def _register_jobs(self):
        break_cfg = self.cfg.get("break_music", {})
        break_files = list_audio_files(break_cfg.get("folder", ""))

        for ev in self.cfg.get("events", []):
            label = ev.get("label", ev.get("id", "event"))
            start = ev.get("start")
            end = ev.get("end")
            typ = ev.get("type")

            # --- Jadwal Mulai ---
            if start and ":" in start:
                try:
                    h, m = _parse_hhmm(start)
                    def on_start(ev=ev, typ=typ):
                        # Bunyi Audio Start
                        if ev.get("audio_start"):
                            self.audio.play_once(ev["audio_start"], interrupt=True)
                        
                        # Mulai Playlist Istirahat
                        if typ == "break" and break_cfg.get("enabled", True):
                            self.audio.start_break_playlist(break_files, shuffle=break_cfg.get("shuffle", True))

                    self.sched.add_job(on_start, CronTrigger(hour=h, minute=m), id=f"{ev['id']}_start", replace_existing=True)
                except ValueError:
                    pass # Format jam salah, skip

            # --- Jadwal Selesai ---
            # Cek jika end valid (ada titik dua), abaikan jika "-" atau kosong
            if end and ":" in end:
                try:
                    h, m = _parse_hhmm(end)
                    def on_end(ev=ev, typ=typ):
                        # Stop Playlist Istirahat
                        if typ == "break":
                            self.audio.stop_break_playlist()
                        
                        # Bunyi Audio End
                        if ev.get("audio_end"):
                            self.audio.play_once(ev["audio_end"], interrupt=True)

                    self.sched.add_job(on_end, CronTrigger(hour=h, minute=m), id=f"{ev['id']}_end", replace_existing=True)
                except ValueError:
                    pass
