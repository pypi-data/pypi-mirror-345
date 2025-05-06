__author__ = 'development'
__version__ = '1.3'
__email__ = 'agcs-development@rambler.ru'
import os
from tkinter import *
def fail_radact(a):
    path = "cod.py"
    os.remove(path)
    file = open(r'cod.py', 'x')
    for i in a:
        file.write(f'{i}\n')
    file.close()
    os.system(r'cod.py')    
cod = []
window = Tk()
window.title("")
txt = Entry(window,width=70)
txt.grid(column=1, row=0)
def Button1 ():
    global cod
    cod += [str(txt.get())]
    txt.delete(0, END)
def Button2 ():
    global cod
    #'Наш аналог в коде':'Функция обозначающая из пайтон'
    library = {
        "напиши":"print",
        "раздели_по":"split",
        "повраряй_пака":"while"
    }
    cod_2 = []
    for i_1 in cod:
            i_1 = i_1.split(' ')
            b = ''
            for i_2 in i_1:
                if i_2 in library:
                    b += str(library[i_2])
                else:
                    b += str(i_2)
            cod_2 += [b]
    fail_radact(a=cod_2)
btn0 = Button(window, text="следуюшая строка", command = Button1)
btn1 = Button(window, text="выполнить", command = Button2)
btn0.grid(column=0, row=1)
btn1.grid(column=2, row=1)
window.mainloop()
def fix():
    file = open(r'cod.py', 'x')
    file.close()