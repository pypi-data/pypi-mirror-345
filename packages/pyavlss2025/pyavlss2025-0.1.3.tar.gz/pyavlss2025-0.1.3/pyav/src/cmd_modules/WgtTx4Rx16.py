# RadarNode -- Class for 77-GHz Radar with 77 GHz IFX chips
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import  Libraries.src.cmd_modules.Rbk2 as Rbk2
import  Libraries.src.cmd_modules.DevRcc1010  as DevRcc1010
import  Libraries.src.cmd_modules.DevRrn7745  as DevRrn7745
import  Libraries.src.cmd_modules.SeqTrig     as SeqTrig

from    numpy import *
import  numpy.matlib

class WgtTx4Rx16(Rbk2.Rbk2):
    """ WgtTx4Rx16 class object:
        (c) Haderer Andreas Inras GmbH
    """

    RxWgtLen = array([157.669469,
                      141.669469,
                      121.669469,
                      105.669469,
                      85.669469,
                      69.669469,
                      49.669469,
                      33.669469,
                      33.669469,
                      49.669469,
                      69.669469,
                      85.669469,
                      105.669469,
                      121.669469,
                      141.669469,
                      157.669469])*1e-3
    TxWgtLen = array([122.419469,
                      44.919469,
                      44.919469,
                      122.419469])*1e-3
    Wgta = 3.1e-3
    RCor = 0.22

    def __init__(self, stConType, stIpAdr):
        super(WgtTx4Rx16, self).__init__(stConType, stIpAdr)

        self.Rf_fStrt               =   76e9
        self.Rf_fStop               =   77e9
        self.Rf_TRampUp             =   256e-6
        self.Rf_TRampDo             =   256e-6

        #------------------------------------------------------------------
        # Define flags of Rpn7720 registers
        #------------------------------------------------------------------
        self.RPN7720_REG_PACON_MUX_P1                   =   3
        self.RPN7720_REG_PACON_MUX_P2                   =   3*16

        self.PaCtrl_TxOff                               =   0
        self.PaCtrl_Tx1                                 =   2
        self.PaCtrl_Tx2                                 =   4
        self.PaCtrl_Tx3                                 =   8
        self.PaCtrl_Tx4                                 =   16
        self.TxPwr                                      =   60

        #------------------------------------------------------------------
        # RPN7720
        #   Cfg1:   TX1 and TX2
        #   Cfg2:   TX3 and TX4
        #   Cfg3:   LO Buffer
        #------------------------------------------------------------------
        self.Rf_Rpn7720Cfg1_Mask                        =   1
        self.Rf_Rpn7720Cfg1_LoChain                     =   int('01111111',2)
        self.Rf_Rpn7720Cfg1_Pa1                         =   0
        self.Rf_Rpn7720Cfg1_Pa2                         =   0
        self.Rf_Rpn7720Cfg1_PaCon                       =   0
        self.Rf_Rpn7720Cfg1_Mux                         =   int('10000',2)

        self.Rf_Rpn7720Cfg2_Mask                        =   2
        self.Rf_Rpn7720Cfg2_LoChain                     =   int('01111111',2)
        self.Rf_Rpn7720Cfg2_Pa1                         =   0
        self.Rf_Rpn7720Cfg2_Pa2                         =   0
        self.Rf_Rpn7720Cfg2_PaCon                       =   0
        self.Rf_Rpn7720Cfg2_Mux                         =   int('10000',2)

        #--------------------------------------------------------------------------
        # Static RX Rrn7745 configuration
        #--------------------------------------------------------------------------
        # RX 1
        self.Rf_Rrn7745_Cfg1_Mask                       =   1
        self.Rf_Rrn7745_Cfg1_Tst_I                      =   int('10000000', 2)
        self.Rf_Rrn7745_Cfg1_Tst_Q                      =   int('10000000', 2)
        self.Rf_Rrn7745_Cfg1_Lo_I                       =   int('00000000', 2)
        self.Rf_Rrn7745_Cfg1_Lo_Q                       =   int('10000000', 2)
        self.Rf_Rrn7745_Cfg1_Ena_Mix                    =   2 + 4 + 8 + 16 + 32 + 64 + 128
        self.Rf_Rrn7745_Cfg1_Mux                        =   0
        self.Rf_Rrn7745_Cfg1_Dc1                        =   4*32
        self.Rf_Rrn7745_Cfg1_Dc2                        =   4*32
        self.Rf_Rrn7745_Cfg1_Dc3                        =   4*32
        self.Rf_Rrn7745_Cfg1_Dc4                        =   4*32

        # Rx 2
        self.Rf_Rrn7745_Cfg2_Mask                       =   2
        self.Rf_Rrn7745_Cfg2_Tst_I                      =   int('10000000', 2)
        self.Rf_Rrn7745_Cfg2_Tst_Q                      =   int('10000000', 2)
        self.Rf_Rrn7745_Cfg2_Lo_I                       =   int('00000000', 2)
        self.Rf_Rrn7745_Cfg2_Lo_Q                       =   int('10000000', 2)
        self.Rf_Rrn7745_Cfg2_Ena_Mix                    =   2 + 4 + 8 + 16 + 32 + 64 + 128
        self.Rf_Rrn7745_Cfg2_Mux                        =   0
        self.Rf_Rrn7745_Cfg2_Dc1                        =   4*32
        self.Rf_Rrn7745_Cfg2_Dc2                        =   4*32
        self.Rf_Rrn7745_Cfg2_Dc3                        =   4*32
        self.Rf_Rrn7745_Cfg2_Dc4                        =   4*32

        # Init RCC1010 Device
        self.Rcc1010                =   DevRcc1010.DevRcc1010(self, 1)

        self.SampSeq                =   int('000001',2)

        self.Rad_ArmMemCfg_WaitLev  =   32768/4 - 1024
        self.Rad_ArmMemCfg_FifoSiz  =   32768/4

        self.Set('NrChn',16)


    def BrdDispSts(self):
        #   @function       Get
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Disp status of RF board
        self.BrdDispInf()
        self.Fpga_DispRfChipSts(1)

    def RfSet(self, *varargin):
        if len(varargin):
            if isinstance(varargin[0], str):
                print("Rbkii77Tx4Rx16::RfSet string")
                pass
            elif isinstance(varargin[0], dict):
                print("Rbkii77Tx4Rx16::RfSet dict")
                pass
            else:
                print("Rbkii77Tx4Rx16::RfSet parameter not recognized")

    def RfGet(self, *varargin):
        #   @function       RfGet
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Get Parameters of Radar Frontend
        #   @paramin[in]    stSelect: String to select parameter to change
        #
        #                   Known stSelect Parameter Strings:
        #                       TxPosn:    Position of Tx Antennas
        if len(varargin) > 0:
            stVal = varargin[0]
            if stVal == 'TxPosn':
                Ret = (arange(4) - 1.5)*94e-3
            elif stVal == 'TxPosn_X':
                Ret = (arange(4) - 1.5)*94e-3
            elif stVal == 'TxPosn_Y':
                Ret = ones((4,))*30e-3
            elif stVal == 'RxPosn':
                Ret = (arange(15) - 7.5)*23.5e-3
            elif stVal == 'RxPosn_X':
                Ret = (arange(15) - 7.5)*23.5e-3
            elif stVal == 'RxPosn_Y':
                Ret = zeros((15,))
            elif stVal == 'RxWgtLen':
                Ret = self.RxWgtLen
            elif stVal == 'TxWgtLen':
                Ret = self.TxWgtLen
            elif stVal == 'B':
                Ret     =   self.Rf_fStop - self.Rf_fStrt
            elif stVal == 'kf':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
            elif stVal == 'kfUp':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
            elif stVal == 'kfDo':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampDo
            elif stVal == 'fc':
                Ret     =   (self.Rf_fStop + self.Rf_fStrt)/2
        return -1


    # DOXYGEN ------------------------------------------------------
    #> @brief Enable Receive chips
    #>
    #> Function is not used in L-class; receivers are enabled by
    #> default; configuration of receiver is performed in FPGA
    #>
    def     RfRxEna(self):
        dCfg                =   dict()
        dCfg['Mask']        =   self.Rf_Rrn7745_Cfg1_Mask
        dCfg['Tst_I']       =   self.Rf_Rrn7745_Cfg1_Tst_I
        dCfg['Tst_Q']       =   self.Rf_Rrn7745_Cfg1_Tst_Q
        dCfg['Lo_I']        =   self.Rf_Rrn7745_Cfg1_Lo_I
        dCfg['Lo_Q']        =   self.Rf_Rrn7745_Cfg1_Lo_Q
        dCfg['Ena_Mix']     =   self.Rf_Rrn7745_Cfg1_Ena_Mix
        dCfg['Mux']         =   self.Rf_Rrn7745_Cfg1_Mux
        dCfg['Dc1']         =   self.Rf_Rrn7745_Cfg1_Dc1
        dCfg['Dc2']         =   self.Rf_Rrn7745_Cfg1_Dc2
        dCfg['Dc3']         =   self.Rf_Rrn7745_Cfg1_Dc3
        dCfg['Dc4']         =   self.Rf_Rrn7745_Cfg1_Dc4
        self.RfRrn7745Ini(dCfg)

        dCfg                =   dict()
        dCfg['Mask']        =   self.Rf_Rrn7745_Cfg2_Mask
        dCfg['Tst_I']       =   self.Rf_Rrn7745_Cfg2_Tst_I
        dCfg['Tst_Q']       =   self.Rf_Rrn7745_Cfg2_Tst_Q
        dCfg['Lo_I']        =   self.Rf_Rrn7745_Cfg2_Lo_I
        dCfg['Lo_Q']        =   self.Rf_Rrn7745_Cfg2_Lo_Q
        dCfg['Ena_Mix']     =   self.Rf_Rrn7745_Cfg2_Ena_Mix
        dCfg['Mux']         =   self.Rf_Rrn7745_Cfg2_Mux
        dCfg['Dc1']         =   self.Rf_Rrn7745_Cfg2_Dc1
        dCfg['Dc2']         =   self.Rf_Rrn7745_Cfg2_Dc2
        dCfg['Dc3']         =   self.Rf_Rrn7745_Cfg2_Dc3
        dCfg['Dc4']         =   self.Rf_Rrn7745_Cfg2_Dc4
        self.RfRrn7745Ini(dCfg)


    def RfRxDi(self):
        pass

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
        TxChn   =   TxChn % 5
        TxPwr   =   TxPwr % 64

        dCfg1                   =       dict()
        dCfg2                   =       dict()

        if TxChn == 0:
           dCfg1['Mask']        =       self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain']     =       self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1']         =       0
           dCfg1['Pa2']         =       0
           dCfg1['PaCon']       =       0
           dCfg1['Mux']         =       self.Rf_Rpn7720Cfg1_Mux

           dCfg2['Mask']        =       self.Rf_Rpn7720Cfg2_Mask
           dCfg2['LoChain']     =       self.Rf_Rpn7720Cfg2_LoChain
           dCfg2['Pa1']         =       0
           dCfg2['Pa2']         =       0
           dCfg2['PaCon']       =       0
           dCfg2['Mux']         =       self.Rf_Rpn7720Cfg2_Mux

        elif TxChn == 1:
           dCfg1['Mask']        =       self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain']     =       self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1']         =       TxPwr
           dCfg1['Pa2']         =       0
           dCfg1['PaCon']       =       self.RPN7720_REG_PACON_MUX_P1
           dCfg1['Mux']         =       self.Rf_Rpn7720Cfg1_Mux

           dCfg2['Mask']        =       self.Rf_Rpn7720Cfg2_Mask
           dCfg2['LoChain']     =       self.Rf_Rpn7720Cfg2_LoChain
           dCfg2['Pa1']         =       0
           dCfg2['Pa2']         =       0
           dCfg2['PaCon']       =       0
           dCfg2['Mux']         =       self.Rf_Rpn7720Cfg2_Mux

        elif TxChn == 2:
           dCfg1['Mask']        =       self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain']     =       self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1']         =       0
           dCfg1['Pa2']         =       TxPwr
           dCfg1['PaCon']       =       self.RPN7720_REG_PACON_MUX_P2
           dCfg1['Mux']         =       self.Rf_Rpn7720Cfg1_Mux

           dCfg2['Mask']        =       self.Rf_Rpn7720Cfg2_Mask
           dCfg2['LoChain']     =       self.Rf_Rpn7720Cfg2_LoChain
           dCfg2['Pa1']         =       0
           dCfg2['Pa2']         =       0
           dCfg2['PaCon']       =       0
           dCfg2['Mux']         =       self.Rf_Rpn7720Cfg2_Mux

        elif TxChn == 3:
           dCfg1['Mask']        =       self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain']     =       self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1']         =       0
           dCfg1['Pa2']         =       0
           dCfg1['PaCon']       =       0
           dCfg1['Mux']         =       self.Rf_Rpn7720Cfg1_Mux

           dCfg2['Mask']        =       self.Rf_Rpn7720Cfg2_Mask
           dCfg2['LoChain']     =       self.Rf_Rpn7720Cfg2_LoChain
           dCfg2['Pa1']         =       TxPwr
           dCfg2['Pa2']         =       0
           dCfg2['PaCon']       =       self.RPN7720_REG_PACON_MUX_P1
           dCfg2['Mux']         =       self.Rf_Rpn7720Cfg2_Mux

        elif TxChn == 4:

           dCfg1['Mask']        =       self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain']     =       self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1']         =       0
           dCfg1['Pa2']         =       0
           dCfg1['PaCon']       =       0
           dCfg1['Mux']         =       self.Rf_Rpn7720Cfg1_Mux

           dCfg2['Mask']        =       self.Rf_Rpn7720Cfg2_Mask
           dCfg2['LoChain']     =       self.Rf_Rpn7720Cfg2_LoChain
           dCfg2['Pa1']         =       0
           dCfg2['Pa2']         =       TxPwr
           dCfg2['PaCon']       =       self.RPN7720_REG_PACON_MUX_P2
           dCfg2['Mux']         =       self.Rf_Rpn7720Cfg2_Mux

        else:

           dCfg1['Mask']        =       self.Rf_Rpn7720Cfg1_Mask
           dCfg1['LoChain']     =       self.Rf_Rpn7720Cfg1_LoChain
           dCfg1['Pa1']         =       0
           dCfg1['Pa2']         =       0
           dCfg1['PaCon']       =       0
           dCfg1['Mux']         =       self.Rf_Rpn7720Cfg1_Mux

           dCfg2['Mask']        =       self.Rf_Rpn7720Cfg2_Mask
           dCfg2['LoChain']     =       self.Rf_Rpn7720Cfg2_LoChain
           dCfg2['Pa1']         =       0
           dCfg2['Pa2']         =       0
           dCfg2['PaCon']       =       0
           dCfg2['Mux']         =       self.Rf_Rpn7720Cfg2_Mux

        self.Rf_Rpn7720Cfg1_Mask             =   dCfg1['Mask']
        self.Rf_Rpn7720Cfg1_LoChain          =   dCfg1['LoChain']
        self.Rf_Rpn7720Cfg1_Pa1              =   dCfg1['Pa1']
        self.Rf_Rpn7720Cfg1_Pa2              =   dCfg1['Pa2']
        self.Rf_Rpn7720Cfg1_PaCon            =   dCfg1['PaCon']
        self.Rf_Rpn7720Cfg1_Mux              =   dCfg1['Mux']

        self.Rf_Rpn7720Cfg2_Mask             =   dCfg2['Mask']
        self.Rf_Rpn7720Cfg2_LoChain          =   dCfg2['LoChain']
        self.Rf_Rpn7720Cfg2_Pa1              =   dCfg2['Pa1']
        self.Rf_Rpn7720Cfg2_Pa2              =   dCfg2['Pa2']
        self.Rf_Rpn7720Cfg2_PaCon            =   dCfg2['PaCon']
        self.Rf_Rpn7720Cfg2_Mux              =   dCfg2['Mux']

        self.RfRpn7720Ini(dCfg1)
        self.RfRpn7720Ini(dCfg2)


    def RfRst(self):
        #   @function       RfRst
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Reset RF transceivers: reset RCC, -> transmitter do not require reset
        self.Rcc1010.DevRst()

    def RfDispCfg(self):
        #   @function       RfDispCfg
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Disp RF configuration
        print('Rf Cfg')
        print('  fStrt:    ', self.Rf_fStrt/1e9,' GHz')
        print('  fStop:    ', self.Rf_fStop/1e9,' GHz')
        print('  TUp  :    ', self.Rf_TRampUp/1e-6,' us')
        print('  TDown:    ', self.Rf_TRampDo/1e-6,' us')



    def     IoBrdGetTemp(self):
        FpgaCmd         =   zeros(1,dtype='uint32')
        Cod             =   int('0x9407',0)
        FpgaCmd[0]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        print(Ret)
        if Ret[0]:
            Ret         =   Ret[1]
            if Ret > 2**31:
                Ret     =   Ret - 2**32
            Ret         =   Ret/10000

        return Ret

    # DOXYGEN ------------------------------------------------------
    #> @brief Set Actual Ramp Parameters
    #>
    #> Set static setup for tx antenna and power
    #>
    #> @param[in] Cfg: Configuration structure
    def     SetActRampParams(self, dCfg):
        nStop               =   round(dCfg['fStop']/40e6*(2**16))
        nStrt               =   round(dCfg['fStrt']/40e6*(2**16))
        nStep               =   round(abs(nStop - nStrt)/(40e6*dCfg['TRampUp'] - 1))
        TRampAct            =   ceil(abs(nStop - nStrt)/nStep + 1)*25e-9
        self.Rf_fStrt       =   nStrt/(2**16)*40e6
        self.Rf_fStop       =   nStop/(2**16)*40e6
        self.Rf_TRampUp     =   TRampAct
        nStep               =   round(abs(nStop - nStrt)/(40e6*dCfg['TRampDo'] - 1))
        TRampAct            =   ceil(abs(nStop - nStrt)/nStep + 1)*25e-9
        self.Rf_TRampDo     =   TRampAct

    def RfMeas(self, *varargin):

        if len(varargin) > 1:
            stMod       =   varargin[0]

            if stMod == 'ExtTrigUp':

                print('Simple Measurement Mode: ExtTrigUp')
                self.RfRst()
                self.Rcc1010.SmartIni('ExtTrigMux2')
                dCfg     =   varargin[1]

                if not ('fStrt' in dCfg):
                    print('RfMeas: fStrt not specified!')
                if not ('fStop' in dCfg):
                    print('RfMeas: fStop not specified!')
                if not ('TRampUp' in dCfg):
                    print('RfMeas: TRampUp not specified!')
                if not ('TRampDo' in dCfg):
                    print('RfMeas: TRampDo not specified!')
                if not ('NrFrms' in dCfg):
                    print('RfMeas: NrFrms not specified!')
                if not ('N' in dCfg):
                    print('RfMeas: N not specified!')
                if not ('TInt' in dCfg):
                    print('RfMeas: TInt not specified!')

                dCfg            =   self.ChkMeasCfg(dCfg)

                #Programm Memory
                dRampCfg1           =   {
                                            "fStrt"     :   dCfg["fStrt"],
                                            "fStop"     :   dCfg["fStop"],
                                            "TRamp"     :   dCfg["TRampUp"]
                                        }
                lRampCfg            =   [dRampCfg1]
                #Use different names: d is inserted as pointer !!!!
                dRampCfg2           =   {
                                            "fStrt"     :   dCfg["fStop"],
                                            "fStop"     :   dCfg["fStrt"],
                                            "TRamp"     :   dCfg["TRampDo"]
                                        }
                lRampCfg.append(dRampCfg2)

                self.Rcc1010.ProgRampMemory(int('0x1000',0), lRampCfg)
                self.SetActRampParams(dCfg)

                # Execute Processing Cals
                self.Rcc1010.DevProcCall("SetModRun")
                self.Rcc1010.DevProcCall("InitBasic")
                self.Rcc1010.DevProcCall("OutputStaticFrequency", (dCfg["fStrt"] + dCfg["fStop"])/2)
                self.Rcc1010.DevProcCall("SetTxReg",1, int('11001111',2))
                self.Rcc1010.DevProcCall("SetTxReg",2, int('11001111',2))
                self.Rcc1010.DevProcCall("SetTxReg",3, int('11001111',2))
                self.Rcc1010.DevProcCall("StartCoarseTuneCalibration")
                self.Rcc1010.DevProcCall("StartFQMCalibration")

                # Calculate Sampling Rate
                N       =   dCfg['N']
                if N > 4096 - 128:
                    N   =   4096 -128
                IniCic  =   1
                if 'IniCic' in dCfg:
                    if dCfg['IniCic'] == 0:
                        IniCic  =   0

                if IniCic > 0:
                    Ts      =   dCfg['TRampUp']/N
                    fs      =   1/Ts
                    fAdc    =   self.Get('fAdc')
                    Div     =   floor(fAdc/fs)
                    if Div < 1:
                        Div     = 1
                    print('  fAdc:  ', (fAdc/1e6), ' MHz')
                    print('  CicR:  ', (Div), ' ')
                    print('  TSamp: ', (N/(fAdc/Div)/1e-6), ' us')
                    # Configure CIC Filter
                    self.CfgCicFilt(Div)

                self.Set('N', N)

                self.Fpga_MimoSeqRst()
                self.Fpga_MimoSeqNrEntries(1)

                Regs    =   self.Rcc1010.GetRegsProcCallExtTrig(int('0x1000',0), 2, 1, 0)
                self.Fpga_MimoSeqSetCrocRegs(0, Regs)

                self.Rad_FrmCtrlCfg_RegChnCtrl   =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA
                self.BrdSampIni()

                # Programm Timing to Board: Nios is used to initialize
                # pattern
                IniEve          =   1
                if 'IniEve' in dCfg:
                    IniEve  =   dCfg['IniEve']
                IniTim          =   0.5e-3
                if 'IniTim' in dCfg:
                    IniTim  =   dCfg['IniTim']
                CfgTim          =   40e-6
                if 'CfgTim' in dCfg:
                    CfgTim      =   dCfg['CfgTim']
                MeasEve         =   0
                if 'ExtEve' in dCfg:
                    MeasEve     =   dCfg['ExtEve']
                    if dCfg['ExtEve'] > 0:
                        dCfg['MeasTim']     = dCfg['TRampUp'] + dCfg['TRampDo'] + 100e-6

                dTimCfg             =   dict()
                dTimCfg['IniEve']   =   IniEve                         #   Use ExtEve after Ini phase
                dTimCfg['IniTim']   =   IniTim                         #   Duration of Ini phase in us
                dTimCfg['CfgTim']   =   CfgTim                         #   Configuration: Configure RCC for ExtTrig
                dTimCfg['MeasEve']  =   MeasEve                        #   Use ExtEve after meas phase
                dTimCfg['MeasTim']  =   dCfg['TInt'] - dTimCfg['CfgTim']

                # TODO Set Timing
                self.BrdSetTim_RccM1PW(dTimCfg)
                if 'Strt' in dCfg:
                    if dCfg['Strt'] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()

            elif stMod == 'RccMs':
                print('RCC being Master and Power Control with ')
                lRampCfg            =   varargin[1]
                dCfg                =   varargin[2]
                self.RfRst()
                # Initialize Transceivers and Receivers
                self.RfRxEna()
                if 'TxPwr' in dCfg:
                    self.TxPwr       =   dCfg['TxPwr']
                self.RfTxPaEna(self.TxPwr)
                self.Rcc1010.SmartIni('ExtTrigMux2PaCtrl')

                if not ('NLoop' in dCfg):
                    dCfg['NLoop']       =   1

                if isinstance(lRampCfg,list):
                    self.SetActRampParams(dCfg)
                    # Configure Ramp Memory with P0 - P4 to set transmit antenna
                    # [P4,P3,P2,P1,P0] -> used to control Dpa signals
                    # 0: all Tx off
                    # 1: Tx1
                    # 2: Tx2 ...

                    self.Rcc1010.ProgRampMemory(int('0x1000',0), lRampCfg)

                    nSet    =   len(lRampCfg)

                    TRamp   =   self.Rcc1010.GetRampSeqDuration(lRampCfg)
                    TInt    =   dCfg['TInt']

                    print("TInt:", TInt)

                    if (TInt + 0.1e-3) < TRamp*dCfg['NLoop']:
                        TInt    =   TRamp*dCfg['NLoop'] + 0.1e-3
                        print('Increase Repition')

                    # Execute Processing Cals
                    self.Rcc1010.DevProcCall("SetModRun")
                    self.Rcc1010.DevProcCall("InitBasic")
                    self.Rcc1010.DevProcCall("OutputStaticFrequency", (dCfg["fStrt"] + dCfg["fStop"])/2)
                    self.Rcc1010.DevProcCall("SetTxReg",1, int('11001111',2))
                    self.Rcc1010.DevProcCall("SetTxReg",2, int('11001111',2))
                    self.Rcc1010.DevProcCall("SetTxReg",3, int('11001111',2))
                    self.Rcc1010.DevProcCall("StartCoarseTuneCalibration")
                    self.Rcc1010.DevProcCall("StartFQMCalibration")

                    # Calculate Sampling Rate
                    N       =   dCfg['N']
                    if N > 4096 - 128:
                        N   =   4096 -128
                    IniCic  =   1
                    if 'IniCic' in dCfg:
                        if dCfg['IniCic'] == 0:
                            IniCic  =   0

                    if IniCic > 0:
                        Ts      =   dCfg['TRampUp']/N
                        fs      =   1/Ts
                        fAdc    =   self.Get('fAdc')
                        Div     =   floor(fAdc/fs)
                        if Div < 1:
                            Div     = 1
                        print('  fAdc:  ', (fAdc/1e6), ' MHz')
                        print('  CicR:  ', (Div), ' ')
                        print('  TSamp: ', (N/(fAdc/Div)/1e-6), ' us')
                        # Configure CIC Filter
                        self.CfgCicFilt(Div)
                    self.Set('N', N)

                    self.Fpga_MimoSeqRst()
                    self.Fpga_MimoSeqNrEntries(1)
                    Regs    =   self.Rcc1010.GetRegsProcCallExtTrig(int('0x1000',0), nSet, dCfg['NLoop'], 0)
                    self.Fpga_MimoSeqSetCrocRegs(0, Regs)

                    self.Rad_FrmCtrlCfg_RegChnCtrl   =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA
                    self.BrdSampIni()

                    # Programm Timing to Board: Nios is used to initialize
                    # pattern
                    IniEve          =   1
                    if 'IniEve' in dCfg:
                        IniEve  =   dCfg['IniEve']
                    IniTim          =   2e-3
                    if 'IniTim' in dCfg:
                        IniTim  =   dCfg['IniTim']
                    CfgTim          =   60e-6
                    if 'CfgTim' in dCfg:
                        CfgTim      =   dCfg['CfgTim']
                    MeasEve         =   0
                    if 'ExtEve' in dCfg:
                        MeasEve     =   dCfg['ExtEve']
                    dTimCfg             =   dict()
                    dTimCfg['IniEve']   =   IniEve                          #   Use ExtEve after Ini phase
                    dTimCfg['IniTim']   =   IniTim                          #   Duration of Ini phase in us
                    dTimCfg['CfgTim']   =   CfgTim                          #   Configuration: Configure RCC for ExtTrig
                    dTimCfg['MeasEve']  =   MeasEve                         #   Use ExtEve after meas phase
                    dTimCfg['MeasTim']  =   TInt - dTimCfg['CfgTim']

                    print("IniEve: ", IniEve)
                    print("IniTim: ", IniTim)
                    # TODO Set Timing
                    self.BrdSetTim_RccM1PW_Ms(dTimCfg)

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
    #> @brief Configure CIC filter for clock divider
    #>
    #> Configure CIC filter: Filter transfer function is adjusted to sampling rate divider
    #>
    #> @param[in] Div:
    def     CfgCicFilt(self, Div):
        if Div >= 16:
            self.Set('CicEna')
            self.Set('CicR', Div)
            self.Set('CicDelay',16)
            self.Set('CicStages',4)
        elif Div >= 8:
            self.Set('CicEna')
            self.Set('CicR', Div)
            self.Set('CicDelay',8)
            self.Set('CicStages',4)
        elif Div >= 4:
            self.Set('CicEna')
            self.Set('CicR',Div)
            self.Set('CicDelay',4)
            self.Set('CicStages',4)
        elif Div >= 2:
            self.Set('CicEna')
            self.Set('CicR', Div)
            self.Set('CicDelay',2)
            self.Set('CicStages',4)
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
            IniEve  =   floor(dCfg['IniEve'])
            IniEve  =   (IniEve % 2)
            if IniEve != dCfg['IniEve']:
                print('Rbkii77Tx4Rx16: IniEve set to ', (IniEve))
            dCfg['IniEve']  =   IniEve

        if 'ExtEve' in dCfg:
            ExtEve  =   floor(dCfg['ExtEve'])
            ExtEve  =   (ExtEve % 2)
            if ExtEve != dCfg['ExtEve']:
                print('Rbkii77Tx4Rx16: ExtEve set to ', (ExtEve))
            dCfg['ExtEve']  =   ExtEve

        if 'N' in dCfg:
            N   =   ceil(dCfg['N']/8)*8
            if (N != dCfg['N']):
                print('Rbkii77Tx4Rx16: N must be a mulitple of 8 -> Set N to ', N)
            if N > 4096 - 128:
                N   =   4096 - 128
                print('Rbkii77Tx4Rx16: N to large -> Set N to ', N)
            dCfg['N']   =   N
            if  N < 8:
                N   =   8
                print('Rbkii77Tx4Rx16: N to small -> Set N to ', N)

        # Check number of repetitions: standard timing modes can only can be used with 256 repttions
        # Np must be greater or equal to 1 and less or equal than 256
        if 'Np' in dCfg:
            Np  =   ceil(dCfg['Np'])
            if Np < 1:
                Np  =   1
            if Np > 256:
                Np  =   256
            if Np != dCfg['Np']:
                print('Rbkii77Tx4Rx16: Np -> Set Np to ', Np)
            dCfg['Np']  =   Np

        # Check number of frames: at least one frame must be measured
        if 'NrFrms' in dCfg:
            dCfg['NrFrms']  =   ceil(dCfg['NrFrms'])
            if dCfg['NrFrms'] < 1:
                dCfg['NrFrms']  =   1
                print('Rbkii77Tx4Rx16: NrFrms < 1 -> Set to 1')

        # Initialization time (used to generate dummy frame and reset signal processing chain and data interface)
        if 'IniTim' in dCfg:
            IniEve  =   1
            if 'IniEve' in dCfg:
                IniEve      =   dCfg['IniEve']
            # If external event is programmed after init, a too long ini time can result that the event is missed
            if (IniEve > 0) and (dCfg['IniTim'] > 5e-3):
                print('Rbkii77Tx4Rx16: Trigger Event could be missed (Meas does not start)')

        # Tx Field: SeqTrig MMP < 2.0.0 support 16 entries in the sequence table:
        if 'TxSeq' in dCfg:
            TxSeq   =   dCfg['TxSeq']
            NSeq    =   len(TxSeq)
            if NSeq > 16:
                print('Rbkii77Tx4Rx16: TxSeq to long -> limit to 16')
                TxSeq   =   TxSeq[1:16]
            if NSeq < 1:
                TxSeq   =   0
                print('Rbkii77Tx4Rx16: TxSeq empty -> Set to 0')
            dCfg['TxSeq']   =   TxSeq

        return dCfg



    def     BrdSetTim_RccM1PW(self, dCfg):
        fSeqTrig                =   100e6
        Seq                     =   SeqTrig.SeqTrig(fSeqTrig)

        print('BrdSetTim_RccM1PW')
        SeqTrigCfg                  =   dict()
        SeqTrigCfg['Mask']          =   1
        SeqTrigCfg['Ctrl']          =   0;                                  # Enable interrupt event on channel 2
        SeqTrigCfg['ChnEna']        =   Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA
        SeqTrigCfg['Seq']           =   list()

        # Phase 0: Ini with dummy frame: (lSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1)
        if dCfg['IniEve'] > 0:
            lSeq                    =   Seq.IniSeq('IniExt', dCfg['IniTim'])
        else:
            lSeq                    =   Seq.IniSeq('Ini', dCfg['IniTim'])
        # Phase 1: Cfg: Generate Irq:
        lSeq                        =   Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 2, 0)
        # Phase 2: Meas
        if dCfg['MeasEve'] > 0:
            lSeq                    =   Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTim'], 1, 0)
        else:
            lSeq                    =   Seq.AddSeq(lSeq,'RccMeas', dCfg['MeasTim'], 1, 0)
        SeqTrigCfg['Seq']           =   lSeq

        self.SeqCfg                 =   SeqTrigCfg

        self.Fpga_SeqTrigRst(self.SeqCfg['Mask'])
        NSeq        =   len(self.SeqCfg['Seq'])
        print('Run SeqTrig: ', NSeq, ' Entries')

        for Idx in range(0,NSeq):
            self.Fpga_SeqTrigCfgSeq(self.SeqCfg['Mask'],Idx, self.SeqCfg['Seq'][Idx])


    def     BrdSetTim_RccM1PW_Ms(self, dCfg):
        fSeqTrig                    =   100e6
        Seq                         =   SeqTrig.SeqTrig(fSeqTrig)

        print('BrdSetTim_RccM1PW_Ms')
        SeqTrigCfg                  =   dict()
        SeqTrigCfg['Mask']          =   1
        SeqTrigCfg['Ctrl']          =   0                                        # Enable interrupt event on channel 2
        SeqTrigCfg['ChnEna']        =   Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA
        SeqTrigCfg['Seq']           =   list()

        # Phase 0: Ini with dummy frame: (lSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1)
        if dCfg['IniEve'] > 0:
            lSeq                    =   Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6)
            lSeq                    =   Seq.AddSeq(lSeq, 'WaitEve', 10e-6, 2, 0)
        else:
            lSeq                    =   Seq.IniSeq('Ini', dCfg['IniTim'] - 10e-6)
            lSeq                    =   Seq.AddSeq(lSeq, 'Wait', 10e-6, 2, 0)
        # Phase 1: Cfg: Generate Irq:
        lSeq                        =   Seq.AddSeq(lSeq, 'RccCfg', dCfg['CfgTim'], 3, 0)
        lSeq[2]['Chn3Cfg']          =   (2**31)
        # Phase 2: Meas
        if dCfg['MeasEve'] > 0:
            lSeq                    =   Seq.AddSeq(lSeq,'RccMeasWait', dCfg['MeasTim'], 2, 0)
        else:
            lSeq                    =   Seq.AddSeq(lSeq,'RccMeas', dCfg['MeasTim'], 2, 0)
        lSeq[3]['Chn3Cfg']          =   (2**31)
        SeqTrigCfg['Seq']           =   lSeq

        self.SeqCfg                 =   SeqTrigCfg

        self.Fpga_SeqTrigRst(self.SeqCfg['Mask'])
        NSeq        =   len(self.SeqCfg['Seq'])
        print('Run SeqTrig: ', (NSeq), ' Entries')
        for Idx in range(0,NSeq):
             self.Fpga_SeqTrigCfgSeq(self.SeqCfg['Mask'], Idx, self.SeqCfg['Seq'][Idx])


    def     RfRrn7745Ini(self, *varargin):
        if len(varargin) > 0:
            dCfg                =   varargin[0]
        else:
            dCfg                =   dict()
            dCfg['Mask']        =   self.Rf_Rrn7745_Cfg1_Mask
            dCfg['Tst_I']       =   self.Rf_Rrn7745_Cfg1_Tst_I
            dCfg['Tst_Q']       =   self.Rf_Rrn7745_Cfg1_Tst_Q
            dCfg['Lo_I']        =   self.Rf_Rrn7745_Cfg1_Lo_I
            dCfg['Lo_Q']        =   self.Rf_Rrn7745_Cfg1_Lo_Q
            dCfg['Ena_Mix']     =   self.Rf_Rrn7745_Cfg1_Ena_Mix
            dCfg['Mux']         =   self.Rf_Rrn7745_Cfg1_Mux
            dCfg['Dc1']         =   self.Rf_Rrn7745_Cfg1_Dc1
            dCfg['Dc2']         =   self.Rf_Rrn7745_Cfg1_Dc2
            dCfg['Dc3']         =   self.Rf_Rrn7745_Cfg1_Dc3
            dCfg['Dc4']         =   self.Rf_Rrn7745_Cfg1_Dc4
        if self.DebugInf > 1:
            print('IFRX Rf_Init')
        self.SetRrn7745(dCfg)


    def     RfRpn7720Ini(self, *varargin):
        if len(varargin) > 0:
            dCfg                =   varargin[0]
        else:
            dCfg['Mask']        =   self.Rf_Rpn7720Cfg1_Mask
            dCfg['LoChain']     =   self.Rf_Rpn7720Cfg1_LoChain
            dCfg['Pa1']         =   self.Rf_Rpn7720Cfg1_Pa1
            dCfg['Pa2']         =   self.Rf_Rpn7720Cfg1_Pa2
            dCfg['PaCon']       =   self.Rf_Rpn7720Cfg1_PaCon
            dCfg['Mux']         =   self.Rf_Rpn7720Cfg1_Mux
        if self.DebugInf > 1:
            print('IFTX Rf_Init')
        self.SetRpn7720(dCfg)

    def     RfTxPaEna(self, TxPwr):
        TxPwr   =   TxPwr % 64
        dCfg1                   =       dict()
        dCfg1['Mask']           =       self.Rf_Rpn7720Cfg1_Mask
        dCfg1['LoChain']        =       self.Rf_Rpn7720Cfg1_LoChain
        dCfg1['Pa1']            =       TxPwr
        dCfg1['Pa2']            =       TxPwr
        dCfg1['PaCon']          =       2*16+1
        dCfg1['Mux']            =       self.Rf_Rpn7720Cfg1_Mux

        dCfg2                   =       dict()
        dCfg2['Mask']           =       self.Rf_Rpn7720Cfg2_Mask
        dCfg2['LoChain']        =       self.Rf_Rpn7720Cfg2_LoChain
        dCfg2['Pa1']            =       TxPwr
        dCfg2['Pa2']            =       TxPwr
        dCfg2['PaCon']          =       2*16+1
        dCfg2['Mux']            =       self.Rf_Rpn7720Cfg2_Mux

        self.Rf_Rpn7720Cfg1_Mask            =   dCfg1['Mask']
        self.Rf_Rpn7720Cfg1_LoChain         =   dCfg1['LoChain']
        self.Rf_Rpn7720Cfg1_Pa1             =   dCfg1['Pa1']
        self.Rf_Rpn7720Cfg1_Pa2             =   dCfg1['Pa2']
        self.Rf_Rpn7720Cfg1_PaCon           =   dCfg1['PaCon']
        self.Rf_Rpn7720Cfg1_Mux             =   dCfg1['Mux']

        self.Rf_Rpn7720Cfg2_Mask            =   dCfg2['Mask']
        self.Rf_Rpn7720Cfg2_LoChain         =   dCfg2['LoChain']
        self.Rf_Rpn7720Cfg2_Pa1             =   dCfg2['Pa1']
        self.Rf_Rpn7720Cfg2_Pa2             =   dCfg2['Pa2']
        self.Rf_Rpn7720Cfg2_PaCon           =   dCfg2['PaCon']
        self.Rf_Rpn7720Cfg2_Mux             =   dCfg2['Mux']

        self.RfRpn7720Ini(dCfg1)
        self.RfRpn7720Ini(dCfg2)


    def     Fpga_SetIfrxReg(self, Mask, Reg):
        Cod         =   int('0x9206',0)
        FpgaCmd     =   asarray([Mask, 1])
        FpgaCmd     =   append(FpgaCmd, asarray(Reg))
        Ret         =   self.CmdSend(0, Cod, FpgaCmd)
        Ret         =   self.CmdRecv()
        return Ret


    def     Fpga_GetIfrxReg(self, Mask, Reg):
        Cod         =   int('0x9206',0)
        FpgaCmd     =   asarray([Mask, 2])
        FpgaCmd     =   append(FpgaCmd, asarray(Reg))
        Ret         =   self.CmdSend(0,Cod,FpgaCmd)
        Ret         =   self.CmdRecv()
        return Ret


    def     Fpga_SetIfTxReg(self, Mask, Reg):
        Cod         =   int('0x9205',0)
        FpgaCmd     =   asarray([Mask, 1])
        FpgaCmd     =   append(FpgaCmd, asarray(Reg))
        Ret         =   self.CmdSend(0, Cod, FpgaCmd)
        Ret         =   self.CmdRecv()
        return Ret


    def     Fpga_GetIfTxReg(self, Mask, Reg):
        Cod         =   int('0x9205',0)
        FpgaCmd     =   asarray([Mask, 2])
        FpgaCmd     =   append(FpgaCmd, asarray(Reg))
        Ret         =   self.CmdSend(0, Cod, FpgaCmd)
        Ret         =   self.CmdRecv()
        return Ret


    def     SetRpn7720(self, dCfg):
        Data        =   []
        # Programm LoChain
        Data        =   Data + [ (2**15) + (2**14) + 0*(2**8) + (dCfg['LoChain'] % 256)]
        # Programm Pa1
        Data        =   Data + [ (2**15) + (2**14) + 1*(2**8) + (dCfg['Pa1'] % 256)]
        # Programm Pa2
        Data        =   Data + [ (2**15) + (2**14) + 2*(2**8) + (dCfg['Pa2'] % 256)]
        # Programm PaCon
        Data        =   Data + [ (2**15) + (2**14) + 4*(2**8) + (dCfg['PaCon'] % 256)]
        # Programm Mux
        Data        =   Data + [ (2**15) + (2**14) + 5*(2**8) + (dCfg['Mux'] % 256)]
        Ret         =   self.Fpga_SetIfTxReg(dCfg['Mask'], asarray(uint32(Data)))
        return Ret


    def     SetRrn7745(self, dCfg):
        # Programm Tst_I
        Data    =   [(2**15) + (2**14) + 32*(2**8) + (dCfg['Tst_I'] % 256)]
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
        Ret     =   self.Fpga_SetIfrxReg(dCfg['Mask'], asarray(uint32(Data)))
        return Ret

    def     GetRxFrqOffsets(self, Mod=1):
        if Mod < 1:
            c0 = 299792458   # speed of light
            a = 3.1e-3   # rectangular waveguide dimension

            # RWG length in meter indexed as in framework
            RwgRxLength = array([163.419469, 143.419469, 126.419469, 106.419469,
                                 89.419469, 69.419469, 52.419469, 32.419469,
                                 25.919469, 45.919469, 62.919469, 82.919469,
                                 99.919469, 119.919469, 136.919469, 156.919469])*1e-3
            # MS line length from feed to RRN7745
            MsRxLength = tile(array([8.137, 6.882, 7.642, 8.897])*1e-3,4)
            # MS line (se) length LOs
            MsRxLOLength = repeat(array([38.536, 23.012, 17.792, 32.532])*1e-3,4)

            CFreq = (self.Rf_fStop + self.Rf_fStrt)/2       # center frequency
            kf = (self.Rf_fStop -  self.Rf_fStrt)/ self.Rf_TRampUp

            RwgBeta = sqrt((2*pi*CFreq/c0)**2 - (pi/a)**2)  # see Pozar p. 117
            RwgVelPhase = 2*pi*CFreq/RwgBeta
            RwgVelGrp = c0**2/RwgVelPhase
            RwgRxGrpDly = RwgRxLength/RwgVelGrp

            LambdaMlin = 10e-3/(1453.99/360)
            MlinBeta = 2*pi/LambdaMlin
            MlinVelPhase = 2*pi*CFreq/MlinBeta
            MlinVelGrp = c0**2/MlinVelPhase
            MlinRxGrpDly = MsRxLength/MlinVelGrp
            MlinRxLoGrpDly = MsRxLOLength/MlinVelGrp

            if Mod == 1:
                Frq = kf*RwgRxGrpDly
            elif Mod == 2:
                Frq = kf*(RwgRxGrpDly + MlinRxGrpDly)
            else:
                Frq = kf*(RwgRxGrpDly + MlinRxGrpDly + MlinRxLoGrpDly)
        else:
            Frq = zeros((int(self.Rad_NrChn),))

        return Frq


    def     GetTxFrqOffsets(self, Mod=1):
        if Mod < 0:
            c0 = 299792458  # speed of light
            a = 3.1e-3      # rectangular waveguide dimension

            # RWG length in meter at the TX side
            RwgTxLength = array([149.169469, 65.669469, 59.169469, 142.669469])*1e-3
            #  MS line (diff) length
            #msdTXLength = tile(array([4.745 + 5.138)/2*1e-3],4)
            #msTXLOLength = repeat(array[11.601, 22.494]*1e-3,2)

            CFreq = (self.Rf_fStop + self.Rf_fStrt)/2        # center frequency
            kf = (self.Rf_fStop -  self.Rf_fStrt)/ self.Rf_TRampUp

            RwgBeta = sqrt((2*pi*CFreq/c0)**2 - (pi/a)**2)   # see Pozar p. 117
            RwgVelPhase = 2*pi*CFreq/RwgBeta
            RwgVelGrp = c0**2/RwgVelPhase
            RwgTxGrpDly = RwgTxLength/RwgVelGrp

            Frq = kf*RwgTxGrpDly
        else:
            Frq = zeros((4,))

        return Frq

    def     RefCornerCube(self, fc, aCorner, R, *varargin):
            c0          =   3e8
            #--------------------------------------------------------------------------
            # Transmit Power
            #--------------------------------------------------------------------------
            PtdBm       =   6
            GPa         =   11
            GtdB        =   13.2
            GrdB        =   13.2
            GcdB        =   22
            GLna        =   13

#            if len(varargin) > 1:
#                Cfg       =   varargin[0]
#            if nargin > 3
#                Cfg     =   varargin
#                if isfield(Cfg,'PtdBm')
#                    PtdBm   =   Cfg.PtdBm
#                end
#            end
            #--------------------------------------------------------------------------
            # Calculate Values
            #--------------------------------------------------------------------------
            Pt          =   10**((PtdBm+GPa)/10)*1e-3
            Gt          =   10**(GtdB/10)
            Gr          =   10**(GrdB/10)
            Lambdac     =   c0/fc

            RCS         =   4*pi*aCorner**4/(3*Lambdac**2)

            Pr          =   Pt/(4*pi*R**4)*Gt/(4*pi)*Gr/(4*pi)*RCS*Lambdac**2
            PrdBm       =   10*log10(Pr/1e-3)
            PIfdBm      =   PrdBm + GcdB + GLna
            UIf         =   sqrt(50*10**(PIfdBm/10)*1e-3)*sqrt(2)/2
            UIfdB       =   20*log10(UIf)

            return UIfdB
