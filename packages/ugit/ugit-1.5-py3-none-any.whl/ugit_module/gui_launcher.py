def main():
    try:
        from ugit_module import ugit_gui  # Updated import path
        ugit_gui.root.mainloop()          # 👈 This line starts the GUI
    except ImportError as e:
        print("Error: Could not import ugit_module.ugit_gui.")
        print("Make sure ugit_gui.py is inside the ugit_module package.")
        print("Details:", e)
