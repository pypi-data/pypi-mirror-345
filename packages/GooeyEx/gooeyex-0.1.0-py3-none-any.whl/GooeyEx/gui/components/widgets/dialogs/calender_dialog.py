from .base_dialog import BaseDialog
from GooeyEx.gui.three_to_four import Classes
from GooeyEx.gui.lang.i18n import _


class CalendarDlg(BaseDialog):
    def __init__(self, parent):
        super(CalendarDlg, self).__init__(
            parent,
            pickerClass=Classes.DatePickerCtrl,
            pickerGetter=lambda datepicker: datepicker.GetValue().FormatISODate(),
            localizedPickerLabel=_("select_date"),
        )
