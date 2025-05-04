import tkinter as tk
from PIL import ImageTk

class PixelPreview:
    def __init__(self, pixel_generator):
        self.root = tk.Tk()
        self.pixel_generator = pixel_generator
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()


    def update_preview(self):
        img = Image.fromarray(self.pixel_generator.canvas)
        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=photo, anchor="nw")
        self.root.after(100, self.update_preview)

    def start(self):
        self.update_preview()
        self.root.mainloop()    
        
    def update_preview(self):
        img = Image.fromarray(self.pixel_generator.get_canvas_with_grid())  # Use canvas with grid
        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=photo, anchor="nw")
        self.root.after(100, self.update_preview)
        
        
        
        
        
