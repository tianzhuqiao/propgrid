import wx
from .propxpm import radio_xpm, tree_xpm

def BitmapFromXPM(xpm):
    xpm_b = [x.encode('utf-8') for x in xpm]
    return wx.Bitmap(xpm_b)

class PropArtNative(object):

    def __init__(self):
        self.margin = {'top':0, 'bottom':0, 'left':0, 'right':0}
        self.gap_x = 2
        self.title_width = 150
        self.expansion_width = 12
        self.check_width = 16
        self.splitter_width = 8
        self.indent_width = 28
        self._font_label = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._font_value = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.text_clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        self.text_clr_sel = wx.WHITE
        self.text_clr_disabled = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        self.bg_clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self.bg_clr_sel = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self.bg_clr_disabled = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)

    def SetTitleWidth(self, width):
        """set the title width"""
        self.title_width = width

    def GetTitleWidth(self):
        """return the width"""
        return self.title_width

    def SetLabelFont(self, font):
        """set label font"""
        self._font_label = font

    def GetLabelFont(self):
        """get label font"""
        return self._font_label

    def SetValueFont(self, font):
        """set value font"""
        self._font_value = font

    def GetValueFont(self):
        """get value font"""
        return self._font_value

    def SetTextColor(self, clr=None, clr_sel=None, clr_disabled=None):
        """
        set the text colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.text_clr = clr
        if not self.text_clr:
            self.text_clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        self.text_clr_sel = clr_sel
        if not self.text_clr_sel:
            self.text_clr_sel = wx.WHITE
        self.text_clr_disabled = clr_disabled
        if not self.text_clr_disabled:
            self.text_clr_disabled = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

    def GetTextColor(self):
        """get the text colors"""
        return (self.text_clr, self.text_clr_sel, self.text_clr_disabled)

    def SetBgColor(self, clr=None, clr_sel=None, clr_disabled=None):
        """
        set the background colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        GetColour = wx.SystemSettings.GetColour
        self.bg_clr = clr
        if not self.bg_clr:
            self.bg_clr = GetColour(wx.SYS_COLOUR_WINDOW)
        self.bg_clr_sel = clr_sel
        if not self.bg_clr_sel:
            self.bg_clr_sel = GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self.bg_clr_disabled = clr_disabled
        if not self.bg_clr_disabled:
            self.bg_clr_disabled = GetColour(wx.SYS_COLOUR_3DFACE)

    def GetBgColor(self):
        """get the background colors"""
        return (self.bg_clr, self.bg_clr_sel, self.bg_clr_disabled)

    def PrepareDrawRect(self, p):
        """calculate the rect for each section"""
        mx = self.gap_x
        irc = p.GetRect()
        irc.SetLeft(irc.GetLeft()+self.margin['left'])
        irc.SetRight(irc.GetRight()+self.margin['right'])
        irc.SetTop(irc.GetTop()+self.margin['top'])
        irc.SetBottom(irc.GetBottom()+self.margin['bottom'])
        x = irc.x
        x = x + mx*2 + p.indent*self.indent_width

        if self.expansion_width > 0 and p.HasChildren():
            # expander icon
            rc = wx.Rect(*irc)
            rc.x = x + mx
            rc.SetWidth(self.expansion_width)
            p.regions['expander'] = rc
            x = rc.right

        if self.check_width > 0 and p.IsShowCheck():
            # radio/check icon
            rc = wx.Rect(*irc)
            rc.x = x + mx
            rc.SetWidth(self.check_width+2)
            p.regions['check'] = rc
            x = rc.right

        # label
        p.regions['label'] = wx.Rect(*irc)
        p.regions['label'].x = x + mx*2

        if not p.IsSeparator():
            title_width = p.title_width
            if title_width < 0:
                title_width = self.title_width
            p.regions['label'].SetRight(title_width)
            x = p.regions['label'].right

            rc = wx.Rect(*irc)
            rc.x = x + mx
            rc.SetWidth(self.splitter_width)
            p.regions['splitter'] = rc
            x = rc.right

            rc = wx.Rect(*irc)
            rc.x = x
            rc.SetWidth(irc.right-x)
            rc.Deflate(1, 1)
            p.regions['value'] = rc
        else:
            # separator does not have splitter & value
            p.regions['label'].SetWidth(p.regions['label'].GetWidth() + irc.right-x)
            p.regions['splitter'] = wx.Rect(irc.right, irc.top, 0, 0)
            p.regions['value'] = wx.Rect(irc.right, irc.top, 0, 0)

    def DrawCheck(self, dc, p):
        # draw radio button
        if self.check_width > 0 and p.IsShowCheck():
            render = wx.RendererNative.Get()
            state = 0
            if not p.IsEnabled():
                state |= wx.CONTROL_DISABLED
            if p.IsChecked():
                state |= wx.CONTROL_CHECKED
            if p.IsActivated():
                state |= wx.CONTROL_FOCUSED

            w, h = self.check_width, self.check_width
            rc = p.regions['check']
            x = rc.x+(rc.width-w)/2
            y = rc.y+(rc.height-h)/2+1
            render.DrawRadioBitmap(p.grid, dc, (x, y, w, h), state)

    def DrawSplitter(self, dc, p):
        # draw splitter
        rcs = p.regions['splitter']
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rcs.left, rcs.top, rcs.left, rcs.bottom)
        dc.DrawLine(rcs.right-1, rcs.top, rcs.right-1, rcs.bottom)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHILIGHT)))
        dc.DrawLine(rcs.left+1, rcs.top, rcs.left+1, rcs.bottom)
        dc.DrawLine(rcs.right, rcs.top, rcs.right, rcs.bottom)

    def DrawLabel(self, dc, p):
        # draw label
        if p.font_label is None:
            font = self._font_label
        else:
            font = wx.Font(p.font_label)
        dc.SetFont(font)

        if not p.IsEnabled() or p.IsReadonly():
            clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        else:
            clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        dc.SetTextForeground(clr)
        rc = p.regions['label']
        dc.SetClippingRegion(rc)
        (w, h) = dc.GetTextExtent(p.label)

        dc.DrawText(p.label, rc.x, rc.y + (rc.height - h)/2)
        p.show_label_tips = w > rc.width
        dc.DestroyClippingRegion()

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

            dc.SetPen(wx.Pen(crtxt, 1, wx.PENSTYLE_TRANSPARENT))
            dc.SetBrush(wx.Brush(crbg))

            rc = p.regions['value']
            dc.DrawRectangle(rc)

            dc.SetTextForeground(crtxt)

            value = p.GetValueAsString()
            (w, h) = dc.GetTextExtent(value)
            dc.SetClippingRegion(rc)
            dc.DrawText(value, rc.x + 5, rc.top + (rc.height - h)/2)
            p.show_value_tips = rc.width < w
            dc.DestroyClippingRegion()

    def DrawExpansion(self, dc, p):
        if self.expansion_width > 0 and p.HasChildren():
            w, h = self.expansion_width, self.expansion_width
            rc = p.regions['expander']
            x = rc.x+(rc.width-w)/2
            y = rc.y+(rc.height-h)/2+1
            dc.SetPen(wx.Pen(wx.BLACK))
            dc.SetBrush(wx.BLACK_BRUSH)
            render = wx.RendererNative.Get()
            if p.IsExpanded():
                render.DrawTreeItemButton(p.grid, dc, (x, y, w, h), wx.CONTROL_EXPANDED)
            else:
                render.DrawTreeItemButton(p.grid, dc, (x, y, w, h))

    def DrawSelectedBox(self, dc, p):
        # draw select rectangle
        if p.activated:
            dc.SetPen(wx.Pen(wx.BLACK, 1, wx.PENSTYLE_DOT))
            dc.SetBrush(wx.Brush(wx.BLACK, wx.BRUSHSTYLE_TRANSPARENT))
            dc.DrawRectangle(p.GetRect())

    def DrawItem(self, dc, p):
        """draw the property"""
        if not p.IsVisible():
            return

        dc.SetBackgroundMode(wx.TRANSPARENT)

        rc = p.GetRect()
        self.PrepareDrawRect(p)

        # draw background
        bg = p.GetGrid().GetBackgroundColour()
        pen = wx.Pen(wx.BLACK, 1, wx.PENSTYLE_TRANSPARENT)
        dc.SetPen(pen)
        brush = wx.Brush(bg)
        dc.SetBrush(brush)
        dc.DrawRectangle(rc.x, rc.y, rc.width, rc.height)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rc.left, rc.bottom, rc.right, rc.bottom)
        dc.DrawLine(rc.left, rc.top, rc.left, rc.bottom)
        dc.DrawLine(rc.right-1, rc.top, rc.right-1, rc.bottom)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHILIGHT)))
        dc.DrawLine(rc.left, rc.top, rc.right, rc.top)
        dc.DrawLine(rc.left+1, rc.top, rc.left+1, rc.bottom)
        dc.DrawLine(rc.right, rc.top, rc.right, rc.bottom)

        self.DrawExpansion(dc, p)
        self.DrawLabel(dc, p)

        # separator does not have radio button, splitter bar and value sections
        if not p.IsSeparator():
            self.DrawCheck(dc, p)
            self.DrawSplitter(dc, p)
            self.DrawValue(dc, p)

        self.DrawSelectedBox(dc, p)

class PropArtSimple(PropArtNative):
    def __init__(self):
        super(PropArtSimple, self).__init__()
        self.check_width = 0
    def DrawCheck(self, dc, p):
        pass

class PropArtDefault(PropArtNative):
    def __init__(self):
        super(PropArtDefault, self).__init__()

        self.img_check = wx.ImageList(16, 16, True, 4)
        self.img_expand = wx.ImageList(12, 12, True, 2)
        self.img_check.Add(BitmapFromXPM(radio_xpm))
        self.img_expand.Add(BitmapFromXPM(tree_xpm))

        self.expansion_width = 12
        self.check_width = 16

    def DrawCheck(self, dc, p):
        # draw radio button
        if p.IsShowCheck():
            state = 0
            if not p.IsEnabled():
                state = 1
            elif p.IsChecked():
                state = 2
                if p.IsActivated():
                    state = 3

            if self.img_check.GetImageCount() == 4:
                (w, h) = self.img_check.GetSize(0)
                rc = p.regions['check']
                x = rc.x+(rc.width-w)/2
                y = rc.y+(rc.height-h)/2+1
                self.img_check.Draw(state, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)
            else:
                super(PropArtDefault, self).DrawCheck(dc, p)

    def DrawExpansion(self, dc, p):
        if p.HasChildren():
            if self.img_expand.GetImageCount() == 2:
                (w, h) = self.img_expand.GetSize(0)
                rc = p.regions['expander']
                x = rc.x+(rc.width-w)/2
                y = rc.y+(rc.height-h)/2+1
                idx = 0
                if not p.IsExpanded():
                    idx = 1
                self.img_expand.Draw(idx, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)
            else:
                super(PropArtDefault, self).DrawExpansion(dc, p)
