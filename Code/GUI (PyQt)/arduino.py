import serial
import serial.tools.list_ports
import time


class ArduinoController:
    def __init__(self):
        self.arduino = None
        self.port_name = None
        self.ready = False

    def scan_and_connect(self):
        ports = serial.tools.list_ports.comports()
        available_ports = [p.device for p in ports]

        # Already connected
        if self.arduino is not None:
            if (self.arduino.is_open and self.port_name in available_ports):
                return True

            # Connection lost
            try:
                self.arduino.close()
            except:
                pass

            self.arduino = None
            self.port_name = None
            self.ready = False

        # Scaning ports
        for port in ports:
            try:
                arduino = serial.Serial(port=port.device, baudrate=9600, timeout=0.2, write_timeout=0.2)

                # microcontroller resets when serial connection opens
                time.sleep(2)

                arduino.reset_input_buffer()
                arduino.reset_output_buffer()

                # Ask Arduino to identify itself
                arduino.write(b"PING\n")

                response = arduino.readline().decode("ascii", errors="ignore").strip()

                if response == "PONG":
                    self.arduino = arduino
                    self.port_name = port.device
                    self.ready = True

                    print(f"Arduino connected on {port.device}")

                    return True

                # Not our Arduino :(
                arduino.close()

            except (serial.SerialException, OSError):
                continue

        return False

       

    def set_color(self, r, g, b):
        if not self.ready or not self.arduino:
            return
        if not self.arduino.is_open:
            self.ready = False
            return

        command = f"COLOR:{r},{g},{b}\n"

        try:
            self.arduino.write(command.encode("ascii"))
        except (serial.SerialException, OSError):
            self.ready = False
            try:
                self.arduino.close()
            except:
                pass

            self.arduino = None
            self.port_name = None
            
    def disconnect(self):
        if self.arduino is not None:
            try:
                self.arduino.close()
            except:
                pass

        self.arduino = None
        self.port_name = None
        self.ready = False
    
