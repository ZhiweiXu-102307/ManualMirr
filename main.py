from utils.process import ImageMirrorApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = ImageMirrorApp(root)
    root.mainloop()    

if __name__ == "__main__":
    main()