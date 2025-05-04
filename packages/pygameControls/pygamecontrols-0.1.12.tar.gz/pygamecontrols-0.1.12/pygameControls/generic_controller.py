import pygame
from pygameControls.controlsbase import ControlsBase
        
class GenericController(ControlsBase):
    def __init__(self, joy):
        self.device = joy
        self.instance_id: int = self.device.get_instance_id()
        self.name = self.device.get_name()
        self.guid = self.device.get_guid()
        self.numaxis: int = self.device.get_numaxes()
        self.axis: list = [self.device.get_axis(a) for a in range(self.numaxis)]
        self.numhats: int = self.device.get_numhats()
        self.hats: list = [self.device.get_hat(h) for h in range(self.numhats)]
        self.numbuttons: int = self.device.get_numbuttons()
        self.buttons: list = [self.device.get_button(b) for b in range(self.numbuttons)]
        self.mapping = {
            "r2 trigger": 7,
            "l2 trigger": 6,
            "l1 button": 4,
            "r1 button": 5,
            "X button": 0,
            "Y button": 3,
            "A button": 1,
            "B button": 2,
            "left stick button": 10,
            "right stick button": 11,
            "back button": 8,
            "start button": 9,
            "logo button": None
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
    