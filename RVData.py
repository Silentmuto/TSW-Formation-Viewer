#BTT decides what request to make to get the position of the p/g/r switch
#BPT decides what request to make for the BP pressure
#BCT decides what request to make for the BC pressure
#they're relevant only for the first query as we will make a subscription for the updates
PressureUnit = [ "Pressure_BAR_G", "Pressure_PSI_G"]
    
VehicleData = {
    "BR101" : { 
        "Weight": 84,
        "BTT": 6,
        "BPT": 2, # BP = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/BP (AirPipe).Pressure_BAR_G", headers = header).json())
        "BCT": 2, #BC = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/BrakeCylinder_1.Pressure_BAR_G", headers = header).json() 
        "isWagon": False
        },
    "OBB1020" : { 
        "Weight": 120,
        "BTT" : 7,
        "BPT" : 1, # BP = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/AirPipe (BP).Pressure_BAR_G", headers = header).json()
        "BCT" : 5, #     BC = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/Brake Cylinder Volume A.Pressure_BAR_G", headers = header).json() 
        "isWagon": False
    },
    "BR103" : {
        "Weight": 114,
        "BTT": 5, #BrakeMode 
        "BPT": 3, # BP = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/HL.Pressure_BAR_G", headers = header).json() 
        "BCT": 3, # BC = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/BrakeCylinder2.Pressure_BAR_G", headers = header).json() 
        "isWagon": False,
    },
    "BR110" : {
        "Weight": 85,
        "BTT": 5,
        "BPT": 3,
        "BCT": 3,
        "isWagon": False,
    },
    "BR111" : {
        "Weight": 85,
        "BTT": 5,
        "BPT": 3,
        "BCT": 3,
        "isWagon": False,
    },
    "OBB1116": {
        "Weight": 88,
        "BTT": 8,
        "BPT": 2,  
        "BCT": 1, # BC = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/BrakeCylinder.Pressure_BAR_G", headers = header).json() 
        "isWagon": False,
    },
    "BR112" : {
        "Weight": 82.5,
        "BTT": 10, #BrakeMode_F
        "BPT": 1,
        "BCT": 1,
        "isWagon": False,
    },
    "BR114" : {
        "Weight": 82.5,
        "BTT": 5,
        "BPT": 1,
        "BCT": 1,
        "isWagon": False,
    },
    "BR140" : {
        "Weight" : 83,
        "BTT" : 5,
        "BPT" : 3,
        "BCT" : 3,
        "isWagon": False,
    },
    "BR143" : {
        "Weight": 82.5,
        "BTT": 5,
        "BPT": 1,
        "BCT": 1,
        "isWagon": False,
    },
    "DB146": {
        "Weight": 85,
        "BTT": 3,
        "BPT": 2,
        "BCT": 1,
        "isWagon": False,
    },
    "BR146-2": {
        "Weight": 85,
        "BTT": 3,
        "BPT": 2,
        "BCT": 1,
        "isWagon": False,
    },
    "BR155" : {
        "Weight": 123,
        "BTT": 4,  #BrakeMode_Switch 
        "BPT": 1,
        "BCT": 1,
        "isWagon": False,
    },
    "BR182" : {
        "Weight": 86,
        "BTT": 8,
        "BPT": 2,
        "BCT": 1,
        "isWagon": False,
    },
    "BR185" : {
        "Weight": 85,
        "BTT": 3,
        "BPT": 2,
        "BCT": 1,
        "isWagon": False,
    },
    "BR185-2" : {
        "Weight": 85,
        "BTT": 3,
        "BPT": 2,
        "BCT": 1,
        "isWagon": False,
    },
    "BR185-5" : {
        "Weight": 85,
        "BTT": 8,
        "BPT": 2,
        "BCT": 2,
        "isWagon": False,
    },
    "BR187" : {
        "Weight": 85,
        "BTT": -1,
        "BPT": 2,
        "BCT": 2,
        "isWagon": False,

    },
    "Vectron" : {
        "Weight": 90,
        "BTT": 3,
        "BPT": 2,
        "BCT": 4, # BC = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/BrakeCylinder_1_2.Pressure_BAR_G", headers = header).json() 
        "isWagon": False,
    },
    "BR194" : {
        "Weight": 120,
        "BTT": 7,
        "BPT": 1,
        "BCT": 5,
        "isWagon": False,
    },
    "BR204" : {
        "Weight": 70,
        "BTT": -1,
        "BPT": 1,
        "BCT": 2,
        "isWagon": False,
    },
    "BR218" : {
        "Weight": 80,
        "BTT": 5,
        "BPT": 3,
        "BCT": 3,
        "isWagon": False,
    },
    "BR294" : {
        "Weight": 85,
        "BTT": 5,
        "BPT": 1,
        "BCT": 1,
        "isWagon": False,
    },
    "BR363" : {
        "Weight": 55,
        "BTT": -1,
        "BPT": 1,
        "BCT": 2,
        "isWagon": False,
    },
    "BR365" : {
        "Weight": 55,
        "BTT": -1,
        "BPT": 1,
        "BCT": 2,
        "isWagon": False,
    },
    "E94" : {
        "Weight": 120,
        "BTT": 7,
        "BPT": 1,
        "BCT": 5,
        "isWagon": False,
    },
    "G6" : {
        "Weight": 65,
        "BTT": -1,
        "BPT": 1,
        "BCT": 6, # /get/CurrentFormation/0/Simulation/Bremszylinder1.Pressure_BAR_G
        "isWagon": False,
    },
    "Eanos" : {
        "Weight": 26,
        "BTT": 1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Es050" : {
        "Weight": 11,
        "BTT": 2, # PassengerGoodsValve
        "BPT": 1,
        "BCT": 7, #BC = request.get(tswapi + "/get/CurrentFormation/" + str(i) + "/Simulation/BrakeCylinder_2.Pressure_BAR_G", headers = header).json() 
        "isWagon": True,
    },
    "Falns183" : {
        "Weight": 24,
        "BTT": 2,
        "BPT": 1,
        "BCT": 7,
        "isWagon": True,
    },
    "Gbs254" : {
        "Weight": 13,
        "BTT": 2,
        "BPT": 1,
        "BCT": 7,
        "isWagon": True,
    },
    "Habbins" : {
        "Weight": 27,
        "BTT": 1, # G/P_Brake selector
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Habbiins" : {
        "Weight": 27,
        "BTT": 1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Habbiins344" : {
        "Weight": 27,
        "BTT": -1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Kijls" : {
        "Weight": 17,
        "BTT": 3, # BrakeSelector
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Rmms663" : {
        "Weight": 21,
        "BTT": 2,
        "BPT": 1,
        "BCT": 7,
        "isWagon": True,
    },
    "Roos-t645" : {
        "Weight": 25,
        "BTT": -1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Roos-t" : {
        "Weight": 25,
        "BTT": 1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Shimmns-u" : {
        "Weight": 22,
        "BTT": 0,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Shimmns" : {
        "Weight": 22,
        "BTT": 0,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Shimmns-U708" : {
        "Weight": 22,
        "BTT": 0,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Shimmns-TTU722" : {
        "Weight": 24,
        "BTT": 0,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Tadgs" : {
        "Weight": 24,
        "BTT": 420,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Tadgs959" : {
        "Weight": 24,
        "BTT": 420,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Uacns82" : {
        "Weight": 18,
        "BTT": -1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Zacns" : {
        "Weight": 23,
        "BTT": 1,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Laaers" : {
        "Weight": 30,
        "BTT" : 1,
        "BPT": 1,
        "BCT": 1,
        "isWagon" : True
    },
    "Sggmrss" : {
        "Weight" : 30,
        "BTT" : 1,
        "BPT" : 1,
        "BCT" : 1,
        "isWagon" : True 

    },
    "ABnb-703": {
        "Weight": 35,
        "BTT": 14,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Avmz" : {
        "Weight": 50,
        "BTT": 11,
        "BPT": 1,
        "BCT": 2,
        "isWagon": True,
    },
    "Bmmz" : {
        "Weight": 50,
        "BTT": 11,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bmmdz" : {
        "Weight": 45,
        "BTT": 11,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bmmbz" : {
        "Weight": 50,
        "BTT": 11,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bmz" : {
        "Weight": 55,
        "BTT": 11,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bnb-719" : {
        "Weight" : 35,
        "BTT" : 14,
        "BPT":  1,
        "BCT" : 1,
        "isWagon": True
    },
    "Bnr" : {
        "Weight": 40,
        "BTT": 12,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bnrdfz" : {
        "Weight": 40,
        "BTT": 12,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bnrdzf" : {
        "Weight": 40,
        "BTT": 12,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bpmmbdzf" : {
        "Weight": 55,
        "BTT": 11,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "Bpmz" : {
        "Weight": 50,
        "BTT": 11,
        "BPT": 1,
        "BCT": 2,
        "isWagon": True,
    },
    "Byg516" : {
        "Weight": 35,
        "BTT": 15,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "766pbzfa" : {
        "Weight": 60,
        "BTT": 13,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "785pza" : {
        "Weight": 60,
        "BTT": 13,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },
    "780pza" : {
        "Weight": 60,
        "BTT": 13,
        "BPT": 1,
        "BCT": 1,
        "isWagon": True,
    },

    }
