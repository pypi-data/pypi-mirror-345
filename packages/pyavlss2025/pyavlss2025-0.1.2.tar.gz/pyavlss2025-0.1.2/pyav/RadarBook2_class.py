import pyav.src.cmd_modules.Rbk2IfxTx2Rx16 as Rbk2IfxTx2Rx16
'''
    Designed for MIMO RadarBook2
'''


import  numpy as np
import numpy.matlib

import copy, sys, time, dill, threading

from threading                              import Thread
from tqdm                                   import tqdm 
from scipy                                  import signal

from pyav.SignalProcessing_class            import SignalProcessing
from datetime                               import datetime
# from numba                                  import jit


c0 = 299792458

class RadarBook2():
    def __init__(self,  RMin, 
                        RMax,
                        VMin,
                        VMax,
                        nPointsFFTrange,
                        nPointsFFTvel, 
                        nPointsFFTang, 
                        DelayProcessing,
                        Nchirp = 100 ):

        self.RMin = RMin
        self.RMax = RMax

        self.VMin = VMin
        self.VMax = VMax

        self.NFFT       = nPointsFFTrange
        self.NFFTVel    = nPointsFFTvel
        self.NFFTAnt    = nPointsFFTang

        self.DelayProcessing = DelayProcessing


        
        # Setup Connection
        #--------------------------------------------------------------------------
        #Brd     =   Rbk2IfxTx2Rx16.Rbk2IfxTx2Rx16('RadServe', '127.0.0.1', 8000, '192.168.1.1')
        self.Brd     =   Rbk2IfxTx2Rx16.Rbk2IfxTx2Rx16('PNet','192.168.1.1')

        self.Brd.BrdRst()
        self.Brd.BrdPwrEna()

        # Use 40 MHz clock for Range Doppler processing. The standard 20 MHz can
        # cause problems with the synchronisation of the sampling and the ramps
        self.Brd.BrdSetRole('Ms', 40e6)


        # Load Calibration Data
        #--------------------------------------------------------------------------
        self.dCalCfg = dict()
        self.dCalCfg['Mask'] = 1
        self.dCalCfg['Len'] = 32
        self.CalData = self.Brd.BrdGetCalData(self.dCalCfg)
        self.CalData_abs = abs(self.CalData)
        self.CalData_angle = np.angle(self.CalData)*180/np.pi #express in deg no rad

        # Configure Up-Chirp
        #--------------------------------------------------------------------------
        self.dCfg = dict()
        self.dCfg['fStrt'] = 76e9
        self.dCfg['fStop'] = 77e9
        self.dCfg['TRampUp'] = 102.4e-6
        self.dCfg['TRampDo'] = 18.8e-6
        self.dCfg['N'] = 512    # number of samples per chirp
        # self.dCfg['NrFrms'] = 100000 # different by number of chirp(=ramp frequency)
        self.dCfg['NLoop'] = Nchirp
        self.dCfg['IniEve'] = 0
        # self.dCfg['IniTim'] = 100e-3
        # self.dCfg['CfgTim'] = 10e-6
        

        self.chirp_totalTime = self.dCfg['NLoop'] * (self.dCfg['TRampUp']+self.dCfg['TRampDo'])
        self.dCfg['TInt'] = self.DelayProcessing  # period of each ramp sequence(=NLoop ramp frequency) = period between adjacent packets of (NLoop)chirps

        #--------------------------------------------------------------------------
        # Configure DMA Transfer to copy Cfg.NLoop frames simultaneously.
        # Required to achiev maximal data transfer between FPGA and Soc 
        self.Brd.Set('DmaMult', self.dCfg['NLoop'])
        # Copy only the data of a single channel. RX1. The data of the residual channels
        # is sampled but not transfered
        # self.Brd.Set('NrChn',16)



        #--------------------------------------------------------------------------
        # Configure Antenna activation sequence and timing with RCC1010 being the
        # master; This is the more advanced measurement mode and Cfg.NLoop can be
        # used to automatically repeat the measurements:
        # (1) The FPGA starts the programmed sequence after Cfg.TInt.
        # (2) The programmed sequence (caRampCfg) has to be shorter than TInt
        #--------------------------------------------------------------------------
        self.lRampCfg = list()
        # Up Chirp and trigger sampling
        self.dRampCfg = dict()
        self.dRampCfg['fStrt'] = self.dCfg['fStrt']
        self.dRampCfg['fStop'] = self.dCfg['fStop']
        self.dRampCfg['TRamp'] = self.dCfg['TRampUp']
        self.dRampCfg['TWait'] = 0
        self.dRampCfg['RampCfg'] = self.Brd.SampSeq + self.Brd.PaCtrl_Tx1

        self.lRampCfg.append(self.dRampCfg)
        # Downchirp with no sampling
        self.dRampCfg = dict()
        self.dRampCfg['fStrt'] = self.dCfg['fStop']
        self.dRampCfg['fStop'] = self.dCfg['fStrt']
        self.dRampCfg['TRamp'] = self.dCfg['TRampDo']
        self.dRampCfg['RampCfg'] = self.Brd.PaCtrl_Tx1
        self.dRampCfg['TWait'] = 0
        self.lRampCfg.append(self.dRampCfg)

        self.Tp = self.lRampCfg[0]['TRamp'] + self.lRampCfg[1]['TRamp']  

        self.Brd.RfMeas('RccMs', self.lRampCfg, self.dCfg)

        self.fs = self.Brd.Get('fs')
        self.N = int(self.Brd.Get('N'))
        self.Np = int(self.dCfg['NLoop'])
        self.NrChn = int(self.Brd.Get('NrChn'))
        self.fAdc  = int(self.Brd.Get('fAdc'))
        self.Rcic  = int(self.Brd.Get('CicR'))
        self.B               =   self.dCfg['fStop']-self.dCfg['fStrt'] # bandwitdh
        self.delta_R         =   c0/(2*self.B) # range resolution
        self.delta_v         =   (c0/((self.dCfg['fStop'] + self.dCfg['fStrt'])/2))/(2*self.dCfg['NLoop']*self.Tp) # velocity resolution 
        self.delta_theta     =   2/self.NrChn # angular resolution
        self.Txpos           =   self.Brd.RfGet('TxPosn') #position of the transmit antennas. The transmit antennas are spaced of (lambda*15)/2 each other
        self.Rxpos           =   self.Brd.RfGet('RxPosn') #position of the receive antennas. The receive antennas are spaced of lambda/2 each other
        # TX2 is spaced from RX1 by (lambda*16)/5
        self.f0              =   (self.dCfg['fStrt'] +self.dCfg['fStop'])/2
        self.waveLenght      =   c0/self.f0


        # Configure Signal Processing
        #--------------------------------------------------------------------------
        # Processing of range profile
        self.Win2D = self.Brd.hanning(self.N-1,self.Np)
        self.Win2D_ang = self.Brd.hanning(self.N-1,self.NrChn)

        self.ScaWin = sum(self.Win2D[:,0])
        self.ScaWin_ang = sum(self.Win2D_ang[:,0])


        self.kf = (self.dCfg['fStop'] - self.dCfg['fStrt'])/self.dCfg['TRampUp'] # = B/TrampUp
        self.vRange = np.arange(self.NFFT//2)/self.NFFT*self.fs*c0/(2*self.kf)
        self.fc = (self.dCfg['fStop'] + self.dCfg['fStrt'])/2


        self.RMinIdx = np.argmin(np.abs(self.vRange - self.RMin))
        self.RMaxIdx = np.argmin(np.abs(self.vRange - self.RMax))
        self.vRangeExt = self.vRange[self.RMinIdx:self.RMaxIdx+1 ]


        self.WinVel2D = self.Brd.hanning(int(self.Np), len(self.vRangeExt))
        self.ScaWinVel = sum(self.WinVel2D[:,0])
        self.WinVel2D = self.WinVel2D.T



        self.vFreqVel = np.arange(-self.NFFTVel//2,self.NFFTVel//2)/self.NFFTVel*(1/self.Tp)
        self.vFreqVel_max    =   1/(2*self.Tp)
        self.vFreqVel_step   =   1/(self.NFFTVel*self.Tp) # frequency bin's resolution
        self.vVel            =   self.vFreqVel*c0/(2*self.fc)
        self.vVel_max        =   self.vFreqVel_max*c0/(2.*self.fc) # max velocity = lambda/(4*Tp)
        self.vVel_step       =   self.vFreqVel_step*c0/(2.*self.fc) # velocity bin's resolution

        self.VMinIdx = np.argmin(np.abs(self.vVel - self.VMin))
        self.VMaxIdx = np.argmin(np.abs(self.vVel - self.VMax))
        self.vVelExt = self.vVel[self.VMinIdx:self.VMaxIdx+1]


        # WinAnt2D = self.Brd.hanning(NrChn, len(vRangeExt))
        self.WinAnt2D = self.Brd.hanning(self.NrChn, 1)
        self.ScaWinAnt = np.sum(self.WinAnt2D[:,0])
        self.WinAnt2D = self.WinAnt2D.T
        self.vAngDeg  = np.arcsin(2*np.arange(-self.NFFTAnt//2, self.NFFTAnt//2)/self.NFFTAnt)/np.pi*180
        self.vAngDeg_min = self.vAngDeg[0]
        self.vAngDeg_max = self.vAngDeg[len(self.vAngDeg)-1]

        self.mCalData = np.matlib.repmat(self.CalData, self.N-1,1) # calibration matrix where each column is a repetition of the calibration coefficients of the respective channel. (N-1) copies of CalData' 


        #--------------------------------------------------------------------------
        # Measure and calculate Range Doppler Map
        #--------------------------------------------------------------------------
        # Select channel to be processed. ChnSel <= NrChn
        # ChnSel = 0
        self.mCalData_rep=np.zeros((self.N-1, self.Np, self.NrChn),dtype="complex")
        self.Win2D_ang_rep=np.zeros((self.N-1, self.Np, self.NrChn),dtype="complex")
        self.WinVel2D_rep=np.zeros((self.vRangeExt.size, self.Np, self.NrChn),dtype="complex")

        for j in range( self.mCalData.shape[1]):
            for i in range( self.Np):
                self.mCalData_rep[:,i,j] = copy.copy(self.mCalData[:,j])
                self.Win2D_ang_rep[:,i,j] = copy.copy(self.Win2D_ang[:,j])
            self.WinVel2D_rep[:,:,j] = copy.copy(self.WinVel2D)



        #   ----------------------------------------------------------------------

        #   Print radar info
        self.print_info()

        self.SignalProcessing = SignalProcessing()

        
        #   Saved data
        self.SavedData  = { 'data':[] , 'times':[] , 'acquisitionTime': None, 
                            'emptyroom':{'RD':None, 'RDA':None},
                            'localization':{'absLocalization':[], 'RDALocalization':[]}
                            }

        
        # freeze
        self.freezeBrd = None



    def print_info(self):
        print();print()
        print('Range:')
        print('\tMinimum range:\t'+repr(self.RMin) + ' m')
        print('\tMaximum range:\t'+repr(self.RMax) + ' m')

        print()

        print('\tRange:\t\tnumber of bin: '+ repr(self.getRange_bin().shape[0]), end='\t')
        print('Average range bin size\t'+ repr(round( np.diff(self.vRange).mean(axis=0), 4 )) + ' m')

        print('\tvelocity:\tnumber of bin: '+ repr(self.getVelocity_bin().shape[0]), end='\t')
        print('Average velocity bin size\t'+ repr(round( np.diff(self.getVelocity_bin()).mean(axis=0), 4 )) + ' m/s')

        print('\tangle:\t\tnumber of bin: '+ repr(self.getAngle_bin().shape[0]), end='\t' )
        print('Average angle bin size\t'+ repr(round( np.diff(self.getAngle_bin()).mean(axis=0), 4 )) + ' °')

        print()

        self.dCfg['fStrt'] = 76e9
        self.dCfg['fStop'] = 77e9
        print('\tFrequency:')
        print('\t\tfreq start ' + repr(self.dCfg['fStrt'])+ 'Hz' )
        print('\t\tfreq stop ' + repr(self.dCfg['fStop'])+ ' Hz' )

        print()

        print('\tChirp:')
        print('\t\ttime RampUp\t\t' + repr(self.dCfg['TRampUp'])+ ' s' )
        print('\t\ttime RampDo\t\t' + repr(self.dCfg['TRampDo'])+ ' s' )
        print('\t\tNumber of chirp\t\t' + repr(self.dCfg['NLoop']) )
        print('\t\tTime to collect chirps\t' + repr(self.chirp_totalTime)+' s' ) 


        print()
        print('\tProcessing time '+ repr(round(self.DelayProcessing ,6) ) +' s')
        print('\tTotal delay between measurements ( Processing + collect data time) '+ (repr(self.dCfg['TInt']) if self.dCfg['TInt'] > self.chirp_totalTime else repr(self.chirp_totalTime) )+' s' )
        print('\tAcutal time calculation...')
        delta = []
        for i in tqdm(range(10)):
            t0 = time.time()
            radarData = self.get_radar_data()
            t1 = time.time()
            delta.append(t1-t0) 
        delta=np.array(delta).mean()
        print('\tActual time '+ repr(round(delta ,6) ) +' s')
        print('-------------- GO --------------')

        print();print()

    #    S A M P L E   R A T E   ------------------------------------------------------------------------------------------------
    def get_ChirpDuration(self, N=1):
        '''
        Input:
            N           :   number of chirp sends
                int
        Return:
            delta_t     :   the duration of a chirp multiplyed for the number of chirps
                float
        '''
        delta_t = (self.dCfg['TRampUp'] + self.dCfg['TRampDo'])*N
        return delta_t


    #    R A N G E   B I N   ------------------------------------------------------------------------------------------------
    def getRange_bin(self):
        '''
        Return:
            vRangeExt:      values of bins from RMin to RMax (shape: if N bin, then N+1 value)
                np.array
        '''
        return self.vRangeExt
    


    #    V E L O C I T Y   B I N   ------------------------------------------------------------------------------------------------
    def getVelocity_bin(self):
        '''
        Return:
            vVel:           values of bins (shape: if N bin, then N+1 value)
                np.array
        '''
        return self.vVelExt
    


    #    A N G L E S   B I N   ------------------------------------------------------------------------------------------------
    def getAngle_bin(self):
        '''
        Return:
            vAngDeg:        values of bins (shape: if N bin, then N+1 value)
                np.array
        '''
        return self.vAngDeg



    #    S A V E   ------------------------------------------------------------------------------------------------
    def SaveData(   self, 
                    numMeas,     # number of measurements
                    print_ProgressBar = True,
                    ):
        '''
            Saves a certain number of measurements in the variable self.SavedData.
            self.SavedData is a dict with key { 'data':list of np.array, 
                                                'times': list of time info for each getData, 
                                                'acquisitionTime: datetime time         }    

            Input:
                numMeas:                number of data that will be collected
                    int

                print_progressBar:      choice to print or not the progress bar
                    bool(=True)
                
                saveAs_DataCube:        specify if data is saved as a cube
                    bool(=True)
            
            example:    file_to_store = open("Serialized_obj/meas1.dill", "wb")
                        dill.dump( radar, file_to_store)  # file
                        file_to_store.close()
        '''
        
        acquisitionTime_start = datetime.now()

        if print_ProgressBar:
            for i in tqdm(range(numMeas), colour='green'):

                start_time = datetime.now()
                self.SavedData['data'].append( self.get_radar_data( ) )
                end_time = datetime.now()

                self.SavedData['times'].append({ 'start_time': start_time,
                                                'end_time'  : end_time          })


       
        else:
            for i in range(numMeas):

                start_time = datetime.now()
                self.SavedData['data'].append( self.get_radar_data( ) )
                end_time = datetime.now()

                self.SavedData['times'].append({    'start_time': start_time,
                                                    'end_time'  : end_time          })

        acquisitionTime_end = datetime.now()

        self.SavedData['acquisitionTime'] = acquisitionTime_end - acquisitionTime_start
        
        print('measurement avaiable in "SavedData", shape '+ repr(len(self.SavedData['data'])) + '\tacquisition time: ', self.SavedData['acquisitionTime'] )

    

    #    L O A D   ------------------------------------------------------------------------------------------------
    def LoadData( self ):
        '''
            Return  self.SavedData['data'] that is a list of np.array,
                    self.SavedData['times'] that is a list of time info about measurements
                    self.SavedData['acquisitionTime'] that is a datetime object 
                    ...

            example:    file_to_store = open("Serialized_obj/meas1.dill", "wb")
                        radar = dill.load(file_to_store)  # file
                        file_to_store.close()
        '''
        return  np.array(self.SavedData['data']), self.SavedData['times'], self.SavedData['acquisitionTime'], self.SavedData['emptyroom'], self.SavedData['localization']

        

    #    F R E E Z E    ------------------------------------------------------------------------------------------------
    def freeze(self):
        '''
            To freeze the obj in order to save it on binary file
                for example with library  dill (https://dill.readthedocs.io/en/latest/) or 
                                          pickle (https://docs.python.org/3/library/pickle.html)
        '''
        self.Brd.cRadDatSocket = None
        self.Brd.cRadSocket = None





    #    G E T   D A T A    ------------------------------------------------------------------------------------------------
    def get_radar_data(self):
        '''

            Return:
                    Data:   to collect data with the radar (shape: (n_samples, n_chirp,  16) )
                    
        '''
        Data = self.Brd.BrdGetData(self.Np)
        # Reshape
        Data = np.reshape(Data[:,:], (self.N, self.Np, self.NrChn), order='F')

        # Removing chirp index
        Data = Data[1:,:] 
        return Data
    


    #    R A N G E   F F T     ------------------------------------------------------------------------------------------------
    def compute_rangeFFT(self, DataCube):
        rangeFFT=np.fft.fft(DataCube[:,:,:]*self.Win2D_ang_rep*self.mCalData_rep,n=self.NFFT,axis=0)*self.Brd.FuSca/self.ScaWin_ang
        rangeFFT=rangeFFT[self.RMinIdx: self.RMaxIdx+1,:,:]

        return rangeFFT
    


    #    V E L O C I T Y   F F T     ------------------------------------------------------------------------------------------------
    def compute_velFFT(self, rangeFFT, antenna = 0):
        velFFT=np.fft.fft(rangeFFT[:,:,antenna]*self.WinVel2D, n=self.NFFTVel, axis=1)/self.ScaWinVel
        velFFT=np.fft.fftshift(velFFT, axes=1)
        velFFT=velFFT[:,self.VMinIdx:self.VMaxIdx+1]
        return velFFT



    #    A N G L E   F F T     ------------------------------------------------------------------------------------------------
    def compute_angleFFT(self, rangeFFT, idx = 0):
        angleFFT = np.fft.fft(rangeFFT[ : ,idx,:] * self.WinAnt2D, n=self.NFFTAnt, axis=1)/self.ScaWinAnt
        angleFFT = np.fft.fftshift(angleFFT, axes=1) 

        return angleFFT



    #    R A N G E - D O P P L E R     ------------------------------------------------------------------------------------------------
    def createMap_RangeDoppler(self, DataCube, antenna=0):
        '''
            Create a range dopplere map
            Input:
                DataCube        : Data obtained from  self.get_radar_data() 
                    np.array      shape(n_samples, n_chirp,  16)
                
                antenna         : define the antenna index to use for creating the range doppler map.
                    int/'all'     if 'all' the mean over all antennas will be computed.

            Return:
                rangeDoppler    : Range doppler map
                    np.array      shape(n_samples range FFT from RMin to RMax, n_samples velocity FFT)

        '''

        if antenna == 'all':
            rangeDoppler =np.array([ abs(self.compute_velFFT(self.compute_rangeFFT(DataCube), antenna)).T for antenna in range(16) ]).mean(axis=0)

        else:
            rangeFFT      = self.compute_rangeFFT(DataCube)
            rangeDoppler  = self.compute_velFFT(rangeFFT, antenna)
            rangeDoppler = abs(rangeDoppler).T

        return rangeDoppler



    #    R A N G E - A N G L E     ------------------------------------------------------------------------------------------------
    def createMap_RangeAngle(self, DataCube, chirpIdx=0):
        '''
            Create a range dopplere map
            Input:
                DataCube        : Data obtained from  self.get_radar_data() 
                    np.array      shape(n_samples, n_chirp,  16)
                
                chirpIdx        : define the chirp index to use for creating the range angle map.
                    int/'all'     if 'all' the mean over all chirps will be computed.

            Return:
                rangeAngle      :   range angle map
                    np.array        shape(n_samples range FFT from RMin to RMax, n_samples angles FFT)

        '''
        
        if chirpIdx == 'all':
            rangeAngle =np.array([ abs(self.compute_angleFFT(self.compute_rangeFFT(DataCube), chirpIdx)).T  for chirpIdx in range(DataCube.shape[1])] ).mean(axis=0)

        else:
            rangeFFT = self.compute_rangeFFT(DataCube)
            angleFFT = self.compute_angleFFT(rangeFFT, chirpIdx)
            rangeAngle =abs(angleFFT).T

        return rangeAngle


    #    R A N G E - D O P P L E R - A N G L E     ------------------------------------------------------------------------------------------------
    def createMap_RangeVelocityAngle(self, DataCube ):
        '''
            Create a range dopplere angle map
            Input:
                DataCube        : Data obtained from  self.get_radar_data() 
                    np.array      shape(n_samples, n_chirp,  16)
                
            Return:
                rangeAngle      :   range velocity angle map
                    np.array        shape(n_samples range FFT from RMin to RMax, n_samples vel FFT from VMin to VMax n_samples angles FFT)

        '''

        data = DataCube*self.Win2D_ang_rep*self.mCalData_rep
        R = np.fft.fft(data,n=self.NFFT,axis=0) * self.Brd.FuSca/self.ScaWin_ang
        R= R[ self.RMinIdx: self.RMaxIdx+1, :, :]

        R_temp = np.zeros(R.shape, dtype=complex)
        for antenna in range(16):
            R_temp[:,:,antenna] = R[:,:, antenna] *self.WinVel2D
        R =R_temp
        
        RV = np.fft.fft(R, n=self.NFFTVel,axis=1)/self.ScaWinVel
        RV=np.fft.fftshift(RV, axes=1)
        RV = RV[:,self.VMinIdx:self.VMaxIdx+1,:]

        RV_temp = np.zeros(RV.shape,dtype=complex)
        for idx in range(RV.shape[1]): 
            RV_temp[ : ,idx,:]  = RV[ : ,idx,:] * self.WinAnt2D
        RV = RV_temp

        RVA = np.fft.fft(RV,n=self.NFFTAnt,axis=2)
        RVA=np.fft.fftshift(RVA, axes=2)

        absRVA = abs(RVA)

        return absRVA
    

    #    R A N G E - D O P P L E R   &   R A N G E - D O P P L E R - A N G L E     ------------------------------------------------------------------------------------------------
    def createMAP_RDA_RD(self, DataCube ):
        '''
            Create a range dopplere angle map
            Input:
                DataCube        : Data obtained from  self.get_radar_data() 
                    np.array      shape(n_samples, n_chirp,  16)
                
            Return:
                rangeAngle      :   range velocity angle map
                    np.array        shape(n_samples range FFT from RMin to RMax, n_samples vel FFT from VMin to VMax n_samples angles FFT)

        '''

        data = DataCube*self.Win2D_ang_rep*self.mCalData_rep
        R = np.fft.fft(data,n=self.NFFT,axis=0) * self.Brd.FuSca/self.ScaWin_ang
        R= R[ self.RMinIdx: self.RMaxIdx+1, :, :]

        R_temp = np.zeros(R.shape, dtype=complex)
        for antenna in range(16):
            R_temp[:,:,antenna] = R[:,:, antenna] *self.WinVel2D
        R =R_temp
        
        RD = np.fft.fft(R, n=self.NFFTVel,axis=1)/self.ScaWinVel
        RD=np.fft.fftshift(RD, axes=1)
        RD = RD[:,self.VMinIdx:self.VMaxIdx+1,:]

        rangeDoppler = abs(RD).mean(axis=2).T
        
        RD_temp = np.zeros(RD.shape,dtype=complex)
        for idx in range(RD.shape[1]): 
            RD_temp[ : ,idx,:]  = RD[ : ,idx,:] * self.WinAnt2D
        RD = RD_temp

        RDA = np.fft.fft(RD,n=self.NFFTAnt,axis=2)
        RDA=np.fft.fftshift(RDA, axes=2)

        rangeDopplerAngle = abs(RDA)

        return rangeDopplerAngle, rangeDoppler


    #    R D   &   R D A   &   R bins A   f o r   c l a s s i f i c a t i o n    ------------------------------------------------------------------------------------------------
    def createMAP_RD_RDA_RBA(self, DataCube ):
        '''
            Create a range dopplere angle map
            Input:
                DataCube        : Data obtained from  self.get_radar_data() 
                    np.array      shape(n_samples, n_chirp,  16)
                
            Return:
                rangeDopplerAngle      :   RDA reduced (i.e. relevant velocity bins)
                    np.array                
                
                rangeDoppler            :   RD reduced (i.e. relevant velocity bins)
                    np.array  

                rangeBinsAngle          :   RA for each bins 
                    np.array  
        '''


        data = DataCube*self.Win2D_ang_rep*self.mCalData_rep
        R = np.fft.fft(data,n=self.NFFT,axis=0) * self.Brd.FuSca/self.ScaWin_ang
        R= R[ self.RMinIdx: self.RMaxIdx+1, :, :]

        R_temp = np.zeros(R.shape, dtype=complex)
        for antenna in range(16):
            R_temp[:,:,antenna] = R[:,:, antenna] *self.WinVel2D
        # R =R_temp
        
        RD = np.fft.fft(R_temp, n=self.NFFTVel,axis=1)/self.ScaWinVel
        RD=np.fft.fftshift(RD, axes=1)
        RD = RD[:,self.VMinIdx:self.VMaxIdx+1,:]

        rangeDoppler = abs(RD).mean(axis=2).T
        
        RD_temp = np.zeros(RD.shape,dtype=complex)
        for idx in range(RD.shape[1]): 
            RD_temp[ : ,idx,:]  = RD[ : ,idx,:] * self.WinAnt2D
        # RD = RD_temp

        RDA = np.fft.fft(RD_temp,n=self.NFFTAnt,axis=2)
        RDA=np.fft.fftshift(RDA, axes=2)

        rangeDopplerAngle = abs(RDA)
        
        #   R A       ------------------------------------
        R_temp = np.zeros(R.shape,dtype=complex)
        for idx in range(R.shape[1]): 
            R_temp[ : ,idx,:]  = R[ : ,idx,:] * self.WinAnt2D
        RbA = np.fft.fft(R_temp,n=self.NFFTAnt,axis=2)
        RbA=np.fft.fftshift(RbA, axes=2)
        rangeBinAngle = abs(RbA)

        return rangeDopplerAngle, rangeDoppler, rangeBinAngle
        #              RDA              RD          RbA=range-bins-angle for classification


    #   G E T   A N G L E   G I V E N   A   R A N G E   B I N     ------------------------------------------------------------------------------------------------
    def getAngle_givenRangeBin(self, centroid, dataCube, noise=None ):
        '''
            Given a range bin return the most likelihood angle. Use the angle FFT peak.

            Input:
                rangeFFT        :   the output of self.compute_rangeFFT( ... )
                    3D np.array

                rangeBinIndex   :   the identified range bin for which the angle is calculated
                    int
                
                noise       :   background noise
                    2D np.array


            Return:
                angle           :   is the closest angle bin to the FFT peak angle.
                    angle [deg]
        '''

        r , v = centroid

        rIdx = np.abs( self.getRange_bin() - r ).argmin()

        if noise is not None    : angleFFTvector = self.createMap_RangeAngle(dataCube, 0)[:,rIdx] - noise[:,rIdx]
        else                    : angleFFTvector = self.createMap_RangeAngle(dataCube, 0)

        angle = self.getAngle_bin()[ angleFFTvector.argmax() ]
        return angle


    
    # #   N U M B A   R A N G E - D O P P L E R    M A P     ------------------------------------------------------------------------------------------------
    # @jit
    # def createRD_withNumba(self, radarData):
    #     '''
    #         Numba is emplyed to make fast the code. The range-Doppler map is created meaning over all the antennas
    #     '''

    #     rangeFFT=np.fft.fft(radarData[:,:,:]*self.Win2D_ang_rep*self.mCalData_rep,n=self.NFFT,axis=0)*self.Brd.FuSca/self.ScaWin_ang
    #     rangeFFT=rangeFFT[self.RMinIdx: self.RMaxIdx+1,:,:]

    #     rangeDoppler = []
    #     for antenna in range(16):
    #         velFFT=np.fft.fft(rangeFFT[:,:,antenna]*self.WinVel2D, n=self.NFFTVel, axis=1)/self.ScaWinVel
    #         velFFT=np.fft.fftshift(velFFT, axes=1)
    #         velFFT=velFFT[:,self.VMinIdx:self.VMaxIdx+1]
    #         rangeDoppler.append(abs(velFFT).T)
        
    #     rangeDoppler = np.array(rangeDoppler ).mean(axis=0)
    #     return rangeDoppler


    # #   N U M B A   R A N G E - A N G L E   M A P     ------------------------------------------------------------------------------------------------
    # @jit
    # def createRA_withNumba(self, radarData):
    #     '''
    #         Return a list of chirp, each represented with its range-angle map
    #     '''
    #     allChirp = []

    #     rangeFFT=np.fft.fft(radarData[:,:,:]*self.Win2D_ang_rep*self.mCalData_rep,n=self.NFFT,axis=0)*self.Brd.FuSca/self.ScaWin_ang
    #     rangeFFT=rangeFFT[self.RMinIdx: self.RMaxIdx+1,:,:]

    #     for idx in range(radarData.shape[1]):
    #         angleFFT = np.fft.fft(rangeFFT[ : ,idx,:] * self.WinAnt2D, n=self.NFFTAnt, axis=1)/self.ScaWinAnt
    #         angleFFT = abs(np.fft.fftshift(angleFFT, axes=1) ).T
    #         allChirp.append( angleFFT )

    #     rangeAngle = np.array(allChirp ).mean(axis=0)
    #     return rangeAngle

    # '''


    ####    M O R E    ############################################################################################
    def debug(self):
        '''
            Debug function inside class
        '''
        d = 0

    
    


    

    #    R D   &   R D A   &   R bins A   f o r   c l a s s i f i c a t i o n    ------------------------------------------------------------------------------------------------
    def createMAP_RD_RDA_RBA_threading(self, DataCube, numThreads=15 ):
        '''
            Create a range dopplere angle map
            Input:
                DataCube        : Data obtained from  self.get_radar_data() 
                    np.array      shape(n_samples, n_chirp,  16)

                numThreads      : Number of threads used
                    int
                
            Return:
                rangeDopplerAngle      :   RDA reduced (i.e. relevant velocity bins)
                    np.array                
                
                rangeDoppler            :   RD reduced (i.e. relevant velocity bins)
                    np.array  

                rangeBinsAngle          :   RA for each bins 
                    np.array  
        '''
        def fft_thread(index, **kwargs):
            data_chunks[index] = np.fft.fft(data_chunks[index], **kwargs)


        data = DataCube*self.Win2D_ang_rep*self.mCalData_rep

        # R = np.fft.fft(data,n=self.NFFT,axis=0) * self.Brd.FuSca/self.ScaWin_ang
        data_chunks = np.array_split(data, numThreads, axis=1) # axis 1 for because fft is on axis=0
        # threads = [ threading.Thread( target=np.fft.fft, kwargs={'a':data_chunks[i], 'n':self.NFFT, 'axis': 0} )     for i in range(len(data_chunks))]
        threads = [ threading.Thread( target=fft_thread, args=(i, ), kwargs={'n':self.NFFT, 'axis': 0} )     for i in range(len(data_chunks))]
        for t in threads: t.start()
        for t in threads: t.join()
        R = np.concatenate(data_chunks, axis=1) * self.Brd.FuSca/self.ScaWin_ang
        R= R[ self.RMinIdx: self.RMaxIdx+1, :, :]


        R_temp = np.zeros(R.shape, dtype=complex)
        for antenna in range(16):
            R_temp[:,:,antenna] = R[:,:, antenna] *self.WinVel2D

        
        # RD = np.fft.fft(R_temp, n=self.NFFTVel,axis=1)/self.ScaWinVel
        data_chunks = np.array_split(R_temp, numThreads, axis=0) # axis 0 for because fft is on axis=1
        # threads = [ threading.Thread( target=np.fft.fft, kwargs={'a':data_chunks[i], 'n':self.NFFTVel, 'axis': 1} )     for i in range(len(data_chunks))]
        threads = [ threading.Thread( target=fft_thread, args=(i, ), kwargs={'n':self.NFFTVel, 'axis': 1} )     for i in range(len(data_chunks))]
        for t in threads: t.start()
        for t in threads: t.join()
        RD = np.concatenate(data_chunks, axis=0)/self.ScaWinVel
        RD=np.fft.fftshift(RD, axes=1)
        RD = RD[:,self.VMinIdx:self.VMaxIdx+1,:]

        rangeDoppler = abs(RD).mean(axis=2).T
        
        RD_temp = np.zeros(RD.shape,dtype=complex)
        for idx in range(RD.shape[1]): 
            RD_temp[ : ,idx,:]  = RD[ : ,idx,:] * self.WinAnt2D
        # RD = RD_temp

        # RDA = np.fft.fft(RD_temp,n=self.NFFTAnt,axis=2)
        data_chunks = np.array_split(RD_temp, numThreads, axis=0) # axis 0 for because fft is on axis=2
        # threads = [ threading.Thread( target=np.fft.fft, kwargs={'a':data_chunks[i], 'n':self.NFFTAnt, 'axis': 2} )     for i in range(len(data_chunks))]
        threads = [ threading.Thread( target=fft_thread, args=(i, ), kwargs={'n':self.NFFTAnt, 'axis': 2} )     for i in range(len(data_chunks))]
        for t in threads: t.start()
        for t in threads: t.join()
        RDA = np.concatenate(data_chunks, axis=0)
        RDA=np.fft.fftshift(RDA, axes=2)

        rangeDopplerAngle = abs(RDA)
        
        #   R A       ------------------------------------
        R_temp = np.zeros(R.shape,dtype=complex)
        for idx in range(R.shape[1]): 
            R_temp[ : ,idx,:]  = R[ : ,idx,:] * self.WinAnt2D

        # RbA = np.fft.fft(R_temp,n=self.NFFTAnt,axis=2)
        data_chunks = np.array_split(R_temp, numThreads, axis=0) # axis 0 for because fft is on axis=2
        # threads = [ threading.Thread( target=np.fft.fft, kwargs={'a':data_chunks[i], 'n':self.NFFTAnt, 'axis': 2} )     for i in range(len(data_chunks))]
        threads = [ threading.Thread( target=fft_thread, args=(i, ), kwargs={'n':self.NFFTAnt, 'axis': 2} )     for i in range(len(data_chunks))]
        for t in threads: t.start()
        for t in threads: t.join()
        RbA = np.concatenate(data_chunks, axis=0)
        RbA=np.fft.fftshift(RbA, axes=2)
        rangeBinAngle = abs(RbA)

        return rangeDopplerAngle, rangeDoppler, rangeBinAngle
        #              RDA              RD          RbA=range-bins-angle for classification