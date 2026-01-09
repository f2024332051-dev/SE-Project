"""
ARENA - Online Gaming Tournament Management System
Main entry point for the application

A complete implementation of the Tournament Management System with:
- User authentication and role-based access control
- League and tournament creation and management
- Match scheduling and result recording
- Player registration and statistics tracking
- Spectator dashboard with live match viewing
- Advertiser management system
"""

import tkinter as tk
from gui import ArenaGUI


def main():
    """Main entry point - Create the root window and start the application"""
    root = tk.Tk()
    app = ArenaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
