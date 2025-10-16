import tkinter as tk
from tkinter import ttk
import math
import can

from can_reading import CANBusReader

class AccelerationPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#0a0a0a')
        self.accel = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.motor_speed = 0  # Variable pour stocker la vitesse du moteur
        self.reader = CANBusReader
        self.create_widgets()
        self.update_rotation()

        try:
            self.bus = can.interface.Bus('can0', bustype='socketcan')
        except Exception as e:
            print(f"CAN init error: {e}")
            self.bus = None

    def create_widgets(self):
        main_frame = tk.Frame(self, bg='#0a0a0a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        left_frame = tk.Frame(main_frame, bg='#0a0a0a')
        left_frame.pack(side='left', fill='y', padx=(0, 20))

        self.data_panel = tk.Frame(left_frame, bg='#1a1a1a', relief='flat', bd=0)
        self.data_panel.pack(fill='y', pady=10)
        self.data_panel.configure(width=300)

        header = tk.Frame(self.data_panel, bg='#00d4ff', height=50)
        header.pack(fill='x')
        header_label = tk.Label(header, text="🌀 ANGULAR DATA", bg='#00d4ff', fg='#000000',
                               font=('Arial', 14, 'bold'))
        header_label.pack(pady=15)

        content_frame = tk.Frame(self.data_panel, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True, pady=20, padx=20)

        sensors = [
            ("α ALPHA", "alpha", "#FF9800"),
            ("θ THETA", "theta", "#9C27B0"), 
            ("ψ PSI", "psi", "#4CAF50"),
            ("ANEMO", "anemo", "#1C0FF0")
        ]

        for title, key, color in sensors:
            sensor_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
            sensor_frame.pack(fill='x', pady=8, padx=10)
            
            title_label = tk.Label(sensor_frame, text=title, bg='#2a2a2a', fg='#ffffff',
                                  font=('Arial', 12, 'bold'))
            title_label.pack(anchor='w', padx=10, pady=(10, 0))
            
            value_frame = tk.Frame(sensor_frame, bg='#2a2a2a')
            value_frame.pack(fill='x', padx=10, pady=(5, 10))
            
            value_label = tk.Label(value_frame, text="0.00", bg='#2a2a2a', fg=color,
                                  font=('Arial', 16, 'bold'))
            value_label.pack(side='left')
            setattr(self, f'{key}_label', value_label)
            
            unit_label = tk.Label(value_frame, text="rad", bg='#2a2a2a', fg='#888888',
                                 font=('Arial', 10))
            unit_label.pack(side='left', padx=(5, 0))

        # Frame pour le contrôle du moteur
        motor_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='flat', bd=0)
        motor_frame.pack(fill='x', pady=15, padx=10)
        
        motor_title = tk.Label(motor_frame, text="🚀 MOTOR SPEED CONTROL", bg='#2a2a2a', fg='#ffffff',
                              font=('Arial', 12, 'bold'))
        motor_title.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Frame pour la valeur numérique
        motor_value_frame = tk.Frame(motor_frame, bg='#2a2a2a')
        motor_value_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        self.motor_value_label = tk.Label(motor_value_frame, text="0", bg='#2a2a2a', fg='#FF6B35',
                                         font=('Arial', 16, 'bold'))
        self.motor_value_label.pack(side='left')
        
        motor_unit_label = tk.Label(motor_value_frame, text="/255", bg='#2a2a2a', fg='#888888',
                                   font=('Arial', 10))
        motor_unit_label.pack(side='left', padx=(5, 0))
        
        self.motor_slider = tk.Scale(
            motor_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            length=250,
            showvalue=False,
            bg='#2a2a2a',
            fg='#ffffff',
            highlightbackground='#2a2a2a',
            troughcolor='#1a1a1a',
            activebackground='#FF6B35',
            sliderrelief='flat',
            sliderlength=20,
            command=self._on_motor_speed_change
        )
        
        # Style personnalisé pour le slider
        self.motor_slider.configure(
            background='#2a2a2a',
            troughcolor='#1a1a1a',
            activebackground='#FF6B35'
        )
        
        self.motor_slider.pack(fill='x', padx=10, pady=(5, 15))
        
        # Labels min/max
        slider_labels_frame = tk.Frame(motor_frame, bg='#2a2a2a')
        slider_labels_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        min_label = tk.Label(slider_labels_frame, text="0", bg='#2a2a2a', fg='#888888',
                            font=('Arial', 9))
        min_label.pack(side='left')
        
        max_label = tk.Label(slider_labels_frame, text="255", bg='#2a2a2a', fg='#888888',
                            font=('Arial', 9))
        max_label.pack(side='right')

        visualization_frame = tk.Frame(main_frame, bg='#0a0a0a')
        visualization_frame.pack(side='right', fill='both', expand=True)

        viz_header = tk.Frame(visualization_frame, bg='#00d4ff', height=50)
        viz_header.pack(fill='x')
        viz_label = tk.Label(viz_header, text="3D ACCELERATION VISUALIZATION", bg='#00d4ff', fg='#000000',
                            font=('Arial', 14, 'bold'))
        viz_label.pack(pady=15)

        self.cube_canvas = tk.Canvas(visualization_frame, width=500, height=500, bg='#070707', 
                                    highlightthickness=2, highlightbackground='#00d4ff')
        self.cube_canvas.pack(expand=True, pady=20)

    def _on_motor_speed_change(self, value):
        try:
            id = 0x03
            data = [int(value), 0, 0, 1, 3, 1, 4, 1]
            speed = hex(int(value))
            self.reader.send_message(self, id, data)
            print(f"Commanding motor speed: {speed}")
        except ValueError:
            pass

    def set_accel(self, x, y, z):
        self.accel = [x, y, z]

    def update_rotation(self):
        ax, ay, az = self.accel
        self.rotation[0] = ax * 2
        self.rotation[1] = ay * 2
        self.rotation[2] = az * 2
        
        self.draw_modern_cube()
        
        self.alpha_label.config(text=f"{ax:.2f}")
        self.theta_label.config(text=f"{ay:.2f}")
        self.psi_label.config(text=f"{az:.2f}")

        self.anemo_label.config(text=f"{az:.2f}")
        
        self.after(30, self.update_rotation)

    def draw_modern_cube(self):
        self.cube_canvas.delete("all")
        
        width = self.cube_canvas.winfo_width()
        height = self.cube_canvas.winfo_height()
        center_x, center_y = width // 2, height // 2
        
        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        
        projected = []
        for vertex in vertices:
            x, y, z = vertex
            
            x, y, z = self.rotate_x(x, y, z, self.rotation[0])
            x, y, z = self.rotate_y(x, y, z, self.rotation[1])
            x, y, z = self.rotate_z(x, y, z, self.rotation[2])
            
            scale = 80
            x_proj = x * scale + center_x
            y_proj = y * scale + center_y
            
            projected.append((x_proj, y_proj, z))
        
        faces = [
            [0, 1, 2, 3], [4, 5, 6, 7], [0, 4, 7, 3],
            [1, 5, 6, 2], [0, 1, 5, 4], [3, 2, 6, 7]
        ]
        
        colors = ['#00d4ff', '#0096B4', '#0074D3', '#005A8F', '#004170', '#002851']
        
        for i, face in enumerate(faces):
            points = []
            avg_z = 0
            for vertex_idx in face:
                points.extend(projected[vertex_idx][:2])
                avg_z += projected[vertex_idx][2]
            avg_z /= len(face)
            
            self.cube_canvas.create_polygon(points, fill=colors[i], outline='#ffffff', width=2, 
                                          stipple='gray50' if i % 2 == 0 else '')

    def rotate_x(self, x, y, z, angle):
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        y_new = y * cos_a - z * sin_a
        z_new = y * sin_a + z * cos_a
        return x, y_new, z_new

    def rotate_y(self, x, y, z, angle):
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        x_new = x * cos_a + z * sin_a
        z_new = -x * sin_a + z * cos_a
        return x_new, y, z_new

    def rotate_z(self, x, y, z, angle):
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        x_new = x * cos_a - y * sin_a
        y_new = x * sin_a + y * cos_a
        return x_new, y_new, z