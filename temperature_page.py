import tkinter as tk
from tkinter import ttk
import math

class TemperaturePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#0a0a0a')
        self.temp = 0
        self.pressure = 0
        self.create_widgets()
        self.update_temp()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg='#0a0a0a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        left_frame = tk.Frame(main_frame, bg='#0a0a0a')
        left_frame.pack(side='left', fill='y', padx=(0, 20))

        self.data_panel = tk.Frame(left_frame, bg='#1a1a1a', relief='flat', bd=0)
        self.data_panel.pack(fill='y', pady=10)
        self.data_panel.configure(width=300)

        header = tk.Frame(self.data_panel, bg='#FF4444', height=50)
        header.pack(fill='x')
        header_label = tk.Label(header, text="🌡️ ENVIRONMENT DATA", bg='#FF4444', fg='#000000',
                               font=('Arial', 14, 'bold'))
        header_label.pack(pady=15)

        content_frame = tk.Frame(self.data_panel, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True, pady=20, padx=20)

        temp_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
        temp_frame.pack(fill='x', pady=12, padx=10)
        
        temp_title = tk.Label(temp_frame, text="TEMPERATURE", bg='#2a2a2a', fg='#ffffff',
                             font=('Arial', 12, 'bold'))
        temp_title.pack(anchor='w', padx=10, pady=(10, 0))
        
        temp_value_frame = tk.Frame(temp_frame, bg='#2a2a2a')
        temp_value_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        self.temp_value_label = tk.Label(temp_value_frame, text="0.0", bg='#2a2a2a', fg='#FF4444',
                                        font=('Arial', 20, 'bold'))
        self.temp_value_label.pack(side='left')
        
        temp_unit = tk.Label(temp_value_frame, text="°C", bg='#2a2a2a', fg='#888888',
                            font=('Arial', 12))
        temp_unit.pack(side='left', padx=(10, 0), pady=5)

        pressure_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
        pressure_frame.pack(fill='x', pady=12, padx=10)
        
        pressure_title = tk.Label(pressure_frame, text="PRESSURE", bg='#2a2a2a', fg='#ffffff',
                                 font=('Arial', 12, 'bold'))
        pressure_title.pack(anchor='w', padx=10, pady=(10, 0))
        
        pressure_value_frame = tk.Frame(pressure_frame, bg='#2a2a2a')
        pressure_value_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        self.pressure_value_label = tk.Label(pressure_value_frame, text="0.0", bg='#2a2a2a', fg='#4FC3F7',
                                            font=('Arial', 20, 'bold'))
        self.pressure_value_label.pack(side='left')
        
        pressure_unit = tk.Label(pressure_value_frame, text="kPa", bg='#2a2a2a', fg='#888888',
                                font=('Arial', 12))
        pressure_unit.pack(side='left', padx=(10, 0), pady=5)

        state_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
        state_frame.pack(fill='x', pady=12, padx=10)
        
        state_title = tk.Label(state_frame, text="THERMAL STATE", bg='#2a2a2a', fg='#ffffff',
                              font=('Arial', 12, 'bold'))
        state_title.pack(anchor='w', padx=10, pady=(10, 0))
        
        self.state_value_label = tk.Label(state_frame, text="NORMAL", bg='#2a2a2a', fg='#4CAF50',
                                         font=('Arial', 14, 'bold'))
        self.state_value_label.pack(anchor='w', padx=10, pady=(5, 10))

        visualization_frame = tk.Frame(main_frame, bg='#0a0a0a')
        visualization_frame.pack(side='right', fill='both', expand=True)

        viz_header = tk.Frame(visualization_frame, bg='#FF4444', height=50)
        viz_header.pack(fill='x')
        viz_label = tk.Label(viz_header, text="THERMAL VISUALIZATION", bg='#FF4444', fg='#000000',
                            font=('Arial', 14, 'bold'))
        viz_label.pack(pady=15)

        self.thermo_canvas = tk.Canvas(visualization_frame, width=400, height=400, bg='#111111', 
                                      highlightthickness=2, highlightbackground='#FF4444')
        self.thermo_canvas.pack(expand=True, pady=20)

    def set_temp(self, value):
        self.temp = value
    
    def set_pressure(self, value):
        self.pressure = value

    def update_temp(self):
        temp_val = max(-20, min(60, self.temp))
        pressure_val = max(0, min(100, self.pressure))
        
        self.thermo_canvas.delete("all")
        
        width = self.thermo_canvas.winfo_width()
        height = self.thermo_canvas.winfo_height()
        
        thermo_width = 80
        thermo_height = 300
        thermo_x = (width - thermo_width) // 2
        thermo_y = (height - thermo_height) // 2
        
        self.thermo_canvas.create_rectangle(thermo_x, thermo_y, 
                                          thermo_x + thermo_width, thermo_y + thermo_height,
                                          fill='#2a2a2a', outline='#ffffff', width=2)
        
        temp_range = 80
        temp_height = int((temp_val + 20) / temp_range * thermo_height)
        temp_y = thermo_y + thermo_height - temp_height
        
        hue = 240 - (temp_val + 20) * 3
        r, g, b = self.hsv_to_rgb(hue, 1, 1)
        color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        
        self.thermo_canvas.create_rectangle(thermo_x, temp_y, 
                                          thermo_x + thermo_width, thermo_y + thermo_height,
                                          fill=color, outline='')
        
        for i in range(0, 81, 10):
            y_pos = thermo_y + thermo_height - (i / temp_range * thermo_height)
            self.thermo_canvas.create_line(thermo_x - 10, y_pos, thermo_x, y_pos, fill='#ffffff', width=1)
            self.thermo_canvas.create_text(thermo_x - 15, y_pos, text=str(i-20), fill='#ffffff', 
                                         font=('Arial', 10))
        
        self.temp_value_label.config(text=f"{temp_val:.1f}")
        self.pressure_value_label.config(text=f"{pressure_val:.1f}")
        
        state = "HOT" if temp_val > 35 else "WARM" if temp_val > 15 else "COLD"
        state_color = "#FF4444" if temp_val > 35 else "#FF9800" if temp_val > 15 else "#4FC3F7"
        self.state_value_label.config(text=state, fg=state_color)
        
        self.after(50, self.update_temp)

    def hsv_to_rgb(self, h, s, v):
        h = max(0, min(360, h))
        s = max(0, min(1, s))
        v = max(0, min(1, v))
        
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return r + m, g + m, b + m