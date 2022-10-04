#!/usr/bin/env python3
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

import asyncio
import datetime
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import ui_oled_bonnet
from absl import app, flags
from adafruit_debouncer import Debouncer
from PIL import Image, ImageDraw, ImageFont
from sshkeyboard import listen_keyboard

from ccline import client
from ccline.config import read_config, timestamp_stub
from ccline.resolver import Resolver

FLAGS = flags.FLAGS

# The UI is compact and simple so that it can easily be adapted to a variety of
# displays or extended for unique use cases.
# On a large enough display it has 3 rows of information:
#   1. A menu item which will be activated on a button press
#   2. Stats relevant to collection or other operation
#   3. Overall status of the array
# Some displays also have room for feedback to let the user know a button
# press or joystick move was received (i.e. a dot flashes when the button is
# pressed even if there's no other observable change).
# In general a menu item is an action. In some cases the action is very simple,
# like displaying the IP address or some other info. In those cases the stats
# row may immediately update to show the info.


def do_hat_button_queue(queue: List[str], buttons: Dict):
    """The dict buttons has string names as a key for each button which is a
    DigitalInOut
    """
    switches = {n: Debouncer(b) for n, b in buttons.items()}
    while True:
        for name, switch in switches.items():
            switch.update()
            if switch.rose:
                queue.append(name)


def do_keyboard_queue(queue: List[str]):
    def press(key):
        queue.append(key)

    def release(key):
        pass

    listen_keyboard(
        on_press=press,
        on_release=release,
    )


class FakeDisplay:
    height = 100
    width = 200


class FakeButton:
    pass


class FakeDisplayHat:

    def __init__(self):
        self.display_ = FakeDisplay()
        self.button_a_ = FakeButton()
        self.button_b_ = FakeButton()

    def get_display(self):
        return self.display_

    def get_button_a(self):
        return self.button_a_

    def get_button_b(self):
        return self.button_b_


@dataclass
class FakeUiParam:
    name: str
    values: List[str]
    index: int


class FakeCclineClient:

    def __init__(self):
        self.start_sec_ = 0
        # Meant to represent a list of gin configs to select different
        # sets of parameters for the camera array.
        self.configs_ = ["short_exp.gin", "long_exp.gin", "auto_exp.gin"]
        self.selected_config_idx_ = 0
        self.params_ = [
            FakeUiParam(
                "Node IP",
                [
                    "gamma1 123.456.654.321",
                    "gamma2 1.456.654.321",
                    "gamma3 23.456.654.321",
                    "gamma4 192.4.4.1",
                ],
                0,
            )
        ]

    def stat_image_count(self):
        """Return a simulated number of images"""
        now = datetime.datetime.now()
        return f"Count: {int((now.minute * 60 + now.second) * 2.5)}"

    def select_previous_param(self, index: int):
        param = self.params_[index]
        param.index -= 1
        if param.index <= 0:
            param.index = len(param.values) - 1

    def select_next_param(self, index: int):
        param = self.params_[index]
        param.index += 1
        if param.index >= len(param.values):
            param.index = 0

    def selected_param(self, index: int):
        param = self.params_[index]
        return param.values[param.index]


@dataclass
class UiAction:
    """
    `name`: displayed on the menu
    `runnable`: runs on activation button
    `left_runnable`: runs on left button
    `right_runnable`: runs on right button
    `statistic`: provides string to show on stats row
    """

    name: str
    runnable: Optional[Callable]
    left_runnable: Optional[Callable]
    right_runnable: Optional[Callable]
    statistic: Optional[Callable]


def now_ms():
    return time.monotonic_ns() // 1_000_000


class Ui:

    def __init__(self):
        # The display library abstracts away most display details but each HAT
        # has different IO pins so the XyzDisplayHat classes hold on to those
        # details.
        self.display_hat_ = ui_oled_bonnet.OledBonnet()
        # self.display_hat_ = FakeDisplayHat()
        self.ccline_client_ = FakeCclineClient()
        self.display_ = self.display_hat_.get_display()
        self.width_ = 128
        self.height_ = 64
        self.refresh_pause_ms_ = 200
        self.next_refresh_ms_ = now_ms()
        self.active_recording_ = ""

        c = self.ccline_client_
        self.actions_ = [
            UiAction("start", self.start, None, None, self.get_current_count),
            UiAction("stop", self.stop, None, None, self.get_current_count),
            UiAction(
                "addresses",
                self.stop,
                lambda: c.select_previous_param(0),
                lambda: c.select_next_param(0),
                lambda: c.selected_param(0),
            ),
            UiAction("shutdown", self.shutdown, None, None, lambda: "power off"),
        ]

        # Python dicts are ordered by key insertion order.
        self.selected_action_idx_ = 0

        self.padding_ = 5
        self.font_ = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10
        )
        self.height_ = self.display_.height
        self.width_ = self.display_.width

    def active(self):
        # TODO: Detect connected display or read a config value.
        return True

    def get_current_count(self):
        if self.active_recording_ == "":
            return " Stopped "
        r = Path(f"/home/pi/data/{self.active_recording_}")
        count = len([x for x in r.iterdir() if x.suffix == ".jpg"])
        return f"frames: {count}"

    def draw_text(self, row, text):
        x = self.padding_
        top = self.padding_ + row * 20
        # print(f'text line {row}/{x},{top}: {text}')
        self.draw_.text((x, top), text, font=self.font_, outline=255, fill=1)

    def write_action(self):
        self.draw_text(0, self.actions_[self.selected_action_idx_].name)

    def write_stats(self):
        # Supported stats:
        #  Active collection destination
        #  Frame count, video length, etc - config in CliRunner
        #  IP addresses, hostname
        #  Peers online
        stat_updater = self.actions_[self.selected_action_idx_].statistic
        text = ""
        if stat_updater:
            text = stat_updater()
        self.draw_text(1, text)

    def refresh_all(self):
        self.image_ = Image.new("1", (self.width_, self.height_))
        self.draw_ = ImageDraw.Draw(self.image_)
        self.write_action()
        self.write_stats()
        self.display_.image(self.image_)
        self.display_.show()

    def start(self):
        read_config()
        resolver = Resolver()
        coordinator = asyncio.run(client.find_coordinator(resolver=resolver))
        if coordinator is None:
            print(f"No coordinator found.")
            return
        recording_id = f"r_{timestamp_stub()}"
        asyncio.run(client.start_collecting(coordinator, resolver, recording_id))
        self.active_recording_ = recording_id

    def stop(self):
        read_config()
        resolver = Resolver()
        coordinator = asyncio.run(client.find_coordinator(resolver=resolver))
        if coordinator is None:
            print(f"No coordinator found.")
            return
        asyncio.run(client.stop_collecting(coordinator, resolver))
        self.active_recording_ = ""

    def shutdown(self):
        read_config()
        resolver = Resolver()
        coordinator = asyncio.run(client.find_coordinator(resolver=resolver))
        if coordinator is None:
            print(f"No coordinator found.")
            return
        asyncio.run(client.shutdown(coordinator, resolver))

    def select_next_action(self):
        self.selected_action_idx_ = self.selected_action_idx_ + 1
        if self.selected_action_idx_ >= len(self.actions_):
            self.selected_action_idx_ = 0
        return True

    def select_previous_action(self):
        i = self.selected_action_idx_
        self.selected_action_idx_ = self.selected_action_idx_ - 1
        if self.selected_action_idx_ < 0:
            self.selected_action_idx_ = len(self.actions_) - 1
        return i == self.selected_action_idx_

    def handle_input(self, input):
        action = self.actions_[self.selected_action_idx_]
        refresh = False
        if input == "up":
            refresh |= self.select_previous_action()
        elif input == "down":
            refresh |= self.select_next_action()
        elif input == "left" and action.left_runnable:
            print(f"left {action.left_runnable}")
            action.left_runnable()
        elif input == "right" and action.right_runnable:
            action.right_runnable()
        if input == "a" and action.runnable:
            action.runnable()
        # TODO: No way to know if the stats line needs updating
        self.refresh_all()

    def run(self):
        queue: List[str] = []
        use_fake = False
        update_thread = None
        if use_fake:
            update_thread = threading.Thread(target=do_keyboard_queue, args=[queue])
        else:
            update_thread = threading.Thread(
                target=do_hat_button_queue,
                args=[queue, self.display_hat_.get_buttons()],
            )
        update_thread.start()
        done = False
        while update_thread.is_alive() and not done:
            if len(queue):
                self.handle_input(queue.pop(0))
            # TODO: There should be a way to sleep here without disrupting anything.
            if self.next_refresh_ms_ < now_ms():
                # update_start = now_ms()
                self.next_refresh_ms_ = self.next_refresh_ms_ + self.refresh_pause_ms_
                self.refresh_all()
                # update_end = now_ms()
                # print(f'update time {update_end - update_start}')
                n = now_ms()
                if self.next_refresh_ms_ < n:
                    print(
                        f"Failed to keep up with frame rate {self.next_refresh_ms_} < {n} by {n - self.next_refresh_ms_}"
                    )
        update_thread.join()


def main(argv):
    del argv  # Unused.
    ui = Ui()
    if ui.active():
        ui.run()
    else:
        while True:
            time.sleep(10)


if __name__ == "__main__":
    app.run(main)
