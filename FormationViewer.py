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
import VehicleF
from VehicleF import Vehicle
from VehicleF import GetVehicleName
#750 = Simulation/BrakePipe Simulation/BC_1
PU = 0
tswapi = "http://127.0.0.1:31270"   
subid = 42
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
print(ApiKey)
header = {"DTGCommKey": ApiKey }

VehicleF.SetAPIKey(ApiKey)

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
        wx.Dialog.__init__(self,None,-1,"Column Toggle",(0,0),(350,180))
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
        self.ColumnTog11 = wx.CheckBox(self,ID.ToggleColumnID+10,"Front Anglecock")
        self.ColumnTog12 = wx.CheckBox(self,ID.ToggleColumnID+11,"Rear Anglecock")
        self.ColumnTog13 = wx.CheckBox(self,ID.ToggleColumnID+12,"Front Gladhand")
        self.ColumnTog14 = wx.CheckBox(self,ID.ToggleColumnID+13,"Rear GladHand")
        self.ColumnTog15 = wx.CheckBox(self,ID.ToggleColumnID+14,"Handbrake")
        self.ColumnTog16 = wx.CheckBox(self,ID.ToggleColumnID+15,"Brake Heat")
        self.ColumnLab= wx.CheckBox(self,ID.ToggleColumnID+16, "Column Labels(Titles)")
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
        self.ColumnSizer.Add(self.ColumnTog11,0)
        self.ColumnSizer.Add(self.ColumnTog12,0)
        self.ColumnSizer.Add(self.ColumnTog13,0)
        self.ColumnSizer.Add(self.ColumnTog14,0)
        self.ColumnSizer.Add(self.ColumnTog15,0)
        self.ColumnSizer.Add(self.ColumnTog16,0)
        self.ColumnSizer.Add(self.ColumnLab,1,wx.LEFT)
        self.SetSizer(self.ColumnSizer)
        self.ColumnSizer.Layout()
        if not MainWindow.FormationDisplay.IsColShown(0):
            self.ColumnTog1.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(1):
            self.ColumnTog2.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(2):
            self.ColumnTog3.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(3):
            self.ColumnTog4.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(4):
            self.ColumnTog5.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(5):
            self.ColumnTog6.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(6):
            self.ColumnTog7.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(7):
            self.ColumnTog8.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(8):
            self.ColumnTog9.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(9):
            self.ColumnTog10.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(10):
            self.ColumnTog11.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(11):
            self.ColumnTog12.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(12):
            self.ColumnTog13.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(13):
            self.ColumnTog14.SetValue(1) 
        if not MainWindow.FormationDisplay.IsColShown(14):
            self.ColumnTog15.SetValue(1)
        if not MainWindow.FormationDisplay.IsColShown(15):
            self.ColumnTog16.SetValue(1)
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
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn11,id = ID.ToggleColumnID+10)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn12,id = ID.ToggleColumnID+11)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn13,id = ID.ToggleColumnID+12)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn14,id = ID.ToggleColumnID+13)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn15,id = ID.ToggleColumnID+14)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumn16,id = ID.ToggleColumnID+15)
        self.Bind(wx.EVT_CHECKBOX,self.OnColumnLab,id = ID.ToggleColumnID + 16)
        self.Bind(wx.EVT_CLOSE,self.OnClose,source = self)
    def OnClose(self,event):
        file = open("columns.ini","w")
        file.write(str(self.ColumnTog1.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog2.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog3.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog4.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog5.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog6.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog7.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog8.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog9.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog10.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog11.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog12.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog13.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog14.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog15.IsChecked()))
        file.write("\n")
        file.write(str(self.ColumnTog16.IsChecked()))
        file.write("\n")
        file.close()
        event.Skip()
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
    def OnColumn11(self,event):
        if MainWindow.FormationDisplay.IsColShown(10):
            MainWindow.FormationDisplay.HideCol(10)
        else:
            MainWindow.FormationDisplay.ShowCol(10)
    def OnColumn12(self,event):
        if MainWindow.FormationDisplay.IsColShown(11):
            MainWindow.FormationDisplay.HideCol(11)
        else:
            MainWindow.FormationDisplay.ShowCol(11)
    def OnColumn13(self,event):
        if MainWindow.FormationDisplay.IsColShown(12):
            MainWindow.FormationDisplay.HideCol(12)
        else:
            MainWindow.FormationDisplay.ShowCol(12)
    def OnColumn14(self,event):
        if MainWindow.FormationDisplay.IsColShown(13):
            MainWindow.FormationDisplay.HideCol(13)
        else:
            MainWindow.FormationDisplay.ShowCol(13)
    def OnColumn15(self,event):
        if MainWindow.FormationDisplay.IsColShown(14):
            MainWindow.FormationDisplay.HideCol(14)
        else:
            MainWindow.FormationDisplay.ShowCol(14)
    def OnColumn16(self,event):
        if MainWindow.FormationDisplay.IsColShown(15):
            MainWindow.FormationDisplay.HideCol(15)
        else:
            MainWindow.FormationDisplay.ShowCol(15)
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
    FileOpened = 0
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
        self.SecondRowSizer = wx.BoxSizer()
        LogFile.write("Frame + sizers Initialized \n")
        LogFile.flush() 
        self.FormationDisplay = VG.VehicleGrid(self.MainPanel)
        self.OnTopToggle = wx.CheckBox(self.MainPanel,ID.OnTopToggleID,label = "Stay on Top")
        self.PressureUnitChoice = wx.Choice(self.MainPanel,ID.PressureChoiceID,choices = ["BAR", "PSI"],name= "Pressure Unit Choice")
        self.Toggle5Button = buttons.GenButton(self.MainPanel,ID.Toggle5ID,"Toggle First 5")
        self.ToggleAllButton = buttons.GenButton(self.MainPanel,ID.ToggleAllID,"Toggle All Wagons")
        self.ToggleColumnButton = buttons.GenButton(self.MainPanel,ID.ToggleColumnButtonID,"Column Toggle")
        self.RefreshButton = buttons.GenButton(self.MainPanel,ID.RefreshButtonID,"Refresh")
        self.WheelButton = buttons.GenButton(self.MainPanel,ID.WheelButtonID,"Hit Wheels")
        self.ThemeChoice = wx.Choice(self.MainPanel,ID.ThemeChoiceID,choices = ["Night Moss", "Flora", "Black", "Blue","Custom"] )
        self.ThemeChoice.SetSelection(0)
        
        self.PressureUnitChoice.SetSelection(0)
        self.ButtonSizer = wx.BoxSizer()
        self.MainSizer.Add(self.FormationDisplay,1,wx.EXPAND)
        self.ButtonSizer.Add(self.OnTopToggle,0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL ,11)
        self.ButtonSizer.Add(self.PressureUnitChoice,0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL,10)
        self.ButtonSizer.Add(self.Toggle5Button,0,wx.LEFT,10)
        self.ButtonSizer.Add(self.ToggleAllButton,0,wx.LEFT,10)
        
        self.SecondRowSizer.Add(self.ToggleColumnButton,0,wx.LEFT,10)
        self.SecondRowSizer.Add(self.RefreshButton,0,wx.LEFT,10)
        self.SecondRowSizer.Add(self.WheelButton,0,wx.LEFT,10)
        self.SecondRowSizer.Add(self.ThemeChoice,0,wx.LEFT| wx.ALIGN_CENTER_VERTICAL,10)
        self.MainSizer.Add(self.ButtonSizer,0,wx.TOP,5)
        self.MainSizer.Add(self.SecondRowSizer,0,wx.TOP,5)
        


        self.MainBar = wx.MenuBar();
        self.OptionsMenu = wx.Menu("Options")
        self.OptionsMenu.AppendCheckItem(ID.ExpertControlsID,"Toggle Expert Controls")
        self.OptionsMenu.Append(ID.SubsItemID,"Subscription ID")
        self.OptionsMenu.Append(ID.ControlDisplayID,"Display settings")
        self.HelpMenu = wx.Menu("Help")
        self.MainBar.Append(self.OptionsMenu,"Options")
        self.MainBar.Append(self.HelpMenu,"Help")

        self.SetMenuBar(self.MainBar)        
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
        self.RefreshButton.SetBackgroundColour(self.BackgroundColourC)
        self.RefreshButton.SetForegroundColour(self.TextColourC)
        self.ToggleColumnButton.SetBackgroundColour(self.BackgroundColourC)
        self.ToggleColumnButton.SetForegroundColour(self.TextColourC)
        self.WheelButton.SetBackgroundColour(self.BackgroundColourC)
        self.WheelButton.SetForegroundColour(self.TextColourC)
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
        #4self.FormationDisplay.AddVehicle(["test","g","0","0","100","0","4","0"],1)
        a = Path("columns.ini")
        if a.exists():
            self.FileOpened = 1
            file = open("columns.ini","r")

        self.Refresh()
        self.Show(True)
        self.Center()
        if IsTSWOpen():
            ReqData = request.get(tswapi +"/list/CurrentFormation/",headers = header).json()
            if not ReqData['Result'] == "Error":
                donethread = threading.Thread(target =self.UpdateFunction)
                donethread.start()
            else:
                self.UpdateText("No Formation Detected")

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
        self.Bind(wx.EVT_BUTTON,self.OnWheel, source =self.WheelButton)
        self.Bind(wx.EVT_MENU,self.OnExpertToggle,id = ID.ExpertControlsID)
        self.Bind(wx.EVT_MENU,self.OnSubChange,id = ID.SubsItemID)
        self.Bind(wx.EVT_MENU,self.OnControlOption,id = ID.ControlDisplayID)
        self.UpdateThread = threading.Thread(target=self.RequestUpdate)
        self.UpdateThread.daemon = True
        if self.FileOpened:
            for i in range(16):
                a = file.readline()
                a = a.replace("\n","")
                if str(a) == "True":
                    self.FormationDisplay.HideCol(i)
        self.UpdateThread.start()
    def OnExpertToggle(self,event):
        if self.OptionsMenu.IsChecked(ID.ExpertControlsID):
            self.FormationDisplay.HideCol(10)
            self.FormationDisplay.HideCol(11)
            self.FormationDisplay.HideCol(12)
            self.FormationDisplay.HideCol(13)
            self.FormationDisplay.HideCol(14)
            self.FormationDisplay.HideCol(15)
            self.SecondRowSizer.Show(self.WheelButton,False)
            self.SecondRowSizer.Layout()
            self.Refresh()
        else:
            self.FormationDisplay.ShowCol(10)
            self.FormationDisplay.ShowCol(11)
            self.FormationDisplay.ShowCol(12)
            self.FormationDisplay.ShowCol(13)
            self.FormationDisplay.ShowCol(14)
            self.FormationDisplay.ShowCol(15)
            self.SecondRowSizer.Show(self.WheelButton,True)
            self.SecondRowSizer.Layout()
            self.Refresh()
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
    def OnControlOption(self,event):
        dialog = wx.MultiChoiceDialog(self,"Choose which controls to display","Control Display",["Pressure Choice","Toggle fist 5","Toggle all wagons","Column Toggle","Refresh","Hit Wheels","Theme Selection"])
        sel = []
        if self.PressureUnitChoice.IsShown():
            sel.append(0)
        if self.Toggle5Button.IsShown():
            sel.append(1)
        if self.ToggleAllButton.IsShown():
            sel.append(2)
        if self.ToggleColumnButton.IsShown():
            sel.append(3)
        if self.RefreshButton.IsShown():
            sel.append(4)
        if self.WheelButton.IsShown():
            sel.append(5)
        if self.ThemeChoice.IsShown():
            sel.append(6)
        dialog.SetSelections(sel)
        if dialog.ShowModal() == wx.ID_OK:
            Choices = dialog.GetSelections()
            self.PressureUnitChoice.Hide()
            self.Toggle5Button.Hide()
            self.ToggleAllButton.Hide()
            self.ToggleColumnButton.Hide()
            self.RefreshButton.Hide()
            self.WheelButton.Hide()
            self.ThemeChoice.Hide()
            for i in range(len(Choices)):
                if Choices[i] == 0:
                    self.PressureUnitChoice.Show()
                if Choices[i] == 1:
                    self.Toggle5Button.Show()
                if Choices[i] == 2:
                    self.ToggleAllButton.Show()
                if Choices[i] == 3:
                    self.ToggleColumnButton.Show()
                if Choices[i] == 4:
                    self.RefreshButton.Show()
                if Choices[i] == 5:
                    self.WheelButton.Show()
                if Choices[i] == 6:
                    self.ThemeChoice.Show()
        self.MainSizer.Layout()
        self.ButtonSizer.Layout()
        self.SecondRowSizer.Layout()
        self.WindowSizer.Layout()

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
    def OnWheel(self,event):
        WheelThread = threading.Thread(target = self.HitDaWheel)
        WheelThread.start()
    def HitDaWheel(self):
        for i in range(len(self.FormationList)):
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_1L.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_1R.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_2L.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_2R.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_3L.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_3R.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_4L.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_4R.InputValue?Value=1",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_1L.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_1R.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_2L.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_2R.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_3L.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_3R.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_4L.InputValue?Value=0",headers= header)
            request.patch(tswapi + "/set/CurrentFormation/" + str(i) + "/HitWheel_4R.InputValue?Value=0",headers= header)
    def OnSubChange(self,event):
        global subid
        subid = wx.GetNumberFromUser("Introduce the new subscription ID","New Sub ID","Change Subscription ID",subid,0,5000)
        VehicleF.SetSubID(subid)
        subrebuildthread = threading.Thread(target = self.RebuildSubs)
        subrebuildthread.start()

    def OnCellClick(self,event):
        Col = event.GetCol()
        Row = event.GetRow()
        if Col > 7 :
            if Col < 10:
                if Col == 8:
                    self.FormationList[Row].ChangeCoupling(1,1)
                if Col == 9:
                    self.FormationList[Row].ChangeCoupling(0,0)
            else:
                event.Skip()
        else:
            event.Skip()
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
        self.RefreshButton.SetBackgroundColour(BKG)
        self.RefreshButton.SetForegroundColour(TXT)
        self.ToggleColumnButton.SetBackgroundColour(BKG)
        self.ToggleColumnButton.SetForegroundColour(TXT)
        self.WheelButton.SetBackgroundColour(BKG)
        self.WheelButton.SetForegroundColour(TXT)
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
                if Col == 10:
                    self.FormationList[Row].ChangeAngleCock(Value,1)
                if Col == 11:
                    self.FormationList[Row].ChangeAngleCock(Value,0)
                if Col == 14:
                    self.hbthread = threading.Thread(target = self.FormationList[Row].ChangeHandbrake,args = [Value])
                    self.hbthread.start()

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
    def RebuildSubs(self):
        self.Rebuilding = 1
        vc = len(self.FormationList)
        for i in range(vc):
            self.UpdateText("Rebuilding Subscriptions[" + str(i+1) + "/" + str(vc)+ "]")
            self.FormationList[i].SetSubs()
        self.Rebuilding = 0
        self.UpdateText("Displaying Formation")
        
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
        while i < self.FormationDisplay.GetNumberRows()*12:
            BP = -1
            BC = -1
            BI = -1
            DI = -1
            FAC = -1 #front angle cock
            RAC = -1 # rear angle cock
            FAH = -1 #front air hose
            RAH = -1 #rear air hose
            HBK = -1 #handbrake
            BrakeState = -1 #brake temp state
            BPstr = "N/A"
            BCstr = "N/A"
            BMstr = "N/A"
            Dstr  = "N/A"
            HasDoubleBrake = 0
            Vidx = int(i/12) #vehicle index, divided by 6 because there are 6 entries(7 for BTT = 7/ BTT =420) for each vehicle
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

            if not str(UpdateData['Entries'][i+6]['Values']) == "None":
                FAC = UpdateData['Entries'][i+6]['Values']['ReturnValue']
            
            if not str(UpdateData['Entries'][i+7]['Values']) == "None":
                RAC = UpdateData['Entries'][i+7]['Values']['ReturnValue']
            if not str(UpdateData['Entries'][i+8]['Values']) == "None":
                tval = UpdateData['Entries'][i+8]['Values']['ReturnValue']
                if tval:
                    FAH = 1
                else:
                    FAH = 0
            if not str(UpdateData['Entries'][i+9]['Values']) == "None":
                tval = UpdateData['Entries'][i+9]['Values']['ReturnValue']
                if tval:
                    RAH = 1
                else:
                    RAH = 0
            if not str(UpdateData['Entries'][i+10]['Values']) == "None":
                HBK = round(UpdateData['Entries'][i+10]['Values']['Value'],2)
                HBK = HBK * 100
            if not str(UpdateData['Entries'][i+11]['Values']) == "None":
                axlelist = [UpdateData['Entries'][i+11]['Values']['Axle_1'], UpdateData['Entries'][i+11]['Values']['Axle_2']]
                BrakeState = max(axlelist)
            #updating the grid
            self.FormationDisplay.SetCellValue(Vidx,0,self.FormationList[Vidx].Name)
            self.FormationDisplay.SetCellValue(Vidx,1,BMstr) 
            self.FormationDisplay.SetCellValue(Vidx,2,BPstr) 
            self.FormationDisplay.SetCellValue(Vidx,3,BCstr)
            if not self.FormationDisplay.GetCellValue(Vidx,6) == BMstr:  #so we dont override user input
                self.FormationDisplay.SetCellValue(Vidx,6,BMstr)
            if not self.FormationDisplay.GetCellValue(Vidx,6) == Dstr:
                self.FormationDisplay.SetCellValue(Vidx,7,Dstr)
            if not self.FormationList[Vidx].Name == "Sggmrss":
                if FAC == 1:
                    self.FormationDisplay.SetCellValue(Vidx,10,"Open")
                elif FAC == 0:
                    self.FormationDisplay.SetCellValue(Vidx,10,"Closed")
                elif not FAC == -1:
                    self.FormationDisplay.SetCellValue(Vidx,10,"Partially Open")
                else:
                    self.FormationDisplay.SetCellValue(Vidx,10,"N/A")
                
                if RAC == 1:
                    self.FormationDisplay.SetCellValue(Vidx,11,"Open")
                elif RAC == 0:
                    self.FormationDisplay.SetCellValue(Vidx,11,"Closed")
                elif not RAC == -1:
                    self.FormationDisplay.SetCellValue(Vidx,11,"Partially Open")
                else:
                    self.FormationDisplay.SetCellValue(Vidx,11,"N/A")
            else:
                if RAC == 1:
                    if FAC == 0:
                        self.FormationList[Vidx].FLA = 1
                        self.FormationDisplay.SetCellValue(Vidx,10,"Open")
                        self.FormationDisplay.SetCellValue(Vidx,11,"Closed")
                    else:
                        if FAC == 1:
                            self.FormationDisplay.SetCellValue(Vidx,10,"Open")
                        elif FAC == 0:
                            self.FormationDisplay.SetCellValue(Vidx,10,"Closed")
                        elif not FAC == -1:
                            self.FormationDisplay.SetCellValue(Vidx,10,"Partially Open")
                        else:
                            self.FormationDisplay.SetCellValue(Vidx,10,"N/A")
                        
                        if RAC == 1:
                            self.FormationDisplay.SetCellValue(Vidx,11,"Open")
                        elif RAC == 0:
                            self.FormationDisplay.SetCellValue(Vidx,11,"Closed")
                        elif not RAC == -1:
                            self.FormationDisplay.SetCellValue(Vidx,11,"Partially Open")
                        else:
                            self.FormationDisplay.SetCellValue(Vidx,11,"N/A")
                else:
                        if FAC == 1:
                            self.FormationDisplay.SetCellValue(Vidx,10,"Open")
                        elif FAC == 0:
                            self.FormationDisplay.SetCellValue(Vidx,10,"Closed")
                        elif not FAC == -1:
                            self.FormationDisplay.SetCellValue(Vidx,10,"Partially Open")
                        else:
                            self.FormationDisplay.SetCellValue(Vidx,10,"N/A")
                        
                        if RAC == 1:
                            self.FormationDisplay.SetCellValue(Vidx,11,"Open")
                        elif RAC == 0:
                            self.FormationDisplay.SetCellValue(Vidx,11,"Closed")
                        elif not RAC == -1:
                            self.FormationDisplay.SetCellValue(Vidx,11,"Partially Open")
                        else:
                            self.FormationDisplay.SetCellValue(Vidx,11,"N/A")
                        
            if FAH == 1:
                self.FormationDisplay.SetCellValue(Vidx,12,"Connected")
            elif FAH == 0:
                self.FormationDisplay.SetCellValue(Vidx,12,"Disconnected")
            else:
                self.FormationDisplay.SetCellValue(Vidx,12,"N/A")
            if RAH == 1:
                self.FormationDisplay.SetCellValue(Vidx,13,"Connected")
            elif RAH == 0:
                self.FormationDisplay.SetCellValue(Vidx,13,"Disconnected")
            else:
                self.FormationDisplay.SetCellValue(Vidx,13,"N/A")
            if not HBK == -1:
                self.FormationList[Vidx].CHB = HBK
                self.FormationDisplay.SetCellValue(Vidx,14,str(HBK))
            else:
                self.FormationDisplay.SetCellValue(Vidx,14,"N/A")
            if not BrakeState == -1:
                if BrakeState == 0:
                    self.FormationDisplay.SetCellValue(Vidx,15,"Cold")
                if BrakeState == 1:
                    self.FormationDisplay.SetCellValue(Vidx,15,"Warm")
                if BrakeState == 2:
                    self.FormationDisplay.SetCellValue(Vidx,15,"Hot")
            else:
                self.FormationDisplay.SetCellValue(Vidx,15,"N/A")
            i = i+12 # move to the next vehicle
                    
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
    def UpdateFunction(self):
        self.RebuildFormation()
    def UpdateOptions(self):
        pass
    def RebuildFormation(self):
        self.Rebuilding = 1
        self.AVH = 0
        self.LocoCount = 0
        self.ClearList()
        LogFile.write("Rebuilding Formation \n")
        LogFile.flush() # Add this line
        requests.delete(tswapi + "/subscription/?Subscription=" + str(subid), headers = header)
        self.statustext.SetLabel("Rebuilding Formation")

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
                            self.UpdateText("Rebuilding Formation[" + str(i) +"/" + str(self.fl) + "]")
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
                                    CurrentVehicle.FindData()
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
                            self.UpdateText("Rebuilding Formation[" + str(self.fl-i) +"/" + str(self.fl) + "]")
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
                                    CurrentVehicle.FindData()
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
                                    UpdateData = request.get(tswapi + "/subscription?Subscription=" + str(subid), headers = header).json()
                                except requests.exceptions.ConnectionError as e:
                                    time.sleep(1)
                            else:
                                print("Formation Changed")
                                Vh = 0
                                LogFile.write("Formation Changed, Rebuilding... \n")
                                LogFile.flush() 
                                if not self.Rebuilding:
                                    donethread = threading.Thread(target =self.UpdateFunction)
                                    donethread.start()
                                    time.sleep(1)
                        else:
                            print("Formation Changed")
                            Vh = 0
                            LogFile.write("Formation Changed, Rebuilding... \n")
                            LogFile.flush() 
                            if not self.Rebuilding:
                                donethread = threading.Thread(target = self.UpdateFunction)
                                donethread.start()
                                time.sleep(1)
                    else:
                        try :
                            requests.delete(tswapi + "/subscription/?Subscription=" + str(subid), headers = header).json()
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
MainWindow = MainWindowClass(None, "Formation Viewer 1.3.1")
app.MainLoop()