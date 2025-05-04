from pygameControls.controlsbase import ControlsBase

class DualShock3Controller(ControlsBase):
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
            "l1 button": 4,
            "r1 button": 5,
            "cross button": 0,
            "triangle button": 2,
            "circle button": 1,
            "square button": 3,
            "left stick button": 11,
            "right stick button": 12,
            "logo button": 10,
            "select button": 8,
            "start button": 9,
            "down button": 14,
            "up button": 13,
            "left button": 15,
            "right button": 16
            }
        print(f"{self.name} connected.")
    
    def close(self):
        self.device.quit()
    
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
    
    def rumble(self, left, right, duration=0):
        if not left in range(256) or not right in range(256):
            raise ValueError("left and right values must be in the range 0 - 255")
        self.device.rumble(left / 255, right / 255, duration)
    
    def stop_rumble(self):
        self.device.stop_rumble()
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name
    