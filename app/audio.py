import threading, time
import pygame

class AudioEngine:
    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.Lock()
        self._break_mode = False
        self._break_thread = None
        self._stop_flag = False

    def play_once(self, path: str, interrupt: bool = True, volume: float = 1.0):
        if not path:
            return
        with self._lock:
            if interrupt:
                pygame.mixer.music.stop()
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

        # block sampai selesai (biar bel tidak ketumpuk)
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    def stop(self):
        with self._lock:
            pygame.mixer.music.stop()

    def start_break_playlist(self, files: list[str], shuffle: bool = True):
        if not files:
            return
        import random

        self._break_mode = True
        self._stop_flag = False

        def loop():
            idx = 0
            playlist = files[:]
            if shuffle:
                random.shuffle(playlist)

            while self._break_mode and not self._stop_flag:
                if idx >= len(playlist):
                    idx = 0
                    playlist = files[:]
                    if shuffle:
                        random.shuffle(playlist)

                self.play_once(playlist[idx], interrupt=False)
                idx += 1

        self._break_thread = threading.Thread(target=loop, daemon=True)
        self._break_thread.start()

    def stop_break_playlist(self):
        self._break_mode = False
        self._stop_flag = True
        self.stop()
