import digitalio
import time

class Debouncer:

    DEBOUNCED_STATE = 0x01
    UNSTABLE_STATE = 0x02
    CHANGED_STATE = 0x04


    def __init__(self, pin, mode=None, interval=0.010):
        """Make am instance.
           :param int pin: the pin (from board) to debounce
           :param int mode: digitalio.Pull.UP or .DOWN (default is no pull up/down)
           :param int interval: bounce threshold in seconds (default is 0.010, i.e. 10 milliseconds)
        """
        self.state = 0x00
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.INPUT
        if mode != None:
            self.pin.pull = mode
        if self.pin.value:
            self.__set_state(Debouncer.DEBOUNCED_STATE | Debouncer.UNSTABLE_STATE)
        self.previous_time = 0
        if interval == None:
            self.interval = 0.010
        else:
            self.interval = interval


    def __set_state(self, bits):
        self.state |= bits


    def __unset_state(self, bits):
        self.state &= ~bits


    def __toggle_state(self, bits):
        self.state ^= bits


    def __get_state(self, bits):
        return (self.state & bits) != 0
    
    
    def update(self):
        self.__unset_state(Debouncer.CHANGED_STATE)
        current_state = self.pin.value
        if current_state != self.__get_state(Debouncer.UNSTABLE_STATE):
            self.previous_time = time.monotonic()
            self.__toggle_state(Debouncer.UNSTABLE_STATE)
        else:
            if time.monotonic() - self.previous_time >= self.interval:
                if current_state != self.__get_state(Debouncer.DEBOUNCED_STATE):
                    self.previous_time = time.monotonic()
                    self.__toggle_state(Debouncer.DEBOUNCED_STATE)
                    self.__set_state(Debouncer.CHANGED_STATE)


    @property
    def value(self):
        """Return the current debounced value of the input."""
        return self.__get_state(Debouncer.DEBOUNCED_STATE)


    @property
    def rose(self):
        """Return whether the debounced input went from low to high at the most recent update."""
        return self.__get_state(Debouncer.DEBOUNCED_STATE) and self.__get_state(Debouncer.CHANGED_STATE)


    @property
    def fell(self):
        """Return whether the debounced input went from high to low at the most recent update."""
        return (not self.__get_state(Debouncer.DEBOUNCED_STATE)) and self.__get_state(Debouncer.CHANGED_STATE)
    
