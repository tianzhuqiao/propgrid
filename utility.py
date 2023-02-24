import wx
from wx.lib.agw import aui

def PopupMenu(wnd, menu):
    if not wnd or not menu:
        return wx.ID_NONE

    cc = aui.ToolbarCommandCapture()
    wnd.PushEventHandler(cc)

    wnd.PopupMenu(menu)

    command = cc.GetCommandId()
    wnd.PopEventHandler(True)
    return command
