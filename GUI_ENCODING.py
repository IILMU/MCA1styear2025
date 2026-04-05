# the practice of concealing messages or information within other non-secret text or data.

import tkinter as tk
import tkinter.font as tkFont
from tkinter import * #for makinG it GUI environment
import stepic #for stagnoGraphy
from PIL import Image #for image import aka PILLOW 


def steg():
    # txt=input("THE Hidden txt that you want to write inn:-")#jo bhi hidden msg hain isme aayega
    # file=input("The Image that you want to use:-") # JO IMAGE MEI hume use krna h
    txt=GLineEdit_851.get() #ENTER THE HIDDEN TXT HERE
    file=GLineEdit_153.get() #INPUT THE IMAGE TO be ENCODED
    img=Image.open(file) #IMAGE OPENed throught PIL
    img_stagno= stepic.encode(img,txt.encode()) #we Encoded the text into The IMAGE
    img_stagno.save("STAGNO.png") #here we saved the IMAGE as STAGNO.png

class App:
    def __init__(self, root):
     
        #setting title
        root.title("Steganography Tool")
        root.configure(background="Black")
        #setting window size
        width=600
        height=500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        GLabel_866=tk.Label(root)
        ft = tkFont.Font(family='Times',size=16)
        GLabel_866["font"] = ft
        GLabel_866["fg"] = "#333333"
        GLabel_866["justify"] = "center"
        GLabel_866["text"] = "STEGNOGRAPHY TOOL"
        GLabel_866["background"] = "#fab055"
        GLabel_866.place(x=130,y=30,width=317,height=30)

        GMessage_456=tk.Message(root)
        GMessage_456["bg"] = "#fad400"
        ft = tkFont.Font(family='Times',size=19)
        GMessage_456["font"] = ft
        GMessage_456["fg"] = "#333333"
        GMessage_456["justify"] = "center"
        GMessage_456["text"] = "ENTER THE HIDDEN TEXT HERE"
        GMessage_456.place(x=0,y=130,width=282,height=90)

        global GLineEdit_851 #entry for the text inpuT!!
        GLineEdit_851=tk.Entry(root) #ENTRY for txt like INPUT BOX
        GLineEdit_851["bg"] = "#00ced1"
        GLineEdit_851["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=14)
        GLineEdit_851["font"] = ft
        GLineEdit_851["fg"] = "#040404"
        GLineEdit_851["justify"] = "center"
        GLineEdit_851["text"] = ""
        GLineEdit_851.place(x=310,y=130,width=281,height=90)

        GMessage_140=tk.Message(root)
        GMessage_140["bg"] = "#fad400"
        ft = tkFont.Font(family='Times',size=14)
        GMessage_140["font"] = ft
        GMessage_140["fg"] = "#333333"
        GMessage_140["justify"] = "center"
        GMessage_140["text"] = "ENTER IMAGE LOCATION/ NAME with extension"
        GMessage_140.place(x=0,y=240,width=282,height=90)

        global GLineEdit_153 # IMAGE's Input using this COMMAND
        GLineEdit_153=tk.Entry(root) #ENTRY FOR THE IMG location!
        GLineEdit_153["bg"] = "#00ced1"
        GLineEdit_153["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=13)
        GLineEdit_153["font"] = ft
        GLineEdit_153["fg"] = "#333333"
        GLineEdit_153["justify"] = "center"
        GLineEdit_153["text"] = ""
        GLineEdit_153.place(x=310,y=240,width=286,height=90)

        GButton_129=tk.Button(root)
        GButton_129["activebackground"] = "#ffffff"
        GButton_129["bg"] = "#5bff89"
        ft = tkFont.Font(family='Times',size=10)
        GButton_129["font"] = ft
        GButton_129["fg"] = "#000000"
        GButton_129["justify"] = "center"
        GButton_129["text"] = "ENCODE"
        GButton_129.place(x=210,y=390,width=142,height=48)
        GButton_129["command"] = self.GButton_129_command

    def GButton_129_command(self):
        steg()
        GLabel_307=tk.Label(root)
        GLabel_307["bg"] = "#80dbff"
        ft = tkFont.Font(family='Times',size=10)
        GLabel_307["font"] = ft
        GLabel_307["fg"] = "#333333"
        GLabel_307["justify"] = "center"
        GLabel_307["text"] = "ENCODED DONE" # THIS WILL POP UP THE CODE EXECUTION HERE!!!!
        GLabel_307.place(x=100,y=440,width=403,height=50)

    

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
