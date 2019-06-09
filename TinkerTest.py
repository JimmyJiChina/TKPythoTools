import numpy as np 
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.filedialog import askdirectory
import sys
sys.path.append('C:/Users/Administrator/.ipython')
print(sys.path)
import psd_jimmy as psd
top = tk.Tk()
top.title('BF Calibration Data Analyzer')
top.geometry('400x300')  

def DataAnalyze():
    pathname = getdir()
    print(pathname)
    rx_data = getdata(pathname)
    DataPlot(rx_data)
    PSD(rx_data)
    plt.show()

def getdir():
    pathname = askdirectory(initialdir='f:/Data')
    return(pathname)

def DataPlot(rx_data):
    fig, ax = plt.subplots(8,8)
    pic_ind = 0
    for row in ax:
        for col in row:
            col.plot(rx_data[pic_ind].real[:128])
            col.plot(rx_data[pic_ind].imag[:128])
    #plt.show()
    pic_ind = pic_ind + 1

def PSD(rx_data):
    ind = 0
    for pic in range(4):
        fig,ax = plt.subplots(4,4)
        for row in ax:
            for col in row:
                psd.psd_jimmy(rx_data[ind],ax4=col)
                ind = ind + 1
    #plt.show()



def getdata(pathname):
    rx_data = list()
    for pipe in range(64) :
        filename = pathname + '/Ant{}_cap_samp.bin'.format(pipe)
        fid = open(filename,'rb')
        dd = fid.read()
        data = np.frombuffer(dd,dtype='>i2')
        sig = data[1::2] + 1j*data[::2]
        rx_data.append(sig)
        fid.close()
    return rx_data


Button1 = tk.Button(top, text='Choose the Directory', font=('Arial', 12), width=30, height=1,command = DataAnalyze )
Button1.pack()

Button2 = tk.Button(top, text='Reserved', font=('Arial', 12), width=30, height=1,)
Button2.pack()

top.mainloop()

