import sys
import traceback
import copy
import six
import wx
import wx.adv
from .validators import *
from .formatters import *

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
EVT_PROP_DROP = wx.PyEventBinder(wxEVT_PROP_DROP, 1)
EVT_PROP_BEGIN_DRAG = wx.PyEventBinder(wxEVT_PROP_BEGIN_DRAG, 1)
EVT_PROP_CLICK_CHECK = wx.PyEventBinder(wxEVT_PROP_CLICK_CHECK, 1)

PROP_CTRL_DEFAULT = 0
PROP_CTRL_NONE = 1
PROP_CTRL_EDIT = 2
PROP_CTRL_CHOICE = 3
PROP_CTRL_FILE_SEL = 4
PROP_CTRL_FOLDER_SEL = 5
PROP_CTRL_SLIDER = 6
PROP_CTRL_SPIN = 7
PROP_CTRL_CHECK = 8
PROP_CTRL_RADIO = 9
PROP_CTRL_COLOR = 10
PROP_CTRL_DATE = 11
PROP_CTRL_TIME = 12
PROP_CTRL_NUM = 13

PROP_HIT_NONE = 0
PROP_HIT_EXPAND = 1
PROP_HIT_CHECK = 2
PROP_HIT_TITLE = 3
PROP_HIT_SPLITTER = 4
PROP_HIT_VALUE = 5
PROP_HIT_EDGE_BOTTOM = 6
PROP_HIT_EDGE_TOP = 7

class Property(object):

    def __init__(self, grid, name, label, value):
        self.grid = grid
        self.name = name
        self.label = label
        self.label_tip = ''
        self.value = value
        self.value_tip = ''
        self.title_width = 80
        self.indent = 0
        self.show_check = False
        self.checked = False
        self.activated = False
        self.enable = True
        self.italic = False
        self.has_children = False
        self.expanded = True
        self.visible = True
        self.readonly = False
        self.ctrl_type = PROP_CTRL_DEFAULT
        self.window = None
        self.parent = -1
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
        self.value_rc = wx.Rect(0, 0, 0, 0)
        self.show_label_tips = False
        self.show_value_tips = False
        self.separator = False
        self.data = None
        self.formatter = None

    def duplicate(self):
        """
        copy the object

        copy.deepcopy does not work since the object contains pointer to wx
        objects
        """
        p = Property(self.grid, self.name, self.label, self.value)
        p.label_tip = self.label_tip
        p.value_tip = self.value_tip
        p.title_width = self.title_width
        p.indent = self.indent
        p.show_check = self.show_check
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
        p.SetGripperColor(self.gripper_clr)
        p.SetTextColor(self.text_clr, self.text_clr_sel, self.text_clr_disabled, True)
        p.SetBgColor(self.bg_clr, self.bg_clr_sel, self.bg_clr_disabled, True)
        p.show_label_tips = self.show_label_tips
        p.show_value_tips = self.show_value_tips
        p.separator = self.separator
        p.data = self.data
        p.formatter = copy.copy(p.formatter)
        return p

    def SetGrid(self, grid):
        """set the grid window"""
        self.grid = grid

    def GetGrid(self):
        """return the grid window"""
        return self.grid

    def SetData(self, data):
        self.data = data

    def GetData(self):
        return self.data

    def SetSeparator(self, sep=True, silent=False):
        """set the property to be a separator"""
        if self.separator == sep:
            return
        self.separator = sep
        if not silent:
            self.Refresh()

    def IsSeparator(self):
        """return true if the property is a separator"""
        return self.separator

    def SetControlStyle(self, style):
        """set the control type
        style: none | editbox | combobox | file_sel_button |
               folder_sel_button | slider | spin | checkbox | radiobox |
               color
        """
        self.UpdatePropValue()
        self.DestroyControl()
        str_style = {'default': PROP_CTRL_DEFAULT, 'none': PROP_CTRL_NONE,
                     'editbox': PROP_CTRL_EDIT, 'choice':PROP_CTRL_CHOICE,
                     'file_dialog':PROP_CTRL_FILE_SEL,
                     'dir_dialog': PROP_CTRL_FOLDER_SEL,
                     'slider': PROP_CTRL_SLIDER, 'spin': PROP_CTRL_SPIN,
                     'checkbox': PROP_CTRL_CHECK, 'radiobox': PROP_CTRL_RADIO,
                     'color': PROP_CTRL_COLOR, 'date': PROP_CTRL_DATE,
                     'time': PROP_CTRL_TIME}
        if isinstance(style, six.string_types):
            style = str_style.get(style, None)
        if style < PROP_CTRL_NONE or style >= PROP_CTRL_NUM:
            return False
        self.ctrl_type = style
        return True

    def GetControlStyle(self):
        """return the control type"""
        return self.ctrl_type

    def Enable(self, enable=True, silent=False):
        """enable/disable the property"""
        if self.enable == enable:
            return
        self.enable = enable
        if not silent:
            self.Refresh()

    def IsEnabled(self):
        """return true if the property is enabled"""
        return self.enable

    def SetName(self, name, silent=False):
        """set the name"""
        if self.name == name:
            return
        self.name = name
        if not silent:
            self.Refresh()

    def GetName(self):
        """get the name"""
        return self.name

    def SetLabel(self, label, silent=False):
        """set the label"""
        if self.label == label:
            return
        self.label = label
        if not silent:
            self.Refresh()

    def GetLabel(self):
        """get the label"""
        return self.label

    def SetLabelTip(self, tip):
        """set the label tip"""
        self.label_tip = tip

    def GetLabelTip(self):
        """get the label tip"""
        if self.label_tip:
            return self.label_tip
        return self.GetName()

    def Italic(self, italic=True, silent=False):
        """turn on/of the italic text"""
        if self.italic == italic:
            return
        self.italic = italic
        if not silent:
            self.Refresh()

    def IsItalic(self):
        "return true if the italic is used for drawing"
        return self.italic

    def SetVisible(self, visible=True, silent=False):
        """
        show/hide the property

        The property may be hidden if its parent is in collapsed mode.
        """
        if self.visible == visible:
            return
        self.visible = visible
        if not silent:
            self.Refresh(True)

    def IsVisible(self):
        """return true if the property is visible"""
        return self.visible

    def SetParent(self, prop):
        """set the parent property"""
        if prop and prop.GetIndent() >= self.GetIndent():
            return
        self.parent = prop

    def GetParent(self):
        """return the parent property"""
        return self.parent

    def SetShowCheck(self, show=True, silent=True):
        """show/hide radio button"""
        if self.show_check == show:
            return
        self.show_check = show
        if not silent:
            self.Refresh()

    def IsShowCheck(self):
        """return whether the icon is shown"""
        return self.show_check

    def SetChecked(self, check=True, silent=False):
        """check/uncheck the radio button"""
        if check != self.IsChecked():
            self.checked = check
            if not self.SendPropEvent(wxEVT_PROP_CLICK_CHECK):
                self.checked = not check
            if not silent:
                self.Refresh()

    def IsChecked(self):
        """return true if the radio button is checked"""
        return self.checked

    def SetValue(self, value, silent=False):
        """set the value"""
        if self.IsReadonly():
            return False
        if self.value != value:
            self.DestroyControl()
            fmt = self.formatter
            if fmt and not fmt.validate(fmt.format(value)):
                return False
            self.value = value
            if not silent:
                self.Refresh()
            return True
        return False

    def GetValue(self):
        """get the value"""
        return self.value

    def GetValueAsString(self):
        """get the value as string"""
        if self.formatter:
            return self.formatter.format(self.value)
        return str(self.value)

    def SetValueTip(self, tip):
        """set the value tip"""
        self.value_tip = tip

    def GetValueTip(self):
        """get the valuetip"""
        if self.value_tip:
            return self.value_tip
        return self.value

    def SetFormatter(self, formatter):
        if not formatter or not hasattr(formatter, 'validate') or\
           not hasattr(formatter, 'format') or not hasattr(formatter, 'coerce'):
            formatter = None
        self.formatter = formatter

    def GetFormatter(self, formatter):
        return self.formatter

    def SetIndent(self, indent, silent=False):
        """set the indent to a positive integer"""
        if indent < 0:
            indent = 0
        if indent == self.indent:
            return
        self.indent = indent
        if not silent:
            self.SendPropEvent(wxEVT_PROP_INDENT)

    def GetIndent(self):
        """get the indent"""
        return self.indent

    def SetExpand(self, expand=True, silent=False):
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

    def IsExpanded(self):
        """return true if the expand/collapse button is expanded"""
        return self.expanded

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

    def HasChildren(self):
        """return true if the property has children"""
        return self.has_children

    def SetActivated(self, activated=True):
        """activate the property"""
        if activated == self.activated:
            return
        self.activated = activated
        if not activated:
            # destroy the control if the property is inactivated
            self.OnTextEnter()
        else:
            self.SendPropEvent(wxEVT_PROP_SELECTED)

    def IsActivated(self):
        """return true if the property is activated"""
        return self.activated

    def SetReadonly(self, readonly=True, silent=False):
        """set the property to readonly"""
        if readonly != self.IsReadonly():
            self.readonly = readonly
            if not silent:
                self.Refresh()

    def IsReadonly(self):
        """return true if the property is readonly"""
        return self.readonly

    def SetGripperColor(self, clr=None):
        self.gripper_clr = clr

    def GetGripperColor(self):
        return self.gripper_clr

    def SetTextColor(self, clr=None, clr_sel=None, clr_disabled=None,
                     silent=False):
        """
        set the text colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.text_clr = clr
        if not self.text_clr:
            self.text_clr = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT).\
                             GetAsString(wx.C2S_HTML_SYNTAX)
        self.text_clr_sel = clr_sel
        if not self.text_clr_sel:
            self.text_clr_sel = wx.WHITE.GetAsString(wx.C2S_HTML_SYNTAX)
        self.text_clr_disabled = clr_disabled
        if not self.text_clr_disabled:
            self.text_clr_disabled = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)\
                                    .GetAsString(wx.C2S_HTML_SYNTAX)
        if not silent:
            self.Refresh()

    def GetTextColor(self):
        """get the text colors"""
        return (self.text_clr, self.text_clr_sel, self.text_clr_disabled)

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
            self.bg_clr_sel = GetColour(wx.SYS_COLOUR_HIGHLIGHT).GetAsString(wx.C2S_HTML_SYNTAX)
        self.bg_clr_disabled = clr_disabled
        if not self.bg_clr_disabled:
            self.bg_clr_disabled = GetColour(wx.SYS_COLOUR_3DFACE).GetAsString(wx.C2S_HTML_SYNTAX)
        if not silent:
            self.Refresh()

    def GetBgColor(self):
        """get the background colors"""
        return (self.bg_clr, self.bg_clr_sel, self.bg_clr_disabled)

    def SetTitleWidth(self, width):
        """set the title width"""
        self.title_width = width

    def GetTitleWidth(self):
        """return the width"""
        return self.title_width

    def SetClientRect(self, rc):
        """set the client rect"""
        if self.client_rc != rc:
            self.client_rc = wx.Rect(*rc)
            # redraw the item
            self.Refresh()
            wx.CallAfter(self.LayoutControl)

    def GetClientRect(self):
        """return the client rect"""
        return wx.Rect(*self.client_rc)

    def SetMinSize(self, size, silent=False):
        """set the min size"""
        if self.min_size != size:
            self.min_size = wx.Size(*size)
            if not silent:
                self.Resize()

    def GetMinSize(self):
        """return the min size"""
        if self.window:
            size = self.window.GetSize()
            sz = self.min_size
            size.y = max(sz.y, size.y+2)
            return size
        return wx.Size(*self.min_size)

    def GetSize(self):
        """return the current size"""
        return self.client_rc.GetSize()

    def GetShowLabelTips(self):
        """return whether label tooltip is allowed"""
        return self.show_label_tips

    def GetShowValueTips(self):
        """return whether value tooltip is allowed"""
        return self.show_value_tips

    def HitTest(self, pt):
        """find the mouse position relative to the property"""
        # bottom edge
        rc = wx.Rect(*self.client_rc)
        rc.SetTop(rc.bottom-2)
        if rc.Contains(pt):
            return PROP_HIT_EDGE_BOTTOM
        # top edge
        rc = wx.Rect(*self.client_rc)
        rc.SetBottom(rc.top+2)
        if rc.Contains(pt):
            return PROP_HIT_EDGE_TOP

        if self.expander_rc.Contains(pt):
            return PROP_HIT_EXPAND
        elif self.radio_rc.Contains(pt):
            return PROP_HIT_CHECK
        elif self.label_rc.Contains(pt):
            return PROP_HIT_TITLE
        elif self.splitter_rc.Contains(pt):
            return PROP_HIT_SPLITTER
        elif self.value_rc.Contains(pt):
            return PROP_HIT_VALUE

        return PROP_HIT_NONE

    def OnMouseDown(self, pt):
        ht = self.HitTest(pt)
        # click on the expand buttons? expand it?
        if self.HasChildren() and ht == PROP_HIT_EXPAND:
            self.SetExpand(not self.expanded)

        if ht == PROP_HIT_VALUE:
            if not self.IsReadonly() and self.IsActivated():
                self.CreateControl()
        else:
            self.UpdatePropValue()
            self.DestroyControl()

        return ht

    def OnMouseUp(self, pt):
        ht = self.HitTest(pt)
        if self.IsEnabled():
            # click on the check icon? change the state
            if self.IsShowCheck() and ht == PROP_HIT_CHECK:
                checked = self.IsChecked()
                self.SetChecked(not checked)
        return ht

    def OnMouseDoubleClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            if ht == PROP_HIT_VALUE:
                if not self.IsReadonly():
                    self.CreateControl()
            else:
                self.UpdatePropValue()
                self.DestroyControl()

            if ht == PROP_HIT_EXPAND:
                self.SetExpand(not self.expanded)

            self.SendPropEvent(wxEVT_PROP_DOUBLE_CLICK)

        return ht

    def OnMouseRightClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            # destroy the control when the mouse moves out
            if ht == PROP_HIT_NONE:
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
        self.Refresh()

    def CreateControl(self):
        """create the control"""
        if self.window != None or self.IsSeparator():
            return
        style = self.ctrl_type
        if style == PROP_CTRL_DEFAULT:
            style = PROP_CTRL_EDIT
            if isinstance(self.formatter, EnumFormatter):
                style = PROP_CTRL_CHOICE
            elif isinstance(self.formatter, BoolFormatter):
                style = PROP_CTRL_CHECK
            elif isinstance(self.formatter, PathFormatter):
                if self.formatter.types == 'file':
                    style = PROP_CTRL_FILE_SEL
                elif self.formatter.types == 'folder':
                    style = PROP_CTRL_FOLDER_SEL
            elif isinstance(self.formatter, ColorFormatter):
                style = PROP_CTRL_COLOR
            elif isinstance(self.formatter, DateFormatter):
                style = PROP_CTRL_DATE
                if isinstance(self.formatter, TimeFormatter):
                    style = PROP_CTRL_TIME
        win = None
        if style == PROP_CTRL_EDIT:
            win = wx.TextCtrl(self.grid, wx.ID_ANY, self.GetValueAsString(),
                              style=wx.TE_PROCESS_ENTER)
            if self.formatter:
                validator = TextValidator(self, 'value', self.formatter,
                                          False, None)
                win.SetValidator(validator)
            win.Bind(wx.EVT_TEXT_ENTER, self.OnPropTextEnter)

        elif style == PROP_CTRL_CHOICE:
            win = wx.Choice(self.grid, wx.ID_ANY)
            if self.formatter:
                validator = SelectorValidator(self, 'value', self.formatter,
                                              True)
                win.SetValidator(validator)

        elif style == PROP_CTRL_FILE_SEL:
            win = wx.Button(self.grid, wx.ID_ANY, self.GetValueAsString())
            win.Bind(wx.EVT_BUTTON, self.OnSelectFile)

        elif style == PROP_CTRL_FOLDER_SEL:
            win = wx.Button(self.grid, wx.ID_ANY, self.GetValueAsString())
            win.Bind(wx.EVT_BUTTON, self.OnSelectFolder)

        elif style == PROP_CTRL_SLIDER:
            win = wx.Slider(self.grid, wx.ID_ANY, value=int(self.value),
                            style=wx.SL_LABELS | wx.SL_HORIZONTAL | wx.SL_TOP)
            if self.formatter:
                validator = SpinSliderValidator(self, 'value', self.formatter,
                                                True)
                win.SetValidator(validator)

        elif style == PROP_CTRL_SPIN:
            win = wx.SpinCtrl(self.grid, wx.ID_ANY, str(self.value),
                              style=wx.SP_ARROW_KEYS)
            if self.formatter:
                validator = SpinSliderValidator(self, 'value', self.formatter,
                                                True)
                win.SetValidator(validator)

        elif style == PROP_CTRL_CHECK:
            win = wx.CheckBox(self.grid, wx.ID_ANY)
            win.SetValue(int(self.value) != 0)

        elif style == PROP_CTRL_RADIO:
            choices = []
            if self.formatter and hasattr(self.formatter, 'validValues'):
                choices = [x[1] for x in self.formatter.validValues()]

            win = wx.RadioBox(self.grid, wx.ID_ANY, "",
                              self.value_rc.GetTopLeft(), wx.DefaultSize,
                              sorted(choices), 5, wx.RA_SPECIFY_COLS)

            if self.formatter:
                validator = RadioBoxValidator(self, 'value', self.formatter,
                                              True)
                win.SetValidator(validator)

        elif style == PROP_CTRL_COLOR:
            win = wx.ColourPickerCtrl(self.grid, wx.ID_ANY, wx.BLACK,
                                      style=wx.CLRP_DEFAULT_STYLE |
                                      wx.CLRP_SHOW_LABEL)
            try:
                win.SetColour(self.value)
            except ValueError:
                pass

        elif style == PROP_CTRL_DATE:
            win = wx.adv.DatePickerCtrl(self.grid, wx.ID_ANY)
            try:
                win.SetValue(self.value)
            except ValueError:
                pass

        elif style == PROP_CTRL_TIME:
            win = wx.adv.TimePickerCtrl(self.grid, wx.ID_ANY)
            try:
                win.SetValue(self.value)
            except ValueError:
                pass
        if win:
            if win.GetValidator():
                win.GetValidator().TransferToWindow()
            self.window = win
            # the window size may be larger than the value rect, notify parent
            # grid to update it
            self.Resize()
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
        evt.Skip()
        wnd = evt.GetWindow()
        while wnd:
            if wnd.GetParent() == self.window:
                return
            wnd = wnd.GetParent()
        # color window does not work on Mac
        #wx.CallAfter(self.OnTextEnter)

    def OnSelectFile(self, evt):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dlg = wx.FileDialog(self.grid, "Choose a file", self.GetValueAsString(),
                            "", "*.*", style)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnSelectFolder(self, evt):
        dlg = wx.DirDialog(self.grid, "Choose input directory", self.GetValueAsString(),
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()

    def LayoutControl(self):
        """re-positioning the control"""
        if self.window is None:
            return
        (x, y) = self.grid.GetViewStart()
        rc = wx.Rect(*self.value_rc)
        rc.Offset(wx.Point(-x*5, -y*5))
        self.window.SetSize(rc.GetSize())
        self.window.Move(rc.GetTopLeft())

    def DestroyControl(self):
        """destroy the value setting control"""
        if self.window:
            self.window.Show(False)
            self.window.Destroy()
            self.window = None
            self.Resize()
            return True
        return False

    def UpdatePropValue(self):
        """update the value"""
        if self.window is None:
            return False
        validator = self.window.GetValidator()
        if validator:
            validator.TransferFromWindow()
            return

        value_old = self.value
        style = self.ctrl_type
        value = None
        if isinstance(self.window, wx.TextCtrl):
            value = self.window.GetValue()

        elif isinstance(self.window, wx.Button):
            # [PROP_CTRL_FILE_SEL, PROP_CTRL_FOLDER_SEL]
            value = self.window.GetLabel()

        elif isinstance(self.window, wx.RadioBox) or\
             isinstance(self.window, wx.Choice):
            sel = self.window.GetSelection()
            if sel >= 0 and sel < self.window.GetCount():
                value = self.window.GetString(sel)

        elif isinstance(self.window, wx.Slider):
            value = self.window.GetValue()

        elif isinstance(self.window, wx.SpinCtrl):
            value = self.window.GetValue()

        elif isinstance(self.window, wx.CheckBox):
            value = self.window.GetValue()

        elif isinstance(self.window, wx.ColourPickerCtrl):
            clr = self.window.GetColour()
            value = clr.GetAsString(wx.C2S_HTML_SYNTAX)

        elif isinstance(self.window, wx.adv.DatePickerCtrl) or\
             isinstance(self.window, wx.adv.TimePickerCtrl):
            value = self.window.GetValue()
            if self.formatter:
                value = self.formatter.format(value)
        try:
            if self.formatter:
                if self.formatter.validate(str(value)):
                    value = self.formatter.coerce(str(value))
                else:
                    return False
            else:
                value = type(self.value)(value)
            self.SetValue(value, silent=True)
        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return False

        if self.SendPropEvent(wxEVT_PROP_CHANGING):
            self.SendPropEvent(wxEVT_PROP_CHANGED)
            self.Refresh()
            return True
        else:
            #the parent rejects the operation, restore the original value
            self.SetValue(value_old)
            return False

    def SendPropEvent(self, event):
        """ send property grid event to parent"""
        win = self.GetGrid()
        evt = PropertyEvent(event)
        evt.SetProperty(self)
        evt.SetEventObject(win)
        evt_handler = win.GetEventHandler()

        if evt_handler.ProcessEvent(evt):
            return not evt.GetVeto()
        return False

    def Resize(self):
        """notify parent grid the size needs to be updated"""
        self.SendPropEvent(wxEVT_PROP_RESIZE)

    def Refresh(self, force=False):
        """notify the parent to redraw the property"""
        if self.IsVisible() or force:
            self.SendPropEvent(wxEVT_PROP_REFRESH)


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
