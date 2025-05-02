# tuilib: Your Pythonic Terminal UI Companion

## What is tuilib?

`tuilib` is a Python library designed to simplify the creation of Terminal User Interfaces (TUIs). It provides a high-level, intuitive, and Pythonic way to build interactive command-line applications. Instead of wrestling with low-level curses functions, `tuilib` allows you to define your UI with Python objects and methods.

## Why tuilib?

I created `tuilib` because I found that existing TUI libraries for Python often felt cumbersome and not very "Pythonic". Many required developers to manage low-level details, making the development process more complex than it needed to be. There was a need for a library that allowed Python developers to quickly and easily create TUIs using familiar Python concepts. `tuilib` aims to fill that gap by providing:

* **A High-Level API:** Focus on defining your UI's structure and behavior, not on low-level terminal manipulation.
* **Intuitive Design:** Create UI elements and manage interactions in a way that feels natural to Python programmers.
* **Pythonic Conventions:** Embrace Python's principles of readability and simplicity.

## Who Benefits from tuilib?

`tuilib` is ideal for Python programmers who want to:

* Build interactive command-line tools.
* Create user-friendly interfaces for scripts and applications.
* Develop terminal-based dashboards or monitoring tools.
* Quickly prototype and iterate on command-line UI ideas.
* Avoid the complexities of lower-level TUI libraries.

Essentially, any Python developer who needs a TUI and values a clean, efficient, and Pythonic approach will find `tuilib` beneficial.

## How Does It Work?

`tuilib` provides a set of classes and functions that represent common TUI elements, such as windows, layouts, and input fields. Here's a simplified overview:

1.  **Initialization:** You initialize the library, which sets up the terminal environment.
2.  **Layout Definition:** You define the structure of your UI using layout managers. These managers control how UI elements are arranged within the terminal window.
3.  **Widget Creation:** You create UI elements (widgets) like text boxes, input fields, buttons, and more.
4.  **Event Handling:** You define how the application should respond to user input (e.g., key presses, mouse clicks).
5.  **Main Loop:** `tuilib` handles the main loop, which listens for user input, updates the UI, and redraws the screen as needed.

Under the hood, `tuilib` likely uses a more established library (like `curses` or another backend) to interact with the terminal. However, `tuilib` abstracts away these low-level details, providing a much simpler interface.

## Example Cases

Here are some example cases to illustrate what you can do with `tuilib`:

* **Number Selection:**

    ```python
    from tuilib import tui
    def main(stdscr):
        num:int = tui.number_selector(stdscr,0,0,10) #starts at 0, minimum 0, maximum 10
        tui.func_exit(stdscr)
        print(num)
    tui.main(main)
    ```

    This example demonstrates how to create a number selector, allowing the user to choose a number within a specified range.

* **List Selection:**

    ```python
    from tuilib import tui
    def main(stdscr):
        options = ["banana","grape","cherry","apple"]
        choice = tui.list_selector(stdscr,options)
        tui.func_exit(stdscr)
        print("you chose",choice)
    tui.main(main)
    ```

    This example shows how to present the user with a list of options and retrieve their selection.

* **Real-time Input:**

    ```python
    from tuilib import tui
    def main(stdscr):
        name:str = tui.real_time_input(stdscr,"what is your name?: ")
        tui.func_exit(stdscr)
        print("hello",name)
    tui.main(main)
    ```

    This example illustrates how to capture user input in real-time and display it in the terminal.