def main():
    import os
    import sys

    # Allow importing ugit_gui from the project root
    sys.path.insert(0, os.getcwd())

    try:
        import ugit_gui  # This will run the GUI directly
    except ImportError as e:
        print("Error: Could not import ugit_gui.py.")
        print("Make sure ugit_gui.py exists in the project root.")
        print("Details:", e)
