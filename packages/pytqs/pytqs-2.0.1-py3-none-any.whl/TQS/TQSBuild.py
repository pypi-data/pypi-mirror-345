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
#       TQSBuild.py     Leitura e gravação de dados de edifício TQS
#-----------------------------------------------------------------------------
import ctypes
import TQS.TQSUtil

#-----------------------------------------------------------------------------
#
#    Tipos de pórtico
#
PORTICO_INDEF           = 0             # (I)   Modelo indefinido
PORTICO_NAO             = 1             # (II)  Não calcula
PORTICO_HOR             = 2             # (III) Somente para esforços horizontais
PORTICO_HORVER          = 3             # (IV)  Esforços horizontais e verticais + flexibilização
PORTICO_CONJUN          = 4             # (V)   Modelo articulado/engastado
PORTICO_LAJES           = 5             # (VI)  Com subestruturas de lajes e flexibilização
#
#       Tipos de grelha
#
GRELHA_INDEF            = 0             # Indefinido
GRELHA_VIGAS            = 1             # Vigas contínuas
GRELHA_LAJNER           = 2             # Grelha de lajes nervuradas
GRELHA_LAJPLA           = 3             # Grelha de laje plana
GRELHA_GREVIG           = 4             # Grelha só de vigas
GRELHA_PLACAS           = 5             # Grelha de laje plana de placa
GRELHA_AUTOMA           = 6             # Automático: Nervurada ou Plana
#
#       Classe de planta
#
ICLFUN                  = 1             # Fundação
ICLSUB                  = 2             # Subsolo
ICLTER                  = 3             # Térreo
ICLMEZ                  = 4             # Mezzanino
ICLTRN                  = 5             # Transição
ICLPRI                  = 6             # Primeiro
ICLTIP                  = 7             # Tipo
ICLCOB                  = 8             # Cobertura
ICLATI                  = 9             # Ático
ICLDUP                  = 10            # Duplex
ICLTRI                  = 11            # Triplex
#
#       Etapas construtivas
#
PISOINDEF               = -1            # Sem definição de piso
#
#        Normas de alvenaria estrutural
#
NORMALVS_10837          = "NBR 10837 : 1989 - Blocos vazados de Concreto"#!NTR
NORMALVI_10837          = 0
NORMALVS_15961          = "NBR 15961-1 : 2011 - Blocos de Concreto"#!NTR
NORMALVI_15961          = 1
NORMALVS_15812          = "NBR 15812-1 : 2010 - Blocos Cerâmicos"#!NTR
NORMALVI_15812          = 2
NORMALVS_16868          = "NBR 16868-1 : 2020 - Blocos de Concreto e Cerâmicos"#!NTR
NORMALVI_16868          = 3
#
#       Materiais de alvenaria estrutural
#
MATRALVS_CONVAZ         = "Blocos vazados de CONCRETO"
MATRALVI_CONVAZ         = 0
MATRALVS_CONMAC         = "Blocos maciços de CONCRETO"
MATRALVI_CONMAC         = 1
MATRALVS_CERVAZ         = "Blocos CERÂMICOS vazados"
MATRALVI_CERVAZ         = 2
MATRALVS_CERMAC         = "Blocos CERÂMICOS maciços"
MATRALVI_CERMAC         = 3
MATRALVS_SILVAZ         = "Blocos SILICO-CALCÁREOS vazados"
MATRALVI_SILVAZ         = 4
MATRALVS_SILMAC         = "Blocos SILICO-CALCÁREOS maciços"
MATRALVI_SILMAC         = 5
MATRALVS_OUTROS         = "Outro (Bloco/Tijolo)"
MATRALVI_OUTROS         = 6
#
#        Normas de paredes de concreto
#
NORMAPAREDS_NBR16055    = "NBR 16055:2012 - Paredes de Concreto"
NORMAPAREDI_NBR16055    = 0
#
#        Normas de concreto armador
#
NORMA_INDEF             = 0
SNORMA_INDEF            = "Norma indefinida"

NORMA_NB1_78            = 1
SNORMA_NB1_78           = "NB1-78"                      #!NTR
ANORMA_NB1_78           = "NB1-78"                      #!NTR

NORMA_NBR_6118_2003     = 2
SNORMA_NBR_6118_2003    = "NBR-6118:2003"               #!NTR
ANORMA_NBR_6118_2003    = "NBR-6118-2003"               #!NTR

NORMA_NBR_6118_2014     = 3
SNORMA_NBR_6118_2014    = "NBR-6118:2014"               #!NTR
ANORMA_NBR_6118_2014    = "NBR-6118-2014"               #!NTR

NORMA_CIRSOC            = 4
SNORMA_CIRSOC           = "CIRSOC-2005"                #!NTR
ANORMA_CIRSOC           = "CIRSOC-2005"                #!NTR

NORMA_ACI_318_05        = 5
SNORMA_ACI_318_05       = "ACI-318-05"                 #!NTR
ANORMA_ACI_318_05       = "ACI-318-05"                 #!NTR

NORMA_ACI_318_14        = 6
SNORMA_ACI_318_14       = "ACI-318-14"                 #!NTR
ANORMA_ACI_318_14       = "ACI-318-14"                 #!NTR
#
#        Países para escolha de isopletas e mapa de sismo
#
PAIS_INDEF              = 0
PAIS_BRASIL             = 1
PAIS_ARGENTINA          = 2
PAIS_COLOMBIA           = 3
PAIS_BOLIVIA            = 4
PAIS_EUA                = 5
PAIS_PARAGUAI           = 6
#
#        Classes de agressividade ambiental CIRSOC
#
CLAGCIRSOC_A1           = 0             # Não agressiva
CLAGCIRSOC_A2           = 1             # Moderada
CLAGCIRSOC_A3           = 2             # Quente úmido
CLAGCIRSOC_CL           = 3             # Submerso
CLAGCIRSOC_M1           = 4             # Marinho 1
CLAGCIRSOC_M2           = 5             # Marinho 2
CLAGCIRSOC_M3           = 6             # Marinho 3
CLAGCIRSOC_C1           = 7             # Gelo e degelo 1
CLAGCIRSOC_C2           = 8             # Gelo e degelo 2
CLAGCIRSOC_Q1           = 9             # Agressividade química 1
CLAGCIRSOC_Q2           = 10            # Agressividade química 2
CLAGCIRSOC_Q3           = 11            # Agressividade química 3
#
#        Classes de protensão CIRSOC
#
CLPRCIRSOC_FTU          = 0             # Ft <= 0.7xSQRT (F'c)
CLPRCIRSOC_FTT          = 1             # 0.7xSQRT (F'c) < Ft <= SQRT (F'c)
CLPRCIRSOC_FTC          = 2             # Ft > SQRT (F'c)
#
#        Prefixos de cargas
#
PREFIXOTODAS            = "TODAS"      #!NTR Todas verticais
PREFIXOPP               = "PP"         #!NTR Peso Próprio
PREFIXOPERM             = "PERM"       #!NTR Cargas permanentes
PREFIXOACID             = "ACID"       #!NTR Cargas acidentais
PREFIXOEMPU             = "EMPU"       #!NTR Empuxo
PREFIXORETR             = "RETR"       #!NTR Retração
PREFIXOSISM             = "SISM"       #!NTR Sismo
PREFIXOTEMP             = "TEMP"       #!NTR Temperatura
PREFIXOVENT             = "VENT"       #!NTR Vento
PREFIXODESA             = "DESA"       #!NTR Desaprumo
PREFIXOHIPER            = "HIPER"      #!NTR Hiperestático de protensão
PREFIXOFORALI           = "FORALI"     #!NTR Forças de alívio de protenção
PREFIXOADIC             = "ADI"        #!NTR Cargas adicionais do usuário
PREFIXOGELO             = "GELO"       #!NTR Gelo
PREFIXOFLUI             = "FLUI"       #!NTR Pressão de fluídos
PREFIXOENCH             = "ENCH"       #!NTR Cargas de enchente
PREFIXOTELH             = "TELH"       #!NTR Cargas acidentais em telhado
PREFIXOCHUV             = "CHUV"       #!NTR Chuva
PREFIXONEVE             = "NEVE"       #!NTR Neve
PREFIXOVEGE             = "VEGE"       #!NTR Vento sobre gelo

#------------------------------------------------------------------------------
#       Funções globais, sem edifício aberto
#
def BuildingContext ():
        """
        Retorna dados do contexto do edifício, se pasta atual de edifício.\n
        nprjpv          // -> Número do projeto do pavimento\n
        nprjed          // -> Número do projeto do edificio\n
        nombde          // -> Nome completo do EDIFICIO.BDE\n
        nomedi          // -> Nome do edifício\n
        nompav          // -> Nome do pavimento\n
        istat           // -> (!=0) se fora do contexto do edifício
        """
        acessol         = TQS.TQSUtil.LoadDll ("ACESSOL.DLL")
        parnprjpv       = ctypes.c_int (0)
        parnprjed       = ctypes.c_int (0)
        parnombde       = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan1         = ctypes.c_int (0)
        parnomedi       = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan2         = ctypes.c_int (0)
        parnompav       = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan3         = ctypes.c_int (0)
        paristat        = ctypes.c_int (0)
        acessol.ACLPAV  (ctypes.byref (parnprjpv), ctypes.byref (parnprjed), 
                         parnombde, argfan1, parnomedi, argfan2, parnompav, argfan3, 
                         ctypes.byref (paristat))
        nprjpv          = parnprjpv.value
        nprjed          = parnprjed.value
        nombde          = parnombde.value.decode(TQS.TQSUtil.CHARSET)
        nomedi          = parnomedi.value.decode(TQS.TQSUtil.CHARSET)
        nompav          = parnompav.value.decode(TQS.TQSUtil.CHARSET)
        istat           = paristat.value
        return          nprjpv, nprjed, nombde, nomedi, nompav, istat 

def BuildingRoot ():
        """
        Retorna a raiz geral da árvore de edifícios
        """
        parraiz         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan          = ctypes.c_int (0)
        acessol         = TQS.TQSUtil.LoadDll ("ACESSOL.DLL")
        acessol.ACLRAIZGERAL (parraiz, argfan);
        raiz            = parraiz.value.decode(TQS.TQSUtil.CHARSET)
        return          raiz

#------------------------------------------------------------------------------
#       Objeto que controla todo o edifício
#
class Building ():

    def __init__ (self, nomodelo=""):
        """
        Inicialização: recebe um parâmetro opcional com um nome\n
        de modelo "template" cadastrado
        """
        self.m_edilib   = TQS.TQSUtil.LoadDll ("NEDILIB.DLL")
        self.file       = File (self)
        self.project    = Project (self)
        self.model      = Model (self)
        self.floorsplan = FloorsPlan (self)
        self.materials  = Materials (self)
        self.covers     = Covers (self)
        self.loads      = Loads (self)
        self.management = Management (self)
        self.m_nomodelo = nomodelo
        self.m_inovo    = 1
        if              (len (nomodelo) == 0):
            self.m_edilib.EDILIB_INICIAR ()
            self.m_imodelo = 0
        else:
            parmodelo   = ctypes.c_char_p (nomodelo.encode(TQS.TQSUtil.CHARSET))
            self.m_edilib.EDILIB_INICIAR_MODELO (parmodelo)
            self.m_imodelo = 1

    def __str__(self):
        msg             = "Classe TQSBuild"
        msg             += "\n   self.m_edilib  " + str (self.m_edilib)
        msg             += "\n   self.file      " + str (self.file    )
        msg             += "\n   self.project   " + str (self.project )
        msg             += "\n   self.model     " + str (self.model   )
        msg             += "\n   self.floors    " + str (self.floorsplan)
        msg             += "\n   self.materials " + str (self.materials)
        msg             += "\n   self.covers    " + str (self.covers)
        msg             += "\n   self.loads     " + str (self.loads)
        msg             += "\n   self.management" + str (self.management)
        return          (msg)

    def _GetVarDouble (self, nomvar):
        """
        Retorna valor double da estrutura EDIFICIO
        """
        varnomvar       = ctypes.c_char_p (nomvar.encode(TQS.TQSUtil.CHARSET))
        varval          = ctypes.c_double (0.)
        self.m_edilib.EDILIB_GET_EDIF_DOUBLE (varnomvar, ctypes.byref (varval))
        return          varval.value

    def _SetVarDouble (self, nomvar, val):
        """
        Define valor double da estrutura EDIFICIO
        """
        varnomvar       = ctypes.c_char_p (nomvar.encode(TQS.TQSUtil.CHARSET))
        varval          = ctypes.c_double (val)
        self.m_edilib.EDILIB_SET_EDIF_DOUBLE (varnomvar, varval)

    def _GetVarInt (self, nomvar):
        """
        Retorna valor int da estrutura EDIFICIO
        """
        varnomvar       = ctypes.c_char_p (nomvar.encode(TQS.TQSUtil.CHARSET))
        varival         = ctypes.c_int (0)
        self.m_edilib.EDILIB_GET_EDIF_INT (varnomvar, ctypes.byref (varival))
        return          varival.value

    def _SetVarInt (self, nomvar, ival):
        """
        Define valor int da estrutura EDIFICIO
        """
        varnomvar       = ctypes.c_char_p (nomvar.encode(TQS.TQSUtil.CHARSET))
        varival         = ctypes.c_int (ival)
        self.m_edilib.EDILIB_SET_EDIF_INT (varnomvar, varival)

    def _GetVarStr (self, nomvar):
        """
        Retorna valor string da estrutura EDIFICIO
        """
        varnomvar       = ctypes.c_char_p (nomvar.encode(TQS.TQSUtil.CHARSET))
        varstr          = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_edilib.EDILIB_GET_EDIF_STR (varnomvar, varstr)
        str             = varstr.value.decode(TQS.TQSUtil.CHARSET)
        return          str

    def _SetVarStr (self, nomvar, str):
        """
        Define valor string da estrutura EDIFICIO
        """
        varnomvar       = ctypes.c_char_p (nomvar.encode(TQS.TQSUtil.CHARSET))
        varstr          = ctypes.c_char_p (str.encode(TQS.TQSUtil.CHARSET))
        self.m_edilib.EDILIB_SET_EDIF_STR (varnomvar, varstr)

    def RootFolder (self, filename):
        """
        Entra na pasta raiz de um edifício de nome filename\n
        Retorna:\n
        istat           -> (!=0) se não existe o edifício
        """
        parfilename     = ctypes.c_char_p (filename.encode(TQS.TQSUtil.CHARSET))
        self.m_edilib.EDILIB_EDIFICIO_PASTA_RAIZ (parfilename)
        nprjpv, nprjed, nombde, nomedi, nompav, istat = BuildingContext ()
        if              (istat == 0):
            if          (filename.lower () != nomedi.lower ()):
                istat   = 1
        return          istat

#------------------------------------------------------------------------------
#       Arquivos - ler e gravar edifícios
#
class File ():

    def __init__ (self, building):
        self.m_building     = building
        self.m_filename     = ""

    def Open (self, filename):
        """
        Carrega um edifício com nome filename\n
        Retorna (!=0) se não leu
        """
        self.m_filename = filename
        parfilename     = ctypes.c_char_p (filename.encode(TQS.TQSUtil.CHARSET))
        istat           = 0
        paristat        = ctypes.c_int (istat)
        self.m_building.m_edilib.EDILIB_EDIFICIO_LER (parfilename, ctypes.byref (paristat))
        istat           = paristat.value
        if              (istat == 0):
            self.m_building.m_inovo = 0
        return          (istat)

    def Save (self):
        """
        Salva o edifício atual aberto com Open\n
        Retorna (!=0) se não gravou
        """
        if              self.m_filename == "":
            TQS.TQSUtil.writef ("Não posso salvar: nome do edifício indefinido")
            return      1
        return          self.SaveAs (self.m_filename)

    def SaveAs (self, filename):
        """
        Salva um edifício com nome filename\n
        Retorna (!=0) se não gravou
        """
        self.m_filename = filename
        parfilename     = ctypes.c_char_p (filename.encode(TQS.TQSUtil.CHARSET))
        parimodelo      = ctypes.c_int (self.m_building.m_imodelo)
        iduplicar       = 0
        if              (self.m_building.m_inovo == 0):
            iduplicar   = 1
        pariduplicar    = ctypes.c_int (iduplicar)
        parnomodelo     = ctypes.c_char_p (self.m_building.m_nomodelo.encode(TQS.TQSUtil.CHARSET))
        istat           = 0
        paristat        = ctypes.c_int (istat)
        self.m_building.m_edilib.EDILIB_EDIFICIO_GRAVARMOD (parfilename, 
                            pariduplicar, parimodelo, parnomodelo, ctypes.byref (paristat))
        istat           = paristat.value
        return          (istat)

    def SuppressMessages (self, isuprimir):
        """
        Suprime mensagens no salvamento do edifício (0) Não (1) Sim
        """
        parisuprimir    = ctypes.c_int (isuprimir)
        self.m_building.m_edilib.EDILIB_EDIFICIO_SUPRIMIRMSG (parisuprimir)


#------------------------------------------------------------------------------
#       Aba gerais - identificação, títulos, tipo de estrutura
#
class Project ():

    def __init__ (self, building):
        self.m_building     = building

    @property
    def projectTitle (self):
        """
        Título do edifício
        """
        return          self.m_building._GetVarStr ("titged")#!NTR

    @projectTitle.setter
    def projectTitle (self, stitle):
        """
        Título do edifício
        """
        self.m_building._SetVarStr ("titged", stitle)#!NTR

    @property
    def clientTitle (self):
        """
        Título do cliente
        """
        return          self.m_building._GetVarStr ("cliged")#!NTR

    @clientTitle.setter
    def clientTitle (self, stitle):
        """
        Título do cliente
        """
        self.m_building._SetVarStr ("cliged", stitle)#!NTR

    @property
    def projectAddress (self):
        """
        Endereço da obra
        """
        return          self.m_building._GetVarStr ("enderobra")#!NTR

    @projectAddress.setter
    def projectAddress (self, saddress):
        """
        Endereço da obra
        """
        self.m_building._SetVarStr ("enderobra", saddress)#!NTR

    @property
    def projectNumber (self):
        """
        Número arbitrário de projeto 1..9999
        """
        return          self.m_building._GetVarInt ("nprjed")#!NTR

    @projectNumber.setter
    def projectNumber (self, nprj):
        """
        Número arbitrário de projeto 1..9999
        """
        self.m_building._SetVarInt ("nprjed", nprj)#!NTR

    @property
    def blueprintPrefix (self):
        """
        Prefixo arbitrário para plantas plotadas
        """
        return          self.m_building._GetVarStr ("prefedipla")#!NTR

    @blueprintPrefix.setter
    def blueprintPrefix (self, sprefix):
        """
        Prefixo arbitrário para plantas plotadas
        """
        self.m_building._SetVarStr ("prefedipla", sprefix)#!NTR

    @property
    def projectDescription (self):
        """
        Descrição do projeto
        """
        return          self.m_building._GetVarStr ("descricao")#!NTR

    @projectDescription.setter
    def projectDescription (self, sdescription):
        """
        Descrição do projeto
        """
        self.m_building._SetVarStr ("descricao", sdescription)#!NTR

    @property
    def structureType (self):
        """
        Tipo da estrutura\n
        (0) Concreto armado/protendido\n
        (1) Concreto pré-moldado\n
        (2) Alvenaria estrutural\n
        (3) Paredes de concreto
        """
        itype           = -1
        ialvened        = self.m_building._GetVarInt ("ialvened")#!NTR
        if              ialvened == 0:
            varipremold = ctypes.c_int (0)
            self.m_building.m_edilib.EDILIB_ECP_GET_IPREMOLD (ctypes.byref (varipremold))
            ipremold    = varipremold.value
            if          ipremold == 0:
                itype   = 0
            else:
                itype   = 1
        elif            ialvened == 1:
            itype       = 2
        elif            ialvened == 2:
            itype       = 3
        return          itype


    @structureType.setter
    def structureType (self, itype):
        """
        Tipo da estrutura\n
        (0) Concreto armado/protendido\n
        (1) Concreto pré-moldado\n
        (2) Alvenaria estrutural\n
        (3) Paredes de concreto
        """
        if              itype == 0:
            self.m_building._SetVarInt ("ialvened", 0)#!NTR
            varipremold = ctypes.c_int (0)
            self.m_building.m_edilib.EDILIB_ECP_SET_IPREMOLD (varipremold)

        elif            itype == 1:
            self.m_building._SetVarInt ("ialvened", 0)#!NTR
            varipremold = ctypes.c_int (1)
            self.m_building.m_edilib.EDILIB_ECP_SET_IPREMOLD (varipremold)

        elif            itype == 2:
            self.m_building._SetVarInt ("ialvened", 1)#!NTR
            varipremold = ctypes.c_int (0)
            self.m_building.m_edilib.EDILIB_ECP_SET_IPREMOLD (varipremold)
    
        elif            itype == 3:
            self.m_building._SetVarInt ("ialvened", 2)#!NTR
            varipremold = ctypes.c_int (0)
            self.m_building.m_edilib.EDILIB_ECP_SET_IPREMOLD (varipremold)

    @property
    def formworkActive (self):
        """
        (1) Se com projeto de formas de madeira
        """
        return          self.m_building._GetVarInt ("icrmed")#!NTR

    @formworkActive.setter
    def formworkActive (self, iactive):
        """
        (1) Se com projeto de formas de madeira
        """
        self.m_building._SetVarInt ("icrmed", iactive)#!NTR

    @property
    def concreteCode (self):
        """
        Norma de concreto TQSBuild.NORMA_xxxx
        """
        varinorma       = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_NORMACONCR (ctypes.byref (varinorma))
        return          varinorma.value

    @concreteCode.setter
    def concreteCode (self, icode):
        """
        Norma de concreto TQSBuild.NORMA_xxxx
        """
        varinorma       = ctypes.c_int (icode)
        self.m_building.m_edilib.EDILIB_SET_NORMACONCR (varinorma)

    @property
    def masonryCode (self):
        """
        Norma de alvenaria estrutural TQSBuild.NORMALVI_xxxx
        """
        return          self.m_building._GetVarInt ("inormalven")#!NTR

    @masonryCode.setter
    def masonryCode (self, icode):
        """
        Norma de alvenaria estrutural TQSBuild.NORMALVI_xxxx
        """
        self.m_building._SetVarInt ("inormalven", icode)#!NTR

    @property
    def concreteWallsCode (self):
        """
        Norma de paredes de concreto TQSBuild.NORMAPAREDI_xxxx
        """
        return          self.m_building._GetVarInt ("inormaparede")#!NTR

    @concreteWallsCode.setter
    def concreteWallsCode (self, icode):
        """
        Norma de paredes de concreto TQSBuild.NORMAPAREDI_xxxx
        """
        self.m_building._SetVarInt ("inormaparede", icode)#!NTR

    @property
    def codeStrictUse (self):
        """
        (1) Se forçar o uso de critérios de norma
        """
        return          self.m_building._GetVarInt ("iforcarnorma")#!NTR

    @codeStrictUse.setter
    def codeStrictUse (self, iforcecode):
        """
        (1) Se forçar o uso de critérios de norma
        """
        self.m_building._SetVarInt ("iforcarnorma", iforcecode)#!NTR

    @property
    def floorHeight (self):
        """
        Cota inicial da planta (m)
        """
        return          self.m_building._GetVarDouble ("cotied")

    @floorHeight.setter
    def floorHeight (self, height):
        """
        Cota inicial da planta (m)
        """
        self.m_building._SetVarDouble ("cotied", height)#!NTR

    @property
    def country (self):
        """
        País TQSBuild.PAIS_xxx
        """
        icountry        = self.m_building._GetVarInt ("ipais")#!NTR
        return          icountry

    @country.setter
    def country (self, icountry):
        """
        País TQSBuild.PAIS_xxx
        """
        self.m_building._SetVarInt ("ipais", icountry)#!NTR

    def GetSpacePath (self):
        """
        Retorna o path da pasta espacial
        """
        pardirespac     = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_DIRESPACIAL (pardirespac)
        direspac        = pardirespac.value.decode(TQS.TQSUtil.CHARSET)
        return          (direspac)

        return          drpoed

    def SetSpacePath (self, drpoed):
        """
        Define o path da pasta espacial
        """
        self.m_building._SetVarStr ("drpoed", drpoed)#!NTR

#------------------------------------------------------------------------------
#       Aba Modelo - Modelo de cálculo, vigas de transição, etc
#
class Model ():

    def __init__ (self, building):
        self.m_building   = building
        self.precastmodel = PrecastModel (building, self)

    @property
    def structuralModel (self):
        """
        Modelo IV (TQSBuild.PORTICO_HORVER) ou Modelo VI (TQSBuild.PORTICO_LAJES)
        """
        return          self.m_building._GetVarInt ("ipored")#!NTR

    @structuralModel.setter
    def structuralModel (self, imodel):
        """
        Modelo IV (TQSBuild.PORTICO_HORVER) ou Modelo VI (TQSBuild.PORTICO_LAJES)
        """
        self.m_building._SetVarInt ("ipored", imodel)#!NTR

    @property
    def expansionJoints (self):
        """
        (0) Estrutura única (1) Duas ou mais estruturas separadas por junta de dilatação
        """
        return          self.m_building._GetVarInt ("iduastoujunta")#!NTR

    @expansionJoints.setter
    def expansionJoints (self, ijoints):
        """
        (0) Estrutura única (1) Duas ou mais estruturas separadas por junta de dilatação
        """
        self.m_building._SetVarInt ("iduastoujunta", ijoints)#!NTR

    @property
    def transferBeamModel (self):
        """
        (1) Dois modelos com vigas de transição: inércia enrijecida e inércia real
        """
        return          self.m_building._GetVarInt ("ienvted")#!NTR

    @transferBeamModel.setter
    def transferBeamModel (self, ienvted):
        """
        (1) Dois modelos com vigas de transição: inércia enrijecida e inércia real
        """
        self.m_building._SetVarInt ("ienvted", ienvted)#!NTR

    @property
    def transferBeamModelInertiaMultiplier (self):
        """
        Para modelo de viga de transição enrijecida, o multiplicador de inércia à flexão
        """
        return          self.m_building._GetVarDouble ("vmuletr")

    @transferBeamModelInertiaMultiplier.setter
    def transferBeamModelInertiaMultiplier (self, muletr):
        """
        Para modelo de viga de transição enrijecida, o multiplicador de inércia à flexão
        """
        self.m_building._SetVarDouble ("vmuletr", muletr)#!NTR

    @property
    def transferBemModelPolarInertiaDivider (self):
        """
        Para modelo de viga de transição enrijecida, o divisor da inércia à torção
        """
        return          self.m_building._GetVarDouble ("redtorvtrn")

    @transferBemModelPolarInertiaDivider.setter
    def transferBemModelPolarInertiaDivider (self, redtor):
        """
        Para modelo de viga de transição enrijecida, o divisor da inércia à torção
        """
        self.m_building._SetVarDouble ("redtorvtrn", redtor)#!NTR

    @property
    def secondOrderEfect (self):
        """
        Efeitos globais de segunda ordem calculados por (0) GamaZ (1) P-Delta
        """
        return          self.m_building._GetVarInt ("icalcpdelta")#!NTR

    @secondOrderEfect.setter
    def secondOrderEfect (self, ipdelta):
        """
        Efeitos globais de segunda ordem calculados por (0) GamaZ (1) P-Delta
        """
        self.m_building._SetVarInt ("icalcpdelta", ipdelta)#!NTR

    @property
    def structuralDynamicsAnalysis (self):
        """
        (0) Análise estática (1) Análise dinâmica da estrutura
        """
        return          self.m_building._GetVarInt ("idinamicapor")#!NTR

    @structuralDynamicsAnalysis.setter
    def structuralDynamicsAnalysis (self, idynamic):
        """
        (0) Análise estática (1) Análise dinâmica da estrutura
        """
        self.m_building._SetVarInt ("idinamicapor", idynamic)#!NTR

    @property
    def soilStructureInteraction (self):
        """
        (1) Se integrado ao sistema de interação solo estruturas SISEs
        """
        return          self.m_building._GetVarInt ("intsises")#!NTR

    @soilStructureInteraction.setter
    def soilStructureInteraction (self, isises):
        """
        (1) Se integrado ao sistema de interação solo estruturas SISEs
        """
        self.m_building._SetVarInt ("intsises", isises)#!NTR

    @property
    def soilStructureIntegrateFoundations (self):
        """
        (1) Agregar a fundação discretizada no SISEs no pórtico espacial
        """
        return          self.m_building._GetVarInt ("intsisespor")#!NTR

    @soilStructureIntegrateFoundations.setter
    def soilStructureIntegrateFoundations (self, isisespor):
        """
        (1) Agregar a fundação discretizada no SISEs no pórtico espacial
        """
        self.m_building._SetVarInt ("intsisespor", isisespor)#!NTR

    @property
    def incrementalAnalysis (self):
        """
        (1) Analisar a estrutura considerando efeito incremental
        """
        return          self.m_building._GetVarInt ("iefeitoincrem")#!NTR

    @incrementalAnalysis.setter
    def incrementalAnalysis (self, incremental):
        """
        (1) Analisar a estrutura considerando efeito incremental
        """
        self.m_building._SetVarInt ("iefeitoincrem", incremental)#!NTR

#------------------------------------------------------------------------------
#       Modelo de Pré-Moldados
#
class PrecastModel ():

    def __init__ (self, building, model):
        self.m_building      = building
        self.m_model         = model

    def _GetEtapas (self):
        varnumetapas    = ctypes.c_int (0)
        varnumregioes   = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_ECP_GET_ETAPAS (ctypes.byref (varnumetapas),
                        ctypes.byref (varnumregioes))
        numetapas       = varnumetapas.value
        numregioes      = varnumregioes.value
        return          numetapas, numregioes

    def _SetEtapas (self, numetapas, numregioes):
        varnumetapas    = ctypes.c_int (numetapas)
        varnumregioes   = ctypes.c_int (numregioes)
        self.m_building.m_edilib.EDILIB_ECP_SET_ETAPAS (varnumetapas, varnumregioes)

    def Clear (self):
        """
        Limpa a lista de etapas e regiões construtivas
        """
        self.m_building.EDILIB_ECP_LIMPAR ()

    @property
    def stagesNumber (self):
        """
        Número de etapas construtivas de estrutura pré-moldada
        """
        numetapas, numregioes = self._GetEtapas ()
        return          numetapas

    @stagesNumber.setter
    def stagesNumber (self, numstages):
        """
        Número de etapas construtivas de estrutura pré-moldada
        """
        numetapas, numregioes = self._GetEtapas ()
        self._SetEtapas (numstages, numregioes)

    @property
    def regionsNumber (self):
        """
        Número de regiões construtivas de estrutura pré-moldada
        """
        numetapas, numregioes = self._GetEtapas ()
        return          numregioes

    @regionsNumber.setter
    def regionsNumber (self, numregions):
        """
        Número de regiões construtivas de estrutura pré-moldada
        """
        numetapas, numregioes = self._GetEtapas ()
        self._SetEtapas (numetapas, numregions)

    def GetFloor(self, istage, iregion):
        """
        Retorna para uma etapa e região, até que piso será construído e até\n
        que piso será solidarizado\n
        istage                  <- Etapa construtiva  0..stagesNumber-1\n
        iregion                 <- Região construtiva 0..regionsNumber-1\n
        Retorna:\n
        ifloor                  -> Piso até onde será construído\n
        ifloormonolithic        -> Piso até onde será solidarizado
        """
        varistage       = ctypes.c_int (istage)
        variregion      = ctypes.c_int (iregion)
        varipisof       = ctypes.c_int (0)
        varipisosoli    = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_ECP_GET_ETAPA (varistage, variregion,
                       ctypes.byref (varipisof), ctypes.byref (varipisosoli))
        ipisof          = varipisof.value
        ipisosoli       = varipisosoli.value
        return          ipisof, ipisosoli

    def SetFloor(self, istage, iregion, ifloor, ifloormonolithic):
        """
        Define para uma etapa e região, até que piso será construído e até\n
        que piso será solidarizado\n
        istage                  <- Etapa construtiva  0..stagesNumber-1\n
        iregion                 <- Região construtiva 0..regionsNumber-1\n
        ifloor                  <- Piso até onde será construído\n
        ifloormonolithic        <- Piso até onde será solidarizado
        """
        varistage       = ctypes.c_int (istage)
        variregion      = ctypes.c_int (iregion)
        varipisof       = ctypes.c_int (ifloor)
        varipisosoli    = ctypes.c_int (ifloormonolithic)
        self.m_building.m_edilib.EDILIB_ECP_SET_ETAPA (varistage, variregion,
                       varipisof, varipisosoli)
        
#------------------------------------------------------------------------------
#       Aba Pavimentos - Definição de pavimentos e dados de pavimento
#
class FloorsPlan ():

    def __init__ (self, building):
        self.m_building = building

    def GetFloorsNumber (self):
        """
        Retorna o número de pisos. É diferente do número de plantas, pois uma planta\n
        pode ter repetições.
        """
        varnumpisos     = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_NUMPISOS (ctypes.byref (varnumpisos))
        numpisos        = varnumpisos.value
        return          numpisos

    @property
    def floorsPlanNumber (self):
        """
        Número de plantas. Plantas com repetição são uma única planta.\n
        """
        varnumplantas   = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_PLANTAS_NUMPLANTAS (ctypes.byref (varnumplantas))
        numplantas      = varnumplantas.value
        return          numplantas

    def Clear (self):
        """
        Elimina todas as plantas do edifício
        """
        self.m_building.m_edilib.EDILIB_PLANTAS_LIMPAR ()

    def Create (self, ipla):
        """
        Cria nova planta de índice ipla com base zero\n
        ipla            Índice da planta com base zero
        """
        varipla         = ctypes.c_int (ipla)
        self.m_building.m_edilib.EDILIB_PLANTAS_CRIAR (varipla);

    def CreateAbove (self, nompla, pd, iclass):
        """
        Cria uma planta acima de todas as outras. Define nome e pé-direito\n
        nompla          (string) Nome e título da planta\n
        pd              Altura da planta (m)\n
        iclass          Classe do piso ICLxxx
       """
        varnompla       = ctypes.c_char_p (nompla.encode(TQS.TQSUtil.CHARSET))
        varpd           = ctypes.c_double (pd)
        variclass       = ctypes.c_int (iclass)
        self.m_building.m_edilib.EDILIB_PLANTAS_CRIAR_ACIMA (varnompla, varpd, variclass)

    def Erase (self, ipla):
        """
        Apaga a planta ipla (0..floorsPlanNumber-1)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)
        """
        varipla         = ctypes.c_int (ipla)
        self.m_building.m_edilib.EDILIB_PLANTAS_APAGAR (varipla);

    def GetRepetition (self, ipla):
        """
        Retorna o número de repetições de uma planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        irep            Número de repetições da planta
        """
        varipla         = ctypes.c_int (ipla)
        varirep         = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_NPISSC (varipla, ctypes.byref (varirep))
        irep            = varirep.value
        return          irep

    def SetRepetition (self, ipla, irep):
        """
        Define o número de projeto da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        irep            Número de repetições da planta
        """
        varipla         = ctypes.c_int (ipla)
        varirep         = ctypes.c_int (irep)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_NPISSC (varipla, varirep)

    def GetFloorHeight (self, ipla):
        """
        Retorna a diferença de cota entre a planta atual e a de baixo (m)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        pd              Altura da planta
        """
        varipla         = ctypes.c_int (ipla)
        varpedrsc       = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_PEDRSC (varipla, ctypes.byref (varpedrsc))
        pedrsc          = varpedrsc.value
        return          pedrsc

    def SetFloorHeight (self, ipla, pd):
        """
        Retorna a diferença de cota entre a planta atual e a de baixo (m)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        pd              Altura da planta (m)
        """
        varipla         = ctypes.c_int (ipla)
        varpedrsc       = ctypes.c_double (pd)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_PEDRSC (varipla, varpedrsc)

    def GetClass (self, ipla):
        """
        Retorna a classe de uma planta do tipo TQSBuild.ICLxxx\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        iclass          Classe tipo TQSBuild.ICLxxx
        """
        varipla         = ctypes.c_int (ipla)
        variclass       = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_ICLASC (varipla, ctypes.byref (variclass))
        iclass          = variclass.value
        return          iclass

    def SetClass (self, ipla, iclass):
        """
        Define a classe de uma planta do tipo TQSBuild.ICLxxx\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        iclass          Classe tipo TQSBuild.ICLxxx
        """
        varipla         = ctypes.c_int (ipla)
        variclass       = ctypes.c_int (iclass)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_ICLASC (varipla, variclass)

    def GetProjectNumber (self, ipla):
        """
        Retorna o número de projeto\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        nprj            Número do projeto da planta
        """
        varipla         = ctypes.c_int (ipla)
        varnprj         = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_NPRPLA (varipla, ctypes.byref (varnprj))
        nprj            = varnprj.value
        return          nprj

    def SetProjectNumber (self, ipla, nprj):
        """
        Define o número de projeto da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        nprj            Número arbitrário de projeto da planta. Usado em alguns nomes de arquivos.
        """
        varipla         = ctypes.c_int (ipla)
        varnprj         = ctypes.c_int (nprj)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_NPRPLA (varipla, varnprj)

    def GetName (self, ipla):
        """
        Retorna o nome da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        sname           Nome da planta. Usado também como nome da pasta dos arquivos da planta
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TNMPLA (varipla, varname)
        sname           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          sname

    def SetName (self, ipla, sname):
        """
        Define o nome da planta. \n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        sname           Nome da planta. Usado também como nome da pasta dos arquivos da planta
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (sname.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TNMPLA (varipla, varname)

    def GetDescription (self, ipla):
        """
        Retorna a descrição da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        sdescription    Descrição da planta
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TITPLA (varipla, varname)
        sname           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          sname

    def SetDescription (self, ipla, sdescription):
        """
        Define a descrição da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        sdescription    Descrição da planta
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (sdescription.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TITPLA (varipla, varname)

    def GetFloorPath (self, ipla):
        """
        Retorna a pasta da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DIRPLA (varipla, varname)
        spath           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          spath

    def SetFloorPath (self, ipla, path):
        """
        Define a pasta da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        path            Pasta/diretório\n
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (path.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DIRPLA (varipla, varname)

    def GetBeamsPath (self, ipla):
        """
        Retorna a pasta de vigas se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DIVPLA (varipla, varname)
        spath           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          spath

    def SetBeamsPath (self, ipla, path):
        """
        Define a pasta de vigas se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        path            Pasta/diretório\n
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (path.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DIVPLA (varipla, varname)

    def GetFormworkPath (self, ipla):
        """
        Retorna a pasta de madeira se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DIMPLA (varipla, varname)
        spath           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          spath

    def SetFormworkPath (self, ipla, path):
        """
        Define a pasta de madeira se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (path.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DIMPLA (varipla, varname)


    def GetMasonryPath (self, ipla):
        """
        Retorna a pasta de alvenaria estrutural se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DIAPLA (varipla, varname)
        spath           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          spath

    def SetMasonryPath (self, ipla, path):
        """
        Define a pasta de alvenaria estrutural se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (path.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DIAPLA (varipla, varname)

    def GetStairsPath (self, ipla):
        """
        Retorna a pasta de escadas se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DIRESC (varipla, varname)
        spath           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          spath

    def SetStairsPath (self, ipla, path):
        """
        Define a pasta de escadas se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (path.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DIRESC (varipla, varname)


    def GetOthersPath (self, ipla):
        """
        Retorna a pasta de elementos especiais se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DRESPECIAIS (varipla, varname)
        spath           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          spath

    def SetOthersPath (self, ipla, path):
        """
        Define a pasta de elementos especiais se diferente do padrão\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        path            Pasta/diretório
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (path.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DRESPECIAIS (varipla, varname)

    def GetTitle (self, ipla):
        """
        Retorna a o título da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        stitle          Título da planta
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TITPSC (varipla, varname)
        sname           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          sname

    def SetTitle (self, ipla, stitle):
        """
        Define a o título da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        stitle          Título da planta\n
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (stitle.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TITPSC (varipla, varname)

    def GetBlueprintPrefix (self, ipla):
        """
        Retorna o prefixo de plantas \n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        sprefix         Prefixo opcional para a planta nos layouts de plotagem
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_PREFPAVPLA (varipla, varname)
        sname           = varname.value.decode(TQS.TQSUtil.CHARSET)
        return          sname

    def SetBlueprintPrefix (self, ipla, sprefix):
        """
        Define o prefixo de plantas \n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        sprefix         Prefixo opcional para a planta nos layouts de plotagem
        """
        varipla         = ctypes.c_int (ipla)
        varname         = ctypes.c_char_p (sprefix.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_PREFPAVPLA (varipla, varname)

    def GetPlaneFrameModel (self, ipla):
        """
        Retorna o modelo estrutural da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        igrpla          Modelo estrutural tipo TQSBuild.GRELHA_xxxx
        """
        varipla         = ctypes.c_int (ipla)
        varigrpla       = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_IGRPLA (varipla, ctypes.byref (varigrpla))
        igrpla          = varigrpla.value
        return          igrpla

    def SetPlaneFrameModel (self, ipla, igrpla):
        """
        Define o modelo estrutural da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        igrpla          Modelo estrutural tipo TQSBuild.GRELHA_xxxx
        """
        varipla         = ctypes.c_int (ipla)
        varigrpla       = ctypes.c_int (igrpla)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_IGRPLA (varipla, varigrpla)

    def GetPreStressed (self, ipla):
        """
        Retorna se o pavimento é protendido\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        iprpla          (1) Se o pavimento é protendido
        """
        varipla         = ctypes.c_int (ipla)
        variprpla       = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_IPRPLA (varipla, ctypes.byref (variprpla))
        iprpla          = variprpla.value
        return          iprpla

    def SetPreStressed (self, ipla, iprpla):
        """
        Define o modelo de grelha\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        iprpla          (1) Se o pavimento é protendido
        """
        varipla         = ctypes.c_int (ipla)
        variprpla       = ctypes.c_int (iprpla)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_IPRPLA (varipla, variprpla)

    def GetTemperatureAnalysis (self, ipla):
        """
        Retorna se o pavimento é calculado com carregamento de temperatura\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        itemper         (1) Definida por elemento no Modelador (2) Uniforme na planta
        """
        varipla         = ctypes.c_int (ipla)
        varitemper       = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_ITEMPER (varipla, ctypes.byref (varitemper))
        itemper          = varitemper.value
        return          itemper

    def SetTemperatureAnalysis (self, ipla, itemper):
        """
        Define se o pavimento é calculado com carregamento de temperatura\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        itemper         (1) Definida por elemento no Modelador (2) Uniforme na planta\n
        """
        varipla         = ctypes.c_int (ipla)
        varitemper      = ctypes.c_int (itemper)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_ITEMPER (varipla, varitemper)

    def GetTemperatureTransVariation (self, ipla):
        """
        Retorna o valor da variação transversal de temperatura uniforme na planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        temvartra       Variação transversal de temperatura uniforme na planta em graus
        """
        varipla         = ctypes.c_int (ipla)
        vartemvartra    = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TEMVARTRA (varipla, ctypes.byref (vartemvartra))
        temvartra       = vartemvartra.value
        return          temvartra

    def SetTemperatureTransVariation (self, ipla, temvartra):
        """
        Define o valor da variação transversal de temperatura uniforme na planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        temvartra       Variação transversal de temperatura uniforme na planta em graus\n
        """
        varipla         = ctypes.c_int (ipla)
        vartemvartra    = ctypes.c_double (temvartra)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TEMVARTRA (varipla, vartemvartra)

    def GetTemperatureLongVariation (self, ipla):
        """
        Retorna o valor da variação longitudina de temperatura uniforme na planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        temvarlon       Variação longitudinal de temperatura uniforme na planta em graus
        """
        varipla         = ctypes.c_int (ipla)
        vartemvarlon    = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TEMVARLON (varipla, ctypes.byref (vartemvarlon))
        temvarlon       = vartemvarlon.value
        return          temvarlon

    def SetTemperatureLongVariation (self, ipla, temvarlon):
        """
        Define o valor da variação longitudina de temperatura uniforme na planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        temvarlon       Variação longitudinal de temperatura uniforme na planta em graus
        """
        varipla         = ctypes.c_int (ipla)
        vartemvarlon    = ctypes.c_double (temvarlon)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TEMVARLON (varipla, vartemvarlon)

    def GetTemperatureAnalysis2 (self, ipla):
        """
        Retorna se o pavimento tem um segundo caso de temperatura definido\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        itemper2        (1) Segundo caso de temperatura definido
        """
        varipla         = ctypes.c_int (ipla)
        varitemper2     = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_ITEMPER2 (varipla, ctypes.byref (varitemper2))
        itemper2        = varitemper2.value
        return          itemper2

    def SetTemperatureAnalysis2 (self, ipla, itemper2):
        """
        Define se o pavimento tem um segundo caso de temperatura definido\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        itemper2        (1) Segundo caso de temperatura definido
        """
        varipla         = ctypes.c_int (ipla)
        varitemper2     = ctypes.c_int (itemper2)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TEMVARTRA2 (varipla, varitemper2)

    def GetTemperatureTransVariation2 (self, ipla):
        """
        Retorna o valor da variação transversal do segundo caso de temperatura\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        temvartra2      Variação transversal de temperatura do segundo caso
        """
        varipla         = ctypes.c_int (ipla)
        vartemvartra2   = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TEMVARTRA2 (varipla, ctypes.byref (vartemvartra2))
        temvartra2      = vartemvartra2.value
        return          temvartra2

    def SetTemperatureTransVariation2 (self, ipla, temvartra2):
        """
        Define o valor da variação transversal do segundo caso de temperatura\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        temvartra2      Variação transversal de temperatura do segundo caso
        """
        varipla         = ctypes.c_int (ipla)
        vartemvartra2   = ctypes.c_double (temvartra2)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TEMVARTRA2 (varipla, vartemvartra2)

    def GetTemperatureLongVariation2 (self, ipla):
        """
        Retorna o valor da variação longitudina do segundo caso de temperatura\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        temvarlon2      Variação longitudinal de temperatura do segundo caso43
        """
        varipla         = ctypes.c_int (ipla)
        vartemvarlon2   = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_TEMVARLON2 (varipla, ctypes.byref (vartemvarlon2))
        temvarlon2      = vartemvarlon2.value
        return          temvarlon2

    def SetTemperatureLongVariation2 (self, ipla, temvarlon2):
        """
        Define o valor da variação longitudina do segundo caso de temperatura\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        temvarlon2      Variação longitudinal de temperatura do segundo caso
        """
        varipla         = ctypes.c_int (ipla)
        vartemvarlon2   = ctypes.c_double (temvarlon2)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_TEMVARLON2 (varipla, vartemvarlon2)

    def GetShrinkageAnalysis (self, ipla):
        """
        Retorna se o pavimento é calculado com carregamento de retração\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        ishrink         (1) Definida por elemento no Modelador (2) Uniforme na planta
        """
        varipla         = ctypes.c_int (ipla)
        varishrink      = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_IRETRACAO (varipla, ctypes.byref (varishrink))
        ishrink         = varishrink.value
        return          ishrink

    def SetShrinkageAnalysis (self, ipla, ishrink):
        """
        Define se o pavimento é calculado com carregamento de retração\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        ishrink         (1) Definida por elemento no Modelador (2) Uniforme na planta
        """
        varipla         = ctypes.c_int (ipla)
        varishrink      = ctypes.c_int (ishrink)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_IRETRACAO (varipla, varishrink)

    def GetShrinkageVariation (self, ipla):
        """
        Retorna se o pavimento é calculado com carregamento de retração\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        shrinkage       Variação transversal de temperatura equivalente em graus 
        """
        varipla         = ctypes.c_int (ipla)
        varshrinkage    = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_RETRVAR (varipla, ctypes.byref (varshrinkage))
        shrinkage       = varshrinkage.value
        return          shrinkage

    def SetShrinkageVariation (self, ipla, shrinkage):
        """
        Define se o pavimento é calculado com carregamento de retração\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        shrinkage       Variação transversal de temperatura equivalente em graus 
        """
        varipla         = ctypes.c_int (ipla)
        varshrinkage    = ctypes.c_double (shrinkage)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_RETRVAR (varipla, varshrinkage)

    def GetDegreesOfFreddom (self, ipla):
        """
        Retorna se o tipo de modelo de grelha da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        iporgre         (0) Automático (1) 3 graus de liberdade (2) 6 graus de liberdade
        """
        varipla         = ctypes.c_int (ipla)
        variporgre      = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_IPORGRE (varipla, ctypes.byref (variporgre))
        iporgre         = variporgre.value
        return          iporgre

    def SetDegreesOfFreddom (self, ipla, iporgre):
        """
        Define se o pavimento é calculado com carregamento de retração\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        iporgre         (0) Automático (1) 3 graus de liberdade (2) 6 graus de liberdade
        """
        varipla         = ctypes.c_int (ipla)
        variporgre      = ctypes.c_int (iporgre)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_IPORGRE (varipla, variporgre)

    def GetVehicleLoad (self, ipla):
        """
        Retorna se o tipo de modelo de grelha da planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        ipavveic        Veículos (0)não (1)<= 30kN (2)>30kN
        """
        varipla         = ctypes.c_int (ipla)
        varipavveic     = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_IPAVVEIC (varipla, ctypes.byref (varipavveic))
        ipavveic        = varipavveic.value
        return          ipavveic

    def SetVehicleLoad (self, ipla, ipavveic):
        """
        Define se o pavimento é calculado com carregamento de retração\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        ipavveic        Veículos (0)não (1)<= 30kN (2)>30kN
        """
        varipla         = ctypes.c_int (ipla)
        varipavveic     = ctypes.c_int (ipavveic)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_IPAVVEIC (varipla, varipavveic)

    def GetSlopedElements (self, ipla):
        """
        Retorna (1) se a planta contém elementos inclinados\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        islopedelem     (1) se a planta contém elementos inclinados
        """
        varipla         = ctypes.c_int (ipla)
        varislopedelem  = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_IELEMINCLIN (varipla, 
                            ctypes.byref (varislopedelem))
        islopedelem     = varislopedelem.value
        return          islopedelem

    def SetSlopedElements (self, ipla, islopedelem):
        """
        Retorna (1) se a planta contém elementos inclinados\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        islopedelem     (1) se a planta contém elementos inclinados
        """
        varipla         = ctypes.c_int (ipla)
        varislopedelem  = ctypes.c_int (islopedelem)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_IELEMINCLIN (varipla, varislopedelem)

    def GetAuxiliaryFloorsNumber (self, ipla):
        """
        Retorna o número de pisos auxiliares associados à esta planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        numfloors       Número de pisos auxiliares
        """
        varipla         = ctypes.c_int (ipla)
        varnumfloors    = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_NUMDFSPISO (varipla, ctypes.byref (varnumfloors))
        numfloors          = varnumfloors.value
        return          numfloors

    def SetAuxiliaryFloorsNumber (self, ipla, numfloors):
        """
        Define o número de pisos auxiliares associados à esta planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        numfloors       Número de pisos auxiliares
        """
        varipla         = ctypes.c_int (ipla)
        varnumfloors    = ctypes.c_int (numfloors)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_NUMDFSPISO (varipla, varnumfloors)

    def GetAuxiliaryFloorUnderneath (self, ipla, ifloor):
        """
        Retorna o rebaixo de um piso auxiliar (m)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        ifloor          Índice do piso auxiliar (0..GetAuxiliaryFloorsNumber-1)\n
        Retorna:\n
        undereneath     Rebaixo do piso undereneath (m)
        """
        varipla         = ctypes.c_int (ipla)
        varifloor       = ctypes.c_int (ifloor)
        varundereneath  = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_DFSPISO (varipla, varifloor,
                            ctypes.byref (varundereneath))
        undereneath     = varundereneath.value
        return          undereneath

    def SetAuxiliaryFloorUnderneath (self, ipla, ifloor, undereneath):
        """
        Define o rebaixo de um piso auxiliar (m)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        ifloor          Índice do piso auxiliar (0..GetAuxiliaryFloorsNumber-1)\n
        undereneath     Rebaixo do piso undereneath (m)
        """
        varipla         = ctypes.c_int (ipla)
        varifloor       = ctypes.c_int (ifloor)
        varundereneath  = ctypes.c_double (undereneath)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_DFSPISO (varipla, varifloor, varundereneath)

#------------------------------------------------------------------------------
#       Aba Materiais - principalmente concreto
#
class Materials ():

    def __init__ (self, building):
        self.m_building      = building
        self.precast         = PrecastMaterials (building, self)

    @property
    def disableConcreteCheck (self):
        """
        (1) Para desativar verificação do fck mínimo
        """
        return          self.m_building._GetVarInt ("idesativarverfck")#!NTR

    @disableConcreteCheck.setter
    def disableConcreteCheck (self, idisable):
        """
        (1) Para desativar verificação do fck mínimo
        """
        self.m_building._SetVarInt ("idesativarverfck", idisable)#!NTR

    @property
    def environmentalClass (self):
        """
        Classe de agressividade I..IV (valores 0..3)
        """
        return          self.m_building._GetVarInt ("iclagress")#!NTR

    @environmentalClass.setter
    def environmentalClass (self, ienvclass):
        """
        Classe de agressividade I..IV (valores 0..3)
        """
        self.m_building._SetVarInt ("iclagress", ienvclass)#!NTR

    @property
    def dryClimate (self):
        """
        (1) Se clima seco
        """
        return          self.m_building._GetVarInt ("iclimaseco")#!NTR

    @dryClimate.setter
    def dryClimate (self, idryclimate):
        """
        (1) Se clima seco
        """
        self.m_building._SetVarInt ("iclimaseco", idryclimate)#!NTR

    @property
    def qualityControl (self):
        """
        (1) Se concreto realizado com controle de qualidade
        """
        return          self.m_building._GetVarInt ("icontrolqual")#!NTR

    @qualityControl.setter
    def qualityControl (self, iqualitycontrol):
        """
        (1) Se concreto realizado com controle de qualidade
        """
        self.m_building._SetVarInt ("icontrolqual", iqualitycontrol)#!NTR


    @property
    def beamConcreteStrength (self):
        """
        Concreto de vigas e lajes
        """
        return          self.m_building._GetVarStr ("fckved_tit")#!NTR

    @beamConcreteStrength.setter
    def beamConcreteStrength (self, sfck):
        """
        Concreto de vigas e lajes
        """
        self.m_building._SetVarStr ("fckved_tit", sfck)#!NTR

    @property
    def columnConcreteStrength (self):
        """
        Concreto de pilares
        """
        return          self.m_building._GetVarStr ("fckpdf_tit")#!NTR

    @columnConcreteStrength.setter
    def columnConcreteStrength (self, sfck):
        """
        Concreto de pilares
        """
        self.m_building._SetVarStr ("fckpdf_tit", sfck)#!NTR

    @property
    def foundationConcreteStrength (self):
        """
        Concreto de fundações
        """
        return          self.m_building._GetVarStr ("fckfed_tit")#!NTR

    @foundationConcreteStrength.setter
    def foundationConcreteStrength (self, sfck):
        """
        Concreto de fundações
        """
        self.m_building._SetVarStr ("fckfed_tit", sfck)#!NTR

    @property
    def columnConcreteVariantions (self):
        """
        Número de variações de resistência de concreto em pilares
        """
        return          self.m_building._GetVarInt ("nfcved_tit")#!NTR

    @columnConcreteVariantions.setter
    def columnConcreteVariantions (self, nvar):
        """
        Número de variações de resistência de concreto em pilares
        """
        self.m_building._SetVarInt ("nfcved_tit", nvar)#!NTR

    def GetColumnConcreteVariantion (self, index):
        """
        Retorna um concreto e o último piso onde ele vale \n
        index           Índice da variação 0..columnConcreteVariantions-1\n
        Retorna:\n
        sfck            Título do fck até o piso abaixo\n
        iuntilfloor     Último piso no qual vale o Fck
        """
        varindex        = ctypes.c_int (index)
        varsfck         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        variuntilfloor  = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_FCKPEDTIT (varindex, varsfck, 
                            ctypes.byref (variuntilfloor))
        sfck            = varsfck.value.decode(TQS.TQSUtil.CHARSET)
        iuntilfloor     = variuntilfloor.value
        return          sfck, iuntilfloor


    def SetColumnConcreteVariantion (self, index, sfck, iuntilfloor):
        """
        Define um concreto e o último piso onde ele vale \n
        index           Índice da variação 0..columnConcreteVariantions-1\n
        sfck            Título do fck até o piso abaixo\n
        iuntilfloor     Último piso no qual vale o Fck
        """
        varindex        = ctypes.c_int (index)
        varsfck         = ctypes.c_char_p (sfck.encode(TQS.TQSUtil.CHARSET))
        variuntilfloor  = ctypes.c_int (iuntilfloor)
        self.m_building.m_edilib.EDILIB_SET_FCKPEDTIT (varindex, varsfck, variuntilfloor)

    def GetFloorPlanConcreteStrength (self, ipla):
        """
        Concreto de vigas e lajes específicos de uma planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        sfck            Título do concreto
        """
        varipla         = ctypes.c_int (ipla)
        varsfck         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_FCKPAVTIT (varipla, varsfck)
        sfck            = varsfck.value.decode(TQS.TQSUtil.CHARSET)
        return          sfck

    def SetFloorPlanConcreteStrength (self, ipla, sfck):
        """
        Concreto de vigas e lajes específicos de uma planta\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        sfck            Título do concreto
        """
        varipla         = ctypes.c_int (ipla)
        varsfck         = ctypes.c_char_p (sfck.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_FCKPAVTIT (varipla, varsfck)

    @property
    def masonryMaterial (self):
        """
        Material de alvenaria TQBuilding.MATRALVI_xxx
        """
        return          self.m_building._GetVarInt ("imatralven")#!NTR

    @masonryMaterial.setter
    def masonryMaterial (self, imat):
        """
        Material de alvenaria TQBuilding.MATRALVI_xxx
        """
        self.m_building._SetVarInt ("imatralven", imat)#!NTR

    @property
    def aciExposureClass (self):
        """
        Classe de exposição ambiental TQSBuild.CLAGCIRSOC_xxx
        """
        return          self.m_building._GetVarInt ("cirsoc_iclagress")#!NTR

    @aciExposureClass.setter
    def aciExposureClass (self, iclass):
        """
        Classe de exposição ambiental TQSBuild.CLAGCIRSOC_xxx
        """
        self.m_building._SetVarInt ("cirsoc_iclagress", iclass)#!NTR

#------------------------------------------------------------------------------
#       Materiais - Concreto pré-moldados
#
class PrecastMaterials ():

    def __init__ (self, building, materials):
        self.m_building      = building
        self.m_materials     = materials

    @property
    def pbeamConcreteStrength (self):
        """
        Concreto das vigas pré-moldadas
        """
        varsfck         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_FCKVIGPRE (varsfck)
        sfck            = varsfck.value.decode(TQS.TQSUtil.CHARSET)
        return          sfck

    @pbeamConcreteStrength.setter
    def pbeamConcreteStrength (self, sfck):
        """
        Concreto das vigas pré-moldadas
        """
        varsfck         = ctypes.c_char_p (sfck.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PREDAD_FCKVIGPRE (varsfck)

    @property
    def pbeamDemouldingConcreteStrength (self):
        """
        Concreto das vigas pré-moldadas no saque
        """
        return          self.m_building._GetVarStr ("fckvigpresaq")#!NTR

    @pbeamDemouldingConcreteStrength.setter
    def pbeamDemouldingConcreteStrength (self, sfck):
        """
        Concreto das vigas pré-moldadas no saque
        """
        self.m_building._SetVarStr ("fckvigpresaq", sfck)#!NTR

    @property
    def pbeamLiftingConcreteStrength (self):
        """
        Concreto das vigas pré-moldadas no içamento
        """
        return          self.m_building._GetVarStr ("fckvigprelev")#!NTR

    @pbeamLiftingConcreteStrength.setter
    def pbeamLiftingConcreteStrength (self, sfck):
        """
        Concreto das vigas pré-moldadas no içamento
        """
        self.m_building._SetVarStr ("fckvigprelev", sfck)#!NTR

    @property
    def pcolumnConcreteStrength (self):
        """
        Concreto dos pilares pré-moldados
        """
        varsfck         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_FCKPILPRE (varsfck)
        sfck            = varsfck.value.decode(TQS.TQSUtil.CHARSET)
        return          sfck

    @pcolumnConcreteStrength.setter
    def pcolumnConcreteStrength (self, sfck):
        """
        Concreto dos pilares pré-moldados
        """
        varsfck         = ctypes.c_char_p (sfck.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PREDAD_FCKPILPRE (varsfck)

    @property
    def pcolumnDemouldingConcreteStrength (self):
        """
        Concreto dos pilares pré-moldados no saque
        """
        return          self.m_building._GetVarStr ("fckpilpresaq")#!NTR

    @pcolumnDemouldingConcreteStrength.setter
    def pcolumnDemouldingConcreteStrength (self, sfck):
        """
        Concreto dos pilares pré-moldados no saque
        """
        self.m_building._SetVarStr ("fckpilpresaq", sfck)#!NTR

    @property
    def pcolumnLiftingConcreteStrength (self):
        """
        Concreto dos pilares pré-moldados no içamento
        """
        return          self.m_building._GetVarStr ("fckpilprelev")#!NTR

    @pcolumnLiftingConcreteStrength.setter
    def pcolumnLiftingConcreteStrength (self, sfck):
        """
        Concreto dos pilares pré-moldados no içamento
        """
        self.m_building._SetVarStr ("fckpilprelev", sfck)#!NTR

    @property
    def pslabConcreteStrength (self):
        """
        Concreto das lajes pré-moldadas
        """
        varsfck         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_FCKLAJPRE (varsfck)
        sfck            = varsfck.value.decode(TQS.TQSUtil.CHARSET)
        return          sfck

    @pslabConcreteStrength.setter
    def pslabConcreteStrength (self, sfck):
        """
        Concreto das lajes pré-moldadas
        """
        varsfck         = ctypes.c_char_p (sfck.encode(TQS.TQSUtil.CHARSET))
        self.m_building.m_edilib.EDILIB_SET_PREDAD_FCKLAJPRE (varsfck)

    @property
    def pslabDemouldingConcreteStrength (self):
        """
        Concreto das lajes pré-moldadas no saque
        """
        return          self.m_building._GetVarStr ("fcklajpresaq")#!NTR

    @pslabDemouldingConcreteStrength.setter
    def pslabDemouldingConcreteStrength (self, sfck):
        """
        Concreto das lajes pré-moldadas no saque
        """
        self.m_building._SetVarStr ("fcklajpresaq", sfck)#!NTR

    @property
    def pslabLiftingConcreteStrength (self):
        """
        Concreto das lajes pré-moldadas no içamento
        """
        return          self.m_building._GetVarStr ("fcklajprelev")#!NTR

    @pslabLiftingConcreteStrength.setter
    def pslabLiftingConcreteStrength (self, sfck):
        """
        Concreto das lajes pré-moldadas no içamento
        """
        self.m_building._SetVarStr ("fcklajprelev", sfck)#!NTR

    @property
    def pfoundationConcreteStrength (self):
        """
        Concreto das fundações pré-moldadas
        """
        return          self.m_building._GetVarStr ("fckfunprefin")#!NTR

    @pfoundationConcreteStrength.setter
    def pfoundationConcreteStrength (self, sfck):
        """
        Concreto das fundações pré-moldadas
        """
        self.m_building._SetVarStr ("fckfunprefin", sfck)#!NTR

    @property
    def pfoundationDemouldingConcreteStrength (self):
        """
        Concreto das fundações pré-moldadas no saque
        """
        return          self.m_building._GetVarStr ("fckfunpresaq")#!NTR

    @pfoundationDemouldingConcreteStrength.setter
    def pfoundationDemouldingConcreteStrength (self, sfck):
        """
        Concreto das fundações pré-moldadas no saque
        """
        self.m_building._SetVarStr ("fckfunpresaq", sfck)#!NTR

    @property
    def pfoundationLiftingConcreteStrength (self):
        """
        Concreto das fundações pré-moldadas no içamento
        """
        return          self.m_building._GetVarStr ("fckfunprelev")#!NTR

    @pfoundationLiftingConcreteStrength.setter
    def pfoundationLiftingConcreteStrength (self, sfck):
        """
        Concreto das fundações pré-moldadas no içamento
        """
        self.m_building._SetVarStr ("fckfunprelev", sfck)#!NTR


#------------------------------------------------------------------------------
#       Aba Cobrimentos
#
class Covers ():

    def __init__ (self, building):
        self.m_building      = building
        self.aci             = AciCovers (building, self)
        self.precast         = PrecastCovers (building, self)
        self.floorplan       = FloorPlanCovers(building, self)

    @property
    def disableCoverCheck (self):
        """
        (1) Para desativar verificação do cobrimento mínimo
        """
        return          self.m_building._GetVarInt ("idesativarvercobr")#!NTR

    @disableCoverCheck.setter
    def disableCoverCheck (self, idisable):
        """
        (1) Para desativar verificação do cobrimento mínimo
        """
        self.m_building._SetVarInt ("idesativarvercobr", idisable)#!NTR

    @property
    def beamCover (self):
        """
        Cobrimento cm vigas
        """
        return          self.m_building._GetVarDouble ("cobrvig")

    @beamCover.setter
    def beamCover (self, cover):
        """
        Cobrimento cm vigas
        """
        self.m_building._SetVarDouble ("cobrvig", cover)#!NTR

    @property
    def columnCover (self):
        """
        Cobrimento cm pilares
        """
        return          self.m_building._GetVarDouble ("cobrpil")

    @columnCover.setter
    def columnCover (self, cover):
        """
        Cobrimento cm pilares
        """
        self.m_building._SetVarDouble ("cobrpil", cover)#!NTR

    @property
    def foundationCover (self):
        """
        Cobrimento cm fundações
        """
        return          self.m_building._GetVarDouble ("cobrfund")

    @foundationCover.setter
    def foundationCover (self, cover):
        """
        Cobrimento cm fundações
        """
        self.m_building._SetVarDouble ("cobrfund", cover)#!NTR

    @property
    def foundationSecCover (self):
        """
        Cobrimento secundário cm fundações
        """
        return          self.m_building._GetVarDouble ("cobrfundsec")

    @foundationSecCover.setter
    def foundationSecCover (self, cover):
        """
        Cobrimento secundário cm fundações
        """
        self.m_building._SetVarDouble ("cobrfundsec", cover)#!NTR

    @property
    def slabLowerCover (self):
        """
        Cobrimento cm laje inferior
        """
        return          self.m_building._GetVarDouble ("cobrlajinf")

    @slabLowerCover.setter
    def slabLowerCover (self, cover):
        """
        Cobrimento cm laje inferior
        """
        self.m_building._SetVarDouble ("cobrlajinf", cover)#!NTR

    @property
    def slabUpperCover (self):
        """
        Cobrimento cm laje superior
        """
        return          self.m_building._GetVarDouble ("cobrlajsup")

    @slabUpperCover.setter
    def slabUpperCover (self, cover):
        """
        Cobrimento cm laje superior
        """
        self.m_building._SetVarDouble ("cobrlajsup", cover)#!NTR

    @property
    def slabSecLowerCover (self):
        """
        Cobrimento secundário cm laje inferior
        """
        return          self.m_building._GetVarDouble ("cobrlajsecinf")

    @slabSecLowerCover.setter
    def slabSecLowerCover (self, cover):
        """
        Cobrimento secundário cm laje inferior
        """
        self.m_building._SetVarDouble ("cobrlajsecinf", cover)#!NTR

    @property
    def slabSecUpperCover (self):
        """
        Cobrimento secundário cm laje superior
        """
        return          self.m_building._GetVarDouble ("cobrlajsecsup")

    @slabSecUpperCover.setter
    def slabSecUpperCover (self, cover):
        """
        Cobrimento secundário cm laje superior
        """
        self.m_building._SetVarDouble ("cobrlajsecsup", cover)#!NTR

    @property
    def prestressedSlabLowerCover (self):
        """
        Cobrimento cm protendido inferior
        """
        return          self.m_building._GetVarDouble ("cobrproinf")

    @prestressedSlabLowerCover.setter
    def prestressedSlabLowerCover (self, cover):
        """
        Cobrimento cm protendido inferior
        """
        self.m_building._SetVarDouble ("cobrproinf", cover)#!NTR

    @property
    def prestressedSlabUpperCover (self):
        """
        Cobrimento cm protendido superior
        """
        return          self.m_building._GetVarDouble ("cobrprosup")

    @prestressedSlabUpperCover.setter
    def prestressedSlabUpperCover (self, cover):
        """
        Cobrimento cm protendido superior
        """
        self.m_building._SetVarDouble ("cobrprosup", cover)#!NTR

    @property
    def prestressedSlabSecCover (self):
        """
        Cobrimento cm protendido secundário
        """
        return          self.m_building._GetVarDouble ("cobrprosec")

    @prestressedSlabSecCover.setter
    def prestressedSlabSecCover (self, cover):
        """
        Cobrimento cm protendido secundário
        """
        self.m_building._SetVarDouble ("cobrprosec", cover)#!NTR

    @property
    def beamAndSlabSoilCover (self):
        """
        Cobrimento cm vigas e lajes contato com o solo
        """
        return          self.m_building._GetVarDouble ("cobrvljsol")

    @beamAndSlabSoilCover.setter
    def beamAndSlabSoilCover (self, cover):
        """
        Cobrimento cm vigas e lajes contato com o solo
        """
        self.m_building._SetVarDouble ("cobrvljsol", cover)#!NTR

    @property
    def columnSoilCover (self):
        """
        Cobrimento cm pilares contato com o solo
        """
        return          self.m_building._GetVarDouble ("cobrpilsol")

    @columnSoilCover.setter
    def columnSoilCover (self, cover):
        """
        Cobrimento cm pilares contato com o solo
        """
        self.m_building._SetVarDouble ("cobrpilsol", cover)#!NTR

#-----------------------------------------------------------------------------
#       Cobrimentos específicos ACI
#
class AciCovers ():

    def __init__ (self, building, covers):
        self.m_building      = building
        self.m_covers        = covers

    @property
    def aciPrestressClass (self):
        """
        Classe de protensão TQSBuild.CLPRCIRSOC_xxx
        """
        return          self.m_building._GetVarInt ("cirsoc_iclaprotn")#!NTR

    @aciPrestressClass.setter
    def aciPrestressClass (self, iclass):
        """
        Classe de protensão TQSBuild.CLPRCIRSOC_xxx
        """
        self.m_building._SetVarInt ("cirsoc_iclaprotn", iclass)#!NTR

    @property
    def slabNotpresstressedExposedCover (self):
        """
        Cobrimento cm lajes não protendidas expostas ao ambiente
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrnprexpl")

    @slabNotpresstressedExposedCover.setter
    def slabNotpresstressedExposedCover (self, cover):
        """
        Cobrimento cm lajes não protendidas expostas ao ambiente
        """
        self.m_building._SetVarDouble ("cirsoc_cobrnprexpl", cover)#!NTR

    @property
    def slabPrestressedSoilCover (self):
        """
        Cobrimento cm lajes protendidas em contato com o solo
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrvljsolpro")

    @slabPrestressedSoilCover.setter
    def slabPrestressedSoilCover (self, cover):
        """
        Cobrimento cm lajes protendidas em contato com o solo
        """
        self.m_building._SetVarDouble ("cirsoc_cobrvljsolpro", cover)#!NTR

    @property
    def slabPrestressedExposedCover (self):
        """
        Cobrimento cm lajes protendidas em contato com o solo
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrproexplaje")

    @slabPrestressedExposedCover.setter
    def slabPrestressedExposedCover (self, cover):
        """
        Cobrimento cm lajes protendidas em contato com o solo
        """
        self.m_building._SetVarDouble ("cirsoc_cobrproexplaje", cover)#!NTR

    @property
    def beamSoilCover (self):
        """
        Cobrimento cm vigas em contato com o solo
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrnprljsolv")

    @beamSoilCover.setter
    def beamSoilCover (self, cover):
        """
        Cobrimento cm vigas em contato com o solo
        """
        self.m_building._SetVarDouble ("cirsoc_cobrnprljsolv", cover)#!NTR

    @property
    def beamExposedCover (self):
        """
        Cobrimento cm vigas não protendidas expostas ao ambiente
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrnprexpv")

    @beamExposedCover.setter
    def beamExposedCover (self, cover):
        """
        Cobrimento cm vigas não protendidas expostas ao ambiente
        """
        self.m_building._SetVarDouble ("cirsoc_cobrnprexpv", cover)#!NTR

    @property
    def beamPrestressedExposedCover (self):
        """
        Cobrimento cm vigas pré-moldadas expostas ao ambiente
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrpreexpv")

    @beamPrestressedExposedCover.setter
    def beamPrestressedExposedCover (self, cover):
        """
        Cobrimento cm vigas pré-moldadas expostas ao ambiente
        """
        self.m_building._SetVarDouble ("cirsoc_cobrpreexpv", cover)#!NTR

    @property
    def columnExposedCover (self):
        """
        Cobrimento cm pilar não protendido exposto ao ambiente
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrnprexpp")

    @columnExposedCover.setter
    def columnExposedCover (self, cover):
        """
        Cobrimento cm pilar não protendido exposto ao ambiente
        """
        self.m_building._SetVarDouble ("cirsoc_cobrnprexpp", cover)#!NTR

    @property
    def columnPrecastExposedCover (self):
        """
        Cobrimento cm pilar pré-moldado exposto ao ambiente
        """
        return          self.m_building._GetVarDouble ("cirsoc_cobrpreexpp")

    @columnPrecastExposedCover.setter
    def columnPrecastExposedCover (self, cover):
        """
        Cobrimento cm pilar pré-moldado exposto ao ambiente
        """
        self.m_building._SetVarDouble ("cirsoc_cobrpreexpp", cover)#!NTR


#-----------------------------------------------------------------------------
#       Cobrimentos específicos de pré-moldados
#
class PrecastCovers ():

    def __init__ (self, building, covers):
        self.m_building      = building
        self.m_covers        = covers

    @property
    def pbeamCover (self):
        """
        Cobrimento cm viga pré-moldada
        """
        return          self.m_building._GetVarDouble ("precobrvig")

    @pbeamCover.setter
    def pbeamCover (self, cover):
        """
        Cobrimento cm viga pré-moldada
        """
        self.m_building._SetVarDouble ("precobrvig", cover)#!NTR

    @property
    def pcolumnCover (self):
        """
        Cobrimento cm pilares pré-moldados
        """
        return          self.m_building._GetVarDouble ("precobrpil")

    @pcolumnCover.setter
    def pcolumnCover (self, cover):
        """
        Cobrimento cm pilares pré-moldados
        """
        self.m_building._SetVarDouble ("precobrpil", cover)#!NTR

    @property
    def pfoundationCover (self):
        """
        Cobrimento cm fundações pré-moldadas
        """
        return          self.m_building._GetVarDouble ("precobrfund")

    @pfoundationCover.setter
    def pfoundationCover (self, cover):
        """
        Cobrimento cm fundações pré-moldadas
        """
        self.m_building._SetVarDouble ("precobrfund", cover)#!NTR

    @property
    def pfoundationSecCover (self):
        """
        Cobrimento cm fundações pré-moldadas adicional secundário (<0 primário)
        """
        return          self.m_building._GetVarDouble ("precobrfundsec")

    @pfoundationSecCover.setter
    def pfoundationSecCover (self, cover):
        """
        Cobrimento cm fundações pré-moldadas adicional secundário (<0 primário)
        """
        self.m_building._SetVarDouble ("precobrfundsec", cover)#!NTR

    @property
    def pslabLowerCover (self):
        """
        Cobrimento cm laje inferior
        """
        return          self.m_building._GetVarDouble ("precobrlajinf")

    @pslabLowerCover.setter
    def pslabLowerCover (self, cover):
        """
        Cobrimento cm laje inferior
        """
        self.m_building._SetVarDouble ("precobrlajinf", cover)#!NTR

    @property
    def pslabUpperCover (self):
        """
        Cobrimento cm laje superior
        """
        return          self.m_building._GetVarDouble ("precobrlajsup")

    @pslabUpperCover.setter
    def pslabUpperCover (self, cover):
        """
        Cobrimento cm laje superior
        """
        self.m_building._SetVarDouble ("precobrlajsup", cover)#!NTR

    @property
    def pslabSecLowerCover (self):
        """
        Cobrimento cm laje adicional secundário inferior
        """
        return          self.m_building._GetVarDouble ("precobrlajsecinf")

    @pslabSecLowerCover.setter
    def pslabSecLowerCover (self, cover):
        """
        Cobrimento cm laje adicional secundário inferior
        """
        self.m_building._SetVarDouble ("precobrlajsecinf", cover)#!NTR


#-----------------------------------------------------------------------------
#       Cobrimentos por planta, se definidos
#
class FloorPlanCovers ():

    def __init__ (self, building, covers):
        self.m_building      = building
        self.m_covers        = covers

    def GetFloorPlanBeamsCover (self, ipla):
        """
        Retorna o cobrimento (cm) de vigas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRVIG (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanBeamsCover (self, ipla, cover):
        """
        Define o cobrimento (cm) de vigas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRVIG (varipla, varcover)

    def GetFloorPlanSlabLowerCover (self, ipla):
        """
        Retorna o cobrimento inferior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRLAJINF (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanSlabLowerCover (self, ipla, cover):
        """
        Define o cobrimento inferior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRLAJINF (varipla, varcover)

    def GetFloorPlanSlabUpperCover (self, ipla):
        """
        Retorna o cobrimento superior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRLAJSUP (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanSlabUpperCover (self, ipla, cover):
        """
        Retorna o cobrimento superior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRLAJSUP (varipla, varcover)

    def GetFloorPlanSlabSecLowerCover (self, ipla):
        """
        Retorna o cobrimento secundário inferior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRLAJSECINF (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanSlabSecLowerCover (self, ipla, cover):
        """
        Define o cobrimento secundário inferior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)\n
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRLAJSECINF (varipla, varcover)

    def GetFloorPlanSlabSecUpperCover (self, ipla):
        """
        Retorna o cobrimento secundário superior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRLAJSECSUP (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanSlabSecUpperCover (self, ipla, cover):
        """
        Define o cobrimento secundário superior (cm) de lajes para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRLAJSECSUP (varipla, varcover)

    def GetFloorPlanPrestressedSlabLowerCover (self, ipla):
        """
        Retorna o cobrimento inferior (cm) de lajes protendidas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varcover        = ctypes.c_double (0.)
        varipla         = ctypes.c_int (ipla)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRPROINF (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanPrestressedSlabLowerCover (self, ipla, cover):
        """
        Define o cobrimento inferior (cm) de lajes protendidas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRPROINF (varipla, varcover)

    def GetFloorPlanPrestressedSlabUpperCover (self, ipla):
        """
        Retorna o cobrimento superior (cm) de lajes protendidas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBPROSUP (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanPrestressedSlabUpperCover (self, ipla, cover):
        """
        Define o cobrimento superior (cm) de lajes protendidas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBPROSUP (varipla, varcover)

    def GetFloorPlanPrestressedSlabSecCover (self, ipla):
        """
        Retorna o cobrimento secundário (cm) de lajes protendidas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        Retorna:\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PLANTAS_COBRPROSEC (varipla, ctypes.byref (varcover))
        cover           = varcover.value
        return          cover

    def SetFloorPlanPrestressedSlabSecCover (self, ipla, cover):
        """
        Define o cobrimento secundário (cm) de lajes protendidas para a planta, se (!=0)\n
        ipla            Índice da planta (0..floorsPlanNumber-1)\n
        cover           Valor do cobrimento em cm ou (0)
        """
        varipla         = ctypes.c_int (ipla)
        varcover        = ctypes.c_double (cover)
        self.m_building.m_edilib.EDILIB_SET_PLANTAS_COBRPROSEC (varipla, varcover)


#------------------------------------------------------------------------------
#       Aba Cargas
#
class Loads ():

    def __init__ (self, building):
        self.m_building      = building
        self.precastloads    = PrecastLoads (building, self)
        self.windloads       = WindLoads (building, self)

    def GetLoad (self, prefixo):
        """
        Retorna os parâmetros comuns de um caso simples de carregamento pré-definido TQS\n
        prefixo         Prefixo TQSBuild.PREFIXOxxxx\n
        Retorna:\n
        titulo          Título do carregamento\n
        ipermacid       Grupo (0) permanente (1) acidental (2) excepcional\n
        ivigtrans       (1) Se afetado pelo caso de viga de transição enrigecida\n
        ireduzida       (1) Se afetado pelo caso de carga acidental reduzida\n
        imulaxi         (1) Se aplicar multiplicador de área de pilares MULAXI\n
        gamaf           Ponderador de cargas GamaF favorável\n
        igamafd         (1) Se aplicar ponderador Gamaf desfavorável\n
        gamafd          Ponderador de cargas GamaF desfavorável\n
        psi0            Fator de redução das combinações ELU\n
        psi1            Fator de redução das combinações frequentes ELS\n
        psi2            Fator de redução das combinações quase permanentes ELS\n
        ipavimento      (1) Se aplicado nas grelhas do pavimento\n
        numcasos        Número de casos diferentes gerados por este carregamento\n
        istat           (!= 0) Se prefixo indefinido ou erro
        """
        varprefixo      = ctypes.c_char_p (prefixo.encode(TQS.TQSUtil.CHARSET))
        vartitulo       = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        varmaxnc        = ctypes.c_int (TQS.TQSUtil.MAXNCSTR)
        varipermacid    = ctypes.c_int (0)
        varivigtrans    = ctypes.c_int (0)
        varireduzida    = ctypes.c_int (0)
        varimulaxi      = ctypes.c_int (0)
        vargamaf        = ctypes.c_double (0.)
        varigamafd      = ctypes.c_int (0)
        vargamafd       = ctypes.c_double (0.)
        varpsi0         = ctypes.c_double (0.)
        varpsi1         = ctypes.c_double (0.)
        varpsi2         = ctypes.c_double (0.)
        varipavimento   = ctypes.c_int (0)
        varnumcasos     = ctypes.c_int (0)
        varistat        = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_CARREG (varprefixo, vartitulo, varmaxnc,
                        ctypes.byref (varipermacid), ctypes.byref (varivigtrans),
                        ctypes.byref (varireduzida), ctypes.byref (varimulaxi),
                        ctypes.byref (vargamaf), ctypes.byref (varigamafd),
                        ctypes.byref (vargamafd), ctypes.byref (varpsi0),
                        ctypes.byref (varpsi1), ctypes.byref (varpsi2),
                        ctypes.byref (varipavimento), ctypes.byref (varnumcasos),
                        ctypes.byref (varistat))
        titulo          = vartitulo.value.decode(TQS.TQSUtil.CHARSET)
        ipermacid       = varipermacid.value
        ivigtrans       = varivigtrans.value
        ireduzida       = varireduzida.value
        imulaxi         = varimulaxi.value
        gamaf           = vargamaf.value
        igamafd         = varigamafd.value
        gamafd          = vargamafd.value
        psi0            = varpsi0.value
        psi1            = varpsi1.value
        psi2            = varpsi2.value
        ipavimento      = varipavimento.value
        numcasos        = varnumcasos.value
        istat           = varistat.value
        if              istat != 0:
            TQS.TQSUtil.writef ("TQSBuild: Leitura de cargas com prefixo de carregamento inválido: [%s]" %
                            prefixo)
        return          titulo, ipermacid, ivigtrans, ireduzida, imulaxi, gamaf, igamafd, gamafd, psi0, psi1, psi2, ipavimento, numcasos, istat

    def SetLoad (self, prefixo, titulo, ipermacid, ivigtrans, ireduzida, imulaxi,
                    gamaf, igamafd, gamafd, psi0, psi1, psi2, ipavimento, numcasos, icasadi):
        """
        Fixa os parâmetros comuns de um caso simples de carregamento pré-definido TQS\n
        prefixo         Prefixo TQSBuild.PREFIXOxxxx\n
        titulo          Título do carregamento\n
        ipermacid       Grupo (0) permanente (1) acidental (2) excepcional\n
        ivigtrans       (1) Se afetado pelo caso de viga de transição enrigecida\n
        ireduzida       (1) Se afetado pelo caso de carga acidental reduzida\n
        imulaxi         (1) Se aplicar multiplicador de área de pilares MULAXI\n
        gamaf           Ponderador de cargas GamaF favorável\n
        igamafd         (1) Se aplicar ponderador Gamaf desfavorável\n
        gamafd          Ponderador de cargas GamaF desfavorável\n
        psi0            Fator de redução das combinações ELU\n
        psi1            Fator de redução das combinações frequentes ELS\n
        psi2            Fator de redução das combinações quase permanentes ELS\n
        ipavimento      (1) Se aplicado nas grelhas do pavimento\n
        numcasos        Número de casos diferentes gerados por este carregamento\n
        icasadi         (1) Se este é um caso adicional definido pelo usuário\n
        Retorna:\n
        istat           (!= 0) Se prefixo indefinido ou erro
        """
        varprefixo      = ctypes.c_char_p (prefixo.encode(TQS.TQSUtil.CHARSET))
        vartitulo       = ctypes.c_char_p (titulo.encode(TQS.TQSUtil.CHARSET))
        varipermacid    = ctypes.c_int (ipermacid)
        varivigtrans    = ctypes.c_int (ivigtrans)
        varireduzida    = ctypes.c_int (ireduzida)
        varimulaxi      = ctypes.c_int (imulaxi)
        vargamaf        = ctypes.c_double (gamaf)
        varigamafd      = ctypes.c_int (igamafd)
        vargamafd       = ctypes.c_double (gamafd)
        varpsi0         = ctypes.c_double (psi0)
        varpsi1         = ctypes.c_double (psi1)
        varpsi2         = ctypes.c_double (psi2)
        varipavimento   = ctypes.c_int (ipavimento)
        varnumcasos     = ctypes.c_int (numcasos)
        varicasadi      = ctypes.c_int (icasadi)
        varistat        = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_SET_CARREG (varprefixo, vartitulo, varipermacid,
                        varivigtrans, varireduzida, varimulaxi, vargamaf, varigamafd,
                        vargamafd, varpsi0, varpsi1, varpsi2, varipavimento, 
                        varnumcasos, varicasadi, ctypes.byref (varistat))
        istat           = varistat.value
        if              istat != 0:
            TQS.TQSUtil.writef ("TQSBuild: Definição de cargas com prefixo de carregamento inválido: [%s]" %
                            prefixo)
        istat           = varistat.value
        return          istat


    def CreateLoad (self, prefixo):
        """            
        Cria carregamento com novo prefixo\n
        Retorna:\n
        istat           (!=0) se erro
        """            
        varprefixo      = ctypes.c_char_p (prefixo.encode(TQS.TQSUtil.CHARSET))
        varistat        = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_CRIARCARREG (varprefixo, ctypes.byref (varistat))
        istat           = varistat.value
        return          istat

    def GetAdditionalCasesNumber (self):
        """            
        Retorna o número de casos adicionais definidos. São casos com icasadi!=0 definido
        """            
        varnumcasadi        = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_NUMCASADI (ctypes.byref (varnumcasadi))
        numcasadi       = varnumcasadi.value
        return          numcasadi

    def GetAadditionalCasePrefix (self, icasadi):
        """            
        Retorna o prefixo de um caso adicional\n
        icasadi         Caso adicional 0..GetAdditionalCasesNumber()-1\n
        Retorna:\n
        prefixo         Prefixo do caso adicional
        """            
        varicasadi      = ctypes.c_int (icasadi)
        varprefixo      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_building.m_edilib.EDILIB_GET_PRECASADI (varicasadi, varprefixo)
        prefixo         = varprefixo.value.decode(TQS.TQSUtil.CHARSET)
        return          prefixo

    def GetLiveLoadReduction (self, ifloor):
        """            
        Retorna um redutor de sobrecargas para um piso\n
        ifloor          Número do piso do edifício, começando em zero\n
        Retorna:\n
        reductor        Redutor de sobrecargas. (0.) Não reduz (1.) Reduz 100%
        """            
        varifloor       = ctypes.c_int (ifloor)
        varreductor     = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_REDSOBRE (varifloor, ctypes.byref (varreductor))
        reductor        = varreductor.value
        return          reductor

    def SetLiveLoadReduction (self, ifloor, reductor):
        """            
        Define um redutor de sobrecargas para um piso\n
        ifloor          Número do piso do edifício, começando em zero\n
        reductor        Redutor de sobrecargas. (0.) Não reduz (1.) Reduz 100%
        """            
        varifloor       = ctypes.c_int (ifloor)
        varreductor     = ctypes.c_double (reductor)
        self.m_building.m_edilib.EDILIB_SET_REDSOBRE (varifloor, varreductor)

    @property
    def outOfPlumbCases (self):
        """
        Número de casos de desaprumo
        """
        varnoutofplumb  = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_DESAPRUMO_NUMCASOS (ctypes.byref (varnoutofplumb))
        noutofplumb     = varnoutofplumb.value
        return          noutofplumb

    @outOfPlumbCases.setter
    def outOfPlumbCases (self, noutofplumb):
        """
        Número de casos de desaprumo
        """
        varnoutofplumb  = ctypes.c_int (noutofplumb)
        self.m_building.m_edilib.EDILIB_SET_DESAPRUMO_NUMCASOS (varnoutofplumb)

    def GetOutOfPlumbleAngle (self, ioopcase):
        """
        Retorna o ângulo do caso fornecido em graus\n
        ioopcase        Número do caso de desaprumo 0..outOfPlumbCases()-1\n
        Retorna:\n
        angle           Ângulo em planta do caso de desaprumo em graus
        """
        varioopcase     = ctypes.c_int (ioopcase)
        varangle        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_DESAPRUMO_CASO (varioopcase, ctypes.byref (varangle))
        angle           = varangle.value
        return          angle
    
    def SetOutOfPlumbleAngle (self, ioopcase, angle):
        """
        Define o ângulo do caso fornecido em graus\n
        ioopcase        Número do caso de desaprumo 0..outOfPlumbCases()-1\n
        angle           Ângulo em planta do caso de desaprumo em graus\n
        """
        varioopcase     = ctypes.c_int (ioopcase)
        varangle        = ctypes.c_double (angle)
        self.m_building.m_edilib.EDILIB_SET_DESAPRUMO_CASO (varioopcase, varangle)

#------------------------------------------------------------------------------
#       Cargas de vento
#
class WindLoads ():

    def __init__ (self, building, loads):
        self.m_building      = building
        self.m_loads         = loads 

    def GetWindLoadParametersNBR (self):
        """
        Parâmetros de cálculo de caso de vento pela NBR-6123\n
        Retorna:\n
        windv0          Velocidade básica m/s\n
        winds1          Fator topográfico\n
        iwndrug         Categoria de rugosidade I..IV\n
        winds3          Fator estatístico\n
        iwindclass      Classe (0)A (1)B (2)C\n
        numcaswind      Número de casos em direções diferentes
        """
        varwindv0       = ctypes.c_double (0)
        varwinds1       = ctypes.c_double (0)
        variwndrug      = ctypes.c_int (0)
        varwinds3       = ctypes.c_double (0)
        variwindclass   = ctypes.c_int (0)
        varnumcaswind   = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_CASVEN (ctypes.byref (varwindv0),
                    ctypes.byref (varwinds1), ctypes.byref (variwndrug),
                    ctypes.byref (varwinds3), ctypes.byref (variwindclass),
                    ctypes.byref (varnumcaswind))
        windv0          = varwindv0.value
        winds1          = varwinds1.value
        iwndrug         = variwndrug.value
        winds3          = varwinds3.value
        iwindclass      = variwindclass.value
        numcaswind      = varnumcaswind.value
        return          windv0, winds1, iwndrug, winds3, iwindclass, numcaswind

    def SetWindLoadParametersNBR (self, windv0, winds1, iwndrug, winds3, iwindclass, numcaswind):
        """
        Define os parâmetros de cálculo de caso de vento pela NBR-6123\n
        windv0          Velocidade básica m/s\n
        winds1          Fator topográfico\n
        iwndrug         Categoria de rugosidade I..IV\n
        winds3          Fator estatístico\n
        iwindclass      Classe (0)A (1)B (2)C\n
        numcaswind      Número de casos em direções diferentes
        """
        varwindv0       = ctypes.c_double (windv0)
        varwinds1       = ctypes.c_double (winds1)
        variwndrug      = ctypes.c_int (iwndrug)
        varwinds3       = ctypes.c_double (winds3)
        variwindclass   = ctypes.c_int (iwindclass)
        varnumcaswind   = ctypes.c_int (numcaswind)
        self.m_building.m_edilib.EDILIB_SET_CASVEN (varwindv0, varwinds1, variwndrug,
                        varwinds3, variwindclass, varnumcaswind)

    def GetWindLoadCase (self, iwindcase):
        """
        Retorna dados de um caso de vento em uma direção\n
        iwindcase       Número do caso de vento 0..numcaswind-1\n
        Retorna:\n
        ca              Coeficiente de arrasto\n
        ang             Ângulo de vento em graus\n
        icti            (1) Se cota inicial definida\n
        cti             Cota inicial (m);
        """
        variwindcase    = ctypes.c_int (iwindcase)
        varca           = ctypes.c_double (0.)
        varang          = ctypes.c_double (0.)
        varicti         = ctypes.c_int (0)
        varcti          = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_CASVEN_ICASO (variwindcase, ctypes.byref (varca),
                        ctypes.byref (varang), ctypes.byref (varicti),
                        ctypes.byref (varcti))
        ca              = varca.value
        ang             = varang.value
        icti            = varicti.value
        cti             = varcti.value
        return          ca, ang, icti, cti
   
    def SetWindLoadCase (self, iwindcase, ca, ang, icti, cti):
        """
        Define dados de um caso de vento em uma direção\n
        iwindcase       Número do caso de vento 0..numcaswind-1\n
        ca              Coeficiente de arrasto\n
        ang             Ângulo de vento em graus\n
        icti            (1) Se cota inicial definida\n
        cti             Cota inicial (m);
        """
        variwindcase    = ctypes.c_int (iwindcase)
        varca           = ctypes.c_double (ca)
        varang          = ctypes.c_double (ang)
        varicti         = ctypes.c_int (icti)
        varcti          = ctypes.c_double (cti)
        self.m_building.m_edilib.EDILIB_SET_CASVEN_ICASO (variwindcase, varca,
                        varang, varicti, varcti)

    def InitWindEccentricity (self, iwindcase):
        """
        Inicializa excenctricidades de vento e outros dados para o caso fornecido\n
        iwindcase       Número do caso de vento 0..numcaswind-1
        """
        variwindcase    = ctypes.c_int (iwindcase)
        self.m_building.m_edilib.EDILIB_EXCVEN_INICIARCASO (variwindcase)

    def GetWindEccentricityNumber (self, iwindcase):
        """
        Retorna o número de excentricidades de vento associadas a um caso\n
        iwindcase       Número do caso de vento 0..numcaswind-1\n
        Retorna:\n
        numwindecc      Número de excentricidades do caso iwindcase
        """
        variwindcase    = ctypes.c_int (iwindcase)
        varnumwindecc   = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_EXCVEN_NUMEXCVEN (variwindcase, 
                            ctypes.byref (varnumwindecc))
        numwindecc      = varnumwindecc.value
        return          numwindecc

    def AddWindEccentricity (self, iwindcase, ipisoi, ipisof, ipil, excven, alrgpis,
                            forven, s2b, s2fr, s2p, forlat, amomz):
        """
        Adiciona excentricidade e outros dados no caso de vento fornecido\n
        iwindcase       Número do caso de vento 0..numcaswind-1\n
        ipisoi          Piso inicial (-1) o primeiro\n
        ipisof          Piso final   (-1) o último\n
        ipil            Número do pilar (-1) distriui em todos\n
        excven          Excentricidade porcentual % \n
        alrgpis         Largura imposta do piso (m)\n
        forven          Forca total de vento no piso, tf\n
        s2b             Parâmetro meteorológico\n
        s2fr            Fr- Fator de rajada\n
        s2p             p - Expoente da lei potencial S2\n
        forlat          Força lateral de vento (tf)\n
        amomz           Momento torsor de vento (tfm)
        """
        variwindcase    = ctypes.c_int (iwindcase)
        varipisoi       = ctypes.c_int (ipisoi)
        varipisof       = ctypes.c_int (ipisof)
        varipil         = ctypes.c_int (ipil)
        varexcven       = ctypes.c_double (excven)
        varalrgpis      = ctypes.c_double (alrgpis)
        varforven       = ctypes.c_double (forven)
        vars2b          = ctypes.c_double (s2b)
        vars2fr         = ctypes.c_double (s2fr)
        vars2p          = ctypes.c_double (s2p)
        varforlat       = ctypes.c_double (forlat)
        varamomz        = ctypes.c_double (amomz)
        self.m_building.m_edilib.EDILIB_ADD_EXCVEN (variwindcase, varipisoi, varipisof,
                        varipil, varexcven, varalrgpis, varforven, vars2b, vars2fr,
                        vars2p, varforlat, varamomz)

    def GetWindEccentricity (self, iwindcase, iwindexc):
        """
        Retorna a excentricidade e outros dados no caso de vento fornecido\n
        iwindcase       Número do caso de vento 0..numcaswind-1\n
        iwindexc        Número da excentricidade 0..GetWindEccentricityNumber()-1\n
        Retorna:\n
        ipisoi          Piso inicial (-1) o primeiro\n
        ipisof          Piso final   (-1) o último\n
        ipil            Número do pilar (-1) distriui em todos\n
        excven          Excentricidade porcentual % \n
        alrgpis         Largura imposta do piso (m)\n
        forven          Forca total de vento no piso, tf\n
        s2b             Parâmetro meteorológico\n
        s2fr            Fr- Fator de rajada\n
        s2p             p - Expoente da lei potencial S2\n
        forlat          Força lateral de vento (tf)\n
        amomz           Momento torsor de vento (tfm)
        """
        variwindcase    = ctypes.c_int (iwindcase)
        variwindexc     = ctypes.c_int (iwindexc)
        varipisoi       = ctypes.c_int (0)
        varipisof       = ctypes.c_int (0)
        varipil         = ctypes.c_int (0)
        varexcven       = ctypes.c_double (0.)
        varalrgpis      = ctypes.c_double (0.)
        varforven       = ctypes.c_double (0.)
        vars2b          = ctypes.c_double (0.)
        vars2fr         = ctypes.c_double (0.)
        vars2p          = ctypes.c_double (0.)
        varforlat       = ctypes.c_double (0.)
        varamomz        = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_EXCVEN (variwindcase, variwindexc,
                        ctypes.byref (varipisoi), ctypes.byref (varipisof),
                        ctypes.byref (varipil), ctypes.byref (varexcven), 
                        ctypes.byref (varalrgpis), ctypes.byref (varforven), 
                        ctypes.byref (vars2b), ctypes.byref (vars2fr),
                        ctypes.byref (vars2p), ctypes.byref (varforlat), 
                        ctypes.byref (varamomz))
        ipisoi          = varipisoi.value
        ipisof          = varipisof.value
        ipil            = varipil.value
        excven          = varexcven.value
        alrgpis         = varalrgpis.value
        forven          = varforven.value
        s2b             = vars2b.value
        s2fr            = vars2fr.value
        s2p             = vars2p.value
        forlat          = varforlat.value
        amomz           = varamomz.value
        return          ipisoi, ipisof, ipil, excven, alrgpis, forven, s2b, s2fr, s2p, forlat, amomz

    @property
    def windInPlanFloor (self):
        """
        (1) Se caso de vento na planta de formas e grelha
        """
        return          self.m_building._GetVarInt ("icasoventofor")#!NTR

    @windInPlanFloor.setter
    def windInPlanFloor (self, cover):
        """
        (1) Se caso de vento na planta de formas e grelha
        """
        self.m_building._SetVarInt ("icasoventofor", cover)#!NTR

    @property
    def windTunnelGlobalSystem (self):
        """
        Túnel de vento: (1) Se sistema global
        """
        return          self.m_building._GetVarInt ("isisglob")#!NTR

    @windTunnelGlobalSystem.setter
    def windTunnelGlobalSystem (self, isisglob):
        """
        Túnel de vento: (1) Se sistema global
        """
        self.m_building._SetVarInt ("isisglob", isisglob)#!NTR

    @property
    def windTunnelInvertSignal (self):
        """
        Túnel de vento: (1) Se inverter sinal
        """
        return          self.m_building._GetVarInt ("invertsn")#!NTR

    @windTunnelInvertSignal.setter
    def windTunnelInvertSignal (self, invertsn):
        """
        Túnel de vento: (1) Se inverter sinal
        """
        self.m_building._SetVarInt ("invertsn", invertsn)#!NTR

    @property
    def windTunnelIgnoreColumns (self):
        """
        Túnel de vento: Número de colunas a desprezar
        """
        return          self.m_building._GetVarInt ("idespcol")#!NTR

    @windTunnelIgnoreColumns.setter
    def windTunnelIgnoreColumns (self, idespcol):
        """
        Túnel de vento: Número de colunas a desprezar
        """
        self.m_building._SetVarInt ("idespcol", idespcol)#!NTR

    @property
    def windTunnelIgnoreLines (self):
        """
        Túnel de vento: Número de linhas a desprezar
        """
        return          self.m_building._GetVarInt ("idesplin")#!NTR

    @windTunnelIgnoreLines.setter
    def windTunnelIgnoreLines (self, idesplin):
        """
        Túnel de vento: Número de linhas a desprezar
        """
        self.m_building._SetVarInt ("idesplin", idesplin)#!NTR

    @property
    def windTunnelTopToBottom (self):
        """
        Túnel de vento: (1) Se de cima para baixo
        """
        return          self.m_building._GetVarInt ("iordpiso")#!NTR

    @windTunnelTopToBottom.setter
    def windTunnelTopToBottom (self, iordpiso):
        """
        Túnel de vento: (1) Se de cima para baixo
        """
        self.m_building._SetVarInt ("iordpiso", iordpiso)#!NTR

    @property
    def windTunnelFirstFloor (self):
        """
        Túnel de vento: Primeiro piso da lista ou (-1)
        """
        return          self.m_building._GetVarInt ("iprimpis")#!NTR

    @windTunnelFirstFloor.setter
    def windTunnelFirstFloor (self, iprimpis):
        """
        Túnel de vento: Primeiro piso da lista ou (-1)
        """
        self.m_building._SetVarInt ("iprimpis", iprimpis)#!NTR

    @property
    def windTunnelForcesUnits (self):
        """
        Túnel de vento: (0) tf e tfm (1) se kN e kNm
        """
        return          self.m_building._GetVarInt ("iunidknm")#!NTR

    @windTunnelForcesUnits.setter
    def windTunnelForcesUnits (self, iunidknm):
        """
        Túnel de vento: (0) tf e tfm (1) se kN e kNm
        """
        self.m_building._SetVarInt ("iunidknm", iunidknm)#!NTR

    @property
    def windTunnelGlobalSystem (self):
        """
        Túnel de vento: (0) Forças no sistema local (1) sistema global\n
        Somente aplicável no momento da leitura da tabela de forças
        """
        return          self.m_building._GetVarInt ("isisglobexc")#!NTR

    @windTunnelGlobalSystem.setter
    def windTunnelGlobalSystem (self, isisglobexc):
        """
        Túnel de vento: (0) Forças no sistema local (1) sistema global\n
        Somente aplicável no momento da leitura da tabela de forças
        """
        self.m_building._SetVarInt ("isisglobexc", isisglobexc)#!NTR

    @property
    def windTunnelInvertExcc (self):
        """
        Túnel de vento: (1) Excentricidades armazenadas com sinal invertido
        """
        return          self.m_building._GetVarInt ("invertsnexc")#!NTR

    @windTunnelInvertExcc.setter
    def windTunnelInvertExcc (self, invertsnexc):
        """
        Túnel de vento: (1) Excentricidades armazenadas com sinal invertido
        """
        self.m_building._SetVarInt ("invertsnexc", invertsnexc)#!NTR

    @property
    def aciBasicWindSpeed (self):
        """
        ACI-318 Velocidade básica de vento (m/s)
        """
        return          self.m_building._GetVarDouble ("cirsoc_v0")

    @aciBasicWindSpeed.setter
    def aciBasicWindSpeed (self, v0):
        """
        ACI-318 Velocidade básica de vento (m/s)
        """
        self.m_building._SetVarDouble ("cirsoc_v0", v0)#!NTR

    @property
    def aciNaturalFrequency (self):
        """
        ACI-318 Frequência natural Hz (aciStructureStiffness() != 0)
        """
        return          self.m_building._GetVarDouble ("cirsoc_freqnat")

    @aciNaturalFrequency.setter
    def aciNaturalFrequency (self, fr):
        """
        ACI-318 Frequência natural Hz (aciStructureStiffness() != 0)
        """
        self.m_building._SetVarDouble ("cirsoc_freqnat", fr)#!NTR

    @property
    def aciDampingRate (self):
        """
        ACI-318 Taxa amortecimento % valor crítico (aciStructureStiffness() != 0)
        """
        return          self.m_building._GetVarDouble ("cirsoc_txamort")

    @aciDampingRate.setter
    def aciDampingRate (self, dr):
        """
        ACI-318 Taxa amortecimento % valor crítico (aciStructureStiffness() != 0)
        """
        self.m_building._SetVarDouble ("cirsoc_txamort", dr)#!NTR

    @property
    def aciStructureStiffness (self):
        """
        ACI-318 (0) Edifício rígido (1) flexível
        """
        return          self.m_building._GetVarInt ("cirsoc_iflex")#!NTR

    @aciStructureStiffness.setter
    def aciStructureStiffness (self, istiff):
        """
        ACI-318 (0) Edifício rígido (1) flexível
        """
        self.m_building._SetVarInt ("cirsoc_iflex", istiff)#!NTR

    @property
    def aciTopographicFactor (self):
        """
        ACI-318 Fator topográfico Kzt
        """
        return          self.m_building._GetVarDouble ("cirsoc_akzt")

    @aciTopographicFactor.setter
    def aciTopographicFactor (self, fact):
        """
        ACI-318 Fator topográfico Kzt
        """
        self.m_building._SetVarDouble ("cirsoc_akzt", fact)#!NTR

    @property
    def aciMinimumWindPressure (self):
        """
        ACI-318 Pressão mínima de vento, tf/m2
        """
        return          self.m_building._GetVarDouble ("cirsoc_pmintfm2")

    @aciMinimumWindPressure.setter
    def aciMinimumWindPressure (self, press):
        """
        ACI-318 Pressão mínima de vento, tf/m2
        """
        self.m_building._SetVarDouble ("cirsoc_pmintfm2", press)#!NTR

    @property
    def aciOccupancyCategory (self):
        """
        ACI-318 Natureza de ocupação (0)I (1)II (2)III (3)IV
        """
        return          self.m_building._GetVarInt ("cirsoc_inaturocup")#!NTR

    @aciOccupancyCategory.setter
    def aciOccupancyCategory (self, iocc):
        """
        ACI-318 Natureza de ocupação (0)I (1)II (2)III (3)IV
        """
        self.m_building._SetVarInt ("cirsoc_inaturocup", iocc)#!NTR

    @property
    def aciExposureCategory (self):
        """
        ACI-318 Categoria de exposição (0)A (1)B (2)C (3)D
        """
        return          self.m_building._GetVarInt ("cirsoc_icatexposi")#!NTR

    @aciExposureCategory.setter
    def aciExposureCategory (self, icat):
        """
        ACI-318 Categoria de exposição (0)A (1)B (2)C (3)D
        """
        self.m_building._SetVarInt ("cirsoc_icatexposi", icat)#!NTR

    @property
    def aciAltitude (self):
        """
        ACI-318 Altitude da edificação em relação ao nível do mar (m)
        """
        return          self.m_building._GetVarDouble ("altitmar")#!NTR

    @aciAltitude.setter
    def aciAltitude (self, icat):
        """
        ACI-318 Altitude da edificação em relação ao nível do mar (m)
        """
        self.m_building._SetVarDouble ("altitmar", icat)#!NTR

#------------------------------------------------------------------------------
#       Cargas em estruturas pré-moldadas
#
class PrecastLoads ():

    def __init__ (self, building, loads):
        self.m_building      = building
        self.m_loads         = loads 

    @property
    def fracSelfLoadConsStage (self):
        """
        Fração % da carga de peso próprio engastado nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCARPPEN (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracSelfLoadConsStage.setter
    def fracSelfLoadConsStage (self, frac):
        """
        Fração % da carga de peso próprio engastado nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCARPPEN (varfrac)

    @property
    def fracDeadLoadConsStage (self):
        """
        Fração % da carga permanente nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCARPERM (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracDeadLoadConsStage.setter
    def fracDeadLoadConsStage (self, frac):
        """
        Fração % da carga permanente nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCARPERM (varfrac)

    @property
    def fracLiveLoadConsStage (self):
        """
        Fração % de sobrecargas nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCARSOBR (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracLiveLoadConsStage.setter
    def fracLiveLoadConsStage (self, frac):
        """
        Fração % de sobrecargas nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCARSOBR (varfrac)
        
    @property
    def fracWindConsStage (self):
        """
        Fração % de carga de vento nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCARVENT (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracWindConsStage.setter
    def fracWindConsStage (self, frac):
        """
        Fração % de carga de vento nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCARVENT (varfrac)

    @property
    def fracEarthPressureStage (self):
        """
        Fração % de carga de empuxo de terra nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCAREMPU (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracEarthPressureStage.setter
    def fracEarthPressureStage (self, frac):
        """
        Fração % de carga de empuxo de terra nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCAREMPU (varfrac)

    @property
    def fracTemperatureStage (self):
        """
        Fração % de carga de temperatura nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCARTEMP (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracTemperatureStage.setter
    def fracTemperatureStage (self, frac):
        """
        Fração % de carga de temperatura nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCARTEMP (varfrac)

    @property
    def fracShrinkageStage (self):
        """
        Fração % de carga de empuxo de terra nas etapas construtivas
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_PERCARRETR (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @fracShrinkageStage.setter
    def fracShrinkageStage (self, frac):
        """
        Fração % de carga de empuxo de terra nas etapas construtivas
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_PERCARRETR (varfrac)

    @property
    def outOfPlumbNumber (self):
        """
        Número de casos de desaprumo
        """
        varfrac         = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_NUMCASODES (ctypes.byref (varfrac))
        frac            = varfrac.value
        return          frac

    @outOfPlumbNumber.setter
    def outOfPlumbNumber (self, frac):
        """
        Número de casos de desaprumo
        """
        varfrac         = ctypes.c_double (frac)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_NUMCASODES (varfrac)

    @property
    def outOfPlumbInverseAngle (self):
        """
        Inverso do ângulo de desaprumo
        """
        varinvangle     = ctypes.c_double (0.)
        self.m_building.m_edilib.EDILIB_GET_PREDAD_DESAPRUMO (ctypes.byref (varinvangle))
        invangle        = varinvangle.value
        return          invangle

    @outOfPlumbInverseAngle.setter
    def outOfPlumbInverseAngle (self, invangle):
        """
        Inverso do ângulo de desaprumo
        """
        varinvangle     = ctypes.c_double (invangle)
        self.m_building.m_edilib.EDILIB_SET_PREDAD_DESAPRUMO (varinvangle)

#------------------------------------------------------------------------------
#       Aba Gerenciamento
#
class Management ():

    def __init__ (self, building):
        self.m_building      = building

    def _GetGerPre (self):
        varicgerpre     = ctypes.c_int (0)
        variconsfer     = ctypes.c_int (0)
        variapdfpla     = ctypes.c_int (0)
        variadwfpla     = ctypes.c_int (0)
        variadxfpla     = ctypes.c_int (0)
        self.m_building.m_edilib.EDILIB_GET_GERPRE (ctypes.byref (varicgerpre),
                        ctypes.byref (variconsfer), ctypes.byref (variapdfpla),
                        ctypes.byref (variadwfpla), ctypes.byref (variadxfpla))
        icgerpre        = varicgerpre.value
        iconsfer        = variconsfer.value
        iapdfpla        = variapdfpla.value
        iadwfpla        = variadwfpla.value
        iadxfpla        = variadxfpla.value
        return          icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla

    def _SetGerPre (self, icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla):
        varicgerpre     = ctypes.c_int (icgerpre)
        variconsfer     = ctypes.c_int (iconsfer)
        variapdfpla     = ctypes.c_int (iapdfpla)
        variadwfpla     = ctypes.c_int (iadwfpla)
        variadxfpla     = ctypes.c_int (iadxfpla)
        self.m_building.m_edilib.EDILIB_SET_GERPRE (varicgerpre, variconsfer,
                        variapdfpla, variadwfpla, variadxfpla)

    @property
    def gerpreActive (self):
        """
        (1) Se controle e transferência para o GerPrE ativada
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        return          icgerpre

    @gerpreActive.setter
    def gerpreActive (self, icgerpre):
        """
        (1) Se controle e transferência para o GerPrE ativada
        """
        icgerpre2, iconsfer, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        self._SetGerPre (icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla)

    @property
    def checkVariableRebar (self):
        """
        (1) Verificar a existência de ferros corridos e variáveis
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        return          iconsfer

    @checkVariableRebar.setter
    def checkVariableRebar (self, iconsfer):
        """
        (1) Verificar a existência de ferros corridos e variáveis
        """
        icgerpre, iconsfer2, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        self._SetGerPre (icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla)

    @property
    def pdfRequired (self):
        """
        (1) PDF de plantas requerido
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        return          iapdfpla

    @pdfRequired.setter
    def pdfRequired (self, iapdfpla):
        """
        (1) PDF de plantas requerido
        """
        icgerpre, iconsfer, iapdfpla2, iadwfpla, iadxfpla = self._GetGerPre ()
        self._SetGerPre (icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla)

    @property
    def dwfRequired (self):
        """
        (1) DWF de plantas requerido
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        return          iadwfpla

    @dwfRequired.setter
    def dwfRequired (self, iadwfpla):
        """
        (1) DWF de plantas requerido
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla2, iadxfpla = self._GetGerPre ()
        self._SetGerPre (icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla)

    @property
    def dxfRequired (self):
        """
        (1) DXF de plantas requerido
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla = self._GetGerPre ()
        return          iadxfpla

    @dxfRequired.setter
    def dxfRequired (self, iadxfpla):
        """
        (1) DXF de plantas requerido
        """
        icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla2 = self._GetGerPre ()
        self._SetGerPre (icgerpre, iconsfer, iapdfpla, iadwfpla, iadxfpla)


