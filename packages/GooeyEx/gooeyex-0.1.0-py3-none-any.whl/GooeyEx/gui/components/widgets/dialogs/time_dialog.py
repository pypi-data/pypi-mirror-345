from .base_dialog import BaseDialog
from GooeyEx.gui.three_to_four import Classes
from GooeyEx.gui.lang.i18n import _


class TimeDlg(BaseDialog):
    def __init__(self, parent):
        super(TimeDlg, self).__init__(
            parent,
            pickerClass=Classes.TimePickerCtrl,
            pickerGetter=lambda datepicker: datepicker.GetValue().FormatISOTime(),
            localizedPickerLabel=_("select_time"),
        )
