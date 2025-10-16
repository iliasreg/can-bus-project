import tkinter as tk
from tkinter import ttk, messagebox
import time
from collections import deque
from datetime import datetime

import can

from temperature_page import TemperaturePage
from acceleration_page import AccelerationPage
from light_page import LightPage
from can_reading import CANBusReader

class ModernCANBusHMI:
    def __init__(self):

        self.reader = CANBusReader()

        self.root = tk.Tk()
        self.root.title("CAN Bus Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.max_data_points = 100
        self.lux_data = deque(maxlen=self.max_data_points)
        self.accel_data = deque(maxlen=self.max_data_points)
        self.temp_data = deque(maxlen=self.max_data_points)
        self.time_data = deque(maxlen=self.max_data_points)
        
        self.current_values = {
            'lux': 0,
            'range': 0,
            'anemo': 0,
            'temperature': 0,
            'pressure': 0,
            'alpha': 0,
            'theta': 0,
            'psi': 0
        }

        try:
            self.bus = can.interface.Bus('can0', bustype='socketcan')
        except Exception as e:
            print(f"CAN init error: {e}")
            self.bus = None

        self.display_mode = "lux"
        
        self.is_connected = False
        self.last_update = "Never"
        self.running = True
        self.start_time = time.time()
        
        self._build_ui()
        
    def configure_styles(self):
        self.style.configure('TNotebook', background='#0a0a0a', borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                           background='#1a1a1a', 
                           foreground='#e0e0e0',
                           padding=[25, 12],
                           focuscolor='none',
                           font=('Arial', 11, 'bold'))
        self.style.map('TNotebook.Tab',
                      background=[('selected', '#00d4ff')],
                      foreground=[('selected', '#000000')])
        
        self.style.configure('TFrame', background='#0a0a0a')
        self.style.configure('TButton', 
                           background='#00d4ff',
                           foreground='#000000',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Arial', 10, 'bold'))
        self.style.map('TButton',
                      background=[('active', '#00aaff'),
                                 ('pressed', '#0088cc')])
    
    def _build_ui(self):
        header_frame = tk.Frame(self.root, bg='#0a0a0a')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(header_frame, text="CAN BUS DASHBOARD", 
                              bg='#0a0a0a', fg='#00d4ff', 
                              font=('Arial', 24, 'bold'))
        title_label.pack(side='left')
        
        if self.is_connected:
            self.connection_status = tk.Label(header_frame, text="● CONNECTED", 
                                            bg='#0a0a0a', fg='#00ff88',
                                            font=('Arial', 12, 'bold'))
        else:
            self.connection_status = tk.Label(header_frame, text="● DISCONNECTED", 
                                            bg='#0a0a0a', fg='#ff0088',
                                            font=('Arial', 12, 'bold'))

        self.connection_status.pack(side='right', padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.dashboard_page = self._create_dashboard()
        self.accel_page = AccelerationPage(self.notebook)
        self.light_page = LightPage(self.notebook)
        self.temp_page = TemperaturePage(self.notebook)
        
        self.notebook.add(self.dashboard_page, text="📊 DASHBOARD")
        self.notebook.add(self.accel_page, text="🌀 ANEMO")
        self.notebook.add(self.light_page, text="💡 LIGHT")
        self.notebook.add(self.temp_page, text="🌡️ TEMPERATURE")
        
    def _create_dashboard(self):
        frame = tk.Frame(self.notebook, bg='#0a0a0a') 
        
        switch_frame = tk.Frame(frame, bg='#0a0a0a')
        switch_frame.pack(fill='x', padx=10, pady=5)
        
        self.mode_switch = tk.Button(
            switch_frame, 
            text="🔁 SWITCH TO RANGE", 
            command=self._toggle_display_mode,
            bg='#2a2a2a', 
            fg='#00d4ff', 
            font=('Arial', 10, 'bold'),
            bd=1,
            relief='solid',
            padx=20,
            pady=8
        )
        self.mode_switch.pack(side='right', padx=10)
        
        # Label pour indiquer le mode actuel
        self.mode_label = tk.Label(
            switch_frame,
            text="Current Mode: LUX",
            bg='#0a0a0a',
            fg='#00ff88',
            font=('Arial', 10, 'bold')
        )
        self.mode_label.pack(side='right', padx=10)
        
        top_cards_frame = tk.Frame(frame, bg='#0a0a0a')
        top_cards_frame.pack(fill='x', padx=10, pady=10)
        
        cards = [
            ("💡 ILLUMINANCE", "lux_value", "lux", "#FFD700"),
            ("📏 RANGE", "range_value", "cm", "#FF6B35"), 
            ("🌀 ANEMO", "accel_value", "m/s", "#00D4FF"),
            ("🌡️ TEMP", "temp_value", "°C", "#FF4444"),
            ("📊 PRESSURE", "pressure_value", "kPa", "#4FC3F7"),  
            ("α ALPHA", "alpha_value", "rad", "#FF9800"),
            ("θ THETA", "theta_value", "rad", "#9C27B0"),
            ("ψ PSI", "psi_value", "rad", "#4CAF50")
        ] 
        
        for i, (title, value_tag, unit, color) in enumerate(cards):
            card = self._create_modern_card(top_cards_frame, title, value_tag, unit, color, i)
        
        plots_frame = tk.Frame(frame, bg='#0a0a0a')
        plots_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        left_plots = tk.Frame(plots_frame, bg='#0a0a0a')
        left_plots.pack(side='left', fill='both', expand=True)
        
        right_plots = tk.Frame(plots_frame, bg='#0a0a0a')
        right_plots.pack(side='right', fill='both', expand=True)

        self.plot_lux = self._create_modern_plot(left_plots, "💡 Illuminance (Lux)", 0, 1000, 0, "#FFD700")
        self.plot_accel = self._create_modern_plot(left_plots, "🌀 Anemo (m/s)", -20, 20, 1, "#00D4FF")
        self.plot_temp = self._create_modern_plot(right_plots, "🌡️ Temperature (°C)", -10, 60, 0, "#FF4444", True)
        
        controls_frame = tk.Frame(frame, bg='#0a0a0a')
        controls_frame.pack(fill='x', padx=10, pady=20)
        
        button_style = {'bg': '#00d4ff', 'fg': '#000000', 'font': ('Arial', 11, 'bold'), 
                       'bd': 0, 'padx': 25, 'pady': 12, 'relief': 'flat'}
        
        reset_btn = tk.Button(controls_frame, text="🔄 RESET DATA", command=self._reset_data, **button_style)
        reset_btn.pack(side='left', padx=10)
        
        export_btn = tk.Button(controls_frame, text="📤 EXPORT DATA", command=self._export_data, **button_style)
        export_btn.pack(side='left', padx=10)
        
        return frame

    def _toggle_display_mode(self):
        if self.display_mode == "lux":
            # Sending first byte diff than 0 (MODE RANGE)
            id = 0x11
            data = [1, 0, 0, 1, 3, 1, 4, 1]
            self.reader.send_message(id, data)
            print("Sent Data:", data)

            self.display_mode = "range"
            self.mode_switch.config(text="🔁 SWITCH TO LUX")
            self.mode_label.config(text="Current Mode: RANGE")
        else:
            # Sending first byte diff = 0 (MODE LUX)
            id = 0x11
            data = [0, 0, 0, 1, 3, 1, 4, 1]
            self.reader.send_message(id, data)
            print("Sent Data:", data)

            self.display_mode = "lux"
            self.mode_switch.config(text="🔁 SWITCH TO RANGE")
            self.mode_label.config(text="Current Mode: LUX")
        
        self._update_plots()

    def _create_modern_card(self, parent, title, value_tag, unit, color, column):
        card = tk.Frame(parent, bg='#1a1a1a', relief='flat', bd=0)
        card.grid(row=0, column=column, padx=8, pady=5, sticky='nsew')
        card.configure(width=160, height=140)
        
        parent.grid_columnconfigure(column, weight=1)
        
        header_frame = tk.Frame(card, bg=color)
        header_frame.pack(fill='x')
        
        title_label = tk.Label(header_frame, text=title, bg=color, fg='#000000',
                              font=('Arial', 10, 'bold'), pady=8)
        title_label.pack()
        
        content_frame = tk.Frame(card, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True, pady=15)
        
        value_label = tk.Label(content_frame, text="0.0", bg='#1a1a1a', fg='#ffffff',
                              font=('Arial', 18, 'bold'))
        value_label.pack()
        setattr(self, value_tag, value_label)
        
        unit_label = tk.Label(content_frame, text=unit, bg='#1a1a1a', fg='#888888',
                             font=('Arial', 10))
        unit_label.pack()
        
        return card
    
    def _create_modern_plot(self, parent, title, y_min, y_max, row, color, full_width=False):
        plot_frame = tk.Frame(parent, bg='#1a1a1a', relief='flat', bd=0)
        if full_width:
            plot_frame.pack(fill='both', expand=True, padx=5, pady=5)
        else:
            plot_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        header_frame = tk.Frame(plot_frame, bg='#2a2a2a')
        header_frame.pack(fill='x')
        
        title_label = tk.Label(header_frame, text=title, bg='#2a2a2a', fg='#ffffff',
                              font=('Arial', 12, 'bold'), pady=8)
        title_label.pack()
        
        canvas = tk.Canvas(plot_frame, bg='#151515', highlightthickness=0)
        canvas.pack(fill='both', expand=True, padx=2, pady=2)
        
        plot_id = title.lower().split(' ')[0].replace('(', '').replace(')', '')
        setattr(self, f'plot_{plot_id}_canvas', canvas)
        setattr(self, f'plot_{plot_id}_range', (y_min, y_max))
        
        return canvas
    
    def _update_plots(self):
        if len(self.time_data) > 1:
            if self.display_mode == "lux":
                data_to_plot = list(self.lux_data)
                y_range = (0, 1000)
                color = '#FFD700'
                title = "💡 Illuminance (Lux)"
            else:
                data_to_plot = [self.current_values['range']] * len(self.time_data)
                y_range = (0, max(data_to_plot) * 1.2 if data_to_plot else 100)
                color = '#FF6B35'
                title = "📏 Range (cm)"
            
            self.plot_lux_canvas.master.master.winfo_children()[0].winfo_children()[0].config(text=title)
            
            self._draw_modern_plot(self.plot_lux_canvas, data_to_plot, y_range, color)
            self._draw_modern_plot(self.plot_accel_canvas, list(self.accel_data), (-20, 20), '#00D4FF')
            self._draw_modern_plot(self.plot_temp_canvas, list(self.temp_data), (-10, 60), '#FF4444')
    
    def _draw_modern_plot(self, canvas, data, y_range, color):
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        y_min, y_max = y_range
        x_scale = width / len(data) if len(data) > 1 else 1
        y_scale = height / (y_max - y_min)
        
        canvas.create_rectangle(0, 0, width, height, fill='#151515', outline='')
        
        for i in range(0, height, 40):
            canvas.create_line(0, i, width, i, fill='#2a2a2a', width=1)
        
        points = []
        for i, value in enumerate(data):
            x = i * x_scale
            y = height - (value - y_min) * y_scale
            points.extend([x, y])
        
        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=3, smooth=True)
            
            for i in range(0, len(points)-2, 2):
                x, y = points[i], points[i+1]
                canvas.create_oval(x-2, y-2, x+2, y+2, fill=color, outline='')
    
    def _start_data_simulation(self):
        def generate_data():
            self.current_values = self.reader.read_can_bus_data()

            if self.current_values is None:
                print(f"There is no data being read")
                return

            if self.current_values['lux'] is not None:
                self.lux_data.append(self.current_values['lux'])
            if self.current_values['anemo'] is not None:
                self.accel_data.append(self.current_values['anemo'])
            if self.current_values['pressure'] is not None:
                self.temp_data.append(self.current_values['pressure'])

            self.last_update = datetime.now().strftime("%H:%M:%S")
            self.is_connected = True
            
            self._update_gui()
            
            if self.running:
                self.root.after(10, generate_data)
        
        generate_data()
    
    def _update_gui(self):
        if hasattr(self, 'lux_value'):
            self.lux_value.config(text=f"{self.current_values['lux']:.1f}")
        if hasattr(self, 'range_value'):
            self.range_value.config(text=f"{self.current_values['range']:.1f}")
        if hasattr(self, 'accel_value'):
            self.accel_value.config(text=f"{self.current_values['anemo']:.2f}")
        if hasattr(self, 'temp_value'):
            self.temp_value.config(text=f"{self.current_values['temperature']:.1f}")
        if hasattr(self, 'pressure_value'):
            self.pressure_value.config(text=f"{self.current_values['pressure']:.1f}")
        if hasattr(self, 'alpha_value'):
            self.alpha_value.config(text=f"{self.current_values['alpha']:.2f}")
        if hasattr(self, 'theta_value'):
            self.theta_value.config(text=f"{self.current_values['theta']:.2f}")
        if hasattr(self, 'psi_value'):
            self.psi_value.config(text=f"{self.current_values['psi']:.2f}")
        
        if self.is_connected:
            self.connection_status.config(text="● CONNECTED", fg='#00ff88')
        else:
            self.connection_status.config(text="● DISCONNECTED", fg='#ff4444')
        
        self._update_plots()
        
        self.accel_page.set_accel(self.current_values['alpha'], self.current_values['theta'], self.current_values['psi'])
        self.light_page.set_lux(self.current_values['lux'])
        self.temp_page.set_temp(self.current_values['temperature'])
        self.temp_page.set_pressure(self.current_values['pressure'])
    
    def _reset_data(self):
        self.lux_data.clear()
        self.accel_data.clear()
        self.temp_data.clear()
        self.time_data.clear()
        messagebox.showinfo("Reset", "All data has been reset successfully!")
    
    def _export_data(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"can_bus_data_{timestamp}.csv"
            with open(filename, 'w') as f:
                f.write("Time,Lux,Acceleration,Temperature\n")
                for i in range(len(self.time_data)):
                    f.write(f"{self.time_data[i]:.2f},{self.lux_data[i]:.2f},{self.accel_data[i]:.2f},{self.temp_data[i]:.2f}\n")
            messagebox.showinfo("Export Successful", f"Data exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
    
    def run(self):
        for i in range(8):
            self.root.grid_columnconfigure(i, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        def on_closing():
            self.running = False
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self._start_data_simulation()
        self.root.mainloop()

if __name__ == '__main__':
    try:
        app = ModernCANBusHMI()
        app.run()
    except KeyboardInterrupt:
        print(f"User Interruption")