import pyecharts.options as opts
from pyecharts.charts import Line
from typing import Any, List, Optional
import numpy as np


__all__ = [
    "PEChart"
]


class PEChart:
    """"""
    def __init__(
            self,
            x: List[str],
            y: List[float],
            title: Optional[str] = None,
            sub_title: Optional[str] = None,
            width: Optional[str] = "680px",
            height: Optional[str] = "360px",
            q: Optional[List[float]] = None,
            show_tools_box: Optional[bool] = False,
            **kwargs: Any,
    ):
        """

        Args:
            x:
            y:
            title:
            sub_title:
            width:
            height:
            q:
            show_tools_box:
            **kwargs:
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.sub_title = sub_title
        self.show_tools_box = show_tools_box
        if q is None:
            self.q = [0.15, 0.5, 0.85]
        else:
            self.q = q

    def line_chart(self, ):
        """

        Returns:

        """
        min_ = round(min(self.y) - min(self.y) * 0.1, 2)
        max_ = round(max(self.y) + max(self.y) * 0.1, 2)
        pe_buy, pe_mid, pe_sell = np.quantile(self.y, self.q)
        markline_data = [
            opts.MarkLineItem(y=pe_buy),
            opts.MarkLineItem(y=pe_mid),
            opts.MarkLineItem(y=pe_sell)
        ]

        chart = Line(
            init_opts=opts.InitOpts(width=self.width, height=self.height)
        )
        chart.add_xaxis(self.x)
        chart.add_yaxis(
            "PE", self.y,
            areastyle_opts=opts.AreaStyleOpts(opacity=0.1),
            markline_opts=opts.MarkLineOpts(data=markline_data),
        )
        chart.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title, subtitle=self.sub_title),
            yaxis_opts=opts.AxisOpts(min_=min_, max_=max_),
            toolbox_opts=opts.ToolboxOpts(is_show=self.show_tools_box),
            datazoom_opts=[opts.DataZoomOpts(type_="inside", range_end=100)],
        )
        return chart

    def render(self, path: str):
        """

        Args:
            path:

        Returns:

        """
        chart = self.line_chart()
        chart.render(path)
