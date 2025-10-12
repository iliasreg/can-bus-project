import tkinter as tk
from tkinter import ttk
import math

class LightPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#0a0a0a')
        self.lux = 0
        self.create_widgets()
        self.update_light()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg='#0a0a0a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        left_frame = tk.Frame(main_frame, bg='#0a0a0a')
        left_frame.pack(side='left', fill='y', padx=(0, 20))

        self.data_panel = tk.Frame(left_frame, bg='#1a1a1a', relief='flat', bd=0)
        self.data_panel.pack(fill='y', pady=10)
        self.data_panel.configure(width=300)

        header = tk.Frame(self.data_panel, bg='#FFD700', height=50)
        header.pack(fill='x')
        header_label = tk.Label(header, text="💡 LIGHT SENSOR DATA", bg='#FFD700', fg='#000000',
                               font=('Arial', 14, 'bold'))
        header_label.pack(pady=15)

        content_frame = tk.Frame(self.data_panel, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True, pady=20, padx=20)

        lux_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
        lux_frame.pack(fill='x', pady=15, padx=10)
        
        lux_title = tk.Label(lux_frame, text="ILLUMINANCE", bg='#2a2a2a', fg='#ffffff',
                            font=('Arial', 12, 'bold'))
        lux_title.pack(anchor='w', padx=10, pady=(10, 0))
        
        lux_value_frame = tk.Frame(lux_frame, bg='#2a2a2a')
        lux_value_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        self.lux_value_label = tk.Label(lux_value_frame, text="0.0", bg='#2a2a2a', fg='#FFD700',
                                       font=('Arial', 24, 'bold'))
        self.lux_value_label.pack(side='left')
        
        lux_unit = tk.Label(lux_value_frame, text="lux", bg='#2a2a2a', fg='#888888',
                           font=('Arial', 12))
        lux_unit.pack(side='left', padx=(10, 0), pady=5)

        state_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
        state_frame.pack(fill='x', pady=15, padx=10)
        
        state_title = tk.Label(state_frame, text="LIGHT STATE", bg='#2a2a2a', fg='#ffffff',
                              font=('Arial', 12, 'bold'))
        state_title.pack(anchor='w', padx=10, pady=(10, 0))
        
        self.state_value_label = tk.Label(state_frame, text="DIM", bg='#2a2a2a', fg='#FFD700',
                                         font=('Arial', 16, 'bold'))
        self.state_value_label.pack(anchor='w', padx=10, pady=(5, 10))

        visualization_frame = tk.Frame(main_frame, bg='#0a0a0a')
        visualization_frame.pack(side='right', fill='both', expand=True)

        viz_header = tk.Frame(visualization_frame, bg='#FFD700', height=50)
        viz_header.pack(fill='x')
        viz_label = tk.Label(viz_header, text="LIGHT INTENSITY VISUALIZATION", bg='#FFD700', fg='#000000',
                            font=('Arial', 14, 'bold'))
        viz_label.pack(pady=15)

        self.light_canvas = tk.Canvas(visualization_frame, width=500, height=500, bg='#0a0a0a', 
                                     highlightthickness=2, highlightbackground='#FFD700')
        self.light_canvas.pack(expand=True, pady=20)

    def set_lux(self, value):
        self.lux = value

    def update_light(self):
        intensity = max(0, min(255, int(self.lux / 4)))
        
        self.light_canvas.delete("all")
        
        width = self.light_canvas.winfo_width()
        height = self.light_canvas.winfo_height()
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2 - 20
        
        for radius in range(max_radius, 0, -8):
            alpha = int(intensity * (radius / max_radius))
            if alpha > 0:
                color = self.get_gradient_color(alpha)
                self.light_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    fill=color, outline='', width=0
                )
        
        self.light_canvas.create_oval(
            center_x - max_radius, center_y - max_radius,
            center_x + max_radius, center_y + max_radius,
            outline='#FFD700', width=2
        )
        
        state = "BRIGHT" if self.lux > 500 else "MODERATE" if self.lux > 100 else "DIM"
        state_color = "#00FF00" if self.lux > 500 else "#FFFF00" if self.lux > 100 else "#FF4444"
        
        self.lux_value_label.config(text=f"{self.lux:.1f}")
        self.state_value_label.config(text=state, fg=state_color)
        
        self.after(50, self.update_light)

    def get_gradient_color(self, alpha):
        r = min(255, 255)
        g = min(255, 215 + alpha // 2)
        b = min(255, 0 + alpha // 3)
        return f'#{r:02x}{g:02x}{b:02x}'