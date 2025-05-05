from pygameControls.controlsbase import ControlsBase
from pydualsense import *


class DualSenseEdgeController(ControlsBase):
    def __init__(self, joy):
        self.device = pydualsense()
        self.device.init()
        self.name = self.device.device.get_product_string()
        self.powerlevel = self.device.battery.Level
        self.batterystate = BATTERY_STATE[str(self.device.battery.State)]
        self.set_player_id(PlayerID.PLAYER_1)
        self.numaxis: int = joy.get_numaxes()
        self.axis: list = [joy.get_axis(a) for a in range(self.numaxis)]
        self.numhats: int = joy.get_numhats()
        self.hats: list = [joy.get_hat(h) for h in range(self.numhats)]
        self.numbuttons: int = joy.get_numbuttons()
        self.buttons: list = [joy.get_button(b) for b in range(self.numbuttons)]
        self.mapping = {
            "left stick x": self.axis[0],
            "left stick y": self.axis[1],
            "right stick x": self.axis[3],
            "right stick y": self.axis[4],
            "right trigger": self.buttons[5],
            "left trigger": self.buttons[2],
            "dhat x": self.hats[0][0],
            "dhat y": self.hats[0][1],
            "left button": self.buttons[4],
            "right button": self.buttons[5],
            "cross button": self.buttons[0],
            "triangle button": self.buttons[2],
            "circle button": self.buttons[1],
            "square button": self.buttons[3],
            "left stick button": self.buttons[11],
            "right stick button": self.buttons[12],
            "connect button": self.buttons[8],
            "list button": self.buttons[9],
            "logo button": self.buttons[10]
            }
        print(f"{self.name} connected")
        print(f"Power level: {self.powerlevel}")
        print(f"Battery state: {self.batterystate}")
    
    def close(self):
        self.device.close()
        
    def handle_input(self, event):
        pass
    
    def set_led(self, red: int, green: int, blue: int):
        self.device.light.setColorI(red, green, blue)

    def set_player_id(self, playerid: PlayerID):
        self.device.light.setPlayerID(playerid)
        
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
    
    def rumble(self, left, right):
        if not left in range(256) or not right in range(256):
            raise ValueError("left and right values must be in the range 0 - 255")
        self.device.setLeftMotor(left)
        self.device.setRightMotor(right)
    
    def stop_rumble(self):
        self.device.setLeftMotor(0)
        self.device.setRightMotor(0)
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name
    
    @property
    def powerlevel(self) -> str:
        return self._powerlevel
    
    @powerlevel.setter
    def powerlevel(self, lvl: str) -> None:
        self._powerlevel = lvl
    
    @property
    def batterystate(self) -> int:
        return self._batterystate
    
    @batterystate.setter
    def batterystate(self, state) -> None:
        self._batterystate = state