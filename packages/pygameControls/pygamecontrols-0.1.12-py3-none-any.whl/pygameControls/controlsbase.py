"""
This is an abstract baseclass for the controls of snake.
"""
from abc import ABC, abstractmethod

class ControlsBase(ABC):
    @abstractmethod
    def handle_input(self, event):
        pass
    
    @abstractmethod
    def left(self):
        pass
    
    @abstractmethod
    def right(self):
        pass
    
    @abstractmethod
    def up(self):
        pass
    
    @abstractmethod
    def down(self):
        pass
    
    @abstractmethod
    def pause(self):
        pass
    
    @abstractmethod
    def rumble(self):
        pass
    
    @abstractmethod
    def stop_rumble(self):
        pass
    
    @abstractmethod
    def close(self):
        pass