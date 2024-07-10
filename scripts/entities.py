import random
import pygame
import math
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.utility import Animation, TextFrame, load_image, load_dir_images
from scripts.projectile import Projectile
from scripts.spell import IceArmor, ThunderStrike, FireBall, ForceBolt

BLOCKCOLOR = (52, 29, 225)
CRITCOLOR = (203, 19, 171)
ECRITCOLOR = (243, 30, 11)
DODGECOLOR = (12, 43, 77)


class Item:
    def __init__(self, game, i_type, pos, size):
        self.game = game
        self.type = i_type
        self.pos = list(pos)
        self.size = size
        self.animation_offset = (-3, -3)
        self.frame = 0
        self.action = 'idle'
        self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self):
        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        surface.blit(self.animation.shot(), (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def collide_check(self, object):
        return self.rect().colliderect(object.rect())


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.action = ''
        self.animation_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        self.frame = 0
        self.velocity = [0, 0]
        self.last_movement = [0, 0]
        self.collision_type = {'up': False,
                               'down': False,
                               'left': False,
                               'right': False,
                               }

    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=(0, 0)):
        self.collision_type = {'up': False,
                               'down': False,
                               'left': False,
                               'right': False,
                               }
        frame_mv = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        # Collide X
        self.pos[0] += frame_mv[0]
        entity_rect = self.rect()
        for rect in tilemap.phys_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_mv[0] > 0:
                    entity_rect.right = rect.left
                    self.collision_type['right'] = True
                if frame_mv[0] < 0:
                    entity_rect.left = rect.right
                    self.collision_type['left'] = True
                self.pos[0] = entity_rect.x
        # Collide Y
        self.pos[1] += frame_mv[1]
        entity_rect = self.rect()
        for rect in tilemap.phys_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_mv[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collision_type['down'] = True
                if frame_mv[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collision_type['up'] = True
                self.pos[1] = entity_rect.y
        # ----------
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        self.velocity[1] = min(6, self.velocity[1] + 0.1)
        self.last_movement = movement
        if self.collision_type['up'] or self.collision_type['down']:
            self.velocity[1] = 0
        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        surface.blit(pygame.transform.flip(self.animation.shot(), self.flip, False), (
            self.pos[0] - offset[0] + self.animation_offset[0], self.pos[1] - offset[1] + self.animation_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size, choose):
        super().__init__(game, 'player', pos, size)
        self.game.assets['player/idle'] = Animation(load_dir_images(f'characters/{choose}/idle'),
                                                    duration=10)
        self.game.assets['player/run'] = Animation(load_dir_images(f'characters/{choose}/run'),
                                                   duration=4)
        self.game.assets['player/jump'] = Animation(load_dir_images(f'characters/{choose}/jump'),
                                                    duration=4)
        self.game.assets['player/wall_slide'] = Animation(load_dir_images(f'characters/{choose}/slide'),
                                                          duration=4)
        self.questitems = []
        self.time_in_air = 0
        self.limit_of_jumps = 1
        self.maxjumps = 1
        self.wall_slide = False
        self.attaking = 0
        self.unvul = False
        self.block = 0
        self.max_block = 0
        self.block_recovery_time = 0
        self.life = 2
        self.max_life = 2
        self.mana = 0
        self.max_mana = 2
        self.mana_recovery = 0
        self.endurance = 0
        self.max_endurance = 2
        self.endurance_recovery = 0
        self.weapon = 'unarmed'
        self.weapon_pos = [self.rect().centerx + 8 + self.game.assets[self.weapon].get_width(),
                           self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]

    def hit_check(self, projectile):
        if self.rect().collidepoint(projectile.get_pos()):
            self.game.projectiles.remove(projectile)
            if not self.unvul:
                self.set_life(max(0, self.get_life() - projectile.get_damage()))
                if not self.get_life():
                    self.game.dead += 1
                self.game.display_shake = max(10, self.game.display_shake)
                # Создание искр и частиц при попадании в игрока
                for _ in range(10 * projectile.get_shards()):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'bloody', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))

    def restart(self):
        self.set_life(self.get_maxlife())
        self.set_mana(self.get_maxmana())
        self.set_endurance(self.get_maxendurance())
        self.block = self.max_block
        self.block_recovery_time = 0
        self.time_in_air = 0
        self.limit_of_jumps = self.get_maxjump()
        self.unvul = False
        self.endurance_recovery = 0
        self.mana_recovery = 0

    def weapon_rect(self):
        return pygame.Rect(self.weapon_pos[0], self.weapon_pos[1], self.game.assets[self.weapon].get_width(),
                           self.game.assets[self.weapon].get_height())

    def get_maxjump(self):
        return self.maxjumps

    def get_velocity(self):
        return self.velocity

    def get_weapon(self):
        return self.weapon

    def set_weapon(self, weapon):
        self.weapon = weapon

    def set_block(self, block):
        self.block = block

    def set_maxblock(self, maxblock):
        self.max_block = maxblock

    def get_block(self):
        return self.block

    def get_maxblock(self):
        return self.max_block

    def set_life(self, life):
        self.life = life

    def get_life(self):
        return self.life

    def set_mana(self, mana):
        self.mana = mana

    def get_mana(self):
        return self.mana

    def set_endurance(self, endurance):
        self.endurance = endurance

    def get_endurance(self):
        return self.endurance

    def set_maxlife(self, life):
        self.max_life = life

    def get_maxlife(self):
        return self.max_life

    def set_maxmana(self, mana):
        self.max_mana = mana

    def get_maxmana(self):
        return self.max_mana

    def set_maxendurance(self, endurance):
        self.max_endurance = endurance

    def get_maxendurance(self):
        return self.max_endurance

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        words = ['brick', 'desert', 'green', 'stone']
        if not self.flip:
            self.weapon_pos = [self.rect().centerx - 4 + self.game.assets[self.weapon].get_width(),
                               self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]
        else:
            self.weapon_pos = [self.rect().centerx - 6 - self.game.assets[self.weapon].get_width(),
                               self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]
        self.time_in_air += 1
        if self.time_in_air > 300:
            if not self.game.dead:
                self.game.killer = 'Высота'
                self.game.display_shake = max(15, self.game.display_shake)
            self.game.dead += 1
        self.wall_slide = False
        if (self.collision_type['left'] or self.collision_type['right']) and self.time_in_air > 4:
            self.wall_slide = True
            self.time_in_air = 6
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collision_type['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        if self.collision_type['down']:
            self.time_in_air = 0
            self.limit_of_jumps = 1
        if not self.wall_slide:
            if self.time_in_air > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        if abs(self.attaking) in {60, 50}:
            for _ in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                particle_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=particle_velocity,
                             frame=random.randint(0, 7)))
        # Нормализация атаки
        if self.attaking > 0:
            self.attaking = max(0, self.attaking - 1)
        else:
            self.attaking = min(0, self.attaking + 1)
        # Направление рывка в атаке
        if abs(self.attaking) > 50:
            self.velocity[0] = abs(self.attaking) / self.attaking * 8
            # После первых 10 кадров ускорения рывок заканчиваеться и скорость быстро нормализуеться. Также работает и как кулдаун атаки
            if abs(self.attaking) == 51:
                self.unvul = False
                self.velocity[0] *= 0.1
            particle_velocity = [abs(self.attaking) / self.attaking * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=particle_velocity,
                                                frame=random.randint(0, 7)))
        # Нормализация ускорения по горизонтали
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.time_in_air = 5
                self.limit_of_jumps = max(0, self.limit_of_jumps - 1)
                self.game.sfx['jump'].play()
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.time_in_air = 5
                self.limit_of_jumps = max(0, self.limit_of_jumps - 1)
                self.game.sfx['jump'].play()
                return True
        elif self.limit_of_jumps:
            self.velocity[1] = -4
            self.time_in_air = 5
            self.limit_of_jumps -= 1
            self.game.sfx['jump'].play()
            return True

    def attack(self):
        if not self.attaking:
            self.unvul = True
            self.game.sfx['attack'].play()
            if self.flip:
                self.attaking = -60
            else:
                self.attaking = 60

    def render(self, surface, offset=(0, 0)):
        if self.attaking < 51:
            super().render(surface, offset=offset)
            # Рендеринг оружия
            if self.flip:
                surface.blit(pygame.transform.flip(self.game.assets[self.weapon], True, False), (
                    self.weapon_pos[0] - offset[0],
                    self.weapon_pos[1] - offset[1]))
            else:
                surface.blit(self.game.assets[self.weapon],
                             (self.weapon_pos[0] - offset[0],
                              self.weapon_pos[1] - offset[1]))

    def get_animation_shot(self):
        return pygame.transform.flip(self.animation.shot(), self.flip, False)


class Ninja(Player):
    def __init__(self, game, pos, size, choose):
        super().__init__(game, pos, size, choose)
        self.weapon = 'dagger'
        self.max_mana = 0
        self.max_life = 2
        self.life = 2
        self.endurance = 3
        self.max_endurance = 3
        self.limit_of_jumps = 2
        self.maxjumps = 2
        self.dodje = 0.3
        self.backstab = 2
        self.dmg = 1

    def attack(self):
        if not self.attaking:
            self.game.sfx['dagger_attack'].play()
            if self.flip:
                self.attaking = -60
            else:
                self.attaking = 60

    def hit_check(self, projectile):
        if self.rect().collidepoint(projectile.get_pos()):
            self.game.projectiles.remove(projectile)
            if not self.unvul:
                if random.random() < self.dodje:
                    self.game.texts.append(
                        TextFrame('Увернулся', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 100, DODGECOLOR))
                else:
                    self.set_life(max(0, self.get_life() - projectile.get_damage()))
                    if not self.get_life():
                        self.game.dead += 1
                    self.game.display_shake = max(10, self.game.display_shake)
                    # Создание искр и частиц при попадании в игрока
                    for _ in range(10 * projectile.get_shards()):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'bloody', self.rect().center,
                                                            velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                      math.sin(angle + math.pi) * speed * 0.5],
                                                            frame=random.randint(0, 7)))

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.time_in_air = 5
                self.limit_of_jumps = max(0, self.limit_of_jumps - 1)
                self.game.sfx['jump'].play()
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.time_in_air = 5
                self.limit_of_jumps = max(0, self.limit_of_jumps - 1)
                self.game.sfx['jump'].play()
                return True
        elif self.limit_of_jumps:
            self.velocity[1] = -4
            self.time_in_air = 5
            self.limit_of_jumps -= 1
            self.game.sfx['jump'].play()
            return True

    def update(self, tilemap, movement=(0, 0)):
        PhysicsEntity.update(self, tilemap, movement=movement)
        words = ['brick', 'desert', 'green', 'stone']
        for word in words:
            if f'{word}_l' in self.questitems and f'{word}_r' in self.questitems:
                self.questitems.remove(f'{word}_l')
                self.questitems.remove(f'{word}_r')
                self.questitems.append(f'{word}_full')
        if self.endurance < self.max_endurance:
            if self.endurance_recovery == 0:
                self.endurance = min(self.max_endurance, self.endurance + 1)
                self.endurance_recovery = 300
            else:
                self.endurance_recovery -= 1
        if not self.flip:
            self.weapon_pos = [self.rect().centerx - 4 + self.game.assets[self.weapon].get_width(),
                               self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]
        else:
            self.weapon_pos = [self.rect().centerx - 6 - self.game.assets[self.weapon].get_width(),
                               self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]
        self.time_in_air += 1
        if self.time_in_air > 350:
            if not self.game.dead:
                self.game.killer = 'Высота'
                self.game.display_shake = max(20, self.game.display_shake)
            self.game.dead += 1
        self.wall_slide = False
        if (self.collision_type['left'] or self.collision_type['right']) and self.time_in_air > 4:
            self.wall_slide = True
            self.time_in_air = 6
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collision_type['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        if self.collision_type['down']:
            self.time_in_air = 0
            self.limit_of_jumps = 1
        if not self.wall_slide:
            if self.time_in_air > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        if abs(self.attaking) in {60, 50}:
            for _ in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                particle_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=particle_velocity,
                             frame=random.randint(0, 7)))
        # Нормализация атаки
        if self.attaking > 0:
            self.attaking = max(0, self.attaking - 1)
        else:
            self.attaking = min(0, self.attaking + 1)
        # Направление рывка в атаке
        if abs(self.attaking) > 44:
            self.unvul = True
            self.velocity[0] = abs(self.attaking) / self.attaking * 6
            # После первых 10 кадров ускорения рывок заканчиваеться и скорость быстро нормализуеться. Также работает и как кулдаун атаки
            if abs(self.attaking) == 45:
                self.unvul = False
                self.velocity[0] *= 0.1
            particle_velocity = [abs(self.attaking) / self.attaking * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=particle_velocity,
                                                frame=random.randint(0, 7)))
        # Нормализация ускорения по горизонтали
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)

    def render(self, surface, offset=(0, 0)):
        if abs(self.attaking) < 46:
            PhysicsEntity.render(self, surface, offset=offset)
            # Рендеринг оружия
            if self.flip:
                surface.blit(pygame.transform.flip(self.game.assets[self.weapon], True, False), (
                    self.weapon_pos[0] + 8 - offset[0],
                    self.weapon_pos[1] + 4 - offset[1]))
            else:
                surface.blit(self.game.assets[self.weapon],
                             (self.weapon_pos[0] - 8 - offset[0],
                              self.weapon_pos[1] + 4 - offset[1]))


class Fighter(Player):
    def __init__(self, game, pos, size, choose):
        super().__init__(game, pos, size, choose)
        self.weapon = 'sword'
        self.life = 3
        self.max_life = 3
        self.max_mana = 0
        self.block = 1
        self.max_block = 1
        self.block_recovery_time = 0
        self.rage = False
        self.crit = 0.3
        self.dmg = 1

    def get_crit(self):
        return self.crit

    def attack(self):
        if not self.attaking:
            self.game.sfx['sword_attack'].play()
            if self.flip:
                self.attaking = -60
            else:
                self.attaking = 60

    def hit_check(self, projectile):
        if self.rect().collidepoint(projectile.get_pos()):
            self.game.projectiles.remove(projectile)
            if self.block == 0 or projectile.isunblockable():
                self.set_life(max(0, self.get_life() - 1))
                if not self.get_life():
                    self.game.dead += 1
                self.game.display_shake = max(15, self.game.display_shake)
                # Создание искр и частиц при попадании в игрока
                for _ in range(10 * projectile.get_shards()):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'bloody', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
            else:
                self.block = max(0, self.block - 1)
                self.endurance = max(0, self.endurance - 1)
                self.game.texts.append(
                    TextFrame('БЛОК', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, BLOCKCOLOR))
                self.game.sfx['weapon_block'].play()
                self.block_recovery_time = 300 // self.max_endurance
                for _ in range(8 * projectile.get_shards()):
                    angle = random.random() * math.pi * 2
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))

    def update(self, tilemap, movement=(0, 0)):
        words = ['brick', 'desert', 'green', 'stone']
        for word in words:
            if f'{word}_l' in self.questitems and f'{word}_r' in self.questitems:
                self.questitems.remove(f'{word}_l')
                self.questitems.remove(f'{word}_r')
                self.questitems.append(f'{word}_full')
        if self.endurance < self.max_endurance:
            if self.endurance_recovery == 0:
                self.endurance = min(self.max_endurance, self.endurance + 1)
                self.endurance_recovery = 500
            else:
                self.endurance_recovery -= 1
        if self.block_recovery_time:
            self.block_recovery_time = max(0, self.block_recovery_time - 1)
        else:
            if self.max_block and self.endurance:
                self.block = min(self.max_block, self.block + 1)
        super().update(tilemap=tilemap, movement=movement)

    def render(self, surface, offset=(0, 0)):
        super().render(surface=surface, offset=offset)
        if self.block_recovery_time % 2 != 0:
            weapon_mask = pygame.mask.from_surface(self.game.assets[self.weapon])
            weapon_mask_sur = pygame.surface.Surface(self.game.assets[self.weapon].get_size())
            weapon_mask.to_surface(weapon_mask_sur)
            weapon_mask_sur.set_colorkey((0, 0, 0))
            if self.flip:
                surface.blit(pygame.transform.flip(weapon_mask_sur, True, False),
                             (self.weapon_pos[0] - offset[0], self.weapon_pos[1] - offset[1]))
            else:
                surface.blit(weapon_mask_sur, (self.weapon_pos[0] - offset[0], self.weapon_pos[1] - offset[1]))


class Knight(Player):
    def __init__(self, game, pos, size, choose):
        super().__init__(game, pos, size, choose)
        self.life = 4
        self.max_life = 4
        self.max_mana = 0
        self.max_endurance = 4
        self.block = 1
        self.max_block = 1
        self.block_recovery_time = 0
        self.weapon = 'shield'
        self.dmg = 1

    def attack(self):
        if not self.attaking:
            self.game.sfx['shield_attack'].play()
            if self.flip:
                self.attaking = -60
            else:
                self.attaking = 60

    def hit_check(self, projectile):
        if not self.unvul:
            if self.rect().collidepoint(projectile.get_pos()):
                self.game.projectiles.remove(projectile)
                if not self.block:
                    self.set_life(max(0, self.get_life() - 1))
                    if not self.get_life():
                        self.game.dead += 1
                    self.game.display_shake = max(15, self.game.display_shake)
                    # Создание искр и частиц при попадании в игрока
                    for _ in range(10 * projectile.get_shards()):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'bloody', self.rect().center,
                                                            velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                      math.sin(angle + math.pi) * speed * 0.5],
                                                            frame=random.randint(0, 7)))
                else:
                    self.block = max(0, self.block - 1)
                    self.endurance = max(0, self.endurance - 1)
                    self.game.texts.append(
                        TextFrame('БЛОК', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, BLOCKCOLOR))
                    self.game.sfx['shield_block'].play()
                    if not self.block_recovery_time:
                        self.block_recovery_time = 300 // self.max_endurance
                    for _ in range(8 * projectile.get_shards()):
                        angle = random.random() * math.pi * 2
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))

    def get_shield_state(self):
        return self.block_cooldown

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3
                self.velocity[1] = -3
                self.time_in_air = 5
                self.limit_of_jumps = max(0, self.limit_of_jumps - 1)
                self.game.sfx['jump'].play()
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3
                self.velocity[1] = -3
                self.time_in_air = 5
                self.limit_of_jumps = max(0, self.limit_of_jumps - 1)
                self.game.sfx['jump'].play()
                return True
        elif self.limit_of_jumps:
            self.velocity[1] = -4
            self.time_in_air = 5
            self.limit_of_jumps -= 1
            self.game.sfx['jump'].play()
            return True

    def update(self, tilemap, movement=(0, 0)):
        words = ['brick', 'desert', 'green', 'stone']
        for word in words:
            if f'{word}_l' in self.questitems and f'{word}_r' in self.questitems:
                self.questitems.remove(f'{word}_l')
                self.questitems.remove(f'{word}_r')
                self.questitems.append(f'{word}_full')
        if self.endurance < self.max_endurance:
            if self.endurance_recovery == 0:
                self.endurance = min(self.max_endurance, self.endurance + 1)
                self.endurance_recovery = 350
            else:
                self.endurance_recovery -= 1
        if self.block_recovery_time:
            self.weapon = 'shield_cooldown'
            self.block_recovery_time = max(0, self.block_recovery_time - 1)
        else:
            if self.max_block and self.endurance:
                if self.weapon == 'shield_cooldown':
                    self.weapon = 'shield'
                    self.game.sfx['take_up_shield'].play()
                    self.block = min(self.max_block, self.block + 1)
        PhysicsEntity.update(self, tilemap=tilemap, movement=movement)
        if not self.flip:
            self.weapon_pos = [self.rect().centerx - 4 + self.game.assets[self.weapon].get_width(),
                               self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]
        else:
            self.weapon_pos = [self.rect().centerx - 6 - self.game.assets[self.weapon].get_width(),
                               self.rect().centery - self.game.assets[self.weapon].get_height() / 1.5]
        self.time_in_air += 1
        if self.time_in_air > 300 and self.action != 'wall_slide':
            if not self.game.dead:
                self.game.killer = 'Высота'
                self.game.display_shake = max(15, self.game.display_shake)
            self.game.dead += 1
        self.wall_slide = False
        if (self.collision_type['left'] or self.collision_type['right']) and self.time_in_air > 4:
            self.wall_slide = True
            self.time_in_air = 6
            self.velocity[1] = min(self.velocity[1], 0.6)
            if self.collision_type['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        if self.collision_type['down']:
            self.time_in_air = 0
            self.limit_of_jumps = 1
        if not self.wall_slide:
            if self.time_in_air > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        if abs(self.attaking) in {60, 55}:
            for _ in range(2):
                self.game.sparks.append(Spark(self.rect().bottomleft, (
                    -1 * random.random() * math.pi / 2 if self.velocity[0] > 0 else (
                            math.pi + random.random() * math.pi / 2)), 2 + random.random()))
        if abs(self.attaking) == 50:
            for _ in range(0):
                self.game.sparks.append(Spark((self.rect().centerx + 18 * self.velocity[0], self.rect().centery), (
                    random.random() * math.pi / 2 if self.velocity[0] > 0 else (
                            math.pi + random.random() * math.pi / 2)), 2 + random.random()))
        # Нормализация атаки
        if self.attaking > 0:
            self.attaking = max(0, self.attaking - 1)
        else:
            self.attaking = min(0, self.attaking + 1)
        # Направление рывка в атаке
        if abs(self.attaking) > 50:
            self.velocity[0] = abs(self.attaking) / self.attaking * 10
            # После первых 10 кадров ускорения рывок заканчиваеться и скорость быстро нормализуеться. Также работает и как кулдаун атаки
            if abs(self.attaking) == 51:
                self.velocity[0] *= 0.01
            self.game.sparks.append(Spark(self.rect().bottomleft, (
                -1 * random.random() * math.pi / 2 if self.velocity[0] > 0 else (
                        math.pi + random.random() * math.pi / 2)), 2 + random.random()))
        # Нормализация ускорения по горизонтали
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)

    def render(self, surface, offset=(0, 0)):
        surface.blit(pygame.transform.flip(self.animation.shot(), self.flip, False), (
            self.pos[0] - offset[0] + self.animation_offset[0], self.pos[1] - offset[1] + self.animation_offset[1]))
        # Рендеринг оружия
        if self.flip:
            surface.blit(pygame.transform.flip(self.game.assets[self.weapon], True, False), (
                self.weapon_pos[0] - 5 - offset[0], self.weapon_pos[1] + 5 - offset[1]))
        else:
            surface.blit(self.game.assets[self.weapon],
                         (self.weapon_pos[0] + 5 - offset[0], self.weapon_pos[1] + 5 - offset[1]))


class Mage(Player):
    def __init__(self, game, pos, size, choose):
        super().__init__(game, pos, size, choose)
        self.weapon = 'magic_staff'
        self.mana = 5
        self.max_mana = 10
        self.max_endurance = 0
        self.spellbook = [ForceBolt(self), FireBall(self), IceArmor(self), ThunderStrike(self)]

    def attack(self):
        if not self.attaking:
            self.game.sfx['mage_attack'].play()
            if self.flip:
                self.attaking = -60
            else:
                self.attaking = 60

    def hit_check(self, projectile):
        if self.rect().collidepoint(projectile.get_pos()):
            self.game.projectiles.remove(projectile)
            if self.block == 0 or projectile.isunblockable():
                self.set_life(max(0, self.get_life() - 1))
                if not self.get_life():
                    self.game.dead += 1
                self.game.display_shake = max(15, self.game.display_shake)
                # Создание искр и частиц при попадании в игрока
                for _ in range(10 * projectile.get_shards()):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'bloody', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
            else:
                self.block = max(0, self.block - 1)
                self.game.texts.append(
                    TextFrame('БЛОК', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, BLOCKCOLOR))
                self.game.sfx['ice_block'].play()
                for _ in range(8 * projectile.get_shards()):
                    angle = random.random() * math.pi * 2
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))

    def update(self, tilemap, movement=(0, 0)):
        words = ['brick', 'desert', 'green', 'stone']
        for word in words:
            if f'{word}_l' in self.questitems and f'{word}_r' in self.questitems:
                self.questitems.remove(f'{word}_l')
                self.questitems.remove(f'{word}_r')
                self.questitems.append(f'{word}_full')
        if self.mana < self.max_mana:
            if self.mana_recovery == 0:
                self.mana = min(self.max_mana, self.mana + 1)
                self.mana_recovery = 200
            else:
                self.mana_recovery -= 1
        super().update(tilemap=tilemap, movement=movement)


class Enemy(PhysicsEntity):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.walking = 0
        self.get_hit_recently = 0
        self.life = 1
        self.max_life = 1
        self.attack_cooldown_time = 0
        self.cooldown = 200
        self.score = 1

    def get_score(self):
        return self.score

    def get_pos(self):
        return self.pos

    def hit_check(self, projectile):
        if projectile.who == 'Player':
            if self.rect().collidepoint(projectile.get_pos()):
                if not self.get_hit_recently:
                    self.set_life(max(0, self.get_life() - projectile.get_damage()))
                    self.game.texts.append(
                        TextFrame('HIT', pygame.font.Font('Blackcraft.ttf', 25), self.pos, duration=50,
                                  color=(0, 0, 0)))
                    # Создание искр и частиц при попадании
                    for _ in range(5 * projectile.get_shards()):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'bloody', self.rect().center,
                                                            velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                      math.sin(angle + math.pi) * speed * 0.5],
                                                            frame=random.randint(0, 7)))
                    if not self.get_life():
                        return [True, True]
                    else:
                        return [False, True]
            else:
                return [False, False]
        else:
            return [False, False]

    def set_life(self, life):
        self.life = life

    def get_life(self):
        return self.life

    def set_maxlife(self, life):
        self.max_life = life

    def get_maxlife(self):
        return self.max_life

    def update(self, tilemap, movement=(0, 0), shards=1, proj='projectile', sound='magic_missle', radius=1):
        # Откат атаки
        if self.attack_cooldown_time:
            self.attack_cooldown_time = max(0, self.attack_cooldown_time - 1)
        # Невосприимчивость к урону
        if self.get_hit_recently:
            self.get_hit_recently = max(0, self.get_hit_recently - 1)
        # Модель перемещения врага базовая
        distance = ((self.game.player.pos[0] - self.pos[0]) / tilemap.tilesize,
                    (self.game.player.pos[1] - self.pos[1]) / tilemap.tilesize)
        if not self.attack_cooldown_time and abs(distance[1]) <= 1 and abs(distance[0]) <= radius and distance[0] * \
                self.velocity[0] >= 0:
            if self.flip:
                self.game.sfx[sound].play()
                self.game.projectiles.append(
                    Projectile(pygame.transform.flip(self.game.assets[proj].convert_alpha(), True, False),
                               self.rect().centerx - 5,
                               self.rect().centery, 1, shards, (-1.5, 0),
                               distance=radius * 20))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5 + math.pi,
                              2 + random.random()))
            if not self.flip:
                self.game.sfx[sound].play()
                self.game.projectiles.append(
                    Projectile(self.game.assets[proj], self.rect().centerx + 5, self.rect().centery, 1, shards,
                               (1.5, 0),
                               distance=radius * 20))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5, 2 + random.random()))
            self.attack_cooldown_time = self.cooldown
        elif self.walking:
            if tilemap.obstacle_check((self.rect().centerx + (-15 if self.flip else 15), self.pos[1] + 35)):
                if self.collision_type['left'] or self.collision_type['right']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            # Выстрел только когда остановился и всего один кадр на проверку
            if not self.walking:
                if abs(distance[1]) <= radius and abs(distance[0]) <= radius:
                    pass
        elif random.random() < 0.01:
            self.walking = random.randint(50, 150)
        super().update(tilemap, movement=movement)
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        # Попал ВОИН
        if type(self.game.player) is Fighter:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(30, self.game.display_shake)
                    if not self.get_hit_recently:
                        if random.random() < self.game.player.get_crit():
                            self.set_life(max(0, self.get_life() - 2 * self.game.player.dmg))
                            self.game.texts.append(
                                TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, CRITCOLOR))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Рыцарь
        elif type(self.game.player) is Knight:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Маг
        elif type(self.game.player) is Mage:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - 1))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Ниндзя
        elif type(self.game.player) is Ninja:
            if abs(self.game.player.attaking) >= 45:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        if self.flip == self.game.player.flip:
                            self.game.texts.append(
                                TextFrame('В СПИНУ', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 100, CRITCOLOR))
                            self.set_life(max(0, self.get_life() - self.game.player.dmg * self.game.player.backstab))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi / 2, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, 3 * math.pi / 2, 3 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False

    def render(self, surface, offset=(0, 0), weapon='magic_staff'):
        super().render(surface, offset=offset)
        # Анимация неуязвимости к урону
        if self.get_hit_recently and self.get_hit_recently % 5 == 0:
            self.game.display.blit(self.mask, dest=(self.rect().x - offset[0], self.rect().y - offset[1]))
        # Рендеринг лайфбара
        if self.__class__ not in [Ghost, Slime]:
            elx = self.rect().centerx - offset[0] - self.get_life() * 14 / 2
            ely = self.rect().centery - self.rect().height / 2 - 20 - offset[1]
            for il in range(self.get_life()):
                surface.blit(self.game.assets['enemy_life'], (elx + il * 8, ely))
            # Рендеринг оружия врага
            if self.flip:
                surface.blit(pygame.transform.flip(self.game.assets[weapon], True, False), (
                    self.rect().centerx - 3 - self.game.assets[weapon].get_width() - offset[0],
                    self.rect().centery - self.game.assets[weapon].get_height() / 1.5 - offset[1]))
            else:
                surface.blit(self.game.assets[weapon],
                             (self.rect().centerx + 3 - offset[0],
                              self.rect().centery - self.game.assets[weapon].get_height() / 1.5 - offset[1]))


class Goblin(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.score = 10

    def render(self, surface, offset=(0, 0), weapon='spear'):
        super().render(surface=surface, offset=offset, weapon=weapon)

    def update(self, tilemap, movement=(0, 0), shards=1, proj='wave', sound='spear_attack', radius=1):
        return super().update(tilemap=tilemap, movement=movement, shards=shards, proj=proj, sound=sound, radius=radius)


class GoblinMedium(Goblin):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.life = 2
        self.max_life = 2
        self.score = 15


class GoblinHeavy(Goblin):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.life = 3
        self.max_life = 3
        self.score = 20


class GoblinMage(Goblin):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.score = 15

    def render(self, surface, offset=(0, 0), weapon='magic_staff'):
        super().render(surface=surface, offset=offset, weapon='magic_staff')

    def update(self, tilemap, movement=(0, 0), shards=2, proj='magic_missle', sound='magic_missle', radius=6):
        if tilemap.obstacle_check((self.rect().centerx + (-15 if self.flip else 15), self.pos[1] + 35)):
            if self.collision_type['left'] or self.collision_type['right'] or random.random() < 0.2:
                self.flip = not self.flip
            else:
                movement = (movement[0] + 0.5 if (self.game.player.pos[0] - self.pos[0]) > 0 else -0.5, movement[1])
        return super().update(tilemap=tilemap, movement=movement, proj='magic_missle', sound=sound, radius=radius)


class GoblinWarlord(Goblin):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.life = 3
        self.max_life = 3
        self.cooldown = 125
        self.score = 30
        self.crit = 0.2
        self.dmg = 1

    def render(self, surface, offset=(0, 0), weapon='axe'):
        super().render(surface=surface, offset=offset, weapon='axe')

    def update(self, tilemap, movement=(0, 0), shards=2, proj='wave', sound='axe_attack', radius=2):
        # Откат атаки
        crit = random.random() < self.crit
        if self.attack_cooldown_time:
            self.attack_cooldown_time = max(0, self.attack_cooldown_time - 1)
        # Невосприимчивость к урону
        if self.get_hit_recently:
            self.get_hit_recently = max(0, self.get_hit_recently - 1)
        # Модель перемещения врага базовая
        distance = ((self.game.player.pos[0] - self.pos[0]) / tilemap.tilesize,
                    (self.game.player.pos[1] - self.pos[1]) / tilemap.tilesize)
        if not self.attack_cooldown_time and abs(distance[1]) <= 1 and abs(distance[0]) <= radius and distance[0] * \
                self.velocity[0] >= 0:
            if self.flip:
                self.game.sfx[sound].play()
                self.game.projectiles.append(
                    Projectile(pygame.transform.flip(self.game.assets[proj].convert_alpha(), True, False),
                               self.rect().centerx - 5,
                               self.rect().centery, (self.dmg * 2 if crit else self.dmg), shards,
                               (-1.5, 0),
                               distance=radius * 20))
                if crit:
                    self.game.texts.append(TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, ECRITCOLOR))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5 + math.pi,
                              2 + random.random()))
            if not self.flip:
                self.game.sfx[sound].play()
                self.game.projectiles.append(
                    Projectile(self.game.assets[proj], self.rect().centerx + 5, self.rect().centery,
                               (self.dmg * 2 if crit else self.dmg), shards,
                               (1.5, 0),
                               distance=radius * 20))
                if crit:
                    self.game.texts.append(TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, ECRITCOLOR))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5, 2 + random.random()))
            self.attack_cooldown_time = self.cooldown
        elif self.walking:
            if tilemap.obstacle_check((self.rect().centerx + (-15 if self.flip else 15), self.pos[1] + 35)):
                if self.collision_type['left'] or self.collision_type['right'] or random.random() < 0.2:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] + 0.5 if distance[0] > 0 else -0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            # Выстрел только когда остановился и всего один кадр на проверку
            if not self.walking:
                if abs(distance[1]) <= radius and abs(distance[0]) <= radius:
                    pass
        elif random.random() < 0.01:
            self.walking = random.randint(50, 100)
        super().update(tilemap, movement=movement)
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        # Попал ВОИН
        if type(self.game.player) is Fighter:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(30, self.game.display_shake)
                    if not self.get_hit_recently:
                        if random.random() < self.game.player.get_crit():
                            self.set_life(max(0, self.get_life() - 2 * self.game.player.dmg))
                            self.game.texts.append(
                                TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, CRITCOLOR))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Рыцарь
        elif type(self.game.player) is Knight:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Маг
        elif type(self.game.player) is Mage:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - 1))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Ниндзя
        elif type(self.game.player) is Ninja:
            if abs(self.game.player.attaking) >= 45:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        if self.flip == self.game.player.flip:
                            self.game.texts.append(
                                TextFrame('В СПИНУ', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 100, CRITCOLOR))
                            self.set_life(max(0, self.get_life() - self.game.player.dmg * self.game.player.backstab))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi / 2, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, 3 * math.pi / 2, 3 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False


class Zombie(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.cooldown = 50
        self.score = 15
        self.life = 2
        self.max_life = 2

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=1, proj='', sound='unarmed_attack', radius=1):
        return super().update(tilemap=tilemap, movement=movement, sound=sound)


class Lich(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.life = 5
        self.max_life = 5
        self.score = 60
        self.dmg = 2
        self.crit = 0.1

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=5, proj='fire_ball', sound='fireball_attack', radius=6):
        # Откат атаки
        crit = random.random() < self.crit
        if self.attack_cooldown_time:
            self.attack_cooldown_time = max(0, self.attack_cooldown_time - 1)
        # Невосприимчивость к урону
        if self.get_hit_recently:
            self.get_hit_recently = max(0, self.get_hit_recently - 1)
        # Модель перемещения врага базовая
        distance = ((self.game.player.pos[0] - self.pos[0]) / tilemap.tilesize,
                    (self.game.player.pos[1] - self.pos[1]) / tilemap.tilesize)
        if not self.attack_cooldown_time and abs(distance[1]) <= 1 and abs(distance[0]) <= radius and distance[0] * \
                self.velocity[0] >= 0:
            if self.flip:
                self.game.sfx[sound].play()
                self.game.projectiles.append(
                    Projectile(pygame.transform.flip(self.game.assets[proj].convert_alpha(), True, False),
                               self.rect().centerx - 5,
                               self.rect().centery, (self.dmg * 2 if crit else self.dmg), shards,
                               (-4, 0),
                               distance=radius * 40))
                if crit:
                    self.game.texts.append(TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, ECRITCOLOR))
                for _ in range(10):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5 + math.pi,
                              2 + random.random()))
            if not self.flip:
                self.game.sfx[sound].play()
                self.game.projectiles.append(
                    Projectile(self.game.assets[proj], self.rect().centerx + 5, self.rect().centery,
                               (self.dmg * 2 if crit else self.dmg), shards,
                               (4, 0),
                               distance=radius * 40))
                if crit:
                    self.game.texts.append(TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, ECRITCOLOR))
                for _ in range(10):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5, 2 + random.random()))
            self.attack_cooldown_time = self.cooldown
        elif self.walking:
            if tilemap.obstacle_check((self.rect().centerx + (-15 if self.flip else 15), self.pos[1] + 35)):
                if self.collision_type['left'] or self.collision_type['right'] or random.random() < 0.3:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] + 0.5 if distance[0] > 0 else -0.5, movement[1])
            else:
                if distance[0] > 0:
                    self.flip = False
                else:
                    self.flip = True
            self.walking = max(0, self.walking - 1)
            # Выстрел только когда остановился и всего один кадр на проверку
            if not self.walking:
                if abs(distance[1]) <= radius and abs(distance[0]) <= radius:
                    pass
        elif random.random() < 0.01:
            self.walking = random.randint(50, 150)
        super().update(tilemap, movement=movement)
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        # Попал ВОИН
        if type(self.game.player) is Fighter:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(30, self.game.display_shake)
                    if not self.get_hit_recently:
                        if random.random() < self.game.player.get_crit():
                            self.set_life(max(0, self.get_life() - 2 * self.game.player.dmg))
                            self.game.texts.append(
                                TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125, CRITCOLOR))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Рыцарь
        elif type(self.game.player) is Knight:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Маг
        elif type(self.game.player) is Mage:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - 1))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Ниндзя
        elif type(self.game.player) is Ninja:
            if abs(self.game.player.attaking) >= 45:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        if self.flip == self.game.player.flip:
                            self.game.texts.append(
                                TextFrame('В СПИНУ', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 100, CRITCOLOR))
                            self.set_life(max(0, self.get_life() - self.game.player.dmg * self.game.player.backstab))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi / 2, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, 3 * math.pi / 2, 3 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False


class Ghost(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.score = 300
        self.cooldown = 30

    def render(self, surface, offset=(0, 0), weapon='scythe'):
        super().render(surface=surface, offset=offset, weapon='scythe')

    def update(self, tilemap, movement=(0, 0), shards=2, proj='projectile', sound='scythe_attack', radius=2):
        super().update(tilemap=tilemap, movement=movement, proj=proj, sound=sound)


class Slime(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.score = 15
        self.cooldown = 30

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=1, proj='', sound='unarmed_attack', radius=1):
        return super().update(tilemap=tilemap, movement=movement, sound=sound)


class Flower(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.idle = 20
        self.set_action('idle')
        self.score = 10

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=1, proj='magic_missle', sound='unarmed_attack', radius=8):
        # Откат атаки
        if self.attack_cooldown_time:
            self.attack_cooldown_time = max(0, self.attack_cooldown_time - 1)
        # Невосприимчивость к урону
        if self.get_hit_recently:
            self.get_hit_recently = max(0, self.get_hit_recently - 1)
        # Модель перемещения врага базовая
        distance = ((self.game.player.pos[0] - self.pos[0]) / tilemap.tilesize,
                    (self.game.player.pos[1] - self.pos[1]) / tilemap.tilesize)
        if not self.attack_cooldown_time and abs(distance[1]) <= 1 and abs(distance[0]) <= radius and distance[0] * \
                self.velocity[0] >= 0:
            self.game.sfx[sound].play()
            if distance[0] < 0:
                self.flip = not self.flip
            if self.flip:
                self.game.projectiles.append(
                    Projectile(pygame.transform.flip(self.game.assets[proj].convert_alpha(), True, False),
                               self.rect().centerx - 5,
                               self.rect().centery, 1, shards, (-1.5, 0),
                               distance=radius * 20))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5 + math.pi,
                              2 + random.random()))
            if not self.flip:
                self.game.projectiles.append(
                    Projectile(self.game.assets[proj], self.rect().centerx + 5, self.rect().centery, 1, shards,
                               (1.5, 0),
                               distance=radius * 10))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5, 2 + random.random()))
            self.attack_cooldown_time = self.cooldown
        elif random.random() < 0.01:
            self.idle = random.randint(50, 150)
        # Попал ВОИН
        if type(self.game.player) is Fighter:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(30, self.game.display_shake)
                    if not self.get_hit_recently:
                        if random.random() < self.game.player.get_crit():
                            self.set_life(max(0, self.get_life() - 2 * self.game.player.dmg))
                            self.game.texts.append(
                                TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125,
                                          CRITCOLOR))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Рыцарь
        elif type(self.game.player) is Knight:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Маг
        elif type(self.game.player) is Mage:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - 1))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Ниндзя
        elif type(self.game.player) is Ninja:
            if abs(self.game.player.attaking) >= 45:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        if self.flip == self.game.player.flip:
                            self.game.texts.append(
                                TextFrame('В СПИНУ', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 100,
                                          CRITCOLOR))
                            self.set_life(max(0, self.get_life() - self.game.player.dmg * self.game.player.backstab))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi / 2, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, 3 * math.pi / 2, 3 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False


class FlowerPredatory(Flower):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.life = 2
        self.max_life = 2
        self.score = 20

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        return super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=1, proj='magic_missle', sound='unarmed_attack', radius=8):
        # Откат атаки
        if self.attack_cooldown_time:
            self.attack_cooldown_time = max(0, self.attack_cooldown_time - 1)
        # Невосприимчивость к урону
        if self.get_hit_recently:
            self.get_hit_recently = max(0, self.get_hit_recently - 1)
        # Модель перемещения врага базовая
        distance = ((self.game.player.pos[0] - self.pos[0]) / tilemap.tilesize,
                    (self.game.player.pos[1] - self.pos[1]) / tilemap.tilesize)
        if not self.attack_cooldown_time and abs(distance[1]) <= 1 and abs(distance[0]) <= radius and distance[0] * \
                self.velocity[0] >= 0:
            self.game.sfx[sound].play()
            if distance[0] < 0:
                self.flip = True
            else:
                self.flip = False
            if self.flip:
                self.game.projectiles.append(
                    Projectile(pygame.transform.flip(self.game.assets[proj].convert_alpha(), True, False),
                               self.rect().centerx - 5,
                               self.rect().centery, 1, shards, (-1.5, 0),
                               distance=radius * 20))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5 + math.pi,
                              2 + random.random()))
            if not self.flip:
                self.game.projectiles.append(
                    Projectile(self.game.assets[proj], self.rect().centerx + 5, self.rect().centery, 1, shards,
                               (1.5, 0),
                               distance=radius * 20))
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1].get_pos(), random.random() - 0.5, 2 + random.random()))
            self.attack_cooldown_time = self.cooldown
        elif random.random() < 0.01:
            self.idle = random.randint(50, 150)
        # Попал ВОИН
        if type(self.game.player) is Fighter:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(30, self.game.display_shake)
                    if not self.get_hit_recently:
                        if random.random() < self.game.player.get_crit():
                            self.set_life(max(0, self.get_life() - 2 * self.game.player.dmg))
                            self.game.texts.append(
                                TextFrame('--КРИТ--', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 125,
                                          CRITCOLOR))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Рыцарь
        elif type(self.game.player) is Knight:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Маг
        elif type(self.game.player) is Mage:
            if abs(self.game.player.attaking) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        self.set_life(max(0, self.get_life() - 1))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False
        # Попал Ниндзя
        elif type(self.game.player) is Ninja:
            if abs(self.game.player.attaking) >= 45:
                if self.rect().colliderect(self.game.player.rect()):
                    self.game.display_shake = max(20, self.game.display_shake)
                    if not self.get_hit_recently:
                        if self.flip == self.game.player.flip:
                            self.game.texts.append(
                                TextFrame('В СПИНУ', pygame.font.Font('Blackcraft.ttf', 25), self.pos, 100,
                                          CRITCOLOR))
                            self.set_life(max(0, self.get_life() - self.game.player.dmg * self.game.player.backstab))
                        else:
                            self.set_life(max(0, self.get_life() - self.game.player.dmg))
                        self.get_hit_recently = 50
                        self.mask = pygame.mask.from_surface(self.animation.shot())
                        self.mask = self.mask.to_surface()
                        self.mask.set_colorkey((0, 0, 0))
                        # Создание искр и частиц при попадании во врага
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi / 2, 3 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, 3 * math.pi / 2, 3 + random.random()))
                    if not self.get_life():
                        # Создание искр и частиц при убийстве врага
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                        return True
                    else:
                        return False


class Mummy(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.life = 3
        self.max_life = 3
        self.score = 20
        self.cooldown = 150

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=1, proj='', sound='unarmed_attack', radius=1):
        return super().update(tilemap=tilemap, movement=movement, sound=sound)


class Rat(Enemy):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.score = 5

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')

    def update(self, tilemap, movement=(0, 0), shards=1, proj='', sound='unarmed_attack', radius=1):
        if random.random() < 0.03:
            self.walking = random.randint(10, 50)
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        return super().update(tilemap=tilemap, movement=movement, sound=sound)


class RatPlague(Rat):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)
        self.score = 10

    def render(self, surface, offset=(0, 0), weapon='unarmed'):
        super().render(surface=surface, offset=offset, weapon='unarmed')
