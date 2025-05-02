import curses


class tui:
    def __init__(self):
        curses.initscr()
        curses.cbreak()  # Enable cbreak mode to capture input immediately
        curses.noecho()  # Disable automatic echoing of input

    def number_selector(stdscr,start_value=0,min_value=-999999999,max_value=9999999):
        value = start_value
        while True:
            stdscr.clear()
            stdscr.addstr(str(value))
            stdscr.refresh()
            key = stdscr.getch()

            if key == curses.KEY_DOWN and value > min_value:
                value -= 1
            elif key == curses.KEY_UP and value < max_value:
                value += 1
            elif key == 10:
                break
        return value

    def list_selector(stdscr, options, start_index=0):
        curses.curs_set(0)  # Hide cursor
        current_index = start_index

        while True:
            stdscr.clear()

        # Display the list with arrow for selection
            for idx, option in enumerate(options):
                if idx == current_index:
                    stdscr.addstr(f"> {option}\n", curses.A_REVERSE)  # Highlight selected item
                else:
                    stdscr.addstr(f"  {option}\n")

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP and current_index > 0:
                current_index -= 1
            elif key == curses.KEY_DOWN and current_index < len(options) - 1:
                current_index += 1
            elif key == 10:  # Enter key
                break

        return options[current_index]


    def real_time_input(stdscr, prompt=""):
        curses.curs_set(1)  # Show cursor
        input_str = ""
        stdscr.clear()
        while True:
            stdscr.clear()
            stdscr.addstr(f"{prompt}{input_str}")
            stdscr.refresh()

            key = stdscr.getch()

            if key == 27:  # ESC key to exit the input loop
                break
            elif key == 10:  # Enter key
                break
            elif key == 127:  # Backspace key
                new_str = []
                input_str = input_str[:-1]
                for string in input_str:
                    string = string.replace("\\b","\b")
                    new_str.append(string)
                input_str = "".join(new_str)
            else:
                input_str += chr(key)

        return input_str
    
    def func_exit(stdscr):
        curses.endwin()
    
    
    def main(func):
        curses.wrapper(func)
