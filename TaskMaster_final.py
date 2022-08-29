
#Joaquin Philco 2022
from ast import Str
from ctypes import sizeof
from distutils.command import check
import tkinter as tk
import pickle
import tkinter.messagebox
from turtle import right
import numpy as np
from tkinter import *
import serial
import serial.tools.list_ports
import functools
import time

ports = serial.tools.list_ports.comports()
superCondition = False
cardSense = False
serialArduino = serial.Serial("COM3", 9600,timeout=1, write_timeout = 2)
serialArduino.close()
time.sleep(2)

status =False

root  = tk.Tk()
root.title("Tasks To do")
#geamotry varaibles
globalW= 400
globalH = 400
root.geometry("{x}x{y}".format(x=globalW,y=globalH))



def initComPort(index):
    currentPort = str(ports[index])
    comPortVar = str(currentPort.split(' ')[0])
    serialArduino.port = comPortVar
'''
for onePort in ports:
    comButton = Button(root, text=onePort, command = functools.partial(initComPort, index = ports.index(onePort)))
    comButton.pack()
'''

def serialStatus():
    global status
    global globalH
    global cardSense
    globalH = 500
    root.geometry("{x}x{y}".format(x=400,y=globalH))
    cardSense = True
    if(status == False):
        serialArduino.open()
        status = True
    else:
        serialArduino.close()
        status = False
        
    button_save_task = Button(root, text="Save Tasks to Card", width=48, command=saveTask)
    button_save_task.pack()

    button_read_card =  Button(root, text= "Read Card for Tasks",width=48, command=readCard)
    button_read_card.pack()
    
    fakeSerialComm = Label(root, text = "Keep card close to reader once you have pressed a button" )
    fakeSerialComm.pack()


#serialMonitor = Frame(root)
#serialMonitor.pack(side =RIGHT)

#dataCanvas = Canvas(serialMonitor, width=500, height=800, bg='white', scrollregion=(0,0,5000,5000))
#dataCanvas.pack( side=RIGHT)


#vsb = Scrollbar(serialMonitor, orient='vertical', command = dataCanvas.yview)
#vsb.pack(side =LEFT, fill = Y)



#dataCanvas.bind('<Configure>', lambda e: dataCanvas.configure(scrollregion=dataCanvas.bbox("all")))
#dataFrame = Frame(dataCanvas)
#dataCanvas.create_window((100,100), window = dataFrame, anchor = 'nw')
#dataCanvas.config(yscrollcommand=vsb.set)

def addTask1():
    task = entry_task.get()
    if task != "":
        listbox_task.insert(END, task)
        entry_task.delete(0, END)
    else:
        tkinter.messagebox.showwarning(title= "WARNING", message = "Entering blank task" )
#overloaded funciton    
def addTask(event):
    task = entry_task.get()
    holder = event
    if task != "":
        listbox_task.insert(END, task)
        entry_task.delete(0, END)
    else:
        tkinter.messagebox.showwarning(title= "WARNING", message = "Entering blank task" )
    
   
def deleteTask():
    try:
        task_index = listbox_task.curselection()[0]
        listbox_task.delete(task_index)
    except:
        tkinter.messagebox.showwarning(title="WARNING!", message="Select a task to delete")
        
 
def loadTask():
    try:
        tasks = pickle.load(open("Tasks.dat", "rb"))
        listbox_task.delete(0,END)
        for task in tasks:
            listbox_task.insert(END, task)
    except:
         tkinter.messagebox.showwarning(title="WARNING!", message="Cant Find previous Loads")
        

    
def saveTask():
    
    time.sleep(0.5)
    tasks = listbox_task.get(0,listbox_task.size())
    data = "1"
    key = ""
    print(tasks)
    for i in range(len(tasks)):
        data+= tasks[i]
        data+='#'
    data += '^'
    print("data: " + data)
    print("data sent, waiting for writting. Keep card close to reader")
    serialArduino.write(data.encode('utf-8'))
       
        
    while key != "done":
        key = serialArduino.readline().decode('utf-8').strip()
        print(key)
    print("data written")

    pickle.dump(tasks, open("Tasks.dat", "wb"))
    
    done = Label(root, text="Tasks saved to Card")
    done.pack()
    

def readCard():
    global key
    time.sleep(1)
    data = "2 rest^"  #adding filler, it wont matter on the long run
    serialArduino.write(data.encode('utf-8'))
    key = ""
    holder =""
    cardData = ""
    print(key)
    print(len(key))
   
    while True:
        key = serialArduino.readline().decode('utf-8').strip()
        if key != "":
            print(key)
            if key[0] == '^':
                if key[len(key)-1] == '^':
                    holder = key
                    break
        time.sleep(1)
       
    print("read")
    print(holder)
    
    #holder has the read data
   
    
    task_to_add = ""
    
    holder = holder[1:]
    print(holder)
    for char in holder:
        task_to_add += char
        if char == '#':
            task_to_add = task_to_add[0:len(task_to_add)-1]
            listbox_task.insert(END, task_to_add)
            entry_task.delete(0, END)
            task_to_add =""
        elif char == '^':
            break
        
    done = Label(root, text = "Card Read")
    done.pack()
    
        
        
    
        

    
def resize():
    global globalW
    
        
    GUIW = int(globalW/10) + 20
    #resizing buttons
    button_add_task.configure(width=GUIW)
    button_delete_task.configure(width=GUIW)
    button_load_task.configure(width=GUIW)
    #button_save_task.configure(width=GUIW)
    increaseB.configure(width=int((GUIW-10)/2))
    decreaseB.configure(width=int((GUIW-10)/2))
    listbox_task.configure(width=GUIW)
    entry_task.configure(width=GUIW)
    root.geometry("{x}x{y}".format(x=globalW,y=globalH))
    
    
def increase():
    global globalW, globalH
    globalW=globalW + 100
    globalH=globalH + 10
    if(globalW >= 400 and globalH >= 400 and globalW <= 800 and globalH <= 800 ): 
        resize()
    else:
        globalW = 800
        tkinter.messagebox.showwarning(title="WARNING!", message="Minimum Size") 
    
    

def decrease():
    global globalW, globalH
    globalW=int(globalW-100)
    globalH=int(globalH-10)
    if(globalW >= 400 and globalH >= 400 and globalW <= 800 and globalH <= 800 ):    
        resize()
    else:
        globalW = 400
        globalH = 400
        tkinter.messagebox.showwarning(title="WARNING!", message="Maximum Size")  
index =0
x, y, distance = 200,20, 20
'''
def checkSerialPort():
    if serialArduino.isOpen() and serialArduino.in_waiting:
        recentPacket = serialArduino.readline()
        recentPacketString = recentPacket.decode('utf-8').rstrip('\n')
        #info = Label(dataFrame, text = recentPacketString)
        global index, x, y, distance
        
        dataCanvas.create_text(x,y + index * distance,text= recentPacketString)
        index = index +1
        dataCanvas.update
        #info.pack()
'''
#creating GUI

frame = Frame(root, width = globalW)
frame.pack()

GUIW = int(globalW/10) + 20
listbox_task = tk.Listbox(frame, height=15, width=GUIW )
listbox_task.pack(side=tkinter.LEFT)

scrollbar_tasks = tk.Scrollbar(frame)
scrollbar_tasks.pack(side=tkinter.RIGHT, fill=tkinter.Y)

listbox_task.config(yscrollcommand = scrollbar_tasks.set)
scrollbar_tasks.config(command=listbox_task.yview)

entry_task = Entry(root, width=50)
root.bind("<Return>", addTask)
entry_task.pack()

button_add_task = Button(root, text="add task", width=48, command=addTask1)

button_add_task.pack()

button_delete_task = Button(root, text="Delete task", width=48, command=deleteTask)
button_delete_task.pack()

button_load_task = Button(root, text="Load task", width=48, command=loadTask)
button_load_task.pack()

openSerial = Button(root, text="Open RFID options", width = 48, command = serialStatus)
openSerial.pack()

change = tkinter.Frame(root, width = 30)
change.pack()



t1 = Label(change, text ="Resize Page", width = 10)
t1.pack(side = LEFT)

size_buttons = Frame(change)
size_buttons.pack(side = RIGHT)

increaseB = Button(size_buttons,text = "+", width = 20 , command = increase)
increaseB.pack(side =LEFT)


decreaseB = Button(size_buttons,text = "-", width = 20, command = decrease)
decreaseB.pack(side=tkinter.RIGHT)

while True:
    root.update()
    
    
    
root.mainloop()
