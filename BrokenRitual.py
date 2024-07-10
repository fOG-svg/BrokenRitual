import math
import scripts.cButton as cButton
import scripts.cSlider as cSlider
from scripts.utility import *
from scripts.paralax import Clouds
from scripts.entities import Item, Fighter, Knight, Mage, Ninja, Zombie, Lich, Ghost, Slime, Flower, FlowerPredatory, \
    Goblin, \
    GoblinHeavy, \
    GoblinMedium, GoblinMage, GoblinWarlord, Mummy, Rat, RatPlague
from scripts.tilemap import Tilemap
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.dropmanager import drop_item, use_item
from scripts.soundmanager import load_sounds, load_sound_volume, save_sound_volume

# CONSTANTS
FPS = 80
WIDTH = 640
HW = WIDTH / 2
HEIGHT = 480
HH = HEIGHT / 2
SCALE = 1
CLASSES = 1


# -------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Broken ritual')
        self.mainClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        pygame.display.set_icon(load_image('icons/icon.png'))
        self.display = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.outlines = pygame.Surface((WIDTH, HEIGHT))
        self.paused_game = True
        self.movementX = [False, False]
        self.movementY = [False, False]
        self.game_state = 'main_menu'
        self.choose = 0
        self.score = 0
        self.cursor = 1
        self.help = False
        self.running = True
        self.cursors = [pygame.cursors.Cursor((4, 0), load_image('ui/cursor.png').convert_alpha()),
                        pygame.cursors.Cursor((0, 0), load_image('ui/cursor_click.png').convert_alpha())]
        pygame.mouse.set_cursor(self.cursors[self.cursor])
        # IMAGES
        load_assets(self)
        # Прозрачность для слизи
        for im in self.assets['slime/idle'].images:
            im.set_alpha(50)
        for im in self.assets['slime/run'].images:
            im.set_alpha(50)
        # Прозрачность для призрака
        for im in self.assets['ghost/idle'].images:
            im.set_alpha(30)
        for im in self.assets['ghost/run'].images:
            im.set_alpha(50)
        # Звуковые настройки
        load_sounds(self)
        load_sound_volume(self)
        # ---------------------
        self.clouds = Clouds(self.assets['clouds'])
        self.tilemap = Tilemap(self)
        self.display_shake = 0
        self.level = 'green1'

    def options_menu(self):
        self.paused_game = True
        slMusic = cSlider.Slider(self.assets['imSlider'],
                                 self.display.get_width() / 2,
                                 self.display.get_height() / 2 - 2 * self.assets['imBack'].get_height() * SCALE,
                                 self.music_volume)
        slAmbience = cSlider.Slider(self.assets['imSlider'],
                                    self.display.get_width() / 2,
                                    self.display.get_height() / 2 - self.assets['imBack'].get_height() * SCALE,
                                    self.ambience_volume)
        slEffects = cSlider.Slider(self.assets['imSlider'],
                                   self.display.get_width() / 2,
                                   self.display.get_height() / 2,
                                   self.sounds)
        btBack1 = cButton.Button(self.assets['imBack'],
                                 self.display.get_width() / 2 - self.assets['imBack'].get_width() / 2 - self.assets[
                                     'imAmbience'].get_width(),
                                 self.display.get_height() / 2 + self.assets['imBack'].get_height() * SCALE, SCALE)
        logo = list('Настройки')
        logo_pos = [0] * len(logo)
        i = -1
        for letter in logo:
            i += 1
            pos = [100 + 40 * i, 30]
            logo_pos[i] = pos
            draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), pos)
        running = True
        while running:
            self.screen.fill((14, 219, 248))
            self.game_state = 'options_menu'
            i = -1
            for letter in logo:
                i += 1
                if random.random() < 0.001:
                    pos = [100 + 40 * i + random.random() * 40, 30 + random.random() * 60]
                    logo_pos[i] = pos
                draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), logo_pos[i])
            slMusic.draw(self.screen)
            slAmbience.draw(self.screen)
            slEffects.draw(self.screen)
            btBack1.draw(self.screen)
            self.screen.blit(self.assets['imMusic'],
                             (slMusic.rectinc.x - self.assets['imBack'].get_width() / 2 - self.assets[
                                 'imAmbience'].get_width(), slMusic.rectinc.y))
            self.screen.blit(self.assets['imAmbience'],
                             (slAmbience.rectinc.x - self.assets['imBack'].get_width() / 2 - self.assets[
                                 'imAmbience'].get_width(), slAmbience.rectinc.y))
            self.screen.blit(self.assets['imEffects'],
                             (slEffects.rectinc.x - self.assets['imBack'].get_width() / 2 - self.assets[
                                 'imEffects'].get_width(), slEffects.rectinc.y))
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        del btBack1
                        del slMusic
                        del slAmbience
                        del slEffects
                        save_sound_volume(self)
                        return 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        ambience = slAmbience.get_status()
                        music = slMusic.get_status()
                        effects = slEffects.get_status()
                        if ambience[0]:
                            self.ambience_volume = max(0, self.ambience_volume - 1)
                            self.sfx['ambience'].set_volume(self.volumes[self.ambience_volume])
                            self.sfx['stone12'].set_volume(self.volumes[self.ambience_volume])
                            self.sfx['brick12'].set_volume(self.volumes[self.ambience_volume])
                            self.sfx['desert12'].set_volume(self.volumes[self.ambience_volume])
                        if ambience[1]:
                            self.ambience_volume = min(10, self.ambience_volume + 1)
                            self.sfx['ambience'].set_volume(self.volumes[self.ambience_volume])
                            self.sfx['stone12'].set_volume(self.volumes[self.ambience_volume])
                            self.sfx['brick12'].set_volume(self.volumes[self.ambience_volume])
                            self.sfx['desert12'].set_volume(self.volumes[self.ambience_volume])
                        if music[0]:
                            self.music_volume = max(0, self.music_volume - 1)
                            pygame.mixer.music.set_volume(self.volumes[self.music_volume])
                        if music[1]:
                            self.music_volume = min(10, self.music_volume + 1)
                            pygame.mixer.music.set_volume(self.volumes[self.music_volume])
                        if effects[0]:
                            self.sounds = max(0, self.sounds - 1)
                        if effects[1]:
                            self.sounds = min(10, self.sounds + 1)
                        self.screen.blit(self.assets['imMusic'],
                                         (slMusic.rectinc.x - self.assets['imBack'].get_width() / 2 - self.assets[
                                             'imAmbience'].get_width(), slMusic.rectinc.y))
                        self.screen.blit(self.assets['imAmbience'],
                                         (slAmbience.rectinc.x - self.assets['imBack'].get_width() / 2 - self.assets[
                                             'imAmbience'].get_width(), slAmbience.rectinc.y))
                        self.screen.blit(self.assets['imEffects'],
                                         (slEffects.rectinc.x - self.assets['imBack'].get_width() / 2 - self.assets[
                                             'imEffects'].get_width(), slEffects.rectinc.y))
                        if btBack1.get_status():
                            del btBack1
                            del slMusic
                            del slAmbience
                            del slEffects
                            save_sound_volume(self)
                            return 1
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        slAmbience.clickeddec = False
                        slAmbience.clickedinc = False
                        slMusic.clickedinc = False
                        slMusic.clickeddec = False
                        slEffects.clickedinc = False
                        slEffects.clickeddec = False
            pygame.display.update()
            self.mainClock.tick(FPS)

    def main_menu(self):
        pygame.mixer.music.load('sounds/bgm/Main_menu.mp3')
        pygame.mixer.music.play(-1)
        btNewGame = cButton.Button(self.assets['imNewGame'],
                                   0,
                                   220 - self.assets['imNewGame'].get_height() * SCALE,
                                   SCALE)
        btHeroHall = cButton.Button(self.assets['imHeroHall'],
                                    0, 220,
                                    SCALE)
        btOptions = cButton.Button(self.assets['imOptions'],
                                   0,
                                   220 + self.assets['imOptions'].get_height() * SCALE,
                                   SCALE)
        logo = list('Broken ritual')
        logo_pos = [0] * 13
        i = -1
        for letter in logo:
            i += 1
            pos = [100 + 40 * i, 30]
            logo_pos[i] = pos
            draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), pos)
        running = True
        while running:
            self.screen.blit(pygame.transform.scale(self.assets['imTitle'], self.screen.get_size()), (0, 0))
            self.game_state = 'main_menu'
            btNewGame.draw(self.screen)
            btHeroHall.draw(self.screen)
            btOptions.draw(self.screen)
            i = -1
            for letter in logo:
                i += 1
                if random.random() < 0.001:
                    pos = [100 + 40 * i + random.random() * 40, 30 + random.random() * 60]
                    logo_pos[i] = pos
                draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), logo_pos[i])
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btNewGame.get_status():
                            # NEW GAME MENU
                            running = self.new_game_menu()
                            continue
                        elif btHeroHall.get_status():
                            # HEROHALL MENU
                            running = self.hero_hall_menu()
                            continue
                        elif btOptions.get_status():
                            # OPTIONS MENU
                            running = self.options_menu()
                            continue
            pygame.display.update()
            self.mainClock.tick(FPS)
        del btNewGame
        del btHeroHall
        return

    def dead_screen(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load('sounds/bgm/results.mp3')
        pygame.mixer.music.play(-1)
        r = 61
        g = 120
        fin = open('herohall/hall.txt', 'r', encoding='utf8')
        heroes = []
        for line in fin.readlines():
            name, score = line.split()
            heroes.append([name, int(score)])
        fin.close()
        while True:
            r = (r + 1) % 61
            g = (g + 1) % 120
            text_color = (61 + r, 120 + g, 55)
            self.screen.blit(pygame.transform.scale(self.assets['imDeadScreen'], (WIDTH, HEIGHT)), (0, 0))
            draw_text(self.screen, 'Ваше приключение окончено', pygame.font.Font('Blackcraft.ttf', 35),
                      (WIDTH - 50, HH / 4),
                      'white')
            draw_text(self.screen, 'Счёт: ' + str(self.score), pygame.font.Font('Blackcraft.ttf', 50),
                      (WIDTH / 2 + 50, HH / 2),
                      text_color)
            draw_text(self.screen, 'Нажмите ESCAPE для выхода', pygame.font.Font('Blackcraft.ttf', 35),
                      (WIDTH - 50, HH),
                      'white')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    heroes.append([self.player_name, self.score])
                    heroes.sort(key=lambda x: x[1], reverse=True)
                    heroes = heroes[:10]
                    fout = open('herohall/hall.txt', 'w', encoding='utf8')
                    for h in heroes:
                        print(h[0], h[1], file=fout)
                    fout.close()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        heroes.append([self.player_name, self.score])
                        heroes.sort(key=lambda x: x[1], reverse=True)
                        heroes = heroes[:10]
                        fout = open('herohall/hall.txt', 'w', encoding='utf8')
                        for h in heroes:
                            print(h[0], h[1], file=fout)
                        fout.close()
                        pygame.quit()
                        return
            pygame.display.update()
            self.mainClock.tick(FPS)

    def hero_hall_menu(self):
        btBack = cButton.Button(self.assets['imBack'],
                                self.screen.get_width() / 2 - self.assets['imBack'].get_width() / 2,
                                self.screen.get_height() - self.assets['imBack'].get_height() * SCALE, SCALE)
        running = True
        fin = open('herohall/hall.txt', 'r', encoding='utf8')
        data = [line.strip() for line in fin.readlines()]
        fin.close()
        offsety = -HEIGHT
        while running:
            self.screen.fill((14, 219, 248))
            self.screen.blit(pygame.transform.scale(self.assets['imHeroTitle'], self.screen.get_size()), (0, 0))
            btBack.draw(self.screen)
            self.game_state = 'hero_hall'
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'main_menu'
                        self.screen.fill((14, 219, 248))
                        self.screen.blit(pygame.transform.scale(self.assets['imTitle'], self.screen.get_size()),
                                         (0, 0))
                        del btBack
                        return 1
                if event.type == pygame.MOUSEWHEEL:
                    if event.precise_y == 2.0:
                        offsety += 10
                    if event.precise_y == -2.0:
                        offsety -= 10
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btBack.get_status():
                            self.game_state = 'main_menu'
                            self.screen.fill((14, 219, 248))
                            self.screen.blit(pygame.transform.scale(self.assets['imTitle'], self.screen.get_size()),
                                             (0, 0))
                            del btBack
                            return 1
            i = -1
            for line in data:
                i += 1
                draw_text(self.screen, f'{i + 1}) {line}', pygame.font.Font('Blackcraft.ttf', 50),
                          (2 * WIDTH / 3, 50 * i - offsety))
            offsety += 1.0
            pygame.display.update()
            self.mainClock.tick(FPS)

    def new_game_menu(self):
        self.screen.fill((14, 219, 248))
        btFighter = cButton.Button(self.assets['imFighter'], 80, 120, SCALE)
        btKnight = cButton.Button(self.assets['imKnight'], 80 + self.assets['imKnight'].get_width(), 120, SCALE)
        btMage = cButton.Button(self.assets['imMage'], 80 + 2 * self.assets['imMage'].get_width(), 120, SCALE)
        btNinja = cButton.Button(self.assets['imNinja'], 80 + 3 * self.assets['imNinja'].get_width(), 120, SCALE)
        btBack = cButton.Button(self.assets['imBack'],
                                self.screen.get_width() / 2 - self.assets['imBack'].get_width() / 2,
                                self.screen.get_height() - self.assets['imBack'].get_height() * SCALE, SCALE)
        logo = list('Новая игра')
        logo_pos = [0] * 13
        i = -1
        for letter in logo:
            i += 1
            pos = [100 + 40 * i, 30]
            logo_pos[i] = pos
            draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), pos)
        running = True
        while running:
            self.screen.blit(pygame.transform.scale(load_image('pano/Cloud_Tree.png').convert(), (WIDTH, HEIGHT)),
                             (0, 0))
            btFighter.draw(self.screen)
            btKnight.draw(self.screen)
            btMage.draw(self.screen)
            btNinja.draw(self.screen)
            btBack.draw(self.screen)
            if btFighter.collide_check():
                self.screen.blit(self.assets['fighter_info'], (100, HH / 2 + 30))
            if btKnight.collide_check():
                self.screen.blit(self.assets['knight_info'], (100, HH / 2 + 30))
            if btMage.collide_check():
                self.screen.blit(self.assets['mage_info'], (100, HH / 2 + 30))
            if btNinja.collide_check():
                self.screen.blit(self.assets['ninja_info'], (100, HH / 2 + 30))
            self.game_state = 'new_game_menu'
            i = -1
            for letter in logo:
                i += 1
                if random.random() < 0.0002:
                    pos = [100 + 40 * i + random.random() * 40, 30 + random.random() * 60]
                    logo_pos[i] = pos
                draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), logo_pos[i])
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'main_menu'
                        self.screen.fill((14, 219, 248))
                        self.screen.blit(pygame.transform.scale(self.assets['imTitle'], self.display.get_size()),
                                         (0, 0))
                        return True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btBack.get_status():
                            self.game_state = 'main_menu'
                            self.screen.fill((14, 219, 248))
                            self.screen.blit(pygame.transform.scale(self.assets['imTitle'], self.display.get_size()),
                                             (0, 0))
                            return True
                        elif btFighter.get_status():
                            self.choose = 0
                            del btFighter
                            del btKnight
                            del btMage
                            return False
                        elif btKnight.get_status():
                            self.choose = 1
                            del btFighter
                            del btKnight
                            del btMage
                            return False
                        elif btMage.get_status():
                            self.choose = 2
                            del btFighter
                            del btKnight
                            del btMage
                            return False
                        elif btNinja.get_status():
                            self.choose = 3
                            del btFighter
                            del btKnight
                            del btMage
                            return False
            pygame.display.update()
            self.mainClock.tick(FPS)

    def pause_menu(self):
        btResume = cButton.Button(self.assets['imResume'],
                                  self.display.get_width() / 2 - self.assets['imResume'].get_width() / 2,
                                  300 - self.assets['imResume'].get_height() * SCALE, SCALE)
        btOptions = cButton.Button(self.assets['imOptions'],
                                   self.display.get_width() / 2 - self.assets['imOptions'].get_width() / 2,
                                   300, SCALE)
        btExit = cButton.Button(self.assets['imExit'],
                                self.display.get_width() / 2 - self.assets['imExit'].get_width() / 2,
                                300 + self.assets['imExit'].get_height() * SCALE, SCALE)
        logo = list('Пауза')
        logo_pos = [0] * len(logo)
        i = -1
        for letter in logo:
            i += 1
            pos = [100 + 40 * i, 30]
            logo_pos[i] = pos
            draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), pos)
        running = True
        while running:
            self.screen.fill((14, 219, 248))
            self.paused_game = True
            self.game_state = 'paused_game'
            btResume.draw(self.screen)
            btOptions.draw(self.screen)
            btExit.draw(self.screen)
            i = -1
            for letter in logo:
                i += 1
                if random.random() < 0.001:
                    pos = [200 + 40 * i + random.random() * 40, 30 + random.random() * 60]
                    logo_pos[i] = pos
                draw_text(self.screen, letter, pygame.font.Font('Blackcraft.ttf', 40), logo_pos[i])
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        del btExit
                        del btResume
                        del btOptions
                        self.paused_game = False
                        return True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btResume.get_status():
                            del btExit
                            del btResume
                            del btOptions
                            self.paused_game = False
                            return True
                        if btExit.get_status():
                            pygame.quit()
                            sys.exit()
                        if btOptions.get_status():
                            self.options_menu()
            pygame.display.update()
            self.mainClock.tick(FPS)

    def run(self):
        # MAIN MENU
        self.main_menu()
        self.player_name = textinput(self, self.screen).replace(' ', '_')
        self.game_state = 'game'
        self.paused_game = False
        # Init game loop
        if self.choose == 0:
            self.player = Fighter(self, (self.display.get_width() / 2, self.display.get_height() / 2),
                                  (25, 25), self.choose)
        elif self.choose == 1:
            self.player = Knight(self, (self.display.get_width() / 2, self.display.get_height() / 2),
                                 (25, 25), self.choose)
        elif self.choose == 2:
            self.player = Mage(self, (self.display.get_width() / 2, self.display.get_height() / 2),
                               (25, 25), self.choose)
        elif self.choose == 3:
            self.player = Ninja(self, (self.display.get_width() / 2, self.display.get_height() / 2),
                                (25, 25), self.choose)
        self.load_level(self.level)
        while self.running:
            self.game_state = 'game'
            self.display.fill((0, 0, 0, 0))
            if self.level == 'green1' or self.level == 'green2':
                self.outlines.blit(self.assets['imBackGround'], (0, 0))
            elif self.level == 'stone1' or self.level == 'stone2':
                self.outlines.blit(self.assets['imStone'], (0, 0))
            elif self.level == 'brick1' or self.level == 'brick2':
                self.outlines.blit(self.assets['imStone'], (0, 0))
            elif self.level == 'desert1' or self.level == 'desert2':
                self.outlines.blit(self.assets['imDesert'], (0, 0))
            elif self.level == 'win':
                self.outlines.blit(self.assets['imWin'], (0, 0))
            self.display_shake = max(0, self.display_shake - 1)
            # ИГРОВОЙ ПРОЦЕСС
            if self.transition_time < 0:
                self.transition_time += 1
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition_time = min(30, self.transition_time + 1)
                if self.dead > 40:
                    self.sfx['ambience'].stop()
                    self.sfx['fall'].play()
                    self.paused_game = True
                    self.dead_screen()
                    self.running = False
                    break
            self.camera[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.camera[0]) / 30
            self.camera[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.camera[1]) / 30
            camera_render = (int(self.camera[0]), int(self.camera[1]))
            # Создание частиц. 50_000 понижает вероятность рождения частицы каждый кадр. Если поставить 1 вероятность ~100%
            for leaf in self.leaf_spawner:
                if random.random() * 50_000 < leaf.width * leaf.height:
                    pos = (leaf.x + random.random() * leaf.width, leaf.y + random.random() * leaf.height)
                    self.particles.append(
                        Particle(self, 'leaf', pos, velocity=(-0.5 + random.random(), random.random()),
                                 frame=random.randint(0, 18)))
            if self.level in ['green1', 'green2', 'desert1', 'desert2']:
                self.clouds.update()
                self.clouds.render(self.outlines, offset=camera_render)
            self.tilemap.render(self.display, offset=camera_render)
            # Отслеживание снарядов [[x, y], direction, time]
            for projectile in self.projectiles.copy():
                projectile.update()
                projectile.render(self.display, camera_render)
                if self.tilemap.obstacle_check(projectile.get_pos()):
                    # Создание искр при попадании в препятствие
                    for _ in range(4 * projectile.get_shards()):
                        self.sparks.append(
                            Spark(projectile.get_pos(),
                                  random.random() - 0.5 + (math.pi if projectile.get_velocity()[0] > 0 else 0),
                                  2 + random.random()))
                    projectile.set_distance(0)
                # Вычисление попадания по игроку
                elif projectile.who == 'Player':
                    for enemy in self.enemies.copy():
                        if projectile.get_pos()[0] - 10 <= enemy.get_pos()[0] <= projectile.get_pos()[0] + 10:
                            kill = enemy.hit_check(projectile)
                            if kill[0]:
                                drop_item(self, enemy)
                                self.score += enemy.get_score()
                                self.enemies.remove(enemy)
                            if kill[1]:
                                projectile.set_distance(0)
                elif projectile.who == 'Enemy':
                    self.player.hit_check(projectile)
                if projectile.isdead():
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
            # Отслеживание врагов
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, movement=(0, 0))
                enemy.render(self.display, offset=camera_render)
                if kill:
                    drop_item(self, enemy)
                    self.score += enemy.get_score()
                    self.enemies.remove(enemy)
            # Отслеживание предметов
            for item in self.items.copy():
                item.update()
                item.render(self.display, offset=camera_render)
                use_item(self, item, self.player)
            # Отслеживание квестовых предметов
            for item in self.questitems.copy():
                item.update()
                item.render(self.display, offset=camera_render)
                use_item(self, item, self.player)
            if not self.dead:
                self.player.update(self.tilemap, (self.movementX[1] - self.movementX[0], 0))
                self.player.render(self.display, offset=camera_render)
            # Отслеживание искр
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=camera_render)
                if kill:
                    self.sparks.remove(spark)
            if self.game_state == 'game':
                display_mask = pygame.mask.from_surface(self.display)
                display_shadow = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    self.outlines.blit(display_shadow, offset)
            # Отслеживание частиц
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=camera_render)
                # Траектория листика по синусоиде
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            # Отслеживание вслывающей информации
            for text in self.texts.copy():
                kill = text.update()
                text.render(self.outlines, offset=camera_render)
                if kill:
                    self.texts.remove(text)

            # ПЕРЕХВАТЧИК СОБЫТИЙ
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if self.player.__class__ == Mage:
                        if event.key == pygame.K_e:
                            self.player.spellbook[0].cast()
                        elif event.key == pygame.K_r:
                            self.player.spellbook[1].cast()
                        elif event.key == pygame.K_t:
                            self.player.spellbook[2].cast()
                        elif event.key == pygame.K_y:
                            self.player.spellbook[3].cast()
                        elif event.key == pygame.K_a:
                            self.movementX[0] = True
                        elif event.key == pygame.K_d:
                            self.movementX[1] = True
                        elif event.key == pygame.K_SPACE:
                            self.player.jump()
                            self.movementY[0] = True
                        elif event.key == pygame.K_s:
                            self.movementY[1] = True
                    else:
                        if event.key == pygame.K_e:
                            self.player.attack()
                        elif event.key == pygame.K_a:
                            self.movementX[0] = True
                        elif event.key == pygame.K_d:
                            self.movementX[1] = True
                        elif event.key == pygame.K_SPACE:
                            self.player.jump()
                            self.movementY[0] = True
                        elif event.key == pygame.K_s:
                            self.movementY[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_F1:
                        self.help = not self.help
                    if event.key == pygame.K_ESCAPE:
                        self.paused_game = True
                        self.game_state = 'pause_menu'
                        self.pause_menu()
                    if event.key == pygame.K_a:
                        self.movementX[0] = False
                    elif event.key == pygame.K_d:
                        self.movementX[1] = False
                    elif event.key == pygame.K_SPACE:
                        self.movementY[0] = False
                    elif event.key == pygame.K_s:
                        self.movementY[1] = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # Анимация загрузки.------
            if self.game_state == 'game' and self.transition_time:
                load_surface = pygame.Surface(self.display.get_size())
                pygame.draw.circle(load_surface, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition_time)) * 8)
                load_surface.set_colorkey((255, 255, 255))
                self.display.blit(load_surface, (0, 0))
            self.outlines.blit(self.display, (0, 0))
            shake_offset = (random.random() * self.display_shake - self.display_shake / 2,
                            random.random() * self.display_shake - self.display_shake / 2)
            if self.game_state == 'game':
                # Отрисовка игровых статусов
                counter = -1
                for qitem in self.player.questitems:
                    counter += 1
                    self.outlines.blit(self.assets[f'{qitem}/idle'].images[0], (200 + counter * 28, 0))
                icolhud = self.assets['hud'][0]
                icomemp = self.assets['hud'][1]
                icomend = self.assets['hud'][2]
                icomlif = self.assets['hud'][3]
                icomman = self.assets['hud'][4]
                icorlif = self.assets['hud'][5]
                icorman = self.assets['hud'][6]
                icorend = self.assets['hud'][7]
                self.outlines.blit(icolhud, (0, 0))
                for iempty in range(self.player.get_maxlife()):
                    self.outlines.blit(icomemp, (icolhud.get_width() + icomemp.get_width() * iempty, 4))
                for iempty in range(self.player.get_maxmana()):
                    self.outlines.blit(icomemp, (icolhud.get_width() + icomemp.get_width() * iempty, 24))
                for iempty in range(self.player.get_maxendurance()):
                    self.outlines.blit(icomemp, (icolhud.get_width() + icomemp.get_width() * iempty, 44))
                for ilife in range(self.player.get_life()):
                    self.outlines.blit(icomlif, (icolhud.get_width() + icomlif.get_width() * ilife, 5))
                for imana in range(self.player.get_mana()):
                    self.outlines.blit(icomman, (icolhud.get_width() + icomman.get_width() * imana, 25))
                for iendurance in range(self.player.get_endurance()):
                    self.outlines.blit(icomend, (icolhud.get_width() + icomend.get_width() * iendurance, 45))
                self.outlines.blit(icorlif, (icolhud.get_width() + self.player.get_maxlife() * icomemp.get_width(), 2))
                self.outlines.blit(icorman, (icolhud.get_width() + self.player.get_maxmana() * icomemp.get_width(), 22))
                self.outlines.blit(icorend,
                                   (icolhud.get_width() + self.player.get_maxendurance() * icomemp.get_width(), 42))
                if self.player.__class__ == Mage:
                    for ispell in range(len(self.player.spellbook)):
                        self.player.spellbook[ispell].update()
                        self.player.spellbook[ispell].render(self.outlines, (ispell, camera_render))
                self.outlines.blit(self.player.get_animation_shot(), (16, 16))
                self.outlines.blit(self.assets['score_bar'], (WIDTH - 72, 0))
                draw_text(self.outlines, str(self.score), pygame.font.Font('Blackcraft.ttf', 20), (WIDTH, 0))
                if self.help:
                    if self.player.__class__ == Fighter:
                        self.outlines.blit(self.assets['fighter_info'], (100, HH / 2 + 30))
                    elif self.player.__class__ == Knight:
                        self.outlines.blit(self.assets['knight_info'], (100, HH / 2 + 30))
                    elif self.player.__class__ == Mage:
                        self.outlines.blit(self.assets['mage_info'], (100, HH / 2 + 30))
                    elif self.player.__class__ == Ninja:
                        self.outlines.blit(self.assets['ninja_info'], (100, HH / 2 + 30))
                self.screen.blit(self.outlines, shake_offset)
            else:
                self.screen.blit(self.display, shake_offset)
            pygame.display.update()
            self.mainClock.tick(FPS)

    def load_level(self, map):
        self.tilemap.load('maps/' + str(map) + '.json')
        # Генератор листочков
        self.leaf_spawner = []
        for tree in self.tilemap.extract(
                [('decor_green', 11), ('decor_green', 12), ('decor_green', 13), ('decor_green', 14),
                 ('decor_green', 15), ('decor_green', 16), ('decor_green', 17)], keep=True):
            self.leaf_spawner.append(pygame.Rect(3 + tree['pos'][0], 3 + tree['pos'][1], 32, 64))
        # Расстановка квестовых предметов
        self.questitems = []
        self.items = []
        for item in self.tilemap.extract([('exit', 0), ('decor_brick', 13)]):
            if item['type'] == 'exit' and item['variant'] == 0:
                self.items.append(Item(self, 'iexit', item['pos'], (45, 48)))
            elif item['type'] == 'decor_brick' and item['variant'] == 13:
                self.items.append(Item(self, 'coin', item['pos'], (23, 23)))
        for item in self.tilemap.extract(
                [('quests', 0), ('quests', 1), ('quests', 2), ('quests', 3), ('quests', 4), ('quests', 5),
                 ('quests', 6), ('quests', 7)]):
            if item['variant'] == 0:
                self.questitems.append(Item(self, 'brick_l', item['pos'], (28, 28)))
            elif item['variant'] == 1:
                self.questitems.append(Item(self, 'brick_r', item['pos'], (28, 28)))
            elif item['variant'] == 2:
                self.questitems.append(Item(self, 'desert_l', item['pos'], (28, 28)))
            elif item['variant'] == 3:
                self.questitems.append(Item(self, 'desert_r', item['pos'], (28, 28)))
            elif item['variant'] == 4:
                self.questitems.append(Item(self, 'green_l', item['pos'], (28, 28)))
            elif item['variant'] == 5:
                self.questitems.append(Item(self, 'green_r', item['pos'], (28, 28)))
            elif item['variant'] == 6:
                self.questitems.append(Item(self, 'stone_l', item['pos'], (28, 28)))
            elif item['variant'] == 7:
                self.questitems.append(Item(self, 'stone_r', item['pos'], (28, 28)))
        # Расстановка врагов
        self.enemies = []
        for spawn in self.tilemap.extract(
                [('spawn', 0), ('spawn', 1), ('spawn', 2), ('spawn', 3), ('spawn', 4), ('spawn', 5), ('spawn', 6),
                 ('spawn', 7), ('spawn', 8), ('spawn', 9), ('spawn', 10), ('spawn', 11), ('spawn', 12), ('spawn', 13),
                 ('spawn', 14)]):
            if spawn['variant'] == 0:
                self.player.pos = spawn['pos']
                self.player.time_in_air = 0
            else:
                if spawn['variant'] == 1:
                    self.enemies.append(Zombie(self, 'zombie', spawn['pos'], (30, 30)))
                if spawn['variant'] == 7:
                    self.enemies.append(Goblin(self, 'goblin', spawn['pos'], (30, 30)))
                if spawn['variant'] == 8:
                    self.enemies.append(GoblinHeavy(self, 'goblin_heavy', spawn['pos'], (30, 30)))
                if spawn['variant'] == 9:
                    self.enemies.append(GoblinMedium(self, 'goblin_medium', spawn['pos'], (30, 30)))
                if spawn['variant'] == 10:
                    self.enemies.append(GoblinMage(self, 'goblin_mage', spawn['pos'], (30, 30)))
                if spawn['variant'] == 2:
                    self.enemies.append(Lich(self, 'lich', spawn['pos'], (30, 30)))
                if spawn['variant'] == 3:
                    self.enemies.append(Ghost(self, 'ghost', spawn['pos'], (30, 30)))
                if spawn['variant'] == 4:
                    self.enemies.append(Slime(self, 'slime', spawn['pos'], (30, 30)))
                if spawn['variant'] == 5:
                    self.enemies.append(Flower(self, 'flower', spawn['pos'], (30, 30)))
                if spawn['variant'] == 6:
                    self.enemies.append(FlowerPredatory(self, 'flower_predatory', spawn['pos'], (30, 30)))
                if spawn['variant'] == 11:
                    self.enemies.append(GoblinWarlord(self, 'goblin_warlord', spawn['pos'], (30, 30)))
                if spawn['variant'] == 12:
                    self.enemies.append(Mummy(self, 'mummy', spawn['pos'], (30, 30)))
                if spawn['variant'] == 13:
                    self.enemies.append(Rat(self, 'rat', spawn['pos'], (30, 30)))
                if spawn['variant'] == 14:
                    self.enemies.append(RatPlague(self, 'rat_plague', spawn['pos'], (30, 30)))
        # Список частиц/снарядов
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.texts = []
        self.camera = [0, 0]
        self.dead = 0
        self.transition_time = -30
        self.killer = ''
        self.help = False
        load_sound_volume(self)
        if self.level == 'green1' or self.level == 'green2':
            self.sfx['ambience'].play(-1)
            pygame.mixer.music.load(f'sounds/bgm/Level{0}.mp3')
            pygame.mixer.music.play(-1)
        elif self.level == 'stone1' or self.level == 'stone2':
            self.sfx['stone12'].play(-1)
            pygame.mixer.music.load(f'sounds/bgm/Level{1}.mp3')
            pygame.mixer.music.play(-1)
        elif self.level == 'brick1' or self.level == 'brick2':
            self.sfx['brick12'].play(-1)
            pygame.mixer.music.load(f'sounds/bgm/Level{2}.wav')
            pygame.mixer.music.play(-1)
        elif self.level == 'desert1' or self.level == 'desert2':
            self.sfx['desert12'].play(-1)
            pygame.mixer.music.load(f'sounds/bgm/Level{3}.wav')
            pygame.mixer.music.play(-1)
        elif self.level == 'win':
            pygame.mixer.stop()
            pygame.mixer.music.load(f'sounds/bgm/Level4 ({random.randint(1, 3)}).wav')
            pygame.mixer.music.play(-1)


while True:
    game = Game()
    game.run()
