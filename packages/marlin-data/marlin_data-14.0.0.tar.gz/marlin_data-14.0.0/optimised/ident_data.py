#!/usr/bin/env/pyhton3

"""
MARLIN IDent
c. Rahul Tandon, R.S. Aqua, 2024
E: r.tandon@rsaqua.co.uk

Optimised IDent data srtucture for optimised data statistics and data reporting.
"No python" approach in order to compile to machine code with native datatypes. 


"""

duration = {}
def startt(name=""):
    duration[name] = t.time()
    
def stopt(desc = "", name="", out=0):
    # print (desc)
    if name == "":
        name = desc
    
    d_ = t.time() - duration[name]
    if out == 1:
        print (f'{desc} => {d_} (s)')
    duration[name] = d_


# ================================== band pass


import numpy as np
import os
from scipy.io import wavfile

WAV_FILE_NAME = 'my_audio.wav'
lowcut = 1200.0
highcut = 1300.0
FRAME_RATE = 16000

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def bandpass_filter(buffer):
    return butter_bandpass_filter(buffer, lowcut, highcut, FRAME_RATE, order=6)

# samplerate, data = wavfile.read(os.path.join(record_path, WAV_FILE_NAME))
# assert samplerate == FRAME_RATE
# filtered = np.apply_along_axis(bandpass_filter, 0, data).astype('int16')
# wavfile.write(os.path.join(record_path, f'filtered_{WAV_FILE_NAME}'), samplerate, filtered)
    
    
# ================================== band pass
    

# Standard science imports
import numpy as np
from scipy import signal
import time as t

# Optmisied imports
from numba import int32, float32, njit, jit
from numba.experimental import jitclass
import antropy as ant


import librosa


# Define Numba types for jitclass (NO PYTHON)
IdentDataClassSpec = [      # a simple scalar field
    ('data_source', float32[:]),
    ('source_spectrogram', float32[:,:]),
    ('time_vector', float32[:]),
    ('frequency_vector', float32[:]),
    ('discretised_data', float32[:]),
    ('number_discretised_data', int32)
]

@jitclass(IdentDataClassSpec)
class IdentData(object):
    
    def __init__(self, data_source : np.ndarray = None):
       
        
        self.data_source = data_source
        # self.number_discretised_data = number_discretised_data
        # discretised_data_32 = discretised_data.dtype("float32")
        # self.discretised_data = discretised_data_32
    
    def fft_it(self):
        # n = len(self.data_source)
        n = 32768
       
        Y = np.fft.fft(self.data_source)/n
        # print (f'FFT shape : ')
        # print (Y.shape)
        Y = Y[:n//2]
        return Y
        # amplitudes =  abs(Y) 
        # max_power = np.max(amplitudes)
        
    def spec_it(self, Y : np.ndarray = None, sr = 19000):
        # f, t, Sxx = signal.spectrogram(Y, sr)
        pass
        
    def estimate_f_p_domain(self, Y):
        amplitudes = np.abs(Y)
        return amplitudes
        
    def set_source_spectrogram(self, spectrogram,  frequency_vector, time_vector):
    
        # Set the data vectors. These are required for data query. Use external routive and Librosa outside to 
        # to build the structure. External DFT (FFT) already optimised ( C wrapper )
        self.source_spectrogram = spectrogram
        self.time_vector = time_vector
        self.frequency_vector = frequency_vector
            
    def query_energy(self, time, frequency):
        """
        Main data query routine. 
        time : int : (ms) ->    data for this snapshot starts from zero so we need delta t from the start
                                of the snapshot. Will look for closest value
        
        frequency : float : (Hz) -> frequency of interest. Will look for closest frequency data. 
        
        """
        
        search_time_seconds = time / 1000
        search_frequency = frequency
        
        # query against the spectrogram data - time
        time_idx_value = np.argmin(np.abs(self.time_vector - search_time_seconds))
        print (f'Search time idx : {time_idx_value}')
        # query against the spectrogram data - frequency
        frequency_idx_value = np.argmin(np.abs(self.frequency_vector - search_frequency))
        print (f'Search frequency idx : {frequency_idx_value}')
        spectral_energy = self.source_spectrogram[frequency_idx_value][time_idx_value]
        print (f'Spectral energy : {spectral_energy}')
          
class IdentQuery(object):
    def __init__(self, delta_f, delta_t):
        self.delta_t = delta_t
        self.delta_f = delta_f
    
    def query_spectral_energy(self, source_spectrogram, frequency_vector, time_vector, frequency, time):
        
        time_idx_value = int((time)//self.delta_t)
        print (time_idx_value)
        # time_idx_value = np.argmin(np.abs(time_vector - time))
        
        # time_idx_value = grab_array_index(time_vector, time)
        
        # freq_idx_value = np.argmin(np.abs(frequency_vector - frequency))
        
        # freq_idx_value = grab_array_index(frequency_vector, frequency)
        
        freq_idx_value = int((frequency)//self.delta_f)
        # print (freq_idx_value)
        spectral_energy = source_spectrogram[freq_idx_value,time_idx_value]
        
        return float(spectral_energy)

def discretise_data(source_data, sr, discretise_delta_t,number_discretised_data, start_idx, end_idx):
    # discretised_data = np.zeros(10,dtype="float32")
    delta_wf_dim = int(sr * (discretise_delta_t))
    print (delta_wf_dim)
    print (discretise_delta_t, number_discretised_data)
    all_wf = []
    start_idx = start_idx
    end_idx = end_idx
    discretised_data = []
    for i in range(0,number_discretised_data):
        
        tmp_wf = source_data[start_idx:end_idx]
        all_wf.append(tmp_wf)
        discretised_data.append(tmp_wf)
        start_idx = start_idx + delta_wf_dim
        end_idx = start_idx + delta_wf_dim
    
    
    return (discretised_data)
        

def grab_array_index(  vector : np.array,  search_val : float32 = 0.0):
    #v3.0
    
    # numpy_time_start = t.time()
    idx_value = np.argmin(np.abs(vector - search_val))
    
    #idx_value = data_arr[frequency_index].flat[np.abs(data_arr[frequency_index] - _time).argmin()]
    
    return (idx_value)
    # print (idx_value)
    # numpy_time_end = t.time()
    # numpy_time = numpy_time_end - numpy_time_start
    # print (f'HYPED NUMPY index query time {numpy_time}')
         

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import json
    
    print ("Debug Tester")
    print ("################")
    
    source_filepath = "/home/vixen/rs/dev/marlin_data/optimised/cc_test_1.dat"
    source_wav_filepath = "/home/vixen/rs/dev/marlin_data/optimised/cc_test_1.wav"
    sr = librosa.get_samplerate(source_wav_filepath)
    
    # start and end s
    start_time = 0
    end_time = 300
    
    start_idx = int(sr * start_time)
    end_idx = int(sr * end_time)
    
    discretise_delta_t = 1 # discretise seconds
    total_src_time = end_time - start_time # src secondss
    source_data = None
    #load source data
   
   
    # 10s input data
    # source_filepath = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sim/streamedfile_999876447769858733241497.dat"
    # china creek test data
    
   
    dtype = np.dtype("float32")
    x, sr= librosa.load(source_wav_filepath,sr=sr)
    

    with open(source_filepath,'wb') as fp:
        x.tofile(fp)
    
    with open(source_filepath, 'rb') as fr:
        c = fr.read()
        np_data = None
        dtype = np.dtype("float32")
        source_data  = np.frombuffer(c, dtype=dtype)
        # source_data = np.load(source_filepath)
        
    print (source_data)
    print (source_data.shape)
    print (source_data.dtype)
    
    
  
    number_intervals = int (total_src_time / discretise_delta_t )
    discrete_data_src = discretise_data(source_data, sr, discretise_delta_t, number_intervals, start_idx, end_idx)
   
    
    #=========================== report ===============================
    n = 32768
    op_adapters = []
    entr_arr = []
    
    
    start_time_s = 0
    for data_src in discrete_data_src:
        
        op_adapter =  IdentData(data_src)
        
        # fft
        startt('small_fft')
        Y = np.abs(op_adapter.fft_it())
        stopt('small_fft')
        
        # permutation entropy
        startt('perm_entr')
        en = ant.perm_entropy(data_src, normalize=True)
        stopt('perm_entr')
        entr_arr.append(en)
        
        # autocorr -> of fft vector
        tmp_corr = signal.correlate(Y, Y, mode='full', method='auto')
        
        # Build freq vector 
        T = n/sr
        k = np.arange(n)
        frq = k/T # two sides frequency range
        frq = frq[:len(frq)//2] 
        
        # Fourier of signal autocorr
        tmp_adapter = IdentData(tmp_corr)
        corr_fourier = np.abs(tmp_adapter.fft_it())
        
        
        
        # --- Plots ---
        # plt.plot(en,color='green',linewidth=0.5, markersize=0.5) 
        # plt.title(f'Permutation Entropy ')
        # plt.xlabel('f (Hz)')
        # plt.ylabel('|P(freq)|')
        # plt.savefig(f'/home/vixen/html/demo/perm_entropy_{start_time_s}.png')
        # plt.close()
        
        plt.plot(frq,Y,color='blue',linewidth=0.5, markersize=0.5) 
        max_e = np.max(Y)
        plt.ylim(0,max_e)
       
        plt.title(f'Fourier Plot')
        plt.savefig(f'/home/vixen/html/demo/frequency_pdf_{start_time_s}.png')
        plt.close()
        
        x_vals = np.arange(len(tmp_corr))
        plt.plot(tmp_corr,color='red',linewidth=0.5, markersize=0.5) 
        plt.title(f'Auto Correlation')
        plt.savefig(f'/home/vixen/html/demo/auto_corr_pfd_{start_time_s}.png')
        plt.close()
        
        plt.plot(frq,corr_fourier,color='red',linewidth=0.5, markersize=0.5) 
        max_e = np.max(corr_fourier)
        plt.ylim(0,max_e)
        plt.title(f'Fourier Autocorrelate Plot')
        plt.savefig(f'/home/vixen/html/demo/fourier_of_signal_autocorr_{start_time_s}.png')
        plt.close()
    
            
        start_time_s += discretise_delta_t
        
        
            
        

    startt('main_fft')
    main_adapter = IdentData(source_data)
    Z = np.abs(main_adapter.fft_it())        
    stopt('main_fft')
    # print (entr_arr)
    # plot
    x_vals = np.arange(len(entr_arr))
    plt.plot(x_vals,entr_arr,color='green',linewidth=0.5, markersize=0.5) 
    plt.title(f'Permutation Entropy')
    plt.xlabel('f (Hz)')
    plt.ylabel('|P(freq)|')

    # plt.xlim(0, 200)
    plt.savefig(f'/home/vixen/html/demo/perm_entropy_all.png')
    plt.close()
    
    _c_source = signal.correlate(Z, Z, mode='full', method='auto')
    
    _c_ = signal.correlate(source_data[start_idx:end_idx], source_data[start_idx:end_idx], mode='full', method='auto')
    
    T = n/sr
    k = np.arange(n)
    frq = k/T # two sides frequency range
    frq = frq[:len(frq)//2] # one side frequency range
    
    
    
    x_vals = np.arange(len(_c_))
    plt.plot(_c_,color='red',linewidth=0.5, markersize=0.5) 
    plt.title(f'Auto Correlation')
    plt.savefig(f'/home/vixen/html/demo/auto_corr_signal_all.png')
    plt.close()
    
    x_vals = np.arange(len(_c_source))
    plt.plot(_c_source,color='red',linewidth=0.1, markersize=0.1) 
    plt.title(f'Auto Correlation')
    plt.savefig(f'/home/vixen/html/demo/auto_corr_fourier_all.png')
    plt.close()
    
    x_vals = np.arange(len(Z))
    plt.plot(frq,Z,color='red',linewidth=0.5, markersize=0.5) 
    # plt.xlim(20,400)
    max_e = np.max(Z)
    
    plt.ylim(0,max_e)
    plt.title(f'Fourier Plot')
    plt.savefig(f'/home/vixen/html/demo/frequency_pdf_all.png')
    plt.close()
    
    # print(duration)
    with open('/home/vixen/html/demo/performance_log.log', 'w') as pf:
        json.dump( duration, pf)
    
    
    
    # -------------- auto corr-----------
    
    corr_adapter = IdentData(_c_)
    
    corr_Z = np.abs(corr_adapter.fft_it())
   
    plt.plot(frq,corr_Z,color='red',linewidth=0.5, markersize=0.5) 
    # plt.xlim(20, 100)
    # plt.ylim(0,2)
    plt.title(f'Fourier Autocorrelate Plot')
    plt.savefig(f'/home/vixen/html/demo/fourier_of_signal_autocorr_all.png')
    plt.close()
    
    
    
    exit()
    #=========================== optimised data adapter ===============================
    
    tester = IdentData(source_data)
    tester.discretise_data(source_data, sr, discretise_delta_t)
   
    # print ('Building fft - np.nfft')
    fft_start = t.time()

    Y = tester.fft_it()
    
    fff_end = t.time()
    fft_run_time = fff_end - fft_start
    # print (f'FFT took {fft_run_time} (s)')
    # print ("################")
    
    # print ('Building fft - np.nfft')
    fft_start = t.time()

    Y = tester.fft_it()
    # print (Y.shape)
    # print (Y)
    fff_end = t.time()
    fft_run_time = fff_end - fft_start
    print (f'FFT took {fft_run_time} (s)')
    print ("################")
    
    

    # print ('Building Power')
    power_start = t.time()

    amplitudes = tester.estimate_f_p_domain(Y)
    
    # print (amplitudes.shape)
    # print (amplitudes)
    power_end = t.time()
    power_run_time = power_end - power_start
    # print (f'Power took {power_run_time} (s)')
    # print ("################")
    
    print ('Building Power')
    power_start = t.time()

    amplitudes = tester.estimate_f_p_domain(Y)
    
    power_end = t.time()
    power_run_time = power_end - power_start
    print (f'Power took {power_run_time} (s)')
    print ("################")
    
    # print (amplitudes.shape)
    n = 16384
    k = np.arange(n)
    # print (k)
    T = n/sr
    
    frq = k/T # two sides frequency range
    frq = frq[:len(frq)//2] # one side frequency range
    # print (len(frq))
    
    plt.plot(frq,amplitudes,color='green',linewidth=0.1, markersize=0.5) 
    plt.title(f'Power Spectrum')
    plt.xlabel('f (Hz)')
    plt.ylabel('|P(freq)|')

    plt.xlim(0, 200)
    plt.savefig(f'powerprofile_.png')
    plt.close()
        
    hop_length = n // 2
    libosa_time_start = t.time()
    D = librosa.stft(source_data, n_fft=n, hop_length= (hop_length))
    # print (D.shape)
    # print (D)
    librosa_time_end = t.time()
    librosa_time = librosa_time_end - libosa_time_start
    print (f'Librosa FFT took {librosa_time} (s)')
    print ("################")
    
    
    libosa_time_start = t.time()
    D_abs = np.abs(D)
    # print (D_abs.shape)
    # print (D_abs)
    librosa_time_end = t.time()
    librosa_time = librosa_time_end - libosa_time_start
    print (f'Librosa Power took {librosa_time} (s)')
    print ("################")
    
    librosa_time_bins = librosa.frames_to_time(range(0, D_abs.shape[1]), sr=sr, hop_length=(n//2), n_fft=n-1).astype(np.float32)
    print (type(librosa_time_bins))
    librosa_f_bins = librosa.core.fft_frequencies(n_fft=n, sr=sr).astype(np.float32)
    print (type(librosa_f_bins))
    
    spec_start = t.time()
    # tester.spec_it(source_data)
    f_, t_, Sxx = signal.spectrogram(source_data, sr)
    spec_end = t.time()
    spec_run = spec_end - spec_start
    print (f'SPEC run time : {spec_run}')
    print ("################")
    # print (f_)
    # print (t_)
    
    tester.set_source_spectrogram(Sxx,librosa_f_bins,librosa_time_bins  )
    # spec_start = t.time()
    # tester.spec_it(source_data)
    # spec_end = t.time()
    # spec_run = spec_end - spec_start
    # print (f'SPEC run time : {spec_run}')
    
    data_query_time_start = t.time()
    tester.query_energy(2.2, 50)
    data_query_time_end = t.time()
    data_query_time = data_query_time_end - data_query_time_start
    print (f'data query time (numba): {data_query_time}')
    
    # external t idx
    # data_query_time_start = t.time()
    # time_idx_value = np.argmin(np.abs(librosa_time_bins - 2.2))
    # data_query_time_end = t.time() 
    # data_query_time = data_query_time_end - data_query_time_start
    # print (f'data query time : {data_query_time}')
    # print (time_idx_value)
    
    # data_query_time_start = t.time()
    # freq_idx_value = np.argmin(np.abs(librosa_f_bins - 50.0))
    # data_query_time_end = t.time() 
    # data_query_time = data_query_time_end - data_query_time_start
    # print (f'data query time : {data_query_time}')
    # print (freq_idx_value)
    
    # print (tester.source_spectrogram[freq_idx_value, time_idx_value])
    
    

    # data_query_time_start = t.time()
    # freq_idx_value = np.argmin(np.abs(librosa_f_bins - 50.0))
    # data_query_time_end = t.time() 
    # data_query_time = data_query_time_end - data_query_time_start
    # print (f'data query time : {data_query_time}')
    # print (freq_idx_value)

    delta_f = librosa_f_bins[1]-librosa_f_bins[0]
    delta_t = librosa_time_bins[1] - librosa_time_bins[0]
    e_query = IdentQuery(delta_f, delta_t)
    data_query_time_start = t.time()
    spectral_e = e_query.query_spectral_energy(tester.source_spectrogram,librosa_f_bins,librosa_time_bins,120.0, 2.4)
    data_query_time_end = t.time() 
    data_query_time = data_query_time_end - data_query_time_start
    print (f'data query time (ext) : {data_query_time}')
    # print (spectral_e)
    
    
   