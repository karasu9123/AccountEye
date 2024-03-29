import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import json


fromfile = True
file = ''   # Picture name in ./Test/ folder.



def CountCameras():
    count = 0
    while True:
        cap = cv2.VideoCapture(count)
        if cap.isOpened():
            count += 1
            cap.release()
        else:
            break
    return count


class Settings:
    def __init__(self):
        self.camCount = 0
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root)
        self.camLabel = tk.Label(self.root)
        self.camLBox = tk.Listbox(self.root)
        self.periodLabel = tk.Label(self.root)
        self.periodNum = tk.Spinbox(self.root)
        self.digitLabel = tk.Label(self.root)
        self.digitNum = tk.Spinbox(self.root)
        self.buttonSave = tk.Button(self.root)
        self.CreateWidgets()
        self.curIndex = 0
        self.rectangles = ()
        self.isDrawing = False
        self.startPoint = None
        self.endPoint = None
        if not fromfile:
            self.camCount = CountCameras()
            if self.camCount == 0:
                messagebox.showwarning("Camera not found!", "Please, connect camera to device and try again.")
                self.root.quit()
            else:
                self.cap = cv2.VideoCapture(self.curIndex)
                self.ShowVideo()
        else:
            self.ShowVideo()


    def CreateWidgets(self):
        # root.
        self.root.title("Settings")
        self.root.geometry('550x550')

        # camLabel.
        self.camLabel["text"] = "Current camera:"

        # camLBox.
        self.camLBox["selectmode"] = tk.SINGLE
        self.camLBox["height"] = 1
        for index in range(self.camCount):
            self.camLBox.insert(index, "camera №" + str(index))
        self.camLBox.selection_set(0)
        self.camLBox.bind('<<ListboxSelect>>', self.SelectedCamChanged)

        # periodLabel.
        self.periodLabel["text"] = "Period (days):"

        # periodNum.
        self.periodNum["values"] = list(range(1, 32))

        # digitLabel
        self.digitLabel["text"] = "Number of digits:"

        # digitNum.
        self.digitNum["values"] = list(range(1, 16))

        # buttonSave.
        self.buttonSave["text"] = "Save"
        self.buttonSave["command"] = self.ButtonSaveClicked

        # canvas.
        self.canvas["bg"] = "black"
        self.canvas.bind("<Button-1>", self.ButtonClick)
        self.canvas.bind("<ButtonRelease-1>", self.ButtonRelease)
        self.canvas.bind("<B1-Motion>", self.ButtonMove)

        # Packing.
        self.buttonSave.pack(anchor=tk.NW)
        self.periodLabel.pack(anchor=tk.N)
        self.periodNum.pack(anchor=tk.N)
        self.digitLabel.pack(anchor=tk.N)
        self.digitNum.pack(anchor=tk.N)
        self.camLabel.pack(anchor=tk.N)
        self.camLBox.pack(anchor=tk.N)
        self.canvas.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)


    def ShowVideo(self):
        data = None
        if fromfile:
            data = cv2.imread('Test/' + file + '.jpg', 1)
        while True:
            if not fromfile:
                if not self.cap.isOpened():
                    print("camera isn't open")
                    cv2.waitKey(200)
                    continue
                flag, data = self.cap.read()
                data = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
                if not flag:
                    print("can't read frame")
                    cv2.waitKey(100)
                    continue
            try:
                im = Image.fromarray(data)
                im = im.resize((int(self.canvas.winfo_width()), int(self.canvas.winfo_height())), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image=im)
                self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                if self.startPoint is not None:
                    self.CreateRectangle()
                self.root.update()
                cv2.waitKey(25)
            except:
                if not fromfile:
                    self.cap.release()
                raise


    def SelectedCamChanged(self, evt):
        if self.curIndex == self.camLBox.curselection()[0]:
            return
        oldCap = self.cap
        self.curIndex = self.camLBox.curselection()[0]
        self.cap = cv2.VideoCapture(self.curIndex)
        oldCap.release()


    def ButtonSaveClicked(self):
        if self.startPoint is None:
            messagebox.showwarning("Region isn't selected", "Please, select the region.")
            return
        answer = messagebox.askquestion("Are you sure?", "Do you want to save settings?")
        if answer == "yes":
            d = filedialog.askdirectory()
            (x0, y0, x1, y1) = self.ComparePoint()
            x0 /= self.canvas.winfo_width()
            x1 /= self.canvas.winfo_width()
            y0 /= self.canvas.winfo_height()
            y1 /= self.canvas.winfo_height()
            data = {
                "period": int(self.periodNum.get()),
                "digitNum": int(self.digitNum.get()),
                "region": {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
            }
            path = str(d) + '/' + file + ".json" if fromfile else str(d) + "/settings.json"
            with open(path, "w") as outfile:
                json.dump(data, outfile)


    def ButtonClick(self, evt):
        self.isDrawing = True
        self.endPoint = {"x": evt.x, "y": evt.y}
        self.startPoint = {"x": evt.x, "y": evt.y}


    def ButtonMove(self, evt):
        if self.isDrawing:
            self.endPoint = {"x": evt.x, "y": evt.y}


    def ButtonRelease(self, evt):
        self.endPoint = {"x": evt.x, "y": evt.y}
        self.isDrawing = False


    def CreateRectangle(self):
        (x0, y0, x1, y1) = self.ComparePoint()
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="red")

        rectCount = int(self.digitNum.get())
        rectWidth = (x1 - x0) / rectCount
        x = x0
        for i in range(1, rectCount):
            x += rectWidth
            self.canvas.create_line(x, y0, x, y1, fill="red")


    def ComparePoint(self):
        if self.startPoint["x"] < self.endPoint["x"]:
            x0 = self.startPoint["x"]
            x1 = self.endPoint["x"]
        else:
            x0 = self.endPoint["x"]
            x1 = self.startPoint["x"]
        if self.startPoint["y"] < self.endPoint["y"]:
            y0 = self.startPoint["y"]
            y1 = self.endPoint["y"]
        else:
            y0 = self.endPoint["y"]
            y1 = self.startPoint["y"]
        return x0, y0, x1, y1


if __name__ == "__main__":
    Settings()
