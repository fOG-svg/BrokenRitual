import pygame


def load_sounds(game):
    game.sfx = {
        'jump': pygame.mixer.Sound('sounds/sfx/Jump.wav'),
        'attack': pygame.mixer.Sound('sounds/sfx/Attack.wav'),
        'axe_attack': pygame.mixer.Sound('sounds/sfx/aAttack.wav'),
        'unarmed_attack': pygame.mixer.Sound('sounds/sfx/uAttack.wav'),
        'scythe_attack': pygame.mixer.Sound('sounds/sfx/scAttack.wav'),
        'sword_attack': pygame.mixer.Sound('sounds/sfx/sAttack.wav'),
        'dagger_attack': pygame.mixer.Sound('sounds/sfx/dAttack.wav'),
        'bow_attack': pygame.mixer.Sound('sounds/sfx/bAttack.wav'),
        'spear_attack': pygame.mixer.Sound('sounds/sfx/spAttack.wav'),
        'shield_attack': pygame.mixer.Sound('sounds/sfx/shAttack.wav'),
        'fireball_attack': pygame.mixer.Sound('sounds/sfx/fireballAttack.wav'),
        'mage_attack': pygame.mixer.Sound('sounds/sfx/mageAttack.wav'),
        'weapon_block': pygame.mixer.Sound('sounds/sfx/weaponBlock.wav'),
        'shield_block': pygame.mixer.Sound('sounds/sfx/shieldBlock.mp3'),
        'take_up_shield': pygame.mixer.Sound('sounds/sfx/take_up_shield.mp3'),
        'ice_block': pygame.mixer.Sound('sounds/sfx/iceCracking.wav'),
        'ice_armor': pygame.mixer.Sound('sounds/sfx/iceArmor.mp3'),
        'thunder_strike': pygame.mixer.Sound('sounds/sfx/thunder_strike.mp3'),
        'hit': pygame.mixer.Sound('sounds/sfx/Hit.wav'),
        'ambience': pygame.mixer.Sound('sounds/sfx/Ambience_Birds.wav'),
        'stone12': pygame.mixer.Sound('sounds/sfx/Ambience_Vent.wav'),
        'brick12': pygame.mixer.Sound('sounds/sfx/Ambience_Vent.wav'),
        'desert12': pygame.mixer.Sound('sounds/sfx/Ambience_Wind.wav'),
        'magic_missle': pygame.mixer.Sound('sounds/sfx/Magic_missle.wav'),
        'pickup': pygame.mixer.Sound('sounds/sfx/Pickup.wav'),
        'powerup': pygame.mixer.Sound('sounds/sfx/Powerup.wav'),
        'fall': pygame.mixer.Sound('sounds/sfx/Fall.wav'),
        'lifep': pygame.mixer.Sound('sounds/sfx/potion.mp3'),
        'manap': pygame.mixer.Sound('sounds/sfx/potion.mp3'),
        'endurancep': pygame.mixer.Sound('sounds/sfx/potion.mp3'),
        'questitem': pygame.mixer.Sound('sounds/sfx/questItem.wav'),
        'exit': pygame.mixer.Sound('sounds/sfx/exit.wav')
    }


def save_sound_volume(game):
    pygame.mixer.music.set_volume(game.volumes[game.music_volume])
    game.sfx['ambience'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['stone12'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['brick12'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['desert12'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['jump'].set_volume(game.volumes[game.sounds])
    game.sfx['unarmed_attack'].set_volume(game.volumes[max(0, game.sounds - 1)])
    game.sfx['attack'].set_volume(game.volumes[max(0, game.sounds - 1)])
    game.sfx['scythe_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['axe_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['sword_attack'].set_volume(game.volumes[max(0, game.sounds - 1)])
    game.sfx['dagger_attack'].set_volume(game.volumes[max(0, game.sounds - 1)])
    game.sfx['bow_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['spear_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['shield_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['fireball_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['ice_armor'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['thunder_strike'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['mage_attack'].set_volume(game.volumes[min(10, game.sounds + 1)])
    game.sfx['weapon_block'].set_volume(game.volumes[game.sounds])
    game.sfx['shield_block'].set_volume(game.volumes[game.sounds])
    game.sfx['hit'].set_volume(game.volumes[game.sounds])
    game.sfx['magic_missle'].set_volume(game.volumes[game.sounds])
    game.sfx['pickup'].set_volume(game.volumes[min(10, game.sounds + 2)])
    game.sfx['powerup'].set_volume(game.volumes[min(10, game.sounds + 2)])
    game.sfx['fall'].set_volume(game.volumes[min(10, game.sounds + 3)])
    game.sfx['lifep'].set_volume(game.volumes[min(10, game.sounds + 3)])
    game.sfx['manap'].set_volume(game.volumes[min(10, game.sounds + 3)])
    game.sfx['endurancep'].set_volume(game.volumes[min(10, game.sounds + 3)])
    game.sfx['questitem'].set_volume(game.volumes[min(10, game.sounds + 3)])
    game.sfx['exit'].set_volume(game.volumes[min(10, game.sounds + 3)])
    settings = open('settings.txt', mode='w')
    print(f'music {game.music_volume}', file=settings)
    print(f"ambience {game.ambience_volume}", file=settings)
    print(f"sounds {game.sounds}", file=settings)
    settings.close()


def load_sound_volume(game):
    game.volumes = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    settings = open('settings.txt', mode='r')
    sett = [i.split() for i in settings.readlines()]
    game.music_volume = int(sett[0][1])
    pygame.mixer.music.set_volume(game.volumes[game.music_volume])
    game.ambience_volume = int(sett[1][1])
    game.sfx['ambience'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['stone12'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['brick12'].set_volume(game.volumes[game.ambience_volume])
    game.sfx['desert12'].set_volume(game.volumes[game.ambience_volume])
    game.sounds = int(sett[2][1])
    game.sfx['jump'].set_volume(game.volumes[game.sounds])
    game.sfx['unarmed_attack'].set_volume(game.volumes[max(0, game.sounds)])
    game.sfx['attack'].set_volume(game.volumes[max(0, game.sounds)])
    game.sfx['scythe_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['axe_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['sword_attack'].set_volume(game.volumes[max(0, game.sounds)])
    game.sfx['dagger_attack'].set_volume(game.volumes[max(0, game.sounds)])
    game.sfx['bow_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['spear_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['shield_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['fireball_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['ice_armor'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['thunder_strike'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['mage_attack'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['weapon_block'].set_volume(game.volumes[game.sounds])
    game.sfx['shield_block'].set_volume(game.volumes[game.sounds])
    game.sfx['hit'].set_volume(game.volumes[game.sounds])
    game.sfx['magic_missle'].set_volume(game.volumes[game.sounds])
    game.sfx['pickup'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['powerup'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['fall'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['lifep'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['manap'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['endurancep'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['questitem'].set_volume(game.volumes[min(10, game.sounds)])
    game.sfx['exit'].set_volume(game.volumes[min(10, game.sounds)])
    settings.close()
