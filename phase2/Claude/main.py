"""
main.py — Application entry point.

Run:
    python main.py
"""
from src.ui.app import Application


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
