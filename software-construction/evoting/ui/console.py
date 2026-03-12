from __future__ import annotations

import os
import sys

from evoting.ui import themes


class Console:
    def __init__(self) -> None:
        if sys.platform == "win32":
            os.system("")

    def colored(self, text: str, color: str) -> str:
        return f"{color}{text}{themes.RESET}"

    def header(self, title: str, theme_color: str) -> None:
        width = 58
        top = f"  {theme_color}{'═' * width}{themes.RESET}"
        mid = (
            f"  {theme_color}{themes.BOLD} {title.center(width - 2)} "
            f"{themes.RESET}{theme_color} {themes.RESET}"
        )
        bot = f"  {theme_color}{'═' * width}{themes.RESET}"
        print(top)
        print(mid)
        print(bot)

    def subheader(self, title: str, theme_color: str) -> None:
        print(f"\n  {theme_color}{themes.BOLD}▸ {title}{themes.RESET}")

    def table_header(self, format_str: str, theme_color: str) -> None:
        print(f"  {theme_color}{themes.BOLD}{format_str}{themes.RESET}")

    def table_divider(self, width: int, theme_color: str) -> None:
        print(f"  {theme_color}{'─' * width}{themes.RESET}")

    def error(self, message: str) -> None:
        print(f"  {themes.RED}{themes.BOLD} {message}{themes.RESET}")

    def success(self, message: str) -> None:
        print(f"  {themes.GREEN}{themes.BOLD} {message}{themes.RESET}")

    def warning(self, message: str) -> None:
        print(f"  {themes.YELLOW}{themes.BOLD} {message}{themes.RESET}")

    def info(self, message: str) -> None:
        print(f"  {themes.GRAY}{message}{themes.RESET}")

    def menu_item(self, number: int, text: str, color: str) -> None:
        print(f"  {color}{themes.BOLD}{number:>3}.{themes.RESET}  {text}")

    def status_badge(self, text: str, is_good: bool) -> str:
        color = themes.GREEN if is_good else themes.RED
        return f"{color}{text}{themes.RESET}"

    def prompt(self, text: str) -> str:
        return input(f"  {themes.BRIGHT_WHITE}{text}{themes.RESET}").strip()

    def masked_input(self, prompt_text: str = "Password: ") -> str:
        print(f"  {themes.BRIGHT_WHITE}{prompt_text}{themes.RESET}", end="", flush=True)
        password = ""
        if sys.platform == "win32":
            import msvcrt

            while True:
                char = msvcrt.getwch()
                if char in {"\r", "\n"}:
                    print()
                    break
                if char in {"\x08", "\b"}:
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue
                if char == "\x03":
                    raise KeyboardInterrupt
                password += char
                sys.stdout.write(f"{themes.YELLOW}*{themes.RESET}")
                sys.stdout.flush()
            return password

        import termios
        import tty

        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            while True:
                char = sys.stdin.read(1)
                if char in {"\r", "\n"}:
                    print()
                    break
                if char in {"\x7f", "\x08"}:
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue
                if char == "\x03":
                    raise KeyboardInterrupt
                password += char
                sys.stdout.write(f"{themes.YELLOW}*{themes.RESET}")
                sys.stdout.flush()
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
        return password

    def clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def pause(self) -> None:
        input(f"\n  {themes.DIM}Press Enter to continue...{themes.RESET}")
