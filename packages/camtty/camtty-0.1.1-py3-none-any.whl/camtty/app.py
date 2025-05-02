from .ascii_converter import ASCIIConverter
from .camera_handler import CameraHandler
from .terminal_display import TerminalDisplay
import sys
import os
import cv2
import datetime

class CamCharApp:
    def __init__(self, camera_index=0, ascii_chars=" .:-=+*#%@", fps=30, use_color=False):
        self.converter = ASCIIConverter(ascii_chars, use_color)
        self.camera = CameraHandler(camera_index)
        self.display = TerminalDisplay()
        self.display.set_fps(fps)
        self.running = False
        self.current_effect = None
        self.current_frame = None
        self.current_ascii = None

    def save_frame(self, path=None):
        """Save current ASCII frame to a file"""
        if self.current_ascii is None:
            return False
            
        if path is None:
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"ascii_frame_{timestamp}.txt"
        
        try:
            with open(path, 'w') as f:
                f.write(self.current_ascii)
            return True
        except Exception as e:
            print(f"Error saving frame: {e}")
            return False

    def set_effect(self, effect):
        """Set current effect (None, 'invert', 'mirror', 'rotate')"""
        if effect in (None, 'invert', 'mirror', 'rotate'):
            self.current_effect = effect
            return True
        return False

    def start(self):
        """Start the ASCII webcam feed"""
        try:
            self.running = True
            self.camera.start()
            
            while self.running:
                # Get terminal dimensions
                width, height = self.display.get_terminal_size()
                if width < 10 or height < 5:
                    print("Terminal size too small")
                    break

                # Capture and convert frame
                self.current_frame = self.camera.get_frame()
                if self.current_frame is None:
                    break
                
                # Convert to ASCII and display
                self.current_ascii = self.converter.frame_to_ascii(
                    self.current_frame, 
                    width, 
                    height,
                    self.current_effect
                )
                self.display.display_frame(self.current_ascii)

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the application and clean up resources"""
        self.running = False
        self.camera.release()