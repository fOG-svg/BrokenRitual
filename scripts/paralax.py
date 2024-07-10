import random


class Cloud:
    def __init__(self, img, pos, speed, layer):
        self.image = img
        self.pos = list(pos)
        self.speed = speed
        self.layer = layer

    def update(self):
        self.pos[0] += self.speed

    def render(self, surface, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.layer, self.pos[1] - offset[1] * self.layer)
        surface.blit(self.image,
                     (render_pos[0] % (surface.get_width() + self.image.get_width()) - self.image.get_width(),
                      render_pos[1] % (surface.get_height() + self.image.get_height()) - self.image.get_height()))


class Clouds:
    def __init__(self, images, count=10):
        self.clouds = []
        for i in range(count):
            self.clouds.append(Cloud(random.choice(images), (random.random() * 9999, random.random() * 200),
                                     random.random() * 0.05 - 0.05, random.random() * 0.7 + 0.1))
        self.clouds.sort(key=lambda x: x.layer)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surface, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surface, offset=offset)
