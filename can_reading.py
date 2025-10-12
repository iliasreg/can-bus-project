import struct
import can

class CANBusReader:
    def __init__(self, interface='socketcan', channel='can0'):
        try:
            self.bus = can.interface.Bus(channel=channel, interface=interface)
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to CAN Bus: {e}")
            self.connected = False


    def send_message(self, hex_id, data_to_send):
        with self.bus as canbus:
            msg = can.Message(arbitration_id=hex_id, data=data_to_send, is_extended_id=False)
            print("Sending message:", msg)
            canbus.send(msg)
    
    def read_sensor_data(self):
        if not self.connected:
            return None
        
        try:
            message = self.bus.recv(timeout=1.0)

            if message is None:
                return None
            
            if message.arbitration_id == 0x11:

                if len(message.data) >= 2:
                    flag = struct.unpack(">H", message.data[0:2])[0]
                    value = struct.unpack(">H", message.data[2:4])[0]

                    if flag == 0:
                        print("Lux:", value)
                        return {'type': 'lux', 'value': value}
                    elif flag == 1:
                        print("Range:", value)  
                        return {'type': 'range', 'value': value}
                    else:
                        return {}
            
            elif message.arbitration_id == 0X03:
                if len(message.data) > 2:
                    anemo = struct.unpack(">H", message.data[0:2])[0]
                    print("Anemo:", anemo)
                    return {'type': 'anemo', 'value': anemo}
            
            elif message.arbitration_id == 0x12:  
                if len(message.data) > 2:
                    temp = struct.unpack(">H", message.data[0:2])[0]
                    humidity = struct.unpack(">H", message.data[2:4])[0]
                    print("temperature:", temp/1000, "humidity:", humidity/1000)
                    return [{'type': 'temperature', 'value': temp/1000}, {'type': 'humidity', 'value': humidity/1000}]
                
            elif message.arbitration_id == 0x13:  
                if len(message.data) > 2:
                    pression1 = struct.unpack(">H", message.data[0:2])[0]
                    pression2 = struct.unpack(">H", message.data[2:4])[0]
                    pression = (pression1*(2**16) + pression2)/1000
                    print("pressure:", pression)
                    return {'type': 'pressure', 'value': pression}
            
            elif message.arbitration_id == 0x21:  
                if len(message.data) > 2:
                    alpha = struct.unpack(">H", message.data[0:2])[0]
                    theta = struct.unpack(">H", message.data[2:4])[0]
                    psi = struct.unpack(">H", message.data[4:6])[0]

                    print("Alpha:", alpha/1000, "Theta:", theta/1000, "Psi:", psi/1000)
                    return [{'type': 'alpha', 'value': alpha/1000},
                            {'type': 'theta', 'value': theta/1000},
                            {'type': 'psi', 'value': psi/1000}]
            
        except Exception as e:
            print(f"Error reading CAN message: {e}")
            return None
        
        return None

def read_can_bus_data(self):
    if not hasattr(self, 'can_reader'):
        self.can_reader = CANBusReader()
    
    data = {
        'lux': 0,
        'range': 0,
        'anemo': 0,
        'temperature': 0,
        'pressure': 0,
        'alpha': 0,
        'theta': 0,
        'psi': 0
    }
    
    for _ in range(10):  
        sensor_data = self.can_reader.read_sensor_data()
        if hasattr(sensor_data, "__len__"):
            for obj in sensor_data:
                data[obj['type']] = obj['value']
        else:
            data[sensor_data['type']] = sensor_data['value']


    return data

if __name__ == "__main__":

    canBus = CANBusReader()
    
    id = 0x03
    data = [0, 0, 0, 1, 3, 1, 4, 1]

    #canBus.send_message(id, data)
    #can.read_sensor_data()
    #canBus.read_sensor_data()

    """
    flag = input("Lux (0) or Range (1) ?")
    if flag == 0:
        canBus.send_message(0x11, [0, 0, 0, 1, 3, 1, 4, 1])
    elif flag == 1:
        canBus.send_message(0x11, [0xF, 0xF, 0, 1, 3, 1, 4, 1])
    else:
        print("Invalid syntax")
    """

    while True:
        canBus.read_sensor_data()