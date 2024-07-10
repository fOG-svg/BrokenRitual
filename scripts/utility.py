import pygame
import os
import sys
import random
import tkinter
from tkinter import filedialog
IMAGE_DIR = 'img/'


def load_assets(game):
    game.assets = {
        'exit': load_dir_images('tiles/exit'),
        'decor_green': load_dir_images('tiles/decor/green'),
        'decor_desert': load_dir_images('tiles/decor/desert'),
        'decor_brick': load_dir_images('tiles/decor/brick'),
        'decor_stone': load_dir_images('tiles/decor/stone'),
        'decor_ice': load_dir_images('tiles/decor/ice'),
        'decor_objects': load_dir_images('tiles/decor/objects'),
        'brick': load_dir_images('tiles/brick'),
        'desert': load_dir_images('tiles/desert'),
        'desert_brick': load_dir_images('tiles/desert_brick'),
        'desert_small_brick': load_dir_images('tiles/desert_small_brick'),
        'smooth_stone': load_dir_images('tiles/smooth_stone'),
        'stone': load_dir_images('tiles/stone'),
        'grass': load_dir_images('tiles/grass'),
        'ice': load_dir_images('tiles/ice'),
        'glass': load_dir_images('tiles/glass'),
        # Enemy IMAGES--------
        'flower/idle': Animation(load_dir_images(f'enemy/flower/idle'), duration=10),
        'flower_predatory/idle': Animation(load_dir_images(f'enemy/flower_predatory/idle'), duration=10),
        'ghost/idle': Animation(load_dir_images(f'enemy/ghost/idle'), duration=10),
        'ghost/run': Animation(load_dir_images(f'enemy/ghost/run'), duration=4),
        'goblin_heavy/idle': Animation(load_dir_images(f'enemy/goblin_heavy/idle'), duration=10),
        'goblin_heavy/run': Animation(load_dir_images(f'enemy/goblin_heavy/run'), duration=4),
        'goblin/idle': Animation(load_dir_images(f'enemy/goblin/idle'), duration=10),
        'goblin/run': Animation(load_dir_images(f'enemy/goblin/run'), duration=4),
        'goblin_mage/idle': Animation(load_dir_images(f'enemy/goblin_mage/idle'), duration=10),
        'goblin_mage/run': Animation(load_dir_images(f'enemy/goblin_mage/run'), duration=4),
        'goblin_medium/idle': Animation(load_dir_images(f'enemy/goblin_medium/idle'), duration=10),
        'goblin_medium/run': Animation(load_dir_images(f'enemy/goblin_medium/run'), duration=4),
        'goblin_warlord/idle': Animation(load_dir_images(f'enemy/goblin_warlord/idle'), duration=10),
        'goblin_warlord/run': Animation(load_dir_images(f'enemy/goblin_warlord/run'), duration=4),
        'lich/idle': Animation(load_dir_images(f'enemy/lich/idle'), duration=10),
        'lich/run': Animation(load_dir_images(f'enemy/lich/run'), duration=4),
        'mummy/idle': Animation(load_dir_images(f'enemy/mummy/idle'), duration=10),
        'mummy/run': Animation(load_dir_images(f'enemy/mummy/run'), duration=4),
        'rat/idle': Animation(load_dir_images(f'enemy/rat/idle'), duration=10),
        'rat/run': Animation(load_dir_images(f'enemy/rat/run'), duration=4),
        'rat_plague/idle': Animation(load_dir_images(f'enemy/rat_plague/idle'), duration=10),
        'rat_plague/run': Animation(load_dir_images(f'enemy/rat_plague/run'), duration=4),
        'slime/idle': Animation(load_dir_images(f'enemy/slime/idle'), duration=10),
        'slime/run': Animation(load_dir_images(f'enemy/slime/run'), duration=4),
        'zombie/idle': Animation(load_dir_images(f'enemy/zombie/idle'), duration=10),
        'zombie/run': Animation(load_dir_images(f'enemy/zombie/run'), duration=4),
        # Оружие----
        'magic_staff': load_image('weapons/magic_staff.png'),
        'bow': load_image('weapons/bow.png'),
        'dagger': load_image('weapons/dagger.png'),
        'scythe': load_image('weapons/scythe.png'),
        'shield': load_image('weapons/shield.png'),
        'shield_cooldown': load_image('weapons/shield_cooldown.png'),
        'spear': load_image('weapons/spear.png'),
        'sword': load_image('weapons/sword.png'),
        'axe': load_image('weapons/axe.png'),
        'unarmed': load_image('weapons/unarmed.png'),
        'sphere': load_image('weapons/sphere.png'),
        # Снаряды-----
        'arrow': load_image('projectiles/arrow.png'),
        'pfire_ball1': load_image('projectiles/pfire_ball.png'),
        'fire_ball': load_image('projectiles/fire_ball.png', color_key=(0, 0, 0)),
        'projectile': load_image('projectiles/projectile.png', color_key=(0, 0, 0)),
        'magic_missle': load_image('projectiles/magic_missle.png'),
        'wave': load_image('projectiles/wave.png'),
        # Предметы-----
        'iexit/idle': Animation(load_dir_images('items/exit/idle'), duration=10),
        'coin/idle': Animation(load_dir_images('items/coin/idle'), duration=10),
        'manap/idle': Animation(load_dir_images('items/manap/idle'), duration=10),
        'lifep/idle': Animation(load_dir_images('items/lifep/idle'), duration=10),
        'endurancep/idle': Animation(load_dir_images(f'items/endurancep/idle'), duration=10),
        # Квестовые предметы
        'brick_full/idle': Animation(load_dir_images('quests/brick/brick_full/idle'), duration=10),
        'brick_l/idle': Animation(load_dir_images('quests/brick/brick_l/idle'), duration=10),
        'brick_r/idle': Animation(load_dir_images('quests/brick/brick_r/idle'), duration=10),
        'desert_full/idle': Animation(load_dir_images('quests/desert/desert_full/idle'), duration=10),
        'desert_l/idle': Animation(load_dir_images('quests/desert/desert_l/idle'), duration=10),
        'desert_r/idle': Animation(load_dir_images('quests/desert/desert_r/idle'), duration=10),
        'green_full/idle': Animation(load_dir_images('quests/green/green_full/idle'), duration=10),
        'green_l/idle': Animation(load_dir_images('quests/green/green_l/idle'), duration=10),
        'green_r/idle': Animation(load_dir_images('quests/green/green_r/idle'), duration=10),
        'stone_full/idle': Animation(load_dir_images('quests/stone/stone_full/idle'), duration=10),
        'stone_l/idle': Animation(load_dir_images('quests/stone/stone_l/idle'), duration=10),
        'stone_r/idle': Animation(load_dir_images('quests/stone/stone_r/idle'), duration=10),
        # SpellBook----
        'force_bolt': [load_image('spells/force_bolt_ready.png'), load_image('spells/force_bolt_notready.png')],
        'ice_armor': [load_image('spells/ice_armor_ready.png'), load_image('spells/ice_armor_notready.png')],
        'thunder_strike': [load_image('spells/thunder_strike_ready.png'),
                           load_image('spells/thunder_strike_notready.png')],
        'pfire_ball': [load_image('spells/fire_ball_ready.png'), load_image('spells/fire_ball_notready.png')],
        # HUD---------
        'hud': (
            load_image('ui/hud/left.png'), load_image('ui/hud/mid_empty.png'),
            load_image('ui/hud/mid_endurance.png'),
            load_image('ui/hud/mid_life.png'), load_image('ui/hud/mid_mana.png'),
            load_image('ui/hud/right_life.png'),
            load_image('ui/hud/right_mana.png'), load_image('ui/hud/right_endurance.png')),
        'enemy_life': load_image('ui/enemy_life.png'),
        'score_bar': load_image('ui/score_bar.png'),
        # F1-----------
        'mage_info': load_image('info/Mage.png'),
        'fighter_info': load_image('info/Fighter.png'),
        'knight_info': load_image('info/Knight.png'),
        'ninja_info': load_image('info/Ninja.png'),
        # PLAYER-------
        'player/idle': Animation(load_dir_images(f'characters/{0}/idle'), duration=10),
        'player/run': Animation(load_dir_images(f'characters/{0}/run'), duration=4),
        'player/jump': Animation(load_dir_images(f'characters/{0}/jump'), duration=4),
        'player/wall_slide': Animation(load_dir_images(f'characters/{0}/slide'), duration=4),
        'clouds': load_dir_images('bd/paralax/clouds'),
        'particle/leaf': Animation(load_dir_images('particles/leaf', color_key=(0, 0, 0)), duration=15,
                                   looped=False),
        'particle/particle': Animation(load_dir_images('particles/particle', color_key=(0, 0, 0)), duration=6,
                                       looped=False),
        'particle/bloody': Animation(load_dir_images('particles/bloody'), duration=6,
                                     looped=False),
        'imFighter': load_image('ui/btFighter0.png'),
        'imKnight': load_image('ui/btKnight0.png'),
        'imMage': load_image('ui/btMage0.png'),
        'imNinja': load_image('ui/btNinja0.png'),
        'imTitle': load_image('pano/Title_Castle.png'),
        'imDeadScreen': load_image('pano/imDeadScreen.jpg'),
        'imHeroTitle': load_image('pano/Title_Castle_Cloud.png'),
        'imSlider': load_dir_images('ui/slider_bar'),
        'imResume': load_image('ui/btResume0.png'),
        'imBack': load_image('ui/btBack0.png'),
        'imHeroHall': load_image('ui/btHeroHall0.png'),
        'imNewGame': load_image('ui/btNewGame0.png'),
        'imExit': load_image('ui/btExit0.png'),
        'imOptions': load_image('ui/btOptions0.png'),
        'imMusic': load_image('ui/lbMusic.png'),
        'imAmbience': load_image('ui/lbAmbience.png'),
        'imEffects': load_image('ui/lbEffects.png'),
        'imWall': load_image('tiles/wall.png'),
        'imBackGround': load_image('bd/paralax/green0.png', (77, 112, 140)),
        'imStone': load_image('bd/paralax/stone0.png'),
        'imDesert': load_image('bd/paralax/desert0.png'),
        'imWin': load_image('bd/paralax/win.png')
    }

def textinput(game, surface):
    w, h = surface.get_size()
    font = pygame.font.Font('Blackcraft.ttf', 50)
    text = ''
    while True:
        text_image = font.render(text, True, 'black')
        text_rect = text_image.get_rect()
        text_rect.topleft = (w / 6, h / 4)
        text_rect.width = max(100, text_image.get_width())
        surface.blit(pygame.transform.scale(game.assets['imDeadScreen'], surface.get_size()), (0, 0))
        draw_text(surface, 'Введите имя героя:', font, (3*surface.get_size()[0]/4, 0))
        surface.blit(text_image, (w / 6, h / 4))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 10:
                        text += event.unicode
        pygame.display.update()
        game.mainClock.tick(60)

def draw_text(surf, text, font, pos=(0, 0), color='black'):
    img = font.render(text, True, color)
    surf.blit(img, (pos[0] - img.get_width() - 9, pos[1]))


def save_map():
    save_dlg = tkinter.Tk()
    save_dlg.title('Сохранение уровня')
    app_w = 500
    app_h = 100
    sw = save_dlg.winfo_screenwidth()
    sh = save_dlg.winfo_screenheight()
    x = int((sw / 2) - (app_w / 2))
    y = int((sh / 2) - (app_h / 2))
    save_dlg.geometry(f'{app_w}x{app_h}+{x}+{y}')
    save_dlg.filename = filedialog.asksaveasfilename(initialdir=sys.path[0]+r'\maps', title='Выберите каталог для сохранения и введите имя',
                                                   filetypes=(('Файл-json', '*.json'),))
    tkinter.Label(save_dlg, text='Выбран файл:\n' + save_dlg.filename).pack()
    if save_dlg.filename == '':
        filejson = 'map.json'
    else:
        if '.json' == save_dlg.filename[-5:]:
            filejson = save_dlg.filename
        else:
            filejson = save_dlg.filename + '.json'
    save_dlg.destroy()
    return filejson


def load_map():
    load_dlg = tkinter.Tk()
    load_dlg.title('Загрузка уровня')
    app_w = 500
    app_h = 100
    sw = load_dlg.winfo_screenwidth()
    sh = load_dlg.winfo_screenheight()
    x = int((sw / 2) - (app_w / 2))
    y = int((sh / 2) - (app_h / 2))
    load_dlg.geometry(f'{app_w}x{app_h}+{x}+{y}')
    load_dlg.filename = filedialog.askopenfilename(initialdir=sys.path[0]+r'\maps', title='Выберите файл для открытия',
                                                   filetypes=(('Файл-json', '*.json'),))
    tkinter.Label(load_dlg, text='Выбран файл:\n' + load_dlg.filename).pack()
    if load_dlg.filename == '':
        filejson = 'maps/map.json'
    else:
        filejson = load_dlg.filename
    load_dlg.destroy()
    return filejson

def load_image(path, color_key=None):
    full_path = os.path.join(IMAGE_DIR + path)
    if not os.path.isfile(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        sys.exit()
    image = pygame.image.load(full_path).convert_alpha()
    image.set_colorkey(color_key)
    return image


def load_dir_images(path, color_key=None):
    images = []
    for im in os.listdir(IMAGE_DIR + path):
        images.append(load_image(path + '/' + im, color_key=color_key))
    return images


class Animation:
    def __init__(self, images, duration=5, looped=True):
        self.frame = 0
        self.images = images
        self.looped = looped
        self.duration = duration
        self.ended = False

    def copy(self):
        return Animation(self.images, self.duration, self.looped)

    def shot(self):
        return self.images[int(self.frame / self.duration)]

    def update(self):
        if self.looped:
            self.frame = (self.frame + 1) % (len(self.images) * self.duration)
        else:
            self.frame = min(len(self.images) * self.duration - 1, self.frame + 1)
            if self.frame >= len(self.images) * self.duration - 1:
                self.ended = True


class TextFrame:
    def __init__(self, text, font, pos=(0, 0), duration=50, color=(0, 0, 0)):
        self.font = font
        self.text = text
        self.color = color
        self.pos = list(pos)
        self.duration = duration

    def update(self):
        kill = False
        self.duration = max(0, self.duration - 1)
        self.pos[0] += random.random() * 4 - 2
        self.pos[1] -= 0.5
        if not self.duration:
            kill = True
        return kill

    def render(self, surface, offset=(0, 0)):
        textobj = self.font.render(self.text, 1, self.color)
        textrect = textobj.get_rect()
        textrect.topleft = self.pos
        surface.blit(textobj, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
