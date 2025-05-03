"""This module contains the classes and methods for the remote controll of the
RadarLog base-band board
   """
import  os
import  sys
import  ctypes
import  socket
from    numpy import *
import  pyav.src.cmd_modules.Rbk2 as Rbk2
import  pyav.src.cmd_modules.DevRcc1010  as DevRcc1010
import  pyav.src.cmd_modules.DevRrn7745  as DevRrn7745
import  pyav.src.cmd_modules.SeqTrig     as SeqTrig 
import  weakref
import  traceback

#< @version  2.3.0
#< Support GPS mode in RccMs Mode

class Rbk2IfxTx2Rx16(Rbk2.Rbk2):

    ## Constructor
    def __init__(self, stConType, *args):
        super(Rbk2IfxTx2Rx16, self).__init__(stConType, *args)

        #------------------------------------------------------------------
        # Define flags of RRN7745 registers
        #------------------------------------------------------------------          
        self.RRN7745_REG_ENA_MIX_DAC_TST = 1
        self.RRN7745_REG_ENA_MIX_DAC_LO = 2
        self.RRN7745_REG_ENA_MIX_RX_1 = 4
        self.RRN7745_REG_ENA_MIX_RX_2 = 8
        self.RRN7745_REG_ENA_MIX_RX_3 = 16
        self.RRN7745_REG_ENA_MIX_RX_4 = 32
        self.RRN7745_REG_ENA_MIX_RX_ALL = 4 + 8 + 16 + 32
        self.RRN7745_REG_ENA_MIX_RST = 64 + 128
        self.RRN7745_REG_MUX_TRI = 0
        self.RRN7745_REG_MUX_TEMP = 16
        self.RRN7745_REG_MUX_PTST = 32
        self.RRN7745_REG_MUX_PLO = 48
        self.RRN7745_REG_DCX_VAL_OFFS = 32   
    
        #------------------------------------------------------------------
        # Define flags of Rpn7720 registers
        #------------------------------------------------------------------        
        self.RPN7720_REG_PACON_MUX_P1 = 3
        self.RPN7720_REG_PACON_MUX_P2 = 3*16   
        
        self.PaCtrl_TxOff = 0        
        self.PaCtrl_Tx1 = 2
        self.PaCtrl_Tx2 = 4
        self.TxPwr = 63
        
        # P5 is used to control the sampling chain
        self.SampSeq = int('000001', 2)   

        self.Rf_fStrt = 76e9
        self.Rf_fStop = 77e9
        self.Rf_TRampUp = 256e-6
        self.Rf_TRampDo = 256e-6
        
        self.Rf_Rpn7720Cfg1_Mask = 1
        self.Rf_Rpn7720Cfg1_LoChain = int('01111111',2)
        self.Rf_Rpn7720Cfg1_Pa1 = 0
        self.Rf_Rpn7720Cfg1_Pa2 = 0
        self.Rf_Rpn7720Cfg1_PaCon = 0
        self.Rf_Rpn7720Cfg1_Mux = int('10000',2)
        
        #--------------------------------------------------------------------------
        # Static RX Rrn7745 configuration
        #--------------------------------------------------------------------------
        # RX 1
        self.Rf_Rrn7745_Cfg1_Mask = 1
        self.Rf_Rrn7745_Cfg1_Tst_I = int('10000000', 2)
        self.Rf_Rrn7745_Cfg1_Tst_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg1_Lo_I = int('00000000', 2)
        self.Rf_Rrn7745_Cfg1_Lo_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg1_Ena_Mix = 2 + 4 + 8 + 16 + 32 + 64 + 128
        self.Rf_Rrn7745_Cfg1_Mux = 0
        self.Rf_Rrn7745_Cfg1_Dc1 = 4*32
        self.Rf_Rrn7745_Cfg1_Dc2 = 4*32
        self.Rf_Rrn7745_Cfg1_Dc3 = 4*32
        self.Rf_Rrn7745_Cfg1_Dc4 = 4*32
        
        # Rx 2
        self.Rf_Rrn7745_Cfg2_Mask = 2
        self.Rf_Rrn7745_Cfg2_Tst_I = int('10000000', 2)
        self.Rf_Rrn7745_Cfg2_Tst_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg2_Lo_I = int('00000000', 2)
        self.Rf_Rrn7745_Cfg2_Lo_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg2_Ena_Mix = 2 + 4 + 8 + 16 + 32 + 64 + 128
        self.Rf_Rrn7745_Cfg2_Mux = 0
        self.Rf_Rrn7745_Cfg2_Dc1 = 4*32
        self.Rf_Rrn7745_Cfg2_Dc2 = 4*32
        self.Rf_Rrn7745_Cfg2_Dc3 = 4*32
        self.Rf_Rrn7745_Cfg2_Dc4 = 4*32

        # Rx 3
        self.Rf_Rrn7745_Cfg3_Mask = 4
        self.Rf_Rrn7745_Cfg3_Tst_I = int('10000000', 2)
        self.Rf_Rrn7745_Cfg3_Tst_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg3_Lo_I = int('00000000', 2)
        self.Rf_Rrn7745_Cfg3_Lo_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg3_Ena_Mix = 2 + 4 + 8 + 16 + 32 + 64 + 128
        self.Rf_Rrn7745_Cfg3_Mux = 0
        self.Rf_Rrn7745_Cfg3_Dc1 = 4*32
        self.Rf_Rrn7745_Cfg3_Dc2 = 4*32
        self.Rf_Rrn7745_Cfg3_Dc3 = 4*32
        self.Rf_Rrn7745_Cfg3_Dc4 = 4*32
        
        # Rx 4
        self.Rf_Rrn7745_Cfg4_Mask = 8
        self.Rf_Rrn7745_Cfg4_Tst_I = int('10000000', 2)
        self.Rf_Rrn7745_Cfg4_Tst_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg4_Lo_I = int('00000000', 2)
        self.Rf_Rrn7745_Cfg4_Lo_Q = int('10000000', 2)
        self.Rf_Rrn7745_Cfg4_Ena_Mix = 2 + 4 + 8 + 16 + 32 + 64 + 128
        self.Rf_Rrn7745_Cfg4_Mux = 0
        self.Rf_Rrn7745_Cfg4_Dc1 = 4*32
        self.Rf_Rrn7745_Cfg4_Dc2 = 4*32
        self.Rf_Rrn7745_Cfg4_Dc3 = 4*32
        self.Rf_Rrn7745_Cfg4_Dc4 = 4*32        
        
        self.Rf_RccCfg_Mask = 1
        self.stRfVers = '2.3.0'
        self.Rf_Rpn7720_Pwr1 = 63
        self.Rf_Rpn7720_Pwr2 = 63

        self.RCC1010_PaCfg_Pa1 = 1   
        self.RCC1010_PaCfg_Pa2 = 2 
        self.RCC1010_PaCfg_Pa3 = 4
        self.RCC1010_PaCfg_Pa4 = 8
        self.RCC1010_PaCfg_LO = 16
        self.RCC1010_PaCfg_EN = 128 

        self.Rcc1010 = DevRcc1010.DevRcc1010(weakref.ref(self), 1)

        self.Rad_FUsbCfg_WaitLev = 2**15-4096
        self.Set('NrChn',16)
        
        self.Computation.Enable();

    # DOXYGEN ------------------------------------------------------
    #> @brief Get Version information of frontend class
    #>
    #> Get version of class 
    #>      - Version string is returned as string
    #>
    #> @return  Returns the version string of the class (e.g. 0.5.0)          
    def     RfGetVers(self):            
        return self.stRfVers

    # DOXYGEN -------------------------------------------------
    #> @brief Displays version information in Matlab command window  
    #>
    #> Display version of class in Matlab command window            
    def     RfDispVers(self):         
        print('Rbk2IfxTx2Rx16 Class Version: ',self.stRfVers) 

    # DOXYGEN ------------------------------------------------------
    #> @brief Set attribute of class object
    #>
    #> Sets different attributes of the class object
    #>
    #> @param[in]     stSel: String to select attribute
    #> 
    #> @param[in]     Val: value of the attribute (optional); can be a string or a number  
    #>  
    #> Supported parameters  
    #>      -   <span style="color: #ff9900;"> 'TxPwrAll': </span> TxPwr with PaControl <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode    
    #>      -   <span style="color: #ff9900;"> 'Tx1Pwr': </span> TxPwr with PaControl for Tx1 <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode    
    #>      -   <span style="color: #ff9900;"> 'Tx2Pwr': </span> TxPwr with PaControl for Tx2 <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode    
    #>      -   <span style="color: #ff9900;"> 'Tx3Pwr': </span> TxPwr with PaControl for Tx3 <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode    
    #>      -   <span style="color: #ff9900;"> 'Tx4Pwr': </span> TxPwr with PaControl for Tx4 <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode         
    #>      -   <span style="color: #ff9900;"> 'Tx5Pwr': </span> TxPwr with PaControl for Tx5 <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode          
    #>      -   <span style="color: #ff9900;"> 'Tx4Pwr': </span> TxPwr with PaControl for Tx6 <br>
    #>          TxPwr 0..255: Control of TX output power in TxSeq mode          
    def     RfSet(self,*varargin):
        if len(varargin) > 0:
            stVal = varargin[0] 
            if stVal == 'Tx1Pwr':
                self.Rf_Rpn7720_Pwr1 = varargin[1] % 64
            elif stVal == 'Tx2Pwr':
                self.Rf_Rpn7720_Pwr2 = varargin[1] % 64                      
            elif stVal == 'TxPwrAll':
                self.Rf_Rpn7720_Pwr1 = varargin[1] % 64
                self.Rf_Rpn7720_Pwr2 = varargin[1] % 64  

    # DOXYGEN ------------------------------------------------------
    #> @brief Get attribute of class object
    #>
    #> Reads back different attributs of the object
    #>
    #> @param[in]   stSel: String to select attribute
    #> 
    #> @return      Val: value of the attribute (optional); can be a string or a number  
    #>  
    #> Supported parameters  
    #>      -   <span style="color: #ff9900;"> 'TxPosn': </span> Positions of transmit anntennas in m <br>
    #>      -   <span style="color: #ff9900;"> 'RxPosn': </span> Positions of receive antennas in m <br>
    #>      -   <span style="color: #ff9900;"> 'ChnDelay': </span> Channel delay shifts<br>
    #>      -   <span style="color: #ff9900;"> 'B': </span> bandwidth of frequency chirp <br>
    #>      -   <span style="color: #ff9900;"> 'kf': </span>  Slope of frequency ramp
    #>      -   <span style="color: #ff9900;"> 'kfUp': </span> Slope of frequency ramp upchirp <br>
    #>      -   <span style="color: #ff9900;"> 'kfDo': </span> Slope of frequency ramp downchirp <br>
    #>      -   <span style="color: #ff9900;"> 'fc': </span> Center frequency <br>
    #>        
    #> e.g. Read Tx-Positions
    #>   @code
    #>      Brd = Rbk2IfxTx2Rx16( )
    #>      
    #>      Brd.RfGet('TxPosn')
    #>              
    #>   @endcode  
    def     RfGet(self, *varargin):
        if len(varargin) > 0:
            stVal = varargin[0]
            if stVal == 'TxGain':
                Ret = ones(2)*16.5
            elif stVal == 'RxGain':
                Ret = ones(16)*14.2
            elif stVal == 'TxPosn':
                Ret = asarray([-42.114, -12.864])*1e-3
            elif stVal == 'RxPosn':
                Ret = linspace(0,15,16)*1.948e-3
            elif stVal == 'B':
                Ret = self.Rf_fStop - self.Rf_fStrt
            elif stVal == 'kf':
                Ret = (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
            elif stVal == 'kfUp':
                Ret = (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
            elif stVal == 'kfDo':
                Ret = (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampDo
            elif stVal == 'fc':
                Ret = (self.Rf_fStop + self.Rf_fStrt)/2
            else:
                Ret = []
        return Ret
    
    # DOXYGEN ------------------------------------------------------
    #> @brief Enable Receive chips
    #>
    #> Function is not used in L-class; receivers are enabled by
    #> default; configuration of receiver is performed in FPGA
    #>           
    def     RfRxEna(self):
        dCfg = dict()
        dCfg['Mask'] = self.Rf_Rrn7745_Cfg1_Mask
        dCfg['Tst_I'] = self.Rf_Rrn7745_Cfg1_Tst_I
        dCfg['Tst_Q'] = self.Rf_Rrn7745_Cfg1_Tst_Q
        dCfg['Lo_I'] = self.Rf_Rrn7745_Cfg1_Lo_I
        dCfg['Lo_Q'] = self.Rf_Rrn7745_Cfg1_Lo_Q
        dCfg['Ena_Mix'] = self.Rf_Rrn7745_Cfg1_Ena_Mix
        dCfg['Mux'] = self.Rf_Rrn7745_Cfg1_Mux
        dCfg['Dc1'] = self.Rf_Rrn7745_Cfg1_Dc1
        dCfg['Dc2'] = self.Rf_Rrn7745_Cfg1_Dc2
        dCfg['Dc3'] = self.Rf_Rrn7745_Cfg1_Dc3
        dCfg['Dc4'] = self.Rf_Rrn7745_Cfg1_Dc4
        self.RfRrn7745Ini(dCfg)

        dCfg = dict()
        dCfg['Mask'] = self.Rf_Rrn7745_Cfg2_Mask
        dCfg['Tst_I'] = self.Rf_Rrn7745_Cfg2_Tst_I
        dCfg['Tst_Q'] = self.Rf_Rrn7745_Cfg2_Tst_Q
        dCfg['Lo_I'] = self.Rf_Rrn7745_Cfg2_Lo_I
        dCfg['Lo_Q'] = self.Rf_Rrn7745_Cfg2_Lo_Q
        dCfg['Ena_Mix'] = self.Rf_Rrn7745_Cfg2_Ena_Mix
        dCfg['Mux'] = self.Rf_Rrn7745_Cfg2_Mux
        dCfg['Dc1'] = self.Rf_Rrn7745_Cfg2_Dc1
        dCfg['Dc2'] = self.Rf_Rrn7745_Cfg2_Dc2
        dCfg['Dc3'] = self.Rf_Rrn7745_Cfg2_Dc3
        dCfg['Dc4'] = self.Rf_Rrn7745_Cfg2_Dc4
        self.RfRrn7745Ini(dCfg)

        dCfg = dict()
        dCfg['Mask'] = self.Rf_Rrn7745_Cfg3_Mask
        dCfg['Tst_I'] = self.Rf_Rrn7745_Cfg3_Tst_I
        dCfg['Tst_Q'] = self.Rf_Rrn7745_Cfg3_Tst_Q
        dCfg['Lo_I'] = self.Rf_Rrn7745_Cfg3_Lo_I
        dCfg['Lo_Q'] = self.Rf_Rrn7745_Cfg3_Lo_Q
        dCfg['Ena_Mix'] = self.Rf_Rrn7745_Cfg3_Ena_Mix
        dCfg['Mux'] = self.Rf_Rrn7745_Cfg3_Mux
        dCfg['Dc1'] = self.Rf_Rrn7745_Cfg3_Dc1
        dCfg['Dc2'] = self.Rf_Rrn7745_Cfg3_Dc2
        dCfg['Dc3'] = self.Rf_Rrn7745_Cfg3_Dc3
        dCfg['Dc4'] = self.Rf_Rrn7745_Cfg3_Dc4
        self.RfRrn7745Ini(dCfg)    

        dCfg = dict()
        dCfg['Mask'] = self.Rf_Rrn7745_Cfg4_Mask
        dCfg['Tst_I'] = self.Rf_Rrn7745_Cfg4_Tst_I
        dCfg['Tst_Q'] = self.Rf_Rrn7745_Cfg4_Tst_Q
        dCfg['Lo_I'] = self.Rf_Rrn7745_Cfg4_Lo_I
        dCfg['Lo_Q'] = self.Rf_Rrn7745_Cfg4_Lo_Q
        dCfg['Ena_Mix'] = self.Rf_Rrn7745_Cfg4_Ena_Mix
        dCfg['Mux'] = self.Rf_Rrn7745_Cfg4_Mux
        dCfg['Dc1'] = self.Rf_Rrn7745_Cfg4_Dc1
        dCfg['Dc2'] = self.Rf_Rrn7745_Cfg4_Dc2
        dCfg['Dc3'] = self.Rf_Rrn7745_Cfg4_Dc3
        dCfg['Dc4'] = self.Rf_Rrn7745_Cfg4_Dc4
        self.RfRrn7745Ini(dCfg)                

    # DOXYGEN ------------------------------------------------------
    #> @brief Display RF chip status
    #>
    #> Display status of RF chips
    def     BrdDispSts(self):
        Val = self.Fpga_GetRfChipSts(1)

        if len(Val) > 2:
            print('RF UID = ', hex(Val[0]))
            print('RF RevNr = ', self.RevStr(Val[1]))
            print('RF SerialNr = ', hex(Val[2]))
            print('RF Date = ', Val[3])
            print('RF Startup = ', Val[4])
            print('--------------------')
            print('RCC = ',hex(Val[5]), hex(Val[6]))
            print('DPA1 = ',hex(Val[7]), hex(Val[8]))
            print('MRX1 = ',hex(Val[9]), hex(Val[10]))
            print('MRX2 = ',hex(Val[11]), hex(Val[12]))
            print('MRX3 = ',hex(Val[13]), hex(Val[14]))
            print('MRX4 = ',hex(Val[15]), hex(Val[16]))
        
    # DOXYGEN ------------------------------------------------------
    #> @brief Enable transmit antenna static
    #>
    #> Set static setup for tx antenna and power
    #> 
    #> @param[in] TxChn: Transmit antenna to activate 0-6; 0->all off
    #>
    #> @param[in] TxPwr: Output power setting 0..255 (register setting for tranmitter)
    #>                  - 255 maximum output power 
    def     RfTxEna(self, TxChn, TxPwr):
        TxChn = TxChn % 3
        TxPwr = TxPwr % 64
        
        dCfg1 = dict()
        if TxChn == 0:
           dCfg1['Mask'] = self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain'] = self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1'] = 0
           dCfg1['Pa2'] = 0
           dCfg1['PaCon'] = 0
           dCfg1['Mux'] = self.Rf_Rpn7720Cfg1_Mux                        
        elif TxChn == 1:
           dCfg1['Mask'] = self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain'] = self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1'] = TxPwr
           dCfg1['Pa2'] = 0
           dCfg1['PaCon'] = self.RPN7720_REG_PACON_MUX_P1
           dCfg1['Mux'] = self.Rf_Rpn7720Cfg1_Mux    
        elif TxChn == 2:
           dCfg1['Mask'] = self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain'] = self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1'] = 0
           dCfg1['Pa2'] = TxPwr
           dCfg1['PaCon'] = self.RPN7720_REG_PACON_MUX_P2
           dCfg1['Mux'] = self.Rf_Rpn7720Cfg1_Mux
        else:   
           dCfg1['Mask'] = self.Rf_Rpn7720Cfg1_Mask;
           dCfg1['LoChain'] = self.Rf_Rpn7720Cfg1_LoChain;
           dCfg1['Pa1'] = 0;
           dCfg1['Pa2'] = 0;
           dCfg1['PaCon'] = 0;
           dCfg1['Mux'] = self.Rf_Rpn7720Cfg1_Mux; 
                                     
        self.Rf_Rpn7720Cfg1_Mask = dCfg1['Mask'];
        self.Rf_Rpn7720Cfg1_LoChain = dCfg1['LoChain'];
        self.Rf_Rpn7720Cfg1_Pa1 = dCfg1['Pa1'];
        self.Rf_Rpn7720Cfg1_Pa2 = dCfg1['Pa2'];
        self.Rf_Rpn7720Cfg1_PaCon = dCfg1['PaCon'];
        self.Rf_Rpn7720Cfg1_Mux = dCfg1['Mux'];
        self.RfRpn7720Ini(dCfg1)
        
    def Fpga_DispBrdInf(self):          
        print(' ');
        print('-------------------------------------------------------------------')
        print('Radarbook2: Board Information')
        Val = self.Fpga_GetBrdInf()
        if len(Val) > 2:
            Temp = Val[2] - 273;
            print('UID = ',Val[1], Val[0])
            print('Temp = ',Temp, 'deg')
            print('Temp Rf = ',Val[3],' deg')
            print('RF1 Vcc = ',Val[4]/100,' V')
            print('RF1 Icc = ',Val[5]/100,' A')
         
        else:
            print('Board does not respond!')
        print('-------------------------------------------------------------------')
        return Val


    def     RfTxPaEna(self, TxPwr):
        TxPwr = TxPwr % 64
        dCfg1 = dict()
        dCfg1['Mask'] = self.Rf_Rpn7720Cfg1_Mask
        dCfg1['LoChain'] = self.Rf_Rpn7720Cfg1_LoChain
        dCfg1['Pa1'] = TxPwr
        dCfg1['Pa2'] = TxPwr
        dCfg1['PaCon'] = 2*16+1
        dCfg1['Mux'] = self.Rf_Rpn7720Cfg1_Mux
          
        self.Rf_Rpn7720Cfg1_Mask = dCfg1['Mask']
        self.Rf_Rpn7720Cfg1_LoChain = dCfg1['LoChain']
        self.Rf_Rpn7720Cfg1_Pa1 = dCfg1['Pa1']
        self.Rf_Rpn7720Cfg1_Pa2 = dCfg1['Pa2']
        self.Rf_Rpn7720Cfg1_PaCon = dCfg1['PaCon']
        self.Rf_Rpn7720Cfg1_Mux = dCfg1['Mux']
        
        self.RfRpn7720Ini(dCfg1)
                
    # DOXYGEN ------------------------------------------------------
    #> @brief Set Actual Ramp Parameters
    #>
    #> Set static setup for tx antenna and power
    #> 
    #> @param[in] Cfg: Configuration structure
    def     SetActRampParams(self, dCfg):
        nStop = round(dCfg['fStop']/40e6*(2**16))
        nStrt = round(dCfg['fStrt']/40e6*(2**16))
        nStep = round(abs(nStop - nStrt)/(40e6*dCfg['TRampUp'] - 1))
        TRampAct = ceil(abs(nStop - nStrt)/nStep + 1)*25e-9    
        self.Rf_fStrt = nStrt/(2**16)*40e6
        self.Rf_fStop = nStop/(2**16)*40e6
        self.Rf_TRampUp = TRampAct
        nStep = round(abs(nStop - nStrt)/(40e6*dCfg['TRampDo'] - 1))
        TRampAct = ceil(abs(nStop - nStrt)/nStep + 1)*25e-9                           
        self.Rf_TRampDo = TRampAct      
 
    # DOXYGEN ------------------------------------------------------
    #> @brief RfMeasurement modes
    #>
    #> Set timing and ramp configuration for the mode
    #> 
    #> @param[in] stSel: String to select predefined mode
    #>
    #> @param[in] Cfg: Structure to configure measurement mode   
    #>      -   <span style="color: #ff9900;"> 'ExtTrigUp': </span> FMCW measurement mode with uniform timing <br>
    #>          -   dCfg['fStrt']       Start frequency in Hz (mandatory)
    #>          -   dCfg['fStop']       Stop frequency in Hz (mandatory)
    #>          -   dCfg['TRampUp']     Upchirp ramp duration (mandatory)
    #>          -   dCfg['TRampDo']     Downchirp ramp duration (mandatory)
    #>          -   dCfg['NrFrms']      Number of measured Upchirps 
    #>          -   dCfg['N']           Desired number of samples N (mandatory)
    #>          -   dCfg['IniEve']      Enable disable trigger event after start phase: (default 1)
    #>                              If set to 0, measurement is started automatically
    #>                              If set to 1, Fpga_SeqTrigExtEve starts the measurement    
    #>          -   dCfg['IniTim']      Time duration of ini phase in s (default 2ms)
    #>                              Can be helpful to delay measurements if initialization takes longer (e.g large USB data frames)
    #>          -   dCfg['CfgTim']      Duration for reconfiguration of PLL (default 50us)
    #>          -   dCfg['ExtEve']      Wait for external event after measurement frame (default 0)
    #>                              If set to 1, Fpga_SeqTrigExtEve must be called to initiate next measurement
    #>          -   dCfg['Start']       Enable disable start of timing in FPGA
    #>          
    #>      -   <span style="color: #ff9900;"> 'ExtTrigUpNp': </span> FMCW measurement mode with NP uniform chirps (sequence) <br>
    #>          -   dCfg['fStrt']       Start frequency in Hz (mandatory)
    #>          -   dCfg['fStop']       Stop frequency in Hz (mandatory)
    #>          -   dCfg['TRampUp']     Upchirp ramp duration (mandatory)
    #>          -   dCfg['TRampDo']     Downchirp ramp duration (mandatory)
    #>          -   dCfg['NrFrms']      Number of sequences (one sequence consists of Np chirps)
    #>          -   dCfg['N']           Desired number of samples N (mandatory)
    #>          -   dCfg['Np']          Number of subsequent frames Np (mandatory)
    #>          -   dCfg['Tp']          Chirp repetition interval (mandatory)
    #>          -   dCfg['TInt']        Interval between adjacent sequencies      
    #>          -   dCfg['IniEve']      Enable disable trigger event after start phase: (default 1)
    #>                              If set to 0, measurement is started automatically
    #>                              If set to 1, Fpga_SeqTrigExtEve starts the measurement    
    #>          -   dCfg['IniTim']      Time duration of ini phase in s (default 2ms)
    #>                              Can be helpful to delay measurements if initialization takes longer (e.g large USB data frames)
    #>          -   dCfg['CfgTim']      Duration for reconfiguration of PLL (default 50us)
    #>          -   dCfg['ExtEve']      Wait for external event after a sequence (default 0)
    #>                              If set to 1, Fpga_SeqTrigExtEve must be called to initiate next measurement sequence (Np frames)
    #>          -   dCfg['Start']       Enable disable start of timing in FPGA                
    def     RfMeas(self, *varargin):
        if len(varargin) > 1:
            stMod = varargin[0]

            if stMod == 'ExtTrigUp':

                print('Simple Measurement Mode: ExtTrigUp');
                self.RfRst()
                self.Rcc1010.SmartIni('ExtTrigMux2')
                dCfg = varargin[1]
                  
                if not ('fStrt' in dCfg):
                    print('RfMeas: fStrt not specified!')
                    traceback.print_exc()
                if not ('fStop' in dCfg):
                    print('RfMeas: fStop not specified!')
                    traceback.print_exc()
                if not ('TRampUp' in dCfg):
                    print('RfMeas: TRampUp not specified!')
                    traceback.print_exc()
                if not ('TRampDo' in dCfg):
                    print('RfMeas: TRampDo not specified!')
                    traceback.print_exc()
                if not ('N' in dCfg):
                    print('RfMeas: N not specified!')
                    traceback.print_exc()
                if not ('TInt' in dCfg):
                    print('RfMeas: TInt not specified!')
                    traceback.print_exc()

                dCfg = self.ChkMeasCfg(dCfg)
                
                self.SetActRampParams(dCfg)
                # Programm Memory
                lRampCfg = list()
                dRampCfg = dict()
                dRampCfg['fStrt'] = dCfg['fStrt']
                dRampCfg['fStop'] = dCfg['fStop']
                dRampCfg['TRamp'] = dCfg['TRampUp']
                lRampCfg.append(dRampCfg)
                dRampCfg = dict()
                dRampCfg['fStrt'] = dCfg['fStop']
                dRampCfg['fStop'] = dCfg['fStrt']
                dRampCfg['TRamp'] = dCfg['TRampDo']
                lRampCfg.append(dRampCfg)
                
                self.Rcc1010.ProgRampMemory(int('0x1000',0), lRampCfg)
                
                # Execute Processing Cals;
                self.Rcc1010.DevProcCall("SetModRun")
                self.Rcc1010.DevProcCall("InitBasic")
                self.Rcc1010.DevProcCall("OutputStaticFrequency", (dCfg["fStrt"] + dCfg["fStop"])/2)
                self.Rcc1010.DevProcCall("SetTxReg",1, int('11001111',2))
                self.Rcc1010.DevProcCall("SetTxReg",2, int('11001111',2))
                self.Rcc1010.DevProcCall("SetTxReg",3, int('11001111',2))
                self.Rcc1010.DevProcCall("StartCoarseTuneCalibration")
                self.Rcc1010.DevProcCall("StartFQMCalibration")

                # Calculate Sampling Rate
                N = dCfg['N']
                IniCic = 1
                if 'IniCic' in dCfg:
                    if dCfg['IniCic'] == 0:
                        IniCic = 0

                if IniCic > 0:
                    Ts = dCfg['TRampUp']/N
                    fs = 1/Ts
                    fAdc = self.Get('fAdc') 
                    Div = floor(fAdc/fs)
                    if Div < 1:
                        Div = 1
                    print('  fAdc:  ', (fAdc/1e6), ' MHz')
                    print('  CicR:  ', (Div), ' ')
                    print('  TSamp: ', (N/(fAdc/Div)/1e-6), ' us')                      
                    # Configure CIC Filter 
                    self.CfgCicFilt(Div)

                self.Set('N', N)

                self.Fpga_MimoSeqRst()
                self.Fpga_MimoSeqNrEntries(1)

                Regs = self.Rcc1010.GetRegsProcCallExtTrig(int('0x1000',0), 2, 1, 0)
                self.Fpga_MimoSeqSetCrocRegs(0, Regs)
                
                self.Rad_FrmCtrlCfg_RegChnCtrl = self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA;    
                self.BrdSampIni()

                # Programm Timing to Board: Nios is used to initialize
                # pattern
                IniEve = 0
                if 'IniEve' in dCfg:
                    IniEve = dCfg['IniEve']
                IniTim = 0.2e-3
                if 'IniTim' in dCfg:
                    IniTim = dCfg['IniTim']
                CfgTim = 60e-6
                if 'CfgTim' in dCfg:
                    CfgTim = dCfg['CfgTim']
                if CfgTim < 30e-6:
                    CfgTim = 30e-6
                    print('RCC1010 configuration time set to 30 us')

                MeasEve = 0
                if 'ExtEve' in dCfg:
                    MeasEve = dCfg['ExtEve']
                    if dCfg['ExtEve'] > 0:
                        dCfg['MeasTim']     = dCfg['TRampUp'] + dCfg['TRampDo'] + 60e-6   

                if dCfg['TInt'] < dCfg['TRampUp'] + dCfg['TRampDo'] + CfgTim + 1e-6:
                    dCfg['TInt'] = dCfg['TRampUp'] + dCfg['TRampDo'] + CfgTim + 1e-6
                    print('TInt to short; set to ', (dCfg['TInt']/1e-6), ' us')
                
                dTimCfg = dict()
                dTimCfg['IniEve'] = IniEve                         #   Use ExtEve after Ini phase
                dTimCfg['IniTim'] = IniTim                         #   Duration of Ini phase in us 
                dTimCfg['CfgTim'] = CfgTim                         #   Configuration: Configure RCC for ExtTrig 
                dTimCfg['MeasEve'] = MeasEve                        #   Use ExtEve after meas phase
                dTimCfg['MeasTim'] = dCfg['TInt'] - dTimCfg['CfgTim']      

                # TODO Set Timing 
                self.BrdSetTim_RccM1PW(dTimCfg)
                    
                self.Setfs();
                self.SetFuSca(); 
                self.Computation.SetParam('fStrt',   dCfg['fStrt']);
                self.Computation.SetParam('fStop',   dCfg['fStop']);
                self.Computation.SetParam('TRampUp', dCfg['TRampUp']); 
                
                if 'Strt' in dCfg:
                    if dCfg['Strt'] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()

            elif stMod == 'Cw':
                if self.cDebugInf > 0:
                    print('Simple Measurement Mode: Cw')
            
                self.RfRst()
                self.Rcc1010.SmartIni('ExtTrigMux2')
                dCfg = varargin[1]

                if not ('fCenter' in dCfg):
                    print('RfMeas: fCenter not specified!')
                    traceback.print_exc()

                if not ('TMeas' in dCfg):
                    print('RfMeas: TMeas not specified!')
                    traceback.print_exc()

                if not ('NrFrms' in dCfg):
                    print('RfMeas: NrFrms not specified!')
                    traceback.print_exc()
                   
                if not ('N' in dCfg):
                    print('RfMeas: N not specified!')
                    traceback.print_exc()
                
                if not ('TInt' in dCfg):
                    print('RfMeas: TInt not specified!')
                    traceback.print_exc()
                

                dCfg = self.ChkMeasCfg(dCfg)
                

                self.Rf_fStrt = dCfg['fCenter']
                self.Rf_fStop = dCfg['fCenter']
                self.Rf_TRampUp = dCfg['TMeas']
                self.Rf_TRampDo = 0
                
                self.Rcc1010.DevProcCall("SetModRun")
                self.Rcc1010.DevProcCall("InitBasic")
                self.Rcc1010.DevProcCall("OutputStaticFrequency", dCfg['fCenter'])
                self.Rcc1010.DevProcCall("SetTxReg",1, int('11001111',2))
                self.Rcc1010.DevProcCall("SetTxReg",2, int('11001111',2))
                self.Rcc1010.DevProcCall("SetTxReg",3, int('11001111',2))
                self.Rcc1010.DevProcCall("StartCoarseTuneCalibration")
                self.Rcc1010.DevProcCall("StartFQMCalibration")    
                self.Rcc1010.DevProcCall("OutputStaticFrequency", dCfg['fCenter'])            
                
                # Calculate Sampling Rate
                N = dCfg['N']
                IniCic = 1
                if ('IniCic' in dCfg):
                    if dCfg['IniCic'] == 0:
                        IniCic = 0

                if IniCic > 0:
                    Ts = dCfg['TMeas']/N
                    fs = 1/Ts
                    fAdc = self.Get('fAdc') 
                    Div = floor(fAdc/fs)
                    if Div < 1:
                        Div = 1

                    if self.cDebugInf > 0: 
                        print('  fAdc:  ', (fAdc/1e6), ' MHz')
                        print('  CicR:  ', (Div), ' ')
                        print('  TSamp: ', (N/(fAdc/Div)/1e-6), ' us')  
                                        
                    # Configure CIC Filter 
                    self.CfgCicFilt(Div)

                self.Set('N', N)

                self.Fpga_MimoSeqRst()

                self.Rad_FrmCtrlCfg_RegChnCtrl = self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA    
                self.BrdSampIni()

                # Programm Timing to Board: Nios is used to initialize
                # pattern
                
                if dCfg['TInt'] < dCfg['TMeas'] + 1e-6:
                    dCfg['TInt'] = dCfg['TMeas'] + 1e-6
                    print('TInt to short; set to ', (dCfg['TInt']/1e-6), ' us')
                


                # TODO Set Timing 
                self.BrdSetTimCont('ContUnifM1', dCfg['TInt']);
                
                self.Setfs();
                self.SetFuSca(); 
                
                
                if ('Strt' in dCfg):
                    if dCfg['Strt'] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                    
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()
             
                              
            elif stMod == 'RccMs':
                print('RCC being Master and Power Control with ')
                lRampCfg = varargin[1]
                dCfg = varargin[2] 
                self.RfRst()
                # Initialize Transceivers and Receivers
                self.RfRxEna()
                if 'TxPwr' in dCfg:
                    self.TxPwr = dCfg['TxPwr']
                self.RfTxPaEna(self.TxPwr)
                self.Rcc1010.SmartIni('ExtTrigMux2PaCtrl')
                
                if not ('NLoop' in dCfg):
                    dCfg['NLoop'] = 1
                
                dCfg = self.ChkMeasCfg(dCfg)

                if isinstance(lRampCfg,list):
                    self.SetActRampParams(dCfg)
                    # Configure Ramp Memory with P0 - P4 to set transmit antenna
                    # [P4,P3,P2,P1,P0] -> used to control Dpa signals
                    # 0: all Tx off
                    # 1: Tx1
                    # 2: Tx2 ...
                    
                    self.Rcc1010.ProgRampMemory(int('0x1000',0), lRampCfg)

                    nSet = len(lRampCfg)

                    TRamp = self.Rcc1010.GetRampSeqDuration(lRampCfg)
                    TInt = dCfg['TInt']
                    

                    if (TInt + 0.1e-3) < TRamp*dCfg['NLoop']:
                        TInt = TRamp*dCfg['NLoop'] + 0.1e-3
                        print('Increase Repition')

                    # Execute Processing Cals;
                    self.Rcc1010.DevProcCall("SetModRun")
                    self.Rcc1010.DevProcCall("InitBasic")
                    self.Rcc1010.DevProcCall("OutputStaticFrequency", (dCfg["fStrt"] + dCfg["fStop"])/2)
                    self.Rcc1010.DevProcCall("SetTxReg",1, int('11101111',2))
                    self.Rcc1010.DevProcCall("SetTxReg",2, int('11101111',2))
                    self.Rcc1010.DevProcCall("SetTxReg",3, int('11101111',2))
                    self.Rcc1010.DevProcCall("StartCoarseTuneCalibration")
                    self.Rcc1010.DevProcCall("StartFQMCalibration")

                    # Calculate Sampling Rate
                    N = dCfg['N']
                    IniCic = 1
                    if 'IniCic' in dCfg:
                        if dCfg['IniCic'] == 0:
                            IniCic = 0
                    
                    if IniCic > 0:
                        Ts = dCfg['TRampUp']/N
                        fs = 1/Ts
                        fAdc = self.Get('fAdc') 
                        Div = floor(fAdc/fs)
                        if Div < 1:
                            Div = 1
                        print('  fAdc:  ', (fAdc/1e6), ' MHz')
                        print('  CicR:  ', (Div), ' ')
                        print('  TSamp: ', (N/(fAdc/Div)/1e-6), ' us')                      
                        # Configure CIC Filter 
                        self.CfgCicFilt(Div)
                    self.Set('N', N)

                    self.Fpga_MimoSeqRst()
                    self.Fpga_MimoSeqNrEntries(1)
                    Regs = self.Rcc1010.GetRegsProcCallExtTrig(int('0x1000',0), nSet, dCfg['NLoop'], 0)
                    self.Fpga_MimoSeqSetCrocRegs(0, Regs)

                    if self.Gps > 0:
                        print("Enable Padding")
                        self.Rad_FrmCtrlCfg_RegChnCtrl = self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA + self.cFRMCTRL_REG_CH0CTRL_PADENA    
                    else:
                        self.Rad_FrmCtrlCfg_RegChnCtrl = self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA     
                    self.BrdSampIni()

                    # Use External events to synchronize boards to
                    # master timing
                    if (self.Rad_Role >= self.cRAD_ROLE_SL):
                        dCfg['IniEve'] = 1
                        dCfg['ExtEve'] = 1
                        print('Set Role Slave')
                
                    # Programm Timing to Board: Nios is used to initialize
                    # pattern
                    IniEve = 1
                    if 'IniEve' in dCfg:
                        IniEve = dCfg['IniEve']
                    IniTim = 0.2e-3
                    if 'IniTim' in dCfg:
                        IniTim = dCfg['IniTim']
                    CfgTim = 60e-6
                    if 'CfgTim' in dCfg:
                        CfgTim = dCfg['CfgTim']
                    if CfgTim < 30e-6:
                        CfgTim = 30e-6
                        print('RCC1010 configuration time set to 30 us')

                    MeasEve = 0
                    if 'ExtEve' in dCfg:
                        MeasEve = dCfg['ExtEve']
                    if  TInt < TRamp*dCfg['NLoop'] + CfgTim:
                        TInt = TRamp*dCfg['NLoop'] + CfgTim
                        print('TInt to short; increase to ', TInt, ' us')

                    dTimCfg = dict()

                    dTimCfg['MeasEveN'] = 1
                    if (self.Rad_Role == self.RAD_ROLE_SL):
                        TInt = TInt - 10e-6
                    elif (self.Rad_Role == self.RAD_ROLE_INTGPS):
                        if 'ExtEveNMeas' in dCfg:
                            dTimCfg['MeasEveN'] = dCfg['ExtEveNMeas']
                            dTimCfg['MeasTimAct'] = TRamp*dCfg['NLoop'] + CfgTim;  
                        
                    
                    dTimCfg['IniEve'] = IniEve                          #   Use ExtEve after Ini phase
                    dTimCfg['IniTim'] = IniTim                          #   Duration of Ini phase in us 
                    dTimCfg['CfgTim'] = CfgTim                          #   Configuration: Configure RCC for ExtTrig 
                    dTimCfg['MeasEve'] = MeasEve                         #   Use ExtEve after meas phase
                    dTimCfg['MeasTim'] = TInt - dTimCfg['CfgTim']       

                    # TODO Set Timing 
                    self.BrdSetTim_RccM1PW_Ms(dTimCfg)
                        
                    self.Setfs();
                    self.SetFuSca(); 
                    self.Computation.SetParam('Tp', dCfg['TInt']);
                    self.Computation.SetParam('Np', dCfg['NLoop']);
                    self.Computation.SetParam('fStrt',   dCfg['fStrt']);
                    self.Computation.SetParam('fStop',   dCfg['fStop']);
                    self.Computation.SetParam('TRampUp', dCfg['TRampUp']); 
                    
                    if 'Strt' in dCfg:
                        if dCfg['Strt'] > 0:
                            self.BrdAccessData()
                            self.BrdSampStrt()
                    else:
                        self.BrdAccessData()                        
                        self.BrdSampStrt()     

            else:
                print("Measurement Mode not known")

    # DOXYGEN ------------------------------------------------------
    #> @brief Display last chirp configuration
    #>    
    def     RfDispCfg(self):
        print('Rf Cfg')
        print('  fStrt:    ', (self.Rf_fStrt/1e9),' GHz')
        print('  fStop:    ', (self.Rf_fStop/1e9),' GHz')
        print('  TUp  :    ', (self.Rf_TRampUp/1e-6),' us')
        print('  TDown:    ', (self.Rf_TRampDo/1e-6),' us')

    def     RfRrn7745Ini(self, *varargin):
        if len(varargin) > 0:
            dCfg = varargin[0]
        else:
            dCfg = dict()
            dCfg['Mask'] = self.Rf_Rrn7745_Cfg1_Mask
            dCfg['Tst_I'] = self.Rf_Rrn7745_Cfg1_Tst_I
            dCfg['Tst_Q'] = self.Rf_Rrn7745_Cfg1_Tst_Q
            dCfg['Lo_I'] = self.Rf_Rrn7745_Cfg1_Lo_I
            dCfg['Lo_Q'] = self.Rf_Rrn7745_Cfg1_Lo_Q
            dCfg['Ena_Mix'] = self.Rf_Rrn7745_Cfg1_Ena_Mix
            dCfg['Mux'] = self.Rf_Rrn7745_Cfg1_Mux
            dCfg['Dc1'] = self.Rf_Rrn7745_Cfg1_Dc1
            dCfg['Dc2'] = self.Rf_Rrn7745_Cfg1_Dc2
            dCfg['Dc3'] = self.Rf_Rrn7745_Cfg1_Dc3
            dCfg['Dc4'] = self.Rf_Rrn7745_Cfg1_Dc4             
        if self.cDebugInf > 1:
            print('IFRX Rf_Init')
        self.SetRrn7745(dCfg)
    
    def     RfRrn7745GetReg(self, Mask, Adr):
        Adr = Adr % 2**14
        Val = [];
        if DebugInf > 1:
            print('IFRX Regs Ini')
        Val = self.Fpga_GetIfrxReg(Mask, Adr)
        return Ret
        

    def     RfRst(self):
        self.Rcc1010.DevRst()
    
   

    def     RfRpn7720Ini(self, *varargin):
        if len(varargin) > 0:
            dCfg = varargin[0]
        else:
            dCfg['Mask'] = self.Rf_Rpn7720Cfg1_Mask
            dCfg['LoChain'] = self.Rf_Rpn7720Cfg1_LoChain
            dCfg['Pa1'] = self.Rf_Rpn7720Cfg1_Pa1
            dCfg['Pa2'] = self.Rf_Rpn7720Cfg1_Pa2
            dCfg['PaCon'] = self.Rf_Rpn7720Cfg1_PaCon
            dCfg['Mux'] = self.Rf_Rpn7720Cfg1_Mux                 
        if self.cDebugInf > 1:
            print('IFTX Rf_Init')
        self.SetRpn7720(dCfg)

    def     SetRpn7720(self, dCfg):
        Data = []
        # Programm LoChain
        Data = Data + [ (2**15) + (2**14) + 0*(2**8) + (dCfg['LoChain'] % 256)]              
        # Programm Pa1
        Data = Data + [ (2**15) + (2**14) + 1*(2**8) + (dCfg['Pa1'] % 256)]
        # Programm Pa2
        Data = Data + [ (2**15) + (2**14) + 2*(2**8) + (dCfg['Pa2'] % 256)]
        # Programm PaCon
        Data = Data + [ (2**15) + (2**14) + 4*(2**8) + (dCfg['PaCon'] % 256)]
        # Programm Mux
        Data = Data + [ (2**15) + (2**14) + 5*(2**8) + (dCfg['Mux'] % 256)]
        Ret = self.Fpga_SetIfTxReg(dCfg['Mask'], asarray(uint32(Data)))            
        return Ret

    def     Fpga_SetPaCtrl(self, Mask, Strt, Reg):
        if len(Reg) > 28:
            Reg = Reg[0:28]
        Cod = int('0x9215',0)
        FpgaCmd = asarray([Mask, 1 , Strt])
        FpgaCmd = append(FpgaCmd, Reg)
        Ret = self.CmdSend(0,Cod,FpgaCmd)
        Ret = self.CmdRecv()
        return Ret

    def     Fpga_GetDpaReg(self, Mask, Reg):
        Cod = int('0x9205',0)
        FpgaCmd = asarray([Mask, 2 , Reg])
        Ret = self.CmdSend(0,Cod,FpgaCmd)
        Ret = self.CmdRecv()
        return Ret


    def     Fpga_SetIfTxReg(self, Mask, Reg):
        Cod = int('0x9205',0)
        FpgaCmd = asarray([Mask, 1])
        FpgaCmd = append(FpgaCmd, asarray(Reg))
        Ret = self.CmdSend(0, Cod, FpgaCmd)
        Ret = self.CmdRecv()
        return Ret

    def     Fpga_GetIfTxReg(self, Mask, Reg):
        Cod = int('0x9205',0)
        FpgaCmd = asarray([Mask, 2])
        FpgaCmd = append(FpgaCmd, asarray(Reg))        
        Ret = self.CmdSend(0, Cod, FpgaCmd)
        Ret = self.CmdRecv()
        return Ret

    def     Fpga_SetIfrxReg(self, Mask, Reg):
        Cod = int('0x9206',0)
        FpgaCmd = asarray([Mask, 1]) 
        FpgaCmd = append(FpgaCmd, asarray(Reg)) 
        Ret = self.CmdSend(0, Cod, FpgaCmd)
        Ret = self.CmdRecv()
        return Ret

    def     Fpga_GetIfrxReg(self, Mask, Reg):
        Cod = int('0x9206',0)
        FpgaCmd = asarray([Mask, 2])
        FpgaCmd = append(FpgaCmd, asarray(Reg))
        Ret = self.CmdSend(0,Cod,FpgaCmd)
        Ret = self.CmdRecv()
        return Ret

    def     SetRrn7745(self, dCfg):
        # Programm Tst_I
        Data = [(2**15) + (2**14) + 32*(2**8) + (dCfg['Tst_I'] % 256)]
        # Programm Tst_Q
        Data.append( (2**15) + (2**14) + 33*(2**8) + (dCfg['Tst_Q'] % 256))
        # Programm Lo_I
        Data.append( (2**15) + (2**14) + 34*(2**8) + (dCfg['Lo_I'] % 256))               
        # Programm Lo_Q
        Data.append( (2**15) + (2**14) + 35*(2**8) + (dCfg['Lo_Q'] % 256))               
        # Programm Ena_Mix
        Data.append( (2**15) + (2**14) + 36*(2**8) + (dCfg['Ena_Mix'] % 256))            
        # Programm Mux
        Data.append( (2**15) + (2**14) + 37*(2**8) + (dCfg['Mux'] % 256))               
        # Programm DC1
        Data.append( (2**15) + (2**14) + 40*(2**8) + (dCfg['Dc1'] % 256))            
        # Programm DC2
        Data.append( (2**15) + (2**14) + 41*(2**8) + (dCfg['Dc2'] % 256))                
        # Programm DC3
        Data.append( (2**15) + (2**14) + 42*(2**8) + (dCfg['Dc3'] % 256))           
        # Programm DC4
        Data.append( (2**15) + (2**14) + 43*(2**8) + (dCfg['Dc4'] % 256))              
        Ret = self.Fpga_SetIfrxReg(dCfg['Mask'], asarray(uint32(Data)))
        return Ret
    
    def     RfRcc1010_GetRegsRampScenarioExtTrig(self, Adr, NSet, NLoop, ExitCfg):
        if Adr < int('0x1000',0):
            Adr = uint32('0x1000',0)
        if Adr > int('0x7FF0',0):
            Adr = uint32('0x1000',0)
        NSet = uint32(NSet % 1792)
        NLoop = uint32(NLoop % (2**16))
        ExitCfg = uint32(ExitCfg % (2**16))

        Data = asarray([Adr, NSet, NLoop])
        Regs = append(self.RCC1010_CallCode_StartRampScenarioExtTrig, Data)
        Regs = append(Regs, ExitCfg)     
        Regs = Regs + self.RCC1010_Reg_ProcessingCall_Adr*(2**16) + (2**31) 
        return Regs
                
    # DOXYGEN ------------------------------------------------------
    #> @brief Configure CIC filter for clock divider
    #>
    #> Configure CIC filter: Filter transfer function is adjusted to sampling rate divider
    #> 
    #> @param[in] Div: 
    def     CfgCicFilt(self, Div):
        if Div >= 16:
            self.Set('CicEna')                         
            self.Set('CicR', Div)
            self.Set('CicDelay', 16)
        elif Div >= 8:
            self.Set('CicEna')                        
            self.Set('CicR',Div)
            self.Set('CicDelay',8)
        elif Div >= 4:
            self.Set('CicEna')                         
            self.Set('CicR',Div)
            self.Set('CicDelay',4)
        elif Div >= 2:    
            self.Set('CicEna')                           
            self.Set('CicR',Div)
            self.Set('CicDelay',2)
        else:
            self.Set('CicDi')       
  
    # DOXYGEN ------------------------------------------------------
    #> @brief Check measurement configuration 
    #> 
    #> Check measurement configuration structure
    #> 
    #> @param[in] Cfg: 
    def     ChkMeasCfg(self, dCfg):
        if 'IniEve' in dCfg:
            IniEve = floor(dCfg['IniEve'])
            IniEve = (IniEve % 2)
            if IniEve != dCfg['IniEve']:
                print('Rbk2IfxTx2Rx16: IniEve set to ', (IniEve))
            dCfg['IniEve'] = IniEve
        
        if 'ExtEve' in dCfg:
            ExtEve = floor(dCfg['ExtEve'])
            ExtEve = (ExtEve % 2)
            if ExtEve != dCfg['ExtEve']:
                print('Rbk2IfxTx2Rx16: ExtEve set to ', (ExtEve))
            dCfg['ExtEve'] = ExtEve
                      
        if 'N' in dCfg:
            N = ceil(dCfg['N']/8)*8
            if (N != dCfg['N']):
                print('Rbk2IfxTx2Rx16: N must be a mulitple of 8 -> Set N to ', N)
            if N > 4096:
                N = 4096
                print('Rbk2IfxTx2Rx16: N to large -> Set N to ', N)
            dCfg['N'] = N
            if  N < 8:
                N = 8
                print('Rbk2IfxTx2Rx16: N to small -> Set N to ', N)

        # Check number of repetitions: standard timing modes can only can be used with 256 repttions
        # Np must be greater or equal to 1 and less or equal than 256
        if 'Np' in dCfg:
            Np = ceil(dCfg['Np'])
            if Np < 1: 
                Np = 1
            if Np > 256:
                Np = 256
            if Np != dCfg['Np']:
                print('Rbk2IfxTx2Rx16: Np -> Set Np to ', Np)
            dCfg['Np'] = Np

        # Check number of frames: at least one frame must be measured
        #if 'NrFrms' in dCfg:
        #    dCfg['NrFrms'] = ceil(dCfg['NrFrms'])
        #    if dCfg['NrFrms'] < 1:
        #        dCfg['NrFrms'] = 1
        #        print('Rbk2IfxTx2Rx16: NrFrms < 1 -> Set to 1')
        
        # Initialization time (used to generate dummy frame and reset signal processing chain and data interface)
        if 'IniTim' in dCfg:
            IniEve = 1
            if 'IniEve' in dCfg:
                IniEve = dCfg['IniEve']
            # If external event is programmed after init, a too long ini time can result that the event is missed
            if (IniEve > 0) and (dCfg['IniTim'] > 5e-3):
                print('Rbk2IfxTx2Rx16: Trigger Event could be missed (Meas does not start)')

        # Tx Field: SeqTrig MMP < 2.0.0 support 16 entries in the sequence table:
        if 'TxSeq' in dCfg:
            TxSeq = dCfg['TxSeq']
            NSeq = len(TxSeq)
            if NSeq > 16:
                print('Rbk2IfxTx2Rx16: TxSeq to long -> limit to 16')    
                TxSeq = TxSeq[1:16]
            if NSeq < 1:
                TxSeq = 0
                print('Rbk2IfxTx2Rx16: TxSeq empty -> Set to 0')  
            dCfg['TxSeq'] = TxSeq

        return dCfg

    def     BrdSetTim_RccM1PW(self, dCfg):
        fSeqTrig = self.Rad_fAdc;
        Seq = SeqTrig.SeqTrig(fSeqTrig)

        print('BrdSetTim_RccM1PW')
        SeqTrigCfg = dict()
        SeqTrigCfg['Mask'] = 1;
        SeqTrigCfg['Ctrl'] = Seq.SEQTRIG_REG_CTRL_IRQ2ENA; # Enable interrupt event on channel 2 
        SeqTrigCfg['ChnEna'] = Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA;
        SeqTrigCfg['Seq'] = list()

        # Phase 0: Ini with dummy frame: (lSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1);
        if dCfg['IniEve'] > 0:
            lSeq = Seq.IniSeq('IniExt', dCfg['IniTim'])    
        else:
            lSeq = Seq.IniSeq('Ini', dCfg['IniTim'])     
        # Phase 1: Cfg: Generate Irq:
        lSeq = Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 2, 0)
        # Phase 2: Meas 
        if dCfg['MeasEve'] > 0:
            lSeq = Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTim'], 1, 0)
        else:
            lSeq = Seq.AddSeq(lSeq,'RccMeas', dCfg['MeasTim'], 1, 0)
        SeqTrigCfg['Seq'] = lSeq

        self.SeqCfg = SeqTrigCfg

        self.Fpga_SeqTrigRst(self.SeqCfg['Mask'])
        NSeq = len(self.SeqCfg['Seq'])
        print('Run SeqTrig: ', NSeq, ' Entries')
    
        for Idx in range(0,NSeq):
            self.Fpga_SeqTrigCfgSeq(self.SeqCfg['Mask'],Idx, self.SeqCfg['Seq'][Idx])


    def     BrdSetTim_RccM1PW_Ms(self, dCfg):
        fSeqTrig = self.Rad_fAdc;
        Seq = SeqTrig.SeqTrig(fSeqTrig)
        
        print('BrdSetTim_RccM1PW_Ms')
        SeqTrigCfg = dict()
        SeqTrigCfg['Mask'] = 1
        SeqTrigCfg['Ctrl'] = Seq.SEQTRIG_REG_CTRL_IRQ2ENA  # Enable interrupt event on channel 2 
        SeqTrigCfg['ChnEna'] = Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA + Seq.SEQTRIG_REG_CTRL_CH3ENA
        SeqTrigCfg['Seq'] = list()

        if dCfg['MeasEveN'] > 1:
            # in this mode the board is configured as slave
            if dCfg['IniEve'] > 0:
                lSeq = Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6)
                lSeq = Seq.AddSeq(lSeq, 'WaitEve', 10e-6, 2, 0)
                lSeq[-1]['Chn3Cfg'] = 2**30
            else:
                lSeq = Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6)
                lSeq = Seq.AddSeq(lSeq, 'Wait', 10e-6, 2, 0)
                lSeq[-1]['Chn3Cfg'] = 2**30
            
            # Phase 1: Cfg: Generate Irq:
            lSeq = Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 3, 0)                                 #2
            # Set input trigger to external input event
            lSeq[-1]['Chn3Cfg'] = 2**30 + 2**31 
            lSeq = Seq.AddSeq(lSeq,'RccMeasN', dCfg['MeasTim'], 2, 4, dCfg['MeasEveN'] - 1, 0)      #3
            lSeq[-1]['Chn3Cfg'] = 2**30 + 2**31 
            lSeq = Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 5, 0)                                 #4
            lSeq[-1]['Chn3Cfg'] = 2**30 + 2**31
            lSeq = Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTimAct'], 2, 0)                         #5
            lSeq[-1]['Chn3Cfg'] = 2**30 + 2**31

        else:
            # Phase 0: Ini with dummy frame: (lSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1);
            if dCfg['IniEve'] > 0:
                lSeq = Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6)
                lSeq = Seq.AddSeq(lSeq, 'WaitEve', 10e-6, 2, 0)
                if self.Rad_Role >= self.cRAD_ROLE_SL:
                    # Set input trigger to external input event
                    lSeq[-1]['Chn3Cfg'] = 2**30             
            else:
                lSeq = Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6) 
                lSeq = Seq.AddSeq(lSeq, 'Wait', 10e-6, 2, 0)
                if self.Rad_Role >= self.cRAD_ROLE_SL:
                    # Set input trigger to external input event
                    lSeq[-1]['Chn3Cfg'] = 2**30

            # Phase 1: Cfg: Generate Irq:
            lSeq = Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 3, 0)
            if self.Rad_Role >= self.cRAD_ROLE_SL:
                # Set input trigger to external input event
                lSeq[-1]['Chn3Cfg'] = 2**30 + 2**31  
            else:
                lSeq[-1]['Chn3Cfg'] = 2**31

            # Phase 2: Meas 
            if dCfg['MeasEve'] > 0:
                lSeq = Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTim'], 2, 0)
            else:
                lSeq = Seq.AddSeq(lSeq,'RccMeas', dCfg['MeasTim'], 2, 0)     
            if self.Rad_Role >= self.cRAD_ROLE_SL:
                # Set input trigger to external input event
                lSeq[-1]['Chn3Cfg'] = 2**30 + 2**31  
            else:
                lSeq[-1]['Chn3Cfg'] = 2**31


        SeqTrigCfg['Seq'] = lSeq

        self.SeqCfg = SeqTrigCfg

        self.Fpga_SeqTrigRst(self.SeqCfg['Mask'])
        NSeq = len(self.SeqCfg['Seq'])
        print('Run SeqTrig: ', (NSeq), ' Entries')
        for Idx in range(0,NSeq):
             self.Fpga_SeqTrigCfgSeq(self.SeqCfg['Mask'], Idx, self.SeqCfg['Seq'][Idx])









    def     BrdSetTim_RccM1PW_MsIniStop(self, dCfg):
        fSeqTrig = self.Rad_fAdc;
        Seq = SeqTrig.SeqTrig(fSeqTrig)
        print('BrdSetTim_RccM1PW_MsIniStop')
        SeqTrigCfg = dict()
        SeqTrigCfg['Mask'] = 1
        SeqTrigCfg['Ctrl'] = Seq.SEQTRIG_REG_CTRL_IRQ2ENA                                        # Enable interrupt event on channel 2 
        SeqTrigCfg['ChnEna'] = Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA
        SeqTrigCfg['Seq'] = list()

        # Phase 0: Ini with dummy frame: (lSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1);
        if dCfg['IniEve'] > 0:
            lSeq = Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6)
            lSeq = Seq.AddSeq(lSeq, 'WaitEve', 10e-6, 2, 0)
        else:
            lSeq = Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6) 
            lSeq = Seq.AddSeq(lSeq, 'Wait', 10e-6, 2, 0)    
        # Phase 1: Cfg: Generate Irq:
        lSeq = Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 3, 0)
        lSeq[2]['Chn3Cfg'] = (2**31)
        # Phase 2: Meas
        # stay in this phase for ever loop back to itselfe 
        if dCfg['MeasEve'] > 0:
            lSeq = Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTim'], 4, 0)
        else:
            lSeq = Seq.AddSeq(lSeq,'RccMeas', dCfg['MeasTim'], 4, 0)     
        lSeq[3]['Chn3Cfg'] = (2**31)
        if dCfg['MeasEve'] > 0:
            lSeq = Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTim'], 4, 0)
        else:
            lSeq = Seq.AddSeq(lSeq,'RccMeas', dCfg['MeasTim'], 4, 0)     
        lSeq[4]['Chn3Cfg'] = (2**31)        

        SeqTrigCfg['Seq'] = lSeq

        self.SeqCfg = SeqTrigCfg

        self.Fpga_SeqTrigRst(self.SeqCfg['Mask'])
        NSeq = len(self.SeqCfg['Seq'])
        print('Run SeqTrig: ', (NSeq), ' Entries')
        for Idx in range(0,NSeq):
             self.Fpga_SeqTrigCfgSeq(self.SeqCfg['Mask'], Idx, self.SeqCfg['Seq'][Idx])

