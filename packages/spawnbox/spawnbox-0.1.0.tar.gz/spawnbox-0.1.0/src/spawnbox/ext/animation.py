import os

class Animation:
    def __init__(self, anim_folder, anim_time):
        self.frames = []
        self.anim_time = anim_time
        self.folder = anim_folder
        
        for f in os.listdir(anim_folder):
            if os.path.splitext(f)[1] == ".png" or os.path.splitext(f)[1] == ".jpg":
                self.frames.append(f)

        self.frames = sorted(self.frames)
        self.count = len(self.frames)

'''
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
'''