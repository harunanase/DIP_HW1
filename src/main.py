import tkinter as tk
import gui
from error import *

def main():
    
    root = tk.Tk()
    gui.Gui(root).pack(side="top", fill="both", expand=True)       
    try:
        root.mainloop()
    except AppError as e:
        print(str(e))



if __name__ == "__main__":
    main()
