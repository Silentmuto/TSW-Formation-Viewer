import wx.grid
import wx.lib
class CoupleButtonRenderer(wx.grid.GridCellRenderer):
    def Draw(self,grid, attr, dc, rect, row, col, isSelected):
        renderer = wx.RendererNative.Get()
        text = "Couple"
        renderer.DrawPushButton(grid, dc, rect)
        dc.SetFont(attr.GetFont())
        dc.SetTextForeground(attr.GetTextColour())
        dc.DrawLabel(text, rect.Deflate(2), alignment=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        dc.SetBackground(wx.Brush(attr.GetBackgroundColour()))
class UncoupleButtonRenderer(wx.grid.GridCellRenderer):
    def Draw(self,grid, attr, dc, rect, row, col, isSelected):
        renderer = wx.RendererNative.Get()
        text = "Uncouple"
        renderer.DrawPushButton(grid, dc, rect)
        dc.SetFont(attr.GetFont())
        dc.SetTextForeground(attr.GetTextColour())
        dc.DrawLabel(text, rect.Deflate(2), alignment=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        dc.SetBackground(wx.Brush(attr.GetBackgroundColour()))
def GetGPREditor():
    GPRChoiceEditor = wx.grid.GridCellChoiceEditor(["G","P","R"])
    return GPRChoiceEditor
def GetGPEditor():
    GPChoiceEditor = wx.grid.GridCellChoiceEditor(["G","P"])
    return GPChoiceEditor
def GetPRMGEditor():
    PRMGChoiceEditor = wx.grid.GridCellChoiceEditor(["P","R","R+Mg"])
    return PRMGChoiceEditor
def GetGPP2REditor():
    GPP2RChoiceEditor = wx.grid.GridCellChoiceEditor(["G","P","P2","R"])
    return GPP2RChoiceEditor
def GetNullChoiceEditor():
    NullChoiceEditor = wx.grid.GridCellChoiceEditor(["N/A"])
    return NullChoiceEditor
def GetDistributorEditor():
    DistributorChoiceEditor = wx.grid.GridCellChoiceEditor(["Close","Open"])
    return DistributorChoiceEditor
def GetCouplerEditor():
    CoupleEditor = wx.grid.GridCellChoiceEditor(["Couple","Uncouple"])
    return CoupleEditor

def GetButtonRenderer(type):
    if type == 0:
        Render = UncoupleButtonRenderer()
    else:
        Render = CoupleButtonRenderer()
    return Render