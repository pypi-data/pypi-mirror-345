# coding: latin-1
# Copyright (C) 1986-2024 TQS Informatica Ltda
#
#  This software is provided 'as-is', without any express or implied
#  warranty. In no event will the authors be held liable for any damages
#  arising from the use of this software.
#
#  Permission is granted to anyone to use this software exclusively in
#  conjunction with TQS software, subject to the following restrictions:
#
#  1. The origin of this software must not be misrepresented. You must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     required.
#  2. Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
#  3. This notice may not be removed or altered from any source distribution.
#
#  www.tqs.com.br
#  suporte@tqs.com.br
#-----------------------------------------------------------------------------
#    TQSGrid.PY  Módulo para a gravação de tabelas em desenho
#                Interface semelhante às bibliotecas de grid para Windowss
#-----------------------------------------------------------------------------
import ctypes
import TQS.TQSUtil
import TQS.TQSDwg

#-----------------------------------------------------------------------------
#       Atributo de grid. É usado nesta ordem:
#               Vem da célula se existir;
#               Senão vem da coluna se existir;
#               Senão vem da linha se existir;
#               Senão vem do grid
#
class GridDwgAttrib ():
    """
    Atributo que pode ser definido nesta ordem para:\n
    Célula, Coluna, Linha, Grid
    """

    ALIN_HINVAL   = -1      # Alinhamento horizontal inválido
    ALIN_HESQ     =  0      # Alinhamento horizontal esquerdo
    ALIN_HCEN     =  1      # Alinhamento horizontal central
    ALIN_HDIR     =  2      # Alinhamento horizontal direito

    ALIN_VINVAL   = -1      # Alinhamento vertical   inválido
    ALIN_VINF     =  0      # Alinhamento vertical   inferior
    ALIN_VCEN     =  1      # Alinhamento vertical   central
    ALIN_VSUP     =  2      # Alinhamento vertical   superior

    def __init__ (self, griddwg):
        self.m_griddwg = griddwg
        self.m_patrgrid= None
        parpdwggrid    = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parpatrgrid    = ctypes.c_void_p (self.m_patrgrid)
        self.m_griddwg.m_dwggriddll.DWGGRID_CRIARATRIB (parpdwggrid, ctypes.byref (parpatrgrid))
        self.m_patrgrid = parpatrgrid.value

    @property
    def level (self):
        """
        Nível de desenho
        """
        parpatrgrid    = ctypes.c_void_p (self.m_patrgrid)
        nivel          = 0;
        parnivel       = ctypes.c_int (nivel)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETNIVEL (parpatrgrid, ctypes.byref (parnivel))
        nivel          = parnivel.value
        return         (nivel);

    @level.setter
    def level (self, val):
        """
        Nível de desenho
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        parnivel        = ctypes.c_int (val)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETNIVEL (parpatrgrid, parnivel)

    @property
    def hText (self):
        """
        Altura de texto
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        htex            = 0.
        parhtex         = ctypes.c_double (htex)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETHTEX (parpatrgrid, ctypes.byref (parhtex))
        htex            = parhtex.value
        return          (htex);

    @hText.setter
    def hText (self, val):
        """
        Altura de texto
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        parhtex         = ctypes.c_double (val)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETHTEX (parpatrgrid, parhtex)

    @property
    def iHorizontalAlignment (self):
        """
        Alinhamento de texto GridDwgAttrib.ALIN_Hxxxx
        """
        parpatrgrid = ctypes.c_void_p (self.m_patrgrid)
        ialinh       = 0;
        parialinh    = ctypes.c_int (ialinh)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETIALINH (parpatrgrid, ctypes.byref (parialinh))
        ialinh       = parialinh.value
        return          (ialinh);

    @iHorizontalAlignment.setter
    def iHorizontalAlignment (self, val):
        """
        Alinhamento de texto GridDwgAttrib.ALIN_Hxxxx
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        parialinh     = ctypes.c_int (val)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETIALINH (parpatrgrid, parialinh)

    @property
    def iVerticalAlignment (self):
        """
        Alinhamento de texto GridDwgAttrib.ALIN_Vxxxx
        """
        parpatrgrid = ctypes.c_void_p (self.m_patrgrid)
        ialinv       = 0;
        parialinv    = ctypes.c_int (ialinv)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETIALINV (parpatrgrid, ctypes.byref (parialinv))
        ialinv       = parialinv.value
        return          (ialinv);

    @iVerticalAlignment.setter
    def iVerticalAlignment (self, val):
        """
        Alinhamento de texto GridDwgAttrib.ALIN_Vxxxx
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        parialinv     = ctypes.c_int (val)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETIALINV (parpatrgrid, parialinv)

    @property
    def cellHeight (self):
        """
        Altura da célula
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        altur           = 0.;
        paraltur        = ctypes.c_double (altur)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETALTUR (parpatrgrid, ctypes.byref (paraltur))
        altur           = paraltur.value
        return          (altur);

    @cellHeight.setter
    def cellHeight (self, val):
        """
        Altura da célula
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        paraltur        = ctypes.c_double (val)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETALTUR (parpatrgrid, paraltur)

    @property
    def cellWidth (self):
        """
        Largura da célula
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        alarg           = 0.;
        paralarg        = ctypes.c_double (alarg)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETALARG (parpatrgrid, ctypes.byref (paralarg))
        alarg           = paralarg.value
        return          (alarg);

    @cellWidth.setter
    def cellWidth (self, val):
        """
        Largura da célula
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        paralarg        = ctypes.c_double (val)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETALARG (parpatrgrid, paralarg)

    @property
    def cellFormat (self, format):
        """
        Formato da célula, família C printf. Tem que bater o tipo usado
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        parformat       = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_GETFORMAT (parpatrgrid, parformat)
        return          parformat.value.decode(TQS.TQSUtil.CHARSET)

    @cellFormat.setter
    def cellFormat (self, format):
        """
        Formato da célula, família C printf. Tem que bater o tipo usado
        """
        parpatrgrid     = ctypes.c_void_p (self.m_patrgrid)
        parformat       = ctypes.c_char_p (format.encode(TQS.TQSUtil.CHARSET))
        self.m_griddwg.m_dwggriddll.DWGGRID_ATRIB_SETFORMAT (parpatrgrid, parformat)

#-----------------------------------------------------------------------------
class GridDwg ():
    """
    Classe de Grid em DWG. Grava também LST e HTML
    """

    def __init__ (self):
        self.m_dwggriddll = TQS.TQSUtil.LoadDll ("NDWGGRID.DLL")
        self.m_pdwggrid   = None
        parpdwggrid       = ctypes.c_void_p (self.m_pdwggrid)
        self.m_dwggriddll.DWGGRID_INICIAR (ctypes.byref (parpdwggrid))
        self.m_pdwggrid   = parpdwggrid.value
        self.file         = File (self)
        self.attrib       = Attrib (self)
        self.format       = Format (self)

#
#    Representação deste objeto
#
    def __str__(self):
        msg         = "Class TQSGrid"
        msg         += "\n   m_dwggriddll " + str (self.m_dwggriddll)
        msg         += "\n   m_pdwggrid   " + str (self.m_pdwggrid)
        msg         += "\n   linhas       " + str (self.m_format.lines)
        msg         += "\n   colunas      " + str (self.m_format.columns)
        return         msg

#-----------------------------------------------------------------------------
class File ():
    """
    Gravação do grid em DWG, LST e HTML
    """

    def __init__ (self, griddwg):
        self.m_griddwg = griddwg


    def SaveAndMergeDwg (self, dwg, xorg, yorg):
        """
        Salva misturando em DWG fornecido\n
        dwg             Objeto de desenho\n
        xorg            Coordenadas da origem da tabela\n
        yorg            Coordenadas da origem da tabela
        """
        parpdwggrid       = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        pedmv           = dwg.handle_pedmv
        parpedmv        = ctypes.c_void_p (pedmv)
        parxorg         = ctypes.c_double (xorg)
        paryorg         = ctypes.c_double (yorg)
        self.m_griddwg.m_dwggriddll.DWGGRID_SALVAREMDWG (parpdwggrid, parpedmv, parxorg, paryorg)

    def SaveAsDwg (self, nomdwg):
        """
        Salva em DWG com nome fornecido
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parnomdwg       = ctypes.c_char_p (nomdwg.encode(TQS.TQSUtil.CHARSET))
        self.m_griddwg.m_dwggriddll.DWGGRID_SALVARCOMODWG (parpdwggrid, parnomdwg)

    def SaveAsLst (self, nomlst):
        """
        Salva em LST com nome fornecido
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parnomlst       = ctypes.c_char_p (nomlst.encode(TQS.TQSUtil.CHARSET))
        self.m_griddwg.m_dwggriddll.DWGGRID_SALVARCOMOLST (parpdwggrid, parnomlst)

    def SaveAsHtml (self, nomhtm):
        """
        Salva em HTM com nome fornecido
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parnomhtm       = ctypes.c_char_p (nomhtm.encode(TQS.TQSUtil.CHARSET))
        self.m_griddwg.m_dwggriddll.DWGGRID_SALVARCOMOHTM (parpdwggrid, parnomhtm)

    def SaveAsPdf (self, nompdf):
        """
        Salva em PDF com nome fornecido
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parnompdf       = ctypes.c_char_p (nompdf.encode(TQS.TQSUtil.CHARSET))
        self.m_griddwg.m_dwggriddll.DWGGRID_SALVARCOMOPDF (parpdwggrid, parnompdf)

#-----------------------------------------------------------------------------
class Attrib ():
    """
    Definição dos atributos do grid
    """

    def __init__ (self, griddwg):
        self.m_griddwg = griddwg

    def SetAttribGrid (self, attrgrid):
        """
        Define os atributos gerais do grid
        """
        parpdwggrid    = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parpatrgrid    = ctypes.c_void_p (attrgrid.m_patrgrid)
        self.m_griddwg.m_dwggriddll.DWGGRID_SETATRIBGRID (parpdwggrid, parpatrgrid)

    def SetAttribLine (self, line, attrgrid):
        """
        Define os atributos da linha line= 0..lines-1
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parline         = ctypes.c_int (line)
        parpatrgrid     = ctypes.c_void_p (attrgrid.m_patrgrid)
        self.m_griddwg.m_dwggriddll.DWGGRID_SETATRIBLINHA (parpdwggrid, parline, parpatrgrid)

    def SetAttribColumn (self, column, attrgrid):
        """
        Define os atributos da coluna column= 0..columns-1
        """
        parpdwggrid    = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parcolumn         = ctypes.c_int (column)
        parpatrgrid    = ctypes.c_void_p (attrgrid.m_patrgrid)
        self.m_griddwg.m_dwggriddll.DWGGRID_SETATRIBCOLUNA (parpdwggrid, parcolumn, parpatrgrid)

    def SetAttribCell (self, line, column, attrgrid):
        """
        Define os atributos da célula com \n
        linha line= 0..lines-1\n
        coluna column= 0..columns-1
        """
        parpdwggrid    = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parline         = ctypes.c_int (line)
        parcolumn         = ctypes.c_int (column)
        parpatrgrid    = ctypes.c_void_p (attrgrid.m_patrgrid)
        self.m_griddwg.m_dwggriddll.DWGGRID_SETATRIBCEL (parpdwggrid, parline, parcolumn, parpatrgrid)

#-----------------------------------------------------------------------------
class Format ():
    """
    Formatação do grid e preenchimento das células
    """

    def __init__ (self, griddwg):
        self.m_griddwg = griddwg

    @property
    def columns (self):
        """
        Número de colunas do grid
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        numcolunas      = 0;
        parnumcolunas   = ctypes.c_int (numcolunas)
        self.m_griddwg.m_dwggriddll.DWGGRID_GETCOLUNAS (parpdwggrid, ctypes.byref (parnumcolunas))
        numcolunas      = parnumcolunas.value
        return          (numcolunas);

    @columns.setter
    def columns (self, numcolumns):
        """
        Número de colunas do grid
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parnumcolunas   = ctypes.c_int (numcolumns)
        self.m_griddwg.m_dwggriddll.DWGGRID_SETCOLUNAS (parpdwggrid, parnumcolunas)

    @property
    def lines (self):
        """
        Número de linhas do grid
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        numlinhas      = 0;
        parnumlinhas   = ctypes.c_int (numlinhas)
        self.m_griddwg.m_dwggriddll.DWGGRID_GETLINHAS (parpdwggrid, ctypes.byref (parnumlinhas))
        numlinhas      = parnumlinhas.value
        return          (numlinhas);

    @lines.setter
    def lines (self, numlines):
        """
        Número de linhas do grid
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parnumlinhas    = ctypes.c_int (numlines)
        self.m_griddwg.m_dwggriddll.DWGGRID_SETLINHAS (parpdwggrid, parnumlinhas)

    def MergeLine (self, line, startColumn, endColumn):
        """
        Mistura as colunas startColumn a endColumn inclusive da linha line\n
        As linhas misturadas não tem linha divisória
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parilin         = ctypes.c_int (line)
        paricolini      = ctypes.c_int (startColumn)
        paricolfin      = ctypes.c_int (endColumn)
        self.m_griddwg.m_dwggriddll.DWGGRID_MESCLARLINHA (parpdwggrid, 
                            parilin, paricolini, paricolfin)

    def MergeColumn (self, column, startLine, endLine):
        """
        Mistura as linhas startLine a endLine inclusive, da coluna column\n
        As colunas misturadas não tem linha divisória
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        paricol         = ctypes.c_int (column)
        parilinini      = ctypes.c_int (startLine)
        parilinfin      = ctypes.c_int (endLine)
        self.m_griddwg.m_dwggriddll.DWGGRID_MESCLARCOLUNA (parpdwggrid, 
                            paricol, parilinini, parilinfin)

    def SetCell (self, line, column, val):
        """
        Valor de uma célula. Pode ser inteiro, real ou texto
        """
        parpdwggrid     = ctypes.c_void_p (self.m_griddwg.m_pdwggrid)
        parilin         = ctypes.c_int (line)
        paricol         = ctypes.c_int (column)

        if              (isinstance (val, int)):
            parival     = ctypes.c_int (val)
            self.m_griddwg.m_dwggriddll.DWGGRID_SETVALORINT (parpdwggrid, 
                            parilin, paricol, parival)

        elif            (isinstance (val, float)):
            pardval     = ctypes.c_double (val)
            self.m_griddwg.m_dwggriddll.DWGGRID_SETVALORDOUBLE (parpdwggrid, 
                            parilin, paricol, pardval)

        elif            (isinstance (val, str)):
            parsval     = ctypes.c_char_p (val.encode(TQS.TQSUtil.CHARSET))
            self.m_griddwg.m_dwggriddll.DWGGRID_SETVALORSTR (parpdwggrid, 
                            parilin, paricol, parsval)

        else:
            TQSUtil.writef ("TQSGrid: Valor inválido linha %d coluna %d" % (line, column));
            return

