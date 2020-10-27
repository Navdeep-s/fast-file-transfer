# from tkinter import *
# from tkinter import ttk
# from tkinter import filedialog
# gui = Tk()
# gui.geometry("400x400")
# gui.title("FC")

# def getFolderPath():
#     folder_selected = filedialog.askdirectory()
#     folderPath.set(folder_selected)

# def doStuff():
#     folder = folderPath.get()
#     print("Doing stuff with folder", folder)

# folderPath = StringVar()
# a = Label(gui ,text="Select folder where you want to save your files")
# a.grid(row=0,column = 0)
# # E = Entry(gui,textvariable=folderPath)
# # E.grid(row=0,column=1)
# btnFind = ttk.Button(gui, text="Browse Folder",command=getFolderPath)
# btnFind.grid(row=0,column=2)

# c = ttk.Button(gui ,text="find", command=doStuff)
# c.grid(row=4,column=0)
# gui.mainloop()


#how to create simple GUI registration form.
#importing tkinter module for GUI application

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from tkinter import messagebox

import json

# An error box


#Creating object 'root' of Tk()
root = Tk()


saving_path = ""
ip = ""
buffer_size = ""



def getFolderPath():
	global saving_path
	folder_selected = filedialog.askdirectory()
	label_4.config(text = folder_selected)
	saving_path = folder_selected
	# label_4.labelText = folderPath
    # label_4.depositLabel.config(text=folder_selected)

    


def do_changes():

	dic = {
    "saving_path": saving_path,
    "hosting_ip": ip,
    "buffer_size": buffer_size
		}

	with open('configuration.json', 'w') as outfile:
		json.dump(dic, outfile)


def submit():
	global ip, buffer_size
	try:
		ip = entry_1.get()
		buffer_size = int(entry_3.get())
		do_changes()
		root.quit()
		print(saving_path,ip,buffer_size)
	except Exception:
		messagebox.showerror("Error", "Please fill the boxes correctly")



root.geometry("500x500")
root.title('Configuration Master')
label_0 =Label(root,text="Configuration master", width=20,font=("bold",20))
label_0.place(x=90,y=60)
label_1 =Label(root,text="Ip address", width=20,font=("bold",10))
label_1.place(x=80,y=130)
entry_1=Entry(root)
entry_1.place(x=240,y=130)
label_3 =Label(root,text="Buffer Size", width=20,font=("bold",10))
label_3.place(x=68,y=180)
entry_3=Entry(root)
entry_3.place(x=240,y=180)
label_4 =Label(root,text="Path to save files", width=20,font=("bold",10))
label_4.place(x=70,y=230)
var=IntVar()
btnFind = ttk.Button(root, text="Browse Folder",command=getFolderPath)
btnFind.place(x=235,y=230)
Button(root, text='Done' , width=20,bg="black",fg='white',command=submit).place(x=180,y=380)
root.mainloop()