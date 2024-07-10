import pygame


class Slider:
    def __init__(self, image, x, y, bar):
        self.w, self.h = image[0].get_width(), image[0].get_height()
        self.bar = bar
        self.image = image
        self.rectinc = pygame.Rect(0, 0, 19, 24)
        self.rectinc.topleft = (x, y)
        self.rectdec = pygame.Rect(0, 0, 19, 24)
        self.rectdec.topleft = (x + self.w - 19, y)
        self.clickedinc = False
        self.clickeddec = False

    def draw(self, surface):
        surface.blit(self.image[self.bar], (self.rectinc.x, self.rectinc.y))

    def get_status(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rectinc.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.clickedinc = True
                self.bar = max(0, self.bar - 1)
        if self.rectdec.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.clickeddec = True
                self.bar = min(10, self.bar + 1)
        return (self.clickedinc, self.clickeddec)
