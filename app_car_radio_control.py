import RPi.GPIO as GPIO
import time

class CarRadioController:
    def __init__(self):
        
        self.PIN_STATE = 17  # The "Menu Select" pulse pin
        self.PIN_A = 22      # Encoder Phase A
        self.PIN_B = 27      # Encoder Phase B
        
        self.MENU_ITEMS = ["Bass", "Mid", "Treble", "Balance", "Fader"]
        self.current_menu_index = 0
        
        self.values = {item: 0 for item in self.MENU_ITEMS}

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.PIN_STATE, self.PIN_A, self.PIN_B], GPIO.OUT, initial=GPIO.LOW)

    def _pulse_state(self):
        GPIO.output(self.PIN_STATE, GPIO.HIGH)
        time.sleep(0.1) 
        GPIO.output(self.PIN_STATE, GPIO.LOW)
        time.sleep(0.1)
        self.current_menu_index = (self.current_menu_index + 1) % len(self.MENU_ITEMS)
        
    def _step_increase(self, steps=1, delay=0.01):
        for _ in range(steps):
            GPIO.output(self.PIN_B, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.PIN_A, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.PIN_B, GPIO.LOW)
            time.sleep(delay)
            GPIO.output(self.PIN_A, GPIO.LOW)
            time.sleep(delay)

    def select_menu(self, target_name):
        if target_name not in self.MENU_ITEMS:
            return
        
        print(f"Switching to {target_name}...")
        while self.MENU_ITEMS[self.current_menu_index] != target_name:
            self._pulse_state()

    def increase_value(self, target_name, amount=1):
        self.select_menu(target_name)
        print(f"Increasing {target_name} by {amount} units.")
        self._step_increase(steps=amount)
        self.values[target_name] += amount

try:
    radio = CarRadioController()
    
    radio.increase_value("Mid", 5)
    
    radio.increase_value("Treble", 2)

finally:
    GPIO.cleanup()