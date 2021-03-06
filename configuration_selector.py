

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

    


#Providing Geometry to the form
root.geometry("500x500")

#Providing title to the form
root.title('Configuration Master')

#this creates 'Label' widget for Registration Form and uses place() method.
label_0 =Label(root,text="Configuration master", width=20,font=("bold",20))
#place method in tkinter is  geometry manager it is used to organize widgets by placing them in specific position
label_0.place(x=90,y=60)

#this creates 'Label' widget for Fullname and uses place() method.
label_1 =Label(root,text="Ip address", width=20,font=("bold",10))
label_1.place(x=80,y=130)

#this will accept the input string text from the user.
entry_1=Entry(root)
entry_1.place(x=240,y=130)

#this creates 'Label' widget for Email and uses place() method.
label_3 =Label(root,text="Buffer Size", width=20,font=("bold",10))
label_3.place(x=68,y=180)

entry_3=Entry(root)
entry_3.place(x=240,y=180)



# 

#this creates 'Label' widget for Gender and uses place() method.
label_4 =Label(root,text="Path to save files", width=20,font=("bold",10))
label_4.place(x=70,y=230)


#the variable 'var' mentioned here holds Integer Value, by deault 0
var=IntVar()



btnFind = ttk.Button(root, text="Browse Folder",command=getFolderPath)
btnFind.place(x=235,y=230)
#this creates 'Radio button' widget and uses place() method


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



#this creates button for submitting the details provides by the user

Button(root, text='Done' , width=20,bg="black",fg='white',command=submit).place(x=180,y=380)


#this will run the mainloop.
root.mainloop()