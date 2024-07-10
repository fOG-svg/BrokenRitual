import pygame
import sys
from scripts.utility import load_image, load_dir_images, load_map, save_map
from scripts.tilemap import Tilemap

# CONSTANTS
FPS = 60
WIDTH = 1240
HW = WIDTH / 2
HEIGHT = 768
HH = HEIGHT / 2
SCALE = 10
UI_TOP_LEFT = (10, 10)
UI_HEIGHT = 32


# -------------------------------
class Editor:
    def __init__(self):
        self.filejson = load_map()
        pygame.init()
        pygame.display.set_caption('Редактор уровней')
        self.FONT = pygame.font.SysFont(None, 20)
        self.mainClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        pygame.display.set_icon(load_image('icons/icon_editor.png'))
        self.display = pygame.Surface((WIDTH, HEIGHT))
        self.ongrid_ico = load_image('icons/on_grid_ico.png')
        self.offgrid_ico = load_image('icons/off_grid_ico.png')
        self.save_map_ico = load_image('icons/save_map.png')
        self.load_map_ico = load_image('icons/load_map.png')
        self.movementX = [False, False]
        self.movementY = [False, False]
        # Спрайты
        self.assets = {
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
            'spawn': load_dir_images('spawn'),
            'quests': load_dir_images('quests/level_editor'),
            'exit': load_dir_images('tiles/exit')
        }
        self.tilemap = Tilemap(self, tilesize=48)
        try:
            self.tilemap.load(self.filejson)
        except FileNotFoundError:
            print(f'Файл {self.filejson} не найден.')
        self.camera = [0, 0]
        self.clicked = False
        self.right_clicked = False
        self.shifted = False
        self.on_grid = True
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

    def run(self):
        collide = False
        # Запуск цикла редактора уровней
        while True:
            self.display.fill((0, 0, 0))
            # Движение камеры
            self.camera[0] += (self.movementX[1] - self.movementX[
                0]) * SCALE  # Для более быстрого движения камеры множитель можно менять
            self.camera[1] += (self.movementY[1] - self.movementY[
                0]) * SCALE  # Для более быстрого движения камеры множитель можно менять
            render_camera = (int(self.camera[0]), int(self.camera[1]))
            self.tilemap.render(self.display, offset=render_camera)
            # Выбор тайла
            current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_image.set_alpha(127)  # Прозрачность(0 - невидимый, 255 - непрозрачный)
            mouse_pos = pygame.mouse.get_pos()
            mouse_tile_pos = (int((mouse_pos[0] + self.camera[0]) // self.tilemap.tilesize),
                              int((mouse_pos[1] + self.camera[1]) // self.tilemap.tilesize))
            # Интерфейс редактора
            if self.on_grid:
                self.display.blit(self.ongrid_ico, UI_TOP_LEFT)  # 1
            else:
                self.display.blit(self.offgrid_ico, UI_TOP_LEFT)  # 1
            self.display.blit(self.save_map_ico, (UI_TOP_LEFT[0], UI_TOP_LEFT[1] + UI_HEIGHT * 2))  # 2
            self.display.blit(self.load_map_ico, (UI_TOP_LEFT[0], UI_TOP_LEFT[1] + UI_HEIGHT * 3))  # 3
            if self.clicked:
                collide = False
                save_rect = pygame.Rect(UI_TOP_LEFT[0], UI_TOP_LEFT[1] + UI_HEIGHT * 2, self.save_map_ico.get_width(),
                                        self.save_map_ico.get_height())
                load_rect = pygame.Rect(UI_TOP_LEFT[0], UI_TOP_LEFT[1] + UI_HEIGHT * 3, self.load_map_ico.get_width(),
                                        self.load_map_ico.get_height())
                # Кнопка сохнарить карту
                if save_rect.collidepoint(mouse_pos):
                    self.filejson = save_map()
                    self.tilemap.save(self.filejson)
                    self.clicked = False
                    collide = True
                # Кнопка загрузить карту
                if load_rect.collidepoint(mouse_pos):
                    self.filejson = load_map()
                    try:
                        self.tilemap.load(self.filejson)
                    except FileNotFoundError:
                        print(f'Файл {self.filejson} не найден.')
                    self.clicked = False
                    collide = True
            if self.on_grid:
                # Отображение предполагаемого места размещения по сетке
                self.display.blit(current_tile_image, (mouse_tile_pos[0] * self.tilemap.tilesize - self.camera[0],
                                                       mouse_tile_pos[1] * self.tilemap.tilesize - self.camera[1]))
            else:
                # Отображение предполагаемого места размещения не по сетке
                self.display.blit(current_tile_image, mouse_pos)
            # Добавить тайл на карту
            if self.on_grid and self.clicked:
                self.tilemap.tilemap[str(mouse_tile_pos[0]) + ';' + str(mouse_tile_pos[1])] = {
                    'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': mouse_tile_pos}
            # Удалить тайл с карты
            if self.right_clicked:
                mouse_loc = str(mouse_tile_pos[0]) + ';' + str(mouse_tile_pos[1])
                if mouse_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[mouse_loc]
                else:
                    for tile in self.tilemap.tiles_offgrid.copy():
                        t_img = self.assets[tile['type']][tile['variant']]
                        t_rect = pygame.Rect(tile['pos'][0] - self.camera[0], tile['pos'][1] - self.camera[1],
                                             t_img.get_width(), t_img.get_height())
                        if t_rect.collidepoint(mouse_pos):
                            self.tilemap.tiles_offgrid.remove(tile)
            # -----------
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.filejson = save_map()
                        self.tilemap.save(self.filejson)
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicked = True
                        # Чтобы не добавлять тайлы вне сетки со скоростью FPS код добавления в список тут
                        if not self.on_grid:
                            self.tilemap.tiles_offgrid.append({'type': self.tile_list[self.tile_group],
                                                               'variant': self.tile_variant, 'pos': (
                                    mouse_pos[0] + self.camera[0], mouse_pos[1] + self.camera[1])})
                    if event.button == 3:
                        self.right_clicked = True
                    if self.shifted:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicked = False
                    if event.button == 3:
                        self.right_clicked = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F5:
                        self.filejson = save_map()
                        self.tilemap.save(self.filejson)

                    if event.key == pygame.K_SPACE:
                        self.on_grid = not self.on_grid
                    if event.key == pygame.K_a:
                        self.movementX[0] = True
                    if event.key == pygame.K_d:
                        self.movementX[1] = True
                    if event.key == pygame.K_w:
                        self.movementY[0] = True
                    if event.key == pygame.K_s:
                        self.movementY[1] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shifted = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movementX[0] = False
                    if event.key == pygame.K_d:
                        self.movementX[1] = False
                    if event.key == pygame.K_w:
                        self.movementY[0] = False
                    if event.key == pygame.K_s:
                        self.movementY[1] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shifted = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # ------------------------------------
            self.screen.blit(self.display, (0, 0))
            pygame.display.update()
            self.mainClock.tick(FPS)


Editor().run()
