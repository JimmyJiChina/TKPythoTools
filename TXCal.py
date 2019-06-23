import numpy as np
from scipy.signal import resample_poly
import os
from scipy.signal import freqz 
from scipy.signal import resample


DATA_START = 256
DATA_LENGTH = 2048
DATA_SECTION = 2560
CAPTURE_LENGTH = 20480
FFTSIZE = 128
TAPS = 16
FIR_DELAY = 8
ANT_TOAL = 64
REF_PORT = 46 # counting from 0


CALPATH = 'C:\\Users\\jimji\\JupyterNotebook\\AEQA_BF_Cali\\calibrationwithnotraffic\\'

def get_fir(ant_measure,ant_ref):
    corr_h = np.matmul(ant_measure.H,ant_measure)
    xcorr_h = np.matmul(ant_measure.H,ant_ref)
    #print('condition number:{}'.format(np.linalg.cond(Rh)))
    corr_h = corr_h + np.max(np.abs(corr_h))*1e-7*np.eye(len(corr_h))
    #print('condition number:{}'.format(np.linalg.cond(Rh)))
    fir = np.matmul(np.linalg.inv(corr_h),xcorr_h)
    return fir

def capture_to_list(filename,tx_data_list):
    fid = open(filename,'rb')
    dd = fid.read()
    fid.close()
    data = np.frombuffer(dd,dtype='>i2')
    data= data[1::2] + data[::2]*1j
    n1 = resample(data,num= 4 * len(data))
    n2 = resample(n1,num= len(n1)//5)
    data = n2
    for pipe in range(8):
        coe = data[DATA_SECTION*pipe:DATA_SECTION*pipe + DATA_SECTION]
        coe = coe[DATA_START-8:DATA_START + DATA_LENGTH+8]
        tx_data_list.append(coe)
    return tx_data_list





if __name__ == "__main__":
    
    #get the data from capture
    tx_data_list = list()
    for fileind in range(8):
        filename = CALPATH+'GROUP{}.bin'.format(fileind)
        if not os.path.isfile(filename):
            print('error file can not be found {}'.format(filename))
            break
        
        else :
            print('files there')
            tx_data_list = capture_to_list(filename,tx_data_list)
  
    
    # calculate the FIR coefficients
    data_ref = np.matrix(tx_data_list[REF_PORT][8:-8].reshape(-1,1))
    A_list = list()
    fir_list = list()
    for pipe in range(64):
        matrix_ant = np.zeros((len(data_ref),TAPS)) + np.zeros((len(data_ref),TAPS))*1j
        for dly in range(16):
            matrix_ant[:,dly] = tx_data_list[pipe][16-dly:16-dly + DATA_LENGTH]
        fir = get_fir(np.matrix(matrix_ant),data_ref)
        fir_list.append(fir)
        A_list.append(np.matrix(matrix_ant))

    
    

            



    

