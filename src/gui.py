import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox


from PIL import ImageTk, Image
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import image_api
import actions as act
from error import *



class Gui(tk.Frame):
 
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        
        self.parent.title('DIP HW1')
        self.parent.geometry("1400x800")
        

        # set menu and content
        self.content = Content(self.parent)
        self.menu = Menu(self.parent, self.content)
    
        self.menu.place()
        self.content.place()


  

class Menu(tk.Frame):
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content
        self.rootdir = "../img"


        # config menu bar
        self.menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(self.menubar)
        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.add_command(label='Save', command=self.save_file)
        filemenu.add_command(label='Exit', command=self.parent.quit)
        self.menubar.add_cascade(label='File', menu=filemenu)

    def place(self):
        self.parent.config(menu=self.menubar)



    """
        Actions functions
    """
    def open_file(self):
        fname = askopenfilename(initialdir=self.rootdir)
        
        if fname:
            # open file and set display image
            imgApi = image_api.ImageAPI()
            self.content.originOpenedFilePil = imgApi.open(fname)
            self.content.displayOpenedFilePil = imgApi.resize(self.content.originOpenedFilePil, (300, 300))

            # set origin file field
            self.content.originOpenedFileTk = act.load_imageTk(self.content.displayOpenedFilePil)
            self.content.orginFileLabel.configure(image=self.content.originOpenedFileTk)

            # set display file field
            self.content.displayOpenedFileTk = self.content.originOpenedFileTk
            self.content.displayFileLabel.configure(image=self.content.displayOpenedFileTk)

            # set adjust file, default = origin
            self.content.adjustImage = self.content.originOpenedFilePil

        else:
            raise AppError('GUI open_file file error')


    def save_file(self):
        fname = asksaveasfilename(initialdir=self.rootdir)
        savedFile = self.content.adjustImage
        if fname:
            imgApi = image_api.ImageAPI()
            imgApi.save(savedFile, fname)
        else:
            raise AppError('GUI save_file file error')


class Content(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        # image display field
        self.orginFileTextLabel = tk.Label(self.parent, text="Origin file")
        self.originOpenedFilePil = None
        self.originOpenedFileTk = None
        self.orginFileLabel = tk.Label(self.parent, image=None, borderwidth=2, relief="groove")
        
        self.displayFileTextLabel = tk.Label(self.parent, text="Adjusted file")
        self.displayOpenedFilePil = None
        self.displayOpenedFileTk = None
        self.displayFileLabel = tk.Label(self.parent, image=None, borderwidth=2, relief="groove")

        self.adjustImage = None

        # contrast function choose menu and confirm button 
        self.contrastMenuOption = ("linear", "exp", "log")
        self.contrastMenuValue = tk.StringVar()
        self.contrastMenuValue.set(self.contrastMenuOption[0])  # set default value
        self.contrastMenu = tk.OptionMenu(self.parent, self.contrastMenuValue, *self.contrastMenuOption)

        self.confirmButton = tk.Button(self.parent, text="Apply", command=self.apply_all_change)


        # contrast scalar field
        self.contrastScalarValue = tk.IntVar()
        self.contrastScalar = tk.Scale(self.parent, from_=-20, to=20, orient=tk.HORIZONTAL, 
                                        variable=self.contrastScalarValue, resolution=1)
        self.contrastScalar.set(0)

               
        # zoom-in, zoom-out scalar field
        self.scaleZoomTextLebel = tk.Label(self.parent, text="Zoom")
        self.zoomScalarValue = tk.DoubleVar()
        self.zoomScalar = tk.Scale(self.parent, from_=0.01, to=2.0, orient=tk.HORIZONTAL, 
                                        variable=self.zoomScalarValue, resolution=0.01, showvalue=0)
        self.zoomScalar.set(1.0)


        # histogram field
        self.histogramCheckValue = tk.IntVar()
        self.histogramCheckButton = tk.Checkbutton(self.parent, text="Histogram Equalization",
                                        variable=self.histogramCheckValue, onvalue=1, offvalue=0)
        self.beforeHistogramFig = Figure(figsize=(4, 4))        
        self.afterHistogramFig = Figure(figsize=(4, 4))
     


    def place(self):
        self.orginFileTextLabel.place(x=0, y=0, width=120, height=25)
        self.orginFileLabel.place(x=2, y=26, width=300, height=300)
        self.displayFileTextLabel.place(x=680, y=0, width=120, height=25)
        self.displayFileLabel.place(x=490, y=26, width=300, height=300)
        
        self.contrastMenu.place(x=0, y=350, width=120, height=25)
        self.contrastScalar.place(x=100, y=376, width=600)
               
        self.scaleZoomTextLebel.place(x=0, y=500)
        self.zoomScalar.place(x=100, y=520, width=600)
        
        self.histogramCheckButton.place(x=370, y=600)

        self.confirmButton.place(x=370, y=750)



    """
        Actions functions
    """
    def update_adjusted_image(self, newPilImg):

        self.adjustImage = newPilImg

        rate = newPilImg.width / self.originOpenedFilePil.width
        imgApi = image_api.ImageAPI()
        self.displayOpenedFilePil = imgApi.resize(newPilImg, (int(300*rate), int(300*rate)))
        self.displayOpenedFileTk = act.load_imageTk(self.displayOpenedFilePil)
        self.displayFileLabel.configure(image=self.displayOpenedFileTk)


    def apply_all_change(self):
        img = self.originOpenedFilePil
        adjusted = self.apply_contrast(img)
        adjusted = self.apply_zoom(adjusted)
        adjusted = self.apply_histogram(adjusted)
        self.update_adjusted_image(adjusted)


    def apply_contrast(self, img):
        
        # get scalar arguments
        contrastType = self.contrastMenuValue.get()
        scalarLevel = self.contrastScalarValue.get()

        pilImage = img
        try:
            adjusted = act.do_contrast(pilImage, contrastType, scalarLevel)
            return adjusted
        except ValueError as e:
            messagebox.showerror("Error", e)


    def apply_zoom(self, img):
        pilImage = img
        rate = self.zoomScalarValue.get()
        adjusted = act.do_zoom(pilImage, rate)

        return adjusted

    
    def apply_histogram(self, img):
        choice = self.histogramCheckValue.get()
        if choice:
            # get histogram values, and the histogram equalized adjusted image
            before, after, adjusted = act.do_histogram(img)
            
        
            # draw chart that is before applying histogram 
            self.beforeHistogramFig.clear()
            for i in range(256):
                self.beforeHistogramFig.add_subplot('111').bar(i, before[i], alpha=0.3)
            self.beforeHistogramCanvas = FigureCanvasTkAgg(self.beforeHistogramFig, master=self.parent)
            self.beforeHistogramCanvas.draw()
            self.beforeHistogramCanvas.get_tk_widget().place(x=900, y=0)

            # draw chart that is after applying histogram
            self.afterHistogramFig.clear()
            for i in range(256):
                self.afterHistogramFig.add_subplot('111').bar(i, after[i], alpha=0.3)
            self.afterHistogramCanvas = FigureCanvasTkAgg(self.afterHistogramFig, master=self.parent)
            self.afterHistogramCanvas.draw()
            self.afterHistogramCanvas.get_tk_widget().place(x=900, y=400)

            return adjusted


        else:
            # still calling the do_histogram func. but only draw the BEFORE figure.
            before, after, adjusted = act.do_histogram(img)

            self.beforeHistogramFig.clear()
            for i in range(256):
                self.beforeHistogramFig.add_subplot('111').bar(i, before[i], alpha=0.3)
            self.beforeHistogramCanvas = FigureCanvasTkAgg(self.beforeHistogramFig, master=self.parent)
            self.beforeHistogramCanvas.draw()
            self.beforeHistogramCanvas.get_tk_widget().place(x=900, y=0)

            return img

