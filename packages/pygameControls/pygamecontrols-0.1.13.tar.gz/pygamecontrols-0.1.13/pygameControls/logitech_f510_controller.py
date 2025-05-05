"""
Logitech F310 Controller class.
This controller is a usb controller, with the following features.
(XInput mode)
6 axis
11 buttons
1 hat

(DirectInput mode)
4 axis
12 buttons
1 hat
"""

import pygame
from pygameControls.controlsbase import ControlsBase
from enum import Enum

class InputMode(Enum):
    DirectInput = 1
    XInput = 2

class ConnectionType(Enum):
    WIRED = 1
    WIRELESS = 2
    
class LogitechF510Controller(ControlsBase):
    def __init__(self, joy):
        self.device = joy
        self.instance_id: int = self.device.get_instance_id()
        self.name = self.device.get_name()
        self.numaxis: int = self.device.get_numaxis()
        self.axis: list = []
        self.numhats: int = self.device.get_numhats()
        self.hats: list = []
        self.numbuttons: int = self.device.get_numbuttons()
        self.buttons: list = []
        self.input_mode: InputMode.DirectInput
        self.mapping = {
            "l1 button": 4,
            "r1 button": 5,
            "X button": 2,
            "Y button": 3,
            "A button": 0,
            "B button": 1,
            "left stick button": 9,
            "right stick button": 10,
            "back button": 6,
            "start button": 7,
            "logo button": 8
            }
        print(f"{self.name} connected.")
    
    def close(self):
        pass
    
    def handle_input(self, event):
        pass
    
    def left(self):
        pass
    
    def right(self):
        pass
    
    def up(self):
        pass
    
    def down(self):
        pass
    
    def pause(self):
        pass
    
    def rumble(self):
        pass
    
    def stop_rumble(self):
        pass
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name
    
    @property
    def axis(self) -> list:
        return self._axis
    
    @axis.setter
    def axis(self) -> None:
        self._axis = [self.device.get_axis(a) for a in range(self.numaxis)]
    
    @property
    def hats(self) -> list:
        return self._hats
    
    @hats.setter
    def hats(self) -> None:
        self.hats = [self.device.get_hats(h) for h in range(self.numhats)]
    
    @property
    def buttons(self) -> list:
        return self._buttons
    
    @buttons.setter
    def buttons(self) -> None:
        self._buttons = [self.device.get_buttons(b) for b in range(self.numbuttons)]
    
    @property
    def input_mode(self) -> int:
        return self._inputmode
    
    @input_mode.setter
    def input_mode(self, mode: int) -> None:
        self._inputmode = mode
    
    @property
    def input_connection(self) -> int:
        return self._input_connection
    
    @input_connection.setter
    def input_connection(self, conn: int) -> None:
        self._input_connection = conn