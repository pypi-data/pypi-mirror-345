import sdl2
from spawnbox.input import Input

'''
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
'''

class SpawnBox:
    def __init__(self, title = None, width = 800, height = 600, bg_color = (0,0,0,255)):
        self.title = title.encode() if title else b"SpawnBox Project"
        self.width = width
        self.height = height
        self.bg_color = bg_color

        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)

        self.window = sdl2.SDL_CreateWindow(self.title, sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, self.width, self.height, sdl2.SDL_WINDOW_SHOWN)
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, 0)

        self.running = True

        self.delta = 1/60

        self.u_delta = 0
        self.updaters = []
        self.drawers = []

        self.input = Input()
    
    def startUpdaters(self, delta):
        self.u_delta += delta
        while self.u_delta > self.delta:
            for updater in self.updaters:
                updater(self.delta)
            self.u_delta -= self.delta
    
    def startDrawers(self):
        for drawer in self.drawers:
            drawer()
      
    def mainloop(self):
        sdl2.SDL_ShowWindow(self.window)

        current = sdl2.SDL_GetPerformanceCounter()
        frequency = sdl2.SDL_GetPerformanceFrequency()
        
        event = sdl2.SDL_Event()

        while self.running != False:
            while sdl2.SDL_PollEvent(event) != 0:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    self.input.updateMouse(event)
        
            new = sdl2.SDL_GetPerformanceCounter()
            self.startUpdaters((new - current) / frequency)
            current = new
            sdl2.SDL_RenderClear(self.renderer)
            self.startDrawers()
            sdl2.SDL_SetRenderDrawColor(self.renderer, self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
            sdl2.SDL_RenderPresent(self.renderer)
        
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def quit(self):
        self.running = False
    
    def addUpdater(self, fn):
        self.updaters.append(fn)
        return fn
    
    def addDrawer(self, fn):
        self.drawers.append(fn)
        return fn