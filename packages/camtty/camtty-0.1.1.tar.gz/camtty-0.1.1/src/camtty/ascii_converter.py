import numpy as np
import cv2

class ASCIIConverter:
    def __init__(self, chars=" .:-=+*#%@", use_color=False):
        self.ascii_chars = chars
        self.use_color = use_color
        self._generate_ascii_map()

    def _generate_ascii_map(self):
        """Precompute ASCII mappings for gd performance """
        self.ascii_map = [self.ascii_chars[int(i / 256 * len(self.ascii_chars))] 
                         for i in range(256)]

    def pixel_to_ascii(self, pixel, color=None):
        """Convert a single pixel value to ASCII character with optional color"""
        char = self.ascii_map[pixel]
        if self.use_color and color is not None:
            b, g, r = color
            return f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        return char

    def frame_to_ascii(self, frame, width, height, effect=None):
        """Convert an entire frame to ASCII art with optional effects"""
        # Resize frame to fit desired dimensions
        resized = cv2.resize(frame, (width, height))

        # Apply effects if specified
        if effect == 'invert':
            resized = cv2.bitwise_not(resized)
        elif effect == 'mirror':
            resized = cv2.flip(resized, 1)
        elif effect == 'rotate':
            resized = cv2.rotate(resized, cv2.ROTATE_90_CLOCKWISE)

        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Convert to ASCII
        if self.use_color:
            ascii_img = []
            for y, row in enumerate(gray):
                ascii_row = []
                for x, pixel in enumerate(row):
                    color = resized[y, x]
                    ascii_row.append(self.pixel_to_ascii(pixel, color))
                ascii_img.append("".join(ascii_row))
        else:
            ascii_img = ["".join([self.pixel_to_ascii(pixel) for pixel in row]) 
                        for row in gray]
        
        return "\n".join(ascii_img)