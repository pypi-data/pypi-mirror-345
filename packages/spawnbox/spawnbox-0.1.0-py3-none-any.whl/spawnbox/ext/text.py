import sdl2, sdl2.sdlttf, ctypes

class Text(object):
    def __init__(self, window, text, font, size = 24, x = 0, y = 0, color = (255, 255, 255, 255)):
        self.window = window
        self.text = text
        self.size = size
        self.x = x
        self.y = y
        self.color = color
        sdl2.sdlttf.TTF_Init()
        self.font = sdl2.sdlttf.TTF_OpenFont(font.encode(), self.size)
        if not self.font:
            print("[SPAWNBOX] Font is missing or corrupted.")
        self.surface = sdl2.sdlttf.TTF_RenderText_Blended(self.font, self.text.encode(), sdl2.SDL_Color(self.color[0], self.color[1], self.color[2], self.color[3]))
        self.texture = sdl2.SDL_CreateTextureFromSurface(self.window.renderer, self.surface)
        if not self.texture:
            print("[SPAWNBOX] Could not create a SDL texture.")
   
    def draw(self):
        t = sdl2.SDL_FRect(self.x, self.y)
        w = ctypes.pointer(ctypes.c_int(0))
        h = ctypes.pointer(ctypes.c_int(0))
        sdl2.SDL_QueryTexture(self.texture, None, None, w, h)
        t.w = w.contents.value
        t.h = h.contents.value
        sdl2.SDL_RenderCopyF(self.window.renderer, self.texture, None, t)

'''
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
'''