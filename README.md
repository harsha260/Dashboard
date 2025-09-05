-----

# TUI Dashboard

A personal, terminal-based dashboard built with the Python [Textual](https://github.com/Textualize/textual) framework. This application integrates your calendar, tasks, service statuses, and common command-line tools into a single, efficient, and navigable interface.
![Screenshot]("D:/Harsha/practice/python/dashboard/v2/img/Screenshot1.png") 
![Screenshot]("D:/Harsha/practice/python/dashboard/v2/img/Screenshot2.png") 
![Screenshot]("D:/Harsha/practice/python/dashboard/v2/img/Screenshot3.png") 
![Screenshot]("D:/Harsha/practice/python/dashboard/v2/img/Screenshot4.png") 
![Screenshot]("D:/Harsha/practice/python/dashboard/v2/img/Screenshot5.png") 
## Features

  * **Home Tab**: A consolidated view displaying your `gcalcli` agenda and `taskbook` items side-by-side.
  * **Interactive Taskbook**: A dedicated tab to add, check/uncheck, and delete tasks and notes from `taskbook` without leaving the dashboard.
  * **Service Status Monitor**: A simple monitor to check if a specified process (e.g., `copyparty`) is running.
  * **Disk Management**: Displays a clean, formatted overview of disk usage by running the `duf` command.
  * **Tool Launcher**: Quickly launch external terminal applications like a task manager (`btop`) and a file explorer (`superfile`).
  * **Keyboard Navigation**: Uses home-row keys (`h`, `b`, `s`, `l`, `f`) to switch between tabs for quick navigation.

## Prerequisites

This dashboard acts as a frontend for several powerful command-line tools. You must install them for the dashboard to be fully functional.

### Python Packages

  * `textual`
  * `psutil`

### External CLI Tools

  * **`gcalcli`**: Required for the Calendar pane.
      * **Note**: You must run `gcalcli` at least once from your terminal to authorize it with your Google account.
  * **`tb` (`taskbook`)**: Required for all task and note functionality.
  * **`duf`**: Required for the Disk Management tab.
  * **`btop`** (or `btop4win`): Used by the "Task Manager" button.
  * **`superfile`** (as `spf`): Used by the "File Explorer" button.

## Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/harsha260/Dashboard.git
    cd Dashboard
    ```

2.  **Set up a Virtual Environment (Recommended)**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install Python Dependencies**
    Create a `requirements.txt` file with the following content:

    ```txt
    textual
    psutil
    ```

    Then, install the packages:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Install External Tools**
    Use your system's package manager (e.g., Homebrew, APT, Pacman) to install the CLI tools listed in the **Prerequisites** section. For example, on macOS:

    ```bash
    brew install gcalcli taskbook duf btop superfile
    ```

## Usage

Once all prerequisites and dependencies are installed, run the application from the root directory:

```bash
python main.py
```

## Keybindings

The following keybindings are available for navigation and basic functions:

| Key | Action                          | Description                            |
|:---:|---------------------------------|----------------------------------------|
| `d` | `toggle_dark`                   | Toggle between light and dark modes.   |
| `q` | `quit`                          | Quit the application.                  |
| `h` | `switch_tab('home-tab')`        | Switch to the **Home** tab.            |
| `b` | `switch_tab('taskbook-tab')`    | Switch to the **Taskbook** tab.        |
| `s` | `switch_tab('services-tab')`    | Switch to the **Services** tab.        |
| `l` | `switch_tab('tools-tab')`       | Switch to the **Launch Tools** tab.    |
| `f` | `switch_tab('disk-management')` | Switch to the **Disk Management** tab. |

## Configuration

  * **Tool Executable Names**: The script uses specific command names like `btop4win` and `spf`. If your executables are named differently (e.g., `btop`), you will need to edit the `on_button_pressed` method in `main.py` to match.
  * **Service Monitoring**: The service monitor is hardcoded to check for a process named `copyparty`. To monitor a different service, change this name in the `update_copyparty_status` function in `main.py`.
  * **Calendar Errors**: The calendar widget includes specific error handling for a missing `gcalcli` or a common `pydantic` dependency issue, and will guide you on how to fix it.
