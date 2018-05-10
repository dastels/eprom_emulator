import digitalio
import adafruit_mcp230xx

# control pin values

programmer_use = False
ice_use = True
    
write_enabled = False
write_disabled = True

chip_enabled = False
chip_disabled = True

clock_active = False
clock_inactive = True

reset_inactive = False
reset_active = True

led_off = False
led_on = True

enable_host_access = False
disable_host_access = True


class Emulator:

    
    def __init__(self, i2c):
        self.mcp = adafruit_mcp230xx.MCP23017(i2c)
        self.mcp.iodir = 0x0000

        self.mode_pin = self.mcp.get_pin(8)
        self.mode_pin.direction = digitalio.Direction.OUTPUT
        self.mode_pin.value = programmer_use
        
        self.write_pin = self.mcp.get_pin(9)
        self.write_pin.direction = digitalio.Direction.OUTPUT
        self.write_pin.value = write_disabled

        self.select_pin = self.mcp.get_pin(10)
        self.select_pin.direction = digitalio.Direction.OUTPUT
        self.select_pin.value = chip_disabled
        
        self.clock_pin = self.mcp.get_pin(11)
        self.clock_pin.direction = digitalio.Direction.OUTPUT
        self.clock_pin.value = clock_inactive
        
        self.reset_pin = self.mcp.get_pin(12)
        self.reset_pin.direction = digitalio.Direction.OUTPUT
        self.reset_pin.value = reset_inactive

        self.led_pin = self.mcp.get_pin(13)
        self.led_pin.direction = digitalio.Direction.OUTPUT
        self.led_pin.value = False

        
    def enter_programmer_mode(self):
        self.mode_pin.value = programmer_use
        self.led_pin.value = led_off

        
    def enter_ice_mode(self):
        self.mode_pin.value = ice_use
        self.led_pin.value = led_on


    def pulse_write(self):
        self.write_pin.value = write_enabled
        self.write_pin.value = write_disabled

        
    def deactivate_ram(self):
        self.select_pin.value = chip_disabled

        
    def activate_ram(self):
        self.select_pin.value = chip_enabled

        
    def reset_address_counter(self):
        self.reset_pin.value = reset_active
        self.reset_pin.value = reset_inactive

        
    def advance_address_counter(self):
        self.clock_pin.value = clock_active
        self.clock_pin.value = clock_inactive
        
        
    def load_ram(self, code):
        self.enter_programmer_mode()
        self.reset_address_counter()
        for data_byte in code:
            self.mcp.gpio = (self.mcp.gpio & 0xFF00) | (data_byte & 0x00FF)
            self.activate_ram()
            self.pulse_write()
            self.deactivate_ram()
            self.advance_address_counter()
    
    
