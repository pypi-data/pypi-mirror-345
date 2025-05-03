import numpy as np
from scipy import signal
from pyav.Wavelet_class import ContinuousWavelet

class SignalProcessing():
    def __init__(self):

        self.obj_CWT = ContinuousWavelet()

    def compute_RD_RDAthresholds(self, RDmaps, RDAmaps, constCoeff=True):
        '''
            Return thresholds for each point of RD and RDA
            Input:
                RDmaps       : range-Doppler map. None to not compute
                    np.array
                
                RDAmaps      : range-Doppler-angle map. None to not compute
                    np.array

                constCoeff : if true thresholds are all set using the maximum coefficient
                    bool
        '''
        if RDmaps is not None:
            #   R D    ----------------------------------------------------------------------------------------------------------------------
            mu_RD  = RDmaps.mean(axis=0)    # mean
            std_RD = RDmaps.std (axis=0)    # standard deviation

            real_coeff_RD   = (RDmaps.max(axis=0) - mu_RD)/std_RD
            approx_coeff_RD = np.ceil( real_coeff_RD  *10 )/10     #example: 11.2945 --> 11.3

            if constCoeff:
                RD_thresholds  = mu_RD  + approx_coeff_RD.max()*std_RD
            else:
                RD_thresholds = mu_RD+ approx_coeff_RD*std_RD

        else: RD_thresholds = None


        if RDAmaps is not None:
            #   R D A    --------------------------------------------------------------------------------------------------------------------
            mu_RDA  = RDAmaps.mean(axis=0)    # mean
            std_RDA = RDAmaps.std (axis=0)    # standard deviation

            real_coef_RDA    = (RDAmaps.max(axis=0) - mu_RDA)/std_RDA
            approx_coeff_RDA = np.ceil( real_coef_RDA  *10 )/10     #example: 11.2945 --> 11.3

            if constCoeff:                
                RDA_thresholds = mu_RDA + approx_coeff_RDA.max()*std_RDA 
            else:
                RDA_thresholds = mu_RDA + approx_coeff_RDA*std_RDA

        else: RDA_thresholds = None


        return RD_thresholds, RDA_thresholds

    #    E R    ------------------------------------------------------------------------------
    def compute_emptyRoom(self,sig, noise):
        ''' 
            Empty room filter

            Input:          
                sig  :     expected sig shape is ( …, …, …).
                    np.array

                noise:      same shape of sig. It will be subtracted from data
                    np.array

            Return:
                cleaned:    the filtered data (same shape of sig)
                    np.array
            
        '''
        cleaned = sig - noise
        cleaned[cleaned <0] = 0
        return  cleaned


    #    S D C    ------------------------------------------------------------------------------
    def compute_singleDelayCanceller(self, sig_k, sig_k_1=None):
        '''
        The single-delay canceller (SDC) is particularly suitable for high maneuvering targets and 
            exhibits good performance even for dynamic environments, 
            until the per-frame variability of the targets echoes is greater than the clutter one.

        Input:
            sig_k  :     expected sig shape is ( …, …, …).
                    np.array
            
            sig_k  :     expected sig shape is ( …, …, …). It is the signal at time instant k-1
                    np.array

        Return  :   the filtered data (same shape of sig)
            np.array

        '''
        sig =  (sig_k - sig_k_1) if sig_k_1 is not None else sig_k
        sig[sig<0]=0
        return sig
        

    #    E A F    ------------------------------------------------------------------------------ 
    def compute_exponentialAveragingFilter(self, sig_k, sig_k_1, beta=0.5 ):
        '''
        The parameter β ∈ (0, 1) weights the clutter signal at the previous frame and
            the current received frame to obtain the current clutter estimate. 
            This mitigation filter rejects the static clutter while being robust to slow environmental changes.
            However, echoes originated by slow moving targets are also attenuated, potentially causing performance degradation.

        Input:
            sig_k               :   expected sig shape is ( …, …, …).
                    np.array
            
            sig_k               :   expected sig shape is ( …, …, …). It is the signal at time instant k-1
                    np.array

            beta                :   weights the clutter signal at the previous frame and the current received frame 
                float (0, 1)            to obtain the current clutter estimate.

        Return  :   the filtered data (same shape of sig)
            np.array

        '''
        sig = sig_k - (beta*sig_k_1 +(1-beta)*sig_k)
        sig[sig<0]=0
        return sig



    #    C R E A T O R    ------------------------------------------------------------------------------
    def create_signal(self, N, f, fs, Amplitude = 1):
        '''
            Signal creator based on sin wave

            Input:
                N        :  [int]   Number of samples

                Amplitude:  [float or vector] sig amplitude

                f        :  [float] sig frequency
                
                fs       :  [float] sample rate

            Return:
                pi2t:       np.array containing the temporal value
                            shape( numberOf_time_period * n_pointsPerPeriod, )

                sig:     np.array containing the sig coefficients
                            shape( numberOf_time_period * n_pointsPerPeriod, )       
        '''
        time = np.arange( N ) / float(fs)

        sig = Amplitude    *  np.sin(2 * np.pi * f * time )

        return sig



    # version 2
    def create_signal_2(self, numberOf_time_period = 1, n_pointsPerPeriod = 100, signal_frequency=1):
        '''
            Signal creator based on sin wave

            Input:
                numberOf_time_period:   [int]   multiply 2*π in order to define the maximum time value

                n_pointsPerPeriod:      [int]   number of samples per period

                signal_frequency:       [int]   number of sin in a temporal period of 2*π

            Return:
                pi2t:       np.array containing the temporal value
                            shape( numberOf_time_period * n_pointsPerPeriod, )

                signal:     np.array containing the signal coefficients
                            shape( numberOf_time_period * n_pointsPerPeriod, )       
        '''

        pi2t = np.linspace(  0, numberOf_time_period * 2*np.pi, numberOf_time_period * n_pointsPerPeriod)

        signal = np.sin( signal_frequency * pi2t)

        return pi2t, signal



    #    S H O R T   T I M E   F O U R I E R   T R A N S F O R M    ------------------------------------------------------------------------------
    def transform_STFT(self, sig, fs, frameSize=None, hop_size=None):
        '''
            Input:
                sig       :     1D array of samples
                    1D np.array [float/complex]  
                
                fs        :     sample rate
                    float

                frameSize :     number of samples for window
                    int

                hop_size  :     number of samples whose window is moved
                    int
                
            Return:
                f               :       frequencies     (y-axis of 'timefrequency')
                    np.array [float]

                t               :       time            (x-axis of 'timefrequency')
                    1D np.array [float]
                
                timefrequency   :       STFT result
                    2D np.array   
        '''


        if not frameSize : frameSize = sig.shape[0] // 8
        if not hop_size  : hop_size  = frameSize // 4

        f, t, timefrequency = signal.stft(  sig, 
                                            fs, 
                                            nperseg  = frameSize, 
                                            noverlap = frameSize - hop_size,
                                            boundary = None )

        timefrequency = np.flip(timefrequency, axis=0)
        timefrequency = abs(timefrequency)

        f  = np.flip(f,axis=0)

        return f,t, timefrequency



    #    C O N T I N U O U S   W A V E L E T    ------------------------------------------------------------------------------
    def transform_CWT(self, sig, scales, motherWavelet):
        '''
            Note:   scales must be already normalized to Ts=1

            Input:
                sig:                     1D array of samples
                    1D np.array of float  
                
                scales:                     List of scales to be computed
                    1D np.array of float/int

                motherWavelet:              name of the mother wavelet that will be used 
                    string
                
            Return:
                cwt:                        axis-0 containes the wavelet applied (shape equal to the scales one)
                    2D np.array             axis-1 containes the transformed sig samples (shape equal to the sig one)
                
                freqs:
                    1D np.array             list of frequencies (multiply for sample time to normalize)
        '''

        cwt, freqs = self.obj_CWT.compute_ContinuousWavelet(sig, scales, motherWavelet)

        return cwt, freqs
    
