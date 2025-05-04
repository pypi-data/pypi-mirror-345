import wx  # type: ignore

from GooeyEx.gui import formatters
from GooeyEx.gui.components.widgets.bases import TextContainer
from GooeyEx.python_bindings import types as t


class Slider(TextContainer):
    """
    An integer input field
    """

    widget_class = wx.Slider

    def getWidget(self, *args, **options):
        widget = self.widget_class(
            self,
            minValue=self._options.get("min", 0),
            maxValue=self._options.get("max", 100),
            style=wx.SL_MIN_MAX_LABELS | wx.SL_VALUE_LABEL,
        )
        return widget

    def getWidgetValue(self):
        return self.widget.GetValue()

    def setValue(self, value):
        self.widget.SetValue(value)

    def formatOutput(self, metatdata, value):
        return formatters.general(metatdata, str(value))

    def getUiState(self) -> t.FormField:
        widget: wx.Slider = self.widget
        return t.Slider(
            id=self._id,
            type=self.widgetInfo["type"],
            value=self.getWidgetValue(),
            min=widget.GetMin(),
            max=widget.GetMax(),
            error=self.error.GetLabel() or None,
            enabled=self.IsEnabled(),
            visible=self.IsShown(),
        )
