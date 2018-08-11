import numpy as np
import wx
import wx.lib.agw.aui as aui
import wx.py as py
from . import propgrid as pg
from . import formatters as fmt
from . import enumtype
from . import propart as pa

class MainFrame(wx.Frame):
    ID_ART_NATIVE = wx.NewId()
    ID_ART_DEFAULT = wx.NewId()
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'PropGrid Demo', size=(800, 600))
        self._mgr = aui.AuiManager()

        # tell AuiManager to manage this frame
        self._mgr.SetManagedWindow(self)
        self._mgr.SetAGWFlags(self._mgr.GetAGWFlags()
                              | aui.AUI_MGR_ALLOW_ACTIVE_PANE
                              | aui.AUI_MGR_SMOOTH_DOCKING
                              | aui.AUI_MGR_USE_NATIVE_MINIFRAMES
                              | aui.AUI_MGR_LIVE_RESIZE)
        menubar = wx.MenuBar()
        viewMenu = wx.Menu()
        item = wx.MenuItem(viewMenu, self.ID_ART_DEFAULT, text="Default Art",
                           kind=wx.ITEM_CHECK)
        viewMenu.Append(item)
        item = wx.MenuItem(viewMenu, self.ID_ART_NATIVE, text="Native Art",
                           kind=wx.ITEM_CHECK)
        viewMenu.Append(item)
        menubar.Append(viewMenu, '&Options')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_TOOL, self.OnProcessTool)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateCmdUI)


        self.propgrid = pg.PropGrid(self)
        g = self.propgrid

        # general
        p = g.InsertSeparator('general', 'general')

        p = g.InsertProperty('string', 'string', 'hello world!')
        p.SetIndent(1)

        p = g.InsertProperty('disable', 'disable', 'hello world!')
        p.SetIndent(1)
        p.Enable(False)

        p = g.InsertProperty('italic', 'italic', 'hello world!')
        p.SetIndent(1)
        p.Italic()

        p = g.InsertProperty('with check', 'with check', 'hello world!')
        p.SetIndent(1)
        p.SetShowCheck(True)

        p = g.InsertProperty('integer', 'integer', 42)
        p.SetIndent(1)
        p.SetFormatter(fmt.IntFormatter())

        p = g.InsertProperty('hex', 'hex', 42)
        p.SetIndent(1)
        p.SetFormatter(fmt.HexFormatter())

        p = g.InsertProperty('bin', 'bin', 42)
        p.SetIndent(1)
        p.SetFormatter(fmt.BinFormatter())

        p = g.InsertProperty('float', 'float', 42.0)
        p.SetIndent(1)
        p.SetFormatter(fmt.FloatFormatter())

        p = g.InsertProperty('date', 'date', wx.DateTime.Today())
        p.SetIndent(1)
        p.SetFormatter(fmt.DateFormatter())

        p = g.InsertProperty('time', 'time', wx.DateTime.Now())
        p.SetIndent(1)
        p.SetFormatter(fmt.TimeFormatter())

        p = g.InsertProperty('datetime', 'datetime', wx.DateTime.Now())
        p.SetIndent(1)
        p.SetFormatter(fmt.DateTimeFormatter())
        p.SetControlStyle('none')

        # control
        p = g.InsertSeparator('type', 'type')

        p = g.InsertProperty('editbox', 'editbox', 'string')
        p.SetIndent(1)

        p = g.InsertProperty('choice', 'choice', 1)
        choices = enumtype.EnumType(Monday=1, Tuesday=2, Wednesday=3,
                                    Thursday=4, Friday=5, Saturday=6, Sunday=7)
        p.SetFormatter(fmt.EnumFormatter(choices))
        p.SetIndent(1)

        p = g.InsertProperty('dir_dialog', 'folder', '/home')
        #p.SetControlStyle('dir_dialog')
        p.SetFormatter(fmt.PathFormatter(False, 'folder'))
        p.SetIndent(1)

        p = g.InsertProperty('file_dialog', 'file', '/home/temp.txt')
        #p.SetControlStyle('file_dialog')
        p.SetFormatter(fmt.PathFormatter(False, 'file'))
        p.SetIndent(1)

        p = g.InsertProperty('slider', 'slider', 50)
        p.SetControlStyle('slider')
        p.SetFormatter(fmt.IntFormatter(1, 101))
        p.SetIndent(1)

        p = g.InsertProperty('spin', 'spin', 50)
        p.SetControlStyle('spin')
        p.SetFormatter(fmt.IntFormatter(1, 100))
        p.SetIndent(1)

        p = g.InsertProperty('checkbox', 'checkbox', 0)
        p.SetControlStyle('checkbox')
        p.SetFormatter(fmt.BoolFormatter())
        p.SetIndent(1)

        p = g.InsertProperty('radiobox', 'radiobox', 1)
        p.SetFormatter(fmt.EnumFormatter(choices))
        p.SetControlStyle('radiobox')
        p.SetIndent(1)

        # formatter
        p = g.InsertProperty('integer', 'Integer', 10)
        p.SetFormatter(fmt.IntFormatter())
        p.SetIndent(1)

        # color
        self.clr_map = np.array([[170., 110.,  40., 255.],
                               [  0.,  0., 128., 255.],
                               [255., 225., 25., 255.],
                               [128., 128., 128.,255.],
                               [128.,   0.,   0.,255.],
                               [  0., 128., 128.,255.],
                               [  0.,   0.,   0.,255.],
                               [210.,245.,  60., 255.],
                               [250., 190., 190., 255.],
                               [145.,  30., 180., 255.],
                               [128., 128.,   0., 255.],
                               [240.,  50., 230., 255.],
                               [230.,  25.,  75., 255.],
                               [255., 255., 255., 255.],
                               [230., 190., 255., 255.],
                               [255., 215., 180., 255.],
                               [ 60., 180.,  75., 255.],
                               [255., 250., 200., 255.],
                               [245., 130.,  48., 255.],
                               [0.,   130., 200., 255.],
                               [70.,  240., 240., 255.],
                               [170., 255., 195., 255.]])/255
        chex = self.rgb2hex(self.clr_map[:, :-1])
        p = self.propgrid.InsertSeparator("color", "color")
        for i, c in enumerate(chex):
            p = self.propgrid.InsertProperty("clr-%d"%i, '%d'%i, wx.Colour(c))
            #p.SetControlStyle(pg.PROP_CTRL_COLOR)
            p.SetBgColor(c, c, c)
            p.SetFormatter(fmt.ColorFormatter())
            t = wx.Colour(c)
            t.SetRGB(t.GetRGB()^0xFFFFFF)
            t = t.GetAsString(wx.C2S_HTML_SYNTAX)
            p.SetTextColor(t, t, t)
            p.SetIndent(1)

        pane_grid = aui.AuiPaneInfo().Name("propgrid").Caption("PropGrid").\
                    CenterPane()
        self._mgr.AddPane(self.propgrid, pane_grid)
        ns = {}
        ns['wx'] = wx
        ns['app'] = wx.GetApp()
        ns['frame'] = self
        self.shell = py.shell.Shell(self, -1, locals=ns)

        pane_shell = aui.AuiPaneInfo().Name("Shell").Caption("Shell").Bottom()\
                          .BestSize((300, 300)).DestroyOnClose(False).Snappable()\
                          .Dockable().MinimizeButton(True).MaximizeButton(True)\
                          .Row(-1).Bottom().Position(99)

        self._mgr.AddPane(self.shell, pane_shell)
        self._mgr.ShowPane(g, True)
        self._mgr.MinimizePane(pane_shell)
        self._mgr.Update()

        self.Bind(pg.EVT_PROP_CHANGED, self.OnPropChanged, id=wx.ID_ANY)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(100)

    def rgb2hex(self, clr):
        clr = np.sum(clr*255*[2**16, 2**8, 1], 1).astype(np.int32)
        return ["#{:06x}".format(c) for c in clr]

    def OnPropChanged(self, evt):
        p = evt.GetProperty()
        if p.GetName().startswith('clr-'):
            idx = int(p.GetLabel())
            if idx >= 0 and idx < len(self.clr_map):
                t = wx.Colour(p.GetValue())
                self.clr_map[idx] = [t.Red()/255., t.Green()/255., t.Blue()/255., 1.]
                c = t.GetAsString(wx.C2S_HTML_SYNTAX)
                p.SetBgColor(c, c, c)
                t.SetRGB(t.GetRGB()^0xFFFFFF)
                t = t.GetAsString(wx.C2S_HTML_SYNTAX)
                p.SetTextColor(t, t, t)

    def OnTimer(self, event):
        p = self.propgrid.GetProperty('datetime')
        if p:
            p.SetValue(wx.DateTime.Now())

    def OnUpdateCmdUI(self, event):
        eid = event.GetId()
        if eid == self.ID_ART_NATIVE:
            event.Check(type(self.propgrid.GetArtProvider()) == pa.PropArtNative)
        elif eid == self.ID_ART_DEFAULT:
            event.Check(type(self.propgrid.GetArtProvider()) == pa.PropArtDefault)
        else:
            event.Skip()

    def OnProcessTool(self, event):
        eid = event.GetId()
        if eid == self.ID_ART_NATIVE:
            self.propgrid.SetArtProvider(pa.PropArtNative())
        elif eid == self.ID_ART_DEFAULT:
            self.propgrid.SetArtProvider(pa.PropArtDefault())
        else:
            event.Skip()

class RunApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        frame = MainFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        self.frame = frame
        return True

def main():
    app = RunApp()
    app.MainLoop()

if __name__ == '__main__':
    main()
