import pygame.transform
from scripts.projectile import Projectile
from scripts.utility import load_image, TextFrame


class Spell:
    def __init__(self, player, pos, iconset, cost, duration=1, cooldown=2):
        self.pos = list(pos)
        self.iconset = iconset
        self.duration = duration
        self.maxduration = duration
        self.recovery = 0
        self.cooldown = cooldown
        self.player = player
        self.cost = cost

    def isready(self):
        return not self.recovery and (self.player.get_mana() - self.cost) >= 0

    def update(self):
        self.duration = max(0, self.duration - 1)
        self.recovery = max(0, self.recovery - 1)

    def cast(self):
        if self.isready():
            self.recovery = self.cooldown
            self.duration = self.maxduration
            self.player.set_mana(self.player.get_mana() - self.cost)

    def render(self, surface, offset):
        surface.blit(self.iconset[not self.isready()],
                     (surface.get_width() / 2 + self.iconset[0].get_width() * offset[0],
                      surface.get_height() - self.iconset[0].get_height()))


class ThunderStrike(Spell):
    def __init__(self, player):
        self.pos = player.pos
        self.iconset = player.game.assets['thunder_strike']
        self.duration = 0
        self.maxduration = 100
        self.recovery = 0
        self.cooldown = 2000
        self.player = player
        self.cost = 8
        self.range = 6
        self.images = []
        for i in range(5):
            self.images.append(load_image(f'spells/thunder_strike{i}.png'))
        for img in self.images:
            img.set_colorkey((64, 128, 128))
        self.frame = 0
        self.image = self.images[self.frame]
        self.image.set_alpha(0)

    def cast(self):
        if self.isready():
            self.image.set_alpha(255)
            self.player.game.sfx['thunder_strike'].play()
            self.recovery = self.cooldown
            self.duration = self.maxduration
            self.player.set_mana(self.player.get_mana() - self.cost)
            for enemy in self.player.game.enemies.copy():
                distx = abs((enemy.pos[0] // self.player.game.tilemap.tilesize) - (self.player.pos[0] // self.player.game.tilemap.tilesize))
                disty = abs((enemy.pos[1] // self.player.game.tilemap.tilesize) - (self.player.pos[1] // self.player.game.tilemap.tilesize))
                if distx < self.range or disty < self.range // 2:
                    enemy.set_life(max(0, enemy.get_life() - 1))
                    self.player.game.texts.append(
                        TextFrame('HIT', pygame.font.Font('Blackcraft.ttf', 25), enemy.pos, duration=50,
                                  color=(0, 0, 0)))
                    if enemy.get_life() == 0:
                        self.player.game.score += enemy.get_score()
                        self.player.game.enemies.remove(enemy)

    def update(self):
        self.pos = self.player.pos
        self.duration = max(0, self.duration - 1)
        if not self.duration:
            self.image = self.images[4]
        else:
            dur = self.duration
            if dur % 20 == 0:
                self.frame = min(len(self.images) - 1, self.frame + 1)
            self.image = self.images[self.frame]
        self.recovery = max(0, self.recovery - 1)

    def render(self, surface, offset=(0, 0)):
        surface.blit(self.iconset[not self.isready()],
                     (surface.get_width() / 2 + self.iconset[0].get_width() * offset[0],
                      surface.get_height() - self.iconset[0].get_height()))
        if self.duration:
            for enemy in self.player.game.enemies.copy():
                distx = abs((enemy.pos[0] // self.player.game.tilemap.tilesize) - (
                            self.player.pos[0] // self.player.game.tilemap.tilesize))
                disty = abs((enemy.pos[1] // self.player.game.tilemap.tilesize) - (
                            self.player.pos[1] // self.player.game.tilemap.tilesize))
                if distx < self.range or disty < self.range // 2:
                    surface.blit(self.image, (enemy.pos[0] - offset[1][0], enemy.pos[1] - offset[1][1] - self.image.get_height()))


class IceArmor(Spell):
    def __init__(self, player):
        self.pos = list(player.pos)
        self.iconset = player.game.assets['ice_armor']
        self.duration = 0
        self.maxduration = 1000
        self.recovery = 0
        self.cooldown = 1500
        self.player = player
        self.cost = 4
        self.images = []
        self.image = 0
        for i in range(3, -1, -1):
            self.images.append(load_image(f'spells/ice_armor{i}.png'))
        for img in self.images:
            img.set_colorkey('black')
            img.set_alpha(80)

    def cast(self):
        if self.isready():
            self.player.game.sfx['ice_armor'].play()
            self.recovery = self.cooldown
            self.duration = self.maxduration
            self.player.set_mana(self.player.get_mana() - self.cost)
            self.player.set_block(3)
            self.player.set_maxblock(3)

    def update(self):
        self.duration = max(0, self.duration - 1)
        if not self.duration:
            self.player.set_maxblock(0)
            self.player.set_block(0)
            self.image = self.images[3]
        else:
            block = self.player.get_block()
            if block == 3:
                self.image = self.images[0]
            elif block == 2:
                self.image = self.images[1]
            elif block == 1:
                self.image = self.images[2]
            elif block == 0:
                self.image = self.images[3]
        self.recovery = max(0, self.recovery - 1)

    def render(self, surface, offset=(0, 0)):
        surface.blit(self.iconset[not self.isready()],
                     (surface.get_width() / 2 + self.iconset[0].get_width() * offset[0],
                      surface.get_height() - self.iconset[0].get_height()))
        surface.blit(self.image, (self.player.pos[0] - self.image.get_width() // 4 - offset[1][0],
                                  self.player.pos[1] - self.image.get_height() // 2 - offset[1][1]))


class ForceBolt(Spell):
    def __init__(self, player):
        super().__init__(player, player.pos, player.game.assets['force_bolt'], 1, duration=100, cooldown=50)

    def cast(self):
        if self.isready():
            self.player.game.sfx['magic_missle'].play()
            self.recovery = self.cooldown
            self.duration = self.maxduration
            self.player.set_mana(self.player.get_mana() - self.cost)
            if not self.player.flip:
                img = self.player.game.assets['magic_missle']
            else:
                img = pygame.transform.flip(self.player.game.assets['magic_missle'], True, False)
            self.player.game.projectiles.append(
                Projectile(img, self.player.pos[0], self.player.pos[1], shards=1,
                           velocity=(-5 if self.player.flip else 5, 0), distance=self.duration, unblockable=False,
                           who='Player'))


class FireBall(Spell):
    def __init__(self, player):
        super().__init__(player, player.pos, player.game.assets['pfire_ball'], 3, duration=250, cooldown=250)

    def cast(self):
        if self.isready():
            self.player.game.sfx['fireball_attack'].play()
            self.recovery = self.cooldown
            self.duration = self.maxduration
            self.player.set_mana(self.player.get_mana() - self.cost)
            if self.player.flip:
                img = pygame.transform.flip(
                    self.player.game.assets['pfire_ball1'], True, False)
                img.set_colorkey((0, 0, 0))
            else:
                img = self.player.game.assets['pfire_ball1']
            self.player.game.projectiles.append(Projectile(img, self.player.pos[0], self.player.pos[1], 2,
                                                           shards=1,
                                                           velocity=(-10 if self.player.flip else 10, 0),
                                                           distance=self.duration, unblockable=False,
                                                           who='Player'))
