import argparse
from camtty import CamCharApp
import sys
import threading
from blessed import Terminal

STYLE_CHARS = {
    'default': " .:-=+*#%@",
    'blocks': " ░▒▓█",
    'lines': " │─┼╋",
    'dots': " ·•●○"
}

def parse_args():
    parser = argparse.ArgumentParser(description="Display webcam feed as ASCII art in terminal")
    parser.add_argument("--fps", type=int, default=30, help="Target frames per second")
    parser.add_argument("--chars", type=str, default=" .:-=+*#%@", help="ASCII characters to use (from dark to light)")
    parser.add_argument("--camera", type=int, default=0, help="Camera index to use (default: 0)")
    parser.add_argument("--color", action="store_true", help="Enable colored output")
    parser.add_argument("--effect", choices=['none', 'invert', 'mirror', 'rotate'], 
                       default='none', help="Apply visual effect to the output")
    parser.add_argument("--save", type=str, help="Save the current frame to specified file when 's' is pressed")
    parser.add_argument("--style", choices=['default', 'blocks', 'lines', 'dots'], default='default',
                       help="Choose predefined ASCII character style")
    return parser.parse_args()

def handle_input(app, args):
    """Handle keyboard input in a separate thread using blessed."""
    term = Terminal()
    # Use blessed context manager for cbreak mode; it handles setup and restoration
    with term.cbreak():
        while app.running:
            # Use term.inkey with a timeout for non-blocking input
            key = term.inkey(timeout=0.1) # timeout in seconds

            # Check if a key was actually pressed (key is not an empty string)
            if key:
                key_char = str(key).lower() # Get lower-case string representation

                # Check for quit keys (q or Esc)
                # Note: Ctrl+C (SIGINT) might still work depending on terminal/blessed,
                # but explicitly handling 'q' and Esc is good
                if key_char == 'q' or key.code == term.KEY_ESCAPE:
                    print(term.move_down(term.height -1) + term.clear_eol + "\rQuitting...\n") # Print at bottom
                    app.running = False
                elif key_char == 's':
                    # Move cursor to bottom line, clear it, print message
                    print(term.move_down(term.height -1) + term.clear_eol, end='')
                    if args.save:
                        if app.save_frame(args.save):
                            print(f"\rFrame saved to {args.save}!\n")
                        else:
                            print(f"\rFailed to save frame to {args.save}.\n")
                    else:
                        print("\rSave path not specified (--save argument missing).\n")
                    # Optional: Reprint controls after message
                    # print("\rControls: q/Esc:quit, s:save, 1-4:effects")
                elif key_char in '1234':
                    effects = ['none', 'invert', 'mirror', 'rotate'] # Map 1 to none
                    effect_name = effects[int(key_char) - 1]
                    app.set_effect(effect_name)
                    # Move cursor to bottom line, clear it, print message
                    print(term.move_down(term.height -1) + term.clear_eol + f"\rEffect set to: {effect_name}\n")
                    # Optional: Reprint controls after message
                    # print("\rControls: q/Esc:quit, s:save, 1-4:effects")

            # No need for explicit time.sleep(), term.inkey(timeout=...) handles waiting

    # No finally block needed here for terminal settings, blessed handles it

def main():
    args = parse_args()
    # Determine ASCII chars based on style and chars arguments
    if args.style != 'default':
        # If a specific style (not default) is chosen, use its characters
        ascii_chars = STYLE_CHARS.get(args.style)
        # Fallback in case of unexpected invalid style (argparse should prevent this
        if ascii_chars is None:
            print(f"Warning: Invalid style '{args.style}' specified. Falling back to --chars value.", file=sys.stderr)
            ascii_chars = args.chars
    else:
        # If style is default, use the value from --chars 
        # (this will be the user's value if provided, otherwise the default chars)
        ascii_chars = args.chars

    app = CamCharApp(
        camera_index=args.camera,
        ascii_chars=ascii_chars, # Pass the correctly determined characters
        fps=args.fps,
        use_color=args.color
    )

    # Set initial effect
    if args.effect != 'none':
        app.set_effect(args.effect)

    # Start input handling in a separate thread
    input_thread = threading.Thread(target=handle_input, args=(app, args), daemon=True)
    input_thread.start()

    # Use blessed for initial control printing as well
    term = Terminal()
    with term.hidden_cursor(): # Hide cursor while app is running
        print(term.clear) # Clear screen initially
        print(term.move_xy(0,0) + "Controls:") # Print controls at top
        print("Press 's' to save the current frame (if --save specified)")
        print("Press 'q' or Esc to quit")
        print("Press '1-4' to switch effects (1:none, 2:invert, 3:mirror, 4:rotate)")

        try:
            app.start() # This loop will now handle frame display
        except KeyboardInterrupt:
            # This might be caught if blessed/cbreak allows it
            print(term.move_down(term.height -1) + term.clear_eol + "\rCtrl+C, stopping...\n")
            app.running = False
        except Exception as e:
            # Ensure cursor is visible and terminal is clean before printing error
            print(term.normal_cursor + term.clear)
            print(f"An error occurred: {e}")
            app.running = False
        finally:
            # Ensure app is signaled to stop and wait for input thread
            if app.running:
                 app.running = False
            if input_thread.is_alive():
                input_thread.join(timeout=1.0) # Wait for input thread to finish
            # Blessed context managers should restore terminal state, py 
            # including cursor visibility and cbreak mode.
            # Explicitly ensure cursor is visible and print exit message at bottom.
            print(term.normal_cursor + term.move_down(term.height -1) + term.clear_eol + "\rExiting application.\n")

if __name__ == "__main__":
    main()