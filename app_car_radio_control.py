import customtkinter as ctk
import RPi.GPIO as GPIO
import time

class CarRadioController:
    def __init__(self):
        self.PIN_STATE = 17  
        self.PIN_A = 22      
        self.PIN_B = 27
        self.PULSE_DELAY = 0.08
        self.TURN_DELAY = 0.1
        
        self.MENU_ITEMS = ["Bass", "Mid", "Treble", "Balance", "Fader"]
        self.current_menu_index = 0
        self.values = {item: 0 for item in self.MENU_ITEMS}
    
        print(f"Initializing GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_STATE, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup([self.PIN_A, self.PIN_B], GPIO.OUT, initial=GPIO.HIGH)

    def _pulse_state(self):
        print(f"Sending one pulse...")
        GPIO.output(self.PIN_STATE, GPIO.HIGH)
        time.sleep(self.PULSE_DELAY) 
        GPIO.output(self.PIN_STATE, GPIO.LOW)
        time.sleep(self.PULSE_DELAY)
        
    def _update_current_menu_index(self):
        self.current_menu_index = (self.current_menu_index + 1) % len(self.MENU_ITEMS)

    def select_menu(self, target_name):
        if target_name not in self.MENU_ITEMS:
            return
        
        print(f"Switching to {target_name}...")
        while self.MENU_ITEMS[self.current_menu_index] != target_name:
            self._pulse_state()
            self._update_current_menu_index()
            
    def _step_quadrature(self, direction, steps, delay=0.1):
        for _ in range(abs(steps)):
            if direction == "increase":
                print(f"Increaaaaaaasing value...")
                GPIO.output(self.PIN_B, GPIO.LOW)
                time.sleep(delay)
                GPIO.output(self.PIN_A, GPIO.LOW)
                time.sleep(delay)
                GPIO.output(self.PIN_B, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(self.PIN_A, GPIO.HIGH)
            else:
                print(f"Decreasing value...")
                GPIO.output(self.PIN_A, GPIO.LOW)
                time.sleep(delay)
                GPIO.output(self.PIN_B, GPIO.LOW)
                time.sleep(delay)
                GPIO.output(self.PIN_A, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(self.PIN_B, GPIO.HIGH)
            time.sleep(delay)

    def set_value(self, target_name, new_value):
        diff = new_value - self.values[target_name]
        
        if diff > 0:
            self._step_quadrature("increase", diff, self.TURN_DELAY)
        elif diff < 0:
            self._step_quadrature("decrease", diff, self.TURN_DELAY)
            
        self.values[target_name] = new_value

class RadioApp(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.radio = controller
                
        print(f"Switching to EQ")
        self.radio._pulse_state()
        
        self.title("Raspberry Pi Car Radio EQ")
        self.geometry("1000x400")
        ctk.set_appearance_mode("dark")

        self.selected_item = ctk.StringVar(value="Bass")
        self.last_interaction = time.time()

        self.label = ctk.CTkLabel(self, text="Control Audio System", font=("Roboto", 24))
        self.label.pack(pady=20)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=20, fill="x")

        for item in self.radio.MENU_ITEMS:
            btn = ctk.CTkButton(self.button_frame, text=item, 
                                command=lambda i=item: self.select_menu_item(i))
            btn.pack(side="left", padx=5, expand=True)

        self.status_label = ctk.CTkLabel(self, text="Selectat: Bass", font=("Roboto", 16))
        self.status_label.pack(pady=10)

        self.slider = ctk.CTkSlider(self, from_=-7, to=7, number_of_steps=14, 
                                    command=self.slider_event)
        self.slider.set(0)
        self.slider.pack(pady=20, padx=50, fill="x")

        self.val_display = ctk.CTkLabel(self, text="Valoare: 0", font=("Roboto", 14))
        self.val_display.pack()

       

    def select_menu_item(self, item):
        self.check_idle()
        self.last_interaction = time.time()
        self.selected_item.set(item)
        self.status_label.configure(text=f"Selectat: {item}")
        self.radio.select_menu(item)
        self.slider.set(self.radio.values[item])
        self.val_display.configure(text=f"Valoare: {int(self.radio.values[item])}")

    def slider_event(self, value):
        self.last_interaction = time.time()
        val = int(value)
        self.val_display.configure(text=f"Valoare: {val}")
        self.radio.set_value(self.selected_item.get(), val)

    def check_idle(self):
        if time.time() - self.last_interaction >= 10:
            print(f"More than 10 secs passed")
            self.radio._pulse_state()

if __name__ == "__main__":
    try:
        radio_hw = CarRadioController()
        app = RadioApp(radio_hw)
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()