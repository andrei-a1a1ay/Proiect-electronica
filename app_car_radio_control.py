import customtkinter as ctk
import RPi.GPIO as GPIO
import time

# --- Clasa Hardware (bazată pe discuția noastră) ---
class CarRadioController:
    def __init__(self):
        self.PIN_STATE = 17  
        self.PIN_A = 23      
        self.PIN_B = 24      
        
        self.MENU_ITEMS = ["Bass", "Mid", "Treble", "Balance", "Fader"]
        self.current_menu_index = 0
        self.values = {item: 0 for item in self.MENU_ITEMS}

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.PIN_STATE, self.PIN_A, self.PIN_B], GPIO.OUT, initial=GPIO.LOW)

    def _pulse_state(self):
        GPIO.output(self.PIN_STATE, GPIO.HIGH)
        time.sleep(0.05) 
        GPIO.output(self.PIN_STATE, GPIO.LOW)
        time.sleep(0.05)
        self.current_menu_index = (self.current_menu_index + 1) % len(self.MENU_ITEMS)

    def _step_quadrature(self, direction, steps, delay=0.005):
        for _ in range(abs(steps)):
            if direction == "increase":
                GPIO.output(self.PIN_B, GPIO.HIGH)
                time.sleep(delay); GPIO.output(self.PIN_A, GPIO.HIGH)
                time.sleep(delay); GPIO.output(self.PIN_B, GPIO.LOW)
                time.sleep(delay); GPIO.output(self.PIN_A, GPIO.LOW)
            else:
                GPIO.output(self.PIN_A, GPIO.HIGH)
                time.sleep(delay); GPIO.output(self.PIN_B, GPIO.HIGH)
                time.sleep(delay); GPIO.output(self.PIN_A, GPIO.LOW)
                time.sleep(delay); GPIO.output(self.PIN_B, GPIO.LOW)
            time.sleep(delay)

    def set_value(self, target_name, new_value):
        # 1. Navigare la meniul corect
        while self.MENU_ITEMS[self.current_menu_index] != target_name:
            self._pulse_state()
        
        # 2. Calculare diferență față de valoarea actuală
        diff = new_value - self.values[target_name]
        
        if diff > 0:
            self._step_quadrature("increase", diff)
        elif diff < 0:
            self._step_quadrature("decrease", diff)
            
        self.values[target_name] = new_value

# --- Interfața Grafică (GUI) ---
class RadioApp(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.radio = controller
        
        self.title("Raspberry Pi Car Radio EQ")
        self.geometry("500x400")
        ctk.set_appearance_mode("dark")

        self.selected_item = ctk.StringVar(value="Bass")

        # Titlu
        self.label = ctk.CTkLabel(self, text="Control Audio System", font=("Roboto", 24))
        self.label.pack(pady=20)

        # Container pentru Butoane (Meniu)
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=20, fill="x")

        for item in self.radio.MENU_ITEMS:
            btn = ctk.CTkButton(self.button_frame, text=item, 
                                command=lambda i=item: self.select_menu_item(i))
            btn.pack(side="left", padx=5, expand=True)

        # Label pentru item-ul selectat
        self.status_label = ctk.CTkLabel(self, text="Selectat: Bass", font=("Roboto", 16))
        self.status_label.pack(pady=10)

        # Slider cu 7 trepte pozitive și 7 negative (-7 la +7 = 15 poziții)
        self.slider = ctk.CTkSlider(self, from_=-7, to=7, number_of_steps=14, 
                                    command=self.slider_event)
        self.slider.set(0)
        self.slider.pack(pady=20, padx=50, fill="x")

        self.val_display = ctk.CTkLabel(self, text="Valoare: 0", font=("Roboto", 14))
        self.val_display.pack()

    def select_menu_item(self, item):
        self.selected_item.set(item)
        self.status_label.configure(text=f"Selectat: {item}")
        # Resetăm slider-ul vizual la valoarea salvată în memorie pentru acel item
        self.slider.set(self.radio.values[item])
        self.val_display.configure(text=f"Valoare: {int(self.radio.values[item])}")

    def slider_event(self, value):
        val = int(value)
        self.val_display.configure(text=f"Valoare: {val}")
        # Trimitem comanda către hardware
        self.radio.set_value(self.selected_item.get(), val)

if __name__ == "__main__":
    try:
        radio_hw = CarRadioController()
        app = RadioApp(radio_hw)
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()