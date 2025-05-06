from dataclasses import dataclass
from typing import Optional, Tuple, Union


@dataclass
class GeoParameter:
    key: str
    label: str
    unit: str
    symbol: Optional[str] = None
    precision: Optional[int] = 1
    percentile_precision: Optional[int] = 2
    legend_: Optional[str] = None
    legend_group: Optional[str] = None
    axis_title: Optional[str] = None
    desc: Optional[str] = None
    equation: Optional[str] = None
    value: Optional[float] = None
    default_value: Optional[float] = None
    value_range: Optional[Tuple] = (None, None)
    axis_scaling_base: Optional[Union[bool, int]] = 2
    tabulator_type: Optional[str] = "number"
    tabulator_editor: Optional[str] = "number"
    tabulator_editor_params: Optional[dict] = None

    @property
    def title(self):
        return f"{self.label.capitalize()}".title()

    @property
    def plot_axis_title(self):
        axis_title = self.axis_title if self.axis_title is not None else self.label.capitalize()
        return f"{axis_title} ({self.unit})"

    @property
    def axis_dimension(self):
        return (self.key, self.label)

    @property
    def symbol_title(self):
        return f"{self.symbol} [{self.unit}]"

    @property
    def tooltip_label(self):
        return f"{self.symbol} ({self.unit})"

    @property
    def legend(self):
        return self.legend_ if self.legend_ else self.symbol

    @property
    def table_column_title(self):
        """Formatted title for Tabulator header"""
        return f"""
            <div class="flex flex-col items-start justify-center pb-2">
                <span class="!font-semibold !text-neutral-700 !text-[13px]">{self.symbol if self.symbol else self.label}</span>
                <span class="!font-light !text-neutral-600 !text-[13px]">[{self.unit}]</span>
            </div>"""

    @property
    def table_column_title_label(self):
        """Formatted title for Tabulator header"""
        return f"""
            <div class="flex flex-col items-start justify-center">
                <span class="font-semibold">{self.label}</span>
                <span class="font-light text-gray-900">[{self.unit}]</span>
            </div>"""

    def static_axis_title(self, symbol: bool = False):
        text_ = []
        label_ = f"\mathbf{{{self.label.capitalize()}}}"
        text_.append(label_)

        if symbol and self.label != self.symbol:
            symbol_ = f",  \mathbf{{{self.symbol}}}"
            text_.append(symbol_)

        unit_ = f"  ({self.unit})"
        text_.append(unit_)

        return f"${''.join(text_)}$".replace(" ", "\/").replace("%", "\%")

    @property
    def tabulator_column(self) -> dict:
        return {
            "field": self.key,
            "title": self.table_column_title,
            "type": self.tabulator_type,
            "editor": self.tabulator_editor,
            "editorParams": self.tabulator_editor_params,
            "titleDownload": f"{self.label} [{self.unit}]",
        }
