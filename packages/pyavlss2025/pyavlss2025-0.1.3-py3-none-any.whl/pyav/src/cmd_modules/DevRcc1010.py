#< @file        DevRcc1010.m                                                                
#< @author      Haderer Andreas (HaAn)                                                  
#< @date        2013-06-13          
#< @brief       Class for configuration of RS28

import  pyav.src.cmd_modules.DevDriver  as DevDriver
from    numpy import * 

__version__     =   "1.0.0"



class DevRcc1010(DevDriver.DevDriver):  

    def __init__(self, Rad, Mask):
        super(DevRcc1010, self).__init__()

        self.Rad            =   Rad
        # Set Reference Clock
        self.RefClk         =   40e6

        self.FreqScale      =   1.0

        self.TRampUp        =   512000.0          
        self.TRampDown      =   512000.0 
        self.TWait1         =   0.0
        self.TWait2         =   0.0

        self.Pa1            =   int('11000111',2)              
        self.Pa2            =   int('11000111',2)                
        self.Pa3            =   int('11011100',2) 

        self.PaCfg_Pa1      =   1   
        self.PaCfg_Pa2      =   2 
        self.PaCfg_Pa3      =   4
        self.PaCfg_Pa4      =   8
        self.PaCfg_LO       =   16
        self.PaCfg_EN       =   128 


        self.Mask           =   Mask
        self.Adr            =   int('0x1000',0)

        self.DefineConst()

    def SetCfg(self, dCfg):
        #   @function       SetCfg                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Set Device Configuration
        #   @param[in]      dCfg
        #                       TxPwr1:     Power of transmitter 1
        #                       TxPwr2:     Power of transmitter 2 
        #                       TxPwr3:     Power of transmitter 3
        #                       RefClk:     RCC1010 Reference Clock
        if "TxPwr1" in dCfg:
            TxPwr1      =   int(dCfg["TxPwr1"])
            if TxPwr1 < 0:
                TxPwr1   =   0
            if TxPwr1 > 255:
                TxPwr1   =   255
            self.RegPa1     =   TxPwr1  
        if "TxPwr2" in dCfg:
            TxPwr2      =   int(dCfg["TxPwr2"])
            if TxPwr2 < 0:
                TxPwr2   =   0
            if TxPwr2 > 255:
                TxPwr2   =   255
            self.RegPa2     =   TxPwr2  
        if "TxPwr3" in dCfg:
            TxPwr3      =   int(dCfg["TxPwr3"])
            if TxPwr3 < 0:
                TxPwr3   =   0
            if TxPwr3 > 255:
                TxPwr3   =   255
            self.RegPa3     =   TxPwr3  
        if "RefClk" in dCfg:
            self.RefClk     =   dCfg["RefClk"]

        if self.Rad().Debug > 0:
            print("RCC1010  Setting:")
            print(" Pa1 %d:", self.RegPa1)
            print(" Pa2 %d:", self.RegPa2)
            print(" Pa3 %d:", self.RegPa3)

    def DevRst(self):
        #   @function       DevRst                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Reset RCC       
        Data            =   zeros(2, dtype='uint32')
        Data[0]         =   self.Mask                           # Mask for RCC  
        Data[1]         =   2                                   # Apply reset signal (set, release again)
        CmdCod          =   int("0x9202", 0)
        Ret             =   self.Rad().CmdSend(0, CmdCod, Data)
        Ret             =   self.Rad().CmdRecv()
        if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 64:
            print("DevRcc1010::DevRst Ret", Ret)
        return      Ret 

    def DevGetReg(self, Adr):
        #   @function       Fpga_GetRccReg                                                               
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Get Register of RCC1010
        #   @paramin[in]    Mask:       Bitmask to select RCC1010 (generally 1, if one RCC1010 is available on frontend)
        #   @paramin[in]    Reg:        32 Bit Value programmed over the SPI interface (Data contains ReadBit + Adr)
        #                               Data can be an array with a maximum of 30 Values              
        
        if hasattr(Adr, "__len__"):
            Reg         =   zeros(len(Adr),dtype='uint32')
            Reg         =   uint32(Adr)    
        else:
            Reg         =   zeros(1, dtype='uint32')
            Reg[0]      =   uint32(Adr)

        if len(Reg) > 30:
            Reg         =   Reg[0:30]

        Cod             =   int('0x9204',0)
        FpgaCmd         =   zeros(1+len(Reg), dtype='uint32')
        FpgaCmd[0]      =   self.Mask
        FpgaCmd[1:]     =   Reg
        Ret             =   self.Rad().CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.Rad().CmdRecv();
        if Ret[0] == True:
            Data        =   Ret[1]
            Data        =   Data % (2**16)
            Ret         =   (True, Data)
           
        if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 64:
            print("DevRcc1010::DevGetReg Ret", Ret)                
        return      Ret         

    def DevSetReg(self, Regs):
        #   @function       SetCfg                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Set Device Configuration
        #   @param[in]      Regs: register values beeing programmed over spi 
        if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
            print("DevRcc1010::DevSetReg")
        Regs            =   Regs.flatten()
        while (len(Regs) > 0):

            if len(Regs) > 28:
                Data            =   zeros(28 + 1, dtype='uint32')
                Data[0]         =   self.Mask
                Data[1:]        =   Regs[0:28]
                Regs            =   Regs[28:]        
            else:
                Data            =   zeros(len(Regs) + 1, dtype='uint32')
                Data[0]         =   self.Mask
                Data[1:]        =   Regs
                Regs            =   zeros(0)                  
            CmdCod              =   int("0x9201", 0)
            Ret                 =   self.Rad().CmdSend(0, CmdCod, Data)
            Ret                 =   self.Rad().CmdRecv()
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 64:
                print("DevRcc1010::DevSetReg Ret", Ret)

        return Ret

    def DevProcCall(self, stCall, *varargin):

        if stCall == "SetModRun":
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                print("DevRcc1010::Proc Call SetRunMod")  
            Reg         =   zeros(1, dtype = 'uint32')
            Val         =   int(self.GenRegVal(self.cRCC1010_REG_GLOBAL_ADR, int('0x1F2',0)))
            Reg[0]      =   uint32(Val)
            self.DevSetReg(Reg)
            self.DevGetReg(self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR * (2**16)) 
        
        if stCall == "InitBasic":
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                print("DevRcc1010::Proc Call InitBasic")  
            Regs        =   zeros(1, dtype = 'uint32')
            Regs[0]     =   int('0x1111',0)     
            Regs[0]     =   Regs[0] + self.cRCC1010_REG_PROCESSINGCALL_ADR* (2**16) + (2**31)    
            self.DevSetReg(Regs)
            RegVal      =   self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR * (2**16)
            Reg         =   zeros(2, dtype = 'uint32')
            Reg[0]      =   RegVal 
            Reg[1]      =   RegVal
            Val         =   self.DevGetReg(Reg)      
            if Val[0] == True:
                Val     =   Val[1]
                Val     =   (Val % 2**16)
                if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                    print('Ret 1: %x' % Val[0],'h')
                    print('Ret 2: %x' % Val[1],'h')
        
        if stCall == "OutputStaticFrequency":
            if len(varargin) > 0:
                StatFreq    =   varargin[0]
                if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                    print("DevRcc1010::Proc Call OutputStaticFrequency", StatFreq/1e6, " MHz")  
                nStatic     =   round(StatFreq/40e6*self.FreqScale*2**16)
                nLsb        =   nStatic % 2**16
                nMsb        =   floor(nStatic/2**16) % (2**15)
                # write to processing call register
                Regs        =   zeros(3, dtype = 'uint32')
                Regs[0]     =   self.cRCC1010_CALLCODE_OUTPUTSTATICFREQUENCY
                Regs[1]     =   nLsb
                Regs[2]     =   nMsb
                Regs        =   Regs + self.cRCC1010_REG_PROCESSINGCALL_ADR* (2**16) + (2**31)
                self.DevSetReg(Regs)
                RegVal      =   self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR * (2**16)
                Reg         =   zeros(2, dtype = 'uint32')
                Reg[0]      =   RegVal 
                Reg[1]      =   RegVal
                Val         =   self.DevGetReg(Reg)    
                if Val[0] == True:
                    Val     =   Val[1]
                    Val     =   (Val % 2**16)
                    if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                        print('Ret 1: %x' % Val[0],'h')
                        print('Ret 2: %x' % Val[1],'h')

        if stCall == "SetTxReg":
            Offs    =   uint32(varargin[0])
            Val     =   uint32(varargin[1])
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                print("DevRcc1010::Proc Call SetTxReg", Offs, " Val:", Val)  
            Data        =   (Offs % 5)*2**8 + (Val % 2**8)
            Reg         =   zeros(2, dtype = 'uint32')
            Reg[0]      =   self.cRCC1010_CALLCODE_SETTXREG
            Reg[1]      =   Data   
            Reg         =   Reg + self.cRCC1010_REG_PROCESSINGCALL_ADR*(2**16) + (2**31)     
            self.DevSetReg(Reg)
            RegVal      =   self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR * (2**16)
            Reg         =   zeros(2, dtype = 'uint32')
            Reg[0]      =   RegVal 
            Reg[1]      =   RegVal
            Val         =   self.DevGetReg(Reg)    
            if Val[0] == True:
                Val     =   Val[1]
                Val     =   (Val % 2**16)
                if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                    print('Ret 1: %x' % Val[0],'h')
                    print('Ret 2: %x' % Val[1],'h')

        if stCall == "StartCoarseTuneCalibration":
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                print("DevRcc1010::Proc Call StartCoarseTuneCalibration") 
            Reg         =   zeros(1, dtype = 'uint32')         
            Reg[0]      =   self.cRCC1010_CALLCODE_COARSETUNECALIBRATION
            Reg         =   Reg + self.cRCC1010_REG_PROCESSINGCALL_ADR*(2**16) + (2**31)     
            self.DevSetReg(Reg)
            RegVal      =   self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR * (2**16)
            Reg         =   zeros(2, dtype = 'uint32')
            Reg[0]      =   RegVal 
            Reg[1]      =   RegVal
            Val         =   self.DevGetReg(Reg)    
            if Val[0] == True:
                Val     =   Val[1]
                Val     =   (Val % 2**16)
                if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                    print('Ret 1: %x' % Val[0],'h')
                    print('Ret 2: %x' % Val[1],'h')            

        if stCall == "StartFQMCalibration": 
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                print("DevRcc1010::Proc Call StartFQMCalibration") 
            Reg         =   zeros(1, dtype = 'uint32')         
            Reg[0]      =   self.cRCC1010_CALLCODE_FQMCALIBRATION
            Reg         =   Reg + self.cRCC1010_REG_PROCESSINGCALL_ADR * (2**16) + (2**31)     
            self.DevSetReg(Reg)
            RegVal      =   self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR * (2**16)
            Reg         =   zeros(2, dtype = 'uint32')
            Reg[0]      =   RegVal 
            Reg[1]      =   RegVal
            Val         =   self.DevGetReg(Reg)    
            if Val[0] == True:
                Val     =   Val[1]
                Val     =   (Val % 2**16)
                if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                    print('Ret 1: %x' % Val[0],'h')
                    print('Ret 2: %x' % Val[1],'h')  

    def GenRegVal(self, Adr, Reg):
        #   @function       GenReg                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Generate register for programming 
        return  (2**31 + Adr*2**16 + Reg)   

    def SmartIni(self, stSel):

        if stSel == 'ExtTrigMux2':
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                print('DevRcc1010: Smart Ini ExtTrigMux2')
            
            Regs        =   zeros(5, dtype = 'uint32')
            Idx         =   0
            
            Addr        =   self.dRegAdr["GlobalDigitalEnable"]                 # 0x020C
            RegVal      =   904                                                 # 0x388
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            Addr        =   self.dRegAdr["Global"]                              # 512 
            RegVal      =   496                                                 # 0x01F0
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # dig_iopads_pull_reg: 0 for pull down, 1 for pull up
            Addr        =   self.dRegAdr["DigIoPadsPull"]                       # 0x029C
            RegVal      =   0;                                                  # 0x0000
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # %p5,p4,p3,p2,p1,p0,dmux2,dmux1, 1 = output, 0 = input
            Addr        =   self.dRegAdr["DigIoPadsIo"]                         # 0x029A
            RegVal      =   int('00001101',2)                    
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # framp_trigger_reg     
            # enable external trigger pin
            # 0...p0, 1...p1, 2...p2, 3...p3, 4...p4, 5...p5, 6...dmux1, 7...dmux2 
            Addr        =   self.dRegAdr["FRampTrigger"]                        # 0x0250
            RegVal      =   int('111',2)                                        # dmux2
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            Ret         =   self.DevSetReg(Regs)
            return Ret

        elif stSel == 'ExtTrigMux2PaCtrl':
            if (int(self.Rad().cDebugInf) & int('0xF0',0)) > 0:
                pass    
            print('DevRcc1010: Smart Ini ExtTrigMux2 PaCtrl')
            
            Regs        =   zeros(11, dtype = 'uint32')
            Idx         =   0

            Addr        =   self.dRegAdr["GlobalDigitalEnable"]                 # 524; 0x020C
            RegVal      =   904                                                 # 0x388
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            Addr        =   self.dRegAdr["Global"]                              # 0x0200
            RegVal      =   496                                                 # 0x01F0
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # dig_iopads_pull_reg: 0 for pull down, 1 for pull up
            Addr        =   self.dRegAdr["DigIoPadsPull"]                       # 0x029C
            RegVal      =   0                                                   # 0x0000
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # %p5,p4,p3,p2,p1,p0,dmux2,dmux1, 1 = output, 0 = input
            Addr        =   self.dRegAdr["DigIoPadsIo"]                         # 0x029A
            RegVal      =   int('11111101',2)                         
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # framp_trigger_reg     
            # enable external trigger pin
            # 0...p0, 1...p1, 2...p2, 3...p3, 4...p4, 5...p5, 6...dmux1, 7...dmux2 
            Addr        =   self.dRegAdr["FRampTrigger"]                        # 0x0250
            RegVal      =   int('111',2)                                        # dmux2
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # P0 -> framp_state_cfg3 P0Map
            Addr        =   self.dRegAdr["P0Map"]                     
            RegVal      =   int('00110',2)                   
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # P1 -> framp_state_cfg2
            Addr        =   self.dRegAdr["P1Map"]                     
            RegVal      =   int('00111',2)                
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # P2 -> framp_state_cfg1
            Addr        =   self.dRegAdr["P2Map"]                      
            RegVal      =   int('01000',2)                 
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # P3 -> framp_state_cfg0
            Addr        =   self.dRegAdr["P3Map"]                      
            RegVal      =   int('01001',2)                
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            # P4 -> framp_state_cfg4
            Addr        =   self.dRegAdr["P4Map"]                      
            RegVal      =   int('01010',2)                   
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1
            
            # P5 -> framp_state_cfg5
            Addr        =   self.dRegAdr["DMux1Map"]                      
            RegVal      =   int('01011',2)                   
            Reg         =   uint32(2**31+Addr*2**16+RegVal)
            Regs[Idx]   =   Reg
            Idx         =   Idx + 1

            Ret         =   self.DevSetReg(Regs)
            return Ret  

 
    def     GetRampSeqDuration(self, lVal):
        #   @function       RfRcc1010GetRampDuration                                                               
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Return Duration of programmed ramp scenario
        #   @paramin[in]    Val:        Cell array of structures with Ramp Sequence
        #                   Mandatory Fields:
        #                       fStrt:          Start frequency in Hz
        #                       fStop:          Stop frequency in Hz
        #                       TRamp:          Ramp duration in s
        #                   Optional Fields:
        #                       TWait:          Wait time in s; 0 if not stated in cell array
        #                       PaCfg:          Power control cfg
        #                       RampCfg:        refer to data sheet  
        #                       nStepScale:     refer to data sheet; 0 if not stated in cell array
        #                       nWaitScale:     refer to data sheet; Sampling clock control (0 Frontend, 1 Baseband)  
        #   @return         Dur: Duration of ramp szenario in s  
        Err     =   False
        Dur     =   0

        if isinstance(lVal, list): 
            Dur     =   0;    

            for dElem in lVal:
                if 'TRamp' in dElem:
                    Dur   =   Dur + dElem["TRamp"]
                else:  
                    print('TRamp Field missing')
                    Err     =   True      
                if 'TWait' in dElem:
                    Dur   =   Dur + dElem["TWait"]
                                                  

        if Err:
            Dur     =   -1
        
        return Dur



    def ProgRampMemory(self, StrtAdr, Val):
        #   @function       RfRcc1010ProgRampMemory                                                               
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Configure RCC1010 Memory for Ramp Sequence
        #   @paramin[in]    Mask:       Bitmask to select RCC1010 (generally 1, if one RCC1010 is available on frontend)
        #   @paramin[in]    StrtAdr:    Startaddress in RCC1010 Memory
        #   @paramin[in]    Val:        Cell array of structures with Ramp Sequence
        #                   Mandatory Fields:
        #                       fStrt:          Start frequency in Hz
        #                       fStop:          Stop frequency in Hz
        #                       TRamp:          Ramp duration in s
        #                   Optional Fields:
        #                       TWait:          Wait time in s; 0 if not stated in cell array
        #                       PaCfg:          Power control cfg
        #                       RampCfg:        refer to data sheet  
        #                       nStepScale:     refer to data sheet; 0 if not stated in cell array
        #                       nWaitScale:     refer to data sheet; Sampling clock control (0 Frontend, 1 Baseband)                
        # Check Start Address
        Err         =   0;
        if StrtAdr < int('0x1000',0):
            Err     =   1;
            print('Programm RCC1010 Memory: Error start address')

        self.Adr    =   StrtAdr

        if isinstance(Val, list): 
            NCell   =   len(Val)
            Adr     =   StrtAdr

            Reg     =   zeros(8*NCell, dtype = 'uint32')

            for Idx in range(0,NCell):

                if Err  == 0:
                    if 'fStrt' in Val[Idx]:
                        fStrt       =   Val[Idx]["fStrt"]
                    else:  
                        print('ProgRampMemory: fStart Field missing')
                        Err         =   1

                    if 'fStop' in Val[Idx]:
                        fStop       =   Val[Idx]["fStop"]
                    else:  
                        print('ProgRampMemory: fStop Field missing')
                        Err         =   1

                    if 'TRamp' in Val[Idx]:
                        TRamp       =   Val[Idx]["TRamp"]
                    else:  
                        print('ProgRampMemory: TRamp Field missing');
                        Err         =   1

                    if 'TWait' in Val[Idx]:
                        TWait       =   Val[Idx]["TWait"]
                    else:  
                        TWait       =   0

                    if 'PaCfg' in Val[Idx]:                        
                        PaCfg       =   Val[Idx]["PaCfg"]
                    else:  
                        PaCfg       =   self.PaCfg_Pa1 + self.PaCfg_Pa2 + self.PaCfg_Pa3 

                    if 'RampCfg' in Val[Idx]:
                        RampCfg     =   Val[Idx]["RampCfg"]
                    else: 
                        RampCfg     =   0 

                    if 'nStepScale' in Val[Idx]:
                        nStepScale  =   Val[Idx]["nStepScale"]
                    else:
                        nStepScale  =   0    

                    if 'nWaitScale' in Val[Idx]:
                        nWaitScale  =   Val[Idx]["nWaitScale"]
                    else:
                        nWaitScale  =   0  


                    if Err == 0:
                        nStrt       =   round(fStrt/40e6*self.FreqScale*2**16);
                        nStop       =   round(fStop/40e6*self.FreqScale*2**16);
                        nStep       =   round((nStepScale+1)*abs(nStop - nStrt)/(TRamp*40e6 - nStepScale -1));
                        nWait       =   round(TWait*40e6/(nWaitScale + 1));

                        nStrt       =   nStrt % 2**31
                        nStop       =   nStop % 2**31
                        nStep       =   nStep % 2**16
                        nWait       =   nWait % 2**16
                        PaCfg       =   PaCfg % 2**6
                        RampCfg     =   RampCfg % 2**6
                        nStepScale  =   nStepScale % 2**6
                        nWaitScale  =   nWaitScale % 2**6

                        nStrtMsb    =   floor(nStrt/2**16)
                        nStrtLsb    =   nStrt % 2**16
                        nStopMsb    =   floor(nStop/2**16)
                        nStopLsb    =   nStop % 2**16

                        Reg[Idx*8+0]    =   uint32(2**31 + 2**16*(Adr) + nStrtLsb)
                        Reg[Idx*8+1]    =   uint32(2**31 + 2**16*(Adr+2) + nStrtMsb)
                        Reg[Idx*8+2]    =   uint32(2**31 + 2**16*(Adr+4) + nStopLsb)
                        Reg[Idx*8+3]    =   uint32(2**31 + 2**16*(Adr+6) + nStopMsb)
                        Reg[Idx*8+4]    =   uint32(2**31 + 2**16*(Adr+8) + nStep)
                        Reg[Idx*8+5]    =   uint32(2**31 + 2**16*(Adr+10) + nWait)
                        Reg[Idx*8+6]    =   uint32(2**31 + 2**16*(Adr+12) + RampCfg + 2**8*nStepScale)
                        Reg[Idx*8+7]    =   uint32(2**31 + 2**16*(Adr+14) + nWaitScale + 2**8*PaCfg)
                        Adr                 =   Adr + 16
        else:
            Val         =   Val.flatten(1);
            NData       =   len(Val)
            if (NData % 8) == 0:
                print('Programm Register Values @Adr: ', StrtAdr)
                Reg     =   zeros(NData, dtype = 'uint32')
                Adr     =   StartAdr
                for Idx in range(0,NData):
                    Reg[Idx]    =   uint32(2**31 + 2**16*Adr + Val[Idx])
                    Adr         =   Adr + 2
            else:
                print('Programm RCC1010 Memory: Error data size');

        if (StrtAdr + 2*len(Reg)) > int('0x7FF0',0):
            Err = 1

        if Err == 0:
            print('Programm RCC1010 Memory') 
            self.DevSetReg(Reg)
        else:
            print('Programm RCC1010 Memory: Error')

    def GetRegsProcCallExtTrig(self, Adr, NSet, NLoop, ExitCfg):
        if Adr < int('0x1000',0):
            Adr     =   int('0x1000',0)
        if Adr > int('0x7FF0',0):
            Adr     =   int('0x1000',0)

        NSet        =   NSet % 1792
        NLoop       =   NLoop % 2**16
        ExitCfg     =   ExitCfg % 2**16
        Regs        =   zeros(5, dtype = 'uint32')
        Regs[0]     =   uint32(self.cRCC1010_CALLCODE_STARTRAMPSCENARIOEXTTRIG)        
        Regs[1]     =   uint32(Adr)
        Regs[2]     =   uint32(NSet)
        Regs[3]     =   uint32(NLoop)
        Regs[4]     =   uint32(ExitCfg)  
        Regs        =   Regs + self.cRCC1010_REG_PROCESSINGCALL_ADR*2**16 + 2**31   

        return Regs

    def RstRegs(self):
        pass

    def DefineConst(self):
        self.dRegAdr    =   {   
                            "Global"                        :   512,
                            "GlobalStatus"                  :   514, 
                            "GlobalError"                   :   516, 
                            "GlobalProcessingCall"          :   518, 
                            "GlobalProcessingCallCount"     :   520,
                            "GlobalProcessingStatus"        :   522, 
                            "GlobalDigitalEnable"           :   524, 
                            "GlobalAnalogEnable1"           :   526, 
                            "GlobalAnalogEnable2"           :   528, 
                            "GlobalInterruptEnable"         :   530, 
                            "GlobalInterruptStatus"         :   532, 
                            "Pd"                            :   534, 
                            "Lf"                            :   536, 
                            "CpBiasControl"                 :   538, 
                            "Cp5VControl"                   :   540, 
                            "LdmClkMmd"                     :   542, 
                            "D2Sd2d"                        :   544, 
                            "FqmCtrl"                       :   546, 
                            "MashCtrl"                      :   548, 
                            "MashOutput"                    :   550,
                            "MashInputLsb"                  :   552, 
                            "MashInputMsb"                  :   554, 
                            "FRamp1NStartLsb"               :   556, 
                            "FRamp1NStartMsb"               :   558, 
                            "FRamp1NStopLsb"                :   560, 
                            "FRamp1NStopMsb"                :   562, 
                            "FRamp1NStep"                   :   564, 
                            "FRamp1NStepScale"              :   566, 
                            "FRamp1NWait"                   :   568, 
                            "FRamp1NWaitScale"              :   570, 
                            "FRamp1NWaitMisc"               :   572, 
                            "FRamp2NStartLsb"               :   574, 
                            "FRamp2NStartMsb"               :   576, 
                            "FRamp2NStopLsb"                :   578, 
                            "FRamp2NStopMsb"                :   580, 
                            "FRamp2NStep"                   :   582, 
                            "FRamp2NStepScale"              :   584, 
                            "FRamp2NWait"                   :   586, 
                            "FRamp2NWaitScale"              :   588, 
                            "FRamp2Misc"                    :   590, 
                            "FRampTrigger"                  :   592, 
                            "AdcConf"                       :   594, 
                            "AdcMux"                        :   596, 
                            "AdcSamplerate"                 :   598, 
                            "AdcData"                       :   600, 
                            "DacData"                       :   602, 
                            "DacControl"                    :   604, 
                            "FCountLow"                     :   606, 
                            "FCountHigh"                    :   608, 
                            "FCountScale"                   :   610,
                            "FCountControl"                 :   612, 
                            "PhControl"                     :   614, 
                            "CrcData"                       :   616, 
                            "CrcResult"                     :   618, 
                            "CrcControl"                    :   620, 
                            "DldLoLimit"                    :   622, 
                            "DldHiLimit"                    :   624, 
                            "DldResult"                     :   626, 
                            "DldControl"                    :   628, 
                            "SpimControl"                   :   630, 
                            "SpimStatus"                    :   632, 
                            "SpimDataWriteLsb"              :   634, 
                            "SpimDataWriteMsb"              :   636, 
                            "SpimDataReadLsb"               :   638, 
                            "SpimDataReadMsb"               :   640, 
                            "DMux1Map"                      :   642, 
                            "DMux2Map"                      :   644, 
                            "P0Map"                         :   646, 
                            "P1Map"                         :   648, 
                            "P2Map"                         :   650, 
                            "P3Map"                         :   652, 
                            "P4Map"                         :   654, 
                            "P5Map"                         :   656, 
                            "AMux1Map"                      :   658, 
                            "AMux2Map"                      :   660, 
                            "DigIoPadsWrite"                :   662, 
                            "DigIoPadsRead"                 :   664, 
                            "DigIoPadsIo"                   :   666, 
                            "DigIoPadsPull"                 :   668, 
                            "DigIoPadsSlope"                :   670, 
                            "LfsrControl"                   :   672, 
                            "Lfsr1Poly"                     :   674, 
                            "Lfsr1State"                    :   676, 
                            "Lfsr2Poly"                     :   678, 
                            "Lfsr2State"                    :   680, 
                            "TestDigital"                   :   682, 
                            "TestAnalog"                    :   684, 
                            "TestDigPads"                   :   686,
                            "TestAdcI"                      :   688, 
                            "TestAdcO"                      :   690, 
                            "TestFqmCtrl"                   :   692, 
                            "TestIrqVecStart"               :   694, 
                            "TestAnalogSpare"               :   696, 
                            "Id1"                           :   762, 
                            "Id2"                           :   764, 
                            "Id3"                           :   766, 
                            "TxConfig0"                     :   768, 
                            "TxConfig1"                     :   770, 
                            "TxConfig2"                     :   772, 
                            "TxConfig3"                     :   774, 
                            "TxConfig4"                     :   776, 
                            "TxConfig5"                     :   778, 
                            "TxDummy1"                      :   780, 
                            "TxDummy2"                      :   782, 
                            "TxId1"                         :   848, 
                            "TxId2"                         :   850,
                            "TxId3"                         :   852
                        }

        self.cRCC1010_CALLCODE_OUTPUTSTATICFREQUENCY        =   int ('0x1130',0) 
        self.cRCC1010_CALLCODE_STARTRAMPSCENARIO            =   int ('0x1120',0) 
        self.cRCC1010_CALLCODE_STARTRAMPSCENARIOEXTTRIG     =   int ('0x1124',0) 
        self.cRCC1010_CALLCODE_STOPRAMPSCENARIO             =   int ('0x1121',0) 
        self.cRCC1010_CALLCODE_COARSETUNECALIBRATION        =   int ('0x1140',0) 
        self.cRCC1010_CALLCODE_SETTXREG                     =   int ('0x1150',0) 
        self.cRCC1010_CALLCODE_SETVERIFYTXREG               =   int ('0x1151',0) 
        self.cRCC1010_CALLCODE_GETTXREG                     =   int ('0x1170',0) 
        self.cRCC1010_CALLCODE_MEASTXTEMPERATURE            =   int ('0x1161',0) 
        self.cRCC1010_CALLCODE_MEASTXPOWER                  =   int ('0x1165',0) 
        self.cRCC1010_CALLCODE_FQMCALIBRATION               =   int ('0x1180',0) 

        self.cRCC1010_REG_GLOBAL_ADR                        =   int ('0x0200',0)
        self.cRCC1010_REG_PROCESSINGCALL_ADR                =   int ('0x0206',0)
        self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR        =   int ('0x020a',0)


        self.cRCC1010_REG_GLOBAL_ADR                         =   512 
        self.cRCC1010_REG_GLOBALSTATUS_ADR                   =   514 
        self.cRCC1010_REG_GLOBALERROR_ADR                    =   516 
        self.cRCC1010_REG_GLOBALPROCESSINGCALL_ADR           =   518 
        self.cRCC1010_REG_GLOBALPROCESSINGCALLCOUNT_ADR      =   520 
        self.cRCC1010_REG_GLOBALPROCESSINGSTATUS_ADR         =   522 
        self.cRCC1010_REG_GLOBALDIGITALENABLE_ADR            =   524 
        self.cRCC1010_REG_GLOBALANALOGENABLE1_ADR            =   526 
        self.cRCC1010_REG_GLOBALANALOGENABLE2_ADR            =   528 
        self.cRCC1010_REG_GLOBALINTERRUPTENABLE_ADR          =   530 
        self.cRCC1010_REG_GLOBALINTERRUPTSTATUS_ADR          =   532 
        self.cRCC1010_REG_PD_ADR                             =   534 
        self.cRCC1010_REG_LF_ADR                             =   536 
        self.cRCC1010_REG_CPBIASCONTROL_ADR                  =   538 
        self.cRCC1010_REG_CP5VCONTROL_ADR                    =   540 
        self.cRCC1010_REG_LDMCLKMMD_ADR                      =   542 
        self.cRCC1010_REG_D2SD2D_ADR                         =   544 
        self.cRCC1010_REG_FQMCTRL_ADR                        =   546 
        self.cRCC1010_REG_MASHCTRL_ADR                       =   548 
        self.cRCC1010_REG_MASHOUTPUT_ADR                     =   550 
        self.cRCC1010_REG_MASHINPUTLSB_ADR                   =   552 
        self.cRCC1010_REG_MASHINPUTMSB_ADR                   =   554 
        self.cRCC1010_REG_FRAMP1NSTARTLSB_ADR                =   556 
        self.cRCC1010_REG_FRAMP1NSTARTMSB_ADR                =   558 
        self.cRCC1010_REG_FRAMP1NSTOPLSB_ADR                 =   560 
        self.cRCC1010_REG_FRAMP1NSTOPMSB_ADR                 =   562 
        self.cRCC1010_REG_FRAMP1NSTEP_ADR                    =   564 
        self.cRCC1010_REG_FRAMP1NSTEPSCALE_ADR               =   566 
        self.cRCC1010_REG_FRAMP1NWAIT_ADR                    =   568 
        self.cRCC1010_REG_FRAMP1NWAITSCALE_ADR               =   570 
        self.cRCC1010_REG_FRAMP1MISC_ADR                     =   572 
        self.cRCC1010_REG_FRAMP2NSTARTLSB_ADR                =   574 
        self.cRCC1010_REG_FRAMP2NSTARTMSB_ADR                =   576 
        self.cRCC1010_REG_FRAMP2NSTOPLSB_ADR                 =   578 
        self.cRCC1010_REG_FRAMP2NSTOPMSB_ADR                 =   580 
        self.cRCC1010_REG_FRAMP2NSTEP_ADR                    =   582 
        self.cRCC1010_REG_FRAMP2NSTEPSCALE_ADR               =   584 
        self.cRCC1010_REG_FRAMP2NWAIT_ADR                    =   586 
        self.cRCC1010_REG_FRAMP2NWAITSCALE_ADR               =   588 
        self.cRCC1010_REG_FRAMP2MISC_ADR                     =   590 
        self.cRCC1010_REG_FRAMPTRIGGER_ADR                   =   592 
        self.cRCC1010_REG_ADCCONF_ADR                        =   594 
        self.cRCC1010_REG_ADCMUX_ADR                         =   596 
        self.cRCC1010_REG_ADCSAMPLERATE_ADR                  =   598 
        self.cRCC1010_REG_ADCDATA_ADR                        =   600 
        self.cRCC1010_REG_DACDATA_ADR                        =   602 
        self.cRCC1010_REG_DACCONTROL_ADR                     =   604 
        self.cRCC1010_REG_FCOUNTLOW_ADR                      =   606 
        self.cRCC1010_REG_FCOUNTHIGH_ADR                     =   608 
        self.cRCC1010_REG_FCOUNTSCALE_ADR                    =   610
        self.cRCC1010_REG_FCOUNTCONTROL_ADR                  =   612 
        self.cRCC1010_REG_PHCONTROL_ADR                      =   614 
        self.cRCC1010_REG_CRCDATA_ADR                        =   616 
        self.cRCC1010_REG_CRCRESULT_ADR                      =   618 
        self.cRCC1010_REG_CRCCONTROL_ADR                     =   620 
        self.cRCC1010_REG_DLDLOLIMIT_ADR                     =   622 
        self.cRCC1010_REG_DLDHILIMIT_ADR                     =   624 
        self.cRCC1010_REG_DLDRESULT_ADR                      =   626 
        self.cRCC1010_REG_DLDCONTROL_ADR                     =   628 
        self.cRCC1010_REG_SPIMCONTROL_ADR                    =   630 
        self.cRCC1010_REG_SPIMSTATUS_ADR                     =   632 
        self.cRCC1010_REG_SPIMDATAWRITELSB_ADR               =   634 
        self.cRCC1010_REG_SPIMDATAWRITEMSB_ADR               =   636 
        self.cRCC1010_REG_SPIMDATAREADLSB_ADR                =   638 
        self.cRCC1010_REG_SPIMDATAREADMSB_ADR                =   640 
        self.cRCC1010_REG_DMUX1MAP_ADR                       =   642 
        self.cRCC1010_REG_DMUX2MAP_ADR                       =   644 
        self.cRCC1010_REG_P0MAP_ADR                          =   646 
        self.cRCC1010_REG_P1MAP_ADR                          =   648 
        self.cRCC1010_REG_P2MAP_ADR                          =   650 
        self.cRCC1010_REG_P3MAP_ADR                          =   652 
        self.cRCC1010_REG_P4MAP_ADR                          =   654 
        self.cRCC1010_REG_P5MAP_ADR                          =   656 
        self.cRCC1010_REG_AMUX1MAP_ADR                       =   658 
        self.cRCC1010_REG_AMUX2MAP_ADR                       =   660 
        self.cRCC1010_REG_DIGIOPADSWRITE_ADR                 =   662 
        self.cRCC1010_REG_DIGIOPADSREAD_ADR                  =   664 
        self.cRCC1010_REG_DIGIOPADSIO_ADR                    =   666 
        self.cRCC1010_REG_DIGIOPADSPULL_ADR                  =   668 
        self.cRCC1010_REG_DIGIOPADSSLOPE_ADR                 =   670 
        self.cRCC1010_REG_LFSRCONTROL_ADR                    =   672 
        self.cRCC1010_REG_LFSR1POLY_ADR                      =   674 
        self.cRCC1010_REG_LFSR1STATE_ADR                     =   676 
        self.cRCC1010_REG_LFSR2POLY_ADR                      =   678 
        self.cRCC1010_REG_LFSR2STATE_ADR                     =   680 
        self.cRCC1010_REG_TESTDIGITAL_ADR                    =   682 
        self.cRCC1010_REG_TESTANALOG_ADR                     =   684 
        self.cRCC1010_REG_TESTDIGPADS_ADR                    =   686 
        self.cRCC1010_REG_TESTADCI_ADR                       =   688 
        self.cRCC1010_REG_TESTADCO_ADR                       =   690 
        self.cRCC1010_REG_TESTFQMCTRL_ADR                    =   692 
        self.cRCC1010_REG_TESTIRQVECSTART_ADR                =   694 
        self.cRCC1010_REG_TESTANALOGSPARE_ADR                =   696 
        self.cRCC1010_REG_ID1_ADR                            =   762 
        self.cRCC1010_REG_ID2_ADR                            =   764 
        self.cRCC1010_REG_ID3_ADR                            =   766 
        self.cRCC1010_REG_TXCONFIG0_ADR                      =   768 
        self.cRCC1010_REG_TXCONFIG1_ADR                      =   770 
        self.cRCC1010_REG_TXCONFIG2_ADR                      =   772 
        self.cRCC1010_REG_TXCONFIG3_ADR                      =   774 
        self.cRCC1010_REG_TXCONFIG4_ADR                      =   776 
        self.cRCC1010_REG_TXCONFIG5_ADR                      =   778 
        self.cRCC1010_REG_TXDUMMY1_ADR                       =   780 
        self.cRCC1010_REG_TXDUMMY2_ADR                       =   782 
        self.cRCC1010_REG_TXID1_ADR                          =   848 
        self.cRCC1010_REG_TXID2_ADR                          =   850 
        self.cRCC1010_REG_TXID3_ADR                          =   852 

