import wx.grid


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