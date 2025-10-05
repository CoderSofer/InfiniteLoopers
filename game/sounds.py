import os
import pygame

class SoundBank:
    def __init__(self,  base_dir="./game/soundfiles", volume=0.9, enabled=True):
        self.base_dir = base_dir
        self.volume = float(volume)
        self.enabled = enabled
        self.sounds = {}

    def load(self, mapping=None):
        # mapping: optional dict of name->filename
        if mapping is None:
            mapping = {
                "BUY":      "buy2.wav",
                "CLICK":    "click1.wav",
                "PICK":     "pick2.wav",
                "HARVEST":  "harvest4.wav",
                # "PLANT":  "plant.wav",  # add if/when you have it
            }
            

        for name, file in mapping.items():
            path = os.path.join(self.base_dir, file)
            try:
                s = pygame.mixer.Sound(path)
                s.set_volume(self.volume)
                self.sounds[name] = s
            except Exception:
                # Missing file? Keep key so .play() is safe to call.
                self.sounds[name] = None


    def play(self, name):
        if not self.enabled:
            return
        s = self.sounds.get(name)
        if s:
            s.play()

    def set_volume(self, v):
        self.volume = max(0.0, min(1.0, float(v)))
        for s in self.sounds.values():
            if s:
                s.set_volume(self.volume)

    def toggle(self, on=None):
        # toggle or force on/off
        self.enabled = (not self.enabled) if on is None else bool(on)

