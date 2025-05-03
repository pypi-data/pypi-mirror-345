import  os
import  platform
import  sys
import  struct
from    numpy import *

__version__     =   "1.0.0"

class   DevRrn7745(object):

    def __init__(self, Rad, Mask):

        self.Rad                =   Rad
        self.Mask               =   Mask

        # Define Constants
        self.DefineConst()

        # Define Default register values
        self.RegTstI                        =   int("01111111",2)
        self.RegTstQ                        =   0
        self.RegLoI                         =   0
        self.RegLoQ                         =   0
        self.RegEnaMix                      =   0
        self.RegMux                         =   int("00010000",2)
        self.RegDc1                         =   0
        self.RegDc2                         =   0
        self.RegDc3                         =   0
        self.RegDc4                         =   0
        self.DevSetCfg()

    def SetCfg(self, dCfg):
        #   @function       SetCfg                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Set Device Configuration
        #   @param[in]      dCfg
        #                       TxChn:      Transmit channel
        #                       TxPwr:      Transmit clocks
        #                       RxEna:      Receive Enable (0-15) bit 0 Rx 0 etc
        if "TxChn" in dCfg:
            TxChn   =   int(dCfg["TxChn"])
            if TxChn < 0:
              TxChn         =     0
            if TxChn > 2:
              TxChn         =     2
            
            if "TxPwr" in dCfg:
                TxPwr   =   int(dCfg["TxPwr"])                
                if TxPwr < 0:
                    TxPwr       =     0
                if TxPwr > 63:
                    TxPwr       =     63
            
            if TxChn == 0:
                self.RegPa1     =   0
                self.RegPa2     =   0
                self.RegPaCon   =   0
            elif TxChn  == 1:
                self.RegPa1     =   TxPwr
                self.RegPa2     =   0
                self.RegPaCon   =   self.cReg_PaCon_MuxP1
            elif TxChn == 2:
                self.RegPa1     =   0
                self.RegPa2     =   TxPwr
                self.RegPaCon   =   self.cReg_PaCon_MuxP2                            
            else:
                self.RegPa1     =   0
                self.RegPa2     =   0
                self.RegPaCon   =   0

        if "TxMask" in dCfg:
            TxMask  =   int(dCfg["TxMask"])
            if "TxPwr" in dCfg:
                TxPwr   =   int(dCfg["TxPwr"])                
                if TxPwr < 0:
                    TxPwr       =     0
                if TxPwr > 63:
                    TxPwr       =     63
            
            self.RegPaCon       =   0
            if (TxMask & int(1)) > 0:
                self.RegPa1     =   TxPwr
                self.RegPaCon   =   self.RegPaCon + self.cReg_PaCon_MuxP1
            if (TxMask & int(2)) > 0:    
                self.RegPa1     =   TxPwr
                self.RegPaCon   =   self.RegPaCon + self.cReg_PaCon_MuxP2             


        if (int(self.Rad.DebugInf) & int('0xF0',0)) > 64:
            print("RPN7720 Registers:")
            print(" LoChain %d:", self.RegLoChain)
            print(" Pa1 %d:", self.RegPa1)
            print(" Pa2 %d:", self.RegPa2)
            print(" PaCon %d:", self.RegPaCon)
            print(" Mux %d:", self.RegMux)

    def SetRegCfg(self, dCfg):
        #   @function       SetCfg                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Set Device Configuration
        #   @param[in]      dCfg
        #                       LoChain:    LO Chain
        #                       Pa1:        Pa1
        #                       Pa2:        Pa2 
        #                       PaCon:      PaControl
        #                       Mux:        Mux                     
        if "LoChain" in dCfg:
            self.RegLoChain     =   dCfg["LoChain"]                     
        if "Pa1" in dCfg:
            self.RegPa1         =   dCfg["Pa1"]
        if "Pa2" in dCfg:
            self.RegPa2         =   dCfg["Pa2"]
        if "PaCon" in dCfg:
            self.RegPaCon       =   dCfg["PaCon"]
        if "Mux" in dCfg:
            self.RegMux         =   dCfg["Mux"] 
        
        if (int(self.Rad.DebugInf) & int('0xF0',0)) > 64:
            print("RPN7720 Registers:")
            print(" LoChain %d:", self.RegLoChain)
            print(" Pa1 %d:", self.RegPa1)
            print(" Pa2 %d:", self.RegPa2)
            print(" PaCon %d:", self.RegPaCon)
            print(" Mux %d:", self.RegMux)

    def DevSetCfg(self):
        # reset this function is currently not implemented
        pass

    def DevRst(self):
        # reset currently not implemented
        pass
    
    def DevEna(self):
        # enable currently not implemented
        pass

    def DevDi(self):
        # disable currently not implemented
        pass

    def DevSetReg(self, Regs):
        #   @function       SetCfg                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Set Device Configuration
        #   @param[in]      Regs: register values beeing programmed over spi
        if (int(self.Rad.DebugInf) & int('0xF0',0)) > 16: 
            print("RPN7720 DevSetReg")
        NReg            =   shape(Regs)
        NEntr           =   int(NReg[0])
        Data            =   zeros(NEntr + 2,dtype='uint32')
        Data[0]         =   self.Mask                       # Mask for device 
        Data[1]         =   1
        Data[2:]        =   Regs               
        CmdCod          =   int("0x9205", 0)
        RxData          =   self.Rad.CmdSend(0, CmdCod, Data)
        Ret             =   self.Rad.CmdRecv()
        if Ret[0] == False:
            print("Error RPN7720 DevSetReg")
        return Ret
    
    def DevGetReg(self, Regs):
        pass

    def IniCfg(self, dCfg):
        #   @function       Ini                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Programm initialization to device          
        self.SetCfg(dCfg)
        Ret     =   self.Ini();
        if Ret[0] == False:
            print("Error RPN7720: IniCfg")
        return Ret[0]

    def Ini(self):
        #   @function       Ini                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Initialize device configure registers   
        Data            =   self.GenRegs()
        Ret             =   self.DevSetReg(Data)
        return Ret[0]

    def GenRegs(self):
        #   @function       GenRegs                                                             
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2015-07-27          
        #   @brief          Generate registers for programming      
        Data            =   zeros(5,dtype='uint32')
        Val             =   self.cWriteVerify + self.cReg_LoChain_Adr*2**8 + self.RegLoChain
        Data[0]         =   Val
        Val             =   self.cWriteVerify + self.cReg_Pa1_Adr*2**8 + self.RegPa1
        Data[1]         =   Val
        Val             =   self.cWriteVerify + self.cReg_Pa2_Adr*2**8 + self.RegPa2
        Data[2]         =   Val
        Val             =   self.cWriteVerify + self.cReg_PaCon_Adr*2**8 + self.RegPaCon
        Data[3]         =   Val
        Val             =   self.cWriteVerify + self.cReg_Mux_Adr*2**8 + self.RegMux
        Data[4]         =   Val
        return Data

    def DefineConst(self):
        self.cReg_LoChain_Adr           =   int("0x0", 0)
        self.cReg_Pa1_Adr               =   int("0x1", 0)
        self.cReg_Pa2_Adr               =   int("0x2", 0)
        self.cReg_PaCon_Adr             =   int("0x4", 0)
        self.cReg_Mux_Adr               =   int("0x5", 0)
        self.cWriteVerify               =   2**15 + 2**14
        self.cReg_PaCon_MuxP1           =   3
        self.cReg_PaCon_MuxP2           =   3*16  
