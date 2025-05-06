from __future__ import annotations
from itertools import combinations
from typing import Any, Callable

from TQS.TQSDwg import Dwg, Iterator

from pygeometry2d import XY, Arc, GeomUtils, Circle, Line, Polyline, BoundingBox

type TQSEntity = TQSLine|TQSText|TQSPolyline|TQSBlock|TQSCircle|TQSArc|TQSSmartObject|TQSCurve|TQSDimension|TQSSmartRebar|TQSSubstructure

class TQSElement():
    __slot__ = ["dwg", "addr", "type", "name", "_layer", "_style", "_color", "color_rgb", "in_block", "is_open_object", "in_xref", "level_lock", "captureable"]

    def __init__(self, iterator_element: Iterator):
        self.dwg: Dwg = iterator_element.m_dwg
        self.addr = iterator_element.GetElementReadPosition()
        self.type = iterator_element.itype
        self.name = iterator_element.elementName
        self._layer = iterator_element.level
        self._style = iterator_element.style
        self._color = iterator_element.color
        self.color_rgb = iterator_element.colorRGB
        self.in_block = bool(iterator_element.inBlock)
        self.is_open_object = bool(iterator_element.isOpenObject)
        self.in_xref = bool(iterator_element.inXref)
        self.level_lock =  bool(iterator_element.levelLock)
        self.captureable = bool(iterator_element.captureable)
    
    @property
    def layer(self):
        return self._layer
    
    @layer.setter
    def layer(self, new_level: int):
        self.dwg.edit.ModifyLevel(self.addr, new_level)
        self._layer = new_level
    
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, new_style: int):
        self.dwg.edit.ModifyStyle(self.addr, new_style)
        self._style = new_style
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, new_color: int):
        self.dwg.edit.ModifyColor(self.addr, new_color)
        self._color = new_color
    
    def move(self, vector: XY) -> TQSElement:
        self.dwg.edit.Move(self.addr, vector.x, vector.y)
        return self
    
    def delete(self):
        self.dwg.edit.Erase(self.addr)
    
    def recover(self):
        self.dwg.edit.Recover(self.addr)

    def bounding_box(self) -> BoundingBox:
        return None

    def mid_point(self) -> XY:
        if bb := self.bounding_box():
            return bb.mid
        
class TQSIterableElement(TQSElement):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        self.elements = TQSElementList()

    def __getitem__(self, index: int) -> TQSEntity:
        return self.elements[index]
    
    def __setitem__(self, index: int, item: Any):
        self.elements[index] = item

    def filter(self, include: dict[str, list] = None, exclude: dict[str, list] = None, filter_function: Callable[[TQSEntity], bool] = None) -> TQSElementList:
        return self.elements.filter(include, exclude, filter_function)

    def filter_layer(self, layer: int | list[int]) -> TQSElementList:
        return self.elements.filter_layer(layer)

    def filter_type(self, typ: type | list[type]) -> TQSElementList:
        return self.elements.filter_type(typ)
    
class TQSText(TQSElement):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        self._text = iterator_element.text
        self.height = iterator_element.textHeight
        self.angle = GeomUtils.deg_to_rad(iterator_element.textAngle)
        self.length = iterator_element.textLength
        self.width = self.length * self.height
        self.point = XY(iterator_element.x1, iterator_element.y1)
        self.end_point = self.point.offset(self.width, self.height).rotate(self.angle, self.point)
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, new_text: str):
        self.delete()
        self.addr = self.dwg.iterator.GetWritePosition()
        self.dwg.draw.Text(self.point.x, self.point.y, self.height, GeomUtils.rad_to_deg(self.angle), new_text)
        self._text = new_text

    def __repr__(self) -> str:
        return f"TQSText[{self.text}]"
    
    def bounding_box(self) -> BoundingBox:
        bottom_left = self.point
        bottom_right = self.point.offset(self.width, 0).rotate(self.angle, self.point)
        top_left = self.point.offset(0, self.height).rotate(self.angle, self.point)
        top_right = self.end_point

        return GeomUtils.get_min_max_point([top_left, top_right, bottom_left, bottom_right])

class TQSLine(TQSElement, Line):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        Line.__init__(self, iterator_element.x1, iterator_element.y1, iterator_element.x2, iterator_element.y2)
    def __repr__(self) -> str:
        return f"TQSLine[{self.start},{self.end}]"
    def bounding_box(self) -> BoundingBox:
        return GeomUtils.get_min_max_point([self.start, self.end])

class TQSPolyline(TQSElement, Polyline):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        Polyline.__init__(self, [XY(point[0], point[1]) for point in iterator_element.xy])
        self.is_filled = iterator_element.isFilled
    def __repr__(self) -> str:
        return f"TQSPolyline{self.points}"
    def bounding_box(self) -> BoundingBox:
        return GeomUtils.get_min_max_point(self.points)

class TQSCurve(TQSElement):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        self.points = [XY(point[0], point[1]) for point in iterator_element.xy]
        self.num_points = iterator_element.xySize
    def __repr__(self) -> str:
        return f"TQSCurve{self.points}"
    def bounding_box(self) -> BoundingBox:
        return GeomUtils.get_min_max_point(self.points)

class TQSArc(TQSElement, Arc):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        Arc.__init__(self, XY(iterator_element.xc, iterator_element.yc), 
                            iterator_element.radius, 
                            GeomUtils.deg_to_rad(iterator_element.startAngle), 
                            GeomUtils.deg_to_rad(iterator_element.endAngle))
    def __repr__(self) -> str:
        return f"TQSArc[{self.center}, {self.radius}, {self.start_angle}, {self.end_angle}]"
    def bounding_box(self) -> BoundingBox:
        return GeomUtils.get_min_max_point(self.arc.discretize(30))

class TQSCircle(TQSElement, Circle):
    def __init__(self, iterator_element: Iterator):
        TQSElement.__init__(self, iterator_element)
        Circle.__init__(self, XY(iterator_element.xc, iterator_element.yc), iterator_element.radius * 2)
    
    def __repr__(self) -> str:
        return f"TQSCircle[{self.center}, {self.diameter}]"
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.center.offset(-self.radius, -self.radius), self.center.offset(self.radius, self.radius))

class TQSBlock(TQSIterableElement):
    def __init__(self, iterator_element: Iterator):
        TQSIterableElement.__init__(self, iterator_element)
        self.point = XY(iterator_element.x1, iterator_element.y1)
        self.block_name: str = iterator_element.blockName
        self._scale_x = iterator_element.xScale
        self._scale_y = iterator_element.yScale
        self._angle = GeomUtils.deg_to_rad(iterator_element.insertAngle)
            
    def __repr__(self) -> str:
        return f"TQSBlock[{self.block_name}, {self.point}]"
    
    @property
    def scale_x(self):
        return self._scale_x
    
    @scale_x.setter
    def scale_x(self, new_scale_x):
        self.dwg.edit.ModifyBlock(self.addr, new_scale_x, self._scale_y, GeomUtils.rad_to_deg(self._angle))
        self._scale_x = new_scale_x

    @property
    def scale_y(self):
        return self._scale_y
    
    @scale_y.setter
    def scale_y(self, new_scale_y):
        self.dwg.edit.ModifyBlock(self.addr, self._scale_x, new_scale_y, GeomUtils.rad_to_deg(self._angle))
        self._scale_y = new_scale_y

    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, new_angle):
        self.dwg.edit.ModifyBlock(self.addr, self._scale_x, self._scale_y, GeomUtils.rad_to_deg(new_angle))
        self._angle = new_angle

    @property
    def is_horizontal(self) -> float:
        return GeomUtils.is_horizontal(self.angle)
    
    @property
    def is_vertical(self) -> float:
        return GeomUtils.is_vertical(self.angle)

    def bounding_box(self) -> BoundingBox:
        bounding_box_list = [element.bounding_box() for element in self.elements if element]
        bounding_box_list = [bb for bb in bounding_box_list if bb]
        return GeomUtils.get_min_max_point([bb.max for bb in bounding_box_list] + [bb.min for bb in bounding_box_list])
    

    def alvest_block_length(self) -> float:
        bb = self.bounding_box()
        return bb.size_x if self.is_horizontal else bb.size_y

class TQSSmartObject(TQSIterableElement):
    def __init__(self, iterator_element: Iterator):
        TQSIterableElement.__init__(self, iterator_element)    
        self.object_name = iterator_element.objectName
        self.object_pointer = iterator_element.objectPointer
        self.smart_rebar = iterator_element.smartRebar
    
    def __repr__(self) -> str:
        return f"TQSSmartObject[{self.object_name}, {self.object_pointer}]"

class TQSDimension(TQSSmartObject):
    def __init__(self, iterator_element: Iterator):
        TQSSmartObject.__init__(self, iterator_element)    
        
    def __repr__(self) -> str:
        return f"TQSDimension[{self.object_name}, {self.object_pointer}]"
    
    @property
    def dim_line(self):
        dim_points = sorted(combinations([element.center for element in self.elements if isinstance(element, TQSCircle)], 2), key=lambda points: points[0].distance(points[1]))[-1]
        return Line(dim_points[0], dim_points[1])

class TQSSmartRebar(TQSSmartObject):
    def __init__(self, iterator_element: Iterator):
        TQSSmartObject.__init__(self, iterator_element)    

    def __repr__(self) -> str:
        return f"TQSSmartRebar[{self.object_name}, {self.object_pointer}]"
    
class TQSSubstructure(TQSSmartObject):
    def __init__(self, iterator_element: Iterator):
        TQSSmartObject.__init__(self, iterator_element)    

    @property
    def title(self) -> str:
        return self.elements.filter_type(TQSText).filter_layer(253)[0].text
    
    @property
    def vertical_fence(self) -> TQSPolyline:
        return self.elements.filter_type(TQSPolyline).filter_layer(253)[0]

    def __repr__(self) -> str:
        return f"TQSSubstructure[{self.title}, {self.object_pointer}]"

class TQSElementList(list[TQSEntity]):
    def filter(self, include: dict[str, list] = None, exclude: dict[str, list] = None, filter_function: Callable[[TQSEntity], bool] = None) -> TQSElementList:
        return TQSElementList([element for element in self if (include is None or all(getattr(element, d[0], "Invalid") in d[1] for d in include.items()))
                                                    and (exclude is None or all(getattr(element, d[0], "Invalid") not in d[1] for d in exclude.items()))
                                                    and (filter_function is None or filter_function(element))])

    def filter_layer(self, layer: int | list[int]) -> TQSElementList:
        return self.filter(include={"layer": ([layer] if isinstance(layer, int) else layer)})
        
    def filter_type(self, typ: type | list[type]) -> TQSElementList:
        return self.filter(filter_function = lambda element: (isinstance(element, typ) if isinstance(typ, type) else type(element) in typ))
    

