from __future__ import annotations

import os
import ctypes
import glob

from os.path import splitext
from contextlib import contextmanager
from typing import Any, Callable
from tempfile import NamedTemporaryFile


from TQS.TQSDwg import Dwg, Iterator
from TQS.TQSUtil import SupportFolder, CHARSET, MAXNCSTR
from TQS import TQSDwg

from pygeometry2d import XY, GeomUtils, Line, BoundingBox, Rectangle
from pytqs.elements import TQSElementList, TQSEntity, TQSLine, TQSText, TQSPolyline, TQSBlock, TQSCircle, TQSArc, TQSSmartObject, TQSCurve, TQSDimension, TQSSmartRebar, TQSSubstructure

is_ezdxf_and_pymupdf_installed = True
try:
    import ezdxf
    import pymupdf
    from ezdxf.addons.drawing import layout, pymupdf, Frontend, RenderContext
    from ezdxf.enums import InsertUnits
    from ezdxf.addons.drawing.properties import LayoutProperties
except ImportError:
    is_ezdxf_and_pymupdf_installed = False

class TQSDrawning():
    def __init__(self, drawning_path: str = None, dwg: Dwg = None, auto_update_entitys: bool = False, iterate_through_invisible_layers = True) -> None:
        self.dwg = dwg or TQSDwg.Dwg()
        if drawning_path:
            self.open(drawning_path)
        self._elements: TQSElementList = None
        self.draw = Draw(self)
        self.auto_update_entitys = auto_update_entitys
        self.iterate_through_invisible_layers = iterate_through_invisible_layers

    def __getitem__(self, index: int) -> TQSEntity:
        return self.elements[index]
    
    def __setitem__(self, index: int, item: Any):
        self.elements[index] = item

    @staticmethod
    def element_convert(iterator_element: Iterator) -> TQSEntity:
        type_dict = {TQSDwg.DWGTYPE_LINE: TQSLine, TQSDwg.DWGTYPE_TEXT: TQSText, TQSDwg.DWGTYPE_POLYLINE: TQSPolyline, TQSDwg.DWGTYPE_BLOCK: TQSBlock, 
                    TQSDwg.DWGTYPE_CIRCLE: TQSCircle, TQSDwg.DWGTYPE_ARC: TQSArc, TQSDwg.DWGTYPE_OBJECT: TQSSmartObject, TQSDwg.DWGTYPE_CURVE: TQSCurve
                    }
        if type_dict.get(iterator_element.itype):
            if iterator_element.itype == TQSDwg.DWGTYPE_OBJECT and iterator_element.objectName == "IPOCOT":
                return TQSDimension(iterator_element)
            elif iterator_element.itype == TQSDwg.DWGTYPE_OBJECT and iterator_element.objectName == "IPOFER":
                return TQSSmartRebar(iterator_element)
            elif iterator_element.itype == TQSDwg.DWGTYPE_OBJECT and iterator_element.objectName == "Ipo_CrkSub":
                return TQSSubstructure(iterator_element)
            else:
                return type_dict[iterator_element.itype](iterator_element)

    @staticmethod
    def get_pen(pen: str) -> dict[int, (str, float)]:
        if pen:
            pen_path = f"{SupportFolder()}\\NGE\\PENAS\\{pen}"
        else:
            pen_files = glob.glob(os.path.join(f"{SupportFolder()}\\NGE\\PENAS", '*.PEN'))
            pen_path = max(pen_files, key=os.path.getmtime)
        file_content = open(pen_path).read().splitlines()[1:-1]
        return {int(file_content[n][27:]): [f"{file_content[n][4:10]}", float(file_content[n+1][6:10])] for n in range(0, len(file_content), 2)}
    

    @property
    def limits(self) -> BoundingBox:
        self.dwg.limits.UpdateLimits()
        xmin, ymin, xmax, ymax = self.dwg.limits.DwgLimits()
        return BoundingBox(XY(xmin, ymin), XY(xmax, ymax))
    
    @property
    def defined_blocks(self) -> list[str]:
        return [self.dwg.blockstable.Name(i) for i in range(self.dwg.blockstable.count)]
        
    @property
    def elements(self):
        if self._elements:
            return self._elements
        with self.turn_all_layers_on_temporarily():
            self.dwg.iterator.Begin()
            current_block_list: list[TQSBlock] = []
            current_smartobject_list: list[TQSSmartObject] = []
            self._elements = TQSElementList()
            while (typ := self.dwg.iterator.Next()) != TQSDwg.DWGTYPE_EOF:
                element = TQSDrawning.element_convert(self.dwg.iterator)
                if current_block_list and element:
                    current_block_list[-1].elements.append(element)
                
                if current_smartobject_list and element:
                    current_smartobject_list[-1].elements.append(element)
                
                if typ == TQSDwg.DWGTYPE_BLOCKBEGIN:
                    current_block_list.append(element)
                elif typ == TQSDwg.DWGTYPE_BLOCKEND:
                    current_block_list = current_block_list[:-1]
                
                elif typ == TQSDwg.DWGTYPE_OBJECT:
                    current_smartobject_list.append(element)
                elif typ == TQSDwg.DWGTYPE_OBJECTEND:
                    current_smartobject_list = current_smartobject_list[:-1]
                
                if typ not in [TQSDwg.DWGTYPE_BLOCKEND, TQSDwg.DWGTYPE_OBJECTEND]:
                    self._elements.append(element)
        return self._elements

    @contextmanager
    def turn_all_layers_on_temporarily(self):
        try:
            if self.iterate_through_invisible_layers:
                off_layers = [layer for layer in range(self.dwg.levelstable.count) if self.dwg.levelstable.IsDefined(layer) and not self.dwg.levelstable.IsOn(layer)]
                self.set_layer_state(off_layers, True)
            yield
        finally:
            if self.iterate_through_invisible_layers:
                self.set_layer_state(off_layers, False)

    @contextmanager
    def auto_update_entitys_temporarily(self):
        try:
            old_auto_update_entitys = self.auto_update_entitys
            self.auto_update_entitys = True
            yield
        finally:
            self.auto_update_entitys = old_auto_update_entitys

    def update_elements(self):
        self._elements = None
        self.elements
    
    def quick_filter(self, types: list[type] = None, layers: list[int] = None) -> TQSElementList:
        type_dict = {TQSDwg.DWGTYPE_LINE: TQSLine, TQSDwg.DWGTYPE_TEXT: TQSText, TQSDwg.DWGTYPE_POLYLINE: TQSPolyline, TQSDwg.DWGTYPE_BLOCK: TQSBlock, 
                    TQSDwg.DWGTYPE_CIRCLE: TQSCircle, TQSDwg.DWGTYPE_ARC: TQSArc, TQSDwg.DWGTYPE_OBJECT: TQSSmartObject, TQSDwg.DWGTYPE_CURVE: TQSCurve
                    }
        with self.turn_all_layers_on_temporarily():
            self.dwg.iterator.Begin()
            elements = []
            while (typ := self.dwg.iterator.Next()) != TQSDwg.DWGTYPE_EOF:
                if (not types or type_dict.get(typ) in types) and (not layers or self.dwg.iterator.level in layers) and (typ not in [TQSDwg.DWGTYPE_BLOCKEND, TQSDwg.DWGTYPE_OBJECTEND]):
                    elements.append(TQSDrawning.element_convert(self.dwg.iterator))
        return elements

    def filter(self, include: dict[str, list] = None, exclude: dict[str, list] = None, filter_function: Callable[[TQSEntity], bool] = None) -> TQSElementList:
        return self.elements.filter(include, exclude, filter_function)

    def filter_layer(self, layer: int | list[int]) -> TQSElementList:
        return self.elements.filter_layer(layer)

    def filter_type(self, typ: type | list[type]) -> TQSElementList:
        return self.elements.filter_type(typ)
    
    def new(self, scale: int = None, system_id: int = None, subsystem_id = None):
        parseed     = ctypes.create_string_buffer (MAXNCSTR)
        self.dwg.m_acessol.ACLSEED(parseed, 0)
        self.dwg.m_nomedwg = "SEM_NOME"
        parpedmv = ctypes.c_void_p (self.dwg.m_pedmv)
        paristat    = ctypes.c_int (0)
        self.dwg.m_mdwg.g_desopn (ctypes.c_char_p(self.dwg.m_nomedwg.encode(CHARSET)), parseed, None, ctypes.byref(parpedmv), ctypes.byref(paristat))
        self.dwg.m_pedmv = parpedmv.value
        
        if paristat.value != 0:
            return
        
        self.dwg.m_mdwg.COTIFOR (parpedmv)
        self.dwg.m_mdwg.COTINI ()
        self.dwg.m_mdwg.g_extpbl (parpedmv)
        self.dwg.CarregarCores()

        if scale:
            self.dwg.settings.scale = scale
        if system_id:
            self.dwg.settings.systemId = system_id
        if subsystem_id:
            self.dwg.settings.subSystemId = subsystem_id

    def open(self, path: str) -> bool:
        self.dwg.m_acessol.ACL_INIACESSO ()
        self.dwg.m_nomedwg = path
        paristat    = ctypes.c_int(0)
        parpedmv     = ctypes.c_void_p(self.dwg.m_pedmv)
        self.dwg.m_mdwg.g_extopn (ctypes.c_char_p(self.dwg.m_nomedwg.encode(CHARSET)), ctypes.byref(paristat), None, ctypes.byref(parpedmv))
        self.dwg.m_pedmv = parpedmv.value
        if paristat.value != 0:
            return False
        self.dwg.m_mdwg.COTIFOR(parpedmv)
        self.dwg.m_mdwg.g_extpbl(parpedmv)
        self.dwg.CarregarCores()
        return True
    
    def save(self):
        parpedmv = ctypes.c_void_p(self.dwg.m_pedmv)
        self.dwg.m_mdwg.g_rectam (parpedmv)
        self.dwg.m_mdwg.g_desslvcon (parpedmv)
    
    def save_as(self, path: str) -> str:
        while True:
            if os.path.exists(path):
                try:
                    os.rename(path, path)
                    break
                except OSError as e:
                    path = path[::-1].partition(".")[2][::-1] + "(1)." + path[::-1].partition(".")[0][::-1]
                    continue
            break
        
        self.dwg.m_nomedwg = path
        parpedmv     = ctypes.c_void_p (self.dwg.m_pedmv)
        pardwgname  = ctypes.c_char_p(path.encode(CHARSET))
        
        if ".DXF" in path.upper():
            self.dwg.m_mdwg.g_salvarcomodxf(parpedmv, pardwgname, ctypes.byref(ctypes.c_int(0)))
        elif ".PDF" in path.upper():
            dimsca  = self.dwg.settings.scale
            pardimsca = ctypes.c_double (dimsca)
            self.dwg.m_mdwg.g_salvarcomopdf (parpedmv, pardwgname, pardimsca, ctypes.byref (ctypes.c_int(0)))
        else:
            self.dwg.m_mdwg.g_edmrdn(parpedmv, pardwgname)
            self.dwg.m_mdwg.g_rectam(parpedmv)
            self.dwg.m_mdwg.g_edmdsn(parpedmv)
            self.dwg.m_mdwg.g_desslvcon(parpedmv)
        return path
    
    def set_layer_state(self, layers: int | list[int], state: bool):
        layers = layers if isinstance(layers, list) else [layers]
        pedmv = ctypes.c_void_p(self.dwg.m_pedmv)
        for layer in layers: 
            (self.dwg.m_mdwg.g_liglay if state else self.dwg.m_mdwg.g_deslay) (pedmv, ctypes.byref(ctypes.c_int(layer)))


    def save_as_temp(self, extension: str = ".DWG") -> str:
        tmp_file_path = NamedTemporaryFile(suffix=extension, delete=False).name
        self.save_as(tmp_file_path)
        return tmp_file_path
    

    def get_plot_settings(self, pen: str) -> dict:
        pen = TQSDrawning.get_pen(pen)
        self.dwg.plotting.LoadPlottingTable()
        
        return {str(i): pen.get(self.dwg.plotting.AttributeRead(i)[0], ["000000", 0.2]) + [self.dwg.plotting.AttributeRead(i)[2]] for i in range(self.dwg.levelstable.count)}
    
    def plot(self, file_path, plot_scale: int = 50, plot_offset: float = 50, pen: str = None, save_dxf: bool = False):
        assert (is_ezdxf_and_pymupdf_installed), "Para usar o comando plot é necessário instalar as bibliotecas ezdxf: https://pypi.org/project/ezdxf/ e PyMuPDF: https://pypi.org/project/PyMuPDF/"
        bb = self.limits
        self.draw.point(bb.min - XY(plot_offset, plot_offset))
        self.draw.point(bb.max + XY(plot_offset, plot_offset))
        
        plot_settings = self.get_plot_settings(pen)
        
        reference_file = self.save_as(f"{splitext(file_path)[0]}.DXF") if save_dxf else self.save_as_temp(".DXF") 

        doc = ezdxf.readfile(reference_file)
        
        doc.dxfversion = "R2013"
        doc.styles.add("Arial", font="Arial.ttf")

        for layer in doc.layers:
            if layer.dxf.name in plot_settings:
                layer.rgb = tuple(int(plot_settings.get(layer.dxf.name)[0][i:i+2], 16) for i in (0, 2, 4))
                layer.dxf.lineweight = int(plot_settings.get(layer.dxf.name)[1] * 100)
        
        model = doc.modelspace()

        for entity in model:
            if entity.dxftype() == 'TEXT':
                entity.dxf.set("style", "Arial")
        
        backend = pymupdf.PyMuPdfBackend()
        Frontend(RenderContext(doc), backend).draw_layout(model, layout_properties=LayoutProperties("properties", background_color="#FFFFFF", units=InsertUnits.Centimeters))
        with open(file_path, "wb") as fp:
            page_settings = layout.Page((bb.size_x+2*plot_offset)/(plot_scale/10), (bb.size_y+2*plot_offset)/(plot_scale/10))
            fp.write(backend.get_pdf_bytes(page_settings))
    def delete(self, entity: TQSEntity):
        entity.delete()
        if self._elements and entity in self._elements:
            self._elements.remove(entity)

class Draw():
    """
    Classe auxiliar para desenhos no TQS.
    """
    def __init__(self, drawning: TQSDrawning):
        self.drawning = drawning
        self.dwg: Dwg = drawning.dwg
    
    @contextmanager
    def set_drawing_properties(self, kwargs: dict[str, Any]):
        try:
            if self.drawning.auto_update_entitys and self.drawning._elements:
                addr = self.dwg.iterator.GetWritePosition()
            
            self._block_begin = None

            old_layer = self.dwg.draw.level
            old_style = self.dwg.draw.style
            old_color = self.dwg.draw.color

            self.dwg.draw.level = kwargs.get("layer") or 0
            self.dwg.draw.style = kwargs.get("style") or -1
            self.dwg.draw.color = kwargs.get("color") or -1

            yield
        finally:
            self.dwg.draw.level = old_layer
            self.dwg.draw.style = old_style
            self.dwg.draw.color = old_color

            if self.drawning.auto_update_entitys and self.drawning._elements:
                with self.drawning.turn_all_layers_on_temporarily():
                    self.dwg.iterator.SetPosition(addr)
                    current_block_list: list[TQSBlock] = []
                    current_smartobject_list: list[TQSSmartObject] = []
                    while (typ := self.dwg.iterator.Next()) != TQSDwg.DWGTYPE_EOF:
                        element = TQSDrawning.element_convert(self.dwg.iterator)

                        if self._block_begin is None:
                            self._block_begin = element

                        if current_block_list and element:
                            current_block_list[-1].elements.append(element)

                        if current_smartobject_list and element:
                            current_smartobject_list[-1].elements.append(element)

                        if typ == TQSDwg.DWGTYPE_BLOCKBEGIN:
                            current_block_list.append(element)
                        elif typ == TQSDwg.DWGTYPE_BLOCKEND:
                            current_block_list = current_block_list[:-1]

                        elif typ == TQSDwg.DWGTYPE_OBJECT:
                            current_smartobject_list.append(element)
                        elif typ == TQSDwg.DWGTYPE_OBJECTEND:
                            current_smartobject_list = current_smartobject_list[:-1]

                        if typ not in [TQSDwg.DWGTYPE_BLOCKEND, TQSDwg.DWGTYPE_OBJECTEND]:
                            self.drawning._elements.append(element)
    
    def _set_dim_properties (self, kwargs: dict[str, Any]):
        dim = self.dwg.dim
        dim.dimtxt = kwargs.get("dimtxt") if kwargs.get("dimtxt") != None else 0.2
        dim.dimexe = kwargs.get("dimexe") if kwargs.get("dimexe") != None else 0.25
        dim.dimdle = kwargs.get("dimdle") if kwargs.get("dimdle") != None else 0.25
        dim.dimtsz = kwargs.get("dimtsz") if kwargs.get("dimtsz") != None else 0.25
        dim.dimexo = kwargs.get("dimexo") if kwargs.get("dimexo") != None else 0.25
        dim.dimlfc = kwargs.get("dimlfc") if kwargs.get("dimlfc") != None else 1
        dim.idmniv = kwargs.get("idmniv") if kwargs.get("idmniv") != None else 221
        dim.idmnic = kwargs.get("idmnic") if kwargs.get("idmnic") != None else -1
        dim.idmnil = kwargs.get("idmnil") if kwargs.get("idmnil") != None else -1
        dim.idmnib = kwargs.get("idmnib") if kwargs.get("idmnib") != None else -1
        dim.idmcim = kwargs.get("idmcim") if kwargs.get("idmcim") != None else 0
        dim.idmar5 = kwargs.get("idmar5") if kwargs.get("idmar5") != None else 0
        dim.dimblk = kwargs.get("dimblk") if kwargs.get("dimblk") != None else "DOT2"
        dim.dimse1 = kwargs.get("dimse1") if kwargs.get("dimse1") != None else 0
        dim.idmcot = kwargs.get("idmcot") if kwargs.get("idmcot") != None else 0
        if kwargs.get("dimtxu") is not None:
            dim.dimtxu = kwargs.get("dimtxu")

    @contextmanager
    def set_dim_properties (self, kwargs: dict[str, Any]):
        try:
            dim = self.dwg.dim
            old_dimtxt = dim.dimtxt #Altura do têxto de cotagem.
            old_dimexe = dim.dimexe #Extensão da linha de chamada.
            old_dimdle = dim.dimdle #Extensão da linha de cotagem.
            old_dimtsz = dim.dimtsz #Tamanho do símbolo de cotagem.
            old_dimexo = dim.dimexo #Folga na linha de chamada.
            old_dimlfc = dim.dimlfc #Multiplicador de comprimentos.
            old_idmniv = dim.idmniv #Nível geral de cotagem.
            old_idmnic = dim.idmnic #Nível da linha de cotagem.
            old_idmnil = dim.idmnil #Nível da linha de chamada.
            old_idmnib = dim.idmnib #Nível do símbolo de cotagem.
            old_idmcim = dim.idmcim #(1) Se têxto abaixo da linha de cotagem
            old_idmar5 = dim.idmar5 #(1) Se medidas arredondadas de 5 em 5.
            old_dimblk = dim.dimblk #Nome do bloco de cotagem (TICK/DOT/ARROW são pré-definidos).
            old_dimse1 = dim.dimse1 #(1) Se suprime linha de chamada
            old_idmcot = dim.idmcot #(1) Se suprime linha de cotagem
            old_dimtxu = dim.dimtxu #Texto manual de cotagem.
            
            self._set_dim_properties(kwargs)
                
            yield
        finally:
            dim.dimtxt = old_dimtxt 
            dim.dimexe = old_dimexe             
            dim.dimdle = old_dimdle 
            dim.dimtsz = old_dimtsz 
            dim.dimexo = old_dimexo 
            dim.dimlfc = old_dimlfc
            dim.idmniv = old_idmniv
            dim.idmnic = old_idmnic
            dim.idmnil = old_idmnil
            dim.idmnib = old_idmnib
            dim.idmcim = old_idmcim
            dim.idmar5 = old_idmar5
            dim.dimblk = old_dimblk
            dim.dimse1 = old_dimse1
            dim.idmcot = old_idmcot

    @contextmanager
    def block_definition (self, block_name: str, insertion_reference: XY = None):
        try:
            if not insertion_reference:
                insertion_reference = XY.zero()
            self.dwg.draw.BlockOpen(block_name, insertion_reference.x, insertion_reference.y)
                
            yield
        finally:
            self.dwg.draw.BlockClose()
    
    def block(self, block_name: str, insertion_point: XY, ang: float = 0, escx: float = 1, escy: float = 1, **kwargs) -> TQSBlock:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.BlockInsert(block_name, insertion_point.x, insertion_point.y, escx, escy, GeomUtils.rad_to_deg(ang))

        return self._block_begin
            
    def point(self, point: XY, **kwargs) -> TQSLine:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Line(point.x, point.y, point.x, point.y)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def point(self, point: XY, **kwargs) -> TQSLine:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Line(point.x, point.y, point.x, point.y)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def text(self, text: str, point: XY, height: float, angle: float = 0, **kwargs) -> TQSText:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Text(point.x, point.y, height, GeomUtils.rad_to_deg(angle), text)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def centered_text(self, text: str, point: XY, height: float, angle: float = 0, **kwargs) -> TQSText:
        with self.set_drawing_properties(kwargs):
            vector = XY(-len(text)*height/2, -height/2)
            text_point = point + vector.rotate(angle)
            self.dwg.draw.Text(text_point.x, text_point.y, height, GeomUtils.rad_to_deg(angle), text)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def line(self, x1: float = None, y1: float = None, x2: float = None, y2: float = None, p1: XY = None, p2: XY = None, line: Line = None, **kwargs) -> TQSLine:
        with self.set_drawing_properties(kwargs):
            if line:
                self.dwg.draw.Line(line.start.x, line.start.y, line.end.x, line.end.y)
            elif p1 and p2:
                self.dwg.draw.Line(p1.x, p1.y, p2.x, p2.y)
            elif x1 is not None and y1 is not None and x2 is not None and y2 is not None:
                self.dwg.draw.Line(x1, y1, x2, y2)
        return self.drawning._elements[-1] if self.drawning._elements else None

    def line_vector(self, point: XY, delta_x: float, delta_y: float, **kwargs) -> TQSLine:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Line(point.x, point.y, point.x + delta_x, point.y + delta_y)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def double_arrow(self, line: Line, arrow_width: float = 12, arrow_height: float = 4, **kwargs):
        with self.set_drawing_properties(kwargs):
            self.line(line = line)
            self.line(p1 = line.start, p2 = line.start + XY(arrow_width, arrow_height/2).rotate(line.angle))
            self.line(p1 = line.start, p2 = line.start + XY(arrow_width, -arrow_height/2).rotate(line.angle))
            self.line(p1 = line.end, p2 = line.end + XY(-arrow_width, arrow_height/2).rotate(line.angle))
            self.line(p1 = line.end, p2 = line.end + XY(-arrow_width, -arrow_height/2).rotate(line.angle))

    def rectangle(self, rect: Rectangle, **kwargs) -> TQSPolyline:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Rectangle(rect.min_corner.x, rect.min_corner.y, rect.max_corner.x, rect.max_corner.y)
        return self.drawning._elements[-1] if self.drawning._elements else None

    def rectangle_by_corner(self, corner: XY, dim_x: float, dim_y: float, **kwargs) -> TQSPolyline:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Rectangle(corner.x, corner.y, corner.x + dim_x, corner.y + dim_y)
        return self.drawning._elements[-1] if self.drawning._elements else None

    def rectangle_by_corners(self, corner1: XY, corner2: XY, **kwargs) -> TQSPolyline:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Rectangle(corner1.x, corner1.y, corner2.x, corner2.y)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def rectangle_by_center(self, center: XY, dim_x: float, dim_y: float, **kwargs) -> TQSPolyline:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Rectangle(center.x - dim_x/2, center.y - dim_y/2, center.x + dim_x/2, center.y + dim_y/2)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def polyline(self, point_list: list[XY], is_filled = False, **kwargs) -> TQSPolyline:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.PolyStart()
            for point in point_list:
                self.dwg.draw.PolyEnterPoint(point.x, point.y)
            self.dwg.draw.PolylineFilled() if is_filled else self.dwg.draw.Polyline()  
        return self.drawning._elements[-1] if self.drawning._elements else None
   
    def arc_by_points(self, point1: XY, point2: XY, point3: XY, **kwargs) -> TQSArc:
        with self.set_drawing_properties(kwargs):
            center, radius, start_angle, end_angle = GeomUtils.arc_by_3_points(point1, point2, point3)
            self.dwg.draw.Arc(center.x, center.y, radius, GeomUtils.rad_to_deg(start_angle), GeomUtils.rad_to_deg(end_angle))
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def circle_by_points(self, point1: XY, point2: XY, point3: XY, **kwargs) -> TQSCircle:
        with self.set_drawing_properties(kwargs):
            center, radius = GeomUtils.circle_by_3_points(point1, point2, point3)
            self.dwg.draw.Circle(center.x, center.y, radius)
        return self.drawning._elements[-1] if self.drawning._elements else None

    def circle(self, center: XY, diameter: float, **kwargs) -> TQSCircle:
        with self.set_drawing_properties(kwargs):
            self.dwg.draw.Circle(center.x, center.y, diameter/2)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
    def circle_array(self, first_center: XY, last_center: XY, number_of_circles: float, diameter: float, **kwargs):
        with self.set_drawing_properties(kwargs):
            vector = (last_center - first_center)/(number_of_circles - 1)
            for i in range(number_of_circles):
                self.dwg.draw.Circle(first_center.x + vector.x * i, first_center.y + vector.y * i, diameter/2)

    def dimension(self, point1: XY, point2: XY, line_offset: float, **kwargs) -> TQSDimension:
        with self.set_dim_properties(kwargs):
            itipo = TQSDwg.IDHOR if abs((point1-point2).x) >= abs((point1-point2).y) else TQSDwg.IDVER
            line_point = XY.mid(point2, point1) + (((point2-point1).perpendicular().normalize() * line_offset) if point1 != point2 else XY.zero())
            self.dwg.dim.Dim3P(itipo, point1.x, point1.y, point2.x, point2.y, line_point.x, line_point.y)
        return self.drawning._elements[-1] if self.drawning._elements else None
    
