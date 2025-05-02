import os
import time

class TerminalDisplay:
    def __init__(self):
        self.last_display_time = 0
        self.target_fps = 30

    def get_terminal_size(self):
        """Get current terminal dimensions"""
        size = os.get_terminal_size()
        return size.columns, size.lines - 2  # Leave space for prompt

    def clear_screen(self):
        """Clear the terminal screen"""
        print("\033[H\033[J", end="")

    def display_frame(self, ascii_frame):
        """Display ASCII frame and maintain frame rate"""
        current_time = time.time()
        elapsed = current_time - self.last_display_time
        sleep_time = max(0, 1/self.target_fps - elapsed)
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        self.clear_screen()
        print(ascii_frame)
        self.last_display_time = time.time()

    def set_fps(self, fps):
        """Set target frame rate"""
        self.target_fps = fps