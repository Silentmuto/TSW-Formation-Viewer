import wx
import requests
import json
import time
import RVData # pyright: ignore[reportMissingImports]
import threading
import sys
from datetime import datetime
import wx.dataview
import psutil
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path

#subscription id = 42
#add reverse display

ListCtrlID = 2
OnTopToggleID = 3
OnTrTogID = 4
PressureChoiceID = 5
BrakeChoiceID = 6
Toggle5ID = 7
ToggleAllID = 8
DstrID = 9
PU = 0
tswapi = "http://127.0.0.1:31270"   
now = datetime.now()

#searching for the key
documents_path = Path.home() / "Documents/My Games/TrainSimWorld6/Saved/Config" 
abc = str(documents_path)
abc = abc + "/CommAPIKey.txt"
print(f"The path is: {abc}")
apifile = open(abc ,"r")
ApiKey = apifile.read()

header = {"DTGCommKey": ApiKey }
retry_strategy = Retry(  
    total=None,          
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
LogFile = open("log.txt", "a")
LogFile.write(str(now))
LogFile.write("\n")
LogFile.flush() 

def IsTSWOpen():
    for p in psutil.process_iter():
       if p.name()  == 'TrainSimWorld.exe':
            return 1
    return 0


def GetVehicleName(ObjectName):
    vname = ObjectName
    fname = vname
    vname = vname.split('_')
    if str(vname[1]) == "RVM":
        tstring = vname[0]
    else:
        tstring = vname[3]
        if tstring.isdigit():
            tstring = vname[2] + vname[3]
        elif tstring == "DB":
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
        if vname[4] == "Coaches":
                    tstring = vname[5]
    return tstring

class Vehicle:
    Name = ""
    BTT = 0 # brake query type for brake type
    BPT = 0 # brake query type so i dont do all of the variants on refresh
    BCT = 0 # same as BPT but for BC
    BrakeType = ""
    BP = 0.0
    BC = 0.0
    isWagon = True
    TotalWeight = 0
    CargoWeight = 0
    index = 0
    DType = 0
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
            #print(self.Name  + "\n")
            #print(self.index)
            self.TotalWeight = RVData.VehicleData[Vname]['Weight']
        else:
            FoundData = FindData(index)
            self.BTT = FoundData[0]
            self.BPT = FoundData[1]
            self.BCT = FoundData[2]
            self.index = index
            #print(f"BCT FOund is {self.BCT}")
            self.isWagon = FoundData[3]
            self.TotalWeight = FoundData[4]
        LogFile.write(f"Finished Constructor for Name = {self.Name}, index = {self.index} \n")

            
            

    def PrintData(self):
         if not self.isWagon:
            return [self.Name, "BTT = " + str(self.BTT), "BPT = " + str(self.BPT),"BCT = " + str(self.BCT)]
         else:
            return [self.Name, "BTT = " + str(self.BTT), "BPT = " + str(self.BPT),"BCT = " + str(self.BCT)]
    
    def ReturnSequence(self):
         return [self.Name, self.BrakeType, "BP: " + str(self.BP), "BC: " + str(self.BC), "Weight: " + str(self.TotalWeight)+"T", "Load: "+str(self.CargoWeight)+"T"]
       
    def UpdateData(self):
            HasError = 0
            BR = -1
            LogFile.write(f"Running update for vehicle i = {self.index}, name = {self.Name} \n")
            #print("PU is " + str(PU))
            if self.BPT == 1:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[PU] + "", headers = header).json()
        
            if self.BPT == 2:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[PU]+ "", headers = header).json()
            
            if self.BPT == 3:
                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.index) + "/Simulation/HL." + RVData.PressureUnit[PU]+ "", headers = header).json()
            if not ReqData['Result'] == "Error":
                self.BP = float(ReqData['Values'][RVData.PressureUnit[PU] ])
                self.BP = round(self.BP,1)
            else:
                LogFile.write(f"Error finding BP values for  vehicle {self.Name} ")
                LogFile.flush() 
                HasError = 1
            
            LogFile.write(f"\n HasError after BP = {HasError} \n")
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
            if not ReqData['Result'] == "Error":
                self.BC = float(ReqData['Values'][RVData.PressureUnit[PU]])
                self.BC = round(self.BC,1)
            else:
                LogFile.write(f"Error finding BC values for  vehicle {self.Name} ")
                LogFile.flush() 
                HasError = 1
            LogFile.write(f"\n HasError after BC = {HasError} \n")

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
                 V2 = ReqData['Values']['ReturnValue']
                 R = max(V1,V2)
                 if R:
                     BR = 0
                     self.BrakeType = "[G]"
                 else:
                     BR = 0
                     self.BrakeType = "[P]"
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
            LogFile.write(str(self.BTT) + "for vehicle")
            LogFile.write(f"\n HasError after BT = {HasError} \n")
            return HasError
    def SetSubs(self):
        #Setting subs for BP  pressure
        if self.BPT == 0:
                request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBPFound1?Subscription=42", headers = header)
                request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBPFound2?Subscription=42", headers = header)
        if self.BPT == 1:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/AirPipe (BP)." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BPT == 2:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BP (AirPipe)." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BPT == 3:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/HL." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/HL." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)

        #subs for BC pressure

        if self.BCT == 0:
                print("subs for no bct")
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/NOBCFOUND1?Subscription=42", headers = header)
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/NOBCFOUND@?Subscription=42", headers = header)
        if self.BCT == 1:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BCT == 2:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BCT == 3:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder2." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder2." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BCT == 4:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1_2." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_1_2." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BCT == 5:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/Brake Cylinder Volume A." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/Brake Cylinder Volume A." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BCT == 6:
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation//Bremszylinder1." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation//Bremszylinder1." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        if self.BCT == 7:
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_2." + RVData.PressureUnit[0]+ "?Subscription=42", headers = header)
                request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Simulation/BrakeCylinder_2." + RVData.PressureUnit[1]+ "?Subscription=42", headers = header)
        
        #subs for BTT
        if self.BTT == 0:
            self.BrakeType = "[?]"
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBSW?Subscription=42", headers = header)
        if self.BTT == -1:
            self.BrakeType = "[?]"
            #print("no switch")
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NOBSW?Subscription=42", headers = header)
        if self.BTT == 1:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 2:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 3:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 4:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeMode_Switch.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 5:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeMode.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 6:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 7:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Bogie1PassGoodsValve (Lever).Function.GetCurrentNotchIndex?Subscription=42", headers = header)
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/Bogie2PassGoodsValve (Lever).Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 8:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeSelector_F.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 9:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeModeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 10:
            request.post(tswapi+ "/subscription/CurrentFormation/" + str(self.index) + "/BrakeMode_F.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 11:
            request.post(tswapi + "/subscription/CurrentFormation/"+ str(self.index) + "/BrakeSelector_L.Function.GetCurrentNotchIndex?Subscription=42", headers = header).json() 
        if self.BTT == 12:
            request.post(tswapi + "/subscription/CurrentFormation/" +  str(self.index) + "/GPR_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header).json()
        if self.BTT == 13:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/BrakeSelector_R-MG.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 14:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/GP_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 15:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/BrakeTimingSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.BTT == 420:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_L.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/G%2fP_BrakeSelector_R.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributerCutOff/",headers = header).json()
        if not TestData['Result'] == "Error":
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributerCutOff.Function.GetCurrentNotchIndex?Subscription=42",headers = header)
            self.DType = 1
        else:
            TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributerCutOut/",headers = header).json()
            if not TestData['Result'] == "Error":
                request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/DistributerCutOut.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
            else:
                TestData = request.get(tswapi + "/list/CurrentFormation/" + str(self.index)+ "/DistributorIsolatingValve/",headers = header).json()
                if not TestData['Result'] == "Error":
                    request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributorIsolatingValve.Function.GetCurrentNotchIndex?Subscription=42",headers = header)
                else:
                    request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NODistributor?Subscription=42",headers = header)
        

    def GetBM(self,BI,BI2 = 0):
        Bstr = "?"
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

    
    def SetBM(self,BIndex):
        print("launched function")
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
            if BIndex == 0:
                print("setting to G")
                print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.InputValue?Value=" + str(0.75),headers = header).url)
                print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.InputValue?Value=" + str(0.75),headers = header).json())
            if BIndex == 1:
                print("setting to P")
                print(request.patch(tswapi + "/set/CurrentFormation/" + str(self.index) + "/PassengerGoodsValve.InputValue?Value=" + str(0),headers = header).json())
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


def FindData(index):
    BTT = 0
    BPT = 0
    BCT = 0
    isWagon = True
    Weight = 0

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
                                                            request.post(tswapi + "/subscription/CurrentFormation/" + str(index) + "/GP_BrakeSelector.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
                                                        else:
                                                            
                                                            if not ReqData['Result'] == "Error":
                                                                BTT = 15
                                                                
                                                                LogFile.write("BrakeMode not found for vehicle \n")
                                                                LogFile.flush() # Add this line

    return [BTT,BPT,BCT,isWagon,Weight]

class VehicleChoiceControl(wx.Choice):
    index = 0
    def Create(self,parent,vpos,TypeID,validChoices,CurrentChoice = 0):
        self.index = vpos
        wx.Choice.Create(self,parent,TypeID,choices = validChoices)
        self.SetSelection(CurrentChoice)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnEraseBackground(self, event):
        pass 
class ChoiceWindow(wx.ScrolledWindow):
    def __init__(self,parent):
        wx.ScrolledWindow.__init__(self,parent,wx.ID_ANY, style=wx.VSCROLL | wx.ALWAYS_SHOW_SB)
        self.StaticPosText = []
        self.BrakeChoiceList = []
        self.DstrChoice = []
        self.lay = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.lay)
        self.lay.SetSizeHints(self)
        self.SetBackgroundColour(colour= [0,0,0])
        self.lay.Layout()
        self.FitInside()
        self.SetScrollRate(0, 20)
    def CreateVehicleControl(self,i,ValidChoices,CBrake):
                statictext = wx.StaticText(self,wx.ID_ANY,str(i),style = wx.ALIGN_CENTER)
                statictext.SetForegroundColour(colour = [255,253,208])
                brakechoice = VehicleChoiceControl()
                brakechoice.Create(self,i,BrakeChoiceID,ValidChoices,CBrake)
                brakechoice.SetBackgroundColour(colour = [0,0,0])
                brakechoice.SetForegroundColour(colour = [255,253,208])
                DChoice = VehicleChoiceControl()
                DChoice.Create(self,i,DstrID,["Close","Open"],1)
                DChoice.SetSelection(1)
                self.DstrChoice.append(DChoice)
                self.StaticPosText.append(statictext)
                self.BrakeChoiceList.append(brakechoice)
                self.ControlSizer = wx.BoxSizer(wx.HORIZONTAL)
                self.ControlSizer.Add(statictext,0,wx.CENTER | wx.LEFT | wx.RIGHT ,5)
                self.ControlSizer.Add(brakechoice,1,wx.ALL)
                self.ControlSizer.Add(DChoice,1,wx.LEFT,5)
                self.lay.Add(self.ControlSizer)

    def RebuildLayout(self):
                self.lay.Layout()
                self.FitInside()
    def ClearLists(self):
        self.StaticPosText.clear()
        self.BrakeChoiceList.clear()
        
class MainWindowClass(wx.Frame):
    FormationList = []
    SkipCurrent = 0
    rindex = 0
    FArti = 0
    FormationLength = 0.0
    VehCount = 0
    isTr = 0
    CurrentChoice = 0
    Rebuilding = 0
    HasGPRSwitch = 0
    LocoCount = 0
    DoubleBrakeSwitchCount = 0
    def __init__(self, parent, title):
        
        LogFile.write("Initializing Frame \n")
        LogFile.flush() 
        wx.Frame.__init__(self,parent,title = title, size = (620,500))
        self.PBar = wx.StatusBar(self)
        self.statustext = wx.StaticText(self.PBar,label = "Test Text",pos = (5,5))
        self.statustext.SetForegroundColour(colour = [255,253,208])
        self.PBar.SetBackgroundColour(colour= [0,0,0])
        self.ListSizer = wx.BoxSizer(wx.VERTICAL)
        self.WindowSizer = wx.BoxSizer(wx.HORIZONTAL)
        LogFile.write("Frame + sizers Initialized \n")
        LogFile.flush() 
        self.FormationListUI = wx.dataview.DataViewListCtrl(self,ListCtrlID,style = wx.dataview.DV_NO_HEADER) #style 
        self.FormationListUI.AppendTextColumn("I",width = 25)
        self.FormationListUI.AppendTextColumn("Name")
        self.FormationListUI.AppendTextColumn("BM",width =50)
        self.FormationListUI.AppendTextColumn("BP")
        self.FormationListUI.AppendTextColumn("BC")
        self.FormationListUI.AppendTextColumn("Weight", width = 70)
        self.FormationListUI.AppendTextColumn("Load", width = 70)
        self.FormationListUI.SetBackgroundColour(colour= [0,0,0])
        self.FormationListUI.SetForegroundColour(colour = [255,253,208])
        self.OnTopToggle = wx.CheckBox(self,OnTopToggleID,label = "Stay on Top")
        self.OnTopToggle.SetForegroundColour(colour = [255,253,208])
        self.PressureUnitChoice = wx.Choice(self,PressureChoiceID,choices = ["BAR", "PSI"],name= "Pressure Unit Choice")
        self.VehControlWindow = ChoiceWindow(self)
        self.Toggle5Button = wx.Button(self,Toggle5ID,"Toggle First 5")
        self.Toggle5Button.SetBackgroundColour(colour = [0,0,0])
        self.Toggle5Button.SetForegroundColour(colour = [255,253,208])
        self.ToggleAllButton = wx.Button(self,ToggleAllID,"Toggle All Wagons")
        self.ToggleAllButton.SetBackgroundColour(colour = [0,0,0])
        self.ToggleAllButton.SetForegroundColour(colour = [255,253,208])
        self.PressureUnitChoice.SetSelection(0)
        self.ListSizer.Add(self.FormationListUI,1,wx.EXPAND)
        self.ListSizer.Add(self.OnTopToggle,0)
        self.ListSizer.Add(self.PressureUnitChoice,0)
        self.ListSizer.Add(self.Toggle5Button,0)
        self.ListSizer.Add(self.ToggleAllButton,0)
        self.SetBackgroundColour(colour= [0,0,0])
        self.SetForegroundColour(colour = [255,253,208])
        #self.OptionsBar = wx.MenuBar();
        #self.OptionsMenu = wx.Menu("Options")
        #self.OptionsBar.Append(self.OptionsMenu,"Options")
        #self.SetMenuBar(self.OptionsBar)        
        self.SetStatusBar(self.PBar)
        if IsTSWOpen():
            LogFile.write(str(requests.delete(tswapi + "/subscription/?Subscription=42", headers = header).json()))
            ReqData = request.get(tswapi + "/list/CurrentFormation", headers = header).json()
            if ReqData['Result'] == "Error":
                self.statustext.SetLabel("Waiting for formation")
                LogFile.write("Waiting for formation...")
                LogFile.flush() # Add this line
            else:

                self.text = request.get(tswapi + "/get/CurrentFormation.FormationLength", headers = header)
                self.text = self.text.json()
                self.fl = int(self.text['Values']['FormationLength'])
                self.VehCount = self.fl
                LogFile.write("Detected " + str(self.VehCount) + " vehicles \n")
                LogFile.flush() 
                self.FormationLength = 0.0
                self.FormationList = []
                for i in range(self.fl):
                        self.SkipCurrent = 0
                        vname = request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName ", headers = header).json()
                        vname = vname['Values']['ObjectName']
                        fname = vname.split("_")
                        VehName = GetVehicleName(vname)
                        print(VehName)
                        LogFile.write("Detected " + vname + " at position " + str(i) + "with reference name " + VehName + "\n")
                        LogFile.flush() 
                        Data = request.get(tswapi+ "/get/CurrentFormation/" + str(i) + ".Function.HUD_GetDirection", headers = header).json()
                        if not Data['Result'] == "Error":
                            self.LocoCount += 1
                        if VehName == "Laaers":
                            if fname[3] == "B":
                                self.SkipCurrent = 1
                            if fname[2] == "B":
                                self.SkipCurrent = 1
                        if not self.SkipCurrent:
                            CurrentVehicle = Vehicle(VehName,i)
                            LogFile.write(str(CurrentVehicle.PrintData()))
                            res = CurrentVehicle.UpdateData()
                            LogFile.write(f"res = {res}")
                            if res:
                                LogFile.write(f"searching data for vehicle with index = {i}")
                                FoundData = FindData(i)
                                CurrentVehicle.BTT = FoundData[0]
                                CurrentVehicle.BPT = FoundData[1]
                                CurrentVehicle.BCT = FoundData[2]
                                CurrentVehicle.isWagon = FoundData[3]
                                CurrentVehicle.CargoWeight = FoundData[4]
                                res = CurrentVehicle.UpdateData()

                            LogFile.write(str(CurrentVehicle.PrintData()))
                            if not str(CurrentVehicle.BTT) == str(0):
                                self.HasGPRSwitch = 1

                            self.FormationList.append(CurrentVehicle)
                            LogFile.write("Adding Vehicle to UI list \n")
                            LogFile.flush() # Add this line
                            idx = self.FormationListUI.GetItemCount()
                            itemlist = []
                            itemlist.append(str(idx))
                            itemlist += CurrentVehicle.ReturnSequence()
                            self.FormationListUI.AppendItem(itemlist)
                            CurrentVehicle.SetSubs()
                            if CurrentVehicle.BTT == 7:
                                self.DoubleBrakeSwitchCount += 1
                            if CurrentVehicle.BTT == 420:
                                self.DoubleBrakeSwitchCount += 1
                CC = self.FormationListUI.GetItemCount()
                if self.HasGPRSwitch:
                    self.Toggle5Button.Show()
                    self.ToggleAllButton.Show()
                    self.FormationListUI.GetColumn(2).SetHidden(0)
                    for i in range(CC):
                        PBM = self.FormationList[i].GetPBM()
                        BMI = self.FormationList[i].GetBMInt()
                        #print(f"for i = {i} PBM = {PBM} BMI = {BMI} BTT = {self.FormationList[i].BTT}")
                        self.VehControlWindow.CreateVehicleControl(i,PBM,BMI)
                else:
                    self.Toggle5Button.Hide()
                    self.ToggleAllButton.Hide()
                    self.FormationListUI.GetColumn(2).SetHidden(1)
        self.VehControlWindow.RebuildLayout()
        self.WindowSizer.Add(self.ListSizer,2 ,wx.EXPAND)
        self.WindowSizer.Add(self.VehControlWindow,1,wx.EXPAND)
        self.SetSizer(self.WindowSizer)
        self.WindowSizer.Layout()
        self.LocoCount = self.LocoCount -1
        self.VehControlWindow.Show()
        self.Show(True)
        self.Center()

        LogFile.write("Opening Update Thread \n")
        LogFile.flush() 
        self.statustext.SetLabel("Displaying Formation")

        self.Bind(wx.EVT_CHECKBOX,self.OnTopToggleF,id = OnTopToggleID)
        self.Bind(wx.EVT_CHOICE,self.OnSelection,id = PressureChoiceID)
        self.Bind(wx.EVT_CHOICE, self.OnBrakeChoice,id =BrakeChoiceID)
        self.Bind(wx.EVT_BUTTON, self.OnToggle5,id = Toggle5ID)
        self.Bind(wx.EVT_BUTTON,self.OnToggleAll, id = ToggleAllID)
        self.Bind(wx.EVT_CHOICE,self.OnDistributor,id = DstrID)
        self.UpdateThread = threading.Thread(target=self.RequestUpdate)
        self.UpdateThread.daemon = True
        self.UpdateThread.start()
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnEraseBackground(self, event):
        pass 
    def OnDistributor(self,event):
        print("ondistr")
        ChoiceObj = event.GetEventObject()
        idx =ChoiceObj.index
        Dindex = event.GetSelection()
        request.patch(tswapi+"/set/CurrentFormation/" + str(idx) +"/DistributerCutOff.InputValue?Value=" + str(Dindex), headers = header)
        if Dindex:
            Dindex = 0
        else:
            Dindex = 1
        request.patch(tswapi+"/set/CurrentFormation/" + str(idx) +"/DistributerCutOut.InputValue?Value=" + str(Dindex), headers = header)
        request.patch(tswapi+"/set/CurrentFormation/" + str(idx) +"/DistributorIsolatingValve.InputValue?Value=" + str(Dindex), headers = header)
    def OnTopToggleF(self,event):
            self.ToggleWindowStyle(wx.STAY_ON_TOP)
    def UpdateText(self,text):
        self.statustext.SetLabel(text)
    def OnToggle5(self,event):
        self.TogThread = threading.Thread(target = self.ToggleBrake, args = [0])
        self.TogThread.start()
    def OnToggleAll(self,event):
        self.TogThread = threading.Thread(target = self.ToggleBrake, args = [1])
        self.TogThread.start()
    def ToggleBrake(self,mode = 0):
        print("thread entered")
        if not mode:
            if str(self.FormationList[1+self.LocoCount].Name) == "Sggmrss":
                for i in range(0,7+self.LocoCount):
                    self.FormationList[i].SetBM(0)
                    self.VehControlWindow.BrakeChoiceList[i].SetSelection(0)
            else:
                for i in range(0,6 + self.LocoCount):
                    self.FormationList[i].SetBM(0)
                    self.VehControlWindow.BrakeChoiceList[i].SetSelection(0)
        else:
            for i in range(1,self.FormationListUI.GetItemCount()):
                self.FormationList[i].SetBM(0)
                self.VehControlWindow.BrakeChoiceList[i].SetSelection(0)
    def OnSelection(self,event):
        #print("choice made")
        global PU
        PU = self.PressureUnitChoice.GetSelection()
        #print(PU)
    def OnBrakeChoice(self,event):
        ChoiceObj = event.GetEventObject()
        idx =ChoiceObj.index
        Bindex = event.GetSelection()
        #print("A choice was made for vehicle " + str(idx) + "with index " +str(Bindex))
        self.BrakeThread = threading.Thread(target =self.FormationList[idx].SetBM, args = [Bindex])
        self.BrakeThread.start()
        #self.FormationList[idx].SetBM(Bindex)
    def OnRefresh(self, UpdateData):
        start_time = time.perf_counter()
        if not self.Rebuilding:
            BP = 0
            BC = 0
            BI = -1
            BI2 = -1
            Bistr = ""
            i = 0
            Had2BrakeSwitches = 0 #for obb1020, tadgs, 194/e94, skips 
            ItemCount = self.FormationListUI.GetItemCount()
            LogFile.write("Item count is " + str(ItemCount) + "\n")
            if ItemCount:
                ReqData = request.get(tswapi + "/get/CurrentFormation/0/RailVehiclePhysicsComponent0.Function.GetFormationLength", headers = header)
                while i < (self.FormationListUI.GetItemCount()*6) + self.DoubleBrakeSwitchCount:
                            # subscription should be 1.BP-BAR 2.BP-PSI 3.BC-BAR 4.BC-PSI 5.BrakeMode(G,P,P2(why?),R,R+Mg)
                                #print("for i = " +str(i) )
                                #LogFile.write("\n")
                                #LogFile.write(str(UpdateData['Entries'][i]))
                                #LogFile.write("\n")
                                #LogFile.write(str(UpdateData['Entries'][i+1]))
                                #LogFile.write("\n")
                                #LogFile.write(str(UpdateData['Entries'][i+2]))
                                #LogFile.write("\n")
                                #LogFile.write(str(UpdateData['Entries'][i+3]))
                                #LogFile.write("\n")
                                #LogFile.write(str(UpdateData['Entries'][i+4]))
                                #LogFile.write("\n")
                                name =  self.FormationListUI.GetTextValue(int(i/6),1)
                                Had2BrakeSwitches = 0
                                if self.FormationList[int(i/6)].BTT == 7:
                                    Had2BrakeSwitches = 1
                                if self.FormationList[int(i/6)].BTT == 420:
                                    Had2BrakeSwitches = 1
                                #LogFile.write(f"Had2BrakeSwitches = {Had2BrakeSwitches}, vehname = {self.FormationList[int(i/6)].Name} \n")
                                if not PU:
                                    if not str(UpdateData['Entries'][i]['Values']) == "None":
                                        BP = UpdateData['Entries'][i]['Values']['Pressure_BAR_G']
                                    if not str(UpdateData['Entries'][i+2]['Values']) == "None":
                                        
                                        BC = UpdateData['Entries'][i+2]['Values']['Pressure_BAR_G']
                                else:
                                    if not str(UpdateData['Entries'][i+1]['Values']) == "None":
                                        BP = UpdateData['Entries'][i+1]['Values']['Pressure_PSI_G']
                                    if not str(UpdateData['Entries'][i+3]['Values']) == "None":
                                        BC = UpdateData['Entries'][i+3]['Values']['Pressure_PSI_G']
                                if  not str(UpdateData['Entries'][i+4]['Values']) == "None":
                                    BI = UpdateData['Entries'][i+4]['Values']['ReturnValue']
                                if Had2BrakeSwitches:
                                    #LogFile.write("entered here \n")
                                    #LogFile.write(str(i))
                                    #LogFile.write(str(UpdateData['Entries'][i+5]))
                                    BI2 = UpdateData['Entries'][i+5]['Values']['ReturnValue']
                                    i = i+1
                                BP = round(BP,1)
                                BC = round(BC,1)
                                BPstr = "BP: " + str(BP)
                                BCstr = "BC: " + str(BC)
                                if not str(UpdateData['Entries'][i+5]['Values']) == "None":
                                    DStatus = UpdateData['Entries'][i+5]['Values']['ReturnValue']
                                    if self.FormationList[int(i/6)].DType:
                                        if not DStatus == self.VehControlWindow.DstrChoice[int(i/6)].GetSelection():
                                            self.VehControlWindow.DstrChoice[int(i/5)].SetSelection(DStatus)
                                    else:
                                        if DStatus:
                                            DStatus = 0
                                        else:
                                            DStatus = 1
                                    if not DStatus == self.VehControlWindow.DstrChoice[int(i/6)].GetSelection():
                                                self.VehControlWindow.DstrChoice[int(i/6)].SetSelection(DStatus) 
                                            
                                # updating the table
                                #LogFile.write(f"bi = {BI}")
                                if not BI == -1:
                                    Bistr = self.FormationList[int(i/6)].GetBM(BI,BI2)
                                    LogFile.write(f"i = {i} Bistr  = {Bistr}")
                                    if not Bistr == "None":
                                        
                                        res = self.FormationListUI.SetTextValue(Bistr,int(i/6),2)
                                        if not self.FormationList[int(i/6)].BTT == 2:
                                            if BI != self.VehControlWindow.BrakeChoiceList[int(i/6)].GetSelection():
                                                self.VehControlWindow.BrakeChoiceList[int(i/6)].SetSelection(BI)
                                        else:
                                            if BI:
                                                BI = 0
                                            else:
                                                BI = 1
                                            if BI != self.VehControlWindow.BrakeChoiceList[int(i/6)].GetSelection():
                                                self.VehControlWindow.BrakeChoiceList[int(i/6)].SetSelection(BI)
                                    else:
                                        self.FormationListUI.SetTextValue("?",int(i/6),2)
                                    
                                else:
                                    self.FormationListUI.SetTextValue("[G]?",int(i/6),2)
                                self.FormationListUI.SetTextValue(BPstr,int(i/6),3)
                                self.FormationListUI.SetTextValue(BCstr,int(i/6),4)
                                i = i + 6
                                #LogFile.write("end of loop")
                                #print("end")
        end_time = time.perf_counter()
        timetaken = end_time-start_time
        print(f"Update function took {timetaken*1000}ms")
    def ClearList(self):
        print("Clearing...")
        self.VehCount = 0
        self.statustext.SetLabel("No Formation Detected,Clearing UI")
        self.Freeze()
        if self.FormationListUI.GetItemCount():
            self.FormationListUI.DeleteAllItems()
        
        self.WindowSizer.Detach(self.VehControlWindow)
        self.VehControlWindow.DestroyChildren()
        self.WindowSizer.Layout()
        self.Thaw()
        self.statustext.SetLabel("Waiting for Formation")
    def UpdateOptions(self):
        pass
    def RebuildFormation(self):
        self.Rebuilding = 1
        self.ClearList()
        LogFile.write("Rebuilding Formation \n")
        LogFile.flush() # Add this line
        requests.delete(tswapi + "/subscription/?Subscription=42", headers = header)
        self.WindowSizer.Detach(self.VehControlWindow)
        self.VehControlWindow.ClearLists()
        self.VehControlWindow.Destroy()
        print("window destroyed")
        self.statustext.SetLabel("Rebuilding Formation")
        self.Freeze()

        self.VehControlWindow = ChoiceWindow(self)

        self.FormationLength = 0
        self.text = request.get(tswapi + "/get/CurrentFormation.FormationLength", headers = header)
        self.text = self.text.json()
        self.fl = int(self.text['Values']['FormationLength'])
        LogFile.write("Detected " + str(self.fl) + " vehicles \n")
        LogFile.flush() 
        self.FormationLength = 0.0
        self.FormationList = []
        for i in range(self.fl):
                    self.SkipCurrent = 0
                    vname = request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName ", headers = header).json()
                    vname = vname['Values']['ObjectName']
                    fname = vname.split("_")
                    VehName = GetVehicleName(vname)
                    LogFile.write("Detected " + vname + " at position " + str(i) + "with reference name " + VehName + "\n")
                    print("Detected " + vname + " at position " + str(i) + "with reference name " + VehName + "\n")
                    if VehName == "Laaers":
                        self.SkipNext = 1
                        if fname[3] == "B":
                            self.SkipCurrent = 1
                        if fname[2] == "B":
                            self.SkipCurrent = 1
                    if not self.SkipCurrent:          
                        CurrentVehicle = Vehicle(VehName,i)
                        LogFile.write(str(CurrentVehicle.PrintData()))
                        res = CurrentVehicle.UpdateData()
                        if res:
                            LogFile.write(f"searching data for vehicle with index = {i}")
                            FoundData = FindData(i)
                            CurrentVehicle.BTT = FoundData[0]
                            CurrentVehicle.BPT = FoundData[1]
                            CurrentVehicle.BCT = FoundData[2]
                            CurrentVehicle.isWagon = FoundData[3]
                            CurrentVehicle.CargoWeight = FoundData[4]
                            res = CurrentVehicle.UpdateData()

                        LogFile.write(str(CurrentVehicle.PrintData()))
                        if not str(CurrentVehicle.BTT) == str(0):
                            self.HasGPRSwitch = 1

                        self.FormationList.append(CurrentVehicle)
                        LogFile.write("Adding Vehicle to UI list \n")
                        LogFile.flush() # Add this line
                        idx = self.FormationListUI.GetItemCount()
                        itemlist = []
                        itemlist.append(str(idx))
                        itemlist += CurrentVehicle.ReturnSequence()
                        self.FormationListUI.AppendItem(itemlist)
                        CurrentVehicle.SetSubs()
                        if CurrentVehicle.BTT == 7:
                            self.DoubleBrakeSwitchCount += 1
                        if CurrentVehicle.BTT == 420:
                            self.DoubleBrakeSwitchCount += 1
                        self.SkipNext = 0
        CC = self.FormationListUI.GetItemCount()
        if self.HasGPRSwitch:
            self.Toggle5Button.Show()
            self.ToggleAllButton.Show()
            self.FormationListUI.GetColumn(2).SetHidden(0)
            for i in range(CC):
                PBM = self.FormationList[i].GetPBM()
                BMI = self.FormationList[i].GetBMInt()
                #print(f"for i = {i} PBM = {PBM} BMI = {BMI} BTT = {self.FormationList[i].BTT}")
                self.VehControlWindow.CreateVehicleControl(i,PBM,BMI)
        else:
                self.Toggle5Button.Hide()
                self.ToggleAllButton.Hide()
                self.FormationListUI.GetColumn(2).SetHidden(1)
        self.VehControlWindow.RebuildLayout()
        self.WindowSizer.Add(self.VehControlWindow,1,wx.EXPAND)
        self.WindowSizer.Layout()
        self.VehControlWindow.Show()
        self.Thaw()
        self.VehCount = self.fl
        self.Rebuilding = 0
        self.statustext.SetLabel("Displaying Formation")
    def RequestUpdate(self):
     UpdateData = 0
     Vh = 0
     SkipToRebuild = 0

     while 1:
            res = IsTSWOpen()
            if res:
                SkipToRebuild = 0
                if not self.Rebuilding:
                    try:
                        isForm = request.get(tswapi + "/get/CurrentFormation.FormationLength", headers = header).json()
                        vname = request.get(tswapi + "/get/CurrentFormation/0.ObjectName ", headers = header).json()
                        if not vname['Result'] == "Error":
                            vname = vname['Values']['ObjectName']
                            fname = vname.split("_")
                            VehName = GetVehicleName(vname)
                            vname = request.get(tswapi + "/get/CurrentFormation/1.ObjectName ", headers = header).json()
                            vname = vname['Values']['ObjectName']
                            fname = vname.split("_")
                            VehName2 = GetVehicleName(vname)
                            if self.VehCount:
                                if not VehName == self.FormationList[0].Name:
                                    SkipToRebuild = 1
                                if not VehName2 == self.FormationList[1].Name:
                                    SkipToRebuild = 1
                    except requests.exceptions.ConnectionError as e:
                        continue
                    if not isForm['Result'] == "Error":
                        Vh = isForm['Values']['FormationLength']

                        if Vh == self.VehCount :
                            if not SkipToRebuild:
                                try:
                                    UpdateData = request.get(tswapi + "/subscription?Subscription=42", headers = header).json()
                                except requests.exceptions.ConnectionError as e:
                                    time.sleep(1)
                            else:
                                print("Formation Changed")
                                Vh = 0
                                LogFile.write("Formation Changed, Rebuilding... \n")
                                LogFile.flush() 
                                wx.CallAfter(self.RebuildFormation)
                                time.sleep(1)
                        else:
                            print("Formation Changed")
                            Vh = 0
                            LogFile.write("Formation Changed, Rebuilding... \n")
                            LogFile.flush() 
                            wx.CallAfter(self.RebuildFormation)
                            time.sleep(1)
                    else:
                        try :
                            requests.delete(tswapi + "/subscription/?Subscription=42", headers = header).json()
                        except requests.exceptions.ConnectionError as e:
                            print("error deleting subs")
                        VehCount = 0
                        MainWindow.statustext.SetLabel("No formation found")
                        if MainWindow.VehCount:
                            wx.CallAfter(self.ClearList)
                        time.sleep(1)
                    if Vh:
                        if UpdateData:
                 
                            wx.CallAfter(self.OnRefresh,UpdateData)
            else:
                print("tsw not open")
                self.UpdateText("Waiting for TSW")
                if self.FormationListUI.GetItemCount():
                    self.FormationListUI.DeleteAllItems()
            time.sleep(0.5)

    


app = wx.App(True,"ProgramOutput.log",)
MainWindow = MainWindowClass(None, "Formation Viewer 0.5.10")
app.MainLoop()