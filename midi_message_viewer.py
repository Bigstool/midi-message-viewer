import tkinter as tk
from tkinter import ttk, messagebox
import mido
import threading
import time


class MidiListener:
    def __init__(self, input_name, log_callback):
        self.input_name = input_name
        self.log_callback = log_callback
        self.running = False
        self.thread = None
        self.inport = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.inport:
            self.inport.close()
            self.inport = None

    def run(self):
        try:
            self.inport = mido.open_input(self.input_name)
            self.log_callback(f"🎧 Listening on: {self.input_name}")
            for msg in self.inport:
                if not self.running:
                    break
                self.log_callback(str(msg))
        except Exception as e:
            self.log_callback(f"Error: {e}")
        finally:
            self.stop()


class MidiListenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Message Viewer 🎹👀")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.listener = None

        # Input selection
        tk.Label(root, text="Input Device:").grid(row=0, column=0, sticky="w")
        self.input_var = tk.StringVar()
        self.input_combo = ttk.Combobox(root, textvariable=self.input_var, width=40, state="readonly")
        self.input_combo['values'] = mido.get_input_names()
        self.input_combo.grid(row=0, column=1)

        # Action buttons frame (for center alignment)
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Start/stop button
        self.toggle_btn = tk.Button(self.button_frame, text="Start Listening", command=self.toggle_listen)
        self.toggle_btn.pack(side='left', padx=5)

        # Refresh button
        self.refresh_btn = tk.Button(self.button_frame, text="Refresh", command=self.refresh_devices)
        self.refresh_btn.pack(side='left', padx=5)

        # Log box
        self.log_text = tk.Text(root, height=15, width=60, state='disabled', bg="#f0f0f0")
        self.log_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def refresh_devices(self):
        devices = mido.get_input_names()
        self.input_combo['values'] = devices
        self.log("🔁 Refreshed device list.")

    def toggle_listen(self):
        if self.listener and self.listener.running:
            # Stop listening
            self.listener.stop()
            self.toggle_btn.config(text="Start Listening")
            self.input_combo['state'] = 'readonly'
            self.refresh_btn['state'] = 'normal'
            self.input_combo['values'] = mido.get_input_names()
            self.log("🛑 Stopped listening.")
        else:
            input_name = self.input_var.get()
            if not input_name:
                messagebox.showwarning("Missing selection", "Please select a MIDI input device.")
                return
            self.input_combo['state'] = 'disabled'
            self.refresh_btn['state'] = 'disabled'
            self.listener = MidiListener(input_name, self.log)
            self.listener.start()
            self.toggle_btn.config(text="Stop Listening")

    def on_close(self):
        if self.listener and self.listener.running:
            self.listener.stop()
            time.sleep(0.1)
        self.root.destroy()


def main():
    root = tk.Tk()
    MidiListenerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
