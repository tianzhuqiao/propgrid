import numpy as np
import wx
import wx.lib.agw.aui as aui
import wx.py as py
from . import propgrid as pg
from . import formatters as fmt
from . import enumtype
from . import propart as pa
from .propxpm import radio_xpm, tree_xpm


def BitmapFromXPM(xpm):
    xpm_b = [x.encode('utf-8') for x in xpm]
    return wx.Bitmap(xpm_b)


class PropArtCustom(pa.PropArtNative):
    def __init__(self):
        super(PropArtCustom, self).__init__()

        self.img_expand = wx.ImageList(12, 12, True, 2)
        self.img_expand.Add(BitmapFromXPM(tree_xpm))

        self.expansion_width = 12
        self.text_clr_sel = self.text_clr

    def DrawExpansion(self, dc, p):
        if p.HasChildren():
            if self.img_expand.GetImageCount() == 2:
                (w, h) = self.img_expand.GetSize(0)
                rc = p.regions['expander']
                x = rc.x + (rc.width - w) / 2
                y = rc.y + (rc.height - h) / 2 + 1
                idx = 0
                if not p.IsExpanded():
                    idx = 1
                self.img_expand.Draw(idx, dc, x, y,
                                     wx.IMAGELIST_DRAW_TRANSPARENT)
            else:
                super(PropArtCustom, self).DrawExpansion(dc, p)

    def DrawLabel(self, dc, p):
        # draw label
        if p.font_label is None:
            font = self._font_label
        else:
            font = wx.Font(p.font_label)
        if p.IsActivated():
            dc.SetFont(font.Bold())
        else:
            dc.SetFont(font)

        if not p.IsEnabled() or p.IsReadonly():
            clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        else:
            clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        dc.SetTextForeground(clr)
        rc = p.regions['label']
        dc.SetClippingRegion(rc)
        (w, h) = dc.GetTextExtent(p.label)

        dc.DrawText(p.label, rc.x, rc.y + (rc.height - h) / 2)
        p.show_label_tips = w > rc.width
        dc.DestroyClippingRegion()

    def DrawSplitter(self, dc, p):
        # draw splitter
        rcs = p.regions['splitter']
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rcs.right - 1, rcs.top, rcs.right - 1, rcs.bottom)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHILIGHT)))
        dc.DrawLine(rcs.right, rcs.top, rcs.right, rcs.bottom)

    def DrawBackground(self, dc, p):
        # draw background
        rc = p.GetRect()
        rcs = p.regions['splitter']
        bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        brush = wx.Brush(bg)
        dc.SetBrush(brush)
        dc.DrawRectangle(rc.x, rc.y, rcs.right, rc.height)

    def DrawValue(self, dc, p):
        # draw value
        if p.font_value is None:
            font = self._font_value
        else:
            font = wx.Font(p.font_value)
        dc.SetFont(font)

        p.show_value_tips = False
        if p.window is None:
            crbg = p.bg_clr
            crtxt = wx.BLACK
            if not p.IsEnabled() or p.IsReadonly():
                crtxt = p.text_clr_disabled
                if not crtxt:
                    crtxt = self.text_clr_disabled
                crbg = p.bg_clr_disabled
                if not crbg:
                    crbg = self.bg_clr_disabled
            elif p.activated:
                crtxt = p.text_clr_sel
                if not crtxt:
                    crtxt = self.text_clr_sel
                crbg = p.bg_clr_sel
                if not crbg:
                    crbg = self.bg_clr_sel
            else:
                crtxt = p.text_clr
                if not crtxt:
                    crtxt = self.text_clr
                crbg = p.bg_clr
                if not crbg:
                    crbg = self.bg_clr
            c = wx.Colour(crbg)
            dc.SetPen(wx.Pen(wx.Colour(c), 1, wx.PENSTYLE_SOLID))
            rc = p.regions['value']
            rcbg = wx.Rect(*rc)

            if p.activated:
                dc.SetBrush(wx.Brush(wx.Colour(c.red, c.green, c.blue, 128)))
                rcbg.Deflate(0, 1)
            else:
                dc.SetBrush(wx.Brush(wx.Colour(c.red, c.green, c.blue, 255)))

            dc.DrawRectangle(rcbg)

            dc.SetPen(wx.Pen(crtxt, 1, wx.PENSTYLE_TRANSPARENT))
            dc.SetTextForeground(crtxt)

            value = p.GetValueAsString()
            (w, h) = dc.GetTextExtent(value)
            dc.SetClippingRegion(rc)
            dc.DrawText(value, rc.x + 5, rc.top + (rc.height - h) / 2)
            p.show_value_tips = rc.width < w
            dc.DestroyClippingRegion()

    def DrawBorder(self, dc, p):
        rc = p.GetRect()
        rcs = p.regions['splitter']
        # value bottom border
        crbg = p.bg_clr
        if p.IsEnabled() and not p.IsReadonly():
            crbg = p.bg_clr_disabled
            if not crbg:
                crbg = self.bg_clr_disabled
        else:
            crbg = p.bg_clr
            if not crbg:
                crbg = self.bg_clr

        dc.SetPen(wx.Pen(wx.Colour(crbg)))
        dc.DrawLine(rc.left, rc.bottom, rc.right, rc.bottom)

        # title top & bottom border
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rc.left, rc.bottom, rcs.right, rc.bottom)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHILIGHT)))
        dc.DrawLine(rc.left, rc.top, rcs.right, rc.top)


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
        item = wx.MenuItem(viewMenu,
                           self.ID_ART_NATIVE,
                           text="Native Art",
                           kind=wx.ITEM_CHECK)
        viewMenu.Append(item)
        item = wx.MenuItem(viewMenu,
                           self.ID_ART_DEFAULT,
                           text="Customized Art",
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
        p.SetValueFont(wx.Font(wx.NORMAL_FONT).Italic())

        p = g.InsertProperty('bold', 'bold', 'hello world!')
        p.SetIndent(1)
        p.SetValueFont(wx.Font(wx.NORMAL_FONT).Bold())

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

        p = g.InsertProperty('choice', 'choice', 2)
        p.SetFormatter(fmt.ChoiceFormatter([2, 4, 8, 16, 32, 64, 128, 256]))
        p.SetIndent(1)

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
        choices = enumtype.EnumType(Monday=1,
                                    Tuesday=2,
                                    Wednesday=3,
                                    Thursday=4,
                                    Friday=5,
                                    Saturday=6,
                                    Sunday=7)
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
        #p.SetFormatter(fmt.EnumFormatter(choices))
        p.SetFormatter(
            fmt.ChoiceFormatter({
                1: '1',
                0: '0',
                'Z': 'Z',
                'X': 'X'
            }))
        p.SetControlStyle('radiobox')
        p.SetIndent(1)

        p = g.InsertProperty('date', 'date', wx.DateTime.Today())
        p.SetIndent(1)
        p.SetFormatter(fmt.DateFormatter())

        p = g.InsertProperty('time', 'time', wx.DateTime.Now())
        p.SetIndent(1)
        p.SetFormatter(fmt.TimeFormatter())

        p = g.InsertProperty('font', 'font', wx.NORMAL_FONT)
        p.SetIndent(1)
        p.SetFormatter(fmt.FontFormatter())

        # color
        self.clr_map = np.array(
            [[170., 110., 40., 255.], [0., 0., 128., 255.],
             [255., 225., 25., 255.], [128., 128., 128., 255.],
             [128., 0., 0., 255.], [0., 128., 128., 255.], [0., 0., 0., 255.],
             [210., 245., 60., 255.], [250., 190., 190., 255.],
             [145., 30., 180., 255.], [128., 128., 0., 255.],
             [240., 50., 230., 255.], [230., 25., 75., 255.],
             [255., 255., 255., 255.], [230., 190., 255., 255.],
             [255., 215., 180., 255.], [60., 180., 75., 255.],
             [255., 250., 200., 255.], [245., 130., 48., 255.],
             [0., 130., 200., 255.], [70., 240., 240., 255.],
             [170., 255., 195., 255.]]) / 255
        chex = self.rgb2hex(self.clr_map[:, :-1])
        p = self.propgrid.InsertSeparator("color", "color")
        for i, c in enumerate(chex):
            p = self.propgrid.InsertProperty("clr-%d" % i, '%d' % i,
                                             wx.Colour(c))
            p.SetBgColor(c, c, c)
            p.SetFormatter(fmt.ColorFormatter())
            t = wx.Colour(c)
            t.SetRGB(t.GetRGB() ^ 0xFFFFFF)
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
        clr = np.sum(clr * 255 * [2**16, 2**8, 1], 1).astype(np.int32)
        return ["#{:06x}".format(c) for c in clr]

    def OnPropChanged(self, evt):
        p = evt.GetProperty()
        if p.GetName().startswith('clr-'):
            idx = int(p.GetLabel())
            if idx >= 0 and idx < len(self.clr_map):
                t = wx.Colour(p.GetValue())
                self.clr_map[idx] = [
                    t.Red() / 255.,
                    t.Green() / 255.,
                    t.Blue() / 255., 1.
                ]
                c = t.GetAsString(wx.C2S_HTML_SYNTAX)
                p.SetBgColor(c, c, c)
                t.SetRGB(t.GetRGB() ^ 0xFFFFFF)
                t = t.GetAsString(wx.C2S_HTML_SYNTAX)
                p.SetTextColor(t, t, t)
        if 'font' in p.GetName():
            p.SetValueFont(p.GetValue())

    def OnTimer(self, event):
        p = self.propgrid.GetProperty('datetime')
        if p:
            p.SetValue(wx.DateTime.Now())

    def OnUpdateCmdUI(self, event):
        eid = event.GetId()
        if eid == self.ID_ART_NATIVE:
            event.Check(
                type(self.propgrid.GetArtProvider()) == pa.PropArtNative)
        elif eid == self.ID_ART_DEFAULT:
            event.Check(type(self.propgrid.GetArtProvider()) == PropArtCustom)
        else:
            event.Skip()

    def OnProcessTool(self, event):
        eid = event.GetId()
        if eid == self.ID_ART_NATIVE:
            self.propgrid.SetArtProvider(pa.PropArtNative())
            self.propgrid.SetBackgroundColour(wx.NullColour)
        elif eid == self.ID_ART_DEFAULT:
            self.propgrid.SetArtProvider(PropArtCustom())
            self.propgrid.SetBackgroundColour(wx.WHITE)
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
