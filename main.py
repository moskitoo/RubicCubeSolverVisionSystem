from typing import List, Dict

import cv2 as cv
import numpy as np
import json
import keyboard
import math
import kociemba
import serial
import time


class ConfigManager:
    """
    Reades config file containing all parameters used by program's components.
    """
    def __init__(self) -> None:
        self.load_config_file()
    
    def load_config_file(self) -> None:
        try:
            with open("config.json", "r+") as self.config_file:
                self.config = json.load(self.config_file)
        except FileNotFoundError:
            print("Config not found")
    
    def update_config_file(self) -> None:
        self.config.update()
        with open("config.json", "w") as self.config_file:
            json.dump(self.config, self.config_file, indent=4)


class WindowManager:
    """
    Creates windows, displaying camera images.
    """
    def __init__(self, config_manager: ConfigManager) -> None:
        self.read_config(config_manager.config)
        self.capture = cv.VideoCapture(self.video_source)
        self.create_window_list()
    
    @staticmethod
    def get_color_mean_values(window: np.ndarray) -> List:
        """remember to insert proper colorscape!"""
        return window.mean(axis=0).mean(axis=0).astype(int).tolist()
    
    def read_config(self, config: json) -> None:
        video_config = config["video"]
        table_config = config["table"]
        self.video_source = video_config["source"]
        self.table_start_x = table_config["start_x"]
        self.table_start_y = table_config["start_y"]
        self.slot_width = config["table"]["slot_width"]
        self.cube_size = config["cube"]["size"]
        self.cube_slots = self.cube_size ** 2
        self.table_color = tuple(config["table"]["color"])
        self.table_line_thickness = config["table"]["line_thickness"]
    
    def show_window(self, **kwargs: List[Dict]) -> None:
        for key, value in kwargs.items():
            cv.imshow(key, value)
    
    def run(self) -> None:
        self.read_base_frame()
        self.get_main_frame()
        self.create_copied_frame()
        
        self.fill_window_list()
        self.get_window_color_list()
        self.draw_table(self.frame_copy)

        self.show_window(frame_copy = self.frame_copy, 
                            crop = self.window_list[0],
                            main_frame = self.main_frame)
    
    def read_base_frame(self):
        self.ret, self.frame = self.capture.read()

    def create_copied_frame(self):
        self.frame_copy = np.copy(self.frame)
    
    def create_window_list(self) -> None:
        self.window_list = []

    def fill_window_list(self) -> None:
        self.reset_list(self.window_list)
        for slot in range(self.cube_slots):
            self.window_list.append(self.get_cropped_frame(slot))
    
    def get_window_color_list(self) -> None:
        self.window_color_list = [self.get_color_mean_values(slot) for slot in self.window_list]

    @staticmethod
    def reset_list(list: list):
        list.clear()

    def get_main_frame(self) -> None:
        self.main_frame = self.frame[self.table_start_y : self.table_start_y + self.slot_width * self.cube_size, 
                                     self.table_start_x : self.table_start_x + self.slot_width * self.cube_size]

    def get_cropped_frame(self, slot_number: int) -> np.ndarray:
        return self.frame[self.get_window_start_y(slot_number) : self.get_window_end_y(slot_number), 
                          self.get_window_start_x(slot_number) : self.get_window_end_x(slot_number)]

    def get_window_end_y(self, slot_number):
        return self.get_window_start_y(slot_number) + self.slot_width

    def get_window_end_x(self, slot_number):
        return self.get_window_start_x(slot_number) + self.slot_width

    def get_window_start_x(self, slot_number: int) -> int:
        return self.table_start_x + \
            ((slot_number + self.cube_size) % self.cube_size) * self.slot_width
    
    def get_window_start_y(self, slot_number: int):
        if slot_number == 0:
            rest = 0
        else:
            rest = slot_number // self.cube_size
        return self.table_start_y + rest * self.slot_width

    def draw_table(self, window) -> None:
        for slot in range(self.cube_slots):
            cv.rectangle(window,
                         (self.get_window_start_x(slot),self.get_window_start_y(slot)),
                         (self.get_window_end_x(slot), self.get_window_end_y(slot)),
                         self.table_color,
                         self.table_line_thickness)


class CalibrationManager:
    """
    Tool compensate impact of variable lighting by calculating mean RGB value of plain color walls.
    """
    
    def __init__(self, config_manager: ConfigManager, window_manager: WindowManager) -> None:
        self.window_manager = window_manager
        self.config_manager = config_manager
        self.load_calibration_colors(self.config_manager.config)
        self.check_provided_colors()

    def load_calibration_colors(self, config):
        try:
            self.color_calibration = config["colors"]
        except KeyError:
            print("Calibration colors not found")

    def check_provided_colors(self) -> None:
        if len(self.color_calibration) != 6:
            print("Some color calibration missing")

    def update_calib_color(self, color: str):
        self.color_calibration[color]["color_values"] = self.window_manager.get_color_mean_values(self.window_manager.main_frame)
        self.config_manager.update_config_file()
        print(f"{color} color calibrated.")


class ColorDetector:
    """
    Tool used by WallScanner to detect color.
    """
    
    def __init__(self, calibration_manager: CalibrationManager) -> None:
        self.calibration_manager = calibration_manager

    def detect_color(self, given_color: List) -> str:
        self.closest_color = self.find_closest_color(given_color)
        return self.calibration_manager.color_calibration[self.closest_color]["code"]

    @staticmethod
    def calculate_distance(given_color: List, calibration_color: List) -> float:
        sum = 0
        for given_color_primary_val, calib_color_primary_val in zip(given_color,
                                                                    calibration_color):
            diff = calib_color_primary_val - given_color_primary_val
            sum += diff ** 2
        return math.sqrt(sum)

    def find_closest_color(self, given_color: List) -> Dict:
        distance_dict = {}
        for key, value in self.calibration_manager.color_calibration.items():
           distance_dict[key] = self.calculate_distance(given_color,
                                                        value["color_values"])
        return min(distance_dict, key=distance_dict.get)

class WallScanner:
    """
    By using camera image projects colors of the rubic cube.
    """

    def __init__(self, window_manager: WindowManager, color_detector: ColorDetector) -> None:
        self.cube_walls = {"up": None,
                           "right": None,
                           "front": None,
                           "down": None,
                           "left": None,
                           "back": None
                           }
        self.window_manager = window_manager
        self.color_detector = color_detector
    
    def scan_wall(self, wall: str) -> None:
        self.cube_walls[wall] = [self.color_detector.detect_color(slot) 
                                 for slot 
                                 in self.window_manager.window_color_list]
        print(f"{wall} scanned")
        print(self.cube_walls[wall])
    
    def set_middle_slots(self):
        self.cube_walls["up"][4] = "W"
        self.cube_walls["right"][4] = "O"
        self.cube_walls["front"][4] = "B"
        self.cube_walls["down"][4] = "Y"
        self.cube_walls["left"][4] = "R"
        self.cube_walls["back"][4] = "G"
        

class KociembaManager:
    """
    Produces moves necessary to solve a cube.
    """
    
    def __init__(self, wall_scanner: WallScanner) -> None:
        self.wall_scanner = wall_scanner
    
    def create_wall_string(self) -> None:
        self.reset_wall_string()
        self.wall_scanner.set_middle_slots()
        for key, value in self.wall_scanner.cube_walls.items():
            a = "".join(value)
            self.wall_string += a
        print(self.wall_scanner.cube_walls)
    
    def reset_wall_string(self) -> None:
        self.wall_string = ""
    
    def get_moves(self) -> None: 
        self.moves = kociemba.solve(self.wall_string).split()


class ArduinoManager():
    """
    Maintains connection with Arduino. Methods are being called by KeyboardManager.
    """
    
    def __init__(self, config_manager: ConfigManager, kociemba_manager: KociembaManager) -> None:
        self.config = config_manager.config
        self.kociemba_manager = kociemba_manager
        self.load_config()
        self.establish_connection()
    
    def load_config(self) -> None:
        arduino_config = self.config["arduino"]
        self.port = arduino_config["port"]
        self.baudrate = arduino_config["baudrate"]
        self.timeout = arduino_config["timeout"]
    
    def establish_connection(self) -> None:
        self.connection = serial.Serial(port=self.port,
                                        baudrate=self.baudrate,
                                        timeout=self.timeout)
    
    def send_moves(self) -> None:
        move_availible = True
        # for move in self.kociemba_manager.moves:
        self.moves = ["U","U","U","U","U","U","U","U"]
        for move in self.moves:
            self.connection.write(self.encode_message(move))
            move_availible = False
            while move_availible == False:
                data = self.decode_message(self.connection.readline().strip())
                if data == "move completed":
                    print(data)
                    move_availible = True
        print("Sending moves completed.")
            
    def write_read(self, x):
        self.connection.write(bytes(x, 'utf-8'))
        time.sleep(0.05)
        data = self.connection.readline()
        return data

    @staticmethod
    def encode_message(message: str) -> bytes:
        return bytes(message, 'utf-8')
    
    @staticmethod
    def decode_message(message: bytes) -> str:
        return message.decode('utf-8')


class KeyboardManager:
    """
    Class responsible for managing keyborad interrupts caused by user
    (color calibration, wall scanning, sending moves to arduino).
    """

    def __init__(self, 
                 config_manager: ConfigManager, 
                 calibration_manager: CalibrationManager, 
                 wall_scanner: WallScanner,
                 kociemba_manager: KociembaManager,
                 arduino_manager: ArduinoManager) -> None:
        self.config = config_manager.config
        self.calibration_manager = calibration_manager
        self.wall_scanner = wall_scanner
        self.kociemba_manager = kociemba_manager
        self.arduino_manager = arduino_manager
        self.availible_buttons = self.load_buttons() 
        
    def run(self) -> None:
        for button in self.availible_buttons:
            if keyboard.is_pressed(button):
                self.manage_button(button)

    def manage_button(self, pressed_button: str) -> None:
        invoke_metadata: Dict = self.get_invoke_metadata(pressed_button)
        object = getattr(self,invoke_metadata['object'])
        try: 
            args = self.get_args_tuple(invoke_metadata['args'])
        except:
            getattr(object,invoke_metadata['function'])()
        else:
            getattr(object,invoke_metadata['function'])(*args)

    @staticmethod
    def get_args_tuple(args_dict: Dict) -> tuple:
        return tuple(args_dict.values())

    def get_invoke_metadata(self, button: str) -> Dict:
        return self.config["buttons"][button]
    
    def load_buttons(self) -> Dict:
        return self.config["buttons"].keys()
    

class RubicSolver():
    """Main class. Responsible for managing other subclasses."""
    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager(self.config_manager)
        self.calibration_manager = CalibrationManager(self.config_manager, 
                                                      self.window_manager)
        self.color_detector = ColorDetector(self.calibration_manager)
        self.wall_scanner = WallScanner(self.window_manager, 
                                        self.color_detector)
        self.kociemba_manager = KociembaManager(self.wall_scanner)
        self.arduino_manager = ArduinoManager(self.config_manager, self.kociemba_manager)
        self.keyboard_manager = KeyboardManager(self.config_manager, 
                                                self.calibration_manager,
                                                self.wall_scanner,
                                                self.kociemba_manager,
                                                self.arduino_manager)
        self.stop_key = self.config_manager.config["video"]["stop_key"]
        self.run_loop = True

    def run(self) -> None:
       while self.run_loop:
           self.window_manager.run()
           self.keyboard_manager.run()
           self.check_stop_flag(self.stop_key)
    
    def check_stop_flag(self, key: str) -> None:
        if cv.waitKey(1) == ord(key):
            print(self.wall_scanner.cube_walls)
            self.run_loop = False

if __name__ == '__main__':
    app = RubicSolver()
    app.run()