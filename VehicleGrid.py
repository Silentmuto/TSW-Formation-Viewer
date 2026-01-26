import wx
import wx.grid as G
import ChoiceEditors as lib
import Vehicle

class VehicleGrid(G.Grid):
	def __init__(self,parent):
		G.Grid.__init__(self,parent)
		self.CreateGrid(0,0)
		self.SetRowLabelSize(30)
		self.AppendCols(9)
		self.EnableCellEditControl(False)
		self.SetColLabelValue(0,"Name")
		self.SetColLabelValue(1,"Brake Mode")
		self.SetColLabelValue(2,"BP")
		self.SetColLabelValue(3,"BC")
		self.SetColLabelValue(4,"Weight")
		self.SetColLabelValue(5,"Load")
		self.SetColLabelValue(6,"Brake Switch")
		self.SetColLabelValue(7,"Distributor Switch")
		self.SetColLabelValue(8,"Coupling")
		#self.SetColLabelValue(9,"Rear Coupler")
		self.SetColMinimalWidth(7,140)
		self.SetColSize(7,140)
	def AddVehicle(self,values): #name, brake mode, BP,BC,Weight,Load,brakeType,isdstr
		self.AppendRows(1)
		CurrentRow = self.GetNumberRows()-1
		self.SetCellValue(CurrentRow,0,values[0])  #SetCellValue (self, row, col, s) #name
		self.SetCellValue(CurrentRow,1,values[1])  #SetCellValue (self, row, col, s) #brake mode
		self.SetCellValue(CurrentRow,2,values[2])  #SetCellValue (self, row, col, s) #bp pressure
		self.SetCellValue(CurrentRow,3,values[3])  #SetCellValue (self, row, col, s) #bc pressure
		self.SetCellValue(CurrentRow,4,values[4])  #SetCellValue (self, row, col, s) #weight
		self.SetCellValue(CurrentRow,5,values[5])  #SetCellValue (self, row, col, s) #load
		if values[6] == 0:
			self.SetCellEditor(CurrentRow,6,lib.GetGPREditor())     # SetCellEditor(self, row, col, editor)
		elif values[6] == 1:
			self.SetCellEditor(CurrentRow,6,lib.GetGPEditor())
		elif values[6] == 2:
			self.SetCellEditor(CurrentRow,6,lib.GetPRMGEditor())
		elif values[6] == 3:
			self.SetCellEditor(CurrentRow,6,lib.GetGPP2REditor())
		elif values[6] == 4:
			self.SetCellEditor(CurrentRow,6,lib.GetNullChoiceEditor())
		if values[7]:
			self.SetCellEditor(CurrentRow,7,lib.GetDistributorEditor())
		else:
			self.SetCellEditor(CurrentRow,7,lib.GetNullChoiceEditor())
		self.SetCellEditor(CurrentRow,8,lib.GetCouplerEditor())

		#SettingCells to ReadOnly
		self.SetReadOnly(CurrentRow,0)
		self.SetReadOnly(CurrentRow,1)
		self.SetReadOnly(CurrentRow,2)
		self.SetReadOnly(CurrentRow,3)
		self.SetReadOnly(CurrentRow,4)
		self.SetReadOnly(CurrentRow,5)
		