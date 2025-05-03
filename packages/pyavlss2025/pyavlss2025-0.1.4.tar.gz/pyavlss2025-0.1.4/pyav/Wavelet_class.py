
import numpy as np
import math
'''
    Continuous WaveLet class based on https://pywavelets.readthedocs.io/en/latest/index.html#contents
'''
class ContinuousWavelet():

    def __init__(self):
        pass



    #    G E T   C E N T R A L   F R E Q U E N C Y    ----------------------------------------------------------------------------
    def get_CentralFrequency(self, motherWavelet_names=None, precision=8, Print=True):
        '''
            Get the mother wavelet central frequency
            
            Input:
                motherWavelet_names:                list of mothers wavelets names. If None return the Fc for all possible mother Wavelet 
                    list of strings ['…', …, '…']  
                
                precision:                          number of significant values in central frequency
                    int
                
                Print:                              If True the output will be printed, otherwise only returned 
                    Boolean
            
            Return:
                Fc:                                 Contains a list of tuples composed by the mother wavelet name and its central frequency
                    list of tuples [(…,…), …]
        '''
        
        Fc = {}

        if motherWavelet_names is None:
            motherWavelet_names = self.get_motherWaveletlist()
            motherWavelet_names = motherWavelet_names[:-1]

        for name in motherWavelet_names:
            # append tuple-->(name,Fc)
            Fc[ name] =  pywt.central_frequency(    wavelet     = name, 
                                                    precision   = precision)   

        if Print:
            for name in Fc:  print(name+'\tFc= '+repr(Fc[name] ))

        return Fc


    #    G E T   M O T H E R S    W A V E L E T S    ----------------------------------------------------------------------------
    def get_motherWaveletlist(self):
        '''
            Return:
                motherWavelet_list:         return list of the mothers wavelets names (last element is a link to documentation)
                    list of string ['…', …]     

        '''
        motherWavelet_list = pywt.wavelist(kind='continuous')
        motherWavelet_list.append('More info:  https://pywavelets.readthedocs.io/en/latest/ref/cwt.html#continuous-wavelet-families')

        return motherWavelet_list


    #    S C A L E   -->   F R E Q U E N C Y    ----------------------------------------------------------------------------
    def scale_to_frequency(self, motherWavelet, scale, Ts=1, precision=8):
        '''
            Input:
                motherWavelet   :   mother wavelet name
                    string  
                
                scale           :   The wavelet scales to be converted
                    list [float/int]
                
                Ts              :   sampling interval (1/Sample_rate)
                    float

                precision       :   number of significant values in central frequency
                    int
                
            Return:
                f:   from a scale return the associated frequency
                    np.array
        '''
        
        freq = []
        for a in scale:
            freq.append(  pywt.scale2frequency(motherWavelet, a, precision=precision)/Ts )

        freq = np.array(freq)
        return freq


    #    F R E Q U E N C Y   -->   S C A L E    ----------------------------------------------------------------------------
    def frequency_to_scale(self, motherWavelet, freq, Ts=1, precision=8):
        '''
            Input:
                motherWavelet:      mother wavelet name
                    string  
                
                freq:              The frequencies to be converted
                    list [float/int]

                Ts              :   sampling interval (1/Sample_rate)
                    float

                precision:          number of significant values in central frequency
                    int
                
            Return:
                scales:   from a frequencies return the associated scales
                    np.array
        '''

        Fc = self.get_CentralFrequency( [motherWavelet], Print=False )
        Fc = Fc[motherWavelet]

        scales = []
        for f in freq:
            # Feq = Fc/a*Ts; Feq = f
            a = (Fc/f) /Ts
            scales.append( a )

        scales = np.array(scales)
        return scales


    #    C O M P U T E   C O N T I N U O U S   W A V E L E T    ----------------------------------------------------------------------------
    def compute_ContinuousWavelet(self, sig, scales, motherWavelet):
        '''
            Note:   scales must be already normalized to Ts=1

            Input:
                sig:                     1D array of samples
                    1D np.array of float  
                
                scales:                     List of scales to be computed ( min scale is 0.1 for pywt.cwt limit )
                    1D np.array of float/int

                motherWavelet:              name of the mother wavelet that will be used 
                    string

            Return:
                cwt:                        axis 0 time
                    2D np.array             axis 1 frequency
                
                freqs:
                    1D np.array             list of frequencies (multiply for sample time to normalize)
        '''

        checked_scales = [ a for a in scales if a >= 0.1]
        cwt, freqs = pywt.cwt(sig, checked_scales, motherWavelet)

        return cwt.T, freqs


    #    C R E A T E   S C A L E S    ----------------------------------------------------------------------------
    def create_scales(self, start, end, voices = 1, precision = 8 ):
        '''
            From the math.floor('start') to math.ceil('end') (included) a list of int is created. 
            Between two successive ints, 'voices' decimal are pushed

            Input:
                start       :   Values ≥ will be returned
                    float  

                end         :   Values ≤ will be returned
                    float  
                
                voices      :   number of values between two successive ints
                    float

                precision   :   number of significant values in central frequency
                    int
                
            Return:
                scales      :   float between 'start' and 'stop' with 'voices' decimals between two successive ints
                    1D np.array          
        '''

        
        start_floor = math.floor(start)
        end_ceil = math.ceil(end)

        temp_scales = []
        for i in range(start_floor, end_ceil ):
            temp_scales.append( i )
            temp_scales += np.linspace(i, i+1 ,voices+2)[1:-1].tolist()

        temp_scales.append( end_ceil )

        scales = []
        for a in temp_scales: 
            if not( a < start or a > end ): 
                scales.append( round(a, precision) )

        scales = np.array(scales)
        return scales


'''
    Discrete Wavelet class based on https://pywavelets.readthedocs.io/en/latest/index.html#contents
'''
class DiscreteWavelet():

    def __init__(self):
        pass


    #    G E T   D I S C R E T E   M O T H E R S   W A V E L E T S    ----------------------------------------------------------------------------
    def get_motherWaveletlist(self):
        '''
            Return:
                motherWavelet_list:         return list of discrete mothers wavelets names 
                    list of string ['…', …]     

        '''
        motherWavelet_list = pywt.wavelist(kind='discrete')
        return motherWavelet_list

    
    #   S I N G L E   L E V E L   D W T     ----------------------------------------------------------------------------
    def compute_DiscreteWavelet(self, sig, motherWavelet, mode='symmetric', axis=-1):
        '''
            Single level Discrete Wavelet Transform.

            Input:
                sig                 : 1D array of samples
                    np.array  
                
                motherWavelet       : name of the mother wavelet that will be used 
                    string
                
                mode                : https://pywavelets.readthedocs.io/en/latest/ref/signal-extension-modes.html#signal-extension-modes
                    str
                
                axis                : axis over which to compute the DWT. If not given, the last axis is used.
                    int

            Return:
                cA                  : approximation coefficients
                    np.array

                cD                  : detail coefficients   
                    np.array                   
        '''
        return pywt.dwt(sig, motherWavelet, mode=mode, axis=axis)


    def maximumDecompositionLevel(self, data_size, motherWaveletName):
        '''
            Return the maximum useful level of decomposition.

            Input:
                data_size           : input data length
                    int

                motherWaveletName   : the name of a discrete mother wavelet
                    str
            
            Return:
                
                max_level           : Maximum level
                    int
        '''
        return pywt.dwt_max_level( data_size, motherWaveletName)

    
    def multilevelDecomposition(self, sig, motherWavelet, level, mode='symmetric', axis=-1):
        '''
            Single level Discrete Wavelet Transform.

            Input:
                sig                 : 1D array of samples
                    np.array  
                
                motherWavelet       : name of the mother wavelet that will be used 
                    string
                
                level               : decomposition level (must be >= 0)
                    int
                
                mode                : https://pywavelets.readthedocs.io/en/latest/ref/signal-extension-modes.html#signal-extension-modes
                    str
                
                axis                : axis over which to compute the DWT. If not given, the last axis is used.
                    int

            Return:
                [cA_n, cD_n, cD_n-1, …, cD2, cD1]   : Ordered list of coefficients arrays where n denotes the level of decomposition. 
                                                      The first element (cA_n) of the result is approximation coefficients array and the following elements (cD_n - cD_1) are details coefficients arrays.               
        '''

        return pywt.wavedec(sig, motherWavelet, level=level, mode=mode, axis=axis)