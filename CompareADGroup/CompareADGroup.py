from tkinter import *
import tkinter.filedialog

def pickFileA():
    filename = tkinter.filedialog.askopenfilename(filetypes = [('TXT','txt')])

    if filename !='':
        entry1.delete(0,END)
        entry1.insert(10,filename)

def pickFileB():
    filename = tkinter.filedialog.askopenfilename(filetypes = [('TXT','txt')])

    if filename !='':
        entry2.delete(0,END)
        entry2.insert(10,filename)

def compareFiles():
    netUserSource = NetUser()
    readFile(entry1,netUserSource)
    netUserTarget = NetUser()
    readFile(entry2,netUserTarget)
    textbox1 = Text(myWindow)
    textbox1.insert(END,netUserSource.ADGroupList - netUserTarget.ADGroupList)
    textbox1.grid(row = 3,columnspan = 6)
    

def readFile(entryObj,netUser):
    fileSource = open(entryObj.get())
    GroupListStart = False
    while True:
        line = fileSource.readline()
        if(not line):
            break
        if line[0:2] == "全名":
            netUser.FullName = line[3:].strip()
        if line[0:3] == "用户名":
            netUser.UserId = line[4:].strip()
        if line[0:5] == "全局组成员":
            GroupListStart = True
        if line[0:6] == "命令成功完成":
            GroupListStart=False
        if GroupListStart:
            netUser.addGroupList(line)
    fileSource.close()
class NetUser:
    FullName = ''
    UserId = ''
    ADGroupList = set()

    def __init__(self):
        self.ADGroupList = set()

    def addGroupList(self,GroupList):
        ADGroupStart = False
        ADGroupTemp = ""
        for char in GroupList:
            if char == '*':
                ADGroupStart = not ADGroupStart
                if ADGroupTemp != "":
                    self.ADGroupList.add(ADGroupTemp.strip())
            if ADGroupStart:
                ADGroupTemp = ADGroupTemp + char
        if ADGroupTemp != "":
            self.ADGroupList.add(ADGroupTemp.strip())

#初始化TK()
myWindow = Tk()
#设置标题
myWindow.title('比较AD Group差异')
#设置窗口大小
#myWindow.geometry('380x300')
width = 380
height = 300
#获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
screenwidth = myWindow.winfo_screenwidth()
screenheight = myWindow.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width,height,(screenwidth -width)/2,(screenheight - height)/2)
myWindow.geometry(alignstr)

#放置控件
Label(myWindow,text = "原始文件:").grid(row = 0)
entry1 = Entry(myWindow)
entry1.grid(row = 0, column = 1)
button1 = Button(myWindow,text = "...",command = pickFileA)
button1.grid(row = 0, column = 2)
Label(myWindow,text = "目标文件:").grid(row = 1)
entry2 = Entry(myWindow)
entry2.grid(row = 1,column = 1)
button2 = Button(myWindow,text = "...", command = pickFileB)
button2.grid(row = 1,column = 2)

button3 = Button(myWindow, text = "开始比较", command = compareFiles)
button3.grid(row = 2,column = 2)
#进入消息循环
myWindow.mainloop()