import random
from scripts.entities import *


def drop_item(game, enemy):
    i = choose_drop(enemy)
    if i == 'lifep':
        game.items.append(Item(game, 'lifep', enemy.pos, (16, 30), ))
    elif i == 'manap':
        game.items.append(Item(game, 'manap', enemy.pos, (16, 30), ))
    elif i == 'endurancep':
        game.items.append(Item(game, 'endurancep', enemy.pos, (16, 30), ))
    elif i == 'coin':
        game.items.append(Item(game, 'coin', enemy.pos, (23, 23), ))
    elif i == 'None':
        pass
    else:
        pass


def use_item(game, item, user):
    if item.collide_check(user):
        if item.type == 'brick_l':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'brick_r':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'desert_l':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'desert_r':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'green_l':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'green_r':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'stone_l':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'stone_r':
            game.sfx['questitem'].play()
            user.questitems.append(item.type)
            game.texts.append(TextFrame('КВЕСТ ОБНОВЛЁН', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100, color=(213, 111, 102)))
            game.questitems.remove(item)
        elif item.type == 'iexit':
            game.sfx['exit'].play()
            if game.level == 'green1' and 'green_l' in game.player.questitems:
                game.load_level('green2')
                game.level = 'green2'
            elif game.level == 'green2' and 'green_full' in game.player.questitems:
                game.level = 'stone1'
                game.load_level('stone1')
            elif game.level == 'stone1' and 'stone_l' in game.player.questitems:
                game.level = 'stone2'
                game.load_level('stone2')
            elif game.level == 'stone2' and 'stone_full' in game.player.questitems:
                game.level = 'brick1'
                game.load_level('brick1')
            elif game.level == 'brick1' and 'brick_l' in game.player.questitems:
                game.level = 'brick2'
                game.load_level('brick2')
            elif game.level == 'brick2' and 'brick_full' in game.player.questitems:
                game.level = 'desert1'
                game.load_level('desert1')
            elif game.level == 'desert1' and 'desert_l' in game.player.questitems:
                game.level = 'desert2'
                game.load_level('desert2')
            elif game.level == 'desert2' and 'desert_full' in game.player.questitems:
                game.level = 'win'
                game.load_level('win')

        elif item.type == 'lifep':
            if user.get_life() < user.get_maxlife():
                game.sfx['lifep'].play()
                user.set_life(min(user.get_maxlife(), user.get_life() + 1))
                game.texts.append(TextFrame('+1HP', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100))
                game.items.remove(item)
        elif item.type == 'manap':
            if user.get_mana() < user.get_maxmana():
                game.sfx['manap'].play()
                user.set_mana(min(user.get_maxmana(), user.get_mana() + 2))
                game.texts.append(TextFrame('+2MP', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100))
                game.items.remove(item)
        elif item.type == 'endurancep':
            if user.get_endurance() < user.get_maxendurance():
                game.sfx['endurancep'].play()
                user.set_endurance(min(user.get_maxendurance(), user.get_endurance() + 2))
                game.texts.append(TextFrame('+2ED', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100))
                game.items.remove(item)
        elif item.type == 'coin':
            game.sfx['powerup'].play()
            game.score += 25
            game.texts.append(TextFrame('+100', pygame.font.Font('Blackcraft.ttf', 20), user.pos, duration=100))
            game.items.remove(item)
        elif item.type == 'None':
            pass
        else:
            pass


def choose_drop(enemy):
    chance = random.random()
    if enemy.__class__ == Goblin:
        if chance < 0.2:
            return 'lifep'
        else:
            return 'None'
    elif enemy.__class__ == GoblinMedium:
        if chance < 0.3:
            return 'lifep'
        else:
            return 'None'
    elif enemy.__class__ == GoblinHeavy:
        if chance < 0.4:
            return 'lifep'
        else:
            return 'None'
    elif enemy.__class__ == GoblinMage:
        if chance < 0.5:
            return 'manap'
        else:
            if chance < 0.7:
                return 'lifep'
            else:
                return 'None'
    elif enemy.__class__ == GoblinWarlord:
        if chance < 0.5:
            return 'lifep'
        else:
            return 'endurancep'
    elif enemy.__class__ == Zombie:
        if chance < 0.1:
            return 'lifep'
        elif chance < 0.2:
            return 'endurancep'
        else:
            return 'None'
    elif enemy.__class__ == Lich:
        if chance < 0.3:
            return 'coin'
        else:
            return 'manap'
    elif enemy.__class__ == Ghost:
        if chance < 0.001:
            return 'coin'
        else:
            return 'None'
    elif enemy.__class__ == Slime:
        if chance < 0.4:
            return 'lifep'
        else:
            return 'None'
    elif enemy.__class__ == Flower:
        return 'None'
    elif enemy.__class__ == FlowerPredatory:
        return 'None'
    elif enemy.__class__ == Mummy:
        if chance < 0.2:
            return 'lifep'
        elif chance < 0.4:
            return 'endurancep'
        else:
            return 'None'
    elif enemy.__class__ == Rat:
        return 'None'
    elif enemy.__class__ == RatPlague:
        return 'None'
