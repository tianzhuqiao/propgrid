import sys
import traceback
import json
import six
import wx
import wx.py.dispatcher as dp
import wx.lib.agw.aui as aui
from .prop import *

wxEVT_PROP_INSERT = wx.NewEventType()
wxEVT_PROP_DELETE = wx.NewEventType()

EVT_PROP_INSERT = wx.PyEventBinder(wxEVT_PROP_INSERT, 1)
EVT_PROP_DELETE = wx.PyEventBinder(wxEVT_PROP_DELETE, 1)

def PopupMenu(wnd, menu):
    if not wnd or not menu:
        return

    cc = aui.ToolbarCommandCapture()
    wnd.PushEventHandler(cc)

    wnd.PopupMenu(menu)

    command = cc.GetCommandId()
    wnd.PopEventHandler(True)
    return command

class PropDropTarget(wx.DropTarget):
    def __init__(self, frame):
        wx.DropTarget.__init__(self)
        self.obj = wx.TextDataObject()
        self.SetDataObject(self.obj)
        self.frame = frame

    def OnEnter(self, x, y, d):
        return super(PropDropTarget, self).OnDragOver(x, y, d)

    def OnLeave(self):
        pass

    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone
        self.frame.OnDrop(x, y, self.obj.GetText())

        return d

    def OnDragOver(self, x, y, d):
        pt = wx.Point(x, y)
        rc = self.frame.GetClientRect()
        if rc.Contains(pt):
            (x, y) = self.frame.GetViewStart()
            if pt.y < 15:
                self.frame.Scroll(-1, y-(15-pt.y)/3)
            if pt.y > rc.bottom-15:
                self.frame.Scroll(-1, y-(rc.bottom-15-pt.y)/3)
        return super(PropDropTarget, self).OnDragOver(x, y, d)

class PropGrid(wx.ScrolledWindow):
    ID_PROP_GRID_ADD_SEP = wx.NewId()
    ID_PROP_GRID_READ_ONLY = wx.NewId()
    ID_PROP_GRID_INDENT_INS = wx.NewId()
    ID_PROP_GRID_INDENT_DES = wx.NewId()
    ID_PROP_GRID_MOVE_UP = wx.NewId()
    ID_PROP_GRID_MOVE_DOWN = wx.NewId()
    ID_PROP_GRID_DELETE = wx.NewId()
    ID_PROP_GRID_PROP = wx.NewId()

    drag_state = 0
    drag_start = wx.Point(0, 0)
    drag_prop = None
    drag_pg = None

    RESIZE_NONE = 0
    RESIZE_SEP = 1
    RESIZE_BOT = 2

    SCROLL_UNIT = 5

    CURSOR_RESIZE_HORZ = 0
    CURSOR_RESIZE_VERT = 1
    CURSOR_STD = 2

    def __init__(self, frame):
        wx.ScrolledWindow.__init__(self, frame)

        self.title_width = 150
        self.prop_selected = None
        self.cursor_mode = self.CURSOR_STD
        self.pos_mouse_down = wx.Point(0, 0)
        self.prop_under_mouse = None
        self.resize_mode = self.RESIZE_NONE

        self._props = []

        # cursor
        self.resize_cursor_horz = wx.Cursor(wx.CURSOR_SIZEWE)
        self.resize_cursor_vert = wx.Cursor(wx.CURSOR_SIZENS)

        # set scroll parameters
        self.SetScrollRate(self.SCROLL_UNIT, self.SCROLL_UNIT)
        self.SetVirtualSize(wx.Size(100, 200))

        self.SetDropTarget(PropDropTarget(self))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDoubleClick)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        # calling CaptureMouse requires to implement EVT_MOUSE_CAPTURE_LOST
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseCaptureLost)

        self.Bind(EVT_PROP_SELECTED, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_CHANGING, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_CHANGED, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_HIGHLIGHTED, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_RIGHT_CLICK, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_COLLAPSED, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_EXPANDED, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_DOUBLE_CLICK, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_INDENT, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_KEYDOWN, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_RESIZE, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_REFRESH, self.OnPropRefresh)
        self.Bind(EVT_PROP_DROP, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_BEGIN_DRAG, self.OnPropEventsHandler)
        self.Bind(EVT_PROP_CLICK_CHECK, self.OnPropEventsHandler)
        self.Bind(wx.EVT_MENU, self.OnProcessCommand)

    def AppendProperty(self, name, label="", value="", update=True):
        return self.InsertProperty(name, label, value, -1, update)

    def _InsertProperty(self, prop, index=-1, update=True):
        # add the prop window to the grid
        if not isinstance(prop, Property):
            return None

        if index == -1 or index >= self.GetPropCount():
            self._props.append(prop)
        else:
            self._props.insert(index, prop)
        name = prop.GetName()

        if index != -1 and (not update):
            self.CheckProp()
        if update:
            self.UpdateGrid()
        if self.SendPropEvent(wxEVT_PROP_INSERT, prop):
            dp.send('prop.insert', prop=prop)
        return prop

    def InsertProperty(self, name, label="", value="", index=-1, update=True):
        # add the prop window to the grid
        prop = Property(self, name, label, value)
        return self._InsertProperty(prop, index, update)

    def CopyProperty(self, prop, index=-1, update=True):
        if not isinstance(prop, Property):
            return None
        p = prop.duplicate()
        p.SetParent(self)
        return self._InsertProperty(p, index, update)

    def InsertSeparator(self, name='Separator', label='', index=-1, update=True):
        prop = self.InsertProperty(name, label, '', index, update)
        if prop:
            prop.SetSeparator(True)
        return prop

    def RemoveProperty(self, prop, update=True):
        # remove property
        if isinstance(prop, six.string_types) or isinstance(prop, Property):
            index = self.FindPropertyIndex(prop)
        elif isinstance(prop, int):
            index = prop
        else:
            return False

        if index >= 0 and index < self.GetPropCount():
            prop = self._props[index]
            activated = False
            if prop == self.prop_selected:
                activated = True
                self.SelectProperty(-1)
            del self._props[index]

            if index != -1 and (not update):
                self.CheckProp()
            if index >= self.GetPropCount():
                index = self.GetPropCount() - 1

            if activated:
                self.SelectProperty(index)
            if update:
                self.UpdateGrid()
            return True
        return False

    def DeleteAllProperties(self, update=True):
        for i in range(len(self._props)-1, -1, -1):
            self.DeleteProperty(self._props[i], update)

    def DeleteProperty(self, prop, update=True):
        if self.SendPropEvent(wxEVT_PROP_DELETE, prop):
            dp.send('prop.delete', prop=prop)
            return self.RemoveProperty(prop, update)
        else:
            return False

    def FindPropertyIndex(self, prop):
        """return the index of prop, or -1 if not found"""
        p = self.GetProperty(prop)
        if not p:
            return -1
        try:
            idx = self._props.index(p)
            return idx
        except ValueError:
            traceback.print_exc(file=sys.stdout)
        return -1

    def GetProperty(self, prop):
        """return the Property instance"""
        if isinstance(prop, Property):
            # if prop is a Property instance, simply return
            return prop
        elif isinstance(prop, six.string_types):
            # search the prop name
            props = [p for p in self._props if p.GetName() == prop]
            if not props:
                return None
            elif len(props) == 1:
                return props[0]
            return props
        elif isinstance(prop, int):
            # prop is the index
            index = prop
            if index >= 0 and index < self.GetPropCount():
                return self._props[index]
        return None

    def GetPropCount(self):
        """return the number of properties"""
        return len(self._props)

    def EnsureVisible(self, prop):
        """scroll the window to make sure prop is visible"""
        p = self.GetProperty(prop)
        if not p:
            return
        rc_prop = p.GetClientRect()
        # translate to the scrolled position
        rc_prop.x, rc_prop.y = self.CalcScrolledPosition(rc_prop.x, rc_prop.y)
        _, y = self.GetViewStart()
        rc = self.GetClientRect()
        if rc.top < rc_prop.top and rc.bottom > rc_prop.bottom:
            # if the prop is visible, simply return
            return
        if rc.top > rc_prop.top:
            # if the prop is on top of the client window, scroll up
            y = y + ((rc_prop.top - rc.top)/self.SCROLL_UNIT)
            self.Scroll(-1, y)
        elif rc.bottom < rc_prop.bottom:
            # if the prop is under bottom of the client window, scroll down
            y = y + ((rc_prop.bottom-rc.bottom)/self.SCROLL_UNIT)
            self.Scroll(-1, y)

    def GetSelection(self):
        """get the index of the selected property"""
        return self.FindPropertyIndex(self.prop_selected)

    def GetSelectedProperty(self):
        """return the selected property"""
        return self.prop_selected

    def SetSelection(self, prop):
        """set the active property"""
        p = self.GetProperty(prop)
        if p != self.prop_selected:
            if self.prop_selected:
                self.prop_selected.SetActivated(False)
            self.prop_selected = p
            if self.prop_selected:
                self.prop_selected.SetActivated(True)
            self.Refresh()
            return True
        return False

    def UpdateGrid(self):
        """update the grid"""
        self.LayoutAll()
        self.Refresh()

    def MoveProperty(self, prop, step):
        """move the property"""
        index = self.FindPropertyIndex(prop)
        if index == -1:
            return

        if step == 0:
            # move zero step is no move at all
            return

        # calculate the new position
        index2 = index + step
        if index2 < 0:
            index2 = 0
        # move the prop, prop will be placed on top of index2
        if index2 < self.GetPropCount():
            self.doMoveProperty(index, index2)
        else:
            self.doMoveProperty(index, -1)

    def doMoveProperty(self, index, index2):
        """move the property"""
        # the same position, ignore it
        if index == index2:
            return

        prop = self.GetProperty(index)
        props = [prop]
        if prop.HasChildren() and (not prop.IsExpanded()):
            # move all the children if they are not visible
            indent = prop.GetIndent()
            for i in six.moves.range(index+1, self.GetPropCount()):
                if self._props[i].GetIndent() <= indent:
                    break
                props.append(self._props[i])

        i = 0
        for p in props:
            if index2 == -1:
                self._props.append(p)
            else:
                #insert it before index2
                self._props.insert(index2+i, p)
                i += 1

        if index2 != -1 and index > index2:
            index = index + len(props)

        # delete the original properties
        for i in six.moves.range(0, len(props)):
            del self._props[index]

        self.UpdateGrid()

    def MovePropertyDown(self, prop):
        """move the property one step down"""
        # here step is 2 instead of 1 because the prop will be moved in front
        # of index + step. For example, prop is at position 5, to move it to
        # position 6:
        #    step 1) copy it in front of position 7 (position 7);
        #    step 2) remove the original prop at position 5
        #    step 3) the copy from step 1) will be at position 6 now
        self.MoveProperty(prop, 2)

    def MovePropertyUp(self, prop):
        """move the property one step up"""
        # here the step is -1. For example, prop is at position 5, to move it
        # to position 4, we can say move it in front of position 4. Delete the
        # original prop will not affect the position of the new copy.
        self.MoveProperty(prop, -1)

    def SendPropEvent(self, event, prop=None):
        """send the property event to the parent"""
        prop = self.GetProperty(prop)
        # prepare the event
        if isinstance(event, PropertyEvent):
            evt = event
        elif isinstance(event, int):
            evt = PropertyEvent(event)
            evt.SetProperty(prop)
        else:
            raise ValueError()

        evt.SetId(self.GetId())
        eventObject = self.GetParent()
        evt.SetEventObject(eventObject)
        evtHandler = eventObject.GetEventHandler()

        evtHandler.ProcessEvent(evt)
        return not evt.GetVeto()

    def NavigateProp(self, down):
        """change the selected property"""
        sel = self.GetSelection()
        # find the next visible property and activate it
        while True:
            if down:
                sel += 1
            else:
                sel -= 1

            if sel < 0 or sel >= self.GetPropCount():
                break

            prop = self._props[sel]
            if prop.IsVisible():
                self.SetSelection(sel)
                self.EnsureVisible(sel)
                break

    def PropHitTest(self, pt):
        """find the property under the mouse"""
        for i, prop in enumerate(self._props):
            prop = self._props[i]
            if  not prop.IsVisible():
                continue
            if prop.GetClientRect().Contains(pt):
                return i
        return -1

    def LayoutAll(self, update=True):
        """layout the properties"""
        rc = self.GetClientRect()
        (w, h) = (rc.width, 1)

        self.CheckProp()
        # calculate the width and height
        for p in self._props:
            if p.IsVisible():
                sz = p.GetMinSize()
                w = max(w, sz.x)
                h = h + sz.y
        if update:
            # update the virtual size
            self.SetVirtualSize(wx.Size(w, h))

        # set the property rect
        rc = self.GetClientRect()
        w, y = max(w, rc.width), 1
        for p in self._props:
            if p.IsVisible():
                h = p.GetMinSize().y
                p.SetClientRect(wx.Rect(0, y, w, h))
                y += h

    def GetDrawRect(self):
        """return the drawing rect"""
        sz = self.GetClientSize()
        rc = wx.Rect(0, 0, sz.x, sz.y)

        # shift the client rectangle to take into account scrolling, converting
        # device to logical coordinates
        (rc.x, rc.y) = self.CalcUnscrolledPosition(rc.x, rc.y)

        return rc

    def CheckProp(self):
        """update the property status"""
        parent = None
        for i, prop in enumerate(self._props):
            parent = self.GetProperty(i-1)
            # find the direct parent property
            while parent:
                if parent.GetIndent() < prop.GetIndent():
                    break
                parent = parent.GetParent()
            prop.SetParent(parent)
            if parent:
                # the parent has children now
                parent.SetHasChildren(True, True)
            # the current one does not have children yet; will be set by its
            # children
            prop.SetHasChildren(False, True)

        # show/hide the properties
        for prop in self._props:
            parent = prop.GetParent()
            if not parent:
                # always show prop without parent
                show = True
            else:
                # prop with parent depends on parent's status
                show = parent.IsExpanded() and parent.IsVisible()
            prop.SetVisible(show)

    def OnPropRefresh(self, evt):
        """refresh the property, for example, due to value changed"""
        self.SendPropEvent(evt.GetEventType(), evt.GetProperty())
        prop = evt.GetProperty()
        if prop is None:
            return
        rc = prop.GetClientRect()
        rc.x, rc.y = self.CalcScrolledPosition(rc.x, rc.y)
        self.RefreshRect(rc, True)

    def GetContextMenu(self, prop):
        # show the context menu
        menu = wx.Menu()
        menu.Append(self.ID_PROP_GRID_ADD_SEP, "&Add separator")
        menu.AppendCheckItem(self.ID_PROP_GRID_READ_ONLY, "&Read only")
        menu.Check(self.ID_PROP_GRID_READ_ONLY, prop.IsReadonly())

        menu.AppendSeparator()
        menu.Append(self.ID_PROP_GRID_INDENT_INS, "Increase Indent\tCtrl-Right")
        menu.Append(self.ID_PROP_GRID_INDENT_DES, "Decrease Indent\tCtrl-Left")
        menu.AppendSeparator()
        menu.Append(self.ID_PROP_GRID_MOVE_UP, "Move up\tCtrl-Up")
        menu.Append(self.ID_PROP_GRID_MOVE_DOWN, "Move down\tCtrl-Down")
        menu.AppendSeparator()
        menu.Append(self.ID_PROP_GRID_DELETE, "&Delete")
        menu.AppendSeparator()
        menu.Append(self.ID_PROP_GRID_PROP, "&Properties")
        return menu

    def OnPropEventsHandler(self, evt):
        """process the property notification"""
        if not self.SendPropEvent(evt.GetEventType(), evt.GetProperty()):
            # vetoed by parent, ignore the event
            return False

        eid = evt.GetEventType()
        if eid in [wxEVT_PROP_COLLAPSED, wxEVT_PROP_EXPANDED,
                   wxEVT_PROP_INDENT, wxEVT_PROP_RESIZE]:
            self.UpdateGrid()
        elif eid == wxEVT_PROP_RIGHT_CLICK:
            menu = self.GetContextMenu(evt.GetProperty())
            cmd = PopupMenu(self, menu)
            self.OnProcessCommand(cmd, evt.GetProperty())
        return True

    def OnProcessCommand(self, eid, prop):
        """process the context menu command"""
        if not prop:
            return

        if eid == self.ID_PROP_GRID_DELETE:
            self.DeleteProperty(prop)
        elif eid == self.ID_PROP_GRID_READ_ONLY:
            prop.SetReadonly(not prop.IsReadonly())
        elif eid == self.ID_PROP_GRID_PROP:
            dlg = PropSettings(self, prop)
            if dlg.ShowModal() == wx.ID_OK:
                prop.Refresh()
        elif eid == self.ID_PROP_GRID_INDENT_INS:
            prop.SetIndent(prop.GetIndent()+1)
        elif eid == self.ID_PROP_GRID_INDENT_DES:
            prop.SetIndent(prop.GetIndent()-1)
        elif eid == self.ID_PROP_GRID_MOVE_UP:
            self.MoveProperty(prop, -1)
        elif eid == self.ID_PROP_GRID_MOVE_DOWN:
            self.MoveProperty(prop, 2)
        elif eid == self.ID_PROP_GRID_ADD_SEP:
            self.InsertSeparator(index=self.GetSelection())

    def OnKeyDown(self, evt):
        """key down event"""
        prop = self.prop_selected
        skip = True
        if prop:
            skip = False
            index = self.GetSelection()
            keycode = evt.GetKeyCode()
            indent = prop.GetIndent()
            if keycode == wx.WXK_LEFT:
                if evt.CmdDown():
                    # Ctrl + Left decrease the indent
                    prop.SetIndent(indent-1)
                else:
                    # Left hide children
                    prop.SetExpand(False)
            elif keycode == wx.WXK_UP:
                if evt.CmdDown():
                    # Ctrl + Up move up
                    self.MovePropertyUp(index)
                else:
                    # Up select the above property
                    self.NavigateProp(False)
            elif keycode == wx.WXK_RIGHT:
                if evt.CmdDown():
                    # Ctrl + Right increase the indent
                    prop.SetIndent(indent+1)
                else:
                    # Right show children
                    prop.SetExpand(True)
            elif keycode == wx.WXK_DOWN:
                if evt.CmdDown():
                    # Ctrl + Down move the property down
                    self.MovePropertyDown(index)
                else:
                    # Down select the property below
                    self.NavigateProp(True)
            elif keycode == wx.WXK_DELETE:
                # delete the property
                self.RemoveProperty(self.GetSelectedProperty())
            else:
                skip = True
        if skip:
            evt.Skip()

    def OnPaint(self, event):
        """draw the property"""
        dc = wx.BufferedPaintDC(self)
        self.DoPrepareDC(dc)

        rc = self.GetDrawRect()
        #draw background
        bg = self.GetBackgroundColour()
        if not bg.IsOk():
            bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        pen = wx.Pen(wx.BLACK, 1, wx.PENSTYLE_TRANSPARENT)
        dc.SetPen(pen)
        brush = wx.Brush(bg)
        dc.SetBrush(brush)
        dc.DrawRectangle(rc.x, rc.y, rc.width, rc.height)

        # draw the top edge
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(rc.left, rc.top, rc.right, rc.top)

        # draw the properties
        for p in self._props:
            if not p.IsVisible():
                continue
            rc_prop = p.GetClientRect()
            if rc.Intersects(rc_prop):
                p.SetTitleWidth(self.title_width)
                p.DrawItem(dc)

    def OnSize(self, evt):
        """resize the properties"""
        self.UpdateGrid()
        evt.Skip()

    def OnEraseBackground(self, evt):
        """redraw the background"""
        #intentionally leave empty to remove the screen flash
        pass

    def OnMouseDown(self, evt):
        """left mouse down"""
        # find the property under mouse
        pt = self.CalcUnscrolledPosition(evt.GetPosition())
        index = self.PropHitTest(pt)
        self.pos_mouse_down = pt
        if index != -1:
            prop = self.GetProperty(index)

            # pass the event to the property
            ht = prop.OnMouseDown(pt)
            self.prop_under_mouse = prop
            self.CaptureMouse()
            self.resize_mode = self.RESIZE_NONE
            if ht == PROP_HIT_SPLITTER:
                # drag the splitter
                self.resize_mode = self.RESIZE_SEP
            elif ht == PROP_HIT_EDGE_BOTTOM:
                # drag the bottom edge
                self.resize_mode = self.RESIZE_BOT
            elif ht == PROP_HIT_EDGE_TOP:
                # drag the bottom edge of the property above
                if index > 0:
                    index = index-1
                    self.prop_under_mouse = self.GetProperty(index)
                    self.resize_mode = self.RESIZE_BOT
            elif ht == PROP_HIT_TITLE:
                # start drag & drop
                PropGrid.drag_start = self.ClientToScreen(pt)
                PropGrid.drag_prop = prop
                PropGrid.drag_state = 1
        # activate the property under mouse
        self.SetSelection(index)
        evt.Skip()

    def OnMouseUp(self, evt):
        """left mouse up"""
        if self.prop_under_mouse:
            pt = self.CalcUnscrolledPosition(evt.GetPosition())
            # pass the event to the property
            self.prop_under_mouse.OnMouseUp(pt)
            self.prop_under_mouse = None

        if self.GetCapture() == self:
            self.ReleaseMouse()

        # finish resizing
        self.pos_mouse_down = wx.Point(0, 0)
        self.resize_mode = self.RESIZE_NONE

        # finish drag & drop
        PropGrid.drag_prop = None
        PropGrid.drag_state = 0
        PropGrid.drag_start = wx.Point(0, 0)

        evt.Skip()

    def OnMouseDoubleClick(self, evt):
        """double click"""
        pt = self.CalcUnscrolledPosition(evt.GetPosition())
        index = self.PropHitTest(pt)
        if index != -1:
            # pass the event to the property
            prop = self.GetProperty(index)
            prop.OnMouseDoubleClick(pt)

        evt.Skip()

    def OnMouseCaptureLost(self, evt):
        pass

    def OnMouseMove(self, evt):
        """mouse move"""
        pt = self.CalcUnscrolledPosition(evt.GetPosition())
        index = self.PropHitTest(pt)
        prop = None
        if index != -1:
            # pass the event to the property
            prop = self.GetProperty(index)
            prop.OnMouseMove(pt)
        # drag & drop
        if evt.LeftIsDown() and PropGrid.drag_prop and\
           PropGrid.drag_state == 1:
            pt = self.ClientToScreen(pt)
            start = PropGrid.drag_start
            if (start.x-pt.x)**2+(start.y-pt.y)**2 > 10:
                if self.SendPropEvent(wxEVT_PROP_BEGIN_DRAG, self.drag_prop):
                    # the mouse is moved, so start drag & drop
                    PropGrid.drag_state = 2
                    PropGrid.drag_pg = self
                    # start drag operation
                    propData = wx.TextDataObject(PropGrid.drag_prop.GetName())
                    source = wx.DropSource(PropGrid.drag_pg)
                    source.SetData(propData)

                    rtn = source.DoDragDrop(True)
                    if rtn == wx.DragError:
                        wx.LogError("An error occurred during drag \
                                     and drop operation")
                    elif rtn == wx.DragNone:
                        pass
                    elif rtn == wx.DragCopy:
                        pass
                    elif rtn == wx.DragMove:
                        pass
                    elif rtn == wx.DragCancel:
                        pass
                    PropGrid.drag_state = 0
                    PropGrid.drag_pg = None

        if evt.LeftIsDown() and self.prop_under_mouse:
            # resize the property
            if self.resize_mode == self.RESIZE_SEP:
                # resize the title width for all properties
                self.title_width = max(evt.GetX(), 50)
                self.Refresh(False)
            elif self.resize_mode == self.RESIZE_BOT:
                # change the height for the property
                sz = self.prop_under_mouse.GetMinSize()
                sz2 = wx.Size(sz.x, sz.y)
                sz.y += (pt.y- self.pos_mouse_down.y)
                sz.y = max(sz.y, 25)
                if sz.y != sz2.y:
                    self.pos_mouse_down.x, self.pos_mouse_down.y = pt.x, pt.y
                    self.prop_under_mouse.SetMinSize(sz)
            else:
                self.prop_under_mouse.OnMouseMove(pt)
        else:
            if not evt.IsButton():
                # no button is pressed, show the tooltip
                tooltip = ""
                mode = self.CURSOR_STD

                if prop:
                    #pass the event to the property
                    ht = prop.OnMouseMove(pt)

                    # change the cursor icon
                    if ht == PROP_HIT_SPLITTER:
                        mode = self.CURSOR_RESIZE_HORZ
                    elif ht == PROP_HIT_EDGE_BOTTOM:
                        mode = self.CURSOR_RESIZE_VERT
                    elif ht == PROP_HIT_EDGE_TOP:
                        if index > 0:
                            mode = self.CURSOR_RESIZE_VERT
                        else:
                            mode = self.CURSOR_STD
                    #if prop.GetShowLabelTips() and ht == Property.PROP_HIT_TITLE:
                    if ht == PROP_HIT_TITLE:
                        tooltip = prop.GetLabelTip()
                    elif prop.GetShowValueTips() and ht == PROP_HIT_VALUE:
                        tooltip = prop.GetValueTip()
                    elif ht == PROP_HIT_EXPAND:
                        tooltip = prop.GetLabelTip()
                # set the tooltip
                if self.GetToolTipText() != tooltip:
                    self.SetToolTip(tooltip)
                # set the cursor
                if mode != self.cursor_mode:
                    self.cursor_mode = mode
                    if mode == self.CURSOR_RESIZE_HORZ:
                        self.SetCursor(self.resize_cursor_horz)
                    elif mode == self.CURSOR_RESIZE_VERT:
                        self.SetCursor(self.resize_cursor_vert)
                    else:
                        self.SetCursor(wx.NullCursor)
        evt.Skip()

    def OnMouseLeave(self, evt):
        """mouse leaves the window"""
        self.SetCursor(wx.NullCursor)
        evt.Skip()

    def OnMouseRightClick(self, evt):
        """right click"""
        pt = self.CalcUnscrolledPosition(evt.GetPosition())
        index = self.PropHitTest(pt)
        # set the active property
        self.SetSelection(index)
        if index != -1:
            # pass the event to the property
            prop = self.GetProperty(index)
            prop.OnMouseRightClick(pt)

    def OnDrop(self, x, y, name):
        """drop the property"""
        pt = wx.Point(x, y)
        pt = self.CalcUnscrolledPosition(pt)
        index2 = self.PropHitTest(pt)
        prop = self.GetProperty(index2)
        # insert a property? Let the parent to determine what to do
        if PropGrid.drag_prop == None:
            dp.send('prop.drop', index=index2, prop=name, grid=self)
            return

        if name != PropGrid.drag_prop.GetName():
            # something is wrong
            return

        index = PropGrid.drag_pg.FindPropertyIndex(PropGrid.drag_prop)
        if index == -1:
            # not find the dragged property, do nothing
            return

        if PropGrid.drag_pg != self:
            # drop the property from the other window, copy it
            indent = PropGrid.drag_prop.GetIndent()
            self.CopyProperty(PropGrid.drag_prop, index2)
            for i in six.moves.range(index+1, PropGrid.drag_pg.GetPropCount()):
                # copy all its children
                child = PropGrid.drag_pg.GetProperty(i)
                if child.GetIndent() <= indent:
                    break
                if index2 != -1:
                    index2 = index2 + 1
                self.CopyProperty(child, index2)
        else:
            # move the property if necessary
            if prop == PropGrid.drag_prop:
                return
            self.doMoveProperty(index, index2)
        self.UpdateGrid()

class PropSettings(wx.Dialog):
    def __init__(self, parent, prop):
        wx.Dialog.__init__(self, parent, title="Settings...",
                           size=wx.Size(402, 494),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.propgrid = PropGrid(self)
        self.prop = prop
        if prop.GetSeparator():
            self.items = (('name', 'Name', '', PROP_CTRL_EDIT),
                          ('label', 'Label', '', PROP_CTRL_EDIT),
                          ('indent', 'Indent level', '', PROP_CTRL_SPIN),
                          ('italic', 'Italic', '', PROP_CTRL_CHECK))
        else:
            self.items = (('name', 'Name', '', PROP_CTRL_EDIT),
                          ('label', 'Label', '', PROP_CTRL_EDIT),
                          ('value', 'Value', '', PROP_CTRL_EDIT),
                          ('description', 'Description', 'text shown next to the value',
                           PROP_CTRL_EDIT),
                          ('value_max', 'Max value', '', PROP_CTRL_SPIN),
                          ('value_min', 'Min value', '', PROP_CTRL_SPIN),
                          ('indent', 'Indent level', '', PROP_CTRL_SPIN),
                          ('show_check', 'Show check icon', '', PROP_CTRL_CHECK),
                          ('enable', 'Enable', '', PROP_CTRL_CHECK),
                          ('italic', 'Italic', '', PROP_CTRL_CHECK),
                          ('readonly', 'Read only', '', PROP_CTRL_CHECK),
                          ('ctrl_type', 'Control window type', '', PROP_CTRL_CHOICE),
                          ('choices', 'Choice list', '', PROP_CTRL_EDIT),
                          ('text_clr', 'Normal text color', '', PROP_CTRL_COLOR),
                          ('text_clr_sel', 'Selected text color', '', PROP_CTRL_COLOR),
                          ('text_clr_disabled', 'Disable text color', '', PROP_CTRL_COLOR),
                          ('bg_clr', 'Normal background color', '', PROP_CTRL_COLOR),
                          ('bg_clr_sel', 'Selected background color', '', PROP_CTRL_COLOR),
                          ('bg_clr_disabled', 'Disable background color', '', PROP_CTRL_COLOR))

        for (name, label, tip, ctrl) in self.items:
            pp = self.propgrid.InsertProperty(name, label, '')
            if prop:
                v = getattr(prop, name)
            else:
                v = ""
            pp.SetLabelTip(label)
            pp.SetValueTip(tip)
            pp.SetControlStyle(ctrl)
            if name == 'ctrl_type':
                choices = {'none':PROP_CTRL_NONE,
                           'editbox':PROP_CTRL_EDIT, 'choice':PROP_CTRL_CHOICE,
                           'select file':PROP_CTRL_FILE_SEL,
                           'select folder':PROP_CTRL_FOLDER_SEL,
                           'slider':PROP_CTRL_SLIDER, 'spin':PROP_CTRL_SPIN,
                           'checkbox':PROP_CTRL_CHECK, 'radio button':PROP_CTRL_RADIO,
                           'colorpicker':PROP_CTRL_COLOR}
                pp.SetChoices(choices)
                pp.SetValue(v)
            if name in ['choices']:
                pp.SetValue(json.dumps(v))
            elif ctrl == PROP_CTRL_CHECK:
                pp.SetValue(v)
            elif ctrl == PROP_CTRL_COLOR:
                pp.SetValue(v)
                pp.SetBgColor(v, v, v)
                t = wx.Colour(v)
                t.SetRGB(t.GetRGB()^0xffffff)
                t = t.GetAsString(wx.C2S_HTML_SYNTAX)
                pp.SetTextColor(t, t, t)
            elif ctrl in [PROP_CTRL_SPIN, PROP_CTRL_SLIDER]:
                pp.SetRange(-2**31-1, 2**31)
                pp.SetValue(v)
            else:
                pp.SetValue(v)
            pp.SetShowCheck(False)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.propgrid, 1, wx.EXPAND | wx.ALL, 1)

        self.stcline = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        sz.Add(self.stcline, 0, wx.EXPAND | wx.ALL, 5)

        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        sz2.Add(wx.Button(self, wx.ID_OK, u"&Ok"), 0, wx.ALL, 5)
        sz2.Add(wx.Button(self, wx.ID_CANCEL, u"&Cancel"), 0, wx.ALL, 5)
        sz.Add(sz2, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)

        self.SetSizer(sz)
        self.Layout()

        # Connect Events
        self.Bind(wx.EVT_BUTTON, self.OnBtnOk, id=wx.ID_OK)
        self.Bind(EVT_PROP_RIGHT_CLICK, self.OnPropEventsHandler)

    def OnPropEventsHandler(self, evt):
        # disable context menu
        evt.Veto()

    def OnBtnOk(self, event):
        if self.propgrid.prop_selected:
            # update the value if necessary
            self.propgrid.prop_selected.OnTextEnter()

        for (name, _, _, ctrl) in self.items:
            v = self.propgrid.GetProperty(name)
            if name in ['choices']:
                self.prop.SetChoices(json.loads(v.GetValue()))
            elif ctrl == PROP_CTRL_CHECK:
                setattr(self.prop, name, bool(int(v.GetValue())))
            elif name == 'ctrl_type':
                self.prop.SetControlStyle(int(v.GetValue()))
            else:
                setattr(self.prop, name, type(getattr(self.prop, name))(v.GetValue()))
        event.Skip()
