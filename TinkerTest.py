import numpy as np 

import tkinter as tk
from tkinter.filedialog import askdirectory
import matplotlib
from string import Template
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from scipy.signal import freqz
sys.path.append('C:/Users/jimji/.ipython')
#print(sys.path)
import psd_jimmy as psd
from scipy.signal import resample
import matplotlib.pyplot as plt
top = tk.Tk()
top.title('BF Calibration Data Analyzer')
top.geometry('400x300')  
plt.rcParams['figure.figsize'] = 15,15

TAPS = 16
PIPE_OF_GROUP = 8
REF_PORT_TX = 1
REF_PORT_RX = 1
TX_CAPTURE_FILE = Template('GROUP${group}.bin')
RX_CAPTURE_FILE = Template('Ant${ant_num}_cap_samp.bin')
RX_COE_FILE_NAME =Template('CoefsUl${dfe}.bin')
TX_COE_FILE_NAME =Template('CoefsDl${dfe}.bin')
FIR_DELAY = 8
SAMPLE_RATE = 122.88
TX_DATA_START = 256
TX_DATA_LENGTH = 2048
TX_DATA_SECTION = 2560
CAPTURE_LENGTH = 20480

class buffer_data:
    def __init__(self):
        print('initialize variables')
        self.rx_data_list =list()
        self.tx_data_list =list()
        self.rx_coe_list =list()
        self.tx_coe_list =list()


def CreateNewWindow(title = 'New windows',size = '400x300'):
    win = tk.Tk()
    win.title(title)
    win.geometry(size) 
    return win

def DataAnalyze(capture = 'TX'):
    #plt.close('all')
    pathname = getdir()
    print(pathname)
    try:
        data = getdata(pathname)
    except FileNotFoundError:
        print('file not found, please try it again')
        return  
    if capture =='TX':
        buffer_data.tx_data_list = data
    else:
        buffer_data.rx_data_list = data

    DataPlot(data)
    PSD(data)
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

def GroupPlot(tx_data,plot_length =None):
    if plot_length == None:
        plot_length = len(tx_data[0])
    #picture_domain = len(tx_data)//2
    fig, ax = plt.subplots(8,8)
    pic_ind = 0
    pipe_ind = 0
    for row in ax:
        for col in row:
            col.plot(tx_data[pipe_ind].real[:plot_length])
            col.plot(tx_data[pipe_ind].imag[:plot_length])
            col.set_title('pipe : {}'.format(pic_ind+1))
            pipe_ind = pipe_ind + 1
    #plt.show()
    
    pic_ind = pic_ind + 1
    fig.suptitle('time domain signal')
    #fig.tight_layout(pad = 0.002 )
    win = CreateNewWindow(title='time domain signal pipe ')
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



def getdata(pathname, direction='TX',group_num = 8):
    if direction == 'RX':
        rx_data = list()
        for pipe in range(64) :
            filename = pathname + '/'+ RX_CAPTURE_FILE.substitute(ant_num=pipe)
            fid = open(filename,'rb')
            dd = fid.read()
            data = np.frombuffer(dd,dtype='<i2')
            sig = data[1::2] + 1j*data[::2]
            rx_data.append(sig)
            fid.close()
        return rx_data
    elif direction =='TX':
        tx_data = list()
        for eachgroup in range(group_num) :
            filename = pathname + '/' + TX_CAPTURE_FILE.substitute(group=eachgroup)
            fid = open(filename,'rb')
            dd = fid.read()
            data = np.frombuffer(dd,dtype='<i2')
            group_data = data[1::2] + 1j*data[::2]
            
           
            for pipe in range(PIPE_OF_GROUP):
                data = group_data[TX_DATA_SECTION*pipe:TX_DATA_SECTION*pipe + TX_DATA_SECTION]
                #n1 = resample(data,num= 4 * len(data))
                #n2 = resample(n1,num= len(n1)//5)
                #data = n2
                data = data[TX_DATA_START-8:TX_DATA_START + TX_DATA_LENGTH+8]
                tx_data.append(data)
    return tx_data


def get_coe(pathname,direction = 'TX'):
    coe_list = list()
    coe_num = 16 # each DFE has 16 FIR
    if direction == 'TX':
        step = 32 # TX coefficients have 16 empty ones
        file_temp = TX_COE_FILE_NAME
    else:
        step = 16 # RX
        file_temp = RX_COE_FILE_NAME
    for dfe_num in range(4) :
        
        filename = pathname + '/' + file_temp.substitute(dfe = dfe_num)
        fid = open(filename,'rb')
        dd = fid.read()
        data = np.frombuffer(dd,dtype='>i2')
        coe = data[1::2] + 1j*data[::2]
        for pipe in range(coe_num):
            coe_list.append(coe[step*pipe:step*pipe + coe_num])
        fid.close()
    
    return coe_list


def get_tx_data(pathname):
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

def coe_plot(coe_list,resp = 'PHASE'):
    ind = 0
   
    for dfe_ind in range(4):
        fig,ax = plt.subplots(4,4)
        for row in ax:
            for col in row:
                coe = coe_list[ind]/2**15
                
                w,h = freqz(coe)
                h = h*np.exp(1j*w*FIR_DELAY)
                if resp == 'PHASE':
                    col.plot(w/np.pi*SAMPLE_RATE,np.angle(h)*180/np.pi)
                else:
                    col.plot(w/np.pi*SAMPLE_RATE,np.log10(np.abs(h)*10))
                ind = ind + 1
                col.set_xlabel('ant {}'.format(ind))
        fig.suptitle('DFE {}'.format(dfe_ind+1))
        fig.tight_layout()
        win = CreateNewWindow(title='DFE {}_coefficients'.format(dfe_ind))
        fig2can(fig,win)
    

def get_data():
    filepath = getdir()
    buffer_data.rx_coe_list = get_coe(filepath,direction ='RX')
    buffer_data.rx_data_list = getdata(filepath,direction ='RX')
    buffer_data.tx_coe_list = get_coe(filepath,direction ='TX')
    buffer_data.tx_data_list = getdata(filepath,direction='TX')
    print('data loaded')
    #plot_rx_coe(resp = 'PHASE')
    #coe_plot(rx_coe_list)


def plot_rx_coe_phase():
    coe_plot(buffer_data.rx_coe_list,resp = 'PHASE')
    
def plot_rx_coe_amp():
    coe_plot(buffer_data.rx_coe_list, resp = 'AMP')

def plot_tx_coe_phase():
    coe_plot(buffer_data.tx_coe_list,resp = 'PHASE')
    
def plot_tx_coe_amp():
    coe_plot(buffer_data.tx_coe_list, resp = 'AMP')

def plot_tx_data():
    DataPlot(buffer_data.tx_data_list)

def plot_rx_data():
    DataPlot(buffer_data.rx_data_list)

def TX_capture_read():
    filepath = './group_capture/'

    buffer_data.tx_data_list = getdata(filepath,direction='TX',group_num=8)
    print('TX data collected length :{}'.format(len(buffer_data.tx_data_list)))
    print('each group data length :{}'.format(len(buffer_data.tx_data_list[0])))
    
    GroupPlot(buffer_data.tx_data_list,plot_length=256)
    fir_list = TX_FIR_calc(buffer_data.tx_data_list)
    coe_plot(fir_list)

	
def TX_FIR_calc(tx_data_list):
    data_ref = np.matrix(tx_data_list[REF_PORT_TX][8:-8].reshape(-1,1))
    A_list = list()
    fir_list = list()
    for pipe in range(len(tx_data_list)):
        matrix_ant = np.zeros((len(data_ref),TAPS)) + np.zeros((len(data_ref),TAPS))*1j
        for dly in range(16):
            matrix_ant[:,dly] = tx_data_list[pipe][16-dly:16-dly + TX_DATA_LENGTH]
        fir = get_fir(np.matrix(matrix_ant),data_ref)
        fir_list.append(fir)
        #A_list.append(np.matrix(matrix_ant))
    return fir_list

def get_fir(ant_measure,ant_ref):
    corr_h = np.matmul(ant_measure.H,ant_measure)
    xcorr_h = np.matmul(ant_measure.H,ant_ref)
    #print('condition number:{}'.format(np.linalg.cond(Rh)))
    corr_h = corr_h + np.max(np.abs(corr_h))*1e-7*np.eye(len(corr_h))
    #print('condition number:{}'.format(np.linalg.cond(Rh)))
    fir = np.matmul(np.linalg.inv(corr_h),xcorr_h)
    return fir

    

   
buffer_data = buffer_data()

Button2 = tk.Button(top, text='Data Retrive', font=('Arial', 12), width=30, height=1,command = get_data)
Button2.pack()

Button3 = tk.Button(top, text='RX Coefficients Plot Phase', font=('Arial', 12), width=30, height=1,command = plot_rx_coe_phase)
Button3.pack()

Button4 = tk.Button(top, text='RX Coefficients Plot Amplitude', font=('Arial', 12), width=30, height=1,command = plot_rx_coe_amp)
Button4.pack()

Button5 = tk.Button(top, text='TX Coefficients Plot Phase', font=('Arial', 12), width=30, height=1,command = plot_tx_coe_phase)
Button5.pack()

Button6 = tk.Button(top, text='TX Coefficients Plot Amplitude', font=('Arial', 12), width=30, height=1,command = plot_tx_coe_amp)
Button6.pack()

Button7 = tk.Button(top, text='TX Data Plot', font=('Arial', 12), width=30, height=1,command = plot_tx_data)
Button7.pack()

Button8 = tk.Button(top, text='RX Data Plot ', font=('Arial', 12), width=30, height=1,command = plot_rx_data)
Button8.pack()


Button9 = tk.Button(top, text='TX Group Read ', font=('Arial', 12), width=30, height=1,command = TX_capture_read)
Button9.pack()


top.mainloop()

