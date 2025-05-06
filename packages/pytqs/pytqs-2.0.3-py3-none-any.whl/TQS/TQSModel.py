# coding: latin-1
# Copyright (C) 1986-2024 TQS Informatica Ltda
#
#  This software is provided 'as-is', without any express or implied
#  warranty.  In no event will the authors be held liable for any damages
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
#       TQSMoldel.py    06-12-2023 Leitura e gravação de modelo estrutural
#-----------------------------------------------------------------------------
import ctypes, os
from TQS import TQSUtil, TQSBuild, TQSJan

#-----------------------------------------------------------------------------
#      Lista tipos de objetos do Modelador
#
TYPE_INDEF                    = -1  # Indefinido
TYPE_VIGAS                    =  0  # Vigas
TYPE_PILARES                  =  1  # Pilares
TYPE_LAJES                    =  2  # Lajes
TYPE_FUNDAC                   =  3  # Fundações
TYPE_FUROS                    =  4  # Furos
TYPE_CAPITEIS                 =  5  # Capiteis
TYPE_FORNER                   =  6  # Formas de lajes nervuradas
TYPE_CTRAUX                   =  7  # Contorno auxiliar
TYPE_EIXOS                    =  8  # Eixos rotulados
TYPE_COTAGENS                 =  9  # Cotagens
TYPE_CORTES                   = 10  # Cortes
TYPE_DADPAV                   = 11  # Dados comuns do pavimento
TYPE_DADEDI                   = 12  # Dados comuns do edificio
TYPE_SECPIL                   = 13  # Secoes de pilares
TYPE_LISMAL                   = 14  # Lista de malhas de lajes
TYPE_CARCON                   = 15  # Cargas concentradas
TYPE_CARLIN                   = 16  # Cargas distribuidas lineares
TYPE_CARARE                   = 17  # Carga distribuida por area
TYPE_BARICEN                  = 18  # Tabela de baricentros de pil
TYPE_CARADI                   = 19  # Carga adicional em laje
TYPE_RAMPAS                   = 20  # TIPO FALSO: laje inclinada
TYPE_ORIEIX                   = 21  # Origem do sistema de eixos
TYPE_TABNP                    = 22  # Tabela de seções não padrão
TYPE_IDCLI                    = 23  # Identificação do cliente
TYPE_CONSBIB                  = 24  # Biblioteca de consolos
TYPE_FUROVIG                  = 25  # Furo em viga
TYPE_ELMLJP                   = 26  # Elemento de laje pré-moldada
TYPE_TABELEM                  = 27  # Tabela c/lista de elementos
TYPE_COTDIA                   = 28  # Cotagem de raio/diâmetro
TYPE_COTANG                   = 29  # Cotagem angular
TYPE_COTNOT                   = 30  # Cotagem de notas
TYPE_VENDST                   = 31  # Tabela de distribuição de vento
TYPE_CENTOR                   = 32  # Centro de torção Túnel de vento
TYPE_CONSIND                  = 33  # Consolos Independentes
TYPE_CAREMP                   = 34  # Cargas de empuxo
TYPE_TABNIVPAV                = 35  # Tabela de níveis de pavimentos
TYPE_LEGDESNIV                = 36  # Tabela de legenda de desníveis
TYPE_SIMDESNIV                = 37  # Símbolo de desnível de pav
TYPE_ELM3D                    = 38  # Elemento 3D
TYPE_INSRBLO                  = 39  # Inserto (de biblioteca)
TYPE_INSRPOS                  = 40  # Inserto (inserção)
TYPE_FACHADA                  = 41  # Fachada de painél pré-moldado
TYPE_TUBOS                    = 42  # Tubos de instalações
TYPE_FUROPIL                  = 43  # Furo em pilar
TYPE_LAJESSOVOL               = 44  # Container CLajes somente volume
TYPE_ESTACRAD                 = 45  # Estaca sob Radier
TYPE_VIGASINC                 = 46  # TIPO FALSO: viga inclinada
TYPE_PILARETES                = 47  # TIPO FALSO: pilaretes
TYPE_ESCADAS                  = 48  # TIPO FALSO: escada
TYPE_PATAMARES                = 49  # TIPO FALSO: patamar
TYPE_ORIBARI                  = 50  # Origem de baricentros
TYPE_EDIEDI                   = 51  # Dados do edifício (mesmo que ACESSOL)
TYPE_PTBAS                    = 52  # Ponto base do projeto
TYPE_PTLVT                    = 53  # Ponto de levantamento topográfico
TYPE_CERCATOR                 = 54  # Cerca de torre (separa torre e periferia)
TYPE_CARTRM                   = 55  # Trem tipo
TYPE_LEGCORCAR                = 56  # Legenda de cores de cargas
#------------------------------------------------------------------------------
#      Modos de visualização (VisModes)
#      
VISMODE_MATUAL                = 0  # Modo de visualização atual
VISMODE_FORMAS                = 1  # Desenho de formas FORnnnn.DWG
VISMODE_VERIFI                = 2  # Modo de verificação
VISMODE_MODELO                = 3  # Desenho MODELO.DWG
VISMODE_GRUPOA                = 4  # Grupo A de visualização do usuário
VISMODE_GRUPOB                = 5  # Grupo B de visualização do usuário
#------------------------------------------------------------------------------
#      Dados gloais de pilares e fundações
#
COLUMNDATA_PILARS             = 0  # Dados de pilares
COLUMNDATA_FUNDAC             = 1  # Dados de fundações
COLUMNDATA_PILRTE             = 2  # Dados de pilaretes
#------------------------------------------------------------------------------
#      Tipo de carga dos dados atuais
#      
TPLOAD_CARVIG                 =  0 # Carga linear para toda a viga
TPLOAD_CARLAJ                 =  1 # Carga distribuída para toda a laje
TPLOAD_FORCFX                 =  2 # Forca concentrada X
TPLOAD_FORCFY                 =  3 # Forca concentrada Y
TPLOAD_FORCFZ                 =  4 # Forca concentrada Z
TPLOAD_FORCMX                 =  5 # Momento concentrado X
TPLOAD_FORCMY                 =  6 # Momento concentrado Y
TPLOAD_CMVCFX                 =  7 # Carga móvel: Forca concentrada   X  
TPLOAD_CMVCFY                 =  8 # Carga móvel: Forca concentrada   Y  
TPLOAD_CMVCFZ                 =  9 # Carga móvel: Forca concentrada   Z  
TPLOAD_CMVCMX                 = 10 # Carga móvel: Momento concentrado X
TPLOAD_CMVCMY                 = 11 # Carga móvel: Momento concentrado Y
TPLOAD_CARLIN                 = 12 # Carga distribuída linear
TPLOAD_CARARE                 = 13 # Carga distribuída por área
TPLOAD_CARADI                 = 14 # Carga adicional em laje
#
#      Tipo de uma carga
#
LOADTYPE_DISARE                = 0  # Distribuída por area
LOADTYPE_DISLIN                = 1  # Distribuída linear
LOADTYPE_CONCEN                = 2  # Concentrada
LOADTYPE_MOMCON                = 3  # Momento concentrado
#-----------------------------------------------------------------------------
#       Como o pilar nasce
#
COLUMNSTART_NASCEDIRT         = 0  # Nasce direto no solo (sem fundação definida)
COLUMNSTART_NASCEVIGA         = 1  # Nasce em viga
COLUMNSTART_NASCEPIFU         = 2  # Nasce em pilar ou fundação
COLUMNSTART_NASCELAJE         = 3  # Nasce em laje
#------------------------------------------------------------------------------
#      Tipo de uso do pilar: compressão ou tração
#
COLUMNUSE_COMPRESSAO          = 0  # Padrão - forças de compressão
COLUMNUSE_TRACAO              = 1  # Principalmente tração, pode compressão
COLUMNUSE_COMPAT              = 2  # Pilar de compatibilização
COLUMNUSE_ESCORA              = 3  # Escora (só compressão)
COLUMNUSE_TIRANTE             = 4  # Tirante (só tração)
#------------------------------------------------------------------------------
#       Definição de molas de pilares no pórtico
#
COLUMNCOIL_IRES_IRX           = 0  # Rotação X
COLUMNCOIL_IRES_IRY           = 1  # Rotação Y
COLUMNCOIL_IRES_IRZ           = 2  # Rotação Z
COLUMNCOIL_IRES_ITX           = 3  # Translação X
COLUMNCOIL_IRES_ITY           = 4  # Translação Y
COLUMNCOIL_IRES_ITZ           = 5  # Translação Z
#
#       Tipo de engaste
#
COLUMNCOIL_IAPOPOR_DEFAULT     = 0  # Engaste ou padrão
COLUMNCOIL_IAPOPOR_ARTICULADO  = 1  # Articulado
COLUMNCOIL_IAPOPOR_ELASTICO    = 2  # Elástico
COLUMNCOIL_IAPOPOR_RECALQUE    = 3  # Recalque
#
#       Gap de restrição de apoio
#
COLUMNCOIL_IGAP_XPOS           = 0  # Gap Tx+
COLUMNCOIL_IGAP_XNEG           = 1  # Gap Tx-
COLUMNCOIL_IGAP_YPOS           = 2  # Gap Ty+
COLUMNCOIL_IGAP_YNEG           = 3  # Gap Ty-
COLUMNCOIL_IGAP_ZPOS           = 4  # Gap Tz+
COLUMNCOIL_IGAP_ZNEG           = 5  # Gap Tz-
#
#       Tipos de seção de pilar
#
COLUMNTYPE_R                   = 0  # Seção Retangular
COLUMNTYPE_L                   = 1  # Seção L
COLUMNTYPE_U                   = 2  # Seção U
COLUMNTYPE_C                   = 3  # Seção Circular
COLUMNTYPE_P                   = 4  # Seção Poligonal
COLUMNTYPE_N                   = 5  # Seção Outras não padrão
#
#       Condições de contorno de grelha
#
COLUMNBEARING_DEFAULT          = 0  # Default
COLUMNBEARING_ARTCONT          = 1  # Articulado contínuo
COLUMNBEARING_ARTINDP          = 2  # Articulado independente
COLUMNBEARING_ELACONT          = 3  # Elástico continuo
COLUMNBEARING_ELAINDP          = 4  # Elástico independente
#
#       Coeficientes de mola na grelha
#
COLUMNSPRING_IRX               = 0  # Rx
COLUMNSPRING_IRY               = 1  # Ry
COLUMNSPRING_ITZ               = 2  # Tz
COLUMNSPRING_ITX               = 3  # Tx
COLUMNSPRING_ITY               = 4  # Ty

#------------------------------------------------------------------------------
#       Fundações
#
FOUNDATION_ITIPOFUNDAC_SAPATA  = 0  # Sapata
FOUNDATION_ITIPOFUNDAC_BLOCO   = 1  # Bloco sobre estacas
FOUNDATION_ITIPOFUNDAC_TUBULAO = 2  # Tubulão
#
#      Dados de cálice
#
FOUNDATION_FORM_RETANGULAR     = 0  # Cálice: Formato retangular
FOUNDATION_FORM_CIRCULAR       = 1  # Cálice: Formato circular
#
#       Rugosidade do cálice
#
FOUNDATION_RUGO_PADRAO         = 0  # Cálice: Rugosidade conforme critérios
FOUNDATION_RUGO_SULISA         = 1  # Cálice: Superfície lisa
FOUNDATION_RUGO_RUGOSA         = 2  # Cálice: Superfíce rugosa, pilar também
FOUNDATION_RUGO_CHAVECIS       = 3  # Cálice: Chave de cisalhamento
#------------------------------------------------------------------------------
#      Atributos BIM do usuário - estrutura global
#
BIM_USRATRTP_PILAR             = 0  # Pilar
BIM_USRATRTP_FUNDC             = 1  # Fundações
BIM_USRATRTP_VIGAS             = 2  # Vigas
BIM_USRATRTP_LAJES             = 3  # Lajes
BIM_USRATRTP_ELM3D             = 4  # Elementos 3D
#
#       Atributos BIM globais
#
BIM_GLBA_GLOBAL                = 0  # Todos do edifício
BIM_GLBA_PLANTA                = 1  # Todos de uma planta
BIM_GLBA_UMPISO                = 2  # Todos de um piso
#------------------------------------------------------------------------------
#      Tipos de cruzamento de vigas
#
BEAMCROSSING_INDEFINIDO        = 0  # Indefinido		
BEAMCROSSING_RECEBE            = 1  # Recebe carga
BEAMCROSSING_CRUZAMENTO        = 2  # Cruzamento sem apoio identificado
BEAMCROSSING_APOIAVIGA         = 3  # Apoia em viga
BEAMCROSSING_APOIAPILAR        = 4  # Apoia em pilar
BEAMCROSSING_N                 = 5  # Neutro
#------------------------------------------------------------------------------
#      Vinculação de viga com laje
#
BEAMCONNECTION_DEFAULT         = 0  # Default
BEAMCONNECTION_ENLIVRE         = 1  # Livre
BEAMCONNECTION_ARTCMXY         = 2  # Articulado mx,my
BEAMCONNECTION_ARTMXYF         = 3  # Articulado mx,my,fx 
BEAMCONNECTION_FATEMGS         = 4  # Engastado com fatengast
#------------------------------------------------------------------------------
#      Furo em viga
#
BEAMOPENINGREFERENCE_TOPO      = 0  # Rebaixo em relação ao topo
BEAMOPENINGREFERENCE_EIXO      = 1  # Rebaixo em relação ao eixo
BEAMOPENINGREFERENCE_BASE      = 2  # Rebaixo em relação à base
#------------------------------------------------------------------------------
#      Tipos de laje
#
SLABTYPE_MACICA                 = 0  # Maciça
SLABTYPE_NERVUR                 = 1  # Nervurada retangular
SLABTYPE_NERVUT                 = 2  # Nervurada trapezoidal
SLABTYPE_VIGOTA                 = 3  # Vigotas treliçadas
SLABTYPE_TRELIC                 = 4  # Treliçada
SLABTYPE_PREFAB                 = 5  # Pré-fabricada
SLABTYPE_MISNER                 = 6  # Mista nervurada (ex: TUPER)
#------------------------------------------------------------------------------
#       Modelo estrutural
#
class Model ():
    """
    Modelo estrutural
    """

    def __init__ (self, tqsjan=None):
        """
        Modelo estrutural
        """
        self.m_eagme    = TQSUtil.LoadDll ("FINTME.DLL")

        self.file       = File (self)
        self.type       = Type (self)
        self.floors     = FloorsList (self)
        self.current    = CurGlobalData (self)
        self.visData    = VisData (self)
        self.m_tqsjan   = tqsjan

    def __str__(self):
        msg             = "TQSModel"
        msg             += "\n   self.m_eagme      " + str (self.m_eagme)
        msg             += "\n   self.file         " + str (self.file)
        msg             += "\n   self.type         " + str (self.type)
        msg             += "\n   self.floorslist   " + str (self.floorslist)
        msg             += "\n   self.current      " + str (self.current)
        msg             += "\n   self.m_tqsjan     " + str (self.m_tqsjan)
        return          msg

#------------------------------------------------------------------------------
#       Lista dos tipos de objeto do Modelador
#
class Type ():

    def __init__ (self, model):
        """
        Inicialização de objeto do Modelador
        """
        self.m_model    = model

    def GetNumTypes (self):
        """
        Retorna o número de tipos de objetos do Modelador
        """
        numlistas       = 0
        varnumlistas    = ctypes.c_int (numlistas)
        self.m_model.m_eagme.BASME_PLANTA_NUMLISTAS (ctypes.byref (varnumlistas))
        numlistas       = varnumlistas.value
        return          numlistas

    def GetTypeClass (self, itype):
        """
        Retorna o nome de classe de um tipo de objeto (classe C++, não do TQSModel)\n
            itype       <- (int) TYPE_xxxx\n
        Retorna:\n
            nomeclasse  -> (string) Nome da classe
        """
        varitype        = ctypes.c_int (itype)
        varnomeclasse   = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        varnomeobjeto   = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        argfan          = ctypes.c_int (0)
        self.m_model.m_eagme.BASME_PLANTA_NOMELISTA (ctypes.byref (varitype),
                        varnomeclasse, argfan, varnomeobjeto, argfan)
        nomeclasse      = varnomeclasse.value.decode(TQSUtil.CHARSET)
        return         nomeclasse
        
    def GetTypeDescription (self, itype):
        """
        Retorna a descrição de um tipo de objeto\n
            itype       <- (int) TYPE_xxxx\n
        Retorna:\n
            nomeobjeto  -> (string) Nome do objeto
        """
        varitype        = ctypes.c_int (itype)
        varnomeclasse   = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        varnomeobjeto   = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        argfan          = ctypes.c_int (0)
        self.m_model.m_eagme.BASME_PLANTA_NOMELISTA (ctypes.byref (varitype),
                        varnomeclasse, argfan, varnomeobjeto, argfan)
        nomeobjeto      = varnomeobjeto.value.decode(TQSUtil.CHARSET)
        return         nomeobjeto

#------------------------------------------------------------------------------
#       Operações de leitura e gravação do modelo
#
class File ():

    def __init__ (self, model):
        """
        Inicialização da classe de arquivos
        """
        self.m_model    = model

    def OpenModel (self):
        """
        Abre modelo existente ou cria novo\n
        Retorna: istat (!=0) Se erro
        """
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.INTME_ABRIRMODELOESP (ctypes.byref (varistat))
        istat           = varistat.value
        return          istat
        
    def OpenNewModel (self):
        """
        Abre modelo novo, apaga velho se já existir\n
        Retorna: istat (!=0) Se erro
        """
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.INTME_ABRIRMODELONOVOESP (ctypes.byref (varistat))
        istat           = varistat.value
        return          istat

    def Save (self):
        """
        Salva o modelo estrutural\n
        Retorna: istat (!=0) Se erro
        """
        pvistav         = None
        if              (self.m_model.m_tqsjan != None):
            pvistav     = self.m_model.m_tqsjan.m_pvistav
        varpvistav      = ctypes.c_void_p (pvistav)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.INTME_SALVARMODELO (ctypes.byref (varpvistav), 
                            ctypes.byref (varistat))
        istat           = varistat.value
        return          istat

    def Close (self):
        """
        Fecha modelo estrutural aberto
        """
        self.m_model.m_eagme.INTME_FECHARMODELOESP ()

#-----------------------------------------------------------------------------
#       Dados globais, usados como modelo para a criação de objetos novos
#
class CurGlobalData ():

    def __init__ (self, model):
        """
        Dados globais, que são usados na criação de objetos novos\n
            model       <- Objeto Model() do modelo atual\n
        Subdividido em objetos:\n
               globalAxisData       Dados de eixos automáticos\n
               globalCutData        Dados de cortes\n
               globalSoilpress      Carregamento de empuxo\n
               globalRefxData       Critérios de referências externas\n
               globalBeamData       Dados de vigas\n
               globalSlabData       Dados de lajes, rampas e escadas\n
               globalColumnData     Dados de pilares e fundações\n
               globalColumnOpening  Furo em pilar\n
               globalPrecast        Dados de pré-moldados\n
               globalBimData        Dados de BIM
        """
        self.m_model          = model

        self.globalAxisData   = GlobalAxisData (model)
        self.globalCutData    = GlobalCutData (model)
        self.globalSoilpress  = GlobalSoilPressureData (model)
        self.globalRefxData   = GlobalRefxData (model)
        self.globalBeamData   = GlobalBeamData (model)
        self.globalSlabData   = GlobalSlabData (model)
        self.globalColumnData = GlobalColumnData (model)
        self.globalColumnOpening= GlobalColumnOpening (model)
        self.globalSlabFPile  = GlobalSlabFoundationPile (model)
        self.globalPrecast    = GlobalPrecastData (model)
        self.globalBimData    = GlobalBimData (model)
#
#       Dados globais de Eixos - CurGlobalData.globalAxisData
#
class GlobalAxisData ():

    def __init__ (self, model):
        """
        Dados globais de eixos\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    @property
    def axis (self):
        """
        Retorna objeto AutoAxis() para geração automática de eixos
        """
        eixaut          = None
        vareixaut       = ctypes.c_void_p (eixaut)
        self.m_model.m_eagme.BASME_DADEDI_EIXAUT_LER (ctypes.byref (vareixaut))
        eixaut          = vareixaut.value
        autoaxis        = AutoAxis (self.m_model, eixaut)
        return          autoaxis

    @property
    def spaceAxis (self):
        """
        Eixos (0) somente planta atual (1) definidos para todas as plantas 
        """
        ieixosespac     = 0
        varieixosespac  = ctypes.c_int (ieixosespac)
        self.m_model.m_eagme.BASME_DADEDI_IEIXOSESPAC_LER (ctypes.byref (varieixosespac))
        ieixosespac     = varieixosespac.value
        return          ieixosespac

    @spaceAxis.setter
    def spaceAxis (self, ieixosespac):
        """
        Eixos (0) somente planta atual (1) definidos para todas as plantas 
        """
        varieixosespac  = ctypes.c_int (ieixosespac)
        self.m_model.m_eagme.BASME_DADEDI_IEIXOSESPAC_DEF (ctypes.byref (varieixosespac))
#
#      Cortes - CurGlobalData.globalCutData
#
class GlobalCutData ():

    def __init__ (self, model):
        """
        Dados globais de cortes
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    @property
    def sectionType (self):
        """
        Corte (0)rebatido (1)profundidade (2)global
        """
        iprofundcor     = 0
        variprofundcor  = ctypes.c_int (iprofundcor)
        self.m_model.m_eagme.BASME_DADEDI_IPROFUNDCOR_LER (ctypes.byref (variprofundcor))
        iprofundcor     = variprofundcor.value
        return          iprofundcor

    @sectionType.setter
    def sectionType (self, iprofundcor):
        """
        Corte (0)rebatido (1)profundidade (2)global
        """
        variprofundcor  = ctypes.c_int (iprofundcor)
        self.m_model.m_eagme.BASME_DADEDI_IPROFUNDCOR_DEF (ctypes.byref (variprofundcor))

    @property
    def sectionElevationAngle (self):
        """
        Cortes: Ângulo de elevação, graus
        """
        angelev         = 0.
        varangelev      = ctypes.c_double (angelev)
        self.m_model.m_eagme.BASME_DADEDI_ANGELEV_LER (ctypes.byref (varangelev))
        angelev         = varangelev.value
        return          angelev

    @sectionElevationAngle.setter
    def sectionElevationAngle (self, angelev):
        """
        Cortes: Ângulo de elevação, graus
        """
        varangelev      = ctypes.c_double (angelev)
        self.m_model.m_eagme.BASME_DADEDI_ANGELEV_DEF (ctypes.byref (varangelev))

    @property
    def sectionDeviationAngle (self):
        """
        Cortes: Ângulo de desvio, graus
        """
        angdesv         = 0.
        varangdesv      = ctypes.c_double (angdesv)
        self.m_model.m_eagme.BASME_DADEDI_ANGDESV_LER (ctypes.byref (varangdesv))
        angdesv         = varangdesv.value
        return          angdesv

    @sectionDeviationAngle.setter
    def sectionDeviationAngle (self, angdesv):
        """
        Cortes: Ângulo de desvio, graus
        """
        varangdesv      = ctypes.c_double (angdesv)
        self.m_model.m_eagme.BASME_DADEDI_ANGDESV_DEF (ctypes.byref (varangdesv))

    @property
    def sectionHatch (self):
        """
        Cortes: Hachurar o resultado
        """
        ihachurar       = 0
        varihachurar    = ctypes.c_int (ihachurar)
        self.m_model.m_eagme.BASME_DADEDI_IHACHURAR_LER (ctypes.byref (varihachurar))
        ihachurar       = varihachurar.value
        return          ihachurar

    @sectionHatch.setter
    def sectionHatch (self, ihachurar):
        """
        Cortes: Hachurar o resultado
        """
        varihachurar      = ctypes.c_int (ihachurar)
        self.m_model.m_eagme.BASME_DADEDI_IHACHURAR_DEF (ctypes.byref (varihachurar))

    @property
    def sectionLabel (self):
        """
        Cortes: (1) p/rotular cortes
        """
        irotular        = 0
        varirotular     = ctypes.c_int (irotular)
        self.m_model.m_eagme.BASME_DADEDI_IROTULAR_LER (ctypes.byref (varirotular))
        irotular       = varirotular.value
        return          irotular

    @sectionLabel.setter
    def sectionLabel (self, irotular):
        """
        Cortes: (1) p/rotular cortes
        """
        varirotular      = ctypes.c_int (irotular)
        self.m_model.m_eagme.BASME_DADEDI_IROTULAR_DEF (ctypes.byref (varirotular))

    @property
    def section3DViewl (self):
        """
        Cortes: (1) Cortar na visualização 3D
        """
        icortarv3d      = 0
        varicortarv3d   = ctypes.c_int (icortarv3d)
        self.m_model.m_eagme.BASME_DADEDI_ICORTARV3D_LER (ctypes.byref (varicortarv3d))
        icortarv3d       = varicortarv3d.value
        return          icortarv3d

    @section3DViewl.setter
    def section3DViewl (self, icortarv3d):
        """
        Cortes: (1) Cortar na visualização 3D
        """
        varicortarv3d      = ctypes.c_int (icortarv3d)
        self.m_model.m_eagme.BASME_DADEDI_ICORTARV3D_DEF (ctypes.byref (varicortarv3d))

    @property
    def sectionProject (self):
        """
        Cortes: (1) Projetar o corte
        """
        iprojetar       = 0
        variprojetar    = ctypes.c_int (iprojetar)
        self.m_model.m_eagme.BASME_DADEDI_IPROJETAR_LER (ctypes.byref (variprojetar))
        iprojetar       = variprojetar.value
        return          iprojetar

    @sectionProject.setter
    def sectionProject (self, iprojetar):
        """
        Cortes: (1) Projetar o corte
        """
        variprojetar    = ctypes.c_int (iprojetar)
        self.m_model.m_eagme.BASME_DADEDI_IPROJETAR_DEF (ctypes.byref (variprojetar))
#
#      Carga de empuxo - CurGlobalData.globalSoilpress
#      
class GlobalSoilPressureData ():

    def __init__ (self, model):
        """
        Dados globais de empuxo\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model      = model

    @property
    def soilPressureLoad (self):
        """
        Carga de empuxo
        """
        caremp          = None
        varcaremp       = ctypes.c_void_p (caremp)
        self.m_model.m_eagme.BASME_DADEDI_CAREMP_LER (ctypes.byref (varcaremp))
        caremp          = varcaremp.value
        nomplafund      = self.m_model.floors.GetFloorName (1)
        floor           = self.m_model.floors.floors [nomplafund]
        if              (floor == None):
            floor       = Floor (self.m_model, nomplafund)
        soilpressure    = SoilPressureLoad (self.m_model, floor, caremp)
        return          soilpressure

#
#      Modos de visualização - model.visData
#      
class VisData ():

    def __init__ (self, model):
        """
        Dados globais de visualização\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    def GetVisModes (self, imode):
        """
        Objeto de modos de visualização\n
            imode       <- Aplicar modos em VISMODE_xxxx
        Retorna:
            visModes    -> Objeto VisModes() para controle de visualização
        """
        varimode        = ctypes.c_int (imode)
        modvis          = None
        varmodvis       = ctypes.c_void_p (modvis)
        self.m_model.m_eagme.BASME_DADEDI_MODVIS_LER (ctypes.byref (varimode), 
                          ctypes.byref (varmodvis))
        modvis          = varmodvis.value
        visModes        = VisModes (self.m_model, modvis)
        return          visModes
#
#      Critérios de referências externas - CurGlobalData.globalRefxData
#
class GlobalRefxData ():

    def __init__ (self, model):
        """
        Critérios de referências externas\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    @property
    def externalReferenceColor (self):
        """
        (1) se referências devem usar cor original
        """
        irefcorori      = 0
        varirefcorori   = ctypes.c_int (irefcorori)
        self.m_model.m_eagme.BASME_DADEDI_IREFCORORI_LER (ctypes.byref (varirefcorori))
        irefcorori      = varirefcorori.value
        return          irefcorori

    @externalReferenceColor.setter
    def externalReferenceColor (self, irefcorori):
        """
        (1) se referências devem usar cor original
        """
        varirefcorori   = ctypes.c_int (irefcorori)
        self.m_model.m_eagme.BASME_DADEDI_IREFCORORI_DEF (ctypes.byref (varirefcorori))

#
#      Vigas - CurGlobalData.globalBeamData
#
class GlobalBeamData ():

    def __init__ (self, model):
        """
        Dados globais de vigas\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    @property
    def beamRestraint (self):
        """
        Objeto de Articulação de viga
        """
        artic           = None
        varartic        = ctypes.c_void_p (artic)
        self.m_model.m_eagme.BASME_DADEDI_ARTIC_LER (ctypes.byref (varartic))
        artic           = varartic.value
        beamRestraintx  = BeamRestraint (self.m_model, artic)
        return          beamRestraintx

    @property
    def firstSlopedBeamNumber (self):
        """
        Numero da primeira viga inclinada
        """
        iprimvigainc    = 0
        variprimvigainc = ctypes.c_int (iprimvigainc)
        self.m_model.m_eagme.BASME_DADEDI_IPRIMVIGAINC_LER (ctypes.byref (variprimvigainc))
        iprimvigainc    = variprimvigainc.value
        return          iprimvigainc

    @firstSlopedBeamNumber.setter
    def firstSlopedBeamNumber (self, iprimvigainc):
        """
        Numero da primeira viga inclinada
        """
        variprimvigainc   = ctypes.c_int (iprimvigainc)
        self.m_model.m_eagme.BASME_DADEDI_IPRIMVIGAINC_DEF (ctypes.byref (variprimvigainc))

    @property
    def slopedBeamIdent (self):
        """
        Identificação de viga inclinada
        """
        identviginc     = None
        varidentviginc  = ctypes.c_void_p (identviginc)
        self.m_model.m_eagme.BASME_DADEDI_IDENTVIGINC_LER (ctypes.byref (varidentviginc))
        identviginc     = varidentviginc.value
        slopedbeamident = SMObjectIdent (self.m_model, identviginc)
        return          slopedbeamident
#
#	Lajes/escadas/rampas - CurGlobalData.globalSlabData
#
class GlobalSlabData ():

    def __init__ (self, model):
        """
        Dados globais de Lajes/escadas/rampas\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    @property
    def stairCase (self):
        """
        Dados de escada
        """
        escdad          = None
        varescdad       = ctypes.c_void_p (escdad)
        self.m_model.m_eagme.BASME_DADEDI_ESCADA_LER (ctypes.byref (varescdad))
        escdad          = varescdad.value
        staircasex      = StairCase (self.m_model, escdad)
        return          staircasex

    @property
    def firstRampNumber (self):
        """
        Número da primeira rampa
        """
        iprimrampa      = 0
        variprimrampa   = ctypes.c_int (iprimrampa)
        self.m_model.m_eagme.BASME_DADEDI_IPRIMRAMPA_LER (ctypes.byref (variprimrampa))
        iprimrampa    = variprimrampa.value
        return          iprimrampa

    @firstRampNumber.setter
    def firstRampNumber (self, iprimrampa):
        """
        Número da primeira rampa
        """
        variprimrampa   = ctypes.c_int (iprimrampa)
        self.m_model.m_eagme.BASME_DADEDI_IPRIMRAMPA_DEF (ctypes.byref (variprimrampa))

    @property
    def volumeOnlySlab (self):
        """
        Laje somente de volume
        """
        lajsovol        = None
        varlajsovol     = ctypes.c_void_p (lajsovol)
        self.m_model.m_eagme.BASME_DADEDI_LAJSOVOL_LER (ctypes.byref (varlajsovol))
        lajsovol        = varlajsovol.value
        volumeonlyslab  = VolumeOnlySlab (self.m_model, lajsovol)
        return          volumeonlyslab

    @property
    def volumeOnlySlabIdent (self):
        """
        Identificador de laje somente de volume
        """
        identrampa      = None
        varidentrampa   = ctypes.c_void_p (identrampa)
        self.m_model.m_eagme.BASME_DADEDI_IDENTRAMPA_LER (ctypes.byref (varidentrampa))
        identrampa      = varidentrampa.value
        volumeonlyslabident = SMObjectIdent (self.m_model, identrampa)
        return          volumeonlyslabident

#
#	Dados de pilares e fundações - CurGlobalData.globalColumnData
#
class GlobalColumnData ():

    def __init__ (self, model):
        """
        Dados globais de eixos\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    def _GetColumnData (self, itipo):
        """
        Dados para criação de pilares e fundações\n
            itipo       <- COLUMNDATA_xxxx
        """
        dadpil          = None
        varitipo        = ctypes.c_int (itipo)
        vardadpil       = ctypes.c_void_p (dadpil)
        self.m_model.m_eagme.BASME_DADEDI_DADPIL_LER (ctypes.byref (varitipo), 
                            ctypes.byref (vardadpil))
        dadpil          = vardadpil.value
        columndata      = ColumnData (self.m_model, dadpil)
        return          columndata

    @property
    def columnData (self):
        """
        Retorna ColumnData () para a criação de pilares
        """
        return          self._GetColumnData (COLUMNDATA_PILARS)

    @property
    def foundationColumnData (self):
        """
        Retorna ColumnData () para a criação de fundações
        """
        return          self._GetColumnData (COLUMNDATA_FUNDAC)

    @property
    def shortColumnData (self):
        """
        Retorna ColumnData () para a criação de pilaretes
        """
        return          self._GetColumnData (COLUMNDATA_PILRTE)
#
#       Dados de fundação
#
    @property
    def foundationData (self):
        """
        Dados de fundação
        """
        fundac          = None
        varfundac       = ctypes.c_void_p (fundac)
        self.m_model.m_eagme.BASME_DADEDI_FUNDAC_LER (ctypes.byref (varfundac))
        fundac          = varfundac.value
        foundationdata  = FoundationData (self.m_model, fundac)
        return          foundationdata

    @property
    def spreadFootingSideWalls (self):
        """
        Sapatas: Valor do colarinho cm
        """
        sapcolar        = 0.
        varsapcolar     = ctypes.c_double (sapcolar)
        self.m_model.m_eagme.BASME_DADEDI_SAPCOLAR_LER (ctypes.byref (varsapcolar))
        sapcolar        = varsapcolar.value
        return          sapcolar

    @spreadFootingSideWalls.setter
    def spreadFootingSideWalls (self, sapcolar):
        """
        Sapatas: Valor do colarinho cm
        """
        varsapcolar   = ctypes.c_double (sapcolar)
        self.m_model.m_eagme.BASME_DADEDI_SAPCOLAR_DEF (ctypes.byref (varsapcolar))

    @property
    def foundationsTopFaceRecess (self):
        """
        Fundações: Valor do rebaixo cm
        """
        fixcotfunddfs   = 0.
        varfixcotfunddfs= ctypes.c_double (fixcotfunddfs)
        self.m_model.m_eagme.BASME_DADEDI_FIXCOTFUNDDFS_LER (ctypes.byref (varfixcotfunddfs))
        fixcotfunddfs   = varfixcotfunddfs.value
        return          fixcotfunddfs

    @foundationsTopFaceRecess.setter
    def foundationsTopFaceRecess (self, fixcotfunddfs):
        """
        Fundações: Valor do rebaixo cm
        """
        varfixcotfunddfs= ctypes.c_double (fixcotfunddfs)
        self.m_model.m_eagme.BASME_DADEDI_FIXCOTFUNDDFS_DEF (ctypes.byref (varfixcotfunddfs))

    @property
    def firstPileNumber (self):
        """
        Fundações: Número de 1a estaca
        """
        iprimestaca     = 0
        variprimestaca  = ctypes.c_int (iprimestaca)
        self.m_model.m_eagme.BASME_DADEDI_IPRIMESTACA_LER (ctypes.byref (variprimestaca))
        iprimestaca     = variprimestaca.value
        return          iprimestaca

    @firstPileNumber.setter
    def firstPileNumber (self, iprimestaca):
        """
        Fundações: Número de 1a estaca
        """
        variprimestaca= ctypes.c_int (iprimestaca)
        self.m_model.m_eagme.BASME_DADEDI_IPRIMESTACA_DEF (ctypes.byref (variprimestaca))

    @property
    def lastPileNumber (self):
        """
        Fundações: Número da última estaca
        """
        iultmestaca     = 0
        variultmestaca  = ctypes.c_int (iultmestaca)
        self.m_model.m_eagme.BASME_DADEDI_IULTMESTACA_LER (ctypes.byref (variultmestaca))
        iultmestaca     = variultmestaca.value
        return          iultmestaca

    @lastPileNumber.setter
    def lastPileNumber (self, iultmestaca):
        """
        Fundações: Número da última estaca
        """
        variultmestaca= ctypes.c_int (iultmestaca)
        self.m_model.m_eagme.BASME_DADEDI_IULTMESTACA_DEF (ctypes.byref (variultmestaca))

#
#	Pré-Moldados - CurGlobalData.globalPrecast
#	
class GlobalPrecastData ():

    def __init__ (self, model):
        """
        Dados globais de pré-moldados\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model
        
    @property
    def precastRegion (self):
        """
        Pré-moldados: Região construtiva
        """
        iregiao         = 0
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_DADEDI_IREGIAO_LER (ctypes.byref (variregiao))
        iregiao         = variregiao.value
        return          iregiao

    @precastRegion.setter
    def precastRegion (self, iregiao):
        """
        Pré-moldados: Região construtiva
        """
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_DADEDI_IREGIAO_DEF (ctypes.byref (variregiao))

    @property
    def corbelData (self):
        """
        Pré-moldados: Dados de consolo
        """
        consolo         = None
        varconsolo      = ctypes.c_void_p (consolo)
        self.m_model.m_eagme.BASME_DADEDI_CONSOLO_LER (ctypes.byref (varconsolo))
        consolo         = varconsolo.value
        corbeldata      = CorbelData (self.m_model, consolo)
        return          corbeldata

    @property
    def initialCorbelIdent (self):
        """
        Pré-moldados: Identificação inicial de consolos (char *)
        """
        varidentcons    = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADEDI_IDENTCONS_LER (varidentcons)
        identcons       = varidentcons.value.decode(TQSUtil.CHARSET)
        return          identcons

    @initialCorbelIdent.setter
    def initialCorbelIdent (self, identcons):
        """
        Pré-moldados: Identificação inicial de consolos (char *)
        """
        varidentcons      = ctypes.c_char_p (identcons.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADEDI_IDENTCONS_DEF (varidentcons)

    @property
    def reinforcementConfig (self):
        """
        Pré-moldados: Prefixo padrão de alojamento de armaduras em elementos alveolares
        """
        varprefaljp     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADEDI_PREFALJP_LER (varprefaljp)
        prefaljp        = varprefaljp.value.decode(TQSUtil.CHARSET)
        return          prefaljp

    @reinforcementConfig.setter
    def reinforcementConfig (self, prefaljp):
        """
        Pré-moldados: Prefixo padrão de alojamento de armaduras em elementos alveolares
        """
        varprefaljp     = ctypes.c_char_p (prefaljp.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADEDI_PREFALJP_DEF (varprefaljp)

    @property
    def precastInsertWidth (self):
        """
        Pré-moldados: Largura do inserto simples cm
        """
        alarginsr       = 0.
        varalarginsr    = ctypes.c_double (alarginsr)
        self.m_model.m_eagme.BASME_DADEDI_ALARGINSR_LER (ctypes.byref (varalarginsr))
        alarginsr       = varalarginsr.value
        return          alarginsr

    @precastInsertWidth.setter
    def precastInsertWidth (self, alarginsr):
        """
        Pré-moldados: Largura do inserto simples cm
        """
        varalarginsr      = ctypes.c_double (alarginsr)
        self.m_model.m_eagme.BASME_DADEDI_ALARGINSR_DEF (ctypes.byref (varalarginsr))

    @property
    def precastInsertLenght (self):
        """
        Pré-moldados: Comprimento do inserto simples cm
        """
        comprinsr       = 0.
        varcomprinsr    = ctypes.c_double (comprinsr)
        self.m_model.m_eagme.BASME_DADEDI_COMPRINSR_LER (ctypes.byref (varcomprinsr))
        comprinsr       = varcomprinsr.value
        return          comprinsr

    @precastInsertLenght.setter
    def precastInsertLenght (self, comprinsr):
        """
        Pré-moldados: Comprimento do inserto simples cm
        """
        varcomprinsr      = ctypes.c_double (comprinsr)
        self.m_model.m_eagme.BASME_DADEDI_COMPRINSR_DEF (ctypes.byref (varcomprinsr))

    @property
    def precastInsertHeight (self):
        """
        Pré-moldados: Espessura do inserto simples cm
        """
        alturinsr       = 0.
        varalturinsr    = ctypes.c_double (alturinsr)
        self.m_model.m_eagme.BASME_DADEDI_ALTURINSR_LER (ctypes.byref (varalturinsr))
        alturinsr       = varalturinsr.value
        return          alturinsr

    @precastInsertHeight.setter
    def precastInsertLenght (self, alturinsr):
        """
        Pré-moldados: Espessura do inserto simples cm
        """
        varalturinsr      = ctypes.c_double (alturinsr)
        self.m_model.m_eagme.BASME_DADEDI_ALTURINSR_DEF (ctypes.byref (varalturinsr))

    @property
    def facadeData (self):
        """
        Pré-moldados: Dados de fachada
        """
        fachada         = None
        varfachada      = ctypes.c_void_p (fachada)
        self.m_model.m_eagme.BASME_DADEDI_FACHADA_LER (ctypes.byref (varfachada))
        fachada         = varfachada.value
        facadedata      = FacadeData (self.m_model, fachada)
        return          facadedata
#
#       Atributos BIM - CurGlobalData.globalBimData
#
class GlobalBimData ():

    def __init__ (self, model):
        """
        Dados globais BIM\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    def GetUserAttrib (self, itypeattrib):
        """
        Atributos de usuário\n
            itypeattrib <- BIM_USRATRTP_xxxx
        """
        varitipoatrib   = ctypes.c_int (itypeattrib)
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        self.m_model.m_eagme.BASME_DADEDI_USRATRIB_LER (ctypes.byref (varitipoatrib),
                ctypes.byref (varusratrib))
        usratrib        = varusratrib.value
        userattrib      = UserAttrib (self.m_model, usratrib)
        return          userattrib

    @property
    def globalAttrib (self):
        """
        Atributos BIM globais\n
            itypeattrib <- (0)Pilar (1) Fundação (2)Viga (3)Laje (4)Elem 3D
        """
        glbatrib        = None
        varglbatrib     = ctypes.c_void_p (glbatrib)
        self.m_model.m_eagme.BASME_DADEDI_GLBATRIB_LER (ctypes.byref (varglbatrib))
        glbatrib        = varglbatrib.value
        globalattrib    = GlobalAttrib (self.m_model, glbatrib)
        return          globalattrib

#-----------------------------------------------------------------------------
#       Furo em pilar
#
class GlobalColumnOpening ():

    def __init__ (self, model):
        """
        Furo em pilar\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model

    @property
    def columnOpening (self):
        """
        Furo em pilar
        """
        furopil         = None
        varfuropil      = ctypes.c_void_p (furopil)
        self.m_model.m_eagme.BASME_DADEDI_FUROPIL_LER (ctypes.byref (varfuropil))
        furopil         = varfuropil.value
        columnopening   = ColumnOpening (self.m_model, furopil)
        return          columnopening
    
#-----------------------------------------------------------------------------
#       Estaca de laje radier - CurGlobalData.globalSlabFPile
#
class GlobalSlabFoundationPile ():

    def __init__ (self, model):
        """
        Dados de uma estaca para laje radier\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model
#
#	Uma estaca de radier p/servir de modelo
#
    @property
    def slabFoundationPile (self):
        """
        Dados de uma estaca para laje radier
        Dados atuais definidos:
            model.current.column.slabFoundationPile\n
        """
        estacrad        = None
        varestacrad     = ctypes.c_void_p (estacrad)
        self.m_model.m_eagme.BASME_DADEDI_ESTACRAD_LER (ctypes.byref (varestacrad))
        estacrad        = varestacrad.value
        slabfoundationpile = SlabFoundationPile (self.m_model, estacrad)
        return          slabfoundationpile


#-----------------------------------------------------------------------------
#      Rotinas que manipulam a lista de plantas
#
class FloorsList ():

    def __init__ (self, model):
        """
        Classe de manipulação de plantas e seu conteúdo\n
            model       <- Objeto Model() do modelo atual
        """
        self.m_model    = model
        self.floors     = dict ()    # [nompla] = Floor ()

    def GetFloor (self, nompla):
        """
        Define a planta atual e retorna um objeto Floor() de planta\n
            nompla      <- (string) Nome da planta\n
        Retorna:\n
            Objeto Floor, com dados de uma planta
        """
        floor           = Floor (self.m_model, nompla)
        return          floor

    def GetNumFloors (self):
        """
        Retorna o número de plantas do edifício
        """
        numplantas      = 0
        varnumplantas   = ctypes.c_int (numplantas)
        self.m_model.m_eagme.INTME_NUMPLANTAS (ctypes.byref (varnumplantas))
        numplantas      = varnumplantas.value
        return          numplantas

    def GetFloorName (self, indpla):
        """
        Nome de uma planta\n
            indpla      <- Índice da planta 1..GetNumFloors()
        """
        varindpla       = ctypes.c_int (indpla)
        varnompla       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.INTME_LERPLANTA (ctypes.byref (varindpla),
                            varnompla)
        nompla          = varnompla.value.decode(TQSUtil.CHARSET)
        return          nompla

    def GetFloorIndex (self, nompla):
        """
        Índice da planta\n
            nompla      <- (string) Nome da planta\n
        Retorna:
            indpla      <- Índice da planta 1..GetNumFloors() ou zero
        """
        varnompla       = ctypes.c_char_p (nompla.encode (TQSUtil.CHARSET))
        indpla          = 0
        varindpla       = ctypes.c_int (indpla)
        self.m_model.m_eagme.INTME_LERINDPLA (varnompla, ctypes.byref (varindpla))
        indpla          = varindpla.value
        return          indpla

    
    def _EnterFloor (self, nompla, floor):
        """
        Associa nome da planta nompla com objeto Floor
        """
        self.floors [nompla] = floor

#-----------------------------------------------------------------------------
#      Planta que contém objetos
#
class Floor ():

    def __init__ (self, model, nompla):
        """
        Classe com dados de uma planta e seus objetos\n
            model       <- Objeto Model() do modelo atual\n
            nompla      <- (string) Nome da planta
        """
        self.m_model    = model
        self.m_nompla   = nompla
        self.m_fabrica  = None
        pvistav         = None
        if              (self.m_model.m_tqsjan != None):
            pvistav     = self.m_model.m_tqsjan.m_pvistav
        varpvistav      = ctypes.c_void_p (pvistav)
        varnompla       = ctypes.c_char_p (nompla.encode (TQSUtil.CHARSET))
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.INTME_ABRIRMODELOPLANTA (ctypes.byref (varpvistav), varnompla, 
                        ctypes.byref (varfabrica), ctypes.byref (varistat))
        istat           = varistat.value
        if              (istat != 0):
            TQSUtil.writef ("Erro abrindo a planta [%s]" % nompla)
            exit        ()
        self.m_fabrica  = varfabrica.value
        self.m_model.floors._EnterFloor (nompla, self)

        self.current    = CurrentFloorData (self.m_model, self)
        self.create     = SMOCreate (self.m_model, self.m_fabrica)
        self.iterator   = SMOIterator (self.m_model, self.m_fabrica)
        self.util       = FloorUtil (self.m_model, self.m_fabrica)

#-----------------------------------------------------------------------------
#      Criação de objetos estruturais em uma planta
#
class SMOCreate ():

    def __init__ (self, model, fabrica):
        """
        Classe com dados de uma planta e seus objetos\n
            model       <- Objeto Model() do modelo atual\n
            fabrica     <- Handle de acesso à planta no Modelador
        """
        self.m_model    = model
        self.m_fabrica  = fabrica

    def _CreateColumnType (self, itipo, xins, yins):
        """
        Criação de um pilar/fundação/pilarete\n
            int itipo   <- Tipo COLUMNDATA_xxxxxx\n
            double xins <- Ponto de inserção\n
            double yins <- Ponto de inserção
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varitipo        = ctypes.c_int (itipo)
        varxins         = ctypes.c_double (xins)
        varyins         = ctypes.c_double (yins)
        pilar           = None
        varpilar        = ctypes.c_void_p (pilar)
        self.m_model.m_eagme.BASME_PILARES_CRIAR (ctypes.byref (varfabrica),
                ctypes.byref (varitipo), ctypes.byref (varxins), ctypes.byref (varyins), 
                ctypes.byref (varpilar))
        pilar           = varpilar.value
        return          Column (self.m_model, self, pilar)


    def CreateColumn (self, xins, yins):
        """
        Criação de um pilar\n
            double xins <- Ponto de inserção\n
            double yins <- Ponto de inserção\n
        Outras variáveis usadas na criação de um pilar:\n
            model       = TQSModel.Model ()\n
            model.current.globalBimData.userAttrib\n
            model.current.globalBimData.globalAttrib\n
            model.current.globalColumnData.foundationData\n
            model.current.globalColumnData.spreadFootingSideWalls\n
            model.current.globalColumnData.foundationsTopFaceRecess\n
            model.current.globalColumnData.firstPileNumber\n
            model.current.globalColumnData.lastPileNumber\n
            model.current.globalColumnData.columnData / foundationColumnData / shortColumnData\n
            columnData.columnDetailing\n
            columnData.columnGeometry\n
            columnData.columnInsertion\n
            columnData.columnPolygon\n
            columnData.columnCoil\n
            columnData.columnIdent\n
            columnData.columnPrecastData\n
            columnData.columnStarts\n
            columnData.columnModel\n
            columnData.columnWindSupport\n
            columnData.columnSectionMode\n
            columnData.columnInterference\n
            columnData.columnSloped\n
            columnData.columnIsAFoundation\n
            columnData.columnHinges\n
            columnData.columnExport\n
            columnData.columnNonLinearity\n
            columnData.columnBucklingX\n
            columnData.columnBucklingY\n
            columnData.columnDoubleStoryX\n
            columnData.columnDoubleStoryY\n
            columnData.columnConcreteFc\n
            columnData.columnExport\n
            floor = model.floors.GetFloor ("nome-da-planta")\n
            floor.current.column.columnFloorNames\n
            floor.current.column.columnBoundaryCond\n
            floor.current.column.columnCover\n
            floor.current.column.columnExposure\n
            floor.current.column.columnDynHorLoad\n
        Retorna:\n
        Objeto tipo Column()
        """
        itipo           = COLUMNDATA_PILARS
        return          self._CreateColumnType (itipo, xins, yins)

    def CreateShortColumn (self, xins, yins):
        """
        Criação de um pilarete\n
        Veja em CreateColumn as variáveis pré-definidas\n
            double xins <- Ponto de inserção X\n
            double yins <- Ponto de inserção Y\n
        Retorna:\n
        Objeto tipo Column()
        """
        itipo           = COLUMNDATA_PILRTE
        return          self._CreateColumnType (itipo, xins, yins)

    def CreateFoundation (self, xins, yins):
        """
        Criação de uma fundação\n
        Veja em CreateColumn as variáveis pré-definidas\n
            double xins <- Ponto de inserção X\n
            double yins <- Ponto de inserção Y\n
        Retorna:\n
        Objeto tipo Column()
        """
        itipo           = COLUMNDATA_FUNDAC
        return          self._CreateColumnType (itipo, xins, yins)

    def CreateBeam (self, xy):
        """
        Cria viga no plano\n
            xy  ((x1,y1),(x2,y2)...)    coordenadas da viga
        Outras variáveis usadas na criação de um pilar:\n
            model       = TQSModel.Model ()\n
            model.current.globalBeamData.beamRestraint\n
            model.current.globalBeamData.firstSlopedBeamNumber\n
            model.current.globalBeamData.slopedBeamIdent\n
            model.current.globalBimData.userAttrib\n
            floor = model.floors.GetFloor ("nome-da-planta")\n
            floor.current.floorBeamData.beamGeometry\n
            floor.current.floorBeamData.beamInertia\n
            floor.current.floorBeamData.beamBond\n
            floor.current.floorBeamData.beamInsertion\n
            floor.current.floorBeamData.beamTemperShrink\n
            floor.current.floorBeamData.beamDetailing\n
            floor.current.floorBeamData.beamExport\n
            floor.current.floorLoadData.load\n
        Retorna:\n
        Objeto tipo Beam()
        """
        self.m_model.m_eagme.BASME_VIGAS_PONTOS_LIMPAR ()
        for             coords in xy:
            varxvig     = ctypes.c_double (coords [0])
            varyvig     = ctypes.c_double (coords [1])
            self.m_model.m_eagme.BASME_VIGAS_ENTRARPONTO (ctypes.byref (varxvig), 
                            ctypes.byref (varyvig))

        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        inclinada       = 0
        varinclinada    = ctypes.c_int (inclinada)
        info3d          = None
        varinfo3d       = ctypes.c_void_p (info3d)
        viga            = None
        varviga         = ctypes.c_void_p (viga)
        self.m_model.m_eagme.BASME_VIGAS_CRIAR_PONTOS (ctypes.byref (varfabrica), 
                            ctypes.byref (varinclinada), ctypes.byref (varinfo3d),
                            ctypes.byref (varviga))
        viga            = varviga.value
        return          Beam (self.m_model, viga)

    def CreateBeamOpening (self, beam, xins, yins):
        """
        Cria um furo horizontal em viga\n
            beam        <- Objeto da viga\n
            xins,yins   <- Centro do furo em planta no eixo da viga\n
        Outras variáveis usadas na criação de um furo em viga\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            floor.floorBeamData.beamOpening\n
        Retorna:\n
        Objeto tipo BeamOpening()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varviga         = ctypes.c_void_p (beam.m_viga)
        varxins         = ctypes.c_double (xins)
        varyins         = ctypes.c_double (yins)
        furovig         = None
        varfurovig      = ctypes.c_void_p (furovig)
        self.m_model.m_eagme.BASME_FUROVIG_CRIAR (ctypes.byref (varfabrica), 
                            ctypes.byref (varviga), ctypes.byref (varxins), 
                            ctypes.byref (varyins), ctypes.byref (varfurovig))
        furovig         = varfurovig.value
        return          BeamOpening (self.m_model, furovig)

    def CreateSlabContour (self, x1, y1, x2, y2):
        """
        Cria contorno auxiliar de laje - bordo livre\n
            x1,y1,x2,y2 <- Coordenadas da linha cm\n
        Retorna:\n
        Objeto tipo SlabContour()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varx1           = ctypes.c_double (x1)
        vary1           = ctypes.c_double (y1)
        varx2           = ctypes.c_double (x2)
        vary2           = ctypes.c_double (y2)
        info3d          = None
        varinfo3d       = ctypes.c_void_p (info3d)
        ctraux          = None
        varctraux       = ctypes.c_void_p (ctraux)
        self.m_model.m_eagme.BASME_CTRAUX_CRIAR (ctypes.byref (varfabrica), 
                            ctypes.byref (varx1), ctypes.byref (vary1),
                            ctypes.byref (varx2), ctypes.byref (vary2),
                            ctypes.byref (varinfo3d), ctypes.byref (varctraux))
        ctraux          = varctraux.value
        return          SlabContour (self.m_model, ctraux)

    def CreateSlab (self, xins, yins, angpri):
        """
        Cria laje dentro de contorno formado por vigas, pilares ou contorno auxiliar\n
            double xins         <- Ponto dentro da laje\n
            double yins         <- Ponto dentro da laje\n
            double angpri       <- Ângulo principal, graus\n
        Outras variáveis usadas na criação de uma laje:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            model.current.globalSlabData.stairCase\n
            model.current.globalSlabData.firstRampNumber\n
            floor.current.floorSlabData.slabIdent\n
            floor.current.floorSlabData.slabFirstNumber\n
            floor.current.floorLoadData.GetLoad\n
            floor.current.floorSlabData.slabGeometry\n
            floor.current.floorSlabData.slabGrid\n
            floor.current.floorSlabData.stairTitle\n
            floor.current.floorSlabData.slabExport\n
            floor.current.floorSlabData.slabDetailing\n
        Retorna:\n
        Objeto tipo Slab()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        irampa          = 0
        varirampa       = ctypes.c_int (irampa)
        iescada         = 0
        variescada      = ctypes.c_int (iescada)
        ipatamar        = 0
        varipatamar     = ctypes.c_int (ipatamar)
        varxins           = ctypes.c_double (xins)
        varyins           = ctypes.c_double (yins)
        varangpri         = ctypes.c_double (angpri)
        info3d          = None
        varinfo3d       = ctypes.c_void_p (info3d)
        lajeinc         = None
        varlajeinc      = ctypes.c_void_p (lajeinc)
        laje            = None
        varlaje         = ctypes.c_void_p (laje)
        self.m_model.m_eagme.BASME_LAJES_CRIAR (ctypes.byref (varfabrica), 
                            ctypes.byref (varirampa), ctypes.byref (variescada), 
                            ctypes.byref (varipatamar), ctypes.byref (varxins), 
                            ctypes.byref (varyins), ctypes.byref (varangpri), 
                            ctypes.byref (varinfo3d), ctypes.byref (varlajeinc), 
                            ctypes.byref (varlaje))
        laje            = varlaje.value
        return          Slab (self.m_model, laje)

    def CreateDropPanel (self, polig):
        """
        Cria capitel\n
            Polygon polig       <- Poligonal fechada que define o capitel\n
        Outras variáveis usadas na criação de um capitel:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            floor.current.floorSlabData.dropPanelThickness\n
            floor.current.floorSlabData.dropPanelDiv\n
        Retorna:\n
        Objeto tipo DropPanel()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varpolig        = ctypes.c_void_p (polig.m_polig)
        capitel         = None
        varcapitel      = ctypes.c_void_p (capitel)
        self.m_model.m_eagme.BASME_CAPITEIS_CRIAR (ctypes.byref (varfabrica), 
                            ctypes.byref (varpolig), ctypes.byref (varcapitel))
        capitel         = varcapitel.value
        return          DropPanel (self.m_model, capitel)

    def CreateSlabMould (self, slab, xnerv, ynerv):
        """
        Cria uma forma/cubeta de laje nevurada\n
            Slab slab           <- Laje onde vai a forma\n
            double xnerv        <- Posição do centro da forma\n
            double ynerv        <- Posição do centro da forma\n
        Outras variáveis usadas na criação de uma forma de nervura:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            floor.current.floorSlabData.slabMouldXSize\n
            floor.current.floorSlabData.slabMouldYSize\n
            floor.current.floorSlabData.slabMouldXSpace\n
            floor.current.floorSlabData.slabMouldYSpace\n
            floor.current.floorSlabData.slabMouldBasePoint\n
        Retorna:\n
        Objeto tipo SlabMould()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varlaje         = ctypes.c_void_p (slab.m_laje)
        varxnerv        = ctypes.c_double (xnerv)
        varynerv        = ctypes.c_double (ynerv)
        forner          = None
        varforner       = ctypes.c_void_p (forner)
        self.m_model.m_eagme.BASME_FORNER_CRIAR (ctypes.byref (varfabrica), 
                            ctypes.byref (varlaje), ctypes.byref (varxnerv), 
                            ctypes.byref (varynerv), ctypes.byref (varforner))
        forner          = varforner.value
        return          SlabMould (self.m_model, forner)

    def CreateSlabOpening (self, polig, irecorte, isobrecapa):
        """
        Cria capitel\n
            Polygon polig       <- Poligonal fechada que define o furo em planta\n
            int irecorte        <- (0) Furo (respeita nervuras) (1) Recorte\n
            int isobrecapa      <- (0) Normal (1) Só na capa de laje nervurada\n
        Retorna:\n
        Objeto tipo SlabOpening()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varpolig        = ctypes.c_void_p (polig.m_polig)
        varirecorte     = ctypes.c_int (irecorte)
        varisobrecapa   = ctypes.c_int (isobrecapa)
        furo            = None
        varfuro         = ctypes.c_void_p (furo)
        self.m_model.m_eagme.BASME_FUROS_CRIAR (ctypes.byref (varfabrica), 
                            ctypes.byref (varpolig), ctypes.byref (varirecorte),
                            ctypes.byref (varisobrecapa), ctypes.byref (varfuro))
        furo            = varfuro.value
        return          SlabOpening (self.m_model, furo)


    def CreateSoilPressureLoad (self, xini, yini, xfin, yfin):
        """
        Cria uma carga de empuxo\n
            xini        <- Ponto inicial X\n
            yini        <- Ponto inicial Y\n
            xfin        <- Ponto final   X\n
            yfin        <- Ponto final   X\n
        Os valores de cargas devem ser definidos primeiro em:\n
            model       = TQSModel.Model ()\n
            model.current.globalSoilpress.soilPressureLoad\n
        Retorna:\n
            Objeto tipo SoilPressureLoad()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varxini         = ctypes.c_double (xini)
        varyini         = ctypes.c_double (yini)
        varxfin         = ctypes.c_double (xfin)
        varyfin         = ctypes.c_double (yfin)
        caremp          = None
        varcaremp       = ctypes.c_void_p (caremp)
        self.m_model.m_eagme.BASME_CAREMP_CRIAR (ctypes.byref (varfabrica), 
                        ctypes.byref (varxini), ctypes.byref (varyini), 
                        ctypes.byref (varxfin), ctypes.byref (varyfin), ctypes.byref (varcaremp))
        caremp          = varcaremp.value
        soilPressureLoad = SoilPressureLoad (self.m_model, self, caremp)
        return          soilPressureLoad

    def CreateAdditionalLoad (self, xins, yins):
        """
        Cria carga adicional em laje\n
            double xins         <- Ponto na laje com o símbolo da carga\n
            double yins         <- Ponto na laje com o símbolo da carga\n
        O valor da carga deve ser definido primeiro em:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            load        = floor.current.floorLoadData.GetLoad (TPLOAD_CARADI)\n
        Retorna:\n
        Objeto tipo AdditionalLoad()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varxins         = ctypes.c_double (xins)
        varyins         = ctypes.c_double (yins)
        caradi          = None
        varcaradi       = ctypes.c_void_p (caradi)
        self.m_model.m_eagme.BASME_CARADI_CRIAR (ctypes.byref (varfabrica), 
                        ctypes.byref (varxins), ctypes.byref (varyins), 
                        ctypes.byref (varcaradi))
        caradi          = varcaradi.value
        additionalLoad  = AdditionalLoad (self.m_model, self, caradi)
        return          additionalLoad


    def CreateAreaDistributedLoad (self, polig):
        """
        Cria distribuída em laje dentro de uma poligonal fechada tf/m2\n
            Polygon polig       <- Poligonal onde a área é aplicada\n
        O valor da carga deve ser definido primeiro em:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            load        = floor.current.floorLoadData.GetLoad (TPLOAD_CARARE)\n
        Retorna:\n
        Objeto tipo AreaDistributedLoad()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varpolig        = ctypes.c_void_p (polig.m_polig)
        carare          = None
        varcarare       = ctypes.c_void_p (carare)
        self.m_model.m_eagme.BASME_CARARE_CRIAR (ctypes.byref (varfabrica), 
                        ctypes.byref (varpolig), ctypes.byref (varcarare))
        carare          = varcarare.value
        areaDistributedLoad = AreaDistributedLoad (self.m_model, self, carare)
        return          areaDistributedLoad

    def CreateConcentratedLoad (self, xins, yins):
        """
        Cria carga concentrada tf\n
            double xins <- Ponto na laje com o símbolo da carga\n
            double yins <- Ponto na laje com o símbolo da carga\n
        O valor da carga deve ser definido primeiro em:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            load        = floor.current.floorLoadData.GetLoad (\n
                        TPLOAD_FORCFX/TPLOAD_FORCFY/TPLOAD_FORCFZ/TPLOAD_FORCMX/TPLOAD_FORCMY)\n
        Retorna:\n
        Objeto tipo ConcentratedLoad()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varxins         = ctypes.c_double (xins)
        varyins         = ctypes.c_double (yins)
        carcon          = None
        varcarcon       = ctypes.c_void_p (carcon)
        self.m_model.m_eagme.BASME_CARCON_CRIAR (ctypes.byref (varfabrica), 
                        ctypes.byref (varxins), ctypes.byref (varyins), 
                        ctypes.byref (varcarcon))
        carcon          = varcarcon.value
        concentratedLoad = ConcentratedLoad (self.m_model, self, carcon)
        return          concentratedLoad

    def CreateLinearyDistributedLoad (self, xins1, yins1, xins2, yins2):
        """
        Cria linear tf/m sobre viga ou laje\n
            double xins1        <- Ponto inicial na laje com o símbolo da carga\n
            double yins1        <- Ponto inicial na laje com o símbolo da carga\n
            double xins2        <- Ponto final   na laje com o símbolo da carga\n
            double yins2        <- Ponto final   na laje com o símbolo da carga\n
        O valor da carga deve ser definido primeiro em:\n
            model       = TQSModel.Model ()\n
            floor       = model.floors.GetFloor ("nome-da-planta")\n
            load        = floor.current.floorLoadData.GetLoad (TPLOAD_CARLIN)\n
        Retorna:\n
        Objeto tipo LinearyDistributedLoad()
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varxins1        = ctypes.c_double (xins1)
        varyins1        = ctypes.c_double (yins1)
        varxins2        = ctypes.c_double (xins2)
        varyins2        = ctypes.c_double (yins2)
        carlin          = None
        varcarlin       = ctypes.c_void_p (carlin)
        self.m_model.m_eagme.BASME_CARLIN_CRIAR (ctypes.byref (varfabrica), 
                        ctypes.byref (varxins1), ctypes.byref (varyins1), 
                        ctypes.byref (varxins2), ctypes.byref (varyins2), 
                        ctypes.byref (varcarlin))
        carlin          = varcarlin.value
        linearyDistributedLoad = LinearyDistributedLoad (self.m_model, self, carlin)
        return          linearyDistributedLoad

#-----------------------------------------------------------------------------
#      Iteração pelos elementos de uma lista de objetos
#
class SMOIterator ():

    def __init__ (self, model, fabrica):
        """
        Classe com dados de uma planta e seus objetos\n
            model       <- Objeto Model() do modelo atual\n
            fabrica     <- Handle de acesso à planta no Modelador
        """
        self.m_model    = model
        self.m_fabrica  = fabrica


    def GetNumObjects (self, itype):
        """
        Retorna o número de objetos de uma lista de uma planta\n
            itype       <- (int) TYPE_xxxx\n
        Retorna:\n
            Número de objetos deste tipo
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varitype        = ctypes.c_int (itype)
        numobjetos      = 0
        varnumobjetos   = ctypes.c_int (numobjetos)
        self.m_model.m_eagme.BASME_PLANTA_NUMOBJETOS (ctypes.byref (varfabrica),
                        ctypes.byref (varitype), ctypes.byref (varnumobjetos))
        numobjetos      = varnumobjetos.value
        return          numobjetos


    def GetObject (self, itype, iobject):
        """
        Retorna um objeto de uma lista\n
            itype       <- (int) TYPE_xxxx\n
            int iobject <- 0..GetNumObjects()-1\n
        Retorna:\n
            smobject    -> Objeto derivado de SMObject ou None
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varitype        = ctypes.c_int (itype)
        variobject      = ctypes.c_int (iobject)
        objme           = None
        varobjme        = ctypes.c_void_p (objme)
        self.m_model.m_eagme.BASME_PLANTA_LEROBJETO (ctypes.byref (varfabrica),
                        ctypes.byref (varitype), ctypes.byref (variobject),
                        ctypes.byref (varobjme))
        objme           = varobjme.value

        if              (itype == TYPE_VIGAS):
            return      Beam (self.m_model, objme)

        if              (itype == TYPE_PILARES):
            return      Column (self.m_model, self, objme)

        if              (itype == TYPE_LAJES):
            return      Slab (self.m_model, objme)

        if              (itype == TYPE_FUNDAC):
            return      Column (self.m_model, objme)

        if              (itype == TYPE_FUROS):
            return      SlabOpening (self.m_model, objme)

        if              (itype == TYPE_CAPITEIS):
            return      DropPanel (self.m_model, objme)

        if              (itype == TYPE_FORNER):
            return      SlabMould (self.m_model, objme)

        if              (itype == TYPE_CTRAUX):
            return      SlabContour (self.m_model, objme)

        if              (itype == TYPE_EIXOS):
            pass

        if              (itype == TYPE_COTAGENS):
            pass

        if              (itype == TYPE_CORTES):
            pass

        if              (itype == TYPE_DADPAV):
            pass

        if              (itype == TYPE_DADEDI):
            pass

        if              (itype == TYPE_SECPIL):
            return      ColumnSection (None, self.m_model, self, objme)

        if              (itype == TYPE_LISMAL):
            pass

        if              (itype == TYPE_CARCON):
            return      ConcentratedLoad (self.m_model, objme)

        if              (itype == TYPE_CARLIN):
            return      LinearyDistributedLoad (self.m_model, objme)

        if              (itype == TYPE_CARARE):
            return      AreaDistributedLoad (self.m_model, objme)

        if              (itype == TYPE_BARICEN):
            pass

        if              (itype == TYPE_CARADI):
            return      AdditionalLoad (self.m_model, objme)

        if              (itype == TYPE_RAMPAS):
            pass

        if              (itype == TYPE_ORIEIX):
            pass

        if              (itype == TYPE_TABNP):
            pass

        if              (itype == TYPE_IDCLI):
            pass

        if              (itype == TYPE_CONSBIB):
            pass

        if              (itype == TYPE_FUROVIG):
            return      BeamOpening (self.m_model, objme)

        if              (itype == TYPE_ELMLJP):
            pass

        if              (itype == TYPE_TABELEM):
            pass

        if              (itype == TYPE_COTDIA):
            pass

        if              (itype == TYPE_COTANG):
            pass

        if              (itype == TYPE_COTNOT):
            pass

        if              (itype == TYPE_VENDST):
            pass

        if              (itype == TYPE_CENTOR):
            pass

        if              (itype == TYPE_CONSIND):
            pass

        if              (itype == TYPE_CAREMP):
            return      SoilPressureLoad (self.m_model, objme)

        if              (itype == TYPE_TABNIVPAV):
            pass

        if              (itype == TYPE_LEGDESNIV):
            pass

        if              (itype == TYPE_SIMDESNIV):
            pass

        if              (itype == TYPE_ELM3D):
            pass

        if              (itype == TYPE_INSRBLO):
            pass

        if              (itype == TYPE_INSRPOS):
            pass

        if              (itype == TYPE_FACHADA):
            pass

        if              (itype == TYPE_TUBOS):
            pass

        if              (itype == TYPE_FUROPIL):
            pass

        if              (itype == TYPE_LAJESSOVOL):
            pass

        if              (itype == TYPE_ESTACRAD):
            pass

        if              (itype == TYPE_VIGASINC):
            pass

        if              (itype == TYPE_PILARETES):
            pass

        if              (itype == TYPE_ESCADAS):
            pass

        if              (itype == TYPE_PATAMARES):
            pass

        if              (itype == TYPE_ORIBARI):
            pass

        if              (itype == TYPE_EDIEDI):
            pass

        if              (itype == TYPE_PTBAS):
            pass

        if              (itype == TYPE_PTLVT):
            pass

        if              (itype == TYPE_CERCATOR):
            pass

        return          None

    def FindObject (self, identobj):
        """    
        Acha um objeto dado seu identificador único\n
            identobj    <- (int) Identificador único de um objeto\n
        Retorna:\n
            objme       -> Objeto ou NULL se não achar\n
            itype       -> Tipo do objeto TYPE_xxxx\n
            index       -> Índice de acesso\n
            istat       -> (0) Ok (1) Não achou
        """    
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        variuniqueid    = ctypes.c_int (identobj)
        objme           = None
        varobjme        = ctypes.c_void_p (objme)
        itype           = 0
        varitype        = ctypes.c_int (itype)
        index           = 0
        varindex        = ctypes.c_int (index)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_PLANTA_ACHAROBJETO (ctypes.byref (varfabrica), 
                        ctypes.byref (variuniqueid), ctypes.byref (varobjme), ctypes.byref (varitype), 
                        ctypes.byref (varindex), ctypes.byref (varistat))
        objme           = varobjme.value
        itype           = varitype.value
        index           = varindex.value
        istat           = varistat.value
        return          objme, itype, index, istat

#------------------------------------------------------------------------------
#       Rotinas utilitárias do pavimento
#
class FloorUtil ():

    def __init__ (self, model, fabrica):
        """
        Classe de rotinas utilitárias do pavimento\n
            model       <- Objeto Model() do modelo atual\n
            fabrica     <- Handle de acesso à planta no Modelador
        """
        self.m_model    = model
        self.m_fabrica  = fabrica

    def DoIntersections (self):
        """
        Refaz as intersecções de vigas, pilares e lajes em uma planta
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        self.m_model.m_eagme.BASME_PLANTA_REFAZERINTERSEC (ctypes.byref (varfabrica))


    def DistributeSlabMould (self, slab, slabMould):
        """
        Distribui formas de laje nervurada em uma laje, a partir de uma fornecida\n
            Slab slab           <- Laje onde será feita a distribuição\n
            SlabMould slabMould <- Forma de nervura como semente
        """
        varfabrica      = ctypes.c_void_p (self.m_fabrica)
        varlaje         = ctypes.c_void_p (slab.m_laje)
        varforner       = ctypes.c_void_p (slabMould.m_forner)
        self.m_model.m_eagme.BASME_FORNER_DISTRIBUIR (ctypes.byref (varfabrica), 
                            ctypes.byref (varlaje), ctypes.byref (varforner))

#------------------------------------------------------------------------------
#       Objeto poligonal usado em vários tipos de objetos
#
class Polygon ():

    def __init__ (self, model, polig=None):
        """
        Cria objeto poligonal vazio. Se polig != None, usa polig, senão cria novo
        """
        self.m_model    = model
        self.m_polig    = None
        if              (polig is None):
            varpolig    = ctypes.c_void_p (self.m_polig)
            self.m_model.m_eagme.BASME_POLIG_LER (ctypes.byref (varpolig))
            self.m_polig= varpolig.value
        else:
            self.m_polig= polig

    def Clear (self):
        """
        Esvazia uma poligonal
        """
        varpolig        = ctypes.c_void_p (self.m_polig)
        self.m_model.m_eagme.BASME_POLIG_LIMPAR (ctypes.byref (varpolig))

    def NumPts (self):
        """
        Retorna o número de pontos
        """
        varpolig        = ctypes.c_void_p (self.m_polig)
        numpts          = 0
        varnumpts      = ctypes.c_int (numpts)
        self.m_model.m_eagme.BASME_POLIG_NUMPTS (ctypes.byref (varpolig),
                        ctypes.byref (varnumpts))
        numpts          = varnumpts.value
        return          numpts

    def GetPt (self, ipt):
        """
        Lê um ponto \n
            ipt         <- índice do ponto 0..NumPts()-1\n
        Retorna:\n
            x, y        <- (double, double) coordenadas do ponto
        """
        varpolig        = ctypes.c_void_p (self.m_polig)
        vaript          = ctypes.c_int (ipt)
        x               = 0.
        varx            = ctypes.c_double (x)
        y               = 0.
        vary            = ctypes.c_double (y)
        self.m_model.m_eagme.BASME_POLIG_LERPT (ctypes.byref (varpolig),
                        ctypes.byref (vaript), ctypes.byref (varx), ctypes.byref (vary))
        x               = varx.value
        y               = vary.value
        return          x, y

    def GetPts (self):
        """
        Lê a poligonal inteira como uma matriz\n
        Retorna:\n
            x[], y[]
        """
        np              = self.NumPts ()
        x               = []
        y               = []
        for             ipt in range (0, np):
            x1, y1      = self.GetPt (ipt)
            x.append    (x1)
            y.append    (y1)
        return          x, y

    def Enter (self, x, y):
        """
        Entra um ponto no final da poligonal\n
            x, y        -> (double, double) coordenadas do ponto
        """
        varpolig        = ctypes.c_void_p (self.m_polig)
        varx            = ctypes.c_double (x)
        vary            = ctypes.c_double (y)
        self.m_model.m_eagme.BASME_POLIG_ENTRAR (ctypes.byref (varpolig), 
                        ctypes.byref (varx), ctypes.byref (vary))

    def Set (self, ipt, x, y):
        """
        Define as coordenadas de um ponto na posição ipt\n
            ipt         <- Índice do ponto 0..NumPts()-1\n
            x, y        <- (double, double) coordenadas do ponto
        """
        varpolig        = ctypes.c_void_p (self.m_polig)
        vaript          = ctypes.c_int (ipt)
        varx            = ctypes.c_double (x)
        vary            = ctypes.c_double (y)
        self.m_model.m_eagme.BASME_POLIG_ENTRAR_IPT (ctypes.byref (varpolig), 
                        ctypes.byref (vaript), ctypes.byref (varx), ctypes.byref (vary))
    def Insert (self, ipt, x, y):
        """
        Entra as coordenadas de um ponto na posição ipt e empurra os demais para frente\n
            ipt         <- Índice do ponto 0..NumPts()-1\n
            x, y        <- (double, double) coordenadas do ponto
        """
        varpolig        = ctypes.c_void_p (self.m_polig)
        vaript          = ctypes.c_int (ipt)
        varx            = ctypes.c_double (x)
        vary            = ctypes.c_double (y)
        self.m_model.m_eagme.BASME_POLIG_INSERIR_IPT (ctypes.byref (varpolig), 
                        ctypes.byref (vaript), ctypes.byref (varx), ctypes.byref (vary))

#------------------------------------------------------------------------------
#       Objeto para a criação de pilares e fundações CDadPil
#
class ColumnData ():

    def __init__ (self, model, dadpil):
        """
        Dados de pilares e fundações\n
            model       <- Objeto Model() do modelo atual\n
            dadpil      <- Apontador para objeto CDadPil
        """
        self.m_model    = model
        self.m_dadpil   = dadpil

    @property
    def columnDetailing (self):
        """
        Dados de detalhamento de pilar
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        detpil          = None
        vardetpil       = ctypes.c_void_p (detpil)
        self.m_model.m_eagme.BASME_DADPIL_DETPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (vardetpil))
        detpil          = vardetpil.value
        columndetailing = ColumnDetailing (self.m_model, detpil)
        return          columndetailing

    @property
    def columnGeometry (self):
        """
        Dados de geometria de pilar
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        geopil          = None
        vargeopil       = ctypes.c_void_p (geopil)
        self.m_model.m_eagme.BASME_DADPIL_GEOPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (vargeopil))
        geopil          = vargeopil.value
        columngeometry  = ColumnGeometry (self.m_model, geopil)
        return          columngeometry

    @property
    def columnInsertion (self):
        """
        Dados de inserção de pilar
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        inspil          = None
        varinspil       = ctypes.c_void_p (inspil)
        self.m_model.m_eagme.BASME_DADPIL_INSPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varinspil))
        inspil          = varinspil.value
        columninsertion = ColumnInsertion (self.m_model, inspil)
        return          columninsertion

    @property
    def columnPolygon (self):
        """
        Contorno de pilar poligonal
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        poligp          = None
        varpoligp       = ctypes.c_void_p (poligp)
        self.m_model.m_eagme.BASME_DADPIL_POLIGPP_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varpoligp))
        poligp          = varpoligp.value
        columnpolygon   = Polygon (self.m_model, poligp)
        return          columnpolygon

    @property
    def columnCoil (self):
        """
        Mola do pilar no pórtico espacial
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        pormol          = None
        varpormol       = ctypes.c_void_p (pormol)
        self.m_model.m_eagme.BASME_DADPIL_PORMOL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varpormol))
        pormol          = varpormol.value
        columncoil      = ColumnCoil (self.m_model, pormol)
        return          columncoil

    @property
    def columnIdent (self):
        """
        Identificação do pilar
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        identpil        = None
        varidentpil     = ctypes.c_void_p (identpil)
        self.m_model.m_eagme.BASME_DADPIL_IDENTPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varidentpil))
        identpil        = varidentpil.value
        columnident     = SMObjectIdent (self.m_model, identpil)
        return          columnident

    @property
    def columnPrecastData (self):
        """
        Dados de pilar pré-moldados CPreGPil
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        pregpil         = None
        varpregpil     = ctypes.c_void_p (pregpil)
        self.m_model.m_eagme.BASME_DADPIL_PREGPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varpregpil))
        pregpil        = varpregpil.value
        columnprecastdata = ColumnPrecastData (self.m_model, pregpil)
        return          columnprecastdata

    @property
    def columnStarts (self):
        """
        Pilar nasce em COLUMNSTART_xxxx 
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        icodnasce       = 0
        varicodnasce    = ctypes.c_int (icodnasce)
        self.m_model.m_eagme.BASME_DADPIL_ICODNASCE_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varicodnasce))
        icodnasce       = varicodnasce.value
        return          icodnasce

    @columnStarts.setter
    def columnStarts (self, icodnasce):
        """
        Pilar nasce em COLUMNSTART_xxxx 
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varicodnasce    = ctypes.c_int (icodnasce)
        self.m_model.m_eagme.BASME_DADPIL_ICODNASCE_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varicodnasce))

    @property
    def columnModel (self):
        """
        Modelo de pilar: COLUMNUSE_xxxxxx
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        itirante        = 0
        varitirante     = ctypes.c_int (itirante)
        self.m_model.m_eagme.BASME_DADPIL_ITIRANTE_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varitirante))
        itirante       = varitirante.value
        return          itirante

    @columnModel.setter
    def columnModel (self, itirante):
        """
        Modelo de pilar: COLUMNUSE_xxxxxx
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varitirante     = ctypes.c_int (itirante)
        self.m_model.m_eagme.BASME_DADPIL_ITIRANTE_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varitirante))

    @property
    def columnWindSupport (self):
        """
        Suporte a vento: (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        isupvento       = 0
        varisupvento    = ctypes.c_int (isupvento)
        self.m_model.m_eagme.BASME_DADPIL_ISUPVENTO_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varisupvento))
        isupvento       = varisupvento.value
        return          isupvento

    @columnWindSupport.setter
    def columnWindSupport (self, isupvento):
        """
        Suporte a vento: (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varisupvento    = ctypes.c_int (isupvento)
        self.m_model.m_eagme.BASME_DADPIL_ISUPVENTO_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varisupvento))
    @property
    def columnSectionMode (self):
        """
        Dados de condições de contorno: (0) da seção (1) do pavimento
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        idefcontpil     = 0
        varidefcontpil  = ctypes.c_int (idefcontpil)
        self.m_model.m_eagme.BASME_DADPIL_IDEFCONTPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varidefcontpil))
        idefcontpil     = varidefcontpil.value
        return          idefcontpil

    @columnSectionMode.setter
    def columnSectionMode (self, idefcontpil):
        """
        Dados de condições de contorno: (0) da seção (1) do pavimento
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varidefcontpil  = ctypes.c_int (idefcontpil)
        self.m_model.m_eagme.BASME_DADPIL_IDEFCONTPIL_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varidefcontpil))
    @property
    def columnInterference (self):
        """
        Verificação de interferências (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        iverifinter     = 0
        variverifinter  = ctypes.c_int (iverifinter)
        self.m_model.m_eagme.BASME_DADPIL_IVERIFINTER_LER (ctypes.byref (vardadpil),
                            ctypes.byref (variverifinter))
        iverifinter     = variverifinter.value
        return          iverifinter

    @columnInterference.setter
    def columnInterference (self, iverifinter):
        """
        Verificação de interferências (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        variverifinter  = ctypes.c_int (iverifinter)
        self.m_model.m_eagme.BASME_DADPIL_IVERIFINTER_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (variverifinter))
    @property
    def columnSloped (self):
        """
        Pilar inclinado (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        inclinado       = 0
        varinclinado    = ctypes.c_int (inclinado)
        self.m_model.m_eagme.BASME_DADPIL_INCLINADO_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varinclinado))
        inclinado       = varinclinado.value
        return          inclinado

    @columnSloped.setter
    def columnSloped (self, inclinado):
        """
        Pilar inclinado (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varinclinado    = ctypes.c_int (inclinado)
        self.m_model.m_eagme.BASME_DADPIL_INCLINADO_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varinclinado))

    @property
    def columnIsAFoundation (self):
        """
        O objeto de pilar representa uma fundação (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        ifundacao       = 0
        varifundacao    = ctypes.c_int (ifundacao)
        self.m_model.m_eagme.BASME_DADPIL_IFUNDACAO_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varifundacao))
        ifundacao       = varifundacao.value
        return          ifundacao

    @columnIsAFoundation.setter
    def columnIsAFoundation (self, ifundacao):
        """
        O objeto de pilar representa uma fundação (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varifundacao    = ctypes.c_int (ifundacao)
        self.m_model.m_eagme.BASME_DADPIL_IFUNDACAO_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varifundacao))

    @property
    def columnHinges (self):
        """
        Pilar articulado em (0)CONTPOR.DAT (1)base/topo (2)base (3)topo
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        iarticbt        = 0
        variarticbt     = ctypes.c_int (iarticbt)
        self.m_model.m_eagme.BASME_DADPIL_IARTICBT_LER (ctypes.byref (vardadpil),
                            ctypes.byref (variarticbt))
        iarticbt        = variarticbt.value
        return          iarticbt

    @columnHinges.setter
    def columnHinges (self, iarticbt):
        """
        Pilar articulado em (0)CONTPOR.DAT (1)base/topo (2)base (3)topo
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        variarticbt     = ctypes.c_int (iarticbt)
        self.m_model.m_eagme.BASME_DADPIL_IARTICBT_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (variarticbt))

    @property
    def columnExport (self):
        """
        Pilar exportável para o 3D (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        iexportavel     = 0
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_DADPIL_IEXPORTAVEL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (variexportavel))
        iexportavel     = variexportavel.value
        return          iexportavel

    @columnExport.setter
    def columnExport (self, iexportavel):
        """
        Pilar exportável para o 3D (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_DADPIL_IEXPORTAVEL_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (variexportavel))

    @property
    def columnNonLinearity (self):
        """
        Coeficientes de não linearidade (0)Pilar (1)Não fissurado (2)Fissurado
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        ipilparnlf      = 0
        varipilparnlf   = ctypes.c_int (ipilparnlf)
        self.m_model.m_eagme.BASME_DADPIL_IPILPARNLF_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varipilparnlf))
        ipilparnlf      = varipilparnlf.value
        return          ipilparnlf

    @columnNonLinearity.setter
    def columnNonLinearity (self, ipilparnlf):
        """
        Coeficientes de não linearidade (0)Pilar (1)Não fissurado (2)Fissurado
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varipilparnlf   = ctypes.c_int (ipilparnlf)
        self.m_model.m_eagme.BASME_DADPIL_IPILPARNLF_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varipilparnlf))

    @property
    def columnBucklingX (self):
        """
        Coeficiente de flambagem X
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        cflamx          = 0
        varcflamx       = ctypes.c_double (cflamx)
        self.m_model.m_eagme.BASME_DADPIL_CFLAMX_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varcflamx))
        cflamx          = varcflamx.value
        return          cflamx

    @columnBucklingX.setter
    def columnBucklingX (self, cflamx):
        """
        Coeficiente de flambagem X
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varcflamx       = ctypes.c_double (cflamx)
        self.m_model.m_eagme.BASME_DADPIL_CFLAMX_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varcflamx))

    @property
    def columnBucklingY (self):
        """
        Coeficiente de flambagem Y
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        cflamy          = 0
        varcflamy       = ctypes.c_double (cflamy)
        self.m_model.m_eagme.BASME_DADPIL_CFLAMY_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varcflamy))
        cflamy          = varcflamy.value
        return          cflamy

    @columnBucklingY.setter
    def columnBucklingY (self, cflamy):
        """
        Coeficiente de flambagem Y
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varcflamy       = ctypes.c_double (cflamy)
        self.m_model.m_eagme.BASME_DADPIL_CFLAMY_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varcflamy))

    @property
    def columnDoubleStoryX (self):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        itravadox       = 0
        varitravadox    = ctypes.c_int (itravadox)
        self.m_model.m_eagme.BASME_DADPIL_ITRAVADOX_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varitravadox))
        itravadox       = varitravadox.value
        return          itravadox

    @columnDoubleStoryX.setter
    def columnDoubleStoryX (self, itravadox):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varitravadox    = ctypes.c_int (itravadox)
        self.m_model.m_eagme.BASME_DADPIL_ITRAVADOX_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varitravadox))

    @property
    def columnDoubleStoryY (self):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        itravadoy       = 0
        varitravadoy    = ctypes.c_int (itravadoy)
        self.m_model.m_eagme.BASME_DADPIL_ITRAVADOY_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varitravadoy))
        itravadoy       = varitravadoy.value
        return          itravadoy

    @columnDoubleStoryY.setter
    def columnDoubleStoryY (self, itravadoy):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varitravadoy    = ctypes.c_int (itravadoy)
        self.m_model.m_eagme.BASME_DADPIL_ITRAVADOY_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varitravadoy))

    @property
    def columnConcreteFc (self):
        """
        Fck diferenciado de pilar (string)
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varfckpil       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADPIL_FCKPIL_LER (ctypes.byref (vardadpil),
                            varfckpil)
        fckpil          = varfckpil.value.decode(TQSUtil.CHARSET)
        return          fckpil

    @columnConcreteFc.setter
    def columnConcreteFc (self, fckpil):
        """
        Fck diferenciado de pilar (string)
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varfckpil       = ctypes.c_char_p (fckpil.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADPIL_FCKPIL_DEF (ctypes.byref (vardadpil),
                            varfckpil)

    @property
    def columnBoundaryCond (self):
        """
        Condições de contorno de pilares
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        contpil         = None
        varcontpil      = ctypes.c_void_p (contpil)
        self.m_model.m_eagme.BASME_DADPIL_CONTPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varcontpil))
        contpil         = varcontpil.value
        columnboundarycond = ColumnBoundaryCond (self.m_model, contpil)
        return          columnboundarycond
        
    @property
    def columnCover (self):
        """
        Cobrimento do pilar na planta, cm
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        cobrpil         = 0.
        varcobrpil      = ctypes.c_double (cobrpil)
        self.m_model.m_eagme.BASME_DADPIL_COBRPIL_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varcobrpil))
        cobrpil        = varcobrpil.value
        return          cobrpil

    @columnCover.setter
    def columnCover (self, cobrpil):
        """
        Cobrimento do pilar na planta, cm
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varcobrpil      = ctypes.c_double (cobrpil)
        self.m_model.m_eagme.BASME_DADPIL_COBRPIL_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varcobrpil))

    @property
    def columnExposure (self):
        """
        Pilar em contato com o solo (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        icontsolo       = 0
        varicontsolo    = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_DADPIL_ICONTSOLO_LER (ctypes.byref (vardadpil),
                            ctypes.byref (varicontsolo))
        icontsolo       = varicontsolo.value
        return          icontsolo

    @columnExposure.setter
    def columnExposure (self, icontsolo):
        """
        Pilar em contato com o solo (0) não (1) sim
        """
        vardadpil       = ctypes.c_void_p (self.m_dadpil)
        varicontsolo = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_DADPIL_ICONTSOLO_DEF (ctypes.byref (vardadpil),
                            ctypes.byref (varicontsolo))

#-----------------------------------------------------------------------------
#      Dados globais por planta - CDadPav 
#      Lista de plantas (mudança de seção) para os pilares criados na planta atual
#
class CurrentFloorData ():

    def __init__ (self, model, floor):
        """
        Dados globais por planta, que são usados na criação de objetos novos\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor() da planta atual
        """
        self.m_model    = model
        self.m_floor    = floor

        self.drawing         = CurFloorDrawingData (model, floor)
        self.floorLoadData   = CurFloorLoadData (model, floor)
        self.floorBeamData   = CurFloorBeamData (model, floor)
        self.floorSlabData   = CurFloorSlabData (model, floor)
        self.floorColumnData = CurFloorColumnData (model, floor)
        self.floorCutData    = CurFloorCutData (model, floor)
        self.floorAxisData   = CurFloorAxisData (model, floor)

#
#       Dados globais de desenho - CurrentFloorData.drawing
#
class CurFloorDrawingData ():

    def __init__ (self, model, floor):
        """
        Dados de desenho por pavimento\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    @property
    def drawingScale (self):
        """
        Escala da planta de formas - cm plotados por cm na escala real
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        escala          = 0.
        varescala       = ctypes.c_double (escala)
        self.m_model.m_eagme.BASME_DADPAV_ESCALA_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varescala))
        escala       = varescala.value
        return          escala

    @drawingScale.setter
    def drawingScale (self, escala):
        """
        Escala da planta de formas - cm plotados por cm na escala real
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varescala       = ctypes.c_double (escala)
        self.m_model.m_eagme.BASME_DADPAV_ESCALA_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varescala))

    @property
    def drawingMultiplier (self):
        """
        Multiplicador de dimensões de formas
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        dimlfc          = 0.
        vardimlfc       = ctypes.c_double (dimlfc)
        self.m_model.m_eagme.BASME_DADPAV_DIMLFC_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vardimlfc))
        dimlfc          = vardimlfc.value
        return          dimlfc

    @drawingMultiplier.setter
    def drawingMultiplier (self, dimlfc):
        """
        Multiplicador de dimensões de formas
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        vardimlfc       = ctypes.c_double (dimlfc)
        self.m_model.m_eagme.BASME_DADPAV_DIMLFC_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (vardimlfc))
#
#       Dados de cargas - CurrentFloorData.load
#
class CurFloorLoadData ():

    def __init__ (self, model, floor):
        """
        Cargas por planta\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    def GetLoad (self, itipocarpav):
        """
        Carga atual de tipo TPLOAD_xxx
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varitipocarpav  = ctypes.c_int (itipocarpav)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_DADPAV_CARGAS_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varitipocarpav), ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx
#
#      Vigas - CurrentFloorData.beam
#
class CurFloorBeamData ():

    def __init__ (self, model, floor):
        """
        Dados globais de vigas por planta\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    @property
    def beamGeometry (self):
        """
        Geometria de viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        geovig          = None
        vargeovig       = ctypes.c_void_p (geovig)
        self.m_model.m_eagme.BASME_DADPAV_GEOVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vargeovig))
        geovig          = vargeovig.value
        beamgeometry    = BeamGeometry (self.m_model, geovig)
        return          beamgeometry

    @property
    def beamInertia (self):
        """
        Inércia de viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        inervig         = None
        varinervig      = ctypes.c_void_p (inervig)
        self.m_model.m_eagme.BASME_DADPAV_INERVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varinervig))
        inervig         = varinervig.value
        beaminertia     = BeamInertia (self.m_model, inervig)
        return          beaminertia

    @property
    def beamBond (self):
        """
        Vinculações e outros dados de viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        vincvig         = None
        varvincvig      = ctypes.c_void_p (vincvig)
        self.m_model.m_eagme.BASME_DADPAV_VINCVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varvincvig))
        vincvig         = varvincvig.value
        beambond        = BeamBond (self.m_model, vincvig)
        return          beambond

    @property
    def beamInsertion (self):
        """
        Dados de inserção de vigas
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        insvig          = None
        varinsvig       = ctypes.c_void_p (insvig)
        self.m_model.m_eagme.BASME_DADPAV_INSVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varinsvig))
        insvig          = varinsvig.value
        beaminsertion   = BeamInsertion (self.m_model, insvig)
        return          beaminsertion

    @property
    def beamTemperShrink (self):
        """
        Temperatura / retração de vigas
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        tempretvig      = None
        vartempretvig   = ctypes.c_void_p (tempretvig)
        self.m_model.m_eagme.BASME_DADPAV_TEMPRETVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vartempretvig))
        tempretvig      = vartempretvig.value
        beamtempershrink= TemperatureShrink (self.m_model, tempretvig)
        return          beamtempershrink

    @property
    def beamDetailing (self):
        """
        Detalhamento de vigas
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        detvig          = None
        vardetvig       = ctypes.c_void_p (detvig)
        self.m_model.m_eagme.BASME_DADPAV_DETVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vardetvig))
        detvig          = vardetvig.value
        beamdetailing   = BeamDetailing (self.m_model, detvig)
        return          beamdetailing

    @property
    def beamOpening (self):
        """
        Furo em viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        furovig         = None
        varfurovig      = ctypes.c_void_p (furovig)
        self.m_model.m_eagme.BASME_DADPAV_FUROVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varfurovig))
        furovig         = varfurovig.value
        beamopening     = BeamOpening (self.m_model, furovig)
        return          beamopening

    @property
    def beamIdent (self):
        """
        Identificação de viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        identvig        = None
        varidentvig     = ctypes.c_void_p (identvig)
        self.m_model.m_eagme.BASME_DADPAV_IDENTVIG_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varidentvig))
        identvig        = varidentvig.value
        beamident       = SMObjectIdent (self.m_model, identvig)
        return          beamident

    @property
    def beamFirstNumber (self):
        """
        Numero da primeira viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        iprimviga       = 0
        variprimviga    = ctypes.c_int (iprimviga)
        self.m_model.m_eagme.BASME_DADPAV_IPRIMVIGA_LER (ctypes.byref (varfabrica),
                            ctypes.byref (variprimviga))
        iprimviga       = variprimviga.value
        return          iprimviga

    @beamFirstNumber.setter
    def beamFirstNumber (self, iprimviga):
        """
        Numero da primeira viga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        variprimviga    = ctypes.c_int (iprimviga)
        self.m_model.m_eagme.BASME_DADPAV_IPRIMVIGA_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (variprimviga))

    @property
    def beamExport (self):
        """
        Viga exportável para o 3D (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        iexportavelv    = 0
        variexportavelv = ctypes.c_int (iexportavelv)
        self.m_model.m_eagme.BASME_DADPAV_IEXPORTAVELV_LER (ctypes.byref (varfabrica),
                            ctypes.byref (variexportavelv))
        iexportavelv    = variexportavelv.value
        return          iexportavelv

    @beamExport.setter
    def beamExport (self, iexportavelv):
        """
        Viga exportável para o 3D (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        variexportavelv = ctypes.c_int (iexportavelv)
        self.m_model.m_eagme.BASME_DADPAV_IEXPORTAVELV_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (variexportavelv))
#
#      Lajes - CurrentFloorData.slab
#
class CurFloorSlabData ():

    def __init__ (self, model, floor):
        """
        Dados globais de lajes por planta\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    @property
    def slabPlastification (self):
        """
        Engaste em viga (0) livre (1) apoio (2) engast laje
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        iengast         = 0
        variengast      = ctypes.c_int (iengast)
        self.m_model.m_eagme.BASME_DADPAV_IENGAST_LER (ctypes.byref (varfabrica),
                            ctypes.byref (variengast))
        iengast         = variengast.value
        return          iengast

    @slabPlastification.setter
    def slabPlastification (self, iengast):
        """
        Engaste em viga (0) livre (1) apoio (2) engast laje
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        variengast      = ctypes.c_int (iengast)
        self.m_model.m_eagme.BASME_DADPAV_IENGAST_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (variengast))

    @property
    def slabReleaseFx (self):
        """
        Liberar Fx no apoio da laje (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        ilivrfx         = 0
        varilivrfx      = ctypes.c_int (ilivrfx)
        self.m_model.m_eagme.BASME_DADPAV_ILIVRFX_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varilivrfx))
        ilivrfx         = varilivrfx.value
        return          ilivrfx

    @slabReleaseFx.setter
    def slabReleaseFx (self, ilivrfx):
        """
        Liberar Fx no apoio da laje (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varilivrfx      = ctypes.c_int (ilivrfx)
        self.m_model.m_eagme.BASME_DADPAV_ILIVRFX_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varilivrfx))

    @property
    def slabFixedSupport (self):
        """
        Valor de engaste de bordo (0..1)
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        valengast       = 0
        varvalengast    = ctypes.c_double (valengast)
        self.m_model.m_eagme.BASME_DADPAV_VALENGAST_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varvalengast))
        valengast       = varvalengast.value
        return          valengast

    @slabFixedSupport.setter
    def slabFixedSupport (self, valengast):
        """
        Valor de engaste de bordo (0..1)
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varvalengast    = ctypes.c_double (valengast)
        self.m_model.m_eagme.BASME_DADPAV_VALENGAST_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varvalengast))

    @property
    def dropPanelThickness (self):
        """
        Altura de capitel cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        caph            = 0
        varcaph         = ctypes.c_double (caph)
        self.m_model.m_eagme.BASME_DADPAV_CAPH_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varcaph))
        caph            = varcaph.value
        return          caph

    @dropPanelThickness.setter
    def dropPanelThickness (self, caph):
        """
        Altura de capitel cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcaph         = ctypes.c_double (caph)
        self.m_model.m_eagme.BASME_DADPAV_CAPH_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcaph))

    @property
    def dropPanelDiv (self):
        """
        Divisor de flexão de capitel
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        capdivflx       = 0
        varcapdivflx    = ctypes.c_double (capdivflx)
        self.m_model.m_eagme.BASME_DADPAV_CAPDIVFLX_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varcapdivflx))
        capdivflx       = varcapdivflx.value
        return          capdivflx

    @dropPanelDiv.setter
    def dropPanelDiv (self, capdivflx):
        """
        Divisor de flexão de capitel
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcapdivflx    = ctypes.c_double (capdivflx)
        self.m_model.m_eagme.BASME_DADPAV_CAPDIVFLX_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcapdivflx))

    @property
    def slabMouldBasePoint (self):
        """
        Ponto base de inserção de nervura (0..5)
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        ibasenerv       = 0
        varibasenerv    = ctypes.c_int (ibasenerv)
        self.m_model.m_eagme.BASME_DADPAV_IBASENERV_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varibasenerv))
        ibasenerv       = varibasenerv.value
        return          ibasenerv

    @slabMouldBasePoint.setter
    def slabMouldBasePoint (self, ibasenerv):
        """
        Ponto base de inserção de nervura (0..5)
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varibasenerv    = ctypes.c_int (ibasenerv)
        self.m_model.m_eagme.BASME_DADPAV_IBASENERV_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varibasenerv))

    @property
    def slabMouldXSize (self):
        """
        Tamanho X da forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        tamxnerv        = 0
        vartamxnerv     = ctypes.c_double (tamxnerv)
        self.m_model.m_eagme.BASME_DADPAV_TAMXNERV_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vartamxnerv))
        tamxnerv        = vartamxnerv.value
        return          tamxnerv

    @slabMouldXSize.setter
    def slabMouldXSize (self, tamxnerv):
        """
        Tamanho X da forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        vartamxnerv     = ctypes.c_double (tamxnerv)
        self.m_model.m_eagme.BASME_DADPAV_TAMXNERV_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (vartamxnerv))

    @property
    def slabMouldYSize (self):
        """
        Tamanho Y da forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        tamynerv        = 0
        vartamynerv     = ctypes.c_double (tamynerv)
        self.m_model.m_eagme.BASME_DADPAV_TAMYNERV_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vartamynerv))
        tamynerv        = vartamynerv.value
        return          tamynerv

    @slabMouldYSize.setter
    def slabMouldYSize (self, tamynerv):
        """
        Tamanho Y da forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        vartamynerv     = ctypes.c_double (tamynerv)
        self.m_model.m_eagme.BASME_DADPAV_TAMYNERV_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (vartamynerv))

    @property
    def slabMouldXSpace (self):
        """
        Espaçamento X de forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        expxnerv        = 0
        varexpxnerv     = ctypes.c_double (expxnerv)
        self.m_model.m_eagme.BASME_DADPAV_ESPXNERV_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varexpxnerv))
        expxnerv        = varexpxnerv.value
        return          expxnerv

    @slabMouldXSpace.setter
    def slabMouldXSpace (self, expxnerv):
        """
        Espaçamento X de forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varexpxnerv     = ctypes.c_double (expxnerv)
        self.m_model.m_eagme.BASME_DADPAV_ESPXNERV_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varexpxnerv))

    @property
    def slabMouldYSpace (self):
        """
        Espaçamento Y de forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        expynerv        = 0.
        varexpynerv     = ctypes.c_double (expynerv)
        self.m_model.m_eagme.BASME_DADPAV_ESPYNERV_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varexpynerv))
        expynerv        = varexpynerv.value
        return          expynerv

    @slabMouldYSpace.setter
    def slabMouldYSpace (self, expynerv):
        """
        Espaçamento Y de forma de nervura cm
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varexpynerv     = ctypes.c_double (expynerv)
        self.m_model.m_eagme.BASME_DADPAV_ESPYNERV_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varexpynerv))

    @property
    def slabFirstNumber (self):
        """
        Número da primeira laje
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        iprimlaje       = 0
        variprimlaje    = ctypes.c_int (iprimlaje)
        self.m_model.m_eagme.BASME_DADPAV_IPRIMLAJE_LER (ctypes.byref (varfabrica),
                            ctypes.byref (variprimlaje))
        iprimlaje       = variprimlaje.value
        return          iprimlaje

    @slabFirstNumber.setter
    def slabFirstNumber (self, iprimlaje):
        """
        Número da primeira laje
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        variprimlaje    = ctypes.c_int (iprimlaje)
        self.m_model.m_eagme.BASME_DADPAV_IPRIMLAJE_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (variprimlaje))

    @property
    def slabExport (self):
        """
        Exportar a laje para visualização 3D (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        iexportavell    = 0
        variexportavell = ctypes.c_int (iexportavell)
        self.m_model.m_eagme.BASME_DADPAV_IEXPORTAVELL_LER (ctypes.byref (varfabrica),
                            ctypes.byref (variexportavell))
        iexportavell    = variexportavell.value
        return          iexportavell

    @slabExport.setter
    def slabExport (self, iexportavell):
        """
        Exportar a laje para visualização 3D (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        variexportavell = ctypes.c_int (iexportavell)
        self.m_model.m_eagme.BASME_DADPAV_IEXPORTAVELL_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (variexportavell))

    @property
    def stairTitle (self):
        """
        Título de escada
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varidentesc     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADPAV_IDENTESC_LER (ctypes.byref (varfabrica),
                            varidentesc)
        identesc        = varidentesc.value.decode(TQSUtil.CHARSET)
        return         identesc

    @stairTitle.setter
    def stairTitle (self, identesc):
        """
        Título de escada
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varidentesc     = ctypes.c_char_p (identesc.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADPAV_IDENTESC_DEF (ctypes.byref (varfabrica),
                            varidentesc)
    @property
    def slabGeometry (self):
        """
        Dados de geometria de laje
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        geolaj          = None
        vargeolaj       = ctypes.c_void_p (geolaj)
        self.m_model.m_eagme.BASME_DADPAV_GEOLAJ_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vargeolaj))
        geolaj          = vargeolaj.value
        slabGeometry    = SlabGeometry (self.m_model, geolaj)
        return          slabGeometry

    @property
    def slabGrid (self):
        """
        Dados para discretização de laje por grelha
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        grelaj          = None
        vargrelaj       = ctypes.c_void_p (grelaj)
        self.m_model.m_eagme.BASME_DADPAV_GRELAJ_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vargrelaj))
        grelaj         = vargrelaj.value
        slabgrid        = SlabGrid (self.m_model, grelaj)
        return          slabgrid

    @property
    def slabTemperShrink (self):
        """
        Temperatura / retração de lajes
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        tempretlaj      = None
        vartempretlaj   = ctypes.c_void_p (tempretlaj)
        self.m_model.m_eagme.BASME_DADPAV_TEMPRETLAJ_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vartempretlaj))
        tempretlaj      = vartempretlaj.value
        slabtempershrink= TemperatureShrink (self.m_model, tempretlaj)
        return          slabtempershrink

    @property
    def slabDetailing (self):
        """
        Detalhamento de lajes
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        detlaj          = None
        vardetlaj       = ctypes.c_void_p (detlaj)
        self.m_model.m_eagme.BASME_DADPAV_DETLAJ_LER (ctypes.byref (varfabrica),
                            ctypes.byref (vardetlaj))
        detlaj          = vardetlaj.value
        slabdetailing   = SlabDetailing (self.m_model, detlaj)
        return          slabdetailing

    @property
    def slabIdent (self):
        """
        Identificação de lajes
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        identlaj        = None
        varidentlaj     = ctypes.c_void_p (identlaj)
        self.m_model.m_eagme.BASME_DADPAV_IDENTLAJ_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varidentlaj))
        identlaj        = varidentlaj.value
        slabident       = SMObjectIdent (self.m_model, identlaj)
        return          slabident
#
#      Pilares - CurrentFloorData.column
#
class CurFloorColumnData ():

    def __init__ (self, model, floor):
        """
        Dados globais de pilares por planta\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    @property
    def columnFloorNames (self):
        """
        Lista de plantas de pilares
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        plapil          = None
        varplapil       = ctypes.c_void_p (plapil)
        self.m_model.m_eagme.BASME_DADPAV_PLAPIL_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varplapil))
        plapil          = varplapil.value
        columnfloornames= ColumnFloorNames (self.m_model, plapil)
        return          columnfloornames

    @property
    def columnDynHorLoad (self):
        """
        Carga dinâmica de veiculo em pilar (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        icargadinvuc    = 0
        varicargadinvuc = ctypes.c_int (icargadinvuc)
        self.m_model.m_eagme.BASME_DADPAV_ICARGADINVUC_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varicargadinvuc))
        icargadinvuc    = varicargadinvuc.value
        return          icargadinvuc

    @columnDynHorLoad.setter
    def columnDynHorLoad (self, icargadinvuc):
        """
        Carga dinâmica de veiculo em pilar (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varicargadinvuc = ctypes.c_int (icargadinvuc)
        self.m_model.m_eagme.BASME_DADPAV_ICARGADINVUC_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varicargadinvuc))

#
#      Cortes - CurrentFloorData.cut
#
class CurFloorCutData ():

    def __init__ (self, model, floor):
        """
        Dados globais de cortes por planta\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    @property
    def cutTitle (self):
        """
        Último título de corte
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        vartitcor       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADPAV_TITCOR_LER (ctypes.byref (varfabrica), 
                            vartitcor)
        titcor          = vartitcor.value.decode(TQSUtil.CHARSET)
        return          titcor

    @cutTitle.setter
    def cutTitle (self, titcor):
        """
        Último título de corte
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        vartitcor      = ctypes.c_char_p (titcor.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADPAV_TITCOR_DEF (ctypes.byref (varfabrica),
                            vartitcor)
#
#      Eixos - CurrentFloorData.axis
#
class CurFloorAxisData ():

    def __init__ (self, model, floor):
        """
        Dados globais de eixos por planta\n
            model            <- Objeto Model() do modelo atual\n
            floor            <- Objeto Floor() da planta atual
        """
        self.m_model          = model
        self.m_floor          = floor

    @property
    def axisHorLabel (self):
        """
        Último rotulo de eixo horizontal
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varrotuloh      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADPAV_ROTULOH_LER (ctypes.byref (varfabrica), 
                            varrotuloh)
        rotuloh         = varrotuloh.value.decode(TQSUtil.CHARSET)
        return          rotuloh

    @axisHorLabel.setter
    def axisHorLabel (self, rotuloh):
        """
        Último rotulo de eixo horizontal
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varrotuloh      = ctypes.c_char_p (rotuloh.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADPAV_ROTULOH_DEF (ctypes.byref (varfabrica),
                            varrotuloh)
    @property
    def axisVerLabel (self):
        """
        Último rótulo de eixo vertical
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varrotulov      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADPAV_ROTULOV_LER (ctypes.byref (varfabrica), 
                            varrotulov)
        rotulov         = varrotulov.value.decode(TQSUtil.CHARSET)
        return          rotulov

    @axisVerLabel.setter
    def axisVerLabel (self, rotulov):
        """
        Último rótulo de eixo vertical
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varrotulov      = ctypes.c_char_p (rotulov.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADPAV_ROTULOV_DEF (ctypes.byref (varfabrica),
                            varrotulov)

    @property
    def axisSlopedLabel (self):
        """
        Último rótulo de eixo inclinado
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varrotuloi      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_DADPAV_ROTULOI_LER (ctypes.byref (varfabrica), 
                            varrotuloi)
        rotuloi         = varrotuloi.value.decode(TQSUtil.CHARSET)
        return          rotuloi

    @axisSlopedLabel.setter
    def axisSlopedLabel (self, rotuloi):
        """
        Último rótulo de eixo inclinado
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varrotuloi      = ctypes.c_char_p (rotuloi.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_DADPAV_ROTULOI_DEF (ctypes.byref (varfabrica),
                            varrotuloi)

    @property
    def axisAngle (self):
        """
        Último angulo de eixo graus
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        angeixo         = 0.
        varangeixo      = ctypes.c_double (angeixo)
        self.m_model.m_eagme.BASME_DADPAV_ANGEIXO_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varangeixo))
        angeixo        = varangeixo.value
        return          angeixo

    @axisAngle.setter
    def axisAngle (self, angeixo):
        """
        Último angulo de eixo graus
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varangeixo      = ctypes.c_double (angeixo)
        self.m_model.m_eagme.BASME_DADPAV_ANGEIXO_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varangeixo))

    @property
    def unlockAxisAngle (self):
        """
        (0) Eixos em X e Y globais (1) ângulo qualquer
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        iangeixo        = 0
        variangeixo     = ctypes.c_int (iangeixo)
        self.m_model.m_eagme.BASME_DADPAV_IANGEIXO_LER (ctypes.byref (varfabrica),
                            ctypes.byref (variangeixo))
        iangeixo        = variangeixo.value
        return          iangeixo

    @unlockAxisAngle.setter
    def unlockAxisAngle (self, iangeixo):
        """
        (0) Eixos em X e Y globais (1) ângulo qualquer
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        variangeixo     = ctypes.c_int (iangeixo)
        self.m_model.m_eagme.BASME_DADPAV_IANGEIXO_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (variangeixo))

    @property
    def axisDirection (self):
        """
        Eixo na direção (0) X (1) Y
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        idirecaoeixo    = 0
        varidirecaoeixo = ctypes.c_int (idirecaoeixo)
        self.m_model.m_eagme.BASME_DADPAV_IDIRECAOEIXO_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varidirecaoeixo))
        idirecaoeixo    = varidirecaoeixo.value
        return          idirecaoeixo

    @axisDirection.setter
    def axisDirection (self, idirecaoeixo):
        """
        Eixo na direção (0) X (1) Y
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varidirecaoeixo = ctypes.c_int (idirecaoeixo)
        self.m_model.m_eagme.BASME_DADPAV_IDIRECAOEIXO_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varidirecaoeixo))

    @property
    def axisDimOrigin (self):
        """
        Cotar distância à origem (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        icotardisteixo  = 0
        varicotardisteixo= ctypes.c_int (icotardisteixo)
        self.m_model.m_eagme.BASME_DADPAV_ICOTARDISTEIXO_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varicotardisteixo))
        icotardisteixo  = varicotardisteixo.value
        return          icotardisteixo

    @axisDimOrigin.setter
    def axisDimOrigin (self, icotardisteixo):
        """
        Cotar distância à origem (0) não (1) sim
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varicotardisteixo= ctypes.c_int (icotardisteixo)
        self.m_model.m_eagme.BASME_DADPAV_ICOTARDISTEIXO_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varicotardisteixo))
#------------------------------------------------------------------------------
#       Objeto base do Modelador Estrutural - vigas, pilares, lajes, etc
#
class SMObject ():

    def __init__ (self, model, objme):
        """
        Inicialização de um objeto do Modelador
        """
        self.m_model  = model
        self.m_objme  = objme

    @property
    def type (self):
        """
        Tipo do objeto (TQSModel.TYPE_xxxx)
        """
        varobjme    = ctypes.c_void_p (self.m_objme)
        ilista      = 0
        varilista   = ctypes.c_int (ilista)
        self.m_model.m_eagme.BASME_OBJ_LISTA_LER (ctypes.byref (varobjme), 
                        ctypes.byref (varilista))
        ilista      = varilista.value
        return      ilista

    @type.setter
    def type (self, ilista):
        """
        Tipo do objeto (TQSModel.TYPE_xxxx)
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        varilista       = ctypes.c_int (ilista)
        self.m_model.m_eagme.BASME_OBJ_LISTA_DEF (ctypes.byref (varobjme), 
                        ctypes.byref (varilista))

    @property
    def identobj (self):
        """
        Identificador único do objeto
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        identobj        = 0
        varidentobj     = ctypes.c_int (identobj)
        self.m_model.m_eagme.BASME_OBJ_IDENTOBJ_LER (ctypes.byref (varobjme), 
                        ctypes.byref(varidentobj))
        identobj        = varidentobj.value
        return          identobj

    @identobj.setter
    def identobj (self, identobj):
        """
        Identificador único do objeto
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        varidentobj     = ctypes.c_int (identobj)
        self.m_model.m_eagme.BASME_OBJ_IDENTOBJ_DEF (ctypes.byref (varobjme), 
                        ctypes.byref(varidentobj))
        identobj        = varidentobj.value
        return          identobj

    @property
    def number (self):
        """
        Número do objeto
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        inum            = 0
        varinum         = ctypes.c_int (inum)
        self.m_model.m_eagme.BASME_OBJ_INUM_LER (ctypes.byref (varobjme), 
                        ctypes.byref (varinum))
        inum            = varinum.value
        return          inum

    @number.setter
    def number (self, inum):
        """
        Número do objeto
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        varinum         = ctypes.c_int (inum)
        self.m_model.m_eagme.BASME_OBJ_INUM_DEF (ctypes.byref (varobjme), 
                        ctypes.byref (varinum))

    @property
    def title (self):
        """
        Título opcional do objeto
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        vartitulo       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_OBJ_TITULO_LER (ctypes.byref (varobjme), vartitulo)
        title           = vartitulo.value.decode(TQSUtil.CHARSET)
        return         title

    @title.setter
    def title (self, titulo):
        """
        Título opcional do objeto
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        vartitulo       = ctypes.c_char_p (titulo.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_OBJ_TITULO_DEF (ctypes.byref (varobjme), vartitulo)

    @property
    def formattedTitle (self):
        """
        Título considerando número e título opcional
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        vartitulo       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_OBJ_TITULO_FORMATADO (ctypes.byref (varobjme), vartitulo)
        formattedTitle  = vartitulo.value.decode(TQSUtil.CHARSET)
        return         formattedTitle

    def GetGuid (self, iadic, ipiso, itrecho):
        """
        iadic           <- Número adicional para diferenciar pisos e trechos\n
        ipiso           <- int Piso\n
        itrecho         <- int Trecho opcional\n
        Retorna:\n
        Identificador GUID
        """
        varobjme        = ctypes.c_void_p (self.m_objme)
        variadic        = ctypes.c_int (iadic)
        varipiso        = ctypes.c_int (ipiso)
        varitrecho      = ctypes.c_int (itrecho)
        varguid         = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_OBJ_LERGUID (ctypes.byref (varobjme), 
                        ctypes.byref (variadic), ctypes.byref (varipiso), 
                        ctypes.byref (varitrecho), varguid)
        guid            = varguid.value.decode(TQSUtil.CHARSET)
        return          guid

#------------------------------------------------------------------------------
#       Um Pilar
#
class Column (SMObject):

    def __init__ (self, model, floor, pilar):
        """
        Criação de um pilar\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor() da planta atual\n
            pilar       <- Objeto CPilares do Modelador
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_pilar    = pilar
        super().__init__(model, self.m_pilar)


    @property
    def columnDetailing (self):
        """
        Dados de detalhamento de pilar
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        detpil          = None
        vardetpil       = ctypes.c_void_p (detpil)
        self.m_model.m_eagme.BASME_PILARES_DETPIL_LER (ctypes.byref (varpilar),
                            ctypes.byref (vardetpil))
        detpil          = vardetpil.value
        columndetailing = ColumnDetailing (self.m_model, detpil)
        return          columndetailing

    @property
    def columnIdent (self):
        """
        Identificação do pilar
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        identpil        = None
        varidentpil     = ctypes.c_void_p (identpil)
        self.m_model.m_eagme.BASME_PILARES_IDENTPIL_LER (ctypes.byref (varpilar),
                            ctypes.byref (varidentpil))
        identpil        = varidentpil.value
        columnident     = SMObjectIdent (self.m_model, identpil)
        return          columnident

    @property
    def columnStarts (self):
        """
        Pilar nasce em COLUMNSTART_xxxx 
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        icodnasce       = 0
        varicodnasce    = ctypes.c_int (icodnasce)
        self.m_model.m_eagme.BASME_PILARES_ICODNASCE_LER (ctypes.byref (varpilar),
                            ctypes.byref (varicodnasce))
        icodnasce       = varicodnasce.value
        return          icodnasce

    @columnStarts.setter
    def columnStarts (self, icodnasce):
        """
        Pilar nasce em COLUMNSTART_xxxx 
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varicodnasce    = ctypes.c_int (icodnasce)
        self.m_model.m_eagme.BASME_PILARES_ICODNASCE_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varicodnasce))

    @property
    def columnModel (self):
        """
        Modelo de pilar: COLUMNUSE_xxxxxx
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        itirante        = 0
        varitirante     = ctypes.c_int (itirante)
        self.m_model.m_eagme.BASME_PILARES_ITIRANTE_LER (ctypes.byref (varpilar),
                            ctypes.byref (varitirante))
        itirante       = varitirante.value
        return          itirante

    @columnModel.setter
    def columnModel (self, itirante):
        """
        Modelo de pilar: COLUMNUSE_xxxxxx
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varitirante     = ctypes.c_int (itirante)
        self.m_model.m_eagme.BASME_PILARES_ITIRANTE_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varitirante))

    @property
    def hasFixedPoint (self):
        """
        (1) Se o pilar tem um ponto fixo
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        ifixedpoint     = 0
        varifixedpoint  = ctypes.c_int (ifixedpoint)
        self.m_model.m_eagme.BASME_PILARES_IPTFIXO_LER (ctypes.byref (varpilar),
                            ctypes.byref (varifixedpoint))
        ifixedpoint     = varifixedpoint.value
        return          ifixedpoint

    @hasFixedPoint.setter
    def hasFixedPoint (self, ifixedpoint):
        """
        (1) Se o pilar tem um ponto fixo
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varifixedpoint  = ctypes.c_int (ifixedpoint)
        self.m_model.m_eagme.BASME_PILARES_IPTFIXO_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varifixedpoint))

    @property
    def fixedPointX (self):
        """
        X do ponto fixo do pilar
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        fixedpointx     = 0.
        varfixedpointx  = ctypes.c_double (fixedpointx)
        self.m_model.m_eagme.BASME_PILARES_PTFIXOX_LER (ctypes.byref (varpilar),
                            ctypes.byref (varfixedpointx))
        fixedpointx     = varfixedpointx.value
        return          fixedpointx

    @fixedPointX.setter
    def fixedPointX (self, fixedpointx):
        """
        X do ponto fixo do pilar
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varfixedpointx  = ctypes.c_double (fixedpointx)
        self.m_model.m_eagme.BASME_PILARES_PTFIXOX_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varfixedpointx))

    @property
    def fixedPointY (self):
        """
        Y do ponto fixo do pilar
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        fixedpointy     = 0.
        varfixedpointy  = ctypes.c_double (fixedpointy)
        self.m_model.m_eagme.BASME_PILARES_PTFIXOY_LER (ctypes.byref (varpilar),
                            ctypes.byref (varfixedpointy))
        fixedpointy     = varfixedpointy.value
        return          fixedpointy

    @fixedPointY.setter
    def fixedPointY (self, fixedpointy):
        """
        Y do ponto fixo do pilar
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varfixedpointy  = ctypes.c_double (fixedpointy)
        self.m_model.m_eagme.BASME_PILARES_PTFIXOY_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varfixedpointy))

    @property
    def columnWindSupport (self):
        """
        Suporte a vento: (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        isupvento       = 0
        varisupvento    = ctypes.c_int (isupvento)
        self.m_model.m_eagme.BASME_PILARES_ISUPVENTO_LER (ctypes.byref (varpilar),
                            ctypes.byref (varisupvento))
        isupvento       = varisupvento.value
        return          isupvento

    @columnWindSupport.setter
    def columnWindSupport (self, isupvento):
        """
        Suporte a vento: (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varisupvento    = ctypes.c_int (isupvento)
        self.m_model.m_eagme.BASME_PILARES_ISUPVENTO_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varisupvento))
    @property
    def columnInterference (self):
        """
        Verificação de interferências (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        iverifinter     = 0
        variverifinter  = ctypes.c_int (iverifinter)
        self.m_model.m_eagme.BASME_PILARES_IVERIFINTER_LER (ctypes.byref (varpilar),
                            ctypes.byref (variverifinter))
        iverifinter     = variverifinter.value
        return          iverifinter

    @columnInterference.setter
    def columnInterference (self, iverifinter):
        """
        Verificação de interferências (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        variverifinter  = ctypes.c_int (iverifinter)
        self.m_model.m_eagme.BASME_PILARES_IVERIFINTER_DEF (ctypes.byref (varpilar),
                            ctypes.byref (variverifinter))
    @property
    def columnSloped (self):
        """
        Inclinação do pilar (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        inclinado       = 0
        varinclinado    = ctypes.c_int (inclinado)
        self.m_model.m_eagme.BASME_PILARES_INCLINADO_LER (ctypes.byref (varpilar),
                            ctypes.byref (varinclinado))
        inclinado       = varinclinado.value
        return          inclinado

    @columnSloped.setter
    def columnSloped (self, inclinado):
        """
        Inclinação do pilar (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varinclinado    = ctypes.c_int (inclinado)
        self.m_model.m_eagme.BASME_PILARES_INCLINADO_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varinclinado))
    @property
    def columnCoil (self):
        """
        Mola do pilar no pórtico espacial
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        pormol          = None
        varpormol       = ctypes.c_void_p (pormol)
        self.m_model.m_eagme.BASME_PILARES_PORMOL_LER (ctypes.byref (varpilar),
                            ctypes.byref (varpormol))
        pormol          = varpormol.value
        columncoil      = ColumnCoil (self.m_model, pormol)
        return          columncoil

    @property
    def columnIsAFoundation (self):
        """
        O objeto de pilar representa uma fundação (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        ifundacao       = 0
        varifundacao    = ctypes.c_int (ifundacao)
        self.m_model.m_eagme.BASME_PILARES_IFUNDACAO_LER (ctypes.byref (varpilar),
                            ctypes.byref (varifundacao))
        ifundacao       = varifundacao.value
        return          ifundacao

    @columnIsAFoundation.setter
    def columnIsAFoundation (self, ifundacao):
        """
        O objeto de pilar representa uma fundação (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varifundacao    = ctypes.c_int (ifundacao)
        self.m_model.m_eagme.BASME_PILARES_IFUNDACAO_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varifundacao))
#
#       Dados de fundação
#
    @property
    def foundationData (self):
        """
        Dados de fundação
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        fundac          = None
        varfundac       = ctypes.c_void_p (fundac)
        self.m_model.m_eagme.BASME_PILARES_FUNDAC_LER (ctypes.byref (varpilar),
                            ctypes.byref (varfundac))
        fundac          = varfundac.value
        foundationdata  = FoundationData (self.m_model, fundac)
        return          foundationdata

    @property
    def foundationDefined (self):
        """
        Fundação definida (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        ideffund       = 0
        varideffund    = ctypes.c_int (ideffund)
        self.m_model.m_eagme.BASME_PILARES_IDEFFUND_LER (ctypes.byref (varpilar),
                            ctypes.byref (varideffund))
        ideffund       = varideffund.value
        return          ideffund

    @foundationDefined.setter
    def foundationDefined (self, ideffund):
        """
        Fundação definida (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varideffund    = ctypes.c_int (ideffund)
        self.m_model.m_eagme.BASME_PILARES_IDEFFUND_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varideffund))
    @property
    def isShortColumn (self):
        """
        O pilar é (0) normal (1) pilarete
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        ipilarete       = 0
        varipilarete    = ctypes.c_int (ipilarete)
        self.m_model.m_eagme.BASME_PILARES_IPILARETE_LER (ctypes.byref (varpilar),
                            ctypes.byref (varipilarete))
        ipilarete       = varipilarete.value
        return          ipilarete

    @isShortColumn.setter
    def isShortColumn (self, ipilarete):
        """
        O pilar é (0) normal (1) pilarete
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varipilarete    = ctypes.c_int (ipilarete)
        self.m_model.m_eagme.BASME_PILARES_IPILARETE_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varipilarete))

    @property
    def shortColumnAuxiliaryFloor (self):
        """
        Piso auxiliar de base do pilarete
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        ipisoauxpilarete= 0
        varipisoauxpilarete = ctypes.c_int (ipisoauxpilarete)
        self.m_model.m_eagme.BASME_PILARES_IPISOAUXPILARETE_LER (ctypes.byref (varpilar),
                            ctypes.byref (varipisoauxpilarete))
        ipisoauxpilarete    = varipisoauxpilarete.value
        return          ipisoauxpilarete

    @shortColumnAuxiliaryFloor.setter
    def shortColumnAuxiliaryFloor (self, ipisoauxpilarete):
        """
        Piso auxiliar de base do pilarete
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varipisoauxpilarete = ctypes.c_int (ipisoauxpilarete)
        self.m_model.m_eagme.BASME_PILARES_IPISOAUXPILARETE_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varipisoauxpilarete))

    @property
    def columnPrecastData (self):
        """
        Dados de pilar pré-moldados
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        pregpil         = None
        varpregpil     = ctypes.c_void_p (pregpil)
        self.m_model.m_eagme.BASME_PILARES_PREGPIL_LER (ctypes.byref (varpilar),
                            ctypes.byref (varpregpil))
        pregpil        = varpregpil.value
        columnprecastdata = ColumnPrecastData (self.m_model, pregpil)
        return          columnprecastdata

    @property
    def columnExport (self):
        """
        Pilar exportável para o 3D (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        iexportavel     = 0
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_PILARES_IEXPORTAVEL_LER (ctypes.byref (varpilar),
                            ctypes.byref (variexportavel))
        iexportavel     = variexportavel.value
        return          iexportavel

    @columnExport.setter
    def columnExport (self, iexportavel):
        """
        Pilar exportável para o 3D (0) não (1) sim
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_PILARES_IEXPORTAVEL_DEF (ctypes.byref (varpilar),
                            ctypes.byref (variexportavel))
    @property
    def columnNonLinearity (self):
        """
        Coeficientes de não linearidade (0)Pilar (1)Não fissurado (2)Fissurado
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        ipilparnlf      = 0
        varipilparnlf   = ctypes.c_int (ipilparnlf)
        self.m_model.m_eagme.BASME_PILARES_IPILPARNLF_LER (ctypes.byref (varpilar),
                            ctypes.byref (varipilparnlf))
        ipilparnlf      = varipilparnlf.value
        return          ipilparnlf

    @columnNonLinearity.setter
    def columnNonLinearity (self, ipilparnlf):
        """
        Coeficientes de não linearidade (0)Pilar (1)Não fissurado (2)Fissurado
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varipilparnlf   = ctypes.c_int (ipilparnlf)
        self.m_model.m_eagme.BASME_PILARES_IPILPARNLF_DEF (ctypes.byref (varpilar),
                            ctypes.byref (varipilparnlf))

    def GetFoudation (self):
        """
        Retorna (Column) fundação ou pilar sob o pilar atual
        """
        pvistav         = None
        if              (self.m_model.m_tqsjan != None):
            pvistav     = self.m_model.m_tqsjan.m_pvistav
        varpvistav      = ctypes.c_void_p (pvistav)
        varpilar        = ctypes.c_void_p (self.m_pilar)
        pilarapo        = None
        varpilarapo     = ctypes.c_void_p (pilarapo)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_PILARES_PILARAPO_LER (
                        ctypes.byref (varpvistav), ctypes.byref (varpilar),
                        ctypes.byref (varpilarapo),ctypes.byref (varistat))
        istat           = varistat.value
        if              istat != 0:
            return      None
        pilarapo        = varpilarapo.value
        return          Column (self.m_model, self.m_floor, pilarapo)

#
#      Atributos BIM do usuário
#
    @property
    def userAttrib (self):
        """
        Atributos de usuário
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        self.m_model.m_eagme.BASME_PILARES_USRATRIB_LER (ctypes.byref (varpilar),
                ctypes.byref (varusratrib))
        usratrib        = varusratrib.value
        userattrib      = UserAttrib (self.m_model, usratrib)
        return          userattrib

#
#      Lista de seções de pilares
#
    def ColumnNumSections (self):
        """
        Retorna o número de seções
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        numsecp         = 0
        varnumsecp      = ctypes.c_int (numsecp)
        self.m_model.m_eagme.BASME_PILARES_NUMSECPIL (ctypes.byref (varpilar),
                ctypes.byref (varnumsecp))
        numsecp         = varnumsecp.value
        return          numsecp

    def ColumnGetSection (self, isec):
        """
        Retorna uma seção\n
            int isec    <- isec=0..ColumnNumSections()-1\n
        Retorna:\n
            objeto ColumnSection 
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varisec         = ctypes.c_int (isec)
        secpil          = None
        varsecpil       = ctypes.c_void_p (secpil)
        self.m_model.m_eagme.BASME_PILARES_SECPIL_LER (ctypes.byref (varpilar),
                            ctypes.byref (varisec), ctypes.byref (varsecpil))
        secpil          = varsecpil.value
        columnSection   = ColumnSection (self, self.m_model, self.m_floor, secpil)
        return          columnSection

    def ColumnCreateSection (self, isec, lastfloor):
        """
        Insere nova seção de pilar. Empurra demais seções\n
        A primeira seção é criada junto com o pilar\n
        Cria a princípio com a geometria da seção anterior\n
            int isec            <- isec=0..ColumnNumSections()-1\n
            char *lastfloor     <- Última planta desta seção\n
        Retorna:\n
            objeto ColumnSection 
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varisec         = ctypes.c_int (isec)
        varplamorre     = ctypes.c_char_p (lastfloor.encode (TQSUtil.CHARSET))
        secpil          = None
        varsecpil       = ctypes.c_void_p (secpil)
        self.m_model.m_eagme.BASME_PILARES_SECPIL_CRIAR (ctypes.byref (varfabrica),
                        ctypes.byref (varpilar), ctypes.byref (varisec), 
                        varplamorre, ctypes.byref (varsecpil))
        secpil          = varsecpil.value
        columnSection   = ColumnSection (self, self.m_model, self.m_floor, secpil)
        return          columnSection

    def ColumnSectionUpdateGeometry (self, columnSection):
        """
        Atualiza uma seção de pilar após alteração de geometria\n
            columnSection       <- Objeto ColumnSection
        """
        varpilar        = ctypes.c_void_p (self.m_pilar)
        varsecpil       = ctypes.c_void_p (columnSection.m_secpil)
        self.m_model.m_eagme.BASME_PILARES_SECPIL_ATUGEO (ctypes.byref (varpilar),
                            ctypes.byref (varsecpil))

#------------------------------------------------------------------------------
#       Dados de detalhamento de pilar CDetPil
#
class ColumnDetailing ():

    def __init__ (self, model, detpil):
        """
        Dados de detalhamento de pilar\n
            model       <- Objeto Model() do modelo atual\n
            detpil      <- Apontador para objeto CDetPil
        """
        self.m_model    = model
        self.m_detpil   = detpil

    @property
    def foundationHeight (self):
        """
        Altura da fundação, cm
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        hfun            = 0.
        varhfun         = ctypes.c_double (hfun)
        self.m_model.m_eagme.BASME_DETPIL_HFUN_LER (ctypes.byref (vardetpil),
                            ctypes.byref (varhfun))
        hfun            = varhfun.value
        return          hfun

    @foundationHeight.setter
    def foundationHeight (self, hfun):
        """
        Altura da fundação, cm
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        varhfun         = ctypes.c_double (hfun)
        self.m_model.m_eagme.BASME_DETPIL_HFUN_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (varhfun))

    @property
    def baseRecess (self):
        """
        Rebaixo da base, cm
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        dfspil          = 0.
        vardfspil       = ctypes.c_double (dfspil)
        self.m_model.m_eagme.BASME_DETPIL_DFSPIL_LER (ctypes.byref (vardetpil),
                            ctypes.byref (vardfspil))
        dfspil          = vardfspil.value
        return          dfspil

    @baseRecess.setter
    def baseRecess (self, dfspil):
        """
        Rebaixo da base, cm
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        vardfspil       = ctypes.c_double (dfspil)
        self.m_model.m_eagme.BASME_DETPIL_DFSPIL_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (vardfspil))

    @property
    def topRecess (self):
        """
        Rebaixo no topo, cm
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        dfstopo         = 0.
        vardfstopo      = ctypes.c_double (dfstopo)
        self.m_model.m_eagme.BASME_DETPIL_DFSTOPO_LER (ctypes.byref (vardetpil),
                            ctypes.byref (vardfstopo))
        dfstopo         = vardfstopo.value
        return          dfstopo

    @topRecess.setter
    def topRecess (self, dfstopo):
        """
        Rebaixo no topo, cm
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        vardfstopo      = ctypes.c_double (dfstopo)
        self.m_model.m_eagme.BASME_DETPIL_DFSTOPO_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (vardfstopo))
    @property
    def isDetailable (self):
        """
        Pilar detalhável (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        idetalhavel     = 0
        varidetalhavel  = ctypes.c_int (idetalhavel)
        self.m_model.m_eagme.BASME_DETPIL_IDETALHAVEL_LER (ctypes.byref (vardetpil),
                            ctypes.byref (varidetalhavel))
        idetalhavel     = varidetalhavel.value
        return          idetalhavel

    @isDetailable.setter
    def isDetailable (self, idetalhavel):
        """
        Pilar detalhável (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        varidetalhavel  = ctypes.c_int (idetalhavel)
        self.m_model.m_eagme.BASME_DETPIL_IDETALHAVEL_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (varidetalhavel))
    @property
    def isCurtain (self):
        """
        Pilar simula cortina (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        icortina     = 0
        varicortina  = ctypes.c_int (icortina)
        self.m_model.m_eagme.BASME_DETPIL_ICORTINA_LER (ctypes.byref (vardetpil),
                            ctypes.byref (varicortina))
        icortina     = varicortina.value
        return          icortina

    @isCurtain.setter
    def isCurtain (self, icortina):
        """
        Pilar simula cortina (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        varicortina  = ctypes.c_int (icortina)
        self.m_model.m_eagme.BASME_DETPIL_ICORTINA_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (varicortina))
    @property
    def canStartOutOfFoundation (self):
        """
        Pode nascer fora do piso fundação (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        inasceforafund  = 0
        varinasceforafund= ctypes.c_int (inasceforafund)
        self.m_model.m_eagme.BASME_DETPIL_INASCEFORAFUND_LER (ctypes.byref (vardetpil),
                            ctypes.byref (varinasceforafund))
        inasceforafund  = varinasceforafund.value
        return          inasceforafund

    @canStartOutOfFoundation.setter
    def canStartOutOfFoundation (self, inasceforafund):
        """
        Pode nascer fora do piso fundação (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        varinasceforafund= ctypes.c_int (inasceforafund)
        self.m_model.m_eagme.BASME_DETPIL_INASCEFORAFUND_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (varinasceforafund))

    @property
    def isFictitious (self):
        """
        Pilar fictício (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        ificticio       = 0
        varificticio    = ctypes.c_int (ificticio)
        self.m_model.m_eagme.BASME_DETPIL_IFICTICIO_LER (ctypes.byref (vardetpil),
                            ctypes.byref (varificticio))
        ificticio       = varificticio.value
        return          ificticio

    @isFictitious.setter
    def isFictitious (self, ificticio):
        """
        Pilar fictício (0) não (1) sim
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        varificticio    = ctypes.c_int (ificticio)
        self.m_model.m_eagme.BASME_DETPIL_IFICTICIO_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (varificticio))

    @property
    def isShearWall (self):
        """
        Pilar parede para o BIM
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        ipilarpar       = 0
        varipilarpar    = ctypes.c_int (ipilarpar)
        self.m_model.m_eagme.BASME_DETPIL_IPILARPAR_LER (ctypes.byref (vardetpil),
                            ctypes.byref (varipilarpar))
        ipilarpar       = varipilarpar.value
        return          ipilarpar

    @isShearWall.setter
    def isShearWall (self, ipilarpar):
        """
        Pilar parede para o BIM
        """
        vardetpil       = ctypes.c_void_p (self.m_detpil)
        varipilarpar    = ctypes.c_int (ipilarpar)
        self.m_model.m_eagme.BASME_DETPIL_IPILARPAR_DEF (ctypes.byref (vardetpil),
                            ctypes.byref (varipilarpar))

#------------------------------------------------------------------------------
#       Dados de mola de pilar no pórtico CPorMol
#
class ColumnCoil ():

    def __init__ (self, model, pormol):
        """
        Dados de mola de pilar no pórtico\n
            model       <- Objeto Model() do modelo atual\n
            pormol      <- Apontador para objeto CPorMol
        """
        self.m_model    = model
        self.m_pormol   = pormol

    def GetSupportType (self, ires):
        """
        Tipo de apoio de pilar\n
            ires        <- Restrição a considerar COLUMNCOIL_IRES_xxxx\n
        Retorna:\n
            iapopor     -> Tipo de apoio COLUMNCOIL_IAPOPOR_xxxx
        """
        varpormol       = ctypes.c_void_p (self.m_pormol)
        varires         = ctypes.c_int (ires)
        iapopor         = 0
        variapopor      = ctypes.c_int (iapopor)
        self.m_model.m_eagme.BASME_PORMOL_IAPOPOR_LER (ctypes.byref (varpormol),
                           ctypes.byref (varires), ctypes.byref (variapopor))
        iapopor         = variapopor.value
        return          iapopor

    def SetSupportType (self, ires, iapopor):
        """
        Tipo de apoio de pilar\n
            ires        <- Restrição a considerar COLUMNCOIL_IRES_xxxx\n
            iapopor     <- Tipo de apoio COLUMNCOIL_IAPOPOR_xxxx
        """
        varpormol       = ctypes.c_void_p (self.m_pormol)
        varires         = ctypes.c_int (ires)
        variapopor      = ctypes.c_int (iapopor)
        self.m_model.m_eagme.BASME_PORMOL_IAPOPOR_DEF (ctypes.byref (varpormol),
                          ctypes.byref (varires), ctypes.byref (variapopor))

    def GetCoil (self, ires):
        """
        Coeficiente de mola\n
            ires        <- Restrição a considerar COLUMNCOIL_IRES_xxxx\n
        Retorna:\n
            pormola     -> Coeficiente de mola à Rotação tfm/rad Translação tf/m
        """
        varpormol       = ctypes.c_void_p (self.m_pormol)
        varires         = ctypes.c_int (ires)
        pormola         = 0.
        varpormola      = ctypes.c_double (pormola)
        self.m_model.m_eagme.BASME_PORMOL_PORMOLA_LER (ctypes.byref (varpormol),
                            ctypes.byref (varires), ctypes.byref (varpormola))
        pormola         = varpormola.value
        return          pormola

    def SetCoil (self, ires, pormola):
        """
        Coeficiente de mola\n
            ires        <- Restrição a considerar COLUMNCOIL_IRES_xxxx\n
            pormola     <- Coeficiente de mola à Rotação tfm/rad Translação tf/m
        """
        varpormol       = ctypes.c_void_p (self.m_pormol)
        varires         = ctypes.c_int (ires)
        varpormola      = ctypes.c_double (pormola)
        self.m_model.m_eagme.BASME_PORMOL_PORMOLA_DEF (ctypes.byref (varpormol),
                            ctypes.byref (varires), ctypes.byref (varpormola))

    def GetGap (self, igap):
        """
        Valor do gap (m) de restrição de apoio\n
            igap        <- Gap TIPO COLUMNCOIL_IGAP_xxxx\n
        Retorna:\n
            gap         -> Valor do gap (m)
        """
        varpormol       = ctypes.c_void_p (self.m_pormol)
        varigap         = ctypes.c_int (igap)
        gap             = 0.
        vargap          = ctypes.c_double (gap)
        self.m_model.m_eagme.BASME_PORMOL_GAP_LER (ctypes.byref (varpormol),
                            ctypes.byref (varigap), ctypes.byref (vargap))
        gap             = vargap.value
        return          gap

    def SetGap (self, igap, gap):
        """
        Valor do gap (m) de restrição de apoio\n
            igap        <- Gap TIPO COLUMNCOIL_IGAP_xxxx\n
            gap         <- Valor do gap (m)
        """
        varpormol       = ctypes.c_void_p (self.m_pormol)
        varigap         = ctypes.c_int (igap)
        vargap          = ctypes.c_double (gap)
        self.m_model.m_eagme.BASME_PORMOL_GAP_DEF (ctypes.byref (varpormol),
                            ctypes.byref (varigap), ctypes.byref (vargap))

#------------------------------------------------------------------------------
#       Dados de fundações CFundac
#
class FoundationData ():

    def __init__ (self, model, fundac):
        """
        Dados de fundações\n
            model       <- Objeto Model() do modelo atual\n
            fundac      <- Apontador para objeto CFundac
        """
        self.m_model    = model
        self.m_fundac  = fundac

    @property
    def type (self):
        """
        Tipo de fundação FOUNDATION_ITIPOFUNDAC_xxxx
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        itipofundac     = 0
        varitipofundac  = ctypes.c_int (itipofundac)
        self.m_model.m_eagme.BASME_FUNDAC_ITIPOFUNDAC_LER (ctypes.byref (varfundac),
                            ctypes.byref (varitipofundac))
        itipofundac     = varitipofundac.value
        return          itipofundac

    @type.setter
    def type (self, itipofundac):
        """
        Tipo de fundação FOUNDATION_ITIPOFUNDAC_xxxx
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varitipofundac  = ctypes.c_int (itipofundac)
        self.m_model.m_eagme.BASME_FUNDAC_ITIPOFUNDAC_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varitipofundac))
        
    @property
    def ficticiousColumn (self):
        """
        Pilar fictício definido (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        idimpildef      = 0
        varidimpildef   = ctypes.c_int (idimpildef)
        self.m_model.m_eagme.BASME_FUNDAC_PILFIC_IDIMPILDEF_LER (ctypes.byref (varfundac),
                            ctypes.byref (varidimpildef))
        idimpildef      = varidimpildef.value
        return          idimpildef

    @ficticiousColumn.setter
    def ficticiousColumn (self, idimpildef):
        """
        Pilar fictício definido (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varidimpildef   = ctypes.c_int (idimpildef)
        self.m_model.m_eagme.BASME_FUNDAC_PILFIC_IDIMPILDEF_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varidimpildef))
        
    @property
    def ficticiousColumnXDim (self):
        """
        Dimensão X de pilar fictício cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        dimxpildef      = 0
        vardimxpildef   = ctypes.c_double (dimxpildef)
        self.m_model.m_eagme.BASME_FUNDAC_PILFIC_DIMXPILDEF_LER (ctypes.byref (varfundac),
                            ctypes.byref (vardimxpildef))
        dimxpildef      = vardimxpildef.value
        return          dimxpildef

    @ficticiousColumnXDim.setter
    def ficticiousColumnXDim (self, dimxpildef):
        """
        Dimensão X de pilar fictício cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vardimxpildef   = ctypes.c_double (dimxpildef)
        self.m_model.m_eagme.BASME_FUNDAC_PILFIC_DIMXPILDEF_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vardimxpildef))

    @property
    def ficticiousColumnYDim (self):
        """
        Dimensão Y de pilar fictício cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        dimypildef      = 0
        vardimypildef   = ctypes.c_double (dimypildef)
        self.m_model.m_eagme.BASME_FUNDAC_PILFIC_DIMYPILDEF_LER (ctypes.byref (varfundac),
                            ctypes.byref (vardimypildef))
        dimypildef      = vardimypildef.value
        return          dimypildef

    @ficticiousColumnYDim.setter
    def ficticiousColumnYDim (self, dimypildef):
        """
        Dimensão X de pilar fictício cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vardimypildef   = ctypes.c_double (dimypildef)
        self.m_model.m_eagme.BASME_FUNDAC_PILFIC_DIMYPILDEF_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vardimypildef))

    @property
    def beamSupport (self):
        """
        Vigas apoiam na fundação (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        ivigapofun      = 0
        varivigapofun   = ctypes.c_int (ivigapofun)
        self.m_model.m_eagme.BASME_FUNDAC_IVIGAPOFUN_LER (ctypes.byref (varfundac),
                            ctypes.byref (varivigapofun))
        ivigapofun      = varivigapofun.value
        return          ivigapofun

    @beamSupport.setter
    def beamSupport (self, ivigapofun):
        """
        Vigas apoiam na fundação (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varivigapofun   = ctypes.c_int (ivigapofun)
        self.m_model.m_eagme.BASME_FUNDAC_IVIGAPOFUN_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varivigapofun))

    @property
    def footingXDim (self):
        """
        Sapatas, dimensão X da base cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        sapdimx         = 0
        varsapdimx      = ctypes.c_double (sapdimx)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPDIMX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsapdimx))
        sapdimx         = varsapdimx.value
        return          sapdimx

    @footingXDim.setter
    def footingXDim (self, sapdimx):
        """
        Sapatas, dimensão X da base cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsapdimx      = ctypes.c_double (sapdimx)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPDIMX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsapdimx))

    @property
    def footingYDim (self):
        """
        Sapatas, dimensão Y da base cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        sapdimy         = 0
        varsapdimy      = ctypes.c_double (sapdimy)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPDIMY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsapdimy))
        sapdimy         = varsapdimy.value
        return          sapdimy

    @footingYDim.setter
    def footingYDim (self, sapdimy):
        """
        Sapatas, dimensão Y da base cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsapdimy      = ctypes.c_double (sapdimy)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPDIMY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsapdimy))

    @property
    def footingTopXDim (self):
        """
        Sapatas, dimensão X do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        saptx           = 0
        varsaptx        = ctypes.c_double (saptx)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPTX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsaptx))
        saptx           = varsaptx.value
        return          saptx

    @footingTopXDim.setter
    def footingTopXDim (self, saptx):
        """
        Sapatas, dimensão X do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsaptx        = ctypes.c_double (saptx)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPTX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsaptx))

    @property
    def footingTopYDim (self):
        """
        Sapatas, dimensão Y do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        sapty           = 0
        varsapty        = ctypes.c_double (sapty)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPTY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsapty))
        sapty           = varsapty.value
        return          sapty

    @footingTopYDim.setter
    def footingTopYDim (self, sapty):
        """
        Sapatas, dimensão Y do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsapty        = ctypes.c_double (sapty)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPTY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsapty))

    @property
    def footingTopXExc (self):
        """
        Sapatas, excentricidade X do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        sapexcx         = 0
        varsapexcx      = ctypes.c_double (sapexcx)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPEXCX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsapexcx))
        sapexcx         = varsapexcx.value
        return          sapexcx

    @footingTopXExc.setter
    def footingTopXExc (self, sapexcx):
        """
        Sapatas, excentricidade X do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsapexcx      = ctypes.c_double (sapexcx)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPEXCX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsapexcx))

    @property
    def footingTopYExc (self):
        """
        Sapatas, eycentricidade Y do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        sapexcy         = 0
        varsapexcy      = ctypes.c_double (sapexcy)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPEXCY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsapexcy))
        sapexcy         = varsapexcy.value
        return          sapexcy

    @footingTopYExc.setter
    def footingTopYExc (self, sapexcy):
        """
        Sapatas, eycentricidade Y do topo cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsapexcy      = ctypes.c_double (sapexcy)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPEXCY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsapexcy))

    @property
    def footingTopExcLeft (self):
        """
        Sapata de divisa à esquerda (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        isapdive        = 0
        varisapdive     = ctypes.c_int (isapdive)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVE_LER (ctypes.byref (varfundac),
                            ctypes.byref (varisapdive))
        isapdive        = varisapdive.value
        return          isapdive

    @footingTopExcLeft.setter
    def footingTopExcLeft (self, isapdive):
        """
        Sapata de divisa à esquerda (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varisapdive     = ctypes.c_int (isapdive)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVE_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varisapdive))

    @property
    def footingTopExcAbove (self):
        """
        Sapata de divisa acima (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        isapdivc        = 0
        varisapdivc     = ctypes.c_int (isapdivc)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVC_LER (ctypes.byref (varfundac),
                            ctypes.byref (varisapdivc))
        isapdivc        = varisapdivc.value
        return          isapdivc

    @footingTopExcAbove.setter
    def footingTopExcAbove (self, isapdivc):
        """
        Sapata de divisa acima (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varisapdivc     = ctypes.c_int (isapdivc)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVC_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varisapdivc))

    @property
    def footingTopExcRight (self):
        """
        Sapata de divisa à direita (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        isapdivd        = 0
        varisapdivd     = ctypes.c_int (isapdivd)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVD_LER (ctypes.byref (varfundac),
                            ctypes.byref (varisapdivd))
        isapdivd        = varisapdivd.value
        return          isapdivd

    @footingTopExcRight.setter
    def footingTopExcRight (self, isapdivd):
        """
        Sapata de divisa à direita (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varisapdivd     = ctypes.c_int (isapdivd)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVD_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varisapdivd))

    @property
    def footingTopExcUnder (self):
        """
        Sapata de divisa abaixo (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        isapdivb        = 0
        varisapdivb     = ctypes.c_int (isapdivb)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVB_LER (ctypes.byref (varfundac),
                            ctypes.byref (varisapdivb))
        isapdivb        = varisapdivb.value
        return          isapdivb

    @footingTopExcUnder.setter
    def footingTopExcUnder (self, isapdivb):
        """
        Sapata de divisa abaixo (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varisapdivb     = ctypes.c_int (isapdivb)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_ISAPDIVB_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varisapdivb))

    @property
    def footingHeight (self):
        """
        Altura total cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        saphs           = 0
        varsaphs        = ctypes.c_double (saphs)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPHS_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsaphs))
        saphs           = varsaphs.value
        return          saphs

    @footingHeight.setter
    def footingHeight (self, saphs):
        """
        Altura total cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsaphs        = ctypes.c_double (saphs)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPHS_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsaphs))
    @property
    def footingXBaseBoard (self):
        """
        Altura X do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        saph0x          = 0
        varsaph0x       = ctypes.c_double (saph0x)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPH0X_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsaph0x))
        saph0x          = varsaph0x.value
        return          saph0x

    @footingXBaseBoard.setter
    def footingXBaseBoard (self, saph0x):
        """
        Altura X do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsaph0x       = ctypes.c_double (saph0x)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPH0X_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsaph0x))

    @property
    def footingYBaseBoard (self):
        """
        Altura Y do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        saph0y          = 0
        varsaph0y       = ctypes.c_double (saph0y)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPH0Y_LER (ctypes.byref (varfundac),
                            ctypes.byref (varsaph0y))
        saph0y          = varsaph0y.value
        return          saph0y

    @footingYBaseBoard.setter
    def footingYBaseBoard (self, saph0y):
        """
        Altura Y do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varsaph0y       = ctypes.c_double (saph0y)
        self.m_model.m_eagme.BASME_FUNDAC_SAPATAS_SAPH0Y_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varsaph0y))
        
    @property
    def pileCapX (self):
        """
        Base X do bloco, cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        blodimx         = 0
        varblodimx      = ctypes.c_double (blodimx)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODIMX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varblodimx))
        blodimx         = varblodimx.value
        return          blodimx

    @pileCapX.setter
    def pileCapX (self, blodimx):
        """
        Base X do bloco, cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varblodimx      = ctypes.c_double (blodimx)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODIMX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varblodimx))
        
    @property
    def pileCapY (self):
        """
        Base Y do bloco, cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        blodimy         = 0
        varblodimy      = ctypes.c_double (blodimy)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODIMY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varblodimy))
        blodimy         = varblodimy.value
        return          blodimy

    @pileCapY.setter
    def pileCapY (self, blodimy):
        """
        Base Y do bloco, cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varblodimy      = ctypes.c_double (blodimy)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODIMY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varblodimy))
        
    @property
    def pileCapHeight (self):
        """
        Altura do bloco, cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        bloalt          = 0
        varbloalt       = ctypes.c_double (bloalt)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLOALT_LER (ctypes.byref (varfundac),
                            ctypes.byref (varbloalt))
        bloalt          = varbloalt.value
        return          bloalt

    @pileCapHeight.setter
    def pileCapHeight (self, bloalt):
        """
        Altura do bloco, cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varbloalt       = ctypes.c_double (bloalt)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLOALT_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varbloalt))

    @property
    def pileCapPiles (self):
        """
        Número de estacas do bloco
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        numest          = 0
        varnumest       = ctypes.c_int (numest)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_NUMEST_LER (ctypes.byref (varfundac),
                            ctypes.byref (varnumest))
        numest          = varnumest.value
        return          numest

    @pileCapPiles.setter
    def pileCapPiles (self, numest):
        """
        Número de estacas do bloco
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varnumest       = ctypes.c_int (numest)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_NUMEST_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varnumest))

    @property
    def pileCapFormat (self):
        """
        Formato (0..) Varia com o número de estacas
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        iblofor         = 0
        variblofor      = ctypes.c_int (iblofor)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_IBLOFOR_LER (ctypes.byref (varfundac),
                            ctypes.byref (variblofor))
        iblofor         = variblofor.value
        return          iblofor

    @pileCapFormat.setter
    def pileCapFormat (self, iblofor):
        """
        Formato (0..) Varia com o número de estacas
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        variblofor      = ctypes.c_int (iblofor)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_IBLOFOR_DEF (ctypes.byref (varfundac),
                            ctypes.byref (variblofor))

    @property
    def pileCapDiameter (self):
        """
        Diâmetro da estaca cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        blodiam         = 0
        varblodiam      = ctypes.c_double (blodiam)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODIAM_LER (ctypes.byref (varfundac),
                            ctypes.byref (varblodiam))
        blodiam         = varblodiam.value
        return          blodiam

    @pileCapDiameter.setter
    def pileCapDiameter (self, blodiam):
        """
        Diâmetro da estaca cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varblodiam      = ctypes.c_double (blodiam)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODIAM_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varblodiam))

    @property
    def pileCapHeightW (self):
        """
        Altura da estaca dentro do bloco cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        bloaltb         = 0
        varbloaltb      = ctypes.c_double (bloaltb)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLOALTB_LER (ctypes.byref (varfundac),
                            ctypes.byref (varbloaltb))
        bloaltb         = varbloaltb.value
        return          bloaltb

    @pileCapHeightW.setter
    def pileCapHeightW (self, bloaltb):
        """
        Altura da estaca dentro do bloco cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varbloaltb      = ctypes.c_double (bloaltb)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLOALTB_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varbloaltb))

    @property
    def pileCapPileXDist (self):
        """
        Distância X entre eixos de estacas cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        blodistx        = 0
        varblodistx     = ctypes.c_double (blodistx)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODISTX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varblodistx))
        blodistx        = varblodistx.value
        return          blodistx

    @pileCapPileXDist.setter
    def pileCapPileXDist (self, blodistx):
        """
        Distância X entre eixos de estacas cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varblodistx     = ctypes.c_double (blodistx)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODISTX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varblodistx))

    @property
    def pileCapPileYDist (self):
        """
        Distância Y entre eiyos de estacas cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        blodisty        = 0
        varblodisty     = ctypes.c_double (blodisty)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODISTY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varblodisty))
        blodisty        = varblodisty.value
        return          blodisty

    @pileCapPileYDist.setter
    def pileCapPileYDist (self, blodisty):
        """
        Distância Y entre eiyos de estacas cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varblodisty     = ctypes.c_double (blodisty)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLODISTY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varblodisty))

    @property
    def pileCapPileFaceDist (self):
        """
        Distância do eixo da estaca à face do bloco cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        distface        = 0
        vardistface     = ctypes.c_double (distface)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_DISTFACE_LER (ctypes.byref (varfundac),
                            ctypes.byref (vardistface))
        distface        = vardistface.value
        return          distface

    @pileCapPileFaceDist.setter
    def pileCapPileFaceDist (self, distface):
        """
        Distância do eixo da estaca à face do bloco cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vardistface     = ctypes.c_double (distface)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_DISTFACE_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vardistface))

    @property
    def pileCapDistMode (self):
        """
        Cálculo da dimensão do bloco (0) dimensões fornecidas (1) distância entre estacas
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        icalceix        = 0
        varicalceix     = ctypes.c_int (icalceix)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_ICALCEIX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varicalceix))
        icalceix        = varicalceix.value
        return          icalceix

    @pileCapDistMode.setter
    def pileCapDistMode (self, icalceix):
        """
        Cálculo da dimensão do bloco (0) dimensões fornecidas (1) distância entre estacas
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varicalceix     = ctypes.c_int (icalceix)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_ICALCEIX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varicalceix))

    @property
    def pileCapPileHeight (self):
        """
        Altura das estacas cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        bloaltesc       = 0
        varbloaltesc    = ctypes.c_double (bloaltesc)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLOALTESC_LER (ctypes.byref (varfundac),
                            ctypes.byref (varbloaltesc))
        bloaltesc       = varbloaltesc.value
        return          bloaltesc

    @pileCapPileHeight.setter
    def pileCapPileHeight (self, bloaltesc):
        """
        Altura das estacas cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varbloaltesc    = ctypes.c_double (bloaltesc)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_BLOALTESC_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varbloaltesc))
    @property
    def pileCapOverPiers (self):
        """
        Bloco sobre tubulões (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        iblocotub       = 0
        variblocotub    = ctypes.c_int (iblocotub)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_IBLOCOTUB_LER (ctypes.byref (varfundac),
                            ctypes.byref (variblocotub))
        iblocotub       = variblocotub.value
        return          iblocotub

    @pileCapOverPiers.setter
    def pileCapOverPiers (self, iblocotub):
        """
        Bloco sobre tubulões (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        variblocotub    = ctypes.c_int (iblocotub)
        self.m_model.m_eagme.BASME_FUNDAC_BLOCOS_IBLOCOTUB_DEF (ctypes.byref (varfundac),
                            ctypes.byref (variblocotub))

    @property
    def pierShaftDiameter (self):
        """
        Tubulão - diâmetro do fuste cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubdia          = 0
        vartubdia       = ctypes.c_double (tubdia)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBDIA_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubdia))
        tubdia          = vartubdia.value
        return          tubdia

    @pierShaftDiameter.setter
    def pierShaftDiameter (self, tubdia):
        """
        Tubulão - diâmetro do fuste cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubdia       = ctypes.c_double (tubdia)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBDIA_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubdia))
       
    @property
    def pierShaftHeight (self):
        """
        Tubulão - altura do fuste cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubalt          = 0
        vartubalt       = ctypes.c_double (tubalt)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBALT_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubalt))
        tubalt          = vartubalt.value
        return          tubalt

    @pierShaftHeight.setter
    def pierShaftHeight (self, tubalt):
        """
        Tubulão - altura do fuste cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubalt       = ctypes.c_double (tubalt)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBALT_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubalt))
       
    @property
    def pierBaseboardDiameter (self):
        """
        Tubulão - diâmetro do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubdiarod       = 0
        vartubdiarod    = ctypes.c_double (tubdiarod)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBDIAROD_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubdiarod))
        tubdiarod       = vartubdiarod.value
        return          tubdiarod

    @pierBaseboardDiameter.setter
    def pierBaseboardDiameter (self, tubdiarod):
        """
        Tubulão - diâmetro do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubdiarod    = ctypes.c_double (tubdiarod)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBDIAROD_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubdiarod))
       
    @property
    def pierBaseboardHeight (self):
        """
        Tubulão - altura do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubaltrod       = 0
        vartubaltrod    = ctypes.c_double (tubaltrod)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBALTROD_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubaltrod))
        tubaltrod       = vartubaltrod.value
        return          tubaltrod

    @pierBaseboardHeight.setter
    def pierBaseboardHeight (self, tubaltrod):
        """
        Tubulão - altura do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubaltrod    = ctypes.c_double (tubaltrod)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBALTROD_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubaltrod))

    @property
    def pierBaseboardCone (self):
        """
        Tubulão - altura do cone cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubaltcon       = 0
        vartubaltcon    = ctypes.c_double (tubaltcon)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBALTCON_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubaltcon))
        tubaltcon       = vartubaltcon.value
        return          tubaltcon

    @pierBaseboardCone.setter
    def pierBaseboardCone (self, tubaltcon):
        """
        Tubulão - altura do rodapé cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubaltcon    = ctypes.c_double (tubaltcon)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBALTCON_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubaltcon))

    @property
    def pierFalseEllipse (self):
        """
        Tubulão com base alargada (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        itubalarg       = 0
        varitubalarg    = ctypes.c_int (itubalarg)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_ITUBALARG_LER (ctypes.byref (varfundac),
                            ctypes.byref (varitubalarg))
        itubalarg       = varitubalarg.value
        return          itubalarg

    @pierFalseEllipse.setter
    def pierFalseEllipse (self, itubalarg):
        """
        Tubulão com base alargada (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varitubalarg    = ctypes.c_int (itubalarg)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_ITUBALARG_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varitubalarg))

    @property
    def pierFalseEllipseWidth (self):
        """
        Tubulão - alargamento da base cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubbasalarg     = 0
        vartubbasalarg  = ctypes.c_double (tubbasalarg)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBBASALARG_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubbasalarg))
        tubbasalarg     = vartubbasalarg.value
        return          tubbasalarg

    @pierFalseEllipseWidth.setter
    def pierFalseEllipseWidth (self, tubbasalarg):
        """
        Tubulão - alargamento da base cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubbasalarg  = ctypes.c_double (tubbasalarg)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBBASALARG_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubbasalarg))

    @property
    def pierFalseEllipseAngle (self):
        """
        Tubulão - Rotação da base, sistema global, graus
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        tubangrot       = 0
        vartubangrot    = ctypes.c_double (tubangrot)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBANGROT_LER (ctypes.byref (varfundac),
                            ctypes.byref (vartubangrot))
        tubangrot       = vartubangrot.value
        return          tubangrot

    @pierFalseEllipseAngle.setter
    def pierFalseEllipseAngle (self, tubangrot):
        """
        Tubulão - Rotação da base, sistema global, graus
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vartubangrot    = ctypes.c_double (tubangrot)
        self.m_model.m_eagme.BASME_FUNDAC_TUBULAO_TUBANGROT_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vartubangrot))

    @property
    def pocketFoundation (self):
        """
        Fundação em cálice (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        icalice         = 0
        varicalice      = ctypes.c_int (icalice)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_ICALICE_LER (ctypes.byref (varfundac),
                            ctypes.byref (varicalice))
        icalice         = varicalice.value
        return          icalice

    @pocketFoundation.setter
    def pocketFoundation (self, icalice):
        """
        Fundação em cálice (0) não (1) sim
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varicalice      = ctypes.c_int (icalice)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_ICALICE_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varicalice))

    @property
    def pocketFoundationFormat (self):
        """
        Cálice: Formato FOUNDATION_FORM_xxxxx
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        iformato        = 0
        variformato     = ctypes.c_int (iformato)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_IFORMATO_LER (ctypes.byref (varfundac),
                            ctypes.byref (variformato))
        iformato         = variformato.value
        return          iformato

    @pocketFoundationFormat.setter
    def pocketFoundationFormat (self, iformato):
        """
        Cálice: Formato FOUNDATION_FORM_xxxxx
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        variformato     = ctypes.c_int (iformato)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_IFORMATO_DEF (ctypes.byref (varfundac),
                            ctypes.byref (variformato))

    @property
    def pocketFoundationRoughness (self):
        """
        Cálice: Rugosidade FOUNDATION_RUGO_xxxx
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        icalrugos       = 0
        varicalrugos    = ctypes.c_int (icalrugos)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_ICALRUGOS_LER (ctypes.byref (varfundac),
                            ctypes.byref (varicalrugos))
        icalrugos       = varicalrugos.value
        return          icalrugos

    @pocketFoundationRoughness.setter
    def pocketFoundationRoughness (self, icalrugos):
        """
        Cálice: Rugosidade FOUNDATION_RUGO_xxxx
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varicalrugos    = ctypes.c_int (icalrugos)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_ICALRUGOS_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varicalrugos))

    @property
    def pocketFoundationXDim (self):
        """
        Cálice: dimensão X em planta cm (D circular)
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        dimx            = 0
        vardimx         = ctypes.c_double (dimx)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_DIMX_LER (ctypes.byref (varfundac),
                            ctypes.byref (vardimx))
        dimx            = vardimx.value
        return          dimx

    @pocketFoundationXDim.setter
    def pocketFoundationXDim (self, dimx):
        """
        Cálice: dimensão X em planta cm (D circular)
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vardimx         = ctypes.c_double (dimx)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_DIMX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vardimx))

    @property
    def pocketFoundationYDim (self):
        """
        Cálice: dimensão Y em planta cm (D circular)
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        dimy            = 0
        vardimy         = ctypes.c_double (dimy)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_DIMY_LER (ctypes.byref (varfundac),
                            ctypes.byref (vardimy))
        dimy            = vardimy.value
        return          dimy

    @pocketFoundationYDim.setter
    def pocketFoundationYDim (self, dimy):
        """
        Cálice: dimensão Y em planta cm (D circular)
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vardimy         = ctypes.c_double (dimy)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_DIMY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vardimy))

    @property
    def pocketFoundationXWall (self):
        """
        Cálice: dimensão parede X cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        parx            = 0
        varparx         = ctypes.c_double (parx)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_PARX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varparx))
        parx            = varparx.value
        return          parx

    @pocketFoundationXWall.setter
    def pocketFoundationXWall (self, parx):
        """
        Cálice: dimensão parede X cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varparx         = ctypes.c_double (parx)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_PARX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varparx))
        
    @property
    def pocketFoundationYWall (self):
        """
        Cálice: dimensão parede Y cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        pary            = 0
        varpary         = ctypes.c_double (pary)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_PARY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varpary))
        pary            = varpary.value
        return          pary

    @pocketFoundationYWall.setter
    def pocketFoundationYWall (self, pary):
        """
        Cálice: dimensão parede Y cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varpary         = ctypes.c_double (pary)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_PARY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varpary))

    @property
    def pocketFoundationXExc (self):
        """
        Cálice: Excentricidade X em relação ao centro da fundação cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        excx            = 0
        varexcx         = ctypes.c_double (excx)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_EXCX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varexcx))
        excx            = varexcx.value
        return          excx

    @pocketFoundationXExc.setter
    def pocketFoundationXExc (self, excx):
        """
        Cálice: Excentricidade X em relação ao centro da fundação cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varexcx         = ctypes.c_double (excx)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_EXCX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varexcx))

    @property
    def pocketFoundationYExc (self):
        """
        Cálice: Excentricidade Y em relação ao centro da fundação cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        excy            = 0
        varexcy         = ctypes.c_double (excy)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_EXCY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varexcy))
        excy            = varexcy.value
        return          excy

    @pocketFoundationYExc.setter
    def pocketFoundationYExc (self, excy):
        """
        Cálice: Excentricidade Y em relação ao centro da fundação cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varexcy         = ctypes.c_double (excy)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_EXCY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varexcy))

    @property
    def pocketFoundationXInc (self):
        """
        Cálice: Caimento X planta parede interna cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        caix            = 0
        varcaix         = ctypes.c_double (caix)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_CAIX_LER (ctypes.byref (varfundac),
                            ctypes.byref (varcaix))
        caix            = varcaix.value
        return          caix

    @pocketFoundationXInc.setter
    def pocketFoundationXInc (self, caix):
        """
        Cálice: Caimento X planta parede interna cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varcaix         = ctypes.c_double (caix)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_CAIX_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varcaix))

    @property
    def pocketFoundationYInc (self):
        """
        Cálice: Caimento Y planta parede interna cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        caiy            = 0
        varcaiy         = ctypes.c_double (caiy)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_CAIY_LER (ctypes.byref (varfundac),
                            ctypes.byref (varcaiy))
        caiy            = varcaiy.value
        return          caiy

    @pocketFoundationYInc.setter
    def pocketFoundationYInc (self, caiy):
        """
        Cálice: Caimento Y planta parede interna cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varcaiy         = ctypes.c_double (caiy)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_CAIY_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varcaiy))

    @property
    def pocketFoundationHeight (self):
        """
        Cálice: Altura cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        hcalice         = 0
        varhcalice      = ctypes.c_double (hcalice)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_HCALICE_LER (ctypes.byref (varfundac),
                            ctypes.byref (varhcalice))
        hcalice            = varhcalice.value
        return          hcalice

    @pocketFoundationHeight.setter
    def pocketFoundationHeight (self, hcalice):
        """
        Cálice: Altura cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        varhcalice      = ctypes.c_double (hcalice)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_HCALICE_DEF (ctypes.byref (varfundac),
                            ctypes.byref (varhcalice))

    @property
    def pocketFoundationRecess (self):
        """
        Cálice: Rebaixo em relação ao nível da fundação cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        dfs             = 0
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_DFS_LER (ctypes.byref (varfundac),
                            ctypes.byref (vardfs))
        dfs             = vardfs.value
        return          dfs

    @pocketFoundationRecess.setter
    def pocketFoundationRecess (self, dfs):
        """
        Cálice: Rebaixo em relação ao nível da fundação cm
        """
        varfundac       = ctypes.c_void_p (self.m_fundac)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_FUNDAC_CALICE_DFS_DEF (ctypes.byref (varfundac),
                            ctypes.byref (vardfs))

#------------------------------------------------------------------------------
#       Dados de pilares pré-moldados CPreGPil
#
class ColumnPrecastData ():

    def __init__ (self, model, pregpil):
        """
        Dados de usuário para o BIM\n
            model       <- Objeto Model() do modelo atual\n
            pregpil     <- Apontador para objeto CPreGPil
        """
        self.m_model    = model
        self.m_pregpil  = pregpil

    @property
    def precastRegion (self):
        """
        Pilar pré-moldado: região construtiva
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        iregiao         = 0
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_PREGPIL_IREGIAO_LER (ctypes.byref (varpregpil),
                            ctypes.byref (variregiao))
        iregiao         = variregiao.value
        return          iregiao

    @precastRegion.setter
    def precastRegion (self, iregiao):
        """
        Pilar pré-moldado: região construtiva
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_PREGPIL_IREGIAO_DEF (ctypes.byref (varpregpil),
                            ctypes.byref (variregiao))

    @property
    def isPrecast (self):
        """
        Pilar pré-moldado: (0) Não (1) Sim
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        ipremoldado     = 0
        varipremoldado  = ctypes.c_int (ipremoldado)
        self.m_model.m_eagme.BASME_PREGPIL_IPREMOLDADO_LER (ctypes.byref (varpregpil),
                            ctypes.byref (varipremoldado))
        ipremoldado     = varipremoldado.value
        return          ipremoldado

    @isPrecast.setter
    def isPrecast (self, ipremoldado):
        """
        Pilar pré-moldado: (0) Não (1) Sim
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        varipremoldado  = ctypes.c_int (ipremoldado)
        self.m_model.m_eagme.BASME_PREGPIL_IPREMOLDADO_DEF (ctypes.byref (varpregpil),
                            ctypes.byref (varipremoldado))

    @property
    def rebarBundling (self):
        """
        Pilar pré-moldado: Alojamento de armadura (0)Critérios (1)TQS Pilar (2)Feixe
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        iarmfeixepil    = 0
        variarmfeixepil = ctypes.c_int (iarmfeixepil)
        self.m_model.m_eagme.BASME_PREGPIL_IARMFEIXEPIL_LER (ctypes.byref (varpregpil),
                            ctypes.byref (variarmfeixepil))
        iarmfeixepil    = variarmfeixepil.value
        return          iarmfeixepil

    @rebarBundling.setter
    def rebarBundling (self, iarmfeixepil):
        """
        Pilar pré-moldado: Alojamento de armadura (0)Critérios (1)TQS Pilar (2)Feixe
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        variarmfeixepil = ctypes.c_int (iarmfeixepil)
        self.m_model.m_eagme.BASME_PREGPIL_IARMFEIXEPIL_DEF (ctypes.byref (varpregpil),
                            ctypes.byref (variarmfeixepil))

    @property
    def rainWaterPipe (self):
        """
        Tubo de água pluvial 
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        preagua         = None
        varpreagua      = ctypes.c_void_p (preagua)
        self.m_model.m_eagme.BASME_PREGPIL_PREAGUA_LER (ctypes.byref (varpregpil),
                            ctypes.byref (varpreagua))
        preagua         = varpreagua.value
        rainwaterpipe   = RainWaterPipe (self.m_model, preagua)
        return          rainwaterpipe

    @property
    def liftingAnchors (self):
        """
        Alça de içamento de pilares pré-moldados
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        prealca         = None
        varprealca      = ctypes.c_void_p (prealca)
        self.m_model.m_eagme.BASME_PREGPIL_PREALCA_LER (ctypes.byref (varpregpil),
                            ctypes.byref (varprealca))
        prealca         = varprealca.value
        liftinganchors  = LiftingAnchors (self.m_model, prealca)
        return          liftinganchors

    @property
    def liftOpenning (self):
        """
        Furos de levantamento de pilares pré-moldados
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        prefur          = None
        varprefur       = ctypes.c_void_p (prefur)
        self.m_model.m_eagme.BASME_PREGPIL_PREFUR_LER (ctypes.byref (varpregpil),
                            ctypes.byref (varprefur))
        prefur          = varprefur.value
        liftinghole     = LiftOpenning (self.m_model, prefur)
        return          liftinghole

    @property
    def preCastGroup (self):
        """
        Grupo de pré-moldados
        """
        varpregpil      = ctypes.c_void_p (self.m_pregpil)
        grupopre        = None
        vargrupopre     = ctypes.c_void_p (grupopre)
        self.m_model.m_eagme.BASME_PREGPIL_GRUPOPRE_LER (ctypes.byref (varpregpil),
                            ctypes.byref (vargrupopre))
        grupopre        = vargrupopre.value
        preCastGroup    = PreCastGroup (self.m_model, grupopre)
        return          preCastGroup

#------------------------------------------------------------------------------
#       Seção de pilar - um pilar pode ter várias seções ao longo do edifício - CSecPil
#
class ColumnSection (SMObject):

    def __init__ (self, column, model, floor, secpil):
        """
        Seção de pilar - um pilar pode ter várias seções ao longo do edifício\n
            column      <- Objeto Column que abriga esta seção ou None\n
            model       <- Objeto Model() do modelo atual\n
            secpil      <- Apontador para objeto CSecPil
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_secpil   = secpil
        if              (column == None):
            varsecpil   = ctypes.c_void_p (self.m_secpil)
            pilar       = None
            varpilar    = ctypes.c_void_p (pilar)
            self.m_model.m_eagme.BASME_SECPIL_PILAR_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varpilar))
            pilar       = varpilar.value
            column      = Column (self.m_model, self.m_floor, pilar)

        self.m_column   = column
        super().__init__(model, self.m_secpil)

    @property
    def column (self):
        """
        Retorna pilar Column() correspondente à seção
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        pilar           = None
        varpilar        = ctypes.c_void_p (pilar)
        self.m_model.m_eagme.BASME_SECPIL_PILAR_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varpilar))
        pilar           = varpilar.value
        return          Column (self.m_model, self.m_floor, pilar)

    @property
    def insertionX (self):
        """
        Ponto de inserção X\n
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        xins            = 0.
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_SECPIL_PTINSX_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varxins))
        xins            = varxins.value
        return          xins

    @insertionX.setter
    def insertionX (self, xins):
        """
        Ponto de inserção X
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_SECPIL_PTINSX_DEF (ctypes.byref (varsecpil), 
                            ctypes.byref (varxins))

    @property
    def insertionY (self):
        """
        Ponto de inserção Y
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        yins            = 0.
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_SECPIL_PTINSY_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varyins))
        yins            = varyins.value
        return          yins

    @insertionY.setter
    def insertionY (self, yins):
        """
        Ponto de inserção Y
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_SECPIL_PTINSY_DEF (ctypes.byref (varsecpil), 
                            ctypes.byref (varyins))

    def GetColumnFloorData (self, floor):
        """
        Retorna um objeto com informações por planta\n
            floor       <- Pavimento Floor()\n
        Retorna:\n
            objeto      ColumnFloorData()
        """
        varfabrica      = ctypes.c_void_p (floor.m_fabrica)
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        infopla         = None
        varinfopla      = ctypes.c_void_p (infopla)
        self.m_model.m_eagme.BASME_SECPIL_INFOPLA_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varsecpil), ctypes.byref (varinfopla))
        infopla         = varinfopla.value
        columnFloordata = ColumnFloorData (self.m_model, infopla)
        return          columnFloordata

    def GetColumnBoundaryCond (self, floor):
        """
        Retorna objeto de condições de contorno de grelha\n
            floor           <- Pavimento Floor()\n
        Retorna:\n
            objeto ColumnBoundaryCond()
        """
        varfabrica      = ctypes.c_void_p (floor.m_fabrica)
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        contpil         = None
        varcontpil      = ctypes.c_void_p (contpil)
        self.m_model.m_eagme.BASME_SECPIL_CONTPIL_LER (ctypes.byref (varfabrica),
                            ctypes.byref (varsecpil), ctypes.byref (varcontpil))
        contpil         = varcontpil.value
        columnBoundaryCond = ColumnBoundaryCond (self.m_model, contpil)
        return          columnBoundaryCond

    def SetColumnBoundaryMode (self, floor, idefcontpil):
        """
        Define se as condições de contorno são por seção de pilar ou planta\n
            floor           <- Pavimento Floor()\n
            idefcontpil     <- Condições de contorno por (0) seção (1) planta
        """
        varfabrica      = ctypes.c_void_p (floor.m_fabrica)
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varidefcontpil  = ctypes.c_int (idefcontpil)
        self.m_model.m_eagme.BASME_SECPIL_IDEFCONTPIL_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varsecpil), ctypes.byref (varidefcontpil))

    def GetShearWallStripNum (self):
        """
        Retorna o número de lâminas de discretização de pilares parede
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        numlam          = 0
        varnumlam       = ctypes.c_int (numlam)
        self.m_model.m_eagme.BASME_SECPIL_LAMINAS_NUMERO_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varnumlam))
        numlam          = varnumlam.value
        return          numlam

    def GetShearWallStripNumPts (self, ilam):
        """
        Retorna o número de pontos de uma lâmina\n
            ilam                <- índice da lâmina 0..GetShearWallStripNum()-1
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varilam         = ctypes.c_int (ilam)
        numpts          = 0
        varnumpts       = ctypes.c_int (numpts)
        self.m_model.m_eagme.BASME_SECPIL_LAMINAS_NUMPTS_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varilam), ctypes.byref (varnumpts))
        numpts          = varnumpts.value
        return          numpts

    def GetShearWallStripPoint (self, ilam, ipt):
        """
        Retorna o número de pontos de uma lâmina\n
            ilam                <- Índice da lâmina 0..GetShearWallStripNum()-1\n
            ipt                 <- Índice do ponto 0..GetShearWallStripNumPts()-1\n
        Retorna:\n
            double x, y         -> Um ponto da lâmina
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varilam         = ctypes.c_int (ilam)
        vaript          = ctypes.c_int (ipt)
        x               = 0.
        varx            = ctypes.c_double (x)
        y               = 0.
        vary            = ctypes.c_double (y)
        self.m_model.m_eagme.BASME_SECPIL_LAMINAS_PONTO_LER (ctypes.byref (varsecpil), 
                            ctypes.byref (varilam), ctypes.byref (vaript), 
                            ctypes.byref (varx), ctypes.byref (vary))
        x               = varx.value
        y               = vary.value
        return          x, y

    @property
    def columnGeometry (self):
        """
        Dados de geometria de pilar
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        geopil          = None
        vargeopil       = ctypes.c_void_p (geopil)
        self.m_model.m_eagme.BASME_SECPIL_GEOPIL_LER (ctypes.byref (varsecpil),
                            ctypes.byref (vargeopil))
        geopil          = vargeopil.value
        columngeometry  = ColumnGeometry (self.m_model, geopil)
        return          columngeometry

    @property
    def sectionPolig (self):
        """
        Seção transversal
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        polig           = None
        varpolig        = ctypes.c_void_p (polig)
        self.m_model.m_eagme.BASME_SECPIL_POLIG_LER (ctypes.byref (varsecpil),
                            ctypes.byref (varpolig))
        polig           = varpolig.value
        sectionPoligx   = Polygon (self.m_model, polig)
        return          sectionPoligx

    @property
    def sectionLastFloor (self):
        """
        Última planta da seção (string)
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varplamorre     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_SECPIL_PLAMORRE_LER (ctypes.byref (varsecpil),
                                varplamorre)
        plamorre        = varplamorre.value.decode(TQSUtil.CHARSET)
        return          plamorre

    @sectionLastFloor.setter
    def sectionLastFloor (self, plamorre):
        """
        Última planta da seção (string)
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        varplamorre     = ctypes.c_char_p (plamorre.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_SECPIL_PLAMORRE_DEF (ctypes.byref (varsecpil),
                                varplamorre)

    @property
    def columnInsertion (self):
        """
        Dados de inserção de pilar
        """
        varsecpil       = ctypes.c_void_p (self.m_secpil)
        inspil          = None
        varinspil       = ctypes.c_void_p (inspil)
        self.m_model.m_eagme.BASME_SECPIL_INSPIL_LER (ctypes.byref (varsecpil),
                            ctypes.byref (varinspil))
        inspil          = varinspil.value
        columninsertion = ColumnInsertion (self.m_model, inspil)
        return          columninsertion

#------------------------------------------------------------------------------
#       Dados de usuário para o BIM - CUsrAtrib
#
class UserAttrib ():

    def __init__ (self, model, usratrib):
        """
        Dados de usuário para o BIM\n
            model       <- Objeto Model() do modelo atual\n
            usratrib    <- Apontador para objeto CUsrAtrib
        """
        self.m_model    = model
        self.m_usratrib = usratrib

    def usratribClear (self):
        """
        Limpa atributos do usuário
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        self.m_model.m_eagme.BASME_USRATRIB_LIMPAR (ctypes.byref (varusratrib))

    def usratribNum (self):
        """
        Retorna o número de atributos
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        numatrib        = 0
        varnumatrib     = ctypes.c_int (numatrib)
        self.m_model.m_eagme.BASME_USRATRIB_NUMATRIB_LER (ctypes.byref (varusratrib),
                            ctypes.byref (varnumatrib))
        numatrib        = varnumatrib.value
        return          numatrib

    def usratribInsert (self, chave, sval):
        """
        Insere novo atributo\n
            char *chave         <- Chave\n
            char *sval          <- Valor
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        varchave        = ctypes.c_char_p (chave.encode (TQSUtil.CHARSET))
        varsval         = ctypes.c_char_p (sval.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_USRATRIB_INSERIR (ctypes.byref (varusratrib),
                            varchave, varsval)
    def usratribErase (self, chave):
        """
        Apaga atributo existente\n
            char *chave         <- Chave do atributo a apagar
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        varchave        = ctypes.c_char_p (chave.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_USRATRIB_APAGAR (ctypes.byref (varusratrib),
                            ctypes.byref (varchave))

    def usratribBegin (self):
        """
        Prepara para ler todos os atributos
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        self.m_model.m_eagme.BASME_USRATRIB_PREPLER (ctypes.byref (varusratrib))

    def usratribReadNext (self):
        """
        Lê próximo atributo\n
        Retorna:\n
            char *chave,        -> Chave\n
            char *sval,         -> Valor\n
            int  istat          -> (0) Ok (!=0) Acabou
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        varchave        = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        varsval         = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_USRATRIB_LERPROX (ctypes.byref (varusratrib),
                            varchave, varsval, ctypes.byref (varistat))
        istat           = varistat.value
        if              (istat == 0):
            chave       = varchave.value.decode(TQSUtil.CHARSET)
            sval        = varsval.value.decode(TQSUtil.CHARSET)
        else:
            chave       = ""
            sval        = ""
        return          chave, sval, istat

    def usratribFind (self, chave):
        """
        Lê próximo atributo\n
            char *chave,        <- Chave a pesquisar\n
        Retorna:\n
            char *sval,         -> Valor\n
            int  istat          -> (0) Ok (!=0) Acabou
        """
        varusratrib     = ctypes.c_void_p (self.m_usratrib)
        varchave        = ctypes.c_char_p (chave.encode (TQSUtil.CHARSET))
        varsval         = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_USRATRIB_ACHAR (ctypes.byref (varusratrib),
                            varchave, varsval, ctypes.byref (varistat))
        istat           = varistat.value
        if              (istat == 0):
            sval        = varsval.value.decode(TQSUtil.CHARSET)
        else:
            sval        = ""
        return          sval, istat
#------------------------------------------------------------------------------
#        Informações por planta, associadas a seções de pilares - CInfoPla
#
class ColumnFloorData ():

    def __init__ (self, model, infopla):
        """
        Informações por planta, associadas à seção de pilar\n
            model       <- Objeto Model() do modelo atual\n
            infopla     <- Apontador para objeto CInfoPla
        """
        self.m_model    = model
        self.m_infopla  = infopla

    @property
    def infoByFloor (self):
        """
        Informações de pilares por (0) Seção de pilar (1) Planta
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        idefcontpil     = 0
        varidefcontpil  = ctypes.c_int (idefcontpil)
        self.m_model.m_eagme.BASME_INFOPLA_IDEFCONTPIL_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varidefcontpil))
        idefcontpil     = varidefcontpil.value
        return          idefcontpil

    @infoByFloor.setter
    def infoByFloor (self, idefcontpil):
        """
        Informações de pilares por (0) Seção de pilar (1) Planta
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varidefcontpil  = ctypes.c_int (idefcontpil)
        self.m_model.m_eagme.BASME_INFOPLA_IDEFCONTPIL_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varidefcontpil))

    @property
    def columnBoundaryCond (self):
        """
        Condições de contorno de pilares
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        contpil         = None
        varcontpil      = ctypes.c_void_p (contpil)
        self.m_model.m_eagme.BASME_INFOPLA_CONTPIL_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varcontpil))
        contpil         = varcontpil.value
        columnboundarycond = ColumnBoundaryCond (self.m_model, contpil)
        return          columnboundarycond

    @property
    def columnBucklingX (self):
        """
        Coeficiente de flambagem X
        """
        varinfopla       = ctypes.c_void_p (self.m_infopla)
        cflamx          = 0
        varcflamx       = ctypes.c_double (cflamx)
        self.m_model.m_eagme.BASME_INFOPLA_CFLAMX_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varcflamx))
        cflamx          = varcflamx.value
        return          cflamx

    @columnBucklingX.setter
    def columnBucklingX (self, cflamx):
        """
        Coeficiente de flambagem X
        """
        varinfopla       = ctypes.c_void_p (self.m_infopla)
        varcflamx       = ctypes.c_double (cflamx)
        self.m_model.m_eagme.BASME_INFOPLA_CFLAMX_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varcflamx))

    @property
    def columnBucklingY (self):
        """
        Coeficiente de flambagem Y
        """
        varinfopla       = ctypes.c_void_p (self.m_infopla)
        cflamy          = 0
        varcflamy       = ctypes.c_double (cflamy)
        self.m_model.m_eagme.BASME_INFOPLA_CFLAMY_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varcflamy))
        cflamy          = varcflamy.value
        return          cflamy

    @columnBucklingY.setter
    def columnBucklingY (self, cflamy):
        """
        Coeficiente de flambagem Y
        """
        varinfopla       = ctypes.c_void_p (self.m_infopla)
        varcflamy       = ctypes.c_double (cflamy)
        self.m_model.m_eagme.BASME_INFOPLA_CFLAMY_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varcflamy))

    @property
    def columnDoubleStoryX (self):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        itravadox       = 0
        varitravadox    = ctypes.c_int (itravadox)
        self.m_model.m_eagme.BASME_INFOPLA_ITRAVADOX_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varitravadox))
        itravadox       = varitravadox.value
        return          itravadox

    @columnDoubleStoryX.setter
    def columnDoubleStoryX (self, itravadox):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varitravadox    = ctypes.c_int (itravadox)
        self.m_model.m_eagme.BASME_INFOPLA_ITRAVADOX_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varitravadox))

    @property
    def columnDoubleStoryY (self):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        itravadoy       = 0
        varitravadoy    = ctypes.c_int (itravadoy)
        self.m_model.m_eagme.BASME_INFOPLA_ITRAVADOY_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varitravadoy))
        itravadoy       = varitravadoy.value
        return          itravadoy

    @columnDoubleStoryY.setter
    def columnDoubleStoryY (self, itravadoy):
        """
        Pé-direito duplo X (0) Geometria (1) Não (2) Sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varitravadoy    = ctypes.c_int (itravadoy)
        self.m_model.m_eagme.BASME_INFOPLA_ITRAVADOY_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varitravadoy))
    @property
    def columnConcreteFc (self):
        """
        Fck diferenciado de pilar (string)
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varfckpil       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_INFOPLA_FCKPIL_LER (ctypes.byref (varinfopla),
                            varfckpil)
        fckpil          = varfckpil.value.decode(TQSUtil.CHARSET)
        return          fckpil

    @columnConcreteFc.setter
    def columnConcreteFc (self, fckpil):
        """
        Fck diferenciado de pilar (string)
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varfckpil       = ctypes.c_char_p (fckpil.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_INFOPLA_FCKPIL_DEF (ctypes.byref (varinfopla),
                            varfckpil)
    @property
    def columnCover (self):
        """
        Cobrimento do pilar na planta, cm
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        cobrpil         = 0.
        varcobrpil      = ctypes.c_double (cobrpil)
        self.m_model.m_eagme.BASME_INFOPLA_COBRPIL_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varcobrpil))
        cobrpil        = varcobrpil.value
        return          cobrpil

    @columnCover.setter
    def columnCover (self, cobrpil):
        """
        Cobrimento do pilar na planta, cm
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varcobrpil      = ctypes.c_double (cobrpil)
        self.m_model.m_eagme.BASME_INFOPLA_COBRPIL_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varcobrpil))

    @property
    def columnExposure (self):
        """
        Pilar em contato com o solo (0) não (1) sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        icontsolo       = 0
        varicontsolo    = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_INFOPLA_ICONTSOLO_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varicontsolo))
        icontsolo       = varicontsolo.value
        return          icontsolo

    @columnExposure.setter
    def columnExposure (self, icontsolo):
        """
        Pilar em contato com o solo (0) não (1) sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varicontsolo = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_INFOPLA_ICONTSOLO_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varicontsolo))


    @property
    def columnHinges (self):
        """
        Pilar articulado em (0)CONTPOR.DAT (1)base/topo (2)base (3)topo
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        iarticbt        = 0
        variarticbt     = ctypes.c_int (iarticbt)
        self.m_model.m_eagme.BASME_INFOPLA_IARTICBT_LER (ctypes.byref (varinfopla),
                            ctypes.byref (variarticbt))
        iarticbt        = variarticbt.value
        return          iarticbt

    @columnHinges.setter
    def columnHinges (self, iarticbt):
        """
        Pilar articulado em (0)CONTPOR.DAT (1)base/topo (2)base (3)topo
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        variarticbt     = ctypes.c_int (iarticbt)
        self.m_model.m_eagme.BASME_INFOPLA_IARTICBT_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (variarticbt))

    @property
    def columnDynHorLoad (self):
        """
        Carga dinâmica de veiculo em pilar (0) não (1) sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        icargadinvuc    = 0
        varicargadinvuc = ctypes.c_int (icargadinvuc)
        self.m_model.m_eagme.BASME_INFOPLA_ICARGADINVUC_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varicargadinvuc))
        icargadinvuc    = varicargadinvuc.value
        return          icargadinvuc

    @columnDynHorLoad.setter
    def columnDynHorLoad (self, icargadinvuc):
        """
        Carga dinâmica de veiculo em pilar (0) não (1) sim
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        varicargadinvuc = ctypes.c_int (icargadinvuc)
        self.m_model.m_eagme.BASME_INFOPLA_ICARGADINVUC_DEF (ctypes.byref (varinfopla),
                            ctypes.byref (varicargadinvuc))

    @property
    def columnTransferBlock (self):
        """
        Dados de Bloco de transição
        """
        varinfopla      = ctypes.c_void_p (self.m_infopla)
        blocotrans      = None
        varblocotrans   = ctypes.c_void_p (blocotrans)
        self.m_model.m_eagme.BASME_INFOPLA_BLOCOTRANS_LER (ctypes.byref (varinfopla),
                            ctypes.byref (varblocotrans))
        blocotrans          = varblocotrans.value
        columntransferblock = ColumnTransferBlock (self.m_model, blocotrans)
        return          columntransferblock
        
#------------------------------------------------------------------------------
#       Dados de geometria de pilar - CGeoPil
#
class ColumnGeometry ():

    def __init__ (self, model, geopil):
        """
        Dados de geometria de pilar \n
            model       <- Objeto Model() do modelo atual\n
            geopil      <- Apontador para objeto CGeoPil
        """
        self.m_model    = model
        self.m_geopil   = geopil

    @property
    def sectionType (self):
        """
        Tipo de seção COLUMNTYPE_xxx
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        itpsec          = 0
        varitpsec       = ctypes.c_int (itpsec)
        self.m_model.m_eagme.BASME_GEOPIL_ITPSEC_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varitpsec))
        itpsec          = varitpsec.value
        return          itpsec

    @sectionType.setter
    def sectionType (self, itpsec):
        """
        Tipo de seção COLUMNTYPE_xxx
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varitpsec       = ctypes.c_int (itpsec)
        self.m_model.m_eagme.BASME_GEOPIL_ITPSEC_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varitpsec))
    @property
    def sectionB1 (self):
        """
        Dimensão B1 de seções R/L/U/C
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        b1              = 0
        varb1           = ctypes.c_double (b1)
        self.m_model.m_eagme.BASME_GEOPIL_B1_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varb1))
        b1              = varb1.value
        return          b1

    @sectionB1.setter
    def sectionB1 (self, b1):
        """
        Dimensão B1 de seções R/L/U/C
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varb1           = ctypes.c_double (b1)
        self.m_model.m_eagme.BASME_GEOPIL_B1_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varb1))
    @property
    def sectionH1 (self):
        """
        Dimensão H1 de seções R/L/U
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        h1              = 0
        varh1           = ctypes.c_double (h1)
        self.m_model.m_eagme.BASME_GEOPIL_H1_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varh1))
        h1              = varh1.value
        return          h1

    @sectionH1.setter
    def sectionH1 (self, h1):
        """
        Dimensão H1 de seções R/L/U
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varh1           = ctypes.c_double (h1)
        self.m_model.m_eagme.BASME_GEOPIL_H1_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varh1))
    @property
    def sectionB2 (self):
        """
        Dimensão B2 de seções L/U
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        b2              = 0
        varb2           = ctypes.c_double (b2)
        self.m_model.m_eagme.BASME_GEOPIL_B2_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varb2))
        b2              = varb2.value
        return          b2

    @sectionB2.setter
    def sectionB2 (self, b2):
        """
        Dimensão B2 de seções L/U
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varb2           = ctypes.c_double (b2)
        self.m_model.m_eagme.BASME_GEOPIL_B2_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varb2))

    @property
    def sectionH2 (self):
        """
        Dimensão H2 de seções L/U
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        h2              = 0
        varh2           = ctypes.c_double (h2)
        self.m_model.m_eagme.BASME_GEOPIL_H2_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varh2))
        h2              = varh2.value
        return          h2

    @sectionH2.setter
    def sectionH2 (self, h2):
        """
        Dimensão H2 de seções L/U
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varh2           = ctypes.c_double (h2)
        self.m_model.m_eagme.BASME_GEOPIL_H2_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varh2))

    @property
    def sectionAngle (self):
        """
        Ângulo de inserção da seção em graus
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        ang             = 0
        varang          = ctypes.c_double (ang)
        self.m_model.m_eagme.BASME_GEOPIL_ANG_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varang))
        ang             = varang.value
        return          ang

    @sectionAngle.setter
    def sectionAngle (self, ang):
        """
        Ângulo de inserção da seção em graus
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varang          = ctypes.c_double (ang)
        self.m_model.m_eagme.BASME_GEOPIL_ANG_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varang))

    @property
    def sectionMaterial (self):
        """
        Título do material diferente do concreto (não padrão)
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varmaternp      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOPIL_MATERNP_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varmaternp))
        maternp         = varmaternp.value.decode(TQSUtil.CHARSET)
        return          maternp

    @sectionMaterial.setter
    def sectionMaterial (self, maternp):
        """
        Título do material diferente do concreto (não padrão)
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varmaternp      = ctypes.c_char_p (maternp.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOPIL_MATERNP_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varmaternp))

    @property
    def sectionName (self):
        """
        Nome de seção não padrão - catalogada
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varsecaonp      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOPIL_SECAONP_LER (ctypes.byref (vargeopil),
                            ctypes.byref (varsecaonp))
        secaonp         = varsecaonp.value.decode(TQSUtil.CHARSET)
        return          secaonp

    @sectionName.setter
    def sectionName (self, secaonp):
        """
        Nome de seção não padrão - catalogada
        """
        vargeopil       = ctypes.c_void_p (self.m_geopil)
        varsecaonp      = ctypes.c_char_p (secaonp.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOPIL_SECAONP_DEF (ctypes.byref (vargeopil),
                            ctypes.byref (varsecaonp))

#------------------------------------------------------------------------------
#       Dados de inserção de pilar CInsPil
#
class ColumnInsertion ():

    def __init__ (self, model, inspil):
        """
        Dados de inserção de pilar\n
            model       <- Objeto Model() do modelo atual\n
            inspil      <- Apontador para objeto CInsPil
        """
        self.m_model    = model
        self.m_inspil   = inspil

    @property
    def insertionType (self):
        """
        Inserção de pilar por (0) Centro (1) Canto
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        ipilins         = 0
        varipilins      = ctypes.c_int (ipilins)
        self.m_model.m_eagme.BASME_INSPIL_IPILINS_LER (ctypes.byref (varinspil),
                            ctypes.byref (varipilins))
        ipilins          = varipilins.value
        return          ipilins

    @insertionType.setter
    def insertionType (self, ipilins):
        """
        Inserção de pilar por (0) Centro (1) Canto
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        varipilins      = ctypes.c_int (ipilins)
        self.m_model.m_eagme.BASME_INSPIL_IPILINS_DEF (ctypes.byref (varinspil),
                            ctypes.byref (varipilins))

    @property
    def insertionCorner (self):
        """
        Numero do canto (0..) para insertionType == 1
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        ipilcan         = 0
        varipilcan      = ctypes.c_int (ipilcan)
        self.m_model.m_eagme.BASME_INSPIL_IPILCAN_LER (ctypes.byref (varinspil),
                            ctypes.byref (varipilcan))
        ipilcan          = varipilcan.value
        return          ipilcan

    @insertionCorner.setter
    def insertionCorner (self, ipilcan):
        """
        Numero do canto (0..) para insertionType == 1
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        varipilcan      = ctypes.c_int (ipilcan)
        self.m_model.m_eagme.BASME_INSPIL_IPILCAN_DEF (ctypes.byref (varinspil),
                            ctypes.byref (varipilcan))

    @property
    def sectionCover (self):
        """
        Revestimento cm
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        revpil          = 0
        varrevpil       = ctypes.c_double (revpil)
        self.m_model.m_eagme.BASME_INSPIL_REVPIL_LER (ctypes.byref (varinspil),
                            ctypes.byref (varrevpil))
        revpil          = varrevpil.value
        return          revpil

    @sectionCover.setter
    def sectionCover (self, revpil):
        """
        Revestimento cm
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        varrevpil       = ctypes.c_double (revpil)
        self.m_model.m_eagme.BASME_INSPIL_REVPIL_DEF (ctypes.byref (varinspil),
                            ctypes.byref (varrevpil))

    @property
    def mediumPointInsertion (self):
        """
        Inserção por ponto intermediário (0) Não (1) Sim
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        intermed        = 0
        varintermed     = ctypes.c_int (intermed)
        self.m_model.m_eagme.BASME_INSPIL_INTERMED_LER (ctypes.byref (varinspil),
                            ctypes.byref (varintermed))
        intermed        = varintermed.value
        return          intermed

    @mediumPointInsertion.setter
    def mediumPointInsertion (self, intermed):
        """
        Inserção por ponto intermediário (0) Não (1) Sim
        """
        varinspil       = ctypes.c_void_p (self.m_inspil)
        varintermed     = ctypes.c_int (intermed)
        self.m_model.m_eagme.BASME_INSPIL_INTERMED_DEF (ctypes.byref (varinspil),
                            ctypes.byref (varintermed))


#------------------------------------------------------------------------------
#       Modos de visualização CModVis
#
class VisModes ():

    def __init__ (self, model, modvis):
        """
        Classe que define modos de visualização do Modelador\n
            model       <- Objeto Model() do modelo atual\n
            modvis      <- Apontador para objeto CModVis
        """
        self.m_model     = model
        self.m_modvis    = modvis

        self.columns     = VisModeColumns (model, self)
        self.beams       = VisModeBeams (model, self)
        self.slabs       = VisModeSlabs (model, self)
        self.details     = VisModeDetails (model, self)
        self.bim         = VisModeBim (model, self)
        self.loads       = VisModeLoads (model, self)
        self.foundations = VisModeFoundations (model, self)
        self.precast     = VisModePrecast (model, self)
#
#       Modos de visualização de pilares
#
class VisModeColumns ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de pilares\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def columns (self):
        """
        Pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilares         = 0
        varpilares      = ctypes.c_int (pilares)
        self.m_model.m_eagme.BASME_MODVIS_PILARES_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilares))
        pilares          = varpilares.value
        return          pilares

    @columns.setter
    def columns (self, pilares):
        """
        Pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilares       = ctypes.c_int (pilares)
        self.m_model.m_eagme.BASME_MODVIS_PILARES_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilares))

    @property
    def name (self):
        """
        Título de pilar (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        piltit          = 0
        varpiltit       = ctypes.c_int (piltit)
        self.m_model.m_eagme.BASME_MODVIS_PILTIT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpiltit))
        piltit          = varpiltit.value
        return          piltit

    @name.setter
    def name (self, piltit):
        """
        Título de pilar (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpiltit       = ctypes.c_int (piltit)
        self.m_model.m_eagme.BASME_MODVIS_PILTIT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpiltit))

    @property
    def dimensions (self):
        """
        Dimensões de pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pildim          = 0
        varpildim       = ctypes.c_int (pildim)
        self.m_model.m_eagme.BASME_MODVIS_PILDIM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpildim))
        pildim          = varpildim.value
        return          pildim

    @dimensions.setter
    def dimensions (self, pildim):
        """
        Dimensões de pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpildim       = ctypes.c_int (pildim)
        self.m_model.m_eagme.BASME_MODVIS_PILDIM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpildim))
    @property
    def overlapUpper (self):
        """
        Sobreposição de pilar atual e superior (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilsobre        = 0
        varpilsobre     = ctypes.c_int (pilsobre)
        self.m_model.m_eagme.BASME_MODVIS_PILSOBRE_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilsobre))
        pilsobre        = varpilsobre.value
        return          pilsobre

    @overlapUpper.setter
    def overlapUpper (self, pilsobre):
        """
        Sobreposição de pilar atual e superior (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilsobre     = ctypes.c_int (pilsobre)
        self.m_model.m_eagme.BASME_MODVIS_PILSOBRE_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilsobre))
    @property
    def overlapBottom (self):
        """
        Sobreposição de pilar atual e inferior(0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilsobreinf     = 0
        varpilsobreinf  = ctypes.c_int (pilsobreinf)
        self.m_model.m_eagme.BASME_MODVIS_PILSOBREINF_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilsobreinf))
        pilsobreinf     = varpilsobreinf.value
        return          pilsobreinf

    @overlapBottom.setter
    def overlapBottom (self, pilsobreinf):
        """
        Sobreposição de pilar atual e inferior(0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilsobreinf  = ctypes.c_int (pilsobreinf)
        self.m_model.m_eagme.BASME_MODVIS_PILSOBREINF_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilsobreinf))

    @property
    def gridSupport (self):
        """
        Condições de apoio em grelha (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilgre          = 0
        varpilgre       = ctypes.c_int (pilgre)
        self.m_model.m_eagme.BASME_MODVIS_PILGRE_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilgre))
        pilgre          = varpilgre.value
        return          pilgre

    @gridSupport.setter
    def gridSupport (self, pilgre):
        """
        Condições de apoio em grelha (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilgre       = ctypes.c_int (pilgre)
        self.m_model.m_eagme.BASME_MODVIS_PILGRE_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilgre))

    @property
    def axes (self):
        """
        Eixos de pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pileix          = 0
        varpileix       = ctypes.c_int (pileix)
        self.m_model.m_eagme.BASME_MODVIS_PILEIX_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpileix))
        pileix          = varpileix.value
        return          pileix

    @axes.setter
    def axes (self, pileix):
        """
        Eixos de pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpileix       = ctypes.c_int (pileix)
        self.m_model.m_eagme.BASME_MODVIS_PILEIX_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpileix))
        
    @property
    def details (self):
        """
        Outros dados de detalhamento de pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pildad          = 0
        varpildad       = ctypes.c_int (pildad)
        self.m_model.m_eagme.BASME_MODVIS_PILDAD_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpildad))
        pildad          = varpildad.value
        return          pildad

    @details.setter
    def details (self, pildad):
        """
        Outros dados de detalhamento de pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpildad       = ctypes.c_int (pildad)
        self.m_model.m_eagme.BASME_MODVIS_PILDAD_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpildad))
        
    @property
    def circle (self):
        """
        Pilares circulares como círculos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        idiscretcirc    = 0
        varidiscretcirc = ctypes.c_int (idiscretcirc)
        self.m_model.m_eagme.BASME_MODVIS_IDISCRETCIRC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varidiscretcirc))
        idiscretcirc    = varidiscretcirc.value
        return          idiscretcirc

    @circle.setter
    def circle (self, idiscretcirc):
        """
        Pilares circulares como círculos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varidiscretcirc = ctypes.c_int (idiscretcirc)
        self.m_model.m_eagme.BASME_MODVIS_IDISCRETCIRC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varidiscretcirc))
        
    @property
    def shearStrip (self):
        """
        Mostra lâmina de pilares parede (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pillamina       = 0
        varpillamina    = ctypes.c_int (pillamina)
        self.m_model.m_eagme.BASME_MODVIS_PILLAMINA_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpillamina))
        pillamina       = varpillamina.value
        return          pillamina

    @shearStrip.setter
    def shearStrip (self, pillamina):
        """
        Mostra lâmina de pilares parede (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpillamina    = ctypes.c_int (pillamina)
        self.m_model.m_eagme.BASME_MODVIS_PILLAMINA_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpillamina))

    @property
    def shearWallDiscret (self):
        """
        Discretização de pilar parede (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pildiscret      = 0
        varpildiscret   = ctypes.c_int (pildiscret)
        self.m_model.m_eagme.BASME_MODVIS_PILDISCRET_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpildiscret))
        pildiscret      = varpildiscret.value
        return          pildiscret

    @shearWallDiscret.setter
    def shearWallDiscret (self, pildiscret):
        """
        Discretização de pilar parede (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpildiscret   = ctypes.c_int (pildiscret)
        self.m_model.m_eagme.BASME_MODVIS_PILDISCRET_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpildiscret))

    @property
    def fixedPoint (self):
        """
        Ponto fixo do pilar (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilptfixo       = 0
        varpilptfixo    = ctypes.c_int (pilptfixo)
        self.m_model.m_eagme.BASME_MODVIS_PILPTFIXO_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilptfixo))
        pilptfixo       = varpilptfixo.value
        return          pilptfixo

    @fixedPoint.setter
    def fixedPoint (self, pilptfixo):
        """
        Ponto fixo do pilar (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilptfixo    = ctypes.c_int (pilptfixo)
        self.m_model.m_eagme.BASME_MODVIS_PILPTFIXO_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilptfixo))

    @property
    def imposedRestraint (self):
        """
        Travamento imposto (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        piltrav         = 0
        varpiltrav      = ctypes.c_int (piltrav)
        self.m_model.m_eagme.BASME_MODVIS_PILTRAV_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpiltrav))
        piltrav         = varpiltrav.value
        return          piltrav

    @imposedRestraint.setter
    def imposedRestraint (self, piltrav):
        """
        Travamento imposto (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpiltrav      = ctypes.c_int (piltrav)
        self.m_model.m_eagme.BASME_MODVIS_PILTRAV_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpiltrav))
        
    @property
    def ficticiousSupport (self):
        """
        Apoios fictícios (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilificticio     = 0
        varpilificticio  = ctypes.c_int (pilificticio)
        self.m_model.m_eagme.BASME_MODVIS_PILIFICTICIO_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilificticio))
        pilificticio     = varpilificticio.value
        return          pilificticio

    @ficticiousSupport.setter
    def ficticiousSupport (self, pilificticio):
        """
        Apoios fictícios (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilificticio  = ctypes.c_int (pilificticio)
        self.m_model.m_eagme.BASME_MODVIS_PILIFICTICIO_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilificticio))
        
    @property
    def horizontalOpenings (self):
        """
        Furos em pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilfur          = 0
        varpilfur       = ctypes.c_int (pilfur)
        self.m_model.m_eagme.BASME_MODVIS_PILFUR_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilfur))
        pilfur          = varpilfur.value
        return          pilfur

    @horizontalOpenings.setter
    def horizontalOpenings (self, pilfur):
        """
        Furos em pilares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilfur       = ctypes.c_int (pilfur)
        self.m_model.m_eagme.BASME_MODVIS_PILFUR_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilfur))

    @property
    def metalCheck (self):
        """
        Resultados de pilares no MetalCheck (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        pilmetalcheck   = 0
        varpilmetalcheck= ctypes.c_int (pilmetalcheck)
        self.m_model.m_eagme.BASME_MODVIS_PILMETALCHECK_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varpilmetalcheck))
        pilmetalcheck   = varpilmetalcheck.value
        return          pilmetalcheck

    @metalCheck.setter
    def metalCheck (self, pilmetalcheck):
        """
        Resultados de pilares no MetalCheck (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varpilmetalcheck= ctypes.c_int (pilmetalcheck)
        self.m_model.m_eagme.BASME_MODVIS_PILMETALCHECK_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varpilmetalcheck))
        
#
#       Modos de visualização de vigas
#
class VisModeBeams ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de vigas\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def beams (self):
        """
        Vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigas           = 0
        varvigas        = ctypes.c_int (vigas)
        self.m_model.m_eagme.BASME_MODVIS_VIGAS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigas))
        vigas           = varvigas.value
        return          vigas

    @beams.setter
    def beams (self, vigas):
        """
        Vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigas        = ctypes.c_int (vigas)
        self.m_model.m_eagme.BASME_MODVIS_VIGAS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigas))

    @property
    def name (self):
        """
        Título de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigtit          = 0
        varvigtit       = ctypes.c_int (vigtit)
        self.m_model.m_eagme.BASME_MODVIS_VIGTIT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigtit))
        vigtit          = varvigtit.value
        return          vigtit

    @name.setter
    def name (self, vigtit):
        """
        Título de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigtit       = ctypes.c_int (vigtit)
        self.m_model.m_eagme.BASME_MODVIS_VIGTIT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigtit))

    @property
    def dimensions (self):
        """
        Título de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigdim          = 0
        varvigdim       = ctypes.c_int (vigdim)
        self.m_model.m_eagme.BASME_MODVIS_VIGDIM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigdim))
        vigdim          = varvigdim.value
        return          vigdim

    @dimensions.setter
    def dimensions (self, vigdim):
        """
        Título de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigdim       = ctypes.c_int (vigdim)
        self.m_model.m_eagme.BASME_MODVIS_VIGDIM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigdim))


    @property
    def axes (self):
        """
        Eixos de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigeix          = 0
        varvigeix       = ctypes.c_int (vigeix)
        self.m_model.m_eagme.BASME_MODVIS_VIGEIX_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigeix))
        vigeix          = varvigeix.value
        return          vigeix

    @axes.setter
    def axes (self, vigeix):
        """
        Eixos de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigeix       = ctypes.c_int (vigeix)
        self.m_model.m_eagme.BASME_MODVIS_VIGEIX_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigeix))

    @property
    def connections (self):
        """
        Vinculações de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigvinc         = 0
        varvigvinc      = ctypes.c_int (vigvinc)
        self.m_model.m_eagme.BASME_MODVIS_VIGVINC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigvinc))
        vigvinc         = varvigvinc.value
        return          vigvinc

    @connections.setter
    def connections (self, vigvinc):
        """
        Vinculações de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigvinc      = ctypes.c_int (vigvinc)
        self.m_model.m_eagme.BASME_MODVIS_VIGVINC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigvinc))

    @property
    def nodes (self):
        """
        Nós de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vignos          = 0
        varvignos       = ctypes.c_int (vignos)
        self.m_model.m_eagme.BASME_MODVIS_VIGNOS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvignos))
        vignos          = varvignos.value
        return          vignos

    @nodes.setter
    def nodes (self, vignos):
        """
        Nós de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvignos       = ctypes.c_int (vignos)
        self.m_model.m_eagme.BASME_MODVIS_VIGNOS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvignos))

    @property
    def details (self):
        """
        Outros dados de detalhamento de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigdad          = 0
        varvigdad       = ctypes.c_int (vigdad)
        self.m_model.m_eagme.BASME_MODVIS_VIGDAD_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigdad))
        vigdad          = varvigdad.value
        return          vigdad

    @details.setter
    def details (self, vigdad):
        """
        Outros dados de detalhamento de vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigdad       = ctypes.c_int (vigdad)
        self.m_model.m_eagme.BASME_MODVIS_VIGDAD_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigdad))

    @property
    def sectionT (self):
        """
        Seção T e B colaborante (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigsect         = 0
        varvigsect      = ctypes.c_int (vigsect)
        self.m_model.m_eagme.BASME_MODVIS_VIGSECT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigsect))
        vigsect         = varvigsect.value
        return          vigsect

    @sectionT.setter
    def sectionT (self, vigsect):
        """
        Seção T e B colaborante (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigsect      = ctypes.c_int (vigsect)
        self.m_model.m_eagme.BASME_MODVIS_VIGSECT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigsect))

    @property
    def cantilever (self):
        """
        Pintar vigas em balanço (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigbal          = 0
        varvigbal       = ctypes.c_int (vigbal)
        self.m_model.m_eagme.BASME_MODVIS_VIGBAL_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigbal))
        vigbal          = varvigbal.value
        return          vigbal

    @cantilever.setter
    def cantilever (self, vigbal):
        """
        Pintar vigas em balanço (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigbal       = ctypes.c_int (vigbal)
        self.m_model.m_eagme.BASME_MODVIS_VIGBAL_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigbal))

    @property
    def openings (self):
        """
        Furos horizontais (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigfur          = 0
        varvigfur       = ctypes.c_int (vigfur)
        self.m_model.m_eagme.BASME_MODVIS_VIGFUR_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigfur))
        vigfur          = varvigfur.value
        return          vigfur

    @openings.setter
    def openings (self, vigfur):
        """
        Furos horizontais (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigfur       = ctypes.c_int (vigfur)
        self.m_model.m_eagme.BASME_MODVIS_VIGFUR_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigfur))

    @property
    def transferBeam (self):
        """
        Viga de transição (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigtrans        = 0
        varvigtrans     = ctypes.c_int (vigtrans)
        self.m_model.m_eagme.BASME_MODVIS_VIGTRANS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigtrans))
        vigtrans        = varvigtrans.value
        return          vigtrans

    @transferBeam.setter
    def transferBeam (self, vigtrans):
        """
        Viga de transição (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigtrans     = ctypes.c_int (vigtrans)
        self.m_model.m_eagme.BASME_MODVIS_VIGTRANS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigtrans))
        
    @property
    def metalCheck (self):
        """
        Vigas no MetalCheck (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigmetalcheck   = 0
        varvigmetalcheck= ctypes.c_int (vigmetalcheck)
        self.m_model.m_eagme.BASME_MODVIS_VIGMETALCHECK_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigmetalcheck))
        vigmetalcheck   = varvigmetalcheck.value
        return          vigmetalcheck

    @metalCheck.setter
    def metalCheck (self, vigmetalcheck):
        """
        Vigas no MetalCheck (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigmetalcheck= ctypes.c_int (vigmetalcheck)
        self.m_model.m_eagme.BASME_MODVIS_VIGMETALCHECK_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigmetalcheck))
        
    @property
    def precast (self):
        """
        Pintar vigas protendidas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vigprotend        = 0
        varvigprotend     = ctypes.c_int (vigprotend)
        self.m_model.m_eagme.BASME_MODVIS_VIGPROTEND_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varvigprotend))
        vigprotend        = varvigprotend.value
        return          vigprotend

    @precast.setter
    def precast (self, vigprotend):
        """
        Pintar vigas protendidas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varvigprotend     = ctypes.c_int (vigprotend)
        self.m_model.m_eagme.BASME_MODVIS_VIGPROTEND_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varvigprotend))
        
#
#       Modos de visualização de lajes
#
class VisModeSlabs ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de lajes\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def slabs (self):
        """
        Lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajes           = 0
        varlajes        = ctypes.c_int (lajes)
        self.m_model.m_eagme.BASME_MODVIS_LAJES_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajes))
        lajes           = varlajes.value
        return          lajes

    @slabs.setter
    def slabs (self, lajes):
        """
        Lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajes        = ctypes.c_int (lajes)
        self.m_model.m_eagme.BASME_MODVIS_LAJES_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajes))

    @property
    def name (self):
        """
        Título de lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajtit          = 0
        varlajtit       = ctypes.c_int (lajtit)
        self.m_model.m_eagme.BASME_MODVIS_LAJTIT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajtit))
        lajtit          = varlajtit.value
        return          lajtit

    @name.setter
    def name (self, lajtit):
        """
        Título de lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajtit       = ctypes.c_int (lajtit)
        self.m_model.m_eagme.BASME_MODVIS_LAJTIT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajtit))

    @property
    def dimensions (self):
        """
        Dimensões de lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajdim          = 0
        varlajdim       = ctypes.c_int (lajdim)
        self.m_model.m_eagme.BASME_MODVIS_LAJDIM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajdim))
        lajdim          = varlajdim.value
        return          lajdim

    @dimensions.setter
    def dimensions (self, lajdim):
        """
        Dimensões de lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajdim       = ctypes.c_int (lajdim)
        self.m_model.m_eagme.BASME_MODVIS_LAJDIM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajdim))

    @property
    def mainDirection (self):
        """
        Símbolo de ângulo principal da laje (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajang          = 0
        varlajang       = ctypes.c_int (lajang)
        self.m_model.m_eagme.BASME_MODVIS_LAJANG_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajang))
        lajang          = varlajang.value
        return          lajang

    @mainDirection.setter
    def mainDirection (self, lajang):
        """
        Símbolo de ângulo principal da laje (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajang       = ctypes.c_int (lajang)
        self.m_model.m_eagme.BASME_MODVIS_LAJANG_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajang))

    @property
    def contour (self):
        """
        Contorno da laje (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajcont         = 0
        varlajcont      = ctypes.c_int (lajcont)
        self.m_model.m_eagme.BASME_MODVIS_LAJCONT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajcont))
        lajcont         = varlajcont.value
        return          lajcont

    @contour.setter
    def contour (self, lajcont):
        """
        Contorno da laje (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajcont      = ctypes.c_int (lajcont)
        self.m_model.m_eagme.BASME_MODVIS_LAJCONT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajcont))

    @property
    def details (self):
        """
        Outros dados de detalhamento de lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajdad          = 0
        varlajdad       = ctypes.c_int (lajdad)
        self.m_model.m_eagme.BASME_MODVIS_LAJDAD_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajdad))
        lajdad          = varlajdad.value
        return          lajdad

    @details.setter
    def details (self, lajdad):
        """
        Outros dados de detalhamento de lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajdad       = ctypes.c_int (lajdad)
        self.m_model.m_eagme.BASME_MODVIS_LAJDAD_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajdad))

    @property
    def ribs (self):
        """
        Nervuras em lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajner          = 0
        varlajner       = ctypes.c_int (lajner)
        self.m_model.m_eagme.BASME_MODVIS_LAJNER_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajner))
        lajner          = varlajner.value
        return          lajner

    @ribs.setter
    def ribs (self, lajner):
        """
        Nervuras em lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajner       = ctypes.c_int (lajner)
        self.m_model.m_eagme.BASME_MODVIS_LAJNER_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajner))

    @property
    def openings (self):
        """
        Furos em lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajfuros        = 0
        varlajfuros     = ctypes.c_int (lajfuros)
        self.m_model.m_eagme.BASME_MODVIS_LAJFUROS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajfuros))
        lajfuros        = varlajfuros.value
        return          lajfuros

    @openings.setter
    def openings (self, lajfuros):
        """
        Furos em lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajfuros     = ctypes.c_int (lajfuros)
        self.m_model.m_eagme.BASME_MODVIS_LAJFUROS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajfuros))

    @property
    def caps (self):
        """
        Capitéis (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajcapit        = 0
        varlajcapit     = ctypes.c_int (lajcapit)
        self.m_model.m_eagme.BASME_MODVIS_LAJCAPIT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajcapit))
        lajcapit        = varlajcapit.value
        return          lajcapit

    @caps.setter
    def caps (self, lajcapit):
        """
        Capitéis (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajcapit     = ctypes.c_int (lajcapit)
        self.m_model.m_eagme.BASME_MODVIS_LAJCAPIT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajcapit))

    @property
    def trapezoidalRibs (self):
        """
        Bordas de nervuras trapezoidais (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajborner       = 0
        varlajborner    = ctypes.c_int (lajborner)
        self.m_model.m_eagme.BASME_MODVIS_LAJBORNER_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajborner))
        lajborner       = varlajborner.value
        return          lajborner

    @trapezoidalRibs.setter
    def trapezoidalRibs (self, lajborner):
        """
        Bordas de nervuras trapezoidais (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajborner    = ctypes.c_int (lajborner)
        self.m_model.m_eagme.BASME_MODVIS_LAJBORNER_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajborner))

    @property
    def ficticiusRibs (self):
        """
        Nervuras em maciços (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajnermac       = 0
        varlajnermac    = ctypes.c_int (lajnermac)
        self.m_model.m_eagme.BASME_MODVIS_LAJNERMAC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajnermac))
        lajnermac       = varlajnermac.value
        return          lajnermac

    @ficticiusRibs.setter
    def ficticiusRibs (self, lajnermac):
        """
        Nervuras em maciços (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajnermac    = ctypes.c_int (lajnermac)
        self.m_model.m_eagme.BASME_MODVIS_LAJNERMAC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajnermac))

    @property
    def prefabDir (self):
        """
        Direção de nervuras (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajdirner       = 0
        varlajdirner    = ctypes.c_int (lajdirner)
        self.m_model.m_eagme.BASME_MODVIS_LAJDIRNER_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajdirner))
        lajdirner       = varlajdirner.value
        return          lajdirner

    @prefabDir.setter
    def prefabDir (self, lajdirner):
        """
        Direção de nervuras (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajdirner    = ctypes.c_int (lajdirner)
        self.m_model.m_eagme.BASME_MODVIS_LAJDIRNER_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajdirner))

    @property
    def cantilever (self):
        """
        Laje em balanço (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        lajbalan       = 0
        varlajbalan    = ctypes.c_int (lajbalan)
        self.m_model.m_eagme.BASME_MODVIS_LAJBALAN_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlajbalan))
        lajbalan       = varlajbalan.value
        return          lajbalan

    @cantilever.setter
    def cantilever (self, lajbalan):
        """
        Laje em balanço (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlajbalan    = ctypes.c_int (lajbalan)
        self.m_model.m_eagme.BASME_MODVIS_LAJBALAN_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlajbalan))

#
#       Modos de visualização de detalhamento (outros dados)
#
class VisModeDetails ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de detalhamento\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def crossSections (self):
        """
        Cortes da planta de formas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        cortes          = 0
        varcortes       = ctypes.c_int (cortes)
        self.m_model.m_eagme.BASME_MODVIS_CORTES_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcortes))
        cortes          = varcortes.value
        return          cortes

    @crossSections.setter
    def crossSections (self, cortes):
        """
        Cortes da planta de formas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcortes       = ctypes.c_int (cortes)
        self.m_model.m_eagme.BASME_MODVIS_CORTES_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcortes))

    @property
    def dimensions (self):
        """
        Cotas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        cotas          = 0
        varcotas       = ctypes.c_int (cotas)
        self.m_model.m_eagme.BASME_MODVIS_COTAS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcotas))
        cotas          = varcotas.value
        return          cotas

    @dimensions.setter
    def dimensions (self, cotas):
        """
        Cotas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcotas       = ctypes.c_int (cotas)
        self.m_model.m_eagme.BASME_MODVIS_COTAS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcotas))

    @property
    def controlPoints (self):
        """
        Pontos de controle de cotagem (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        cotascontrole   = 0
        varcotascontrole= ctypes.c_int (cotascontrole)
        self.m_model.m_eagme.BASME_MODVIS_COTASCONTROLE_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcotascontrole))
        cotascontrole   = varcotascontrole.value
        return          cotascontrole

    @controlPoints.setter
    def controlPoints (self, cotascontrole):
        """
        Pontos de controle de cotagem (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcotascontrole= ctypes.c_int (cotascontrole)
        self.m_model.m_eagme.BASME_MODVIS_COTASCONTROLE_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcotascontrole))
    @property
    def formworkArea (self):
        """
        Áreas de vigas, pilares, lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iareas          = 0
        variareas       = ctypes.c_int (iareas)
        self.m_model.m_eagme.BASME_MODVIS_IAREAS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variareas))
        iareas          = variareas.value
        return          iareas

    @formworkArea.setter
    def formworkArea (self, iareas):
        """
        Áreas de vigas, pilares, lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variareas       = ctypes.c_int (iareas)
        self.m_model.m_eagme.BASME_MODVIS_IAREAS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variareas))

    @property
    def axes (self):
        """
        Eixos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        eixos           = 0
        vareixos        = ctypes.c_int (eixos)
        self.m_model.m_eagme.BASME_MODVIS_EIXOS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (vareixos))
        eixos           = vareixos.value
        return          eixos

    @axes.setter
    def axes (self, eixos):
        """
        Eixos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vareixos        = ctypes.c_int (eixos)
        self.m_model.m_eagme.BASME_MODVIS_EIXOS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (vareixos))

    @property
    def centroidsTable (self):
        """
        Tabela de baricentros (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        baricentros     = 0
        varbaricentros  = ctypes.c_int (baricentros)
        self.m_model.m_eagme.BASME_MODVIS_BARICENTROS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varbaricentros))
        baricentros     = varbaricentros.value
        return          baricentros

    @centroidsTable.setter
    def centroidsTable (self, baricentros):
        """
        Tabela de baricentros (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varbaricentros  = ctypes.c_int (baricentros)
        self.m_model.m_eagme.BASME_MODVIS_BARICENTROS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varbaricentros))

    @property
    def overlapAuxFloors (self):
        """
        Sobrepõe pisos auxiliares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        mixpisosaux     = 0
        varmixpisosaux  = ctypes.c_int (mixpisosaux)
        self.m_model.m_eagme.BASME_MODVIS_MIXPISOSAUX_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varmixpisosaux))
        mixpisosaux     = varmixpisosaux.value
        return          mixpisosaux

    @overlapAuxFloors.setter
    def overlapAuxFloors (self, mixpisosaux):
        """
        Sobrepõe pisos auxiliares (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varmixpisosaux  = ctypes.c_int (mixpisosaux)
        self.m_model.m_eagme.BASME_MODVIS_MIXPISOSAUX_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varmixpisosaux))

    @property
    def elementsTable (self):
        """
        Tabela de elementos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        tabelem         = 0
        vartabelem      = ctypes.c_int (tabelem)
        self.m_model.m_eagme.BASME_MODVIS_TABELEM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (vartabelem))
        tabelem         = vartabelem.value
        return          tabelem

    @elementsTable.setter
    def elementsTable (self, tabelem):
        """
        Tabela de elementos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        vartabelem      = ctypes.c_int (tabelem)
        self.m_model.m_eagme.BASME_MODVIS_TABELEM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (vartabelem))

    @property
    def tunnelReference (self):
        """
        Centro de torção - referência de túnel de vento (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        icentor         = 0
        varicentor      = ctypes.c_int (icentor)
        self.m_model.m_eagme.BASME_MODVIS_ICENTOR_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varicentor))
        icentor         = varicentor.value
        return          icentor

    @tunnelReference.setter
    def tunnelReference (self, icentor):
        """
        Centro de torção - referência de túnel de vento (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varicentor      = ctypes.c_int (icentor)
        self.m_model.m_eagme.BASME_MODVIS_ICENTOR_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varicentor))

    @property
    def linesOutOfXY (self):
        """
        Linhas fora da direção X/Y global (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        linhasincl      = 0
        varlinhasincl   = ctypes.c_int (linhasincl)
        self.m_model.m_eagme.BASME_MODVIS_LINHASINCL_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varlinhasincl))
        linhasincl      = varlinhasincl.value
        return          linhasincl

    @linesOutOfXY.setter
    def linesOutOfXY (self, linhasincl):
        """
        Linhas fora da direção X/Y global (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varlinhasincl   = ctypes.c_int (linhasincl)
        self.m_model.m_eagme.BASME_MODVIS_LINHASINCL_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varlinhasincl))

    @property
    def disablePlotingHatches (self):
        """
        Inibe display de hachuras plotadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        inibdisplayhachur= 0
        varinibdisplayhachur = ctypes.c_int (inibdisplayhachur)
        self.m_model.m_eagme.BASME_MODVIS_INIBDISPLAYHACHUR_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varinibdisplayhachur))
        inibdisplayhachur= varinibdisplayhachur.value
        return          inibdisplayhachur

    @disablePlotingHatches.setter
    def disablePlotingHatches (self, inibdisplayhachur):
        """
        Inibe display de hachuras plotadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varinibdisplayhachur = ctypes.c_int (inibdisplayhachur)
        self.m_model.m_eagme.BASME_MODVIS_INIBDISPLAYHACHUR_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varinibdisplayhachur))

    @property
    def hatchedUnevenness (self):
        """
        Legenda e hachura de desníveis (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ilegdesniv      = 0
        varilegdesniv   = ctypes.c_int (ilegdesniv)
        self.m_model.m_eagme.BASME_MODVIS_ILEGDESNIV_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varilegdesniv))
        ilegdesniv      = varilegdesniv.value
        return          ilegdesniv

    @hatchedUnevenness.setter
    def hatchedUnevenness (self, ilegdesniv):
        """
        Legenda e hachura de desníveis (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varilegdesniv   = ctypes.c_int (ilegdesniv)
        self.m_model.m_eagme.BASME_MODVIS_ILEGDESNIV_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varilegdesniv))

    @property
    def floorLevels (self):
        """
        Cota pavimentos em desnível (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        isimdesniv      = 0
        varisimdesniv   = ctypes.c_int (isimdesniv)
        self.m_model.m_eagme.BASME_MODVIS_ISIMDESNIV_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varisimdesniv))
        isimdesniv      = varisimdesniv.value
        return          isimdesniv

    @floorLevels.setter
    def floorLevels (self, isimdesniv):
        """
        Cota pavimentos em desnível (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varisimdesniv   = ctypes.c_int (isimdesniv)
        self.m_model.m_eagme.BASME_MODVIS_ISIMDESNIV_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varisimdesniv))

    @property
    def floorLevelsTable (self):
        """
        Tabela de nível dos pavimentos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        itabnivpav      = 0
        varitabnivpav   = ctypes.c_int (itabnivpav)
        self.m_model.m_eagme.BASME_MODVIS_ITABNIVPAV_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varitabnivpav))
        itabnivpav      = varitabnivpav.value
        return          itabnivpav

    @floorLevelsTable.setter
    def floorLevelsTable (self, itabnivpav):
        """
        Tabela de nível dos pavimentos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varitabnivpav   = ctypes.c_int (itabnivpav)
        self.m_model.m_eagme.BASME_MODVIS_ITABNIVPAV_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varitabnivpav))

    @property
    def towerFence (self):
        """
        Cerca da torre (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        icercator       = 0
        varicercator    = ctypes.c_int (icercator)
        self.m_model.m_eagme.BASME_MODVIS_ICERCATOR_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varicercator))
        icercator       = varicercator.value
        return          icercator

    @towerFence.setter
    def towerFence (self, icercator):
        """
        Cerca da torre (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varicercator    = ctypes.c_int (icercator)
        self.m_model.m_eagme.BASME_MODVIS_ICERCATOR_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varicercator))

#
#       Modos de visualização de BIM
#
class VisModeBim ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de BIM\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def importStatus (self):
        """
        Status de importação do BIM (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        importstatus    = 0
        varimportstatus = ctypes.c_int (importstatus)
        self.m_model.m_eagme.BASME_MODVIS_IMPORTSTATUS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varimportstatus))
        importstatus    = varimportstatus.value
        return          importstatus

    @importStatus.setter
    def importStatus (self, importstatus):
        """
        Status de importação do BIM (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varimportstatus = ctypes.c_int (importstatus)
        self.m_model.m_eagme.BASME_MODVIS_IMPORTSTATUS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varimportstatus))

    @property
    def notExported (self):
        """
        Elementos não exportados para o BIM (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        inaoexport      = 0
        varinaoexport   = ctypes.c_int (inaoexport)
        self.m_model.m_eagme.BASME_MODVIS_INAOEXPORT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varinaoexport))
        inaoexport      = varinaoexport.value
        return          inaoexport

    @notExported.setter
    def notExported (self, inaoexport):
        """
        Elementos não exportados para o BIM (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varinaoexport   = ctypes.c_int (inaoexport)
        self.m_model.m_eagme.BASME_MODVIS_INAOEXPORT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varinaoexport))

    @property
    def importedPipes (self):
        """
        Tubos importados (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        itubos          = 0
        varitubos       = ctypes.c_int (itubos)
        self.m_model.m_eagme.BASME_MODVIS_ITUBOS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varitubos))
        itubos          = varitubos.value
        return          itubos

    @importedPipes.setter
    def importedPipes (self, itubos):
        """
        Tubos importados (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varitubos       = ctypes.c_int (itubos)
        self.m_model.m_eagme.BASME_MODVIS_ITUBOS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varitubos))

    @property
    def pipeView (self):
        """
        Visualizar tubos (0) Só na vista 3D (1) Na vista 3D e 2D
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        itubosvis       = 0
        varitubosvis    = ctypes.c_int (itubosvis)
        self.m_model.m_eagme.BASME_MODVIS_ITUBOSVIS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varitubosvis))
        itubosvis       = varitubosvis.value
        return          itubosvis

    @pipeView.setter
    def pipeView (self, itubosvis):
        """
        Visualizar tubos (0) Só na vista 3D (1) Na vista 3D e 2D
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varitubosvis    = ctypes.c_int (itubosvis)
        self.m_model.m_eagme.BASME_MODVIS_ITUBOSVIS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varitubosvis))

    @property
    def importedWalls (self):
        """
        Paredes importadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ipared3d        = 0
        varipared3d     = ctypes.c_int (ipared3d)
        self.m_model.m_eagme.BASME_MODVIS_IPARED3D_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varipared3d))
        ipared3d        = varipared3d.value
        return          ipared3d

    @importedWalls.setter
    def importedWalls (self, ipared3d):
        """
        Paredes importadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varipared3d     = ctypes.c_int (ipared3d)
        self.m_model.m_eagme.BASME_MODVIS_IPARED3D_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varipared3d))

    @property
    def objects3D (self):
        """
        Objetos 3D (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ielm3d          = 0
        varielm3d       = ctypes.c_int (ielm3d)
        self.m_model.m_eagme.BASME_MODVIS_IELM3D_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varielm3d))
        ielm3d          = varielm3d.value
        return          ielm3d

    @objects3D.setter
    def objects3D (self, ielm3d):
        """
        Objetos 3D (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varielm3d       = ctypes.c_int (ielm3d)
        self.m_model.m_eagme.BASME_MODVIS_IELM3D_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varielm3d))

    @property
    def plan2D (self):
        """
        Planta 2D como referência para o 3D (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ipla2d3d        = 0
        varipla2d3d     = ctypes.c_int (ipla2d3d)
        self.m_model.m_eagme.BASME_MODVIS_IPLA2D3D_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varipla2d3d))
        ipla2d3d        = varipla2d3d.value
        return          ipla2d3d

    @plan2D.setter
    def plan2D (self, ipla2d3d):
        """
        Planta 2D como referência para o 3D (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varipla2d3d     = ctypes.c_int (ipla2d3d)
        self.m_model.m_eagme.BASME_MODVIS_IPLA2D3D_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varipla2d3d))

    @property
    def reference3D (self):
        """
        Referência externa 3D (0) Abaixo (1) Acima (2) Ambos
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ivisrefext3d    = 0
        varivisrefext3d = ctypes.c_int (ivisrefext3d)
        self.m_model.m_eagme.BASME_MODVIS_IVISREFEXT3D_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varivisrefext3d))
        ivisrefext3d    = varivisrefext3d.value
        return          ivisrefext3d

    @reference3D.setter
    def reference3D (self, ivisrefext3d):
        """
        Referência externa 3D (0) Abaixo (1) Acima (2) Ambos
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varivisrefext3d = ctypes.c_int (ivisrefext3d)
        self.m_model.m_eagme.BASME_MODVIS_IVISREFEXT3D_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varivisrefext3d))

    @property
    def basePoint (self):
        """
        Ponto base de projeto (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iptbas          = 0
        variptbas       = ctypes.c_int (iptbas)
        self.m_model.m_eagme.BASME_MODVIS_IPTBAS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variptbas))
        iptbas          = variptbas.value
        return          iptbas

    @basePoint.setter
    def basePoint (self, iptbas):
        """
        Ponto base de projeto (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variptbas       = ctypes.c_int (iptbas)
        self.m_model.m_eagme.BASME_MODVIS_IPTBAS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variptbas))

    @property
    def surveyPoint (self):
        """
        Ponto de levantamento topográfico (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iptlvt          = 0
        variptlvt       = ctypes.c_int (iptlvt)
        self.m_model.m_eagme.BASME_MODVIS_IPTLVT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variptlvt))
        iptlvt          = variptlvt.value
        return          iptlvt

    @surveyPoint.setter
    def surveyPoint (self, iptlvt):
        """
        Ponto de levantamento topográfico (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variptlvt       = ctypes.c_int (iptlvt)
        self.m_model.m_eagme.BASME_MODVIS_IPTLVT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variptlvt))

#
#       Modos de visualização de cargas
#
class VisModeLoads ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de cargas\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def beamDistributedLoad (self):
        """
        Cargas distribuídas nas vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        cardis          = 0
        varcardis       = ctypes.c_int (cardis)
        self.m_model.m_eagme.BASME_MODVIS_CARDIS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcardis))
        cardis          = varcardis.value
        return          cardis

    @beamDistributedLoad.setter
    def beamDistributedLoad (self, cardis):
        """
        Cargas distribuídas nas vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcardis       = ctypes.c_int (cardis)
        self.m_model.m_eagme.BASME_MODVIS_CARDIS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcardis))
    @property
    def slabDistributedLoad (self):
        """
        Cargas distribuídas nas lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        cardislaj       = 0
        varcardislaj    = ctypes.c_int (cardislaj)
        self.m_model.m_eagme.BASME_MODVIS_CARDISLAJ_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcardislaj))
        cardislaj       = varcardislaj.value
        return          cardislaj

    @slabDistributedLoad.setter
    def slabDistributedLoad (self, cardislaj):
        """
        Cargas distribuídas nas lajes (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcardislaj    = ctypes.c_int (cardislaj)
        self.m_model.m_eagme.BASME_MODVIS_CARDISLAJ_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcardislaj))
    @property
    def concentratedLoad (self):
        """
        Cargas concentradas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        carcon          = 0
        varcarcon       = ctypes.c_int (carcon)
        self.m_model.m_eagme.BASME_MODVIS_CARCON_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcarcon))
        carcon          = varcarcon.value
        return          carcon

    @concentratedLoad.setter
    def concentratedLoad (self, carcon):
        """
        Cargas concentradas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcarcon       = ctypes.c_int (carcon)
        self.m_model.m_eagme.BASME_MODVIS_CARCON_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcarcon))

    @property
    def linearLoad (self):
        """
        Cargas concentradas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        carlin          = 0
        varcarlin       = ctypes.c_int (carlin)
        self.m_model.m_eagme.BASME_MODVIS_CARLIN_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcarlin))
        carlin          = varcarlin.value
        return          carlin

    @linearLoad.setter
    def linearLoad (self, carlin):
        """
        Cargas concentradas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcarlin       = ctypes.c_int (carlin)
        self.m_model.m_eagme.BASME_MODVIS_CARLIN_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcarlin))

    @property
    def areaDistributedLoad (self):
        """
        Carga distribuída por área (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        carare          = 0
        varcarare       = ctypes.c_int (carare)
        self.m_model.m_eagme.BASME_MODVIS_CARARE_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcarare))
        carare          = varcarare.value
        return          carare

    @areaDistributedLoad.setter
    def areaDistributedLoad (self, carare):
        """
        Carga distribuída por área (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcarare       = ctypes.c_int (carare)
        self.m_model.m_eagme.BASME_MODVIS_CARARE_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcarare))
        
    @property
    def soilPressureLoad (self):
        """
        Cargas de empuxo (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        icaremp         = 0
        varicaremp      = ctypes.c_int (icaremp)
        self.m_model.m_eagme.BASME_MODVIS_ICAREMP_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varicaremp))
        icaremp         = varicaremp.value
        return          icaremp

    @soilPressureLoad.setter
    def soilPressureLoad (self, icaremp):
        """
        Cargas de empuxo (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varicaremp      = ctypes.c_int (icaremp)
        self.m_model.m_eagme.BASME_MODVIS_ICAREMP_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varicaremp))

    @property
    def showCaseOnlyLoad (self):
        """
        Restringir ao caso (0)=todos
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        caricaso        = 0
        varcaricaso     = ctypes.c_int (caricaso)
        self.m_model.m_eagme.BASME_MODVIS_CARICASO_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcaricaso))
        caricaso        = varcaricaso.value
        return          caricaso

    @showCaseOnlyLoad.setter
    def showCaseOnlyLoad (self, caricaso):
        """
        Restringir ao caso (0)=todos
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcaricaso     = ctypes.c_int (caricaso)
        self.m_model.m_eagme.BASME_MODVIS_CARICASO_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcaricaso))

    @property
    def manualWindDistribution (self):
        """
        Distribuição manual de vento (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        carvendst       = 0
        varcarvendst    = ctypes.c_int (carvendst)
        self.m_model.m_eagme.BASME_MODVIS_CARVENDST_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varcarvendst))
        carvendst       = varcarvendst.value
        return          carvendst

    @manualWindDistribution.setter
    def manualWindDistribution (self, carvendst):
        """
        Distribuição manual de vento (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcarvendst    = ctypes.c_int (carvendst)
        self.m_model.m_eagme.BASME_MODVIS_CARVENDST_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varcarvendst))
        
    @property
    def manualWindPrefix (self):
        """
        Prefixo do caso de vento para distribuição manual (""=Todos)
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcarvenpref   = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_MODVIS_CARVENPREF_LER (ctypes.byref (varmodvis),
                            varcarvenpref)
        carvenpref      = varcarvenpref.value.decode(TQSUtil.CHARSET)
        return          carvenpref

    @manualWindPrefix.setter
    def manualWindPrefix (self, carvenpref):
        """
        Prefixo do caso de vento para distribuição manual (""=Todos)
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varcarvenpref   = ctypes.c_char_p (carvenpref.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_MODVIS_CARVENPREF_DEF (ctypes.byref (varmodvis),
                            varcarvenpref)
        
    @property
    def loadViewMode (self):
        """
        Mostrar cargas em (0) 2D (1) 3D (2) 2D e 3D
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        icargas3d       = 0
        varicargas3d    = ctypes.c_int (icargas3d)
        self.m_model.m_eagme.BASME_MODVIS_ICARGAS3D_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varicargas3d))
        icargas3d       = varicargas3d.value
        return          icargas3d

    @loadViewMode.setter
    def loadViewMode (self, icargas3d):
        """
        Mostrar cargas em (0) 2D (1) 3D (2) 2D e 3D
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varicargas3d    = ctypes.c_int (icargas3d)
        self.m_model.m_eagme.BASME_MODVIS_ICARGAS3D_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varicargas3d))
        
#
#       Modos de visualização de fundações
#
class VisModeFoundations ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de fundações\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def foundations (self):
        """
        Fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        fundac          = 0
        varfundac       = ctypes.c_int (fundac)
        self.m_model.m_eagme.BASME_MODVIS_FUNDAC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfundac))
        fundac          = varfundac.value
        return          fundac

    @foundations.setter
    def foundations (self, fundac):
        """
        Fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfundac       = ctypes.c_int (fundac)
        self.m_model.m_eagme.BASME_MODVIS_FUNDAC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfundac))

    @property
    def name (self):
        """
        Títulos de fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funtit          = 0
        varfuntit       = ctypes.c_int (funtit)
        self.m_model.m_eagme.BASME_MODVIS_FUNTIT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfuntit))
        funtit          = varfuntit.value
        return          funtit

    @name.setter
    def name (self, funtit):
        """
        Títulos de fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfuntit       = ctypes.c_int (funtit)
        self.m_model.m_eagme.BASME_MODVIS_FUNTIT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfuntit))

    @property
    def dimensions (self):
        """
        Dimensões de fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        fundim          = 0
        varfundim       = ctypes.c_int (fundim)
        self.m_model.m_eagme.BASME_MODVIS_FUNDIM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfundim))
        fundim          = varfundim.value
        return          fundim

    @dimensions.setter
    def dimensions (self, fundim):
        """
        Dimensões de fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfundim       = ctypes.c_int (fundim)
        self.m_model.m_eagme.BASME_MODVIS_FUNDIM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfundim))

    @property
    def details (self):
        """
        Outros dados de detalhamento de fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        fundad          = 0
        varfundad       = ctypes.c_int (fundad)
        self.m_model.m_eagme.BASME_MODVIS_FUNDAD_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfundad))
        fundad          = varfundad.value
        return          fundad

    @details.setter
    def details (self, fundad):
        """
        Outros dados de detalhamento de fundações (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfundad       = ctypes.c_int (fundad)
        self.m_model.m_eagme.BASME_MODVIS_FUNDAD_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfundad))

    @property
    def piles (self):
        """
        Estacas de blocos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funestac        = 0
        varfunestac     = ctypes.c_int (funestac)
        self.m_model.m_eagme.BASME_MODVIS_FUNESTAC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfunestac))
        funestac        = varfunestac.value
        return          funestac

    @piles.setter
    def piles (self, funestac):
        """
        Estacas de blocos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfunestac     = ctypes.c_int (funestac)
        self.m_model.m_eagme.BASME_MODVIS_FUNESTAC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfunestac))

    @property
    def cutOffLevel (self):
        """
        Cotas de arrasamento (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funcotarras     = 0
        varfuncotarras  = ctypes.c_int (funcotarras)
        self.m_model.m_eagme.BASME_MODVIS_FUNCOTARRAS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfuncotarras))
        funcotarras     = varfuncotarras.value
        return          funcotarras

    @cutOffLevel.setter
    def cutOffLevel (self, funcotarras):
        """
        Cotas de arrasamento (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfuncotarras  = ctypes.c_int (funcotarras)
        self.m_model.m_eagme.BASME_MODVIS_FUNCOTARRAS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfuncotarras))

    @property
    def pierDimension (self):
        """
        Dimensão da base do tubulão (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funtitbasetub   = 0
        varfuntitbasetub= ctypes.c_int (funtitbasetub)
        self.m_model.m_eagme.BASME_MODVIS_FUNTITBASETUB_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfuntitbasetub))
        funtitbasetub   = varfuntitbasetub.value
        return          funtitbasetub

    @pierDimension.setter
    def pierDimension (self, funtitbasetub):
        """
        Dimensão da base do tubulão (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfuntitbasetub= ctypes.c_int (funtitbasetub)
        self.m_model.m_eagme.BASME_MODVIS_FUNTITBASETUB_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfuntitbasetub))

    @property
    def pileQuantity (self):
        """
        Quantidade e bitola de estacas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funquantbit     = 0
        varfunquantbit  = ctypes.c_int (funquantbit)
        self.m_model.m_eagme.BASME_MODVIS_FUNQUANTBIT_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfunquantbit))
        funquantbit     = varfunquantbit.value
        return          funquantbit

    @pileQuantity.setter
    def pileQuantity (self, funquantbit):
        """
        Quantidade e bitola de estacas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfunquantbit  = ctypes.c_int (funquantbit)
        self.m_model.m_eagme.BASME_MODVIS_FUNQUANTBIT_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfunquantbit))

    @property
    def pileIdent (self):
        """
        Número da estaca (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funestnum       = 0
        varfunestnum    = ctypes.c_int (funestnum)
        self.m_model.m_eagme.BASME_MODVIS_FUNESTNUM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfunestnum))
        funestnum       = varfunestnum.value
        return          funestnum

    @pileIdent.setter
    def pileIdent (self, funestnum):
        """
        Número da estaca (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfunestnum    = ctypes.c_int (funestnum)
        self.m_model.m_eagme.BASME_MODVIS_FUNESTNUM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfunestnum))

    @property
    def pileDimensions (self):
        """
        Diâmetro da estaca (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        funestdia       = 0
        varfunestdia    = ctypes.c_int (funestdia)
        self.m_model.m_eagme.BASME_MODVIS_FUNESTDIA_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varfunestdia))
        funestdia       = varfunestdia.value
        return          funestdia

    @pileDimensions.setter
    def pileDimensions (self, funestdia):
        """
        Diâmetro da estaca (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varfunestdia    = ctypes.c_int (funestdia)
        self.m_model.m_eagme.BASME_MODVIS_FUNESTDIA_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varfunestdia))

#
#       Modos de visualização de pré-moldados
#
class VisModePrecast ():

    def __init__ (self, model, vismodes):
        """
        Modos de visualização de pré-modados\n
            model       <- Objeto Model() do modelo atual\n
            vismodes    <- Apontador para objeto VisModes
        """
        self.m_model    = model
        self.m_vismodes = vismodes

    @property
    def constructionRegions (self):
        """
        Regiões pré-moldadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iregioes        = 0
        variregioes     = ctypes.c_int (iregioes)
        self.m_model.m_eagme.BASME_MODVIS_IREGIOES_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variregioes))
        iregioes         = variregioes.value
        return          iregioes

    @constructionRegions.setter
    def constructionRegions (self, iregioes):
        """
        Regiões pré-moldadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variregioes     = ctypes.c_int (iregioes)
        self.m_model.m_eagme.BASME_MODVIS_IREGIOES_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variregioes))

    @property
    def floorPlanGroups (self):
        """
        Título dos grupos de formas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        igrupopre       = 0
        varigrupopre    = ctypes.c_int (igrupopre)
        self.m_model.m_eagme.BASME_MODVIS_IGRUPOPRE_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varigrupopre))
        igrupopre       = varigrupopre.value
        return          igrupopre

    @floorPlanGroups.setter
    def floorPlanGroups (self, igrupopre):
        """
        Título dos grupos de formas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varigrupopre    = ctypes.c_int (igrupopre)
        self.m_model.m_eagme.BASME_MODVIS_IGRUPOPRE_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varigrupopre))

    @property
    def reinforcementGroups (self):
        """
        Título dos grupos de armação (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        igrupoarm       = 0
        varigrupoarm    = ctypes.c_int (igrupoarm)
        self.m_model.m_eagme.BASME_MODVIS_IGRUPOARM_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varigrupoarm))
        igrupoarm       = varigrupoarm.value
        return          igrupoarm

    @reinforcementGroups.setter
    def reinforcementGroups (self, igrupoarm):
        """
        Título dos grupos de armação (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varigrupoarm    = ctypes.c_int (igrupoarm)
        self.m_model.m_eagme.BASME_MODVIS_IGRUPOARM_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varigrupoarm))

    @property
    def corbelsName (self):
        """
        Título de consolos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ititcons        = 0
        varititcons     = ctypes.c_int (ititcons)
        self.m_model.m_eagme.BASME_MODVIS_ITITCONS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varititcons))
        ititcons        = varititcons.value
        return          ititcons

    @corbelsName.setter
    def corbelsName (self, ititcons):
        """
        Título de consolos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varititcons     = ctypes.c_int (ititcons)
        self.m_model.m_eagme.BASME_MODVIS_ITITCONS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varititcons))

    @property
    def corbels (self):
        """
        Consolos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iconsolos       = 0
        variconsolos    = ctypes.c_int (iconsolos)
        self.m_model.m_eagme.BASME_MODVIS_ICONSOLOS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variconsolos))
        iconsolos       = variconsolos.value
        return          iconsolos

    @corbels.setter
    def corbels (self, iconsolos):
        """
        Consolos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variconsolos    = ctypes.c_int (iconsolos)
        self.m_model.m_eagme.BASME_MODVIS_ICONSOLOS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variconsolos))

    @property
    def corbelsData (self):
        """
        Dados de consolos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        idadcons        = 0
        varidadcons     = ctypes.c_int (idadcons)
        self.m_model.m_eagme.BASME_MODVIS_IDADCONS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varidadcons))
        idadcons        = varidadcons.value
        return          idadcons

    @corbelsData.setter
    def corbelsData (self, idadcons):
        """
        Dados de consolos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varidadcons     = ctypes.c_int (idadcons)
        self.m_model.m_eagme.BASME_MODVIS_IDADCONS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varidadcons))

    @property
    def accessories (self):
        """
        Acessórios (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iacessorios     = 0
        variacessorios  = ctypes.c_int (iacessorios)
        self.m_model.m_eagme.BASME_MODVIS_IACESSORIOS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variacessorios))
        iacessorios     = variacessorios.value
        return          iacessorios

    @accessories.setter
    def accessories (self, iacessorios):
        """
        Acessórios (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variacessorios  = ctypes.c_int (iacessorios)
        self.m_model.m_eagme.BASME_MODVIS_IACESSORIOS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variacessorios))

    @property
    def slabsReport (self):
        """
        Resultados do cálculo de lajes pré-moldadas, se disponível (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ipreljpcalc     = 0
        varipreljpcalc  = ctypes.c_int (ipreljpcalc)
        self.m_model.m_eagme.BASME_MODVIS_IPRELJPCALC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varipreljpcalc))
        ipreljpcalc     = varipreljpcalc.value
        return          ipreljpcalc

    @slabsReport.setter
    def slabsReport (self, ipreljpcalc):
        """
        Resultados do cálculo de lajes pré-moldadas, se disponível (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varipreljpcalc  = ctypes.c_int (ipreljpcalc)
        self.m_model.m_eagme.BASME_MODVIS_IPRELJPCALC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varipreljpcalc))

    @property
    def showSlabsReport (self):
        """
        Mostrar o relatório após o cálculo de lajes pré-moldadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ipreljprcalc    = 0
        varipreljprcalc = ctypes.c_int (ipreljprcalc)
        self.m_model.m_eagme.BASME_MODVIS_IPRELJPRCALC_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varipreljprcalc))
        ipreljprcalc    = varipreljprcalc.value
        return          ipreljprcalc

    @showSlabsReport.setter
    def showSlabsReport (self, ipreljprcalc):
        """
        Mostrar o relatório após o cálculo de lajes pré-moldadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varipreljprcalc = ctypes.c_int (ipreljprcalc)
        self.m_model.m_eagme.BASME_MODVIS_IPRELJPRCALC_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varipreljprcalc))

    @property
    def beamsSectionTitle (self):
        """
        Título de seções catalogadas vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ipretitsecvig   = 0
        varipretitsecvig= ctypes.c_int (ipretitsecvig)
        self.m_model.m_eagme.BASME_MODVIS_IPRETITSECVIG_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varipretitsecvig))
        ipretitsecvig   = varipretitsecvig.value
        return          ipretitsecvig

    @beamsSectionTitle.setter
    def beamsSectionTitle (self, ipretitsecvig):
        """
        Título de seções catalogadas vigas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varipretitsecvig= ctypes.c_int (ipretitsecvig)
        self.m_model.m_eagme.BASME_MODVIS_IPRETITSECVIG_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varipretitsecvig))

    @property
    def sectionsLines (self):
        """
        Linhas de contorno das seções não padrão (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        iprelinsecnp    = 0
        variprelinsecnp = ctypes.c_int (iprelinsecnp)
        self.m_model.m_eagme.BASME_MODVIS_IPRELINSECNP_LER (ctypes.byref (varmodvis),
                            ctypes.byref (variprelinsecnp))
        iprelinsecnp    = variprelinsecnp.value
        return          iprelinsecnp

    @sectionsLines.setter
    def sectionsLines (self, iprelinsecnp):
        """
        Linhas de contorno das seções não padrão (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        variprelinsecnp = ctypes.c_int (iprelinsecnp)
        self.m_model.m_eagme.BASME_MODVIS_IPRELINSECNP_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (variprelinsecnp))

    @property
    def inserts (self):
        """
        Insertos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        insertos        = 0
        varinsertos     = ctypes.c_int (insertos)
        self.m_model.m_eagme.BASME_MODVIS_INSERTOS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varinsertos))
        insertos        = varinsertos.value
        return          insertos

    @inserts.setter
    def inserts (self, insertos):
        """
        Insertos (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varinsertos     = ctypes.c_int (insertos)
        self.m_model.m_eagme.BASME_MODVIS_INSERTOS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varinsertos))

    @property
    def facades (self):
        """
        Fachadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        ifachadas       = 0
        varifachadas    = ctypes.c_int (ifachadas)
        self.m_model.m_eagme.BASME_MODVIS_IFACHADAS_LER (ctypes.byref (varmodvis),
                            ctypes.byref (varifachadas))
        ifachadas       = varifachadas.value
        return          ifachadas

    @facades.setter
    def facades (self, ifachadas):
        """
        Fachadas (0) Não (1) Sim
        """
        varmodvis       = ctypes.c_void_p (self.m_vismodes.m_modvis)
        varifachadas    = ctypes.c_int (ifachadas)
        self.m_model.m_eagme.BASME_MODVIS_IFACHADAS_DEF (ctypes.byref (varmodvis),
                            ctypes.byref (varifachadas))

#------------------------------------------------------------------------------
#       Objeto de dados de escadas
#
class StairCase ():

    def __init__ (self, model, escdad):
        """
        Dados de escadas\n
            model       <- Objeto Model() do modelo atual\n
            escdad      <- Apontador para objeto CEscDad
        """
        self.m_model    = model
        self.m_escdad   = escdad

    @property
    def tread (self):
        """
        Passo cm
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        passo           = 0.
        varpasso        = ctypes.c_double (passo)
        self.m_model.m_eagme.BASME_ESCDAD_PASSO_LER (ctypes.byref (varescdad),
                            ctypes.byref (varpasso))
        passo           = varpasso.value
        return          passo

    @tread.setter
    def tread (self, passo):
        """
        Passo cm
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        varpasso        = ctypes.c_double (passo)
        self.m_model.m_eagme.BASME_ESCDAD_PASSO_DEF (ctypes.byref (varescdad),
                            ctypes.byref (varpasso))

    @property
    def riser (self):
        """
        Espelho cm
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        espelho         = 0.
        varespelho      = ctypes.c_double (espelho)
        self.m_model.m_eagme.BASME_ESCDAD_ESPELHO_LER (ctypes.byref (varescdad),
                            ctypes.byref (varespelho))
        espelho         = varespelho.value
        return          espelho

    @riser.setter
    def riser (self, espelho):
        """
        Espelho cm
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        varespelho      = ctypes.c_double (espelho)
        self.m_model.m_eagme.BASME_ESCDAD_ESPELHO_DEF (ctypes.byref (varescdad),
                            ctypes.byref (varespelho))

    @property
    def adjustment (self):
        """
        Ajuste inicial ou final cm conforme adjustmentMode
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        ajuste          = 0.
        varajuste       = ctypes.c_double (ajuste)
        self.m_model.m_eagme.BASME_ESCDAD_AJUSTE_LER (ctypes.byref (varescdad),
                            ctypes.byref (varajuste))
        ajuste          = varajuste.value
        return          ajuste

    @adjustment.setter
    def adjustment (self, ajuste):
        """
        Ajuste inicial ou final cm conforme adjustmentMode
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        varajuste       = ctypes.c_double (ajuste)
        self.m_model.m_eagme.BASME_ESCDAD_AJUSTE_DEF (ctypes.byref (varescdad),
                            ctypes.byref (varajuste))

    @property
    def adjustmentMode (self):
        """
        Ajuste (0) Inicial (1) Final
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        iajustefin      = 0
        variajustefin   = ctypes.c_int (iajustefin)
        self.m_model.m_eagme.BASME_ESCDAD_IAJUSTEFIN_LER (ctypes.byref (varescdad),
                            ctypes.byref (variajustefin))
        iajustefin      = variajustefin.value
        return          iajustefin

    @adjustmentMode.setter
    def adjustmentMode (self, iajustefin):
        """
        Ajuste (0) Inicial (1) Final
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        variajustefin   = ctypes.c_int (iajustefin)
        self.m_model.m_eagme.BASME_ESCDAD_IAJUSTEFIN_DEF (ctypes.byref (varescdad),
                            ctypes.byref (variajustefin))

    @property
    def fixedSteps (self):
        """
        Número de degraus fixos
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        ndegrausfixo    = 0
        varndegrausfixo = ctypes.c_int (ndegrausfixo)
        self.m_model.m_eagme.BASME_ESCDAD_NDEGRAUSFIXO_LER (ctypes.byref (varescdad),
                            ctypes.byref (varndegrausfixo))
        ndegrausfixo    = varndegrausfixo.value
        return          ndegrausfixo

    @fixedSteps.setter
    def fixedSteps (self, ndegrausfixo):
        """
        Número de degraus fixos
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        varndegrausfixo = ctypes.c_int (ndegrausfixo)
        self.m_model.m_eagme.BASME_ESCDAD_NDEGRAUSFIXO_DEF (ctypes.byref (varescdad),
                            ctypes.byref (varndegrausfixo))

    @property
    def winderStair (self):
        """
        Representar como escada plissada (0) Não (1) Sim
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        iplissada       = 0
        variplissada    = ctypes.c_int (iplissada)
        self.m_model.m_eagme.BASME_ESCDAD_IPLISSADA_LER (ctypes.byref (varescdad),
                            ctypes.byref (variplissada))
        iplissada       = variplissada.value
        return          iplissada

    @winderStair.setter
    def winderStair (self, iplissada):
        """
        Representar como escada plissada (0) Não (1) Sim
        """
        varescdad       = ctypes.c_void_p (self.m_escdad)
        variplissada    = ctypes.c_int (iplissada)
        self.m_model.m_eagme.BASME_ESCDAD_IPLISSADA_DEF (ctypes.byref (varescdad),
                            ctypes.byref (variplissada))
#------------------------------------------------------------------------------
#       Objeto de lajes somente de volume
#
class VolumeOnlySlab ():

    def __init__ (self, model, lajsovol):
        """
        Dados de laje somente de volume\n
            model       <- Objeto Model() do modelo atual\n
            lajsovol    <- Apontador para objeto CLajSoVol
        """
        self.m_model    = model
        self.m_lajsovol = lajsovol
        
    @property
    def insertionX (self):
        """
        Ponto de inserção X de laje retangular
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        xins            = 0.
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_LAJSOVOL_PTINSX_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varxins))
        xins            = varxins.value
        return          xins

    @insertionX.setter
    def insertionX (self, xins):
        """
        Ponto de inserção X de laje retangular
        """
        varlajsovol       = ctypes.c_void_p (self.m_lajsovol)
        varxins                 = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_LAJSOVOL_PTINSX_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varxins))

    @property
    def insertionY (self):
        """
        Ponto de inserção Y de laje retangular
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        yins            = 0.
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_LAJSOVOL_PTINSY_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varyins))
        yins            = varyins.value
        return          yins

    @insertionY.setter
    def insertionY (self, yins):
        """
        Ponto de inserção Y de laje retangular
        """
        varlajsovol       = ctypes.c_void_p (self.m_lajsovol)
        varyins                 = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_LAJSOVOL_PTINSY_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varyins))

    @property
    def fixedSpace (self):
        """
        Fixar comprimento da laje (0) Não  (1) Sim
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        ifixcompr       = 0
        varifixcompr    = ctypes.c_int (ifixcompr)
        self.m_model.m_eagme.BASME_LAJSOVOL_IFIXCOMPR_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varifixcompr))
        ifixcompr            = varifixcompr.value
        return          ifixcompr

    @fixedSpace.setter
    def fixedSpace (self, ifixcompr):
        """
        Fixar comprimento da laje (0) Não  (1) Sim
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varifixcompr    = ctypes.c_int (ifixcompr)
        self.m_model.m_eagme.BASME_LAJSOVOL_IFIXCOMPR_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varifixcompr))

    @property
    def space (self):
        """
        Comprimento de laje retangular cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        compr           = 0.
        varcompr        = ctypes.c_double (compr)
        self.m_model.m_eagme.BASME_LAJSOVOL_COMPR_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varcompr))
        compr           = varcompr.value
        return          compr

    @space.setter
    def space (self, compr):
        """
        Comprimento de laje retangular cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varcompr        = ctypes.c_double (compr)
        self.m_model.m_eagme.BASME_LAJSOVOL_COMPR_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varcompr))
    @property
    def fixedWidth (self):
        """
        Fixar largura da laje (0) Não  (1) Sim
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        ifixalarg       = 0
        varifixalarg    = ctypes.c_int (ifixalarg)
        self.m_model.m_eagme.BASME_LAJSOVOL_IFIXALARG_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varifixalarg))
        ifixalarg            = varifixalarg.value
        return          ifixalarg

    @fixedWidth.setter
    def fixedWidth (self, ifixalarg):
        """
        Fixar largura da laje (0) Não  (1) Sim
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varifixalarg    = ctypes.c_int (ifixalarg)
        self.m_model.m_eagme.BASME_LAJSOVOL_IFIXALARG_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varifixalarg))

    @property
    def width (self):
        """
        Largura de laje retangular cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        alarg           = 0.
        varalarg        = ctypes.c_double (alarg)
        self.m_model.m_eagme.BASME_LAJSOVOL_ALARG_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varalarg))
        alarg           = varalarg.value
        return          alarg

    @width.setter
    def width (self, alarg):
        """
        Largura de laje retangular cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varalarg        = ctypes.c_double (alarg)
        self.m_model.m_eagme.BASME_LAJSOVOL_ALARG_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varalarg))

    @property
    def fixedAngle (self):
        """
        Fixar ângulo da laje (0) Não  (1) Sim
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        ifixang         = 0
        varifixang      = ctypes.c_int (ifixang)
        self.m_model.m_eagme.BASME_LAJSOVOL_IFIXANG_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varifixang))
        ifixang            = varifixang.value
        return          ifixang

    @fixedAngle.setter
    def fixedAngle (self, ifixang):
        """
        Fixar ângulo da laje (0) Não  (1) Sim
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varifixang      = ctypes.c_int (ifixang)
        self.m_model.m_eagme.BASME_LAJSOVOL_IFIXANG_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varifixang))
    @property
    def angle (self):
        """
        Direção da laje retangular em graus
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        ang             = 0.
        varang          = ctypes.c_double (ang)
        self.m_model.m_eagme.BASME_LAJSOVOL_ANG_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varang))
        ang             = varang.value
        return          ang

    @angle.setter
    def angle (self, ang):
        """
        Direção da laje retangular em graus
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varang          = ctypes.c_double (ang)
        self.m_model.m_eagme.BASME_LAJSOVOL_ANG_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varang))

    @property
    def recess (self):
        """
        Rebaixo inicial em cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        dfs             = 0.
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_LAJSOVOL_DFS_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (vardfs))
        dfs             = vardfs.value
        return          dfs

    @recess.setter
    def recess (self, dfs):
        """
        Rebaixo inicial em cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_LAJSOVOL_DFS_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (vardfs))

    @property
    def zHeight (self):
        """
        Altura Z total em cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        alturaz         = 0.
        varalturaz      = ctypes.c_double (alturaz)
        self.m_model.m_eagme.BASME_LAJSOVOL_ALTURAZ_LER (ctypes.byref (varlajsovol), 
                            ctypes.byref (varalturaz))
        alturaz         = varalturaz.value
        return          alturaz

    @zHeight.setter
    def zHeight (self, alturaz):
        """
        Altura Z total em cm
        """
        varlajsovol     = ctypes.c_void_p (self.m_lajsovol)
        varalturaz      = ctypes.c_double (alturaz)
        self.m_model.m_eagme.BASME_LAJSOVOL_ALTURAZ_DEF (ctypes.byref (varlajsovol), 
                            ctypes.byref (varalturaz))

#------------------------------------------------------------------------------
#       Objeto de estaca para laje radier CEstacRad
#
class SlabFoundationPile (SMObject):

    def __init__ (self, model, estacrad):
        """
        Dados de estaca para laje radier\n
            model       <- Objeto Model() do modelo atual\n
            estacrad    <- Apontador para objeto CEstacRad
        """
        self.m_model    = model
        self.m_estacrad = estacrad
        super().__init__(model, self.m_estacrad)

#------------------------------------------------------------------------------
#       Objeto de furo em pilar CFuroPil
#
class ColumnOpening (SMObject):

    def __init__ (self, model, furopil):
        """
        Dados de furo em pilar\n
            model       <- Objeto Model() do modelo atual\n
            furopil     <- Apontador para objeto CFuroPil
        """
        self.m_model    = model
        self.m_furopil  = furopil
        super().__init__(model, self.m_furopil)

#------------------------------------------------------------------------------
#       Dados de consolos CConsolo
#
class CorbelData ():

    def __init__ (self, model, consolo):
        """
        Pré-moldados: Dados de consolos\n
            model       <- Objeto Model() do modelo atual\n
            consolo      <- Apontador para objeto CConsolo
        """
        self.m_model    = model
        self.m_consolo  = consolo
#------------------------------------------------------------------------------
#       Dados de fachada CFachada
#
class FacadeData (SMObject):

    def __init__ (self, model, fachada):
        """
        Pré-moldados: Dados de fachadas\n
            model       <- Objeto Model() do modelo atual\n
            fachada     <- Apontador para objeto CFachada
        """
        self.m_model    = model
        self.m_fachada  = fachada
        super().__init__(model, self.m_fachada)

#------------------------------------------------------------------------------
#       Dados globais para o BIM CGlbAtrib
#
class GlobalAttrib ():

    def __init__ (self, model, glbatrib):
        """
        Dados globais para o BIM\n
            model       <- Objeto Model() do modelo atual\n
            glbatrib    <- Apontador para objeto CGlbAtrib
        """
        self.m_model    = model
        self.m_glbatrib = glbatrib

    def Clear (self):
        """
        Limpa atributos globais
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        self.m_model.m_eagme.BASME_GLBATRIB_LIMPAR (ctypes.byref (varglbatrib))

    def SetGroup (self, nomgrupo, iabrang, ielementos, ipiso, nompla):
        """
        Define novo grupo. Se já existir, acessa grupo existente
        nomgrupo        Nome do grupo
        iabrang         Abrangência: BIM_GLBA_xxxx
        ielementos      Elementos definidos TYPE_xxxx (TYPE_INDEF=todos)
        ipiso           Piso para iabrang==BIM_GLBA_UMPISO
        nompla          Pavimento para  iabrang==BIM_GLBA_PLANTA
        Retorna: 
        objeto UserAttrib() de atributos do grupo
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        varnomgrupo     = ctypes.c_char_p (nomgrupo.encode (TQSUtil.CHARSET))
        variabrang      = ctypes.c_int (iabrang)
        varielementos   = ctypes.c_int (ielementos)
        varipiso        = ctypes.c_int (ipiso)
        varnompla       = ctypes.c_char_p (nompla.encode (TQSUtil.CHARSET))
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        self.m_model.m_eagme.BASME_GLBATRIB_GRUPO_DEF (ctypes.byref (varglbatrib), \
                    varnomgrupo, ctypes.byref (variabrang), ctypes.byref (varielementos), \
                    ctypes.byref (varipiso), ctypes.byref (varusratrib))
        usratrib        = varusratrib.value
        userattrib      = UserAttrib (self.m_model, usratrib)
        return          userattrib

    def NumGroups (self):
        """
        Retorna o número de grupos de atributos
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        numgrupos       = 0
        varnumgrupos    = ctypes.c_int (numgrupos)
        self.m_model.m_eagme.BASME_GLBATRIB_NUMGRUPOS_LER (ctypes.byref (varglbatrib), \
                        ctypes.byref (varnumgrupos))
        numgrupos       = varnumgrupos.value
        return          numgrupos

    def EraseGroup (self, nomgrupo):
        """
        Apaga atributo existente
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        varnomgrupo     = ctypes.c_char_p (nomgrupo.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GLBATRIB_GRUPO_APAGAR (ctypes.byref (varglbatrib), varnomgrupo)

    def ReadBegin (self):
        """
        Prepara para ler todos os atributos
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        self.m_model.m_eagme.BASME_GLBATRIB_PREPLER (ctypes.byref (varglbatrib))

    def ReadNext (self):
        """
        Lê próximo atributo
        Retorna: 
        nomgrupo        Nome do grupo
        iabrang         Abrangência: BIM_GLBA_xxxx
        ielementos      Elementos definidos TYPE_xxxx (TYPE_INDEF=todos)
        ipiso           Piso para iabrang==BIM_GLBA_UMPISO
        nompla          Pavimento para  iabrang==BIM_GLBA_PLANTA
        UserAttrib()    objeto de atributos do grupo
        istat           (!=0) quando acabar atributos
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        varnomgrupo     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        iabrang         = BIM_GLBA_GLOBAL
        variabrang      = ctypes.c_int (iabrang)
        ielementos      = TYPE_INDEF
        varielementos   = ctypes.c_int (ielementos)
        ipiso           = 0
        varipiso        = ctypes.c_int (ipiso)
        varnompla       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_GLBATRIB_LERPROX (ctypes.byref (varglbatrib),
                    varnomgrupo, ctypes.byref (variabrang), ctypes.byref (varielementos), \
                    ctypes.byref (varipiso), ctypes.byref (varusratrib), \
                    ctypes.byref (varistat))
        nomgrupo        = varnomgrupo.value.decode(TQSUtil.CHARSET)
        iabrang         = variabrang.value
        ielementos      = varielementos.value
        ipiso           = varipiso.value
        usratrib        = varusratrib.value
        userattrib      = UserAttrib (self.m_model, usratrib)
        istat           = varistat.value
        return          nomgrupo, iabrang, ielementos, ipiso, userattrib, istat

    def ReadGroup (self, nomgrupo):
        """
        Lê atributos dado nome do grupo
        nomgrupo        Nome do grupo
        Retorna: 
        iabrang         Abrangência: BIM_GLBA_xxxx
        ielementos      Elementos definidos TYPE_xxxx (TYPE_INDEF=todos)
        ipiso           Piso para iabrang==BIM_GLBA_UMPISO
        nompla          Pavimento para  iabrang==BIM_GLBA_PLANTA
        UserAttrib()    objeto de atributos do grupo
        istat           (!=0) o grupo não existe
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        varnomgrupo     = ctypes.c_char_p (nomgrupo.encode (TQSUtil.CHARSET))
        iabrang         = BIM_GLBA_GLOBAL
        variabrang      = ctypes.c_int (iabrang)
        ielementos      = TYPE_INDEF
        varielementos   = ctypes.c_int (ielementos)
        ipiso           = 0
        varipiso        = ctypes.c_int (ipiso)
        varnompla       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_GLBATRIB_GRUPO_LER (ctypes.byref (varglbatrib),
                    varnomgrupo, ctypes.byref (variabrang), ctypes.byref (varielementos), \
                    ctypes.byref (varipiso), ctypes.byref (varusratrib), \
                    ctypes.byref (varistat))
        iabrang         = variabrang.value
        ielementos      = varielementos.value
        ipiso           = varipiso.value
        usratrib        = varusratrib.value
        userattrib      = UserAttrib (self.m_model, usratrib)
        istat           = varistat.value
        return          iabrang, ielementos, ipiso, userattrib, istat

    def Sort (self):
        """
        Classifica grupos por nome
        """
        varglbatrib     = ctypes.c_void_p (self.m_glbatrib)
        self.m_model.m_eagme.BASME_GLBATRIB_SORT (ctypes.byref (varglbatrib))

#------------------------------------------------------------------------------
#       Lista de plantas de pilares - CPlaPil
#
class ColumnFloorNames ():

    def __init__ (self, model, plapil):
        """
        Dados de usuário para o BIM\n
            model       <- Objeto Model() do modelo atual\n
            plapil      <- Apontador para objeto CPlaPil
        """
        self.m_model    = model
        self.m_plapil   = plapil

    @property
    def floorNumber (self):
        """
        Número de plantas
        """
        varplapil       = ctypes.c_void_p (self.m_plapil)
        numplantas      = 0
        varnumplantas   = ctypes.c_int (numplantas)
        self.m_model.m_eagme.BASME_PLAPIL_NUMPLANTAS_LER (ctypes.byref (varplapil),
                            ctypes.byref (varnumplantas))
        numplantas      = varnumplantas.value
        return          numplantas

    def Clear (self):
        """
        Limpa a lista de plantas e cria duas vazias: a primeira e a última do edifício
        """
        varplapil       = ctypes.c_void_p (self.m_plapil)
        self.m_model.m_eagme.BASME_PLAPIL_LIMPAR (ctypes.byref (varplapil))

    def EnterFloor (self, iplanta, nompla):
        """
        Entra uma planta em posição fixa e empurra as demais plantas\n
            int iplanta         <- Planta 0..floorNumber()-1\n
            char *nompla        <- Nome da planta
        """
        varplapil       = ctypes.c_void_p (self.m_plapil)
        variplanta      = ctypes.c_int (iplanta)
        varnompla       = ctypes.c_char_p (nompla.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_PLAPIL_ENTRAR_IPLANTA (ctypes.byref (varplapil),
                            ctypes.byref (variplanta), varnompla)

    def GetFloor (self, iplanta):
        """
        Lê uma planta do pilar\n
            int iplanta         <- Planta 0..floorNumber()-1\n
        Retorna:\n
            char *nompla        -> Nome da planta
        """
        varplapil       = ctypes.c_void_p (self.m_plapil)
        variplanta      = ctypes.c_int (iplanta)
        varnompla       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_PLAPIL_PLANTA_LER (ctypes.byref (varplapil),
                            ctypes.byref (variplanta), varnompla)
        nompla          = varnompla.value.decode(TQSUtil.CHARSET)
        return         nompla
#------------------------------------------------------------------------------
#       Geometria de vigas - CGeoVig
#
class BeamGeometry ():

    def __init__ (self, model, geovig):
        """
        Geometria de vigas\n
            model       <- Objeto Model() do modelo atual\n
            geovig      <- Apontador para objeto CGeoVig
        """
        self.m_model    = model
        self.m_geovig   = geovig

    @property
    def width (self):
        """
        Largura de viga retangular cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        bvig            = 0.
        varbvig         = ctypes.c_double (bvig)
        self.m_model.m_eagme.BASME_GEOVIG_B_LER (ctypes.byref (vargeovig), 
                            ctypes.byref (varbvig))
        bvig            = varbvig.value
        return          bvig

    @width.setter
    def width (self, bvig):
        """
        Largura de viga retangular cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varbvig         = ctypes.c_double (bvig)
        self.m_model.m_eagme.BASME_GEOVIG_B_DEF (ctypes.byref (vargeovig), 
                            ctypes.byref (varbvig))

    @property
    def depth (self):
        """
        Altura de viga retangular cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        hvig            = 0.
        varhvig         = ctypes.c_double (hvig)
        self.m_model.m_eagme.BASME_GEOVIG_H_LER (ctypes.byref (vargeovig), 
                            ctypes.byref (varhvig))
        hvig            = varhvig.value
        return          hvig

    @depth.setter
    def depth (self, hvig):
        """
        Altura de viga retangular cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varhvig         = ctypes.c_double (hvig)
        self.m_model.m_eagme.BASME_GEOVIG_H_DEF (ctypes.byref (vargeovig), 
                            ctypes.byref (varhvig))
        
    @property
    def eccentricity (self):
        """
        Excentricidade lateral cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        exc             = 0.
        varexc          = ctypes.c_double (exc)
        self.m_model.m_eagme.BASME_GEOVIG_EXC_LER (ctypes.byref (vargeovig), 
                            ctypes.byref (varexc))
        exc             = varexc.value
        return          exc

    @eccentricity.setter
    def eccentricity (self, exc):
        """
        Excentricidade lateral cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varexc          = ctypes.c_double (exc)
        self.m_model.m_eagme.BASME_GEOVIG_EXC_DEF (ctypes.byref (vargeovig), 
                            ctypes.byref (varexc))
        
    @property
    def recess (self):
        """
        Rebaixo em cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        dfs             = 0.
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_GEOVIG_DFS_LER (ctypes.byref (vargeovig), 
                            ctypes.byref (vardfs))
        dfs             = vardfs.value
        return          dfs

    @recess.setter
    def recess (self, dfs):
        """
        Rebaixo em cm
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_GEOVIG_DFS_DEF (ctypes.byref (vargeovig), 
                            ctypes.byref (vardfs))

    def GetFloorRecess (self, floor, beam):
        """
        Rebaixo em cm, considerando piso auxiliar\n
            floor       <- Objeto Floor, com dados de uma planta\n
            beam        <- Objeto Beam que contém esta geometria\n
        Retorna:\n
            double dfspiso -> Rebaixo da viga, cm, considerando piso auxiliar
        """
        varfabrica      = ctypes.c_void_p (floor.m_fabrica)
        varviga         = ctypes.c_void_p (beam.m_viga)
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        dfspiso         = 0.
        vardfspiso      = ctypes.c_double (dfspiso)
        self.m_model.m_eagme.BASME_GEOVIG_DFSPISO_LER (ctypes.byref (varfabrica), 
                            ctypes.byref (varviga), ctypes.byref (vargeovig),
                            ctypes.byref (vardfspiso))
        dfspiso         = vardfspiso.value
        return          dfspiso
    
    @property
    def sectionName (self):
        """
        Nome de seção não padrão - catalogada
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varsecaonp      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOVIG_SECAONP_LER (ctypes.byref (vargeovig),
                            ctypes.byref (varsecaonp))
        secaonp         = varsecaonp.value.decode(TQSUtil.CHARSET)
        return          secaonp

    @sectionName.setter
    def sectionName (self, secaonp):
        """
        Nome de seção não padrão - catalogada
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varsecaonp      = ctypes.c_char_p (secaonp.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOVIG_SECAONP_DEF (ctypes.byref (vargeovig),
                            ctypes.byref (varsecaonp))
    @property
    def sectionRotation (self):
        """
        Ângulo de rotação da seção, graus
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        angsec             = 0.
        varangsec          = ctypes.c_double (angsec)
        self.m_model.m_eagme.BASME_GEOVIG_ANGSEC_LER (ctypes.byref (vargeovig), 
                            ctypes.byref (varangsec))
        angsec             = varangsec.value
        return          angsec

    @sectionRotation.setter
    def sectionRotation (self, angsec):
        """
        Ângulo de rotação da seção, graus
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varangsec          = ctypes.c_double (angsec)
        self.m_model.m_eagme.BASME_GEOVIG_ANGSEC_DEF (ctypes.byref (vargeovig), 
                            ctypes.byref (varangsec))

    @property
    def sectionMaterial (self):
        """
        Título do material diferente do concreto (não padrão)
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varmaternp      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOVIG_MATERNP_LER (ctypes.byref (vargeovig),
                            ctypes.byref (varmaternp))
        maternp         = varmaternp.value.decode(TQSUtil.CHARSET)
        return          maternp

    @sectionMaterial.setter
    def sectionMaterial (self, maternp):
        """
        Título do material diferente do concreto (não padrão)
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        varmaternp      = ctypes.c_char_p (maternp.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOVIG_MATERNP_DEF (ctypes.byref (vargeovig),
                            ctypes.byref (varmaternp))

    @property
    def variableSection (self):
        """
        Retorna objeto VariableSection() para a definição de mísula
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        misvig          = None
        varmisvig       = ctypes.c_void_p (misvig)
        self.m_model.m_eagme.BASME_GEOVIG_MISVIG_LER (ctypes.byref (vargeovig),
                            ctypes.byref (varmisvig))
        misvig          = varmisvig.value
        variablesection = VariableSection (self.m_model, misvig)
        return          variablesection

    @property
    def precastRegion (self):
        """
        Pré-moldados: Região construtiva
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        iregiao         = 0
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_GEOVIG_IREGIAO_LER (ctypes.byref (vargeovig),
                            ctypes.byref (variregiao))
        iregiao         = variregiao.value
        return          iregiao

    @precastRegion.setter
    def precastRegion (self, iregiao):
        """
        Pré-moldados: Região construtiva
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_GEOVIG_IREGIAO_DEF (ctypes.byref (vargeovig),
                            ctypes.byref (variregiao))

    @property
    def beamPrecastData (self):
        """
        Retorna objeto BeamPrecastData para() a definição de viga pré-moldadas
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        previg          = None
        varprevig       = ctypes.c_void_p (previg)
        self.m_model.m_eagme.BASME_GEOVIG_PREVIG_LER (ctypes.byref (vargeovig),
                            ctypes.byref (varprevig))
        previg          = varprevig.value
        beamprecastData = BeamPrecastData (self.m_model, previg)
        return          beamprecastData

    @property
    def beamMetalSection (self):
        """
        Retorna objeto BeamMetalSection() para a definição de viga com seção metálica
        """
        vargeovig       = ctypes.c_void_p (self.m_geovig)
        metvig          = None
        varmetvig       = ctypes.c_void_p (metvig)
        self.m_model.m_eagme.BASME_GEOVIG_METVIG_LER (ctypes.byref (vargeovig),
                            ctypes.byref (varmetvig))
        metvig          = varmetvig.value
        beammetalsection= BeamMetalSection (self.m_model, metvig)
        return          beammetalsection

#------------------------------------------------------------------------------
#       Inércia de viga - CInerVig
#
class BeamInertia ():

    def __init__ (self, model, inervig):
        """
        Geometria de vigas\n
            model       <- Objeto Model() do modelo atual\n
            inervig     <- Apontador para objeto CInerVig
        """
        self.m_model    = model
        self.m_inervig  = inervig

        
    @property
    def effectiveFlange (self):
        """
        Mesa colaborante (0) Não (1) Sim
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        ibcolab         = 0
        varibcolab      = ctypes.c_int (ibcolab)
        self.m_model.m_eagme.BASME_INERVIG_IBCOLAB_LER (ctypes.byref (varinervig),
                            ctypes.byref (varibcolab))
        ibcolab         = varibcolab.value
        return          ibcolab

    @effectiveFlange.setter
    def effectiveFlange (self, ibcolab):
        """
        Mesa colaborante (0) Não (1) Sim
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varibcolab      = ctypes.c_int (ibcolab)
        self.m_model.m_eagme.BASME_INERVIG_IBCOLAB_DEF (ctypes.byref (varinervig),
                            ctypes.byref (varibcolab))

    @property
    def maxEffectiveFlange (self):
        """
        Mesa colaborante máxima cm
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        bcolabmax       = 0.
        varbcolabmax    = ctypes.c_double (bcolabmax)
        self.m_model.m_eagme.BASME_INERVIG_BCOLABMAX_LER (ctypes.byref (varinervig),
                            ctypes.byref (varbcolabmax))
        bcolabmax       = varbcolabmax.value
        return          bcolabmax

    @maxEffectiveFlange.setter
    def maxEffectiveFlange (self, bcolabmax):
        """
        Mesa colaborante máxima cm
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varbcolabmax    = ctypes.c_double (bcolabmax)
        self.m_model.m_eagme.BASME_INERVIG_BCOLABMAX_DEF (ctypes.byref (varinervig),
                            ctypes.byref (varbcolabmax))

    @property
    def fixedEffectiveFlange (self):
        """
        Mesa colaborante fixa cm
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        bcolabfix       = 0.
        varbcolabfix    = ctypes.c_double (bcolabfix)
        self.m_model.m_eagme.BASME_INERVIG_BCOLABFIX_LER (ctypes.byref (varinervig),
                            ctypes.byref (varbcolabfix))
        bcolabfix       = varbcolabfix.value
        return          bcolabfix

    @fixedEffectiveFlange.setter
    def fixedEffectiveFlange (self, bcolabfix):
        """
        Mesa colaborante fixa cm
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varbcolabfix    = ctypes.c_double (bcolabfix)
        self.m_model.m_eagme.BASME_INERVIG_BCOLABFIX_DEF (ctypes.byref (varinervig),
                            ctypes.byref (varbcolabfix))

    @property
    def torsionalMomentMode (self):
        """
        Divisor de inércia à torção definido em (0) Critérios (1) torsionalMomentDivider ()
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        itorcao         = 0
        varitorcao      = ctypes.c_int (itorcao)
        self.m_model.m_eagme.BASME_INERVIG_ITORCAO_LER (ctypes.byref (varinervig),
                            ctypes.byref (varitorcao))
        itorcao         = varitorcao.value
        return          itorcao

    @torsionalMomentMode.setter
    def torsionalMomentMode (self, itorcao):
        """
        Divisor de inércia à torção definido em (0) Critérios (1) torsionalMomentDivider ()
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varitorcao      = ctypes.c_int (itorcao)
        self.m_model.m_eagme.BASME_INERVIG_ITORCAO_DEF (ctypes.byref (varinervig),
                            ctypes.byref (varitorcao))

    @property
    def torsionalMomentDivider (self):
        """
        Divisor de inércia à flexão, conforme torsionalMomentMode
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        divtor          = 0.
        vardivtor       = ctypes.c_double (divtor)
        self.m_model.m_eagme.BASME_INERVIG_DIVTOR_LER (ctypes.byref (varinervig),
                            ctypes.byref (vardivtor))
        divtor          = vardivtor.value
        return          divtor

    @torsionalMomentDivider.setter
    def torsionalMomentDivider (self, divtor):
        """
        Divisor de inércia à flexão, conforme torsionalMomentMode
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        vardivtor       = ctypes.c_double (divtor)
        self.m_model.m_eagme.BASME_INERVIG_DIVTOR_DEF (ctypes.byref (varinervig),
                            ctypes.byref (vardivtor))

    @property
    def inertiaMomentDivider (self):
        """
        Divisor de inércia à flexão, se (!=0)
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        divflex         = 0.
        vardivflex      = ctypes.c_double (divflex)
        self.m_model.m_eagme.BASME_INERVIG_DIVFLEX_LER (ctypes.byref (varinervig),
                            ctypes.byref (vardivflex))
        divflex         = vardivflex.value
        return          divflex

    @inertiaMomentDivider.setter
    def inertiaMomentDivider (self, divflex):
        """
        Divisor de inércia à flexão, se (!=0)
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        vardivflex       = ctypes.c_double (divflex)
        self.m_model.m_eagme.BASME_INERVIG_DIVFLEX_DEF (ctypes.byref (varinervig),
                            ctypes.byref (vardivflex))

    def _GetIndepDeLaje (self, idir):
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varidir         = ctypes.c_int (idir)
        inaoquebrlaj    = 0
        varinaoquebrlaj = ctypes.c_int (inaoquebrlaj)
        self.m_model.m_eagme.BASME_INERVIG_INTERLAJE_LER (ctypes.byref (varinervig),
                            ctypes.byref (varidir), ctypes.byref (varinaoquebrlaj))
        inaoquebrlaj    = varinaoquebrlaj.value
        return          inaoquebrlaj

    def _SetIndepDeLaje (self, idir, inaoquebrlaj):
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varidir         = ctypes.c_int (idir)
        varinaoquebrlaj = ctypes.c_int (inaoquebrlaj)
        self.m_model.m_eagme.BASME_INERVIG_INTERLAJE_DEF (ctypes.byref (varinervig),
                            ctypes.byref (varidir), ctypes.byref (varinaoquebrlaj))

    @property
    def notIntercectLeftSlab (self):
        """
        Viga em relação à laje à esquerda (0) intercepta (1) não intercepta
        """
        inaoquebrlaj    = self._GetIndepDeLaje (0)
        return          inaoquebrlaj

    @notIntercectLeftSlab.setter
    def notIntercectLeftSlab (self, inaoquebrlaj):
        """
        Viga em relação à laje à esquerda (0) intercepta (1) não intercepta
        """
        self._SetIndepDeLaje (0, inaoquebrlaj)
        
    @property
    def notIntercectRightSlab (self):
        """
        Viga em relação à laje à direita (0) intercepta (1) não intercepta
        """
        inaoquebrlaj    = self._GetIndepDeLaje (1)
        return          inaoquebrlaj

    @notIntercectRightSlab.setter
    def notIntercectRightSlab (self, inaoquebrlaj):
        """
        Viga em relação à laje à direita (0) intercepta (1) não intercepta
        """
        self._SetIndepDeLaje (1, inaoquebrlaj)

    @property
    def plasticAdaptability (self):
        """
        Capacidade de adaptação plástica à torção (0) Não (1) Sim
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        icapplastor     = 0
        varicapplastor  = ctypes.c_int (icapplastor)
        self.m_model.m_eagme.BASME_INERVIG_ICAPLPASTTOR_LER (ctypes.byref (varinervig),
                            ctypes.byref (varicapplastor))
        icapplastor     = varicapplastor.value
        return          icapplastor

    @plasticAdaptability.setter
    def plasticAdaptability (self, icapplastor):
        """
        Capacidade de adaptação plástica à torção (0) Não (1) Sim
        """
        varinervig      = ctypes.c_void_p (self.m_inervig)
        varicapplastor  = ctypes.c_int (icapplastor)
        self.m_model.m_eagme.BASME_INERVIG_ICAPLPASTTOR_DEF (ctypes.byref (varinervig),
                            ctypes.byref (varicapplastor))

#------------------------------------------------------------------------------
#       Vinculações e outros dados de viga - CVincVig
#
class BeamBond ():

    def __init__ (self, model, vincvig):
        """
        Geometria de vigas\n
            model       <- Objeto Model() do modelo atual\n
            vincvig     <- Apontador para objeto CVincVig
        """
        self.m_model    = model
        self.m_vincvig  = vincvig

    @property
    def wideBeam (self):
        """
        Viga faixa (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        ivigafaixa      = 0
        varivigafaixa   = ctypes.c_int (ivigafaixa)
        self.m_model.m_eagme.BASME_VINCVIG_IVIGAFAIXA_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varivigafaixa))
        ivigafaixa     = varivigafaixa.value
        return          ivigafaixa

    @wideBeam.setter
    def wideBeam (self, ivigafaixa):
        """
        Viga faixa (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varivigafaixa   = ctypes.c_int (ivigafaixa)
        self.m_model.m_eagme.BASME_VINCVIG_IVIGAFAIXA_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varivigafaixa))

    @property
    def fixAtTheBegin (self):
        """
        Engaste inicial (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        iengastini      = 0
        variengastini   = ctypes.c_int (iengastini)
        self.m_model.m_eagme.BASME_VINCVIG_IENGASTINI_LER (ctypes.byref (varvincvig),
                            ctypes.byref (variengastini))
        iengastini      = variengastini.value
        return          iengastini

    @fixAtTheBegin.setter
    def fixAtTheBegin (self, iengastini):
        """
        Engaste inicial (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        variengastini   = ctypes.c_int (iengastini)
        self.m_model.m_eagme.BASME_VINCVIG_IENGASTINI_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (variengastini))

    @property
    def fixAtTheEnd (self):
        """
        Engaste final (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        iengastfin      = 0
        variengastfin   = ctypes.c_int (iengastfin)
        self.m_model.m_eagme.BASME_VINCVIG_IENGASTFIN_LER (ctypes.byref (varvincvig),
                            ctypes.byref (variengastfin))
        iengastfin      = variengastfin.value
        return          iengastfin

    @fixAtTheEnd.setter
    def fixAtTheEnd (self, iengastfin):
        """
        Engaste final (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        variengastfin   = ctypes.c_int (iengastfin)
        self.m_model.m_eagme.BASME_VINCVIG_IENGASTFIN_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (variengastfin))

    @property
    def disableSelfWeight (self):
        """
        Desabilitar peso próprio (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        npp             = 0
        varnpp          = ctypes.c_int (npp)
        self.m_model.m_eagme.BASME_VINCVIG_NPP_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varnpp))
        npp             = varnpp.value
        return          npp

    @disableSelfWeight.setter
    def disableSelfWeight (self, npp):
        """
        Desabilitar peso próprio (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varnpp          = ctypes.c_int (npp)
        self.m_model.m_eagme.BASME_VINCVIG_NPP_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varnpp))

    @property
    def bearColumnByTheFaces (self):
        """
        Intersececção de pilar com faces (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        iveriffaces     = 0
        variveriffaces  = ctypes.c_int (iveriffaces)
        self.m_model.m_eagme.BASME_VINCVIG_IVERIFFACES_LER (ctypes.byref (varvincvig),
                            ctypes.byref (variveriffaces))
        iveriffaces     = variveriffaces.value
        return          iveriffaces

    @bearColumnByTheFaces.setter
    def bearColumnByTheFaces (self, iveriffaces):
        """
        Intersececção de pilar com faces (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        variveriffaces  = ctypes.c_int (iveriffaces)
        self.m_model.m_eagme.BASME_VINCVIG_IVERIFFACES_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (variveriffaces))

    @property
    def adjustEdges (self):
        """
        Ajuste automático das pontas (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        iajusteaut      = 0
        variajusteaut   = ctypes.c_int (iajusteaut)
        self.m_model.m_eagme.BASME_VINCVIG_IAJUSTEAUT_LER (ctypes.byref (varvincvig),
                            ctypes.byref (variajusteaut))
        iajusteaut      = variajusteaut.value
        return          iajusteaut

    @adjustEdges.setter
    def adjustEdges (self, iajusteaut):
        """
        Ajuste automático das pontas (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        variajusteaut   = ctypes.c_int (iajusteaut)
        self.m_model.m_eagme.BASME_VINCVIG_IAJUSTEAUT_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (variajusteaut))

    @property
    def interceptOthersBeams (self):
        """
        Intersececção com outras vigas (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        intervigas      = 0
        varintervigas   = ctypes.c_int (intervigas)
        self.m_model.m_eagme.BASME_VINCVIG_INTERVIGAS_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varintervigas))
        intervigas      = varintervigas.value
        return          intervigas

    @interceptOthersBeams.setter
    def interceptOthersBeams (self, intervigas):
        """
        Intersececção com outras vigas (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varintervigas   = ctypes.c_int (intervigas)
        self.m_model.m_eagme.BASME_VINCVIG_INTERVIGAS_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varintervigas))

    @property
    def startStrapBeam (self):
        """
        Alavanca inicial (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        ialavancaini    = 0
        varialavancaini = ctypes.c_int (ialavancaini)
        self.m_model.m_eagme.BASME_VINCVIG_IALAVANCAINI_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varialavancaini))
        ialavancaini    = varialavancaini.value
        return          ialavancaini

    @startStrapBeam.setter
    def startStrapBeam (self, ialavancaini):
        """
        Alavanca inicial (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varialavancaini = ctypes.c_int (ialavancaini)
        self.m_model.m_eagme.BASME_VINCVIG_IALAVANCAINI_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varialavancaini))

    @property
    def endStrapBeam (self):
        """
        Alavanca final (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        ialavancafin    = 0
        varialavancafin = ctypes.c_int (ialavancafin)
        self.m_model.m_eagme.BASME_VINCVIG_IALAVANCAFIN_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varialavancafin))
        ialavancafin    = varialavancafin.value
        return          ialavancafin

    @endStrapBeam.setter
    def endStrapBeam (self, ialavancafin):
        """
        Alavanca final (0) Não (1) Sim
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varialavancafin = ctypes.c_int (ialavancafin)
        self.m_model.m_eagme.BASME_VINCVIG_IALAVANCAFIN_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varialavancafin))

    @property
    def transferGirder (self):
        """
        Transição (0) pela geometria (1) Sim (2) Não
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        itransic        = 0
        varitransic     = ctypes.c_int (itransic)
        self.m_model.m_eagme.BASME_VINCVIG_ITRANSIC_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varitransic))
        itransic        = varitransic.value
        return          itransic

    @transferGirder.setter
    def transferGirder (self, itransic):
        """
        Transição (0) pela geometria (1) Sim (2) Não
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varitransic     = ctypes.c_int (itransic)
        self.m_model.m_eagme.BASME_VINCVIG_ITRANSIC_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varitransic))

    @property
    def workAs (self):
        """
        Trabalha como (0) Viga (1) Tirante (2) Escora
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        itirante        = 0
        varitirante     = ctypes.c_int (itirante)
        self.m_model.m_eagme.BASME_VINCVIG_ITIRANTE_LER (ctypes.byref (varvincvig),
                            ctypes.byref (varitirante))
        itirante        = varitirante.value
        return          itirante

    @workAs.setter
    def workAs (self, itirante):
        """
        Trabalha como (0) Viga (1) Tirante (2) Escora
        """
        varvincvig      = ctypes.c_void_p (self.m_vincvig)
        varitirante     = ctypes.c_int (itirante)
        self.m_model.m_eagme.BASME_VINCVIG_ITIRANTE_DEF (ctypes.byref (varvincvig),
                            ctypes.byref (varitirante))

#------------------------------------------------------------------------------
#       Dados de inserção de vigas - CInsVig
#
class BeamInsertion ():

    def __init__ (self, model, insvig):
        """
        Geometria de vigas\n
            model       <- Objeto Model() do modelo atual\n
            insvig      <- Apontador para objeto CInsVig
        """
        self.m_model    = model
        self.m_insvig  = insvig

    @property
    def insertBy (self):
        """
        Alinhamento (0) Esquerda (1) Direita (2) Eixo
        """
        varinsvig       = ctypes.c_void_p (self.m_insvig)
        ialinvig        = 0
        varialinvig     = ctypes.c_int (ialinvig)
        self.m_model.m_eagme.BASME_INSVIG_IALINVIG_LER (ctypes.byref (varinsvig),
                            ctypes.byref (varialinvig))
        ialinvig        = varialinvig.value
        return          ialinvig

    @insertBy.setter
    def insertBy (self, ialinvig):
        """
        Alinhamento (0) Esquerda (1) Direita (2) Eixo
        """
        varinsvig       = ctypes.c_void_p (self.m_insvig)
        varialinvig     = ctypes.c_int (ialinvig)
        self.m_model.m_eagme.BASME_INSVIG_IALINVIG_DEF (ctypes.byref (varinsvig),
                            ctypes.byref (varialinvig))

    @property
    def covering (self):
        """
        Revestimento das faces, cm
        """
        varinsvig       = ctypes.c_void_p (self.m_insvig)
        revvig          = 0.
        varrevvig       = ctypes.c_double (revvig)
        self.m_model.m_eagme.BASME_INSVIG_REVVIG_LER (ctypes.byref (varinsvig),
                            ctypes.byref (varrevvig))
        revvig          = varrevvig.value
        return          revvig

    @covering.setter
    def covering (self, revvig):
        """
        Revestimento das faces, cm
        """
        varinsvig       = ctypes.c_void_p (self.m_insvig)
        varrevvig       = ctypes.c_double (revvig)
        self.m_model.m_eagme.BASME_INSVIG_REVVIG_DEF (ctypes.byref (varinsvig),
                            ctypes.byref (varrevvig))

#------------------------------------------------------------------------------
#       Dados de Temperatura / retração - CTempRet
#
class TemperatureShrink ():

    def __init__ (self, model, tempretvig):
        """
        Dados de Temperatura / retração de vigas\n
            model       <- Objeto Model() do modelo atual\n
            tempretvig  <- Apontador para objeto CTempRet
        """
        self.m_model    = model
        self.m_tempretvig= tempretvig

    @property
    def temperatureDefined (self):
        """
        Definição de variação de temperatura ao longo da viga (0) Não (1) Sim
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        itemperatura     = 0
        varitemperatura  = ctypes.c_int (itemperatura)
        self.m_model.m_eagme.BASME_TEMPRET_ITEMPERATURA_LER (ctypes.byref (vartempret),
                            ctypes.byref (varitemperatura))
        itemperatura     = varitemperatura.value
        return          itemperatura

    @temperatureDefined.setter
    def temperatureDefined (self, itemperatura):
        """
        Definição de variação de temperatura ao longo da viga (0) Não (1) Sim
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        varitemperatura  = ctypes.c_int (itemperatura)
        self.m_model.m_eagme.BASME_TEMPRET_ITEMPERATURA_DEF (ctypes.byref (vartempret),
                            ctypes.byref (varitemperatura))

    @property
    def uniformVariation (self):
        """
        Variação longitudinal de temperatura em graus Celcius
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        temvarlon       = 0.
        vartemvarlon    = ctypes.c_double (temvarlon)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARLON_LER (ctypes.byref (vartempret),
                            ctypes.byref (vartemvarlon))
        temvarlon       = vartemvarlon.value
        return          temvarlon

    @uniformVariation.setter
    def uniformVariation (self, temvarlon):
        """
        Variação longitudinal de temperatura em graus Celcius
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        vartemvarlon  = ctypes.c_double (temvarlon)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARLON_DEF (ctypes.byref (vartempret),
                            ctypes.byref (vartemvarlon))

    @property
    def uniformVariation2 (self):
        """
        Variação longitudinal de temperatura em graus Celcius - caso 2
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        temvarlon2      = 0.
        vartemvarlon2   = ctypes.c_double (temvarlon2)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARLON2_LER (ctypes.byref (vartempret),
                            ctypes.byref (vartemvarlon2))
        temvarlon2      = vartemvarlon2.value
        return          temvarlon2

    @uniformVariation2.setter
    def uniformVariation2 (self, temvarlon2):
        """
        Variação longitudinal de temperatura em graus Celcius - caso 2
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        vartemvarlon2   = ctypes.c_double (temvarlon2)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARLON2_DEF (ctypes.byref (vartempret),
                            ctypes.byref (vartemvarlon2))
    @property
    def transverseVariation (self):
        """
        Variação transversal de temperatura em graus Celcius
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        temvartra       = 0.
        vartemvartra    = ctypes.c_double (temvartra)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARTRA_LER (ctypes.byref (vartempret),
                            ctypes.byref (vartemvartra))
        temvartra       = vartemvartra.value
        return          temvartra

    @transverseVariation.setter
    def transverseVariation (self, temvartra):
        """
        Variação transversal de temperatura em graus Celcius
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        vartemvartra    = ctypes.c_double (temvartra)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARTRA_DEF (ctypes.byref (vartempret),
                            ctypes.byref (vartemvartra))

    @property
    def transverseVariation2 (self):
        """
        Variação transversal de temperatura em graus Celcius - caso 2
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        temvartra2      = 0.
        vartemvartra2   = ctypes.c_double (temvartra2)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARTRA2_LER (ctypes.byref (vartempret),
                            ctypes.byref (vartemvartra2))
        temvartra2      = vartemvartra2.value
        return          temvartra2

    @transverseVariation2.setter
    def transverseVariation2 (self, temvartra2):
        """
        Variação transversal de temperatura em graus Celcius - caso 2
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        vartemvartra2   = ctypes.c_double (temvartra2)
        self.m_model.m_eagme.BASME_TEMPRET_TEMVARTRA2_DEF (ctypes.byref (vartempret),
                            ctypes.byref (vartemvartra2))

    @property
    def shrinkageDefined (self):
        """
        Definição de retração ao longo da viga (0) Não (1) Sim
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        iretracao       = 0
        variretracao    = ctypes.c_int (iretracao)
        self.m_model.m_eagme.BASME_TEMPRET_IRETRACAO_LER (ctypes.byref (vartempret),
                            ctypes.byref (variretracao))
        iretracao       = variretracao.value
        return          iretracao

    @shrinkageDefined.setter
    def shrinkageDefined (self, iretracao):
        """
        Definição de retração ao longo da viga (0) Não (1) Sim
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        variretracao    = ctypes.c_int (iretracao)
        self.m_model.m_eagme.BASME_TEMPRET_IRETRACAO_DEF (ctypes.byref (vartempret),
                            ctypes.byref (variretracao))
        
    @property
    def uniformShrinkage (self):
        """
        Variação longitudinal de temperatura equivalente à retração em graus Celcius
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        retvartemp      = 0.
        varretvartemp   = ctypes.c_double (retvartemp)
        self.m_model.m_eagme.BASME_TEMPRET_RETVARTEMP_LER (ctypes.byref (vartempret),
                            ctypes.byref (varretvartemp))
        retvartemp      = varretvartemp.value
        return          retvartemp

    @uniformShrinkage.setter
    def uniformShrinkage (self, retvartemp):
        """
        Variação longitudinal de temperatura equivalente à retração em graus Celcius
        """
        vartempret      = ctypes.c_void_p (self.m_tempretvig)
        varretvartemp   = ctypes.c_double (retvartemp)
        self.m_model.m_eagme.BASME_TEMPRET_RETVARTEMP_DEF (ctypes.byref (vartempret),
                            ctypes.byref (varretvartemp))
      
#------------------------------------------------------------------------------
#       Detalhamento de vigas - CDetVig
#
class BeamDetailing ():

    def __init__ (self, model, detvig):
        """
        Detalhamento de vigas\n
            model       <- Objeto Model() do modelo atual\n
            detvig      <- Apontador para objeto CDetVig
        """
        self.m_model    = model
        self.m_detvig   = detvig

    @property
    def detailable (self):
        """
        Detalhamento da viga (0) Normal (1) Não (2) De compatibilização
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        idetvigas       = 0
        varidetvigas    = ctypes.c_int (idetvigas)
        self.m_model.m_eagme.BASME_DETVIG_IDETVIGAS_LER (ctypes.byref (vardetvig),
                            ctypes.byref (varidetvigas))
        idetvigas       = varidetvigas.value
        return          idetvigas

    @detailable.setter
    def detailable (self, idetvigas):
        """
        Detalhamento da viga (0) Normal (1) Não (2) De compatibilização
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        varidetvigas    = ctypes.c_int (idetvigas)
        self.m_model.m_eagme.BASME_DETVIG_IDETVIGAS_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (varidetvigas))
    @property
    def cover (self):
        """
        Cobrimento em cm
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        cobrimento      = 0.
        varcobrimento   = ctypes.c_double (cobrimento)
        self.m_model.m_eagme.BASME_DETVIG_COBRIMENTO_LER (ctypes.byref (vardetvig),
                            ctypes.byref (varcobrimento))
        cobrimento      = varcobrimento.value
        return          cobrimento

    @cover.setter
    def cover (self, cobrimento):
        """
        Cobrimento em cm
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        varcobrimento   = ctypes.c_double (cobrimento)
        self.m_model.m_eagme.BASME_DETVIG_COBRIMENTO_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (varcobrimento))
      
    @property
    def exposure (self):
        """
        Em contato com o solo (0) Não (1) Sim (2) Exposta ao ambiente
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        icontsolo       = 0
        varicontsolo    = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_DETVIG_ICONTSOLO_LER (ctypes.byref (vardetvig),
                            ctypes.byref (varicontsolo))
        icontsolo       = varicontsolo.value
        return          icontsolo

    @exposure.setter
    def exposure (self, icontsolo):
        """
        Em contato com o solo (0) Não (1) Sim (2) Exposta ao ambiente
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        varicontsolo    = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_DETVIG_ICONTSOLO_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (varicontsolo))

    @property
    def restrainColumns (self):
        """
        A viga trava pilares (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        itravapil       = 0
        varitravapil    = ctypes.c_int (itravapil)
        self.m_model.m_eagme.BASME_DETVIG_ITRAVAPIL_LER (ctypes.byref (vardetvig),
                            ctypes.byref (varitravapil))
        itravapil       = varitravapil.value
        return          itravapil

    @restrainColumns.setter
    def restrainColumns (self, itravapil):
        """
        A viga trava pilares (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        varitravapil    = ctypes.c_int (itravapil)
        self.m_model.m_eagme.BASME_DETVIG_ITRAVAPIL_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (varitravapil))
    @property
    def simulatesCurtain (self):
        """
        Simula uma cortina (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        icortina        = 0
        varicortina     = ctypes.c_int (icortina)
        self.m_model.m_eagme.BASME_DETVIG_ICORTINA_LER (ctypes.byref (vardetvig),
                            ctypes.byref (varicortina))
        icortina        = varicortina.value
        return          icortina

    @simulatesCurtain.setter
    def simulatesCurtain (self, icortina):
        """
        Simula uma cortina (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        varicortina     = ctypes.c_int (icortina)
        self.m_model.m_eagme.BASME_DETVIG_ICORTINA_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (varicortina))
    @property
    def prestressed (self):
        """
        Protendida (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        iprotendida     = 0
        variprotendida  = ctypes.c_int (iprotendida)
        self.m_model.m_eagme.BASME_DETVIG_IPROTENDIDA_LER (ctypes.byref (vardetvig),
                            ctypes.byref (variprotendida))
        iprotendida     = variprotendida.value
        return          iprotendida

    @prestressed.setter
    def prestressed (self, iprotendida):
        """
        Protendida (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        variprotendida  = ctypes.c_int (iprotendida)
        self.m_model.m_eagme.BASME_DETVIG_IPROTENDIDA_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (variprotendida))
    @property
    def vproInterface (self):
        """
        Interface com o VPRO (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        intervpro       = 0
        varintervpro    = ctypes.c_int (intervpro)
        self.m_model.m_eagme.BASME_DETVIG_INTERVPRO_LER (ctypes.byref (vardetvig),
                            ctypes.byref (varintervpro))
        intervpro       = varintervpro.value
        return          intervpro

    @vproInterface.setter
    def vproInterface (self, intervpro):
        """
        Interface com o VPRO (0) Não (1) Sim
        """
        vardetvig       = ctypes.c_void_p (self.m_detvig)
        varintervpro    = ctypes.c_int (intervpro)
        self.m_model.m_eagme.BASME_DETVIG_INTERVPRO_DEF (ctypes.byref (vardetvig),
                            ctypes.byref (varintervpro))

#------------------------------------------------------------------------------
#       Furo em viga - CFuroVig
#
class BeamOpening ():

    def __init__ (self, model, furovig):
        """
        Furo em viga\n
            model       <- Objeto Model() do modelo atual\n
            furovig     <- Apontador para objeto CFuroVig
        """
        self.m_model    = model
        self.m_furovig  = furovig

    @property
    def insertionX (self):
        """
        Ponto de inserção X cm (centro do furo, eixo da viga)
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        xins            = 0.
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_FUROVIG_PTINSX_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varxins))
        xins            = varxins.value
        return          xins

    @insertionX.setter
    def insertionX (self, xins):
        """
        Ponto de inserção X cm (centro do furo, eixo da viga)
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_FUROVIG_PTINSX_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varxins))
    @property
    def insertionY (self):
        """
        Ponto de inserção Y cm (centro do furo, eixo da viga)
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        yins            = 0.
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_FUROVIG_PTINSY_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varyins))
        yins            = varyins.value
        return          yins

    @insertionY.setter
    def insertionY (self, yins):
        """
        Ponto de inserção Y cm (centro do furo, eixo da viga)
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_FUROVIG_PTINSY_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varyins))
        
    @property
    def width (self):
        """
        Largura ou diâmetro em cm, visto em elevação
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        bfuro           = 0.
        varbfuro        = ctypes.c_double (bfuro)
        self.m_model.m_eagme.BASME_FUROVIG_B_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varbfuro))
        bfuro           = varbfuro.value
        return          bfuro

    @width.setter
    def width (self, bfuro):
        """
        Largura ou diâmetro em cm, visto em elevação
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varbfuro        = ctypes.c_double (bfuro)
        self.m_model.m_eagme.BASME_FUROVIG_B_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varbfuro))

    @property
    def height (self):
        """
        Altura em cm, visto em elevação
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        hfuro           = 0.
        varhfuro        = ctypes.c_double (hfuro)
        self.m_model.m_eagme.BASME_FUROVIG_H_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varhfuro))
        hfuro           = varhfuro.value
        return          hfuro

    @height.setter
    def height (self, hfuro):
        """
        Altura em cm, visto em elevação
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varhfuro        = ctypes.c_double (hfuro)
        self.m_model.m_eagme.BASME_FUROVIG_H_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varhfuro))
        
    @property
    def recess (self):
        """
        Rebaixo em relação à face da viga cm
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        dfs             = 0.
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_FUROVIG_DFS_LER (ctypes.byref (varfurovig),
                            ctypes.byref (vardfs))
        dfs             = vardfs.value
        return          dfs

    @recess.setter
    def recess (self, dfs):
        """
        Rebaixo em relação à face da viga cm
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_FUROVIG_DFS_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (vardfs))

    @property
    def format (self):
        """
        Formato do furo (0) Retangular (1) Circular
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        ifurocirc       = 0
        varifurocirc    = ctypes.c_int (ifurocirc)
        self.m_model.m_eagme.BASME_FUROVIG_IFUROCIRC_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varifurocirc))
        ifurocirc       = varifurocirc.value
        return          ifurocirc

    @format.setter
    def format (self, ifurocirc):
        """
        Formato do furo (0) Retangular (1) Circular
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varifurocirc    = ctypes.c_int (ifurocirc)
        self.m_model.m_eagme.BASME_FUROVIG_IFUROCIRC_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varifurocirc))
        
    @property
    def reference (self):
        """
        Referência do rebaixo BEAMOPENINGREFERENCE_xxxx
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        ireferencia     = 0
        varireferencia  = ctypes.c_int (ireferencia)
        self.m_model.m_eagme.BASME_FUROVIG_IREFERENCIA_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varireferencia))
        ireferencia     = varireferencia.value
        return          ireferencia

    @reference.setter
    def reference (self, ireferencia):
        """
        Referência do rebaixo BEAMOPENINGREFERENCE_xxxx
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varireferencia  = ctypes.c_int (ireferencia)
        self.m_model.m_eagme.BASME_FUROVIG_IREFERENCIA_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varireferencia))

    @property
    def identification (self):
        """
        Identificação opcional
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varident        = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_FUROVIG_IDENT_LER (ctypes.byref (varfurovig),
                            varident)
        ident           = varident.value.decode(TQSUtil.CHARSET)
        return          ident

    @identification.setter
    def identification (self, ident):
        """
        Identificação opcional
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varident        = ctypes.c_char_p (ident.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_FUROVIG_IDENT_DEF (ctypes.byref (varfurovig),
                            varident)

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_FUROVIG_IPISOAUX_LER (ctypes.byref (varfurovig),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varfurovig      = ctypes.c_void_p (self.m_furovig)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_FUROVIG_IPISOAUX_DEF (ctypes.byref (varfurovig),
                            ctypes.byref (varipisoaux))
#------------------------------------------------------------------------------
#        Dados de geometria de laje - CGeoLaj
#
class SlabGeometry ():

    def __init__ (self, model, geolaj):
        """
        Dados de geometria de laje\n
            model       <- Objeto Model() do modelo atual\n
            geolaj      <- Apontador para objeto CGeoLaj
        """
        self.m_model    = model
        self.m_geolaj   = geolaj

    @property
    def type (self):
        """
        Tipo de laje SLABTYPE_xxxxx
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        itipo           = 0
        varitipo        = ctypes.c_int (itipo)
        self.m_model.m_eagme.BASME_GEOLAJ_ITIPO_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varitipo))
        itipo         = varitipo.value
        return          itipo

    @type.setter
    def type (self, itipo):
        """
        Tipo de laje SLABTYPE_xxxxx
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varitipo        = ctypes.c_int (itipo)
        self.m_model.m_eagme.BASME_GEOLAJ_ITIPO_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varitipo))

    @property
    def noSelfWeight (self):
        """
        Desconsiderar peso proprio (0) Não (1) Sim
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        npp             = 0
        varnpp          = ctypes.c_int (npp)
        self.m_model.m_eagme.BASME_GEOLAJ_NPP_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varnpp))
        npp             = varnpp.value
        return          npp

    @noSelfWeight.setter
    def noSelfWeight (self, npp):
        """
        Desconsiderar peso proprio (0) Não (1) Sim
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnpp          = ctypes.c_int (npp)
        self.m_model.m_eagme.BASME_GEOLAJ_NPP_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varnpp))

    def GetSelfWeightLoad (self, floor):
        """
        Retorna carga fixa de peso próprio para lajes preo\n
            floor       <- Objeto Floor, com dados de uma planta\n
        Retorna:\n
            objeto Load ()
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        cargapp         = None
        varcargapp      = ctypes.c_void_p (cargapp)
        self.m_model.m_eagme.BASME_GEOLAJ_CARGAPP_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varcargapp))
        cargapp         = varcargapp.value
        load            = Load (self.m_model, floor, cargapp)
        return          load

    @property
    def thickness (self):
        """
        Altura da laje maciça em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        hlaj            = 0.
        varhlaj         = ctypes.c_double (hlaj)
        self.m_model.m_eagme.BASME_GEOLAJ_H_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varhlaj))
        hlaj            = varhlaj.value
        return          hlaj

    @thickness.setter
    def thickness (self, hlaj):
        """
        Altura da laje maciça em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varhlaj         = ctypes.c_double (hlaj)
        self.m_model.m_eagme.BASME_GEOLAJ_H_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varhlaj))
    
    @property
    def recess (self):
        """
        Rebaixo em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        dfslaj          = 0.
        vardfslaj       = ctypes.c_double (dfslaj)
        self.m_model.m_eagme.BASME_GEOLAJ_DFS_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (vardfslaj))
        dfslaj          = vardfslaj.value
        return          dfslaj

    @recess.setter
    def recess (self, dfslaj):
        """
        Rebaixo em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        vardfslaj       = ctypes.c_double (dfslaj)
        self.m_model.m_eagme.BASME_GEOLAJ_DFS_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (vardfslaj))

    def GetFloorRecess (self, floor, slab):
        """
        Rebaixo em cm, considerando piso auxiliar\n
            floor          <- Objeto Floor, com dados de uma planta\n
            slab           <- Objeto Slab que contém esta geometria\n
        Retorna:\n
            double dfspiso -> Rebaixo da laje, cm, considerando piso auxiliar
        """
        varfabrica      = ctypes.c_void_p (floor.m_fabrica)
        varlaje         = ctypes.c_void_p (slab.m_laje)
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        dfspiso         = 0.
        vardfspiso      = ctypes.c_double (dfspiso)
        self.m_model.m_eagme.BASME_GEOLAJ_DFSPISO_LER (ctypes.byref (varfabrica), 
                            ctypes.byref (varlaje), ctypes.byref (vargeolaj),
                            ctypes.byref (vardfspiso))
        dfspiso         = vardfspiso.value
        return          dfspiso

    @property
    def additionalTopRecess (self):
        """
        Rebaixo adicional superior em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        dfssupadi       = 0.
        vardfssupadi    = ctypes.c_double (dfssupadi)
        self.m_model.m_eagme.BASME_GEOLAJ_DFSSUPADI_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (vardfssupadi))
        dfssupadi       = vardfssupadi.value
        return          dfssupadi

    @additionalTopRecess.setter
    def additionalTopRecess (self, dfssupadi):
        """
        Rebaixo adicional superior em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        vardfssupadi    = ctypes.c_double (dfssupadi)
        self.m_model.m_eagme.BASME_GEOLAJ_DFSSUPADI_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (vardfssupadi))

    @property
    def additionalBottomRecess (self):
        """
        Rebaixo adicional inferior em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        dfsinfadi       = 0.
        vardfsinfadi    = ctypes.c_double (dfsinfadi)
        self.m_model.m_eagme.BASME_GEOLAJ_DFSINFADI_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (vardfsinfadi))
        dfsinfadi       = vardfsinfadi.value
        return          dfsinfadi

    @additionalBottomRecess.setter
    def additionalBottomRecess (self, dfsinfadi):
        """
        Rebaixo adicional inferior em cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        vardfsinfadi    = ctypes.c_double (dfsinfadi)
        self.m_model.m_eagme.BASME_GEOLAJ_DFSINFADI_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (vardfsinfadi))

    @property
    def ribbedTopping (self):
        """
        Laje nervurada: capa, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        capa            = 0.
        varcapa         = ctypes.c_double (capa)
        self.m_model.m_eagme.BASME_GEOLAJ_CAPA_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varcapa))
        capa            = varcapa.value
        return          capa

    @ribbedTopping.setter
    def ribbedTopping (self, capa):
        """
        Laje nervurada: capa, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varcapa         = ctypes.c_double (capa)
        self.m_model.m_eagme.BASME_GEOLAJ_CAPA_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varcapa))

    @property
    def ribbedBottomTopping (self):
        """
        Laje nervurada: capa inferior, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        capainf         = 0.
        varcapainf      = ctypes.c_double (capainf)
        self.m_model.m_eagme.BASME_GEOLAJ_CAPAINF_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varcapainf))
        capainf         = varcapainf.value
        return          capainf

    @ribbedBottomTopping.setter
    def ribbedBottomTopping (self, capainf):
        """
        Laje nervurada: capa inferior, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varcapainf      = ctypes.c_double (capainf)
        self.m_model.m_eagme.BASME_GEOLAJ_CAPAINF_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varcapainf))

    @property
    def ribHeight (self):
        """
        Laje nervurada: altura de nervura cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        hner            = 0.
        varhner         = ctypes.c_double (hner)
        self.m_model.m_eagme.BASME_GEOLAJ_HNER_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varhner))
        hner            = varhner.value
        return          hner

    @ribHeight.setter
    def ribHeight (self, hner):
        """
        Laje nervurada: altura de nervura cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varhner         = ctypes.c_double (hner)
        self.m_model.m_eagme.BASME_GEOLAJ_HNER_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varhner))

    @property
    def ribbedFill (self):
        """
        Laje nervurada: peso de enchimento tf/m3
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        ench            = 0.
        varench         = ctypes.c_double (ench)
        self.m_model.m_eagme.BASME_GEOLAJ_ENCH_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varench))
        ench            = varench.value
        return          ench

    @ribbedFill.setter
    def ribbedFill (self, ench):
        """
        Laje nervurada: peso de enchimento tf/m3
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varench         = ctypes.c_double (ench)
        self.m_model.m_eagme.BASME_GEOLAJ_ENCH_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varench))

    def _GetAverageSize (self, idir):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        dnerv           = 0.
        vardnerv        = ctypes.c_double (dnerv)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_DNERV_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (vardnerv))
        dnerv           = vardnerv.value
        return          dnerv

    def _SetAverageSize (self, idir, dnerv):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        vardnerv        = ctypes.c_double (dnerv)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_DNERV_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (vardnerv))

    @property
    def averageSizeX (self):
        """
        Laje nervurada: distância média horizontal entre nervuras cm
        """
        return          self._GetAverageSize (0)

    @averageSizeX.setter
    def averageSizeX (self, dnerv):
        """
        Laje nervurada: distância média horizontal entre nervuras cm
        """
        self._SetAverageSize (0, dnerv)

    @property
    def averageSizeY (self):
        """
        Laje nervurada: distância média vertical entre nervuras cm
        """
        return          self._GetAverageSize (1)

    @averageSizeX.setter
    def averageSizeY (self, dnerv):
        """
        Laje nervurada: distância média vertical entre nervuras cm
        """
        self._SetAverageSize (1, dnerv)

            
    def _GetTopSpacing (self, idir):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        bnervsup           = 0.
        varbnervsup        = ctypes.c_double (bnervsup)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_BNERVSUP_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (varbnervsup))
        bnervsup           = varbnervsup.value
        return          bnervsup

    def _SetTopSpacing (self, idir, bnervsup):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        varbnervsup        = ctypes.c_double (bnervsup)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_BNERVSUP_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (varbnervsup))

    @property
    def topSpacingX (self):
        """
        Laje nervurada: largura superior de nervura horizontal cm
        """
        return          self._GetTopSpacing (0)

    @topSpacingX.setter
    def topSpacingX (self, bnervsup):
        """
        Laje nervurada: largura superior de nervura horizontal cm
        """
        self._SetTopSpacing (0, bnervsup)

    @property
    def topSpacingY (self):
        """
        Laje nervurada: largura superior de nervura vertical cm
        """
        return          self._GetTopSpacing (1)

    @topSpacingY.setter
    def topSpacingY (self, bnervsup):
        """
        Laje nervurada: largura superior de nervura vertical cm
        """
        self._SetTopSpacing (1, bnervsup)
            
    def _GetBottomSpacing (self, idir):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        bnervinf           = 0.
        varbnervinf        = ctypes.c_double (bnervinf)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_BNERVINF_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (varbnervinf))
        bnervinf           = varbnervinf.value
        return          bnervinf

    def _SetBottomSpacing (self, idir, bnervinf):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        varbnervinf        = ctypes.c_double (bnervinf)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_BNERVINF_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (varbnervinf))

    @property
    def bottomSpacingX (self):
        """
        Laje nervurada: largura inferior de nervura horizontal cm
        """
        return          self._GetBottomSpacing (0)

    @bottomSpacingX.setter
    def bottomSpacingX (self, bnervinf):
        """
        Laje nervurada: largura inferior de nervura horizontal cm
        """
        self._SetBottomSpacing (0, bnervinf)

    @property
    def bottomSpacingY (self):
        """
        Laje nervurada: largura inferior de nervura vertical cm
        """
        return          self._GetBottomSpacing (1)

    @bottomSpacingY.setter
    def bottomSpacingY (self, bnervinf):
        """
        Laje nervurada: largura inferior de nervura vertical cm
        """
        self._SetBottomSpacing (1, bnervinf)

    def _GetInertia (self, idir):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        ailaje          = 0.
        varailaje       = ctypes.c_double (ailaje)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_AILAJE_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (varailaje))
        ailaje          = varailaje.value
        return          ailaje

    def _SetInertia (self, idir, ailaje):
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidir         = ctypes.c_int (idir)
        varailaje       = ctypes.c_double (ailaje)
        self.m_model.m_eagme.BASME_GEOLAJ_NERV_AILAJE_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varidir), ctypes.byref (varailaje))

    @property
    def inertiaX (self):
        """
        Laje nervurada: inércia opcional horizontal cm4
        """
        return          self._GetInertia (0)

    @inertiaX.setter
    def inertiaX (self, ailaje):
        """
        Laje nervurada: inércia opcional horizontal cm4
        """
        self._SetInertia (0, ailaje)

    @property
    def inertiaY (self):
        """
        Laje nervurada: inércia opcional vertical cm4
        """
        return          self._GetInertia (1)

    @inertiaY.setter
    def inertiaY (self, ailaje):
        """
        Laje nervurada: inércia opcional vertical cm4
        """
        self._SetInertia (1, ailaje)

    @property
    def formworkVolume (self):
        """
        Laje nervurada: volume cubeta trapezoidal cm3 
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        volforner       = 0.
        varvolforner    = ctypes.c_double (volforner)
        self.m_model.m_eagme.BASME_GEOLAJ_VOLFORNER_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varvolforner))
        volforner       = varvolforner.value
        return          volforner

    @formworkVolume.setter
    def formworkVolume (self, volforner):
        """
        Laje nervurada: volume cubeta trapezoidal cm3 
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varvolforner    = ctypes.c_double (volforner)
        self.m_model.m_eagme.BASME_GEOLAJ_VOLFORNER_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varvolforner))

    @property
    def mouldManufacturer (self):
        """
        Laje nervurada: nome do fabricante de enchimentos
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnomfab       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOLAJ_NOMFAB_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varnomfab))
        nomfab          = varnomfab.value.decode(TQSUtil.CHARSET)
        return          nomfab

    @mouldManufacturer.setter
    def mouldManufacturer (self, nomfab):
        """
        Laje nervurada: nome do fabricante de enchimentos
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnomfab       = ctypes.c_char_p (nomfab.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOLAJ_NOMFAB_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varnomfab))

    @property
    def mouldID (self):
        """
        Laje nervurada: nome do enchimento
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnomenc       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOLAJ_NOMENC_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varnomenc))
        nomenc          = varnomenc.value.decode(TQSUtil.CHARSET)
        return          nomenc

    @mouldID.setter
    def mouldID (self, nomenc):
        """
        Laje nervurada: nome do enchimento
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnomenc       = ctypes.c_char_p (nomenc.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOLAJ_NOMENC_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varnomenc))

    @property
    def latticeTraverseRibEvery (self):
        """
        Laje treliçada: nervura transversal a cada N blocos
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        nervtcada       = 0
        varnervtcada    = ctypes.c_int (nervtcada)
        self.m_model.m_eagme.BASME_GEOLAJ_NERVTCADA_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varnervtcada))
        nervtcada       = varnervtcada.value
        return          nervtcada

    @latticeTraverseRibEvery.setter
    def latticeTraverseRibEvery (self, nervtcada):
        """
        Laje treliçada: nervura transversal a cada N blocos
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnervtcada    = ctypes.c_int (nervtcada)
        self.m_model.m_eagme.BASME_GEOLAJ_NERVTCADA_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varnervtcada))
    @property
    def latticeTraverseWidth (self):
        """
        Laje treliçada: largura da nervura secundária cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        espsec          = 0.
        varespsec       = ctypes.c_double (espsec)
        self.m_model.m_eagme.BASME_GEOLAJ_ESPSEC_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varespsec))
        espsec          = varespsec.value
        return          espsec

    @latticeTraverseWidth.setter
    def latticeTraverseWidth (self, espsec):
        """
        Laje treliçada: largura da nervura secundária cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varespsec       = ctypes.c_double (espsec)
        self.m_model.m_eagme.BASME_GEOLAJ_ESPSEC_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varespsec))
    @property
    def latticeJoistWidth (self):
        """
        Laje treliçada: largura da vigota cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        bvigota         = 0.
        varbvigota      = ctypes.c_double (bvigota)
        self.m_model.m_eagme.BASME_GEOLAJ_BVIGOTA_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varbvigota))
        bvigota         = varbvigota.value
        return          bvigota

    @latticeJoistWidth.setter
    def latticeJoistWidth (self, bvigota):
        """
        Laje treliçada: largura da vigota cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varbvigota      = ctypes.c_double (bvigota)
        self.m_model.m_eagme.BASME_GEOLAJ_BVIGOTA_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varbvigota))
    @property
    def latticeJoistHeight (self):
        """
        Laje treliçada: altura da vigota cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        hvigota         = 0.
        varhvigota      = ctypes.c_double (hvigota)
        self.m_model.m_eagme.BASME_GEOLAJ_HVIGOTA_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varhvigota))
        hvigota         = varhvigota.value
        return          hvigota

    @latticeJoistHeight.setter
    def latticeJoistHeight (self, hvigota):
        """
        Laje treliçada: altura da vigota cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varhvigota      = ctypes.c_double (hvigota)
        self.m_model.m_eagme.BASME_GEOLAJ_HVIGOTA_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varhvigota))
    @property
    def latticeMiniPanel (self):
        """
        Laje treliçada: minipainél (0) Não (1) Sim
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        minipainel      = 0
        varminipainel   = ctypes.c_int (minipainel)
        self.m_model.m_eagme.BASME_GEOLAJ_MINIPAINEL_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varminipainel))
        minipainel      = varminipainel.value
        return          minipainel

    @latticeMiniPanel.setter
    def latticeMiniPanel (self, minipainel):
        """
        Laje treliçada: minipainél (0) Não (1) Sim
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varminipainel   = ctypes.c_int (minipainel)
        self.m_model.m_eagme.BASME_GEOLAJ_MINIPAINEL_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varminipainel))

    @property
    def compositeHeight (self):
        """
        Laje mista: altura do perfil, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        altperf         = 0.
        varaltperf      = ctypes.c_double (altperf)
        self.m_model.m_eagme.BASME_GEOLAJ_ALTPERF_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varaltperf))
        altperf         = varaltperf.value
        return          altperf

    @compositeHeight.setter
    def compositeHeight (self, altperf):
        """
        Laje mista: altura do perfil, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varaltperf      = ctypes.c_double (altperf)
        self.m_model.m_eagme.BASME_GEOLAJ_ALTPERF_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varaltperf))
        
    @property
    def compositeWidth (self):
        """
        Laje mista: largura do perfil, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        basperf         = 0.
        varbasperf      = ctypes.c_double (basperf)
        self.m_model.m_eagme.BASME_GEOLAJ_BASPERF_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varbasperf))
        basperf         = varbasperf.value
        return          basperf

    @compositeWidth.setter
    def compositeWidth (self, basperf):
        """
        Laje mista: largura do perfil, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varbasperf      = ctypes.c_double (basperf)
        self.m_model.m_eagme.BASME_GEOLAJ_BASPERF_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varbasperf))
        
    @property
    def compositeFlange (self):
        """
        Laje mista: largura da aba, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        abaperf         = 0.
        varabaperf      = ctypes.c_double (abaperf)
        self.m_model.m_eagme.BASME_GEOLAJ_ABAPERF_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varabaperf))
        abaperf         = varabaperf.value
        return          abaperf

    @compositeFlange.setter
    def compositeFlange (self, abaperf):
        """
        Laje mista: largura da aba, cm
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varabaperf      = ctypes.c_double (abaperf)
        self.m_model.m_eagme.BASME_GEOLAJ_ABAPERF_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varabaperf))
        
    @property
    def precastRegion (self):
        """
        Pré-moldados: Região construtiva
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        iregiao         = 0
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_GEOLAJ_IREGIAO_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (variregiao))
        iregiao         = variregiao.value
        return          iregiao

    @precastRegion.setter
    def precastRegion (self, iregiao):
        """
        Pré-moldados: Região construtiva
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        variregiao      = ctypes.c_int (iregiao)
        self.m_model.m_eagme.BASME_GEOLAJ_IREGIAO_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (variregiao))
    @property
    def sectionName (self):
        """
        Nome de seção não padrão - catalogada
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varsecaonp      = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOLAJ_SECAONP_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varsecaonp))
        secaonp         = varsecaonp.value.decode(TQSUtil.CHARSET)
        return          secaonp

    @sectionName.setter
    def sectionName (self, secaonp):
        """
        Nome de seção não padrão - catalogada
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varsecaonp      = ctypes.c_char_p (secaonp.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOLAJ_SECAONP_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varsecaonp))
    @property
    def prestressedReinforcement (self):
        """
        Nome da configuração de armaduras protendidas
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidconf       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GEOLAJ_IDCONF_LER (ctypes.byref (vargeolaj),
                            ctypes.byref (varidconf))
        idconf          = varidconf.value.decode(TQSUtil.CHARSET)
        return          idconf

    @prestressedReinforcement.setter
    def prestressedReinforcement (self, idconf):
        """
        Nome da configuração de armaduras protendidas
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varidconf       = ctypes.c_char_p (idconf.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GEOLAJ_IDCONF_DEF (ctypes.byref (vargeolaj),
                            ctypes.byref (varidconf))

    def LoadManufacturer (self, nomfab, nomenc):
        """
        Carrega os dados de moldes de lajes nervuradas. Retorna (0) Se carregou\n
            char *nomfab        <- Nome do fabricante\n
            char *nomenc        <- Nome do enchimento
        """
        vargeolaj       = ctypes.c_void_p (self.m_geolaj)
        varnomfab       = ctypes.c_char_p (nomfab.encode (TQSUtil.CHARSET))
        varnomenc       = ctypes.c_char_p (nomenc.encode (TQSUtil.CHARSET))
        istat           = 0
        varistat        = ctypes.c_int (istat)
        self.m_model.m_eagme.BASME_GEOLAJ_ACHARFAB (ctypes.byref (vargeolaj),
                            varnomfab, varnomenc, ctypes.byref (varistat))
        istat           = varistat.value
        return          istat

#------------------------------------------------------------------------------
#        Dados para discretização de laje por grelha
#
class SlabGrid ():

    def __init__ (self, model, grelaj):
        """
        Dados para discretização de laje por grelha\n
            model       <- Objeto Model() do modelo atual\n
            grelaj      <- Apontador para objeto CGreLaj
        """
        self.m_model    = model
        self.m_grelaj   = grelaj

    @property
    def asGrid (self):
        """
        Discretizar esta laje em grelha (0) Não (1) Sim
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        idiscret        = 0
        varidiscret     = ctypes.c_int (idiscret)
        self.m_model.m_eagme.BASME_GRELAJ_IDISCRET_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (varidiscret))
        idiscret        = varidiscret.value
        return          idiscret

    @asGrid.setter
    def asGrid (self, idiscret):
        """
        Forçar a discretização em laje de escadas (0) Não (1) Sim
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        varidiscret     = ctypes.c_int (idiscret)
        self.m_model.m_eagme.BASME_GRELAJ_IDISCRET_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (varidiscret))

    @property
    def forceAsGrid (self):
        """
        Forçar a discretização em laje de escadas (0) Não (1) Sim
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        idiscresc       = 0
        varidiscresc    = ctypes.c_int (idiscresc)
        self.m_model.m_eagme.BASME_GRELAJ_IDISCRESC_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (varidiscresc))
        idiscresc       = varidiscresc.value
        return          idiscresc

    @forceAsGrid.setter
    def forceAsGrid (self, idiscresc):
        """
        Forçar a discretização em laje de escadas (0) Não (1) Sim
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        varidiscresc    = ctypes.c_int (idiscresc)
        self.m_model.m_eagme.BASME_GRELAJ_IDISCRESC_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (varidiscresc))

    @property
    def plastSupports (self):
        """
        Plastificação (0) conforme critérios (1) Sim (2) Não
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        iplastif        = 0
        variplastif     = ctypes.c_int (iplastif)
        self.m_model.m_eagme.BASME_GRELAJ_IPLASTIF_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (variplastif))
        iplastif        = variplastif.value
        return          iplastif

    @plastSupports.setter
    def plastSupports (self, iplastif):
        """
        Plastificação (0) conforme critérios (1) Sim (2) Não
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        variplastif     = ctypes.c_int (iplastif)
        self.m_model.m_eagme.BASME_GRELAJ_IPLASTIF_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (variplastif))

    @property
    def elstBase (self):
        """
        Laje sobre base elástica (0) Não (1) Sim 
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        ibaseelast      = 0
        varibaseelast   = ctypes.c_int (ibaseelast)
        self.m_model.m_eagme.BASME_GRELAJ_IBASEELAST_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (varibaseelast))
        ibaseelast      = varibaseelast.value
        return          ibaseelast

    @elstBase.setter
    def elstBase (self, ibaseelast):
        """
        Laje sobre base elástica (0) Não (1) Sim 
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        varibaseelast   = ctypes.c_int (ibaseelast)
        self.m_model.m_eagme.BASME_GRELAJ_IBASEELAST_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (varibaseelast))

    @property
    def elstBaseTxSpring (self):
        """
        Mola de translação Tx por nó tf/m
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        cmolbaseelatx   = 0.
        varcmolbaseelatx= ctypes.c_double (cmolbaseelatx)
        self.m_model.m_eagme.BASME_GRELAJ_CMOLBASEELATX_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (varcmolbaseelatx))
        cmolbaseelatx   = varcmolbaseelatx.value
        return          cmolbaseelatx

    @elstBaseTxSpring.setter
    def elstBaseTxSpring (self, cmolbaseelatx):
        """
        Mola de translação Tx por nó tf/m
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        varcmolbaseelatx= ctypes.c_double (cmolbaseelatx)
        self.m_model.m_eagme.BASME_GRELAJ_CMOLBASEELATX_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (varcmolbaseelatx))
    @property
    def elstBaseTySpring (self):
        """
        Mola de translação Ty por nó tf/m
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        cmolbaseelaty   = 0.
        varcmolbaseelaty= ctypes.c_double (cmolbaseelaty)
        self.m_model.m_eagme.BASME_GRELAJ_CMOLBASEELATY_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (varcmolbaseelaty))
        cmolbaseelaty   = varcmolbaseelaty.value
        return          cmolbaseelaty

    @elstBaseTySpring.setter
    def elstBaseTySpring (self, cmolbaseelaty):
        """
        Mola de translação Ty por nó tf/m
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        varcmolbaseelaty= ctypes.c_double (cmolbaseelaty)
        self.m_model.m_eagme.BASME_GRELAJ_CMOLBASEELATY_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (varcmolbaseelaty))
    @property
    def elstBaseTzSpring (self):
        """
        Mola de translação Tz por nó tf/m
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        cmolbaseelatz   = 0.
        varcmolbaseelatz= ctypes.c_double (cmolbaseelatz)
        self.m_model.m_eagme.BASME_GRELAJ_CMOLBASEELATZ_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (varcmolbaseelatz))
        cmolbaseelatz   = varcmolbaseelatz.value
        return          cmolbaseelatz

    @elstBaseTzSpring.setter
    def elstBaseTzSpring (self, cmolbaseelatz):
        """
        Mola de translação Tz por nó tf/m
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        varcmolbaseelatz= ctypes.c_double (cmolbaseelatz)
        self.m_model.m_eagme.BASME_GRELAJ_CMOLBASEELATZ_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (varcmolbaseelatz))
    @property
    def elstBaseGapZPlus (self):
        """
        Gap de translação Z+ (m)
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        gapzp           = 0.
        vargapzp        = ctypes.c_double (gapzp)
        self.m_model.m_eagme.BASME_GRELAJ_GAPZP_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (vargapzp))
        gapzp           = vargapzp.value
        return          gapzp

    @elstBaseGapZPlus.setter
    def elstBaseGapZPlus (self, gapzp):
        """
        Gap de translação Z+ (m)
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        vargapzp        = ctypes.c_double (gapzp)
        self.m_model.m_eagme.BASME_GRELAJ_GAPZP_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (vargapzp))
    @property
    def elstBaseGapZMinus (self):
        """
        Gap de translação Z- (m)
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        gapzn           = 0.
        vargapzn        = ctypes.c_double (gapzn)
        self.m_model.m_eagme.BASME_GRELAJ_GAPZN_LER (ctypes.byref (vargrelaj),
                            ctypes.byref (vargapzn))
        gapzn           = vargapzn.value
        return          gapzn

    @elstBaseGapZMinus.setter
    def elstBaseGapZMinus (self, gapzn):
        """
        Gap de translação Z- (m)
        """
        vargrelaj       = ctypes.c_void_p (self.m_grelaj)
        vargapzn        = ctypes.c_double (gapzn)
        self.m_model.m_eagme.BASME_GRELAJ_GAPZN_DEF (ctypes.byref (vargrelaj),
                            ctypes.byref (vargapzn))
#------------------------------------------------------------------------------
#        Detalhamento de lajes - CDetLaj
#
class SlabDetailing ():

    def __init__ (self, model, detlaj):
        """
        Detalhamento de lajes - CDetLaj\n
            model       <- Objeto Model() do modelo atual\n
            detlaj      <- Apontador para objeto CDetLaj
        """
        self.m_model    = model
        self.m_detlaj   = detlaj

    @property
    def detailable (self):
        """
        Detalhamento da laje (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        idetlajes       = 0
        varidetlajes    = ctypes.c_int (idetlajes)
        self.m_model.m_eagme.BASME_DETLAJ_IDETALHAVEL_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varidetlajes))
        idetlajes       = varidetlajes.value
        return          idetlajes

    @detailable.setter
    def detailable (self, idetlajes):
        """
        Detalhamento da laje (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varidetlajes    = ctypes.c_int (idetlajes)
        self.m_model.m_eagme.BASME_DETLAJ_IDETALHAVEL_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varidetlajes))

    @property
    def rigidDiafragm (self):
        """
        Diafragma rígido (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        idiafrg         = 0
        varidiafrg      = ctypes.c_int (idiafrg)
        self.m_model.m_eagme.BASME_DETLAJ_IDIAFRG_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varidiafrg))
        idiafrg         = varidiafrg.value
        return          idiafrg

    @rigidDiafragm.setter
    def rigidDiafragm (self, idiafrg):
        """
        Diafragma rígido (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varidiafrg      = ctypes.c_int (idiafrg)
        self.m_model.m_eagme.BASME_DETLAJ_IDIAFRG_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varidiafrg))

    @property
    def prestressed (self):
        """
        Protendida (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        iprotendida     = 0
        variprotendida  = ctypes.c_int (iprotendida)
        self.m_model.m_eagme.BASME_DETLAJ_IPROTENDIDA_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (variprotendida))
        iprotendida     = variprotendida.value
        return          iprotendida

    @prestressed.setter
    def prestressed (self, iprotendida):
        """
        Protendida (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        variprotendida  = ctypes.c_int (iprotendida)
        self.m_model.m_eagme.BASME_DETLAJ_IPROTENDIDA_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (variprotendida))

    @property
    def cover (self):
        """
        Cobrimento diferenciado em cm
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        cobrimento      = 0.
        varcobrimento   = ctypes.c_double (cobrimento)
        self.m_model.m_eagme.BASME_DETLAJ_COBRIMENTO_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varcobrimento))
        cobrimento       = varcobrimento.value
        return          cobrimento

    @cover.setter
    def cover (self, cobrimento):
        """
        Cobrimento diferenciado em cm
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varcobrimento   = ctypes.c_double (cobrimento)
        self.m_model.m_eagme.BASME_DETLAJ_COBRIMENTO_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varcobrimento))
    @property
    def exposure (self):
        """
        Em contato com o solo (0) Não (1) Sim (2) Exposta ao ambiente
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        icontsolo       = 0
        varicontsolo    = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_DETLAJ_ICONTSOLO_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varicontsolo))
        icontsolo       = varicontsolo.value
        return          icontsolo

    @exposure.setter
    def exposure (self, icontsolo):
        """
        Em contato com o solo (0) Não (1) Sim (2) Exposta ao ambiente
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varicontsolo    = ctypes.c_int (icontsolo)
        self.m_model.m_eagme.BASME_DETLAJ_ICONTSOLO_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varicontsolo))
    @property
    def cantileverFactor (self):
        """
        Majorador para laje em balanço ou (0.)
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        gaman           = 0.
        vargaman        = ctypes.c_double (gaman)
        self.m_model.m_eagme.BASME_DETLAJ_GAMAN_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (vargaman))
        gaman           = vargaman.value
        return          gaman

    @cantileverFactor.setter
    def cantileverFactor (self, gaman):
        """
        Majorador para laje em balanço ou (0.)
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        vargaman        = ctypes.c_double (gaman)
        self.m_model.m_eagme.BASME_DETLAJ_GAMAN_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (vargaman))
    @property
    def cantilever (self):
        """
        Verificação de dimensões: Balanço (0) Estimado, geometria (1) Não (2) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        ibalanco        = 0
        varibalanco     = ctypes.c_int (ibalanco)
        self.m_model.m_eagme.BASME_DETLAJ_IBALANCO_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varibalanco))
        ibalanco        = varibalanco.value
        return          ibalanco

    @cantilever.setter
    def cantilever (self, ibalanco):
        """
        Verificação de dimensões: Balanço (0) Estimado, geometria (1) Não (2) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varibalanco     = ctypes.c_int (ibalanco)
        self.m_model.m_eagme.BASME_DETLAJ_IBALANCO_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varibalanco))
    @property
    def estimatedSpan (self):
        """
        Vão estimado ou (0.) cm
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        vaoest          = 0.
        varvaoest       = ctypes.c_double (vaoest)
        self.m_model.m_eagme.BASME_DETLAJ_VAOEST_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varvaoest))
        vaoest          = varvaoest.value
        return          vaoest

    @estimatedSpan.setter
    def estimatedSpan (self, vaoest):
        """
        Vão estimado ou (0.) cm
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varvaoest       = ctypes.c_double (vaoest)
        self.m_model.m_eagme.BASME_DETLAJ_VAOEST_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varvaoest))
    @property
    def roofSlab (self):
        """
        Verificação de dimensões: Laje de cobertura (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        icobertura      = 0
        varicobertura   = ctypes.c_int (icobertura)
        self.m_model.m_eagme.BASME_DETLAJ_ICOBERTURA_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varicobertura))
        icobertura      = varicobertura.value
        return          icobertura

    @roofSlab.setter
    def roofSlab (self, icobertura):
        """
        Verificação de dimensões: Laje de cobertura (0) Não (1) Sim
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varicobertura   = ctypes.c_int (icobertura)
        self.m_model.m_eagme.BASME_DETLAJ_ICOBERTURA_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varicobertura))
    @property
    def flatSlab (self):
        """
        Verificação de dimensões: Laje plana (0) Geometria (1) Não (2) Sim (3) C/capitéis
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        iplana          = 0
        variplana       = ctypes.c_int (iplana)
        self.m_model.m_eagme.BASME_DETLAJ_IPLANA_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (variplana))
        iplana          = variplana.value
        return          iplana

    @flatSlab.setter
    def flatSlab (self, iplana):
        """
        Verificação de dimensões: Laje plana (0) Geometria (1) Não (2) Sim (3) C/capitéis
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        variplana       = ctypes.c_int (iplana)
        self.m_model.m_eagme.BASME_DETLAJ_IPLANA_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (variplana))
    @property
    def bottomReinforcement (self):
        """
        Direção de armação: (0) Padrão (1) uma direção (2) duas direções
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        idirarma        = 0
        varidirarma     = ctypes.c_int (idirarma)
        self.m_model.m_eagme.BASME_DETLAJ_IDIRARMA_LER (ctypes.byref (vardetlaj),
                            ctypes.byref (varidirarma))
        idirarma        = varidirarma.value
        return          idirarma

    @bottomReinforcement.setter
    def bottomReinforcement (self, idirarma):
        """
        Direção de armação: (0) Padrão (1) uma direção (2) duas direções
        """
        vardetlaj       = ctypes.c_void_p (self.m_detlaj)
        varidirarma     = ctypes.c_int (idirarma)
        self.m_model.m_eagme.BASME_DETLAJ_IDIRARMA_DEF (ctypes.byref (vardetlaj),
                            ctypes.byref (varidirarma))

#-----------------------------------------------------------------------------
#      Grupo de pré-moldados - Agrupa/define nome para pré-moldado - CGrupoPre
#
class PreCastGroup ():

    def __init__ (self, model, grupopre):
        """
        Detalhamento de lajes - CDetLaj\n
            model       <- Objeto Model() do modelo atual\n
            grupopre    <- Apontador para objeto CGrupoPre
        """
        self.m_model    = model
        self.m_grupopre = grupopre

    @property
    def floorPlanGroup (self):
        """
        Nome do grupo de formas
        """
        vargrupopre     = ctypes.c_void_p (self.m_grupopre)
        vargrupofor     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GRUPOPRE_GRUPOFOR_LER (ctypes.byref (vargrupopre),
                            ctypes.byref (vargrupofor))
        grupofor        = vargrupofor.value.decode(TQSUtil.CHARSET)
        return          grupofor

    @floorPlanGroup.setter
    def floorPlanGroup (self, grupofor):
        """
        Nome do grupo de formas
        """
        vargrupopre       = ctypes.c_void_p (self.m_grupopre)
        vargrupofor       = ctypes.c_char_p (grupofor.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GRUPOPRE_GRUPOFOR_DEF (ctypes.byref (vargrupopre),
                            ctypes.byref (vargrupofor))

    @property
    def floorPlanNumber (self):
        """
        Número único de elemento do grupo
        """
        vargrupopre     = ctypes.c_void_p (self.m_grupopre)
        igrupofor       = 0
        varigrupofor    = ctypes.c_int (igrupofor)
        self.m_model.m_eagme.BASME_GRUPOPRE_IGRUPOFOR_LER (ctypes.byref (vargrupopre),
                            ctypes.byref (varigrupofor))
        igrupofor       = varigrupofor.value
        return          igrupofor

    @floorPlanNumber.setter
    def floorPlanNumber (self, igrupofor):
        """
        Direção de armação: (0) Padrão (1) uma direção (2) duas direções
        """
        vargrupopre     = ctypes.c_void_p (self.m_grupopre)
        varigrupofor    = ctypes.c_int (igrupofor)
        self.m_model.m_eagme.BASME_GRUPOPRE_IGRUPOFOR_DEF (ctypes.byref (vargrupopre),
                            ctypes.byref (varigrupofor))
    @property
    def reinforcementGroup (self):
        """
        Nome do grupo de armação
        """
        vargrupopre     = ctypes.c_void_p (self.m_grupopre)
        vargrupoarm     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_GRUPOPRE_GRUPOARM_LER (ctypes.byref (vargrupopre),
                            ctypes.byref (vargrupoarm))
        grupoarm        = vargrupoarm.value.decode(TQSUtil.CHARSET)
        return          grupoarm

    @reinforcementGroup.setter
    def reinforcementGroup (self, grupoarm):
        """
        Nome do grupo de armação
        """
        vargrupopre       = ctypes.c_void_p (self.m_grupopre)
        vargrupoarm       = ctypes.c_char_p (grupoarm.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_GRUPOPRE_GRUPOARM_DEF (ctypes.byref (vargrupopre),
                            ctypes.byref (vargrupoarm))
    @property
    def beamLoad (self):
        """
        Carga distribuída para vigas com grupo de armação renumerado tf/m
        """
        vargrupopre     = ctypes.c_void_p (self.m_grupopre)
        cdistv          = 0.
        varcdistv       = ctypes.c_double (cdistv)
        self.m_model.m_eagme.BASME_GRUPOPRE_CDISTV_LER (ctypes.byref (vargrupopre),
                            ctypes.byref (varcdistv))
        cdistv          = varcdistv.value
        return          cdistv

    @beamLoad.setter
    def beamLoad (self, cdistv):
        """
        Carga distribuída para vigas com grupo de armação renumerado (string)
        """
        vargrupopre     = ctypes.c_void_p (self.m_grupopre)
        varcdistv       = ctypes.c_double (cdistv)
        self.m_model.m_eagme.BASME_GRUPOPRE_CDISTV_DEF (ctypes.byref (vargrupopre),
                            ctypes.byref (varcdistv))
#-----------------------------------------------------------------------------
#      Variáveis de um tubo de água pluvial de pilar pré-moldado CPreAgua
#
class RainWaterPipe  ():

    def __init__ (self, model, preagua):
        """
        Tubo de água pluvial\n
            model       <- Objeto Model() do modelo atual\n
            preagua     <- Apontador para objeto CPreAgua
        """
        self.m_model    = model
        self.m_preagua  = preagua

    @property
    def pipeDiameter (self):
        """
        Diâmetro do tubo cm
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        diamtub         = 0.
        vardiamtub      = ctypes.c_double (diamtub)
        self.m_model.m_eagme.BASME_PREAGUA_DIAMTUB_LER (ctypes.byref (varpreagua),
                            ctypes.byref (vardiamtub))
        diamtub         = vardiamtub.value
        return          diamtub

    @pipeDiameter.setter
    def pipeDiameter (self, diamtub):
        """
        Diâmetro do tubo cm
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        vardiamtub      = ctypes.c_double (diamtub)
        self.m_model.m_eagme.BASME_PREAGUA_DIAMTUB_DEF (ctypes.byref (varpreagua),
                            ctypes.byref (vardiamtub))

    @property
    def minFunnelWidth (self):
        """
        Diâmetro do funil menor cm
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        diamfunmin      = 0.
        vardiamfunmin   = ctypes.c_double (diamfunmin)
        self.m_model.m_eagme.BASME_PREAGUA_DIAMFUNMIN_LER (ctypes.byref (varpreagua),
                            ctypes.byref (vardiamfunmin))
        diamfunmin      = vardiamfunmin.value
        return          diamfunmin

    @minFunnelWidth.setter
    def minFunnelWidth (self, diamfunmin):
        """
        Diâmetro do funil menor cm
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        vardiamfunmin   = ctypes.c_double (diamfunmin)
        self.m_model.m_eagme.BASME_PREAGUA_DIAMFUNMIN_DEF (ctypes.byref (varpreagua),
                            ctypes.byref (vardiamfunmin))

    @property
    def maxFunnelWidth (self):
        """
        Diâmetro do funil maior cm
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        diamfunmax      = 0.
        vardiamfunmax   = ctypes.c_double (diamfunmax)
        self.m_model.m_eagme.BASME_PREAGUA_DIAMFUNMAX_LER (ctypes.byref (varpreagua),
                            ctypes.byref (vardiamfunmax))
        diamfunmax      = vardiamfunmax.value
        return          diamfunmax

    @maxFunnelWidth.setter
    def maxFunnelWidth (self, diamfunmax):
        """
        Diâmetro do funil maior cm
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        vardiamfunmax   = ctypes.c_double (diamfunmax)
        self.m_model.m_eagme.BASME_PREAGUA_DIAMFUNMAX_DEF (ctypes.byref (varpreagua),
                            ctypes.byref (vardiamfunmax))

    @property
    def rotation (self):
        """
        Ângulo adicional em relação ao pilar em graus
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        angadi          = 0.
        varangadi       = ctypes.c_double (angadi)
        self.m_model.m_eagme.BASME_PREAGUA_ANGADI_LER (ctypes.byref (varpreagua),
                            ctypes.byref (varangadi))
        angadi          = varangadi.value
        return          angadi

    @rotation.setter
    def rotation (self, angadi):
        """
        Ângulo adicional em relação ao pilar em graus
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        varangadi       = ctypes.c_double (angadi)
        self.m_model.m_eagme.BASME_PREAGUA_ANGADI_DEF (ctypes.byref (varpreagua),
                            ctypes.byref (varangadi))

    @property
    def baseDistance (self):
        """
        Distância de saída da base cm (0.) Adota default
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        distagusai      = 0.
        vardistagusai   = ctypes.c_double (distagusai)
        self.m_model.m_eagme.BASME_PREAGUA_DISTAGUSAI_LER (ctypes.byref (varpreagua),
                            ctypes.byref (vardistagusai))
        distagusai      = vardistagusai.value
        return          distagusai

    @baseDistance.setter
    def baseDistance (self, distagusai):
        """
        Distância de saída da base cm (0.) Adota default
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        vardistagusai   = ctypes.c_double (distagusai)
        self.m_model.m_eagme.BASME_PREAGUA_DISTAGUSAI_DEF (ctypes.byref (varpreagua),
                            ctypes.byref (vardistagusai))

    @property
    def tubeIdentification (self):
        """
        Identificador do tubo
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        varidenttube    = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_PREAGUA_IDENT_LER (ctypes.byref (varpreagua),
                            ctypes.byref (varidenttube))
        identtube       = varidenttube.value.decode(TQSUtil.CHARSET)
        return          identtube

    @tubeIdentification.setter
    def tubeIdentification (self, identtube):
        """
        Identificador do tubo
        """
        varpreagua      = ctypes.c_void_p (self.m_preagua)
        varidenttube    = ctypes.c_char_p (identtube.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_PREAGUA_IDENT_DEF (ctypes.byref (varpreagua),
                            ctypes.byref (varidenttube))
#-----------------------------------------------------------------------------
#      Alça de içamento de pilares pré-moldados- CPreAlca
#
class LiftingAnchors  ():

    def __init__ (self, model, prealca):
        """
        Alça de içamento de pilares pré-moldados\n
            model       <- Objeto Model() do modelo atual\n
            prealca     <- Apontador para objeto CPreAlca
        """
        self.m_model    = model
        self.m_prealca  = prealca

    def GetNumLiftingAnchors (self):
        """
        Retorna o número de alças/rebaixos definidos
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        numalcas        = 0
        varnumalcas     = ctypes.c_int (numalcas)
        self.m_model.m_eagme.BASME_PREALCA_NUMALCAS_LER (ctypes.byref (varprealca),
                            ctypes.byref (varnumalcas))
        numalcas        = varnumalcas.value
        return          numalcas

    def GetLiftingRecess (self, ialca):
        """
        Retorna um rebaixo de alça\n
            int ialca   <- 0..GetNumLifting()-1\n
        Retorna:\n
            double dfs  -> Rebaixo de alça cm
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varialca        = ctypes.c_int (ialca)
        dfs             = 0.
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_PREALCA_DFS_LER (ctypes.byref (varprealca),
                            ctypes.byref (varialca), ctypes.byref (vardfs))
        dfs             = vardfs.value
        return          dfs

    def SetLiftingRecess (self, ialca, dfs):
        """
        Define um rebaixo de alça\n
            int ialca   <- 0..GetNumLifting()-1\n
            double dfs  <- Rebaixo de alça cm 
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varialca        = ctypes.c_int (ialca)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_PREALCA_DFS_DEF (ctypes.byref (varprealca),
                            ctypes.byref (varialca), ctypes.byref (vardfs))

    def EnterLiftingRecess (self, dfs):
        """
        Entra um rebaixo de alça no final da lista\n
            double dfs  <- Rebaixo de alça cm 
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_PREALCA_DFS_ENTRAR (ctypes.byref (varprealca),
                            ctypes.byref (vardfs))

    def EraseLiftingAnchor (self, ialca):
        """
        Apaga um rebaixo de alça\n
            int ialca   <- 0..GetNumLifting()-1
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varialca        = ctypes.c_int (ialca)
        self.m_model.m_eagme.BASME_PREALCA_DFS_APAGAR (ctypes.byref (varprealca),
                            ctypes.byref (varialca))

    def SortLiftingAnchors (self):
        """
        Classifica as alças por ordem de rebaixo
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        self.m_model.m_eagme.BASME_PREALCA_CLASSIFICAR (ctypes.byref (varprealca))

    
    @property
    def liftingAnchorId (self):
        """
        Identificador de alças
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varidentalca    = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_PREALCA_IDENT_LER (ctypes.byref (varprealca),
                            ctypes.byref (varidentalca))
        identalca       = varidentalca.value.decode(TQSUtil.CHARSET)
        return          identalca

    @liftingAnchorId.setter
    def liftingAnchorId (self, identalca):
        """
        Identificador de alças
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varidentalca    = ctypes.c_char_p (identalca.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_PREALCA_IDENT_DEF (ctypes.byref (varprealca),
                            ctypes.byref (varidentalca))

    @property
    def liftingPosition (self):
        """
        Alças em posição padrão (0) Não (1) Sim
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        ialcauto        = 0
        varialcauto     = ctypes.c_int (ialcauto)
        self.m_model.m_eagme.BASME_PREALCA_IALCAUTO_LER (ctypes.byref (varprealca),
                            ctypes.byref (varialcauto))
        ialcauto        = varialcauto.value
        return          ialcauto

    @liftingPosition.setter
    def liftingPosition (self, ialcauto):
        """
        Alças em posição padrão (0) Não (1) Sim
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varialcauto     = ctypes.c_int (ialcauto)
        self.m_model.m_eagme.BASME_PREALCA_IALCAUTO_DEF (ctypes.byref (varprealca),
                            ctypes.byref (varialcauto))
    @property
    def liftingAnchorsDefined (self):
        """
        Alças definidas (0) Não (1) Sim
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        ialcadef        = 0
        varialcadef     = ctypes.c_int (ialcadef)
        self.m_model.m_eagme.BASME_PREALCA_IALCADEF_LER (ctypes.byref (varprealca),
                            ctypes.byref (varialcadef))
        ialcadef        = varialcadef.value
        return          ialcadef

    @liftingAnchorsDefined.setter
    def liftingAnchorsDefined (self, ialcadef):
        """
        Alças definidas (0) Não (1) Sim
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varialcadef     = ctypes.c_int (ialcadef)
        self.m_model.m_eagme.BASME_PREALCA_IALCADEF_DEF (ctypes.byref (varprealca),
                            ctypes.byref (varialcadef))

    @property
    def topLiftingAngle (self):
        """
        Ângulo da alça de topo em graus
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        angtopo         = 0.
        varangtopo      = ctypes.c_double (angtopo)
        self.m_model.m_eagme.BASME_PREALCA_ANGTOPO_LER (ctypes.byref (varprealca),
                            ctypes.byref (varangtopo))
        angtopo         = varangtopo.value
        return          angtopo

    @topLiftingAngle.setter
    def topLiftingAngle (self, angtopo):
        """
        Ângulo da alça de topo em graus
        """
        varprealca      = ctypes.c_void_p (self.m_prealca)
        varangtopo      = ctypes.c_double (angtopo)
        self.m_model.m_eagme.BASME_PREALCA_ANGTOPO_DEF (ctypes.byref (varprealca),
                            ctypes.byref (varangtopo))
#-----------------------------------------------------------------------------
#      Furos de içamento de pilares pré-moldados - CPreFur
#
class LiftOpenning  ():

    def __init__ (self, model, prefur):
        """
        Furos de levantamento de pilares pré-moldados\n
            model      <- Objeto Model() do modelo atual\n
            prefur     <- Apontador para objeto CPreFur
        """
        self.m_model    = model
        self.m_prefur   = prefur

    def GetNumLiftingOpennings (self):
        """
        Retorna o número de furos de içamento definidos
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        numfur          = 0
        varnumfur       = ctypes.c_int (numfur)
        self.m_model.m_eagme.BASME_PREFUR_NUMFUR_LER (ctypes.byref (varprefur),
                            ctypes.byref (varnumfur))
        numfur          = varnumfur.value
        return          numfur

    def GetLiftingRecess (self, ifur):
        """
        Retorna um rebaixo de furo\n
            int ifur    <- 0..GetNumLiftingOpennings()-1\n
        Retorna:\n
            double dfs  -> Rebaixo de furo cm
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        varifur         = ctypes.c_int (ifur)
        dfs             = 0.
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_PREFUR_DFS_LER (ctypes.byref (varprefur),
                            ctypes.byref (varifur), ctypes.byref (vardfs))
        dfs             = vardfs.value
        return          dfs

    def SetLiftingRecess (self, ifur, dfs):
        """
        Define um rebaixo de furo\n
            int ifur    <- 0..GetNumLiftingOpennings()-1\n
            double dfs  <- Rebaixo de furo cm 
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        varifur         = ctypes.c_int (ifur)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_PREFUR_DFS_DEF (ctypes.byref (varprefur),
                            ctypes.byref (varifur), ctypes.byref (vardfs))

    def EnterLiftingRecess (self, dfs):
        """
        Entra um rebaixo de furo no final da lista\n
            double dfs  <- Rebaixo de furo cm 
        """
        varprefur      = ctypes.c_void_p (self.m_prefur)
        vardfs          = ctypes.c_double (dfs)
        self.m_model.m_eagme.BASME_PREFUR_DFS_ENTRAR (ctypes.byref (varprefur),
                            ctypes.byref (vardfs))

    def EraseLiftingOpenning (self, ifur):
        """
        Apaga um rebaixo de furo\n
            int ifur    <- 0..GetNumLifting()-1
        """
        varprefur      = ctypes.c_void_p (self.m_prefur)
        varifur        = ctypes.c_int (ifur)
        self.m_model.m_eagme.BASME_PREFUR_DFS_APAGAR (ctypes.byref (varprefur),
                            ctypes.byref (varifur))

    def SortLiftingOpennings (self):
        """
        Classifica as furos por ordem de rebaixo
        """
        varprefur      = ctypes.c_void_p (self.m_prefur)
        self.m_model.m_eagme.BASME_PREFUR_DFS_CLASSIFICAR (ctypes.byref (varprefur))

    
    @property
    def liftingDiameter (self):
        """
        Diâmetro do furo, cm
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        diamfuro        = 0.
        vardiamfuro     = ctypes.c_double (diamfuro)
        self.m_model.m_eagme.BASME_PREFUR_DIAM_LER (ctypes.byref (varprefur),
                            ctypes.byref (vardiamfuro))
        diamfuro        = vardiamfuro.value
        return          diamfuro

    @liftingDiameter.setter
    def liftingDiameter (self, diamfuro):
        """
        Diâmetro do furo, cm
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        vardiamfuro     = ctypes.c_double (diamfuro)
        self.m_model.m_eagme.BASME_PREFUR_DIAM_DEF (ctypes.byref (varprefur),
                            ctypes.byref (vardiamfuro))

    @property
    def liftingEccentricity (self):
        """
        Excentricidade do furo (cm) em relação ao CG do pilar
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        excenfuro       = 0.
        varexcenfuro    = ctypes.c_double (excenfuro)
        self.m_model.m_eagme.BASME_PREFUR_EXCENFURO_LER (ctypes.byref (varprefur),
                            ctypes.byref (varexcenfuro))
        excenfuro       = varexcenfuro.value
        return          excenfuro

    @liftingEccentricity.setter
    def liftingEccentricity (self, excenfuro):
        """
        Excentricidade do furo (cm) em relação ao CG do pilar
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        varexcenfuro     = ctypes.c_double (excenfuro)
        self.m_model.m_eagme.BASME_PREFUR_EXCENFURO_DEF (ctypes.byref (varprefur),
                            ctypes.byref (varexcenfuro))

    @property
    def liftingPosition (self):
        """
        Furos em posição padrão (0) Não (1) Sim
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        ifuroauto       = 0
        varifuroauto    = ctypes.c_int (ifuroauto)
        self.m_model.m_eagme.BASME_PREFUR_IFUROAUTO_LER (ctypes.byref (varprefur),
                            ctypes.byref (varifuroauto))
        ifuroauto       = varifuroauto.value
        return          ifuroauto

    @liftingPosition.setter
    def liftingPosition (self, ifuroauto):
        """
        Furos em posição padrão (0) Não (1) Sim
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        varifuroauto    = ctypes.c_int (ifuroauto)
        self.m_model.m_eagme.BASME_PREFUR_IFUROAUTO_DEF (ctypes.byref (varprefur),
                            ctypes.byref (varifuroauto))

    @property
    def liftOpenningDefined (self):
        """
        Furos de içamento definidos (0) Não (1) Sim
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        ifurodef        = 0
        varifurodef     = ctypes.c_int (ifurodef)
        self.m_model.m_eagme.BASME_PREFUR_IFURODEF_LER (ctypes.byref (varprefur),
                            ctypes.byref (varifurodef))
        ifurodef        = varifurodef.value
        return          ifurodef

    @liftOpenningDefined.setter
    def liftOpenningDefined (self, ifurodef):
        """
        Furos de içamento definidos (0) Não (1) Sim
        """
        varprefur       = ctypes.c_void_p (self.m_prefur)
        varifurodef     = ctypes.c_int (ifurodef)
        self.m_model.m_eagme.BASME_PREFUR_IFURODEF_DEF (ctypes.byref (varprefur),
                            ctypes.byref (varifurodef))

#------------------------------------------------------------------------------
#        Condições de contorno de pilares - CContPil
#
class ColumnBoundaryCond ():

    def __init__ (self, model, contpil):
        """
        Condições de contorno de pilares\n
            model       <- Objeto Model() do modelo atual\n
            contpil     <- Apontador para objeto CContPil
        """
        self.m_model    = model
        self.m_contpil  = contpil

    @property
    def bearingModel (self):
        """
        Tipo de apoio em grelha COLUMNBEARING_xxxxx
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        iapogre         = 0
        variapogre      = ctypes.c_int (iapogre)
        self.m_model.m_eagme.BASME_CONTPIL_IAPOGRE_LER (ctypes.byref (varcontpil),
                            ctypes.byref (variapogre))
        iapogre         = variapogre.value
        return          iapogre

    @bearingModel.setter
    def bearingModel (self, iapogre):
        """
        Tipo de apoio em grelha COLUMNBEARING_xxxxx
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        variapogre      = ctypes.c_int (iapogre)
        self.m_model.m_eagme.BASME_CONTPIL_IAPOGRE_DEF (ctypes.byref (varcontpil),
                            ctypes.byref (variapogre))

    def GetSpringValue (self, icoef):
        """
        Retorna o valor da mola de rotação ou translação do apoio em pilar nas grelhas\n
            int icoef           <- Coeficiente COLUMNSPRING_xxxx\n
        Retorna:\n
            double coefmola     -> Coeficiente de mola em tfm/rad (rotação) ou tf/m (translação)
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        varicoef        = ctypes.c_int (icoef)
        coefmola        = 0.
        varcoefmola     = ctypes.c_double (coefmola)
        self.m_model.m_eagme.BASME_CONTPIL_COEFMOLA_LER (ctypes.byref (varcontpil),
                            ctypes.byref (varicoef), ctypes.byref (varcoefmola))
        coefmola        = varcoefmola.value
        return          coefmola

    def SetSpringValue (self, icoef, coefmola):
        """
        Define o valor da mola de rotação ou translação do apoio em pilar nas grelhas\n
            int icoef           <- Coeficiente COLUMNSPRING_xxxx\n
            double coefmola     <- Coeficiente de mola em tfm/rad (rotação) ou tf/m (translação)
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        varicoef        = ctypes.c_int (icoef)
        varcoefmola     = ctypes.c_double (coefmola)
        self.m_model.m_eagme.BASME_CONTPIL_COEFMOLA_DEF (ctypes.byref (varcontpil),
                            ctypes.byref (varicoef), ctypes.byref (varcoefmola))

    @property
    def madatoryPunchingShear (self):
        """
        Armadura de punção obrigatória (0) Não (1) Sim
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        ipuncaoobrig    = 0
        varipuncaoobrig = ctypes.c_int (ipuncaoobrig)
        self.m_model.m_eagme.BASME_CONTPIL_IPUNCAOOBRIG_LER (ctypes.byref (varcontpil),
                            ctypes.byref (varipuncaoobrig))
        ipuncaoobrig    = varipuncaoobrig.value
        return          ipuncaoobrig

    @madatoryPunchingShear.setter
    def madatoryPunchingShear (self, ipuncaoobrig):
        """
        Armadura de punção obrigatória (0) Não (1) Sim
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        varipuncaoobrig = ctypes.c_int (ipuncaoobrig)
        self.m_model.m_eagme.BASME_CONTPIL_IPUNCAOOBRIG_DEF (ctypes.byref (varcontpil),
                            ctypes.byref (varipuncaoobrig))
    @property
    def shearWallDiscretization (self):
        """
        Pilar parede discretizado (0) Não (1) Sim, estimado ou discretizado
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        idiscretmodel   = 0
        varidiscretmodel= ctypes.c_int (idiscretmodel)
        self.m_model.m_eagme.BASME_CONTPIL_IDISCRETMODEL_LER (ctypes.byref (varcontpil),
                            ctypes.byref (varidiscretmodel))
        idiscretmodel   = varidiscretmodel.value
        return          idiscretmodel

    @shearWallDiscretization.setter
    def shearWallDiscretization (self, idiscretmodel):
        """
        Pilar parede discretizado (0) Não (1) Sim, estimado ou discretizado
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        varidiscretmodel= ctypes.c_int (idiscretmodel)
        self.m_model.m_eagme.BASME_CONTPIL_IDISCRETMODEL_DEF (ctypes.byref (varcontpil),
                            ctypes.byref (varidiscretmodel))
    def GetGap (self, igap):
        """
        Valor do gap (m) de restrição de apoio\n
            igap        <- Gap TIPO COLUMNCOIL_IGAP_xxxx\n
        Retorna:\n
            gap         -> Valor do gap (m)
        """
        varcontpil      = ctypes.c_void_p (self.m_contpil)
        varigap         = ctypes.c_int (igap)
        gap             = 0.
        vargap          = ctypes.c_double (gap)
        self.m_model.m_eagme.BASME_CONTPIL_GAP_LER (ctypes.byref (varcontpil),
                            ctypes.byref (varigap), ctypes.byref (vargap))
        gap             = vargap.value
        return          gap

    def SetGap (self, igap, gap):
        """
        Valor do gap (m) de restrição de apoio\n
            igap        <- Gap TIPO COLUMNCOIL_IGAP_xxxx\n
            gap         <- Valor do gap (m)
        """
        varcontpil       = ctypes.c_void_p (self.m_contpil)
        varigap         = ctypes.c_int (igap)
        vargap          = ctypes.c_double (gap)
        self.m_model.m_eagme.BASME_CONTPIL_GAP_DEF (ctypes.byref (varcontpil),
                            ctypes.byref (varigap), ctypes.byref (vargap))

#------------------------------------------------------------------------------
#        Dados de Bloco de transição - CBlocoTrans
#
class ColumnTransferBlock ():

    def __init__ (self, model, blocotrans):
        """
        Blocos de transição de pilares\n
            model       <- Objeto Model() do modelo atual\n
            blocotrans  <- Apontador para objeto CBlocoTrans
        """
        self.m_model      = model
        self.m_blocotrans = blocotrans
#------------------------------------------------------------------------------
#       Objeto de identificação de objetos CIdentElem
#
class SMObjectIdent ():

    def __init__ (self, model, ident):
        """
        Classe de identificação de objeto\n
            model       <- Objeto Model() do modelo atual\n
            ident       <- Apontador para objeto CIdent
        """
        self.m_model    = model
        self.m_ident    = ident

    @property
    def objectNumber (self):
        """
        Número do elemento
        """
        varident        = ctypes.c_void_p (self.m_ident)
        numelem         = 0
        varnumelem      = ctypes.c_int (numelem)
        self.m_model.m_eagme.BASME_IDENT_NUMELEM_LER (ctypes.byref (varident),
                            ctypes.byref (varnumelem))
        numelem         = varnumelem.value
        return          numelem

    @objectNumber.setter
    def objectNumber (self, numelem):
        """
        Número do elemento
        """
        varident        = ctypes.c_void_p (self.m_ident)
        varnumelem      = ctypes.c_int (numelem)
        self.m_model.m_eagme.BASME_IDENT_NUMELEM_DEF (ctypes.byref (varident),
                            ctypes.byref (varnumelem))

    @property
    def objectTitle (self):
        """
        Título alfanumérico ou "" se não definido
        """
        varident        = ctypes.c_void_p (self.m_ident)
        vartitulo       = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_IDENT_TITULO_LER (ctypes.byref (varident),
                            vartitulo)
        titulo          = vartitulo.value.decode(TQSUtil.CHARSET)
        return         titulo

    @objectTitle.setter
    def objectTitle (self, titulo):
        """
        Título alfanumérico ou "" se não definido
        """
        varident        = ctypes.c_void_p (self.m_ident)
        vartitulo       = ctypes.c_char_p (titulo.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_IDENT_TITULO_DEF (ctypes.byref (varident),
                            vartitulo)
    @property
    def textPosition (self):
        """
        Retorna objeto TextPosition() com posição de texto editável
        """
        varident        = ctypes.c_void_p (self.m_ident)
        postex          = None
        varpostex       = ctypes.c_void_p (postex)
        self.m_model.m_eagme.BASME_IDENT_POSTEX_LER (ctypes.byref (varident), 
                            ctypes.byref (varpostex))
        postex          = varpostex.value
        textposition    = TextPosition (self.m_model, postex)
        return          textposition


    @property
    def renumerable (self):
        """
        Elemento renumeravel (0) Não (1) Sim
        """
        varident        = ctypes.c_void_p (self.m_ident)
        irenumeravel    = 0
        varirenumeravel = ctypes.c_int (irenumeravel)
        self.m_model.m_eagme.BASME_IDENT_IRENUMERAVEL_LER (ctypes.byref (varident),
                            ctypes.byref (varirenumeravel))
        irenumeravel    = varirenumeravel.value
        return          irenumeravel

    @renumerable.setter
    def renumerable (self, irenumeravel):
        """
        Elemento renumeravel (0) Não (1) Sim
        """
        varident        = ctypes.c_void_p (self.m_ident)
        varirenumeravel = ctypes.c_int (irenumeravel)
        self.m_model.m_eagme.BASME_IDENT_IRENUMERAVEL_DEF (ctypes.byref (varident),
                            ctypes.byref (varirenumeravel))

#-----------------------------------------------------------------------------
#      Objeto de eixos automáticos - CEixAut
#
class AutoAxis ():

    def __init__ (self, model, eixaut):
        """
        Classe p/geração automática de eixos\n
            model       <- Objeto Model() do modelo atual\n
            eixaut      <- Apontador para objeto CEixAut
        """
        self.m_model    = model
        self.m_eixaut   = eixaut

#-----------------------------------------------------------------------------
#       Mísula em viga - somente visual -  CMisVig
#
class VariableSection ():

    def __init__ (self, model, misvig):
        """
        Classe com dados de mísula/seção variável de viga\n
            model       <- Objeto Model() do modelo atual\n
            misvig      <- Apontador para objeto CMisVig
        """
        self.m_model    = model
        self.m_misvig   = misvig

    @property
    def corbelDefined (self):
        """
        Mísula definida (0) Não (1) Sim
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        idefin          = 0
        varidefin       = ctypes.c_int (idefin)
        self.m_model.m_eagme.BASME_MISVIG_IDEFIN_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varidefin))
        idefin          = varidefin.value
        return          idefin

    @corbelDefined.setter
    def corbelDefined (self, idefin):
        """
        Mísula definida (0) Não (1) Sim
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varidefin       = ctypes.c_int (idefin)
        self.m_model.m_eagme.BASME_MISVIG_IDEFIN_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varidefin))

    @property
    def startBottomHeight (self):
        """
        Mísula: Altura inferior inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hinici          = 0.
        varhinici       = ctypes.c_double (hinici)
        self.m_model.m_eagme.BASME_MISVIG_HINICI_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhinici))
        hinici          = varhinici.value
        return          hinici

    @startBottomHeight.setter
    def startBottomHeight (self, hinici):
        """
        Mísula: Altura inferior inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhinici       = ctypes.c_double (hinici)
        self.m_model.m_eagme.BASME_MISVIG_HINICI_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhinici))

    @property
    def endBottomHeight (self):
        """
        Mísula: Altura inferior final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hfinal          = 0.
        varhfinal       = ctypes.c_double (hfinal)
        self.m_model.m_eagme.BASME_MISVIG_HFINAL_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinal))
        hfinal          = varhfinal.value
        return          hfinal

    @endBottomHeight.setter
    def endBottomHeight (self, hfinal):
        """
        Mísula: Altura inferior final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhfinal       = ctypes.c_double (hfinal)
        self.m_model.m_eagme.BASME_MISVIG_HFINAL_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinal))

    @property
    def startTopHeight (self):
        """
        Mísula: Altura superior inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hinicis         = 0.
        varhinicis      = ctypes.c_double (hinicis)
        self.m_model.m_eagme.BASME_MISVIG_HINICIS_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhinicis))
        hinicis         = varhinicis.value
        return          hinicis

    @startTopHeight.setter
    def startTopHeight (self, hinicis):
        """
        Mísula: Altura superior inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhinicis      = ctypes.c_double (hinicis)
        self.m_model.m_eagme.BASME_MISVIG_HINICIS_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhinicis))

    @property
    def endTopHeight (self):
        """
        Mísula: Altura superior final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hfinals         = 0.
        varhfinals      = ctypes.c_double (hfinals)
        self.m_model.m_eagme.BASME_MISVIG_HFINALS_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinals))
        hfinals         = varhfinals.value
        return          hfinals

    @endTopHeight.setter
    def endTopHeight (self, hfinals):
        """
        Mísula: Altura superior final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhfinals      = ctypes.c_double (hfinals)
        self.m_model.m_eagme.BASME_MISVIG_HFINALS_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinals))

    @property
    def startLeftWidth (self):
        """
        Mísula: Largura esquerda inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hinicie         = 0.
        varhinicie      = ctypes.c_double (hinicie)
        self.m_model.m_eagme.BASME_MISVIG_HINICIE_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhinicie))
        hinicie         = varhinicie.value
        return          hinicie

    @startLeftWidth.setter
    def startLeftWidth (self, hinicie):
        """
        Mísula: Largura esquerda inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhinicie      = ctypes.c_double (hinicie)
        self.m_model.m_eagme.BASME_MISVIG_HINICIE_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhinicie))

    @property
    def endLeftWidth (self):
        """
        Mísula: Largura esquerda final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hfinale         = 0.
        varhfinale      = ctypes.c_double (hfinale)
        self.m_model.m_eagme.BASME_MISVIG_HFINALE_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinale))
        hfinale         = varhfinale.value
        return          hfinale

    @endLeftWidth.setter
    def endLeftWidth (self, hfinale):
        """
        Mísula: Largura esquerda final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhfinale      = ctypes.c_double (hfinale)
        self.m_model.m_eagme.BASME_MISVIG_HFINALE_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinale))

    @property
    def startRightWidth (self):
        """
        Mísula: Largura direita inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hinicid         = 0.
        varhinicid      = ctypes.c_double (hinicid)
        self.m_model.m_eagme.BASME_MISVIG_HINICID_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhinicid))
        hinicid         = varhinicid.value
        return          hinicid

    @startRightWidth.setter
    def startRightWidth (self, hinicid):
        """
        Mísula: Largura direita inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhinicid      = ctypes.c_double (hinicid)
        self.m_model.m_eagme.BASME_MISVIG_HINICID_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhinicid))

    @property
    def endRightWidth (self):
        """
        Mísula: Largura direita final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        hfinald         = 0.
        varhfinald      = ctypes.c_double (hfinald)
        self.m_model.m_eagme.BASME_MISVIG_HFINALD_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinald))
        hfinald         = varhfinald.value
        return          hfinald

    @endRightWidth.setter
    def endRightWidth (self, hfinald):
        """
        Mísula: Largura direita final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varhfinald      = ctypes.c_double (hfinald)
        self.m_model.m_eagme.BASME_MISVIG_HFINALD_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varhfinald))

    @property
    def variableSectionDefined (self):
        """
        Seção variável definida (0) Não (1) Sim
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        isecvr          = 0
        varisecvr       = ctypes.c_int (isecvr)
        self.m_model.m_eagme.BASME_MISVIG_ISECVR_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varisecvr))
        isecvr          = varisecvr.value
        return          isecvr

    @variableSectionDefined.setter
    def variableSectionDefined (self, isecvr):
        """
        Seção variável definida (0) Não (1) Sim
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varisecvr       = ctypes.c_int (isecvr)
        self.m_model.m_eagme.BASME_MISVIG_ISECVR_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varisecvr))

    @property
    def startWidth (self):
        """
        Seção variável: Largura inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        basini          = 0.
        varbasini       = ctypes.c_double (basini)
        self.m_model.m_eagme.BASME_MISVIG_BASINI_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varbasini))
        basini          = varbasini.value
        return          basini

    @startWidth.setter
    def startWidth (self, basini):
        """
        Seção variável: Largura inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varbasini       = ctypes.c_double (basini)
        self.m_model.m_eagme.BASME_MISVIG_BASINI_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varbasini))

    @property
    def startHeight (self):
        """
        Seção variável: Altura inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        altini          = 0.
        varaltini       = ctypes.c_double (altini)
        self.m_model.m_eagme.BASME_MISVIG_ALTINI_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varaltini))
        altini          = varaltini.value
        return          altini

    @startHeight.setter
    def startHeight (self, altini):
        """
        Seção variável: Altura inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varaltini       = ctypes.c_double (altini)
        self.m_model.m_eagme.BASME_MISVIG_ALTINI_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varaltini))

    @property
    def startRecess (self):
        """
        Seção variável: Rebaixo inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        dfsini          = 0.
        vardfsini       = ctypes.c_double (dfsini)
        self.m_model.m_eagme.BASME_MISVIG_DFSINI_LER (ctypes.byref (varmisvig),
                            ctypes.byref (vardfsini))
        dfsini          = vardfsini.value
        return          dfsini

    @startRecess.setter
    def startRecess (self, dfsini):
        """
        Seção variável: Rebaixo inicial cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        vardfsini       = ctypes.c_double (dfsini)
        self.m_model.m_eagme.BASME_MISVIG_DFSINI_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (vardfsini))

    @property
    def endWidth (self):
        """
        Seção variável: Largura final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        basfin          = 0.
        varbasfin       = ctypes.c_double (basfin)
        self.m_model.m_eagme.BASME_MISVIG_BASFIN_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varbasfin))
        basfin          = varbasfin.value
        return          basfin

    @endWidth.setter
    def endWidth (self, basfin):
        """
        Seção variável: Largura final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varbasfin       = ctypes.c_double (basfin)
        self.m_model.m_eagme.BASME_MISVIG_BASFIN_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varbasfin))

    @property
    def endHeight (self):
        """
        Seção variável: Altura final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        altfin          = 0.
        varaltfin       = ctypes.c_double (altfin)
        self.m_model.m_eagme.BASME_MISVIG_ALTFIN_LER (ctypes.byref (varmisvig),
                            ctypes.byref (varaltfin))
        altfin          = varaltfin.value
        return          altfin

    @endHeight.setter
    def endHeight (self, altfin):
        """
        Seção variável: Altura final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        varaltfin       = ctypes.c_double (altfin)
        self.m_model.m_eagme.BASME_MISVIG_ALTFIN_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (varaltfin))

    @property
    def endRecess (self):
        """
        Seção variável: Rebaixo final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        dfsfin          = 0.
        vardfsfin       = ctypes.c_double (dfsfin)
        self.m_model.m_eagme.BASME_MISVIG_DFSFIN_LER (ctypes.byref (varmisvig),
                            ctypes.byref (vardfsfin))
        dfsfin          = vardfsfin.value
        return          dfsfin

    @endRecess.setter
    def endRecess (self, dfsfin):
        """
        Seção variável: Rebaixo final cm
        """
        varmisvig       = ctypes.c_void_p (self.m_misvig)
        vardfsfin       = ctypes.c_double (dfsfin)
        self.m_model.m_eagme.BASME_MISVIG_DFSFIN_DEF (ctypes.byref (varmisvig),
                            ctypes.byref (vardfsfin))

#-----------------------------------------------------------------------------
#       Dados de vigas pré-moldadas - CPreVig
#
class BeamPrecastData ():

    def __init__ (self, model, previg):
        """
        Classe com dados de mísula/seção variável de viga\n
            model       <- Objeto Model() do modelo atual\n
            previg      <- Apontador para objeto CPreVig
        """
        self.m_model    = model
        self.m_previg   = previg

#-----------------------------------------------------------------------------
#       Dados de vigas - seção metálica - CMetVig
#
class BeamMetalSection ():

    def __init__ (self, model, metvig):
        """
        Classe com dados de mísula/seção variável de viga\n
            model       <- Objeto Model() do modelo atual\n
            metvig      <- Apontador para objeto CMetVig
        """
        self.m_model    = model
        self.m_metvig   = metvig

#-----------------------------------------------------------------------------
#       Posição de texto editável - CPosTex
#
class TextPosition ():

    def __init__ (self, model, postex):
        """
        Classe com dados de \n
            model       <- Objeto Model() do modelo atual\n
            postex      <- Apontador para objeto CPosTex
        """
        self.m_model    = model
        self.m_postex   = postex
#-----------------------------------------------------------------------------
#       Objeto de viga
#
class Beam (SMObject):

    def __init__ (self, model, viga):
        """
        Criação de uma viga\n
            model       <- Objeto Model() do modelo atual\n
            viga        <- Objeto CVigas do Modelador
        """
        self.m_model    = model
        self.m_viga     = viga
        super().__init__(model, self.m_viga)

    @property
    def beamIdent (self):
        """
        Identificação da viga
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        identvig        = None
        varidentvig     = ctypes.c_void_p (identvig)
        self.m_model.m_eagme.BASME_VIGAS_IDENTVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varidentvig))
        identvig        = varidentvig.value
        beamident       = SMObjectIdent (self.m_model, identvig)
        return          beamident

    def NumNodes (self):
        """
        Número de nós de uma viga (objetos BeamNode)
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        numnos          = 0
        varnumnos       = ctypes.c_int (numnos)
        self.m_model.m_eagme.BASME_VIGAS_NOVIG_NUMNOS (ctypes.byref (varviga),
                            ctypes.byref (varnumnos))
        numnos          = varnumnos.value
        return          numnos


    def GetBeamNode (self, ino):
        """
        Retorna um nó da viga na forma de um objeto BeamNode
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        novig           = None
        varnovig        = ctypes.c_void_p (novig)
        self.m_model.m_eagme.BASME_VIGAS_NOVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (varnovig))
        novig           = varnovig.value
        return          BeamNode (self.m_model, novig)

    def GetBeamGeometry (self):
        """
        Geometria de viga - válida nos trechos sem definição específica (SetSegmentBeamGeometryDefined)
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        geovig          = None
        vargeovig       = ctypes.c_void_p (geovig)
        self.m_model.m_eagme.BASME_VIGAS_GEOVIG_GERAL_LER (ctypes.byref (varviga),
                            ctypes.byref (vargeovig))
        geovig          = vargeovig.value
        beamgeometry    = BeamGeometry (self.m_model, geovig)
        return          beamgeometry

    def GetSegmentBeamGeometry (self, ino):
        """
        Geometria de viga - do trecho ou geral (conforme SetSegmentBeamGeometryDefined)
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        geovig          = None
        vargeovig       = ctypes.c_void_p (geovig)
        self.m_model.m_eagme.BASME_VIGAS_GEOVIG_TRECHO_LER (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (vargeovig))
        geovig          = vargeovig.value
        beamgeometry    = BeamGeometry (self.m_model, geovig)
        return          beamgeometry

    def GetSegmentBeamGeometryDefined (self, ino):
        """
        Retorna (1) se a geometria do trecho ino é específica ou (0) se é geral
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        idefgeovig      = 0
        varidefgeovig   = ctypes.c_int (idefgeovig)
        self.m_model.m_eagme.BASME_VIGAS_IDEFGEOVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (varidefgeovig))
        idefgeovig       = varidefgeovig.value
        return          idefgeovig

    def SetSegmentBeamGeometryDefined (self, ino, idefgeovig):
        """
        Define (1) se a geometria do trecho ino é específica ou (0) se é geral
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        varidefgeovig   = ctypes.c_int (idefgeovig)
        self.m_model.m_eagme.BASME_VIGAS_IDEFGEOVIG_DEF (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (varidefgeovig))

    def GetBeamInertia (self):
        """
        Inércia de viga - válida nos trechos sem definição específica (SetSegmentBeamInertiaDefined)
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        inervig         = None
        varinervig      = ctypes.c_void_p (inervig)
        self.m_model.m_eagme.BASME_VIGAS_INERVIG_GERAL_LER (ctypes.byref (varviga),
                            ctypes.byref (varinervig))
        inervig         = varinervig.value
        beaminertia     = BeamInertia (self.m_model, inervig)
        return          beaminertia

    def GetSegmentBeamInertia (self, ino):
        """
        Inércia de viga - Do trecho ou geral, conforme SetSegmentBeamInertiaDefined
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        inervig         = None
        varinervig      = ctypes.c_void_p (inervig)
        self.m_model.m_eagme.BASME_VIGAS_INERVIG_TRECHO_LER (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (varinervig))
        inervig         = varinervig.value
        beaminertia     = BeamInertia (self.m_model, inervig)
        return          beaminertia

    def GetSegmentBeamInertiaDefined (self, ino):
        """
        Retorna (1) se a inércia do trecho ino é específica ou (0) se é geral
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        idefinervig     = 0
        varidefinervig  = ctypes.c_int (idefinervig)
        self.m_model.m_eagme.BASME_VIGAS_IDEFINERVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (varidefinervig))
        varidefinervig  = varidefinervig.value
        return          varidefinervig

    def SetSegmentBeamInertiaDefined (self, ino, idefinervig):
        """
        Define (1) se a inércia do trecho ino é específica ou (0) se é geral
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varino          = ctypes.c_int (ino)
        varidefinervig  = ctypes.c_int (idefinervig)
        self.m_model.m_eagme.BASME_VIGAS_IDEFINERVIG_DEF (ctypes.byref (varviga),
                            ctypes.byref (varino), ctypes.byref (varidefinervig))

    @property
    def beamBond (self):
        """
        Vinculações e outros dados de viga
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        vincvig         = None
        varvincvig      = ctypes.c_void_p (vincvig)
        self.m_model.m_eagme.BASME_VIGAS_VINCVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varvincvig))
        vincvig         = varvincvig.value
        beambond        = BeamBond (self.m_model, vincvig)
        return          beambond

    @property
    def beamInsertion (self):
        """
        Dados de inserção de vigas
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        insvig          = None
        varinsvig       = ctypes.c_void_p (insvig)
        self.m_model.m_eagme.BASME_VIGAS_VINCVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varinsvig))
        insvig          = varinsvig.value
        beaminsertion   = BeamInsertion (self.m_model, insvig)
        return          beaminsertion

    def GetLoad (self, floor):
        """
        Retorna objeto Load () com carga distribuída em toda a viga\n
            floor       <- Objeto Floor, com dados da planta atual
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_VIGAS_CARGAVIG_LER (ctypes.byref (varviga),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, floor, carga)
        return          loadx

    @property
    def temperShrink (self):
        """
        Temperatura / retração de vigas
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        tempretvig      = None
        vartempretvig   = ctypes.c_void_p (tempretvig)
        self.m_model.m_eagme.BASME_VIGAS_TEMPRET_LER (ctypes.byref (varviga),
                            ctypes.byref (vartempretvig))
        tempretvig      = vartempretvig.value
        tempershrink    = TemperatureShrink (self.m_model, tempretvig)
        return          tempershrink
    
    @property
    def beamDetailing (self):
        """
        Detalhamento de vigas
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        detvig          = None
        vardetvig       = ctypes.c_void_p (detvig)
        self.m_model.m_eagme.BASME_VIGAS_TEMPRET_LER (ctypes.byref (varviga),
                            ctypes.byref (vardetvig))
        detvig          = vardetvig.value
        beamdetailing   = BeamDetailing (self.m_model, detvig)
        return          beamdetailing

    
    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_VIGAS_IPISOAUX_LER (ctypes.byref (varviga),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_VIGAS_IPISOAUX_DEF (ctypes.byref (varviga),
                            ctypes.byref (varipisoaux))

    @property
    def userAttrib (self):
        """
        Atributos de usuário
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        self.m_model.m_eagme.BASME_VIGAS_USRATRIB_LER (ctypes.byref (varviga),
                            ctypes.byref (varusratrib))
        usratrib        = varusratrib.value
        userattrib      = UserAttrib (self.m_model, usratrib)
        return          userattrib

    @property
    def beamExport (self):
        """
        (1) Se viga exportável para o 3D/BIM
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        iexportavel     = 0
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_VIGAS_IEXPORTAVEL_LER (ctypes.byref (varviga),
                            ctypes.byref (variexportavel))
        iexportavel     = variexportavel.value
        return          iexportavel

    @beamExport.setter
    def beamExport (self, iexportavel):
        """
        (1) Se viga exportável para o 3D/BIM
        """
        varviga         = ctypes.c_void_p (self.m_viga)
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_VIGAS_IEXPORTAVEL_DEF (ctypes.byref (varviga),
                            ctypes.byref (variexportavel))

#-----------------------------------------------------------------------------
#       Nó de viga - Objeto CNoVig com dados de um nó/trecho de viga
#
class BeamNode ():

    def __init__ (self, model, novig):
        """
        Classe com dados de mísula/seção variável de viga\n
            model       <- Objeto Model() do modelo atual\n
            novig       <- Apontador para objeto CNoVig
        """
        self.m_model    = model
        self.m_novig    = novig

    @property
    def nodeX (self):
        """
        X do nó da viga
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        xno             = 0.
        varxno          = ctypes.c_double (xno)
        self.m_model.m_eagme.BASME_NOVIG_XYNO_LERX (ctypes.byref (varnovig),
                            ctypes.byref (varxno))
        xno             = varxno.value
        return          xno

    @nodeX.setter
    def nodeX (self, xno):
        """
        X do nó da viga
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        varxno          = ctypes.c_double (xno)
        self.m_model.m_eagme.BASME_NOVIG_XYNO_DEFX (ctypes.byref (varnovig),
                            ctypes.byref (varxno))

    @property
    def nodeY (self):
        """
        Y do nó da viga
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        yno             = 0.
        varyno          = ctypes.c_double (yno)
        self.m_model.m_eagme.BASME_NOVIG_XYNO_LERY (ctypes.byref (varnovig),
                            ctypes.byref (varyno))
        yno             = varyno.value
        return          yno

    @nodeY.setter
    def nodeY (self, yno):
        """
        Y do nó da viga
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        varyno          = ctypes.c_double (yno)
        self.m_model.m_eagme.BASME_NOVIG_XYNO_DEFY (ctypes.byref (varnovig),
                            ctypes.byref (varyno))

    @property
    def crossingType (self):
        """
        Tipo de vinculação do nó da viga BEAMCROSSING_xxxx
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        ivinc           = 0
        varivinc        = ctypes.c_int (ivinc)
        self.m_model.m_eagme.BASME_NOVIG_IVINC_LER (ctypes.byref (varnovig),
                            ctypes.byref (varivinc))
        ivinc           = varivinc.value
        return          ivinc

    @crossingType.setter
    def crossingType (self, ivinc):
        """
        Tipo de vinculação do nó da viga BEAMCROSSING_xxxx
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        varivinc        = ctypes.c_int (ivinc)
        self.m_model.m_eagme.BASME_NOVIG_IVINC_DEF (ctypes.byref (varnovig),
                            ctypes.byref (varivinc))

    def GetSlabConnection (self, idireito):
        """
        Retorna engastamento de um lado da viga com a laje\n
            int    idireito     <- (0) Esquerdo (1) Direito\n
        Retorna:\n
            int    iengast      -> Tipo de engaste BEAMCONNECTION_XXX\n
            double fatengast	-> Fator de engaste 0..1 para iengast == (BEAMCONNECTION_FATEMGS)
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        varidireito     = ctypes.c_int (idireito)
        iengast         = 0
        variengast      = ctypes.c_int (iengast)
        fatengast	= 0.
        varfatengast    = ctypes.c_double (fatengast)
        self.m_model.m_eagme.BASME_NOVIG_IENGAST_LER (ctypes.byref (varnovig),
                            ctypes.byref (varidireito), ctypes.byref (variengast),
                            ctypes.byref (varfatengast))
        iengast         = variengast.value
        fatengast       = varfatengast.value
        return          iengast, fatengast

    def SetSlabConnection (self, idireito, iengast, fatengast):
        """
        Define engastamento de um lado da viga com a laje\n
            int    idireito     <- (0) Esquerdo (1) Direito\n
            int    iengast      <- Tipo de engaste BEAMCONNECTION_XXX\n
            double fatengast	<- Fator de engaste 0..1 para iengast == (BEAMCONNECTION_FATEMGS)
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        varidireito     = ctypes.c_int (idireito)
        variengast      = ctypes.c_int (iengast)
        varfatengast    = ctypes.c_double (fatengast)
        self.m_model.m_eagme.BASME_NOVIG_IENGAST_DEF (ctypes.byref (varnovig),
                            ctypes.byref (varidireito), ctypes.byref (variengast),
                            ctypes.byref (varfatengast))

    def GetRestraint (self, ifinal):
        """
        Retorna objeto de engastamento BeamRestraint() no início ou fim de um trecho\n
            int ifinal          <- (0) Inicial (1) Final
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        varifinal       = ctypes.c_int (ifinal)
        artic           = None
        varartic        = ctypes.c_void_p (artic)
        self.m_model.m_eagme.BASME_NOVIG_ARTIC_LER (ctypes.byref (varnovig),
                            ctypes.byref (varifinal), ctypes.byref (varartic))
        artic           = varartic.value
        beamRestraint   = BeamRestraint (self.m_model, artic)
        return          beamRestraint

    @property
    def arcSegment (self):
        """
        Retorna objeto ArcSegment () com dados de arco no trecho atual
        """
        varnovig        = ctypes.c_void_p (self.m_novig)
        novigarco       = None
        varnovigarco    = ctypes.c_void_p (novigarco)
        self.m_model.m_eagme.BASME_NOVIG_ARCO_LER (ctypes.byref (varnovig),
                            ctypes.byref (varnovigarco))
        novigarco       = varnovigarco.value
        arcsegment      = ArcSegment (self.m_model, novigarco)
        return          arcsegment

#------------------------------------------------------------------------------
#       Articulação de vigas CArtic
#
class BeamRestraint ():

    def __init__ (self, model, artic):
        """
        Classe que define articulação de vigas\n
            model       <- Objeto Model() do modelo atual\n
            artic       <- Apontador para objeto CArtic
        """
        self.m_model    = model
        self.m_artic    = artic
        
    def GetRestraintCoef (self, irdir):
        """
        Coeficientes de articulação na extremidade da viga\n
            int irdir   <- Direção (0) RX (1) RY (2) RZ (3) FZ\n
        Retorna:\n
            int iartic  -> Articulação definida (0) Não (1) Sim\n
            double coef -> Coeficiente de rotação ou translação
        """
        varartic        = ctypes.c_void_p (self.m_artic)
        varirdir        = ctypes.c_int (irdir)
        iartic          = 0
        variartic       = ctypes.c_int (iartic)
        coef            = 0.
        varcoef         = ctypes.c_double (coef)
        self.m_model.m_eagme.BASME_ARTIC_COEFART_LER (ctypes.byref (varartic), 
                        ctypes.byref (varirdir), ctypes.byref (variartic),
                        ctypes.byref (varcoef))
        iartic          = varartic.value
        coef            = varcoef.value
        return          iartic, coef

    def SetRestraint (self, irdir, iartic, coef):
        """
        Coeficientes de articulação na extremidade da viga\n
            int irdir   <- Direção (0) RX (1) RY (2) RZ (3) FZ\n
            int iartic  <- Articulação definida (0) Não (1) Sim\n
            double coef <- Coeficiente de rotação ou translação
        """
        varartic        = ctypes.c_void_p (self.m_artic)
        varirdir        = ctypes.c_int (irdir)
        variartic       = ctypes.c_int (iartic)
        varcoef         = ctypes.c_double (coef)
        self.m_model.m_eagme.BASME_ARTIC_COEFART_DEF (ctypes.byref (varartic), 
                        ctypes.byref (varirdir), ctypes.byref (variartic),
                        ctypes.byref (varcoef))

    def GetPlasticMoments (self, itipopl, imompos):
        """
        Coeficientes de plastificação impostos\n
        Valor máximo de momento fletor em uma ligação\n
            int itipopl <- Definição (0) My (1) Mz\n
            int imompos <- Definição (0) Máximo negativo (1) Positivo\n
        Retorna:\n
            int isfmax    -> (0) Conforme critérios (1) Não definido (2) em esfmax\n
            double esfmax -> Momento máximo tfm 
        """
        varartic        = ctypes.c_void_p (self.m_artic)
        varitipopl      = ctypes.c_int (itipopl)
        varimompos      = ctypes.c_int (imompos)
        isfmax          = 0
        varisfmax       = ctypes.c_int (isfmax)
        esfmax          = 0.
        varesfmax       = ctypes.c_double (esfmax)
        self.m_model.m_eagme.BASME_ARTIC_MOMPLAST_LER (ctypes.byref (varartic), 
                        ctypes.byref (varitipopl), ctypes.byref (varimompos),
                        ctypes.byref (varisfmax), ctypes.byref (varesfmax))
        isfmax          = varisfmax.value
        esfmax          = varesfmax.value
        return          isfmax, esfmax

    def SetPlasticMoments (self, itipopl, imompos, isfmax, esfmax):
        """
        Coeficientes de plastificação impostos\n
        Valor máximo de momento fletor em uma ligação\n
            int itipopl   <- Definição (0) My (1) Mz\n
            int imompos   <- Definição (0) Máximo negativo (1) Positivo\n
            int isfmax    <- (0) Conforme critérios (1) Não definido (2) em esfmax\n
            double esfmax <- Momento máximo tfm 
        """
        varartic        = ctypes.c_void_p (self.m_artic)
        varitipopl      = ctypes.c_int (itipopl)
        varimompos      = ctypes.c_int (imompos)
        varisfmax       = ctypes.c_int (isfmax)
        varesfmax       = ctypes.c_double (esfmax)
        self.m_model.m_eagme.BASME_ARTIC_MOMPLAST_DEF (ctypes.byref (varartic), 
                        ctypes.byref (varitipopl), ctypes.byref (varimompos),
                        ctypes.byref (varisfmax), ctypes.byref (varesfmax))

#------------------------------------------------------------------------------
#       Dados de um trecho de viga em arco CNoVigArco
#
class ArcSegment ():

    def __init__ (self, model, novigarco):
        """
        Classe que define articulação de vigas\n
            model       <- Objeto Model() do modelo atual\n
            novigarco   <- Apontador para objeto CNoVigArco
        """
        self.m_model    = model
        self.m_novigarco= novigarco

    @property
    def startNode (self):
        """
        Nó inicial da viga 0..NumNodes()-1
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        inoini          = 0
        varinoini       = ctypes.c_int (inoini)
        self.m_model.m_eagme.BASME_NOVIGARCO_INOINI_LER (ctypes.byref (varnovigarco),
                            ctypes.byref (varinoini))
        inoini          = varinoini.value
        return          inoini

    @startNode.setter
    def startNode (self, inoini):
        """
        Nó inicial da viga 0..NumNodes()-1
        """
        varnovigarco        = ctypes.c_void_p (self.m_novigarco)
        varinoini        = ctypes.c_int (inoini)
        self.m_model.m_eagme.BASME_NOVIGARCO_INOINI_DEF (ctypes.byref (varnovigarco),
                            ctypes.byref (varinoini))

    @property
    def endNode (self):
        """
        Nó final da viga 0..NumNodes()-1
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        inofin          = 0
        varinofin       = ctypes.c_int (inofin)
        self.m_model.m_eagme.BASME_NOVIGARCO_INOFIN_LER (ctypes.byref (varnovigarco),
                            ctypes.byref (varinofin))
        inofin          = varinofin.value
        return          inofin

    @endNode.setter
    def endNode (self, inofin):
        """
        Nó final da viga 0..NumNodes()-1
        """
        varnovigarco        = ctypes.c_void_p (self.m_novigarco)
        varinofin        = ctypes.c_int (inofin)
        self.m_model.m_eagme.BASME_NOVIGARCO_INOFIN_DEF (ctypes.byref (varnovigarco),
                            ctypes.byref (varinofin))

    @property
    def signal (self):
        """
        Sinal do arco (1) anti-horário (-1) horário
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        isinal          = 0
        varisinal       = ctypes.c_int (isinal)
        self.m_model.m_eagme.BASME_NOVIGARCO_ISINAL_LER (ctypes.byref (varnovigarco),
                            ctypes.byref (varisinal))
        isinal          = varisinal.value
        return          isinal

    @signal.setter
    def signal (self, isinal):
        """
        Sinal do arco (1) anti-horário (-1) horário
        """
        varnovigarco        = ctypes.c_void_p (self.m_novigarco)
        varisinal        = ctypes.c_int (isinal)
        self.m_model.m_eagme.BASME_NOVIGARCO_ISINAL_DEF (ctypes.byref (varnovigarco),
                            ctypes.byref (varisinal))

    @property
    def centerX (self):
        """
        X do centro do arco cm
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        xc              = 0
        varxc           = ctypes.c_double (xc)
        self.m_model.m_eagme.BASME_NOVIGARCO_XC_LER (ctypes.byref (varnovigarco),
                            ctypes.byref (varxc))
        xc              = varxc.value
        return          xc

    @centerX.setter
    def centerX (self, xc):
        """
        X do centro do arco cm
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        varxc           = ctypes.c_double (xc)
        self.m_model.m_eagme.BASME_NOVIGARCO_XC_DEF (ctypes.byref (varnovigarco),
                            ctypes.byref (varxc))

    @property
    def centerY (self):
        """
        Y do centro do arco cm
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        yc              = 0
        varyc           = ctypes.c_double (yc)
        self.m_model.m_eagme.BASME_NOVIGARCO_YC_LER (ctypes.byref (varnovigarco),
                            ctypes.byref (varyc))
        yc              = varyc.value
        return          yc

    @centerY.setter
    def centerY (self, yc):
        """
        Y do centro do arco cm
        """
        varnovigarco    = ctypes.c_void_p (self.m_novigarco)
        varyc           = ctypes.c_double (yc)
        self.m_model.m_eagme.BASME_NOVIGARCO_YC_DEF (ctypes.byref (varnovigarco),
                            ctypes.byref (varyc))

#------------------------------------------------------------------------------
#       Objeto de contorno auxiliar de laje - bordo livre - CCtrAux
#
class SlabContour (SMObject):

    def __init__ (self, model, ctraux):
        """
        Classe que define articulação de vigas\n
            model       <- Objeto Model() do modelo atual\n
            ctraux      <- Apontador para objeto CCtrAux
        """
        self.m_model    = model
        self.m_ctraux   = ctraux
        super().__init__(model, self.m_ctraux)

    def _GetX (self, ifinal):
        varctraux       = ctypes.c_void_p (self.m_ctraux)
        varifinal       = ctypes.c_int (ifinal)
        xctr            = 0
        varxctr         = ctypes.c_double (xctr)
        self.m_model.m_eagme.BASME_CTRAUX_PT_LERX (ctypes.byref (varctraux),
                            ctypes.byref (varifinal), ctypes.byref (varxctr))
        xctr            = varxctr.value
        return          xctr

    def _SetX (self, ifinal, xctr):
        varctraux       = ctypes.c_void_p (self.m_ctraux)
        varifinal       = ctypes.c_int (ifinal)
        varxctr         = ctypes.c_double (xctr)
        self.m_model.m_eagme.BASME_CTRAUX_PT_DEFX (ctypes.byref (varctraux),
                            ctypes.byref (varifinal), ctypes.byref (varxctr))

    def _GetY (self, ifinal):
        varctraux       = ctypes.c_void_p (self.m_ctraux)
        varifinal       = ctypes.c_int (ifinal)
        yctr            = 0
        varyctr         = ctypes.c_double (yctr)
        self.m_model.m_eagme.BASME_CTRAUX_PT_LERY (ctypes.byref (varctraux),
                            ctypes.byref (varifinal), ctypes.byref (varyctr))
        yctr            = varyctr.value
        return          yctr

    def _SetY (self, ifinal, yctr):
        varctraux       = ctypes.c_void_p (self.m_ctraux)
        varifinal       = ctypes.c_int (ifinal)
        varyctr         = ctypes.c_double (yctr)
        self.m_model.m_eagme.BASME_CTRAUX_PT_DEFY (ctypes.byref (varctraux),
                            ctypes.byref (varifinal), ctypes.byref (varyctr))

    @property
    def startX (self):
        """
        X inicial cm
        """
        return          self._GetX (0)

    @startX.setter
    def startX (self, xctr):
        """
        X inicial cm
        """
        self._SetX (0, xctr)

    @property
    def startY (self):
        """
        Y inicial cm
        """
        return          self._GetY (0)

    @startY.setter
    def startY (self, xctr):
        """
        Y inicial cm
        """
        self._SetY (0, xctr)

    @property
    def endX (self):
        """
        X final cm
        """
        return          self._GetX (1)

    @endX.setter
    def endX (self, xctr):
        """
        X final cm
        """
        self._SetX (1, xctr)

    @property
    def endY (self):
        """
        Y final cm
        """
        return          self._GetY (1)

    @endY.setter
    def endY (self, xctr):
        """
        Y final cm
        """
        self._SetY (1, xctr)

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varctraux       = ctypes.c_void_p (self.m_ctraux)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CTRAUX_IPISOAUX_LER (ctypes.byref (varctraux),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varctraux       = ctypes.c_void_p (self.m_ctraux)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CTRAUX_IPISOAUX_DEF (ctypes.byref (varctraux),
                            ctypes.byref (varipisoaux))

#------------------------------------------------------------------------------
#       Objeto de laje - CLajes
#
class Slab (SMObject):

    def __init__ (self, model, laje):
        """
        Classe que define articulação de vigas\n
            model       <- Objeto Model() do modelo atual\n
            laje        <- Apontador para objeto CLajes
        """
        self.m_model    = model
        self.m_laje     = laje
        super().__init__(model, self.m_laje)

    @property
    def slabIdent (self):
        """
        Identificação da laje
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        identlaj        = None
        varidentlaj     = ctypes.c_void_p (identlaj)
        self.m_model.m_eagme.BASME_LAJES_IDENTLAJ_LER (ctypes.byref (varlaje),
                            ctypes.byref (varidentlaj))
        identlaj        = varidentlaj.value
        slabident       = SMObjectIdent (self.m_model, identlaj)
        return          slabident

    def GetLoad (self, floor):
        """
        Carga distribuída em toda a laje tf/m2
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        cargalaj        = None
        varcargalaj     = ctypes.c_void_p (cargalaj)
        self.m_model.m_eagme.BASME_LAJES_CARGALAJ_LER (ctypes.byref (varlaje),
                            ctypes.byref (varcargalaj))
        cargalaj       = varcargalaj.value
        slabload        = Load (self.m_model, floor, cargalaj)
        return          slabload

    @property
    def slabGeometry (self):
        """
        Dados de geometria de laje
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        geolaj          = None
        vargeolaj       = ctypes.c_void_p (geolaj)
        self.m_model.m_eagme.BASME_LAJES_GEOLAJ_LER (ctypes.byref (varlaje),
                            ctypes.byref (vargeolaj))
        geolaj          = vargeolaj.value
        slabGeometry    = SlabGeometry (self.m_model, geolaj)
        return          slabGeometry

    @property
    def slabGrid (self):
        """
        Dados para discretização de laje por grelha
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        grelaj          = None
        vargrelaj       = ctypes.c_void_p (grelaj)
        self.m_model.m_eagme.BASME_LAJES_GRELAJ_LER (ctypes.byref (varlaje),
                            ctypes.byref (vargrelaj))
        grelaj          = vargrelaj.value
        slabGrid        = SlabGrid (self.m_model, grelaj)
        return          slabGrid

    @property
    def mainAngle (self):
        """
        Ângulo principal em graus
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        angpri          = 0.
        varangpri       = ctypes.c_double (angpri)
        self.m_model.m_eagme.BASME_LAJES_ANGPRI_LER (ctypes.byref (varlaje),
                            ctypes.byref (varangpri))
        angpri          = varangpri.value
        return          angpri

    @mainAngle.setter
    def mainAngle (self, angpri):
        """
        Ângulo principal em graus
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        varangpri       = ctypes.c_double (angpri)
        self.m_model.m_eagme.BASME_LAJES_ANGPRI_DEF (ctypes.byref (varlaje),
                            ctypes.byref (varangpri))

    @property
    def slabTemperShrink (self):
        """
        Temperatura / retração de lajes
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        tempretlaj      = None
        vartempretlaj   = ctypes.c_void_p (tempretlaj)
        self.m_model.m_eagme.BASME_LAJES_TEMPRET_LER (ctypes.byref (varlaje),
                            ctypes.byref (vartempretlaj))
        tempretlaj      = vartempretlaj.value
        slabTemperShrink= TemperatureShrink (self.m_model, tempretlaj)
        return          slabTemperShrink

    @property
    def slabDetailing (self):
        """
        Detalhamento de lajes
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        detlaj          = None
        vardetlaj       = ctypes.c_void_p (detlaj)
        self.m_model.m_eagme.BASME_LAJES_DETLAJ_LER (ctypes.byref (varlaje),
                            ctypes.byref (vardetlaj))
        detlaj          = vardetlaj.value
        slabDetailing   = SlabDetailing (self.m_model, detlaj)
        return          slabDetailing

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_LAJES_IPISOAUX_LER (ctypes.byref (varlaje),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_LAJES_IPISOAUX_DEF (ctypes.byref (varlaje),
                            ctypes.byref (varipisoaux))
    @property
    def isAStair (self):
        """
        Lance de escada (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        iescada         = 0
        variescada      = ctypes.c_int (iescada)
        self.m_model.m_eagme.BASME_LAJES_IESCADA_LER (ctypes.byref (varlaje),
                            ctypes.byref (variescada))
        iescada         = variescada.value
        return          iescada

    @isAStair.setter
    def isAStair (self, iescada):
        """
        Lance de escada (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        variescada      = ctypes.c_int (iescada)
        self.m_model.m_eagme.BASME_LAJES_IESCADA_DEF (ctypes.byref (varlaje),
                            ctypes.byref (variescada))

    @property
    def stairCase (self):
        """
        Dados de escada - Objeto StairCase()
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        escdad          = None
        varescdad       = ctypes.c_void_p (escdad)
        self.m_model.m_eagme.BASME_LAJES_ESCADA_LER (ctypes.byref (varlaje),
                            ctypes.byref (varescdad))
        escdad          = varescdad.value
        stairCase       = StairCase (self.m_model, escdad)
        return          stairCase

    @property
    def isALanding (self):
        """
        Patamar de escada (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        ipatamar        = 0
        varipatamar     = ctypes.c_int (ipatamar)
        self.m_model.m_eagme.BASME_LAJES_IPATAMAR_LER (ctypes.byref (varlaje),
                            ctypes.byref (varipatamar))
        ipatamar        = varipatamar.value
        return          ipatamar

    @isALanding.setter
    def isALanding (self, ipatamar):
        """
        Lance de escada (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        varipatamar     = ctypes.c_int (ipatamar)
        self.m_model.m_eagme.BASME_LAJES_IPATAMAR_DEF (ctypes.byref (varlaje),
                            ctypes.byref (varipatamar))

    @property
    def stairIdent (self):
        """
        Título de escadas
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        varidentesc     = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_LAJES_IDENTESC_LER (ctypes.byref (varlaje), varidentesc)
        identesc        = varidentesc.value.decode(TQSUtil.CHARSET)
        return          identesc

    @stairIdent.setter
    def stairIdent (self, identesc):
        """
        Título de escadas
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        varidentesc     = ctypes.c_char_p (identesc.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_LAJES_IDENTESC_DEF (ctypes.byref (varlaje), varidentesc)

    @property
    def isVolumeOnly (self):
        """
        Laje somente de volume (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        ilajsovol       = 0
        varilajsovol    = ctypes.c_int (ilajsovol)
        self.m_model.m_eagme.BASME_LAJES_ILAJSOVOL_LER (ctypes.byref (varlaje),
                            ctypes.byref (varilajsovol))
        ilajsovol       = varilajsovol.value
        return          ilajsovol

    @isVolumeOnly.setter
    def isVolumeOnly (self, ilajsovol):
        """
        Laje somente de volume (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        varilajsovol    = ctypes.c_int (ilajsovol)
        self.m_model.m_eagme.BASME_LAJES_ILAJSOVOL_DEF (ctypes.byref (varlaje),
                            ctypes.byref (varilajsovol))

    @property
    def volumeOnlySlab (self):
        """
        Retorna dados de laje somente de volume - VolumeOnlySlab()
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        lajsovol        = None
        varlajsovol     = ctypes.c_void_p (lajsovol)
        self.m_model.m_eagme.BASME_LAJES_LAJSOVOL_LER (ctypes.byref (varlaje),
                            ctypes.byref (varlajsovol))
        lajsovol        = varlajsovol.value
        volumeOnlySlab  = VolumeOnlySlab (self.m_model, lajsovol)
        return          volumeOnlySlab

    @property
    def userAttrib (self):
        """
        Retorna atributos de usuário - UserAttrib ()
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        usratrib        = None
        varusratrib     = ctypes.c_void_p (usratrib)
        self.m_model.m_eagme.BASME_LAJES_USRATRIB_LER (ctypes.byref (varlaje),
                            ctypes.byref (varusratrib))
        usratrib        = varusratrib.value
        userAttrib      = UserAttrib (self.m_model, usratrib)
        return          userAttrib


    @property
    def slabExport (self):
        """
        Laje exportável para 3D/BIM (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        iexportavel     = 0
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_LAJES_IEXPORTAVEL_LER (ctypes.byref (varlaje),
                            ctypes.byref (variexportavel))
        iexportavel     = variexportavel.value
        return          iexportavel

    @slabExport.setter
    def slabExport (self, iexportavel):
        """
        Laje exportável para 3D/BIM (0) Não (1) Sim
        """
        varlaje         = ctypes.c_void_p (self.m_laje)
        variexportavel  = ctypes.c_int (iexportavel)
        self.m_model.m_eagme.BASME_LAJES_IEXPORTAVEL_DEF (ctypes.byref (varlaje),
                            ctypes.byref (variexportavel))

#------------------------------------------------------------------------------
#       Objeto de capitel - CCapiteis
#
class DropPanel (SMObject):

    def __init__ (self, model, capitel):
        """
        Classe que define capitel\n
            model       <- Objeto Model() do modelo atual\n
            capitel     <- Apontador para objeto CCapiteis
        """
        self.m_model    = model
        self.m_capitel  = capitel
        super().__init__(model, self.m_capitel)

    @property
    def dropPanelPolygon (self):
        """
        Poligonal do capitel - Poygon()
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        poligp          = None
        varpoligp       = ctypes.c_void_p (poligp)
        self.m_model.m_eagme.BASME_CAPITEIS_POLIGONAL_LER (ctypes.byref (varcapitel),
                            ctypes.byref (varpoligp))
        poligp          = varpoligp.value
        columnpolygon   = Polygon (self.m_model, poligp)
        return          columnpolygon


    @property
    def dropPanelThickness (self):
        """
        Altura do capitel, cm
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        hcap            = 0.
        varhcap         = ctypes.c_double (hcap)
        self.m_model.m_eagme.BASME_CAPITEIS_H_LER (ctypes.byref (varcapitel),
                            ctypes.byref (varhcap))
        hcap            = varhcap.value
        return          hcap

    @dropPanelThickness.setter
    def dropPanelThickness (self, hcap):
        """
        Altura do capitel, cm
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        varhcap         = ctypes.c_double (hcap)
        self.m_model.m_eagme.BASME_CAPITEIS_H_DEF (ctypes.byref (varcapitel),
                            ctypes.byref (varhcap))

    @property
    def dropPanelDiv (self):
        """
        Divisor de inércia à flexão do capitel
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        divflx          = 0.
        vardivflx       = ctypes.c_double (divflx)
        self.m_model.m_eagme.BASME_CAPITEIS_DIVFLX_LER (ctypes.byref (varcapitel),
                            ctypes.byref (vardivflx))
        divflx          = vardivflx.value
        return          divflx

    @dropPanelDiv.setter
    def dropPanelDiv (self, divflx):
        """
        Divisor de inércia à flexão do capitel
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        vardivflx       = ctypes.c_double (divflx)
        self.m_model.m_eagme.BASME_CAPITEIS_DIVFLX_DEF (ctypes.byref (varcapitel),
                            ctypes.byref (vardivflx))
    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CAPITEIS_IPISOAUX_LER (ctypes.byref (varcapitel),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varcapitel      = ctypes.c_void_p (self.m_capitel)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CAPITEIS_IPISOAUX_DEF (ctypes.byref (varcapitel),
                            ctypes.byref (varipisoaux))

#------------------------------------------------------------------------------
#       Objeto de forma de nervura
#
class SlabMould (SMObject):

    def __init__ (self, model, forner):
        """
        Classe que define uma forma de nervura\n
            model       <- Objeto Model() do modelo atual\n
            forner      <- Apontador para objeto CForNer
        """
        self.m_model    = model
        self.m_forner   = forner
        super().__init__(model, self.m_forner)

    @property
    def insX (self):
        """
        X de inserção do molde
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        xins            = 0.
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_FORNER_PT_LERX (ctypes.byref (varforner),
                            ctypes.byref (varxins))
        xins            = varxins.value
        return          xins

    @insX.setter
    def insX (self, xins):
        """
        X de inserção do molde
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varxins         = ctypes.c_double (xins)
        self.m_model.m_eagme.BASME_FORNER_PT_DEFX (ctypes.byref (varforner),
                            ctypes.byref (varxins))

    @property
    def insY (self):
        """
        Y de inserção do molde
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        yins            = 0.
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_FORNER_PT_LERY (ctypes.byref (varforner),
                            ctypes.byref (varyins))
        yins            = varyins.value
        return          yins

    @insY.setter
    def insY (self, yins):
        """
        Y de inserção do molde
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varyins         = ctypes.c_double (yins)
        self.m_model.m_eagme.BASME_FORNER_PT_DEFY (ctypes.byref (varforner),
                            ctypes.byref (varyins))

    @property
    def averageSizeX (self):
        """
        Tamanho X médio cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        tamx            = 0.
        vartamx         = ctypes.c_double (tamx)
        self.m_model.m_eagme.BASME_FORNER_GEO_TAMX_LER (ctypes.byref (varforner),
                            ctypes.byref (vartamx))
        tamx            = vartamx.value
        return          tamx

    @averageSizeX.setter
    def averageSizeX (self, tamx):
        """
        Tamanho X médio cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        vartamx         = ctypes.c_double (tamx)
        self.m_model.m_eagme.BASME_FORNER_GEO_TAMX_DEF (ctypes.byref (varforner),
                            ctypes.byref (vartamx))

    @property
    def averageSizeY (self):
        """
        Tamanho Y médio cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        tamy            = 0.
        vartamy         = ctypes.c_double (tamy)
        self.m_model.m_eagme.BASME_FORNER_GEO_TAMY_LER (ctypes.byref (varforner),
                            ctypes.byref (vartamy))
        tamy            = vartamy.value
        return          tamy

    @averageSizeY.setter
    def averageSizeY (self, tamy):
        """
        Tamanho Y médio cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        vartamy         = ctypes.c_double (tamy)
        self.m_model.m_eagme.BASME_FORNER_GEO_TAMY_DEF (ctypes.byref (varforner),
                            ctypes.byref (vartamy))

    @property
    def rotationAngle (self):
        """
        Ângulo de rotação em graus
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        ang             = 0.
        varang          = ctypes.c_double (ang)
        self.m_model.m_eagme.BASME_FORNER_GEO_ANG_LER (ctypes.byref (varforner),
                            ctypes.byref (varang))
        ang             = varang.value
        return          ang

    @rotationAngle.setter
    def rotationAngle (self, ang):
        """
        Ângulo de rotação em graus
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varang          = ctypes.c_double (ang)
        self.m_model.m_eagme.BASME_FORNER_GEO_ANG_DEF (ctypes.byref (varforner),
                            ctypes.byref (varang))

    @property
    def sizeXDelta (self):
        """
        Variação de espessura trapezoidal X cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        vartx           = 0.
        varvartx        = ctypes.c_double (vartx)
        self.m_model.m_eagme.BASME_FORNER_GEO_VARTX_LER (ctypes.byref (varforner),
                            ctypes.byref (varvartx))
        vartx           = varvartx.value
        return          vartx

    @sizeXDelta.setter
    def sizeXDelta (self, vartx):
        """
        Variação de espessura trapezoidal X cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varvartx        = ctypes.c_double (vartx)
        self.m_model.m_eagme.BASME_FORNER_GEO_VARTX_DEF (ctypes.byref (varforner),
                            ctypes.byref (varvartx))

    @property
    def sizeYDelta (self):
        """
        Variação de espessura trapezoidal Y cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varty           = 0.
        varvarty        = ctypes.c_double (varty)
        self.m_model.m_eagme.BASME_FORNER_GEO_VARTY_LER (ctypes.byref (varforner),
                            ctypes.byref (varvarty))
        varty           = varvarty.value
        return          varty

    @sizeYDelta.setter
    def sizeYDelta (self, varty):
        """
        Variação de espessura trapezoidal Y cm
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varvarty        = ctypes.c_double (varty)
        self.m_model.m_eagme.BASME_FORNER_GEO_VARTY_DEF (ctypes.byref (varforner),
                            ctypes.byref (varvarty))

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_FORNER_IPISOAUX_LER (ctypes.byref (varforner),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varforner       = ctypes.c_void_p (self.m_forner)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_FORNER_IPISOAUX_DEF (ctypes.byref (varforner),
                            ctypes.byref (varipisoaux))
#------------------------------------------------------------------------------
#       Objeto de furo em lajes - CFuros
#
class SlabOpening (SMObject):

    def __init__ (self, model, furo):
        """
        Classe que define um furo em laje\n
            model       <- Objeto Model() do modelo atual\n
            furo        <- Apontador para objeto CFuros
        """
        self.m_model    = model
        self.m_furo     = furo
        super().__init__(model, self.m_furo)

    @property
    def slabOpeningPolygon (self):
        """
        Poligonal do furo em laje - Polygon()
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        polig           = None
        varpolig        = ctypes.c_void_p (polig)
        self.m_model.m_eagme.BASME_FUROS_POLIGONAL_LER (ctypes.byref (varfuro),
                            ctypes.byref (varpolig))
        polig           = varpolig.value
        columnpolygon   = Polygon (self.m_model, polig)
        return          columnpolygon

    @property
    def isCut (self):
        """
        Tipo de furo (0) Shaft (respeita nervuras) (1) Corte
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        irecorte        = 0
        varirecorte     = ctypes.c_int (irecorte)
        self.m_model.m_eagme.BASME_FUROS_IRECORTE_LER (ctypes.byref (varfuro),
                            ctypes.byref (varirecorte))
        irecorte        = varirecorte.value
        return          irecorte

    @isCut.setter
    def isCut (self, irecorte):
        """
        Tipo de furo (0) Shaft (respeita nervuras) (1) Corte
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        varirecorte     = ctypes.c_int (irecorte)
        self.m_model.m_eagme.BASME_FUROS_IRECORTE_DEF (ctypes.byref (varfuro),
                            ctypes.byref (varirecorte))
    @property
    def inConcretTopping (self):
        """
        Somente na capa da laje nervurada (0) Não (1) Sim
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        isobrecapa      = 0
        varisobrecapa   = ctypes.c_int (isobrecapa)
        self.m_model.m_eagme.BASME_FUROS_ISOBRECAPA_LER (ctypes.byref (varfuro),
                            ctypes.byref (varisobrecapa))
        isobrecapa      = varisobrecapa.value
        return          isobrecapa

    @inConcretTopping.setter
    def inConcretTopping (self, isobrecapa):
        """
        Somente na capa da laje nervurada (0) Não (1) Sim
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        varisobrecapa   = ctypes.c_int (isobrecapa)
        self.m_model.m_eagme.BASME_FUROS_ISOBRECAPA_DEF (ctypes.byref (varfuro),
                            ctypes.byref (varisobrecapa))
        
    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_FUROS_IPISOAUX_LER (ctypes.byref (varfuro),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varfuro         = ctypes.c_void_p (self.m_furo)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_FUROS_IPISOAUX_DEF (ctypes.byref (varfuro),
                            ctypes.byref (varipisoaux))
#------------------------------------------------------------------------------
#       Valores de cargas - CCargas
#
class Load ():

    def __init__ (self, model, floor, carga):
        """
        Classe de valor de carga - usada pelas cargas aplicadas (concentrada, linear, etc)\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor, com dados de uma planta\n
            carga       <- Apontador para objeto CCargas
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_carga    = carga

    def SetLoad (self, itype):
        """
        Define o tipo de carga\n
            int itype   <- Tipo LOADTYPE_xxxxx
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcarga        = ctypes.c_void_p (self.m_carga)
        varitype        = ctypes.c_int (itype)
        self.m_model.m_eagme.BASME_CARGAS_TIPO_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcarga), ctypes.byref (varitype))

    def SetAlpha (self, icase, ialpha):
        """
        Define modo de carga numérico ou alfanumérico\n
            int icase   <- Caso de carga 1..número de casos de grelha do pavimento\n
            int ialfa   <- Carga (0) Numérica (1) Alfanumérica da tabela de tipos de cargas
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcarga        = ctypes.c_void_p (self.m_carga)
        varicase        = ctypes.c_int (icase)
        varialpha       = ctypes.c_int (ialpha)
        self.m_model.m_eagme.BASME_CARGAS_IALFA_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcarga), ctypes.byref (varicase),
                            ctypes.byref (varialpha))

    def SetLoadName (self, icase, loadname):
        """
        Para cargas alfanuméricas, define o nome da carga na tabela de cargas\n
            int icase   <- Caso de carga 1..número de casos de grelha do pavimento\n
            loadname    <- Nome da carga
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcarga        = ctypes.c_void_p (self.m_carga)
        varicase        = ctypes.c_int (icase)
        varnomcar       = ctypes.c_char_p (loadname.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_CARGAS_NOMCAR_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcarga), ctypes.byref (varicase),
                            varnomcar)

    def SetMainLoad (self, icase, loadval):
        """
        Valor da carga permanente\n
            int icase   <- Caso de carga 1..número de casos de grelha do pavimento\n
            loadval     <- Valor da carga em unidades coerentes
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcarga        = ctypes.c_void_p (self.m_carga)
        varicase        = ctypes.c_int (icase)
        varloadval      = ctypes.c_double (loadval)
        self.m_model.m_eagme.BASME_CARGAS_CPERM_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcarga), ctypes.byref (varicase),
                            ctypes.byref (varloadval))

    def SetLiveLoad (self, icase, loadval):
        """
        Valor da carga variável\n
            int icase   <- Caso de carga 1..número de casos de grelha do pavimento\n
            loadval     <- Valor da carga em unidades coerentes
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcarga        = ctypes.c_void_p (self.m_carga)
        varicase        = ctypes.c_int (icase)
        varloadval      = ctypes.c_double (loadval)
        self.m_model.m_eagme.BASME_CARGAS_CACID_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcarga), ctypes.byref (varicase),
                            ctypes.byref (varloadval))

    def SetWallHeight (self, icase, iwall, wallheight):
        """
        Define o uso da altura da parede\n
            int icase   <- Caso de carga 1..número de casos de grelha do pavimento\n
            int iwall           <- Usa parede para carga por área (0) Não (1) Sim\n
            double wallheight   <- Altura da parede (m) ou (0) Para PD da planta
        """
        varfabrica      = ctypes.c_void_p (self.m_floor.m_fabrica)
        varcarga        = ctypes.c_void_p (self.m_carga)
        varicase        = ctypes.c_int (icase)
        variwall        = ctypes.c_int (iwall)
        varwallheight   = ctypes.c_double (wallheight)
        self.m_model.m_eagme.BASME_CARGAS_PAREDES_DEF (ctypes.byref (varfabrica),
                            ctypes.byref (varcarga), ctypes.byref (varicase),
                            ctypes.byref (variwall), ctypes.byref (varwallheight))

#------------------------------------------------------------------------------
#       Carga de empuxo lateral aplicada em pilares - CCarEmp
#
class SoilPressureLoad (SMObject):

    def __init__ (self, model, floor, caremp):
        """
        Classe que define empuxo lateral de solo\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor, com dados de uma planta\n
            caremp      <- Apontador para objeto CCarEmp
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_caremp   = caremp
        super().__init__(model, self.m_caremp)

    @property
    def topLoad (self):
        """
        Carga de empuxo no topo - Objeto Load()
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        cargatopo       = None
        varcargatopo    = ctypes.c_void_p (cargatopo)
        self.m_model.m_eagme.BASME_CAREMP_CARGATOPO_LER (ctypes.byref (varcaremp),
                            ctypes.byref (varcargatopo))
        cargatopo       = varcargatopo.value
        topload         = Load (self.m_model, self.m_floor, cargatopo)
        return          topload

    @property
    def baseLoad (self):
        """
        Carga de empuxo na base - Objeto Load()
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        cargabase       = None
        varcargabase    = ctypes.c_void_p (cargabase)
        self.m_model.m_eagme.BASME_CAREMP_CARGABASE_LER (ctypes.byref (varcaremp),
                            ctypes.byref (varcargabase))
        cargabase       = varcargabase.value
        baseload        = Load (self.m_model, self.m_floor, cargabase)
        return          baseload

    @property
    def topFloorName (self):
        """
        Nome da planta do topo da carga de empuxo
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varplanttopo    = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_CAREMP_PLANTTOPO_LER (ctypes.byref (varcaremp),
                            varplanttopo)
        planttopo       = varplanttopo.value.decode(TQSUtil.CHARSET)
        return          planttopo

    @topFloorName.setter
    def topFloorName (self, planttopo):
        """
        Nome da planta do topo da carga de empuxo
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varplanttopo    = ctypes.c_char_p (planttopo.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_CAREMP_PLANTTOPO_DEF (ctypes.byref (varcaremp),
                            varplanttopo)

    @property
    def baseFloorName (self):
        """
        Nome da planta da base da carga de empuxo
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varplantbase    = ctypes.create_string_buffer (TQSUtil.MAXNCSTR)
        self.m_model.m_eagme.BASME_CAREMP_PLANTBASE_LER (ctypes.byref (varcaremp),
                            varplantbase)
        plantbase       = varplantbase.value.decode(TQSUtil.CHARSET)
        return          plantbase

    @baseFloorName.setter
    def baseFloorName (self, plantbase):
        """
        Nome da planta da base da carga de empuxo
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varplantbase    = ctypes.c_char_p (plantbase.encode (TQSUtil.CHARSET))
        self.m_model.m_eagme.BASME_CAREMP_PLANTBASE_DEF (ctypes.byref (varcaremp),
                            varplantbase)

    @property
    def startPointX (self):
        """
        Ponto inicial X
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        xini            = 0
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CAREMP_PTINIX_LER (ctypes.byref (varcaremp),
                            ctypes.byref (varxini))
        xini            = varxini.value
        return          xini

    @startPointX.setter
    def startPointX (self, xini):
        """
        Ponto inicial X
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CAREMP_PTINIX_DEF (ctypes.byref (varcaremp),
                            ctypes.byref (varxini))

    @property
    def startPointY (self):
        """
        Ponto inicial Y
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        yini            = 0
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CAREMP_PTINIY_LER (ctypes.byref (varcaremp),
                            ctypes.byref (varyini))
        yini            = varyini.value
        return          yini

    @startPointY.setter
    def startPointY (self, yini):
        """
        Ponto inicial Y
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CAREMP_PTINIY_DEF (ctypes.byref (varcaremp),
                            ctypes.byref (varyini))

    @property
    def endPointX (self):
        """
        Ponto final X
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        xfin            = 0
        varxfin         = ctypes.c_double (xfin)
        self.m_model.m_eagme.BASME_CAREMP_PTFINX_LER (ctypes.byref (varcaremp),
                            ctypes.byref (varxfin))
        xfin            = varxfin.value
        return          xfin

    @endPointX.setter
    def endPointX (self, xfin):
        """
        Ponto final X
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varxfin         = ctypes.c_double (xfin)
        self.m_model.m_eagme.BASME_CAREMP_PTFINX_DEF (ctypes.byref (varcaremp),
                            ctypes.byref (varxfin))

    @property
    def endPointY (self):
        """
        Ponto final Y
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        yfin            = 0
        varyfin         = ctypes.c_double (yfin)
        self.m_model.m_eagme.BASME_CAREMP_PTFINY_LER (ctypes.byref (varcaremp),
                            ctypes.byref (varyfin))
        yfin            = varyfin.value
        return          yfin

    @endPointY.setter
    def endPointY (self, yfin):
        """
        Ponto final Y
        """
        varcaremp       = ctypes.c_void_p (self.m_caremp)
        varyfin         = ctypes.c_double (yfin)
        self.m_model.m_eagme.BASME_CAREMP_PTFINY_DEF (ctypes.byref (varcaremp),
                            ctypes.byref (varyfin))

#------------------------------------------------------------------------------
#       Carga adicional em lajes CCarAdi
#
class AdditionalLoad (SMObject):

    def __init__ (self, model, floor, caradi):
        """
        Carga adicional em lajes tf/m2\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor, com dados de uma planta\n
            caradi      <- Apontador para objeto CCarAdi
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_caradi   = caradi
        super().__init__(model, self.m_caradi)

    @property
    def load (self):
        """
        Valor da carga - Objeto Load ()
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARADI_CARGA_LER (ctypes.byref (varcaradi),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def insertionX (self):
        """
        Ponto de inserção X
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        xini            = 0
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CARADI_PTINS_LERX (ctypes.byref (varcaradi),
                            ctypes.byref (varxini))
        xini            = varxini.value
        return          xini

    @insertionX.setter
    def insertionX (self, xini):
        """
        Ponto de inserção X
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CARADI_PTINS_DEFX (ctypes.byref (varcaradi),
                            ctypes.byref (varxini))

    @property
    def insertionY (self):
        """
        Ponto de inserção Y
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        yini            = 0
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CARADI_PTINS_LERY (ctypes.byref (varcaradi),
                            ctypes.byref (varyini))
        yini            = varyini.value
        return          yini

    @insertionY.setter
    def insertionY (self, yini):
        """
        Ponto de inserção Y
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CARADI_PTINS_DEFY (ctypes.byref (varcaradi),
                            ctypes.byref (varyini))

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARADI_IPISOAUX_LER (ctypes.byref (varcaradi),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varcaradi       = ctypes.c_void_p (self.m_caradi)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARADI_IPISOAUX_DEF (ctypes.byref (varcaradi),
                            ctypes.byref (varipisoaux))
#------------------------------------------------------------------------------
#       Carga distribuída por área em lajes CCarAre
#
class AreaDistributedLoad (SMObject):

    def __init__ (self, model, floor, carare):
        """
        Carga distribuída por área em lajes tf/m2\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor, com dados de uma planta\n
            carare      <- Apontador para objeto CCarAre
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_carare   = carare
        super().__init__(model, self.m_carare)

    @property
    def load (self):
        """
        Valor da carga - Objeto Load()
        """
        varcarare       = ctypes.c_void_p (self.m_carare)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARARE_CARGA_LER (ctypes.byref (varcarare),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def polygon (self):
        """
        Poligonal fechada onde a polig é distribuída - Polygon()
        """
        varcarare       = ctypes.c_void_p (self.m_carare)
        polig           = None
        varpolig        = ctypes.c_void_p (polig)
        self.m_model.m_eagme.BASME_CARARE_POLIG_LER (ctypes.byref (varcarare),
                            ctypes.byref (varpolig))
        polig           = varpolig.value
        polygonx        = Polygon (self.m_model, polig)
        return          polygonx

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varcarare       = ctypes.c_void_p (self.m_carare)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARARE_IPISOAUX_LER (ctypes.byref (varcarare),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varcarare       = ctypes.c_void_p (self.m_carare)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARARE_IPISOAUX_DEF (ctypes.byref (varcarare),
                            ctypes.byref (varipisoaux))

#------------------------------------------------------------------------------
#       Carga concentrada em laje, viga ou pilar CCarCon
#
class ConcentratedLoad (SMObject):

    def __init__ (self, model, floor, carcon):
        """
        Carga concentrada em laje, viga ou pilar\n
            model       <- Objeto Model() do modelo atual\n
            floor       <- Objeto Floor, com dados de uma planta\n
            carcon      <- Apontador para objeto CCarCon
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_carcon   = carcon
        super().__init__(model, self.m_carcon)

    @property
    def loadFx (self):
        """
        Força Fx - tf - Somente pilar - Objeto Load ()
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARCON_FX_LER (ctypes.byref (varcarcon),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def loadFy (self):
        """
        Força Fy - tf - Somente pilar - Objeto Load ()
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARCON_FY_LER (ctypes.byref (varcarcon),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def loadFz (self):
        """
        Força Fz - tf - Pilar, viga ou laje - Objeto Load ()
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARCON_FZ_LER (ctypes.byref (varcarcon),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def loadMx (self):
        """
        Força Mx - tfm - Somente pilar - Objeto Load ()
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARCON_MX_LER (ctypes.byref (varcarcon),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def loadMy (self):
        """
        Força My - tfm - Somente pilar - Objeto Load ()
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARCON_MY_LER (ctypes.byref (varcarcon),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def insertionX (self):
        """
        Ponto de inserção X
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        xini            = 0
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CARCON_PTINS_LERX (ctypes.byref (varcarcon),
                            ctypes.byref (varxini))
        xini            = varxini.value
        return          xini

    @insertionX.setter
    def insertionX (self, xini):
        """
        Ponto de inserção X
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CARCON_PTINS_DEFX (ctypes.byref (varcarcon),
                            ctypes.byref (varxini))

    @property
    def insertionY (self):
        """
        Ponto de inserção Y
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        yini            = 0
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CARCON_PTINS_LERY (ctypes.byref (varcarcon),
                            ctypes.byref (varyini))
        yini            = varyini.value
        return          yini

    @insertionY.setter
    def insertionY (self, yini):
        """
        Ponto de inserção Y
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CARCON_PTINS_DEFY (ctypes.byref (varcarcon),
                            ctypes.byref (varyini))

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARCON_IPISOAUX_LER (ctypes.byref (varcarcon),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varcarcon       = ctypes.c_void_p (self.m_carcon)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARCON_IPISOAUX_DEF (ctypes.byref (varcarcon),
                            ctypes.byref (varipisoaux))
#------------------------------------------------------------------------------
#       Carga linear distribuída por metro sobre laje ou viga CCarLin
#
class LinearyDistributedLoad (SMObject):

    def __init__ (self, model, floor, carlin):
        """
        Carga linear distribuída tf/m\n
            model        <- Objeto Model() do modelo atual\n
            floor        <- Objeto Floor, com dados de uma planta\n
            carlin       <- Apontador para objeto CCarLin
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_carlin   = carlin
        super().__init__(model, self.m_carlin)

    @property
    def load (self):
        """
        Valor da carga - Objeto Load()
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        carga           = None
        varcarga        = ctypes.c_void_p (carga)
        self.m_model.m_eagme.BASME_CARLIN_CARGA_LER (ctypes.byref (varcarlin),
                            ctypes.byref (varcarga))
        carga           = varcarga.value
        loadx           = Load (self.m_model, self.m_floor, carga)
        return          loadx

    @property
    def startPointX (self):
        """
        Ponto inicial X
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        xini            = 0
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CARLIN_PTINI_LERX (ctypes.byref (varcarlin),
                            ctypes.byref (varxini))
        xini            = varxini.value
        return          xini

    @startPointX.setter
    def startPointX (self, xini):
        """
        Ponto inicial X
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        varxini         = ctypes.c_double (xini)
        self.m_model.m_eagme.BASME_CARLIN_PTINI_DEFX (ctypes.byref (varcarlin),
                            ctypes.byref (varxini))

    @property
    def startPointY (self):
        """
        Ponto inicial Y
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        yini            = 0
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CARLIN_PTINI_LERY (ctypes.byref (varcarlin),
                            ctypes.byref (varyini))
        yini            = varyini.value
        return          yini

    @startPointY.setter
    def startPointY (self, yini):
        """
        Ponto inicial Y
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        varyini         = ctypes.c_double (yini)
        self.m_model.m_eagme.BASME_CARLIN_PTINI_DEFY (ctypes.byref (varcarlin),
                            ctypes.byref (varyini))

    @property
    def endPointX (self):
        """
        Ponto final X
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        xfin            = 0
        varxfin         = ctypes.c_double (xfin)
        self.m_model.m_eagme.BASME_CARLIN_PTFIN_LERX (ctypes.byref (varcarlin),
                            ctypes.byref (varxfin))
        xfin            = varxfin.value
        return          xfin

    @endPointX.setter
    def endPointX (self, xfin):
        """
        Ponto final X
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        varxfin         = ctypes.c_double (xfin)
        self.m_model.m_eagme.BASME_CARLIN_PTFIN_DEFX (ctypes.byref (varcarlin),
                            ctypes.byref (varxfin))

    @property
    def endPointY (self):
        """
        Ponto final Y
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        yfin            = 0
        varyfin         = ctypes.c_double (yfin)
        self.m_model.m_eagme.BASME_CARLIN_PTFIN_LERY (ctypes.byref (varcarlin),
                            ctypes.byref (varyfin))
        yfin            = varyfin.value
        return          yfin

    @endPointY.setter
    def endPointY (self, yfin):
        """
        Ponto final Y
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        varyfin         = ctypes.c_double (yfin)
        self.m_model.m_eagme.BASME_CARLIN_PTFIN_DEFY (ctypes.byref (varcarlin),
                            ctypes.byref (varyfin))

    @property
    def auxiliaryFloor (self):
        """
        Piso auxiliar
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        ipisoaux        = 0
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARLIN_IPISOAUX_LER (ctypes.byref (varcarlin),
                            ctypes.byref (varipisoaux))
        ipisoaux        = varipisoaux.value
        return          ipisoaux

    @auxiliaryFloor.setter
    def auxiliaryFloor (self, ipisoaux):
        """
        Piso auxiliar
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        varipisoaux     = ctypes.c_int (ipisoaux)
        self.m_model.m_eagme.BASME_CARLIN_IPISOAUX_DEF (ctypes.byref (varcarlin),
                            ctypes.byref (varipisoaux))

    @property
    def wall (self):
        """
        Parede 3D importada do BIM - Objeto Wall() ou None
        """
        varcarlin       = ctypes.c_void_p (self.m_carlin)
        paresp          = None
        varparesp       = ctypes.c_void_p (paresp)
        self.m_model.m_eagme.BASME_CARLIN_PARESP_LER (ctypes.byref (varcarlin),
                            ctypes.byref (varparesp))
        paresp          = varparesp.value
        wallx           = Wall (self.m_model, self.m_floor, paresp)
        return          wallx
#------------------------------------------------------------------------------
#       Parede 3D importada do BIM - CParEsp
#
class Wall ():

    def __init__ (self, model, floor, paresp):
        """
        Parede importada do BIM\n
            model        <- Objeto Model() do modelo atual\n
            floor        <- Objeto Floor, com dados de uma planta\n
            paresp       <- Apontador para objeto CParEsp
        """
        self.m_model    = model
        self.m_floor    = floor
        self.m_paresp   = paresp
        

