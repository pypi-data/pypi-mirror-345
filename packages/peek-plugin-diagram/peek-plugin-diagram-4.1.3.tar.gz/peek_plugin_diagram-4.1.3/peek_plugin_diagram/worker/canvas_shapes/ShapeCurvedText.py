from typing import Union

from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeText import ShapeText
from peek_plugin_diagram.worker.canvas_shapes.ShapeText import (
    TextHorizontalAlign,
)
from peek_plugin_diagram.worker.canvas_shapes.ShapeText import TextVerticalAlign


class ShapeCurvedText(ShapeBase):
    @staticmethod
    def textStyle(disp) -> DispTextStyleTable:
        return disp.get("fsl", DispTextStyleTable())

    @staticmethod
    def borderColor(disp) -> DispColorTable:
        return disp.get("bcl", DispColorTable())

    @staticmethod
    def color(disp) -> DispColorTable:
        return disp.get("cl", DispColorTable())

    @staticmethod
    def verticalAlign(disp) -> int:
        val = disp.get("va")

        if val == TextVerticalAlign.top:
            return TextVerticalAlign.top

        if val == TextVerticalAlign.bottom:
            return TextVerticalAlign.bottom

        return TextVerticalAlign.center

    @staticmethod
    def horizontalAlign(disp) -> int:
        val = disp.get("ha")

        if val == TextHorizontalAlign.left:
            return TextHorizontalAlign.left

        if val == TextHorizontalAlign.right:
            return TextHorizontalAlign.right

        return TextHorizontalAlign.center

    @staticmethod
    def rotation(disp) -> int:
        return disp.get("r")

    @staticmethod
    def text(disp) -> str:
        return disp.get("te", "")

    @staticmethod
    def height(disp) -> Union[int, None]:
        return disp.get("th", None)

    @staticmethod
    def horizontalStretch(disp) -> float:
        return disp.get("hs")

    @staticmethod
    def centerPointX(disp) -> float:
        return disp["g"][0]

    @staticmethod
    def centerPointY(disp) -> float:
        return disp["g"][1]

    @staticmethod
    def center(disp) -> Point:
        return Point(
            x=ShapeText.centerPointX(disp), y=ShapeText.centerPointY(disp)
        )

    @staticmethod
    def spacingBetweenTexts(disp) -> float:
        return disp.get("sbt")

    @staticmethod
    def geom(disp):
        return disp.get("g")
