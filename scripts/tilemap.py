import pygame
import json

PHYS_TYPES = {'grass', 'glass', 'stone', 'desert_brick', 'brick', 'desert_small_brick', 'ice', 'smooth_stone', 'desert'}
NEAR_OFFSETS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, 0)]


class Tilemap:
    def __init__(self, game, tilesize=48):
        self.game = game
        self.tilesize = tilesize
        self.tilemap = {}
        self.tiles_offgrid = []

    def obstacle_check(self, pos):
        tile_pos = str(int(pos[0] // self.tilesize)) + ';' + str(int(pos[1] // self.tilesize))
        if tile_pos in self.tilemap:
            if self.tilemap[tile_pos]['type'] in PHYS_TYPES:
                return self.tilemap[tile_pos]

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.tiles_offgrid.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.tiles_offgrid.remove(tile)
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                # Копирование информации с карты чтобы не работать с оригиналом
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                # Получение координат тайла в пикселях
                matches[-1]['pos'][0] *= self.tilesize
                matches[-1]['pos'][1] *= self.tilesize
                if not keep:
                    del self.tilemap[loc]
        return matches

    def render(self, surface, offset=(0, 0)):
        for tile in self.tiles_offgrid:
            surface.blit(self.game.assets[tile['type']][tile['variant']],
                         (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        for x in range(offset[0] // self.tilesize, (offset[0] + surface.get_width()) // self.tilesize + 1):
            for y in range(offset[1] // self.tilesize, (offset[1] + surface.get_height()) // self.tilesize + 1):
                tile_coords = str(x) + ';' + str(y)
                if tile_coords in self.tilemap:
                    tile = self.tilemap[tile_coords]
                    surface.blit(self.game.assets[tile['type']][tile['variant']],
                                 (tile['pos'][0] * self.tilesize - offset[0],
                                  tile['pos'][1] * self.tilesize - offset[1]))

    def tiles_around(self, pos):
        tiles = []
        tile_pos = (int(pos[0] // self.tilesize), int(pos[1] // self.tilesize))
        for offset in NEAR_OFFSETS:
            check = str(tile_pos[0] + offset[0]) + ';' + str(tile_pos[1] + offset[1])
            if check in self.tilemap:
                tiles.append(self.tilemap[check])
        return tiles

    def phys_tiles_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYS_TYPES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tilesize, tile['pos'][1] * self.tilesize, self.tilesize,
                                         self.tilesize))
        return rects

    def save(self, path):
        fout = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tiles_offgrid': self.tiles_offgrid, 'tile_size': self.tilesize}, fout)
        fout.close()

    def load(self, path):
        fin = open(path, 'r')
        data = json.load(fin)
        fin.close()
        self.tilemap = data['tilemap']
        self.tiles_offgrid = data['tiles_offgrid']
        self.tilesize = data['tile_size']
