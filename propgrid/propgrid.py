import sys
import traceback
import math
import six
import wx
import wx.py.dispatcher as dp
from .prop import *
from .propart import PropArtNative

wxEVT_PROP_INSERT = wx.NewEventType()
wxEVT_PROP_DELETE = wx.NewEventType()

EVT_PROP_INSERT = wx.PyEventBinder(wxEVT_PROP_INSERT, 1)
EVT_PROP_DELETE = wx.PyEventBinder(wxEVT_PROP_DELETE, 1)

class PropDropTarget(wx.DropTarget):
    def __init__(self, frame):
        wx.DropTarget.__init__(self)
        self.obj = wx.TextDataObject()
        self.SetDataObject(self.obj)
        self.frame = frame
        self.SetDefaultAction(wx.DragMove)

    def OnEnter(self, x, y, d):
        self.frame.OnEnter(x, y, d)
        return d

    def OnLeave(self):
        self.frame.OnLeave()

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone
        self.frame.OnDrop(x, y, self.obj.GetText())

        return d

    def OnDragOver(self, x, y, d):
        self.frame.OnDragOver(x, y, d)
        return d


class PropGrid(wx.ScrolledWindow):
    ID_PROP_GRID_ADD_SEP = wx.NewIdRef()
    ID_PROP_GRID_READ_ONLY = wx.NewIdRef()
    ID_PROP_GRID_INDENT_INS = wx.NewIdRef()
    ID_PROP_GRID_INDENT_DES = wx.NewIdRef()
    ID_PROP_GRID_MOVE_UP = wx.NewIdRef()
    ID_PROP_GRID_MOVE_DOWN = wx.NewIdRef()
    ID_PROP_GRID_DELETE = wx.NewIdRef()
    ID_PROP_GRID_PROP = wx.NewIdRef()

    drag_state = 0
    drag_start = wx.Point(0, 0)
    drag_prop = None
    drag_pg = None

    RESIZE_NONE = 0
    RESIZE_SEP = 1
    RESIZE_BOT = 2

    SCROLL_UNIT = 15

    CURSOR_RESIZE_HORZ = 0
    CURSOR_RESIZE_VERT = 1
    CURSOR_STD = 2

    def __init__(self, frame):
        wx.ScrolledWindow.__init__(self, frame)

        self.prop_selected = None
        self.cursor_mode = self.CURSOR_STD
        self.pos_mouse_down = wx.Point(0, 0)
        self.prop_under_mouse = None
        self.resize_mode = self.RESIZE_NONE

        self._props = []
        self._art = PropArtNative()

        # cursor
        self.resize_cursor_horz = wx.Cursor(wx.CURSOR_SIZEWE)
        self.resize_cursor_vert = wx.Cursor(wx.CURSOR_SIZENS)

        # set scroll parameters
        self.SetScrollRate(self.SCROLL_UNIT, self.SCROLL_UNIT)
        self.SetVirtualSize(wx.Size(100, 200))

        self.SetDropTarget(PropDropTarget(self))
        self.draggable = True
        self.configurable = True

        self.drag_image = None
        self.drag_bitmap = None

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
        self.Bind(wx.EVT_MOUSE_CAPTURE_CHANGED, self.OnMouseCaptureLost)

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
        self.Bind(wx.EVT_MENU, self.OnProcessCommand)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

    def CreateDragImage(self, prop):
        memory = wx.MemoryDC(wx.Bitmap(1, 1))

        w, h = prop.GetSize()
        w = min(500, w-100)

        scale_factor = self.GetContentScaleFactor()
        bitmap = wx.Bitmap(w*scale_factor, h*scale_factor)
        bitmap.SetScaleFactor(scale_factor)
        memory.SelectObject(bitmap)

        memory.Clear()
        p = prop.duplicate()
        p.SetGrid(self)
        p.top_value_border = True
        p.bottom_value_border = True
        p.activated = True
        p.SetRect(wx.Rect(0, 0, w, h))
        self._art.DrawItem(memory, p)

        memory.SelectObject(wx.NullBitmap)

        return bitmap

    def SetArtProvider(self, art):
        self._art = art
        self.Refresh()

    def GetArtProvider(self):
        return self._art

    def Draggable(self, draggable):
        """set if it is allow to drag/drop any prop"""
        self.SetDraggable(draggable)
        return self

    def SetDraggable(self, draggable):
        """set if it is allow to drag/drop any prop"""
        self.draggable = draggable

    def IsDraggable(self):
        """get if it is allow to drag/drop any prop"""
        return self.draggable

    def Configurable(self, configurable):
        """set if it is allow to drag/drop any prop"""
        self.SetConfigurable(configurable)
        return self

    def SetConfigurable(self, configurable):
        """set if it is allow to drag/drop any prop"""
        self.configurable = configurable

    def IsConfigurable(self):
        """get if it is allow to drag/drop any prop"""
        return self.configurable

    def Append(self, prop, update=True):
        return self.Insert(prop, -1, update)

    def Insert(self, prop, index=-1, update=True):
        # add the prop window to the grid
        if not isinstance(prop, PropBase):
            return None

        prop.Grid(self)
        if index == -1 or index >= self.GetCount():
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

    def CopyProp(self, prop, index=-1, update=True):
        if not isinstance(prop, PropBase):
            return None
        p = prop.duplicate()
        p.SetGrid(self)
        p.Activated(False)
        return self.Insert(p, index, update)

    def Remove(self, prop, update=True):
        # remove property
        if isinstance(prop, six.string_types) or isinstance(prop, PropBase):
            index = self.Index(prop)
        elif isinstance(prop, int):
            index = prop
        else:
            return False

        if index >= 0 and index < self.GetCount():
            prop = self._props[index]
            activated = False
            if prop == self.prop_selected:
                activated = True
                self.SetSelection(-1)
            del self._props[index]

            if index != -1 and (not update):
                self.CheckProp()
            if index >= self.GetCount():
                index = self.GetCount() - 1

            if activated:
                self.SetSelection(index)
            if update:
                self.UpdateGrid()
            return True
        return False

    def DeleteAll(self, update=True):
        for i in range(len(self._props) - 1, -1, -1):
            self.Delete(self._props[i], update)

    def Delete(self, prop, update=True):
        if self.SendPropEvent(wxEVT_PROP_DELETE, prop):
            dp.send('prop.delete', prop=prop)
            return self.Remove(prop, update)
        else:
            return False

    def Index(self, prop):
        """return the index of prop, or -1 if not found"""
        p = self.Get(prop)
        if not p:
            return -1
        try:
            idx = self._props.index(p)
            return idx
        except ValueError:
            traceback.print_exc(file=sys.stdout)
        return -1

    def Get(self, prop):
        """return the prop instance"""
        if isinstance(prop, PropBase):
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
            if index >= 0 and index < self.GetCount():
                return self._props[index]
        return None

    def GetCount(self):
        """return the number of properties"""
        return len(self._props)

    def GetScrolledRect(self, rc):
        (x, y) = self.GetViewStart()
        rcs = wx.Rect(*rc)
        rcs.Offset(wx.Point(-x * self.SCROLL_UNIT, -y * self.SCROLL_UNIT))
        return rcs

    def EnsureVisible(self, prop):
        """scroll the window to make sure prop is visible"""
        p = self.Get(prop)
        if not p:
            return
        rc_prop = p.GetRect()
        # translate to the scrolled position
        rc_prop.x, rc_prop.y = self.CalcScrolledPosition(rc_prop.x, rc_prop.y)
        _, y = self.GetViewStart()
        rc = self.GetClientRect()
        if rc.top < rc_prop.top and rc.bottom > rc_prop.bottom:
            # if the prop is visible, simply return
            return
        if rc.top > rc_prop.top:
            # if the prop is on top of the client window, scroll up
            y = y + math.floor((rc_prop.top - rc.top) / self.SCROLL_UNIT)
            self.Scroll(-1, y)
        elif rc.bottom < rc_prop.bottom:
            # if the prop is under bottom of the client window, scroll down
            y = y + math.ceil((rc_prop.bottom - rc.bottom) / self.SCROLL_UNIT)
            self.Scroll(-1, y)

    def GetSelection(self):
        """get the index of the selected property"""
        return self.Index(self.prop_selected)

    def GetSelected(self):
        """return the selected property"""
        return self.prop_selected

    def SetSelection(self, prop):
        """set the active property"""
        p = self.Get(prop)
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
        index = self.Index(prop)
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
        if index2 < self.GetCount():
            self.doMoveProperty(index, index2)
        else:
            self.doMoveProperty(index, -1)

    def doMoveProperty(self, index, index2):
        """move the property"""
        # the same position, ignore it
        if index == index2:
            return

        prop = self.Get(index)
        props = [prop]
        if prop.HasChildren() and (not prop.IsExpanded()):
            # move all the children if they are not visible
            indent = prop.GetIndent()
            for i in six.moves.range(index + 1, self.GetCount()):
                if self._props[i].GetIndent() <= indent:
                    break
                props.append(self._props[i])

        i = 0
        for p in props:
            if index2 == -1:
                self._props.append(p)
            else:
                #insert it before index2
                self._props.insert(index2 + i, p)
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
        prop = self.Get(prop)
        # prepare the event
        if isinstance(event, PropEvent):
            evt = event
        elif isinstance(event, int):
            evt = PropEvent(event, prop)
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

            if sel < 0 or sel >= self.GetCount():
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
            if not prop.IsVisible():
                continue
            if prop.GetRect().Contains(pt):
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
                p.SetRect(wx.Rect(0, y, w, h))
                # let art provider update drawing regions (e.g., value rect)
                self._art.PrepareDrawRect(p)
                y += h
        prev_prop = None
        for p in self._props:
            if not  p.IsVisible():
                continue
            p.top_value_border = False
            if prev_prop is None or prev_prop.IsSeparator() or p.IsSeparator():
                p.top_value_border = True
            prev_prop = p

        next_prop = None
        for p in reversed(self._props):
            if not  p.IsVisible():
                continue
            p.bottom_value_border = False
            if next_prop is None or next_prop.IsSeparator() or p.IsSeparator():
                p.bottom_value_border = True
            next_prop = p

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
            parent = self.Get(i - 1)
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
        self.SendPropEvent(evt.GetEventType(), evt.GetProp())
        prop = evt.GetProp()
        if prop is None:
            return
        rc = prop.GetRect()
        rc.x, rc.y = self.CalcScrolledPosition(rc.x, rc.y)
        self.RefreshRect(rc, True)

    def GetContextMenu(self, prop):
        # show the context menu
        menu = wx.Menu()
        menu.Append(self.ID_PROP_GRID_ADD_SEP, "&Add separator")
        menu.AppendCheckItem(self.ID_PROP_GRID_READ_ONLY, "&Read only")
        menu.Check(self.ID_PROP_GRID_READ_ONLY, prop.IsReadonly())

        menu.AppendSeparator()
        menu.Append(self.ID_PROP_GRID_INDENT_INS,
                    "Increase Indent\tCtrl-Right")
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
        if not self.SendPropEvent(evt.GetEventType(), evt.GetProp()):
            # vetoed by parent, ignore the event
            return False

        eid = evt.GetEventType()
        if eid in [
                wxEVT_PROP_COLLAPSED, wxEVT_PROP_EXPANDED, wxEVT_PROP_INDENT,
                wxEVT_PROP_RESIZE
        ]:
            self.UpdateGrid()
        elif eid == wxEVT_PROP_RIGHT_CLICK:
            prop = evt.GetProp()
            if self.IsConfigurable() and prop.IsConfigurable():
                # show configuration menu
                menu = self.GetContextMenu(prop)
                cmd = self.GetPopupMenuSelectionFromUser(menu)
                self.OnProcessCommand(cmd, prop)
        return True

    def OnProcessCommand(self, eid, prop):
        """process the context menu command"""
        if not prop:
            return

        if eid == self.ID_PROP_GRID_DELETE:
            self.Delete(prop)
        elif eid == self.ID_PROP_GRID_READ_ONLY:
            prop.SetReadonly(not prop.IsReadonly())
        elif eid == self.ID_PROP_GRID_PROP:
            dlg = PropSettings(self, prop)
            if dlg.ShowModal() == wx.ID_OK:
                # Update the prop only may not be enough, for example, if its
                # indent is changed, it may affect the previous prop.
                self.UpdateGrid()
        elif eid == self.ID_PROP_GRID_INDENT_INS:
            prop.SetIndent(prop.GetIndent() + 1)
        elif eid == self.ID_PROP_GRID_INDENT_DES:
            prop.SetIndent(prop.GetIndent() - 1)
        elif eid == self.ID_PROP_GRID_MOVE_UP:
            self.MoveProperty(prop, -1)
        elif eid == self.ID_PROP_GRID_MOVE_DOWN:
            self.MoveProperty(prop, 2)
        elif eid == self.ID_PROP_GRID_ADD_SEP:
            idx = self.Index(prop)
            sep = PropSeparator().Label('Separator')
            self.Insert(sep, idx+1)

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
                    prop.SetIndent(indent - 1)
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
                    prop.SetIndent(indent + 1)
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
                self.Remove(self.GetSelected())
            else:
                skip = True
        if skip:
            evt.Skip()

    def OnPaint(self, event):
        """draw the property"""
        dc = wx.AutoBufferedPaintDC(self)
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
            rc_prop = p.GetRect()
            if rc.Intersects(rc_prop):
                self._art.DrawItem(dc, p)
                p.PostRefresh()

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
            prop = self.Get(index)

            # pass the event to the property
            ht = prop.OnMouseDown(pt)
            self.prop_under_mouse = prop
            self._set_capture(True)
            self.resize_mode = self.RESIZE_NONE
            if ht == 'splitter':
                # drag the splitter
                self.resize_mode = self.RESIZE_SEP
            elif ht == 'bottom_edge':
                # drag the bottom edge
                self.resize_mode = self.RESIZE_BOT
            elif ht == 'top_edge':
                # drag the bottom edge of the property above
                if index > 0:
                    index = index - 1
                    self.prop_under_mouse = self.Get(index)
                    self.resize_mode = self.RESIZE_BOT
            elif ht == 'label' or ht is None:
                # start drag & drop
                if self.IsDraggable() and prop.IsDraggable():
                    PropGrid.drag_start = self.ClientToScreen(pt)
                    PropGrid.drag_prop = prop
                    PropGrid.drag_pg = self
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

        self._set_capture(False)

        # finish resizing
        self.pos_mouse_down = wx.Point(0, 0)
        self.resize_mode = self.RESIZE_NONE

        if PropGrid.drag_state == 1:
            # cancel drag
            PropGrid.drag_start = wx.Point(0, 0)
            PropGrid.drag_prop = None
            PropGrid.drag_pg = None
            PropGrid.drag_state = 0
        evt.Skip()

    def _set_capture(self, capture=True):
        """Control wx mouse capture."""
        if self.HasCapture():
            self.ReleaseMouse()
        if capture:
            self.CaptureMouse()

    def OnMouseDoubleClick(self, evt):
        """double click"""
        pt = self.CalcUnscrolledPosition(evt.GetPosition())
        index = self.PropHitTest(pt)
        if index != -1:
            # pass the event to the property
            prop = self.Get(index)
            prop.OnMouseDoubleClick(pt)

        evt.Skip()

    def OnMouseCaptureLost(self, evt):
        self._set_capture(False)

    def OnMouseMove(self, evt):
        """mouse move"""
        pt = self.CalcUnscrolledPosition(evt.GetPosition())
        index = self.PropHitTest(pt)
        prop = None
        if index != -1:
            # pass the event to the property
            prop = self.Get(index)
            prop.OnMouseMove(pt)

        # drag & drop
        if evt.LeftIsDown() and PropGrid.drag_prop  and PropGrid.drag_pg == self and\
           PropGrid.drag_state == 1:
            pt = self.ClientToScreen(pt)
            start = PropGrid.drag_start

            drag_x_threshold = max(10, wx.SystemSettings.GetMetric(wx.SYS_DRAG_X))
            drag_y_threshold = max(4, wx.SystemSettings.GetMetric(wx.SYS_DRAG_Y))
            if abs(start.x - pt.x) > drag_x_threshold or abs(start.y - pt.y) > drag_y_threshold:
                if self.SendPropEvent(wxEVT_PROP_BEGIN_DRAG, self.drag_prop):
                    # the mouse is moved, so start drag & drop
                    PropGrid.drag_state = 2
                    # start drag operation
                    self._set_capture(False)
                    propData = wx.TextDataObject(PropGrid.drag_prop.GetName())
                    source = wx.DropSource(PropGrid.drag_pg)
                    source.SetData(propData)
                    rtn = source.DoDragDrop(wx.Drag_AllowMove)
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
                    # finish drag & drop
                    PropGrid.drag_prop = None
                    PropGrid.drag_start = wx.Point(0, 0)
                    PropGrid.drag_state = 0
                    PropGrid.drag_pg = None

        if evt.LeftIsDown() and self.prop_under_mouse:
            # resize the property
            if self.resize_mode == self.RESIZE_SEP:
                # resize the title width for all properties
                self._art.SetTitleWidth(max(evt.GetX(), 50))
                self.Refresh(False)
            elif self.resize_mode == self.RESIZE_BOT:
                # change the height for the property
                sz = self.prop_under_mouse.GetMinSize()
                sz2 = wx.Size(sz.x, sz.y)
                sz.y += (pt.y - self.pos_mouse_down.y)
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
                    if ht == 'splitter':
                        mode = self.CURSOR_RESIZE_HORZ
                    elif ht == 'bottom_edge':
                        mode = self.CURSOR_RESIZE_VERT
                    elif ht == 'top_edge':
                        if index > 0:
                            mode = self.CURSOR_RESIZE_VERT
                        else:
                            mode = self.CURSOR_STD
                    if prop.GetShowLabelTips():
                        tooltip = prop.GetLabelTip()
                    elif prop.GetShowValueTips() and ht == 'value':
                        tooltip = prop.GetValueTip()
                    elif ht == 'expander':
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
            prop = self.Get(index)
            prop.OnMouseRightClick(pt)

    def doDrop(self, x, y, name):
        pt = wx.Point(x, y)
        pt = self.CalcUnscrolledPosition(pt)
        index2 = self.PropHitTest(pt)
        prop = self.Get(index2)
        # insert a property? Let the parent to determine what to do
        if PropGrid.drag_prop is None:
            dp.send('prop.drop', index=index2, prop=name, grid=self)
            return

        if name != PropGrid.drag_prop.GetName():
            # something is wrong
            return

        index = PropGrid.drag_pg.Index(PropGrid.drag_prop)
        if index == -1:
            # not find the dragged property, do nothing
            return

        if PropGrid.drag_pg != self:
            # drop the property from the other window, copy it
            indent = PropGrid.drag_prop.GetIndent()
            self.CopyProp(PropGrid.drag_prop, index2)
            for i in six.moves.range(index + 1,
                                     PropGrid.drag_pg.GetCount()):
                # copy all its children
                child = PropGrid.drag_pg.Get(i)
                if child.GetIndent() <= indent:
                    break
                if index2 != -1:
                    index2 = index2 + 1
                self.CopyProp(child, index2)
        else:
            # move the property if necessary
            if prop == PropGrid.drag_prop:
                return
            self.doMoveProperty(index, index2)
        self.UpdateGrid()

    def OnDrop(self, x, y, name):
        """drop the property"""
        self.OnLeave()
        self.doDrop(x, y, name)

    def OnDragOver(self, x, y, d):
        pt = wx.Point(x, y)
        rc = self.GetClientRect()
        if rc.Contains(pt):
            (x, y) = self.GetViewStart()
            if pt.y < 15:
                self.Scroll(-1, y - (15 - pt.y) / 3)
            if pt.y > rc.bottom - 15:
                self.Scroll(-1, y - (rc.bottom - 15 - pt.y) / 3)

        if self.drag_image:
            self.drag_image.Hide()
        if PropGrid.drag_prop and PropGrid.drag_pg == self:
            # only do drop if we are moving the prop in the same propgrid;
            # it is more complicated if moved from another propgrid (e.g.,
            # first moved in, insert prop, then move; if mouse moves away, delete)
            self.doDrop(pt.x, pt.y, PropGrid.drag_prop.GetName())
        if self.drag_image:
            self.drag_image.Move(pt)
            self.drag_image.Show()

    def OnEnter(self, x, y, d):
        if self.HasCapture():
            self.ReleaseMouse()
        self.OnLeave()
        if PropGrid.drag_prop:
            if wx.Platform == "__WXMAC__":
                # not work on GTK3
                self.drag_bitmap = self.CreateDragImage(PropGrid.drag_prop)
                self.drag_image = wx.DragImage(self.drag_bitmap)
                self.drag_image.BeginDrag(wx.Point(0,0), self)
                self.drag_image.Move(wx.Point(x, y))
                self.drag_image.Show()

    def OnLeave(self):
        if self.drag_image:
            self.drag_image.Hide()
            self.drag_image.EndDrag()
            self.drag_image = None

class PropSettings(wx.Dialog):
    def __init__(self, parent, prop):
        wx.Dialog.__init__(self,
                           parent,
                           title="Settings...",
                           size=wx.Size(600, 460),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.propgrid = PropGrid(self).Configurable(False)
        self.propgrid.Draggable(False)
        self.propgrid.GetArtProvider().SetTitleWidth(200)
        self.prop = prop
        if prop.IsSeparator():
            self.items = (('name', PropText().Label('Name'), ''),
                          ('label', PropText().Label('Label'), ''),
                          ('indent',PropSpin(0, 100).Label('Indent level'), ''),
                          ('font_label', PropFont().Label('Label font'), '_font_label'),
                          ('font_value', PropFont().Label('Value font'), '_font_value'))
        else:
            self.items = (('name', PropText('Name'), ''),
                          ('label', PropText('Label'), ''),
                          ('indent', PropSpin(0, 100, 'Indent level'), ''),
                          ('enable', PropCheckBox('Enable'), ''),
                          ('font_label', PropFont('Label font'), '_font_label'),
                          ('font_value', PropFont('Value font'), '_font_value'),
                          ('readonly', PropCheckBox('Read only'), ''),
                          ('text_clr', PropColor('Normal text color'), 'text_clr'),
                          ('text_clr_sel', PropColor('Selected text color'), 'text_clr_sel'),
                          ('text_clr_disabled', PropColor('Disable text color'), 'text_clr_disabled'),
                          ('bg_clr', PropColor('Normal background color'), 'bg_clr'),
                          ('bg_clr_sel', PropColor('Selected background color'), 'bg_clr_sel'),
                          ('bg_clr_disabled', PropColor('Disabled background color'), 'bg_clr_disabled'))

        for (name, pp, gname) in self.items:
            pp = self.propgrid.Insert(pp.Name(name))
            if prop:
                v = getattr(prop, name)
            else:
                v = ""
            if v is None and gname:
                v = getattr(prop.grid.GetArtProvider(), gname)

            pp.SetValue(v)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.propgrid, 1, wx.EXPAND | wx.ALL, 1)

        self.stcline = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        sz.Add(self.stcline, 0, wx.EXPAND | wx.ALL, 5)


        btnsizer = wx.StdDialogButtonSizer()
        btnsizer.AddStretchSpacer(1)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sz.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)

        self.SetSizer(sz)
        self.Layout()

        # Connect Events
        self.Bind(wx.EVT_BUTTON, self.OnBtnOk, id=wx.ID_OK)

    def OnBtnOk(self, event):
        if self.propgrid.prop_selected:
            # update the value if necessary
            self.propgrid.prop_selected.OnTextEnter()

        for (name, pp, _ ) in self.items:
            v = self.propgrid.Get(name)
            if isinstance(pp, PropCheckBox):
                setattr(self.prop, name, bool(int(v.GetValue())))
            if getattr(self.prop, name) is None:
                setattr(self.prop, name, v.GetValue())
            else:
                setattr(self.prop, name,
                        type(getattr(self.prop, name))(v.GetValue()))
        event.Skip()
