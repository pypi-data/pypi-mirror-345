import sdl2, math

from .main import SpawnBox

'''
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
'''

class Entity(object):
    def __init__(self, window: SpawnBox, width = 20, height = 20, x = 0, y = 0, color = (255, 255, 255, 255)):
        self.window = window
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = color
        self.rect = sdl2.SDL_FRect(self.x, self.y, self.width, self.height)
    def draw(self):
        sdl2.SDL_SetRenderDrawColor(self.window.renderer, self.color[0], self.color[1], self.color[2], self.color[3])
        self.rect = sdl2.SDL_FRect(self.x, self.y, self.width, self.height)
        sdl2.SDL_RenderDrawRectF(self.window.renderer, self.rect)
        sdl2.SDL_RenderFillRectF(self.window.renderer, self.rect)
        self.rect = sdl2.SDL_FRect(self.x, self.y, self.width, self.height)
    def collide(self, ent):
        leftA = self.rect.x
        rightA = self.rect.x + self.rect.w
        topA = self.rect.y
        bottomA = self.rect.y + self.rect.h
        leftB = ent.rect.x
        rightB = ent.rect.x + ent.rect.w
        topB = ent.rect.y
        bottomB = ent.rect.y + ent.rect.h
        if bottomA <= topB:
            return False
        if topA >= bottomB:
            return False
        if rightA <= leftB:
            return False
        if leftA >= rightB:
            return False
        return True
    def center(self):
        self.center_x()
        self.center_y()
    def center_x(self):
        self.x = self.window.width / 2 - self.width / 2
    def center_y(self):
        self.y = self.window.height / 2 - self.height / 2
    def distance(ent1, ent2):
        return (round(math.sqrt((ent2.x - ent1.x) ** 2 + (ent2.y - ent1.y) ** 2), 2)) / 10