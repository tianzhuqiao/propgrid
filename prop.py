import sys
import traceback
import copy
import six
import wx
import wx.adv
from .validators import *
from .formatters import *
from .enumtype import EnumType

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


class Property(object):
    controls = EnumType('default', 'none', 'editbox', 'choice', 'file',
                        'folder', 'slider', 'spin', 'checkbox', 'radiobox',
                        'color', 'date', 'time', 'font')

    def __init__(self, grid, name, label, value):
        self.grid = grid
        self.name = name
        self.label = label
        self.label_tip = ''
        self.value = value
        self.value_tip = ''
        # indicate if data is garbage
        self.value_valid = True
        # -1 to use the default one defined in parent's art provider
        self.title_width = -1
        self.indent = 0
        self.activated = False
        self.enable = True
        self.font_label = None
        self.font_value = None
        self.has_children = False
        self.expanded = True
        self.visible = True
        self.readonly = False
        self.ctrl_type = self.controls.default
        self.window = None
        self.parent = -1
        self.SetTextColor(silent=True)
        self.SetBgColor(silent=True)
        self.min_size = wx.Size(200, 25)
        self.rect = wx.Rect(0, 0, 0, 0)
        # non-overlapping regions
        self.regions = {
            'value': wx.Rect(),
            'label': wx.Rect(),
            'splitter': wx.Rect(),
            'expander': wx.Rect()
        }
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
        p.activated = self.activated
        p.enable = self.enable
        if p.font_label:
            self.font_label = wx.Font(p.font_label)
        if p.font_value:
            self.font_value = wx.Font(p.font_value)
        p.has_children = self.has_children
        p.expanded = self.expanded
        p.visible = self.visible
        p.readonly = self.readonly
        p.ctrl_type = self.ctrl_type
        p.parent = self.parent
        p.SetTextColor(self.text_clr, self.text_clr_sel,
                       self.text_clr_disabled, True)
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
        style: default | none | editbox | choice | file | folder | slider |
               spin | checkbox | radiobox | color | date | time
        """
        self.UpdatePropValue()
        self.DestroyControl()
        if style not in self.controls:
            print('Unsupported control style!')
            return False
        self.ctrl_type = self.controls[style]
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

    def SetLabelFont(self, font, silent=False):
        """set label font"""
        self.font_label = font
        if not silent:
            self.Refresh()

    def GetLabelFont(self):
        """get label font"""
        return self.font_label

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

    def SetValue(self, value, silent=False):
        """set the value"""
        if self.IsReadonly():
            return False
        if self.value != value:
            self.DestroyControl()
            fmt = self.formatter
            try:
                if fmt and not fmt.validate(fmt.format(value)):
                    return False
            except:
                traceback.print_exc(file=sys.stdout)
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
        try:
            if self.formatter and self.GetValueValid():
                # ignore format if data is not valid yet
                return self.formatter.format(self.value)
        except:
            traceback.print_exc(file=sys.stdout)

        return str(self.value)

    def SetValueValid(self, valid):
        self.value_valid = valid

    def GetValueValid(self):
        return self.value_valid

    def SetValueTip(self, tip):
        """set the value tip"""
        self.value_tip = tip

    def GetValueTip(self):
        """get the valuetip"""
        if self.value_tip:
            return self.value_tip
        return self.GetValueAsString()

    def SetValueFont(self, font, silent=False):
        """set value font"""
        self.font_value = font
        if not silent:
            self.Refresh()

    def GetValueFont(self):
        """get value font"""
        return self.font_value

    def SetFormatter(self, formatter):
        if not formatter or not hasattr(formatter, 'validate') or\
           not hasattr(formatter, 'format') or not hasattr(formatter, 'coerce'):
            formatter = None
        self.formatter = formatter

    def GetFormatter(self):
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

    def SetTextColor(self,
                     clr=None,
                     clr_sel=None,
                     clr_disabled=None,
                     silent=False):
        """
        set the text colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.text_clr = clr
        self.text_clr_sel = clr_sel
        self.text_clr_disabled = clr_disabled

        if not silent:
            self.Refresh()

    def GetTextColor(self):
        """get the text colors"""
        return (self.text_clr, self.text_clr_sel, self.text_clr_disabled)

    def SetBgColor(self,
                   clr=None,
                   clr_sel=None,
                   clr_disabled=None,
                   silent=False):
        """
        set the background colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.bg_clr = clr
        self.bg_clr_sel = clr_sel
        self.bg_clr_disabled = clr_disabled

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

    def SetRect(self, rc):
        """set the prop rect"""
        if self.rect != rc:
            self.rect = wx.Rect(*rc)
            # redraw the item
            self.Refresh()
            wx.CallAfter(self.LayoutControl)

    def GetRect(self):
        """return the prop rect"""
        return wx.Rect(*self.rect)

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
            size.y = max(sz.y, size.y)
            return size
        return wx.Size(*self.min_size)

    def GetSize(self):
        """return the current size"""
        return self.rect.GetSize()

    def GetShowLabelTips(self):
        """return whether label tooltip is allowed"""
        return self.show_label_tips

    def GetShowValueTips(self):
        """return whether value tooltip is allowed"""
        return self.show_value_tips

    def HitTest(self, pt):
        """find the mouse position relative to the property"""
        # bottom edge
        rc = wx.Rect(*self.rect)
        rc.SetTop(rc.bottom - 2)
        if rc.Contains(pt):
            return 'bottom_edge'
        # top edge
        rc = wx.Rect(*self.rect)
        rc.SetBottom(rc.top + 2)
        if rc.Contains(pt):
            return 'top_edge'

        for k, v in six.iteritems(self.regions):
            if v.Contains(pt):
                return k

        return None

    def OnMouseDown(self, pt):
        ht = self.HitTest(pt)
        # click on the expand buttons? expand it?
        if self.HasChildren() and ht == 'expander':
            self.SetExpand(not self.expanded)

        if ht == 'value':
            if not self.IsReadonly() and self.IsActivated():
                self.CreateControl()
        else:
            self.UpdatePropValue()
            self.DestroyControl()

        return ht

    def OnMouseUp(self, pt):
        ht = self.HitTest(pt)
        return ht

    def OnMouseDoubleClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            if ht == 'value':
                if not self.IsReadonly():
                    self.CreateControl()
            else:
                self.UpdatePropValue()
                self.DestroyControl()

            if ht == 'expander':
                self.SetExpand(not self.expanded)

            self.SendPropEvent(wxEVT_PROP_DOUBLE_CLICK)

        return ht

    def OnMouseRightClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            # destroy the control when the mouse moves out
            if ht is None:
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
        if style == self.controls.default:
            style = self.controls.editbox
            if isinstance(self.formatter, EnumFormatter) or \
               isinstance(self.formatter, ChoiceFormatter):
                style = self.controls.choice
            elif isinstance(self.formatter, BoolFormatter):
                style = self.controls.checkbox
            elif isinstance(self.formatter, PathFormatter):
                if self.formatter.types == 'file':
                    style = self.controls.file
                elif self.formatter.types == 'folder':
                    style = self.controls.folder
            elif isinstance(self.formatter, ColorFormatter):
                style = self.controls.color
            elif isinstance(self.formatter, FontFormatter):
                style = self.controls.font
            elif isinstance(self.formatter, DateFormatter):
                style = self.controls.date
                if isinstance(self.formatter, TimeFormatter):
                    style = self.controls.time
        win = None
        if style == self.controls.editbox:
            style = wx.TE_PROCESS_ENTER
            sz = self.GetMinSize()
            if sz.y > 50:
                style = wx.TE_MULTILINE
            win = wx.TextCtrl(self.grid,
                              wx.ID_ANY,
                              self.GetValueAsString(),
                              style=style)
            if self.formatter:
                validator = TextValidator(self, 'value', self.formatter, False,
                                          None)
                win.SetValidator(validator)

            if style & wx.TE_PROCESS_ENTER:
                win.Bind(wx.EVT_TEXT_ENTER, self.OnPropTextEnter)

        elif style == self.controls.choice:
            win = wx.Choice(self.grid, wx.ID_ANY)
            if self.formatter:
                validator = SelectorValidator(self, 'value', self.formatter,
                                              True)
                win.SetValidator(validator)

        elif style == self.controls.file:
            win = wx.Button(self.grid, wx.ID_ANY, self.GetValueAsString())
            win.Bind(wx.EVT_BUTTON, self.OnSelectFile)

        elif style == self.controls.folder:
            win = wx.Button(self.grid, wx.ID_ANY, self.GetValueAsString())
            win.Bind(wx.EVT_BUTTON, self.OnSelectFolder)

        elif style == self.controls.slider:
            win = wx.Slider(self.grid,
                            wx.ID_ANY,
                            value=int(self.value),
                            style=wx.SL_LABELS | wx.SL_HORIZONTAL | wx.SL_TOP)
            if self.formatter:
                validator = SpinSliderValidator(self, 'value', self.formatter,
                                                True)
                win.SetValidator(validator)

        elif style == self.controls.spin:
            win = wx.SpinCtrl(self.grid,
                              wx.ID_ANY,
                              value=str(self.value),
                              style=wx.SP_ARROW_KEYS)
            if self.formatter:
                validator = SpinSliderValidator(self, 'value', self.formatter,
                                                True)
                win.SetValidator(validator)

        elif style == self.controls.checkbox:
            win = wx.CheckBox(self.grid, wx.ID_ANY)
            win.SetValue(int(self.value) != 0)

        elif style == self.controls.radiobox:
            choices = []
            if self.formatter and hasattr(self.formatter, 'validValues'):
                choices = [x[1] for x in self.formatter.validValues()]

            win = wx.RadioBox(self.grid, wx.ID_ANY, "", wx.DefaultPosition,
                              wx.DefaultSize, choices, 5, wx.RA_SPECIFY_COLS)

            if self.formatter:
                validator = RadioBoxValidator(self, 'value', self.formatter,
                                              True)
                win.SetValidator(validator)

        elif style == self.controls.color:
            win = wx.ColourPickerCtrl(self.grid,
                                      wx.ID_ANY,
                                      wx.BLACK,
                                      style=wx.CLRP_DEFAULT_STYLE
                                      | wx.CLRP_SHOW_LABEL)
            try:
                win.SetColour(self.value)
            except ValueError:
                pass
        elif style == self.controls.font:
            win = wx.FontPickerCtrl(self.grid, wx.ID_ANY)
            try:
                if self.value:
                    win.SetSelectedFont(self.value)
            except ValueError:
                pass

        elif style == self.controls.date:
            win = wx.adv.DatePickerCtrl(self.grid, wx.ID_ANY)
            try:
                win.SetValue(self.value)
            except ValueError:
                pass

        elif style == self.controls.time:
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
        dlg = wx.FileDialog(self.grid, "Choose a file",
                            self.GetValueAsString(), "", "*.*", style)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnSelectFolder(self, evt):
        dlg = wx.DirDialog(self.grid, "Choose input directory",
                           self.GetValueAsString(),
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()

    def LayoutControl(self):
        """re-positioning the control"""
        if self.window is None:
            return
        rc = self.grid.GetScrolledRect(wx.Rect(*self.regions['value']))
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
        value = None
        if isinstance(self.window, wx.TextCtrl):
            value = self.window.GetValue()

        elif isinstance(self.window, wx.Button):
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

        elif isinstance(self.window, wx.FontPickerCtrl):
            font = self.window.GetSelectedFont()
            value = font.GetNativeFontInfoDesc()

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
            elif self.value is not None:
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
