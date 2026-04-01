import RVData
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time


tswapi = "http://127.0.0.1:31270"   
subid = 42
APIKey = ""
isDebugging=0
PU = 0

def SetSubID(value):
    global subid
    subid = value
    print("new value = ")
    print(subid)

def SetAPIKey(value):
    print("entered function")
    global APIKey
    APIKey = value
    global header
    header = {"DTGCommKey": APIKey }
def ChangePU(value):
    global PU
    PU = value

header = {"DTGCommKey": APIKey }
retry_strategy = Retry(  
    total=10,          
    backoff_factor=1,      
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False,
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH", "DELETE"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
request = requests.Session()
request.trust_env = False
request.mount("http://", adapter)
request.mount("https://", adapter)

LogFile = open("VehicleLog.txt","a")

def GetVehicleName(ObjectName):
    vname = ObjectName
    fname = vname
    vname = vname.split('_')
    aux = vname

    for i in range(len(vname)):
        if not vname[i].find("Class") == -1:
            return vname[i]
        if not vname[i].find("Car") == -1:
            return vname[i-1] +" " +  vname[i]
    if str(vname[1]) == "RVM":
        tstring = vname[0]
    if str(vname[1]) == "LBSP":
        return str(vname[2])
    else:
        if len(vname) > 3:
            tstring = vname[3]
        if tstring.isdigit():
            tstring = vname[2] + vname[3]
        elif tstring == "DB":
            if len(vname) >4:
                tstring = vname[4]
        elif tstring == "A":
            tstring = vname[2]
        elif tstring == "B":
            tstring = vname[2]
        elif tstring == "C":
            tstring = vname[2]
        if vname[1] == "E94":
                    tstring = vname[1]
        if vname[3] == "Coaches":
                    tstring = vname[4]
        if len(vname) > 4:
            if vname[4] == "Coaches":
                        tstring = vname[5]
    return tstring

class Vehicle:
    Name = ""
    BTT = 0 # brake query type for brake type
    BPT = 0 # brake query type so i dont do all of the variants on refresh
    BCT = 0 # same as BPT but for BC
    BrakeType = "N/A"
    BP = 0.0
    BC = 0.0
    isWagon = True
    TotalWeight = 0
    CargoWeight = 0
    index = 0
    DType = 0
    CType = 0
    isBackwards = False
    CHB = 0 #current handbrake value
    FLA = 0 #flipped angle cocks
    def __init__(self,Vname,index):
        self.Name = Vname
        #print(Vname)
        if RVData.VehicleData.get(Vname):
            #print("Vehicle found in dictionary")
            self.BTT = RVData.VehicleData[Vname]['BTT']
            self.BPT = RVData.VehicleData[Vname]['BPT']
            self.BCT = RVData.VehicleData[Vname]['BCT']
            self.isWagon = RVData.VehicleData[Vname]['isWagon']
            self.index = index
            self.DType= RVData.VehicleData[Vname]['DiType']
            #print(self.Name  + "\n")
            #print(self.index)
            self.TotalWeight = RVData.VehicleData[Vname]['Weight']
        else:
            self.FindData()
            self.index = index
        LogFile.write(f"Finished Constructor for Name = {self.Name}, index = {self.index} \n")

            
            


    def PrintData(self):
            return [self.Name, "BTT = " + str(self.BTT), "BPT = " + str(self.BPT),"BCT = " + str(self.BCT)]
    
    def ReturnSequence(self):
         
         return [self.Name, self.BrakeType, "BP: " + str(self.BP), "BC: " + str(self.BC), "Weight: " + str(self.TotalWeight)+"T", "Load: "+str(self.CargoWeight)+"T"]

    def GetCouplerType(self):
        if self.Name == "Sggmrss":
            self.CType = 5
        CData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index) + "/Coupler_F%20(Hook)/",headers = header).json()
        if not CData['Result'] == "Error":
            self.CType = 1
        else:
            CData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index) + "/Coupler_F/",headers = header).json()
            if not CData['Result'] == "Error":
                self.CType = 2
            else:
                CData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index) + "/Hook_F(Coupler)/",headers = header).json()
                if not CData['Result'] == "Error":
                    self.CType = 3
                else:
                    CData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index) + "/Coupler(Hook)_F/",headers = header).json()
                    if not CData['Result'] == "Error":
                        self.CType = 4
                    else:
                        LogFile.write("Error getting coupler type \n")
                        LogFile.flush()
        print(f"Coupler is {self.CType} \n")
        
    def UpdateData(self):
            HasError = 0
            BR = -1
            ReqData = 0
            LogFile.write(f"Running update for vehicle i = {self.index}, name = {self.Name} \n")
            #print("PU is " + str(PU))
            if self.BPT == 1:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[PU] + "", headers = header).json()
        
            if self.BPT == 2:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[PU]+ "", headers = header).json()
            
            if self.BPT == 3:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/HL." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if self.BPT == 4:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BrakePipe." + RVData.PressureUnit[PU] +"", headers = header).json()
            if not ReqData == 0:
                if not ReqData['Result'] == "Error":
                    self.BP = float(ReqData['Values'][RVData.PressureUnit[PU] ])
                    self.BP = round(self.BP,1)
            else:
                    LogFile.write(f"Error finding BP values for  vehicle {self.Name} \n")
                    LogFile.flush() 
                    HasError = 1
            ReqData = 0
            if self.BCT == 1:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder." + RVData.PressureUnit[PU]+ "", headers = header).json()    
            if self.BCT == 2:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if self.BCT == 3:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder2." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if self.BCT == 4:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1_2." + RVData.PressureUnit[PU]+ "", headers = header).json() 
            if self.BCT == 5:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/Brake Cylinder Volume A." + RVData.PressureUnit[PU]+ "", headers = header).json() 
            if self.BCT == 6:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation//Bremszylinder1." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if self.BCT == 7:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_2." + RVData.PressureUnit[PU]+ "", headers = header).json() 
            if self.BCT == 8:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BC_1." + RVData.PressureUnit[PU] +"", headers = header).json()
            if self.BCT == 9:
                ReqData == request.get(tswapi + "/get/CurrentFormation/" + str(self.index) +"/Simulation/BC_11_Complementary." + RVData.PressureUnit[PU] + "",headers = header).json()
            if not ReqData == 0:
                if not ReqData['Result'] == "Error":
                    self.BC = float(ReqData['Values'][RVData.PressureUnit[PU]])
                    self.BC = round(self.BC,1)
                else:
                    LogFile.write(f"Error finding BC values for  vehicle {self.Name} \n")
                    LogFile.flush() 
                    HasError = 1

            if self.BTT == 1:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    if not self.Name == "Laaers":
                        BR = ReqData['Values']['ReturnValue']
                        if BR:
                            self.BrakeType = "[P]"
                        else:
                            self.BrakeType = "[G]"
                    else:
                        BR = ReqData['Values']['ReturnValue']
                        if not BR:
                            self.BrakeType = "[P]"
                        else:
                            self.BrakeType = "[G]"
            if self.BTT == 2:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.Function.GetCurrentNotchIndex", headers = header).json()

                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR:
                        self.BrakeType = "[G]"
                    else:
                        self.BrakeType = "[P]"
            if self.BTT == 3:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 4:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeMode_Switch.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                            self.BrakeType = "[G]"
                    elif BR == 1:
                            self.BrakeType = "[P]"
                    elif BR == 2:
                            self.BrakeType = "[R]"
            if self.BTT == 5:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeMode.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 6:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 7:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Bogie1PassGoodsValve (Lever).Function.GetCurrentNotchIndex", headers = header).json()
                BR = ReqData['Values']['ReturnValue']
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Bogie2PassGoodsValve (Lever).Function.GetCurrentNotchIndex", headers = header).json()
                BR2 = ReqData['Values']['ReturnValue']
                if BR == BR2:
                    if BR == 0:
                        self.BrakeType = "[P]"
                    elif BR == 1:
                        self.BrakeType = "[G]"
                else:
                    if BR == 0:
                        self.BrakeType = "[P]"
                    elif BR == 1:
                        self.BrakeType = "[G]"
                    if BR2 == 0:
                        self.BrakeType += "[P]"
                    elif BR == 1:
                        self.BrakeType += "[G]"
            if self.BTT == 8:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeSelector_F.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 9:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 10:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeMode_F.Function.GetCurrentNotchIndex", headers = header).json()
                BR = ReqData['Values']['ReturnValue']
                if not ReqData['Result'] == "Error":
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 11:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeSelector_L.Function.GetCurrentNotchIndex", headers = header).json()
                BR = ReqData['Values']['ReturnValue']
                if not ReqData['Result'] == "Error":
                    if BR == 0:
                        self.BrakeType = "[P]"
                    elif BR == 1:
                        self.BrakeType = "[R]"
                    else:
                        self.BrakeType = "[R+Mg]"
            if self.BTT == 12:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/GPR_BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                BR = ReqData['Values']['ReturnValue']
                if not ReqData['Result'] == "Error":
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 13:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeSelector_R-MG.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[P]"
                    elif BR == 1:
                        self.BrakeType = "[R]"
                    elif BR == 2:
                        self.BrakeType = "[R+Mg]"
            if self.BTT == 14:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/GP_BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[P]"
                    elif BR == 1:
                        self.BrakeType = "[R]"
                    elif BR == 2:
                        self.BrakeType = "[R+Mg]"
            if self.BTT == 15:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/BrakeTimingSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BR = ReqData['Values']['ReturnValue']
                    if BR == 0:
                        self.BrakeType = "[G]"
                    elif BR == 1:
                        self.BrakeType = "[P]"
                    elif BR == 2:
                        self.BrakeType = "[R]"
            if self.BTT == 420:
                 ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_L.Function.GetCurrentNotchIndex", headers = header).json()
                 V1 = ReqData['Values']['ReturnValue']
                 ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_R.Function.GetCurrentNotchIndex", headers = header).json()
                 if not ReqData['Result'] == "Error":
                    V2 = ReqData['Values']['ReturnValue']
                 else:
                     V2 = 0
                 R = max(V1,V2)
                 if R:
                     BR = 0
                     self.BrakeType = "[G]"
                 else:
                     BR = 0
                     self.BrakeType = "[P]"
            if self.DType == 0:
                HasError = 1
            if self.DType == 1:
                TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributerCutOff/",headers = header).json()
                if TestData['Result'] == "Error":
                    HasError = 1
            if self.DType == 2:
                TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributerCutOut/",headers = header).json()
                if  TestData['Result'] == "Error":
                    HasError = 1
            if self.DType == 3:
                TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributorIsolatingValve/",headers = header).json()
                if  TestData['Result'] == "Error":
                    HasError = 1
            if self.DType == 5:
                TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index) + "/AirBrakeSelector_L",headers = header).json()
                if  TestData['Result'] == "Error":
                    HasError = 1
            if BR == -1:
                HasError = 1
            if self.isWagon:
                ReqData = request.get(tswapi+ "/get/CurrentFormation/" + str(self.index) + "/RailVehiclePhysicsComponent0.Function.GetMassOfCargo",headers = header).json()
                Cargo = int(ReqData['Values']['ReturnValue'])
                self.CargoWeight = Cargo/1000
                self.CargoWeight = round(self.CargoWeight,1)
                self.TotalWeight += self.CargoWeight
                self.TotalWeight = round(self.TotalWeight,1)
            if str(self.Name) == "BR218":
                        
                        if BR == 0:
                            self.BrakeType = "[G]"
                        elif BR == 1:
                            self.BrakeType = "[P]"
                        elif BR == 2:
                            self.BrakeType = "[P2]"
                        elif BR == 3:
                            self.BrakeType = "[R]"
            #self.GetCouplerType()
            return HasError
    def SetSubs(self):
        #Setting subs for BP  pressure
        if self.BPT == 0:
                request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBPFound1?Subscription=" + str(subid), headers = header)
                request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBPFound2?Subscription=" + str(subid), headers = header)
        if self.BPT == 1:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BPT == 2:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BPT == 3:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/HL." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/HL." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BPT == 4:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakePipe." + RVData.PressureUnit[0] +"?Subscription=" + str(subid), headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakePipe." + RVData.PressureUnit[1] +"?Subscription=" + str(subid), headers = header)
        #subs for BC pressure

        if self.BCT == 0:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/NOBCFOUND1?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/NOBCFOUND@?Subscription=" + str(subid), headers = header)
        if self.BCT == 1:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 2:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 3:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder2." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder2." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 4:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1_2." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1_2." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 5:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/Brake Cylinder Volume A." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/Brake Cylinder Volume A." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 6:
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation//Bremszylinder1." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation//Bremszylinder1." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 7:
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_2." + RVData.PressureUnit[0]+ "?Subscription=" + str(subid), headers = header)
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_2." + RVData.PressureUnit[1]+ "?Subscription=" + str(subid), headers = header)
        if self.BCT == 8:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BC_1." + RVData.PressureUnit[0] +"?Subscription=" + str(subid), headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BC_1." + RVData.PressureUnit[1] +"?Subscription=" + str(subid), headers = header)
        if self.BCT == 9:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Simulation/BC_11_Complementary." + RVData.PressureUnit[0] + "?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Simulation/BC_11_Complementary." + RVData.PressureUnit[1] + "?Subscription=" + str(subid),headers = header)
        #subs for BTT
        if self.BTT == 0:
            self.BrakeType = "[?]"
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBSW?Subscription=" + str(subid), headers = header)
        if self.BTT == -1:
            self.BrakeType = "[?]"
            #print("no switch")
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBSW?Subscription=" + str(subid), headers = header)
        if self.BTT == 1:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 2:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 3:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 4:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeMode_Switch.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 5:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeMode.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 6:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 7:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Bogie1PassGoodsValve (Lever).Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Bogie2PassGoodsValve (Lever).Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 8:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeSelector_F.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 9:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 10:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeMode_F.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 11:
            request.post(tswapi + "/subscription/CurrentFormation/"+ str(self.index) + "/BrakeSelector_L.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header).json() 
        if self.BTT == 12:
            request.post(tswapi + "/subscription/CurrentFormation/" +  str(self.index) + "/GPR_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header).json()
        if self.BTT == 13:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/BrakeSelector_R-MG.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 14:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/GP_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 15:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/BrakeTimingSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.BTT == 420:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_L.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_R.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributerCutOff/",headers = header).json()
        if self.DType == 1:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributerCutOff.Function.GetCurrentNotchIndex?Subscription=" + str(subid),headers = header)
        if self.DType == 2:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/DistributerCutOut.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
        if self.DType == 3:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributorIsolatingValve.Function.GetCurrentNotchIndex?Subscription=" + str(subid),headers = header)
        if self.DType == 0:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NODistributor?Subscription=" + str(subid),headers = header)
        if self.DType == 4:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributorCutOff.Function.GetCurrentNotchIndex?Subscription=" + str(subid),headers = header)
        if self.DType == 5:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Simulation/Distributor%20CutOff.ValvePosition?Subscription=" + str(subid),headers = header)
        if  self.Name == "Sdggmrss738":
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AngleCock.Function.GetCurrentOutputValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AngleCock_B.Function.GetCurrentOutputValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AirHose_BP_F.Function.IsAirHoseConnected?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AirHose_BP_B.Function.IsAirHoseConnected?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Handbrake.Property.TertiaryValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/BrakePhysicsSimulation.Function.GetWheelTemperatureState?Subscription=" + str(subid),headers = header)
        elif self.Name == "Sggmrss":
            print("here")
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AngleCock_L.Function.GetCurrentOutputValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AngleCock_R.Function.GetCurrentOutputValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AirHose_BP_F.Function.IsAirHoseConnected?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AirHose_BP_B.Function.IsAirHoseConnected?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Handbrake.Property.TertiaryValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/BrakePhysicsSimulation.Function.GetWheelTemperatureState?Subscription=" + str(subid),headers = header)
        else:
            print("idk")
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AngleCock_F.Function.GetCurrentOutputValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AngleCock_B.Function.GetCurrentOutputValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AirHose_F.Function.IsAirHoseConnected?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/AirHose_B.Function.IsAirHoseConnected?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Handbrake.Property.TertiaryValue?Subscription=" + str(subid),headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/BrakePhysicsSimulation.Function.GetWheelTemperatureState?Subscription=" + str(subid),headers = header)
            
    def GetBrakeEditor(self):
        if self.BTT == 0:
            return 4
        if self.BTT == -1:
            return 4
        if self.Name == "BR218":
            return 3
        if self.Name == "Kijls":
            return 1
        if self.Name == "Kijls450":
            return 1
        if self.Name == "BR140":
            return 1
        if self.Name == "Bpmmbdzf":
            return 2
        if self.Name == "Bpmmbdzf":
            return 2
        if self.BTT == 1:
            return 1
        if self.BTT == 2:
            return 1
        if self.BTT == 11:
            return 2
        if self.BTT == 13:
            return 2
        if self.BTT == 14:
            return 2
        return 0
    def GetBM(self,BI,BI2 = 0):
        Bstr = "N/A"
        if self.Name == "Bpmmbdzf":
            if BI == 0:
                return "[P]"
            if BI == 1 :
                return "[R]"
            elif BI == 2:
                return "[R+Mg]"
        if self.Name == "Bpmbdzf":
            if BI == 0:
                return "[P]"
            if BI == 1 :
                return "[R]"
            elif BI == 2:
                return "[R+Mg]"
        if self.Name == "BR218":    
            if BI== 0:
                return  "[G]"
            elif BI == 1:
                return  "[P]"
            elif BI == 2:
                return  "[P2]"
            elif BI == 3:
                return  "[R]"
        if self.BTT == 0:
            return "[?]"
        if self.BTT == -1:
            return "[?]"
        if self.BTT == 1:
            if not self.Name == "Laaers":
                if not BI:
                    return "[G]"
                else:
                    return "[P]"
            else:
                if  BI:
                    return "[G]"
                else:
                    return "[P]"
        if self.BTT == 2:
            if not BI:
                #print(f"brakeisp")
                return "[P]"
            else:
                return "[G]"
        if self.BTT == 3:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 4:
            if str((self.Name)) == "BR218":
                if BI == 0 :
                    return "[G]"
                elif BI == 1:
                    return "[P]"
                elif BI == 2:
                    return "[P2]"
                elif BI == 3:
                    return "[R]"
            else:
                if BI == 0 :
                    return "[G]"
                elif BI == 1:
                    return "[P]"
                elif BI == 2:
                    return "[R]"
        if self.BTT == 5:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 6:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 7:
            if BI == BI2:
                    if BI == 0:
                        Bstr = "[P]"
                    elif BI == 1:
                        Bstr = "[G]"
            else:
                    if BI == 0:
                        Bstr = "[P]"
                    elif BI == 1:
                        Bstr = "[G]"
                    if BI2 == 0:
                        Bstr += "[P]"
                    elif BI2 == 1:
                        Bstr += "[G]"
            return Bstr
        if self.BTT == 8:
            if BI == 0 :
                    return "[G]"
            elif BI == 1:
                    return "[P]"
            elif BI == 2:
                    return "[R]"
        if self.BTT == 9:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 10:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 11:
            if BI == 0:
                return "[G]"
            if BI == 1 :
                return "[P]"
            elif BI == 2:
                return "[R]"
            elif BI == 3:
                return "[R+Mg]"
        if self.BTT == 12:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 13:
            if BI == 0 :
                return "[P]"
            elif BI == 1:
                return "[R]"
            elif BI == 2:
                return "[R+Mg]"
        if self.BTT == 14:
            if BI == 0 :
                return "[P]"
            elif BI == 1:
                return "[R]"
            elif BI == 2:
                return "[R+Mg]"
        if self.BTT == 15:
            if BI == 0 :
                return "[G]"
            elif BI == 1:
                return "[P]"
            elif BI == 2:
                return "[R]"
        if self.BTT == 420:
            if BI == 0:
                if BI2 == 1:
                    return "[P]"
                else:
                    return "[G]"
            if BI == 1:
                return "[P]"
        return Bstr
    def GetPBM(self): #GetPossibleBrakeModes
        if self.Name == "Kijls":
            return ["G","P"]
        if self.Name == "Kijls450":
            return ['G',"P"]
        if self.Name == "BR140":
            return ["G","P"]
        if self.Name == "Bpmmbdzf":
            return ["P","R","R+Mg"]
        if self.Name == "Bpmmbdzf":
            return ["P","R","R+Mg"]
        if self.BTT == -1:
            return ["G"]
        if self.BTT == 0:
            return ["[?]"]
        if self.Name == "BR218":
                return ["G","P","P2","R"]
        if self.BTT == 1:
            if not self.Name == "Laaers":
                return ["G","P"]
            else:
                return ["P","G"]
        if self.BTT == 2:
            return ["G","P"]
        if self.BTT == 3:
            return ["G","P","R"]
        if self.BTT == 4:
                return ["G", "P","R"]
        if self.BTT == 5:
            return ["G","P","R"]
        if self.BTT == 6:
            return ["G","P","R"]
        if self.BTT == 7:
            return ["G","P"]
        if self.BTT == 8:
            return ["G","P","R"]
        if self.BTT == 9:
            return ["G","P","R"]
        if self.BTT == 10:
            return ["G","P","R"]
        if self.BTT == 11:
            return ["G", "P","R","R+Mg"]
        if self.BTT == 12:
            return ["G","P","R"]
        if self.BTT == 13:
            return ["P","R","R+Mg"]
        if self.BTT == 14:
            return ["P","R","R+Mg"]
        if self.BTT == 15:
            return ["G","P","R"]
        if self.BTT == 420:
            return ["G","P"]
        return  ["?"]
    def GetBMInt(self):
        if self.Name == "Bpmmbdzf":
            if self.BrakeType == "[P]":
                return 0
            if self.BrakeType == "[R]":
                return 1
            if self.BrakeType == "[R+Mg]":
                return 2
        if self.Name == "Bpmbdzf":
            if self.BrakeType == "[P]":
                return 0
            if self.BrakeType == "[R]":
                return 1
            if self.BrakeType == "[R+Mg]":
                return 2
        if self.BTT == -1:
            return 0
        if self.BTT == 0:
            return 0
        if self.Name == "BR218":
            if self.BrakeType == "[G]":
                return 0
            if self.BrakeType == "[P]":
                return 1
            if self.BrakeType == "[P2]":
                return 2
            if self.BrakeType == "[R]":
                return 3
        if self.BTT == 4:
            if self.BrakeType == "[G]":
                return 0
            if self.BrakeType == "[P]":
                return 1
            if self.BrakeType =="[R]":
                return 2
        if self.BTT == 11:
            if self.BrakeType == "[G]":
                return 0
            if self.BrakeType == "[P]":
                return 1
            if self.BrakeType == "[R]":
                return 2
            if self.BrakeType == "[R+Mg]":
                return 3
        if self.BTT == 13:
            if self.BrakeType == "[P]":
                return 0
            if self.BrakeType == "[R]":
                return 1
            if self.BrakeType == "[R+Mg]":
                return 2
        if self.BTT == 14:
            if self.BrakeType == "[P]":
                return 0
            if self.BrakeType == "[R]":
                return 1
            if self.BrakeType == "[R+Mg]":
                return 2
        if self.Name == "Laaers":
            if self.BrakeType == "[G]":
                return 1
            if self.BrakeType == "[P]":
                return 0
        if self.BTT == 420:
            if self.BrakeType == "[G]":
                return 0
            else:
                return 1
        if self.BTT == 2:
            if self.BrakeType == "[G]":
                return 1
            if self.BrakeType == "[P]":
                return 0
        if self.BrakeType == "[G]":
            return 0
        if self.BrakeType == "[P]":
            return 1
        if self.BrakeType =="[R]":
            return 2
        return 0

    def GetBMInt2(self,Brake):
        if self.Name == "Bpmmbdzf":
            if Brake == "[P]":
                return 0
            if Brake == "[R]":
                return 1
            if Brake == "[R+Mg]":
                return 2
        if self.Name == "Bpmbdzf":
            if Brake == "[P]":
                return 0
            if Brake == "[R]":
                return 1
            if Brake == "[R+Mg]":
                return 2
        if self.BTT == -1:
            return 0
        if self.BTT == 0:
            return 0
        if self.Name == "BR218":
            if Brake == "[G]":
                return 0
            if Brake == "[P]":
                return 1
            if Brake == "[P2]":
                return 2
            if Brake == "[R]":
                return 3
        if self.BTT == 4:
            if Brake == "[G]":
                return 0
            if Brake == "[P]":
                return 1
            if Brake =="[R]":
                return 2
        if self.BTT == 11:
            if Brake == "[G]":
                return 0
            if Brake == "[P]":
                return 1
            if Brake == "[R]":
                return 2
            if Brake == "[R+Mg]":
                return 3
        if self.BTT == 13:
            if Brake == "[P]":
                return 0
            if Brake == "[R]":
                return 1
            if Brake == "[R+Mg]":
                return 2
        if self.BTT == 14:
            if Brake == "[P]":
                return 0
            if Brake == "[R]":
                return 1
            if Brake == "[R+Mg]":
                return 2
        if self.Name == "Laaers":
            if Brake == "[G]":
                return 1
            if Brake == "[P]":
                return 0
        if self.BTT == 420:
            if Brake == "[G]":
                return 0
            else:
                return 1
        if self.BTT == 2:
            if Brake == "[G]":
                return 1
            if Brake == "[P]":
                return 0
        if Brake == "[G]":
            return 0
        if Brake == "[P]":
            return 1
        if Brake =="[R]":
            return 2
        return 0
    def GetDstr(self,Didx):
        if self.Name == "780pza":
            if Didx:
                return "Closed"
            else:
                return "Open"
        if self.Name == "785pza":
            if Didx:
                return "Closed"
            else:
                return "Open"
        if self.Name == "766pbzfa":
            if Didx:
                return "Closed"
            else:
                return "Open"
        if self.Name == "780pza":
            if Didx:
                return "Closed"
            else:
                return "Open"
        if self.Name == "FCA":
            if Didx:
                return "Closed"
            else:
                return "Open"
        if self.DType == 1:
            if Didx:
                return "Open"
            else:
                return "Closed"
        if self.DType == 4:
            if Didx:
                return "Open"
            else:
                return "Closed"
        else:
            if Didx:
                return "Closed"
            else:
                return  "Open"
            
    def SetBM(self,Brake):
        BIndex = self.GetBMInt2(Brake)
        print(f"Bindex = {BIndex}")
        if not self.BTT == 11:
            if not self.BTT == 5:
                if BIndex == 1:
                    BIndex = 0.5
        if self.BTT == -1:
            return 0
        if self.BTT == 0:
            return 0
        if self.BTT == 1:

            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 2:
                if BIndex:
                    BIndex = 0
                else:
                    BIndex = 1
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.InputValue?Value=" + str(BIndex),headers = header)
                
        if self.BTT == 3:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 4:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode_Switch.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode_Switch.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode_Switch.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 5:
            if self.Name == "BR218":
                if BIndex == 1:
                    BIndex = 0.33
                if BIndex == 2:
                    BIndex = 0.5
                if BIndex == 3:
                    BIndex = 3
            else:
                if BIndex == 1:
                    BIndex = 0.5
                if BIndex == 2:
                    BIndex = 1
            try:
                print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode.InputValue?Value=" + str(BIndex),headers = header).url)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 6:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 7:
            if BIndex:
                BIndex = 0
            else:
                BIndex = 1
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/Bogie1PassGoodsValve (Lever).InputValue?Value=" + str(BIndex),headers = header)
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/Bogie2PassGoodsValve (Lever).InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/Bogie1PassGoodsValve (Lever).InputValue?Value=" + str(BIndex),headers = header)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/Bogie2PassGoodsValve (Lever).InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/Bogie1PassGoodsValve (Lever).InputValue?Value=" + str(BIndex),headers = header)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/Bogie2PassGoodsValve (Lever).InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 8:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_F.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_F.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_F.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 9:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 10:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode_F.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode_F.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeMode_F.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 11:
            if not self.Name == "Bpmmbdzf":
                if BIndex == 1:
                    BIndex = 0.33
                if BIndex == 2:
                    BIndex = 0.66
                if BIndex == 3:
                    BIndex = 1
            else:
                if BIndex == 1:
                    BIndex = 0.5
                if BIndex == 2:
                    BIndex = 1
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_L.InputValue?Value=" + str(BIndex),headers = header)
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_R.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_L.InputValue?Value=" + str(BIndex),headers = header)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_R.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_L.InputValue?Value=" + str(BIndex),headers = header)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_R.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 12:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/GPR_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/GPR_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/GPR_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 13:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_R-MG.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_R-MG.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeSelector_R-MG.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 14:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/GP_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/GP_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/GP_BrakeSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 15:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeTimingSelector.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeTimingSelector.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/BrakeTimingSelector.InputValue?Value=" + str(BIndex),headers = header)
        if self.BTT == 420:
            try:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_L.InputValue?Value=" + str(BIndex),headers = header)
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_R.InputValue?Value=" + str(BIndex),headers = header)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)
                try :
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_L.InputValue?Value=" + str(BIndex),headers = header)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_R.InputValue?Value=" + str(BIndex),headers = header)
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_L.InputValue?Value=" + str(BIndex),headers = header)
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_R.InputValue?Value=" + str(BIndex),headers = header)
        
        return 1
    def SetDistrib(self,Value):
        print(Value)
        if Value == "[Close]":
            Value = 0
        else:
            Value = 1
        Value = int(Value)
        print(Value)
        if self.DType:
            if self.Name == "FCA":
                if Value:
                    Value = 0
                else:
                    Value = 1
            if self.DType == 2:
                if Value:
                    Value = 0
                else:
                    Value = 1
            elif self.DType == 3:
                if Value:
                    Value = 0
                else:
                    Value = 1
            elif self.DType == 5:
                if Value:
                    Value = 0
                else:
                    Value = 1
            elif self.Name == "780pza":
                if Value:
                    Value = 0
                else:
                    Value = 1
            elif self.Name == "785pza":
                if Value:
                    Value = 0
                else:
                    Value = 1
            elif self.Name == "766pbzfa":
                if Value:
                    Value = 0
                else:
                    Value = 1
            print(f"Final Value {Value}")
            if self.DType == 1:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/DistributerCutOff.InputValue?Value="+str(Value), headers = header)
            if self.DType == 2:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/DistributerCutOut.InputValue?Value="+str(Value), headers = header)
            if self.DType == 3:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/DistributorIsolatingValve.InputValue?Value="+str(Value), headers = header)
            if self.DType == 4:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/DistributorCutOff.InputValue?Value="+str(Value), headers = header)
            if self.DType == 5:
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AirBrakeSelector_L.InputValue?Value="+str(Value), headers = header)
                request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AirBrakeSelector_R.InputValue?Value="+str(Value), headers = header)
    def ChangeCoupling(self,selection,side):
        #Function.PerformManualCouple
        if not self.CType == 5:
            if self.isBackwards:
                    if side == 1:
                        side = 0
                    else:
                        side = 1
            if selection == 0:
                if side == 0:
                    if self.CType == 1:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_B%20(Hook).Function.PerformManualCouple",headers = header)
                    if self.CType == 2:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_B.Function.PerformManualCouple",headers = header)
                    if self.CType == 3:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Hook_B(Coupler).Function.PerformManualCouple",headers = header)
                    if self.CType == 4:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler(Hook)_B.Function.PerformManualCouple",headers = header)
                if side == 1:
                    if self.CType == 1:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_F%20(Hook).Function.PerformManualCouple",headers = header)
                    if self.CType == 2:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_F.Function.PerformManualCouple",headers = header)
                    if self.CType == 3:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Hook_F(Coupler).Function.PerformManualCouple",headers = header)
                    if self.CType == 4:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler(Hook)_F.Function.PerformManualCouple",headers = header)
            else:
                if side == 0:
                    if self.CType == 1:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_B%20(Hook).Function.PerformManualUncouple",headers = header).json()
                    if self.CType == 2:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_B.Function.PerformManualUncouple",headers = header)
                    if self.CType == 3:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Hook_B(Coupler).Function.PerformManualUncouple",headers = header)
                    if self.CType == 4:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler(Hook)_B.Function.PerformManualUncouple",headers = header)
                if side == 1:
                    if self.CType == 1:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_F%20(Hook).Function.PerformManualUncouple",headers = header).json()
                    if self.CType == 2:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler_F.Function.PerformManualUncouple",headers = header).json()
                    if self.CType == 3:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Hook_F(Coupler).Function.PerformManualUncouple",headers = header)
                    if self.CType == 4:
                        request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler(Hook)_F.Function.PerformManualUncouple",headers = header)
        else:
            if selection == 0:
                request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler.Function.PerformManualCouple",headers = header)
            else:
                request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Coupler.Function.PerformManualUncouple",headers = header)     
    def ChangeAngleCock(self,position,side):
        print(f"Values are {position} and {side}")
        if self.Name == "Sggmrss":
            if self.FLA:
                if side:
                    side = 0
                else:
                    side = 1
            if side == 1: #L
                if  position == "[Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=1",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=1",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=1",headers = header).json())
                if position == "[Partially Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=0.5",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=0.5",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=0.5",headers = header).json())
                if position == "[Closed]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_L.InputValue?Value=0",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "AngleCock_L.InputValue?Value=0",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "AngleCock_L.InputValue?Value=0",headers = header).json())
            if side == 0: #R
                if  position == "[Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_R.InputValue?Value=1",headers = header)
                if position == "[Partially Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_R.InputValue?Value=0.5",headers = header)
                if position == "[Closed]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_R.InputValue?Value=0",headers = header)
        elif self.name == "Sdggmrss738":
            if side == 1:
                if  position == "[Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=1",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=1",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=1",headers = header).json())
                if position == "[Partially Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=0.5",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=0.5",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=0.5",headers = header).json())
                if position == "[Closed]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock.InputValue?Value=0",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "AngleCock.InputValue?Value=0",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "AngleCock.InputValue?Value=0",headers = header).json())
        else:
            if side == 1:
                if  position == "[Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=1",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=1",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=1",headers = header).json())
                if position == "[Partially Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=0.5",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=0.5",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=0.5",headers = header).json())
                if position == "[Closed]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_F.InputValue?Value=0",headers = header)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "AngleCock_F.InputValue?Value=0",headers = header).url)
                    print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "AngleCock_F.InputValue?Value=0",headers = header).json())
            if side == 0:
                if  position == "[Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_B.InputValue?Value=1",headers = header)
                if position == "[Partially Open]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_B.InputValue?Value=0.5",headers = header)
                if position == "[Closed]":
                    request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/AngleCock_B.InputValue?Value=0",headers = header)
    def ChangeHandbrake(self,targetvalue):
        targetvalue = targetvalue.replace("[","")
        targetvalue = targetvalue.replace("]","")
        targetvalue = int(targetvalue)
        cv = int(self.CHB)
        if targetvalue > cv:
            for i in range(int(cv),targetvalue*5):
                print(f"doing i = {i} iteration")
                request.patch(tswapi+ "/set/CurrentFormation/" + str(self.index) + "/Handbrake.InputValue?Value=1000" ,headers = header)
                time.sleep(0.5)
        else:
            for i in range(0,(cv-targetvalue)*5):
                print(f"doing i = {i} iteration")
                request.patch(tswapi+ "/set/CurrentFormation/" + str(self.index) + "/Handbrake.InputValue?Value=-1000" ,headers = header)
                time.sleep(0.5)
    def FindData(self):
        index = self.index
        BTT = 0
        BPT = 0
        BCT = 0
        isWagon = True
        Weight = 0
        DType = 0
        ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[PU]+ "", headers = header).json()
        if not ReqData['Result'] == "Error":
            BPT = 1
        else:
            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if not ReqData['Result'] == "Error":
                BPT = 2
            else:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/HL." + RVData.PressureUnit[PU]+ "", headers = header).json()
                if not ReqData['Result'] == "Error" :
                    BPT = 3
                else:
                    ReqData = request.get(tswapi + "/list/CurrentFormation/" + str(index) +"/Simulation/Brakepipe/",headers = header).json()
                    if not ReqData['Result'] == "Error":
                        BPT = 4
                    else:
                        LogFile.write("BP not found for vehicle with id " + str(index) + "\n" )
                        LogFile.flush() # Add this line

        
        ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/BrakeCylinder." + RVData.PressureUnit[PU]+ "", headers = header).json() 
        if not ReqData['Result'] == "Error":
            BCT = 1
        else:
            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/BrakeCylinder_1." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if not ReqData['Result'] == "Error":
                BCT = 2
            else:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/BrakeCylinder2." + RVData.PressureUnit[PU]+ "", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BCT = 3
                else:
                    ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/BrakeCylinder_1_2." + RVData.PressureUnit[PU]+ "", headers = header).json() 
                    if not ReqData['Result'] == "Error":
                        BCT = 4
                    else:
                        ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/Brake Cylinder Volume A." + RVData.PressureUnit[PU]+ "", headers = header).json() 
                        if not ReqData['Result'] == "Error":
                            BCT = 5
                        else:
                            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation//Bremszylinder1." + RVData.PressureUnit[PU]+ "", headers = header).json()
                            if not ReqData['Result'] == "Error":
                                BCT = 6
                            else:
                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Simulation/BrakeCylinder_2." + RVData.PressureUnit[PU]+ "", headers = header).json() 
                                if not ReqData['Result'] == "Error":
                                    BCT = 7
                                else:
                                    ReqData = request.get(tswapi + "/list/CurrentFormation/" + str(index) +"/Simulation/BC_1/",headers = header).json()
                                    if not ReqData['Result'] == "Error":
                                        BCT = 8
                                    else:
                                        ReqData = request.get(tswapi + "/list/CurrentFormation/" + str(index) +"/Simulation/BC_11_Complementary/",headers = header).json()
                                        if not ReqData['Result'] == "Error":
                                            BCT = 9
                                        else:
                                            LogFile.write("Couldnt find BC for vehicle with index" + str(index) + "\n")
                                            LogFile.flush() # Add this line
        
        # finding brake mode
        
        ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/G%2fP_BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
        if not ReqData['Result'] == "Error":
                BTT = 1
            
        else:
            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/PassengerGoodsValve.Function.GetCurrentNotchIndex", headers = header).json()
            if not ReqData['Result'] == "Error":
                    BTT = 2
                    
            else:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                if not ReqData['Result'] == "Error":
                    BTT = 3
                    
                else:
                    ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeMode_Switch.Function.GetCurrentNotchIndex", headers = header).json()
                    if not ReqData['Result'] == "Error":
                        BTT = 4
                        
                    else:
                        ReqData  = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeMode.Function.GetCurrentNotchIndex", headers = header).json()
                        if not ReqData['Result'] == "Error":
                            BTT = 5
                            
                        else:
                            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                            if not ReqData['Result'] == "Error":
                                BTT = 6
                            
                            else:
                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/Bogie1PassGoodsValve (Lever).Function.GetCurrentNotchIndex", headers = header).json()
                                if not ReqData['Result'] == "Error":
                                    BTT = 7
                                else:
                                    ReqData = ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeSelector_F.Function.GetCurrentNotchIndex", headers = header).json()
                                    if not ReqData['Result'] == "Error":
                                        BTT = 8
                                        
                                    else:
                                        ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                                        if not ReqData['Result'] == "Error":
                                            BTT = 9
                                        else:
                                            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeMode_F.Function.GetCurrentNotchIndex", headers = header).json()
                                            if not ReqData['Result'] == "Error":
                                                BTT = 10
                                            else:
                                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeSelector_L.Function.GetCurrentNotchIndex", headers = header).json()
                                                if not ReqData['Result'] == "Error":
                                                    BTT = 11
        
                                                else:
                                                    ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/GPR_BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                                                    if not ReqData['Result'] == "Error":
                                                        BTT = 12
                                                        
                                                    else:
                                                        ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/BrakeSelector_R-MG.Function.GetCurrentNotchIndex", headers = header).json()
                                                        if not ReqData['Result'] == "Error":
                                                            BTT = 13
                                                            
                                                        else:
                                                            ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(index) + "/GP_BrakeSelector.Function.GetCurrentNotchIndex", headers = header).json()
                                                            if not ReqData['Result'] == "Error":
                                                                BTT = 14
                                                                request.post(tswapi + "/subscription/CurrentFormation/" + str(index) + "/GP_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=" + str(subid), headers = header)
                                                            else:
                                                                
                                                                if not ReqData['Result'] == "Error":
                                                                    BTT = 15
                                                                    
                                                                    LogFile.write("BrakeMode not found for vehicle \n")
                                                                    LogFile.flush()
        TestData = request.get(tswapi + "/list/CurrentFormation/" + str(index)+ "/DistributerCutOff/",headers = header).json()
        if not TestData['Result'] == "Error":
                DType = 1
        else:
            TestData = request.get(tswapi + "/list/CurrentFormation/" + str(index)+ "/DistributerCutOut/",headers = header).json()
            if not TestData['Result'] == "Error":
                    Dtype = 2
            else:
                TestData = request.get(tswapi + "/list/CurrentFormation/" + str(index)+ "/DistributorIsolatingValve/",headers = header).json()
                if not TestData['Result'] == "Error":
                        DType = 3
                else:
                    TestData = request.get(tswapi + "/list/CurrentFormation/" + str(index) + "/DistributorCutOff/", headers = header).json()
                    if not TestData['Result'] == "Error":
                        DType = 4
                    else:
                        TestData = request.get(tswapi + "/list/CurrentFormation/" + str(index) + "/AirBrakeSelector_R/", headers = header).json()
                        if not TestData['Result'] == "Error":
                            DType = 5
                        LogFile.write("Distributor Valve not found for Vehicle \n")
                        LogFile.flush()
        self.BTT = BTT
        self.BPT = BPT
        self.BCT = BCT
        self.DType = DType

