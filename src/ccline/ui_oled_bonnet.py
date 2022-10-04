# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import adafruit_ssd1306
import board
import digitalio


class OledBonnet:

    def __init__(self):
        i2c = board.I2C()
        width = 128
        height = 64
        self.display_ = adafruit_ssd1306.SSD1306_I2C(width, height, i2c)
        self.button_a = digitalio.DigitalInOut(board.D5)
        self.button_b = digitalio.DigitalInOut(board.D6)
        self.button_l = digitalio.DigitalInOut(board.D27)
        self.button_r = digitalio.DigitalInOut(board.D23)
        self.button_u = digitalio.DigitalInOut(board.D17)
        self.button_d = digitalio.DigitalInOut(board.D22)
        self.button_c = digitalio.DigitalInOut(board.D4)
        for button in [
            self.button_a,
            self.button_b,
            self.button_c,
            self.button_l,
            self.button_r,
            self.button_u,
            self.button_d,
        ]:
            button.switch_to_input(digitalio.Pull.UP)

    def get_display(self):
        return self.display_

    def get_buttons(self):
        return {
            "a": self.button_a,
            "b": self.button_b,
            "c": self.button_c,
            "left": self.button_l,
            "right": self.button_r,
            "up": self.button_u,
            "down": self.button_d,
        }
