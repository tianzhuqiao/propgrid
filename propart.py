import wx
from .propxpm import radio_xpm, tree_xpm

def BitmapFromXPM(xpm):
    xpm_b = [x.encode('utf-8') for x in xpm]
    return wx.Bitmap(xpm_b)

class PropArtNative(object):

    def __init__(self):
        self.margin_x = 2
        self.expansion_width = 12
        self.check_width = 16
        self.splitter_width = 8
        self.indent_width = 20

    def PrepareDrawRect(self, p):
        """calculate the rect for each section"""
        mx = self.margin_x
        rc = p.GetClientRect()
        x = rc.x

        p.gripper_rc = wx.Rect(*rc)
        p.gripper_rc.x = x + mx + p.indent*self.indent_width
        p.gripper_rc.SetWidth(6)
        x = p.gripper_rc.right

        p.expander_rc = wx.Rect(*rc)
        p.expander_rc.x = x + mx
        p.expander_rc.SetWidth(self.expansion_width)
        x = p.expander_rc.right

        p.radio_rc = wx.Rect(*rc)
        p.radio_rc.x = x + mx
        p.radio_rc.SetWidth(self.check_width+2)
        x = p.radio_rc.right

        p.label_rc = wx.Rect(*rc)
        p.label_rc.x = x + mx*2
        if not p.IsSeparator():
            p.label_rc.SetRight(p.title_width)
            x = p.label_rc.right

            p.splitter_rc = wx.Rect(*rc)
            p.splitter_rc.x = x + mx
            p.splitter_rc.SetWidth(self.splitter_width)

            p.value_rc = wx.Rect(*rc)
            p.value_rc.SetX(p.splitter_rc.right)
            p.value_rc.SetWidth(rc.right-p.splitter_rc.right)
            p.value_rc.Deflate(1, 1)
        else:
            # separator does not have splitter & value
            p.label_rc.SetWidth(rc.right-p.radio_rc.right)
            p.splitter_rc = wx.Rect(rc.right, rc.top, 0, 0)
            p.value_rc = wx.Rect(rc.right, rc.top, 0, 0)

    def DrawGripper(self, dc, p):
        # draw gripper
        if p.gripper_clr:
            pen = wx.Pen(wx.BLACK, 1, wx.PENSTYLE_TRANSPARENT)
            dc.SetPen(pen)

            dc.SetBrush(wx.Brush(p.gripper_clr))
            rcg = p.gripper_rc
            dc.DrawRectangle(rcg.x, rcg.y+1, 3, rcg.height-1)

    def DrawCheck(self, dc, p):
        # draw radio button
        if p.IsShowCheck():
            render = wx.RendererNative.Get()
            state = 0
            if not p.IsEnabled():
                state |= wx.CONTROL_DISABLED
            if p.IsChecked():
                state |= wx.CONTROL_CHECKED
            if p.IsActivated():
                state |= wx.CONTROL_FOCUSED

            w, h = self.check_width, self.check_width
            x = p.radio_rc.x+(p.radio_rc.width-w)/2
            y = p.radio_rc.y+(p.radio_rc.height-h)/2+1
            render.DrawRadioBitmap(p.grid, dc, (x, y, w, h), state)

    def DrawSplitter(self, dc, p):
        # draw splitter
        rcs = p.splitter_rc
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rcs.left, rcs.top, rcs.left, rcs.bottom)
        dc.DrawLine(rcs.right-1, rcs.top, rcs.right-1, rcs.bottom)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHILIGHT)))
        dc.DrawLine(rcs.left+1, rcs.top, rcs.left+1, rcs.bottom)
        dc.DrawLine(rcs.right, rcs.top, rcs.right, rcs.bottom)

    def DrawLabel(self, dc, p):
        # draw label
        if not p.IsEnabled() or p.IsReadonly():
            clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        else:
            clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        dc.SetTextForeground(clr)
        dc.SetClippingRegion(p.label_rc)
        (w, h) = dc.GetTextExtent(p.label)

        dc.DrawText(p.label, p.label_rc.GetX(), p.label_rc.GetY() +
                    (p.label_rc.height - h)/2)
        p.show_label_tips = w > p.label_rc.width
        dc.DestroyClippingRegion()

    def DrawValue(self, dc, p):
        # draw value
        p.show_value_tips = False
        if p.window is None:
            crbg = p.bg_clr
            crtxt = wx.BLACK
            if not p.IsEnabled() or p.IsReadonly():
                crtxt = p.text_clr_disabled
                crbg = p.bg_clr_disabled
            elif p.activated:
                crtxt = p.text_clr_sel
                crbg = p.bg_clr_sel
            else:
                crtxt = p.text_clr
                crbg = p.bg_clr

            dc.SetPen(wx.Pen(crtxt, 1, wx.PENSTYLE_TRANSPARENT))
            dc.SetBrush(wx.Brush(crbg))

            dc.DrawRectangle(p.value_rc.x, p.value_rc.y,
                             p.value_rc.width, p.value_rc.height)

            dc.SetTextForeground(crtxt)

            value = p.GetValueAsString()
            (w, h) = dc.GetTextExtent(value)
            dc.SetClippingRegion(p.value_rc)
            dc.DrawText(value, p.value_rc.GetX() + 5,
                        p.value_rc.top + (p.value_rc.height - h)/2)
            p.show_value_tips = p.value_rc.width < w
            dc.DestroyClippingRegion()

    def DrawExpansion(self, dc, p):
        if p.HasChildren():
            w, h = self.expansion_width, self.expansion_width
            x = p.expander_rc.x+(p.expander_rc.width-w)/2
            y = p.expander_rc.y+(p.expander_rc.height-h)/2+1
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
            dc.DrawRectangle(p.GetClientRect())

    def DrawItem(self, dc, p):
        """draw the property"""
        if not p.IsVisible():
            return

        dc.SetBackgroundMode(wx.TRANSPARENT)

        rc = p.GetClientRect()
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

        if p.IsItalic():
            dc.SetFont(wx.ITALIC_FONT)
        else:
            dc.SetFont(wx.NORMAL_FONT)


        self.DrawExpansion(dc, p)
        self.DrawGripper(dc, p)
        self.DrawLabel(dc, p)

        # separator does not have radio button, splitter bar and value sections
        if not p.IsSeparator():
            self.DrawCheck(dc, p)
            self.DrawSplitter(dc, p)
            self.DrawValue(dc, p)

        self.DrawSelectedBox(dc, p)

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
            render = wx.RendererNative.Get()
            state = 0
            if not p.IsEnabled():
                state = 1
            elif p.IsChecked():
                state = 2
                if p.IsActivated():
                    state = 3

            if self.img_check.GetImageCount() == 4:
                (w, h) = self.img_check.GetSize(0)
                x = p.radio_rc.x+(p.radio_rc.width-w)/2
                y = p.radio_rc.y+(p.radio_rc.height-h)/2+1
                self.img_check.Draw(state, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)
            else:
                super(PropArtDefault, self).DrawCheck(dc, p)

    def DrawExpansion(self, dc, p):
        if p.HasChildren():
            if self.img_expand.GetImageCount() == 2:
                (w, h) = self.img_expand.GetSize(0)
                x = p.expander_rc.x+(p.expander_rc.width-w)/2
                y = p.expander_rc.y+(p.expander_rc.height-h)/2+1
                idx = 0
                if not p.IsExpanded():
                    idx = 1
                self.img_expand.Draw(idx, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)
            else:
                super(PropArtDefault, self).DrawExpansion(dc, p)
