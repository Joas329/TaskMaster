'''
    the code must have a while loop that checks for an input:
    This input can have only three options
    --> 0: close program
    --> 1: save tasks to card
    --> 2: read card
    
    upadates (26/07/2022):
    successfull comm between the python and arduino for sending the tasks in a string format initiated by a number that dictates
    one of the three states of the code (mentioned before).
    
'''


import serial
import time

array = ["testing, testing", "is this working?"]

arduino=serial.Serial('COM3', 9600)



def saveTask(state):
    
    tasks = array
    data = state
    key = ""
    print(tasks)
    for i in range(len(tasks)):
        data+= tasks[i]
        data+='#'
    data += '^'
    print("data: " + data)
    print("data sent, waiting for writting. Keep card close to reader")

    return data

while 1:
    
    datafromUser=input("Enter 1 to save to card, 2 to read card, 0 to close program \n").strip()

    if datafromUser == '1':
        data = saveTask(datafromUser)
        arduino.write(data.encode('utf-8'))
        key = ""
        datafromUser =""
        while key != "done":
            key = arduino.readline().decode('utf-8').strip()
            print(key)
        print("data written")
        
        
        
    elif datafromUser == '2':
        data = datafromUser + "rest^"  #adding filler, it wont matter on the long run
        arduino.write(data.encode('utf-8'))
        key = "holder"
        holder =""
        datafromUser = ""
        cardData = ""
        while key[-1] != '^':
            key = arduino.readline().decode('utf-8').strip()
            holder = key
            print(key[-1])
            print(key)
        print("read")
        print(holder)
        cardData = holder[holder.find('^')]
        #holder has the read data
        print(cardData)
        
    elif datafromUser == '0':
        print("program finished")
        break
    else:
        print("wrong input")