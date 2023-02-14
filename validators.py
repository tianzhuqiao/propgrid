#    BaseValidator.py
#
#    ------------------------------------------------------------
#    Copyright 2004 by Samuel Reynolds. All rights reserved.
#
#    Permission to use, copy, modify, and distribute this software and its
#    documentation for any purpose and without fee is hereby granted,
#    provided that the above copyright notice appear in all copies and that
#    both that copyright notice and this permission notice appear in
#    supporting documentation, and that the name of Samuel Reynolds
#    not be used in advertising or publicity pertaining to distribution
#    of the software without specific, written prior permission.
#
#    SAMUEL REYNOLDS DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
#    INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
#    EVENT SHALL SAMUEL REYNOLDS BE LIABLE FOR ANY SPECIAL, INDIRECT, OR
#    CONSEQUENTIAL DAMAGES, OR FOR ANY DAMAGES WHATSOEVER RESULTING FROM
#    LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
#    NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
#    WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#    ------------------------------------------------------------

import sys
import traceback
import wx


class BaseValidator(wx.Validator):
    """
    Base class for validators that validate *attributes* of
    objects and provide two-way data transfer between those
    attributes and UI controls.

    BaseValidator has no knowledge of the specific
    type of widget to be validated. Responsibility for
    interacting with specific types of widgets is delegated
    to subclasses.

    Subclasses must implement the following methods:
        * _setControlValue(self, value)
                Set the value of control to the value provided.
        * _getControlValue(self)
                Return the value of control.
    Remaining logic is implemented in BaseValidator.


    CHAMELEON POWERS:

    To simplify use in an object-editor context (in which
    a single editor GUI is used to edit multiple objects
    of the same type), BaseValidator allows changing
    objects on the fly.

    For example, if references to field widgets are stored
    in a list self._fieldWidgets, the editor class could
    implement the following methods:

        def SetObject(self, editObject):
            "Set object for editing."
            self._editObject = editObject
            self._updateValidators()
            self.TransferDataToWindow()

        def _updateValidators(self):
            for wgt in self._fieldWidgets:
                validator = wgt.GetValidator()
                validator.SetObject(self._editObject)


    FORMATTERS

    BaseValidator uses Formatters for validation and
    two-way reformatting. A Formatter is aware of source data type,
    and handles translation between presentation representation and
    storage representation.

    A Formatter must provide the following interface methods:
        * format(stored_value)
                Format a value for presentation.
        * coerce(presentation_value)
                Convert a presentation-formatted value
                to a storage-formatted value (may include
                type conversion such as string->integer).
        * validate(presentation_value)
                Validate a presentation-formatted value.
                Return True if valid or False if invalid.

    If a formatter is assigned, the BaseValidator
    will call the formatter's format, coerce, and validate
    methods at appropriate points in its processing.

    With a formatter, there is no need of, for example,
    integer-aware entry fields. The formatter handles
    validation and conversion of the input value.
    """
    def __init__(self,
                 obj,
                 attr,
                 formatter=None,
                 required=True,
                 callback=None):
        super(BaseValidator, self).__init__()

        self.obj = obj
        self.attr = attr
        self.required = required
        self.formatter = formatter
        self.callback = callback

    def Clone(self):
        """
        Return a new validator for the same field of the same object.
        """
        return self.__class__(self.obj, self.attr, self.formatter,
                              self.required, self.callback)

    def SetObject(self, obj):
        """
        Set or change the object with which the validator interacts.

        Useful for changing objects when a single panel is used
        to edit a number of identical objects.
        """
        self.obj = obj

    def TransferToWindow(self):
        """
        Transfer data from validator to window.

        Delegates actual writing to destination widget to subclass
        via _setControlValue method.
        """
        try:
            if self.obj is None:
                # Nothing to do
                return True

            # Copy object attribute value to widget
            val = getattr(self.obj, self.attr)
            if val is None:
                val = ''
            if self.formatter:
                val = self.formatter.format(val)
            self._setControlValue(val)

            return True
        except:
            traceback.print_exc(file=sys.stdout)

        return False

    def TransferFromWindow(self):
        """
        Transfer data from window to validator.

        Delegates actual reading from destination widget to subclass
        via _getControlValue method.

        Only copies data if value is actually changed from attribute value.
        """
        try:
            if self.obj is None:
                # Nothing to do
                return True

            if not self.Validate(self.GetWindow()):
                return False

            # Get widget value
            val = self._getControlValue()

            # Check widget value against attribute value; only copy if changed
            # Get object attribute value
            old_val = getattr(self.obj, self.attr)
            if self.formatter:
                old_val = self.formatter.format(old_val)
            if val != old_val:
                if self.formatter:
                    val = self.formatter.coerce(val)
                setattr(self.obj, self.attr, val)

            return True
        except:
            traceback.print_exc(file=sys.stdout)

        return False

    def Validate(self, win):
        """
        Validate the contents of the given control.

        Default behavior: Anything goes.
        """
        valid = True
        try:
            val = self._getControlValue()
            if self.required and val == '':
                valid = False
            if valid and self.formatter:
                valid = self.formatter.validate(val)
            if self.callback:
                self.callback(self.obj, self.attr, val, self.required, valid)
        except:
            traceback.print_exc(file=sys.stdout)

        return valid

    def _setControlValue(self, value):
        """
        Set the value of the target control.

        Subclass must implement.
        """
        raise NotImplementedError('Subclass must implement _setControlValue')

    def _getControlValue(self):
        """
        Return the value from the target control.

        Subclass must implement.
        """
        raise NotImplementedError('Subclass must implement _getControlValue')


class TextValidator(BaseValidator):
    """
    Validator for TextCtrl widgets.
    """
    def __init__(self, *args, **kwargs):
        """ Standard constructor. """
        super(TextValidator, self).__init__(*args, **kwargs)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnKeyDown(self, event):
        event.Skip()
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        wx.CallAfter(self.Validate, textCtrl)

    def Validate(self, win):
        valid = super(TextValidator, self).Validate(win)
        try:
            if not valid:
                win.SetForegroundColour("red")
                win.Refresh()
            else:
                win.SetForegroundColour(wx.NullColour)
                win.Refresh()
        except:
            traceback.print_exc(file=sys.stdout)

        return valid

    def TransferToWindow(self):
        """
        Transfer data from validator to window.

        Delegates actual writing to destination widget to subclass
        via _setControlValue method.
        """
        if self.obj is None:
            # Clear the widget
            wgt = self.GetWindow()
            wgt.Clear()
            return True

        # Default behavior otherwise
        return super(TextValidator, self).TransferToWindow()

    def _setControlValue(self, value):
        """
        Set the value of the TextCtrl.
        """
        wgt = self.GetWindow()
        wgt.SetValue(value)

    def _getControlValue(self):
        """
        Return the value from the TextCtrl.
        """
        wgt = self.GetWindow()
        return wgt.GetValue()


class SelectorValidator(BaseValidator):
    """
    Validator for ControlWithItems widgets (ListBox, Choice).

    For wx.ListBox, assumes single-selection mode (wx.LB_SINGLE).
    """
    def __init__(self, obj, attr, formatter, *args, **kwargs):
        """ Standard constructor. """
        super(SelectorValidator, self).__init__(obj, attr, formatter, *args,
                                                **kwargs)

    def _getFieldOptions(self, name):
        """
        Return list of (id,label) pairs.
        """
        return self.formatter.validValues()

    def _setControlValue(self, value):
        """
        Set the value *and the options* of the control.
        By the time this is called, the value is already mapped for display.
        """
        wgt = self.GetWindow()
        # Get options (list of (id,value) pairs)
        options = self._getFieldOptions(self.attr)
        # Sort alphabetically
        options = [(opt[1], opt) for opt in options]
        #options.sort()
        options = [opt[1] for opt in options]
        # Replace selector contents
        wgt.Clear()
        for id, label in options:
            wgt.Append(label, id)

        # Set selection
        wgt.SetStringSelection(value)

    def _getControlValue(self):
        """
        Return the value from the TextCtrl.
        """
        wgt = self.GetWindow()
        return wgt.GetStringSelection()


class CheckListBoxValidator(BaseValidator):
    """
    Validator for CheckListBox widgets.
    """
    def __init__(self, obj, attr, formatter, *args, **kwargs):
        """ Standard constructor. """
        super(CheckListBoxValidator, self).__init__(obj, attr, formatter,
                                                    *args, **kwargs)

    ########## REQUIRED INTERFACE ##########

    def _getFieldOptions(self, name):
        """
        Return list of (id,label) pairs.
        """
        return self.formatter.validValues()

    def _setControlValue(self, value):
        """
        Set the value *and the options* of the control.
        By the time this is called, the value is already mapped for display.

        @param value:    Sequence of (value, label) pairs.
        """
        wgt = self.GetWindow()

        # Get options (list of (id,value) pairs)
        options = self._getFieldOptions(self.attr)
        # Sort alphabetically
        options = [(opt[1], opt) for opt in options]
        #options.sort()
        options = [opt[1] for opt in options]
        # Replace selector contents
        self._setControlOptions(options)

        # Set selection
        wgt._setControlSelections(value)

    def _getControlValue(self):
        """
        Return the value from the TextCtrl.

        Returns a list of client data values (not row indices).
        """
        wgt = self.GetWindow()
        selections = wgt.GetStringSelections()
        value = [wgt.GetClientData(idx) for idx in selections]
        return value

    ########## END REQUIRED INTERFACE ##########

    def _setControlOptions(self, options):
        """
        Set up or update control options.

        @param options:    Sequence of (id,label) pairs.
        """
        wgt = self.GetWindow()
        wgt.Clear()
        for id, label in options:
            wgt.Append(label, id)

    def _setControlSelections(self, value):
        """
        Select the specified items in the control, and unselect others.

        @param value:    Integer or sequence of integers representing
                        the data value(s) of item(s) to be selected.

                        If None or empty sequence, all currently-selected
                        items will be deselected.

                        Any items in value that are not found in the
                        control have no effect.
        """
        if value is None:
            value = tuple()
        elif not isinstance(value, (list, tuple)):
            value = (value, )

        wgt = self.GetWindow()
        for idx in range(0, wgt.GetCount()):
            item_data = wgt.GetClientData(idx)
            if item_data in value:
                if not wgt.IsChecked(idx):
                    wgt.Check(idx, True)
            else:
                if wgt.IsChecked(idx):
                    wgt.Check(idx, False)


class RadioBoxValidator(BaseValidator):
    """
    Validator for RadioBox widgets.
    """
    def __init__(self, obj, attr, formatter, *args, **kwargs):
        """ Standard constructor. """
        super(RadioBoxValidator, self).__init__(obj, attr, formatter, *args,
                                                **kwargs)

    def _setControlValue(self, value):
        """
        Set the value *and the options* of the control.
        By the time this is called, the value is already mapped for display.
        """
        wgt = self.GetWindow()
        wgt.SetSelection(wgt.FindString(value))

    def _getControlValue(self):
        """
        Return the value from the TextCtrl.
        """
        wgt = self.GetWindow()
        return wgt.GetString(wgt.GetSelection())


class SpinSliderValidator(BaseValidator):
    """
    Validator for wx.SpinCtrl and wx.Slider widgets.

    """
    def __init__(self, obj, attr, formatter, *args, **kwargs):
        """ Standard constructor. """
        super(SpinSliderValidator, self).__init__(obj, attr, formatter, *args,
                                                  **kwargs)

    def _setControlValue(self, value):
        """
        Set the value *and the options* of the control.
        By the time this is called, the value is already mapped for display.
        """
        wgt = self.GetWindow()
        # Get options (list of (id,value) pairs)
        max_val = 100
        min_val = 0
        if hasattr(self.formatter, 'max_val'):
            max_val = self.formatter.max_val
        if hasattr(self.formatter, 'min_val'):
            min_val = self.formatter.min_val
        wgt.SetMax(max_val)
        wgt.SetMin(min_val)
        wgt.SetValue(self.formatter.coerce(value))

    def _getControlValue(self):
        """
        Return the value from the TextCtrl.
        """
        wgt = self.GetWindow()
        return wgt.GetValue()
