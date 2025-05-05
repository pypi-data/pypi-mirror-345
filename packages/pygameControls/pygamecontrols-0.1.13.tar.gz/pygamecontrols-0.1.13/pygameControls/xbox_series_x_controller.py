from pygameControls.controlsbase import ControlsBase

class XboxSeriesXController(ControlsBase):
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
            "l1 button": 6,
            "r1 button": 7,
            "X button": 3,
            "Y button": 4,
            "A button": 0,
            "B button": 1,
            "left stick button": 13,
            "right stick button": 14,
            "logo button": 12,
            "share button": 15,
            "list button": 11,
            "copy button": 10
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
    