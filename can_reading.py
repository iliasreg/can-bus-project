import struct
import can

class CANBusReader:
    def __init__(self, interface='socketcan', channel='can0'):
        try:
            self.bus = can.interface.Bus(channel=channel, bustype=interface)
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to CAN Bus: {e}")
            self.connected = False
    
    def read_sensor_data(self):
        if not self.connected:
            return None
        
        try:
            message = self.bus.recv(timeout=1.0)
            
            if message is None:
                return None
            
            # TODO: REPLACE WITH LUX ID 
            if message.arbitration_id == 0x55:
                print(message.data)  
                lux = int.from_bytes(message.data[:2], byteorder='big')
                return {'type': 'lux', 'value': lux}
            
            # TODO: REPLACE WITH ACCELERATION ID 
            elif message.arbitration_id == 0x124:  
                acceleration = struct.unpack('>f', message.data[:4])[0]
                return {'type': 'acceleration', 'value': acceleration}
            
            # TODO: REPLACE WITH HUMIDITY ID 
            elif message.arbitration_id == 0x125:  
                humidity = int.from_bytes(message.data[:1], byteorder='big')
                return {'type': 'humidity', 'value': humidity}
            
            # TODO: REPLACE WITH PRESSURE ID 
            elif message.arbitration_id == 0x126:  
                pressure = int.from_bytes(message.data[:2], byteorder='big')
                return {'type': 'pressure', 'value': pressure}
            
        except Exception as e:
            print(f"Error reading CAN message: {e}")
            return None
        
        return None

def read_can_bus_data(self):
    if not hasattr(self, 'can_reader'):
        self.can_reader = CANBusReader()
    
    data = {
        'lux': 0,
        'acceleration': 0.0,
        'humidity': 0,
        'pressure': 0
    }
    
    for _ in range(10):  
        sensor_data = self.can_reader.read_sensor_data()
        if sensor_data:
            data[sensor_data['type']] = sensor_data['value']
    
    return data

if __name__ == "__main__":

    can = CANBusReader()
    can.read_sensor_data()