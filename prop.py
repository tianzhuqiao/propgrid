import sys
import traceback
import copy
import six
import wx
import wx.adv
from .validators import *
from .formatters import *
from . import formatters as fmt
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


class PropBase():
    pass

class PropGeneric(PropBase):
    def __init__(self, label=''):
        self.grid = None
        self.name = ''
        self.label = label
        self.label_tip = ''
        self.value = ''
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
        #self.window = None
        self.parent = -1
        self.SetTextColor(silent=True)
        self.SetBgColor(silent=True)
        if wx.Platform == '__WXMSW__':
            self.min_size = wx.Size(200, 35)
        else:
            self.min_size = wx.Size(200, 25)
        self.rect = wx.Rect(0, 0, 0, 0)
        # non-overlapping regions
        self.regions = {
            'value': wx.Rect(),
            'label': wx.Rect(),
            'splitter': wx.Rect(),
            'expander': wx.Rect()
        }
        self.draws = {
            'value': True,
            'label': True,
            'splitter': True,
            'expander': True
            }
        self.show_label_tips = False
        self.show_value_tips = False
        self.separator = False
        self.data = None
        self.formatter = None

        self.draggable = True
        self.configurable = True
        self.top_value_border = False
        self.bottom_value_border = False

    def _prepare_copy(self):
        pass

    def copy(self, p):
        assert isinstance(p, PropGeneric)

        p._prepare_copy()
        self._prepare_copy()

        self.grid = p.grid
        if p.font_label:
            self.font_label = wx.Font(p.font_label)
        if p.font_value:
            self.font_value = wx.Font(p.font_value)
        self.SetTextColor(p.text_clr, p.text_clr_sel, p.text_clr_disabled, True)
        self.SetBgColor(p.bg_clr, p.bg_clr_sel, p.bg_clr_disabled, True)
        self.data = p.data
        if type(self) == type(p) and self.formatter is None and p.formatter:
            self.formatter = copy.copy(p.formatter)

        self.name = p.name
        self.label = p.label
        self.label_tip = p.label_tip
        self.value = p.value
        self.value_tip = p.value_tip
        # indicate if data is garbage
        self.value_valid = p.value_valid
        # -1 to use the default one defined in parent's art provider
        self.title_width = p.title_width
        self.indent = p.indent
        self.activated = p.activated
        self.enable = p.enable
        self.visible = p.visible
        self.readonly = p.readonly
        self.min_size = p.min_size
        self.draws = p.draws
        self.show_label_tips = p.show_label_tips
        self.show_value_tips = p.show_label_tips
        self.separator = p.separator
        self.data = copy.deepcopy(p.data)

        self.draggable = p.draggable
        self.configurable = p.configurable

    def duplicate(self):
        """
        copy the object

        copy.deepcopy does not work since the object contains pointer to wx
        objects
        """
        p = copy.copy(self)
        p.copy(self)
        return p

    def Grid(self, grid):
        self.SetGrid(grid)
        return self

    def SetGrid(self, grid):
        """set the grid window"""
        self.grid = grid

    def GetGrid(self):
        """return the grid window"""
        return self.grid

    def Data(self, data):
        self.SetData(data)
        return self

    def SetData(self, data):
        self.data = data

    def GetData(self):
        return self.data

    def Separator(self, sep=True, silent=True):
        self.SetSeparator(sep, silent)
        return self

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

    def Enable(self, enable=True, silent=True):
        """enable/disable the property"""
        self.SetEnable(enable, silent=silent)
        return self

    def SetEnable(self, enable=True, silent=False):
        """enable/disable the property"""
        if self.enable == enable:
            return
        self.enable = enable
        if not silent:
            self.Refresh()

    def IsEnabled(self):
        """return true if the property is enabled"""
        return self.enable

    def Name(self, name, silent=True):
        self.SetName(name, silent)
        return self

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

    def Label(self, label, silent=True):
        self.SetLabel(label, silent)
        return self

    def SetLabel(self, label, silent=False):
        """set the label"""
        if self.label == label:
            return
        self.label = label
        if not self.name:
            self.SetName(f'_prop_{label}', silent=True)
        if not silent:
            self.Refresh()

    def GetLabel(self):
        """get the label"""
        return self.label

    def LabelTip(self, tip):
        self.SetLabelTip(tip)
        return self

    def SetLabelTip(self, tip):
        """set the label tip"""
        self.label_tip = tip

    def GetLabelTip(self):
        """get the label tip"""
        if self.label_tip:
            return self.label_tip
        return self.GetName()

    def LabelFont(self, font, silent=False):
        self.SetLabelFont(font, silent)
        return self

    def SetLabelFont(self, font, silent=False):
        """set label font"""
        self.font_label = font
        if not silent:
            self.Refresh()

    def GetLabelFont(self):
        """get label font"""
        return self.font_label

    def Visible(self, visible, silent=True):
        """
        show/hide the property

        The property may be hidden if its parent is in collapsed mode.
        """
        self.SetVisible(visible, silent)
        return self

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

    def Parent(self, prop):
        """set the parent property"""
        self.SetParent(prop)
        return self

    def SetParent(self, prop):
        """set the parent property"""
        if prop and prop.GetIndent() >= self.GetIndent():
            return
        self.parent = prop

    def GetParent(self):
        """return the parent property"""
        return self.parent

    def Value(self, value, silent=True):
        """set the value"""
        self.SetValue(value, silent)
        return self

    def SetValue(self, value, silent=False):
        """set the value"""
        if self.IsReadonly():
            return False
        if self.value != value:
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

    def ValueValid(self, valid):
        """mark the value valid"""
        self.SetValueValid(valid)
        return self

    def SetValueValid(self, valid):
        """mark the value valid"""
        self.value_valid = valid

    def GetValueValid(self):
        """return if the value is valid"""
        return self.value_valid

    def ValueTip(self, tip):
        """set the value tip"""
        self.SetValueTip(tip)
        return self

    def SetValueTip(self, tip):
        """set the value tip"""
        self.value_tip = tip

    def GetValueTip(self):
        """get the valuetip"""
        if self.value_tip:
            return self.value_tip
        return self.GetValueAsString()

    def ValueFont(self, font, silent=True):
        """set value font"""
        self.SetValueFont(font, silent)
        return self

    def SetValueFont(self, font, silent=False):
        """set value font"""
        self.font_value = font
        if not silent:
            self.Refresh()

    def GetValueFont(self):
        """get value font"""
        return self.font_value

    def Formatter(self, formatter):
        """set value formatter"""
        self.SetFormatter(formatter)
        return self

    def SetFormatter(self, formatter):
        """set value formatter"""
        if not formatter or not hasattr(formatter, 'validate') or\
           not hasattr(formatter, 'format') or not hasattr(formatter, 'coerce'):
            formatter = None
        self.formatter = formatter

    def GetFormatter(self):
        """get value formatter"""
        return self.formatter

    def Indent(self, indent, silent=True):
        """set the indent to a positive integer"""
        self.SetIndent(indent, silent)
        return self

    def SetIndent(self, indent, silent=False):
        """set the indent to a positive integer"""
        indent = max(indent, 0)
        if indent == self.indent:
            return
        self.indent = indent
        if not silent:
            self.SendPropEvent(wxEVT_PROP_INDENT)

    def GetIndent(self):
        """get the indent"""
        return self.indent

    def Expand(self, expand=True, silent=True):
        """expand/collapse the children"""
        self.SetExpand(expand, silent)
        return self

    def SetExpand(self, expand=True, silent=False):
        """expand/collapse the children"""
        if expand == self.expanded:
            return
        self.expanded = expand

        if silent or not self.HasChildren():
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

    def Children(self, haschildren, silent=True):
        """Indicate that the property has children"""
        self.SetHasChildren(haschildren, silent)
        return self

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

    def Activated(self, activated=True):
        """activate the property"""
        self.SetActivated(activated)
        return self

    def SetActivated(self, activated=True):
        """activate the property"""
        if activated == self.activated:
            return
        self.activated = activated
        if activated:
            self.SendPropEvent(wxEVT_PROP_SELECTED)

    def IsActivated(self):
        """return true if the property is activated"""
        return self.activated

    def Readyonly(self, readonly=True, silent=True):
        """set the property to readonly"""
        self.SetReadonly(readonly, silent)
        return self

    def SetReadonly(self, readonly=True, silent=False):
        """set the property to readonly"""
        if readonly != self.IsReadonly():
            self.readonly = readonly
            if not silent:
                self.Refresh()

    def IsReadonly(self):
        """return true if the property is readonly"""
        return self.readonly

    def TextColor(self, clr=None, clr_sel=None, clr_disabled=None, silent=True):
        """
        set the text colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.SetTextColor(clr, clr_sel, clr_disabled, silent)
        return self

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

    def BgColor(self, clr=None, clr_sel=None, clr_disabled=None, silent=True):
        """
        set the background colors

        All values are string. If the value is None, the color will reset to
        default.
        """
        self.SetBgColor(clr, clr_sel, clr_disabled, silent)
        return self

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

    def TitleWidth(self, width):
        """set the title width"""
        self.SetTitleWidth(width)
        return self

    def SetTitleWidth(self, width):
        """set the title width"""
        self.title_width = width

    def GetTitleWidth(self):
        """return the width"""
        return self.title_width

    def Rect(self, rc):
        """set the prop rect"""
        self.SetRect(rc)
        return self

    def SetRect(self, rc):
        """set the prop rect"""
        if self.rect != rc:
            self.rect = wx.Rect(*rc)
            # redraw the item
            self.Refresh()

    def GetRect(self):
        """return the prop rect"""
        return wx.Rect(*self.rect)

    def MinSize(self, size, silent=True):
        """set the min size"""
        self.SetMinSize(size, silent)
        return self

    def SetMinSize(self, size, silent=False):
        """set the min size"""
        if self.min_size != size:
            self.min_size = wx.Size(*size)
            if not silent:
                self.Resize()

    def GetMinSize(self):
        """return the min size"""
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

    def Draggable(self, draggable):
        """set if it is allow to drag/drop the prop"""
        self.SetDraggable(draggable)
        return self

    def SetDraggable(self, draggable):
        """set if it is allow to drag/drop the prop"""
        self.draggable = draggable

    def IsDraggable(self):
        """get if it is allow to drag/drop the prop"""
        return self.draggable

    def Configurable(self, configurable):
        """set if it is allow to configure the prop"""
        self.SetConfigurable(configurable)
        return self

    def SetConfigurable(self, configurable):
        """set if it is allow to configure the prop"""
        self.configurable = configurable

    def IsConfigurable(self):
        """get if it is allow to configure the prop"""
        return self.configurable

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

        return ht

    def OnMouseUp(self, pt):
        ht = self.HitTest(pt)
        return ht

    def OnMouseDoubleClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            if ht == 'expander':
                self.SetExpand(not self.expanded)

            self.SendPropEvent(wxEVT_PROP_DOUBLE_CLICK)

        return ht

    def OnMouseRightClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            # destroy the control when the mouse moves out
            self.SendPropEvent(wxEVT_PROP_RIGHT_CLICK)

        return ht

    def OnMouseMove(self, pt):
        ht = self.HitTest(pt)
        return ht

    def SendPropEvent(self, event):
        """ send property grid event to parent"""
        win = self.GetGrid()
        evt = PropEvent(event, self)
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

    def PostRefresh(self):
        pass

class PropEvent(wx.PyCommandEvent):
    def __init__(self, commandType, prop, id=0):
        wx.PyCommandEvent.__init__(self, commandType, id)
        self.prop = prop
        self.veto = False

    def GetProp(self):
        """return the attached Property"""
        return self.prop

    def SetProp(self, prop):
        """attach the Property instance"""
        assert isinstance(prop, PropBase)
        self.prop = prop

    def Veto(self, veto=True):
        """refuse the event"""
        self.veto = veto

    def GetVeto(self):
        """return whether the event is refused"""
        return self.veto

class PropControl(PropGeneric):
    def __init__(self, *args, **kwargs):
        PropGeneric.__init__(self, *args, **kwargs)
        self.window = None
        self.allow_editing = True

    def __del__(self):
        self.DestroyControl()

    def _prepare_copy(self):
        # destroy the window, otherwise the copy will also point to the same window
        self.UpdatePropValue()
        self.DestroyControl()

    def duplicate(self):
        # destroy the window, otherwise the copy will also point to the same window
        self.UpdatePropValue()
        self.DestroyControl()
        return super().duplicate()

    def Editing(self, enable):
        self.SetEditting(enable)
        return self

    def SetEditting(self, enable):
        self.allow_editing = enable

    def GetEditting(self):
        return self.allow_editing

    def SetValue(self, value, silent=False):
        self.DestroyControl()
        return super().SetValue(value, silent)

    def SetActivated(self, activated=True):
        """activate the property"""
        super().SetActivated(activated)
        if not activated:
            # destroy the control if the property is inactivated
            self.OnTextEnter()

    def SetRect(self, rc):
        """set the prop rect"""
        if self.rect != rc:
            wx.CallAfter(self.LayoutControl)
        super().SetRect(rc)

    def doCreateControl(self):
        return None

    def CreateControl(self):
        """create the control"""
        if self.window is not None:
            return
        if not self.allow_editing:
            return
        win = self.doCreateControl()

        if win is not None:
            if win.GetValidator():
                win.GetValidator().TransferToWindow()
            self.window = win
            # the window size may be larger than the value rect, notify parent
            # grid to update it
            self.Resize()
            self.LayoutControl()
            self.window.SetFocus()
            #self.window.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
            self.draws['value'] = False

    def OnMouseDown(self, pt):
        ht = super().OnMouseDown(pt)

        if self.IsEnabled() and ht == 'value':
            if not self.IsReadonly() and self.IsActivated():
                self.CreateControl()
        else:
            self.UpdatePropValue()
            self.DestroyControl()

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

        return  super().OnMouseDoubleClick(pt)

    def OnMouseRightClick(self, pt):
        ht = self.HitTest(pt)

        if self.IsEnabled():
            # destroy the control when the mouse moves out
            if ht is None:
                self.UpdatePropValue()
                self.DestroyControl()

        return super().OnMouseRightClick(pt)

    def OnTextEnter(self):
        self.UpdatePropValue()
        self.DestroyControl()
        self.Refresh()

    def OnPropTextEnter(self, evt):
        """send when the enter key is pressed in the property control window"""
        if self.window:
            self.OnTextEnter()

    def DestroyControl(self):
        """destroy the value setting control"""
        def _destroy():
            if self.window:
                self.window.Show(False)
                self.window.Destroy()
                self.window = None
                self.Resize()

        self.draws['value'] = True
        if self.window:
            # otherwise, it may crash (e..g, MacOS)
            # not be able to reproduce it with MacOS 13.2.1
            _destroy()
            return True
        return False

    def doGetValueFromWin(self):
        return None

    def UpdatePropValue(self):
        """update the value"""
        if self.window is None:
            return False
        old_value = self.value
        validator = self.window.GetValidator()
        if validator:
            validator.TransferFromWindow()
        else:
            value = self.doGetValueFromWin()
            if value is not None:
                value = self.coerce(value)
            if value is not None:
                self.SetValue(value, silent=True)
        if old_value == self.value:
            return False

        if self.SendPropEvent(wxEVT_PROP_CHANGING):
            self.SendPropEvent(wxEVT_PROP_CHANGED)
            self.Refresh()
            return True
        else:
            #the parent rejects the operation, restore the original value
            self.SetValue(old_value)
            return False
        return False

    def LayoutControl(self):
        """re-positioning the control"""
        if self.window is None:
            return
        rc = self.grid.GetScrolledRect(wx.Rect(*self.regions['value']))
        self.window.SetSize(rc.GetSize())
        self.window.Move(rc.GetTopLeft())

    def GetMinSize(self):
        """return the min size"""
        if self.window:
            size = self.window.GetSize()
            sz = self.min_size
            size.y = max(sz.y, size.y)
            return size
        return super().GetMinSize()

    def coerce(self, value):
        try:
            if self.formatter:
                if self.formatter.validate(str(value)):
                    value = self.formatter.coerce(str(value))
                else:
                    return None
            elif self.value is not None:
                value = type(self.value)(value)
            return value
        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return None

    def PostRefresh(self):
        """notify the window to redraw itself"""
        if self.window is not None:
            self.window.Refresh()

class PropSeparator(PropGeneric):
    def __init__(self, *args, **kwargs):
        PropGeneric.__init__(self, *args, **kwargs)
        self.regions = {
                'label': wx.Rect(),
                'expander': wx.Rect()
                }
        self.draws = {
                'value': False,
                'label': True,
                'splitter': False,
                'expander': True
                }
        self.Separator(True)

class PropEditBox(PropControl):
    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        style = wx.TE_PROCESS_ENTER
        sz = self.GetMinSize()
        if sz.y > 50:
            style = wx.TE_MULTILINE
        win = wx.TextCtrl(self.grid, wx.ID_ANY, self.GetValueAsString(),
                          style=style)
        if self.formatter:
            validator = TextValidator(self, 'value', self.formatter, False, None)
            win.SetValidator(validator)
        if style & wx.TE_PROCESS_ENTER:
            win.Bind(wx.EVT_TEXT_ENTER, self.OnPropTextEnter)

        return win

    def OnPropTextEnter(self, evt):
        """send when the enter key is pressed in the property control window"""
        if self.window:
            wx.CallAfter(self.OnTextEnter)

    def doGetValueFromWin(self):
        """update the value"""
        if self.window is None:
            return None

        value = None
        if isinstance(self.window, wx.TextCtrl):
            value = self.window.GetValue()

        return value

class PropText(PropEditBox):
    pass

class PropInt(PropText):
    def __init__(self, *args, **kwargs):
        PropText.__init__(self, *args, **kwargs)
        self.Formatter(fmt.IntFormatter())

class PropHex(PropText):
    def __init__(self, *args, **kwargs):
        PropText.__init__(self, *args, **kwargs)
        self.Formatter(fmt.HexFormatter())

class PropBin(PropText):
    def __init__(self, *args, **kwargs):
        PropText.__init__(self, *args, **kwargs)
        self.Formatter(fmt.BinFormatter())

class PropFloat(PropText):
    def __init__(self, *args, **kwargs):
        PropText.__init__(self, *args, **kwargs)
        self.Formatter(fmt.FloatFormatter())

class PropChoice(PropControl):
    def __init__(self, choice, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.Formatter(fmt.ChoiceFormatter(choice))

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        win = wx.Choice(self.grid, wx.ID_ANY)
        if self.formatter:
            validator = SelectorValidator(self, 'value', self.formatter, True)
            win.SetValidator(validator)

        return win

    def doGetValueFromWin(self):
        """update the value"""
        if self.window is None:
            return None

        sel = self.window.GetSelection()
        if sel >= 0 and sel < self.window.GetCount():
            value = self.window.GetString(sel)

        return value


class PropRadioBox(PropControl):
    def __init__(self, choice=None, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        if choice is None:
            choice = []
        self.Formatter(fmt.ChoiceFormatter(choice))

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        choices = []
        if self.formatter and hasattr(self.formatter, 'validValues'):
            choices = [str(x[1]) for x in self.formatter.validValues()]

        win = wx.RadioBox(self.grid, wx.ID_ANY, "", wx.DefaultPosition,
                          wx.DefaultSize, choices, 5, wx.RA_SPECIFY_COLS)

        if self.formatter:
            validator = RadioBoxValidator(self, 'value', self.formatter,
                                          True)
            win.SetValidator(validator)
        return win

    def doGetValueFromWin(self):
        """update the value"""
        if self.window is None:
            return None
        sel = self.window.GetSelection()
        if sel >= 0 and sel < self.window.GetCount():
            value = self.window.GetString(sel)
            return value
        return None

class PropCheckBox(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.Formatter(fmt.BoolFormatter())

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        win = wx.CheckBox(self.grid, wx.ID_ANY)
        win.SetValue(int(self.value) != 0)
        return win

    def doGetValueFromWin(self):
        value = self.window.GetValue()
        return value


class PropFile(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.Formatter(fmt.PathFormatter(False, 'file'))
        self.selected_file = None

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        #win = wx.Button(self.grid, wx.ID_ANY, self.GetValueAsString())
        #win.Bind(wx.EVT_BUTTON, self.OnSelectFile)
        self.selected_file = None
        self.doSelectFile()
        return None

    def doSelectFile(self):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dlg = wx.FileDialog(self.grid, "Choose a file",
                            self.GetValueAsString(), "", "*.*", style)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()

    def doGetValueFromWin(self):
        return self.selected_file

class PropFolder(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.Formatter(fmt.PathFormatter(False, 'folder'))

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        self.doSelectFolder()
        return None

    def doSelectFolder(self):
        dlg = wx.DirDialog(self.grid, "Choose input directory",
                           self.GetValueAsString(),
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()

class PropSpin(PropControl):
    def __init__(self, min_value=0, max_value=2**31-1, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.Formatter(fmt.IntFormatter(min_value, max_value))

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        win = wx.SpinCtrl(self.grid,
                          wx.ID_ANY,
                          value=str(self.value),
                          style=wx.SP_ARROW_KEYS)
        if self.formatter:
            validator = SpinSliderValidator(self, 'value', self.formatter,
                                            True)
            win.SetValidator(validator)
        return win

    def doGetValueFromWin(self):
        """update the value"""
        if self.window is None:
            return None
        value = self.window.GetValue()

        return value

class PropSlider(PropControl):
    def __init__(self, min_value=0, max_value=2**31-1, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.Formatter(fmt.IntFormatter(min_value, max_value))

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        win = wx.Slider(self.grid,
                        wx.ID_ANY,
                        value=int(self.value),
                        style=wx.SL_LABELS | wx.SL_HORIZONTAL | wx.SL_TOP)
        if self.formatter:
            validator = SpinSliderValidator(self, 'value', self.formatter,
                                            True)
            win.SetValidator(validator)
        return win

    def doGetValueFromWin(self):
        if self.window is None:
            return None
        value = self.window.GetValue()
        return value

class PropDate(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.SetFormatter(fmt.DateFormatter())

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        win = wx.adv.DatePickerCtrl(self.grid, wx.ID_ANY)
        try:
            win.SetValue(self.value)
        except ValueError:
            pass
        return win

    def doGetValueFromWin(self):
        if self.window is None:
            return None
        value = self.window.GetValue()
        if self.formatter:
            value = self.formatter.format(value)

        return value

class PropTime(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.SetFormatter(fmt.TimeFormatter())

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        win = wx.adv.TimePickerCtrl(self.grid, wx.ID_ANY)
        try:
            win.SetValue(self.value)
        except ValueError:
            pass
        return win

    def doGetValueFromWin(self):
        if self.window is None:
            return None
        value = self.window.GetValue()
        if self.formatter:
            value = self.formatter.format(value)

        return value

class PropDateTime(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.SetFormatter(fmt.DateTimeFormatter())

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        menu = wx.Menu()
        date = menu.Append(wx.ID_ANY, 'Update date')
        time = menu.Append(wx.ID_ANY, 'Update time')
        cmd = self.GetPopupMenuSelectionFromUser(menu)
        win = None
        if cmd == time.GetId():
            win = wx.adv.TimePickerCtrl(self.grid, wx.ID_ANY)
        elif cmd == date.GetId():
            win = wx.adv.DatePickerCtrl(self.grid, wx.ID_ANY)
        if win is not None:
            try:
                win.SetValue(self.value)
            except ValueError:
                pass
        return win

    def doGetValueFromWin(self):
        if self.window is None:
            return None
        value = self.window.GetValue()
        if self.formatter:
            value = self.formatter.format(value)

        return value

class PropFont(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.SetFormatter(fmt.FontFormatter())

        self.auto_apply = True

    def AutoApply(self, apply):
        self.SetAutoApply(apply, True)

    def SetAutoApply(self, apply, silent=False):
        self.auto_apply = apply
        if not silent:
            self.Refresh()

    def GetAutoApply(self):
        return self.auto_apply

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window

        data = wx.FontData()
        data.SetInitialFont(wx.Font(self.GetValue()))
        dlg = wx.FontDialog(self.grid, data)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetFontData().GetChosenFont())
        return None

    def SetValue(self, value, silent=False):
        if isinstance(value, wx.Font):
            value = value.GetNativeFontInfoDesc()

        if super().SetValue(value, True):
            if self.auto_apply:
                # set the font for value
                font = wx.Font(self.GetValue())
                font.SetFractionalPointSize(wx.NORMAL_FONT.GetFractionalPointSize())
                self.SetValueFont(font, True)
            if not silent:
                self.Refresh()

    def GetValueAsString(self):
        """get the value as string"""
        font =  wx.Font(self.GetValue())
        return f'{font.GetFaceName()}, {font.GetFractionalPointSize()}'

class PropColor(PropControl):
    def __init__(self, *args, **kwargs):
        PropControl.__init__(self, *args, **kwargs)
        self.SetFormatter(fmt.ColorFormatter())
        self.auto_apply = True

    def AutoApply(self, apply):
        self.SetAutoApply(apply, True)

    def SetAutoApply(self, apply, silent=False):
        self.auto_apply = apply
        if not silent:
            self.Refresh()

    def GetAutoApply(self):
        return self.auto_apply

    def doCreateControl(self):
        """create the control"""
        if self.window is not None:
            return self.window
        data = wx.ColourData()
        data.SetColour(wx.Colour(self.GetValue()))
        dlg = wx.ColourDialog(self.grid, data)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetColourData().GetColour())
        return None

    def SetValue(self, value, silent=False):
        if isinstance(value, wx.Colour):
            value = value.GetAsString(wx.C2S_HTML_SYNTAX)
        if super().SetValue(value, True):
            if self.auto_apply:
                t = wx.Colour(self.GetValue())
                c = t.GetAsString(wx.C2S_HTML_SYNTAX)
                self.SetBgColor(c, c, c, True)
                t.SetRGB(t.GetRGB() ^ 0xFFFFFF)
                t = t.GetAsString(wx.C2S_HTML_SYNTAX)
                self.SetTextColor(t, t, t, True)

            if not silent:
                self.Refresh()
