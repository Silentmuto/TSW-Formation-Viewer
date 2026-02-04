import wx
import requests
import json
import time
import RVData # pyright: ignore[reportMissingImports]
import threading
import sys
from datetime import datetime
import psutil
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path
import ctypes
import wx.lib.buttons as buttons
import ID
import VehicleGrid as VG
import wx.grid
#subscription id = 42
#add reverse display
PU = 0
tswapi = "http://127.0.0.1:31270"   

now = datetime.now()

#searching for the key
Found = 0
try:    
    documents_path = Path.home() / "Documents/My Games/TrainSimWorld6/Saved/Config" 
    abc = str(documents_path)
    abc = abc + "/CommAPIKey.txt"
    apifile = open(abc ,"r")
except FileNotFoundError:
    try:
        documents_path = Path.home() / "OneDrive/Documents/My Games/TrainSimWorld6/Saved/Config" 
        abc = str(documents_path)
        abc = abc + "/CommAPIKey.txt"
        apifile = open(abc ,"r")
    except:
        print("here")
        apifile = open("key.txt","r")

ApiKey = apifile.read()

header = {"DTGCommKey": ApiKey }
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
LogFile = open("log.txt", "a")
LogFile.write(str(now))
LogFile.write("\n")
LogFile.flush() 
 
def GetColour(col):
    print(col)
    aux = col
    aux = aux.split(',')
    color = wx.Colour()
    r = int(aux[0])
    g = int(aux[1])
    b = int(aux[2])
    a= int(aux[3])
    color.Set(r,g,b,a)
    return color

def IsTSWOpen():
    for p in psutil.process_iter():
       if p.name()  == 'TrainSimWorld.exe':
            return 1
       if p.name()  == 'TrainSimWorld6.exe':
            return 1
    return 0


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
            FoundData = FindData(index)
            self.BTT = FoundData[0]
            self.BPT = FoundData[1]
            self.BCT = FoundData[2]
            self.index = index
            #print(f"BCT FOund is {self.BCT}")
            self.isWagon = FoundData[3]
            self.TotalWeight = FoundData[4]
            self.DType = FoundData[5]
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
                LogFile.write(f"Error finding BP values for  vehicle {self.Name} \n")
                LogFile.flush() 
                HasError = 1
            
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
        if self.DType == 1:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributerCutOff.Function.GetCurrentNotchIndex?Subscription=42",headers = header)
        if self.DType == 2:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/DistributerCutOut.Function.GetCurrentNotchIndex?Subscription=42", headers = header)
        if self.DType == 3:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributorIsolatingValve.Function.GetCurrentNotchIndex?Subscription=42",headers = header)
        if self.DType == 0:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) + "/NODistributor?Subscription=42",headers = header)
        if self.DType == 4:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index)+ "/DistributorCutOff.Function.GetCurrentNotchIndex?Subscription=42",headers = header)
        if self.DType == 5:
            request.post(tswapi + "/subscription/CurrentFormation/" + str(self.index) +"/Simulation/Distributor%20CutOff.ValvePosition?Subscription=42",headers = header)
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

def FindData(index):
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
    return [BTT,BPT,BCT,isWagon,Weight,DType]
class ThemeWindow(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self,None,-1)
        self.MainSizer = wx.BoxSizer()
        self.TextSizer = wx.BoxSizer(wx.VERTICAL)
        self.CtrlSizer = wx.BoxSizer(wx.VERTICAL)
        self.TTxt = wx.StaticText(self,-1,"Text Colour" )
        self.BTxt = wx.StaticText(self,-1, "Background Colour")
        self.GTxt = wx.StaticText(self,-1, "Gridline Colour")
        self.ITxt = wx.StaticText(self,-1,"Set Custom Theme using RGB Values")
        self.ok = wx.Button(self,120,"Set Theme")
        self.TCCtrl = wx.ColourPickerCtrl(self,-1)
        self.TCCtrl.SetColour(parent.GetForegroundColour())
        self.BCCtrl = wx.ColourPickerCtrl(self,-1)
        self.BCCtrl.SetColour(parent.GetBackgroundColour())
        self.GCCtrl = wx.ColourPickerCtrl(self,-1)
        self.TextSizer.Add(self.TTxt,1)
        self.TextSizer.Add(self.BTxt,1)
        self.TextSizer.Add(self.GTxt,1)
        self.TextSizer.Add(self.ok,1)
        self.CtrlSizer.Add(self.TCCtrl)
        self.CtrlSizer.Add(self.BCCtrl)
        self.CtrlSizer.Add(self.GCCtrl)
        self.MainSizer.Add(self.TextSizer,1,wx.TOP,30)
        self.MainSizer.Add(self.CtrlSizer,1,wx.TOP,30)
        self.SetSizer(self.MainSizer)
        self.MainSizer.Layout()
        self.Refresh()
        self.Show()
        self.Center()
        self.Bind(wx.EVT_BUTTON,self.OnSet,source = self.ok)
    def OnSet(self,event):
            b = str(self.BCCtrl.GetColour())
            b = b.replace("(","")
            b = b.replace(")","")
            t = str(self.TCCtrl.GetColour())
            t = t.replace("(","")
            t = t.replace(")","")
            g = str(self.GCCtrl.GetColour())
            g = g.replace("(","")
            g = g.replace(")","")
            file = open("Program.json","w")
            file.write("{")
            file.write("\n")
            file.write('"' + "BackgroundColour" + '"' + ':' +'"' + b +'"'  +"," ) 
            file.write("\n")
            file.write('"' + "TextColour" + '"' + ':' +'"' + t +'"' + "," ) 
            file.write("\n")
            file.write('"' + "GridLineColour" + '"' + ':' +'"' + g +'"') 
            file.write("\n")
            file.write("}")
            file.close()
            self.Close()
            MainWindow.UpdateTheme(0,0,0,1)
class ColumnDialog(wx.Dialog):
    hidden = 0
    def __init__(self,parent,ColumnList):
        wx.Dialog.__init__(self,None,-1,"Column Toggle",(0,0),(350,150))
        self.ColumnSizer = wx.FlexGridSizer(2)
        self.ColumnTog1= wx.CheckBox(self,ID.ToggleColumnID,"Name")
        self.ColumnTog2 = wx.CheckBox(self,ID.ToggleColumnID+1,"Brake Mode")
        self.ColumnTog3 = wx.CheckBox(self,ID.ToggleColumnID+2,"BP")
        self.ColumnTog4 = wx.CheckBox(self,ID.ToggleColumnID+3,"BC")
        self.ColumnTog5 = wx.CheckBox(self,ID.ToggleColumnID+4,"Weight")
        self.ColumnTog6 = wx.CheckBox(self,ID.ToggleColumnID+5,"Load")
        self.ColumnTog7 = wx.CheckBox(self,ID.ToggleColumnID+6,"Brake Selector")
        self.ColumnTog8 = wx.CheckBox(self,ID.ToggleColumnID+7,"Distributor Control")
        self.ColumnTog9 = wx.CheckBox(self,ID.ToggleColumnID+8,"Uncouple")
        self.ColumnTog10 = wx.CheckBox(self,ID.ToggleColumnID+9,"Couple")
        self.ColumnLab= wx.CheckBox(self,ID.ToggleColumnID+10, "Column Labels(Titles)")
        self.ColumnSizer.Add(self.ColumnTog1,0)
        self.ColumnSizer.Add(self.ColumnTog2,0)
        self.ColumnSizer.Add(self.ColumnTog3,0)
        self.ColumnSizer.Add(self.ColumnTog4,0)
        self.ColumnSizer.Add(self.ColumnTog5,0)
        self.ColumnSizer.Add(self.ColumnTog6,0)
        self.ColumnSizer.Add(self.ColumnTog7,0)
        self.ColumnSizer.Add(self.ColumnTog8,0)
        self.ColumnSizer.Add(self.ColumnTog9,0)
        self.ColumnSizer.Add(self.ColumnTog10,0)
        self.ColumnSizer.Add(self.ColumnLab,1,wx.LEFT)
        self.SetSizer(self.ColumnSizer)
        self.ColumnSizer.Layout()
        self.Show()
        self.Center()
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn1,id = ID.ToggleColumnID)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn2,id = ID.ToggleColumnID+1)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn3,id = ID.ToggleColumnID+2)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn4,id = ID.ToggleColumnID+3)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn5,id = ID.ToggleColumnID+4)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn6,id = ID.ToggleColumnID+5)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn7,id = ID.ToggleColumnID+6)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn8,id = ID.ToggleColumnID+7)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn9,id = ID.ToggleColumnID+8)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn10,id = ID.ToggleColumnID+9)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumnLab,id = ID.ToggleColumnID + 10)

    def OnColumnLab(self,event):
        if not self.hidden:
            MainWindow.FormationDisplay.HideColLabels()
            self.hidden = 1
        else:
            MainWindow.FormationDisplay.SetColLabelSize(30)
            MainWindow.MainSizer.Layout()
            MainWindow.Refresh()
            self.hidden = 0
    def OnColumn1(self,event):
        if MainWindow.FormationDisplay.IsColShown(0):
            MainWindow.FormationDisplay.HideCol(0)
        else:
            MainWindow.FormationDisplay.ShowCol(0)
    def OnColumn2(self,event):
        if MainWindow.FormationDisplay.IsColShown(1):
            MainWindow.FormationDisplay.HideCol(1)
        else:
            MainWindow.FormationDisplay.ShowCol(1)
    def OnColumn3(self,event):
        if MainWindow.FormationDisplay.IsColShown(2):
            MainWindow.FormationDisplay.HideCol(2)
        else:
            MainWindow.FormationDisplay.ShowCol(2)
    def OnColumn4(self,event):
        if MainWindow.FormationDisplay.IsColShown(3):
            MainWindow.FormationDisplay.HideCol(3)
        else:
            MainWindow.FormationDisplay.ShowCol(3)
    def OnColumn5(self,event):
        if MainWindow.FormationDisplay.IsColShown(4):
            MainWindow.FormationDisplay.HideCol(4)
        else:
            MainWindow.FormationDisplay.ShowCol(4)
    def OnColumn6(self,event):
        if MainWindow.FormationDisplay.IsColShown(5):
            MainWindow.FormationDisplay.HideCol(5)
        else:
            MainWindow.FormationDisplay.ShowCol(5)
    def OnColumn7(self,event):
        if MainWindow.FormationDisplay.IsColShown(6):
            MainWindow.FormationDisplay.HideCol(6)
        else:
            MainWindow.FormationDisplay.ShowCol(6)       
    def OnColumn8(self,event):
        if MainWindow.FormationDisplay.IsColShown(7):
            MainWindow.FormationDisplay.HideCol(7)
        else:
            MainWindow.FormationDisplay.ShowCol(7)
    def OnColumn9(self,event):
        if MainWindow.FormationDisplay.IsColShown(8):
            MainWindow.FormationDisplay.HideCol(8)
        else:
            MainWindow.FormationDisplay.ShowCol(8)
    def OnColumn10(self,event):
        if MainWindow.FormationDisplay.IsColShown(9):
            MainWindow.FormationDisplay.HideCol(9)
        else:
            MainWindow.FormationDisplay.ShowCol(9)
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
    AVH = 0
    def __init__(self, parent, title):
        LogFile.write("Initializing Frame \n")
        LogFile.flush() 
        wx.Frame.__init__(self,parent,title = title, size = (900,500))
        try :
            PFile = open("Program.json","r")
            PArgs = json.load(PFile)
            PFile.close()
            self.BackgroundColourC = GetColour(PArgs['BackgroundColour'])
            self.TextColourC = GetColour(PArgs['TextColour'])
            self.GridLineColourC = GetColour(PArgs['GridLineColour'])
        except FileNotFoundError as e:
            self.BackgroundColourC = [51,51,51]
            self.TextColourC = [137,206,148]
            self.GridLineColourC = [82,82,82]

        self.MainPanel = wx.Panel(self,-1,(0,0))
        self.MainPanel.SetBackgroundColour(self.BackgroundColourC)
        self.PBar = wx.StatusBar(self)
        self.statustext = wx.StaticText(self.PBar,label = "Test Text",pos = (5,5))
        self.WindowSizer = wx.BoxSizer()
        self.WindowSizer.Add(self.MainPanel,1,wx.EXPAND)
        self.MainSizer = wx.BoxSizer(wx.VERTICAL)
        LogFile.write("Frame + sizers Initialized \n")
        LogFile.flush() 
        self.FormationDisplay = VG.VehicleGrid(self.MainPanel)
        self.OnTopToggle = wx.CheckBox(self.MainPanel,ID.OnTopToggleID,label = "Stay on Top")
        self.PressureUnitChoice = wx.Choice(self.MainPanel,ID.PressureChoiceID,choices = ["BAR", "PSI"],name= "Pressure Unit Choice")
        self.Toggle5Button = buttons.GenButton(self.MainPanel,ID.Toggle5ID,"Toggle First 5")
        self.ToggleAllButton = buttons.GenButton(self.MainPanel,ID.ToggleAllID,"Toggle All Wagons")
        self.ToggleColumnButton = buttons.GenButton(self.MainPanel,ID.ToggleColumnButtonID,"Column Toggle")
        self.RefreshButton = buttons.GenButton(self.MainPanel,ID.RefreshButtonID,"Refresh")
        self.ThemeChoice = wx.Choice(self.MainPanel,ID.ThemeChoiceID,choices = ["Night Moss", "Flora", "Black", "Blue","Custom"] )
        self.ThemeChoice.SetSelection(0)
        
        self.PressureUnitChoice.SetSelection(0)
        self.ButtonSizer = wx.BoxSizer()
        self.MainSizer.Add(self.FormationDisplay,1,wx.EXPAND)
        self.ButtonSizer.Add(self.OnTopToggle,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.PressureUnitChoice,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.Toggle5Button,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.ToggleAllButton,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.ThemeChoice,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.ToggleColumnButton,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.RefreshButton,0,wx.LEFT,10)
        self.MainSizer.Add(self.ButtonSizer,0,wx.TOP,5)



        #self.OptionsBar = wx.MenuBar();
        #self.OptionsMenu = wx.Menu("Options")
        #self.OptionsBar.Append(self.OptionsMenu,"Options")
        #self.SetMenuBar(self.OptionsBar)        
        self.SetStatusBar(self.PBar)

        self.MainPanel.SetSizer(self.MainSizer)
        self.MainSizer.Layout()
        self.WindowSizer.Layout()

        self.MainPanel.SetBackgroundColour(self.BackgroundColourC)
        self.statustext.SetForegroundColour(self.TextColourC)
        self.PBar.SetBackgroundColour(self.BackgroundColourC)
        self.OnTopToggle.SetForegroundColour(self.TextColourC)
        self.Toggle5Button.SetBackgroundColour(self.BackgroundColourC)
        self.Toggle5Button.SetForegroundColour(self.TextColourC)
        self.SetBackgroundColour(self.BackgroundColourC)
        self.SetForegroundColour(self.TextColourC)
        self.ToggleAllButton.SetBackgroundColour(self.BackgroundColourC)
        self.ToggleAllButton.SetForegroundColour(self.TextColourC)
        self.FormationDisplay.SetBackgroundColour(self.BackgroundColourC)
        self.FormationDisplay.SetForegroundColour(self.TextColourC)
        self.FormationDisplay.SetLabelBackgroundColour(self.BackgroundColourC)
        self.FormationDisplay.SetLabelTextColour(self.TextColourC)
        self.FormationDisplay.SetDefaultCellBackgroundColour(self.BackgroundColourC)
        self.FormationDisplay.SetDefaultCellTextColour(self.TextColourC)
        self.FormationDisplay.SetGridLineColour(self.GridLineColourC)
        hwnd = self.GetHandle()
        try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4
                )
        except Exception:
                pass
        try:
                ctypes.windll.uxtheme.SetWindowTheme(hwnd, "DarkMode_Explorer", None)
        except Exception:
                pass
                
        for child in self.GetChildren():
            hwnd = child.GetHandle()
            try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4
                    )
            except Exception:
                    pass
                    
            try:
                    ctypes.windll.uxtheme.SetWindowTheme(hwnd, "DarkMode_Explorer", None)
            except Exception:
                    pass
        LogFile.write("Opening Update Thread \n")
        LogFile.flush() 
        self.statustext.SetLabel("Displaying Formation")
        self.SetSizer(self.WindowSizer)
        self.WindowSizer.Layout()
        self.Refresh()
        self.Show(True)
        self.Center()
        if IsTSWOpen():
            requests.delete(tswapi + "/subscription/?Subscription=42", headers = header)
            ReqData = request.get(tswapi + "/list/CurrentFormation", headers = header).json()
            if ReqData['Result'] == "Error":
                self.statustext.SetLabel("Waiting for formation")
                LogFile.write("Waiting for formation... \n")
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
                ReqData = request.get(tswapi + "/get/CurrentFormation/0.Function.HUD_GetSpeed",headers = header).json()

                if not ReqData['Result'] == "Error":
                    self.isReverse = 0
                    ReqData = request.get(tswapi + "/get/CurrentFormation/0/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                    self.LocoSign = ReqData['Values']['ReturnValue']['y']
                    if self.LocoSign < 0.0:
                        self.LocoSign = "-"
                    else:
                        self.LocoSign = "+"
                    for i in range(self.fl):
                            self.SkipCurrent = 0
                            vname = request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName ", headers = header).json()
                            vname = vname['Values']['ObjectName']
                            fname = vname.split("_")
                            VehName = GetVehicleName(vname)
                            LogFile.write("Detected " + vname + " at position " + str(i) + " with reference name " + VehName + "\n")
                            LogFile.flush() 
                            Data = request.get(tswapi+ "/get/CurrentFormation/" + str(i) + ".Function.HUD_GetSpeed", headers = header).json()
 
                            if not Data['Result'] == "Error":
                                self.LocoCount += 1
                            if VehName == "Laaers":
                                if fname[3] == "B":
                                    self.SkipCurrent = 1
                                if fname[2] == "B":
                                    self.SkipCurrent = 1
                                if fname[4] == "B":
                                    self.SkipCurrent = 1
                            if not self.SkipCurrent:
                                self.AVH = self.AVH + 1
                                CurrentVehicle = Vehicle(VehName,i)
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                LogFile.write("\n")
                                LogFile.flush()
                                res = CurrentVehicle.UpdateData()
                                LogFile.write(f"res = {res}")
                                if res:
                                    LogFile.write(f"searching data for vehicle with index = {i} \n")
                                    FoundData = FindData(i)
                                    CurrentVehicle.BTT = FoundData[0]
                                    CurrentVehicle.BPT = FoundData[1]
                                    CurrentVehicle.BCT = FoundData[2]
                                    CurrentVehicle.isWagon = FoundData[3]
                                    CurrentVehicle.CargoWeight = FoundData[4]
                                    CurrentVehicle.DType = FoundData[5]
                                    res = CurrentVehicle.UpdateData()
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                if not str(CurrentVehicle.BTT) == str(0):
                                    self.HasGPRSwitch = 1
                                CurrentVehicle.GetCouplerType()
                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                                VehSign = ReqData['Values']['ReturnValue']['y']
                                if VehSign < 0.0:
                                    VehSign = "-"
                                else:
                                    VehSign = "+"
                                if self.LocoSign != VehSign:
                                    if not i == 0:
                                        CurrentVehicle.isBackwards = True
                                self.FormationList.append(CurrentVehicle)
                                list = CurrentVehicle.ReturnSequence() + [CurrentVehicle.GetBrakeEditor()] + [CurrentVehicle.DType]
                                self.FormationDisplay.AddVehicle(list)
                                self.FormationDisplay.SetCellValue(self.AVH-1,6,CurrentVehicle.BrakeType)
                                self.FormationDisplay.SetCellValue(self.AVH-1,7,"Open")
                                LogFile.write("Adding Vehicle to UI list \n")
                                LogFile.flush() 
                                CurrentVehicle.SetSubs()
                                self.MainSizer.Layout()
                                self.ButtonSizer.Layout()
                                self.WindowSizer.Layout()
                                self.Refresh()
                                if CurrentVehicle.BTT == 7:
                                    self.DoubleBrakeSwitchCount += 1
                                if CurrentVehicle.BTT == 420:
                                    self.DoubleBrakeSwitchCount += 1
                else:
                    self.isReverse = 1
                    ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.fl-1) + "/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                    self.LocoSign = ReqData['Values']['ReturnValue']['y']
                    if self.LocoSign < 0.0:
                        self.LocoSign = "+"
                    else:
                        self.LocoSign = "-"
                    for i in range(self.fl-1,-1,-1):
                            self.SkipCurrent = 0
                            vname = request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName", headers = header).json()
                            vname = vname['Values']['ObjectName']
                            fname = vname.split("_")
                            VehName = GetVehicleName(vname)
                            LogFile.write("Detected " + vname + " at position " + str(i) + " with reference name " + VehName + "\n")
                            LogFile.flush() 
                            Data = request.get(tswapi+ "/get/CurrentFormation/" + str(i) + ".Function.HUD_GetSpeed", headers = header).json()
                            if not Data['Result'] == "Error":
                                self.LocoCount += 1
                            if VehName == "Laaers":
                                if fname[3] == "B":
                                    self.SkipCurrent = 1
                                if fname[2] == "B":
                                    self.SkipCurrent = 1
                                if fname[4] == "B":
                                    self.SkipCurrent = 1
                            if not self.SkipCurrent:
                                self.AVH = self.AVH + 1
                                CurrentVehicle = Vehicle(VehName,i)
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                LogFile.write("\n")
                                LogFile.flush()
                                res = CurrentVehicle.UpdateData()
                                LogFile.write(f"res = {res}")
                                if res:
                                    LogFile.write(f"searching data for vehicle with index = {i} \n")
                                    FoundData = FindData(i)
                                    CurrentVehicle.BTT = FoundData[0]
                                    CurrentVehicle.BPT = FoundData[1]
                                    CurrentVehicle.BCT = FoundData[2]
                                    CurrentVehicle.isWagon = FoundData[3]
                                    CurrentVehicle.CargoWeight = FoundData[4]
                                    CurrentVehicle.DType = FoundData[5]
                                    res = CurrentVehicle.UpdateData()
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                if not str(CurrentVehicle.BTT) == str(0):
                                    self.HasGPRSwitch = 1
                                CurrentVehicle.GetCouplerType()
                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                                VehSign = ReqData['Values']['ReturnValue']['y']
                                if VehSign < 0.0:
                                    VehSign = "-"
                                else:
                                    VehSign = "+"
                                if self.LocoSign != VehSign:
                                    if not i == self.fl-1:
                                        CurrentVehicle.isBackwards = True
                                self.FormationList.append(CurrentVehicle)
                                list = CurrentVehicle.ReturnSequence() + [CurrentVehicle.GetBrakeEditor()] + [CurrentVehicle.DType]
                                self.FormationDisplay.AddVehicle(list)
                                self.FormationDisplay.SetCellValue(self.AVH-1,6,CurrentVehicle.BrakeType)
                                self.FormationDisplay.SetCellValue(self.AVH-1,7,"Open")
                                LogFile.write("Adding Vehicle to UI list \n")
                                LogFile.flush() 
                                CurrentVehicle.SetSubs()
                                self.MainSizer.Layout()
                                self.ButtonSizer.Layout()
                                self.WindowSizer.Layout()
                                self.Refresh()
                                if CurrentVehicle.BTT == 7:
                                    self.DoubleBrakeSwitchCount += 1
                                if CurrentVehicle.BTT == 420:
                                    self.DoubleBrakeSwitchCount += 1
                    self.FormationList[0].isBackwards = True
                if self.HasGPRSwitch:
                    self.Toggle5Button.Show()
                    self.ToggleAllButton.Show()
                else:
                    self.Toggle5Button.Hide()
                    self.ToggleAllButton.Hide()
        
        self.Refresh()            
        self.Bind(wx.EVT_CHOICE,self.OnThemeChange,id = ID.ThemeChoiceID)
        self.Bind(wx.EVT_CHECKBOX,self.OnTopToggleF,id = ID.OnTopToggleID)
        self.Bind(wx.EVT_CHOICE,self.OnSelection,id = ID.PressureChoiceID)
        self.Bind(wx.EVT_BUTTON, self.OnToggle5,id = ID.Toggle5ID)
        self.Bind(wx.EVT_BUTTON,self.OnToggleAll, id = ID.ToggleAllID)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED,self.OnCellChanged)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellClick)
        self.Bind(wx.EVT_BUTTON,self.OnColumnToggle, id= ID.ToggleColumnButtonID)
        self.Bind(wx.EVT_BUTTON,self.OnRefreshButton,id = ID.RefreshButtonID)
        self.Bind(wx.EVT_CLOSE,self.OnClose, source = self)
        self.UpdateThread = threading.Thread(target=self.RequestUpdate)
        self.UpdateThread.daemon = True
        self.UpdateThread.start()
    def OnClose(self,event):
            print("")
            b = str(self.GetBackgroundColour())
            b = b.replace("(","")
            b = b.replace(")","")
            t = str(self.GetForegroundColour())
            t = t.replace("(","")
            t = t.replace(")","")
            g = str(self.GetBackgroundColour())
            g = g.replace("(","")
            g = g.replace(")","")
            file = open("Program.json","w")
            file.write("{")
            file.write("\n")
            file.write('"' + "BackgroundColour" + '"' + ':' +'"' + b +'"'  +"," ) 
            file.write("\n")
            file.write('"' + "TextColour" + '"' + ':' +'"' + t +'"' + "," ) 
            file.write("\n")
            file.write('"' + "GridLineColour" + '"' + ':' +'"' + g +'"') 
            file.write("\n")
            file.write("}")
            file.close()
            wx.Exit()
    def OnColumnToggle(self,event):
        col = ColumnDialog(self,7)
        col.Show()
    def OnThemeChange(self,event):
        if event.GetSelection() == 0:
            self.BackgroundColourC = [51,51,51]
            self.TextColourC = [137,206,148]
            self.GridLineColourC = [82,82,82]
        if event.GetSelection() == 1:
            self.TextColourC = [247,178,189]
            self.BackgroundColourC = [5,50,37]
            self.GridLineColourC = [82,82,82]
        if event.GetSelection() == 2:
            self.TextColourC = [242,244,243]
            self.BackgroundColourC = [10,9,8]
            self.GridLineColourC = [82,82,82]
        if event.GetSelection() == 3:
            self.TextColourC = [0,0,0]
            self.BackgroundColourC = [35,201,255]
            self.GridLineColourC = [82,82,82]
        if event.GetSelection() == 4:
            th = ThemeWindow(self)
            th.Show()
        self.UpdateTheme(self.TextColourC,self.BackgroundColourC,self.GridLineColourC)
    def OnRefreshButton(self,event):
        self.RebuildFormation()

    def OnCellClick(self,event):
        Col = event.GetCol()
        Row = event.GetRow()
        if Col == 8:
            self.FormationList[Row].ChangeCoupling(1,1)
        if Col == 9:
            self.FormationList[Row].ChangeCoupling(0,0)
    def UpdateTheme(self,TXT,BKG,GLC,fromFile = 0):
        if fromFile:
            PFile = open("Program.json","r")
            PArgs = json.load(PFile)
            PFile.close()
            BKG = GetColour(PArgs['BackgroundColour'])
            TXT = GetColour(PArgs['TextColour'])
            GLC = GetColour(PArgs['GridLineColour'])
        self.Freeze()
        self.MainPanel.SetBackgroundColour(BKG)
        self.statustext.SetForegroundColour(TXT)
        self.PBar.SetBackgroundColour(BKG)
        self.OnTopToggle.SetForegroundColour(TXT)
        self.Toggle5Button.SetBackgroundColour(BKG)
        self.Toggle5Button.SetForegroundColour(TXT)
        self.SetBackgroundColour(BKG)
        self.SetForegroundColour(TXT)
        self.ToggleAllButton.SetBackgroundColour(BKG)
        self.ToggleAllButton.SetForegroundColour(TXT)
        self.FormationDisplay.SetBackgroundColour(BKG)
        self.FormationDisplay.SetForegroundColour(TXT)
        self.FormationDisplay.SetLabelBackgroundColour(BKG)
        self.FormationDisplay.SetLabelTextColour(TXT)
        self.FormationDisplay.SetDefaultCellBackgroundColour(BKG)
        self.FormationDisplay.SetDefaultCellTextColour(TXT)
        self.FormationDisplay.SetGridLineColour(GLC)
        self.Refresh()
        self.Thaw()
    def OnCellChanged(self,event):
        Col = event.GetCol()
        Row = event.GetRow()
        Value = self.FormationDisplay.GetCellValue(Row,Col)
        Value = "[" + str(Value) + "]"
        if Col > 5:
                if Col == 6:
                    self.FormationList[Row].SetBM(Value)
                if Col == 7:
                    self.FormationList[Row].SetDistrib(Value)

    def OnEraseBackground(self, event):
        pass 
    def OnTopToggleF(self,event):
            self.ToggleWindowStyle(wx.STAY_ON_TOP)
    def UpdateText(self,text):
        self.statustext.SetLabel(text)
    def ToggleBrake(self,mode = 0):
        if not mode:
            if str(self.FormationList[1+self.LocoCount].Name) == "Sggmrss":
                for i in range(0,6+self.LocoCount):
                    self.FormationList[i].SetBM(0)
            elif str(self.FormationList[1+self.LocoCount].Name) == "Laaers":
                for i in range(0,3 + self.LocoCount):
                    self.FormationList[i].SetBM(0)
            else:
                for i in range(0,5 + self.LocoCount):
                    self.FormationList[i].SetBM(0)
        else:
            for i in range(0,self.FormationDisplay.GetNumberRows()):
                self.FormationList[i].SetBM(0)
    def OnToggle5(self,event):
        self.TogThread = threading.Thread(target = self.ToggleBrake, args = [0])
        self.TogThread.start()
    def OnToggleAll(self,event):
        self.TogThread = threading.Thread(target = self.ToggleBrake, args = [1])
        self.TogThread.start()
    
    def OnSelection(self,event):
        #print("choice made")
        global PU
        PU = self.PressureUnitChoice.GetSelection()
        #print(PU)
    def OnRefresh(self, UpdateData):
        i = 0
        BP = -1
        BC = -1
        BI = -1
        DI = -1
        BPstr = "N/A"
        BCstr = "N/A"
        BMstr = "N/A"
        Dstr  = "N/A"
        
        HasDoubleBrake = 0
        while i < self.FormationDisplay.GetNumberRows()*6:
            BP = -1
            BC = -1
            BI = -1
            DI = -1
            BPstr = "N/A"
            BCstr = "N/A"
            BMstr = "N/A"
            Dstr  = "N/A"
            HasDoubleBrake = 0
            Vidx = int(i/6) #vehicle index, divided by 6 because there are 6 entries(7 for BTT = 7/ BTT =420) for each vehicle
            #getting values
            if not PU: #BAR Pressure
                if not str(UpdateData['Entries'][i]['Values']) == "None":
                    BP = UpdateData['Entries'][i]['Values']['Pressure_BAR_G']
                    BP = round(BP,1)
                    BPstr = "BP: " + str(BP)
                if not str(UpdateData['Entries'][i+2]['Values']) == "None":
                    BC = UpdateData['Entries'][i+2]['Values']['Pressure_BAR_G']
                    BC = round(BC,1)
                    BCstr = "BC: " + str(BC)
            else: #PSI Pressure
                if not str(UpdateData['Entries'][i+1]['Values']) == "None":
                    BP = UpdateData['Entries'][i+1]['Values']['Pressure_PSI_G']
                    BP = round(BP,1)
                    BPstr = "BC: " + str(BP)
                if not str(UpdateData['Entries'][i+3]['Values']) == "None":
                    BC = UpdateData['Entries'][i+3]['Values']['Pressure_PSI_G']
                    BC = round(BC,1)
                    BCstr = "BC: " + str(BC)
            if not str(UpdateData['Entries'][i+4]['Values']) == "None":  #brake mode
                BI = UpdateData['Entries'][i+4]['Values']['ReturnValue']
                BMstr = self.FormationList[Vidx].GetBM(BI)
            if self.FormationList[Vidx].BTT == 7: #for the OBB1020, E94/E194
                HasDoubleBrake = 1
            if self.FormationList[Vidx].BTT == 420: #for the TADGS, the switches arent synchronised and if one is in P mode the wagon will be in P mode
                HasDoubleBrake = 1
            if HasDoubleBrake:
                if not str(UpdateData['Entries'][i+5]['Values']) == "None":
                    BI = UpdateData['Entries'][i+5]['Values']['ReturnValue']
                    BMstr += self.FormationList[Vidx].GetBM(BI)
                    i = i+1
            if not str(UpdateData['Entries'][i+5]['Values']) == "None":
                    if not self.FormationList[Vidx].DType == 5:
                        DI = UpdateData['Entries'][i+5]['Values']['ReturnValue']
                        Dstr = self.FormationList[Vidx].GetDstr(DI)
                    else:
                        DI = UpdateData['Entries'][i+5]['Values']['ValvePosition']
                        Dstr = self.FormationList[Vidx].GetDstr(DI)


            #updating the grid
            self.FormationDisplay.SetCellValue(Vidx,0,self.FormationList[Vidx].Name)
            self.FormationDisplay.SetCellValue(Vidx,1,BMstr) 
            self.FormationDisplay.SetCellValue(Vidx,2,BPstr) 
            self.FormationDisplay.SetCellValue(Vidx,3,BCstr)
            if not self.FormationDisplay.GetCellValue(Vidx,6) == BMstr:  #so we dont override user input
                self.FormationDisplay.SetCellValue(Vidx,6,BMstr)
            if not self.FormationDisplay.GetCellValue(Vidx,6) == Dstr:
                self.FormationDisplay.SetCellValue(Vidx,7,Dstr)
            i = i+6 # move to the next vehicle
                    
    def ClearList(self):
        print("Clearing...")
        self.VehCount = 0
        self.statustext.SetLabel("No Formation Detected,Clearing UI")
        if self.FormationDisplay.GetNumberRows() >0 :
            self.Freeze()
            print(self.FormationDisplay.GetNumberRows())
            self.FormationDisplay.DeleteRows(0,self.FormationDisplay.GetNumberRows())
            self.FormationDisplay.ClearGrid()
            self.Thaw()
        
        

        self.statustext.SetLabel("Waiting for Formation")
    
    def UpdateOptions(self):
        pass
    def RebuildFormation(self):
        self.Rebuilding = 1
        self.AVH = 0
        self.LocoCount = 0
        self.ClearList()
        LogFile.write("Rebuilding Formation \n")
        LogFile.flush() # Add this line
        requests.delete(tswapi + "/subscription/?Subscription=42", headers = header)
        self.statustext.SetLabel("Rebuilding Formation")
        self.Freeze()

        self.FormationLength = 0
        self.text = request.get(tswapi + "/get/CurrentFormation.FormationLength", headers = header)
        self.text = self.text.json()
        self.fl = int(self.text['Values']['FormationLength'])
        LogFile.write("Detected " + str(self.fl) + " vehicles \n")
        LogFile.flush() 
        self.FormationLength = 0.0
        self.FormationList = []
        ReqData = request.get(tswapi + "/get/CurrentFormation/0.Function.HUD_GetSpeed",headers = header).json()

        if not ReqData['Result'] == "Error":
                    self.isReverse = 0
                    ReqData = request.get(tswapi + "/get/CurrentFormation/0/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                    self.LocoSign = ReqData['Values']['ReturnValue']['y']
                    if self.LocoSign < 0.0:
                        self.LocoSign = "-"
                    else:
                        self.LocoSign = "+"
                    for i in range(self.fl):
                            self.SkipCurrent = 0
                            print(i)
                            print(str(request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName ", headers = header).url))
                            vname = request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName ", headers = header).json()
                            vname = vname['Values']['ObjectName']
                            print(vname)
                            fname = vname.split("_")
                            VehName = GetVehicleName(vname)
                            print(VehName)
                            LogFile.write("Detected " + vname + " at position " + str(i) + " with reference name " + VehName + "\n")
                            LogFile.flush() 
                            Data = request.get(tswapi+ "/get/CurrentFormation/" + str(i) + ".Function.HUD_GetSpeed", headers = header).json()
 
                            if not Data['Result'] == "Error":
                                self.LocoCount += 1
                            if VehName == "Laaers":
                                if fname[3] == "B":
                                    self.SkipCurrent = 1
                                if fname[2] == "B":
                                    self.SkipCurrent = 1
                                if fname[4] == "B":
                                    self.SkipCurrent = 1
                            if not self.SkipCurrent:
                                self.AVH = self.AVH + 1
                                CurrentVehicle = Vehicle(VehName,i)
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                LogFile.write("\n")
                                LogFile.flush()
                                res = CurrentVehicle.UpdateData()
                                LogFile.write(f"res = {res}")
                                if res:
                                    LogFile.write(f"searching data for vehicle with index = {i} \n")
                                    FoundData = FindData(i)
                                    CurrentVehicle.BTT = FoundData[0]
                                    CurrentVehicle.BPT = FoundData[1]
                                    CurrentVehicle.BCT = FoundData[2]
                                    CurrentVehicle.isWagon = FoundData[3]
                                    CurrentVehicle.CargoWeight = FoundData[4]
                                    CurrentVehicle.DType = FoundData[5]
                                    res = CurrentVehicle.UpdateData()
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                if not str(CurrentVehicle.BTT) == str(0):
                                    self.HasGPRSwitch = 1
                                CurrentVehicle.GetCouplerType()
                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                                VehSign = ReqData['Values']['ReturnValue']['y']
                                if VehSign < 0.0:
                                    VehSign = "-"
                                else:
                                    VehSign = "+"
                                if self.LocoSign != VehSign:
                                    if not i == 0:
                                        CurrentVehicle.isBackwards = True
                                self.FormationList.append(CurrentVehicle)
                                list = CurrentVehicle.ReturnSequence() + [CurrentVehicle.GetBrakeEditor()] + [CurrentVehicle.DType]
                                print(list)
                                self.FormationDisplay.AddVehicle(list)
                                self.FormationDisplay.SetCellValue(self.AVH-1,6,CurrentVehicle.BrakeType)
                                self.FormationDisplay.SetCellValue(self.AVH-1,7,"Open")
                                LogFile.write("Adding Vehicle to UI list \n")
                                LogFile.flush() 
                                CurrentVehicle.SetSubs()
                                self.MainSizer.Layout()
                                self.ButtonSizer.Layout()
                                self.WindowSizer.Layout()
                                self.Refresh()
                                if CurrentVehicle.BTT == 7:
                                    self.DoubleBrakeSwitchCount += 1
                                if CurrentVehicle.BTT == 420:
                                    self.DoubleBrakeSwitchCount += 1
        else:
                    self.isReverse = 1
                    ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(self.fl-1) + "/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                    self.LocoSign = ReqData['Values']['ReturnValue']['y']
                    if self.LocoSign < 0.0:
                        self.LocoSign = "+"
                    else:
                        self.LocoSign = "-"
                    for i in range(self.fl-1,-1,-1):
                            self.SkipCurrent = 0
                            vname = request.get(tswapi + "/get/CurrentFormation/" + str(i) + ".ObjectName", headers = header).json()
                            vname = vname['Values']['ObjectName']
                            fname = vname.split("_")
                            VehName = GetVehicleName(vname)
                            print(VehName)
                            LogFile.write("Detected " + vname + " at position " + str(i) + " with reference name " + VehName + "\n")
                            LogFile.flush() 
                            Data = request.get(tswapi+ "/get/CurrentFormation/" + str(i) + ".Function.HUD_GetSpeed", headers = header).json()
                            if not Data['Result'] == "Error":
                                self.LocoCount += 1
                            if VehName == "Laaers":
                                if fname[3] == "B":
                                    self.SkipCurrent = 1
                                if fname[2] == "B":
                                    self.SkipCurrent = 1
                                if fname[4] == "B":
                                    self.SkipCurrent = 1
                            if not self.SkipCurrent:
                                self.AVH = self.AVH + 1
                                CurrentVehicle = Vehicle(VehName,i)
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                LogFile.write("\n")
                                LogFile.flush()
                                res = CurrentVehicle.UpdateData()
                                LogFile.write(f"res = {res}")
                                if res:
                                    LogFile.write(f"searching data for vehicle with index = {i} \n")
                                    FoundData = FindData(i)
                                    CurrentVehicle.BTT = FoundData[0]
                                    CurrentVehicle.BPT = FoundData[1]
                                    CurrentVehicle.BCT = FoundData[2]
                                    CurrentVehicle.isWagon = FoundData[3]
                                    CurrentVehicle.CargoWeight = FoundData[4]
                                    CurrentVehicle.DType = FoundData[5]
                                    res = CurrentVehicle.UpdateData()
                                LogFile.write(str(CurrentVehicle.PrintData()))
                                if not str(CurrentVehicle.BTT) == str(0):
                                    self.HasGPRSwitch = 1
                                CurrentVehicle.GetCouplerType()
                                ReqData = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/ModelChildActorComponent0.Function.GetForwardVector",headers = header).json()
                                VehSign = ReqData['Values']['ReturnValue']['y']
                                if VehSign < 0.0:
                                    VehSign = "-"
                                else:
                                    VehSign = "+"
                                if self.LocoSign != VehSign:
                                    if not i == self.fl-1:
                                        CurrentVehicle.isBackwards = True
                                self.FormationList.append(CurrentVehicle)
                                list = CurrentVehicle.ReturnSequence() + [CurrentVehicle.GetBrakeEditor()] + [CurrentVehicle.DType]
                                
                                self.FormationDisplay.AddVehicle(list)
                                self.FormationDisplay.SetCellValue(self.AVH-1,6,CurrentVehicle.BrakeType)
                                self.FormationDisplay.SetCellValue(self.AVH-1,7,"Open")
                                LogFile.write("Adding Vehicle to UI list \n")
                                LogFile.flush() 
                                CurrentVehicle.SetSubs()
                                self.MainSizer.Layout()
                                self.ButtonSizer.Layout()
                                self.WindowSizer.Layout()
                                self.Refresh()
                                if CurrentVehicle.BTT == 7:
                                    self.DoubleBrakeSwitchCount += 1
                                if CurrentVehicle.BTT == 420:
                                    self.DoubleBrakeSwitchCount += 1
    





        if self.HasGPRSwitch:
            self.Toggle5Button.Show()
            self.ToggleAllButton.Show()
        else:
                self.Toggle5Button.Hide()
                self.ToggleAllButton.Hide()
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
                            if self.VehCount > 1:
                                vname = request.get(tswapi + "/get/CurrentFormation/1.ObjectName ", headers = header).json()
                                vname = vname['Values']['ObjectName']
                                fname = vname.split("_")
                                VehName2 = GetVehicleName(vname)
                                if not self.isReverse:
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
                        if MainWindow.VehCount:
                            wx.CallAfter(self.ClearList)
                        time.sleep(1)
                    if Vh:
                        if UpdateData:
                 
                            wx.CallAfter(self.OnRefresh,UpdateData)
            else:
                self.UpdateText("Waiting for TSW")
                if MainWindow.VehCount:
                    self.ClearList()
            time.sleep(0.3)

    


app = wx.App(False,"ProgramOutput.log",)
MainWindow = MainWindowClass(None, "Formation Viewer 1.2")
app.MainLoop()