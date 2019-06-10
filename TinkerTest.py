import numpy as np 
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.filedialog import askdirectory
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
sys.path.append('C:/Users/jimji/.ipython')
print(sys.path)
import psd_jimmy as psd
top = tk.Tk()
top.title('BF Calibration Data Analyzer')
top.geometry('400x300')  
plt.rcParams['figure.figsize'] = 15,15

def CreateNewWindow(title = 'New windows',size = '400x300'):
    win = tk.Tk()
    win.title(title)
    win.geometry(size) 
    return win

def DataAnalyze():
    plt.close('all')
    pathname = getdir()
    print(pathname)
    try:
        rx_data = getdata(pathname)
    except FileNotFoundError:
        print('file not found, please try it again')
        return  

    DataPlot(rx_data)
    PSD(rx_data)
    #plt.show()
    return 0

def getdir():
    pathname = askdirectory(initialdir='D:/tmp')
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
    fig.suptitle('time domain signal')
    #fig.tight_layout(pad = 0.002 )
    win = CreateNewWindow(title='time domain signal ')
    fig2can(fig,win)

def fig2can(fig,win):
    canvas = FigureCanvasTkAgg(fig,win) 
    canvas.show()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1) 


def PSD(rx_data):
    ind = 0
    for dfe_ind in range(4):
        fig,ax = plt.subplots(4,4)
        for row in ax:
            for col in row:
                psd.psd_jimmy(rx_data[ind],ax4=col,title='')
                ind = ind + 1
                col.set_xlabel('ant {}'.format(ind))
        fig.suptitle('DFE {}'.format(dfe_ind+1))
        fig.tight_layout()
        win = CreateNewWindow(title='DFE {}_PSD'.format(dfe_ind))
        fig2can(fig,win)
        
        
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
def RXCalCheck():
    DataAnalyze()
    print('done')

def CloseAll():
    plt.close('all')
    print('close all windows')

Button1 = tk.Button(top, text='Choose the Directory', font=('Arial', 12), width=30, height=1,command = RXCalCheck )
Button1.pack()

Button2 = tk.Button(top, text='Reserved', font=('Arial', 12), width=30, height=1,command = CloseAll)
Button2.pack()

top.mainloop()

