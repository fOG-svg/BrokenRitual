import math


class Projectile:
    def __init__(self, image, x, y, dmg=1, shards=1, velocity=(0, 0), distance=360, unblockable=False, who='Enemy'):
        self.image = image
        self.x = x
        self.y = y
        self.damage = dmg
        self.shards = shards
        self.velocity = velocity
        self.distance = distance
        self.unblockable = unblockable
        self.who = who

    def get_damage(self):
        return self.damage

    def get_pos(self):
        return self.x, self.y

    def get_shards(self):
        return self.shards

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()

    def get_velocity(self):
        return self.velocity

    def set_distance(self, dist):
        self.distance = dist

    def update(self):
        self.distance = max(0, self.distance - 1)
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def isdead(self):
        if self.distance > 0:
            return False
        else:
            return True

    def render(self, surface, offset=(0, 0)):
        surface.blit(self.image,
                     (self.x - self.get_width() / 2 - offset[0], self.y - self.get_height() / 2 - offset[1]))

    def isunblockable(self):
        return self.unblockable
