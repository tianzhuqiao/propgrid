import six
import wx
from .propxpm import radio_xpm, tree_xpm

wxEVT_PROP_SELECTED = wx.NewEventType()
wxEVT_PROP_CHANGING = wx.NewEventType()
wxEVT_PROP_CHANGED = wx.NewEventType()
wxEVT_PROP_HIGHLIGHTED = wx.NewEventType()
wxEVT_PROP_RIGHT_CLICK = wx.NewEventType()
wxEVT_PROP_COLLAPSED = wx.NewEventType()
wxEVT_PROP_EXPANDED = wx.NewEventType()
wxEVT_PROP_DOUBLE_CLICK = wx.NewEventType()
wxEVT_PROP_INDENT = wx.NewEventType()
wxEVT_PROP_KEYDOWN = wx.NewEventType()
wxEVT_PROP_RESIZE = wx.NewEventType()
wxEVT_PROP_REFRESH = wx.NewEventType()
wxEVT_PROP_DELETE = wx.NewEventType()
wxEVT_PROP_DROP = wx.NewEventType()
wxEVT_PROP_BEGIN_DRAG = wx.NewEventType()
wxEVT_PROP_CLICK_CHECK = wx.NewEventType()

EVT_PROP_SELECTED = wx.PyEventBinder(wxEVT_PROP_SELECTED, 1)
EVT_PROP_CHANGING = wx.PyEventBinder(wxEVT_PROP_CHANGING, 1)
EVT_PROP_CHANGED = wx.PyEventBinder(wxEVT_PROP_CHANGED, 1)
EVT_PROP_HIGHLIGHTED = wx.PyEventBinder(wxEVT_PROP_HIGHLIGHTED, 1)
EVT_PROP_RIGHT_CLICK = wx.PyEventBinder(wxEVT_PROP_RIGHT_CLICK, 1)
EVT_PROP_COLLAPSED = wx.PyEventBinder(wxEVT_PROP_COLLAPSED, 1)
EVT_PROP_EXPANDED = wx.PyEventBinder(wxEVT_PROP_EXPANDED, 1)
EVT_PROP_DOUBLE_CLICK = wx.PyEventBinder(wxEVT_PROP_DOUBLE_CLICK, 1)
EVT_PROP_INDENT = wx.PyEventBinder(wxEVT_PROP_INDENT, 1)
EVT_PROP_KEYDOWN = wx.PyEventBinder(wxEVT_PROP_KEYDOWN, 1)
EVT_PROP_RESIZE = wx.PyEventBinder(wxEVT_PROP_RESIZE, 1)
EVT_PROP_REFRESH = wx.PyEventBinder(wxEVT_PROP_REFRESH, 1)
EVT_PROP_DELETE = wx.PyEventBinder(wxEVT_PROP_DELETE, 1)
EVT_PROP_DROP = wx.PyEventBinder(wxEVT_PROP_DROP, 1)
EVT_PROP_BEGIN_DRAG = wx.PyEventBinder(wxEVT_PROP_BEGIN_DRAG, 1)
EVT_PROP_CLICK_CHECK = wx.PyEventBinder(wxEVT_PROP_CLICK_CHECK, 1)

PROP_CTRL_DEFAULT = 0
PROP_CTRL_NONE = 1
PROP_CTRL_EDIT = 2
PROP_CTRL_COMBO = 3
PROP_CTRL_FILE_SEL = 4
PROP_CTRL_FOLDER_SEL = 5
PROP_CTRL_SLIDER = 6
PROP_CTRL_SPIN = 7
PROP_CTRL_CHECK = 8
PROP_CTRL_RADIO = 9
PROP_CTRL_COLOR = 10
PROP_CTRL_NUM = 11

def BitmapFromXPM(xpm):
    xpm_b = [x.encode('utf-8') for x in xpm]
    return wx.Bitmap(xpm_b)

class Property(object):
    PROP_HIT_NONE = 0
    PROP_HIT_EXPAND = 1
    PROP_HIT_CHECK = 2
    PROP_HIT_TITLE = 3
    PROP_HIT_SPLITTER = 4
    PROP_HIT_VALUE = 5
    PROP_HIT_EDGE_BOTTOM = 6
    PROP_HIT_EDGE_TOP = 7

    VALIDATE_NONE = 0
    VALIDATE_DEC = 1
    VALIDATE_HEX = 2
    VALIDATE_OCT = 3
    VALIDATE_BIN = 4
    MARGIN_X = 2

    imgRadio = None
    imgExpColp = None
    def __init__(self, grid, name, label, value):
        self.grid = grid
        self.name = name
        self.label = label
        self.label_tip = ''
        self.value = value
        self.value_tip = ''
        self.description = ""
        self.value_max = 100
        self.value_min = 0
        self.title_width = 80
        self.indent = 0
        self.show_check = True
        self.checked = False
        self.activated = False
        self.enable = True
        self.italic = False
        self.has_children = False
        self.expanded = True
        self.visible = True
        self.readonly = False
        self.ctrl_type = PROP_CTRL_EDIT
        self.window = None
        self.parent = -1
        self.choices = {}
        self.SetGripperColor()
        self.SetTextColor(silent=True)
        self.SetBgColor(silent=True)
        self.min_size = wx.Size(200, 25)
        self.client_rc = wx.Rect(0, 0, 0, 0)
        self.gripper_rc = wx.Rect(0, 0, 0, 0)
        self.expander_rc = wx.Rect(0, 0, 0, 0)
        self.radio_rc = wx.Rect(0, 0, 0, 0)
        self.splitter_rc = wx.Rect(0, 0, 0, 0)
        self.label_rc = wx.Rect(0, 0, 0, 0)
        # rect include everything except the splitter and value
        self.value_rc = wx.Rect(0, 0, 0, 0)
        self.show_label_tips = False
        self.show_value_tips = False
        self.separator = False
        #self.m_validate = wx.FILTER_NONE
        #self.m_nValidateType(VALIDATE_NONE)
        if type(self).imgRadio is None or type(self).imgExpColp is None:
            type(self).imgRadio = wx.ImageList(16, 16, True, 4)
            type(self).imgExpColp = wx.ImageList(12, 12, True, 2)
            type(self).imgRadio.Add(BitmapFromXPM(radio_xpm))
            type(self).imgExpColp.Add(BitmapFromXPM(tree_xpm))

    def duplicate(self):
        """
        copy the object

        copy.deepcopy does not work since the object contains pointer to wx
        objects
        """
        p = Property(self.grid, self.name, self.label, self.value)
        p.label_tip = self.label_tip
        p.value_tip = self.value_tip
        p.description = self.description
        p.value_max = self.value_max
        p.value_min = self.value_min
        p.title_width = self.title_width
        p.indent = self.indent
        p.show_icon = self.show_icon
        p.bpCondition = self.bpCondition
        p.checked = self.checked
        p.activated = self.activated
        p.enable = self.enable
        p.italic = self.italic
        p.has_children = self.has_children
        p.expanded = self.expanded
        p.visible = self.visible
        p.readonly = self.readonly
        p.ctrl_type = self.ctrl_type
        p.parent = self.parent
        p.choices = dict(self.choices)
        p.SetGripperColor(self.gripper_clr)
        p.SetTextColor(self.text_clr, self.text_clr_sel, self.text_clr_disabled, True)
        p.SetBgColor(self.bg_clr, self.bg_clr_sel, self.bg_clr_disabled, True)
        p.show_label_tips = self.show_label_tips
        p.show_value_tips = self.show_value_tips
        p.separator = self.separator
        return p

    def SetGrid(self, grid):
        """set the grid window"""
        self.grid = grid

    def GetGrid(self):
        """return the grid window"""
        return self.grid

    def SetSeparator(self, sep, silent=False):
        """set the property to be a separator"""
        if self.separator == sep:
            return
        self.separator = sep
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def GetSeparator(self):
        """return true if the property is a separator"""
        return self.separator

    def SetControlStyle(self, style):
        """set the control type
        style: default | none | editbox | combobox | file_sel_button |
               folder_sel_button | slider | spin | checkbox | radiobox |
               color
        """
        self.UpdatePropValue()
        self.DestroyControl()
        str_style = {'default':PROP_CTRL_DEFAULT, 'none': PROP_CTRL_NONE,
                     'editbox': PROP_CTRL_EDIT, 'combobox':PROP_CTRL_COMBO,
                     'file_sel_button':PROP_CTRL_FILE_SEL,
                     'folder_sel_button': PROP_CTRL_FOLDER_SEL,
                     'slider': PROP_CTRL_SLIDER, 'spin': PROP_CTRL_SPIN,
                     'checkbox': PROP_CTRL_CHECK, 'radiobox': PROP_CTRL_RADIO,
                     'color': PROP_CTRL_COLOR}
        if isinstance(style, six.string_types):
            style = str_style.get(style, None)
        if not isinstance(style, int):
            return False
        if style < PROP_CTRL_DEFAULT or style >= PROP_CTRL_NUM:
            return False
        if style != PROP_CTRL_DEFAULT:
            self.ctrl_type = style
        return True

    def SetChoices(self, choices):
        """set the choices list
        choices:
            # dict
            SetChoice({'1':1, '0':0, 'Z':'Z', 'X':'X'})
            # list
            SetChoice([256, 512, 1024])
        """
        self.choices = {}
        # dict, split the key and value
        if isinstance(choices, dict):
            self.choices = {str(k): v for k, v in six.iteritems(choices)}
        elif isinstance(choices, list):
            self.choices = {str(v):v for v in choices}
        else:
            return False
        return True

    def SetEnable(self, enable, silent=False):
        """enable/disable the property"""
        if self.enable == enable:
            return
        self.enable = enable
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetName(self, name, silent=False):
        """set the name"""
        if self.name == name:
            return
        self.name = name
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetLabel(self, label, silent=False):
        """set the label"""
        if self.label == label:
            return
        self.label = label
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetLabelTip(self, tip):
        """set the label tip"""
        self.label_tip = tip

    def SetDescription(self, description, silent=False):
        """set the description"""
        if self.description == description:
            return
        self.description = description
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetItalicText(self, italic, silent=False):
        """turn on/of the italic text"""
        if self.italic == italic:
            return
        self.italic = italic
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetVisible(self, visible, silent=False):
        """
        show/hide the property

        The property may be hidden if its parent is in collapsed mode.
        """
        if self.visible == visible:
            return
        self.visible = visible
        if not silent:
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetParent(self, prop):
        """set the parent property"""
        if prop == self:
            return
        self.parent = prop

    def SetRange(self, minval, maxval):
        """
        set the min/max values

        It is only used in spin and slider controls.
        """
        self.value_max = float(maxval)
        self.value_min = float(minval)

    def SetShowCheck(self, show, silent=True):
        """show/hide radio button"""
        self.show_check = show
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def GetCtrlStyle(self):
        """return the control type"""
        return self.ctrl_type

    def GetChoices(self):
        """return the choices list"""
        return dict(self.choices)

    def IsEnabled(self):
        """return true if the property is enabled"""
        return self.enable

    def GetName(self):
        """get the name"""
        return self.name

    def GetLabel(self):
        """get the label"""
        return self.label

    def GetLabelTip(self):
        """get the label tip"""
        if self.label_tip:
            return self.label_tip
        return self.GetName()

    def GetValue(self):
        """get the value"""
        return self.value

    def GetValueTip(self):
        """get the valuetip"""
        if self.value_tip:
            return self.value_tip
        return self.value

    def GetDescription(self):
        """get the description"""
        return self.description

    def GetIndent(self):
        """get the indent"""
        return self.indent

    def IsExpanded(self):
        """return true if the expand/collapse button is expanded"""
        return self.expanded

    def HasChildren(self):
        """return true if the property has children"""
        return self.has_children

    def IsChecked(self):
        """return true if the radio button is checked"""
        return self.checked

    def IsItalicText(self):
        "return true if the italic is used for drawing"
        return self.italic

    def GetControlStyle(self):
        """get the control type"""
        return self.ctrl_type

    def GetActivated(self):
        """return true if the property is activated"""
        return self.activated

    def GetVisible(self):
        """return true if the property is visible"""
        return self.visible

    def GetParent(self):
        """return the parent property"""
        return self.parent

    def GetRange(self):
        """return the value range"""
        return (self.value_min, self.value_max)

    def GetReadOnly(self):
        """return true if the property is readonly"""
        return self.readonly

    def GetChecked(self):
        """return true if the radio button is checked"""
        return self.checked

    def GetShowCheck(self):
        """return whether the icon is shown"""
        return self.show_check

    def GetGripperColor(self):
        return self.gripper_clr

    def GetTextColor(self):
        """get the text colors"""
        return (self.text_clr, self.text_clr_sel, self.text_clr_disabled)

    def GetBgColor(self):
        """get the background colors"""
        return (self.bg_clr, self.bg_clr_sel, self.bg_clr_disabled)

    def SetTitleWidth(self, width):
        """set the title width"""
        self.title_width = width

    def GetTitleWidth(self):
        """return the width"""
        return self.title_width

    def Refresh(self):
        """notify the parent to redraw the property"""
        self.SendPropEvent(wxEVT_PROP_REFRESH)

    def DrawGripper(self, dc):
        # draw gripper
        if self.gripper_clr:
            pen = wx.Pen(wx.BLACK, 1, wx.TRANSPARENT)
            pen.SetColour(self.gripper_clr)
            pen.SetStyle(wx.TRANSPARENT)

            dc.SetPen(pen)

            brush = wx.Brush(self.gripper_clr)
            brush.SetStyle(wx.SOLID)
            dc.SetBrush(brush)
            rcg = self.gripper_rc
            dc.DrawRectangle(rcg.x, rcg.y+1, 3, rcg.height-1)

    def DrawCheck(self, dc):
        # draw radio button
        if self.GetShowCheck():
            state = 0
            if not self.IsEnabled():
                state = 1
            elif self.IsChecked():
                state = 2
                if self.GetActivated():
                    state = 3

            if type(self).imgRadio.GetImageCount() == 4:
                (imagex, imagey) = type(self).imgRadio.GetSize(0)
                x = self.radio_rc.x+(self.radio_rc.width-imagex)/2
                y = self.radio_rc.y+(self.radio_rc.height-imagey)/2+1
                type(self).imgRadio.Draw(state, dc, x, y,
                                         wx.IMAGELIST_DRAW_TRANSPARENT)

    def DrawSplitter(self, dc):
        # draw splitter
        rcs = self.splitter_rc
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rcs.left, rcs.top, rcs.left, rcs.bottom)
        dc.DrawLine(rcs.right-1, rcs.top, rcs.right-1, rcs.bottom)
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHILIGHT)))
        dc.DrawLine(rcs.left+1, rcs.top, rcs.left+1, rcs.bottom)
        dc.DrawLine(rcs.right, rcs.top, rcs.right, rcs.bottom)

    def DrawLabel(self, dc):
        # draw label
        if self.italic:
            dc.SetFont(wx.ITALIC_FONT)
        else:
            dc.SetFont(wx.NORMAL_FONT)

        dc.SetClippingRegion(self.label_rc)
        (w, h) = dc.GetTextExtent(self.label)

        dc.DrawText(self.label, self.label_rc.GetX(), self.label_rc.GetY() +
                    (self.label_rc.height - h)/2)
        self.show_label_tips = w > self.label_rc.width
        dc.DestroyClippingRegion()

    def DrawValue(self, dc):
        # draw value
        self.show_value_tips = False
        if self.window is None:
            crbg = self.bg_clr
            crtxt = wx.BLACK
            if not self.enable or self.GetReadOnly():
                crtxt = self.text_clr_disabled
                crbg = self.bg_clr_disabled
            elif self.activated:
                crtxt = self.text_clr_sel
                crbg = self.bg_clr_sel
            else:
                crtxt = self.text_clr
                crbg = self.bg_clr

            dc.SetPen(wx.Pen(crtxt, 1, wx.TRANSPARENT))
            dc.SetBrush(wx.Brush(crbg))

            dc.DrawRectangle(self.value_rc.x, self.value_rc.y,
                             self.value_rc.width, self.value_rc.height)

            dc.SetTextForeground(crtxt)

            value = str(self.GetValue())
            if self.description != "":
                value += " (" + self.description + ")"
            (w, h) = dc.GetTextExtent(value)
            dc.SetClippingRegion(self.value_rc)
            dc.DrawText(value, self.value_rc.GetX() + 1,
                        self.value_rc.top + (self.value_rc.height - h)/2)
            self.show_value_tips = self.value_rc.width < w
            dc.DestroyClippingRegion()

    def DrawItem(self, dc):
        """draw the property"""
        if not self.GetVisible():
            return

        dc.SetBackgroundMode(wx.TRANSPARENT)
        if self.enable:
            dc.SetTextForeground(wx.BLACK)
        else:
            dc.SetTextForeground(wx.LIGHT_GREY)

        rc = self.GetClientRect()
        self.PrepareDrawRect()

        # draw background
        bg = self.GetGrid().GetBackgroundColour()
        pen = wx.Pen(wx.BLACK, 1, wx.TRANSPARENT)
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

        # draw select rectangle
        if self.activated:
            pen.SetColour(wx.BLACK)
            pen.SetStyle(wx.DOT)

            dc.SetPen(pen)
            brush.SetStyle(wx.TRANSPARENT)
            dc.SetBrush(brush)
            dc.DrawRectangle(rc.x, rc.y, rc.width, rc.height)

        if self.HasChildren():
            if type(self).imgExpColp.GetImageCount() == 2:
                (imagex, imagey) = type(self).imgExpColp.GetSize(0)
                x = self.expander_rc.x+(self.expander_rc.width-imagex)/2
                y = self.expander_rc.y+(self.expander_rc.height-imagey)/2+1
                idx = 0
                if not self.expanded:
                    idx = 1
                type(self).imgExpColp.Draw(idx, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)

        self.DrawGripper(dc)
        self.DrawLabel(dc)

        # separator does not have radio button, splitter bar and value sections
        if self.GetSeparator():
            return

        self.DrawCheck(dc)
        self.DrawSplitter(dc)
        self.DrawValue(dc)

    def PrepareDrawRect(self):
        """calculate the rect for each section"""
        MARGIN_X = type(self).MARGIN_X
        rc = self.GetClientRect()
        x = rc.x

        self.gripper_rc = wx.Rect(*rc)
        self.gripper_rc.x = x + MARGIN_X + self.indent*20
        self.gripper_rc.SetWidth(6)
        x = self.gripper_rc.right

        self.expander_rc = wx.Rect(*rc)
        self.expander_rc.x = x + MARGIN_X
        w, _ = self.imgExpColp.GetSize()
        self.expander_rc.SetWidth(w+2)
        x = self.expander_rc.right

        self.radio_rc = wx.Rect(*rc)
        self.radio_rc.x = x + MARGIN_X
        w, _ = self.imgRadio.GetSize()
        self.radio_rc.SetWidth(w+2)
        x = self.radio_rc.right

        self.label_rc = wx.Rect(*rc)
        self.label_rc.x = x + MARGIN_X*2
        self.label_rc.SetRight(self.title_width)
        x = self.label_rc.right

        self.splitter_rc = wx.Rect(*rc)
        self.splitter_rc.x = x + MARGIN_X
        self.splitter_rc.SetWidth(8)

        self.value_rc = wx.Rect(*rc)
        self.value_rc.SetX(self.splitter_rc.right)
        self.value_rc.SetWidth(rc.right-self.splitter_rc.right)
        self.value_rc.Deflate(1, 1)

    def HitTest(self, pt):
        """find the mouse position relative to the property"""
        # bottom edge
        rc = wx.Rect(*self.client_rc)
        rc.SetTop(rc.bottom-2)
        if rc.Contains(pt):
            return self.PROP_HIT_EDGE_BOTTOM
        # top edge
        rc = wx.Rect(*self.client_rc)
        rc.SetBottom(rc.top+2)
        if rc.Contains(pt):
            return self.PROP_HIT_EDGE_TOP

        if self.expander_rc.Contains(pt):
            # expand/collapse icon
            return self.PROP_HIT_EXPAND
        elif self.radio_rc.Contains(pt):
            # radio icon
            return self.PROP_HIT_CHECK
        elif self.label_rc.Contains(pt):
            # elsewhere on the title
            return self.PROP_HIT_TITLE
        elif self.splitter_rc.Contains(pt):
            # gripper
            return self.PROP_HIT_SPLITTER
        elif self.value_rc.Contains(pt):
            # value
            return self.PROP_HIT_VALUE
        return self.PROP_HIT_NONE

    def OnMouseDown(self, pt):
        ht = self.HitTest(pt)
        # click on the expand buttons? expand it?
        if self.HasChildren() and ht == self.PROP_HIT_EXPAND:
            self.SetExpand(not self.expanded)
        elif ht == self.PROP_HIT_SPLITTER or ht == self.PROP_HIT_NONE:
            self.UpdatePropValue()
            self.DestroyControl()
        elif not self.GetReadOnly() and ht == self.PROP_HIT_VALUE:
            # show the control when in PROP_DISP_NORMAL mode
            self.CreateControl()
        return ht

    def OnMouseUp(self, pt):
        ht = self.HitTest(pt)
        if self.IsEnabled():
            # click on the check icon? change the state
            if self.GetShowCheck() and ht == self.PROP_HIT_CHECK:
                checked = self.IsChecked()
                self.SetChecked(not checked)
        return ht

    def OnMouseDoubleClick(self, pt):
        ht = self.HitTest(pt)
        if self.IsEnabled():
            if not self.GetReadOnly():
                # show the control when in PROP_DISP_NORMAL mode
                if ht == self.PROP_HIT_VALUE:
                    self.CreateControl()
            if ht == self.PROP_HIT_EXPAND:
                self.SetExpand(not self.expanded)
            self.SendPropEvent(wxEVT_PROP_DOUBLE_CLICK)
        return ht

    def OnMouseRightClick(self, pt):
        ht = self.HitTest(pt)
        if self.IsEnabled():
            #destory the control when the mouse moves out
            if ht == self.PROP_HIT_NONE:
                self.UpdatePropValue()
                self.DestroyControl()
            self.SendPropEvent(wxEVT_PROP_RIGHT_CLICK)
        return ht

    def OnMouseMove(self, pt):
        ht = self.HitTest(pt)
        return ht

    def OnTextEnter(self):
        self.UpdatePropValue()
        self.DestroyControl()
        self.SendPropEvent(wxEVT_PROP_REFRESH)

    def CreateControl(self):
        """create the control"""
        if self.window != None or self.GetSeparator():
            return
        self.PreparePropValidator()
        style = self.ctrl_type
        win = None
        if style == PROP_CTRL_EDIT:
            win = wx.TextCtrl(self.grid, wx.ID_ANY,
                              self.GetValue(), self.value_rc.GetTopLeft(),
                              wx.DefaultSize, wx.TE_PROCESS_ENTER)

            win.Bind(wx.EVT_TEXT_ENTER, self.OnPropTextEnter)
        elif style == PROP_CTRL_COMBO:
            win = wx.Choice(self.grid, wx.ID_ANY,
                            self.value_rc.GetTopLeft(), wx.DefaultSize,
                            list(six.iterkeys(self.choices)))
            for i in range(win.GetCount()):
                if win.GetString(i) == self.description:
                    win.SetSelection(i)
                    break
        elif style in [PROP_CTRL_FILE_SEL, PROP_CTRL_FOLDER_SEL]:
            # TODO
            #m_control = new BSMPropEditBtn(m_parent,IDC_BSM_PROP_CONTROL,GetValue())
            #sizeCtrl = m_control->GetSize()
            pass

        elif style == PROP_CTRL_SLIDER:
            nmax = int(self.value_max)
            nmin = int(self.value_min)
            val = int(self.value)

            win = wx.Slider(self.grid, wx.ID_ANY, val, nmin, nmax,
                            self.value_rc.GetTopLeft(), wx.DefaultSize,
                            wx.SL_LABELS | wx.SL_AUTOTICKS |
                            wx.SL_HORIZONTAL | wx.SL_TOP)

        elif style == PROP_CTRL_SPIN:
            nmax = int(self.value_max)
            nmin = int(self.value_min)
            val = int(self.value)
            win = wx.SpinCtrl(self.grid, wx.ID_ANY, "%d"%val,
                              self.value_rc.GetTopLeft(), wx.DefaultSize,
                              wx.SP_ARROW_KEYS, nmin, nmax, val)

        elif style == PROP_CTRL_CHECK:
            val = int(self.value)
            win = wx.CheckBox(self.grid, wx.ID_ANY, "",
                              self.value_rc.GetTopLeft(), wx.DefaultSize)
            win.SetValue(val != 0)

        elif style == PROP_CTRL_RADIO:
            win = wx.RadioBox(self.grid, wx.ID_ANY, "",
                              self.value_rc.GetTopLeft(), wx.DefaultSize,
                              list(six.iterkeys(self.choices)), 5, wx.RA_SPECIFY_COLS)
            for i in range(win.GetCount()):
                if win.GetString(i) == self.description:
                    win.SetSelection(i)
                    break

        elif style == PROP_CTRL_COLOR:
            win = wx.ColourPickerCtrl(self.grid, wx.ID_ANY, wx.BLACK,
                                      style=wx.CLRP_DEFAULT_STYLE |
                                      wx.CLRP_SHOW_LABEL)
            try:
                win.SetColour(self.value)
            except ValueError:
                pass

        if win:
            self.window = win
            # the window size may be large than the value rect
            self.SendPropEvent(wxEVT_PROP_RESIZE)
            self.LayoutControl()
            self.window.SetFocus()
            self.window.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnPropTextEnter(self, evt):
        """send when the enter key is pressed in the property control window"""
        if self.window:
            self.OnTextEnter()

    def OnKillFocus(self, evt):
        # destroy the control if it loses focus. Wait until the event has been
        # processed; otherwise, it may crash.
        wx.CallAfter(self.OnTextEnter)
        evt.Skip()

    def LayoutControl(self):
        """re-positioning the control"""
        if self.window is None:
            return
        (x, y) = self.grid.GetViewStart()
        rc = wx.Rect(*self.value_rc)
        rc.Offset(wx.Point(-x*5, -y*5))
        if self.ctrl_type in [PROP_CTRL_EDIT, PROP_CTRL_COMBO, PROP_CTRL_SPIN,
                              PROP_CTRL_CHECK, PROP_CTRL_RADIO, PROP_CTRL_SLIDER,
                              PROP_CTRL_FILE_SEL, PROP_CTRL_FOLDER_SEL,
                              PROP_CTRL_COLOR]:
            self.window.SetSize(rc.GetSize())
            self.window.Move(rc.GetTopLeft())

    def DestroyControl(self):
        """destroy the value setting control"""
        if self.window:
            self.window.Show(False)
            self.window.Destroy()
            self.window = None
            return True
        return False

    def PreparePropValidator(self):
        pass

    def UpdatePropValue(self):
        """update the value"""
        if self.window is None:
            return False

        value = self.value
        description = self.description
        self.value = ""
        self.description = ""
        style = self.ctrl_type
        if style == PROP_CTRL_EDIT:
            self.value = self.window.GetValue()

        elif style in [PROP_CTRL_FILE_SEL, PROP_CTRL_FOLDER_SEL]:
            self.value = self.window.GetLabel()

        elif style == PROP_CTRL_COMBO:
            comb = self.window
            self.value = comb.GetString(comb.GetSelection())
            self.description = ''
            if self.value in self.choices:
                self.description = self.value
                self.value = self.choices[self.value]

        elif style == PROP_CTRL_SLIDER:
            self.value = ("%d"%self.window.GetValue())

        elif style == PROP_CTRL_SPIN:
            self.value = ("%d"%self.window.GetValue())

        elif style == PROP_CTRL_CHECK:
            check = self.window
            self.value = ("%d"%check.GetValue())
            if check.GetValue():
                self.description = "true"
            else:
                self.description = "false"

        elif style == PROP_CTRL_RADIO:
            sel = self.window.GetSelection()
            if sel >= 0 and sel < self.window.GetCount():
                value = self.window.GetString(sel)
                if value in self.choices:
                    self.value = self.choices[value]
                    self.description = value

        elif style == PROP_CTRL_COLOR:
            clr = self.window.GetColour()
            self.value = clr.GetAsString(wx.C2S_HTML_SYNTAX)
            self.SetBgColor(self.value, self.value, self.value)
            clr.SetRGB(clr.GetRGB()^0xffffff)
            t = clr.GetAsString(wx.C2S_HTML_SYNTAX)
            self.SetTextColor(t, t, t)

        if self.SendPropEvent(wxEVT_PROP_CHANGING):
            self.SendPropEvent(wxEVT_PROP_CHANGED)
            return True
        else:
            #the parent rejects the operation, restore the original value
            self.SetDescription(description)
            self.SetValue(value)
            return False

    def UpdateDescription(self):
        """update the description"""
        self.description = ""
        style = self.ctrl_type
        if style == PROP_CTRL_EDIT:
            pass
        elif style in [PROP_CTRL_FILE_SEL, PROP_CTRL_FOLDER_SEL]:
            pass
        elif style in [PROP_CTRL_COMBO, PROP_CTRL_RADIO]:
            for k, v in six.iteritems(self.choices):
                if v == self.value:
                    self.description = k
        elif style == PROP_CTRL_SLIDER:
            pass
        elif style == PROP_CTRL_SPIN:
            pass
        elif style == PROP_CTRL_CHECK:
            value = int(self.value)
            if value == 0:
                self.description = "false"
            elif value == 1:
                self.description = "true"
        return True

    def SendPropEvent(self, event):
        """ send property grid event to parent"""
        eventObject = self.GetGrid()
        evt = PropertyEvent(event)
        evt.SetProperty(self)
        evt.SetEventObject(eventObject)
        evtHandler = eventObject.GetEventHandler()

        if evtHandler.ProcessEvent(evt):
            return not evt.GetVeto()
        return False

    def SetClientRect(self, rcClient):
        """set the client rect"""
        if self.client_rc != rcClient:
            self.client_rc = wx.Rect(*rcClient)
            self.PrepareDrawRect()
            self.LayoutControl()

    def SetMinSize(self, size, silent=False):
        """set the min size"""
        if self.min_size != size:
            self.min_size = wx.Size(*size)
            if not silent:
                self.SendPropEvent(wxEVT_PROP_RESIZE)

    def GetClientRect(self):
        """return the client rect"""
        return wx.Rect(*self.client_rc)

    def GetSize(self):
        """return the current size"""
        return self.client_rc.GetSize()

    def GetMinSize(self):
        """return the min size"""
        if self.window:
            size = self.window.GetSize()
            sz = self.min_size
            size.y = max(sz.y, size.y+2)
            return size
        return wx.Size(*self.min_size)

    def SetValue(self, value, silent=False):
        """set the value"""
        if self.value != str(value):
            self.DestroyControl()
            self.value = str(value)
            self.UpdateDescription()
            if not silent and self.GetVisible():
                self.SendPropEvent(wxEVT_PROP_REFRESH)
            return True
        return False

    def SetValueTip(self, tip):
        """set the value tip"""
        self.value_tip = tip

    def SetIndent(self, indent, silent=False):
        """set the indent to a positive integer"""
        if indent < 0:
            indent = 0
        if indent == self.indent:
            return
        self.indent = indent
        if not silent:
            self.SendPropEvent(wxEVT_PROP_INDENT)

    def SetExpand(self, expand, silent=False):
        """expand/collapse the children"""
        if not self.HasChildren():
            return
        if expand == self.expanded:
            return
        self.expanded = expand
        if silent:
            return
        if self.expanded:
            evt = wxEVT_PROP_EXPANDED
        else:
            evt = wxEVT_PROP_COLLAPSED
        if not silent:
            self.SendPropEvent(evt)

    def SetHasChildren(self, haschildren, silent=False):
        """Indicate that the property has children"""
        if haschildren == self.has_children:
            return
        self.has_children = haschildren
        if silent:
            return
        if self.expanded:
            evt = wxEVT_PROP_EXPANDED
        else:
            evt = wxEVT_PROP_COLLAPSED
        self.SendPropEvent(evt)

    def SetActivated(self, activated):
        """activate the property"""
        if activated == self.activated:
            return
        self.activated = activated
        if not activated:
            # destroy the control if the property is inactivated
            self.OnTextEnter()
        else:
            self.SendPropEvent(wxEVT_PROP_SELECTED)

    def SetReadOnly(self, readonly, silent=False):
        """set the property to readonly"""
        if readonly != self.GetReadOnly():
            self.readonly = readonly
            if not silent and self.GetVisible():
                self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetChecked(self, check, silent=False):
        """check/uncheck the radio button"""
        if check != self.IsChecked():
            self.checked = check
            if not self.SendPropEvent(wxEVT_PROP_CLICK_CHECK):
                self.checked = not check
            if not silent and self.GetVisible():
                self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetGripperColor(self, clr=None):
        self.gripper_clr = clr

    def SetTextColor(self, clr=None, clr_sel=None, clr_disabled=None,
                     silent=False):
        """
        set the text colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.text_clr = clr
        if not self.text_clr:
            self.text_clr = wx.BLACK.GetAsString(wx.C2S_HTML_SYNTAX)
        self.text_clr_sel = clr_sel
        if not self.text_clr_sel:
            self.text_clr_sel = wx.WHITE.GetAsString(wx.C2S_HTML_SYNTAX)
        self.text_clr_disabled = clr_disabled
        if not self.text_clr_disabled:
            self.text_clr_disabled = wx.LIGHT_GREY.GetAsString(wx.C2S_HTML_SYNTAX)
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def SetBgColor(self, clr=None, clr_sel=None, clr_disabled=None, silent=False):
        """
        set the background colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        GetColour = wx.SystemSettings.GetColour
        self.bg_clr = clr
        if not self.bg_clr:
            self.bg_clr = GetColour(wx.SYS_COLOUR_WINDOW).GetAsString(wx.C2S_HTML_SYNTAX)
        self.bg_clr_sel = clr_sel
        if not self.bg_clr_sel:
            self.bg_clr_sel = GetColour(wx.SYS_COLOUR_MENUHILIGHT).GetAsString(wx.C2S_HTML_SYNTAX)
        self.bg_clr_disabled = clr_disabled
        if not self.bg_clr_disabled:
            self.bg_clr_disabled = GetColour(wx.SYS_COLOUR_3DFACE).GetAsString(wx.C2S_HTML_SYNTAX)
        if not silent and self.GetVisible():
            self.SendPropEvent(wxEVT_PROP_REFRESH)

    def GetShowLabelTips(self):
        """return whether label tooltip is allowed"""
        return self.show_label_tips

    def GetShowValueTips(self):
        """return whether value tooltip is allowed"""
        return self.show_value_tips

class PropertyEvent(wx.PyCommandEvent):
    def __init__(self, commandType, id=0):
        wx.PyCommandEvent.__init__(self, commandType, id)
        self.prop = None
        self.veto = False

    def GetProperty(self):
        """return the attached Property"""
        return self.prop

    def SetProperty(self, prop):
        """attach the Property instance"""
        if isinstance(prop, Property):
            self.prop = prop

    def Veto(self, veto=True):
        """refuse the event"""
        self.veto = veto

    def GetVeto(self):
        """return whether the event is refused"""
        return self.veto
