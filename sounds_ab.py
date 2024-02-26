import pygame as pg
import pygame.mixer


pg.mixer.init()
SFX_volume = 0.3
music_volume = 0.5
#pg.mixer.stop()

def sound_effect(effect: str):
    sound_effect = pygame.mixer.Sound('./ab_sounds/' + effect + '.wav')
    sound_effect.set_volume(SFX_volume)
    sound_effect.play()

def play_music_effect(location: str):
    music_effect = pygame.mixer.Sound('./ab_sounds/' + location + '.wav')
    music_effect.set_volume(music_volume)
    if not pg.mixer.get_busy():
        music_effect.play(loops=-1)

def set_sfx_volume(volume: float):
    global SFX_volume
    SFX_volume = volume

def set_music_volume(volume: float):
    global music_volume
    music_volume = volume

def get_sfx_volume() -> float:
    return SFX_volume

def get_music_volume() -> float:
    return music_volume

def menu_effect():
    pass
