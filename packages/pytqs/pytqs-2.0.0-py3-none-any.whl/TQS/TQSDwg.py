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
#    TQSDwg.PY         Módulo para leitura e gravação de desenhos DWG TQS
#                      Inclui geração de cotagens e ferros inteligentes
#-----------------------------------------------------------------------------
import ctypes
import TQS.TQSUtil

#-----------------------------------------------------------------------------
#    Aplicações TQS
#
IEDOUT    = 1    # Outras
IEDFOR    = 2    # Formas
IEDLAJ    = 3    # Lajes
IEDFUS    = 4    # Fundações sapatas
IEDFUE    = 5    # Fundações blocos
IEDFUT    = 6    # Fundações tubuloes
IEDVIG    = 7    # Vigas
IEDPIL    = 8    # Pilares
IEDTAB    = 9    # Armação genérica AGC & DP
IEDARQ    = 10   # Arquitetura
IEDMAD    = 11   # Madeira
IEDMA2    = 12   # Madeira
IEDMA3    = 13   # Madeira
IEDMA4    = 14   # Madeira
IEDCORB   = 15   # Corbar
IEDCOM    = 16   # Cormad
IEDALV    = 17   # Alvest
IEDPOR    = 18   # Pórtico
IEDGRE    = 19   # Grelha
IEDVPP    = 20   # Vigota pré-moldada protend
IEDPLW    = 21   # Leitor de PLW
IEDESC    = 22   # Escadas
IEDISE    = 23   # Interação solo-estrutura
IEDPRE    = 24   # Pré-moldados/Pré-fabricados
IEDRER    = 25   # Reservatórios/especiais
IEDPAR    = 26   # Paredes de concreto
#-----------------------------------------------------------------------------
#    Constantes usadas em cotagem
#
IDHOR     = 0         # Cotagem horizontal
IDVER     = 1         # Cotagem vertical
IDANG     = 2         # Cotagem alinhada
IDINC     = 3         # Cotagem inclinada
#-----------------------------------------------------------------------------
#    Tipos de objeto de desenho
#
DWGTYPE_EOF        = 0    # Fim de arquivo                
DWGTYPE_LINE       = 1    # Linha             
DWGTYPE_TEXT       = 2    # Texto                
DWGTYPE_POLYLINE   = 3    # Polyline            
DWGTYPE_BLOCK      = 4    # Insercao de bloco        
DWGTYPE_BLOCKEND   = 5    # Fim de bloco            
DWGTYPE_BLOCKBEGIN = 4    # Inicio de bloco        
DWGTYPE_CIRCLE     = 6    # Circulo            
DWGTYPE_ARC        = 7    # Arco                
DWGTYPE_CURVE      = 8    # Curva                
DWGTYPE_OBJECT     = 9    # Objeto de desenho
DWGTYPE_OBJECTEND  = 10   # Fim de leitura, objeto de desenho

#-----------------------------------------------------------------------------
#    Constantes usadas em Ferros Inteligentes
#
ICPDEF     = -1        # Usar default do arquivo de critérios

ICPPOS     = 0         # Ferro Reto: armadura horizontal positiva
ICPNEG     = 1         # Ferro Reto: armadura horizontal negativa

ICPTPDOBGAN= 0         # Tipo de dobra: Gancho tração NBR6118:2003 9.4.2.3
ICPTPDOBNOP= 1         # Tipo de dobra: Nó de pórtico NBR6118:2003 18.2.2

ICPSRA     = 0         # Comprimento total: Faces externas sem desconto de raio
ICPCRA     = 1         # Comprimento total: Desenvolvido com desconto de raio
ICPSMS     = 2         # Comprimento total: Soma simples dos trechos

ICPDOBSRA  = 0         # Comprimento das dobras: Face externa sem desconto de raio
ICPDOBCRA  = 1         # Comprimento das dobras: Desenvolvido com raio de dobra
ICPDOBSMS  = 2         # Comprimento das dobras: Comprimento do trecho

ICPMAN     = 0         # Aplicar raio de dobra: manualmente
ICPAUT     = 1         # Aplicar raio de dobra: automaticamente

ICPSCR     = 0         # Círculo da posição: Não
ICPPCR     = 1         # Círculo da posição: Em volta da posição
ICPPCG     = 2         # Círculo da posição: Não: Só texto aumentado
ICPPCA     = 3         # Círculo da posição: Não: Texto antes do número de ferros

ICPNSU     = 0         # Dobra de sustentação: normal
ICPDSU     = 1         # Dobra de sustentação: definida
ICPDS2     = 2         # Dobra de sustentação: definida na mesma direção

ICPESP     = 0         # Número de ferros: Núm Espaçamentos = Núm de ferros
ICPE1P     = 1         # Número de ferros: Núm Espaçamentos = Núm de ferros + 1
ICPE1M     = 2         # Número de ferros: Núm Espaçamentos = Núm de ferros - 1

ICPCIR     = 0         # Ferro em corte: Círculo
ICPFCR     = 1         # Ferro em corte: Bloco 'FERCOR'

ICPNNV     = 0         # Espacamento de ferros: em maciço
ICPNRV     = 1         # Espacamento de ferros: em nervuras

ICPSAL     = 0         # Alternância de ferros: Não
ICPCAL     = 1         # Alternância de ferros: Sim

ICPSTP     = 0         # Tipo de aço como comentário: Não
ICPCTP     = 1         # Tipo de aço como comentário: Sim

ICPSGA     = 0         # Tipo de gancho: Sem gancho
ICP090     = 1         # Tipo de gancho: Gancho a 90  graus
ICP135     = 2         # Tipo de gancho: Gancho a 135 graus
ICP180     = 3         # Tipo de gancho: Gancho a 180 graus

ICPNR2     = 0         # Número de ramos de estribos: 2 ramos 
ICPNR4     = 1         # Número de ramos de estribos: 4 ramos
ICPNR6     = 2         # Número de ramos de estribos: 6 ramos
ICPNR4B    = 3         # Número de ramos de estribos: 4 ramos configuração B

ICPENR     = 0         # Estribo de viga: Normal
ICPEFC     = 1         # Estribo de viga: Fechado
ICPEAB     = 2         # Estribo de viga: Aberto
ICPENC     = 3         # Estribo de viga: Normal com largura colaborante

ICPEGENFEC = 0         # Estribo genérico: Fechado
ICPEGENABR = 1         # Estribo genérico: Aberto
ICPEGENGRA = 2         # Estribo genérico: Grampo de pilar
ICPEGENCIR = 3         # Estribo genérico: Circular

ICPEGPONTOSLONG = 0    # Definição de estribos genéricos: Pontos longitudinais
ICPEGPONTOSSECA = 1    # Definição de estribos genéricos: Pontos da seção longitudinal
ICPEGPONTOSEXTR = 2    # Definição de estribos genéricos: Pontos externos

ICPTPPATA45= 0         # Patas de estribo: 45°
ICPTPPATA90= 1         # Patas de estribo: 90°

ICPCA1     = 0         # Cotagem de ferro negativo alternado: uma ponta
ICPCA2     = 1         # Cotagem de ferro negativo alternado: duas pontas

ICPFRT     = 0         # Tipo de ferro: Ferro reto
ICPFGN     = 1         # Tipo de ferro: Ferro genérico
ICPSTR     = 2         # Tipo de ferro: Estribo
ICPGRA     = 3         # Tipo de ferro: Grampo de vigas
ICPSTRGEN  = 4         # Tipo de ferro: Estribo genérico, pilar
ICPFAIMUL  = 5         # Tipo de ferro: Faixa múltipla (não é ferro)

ICPSRR     = 0         # Ferro repitido: Identificar
ICPCRR     = 1         # Ferro repitido: Identificar somente posição e quantidade

ICPQUEBR_SEMQUEBRA = 0 # Texto de ferro: Sem quebra
ICPQUEBR_SALTOCBCI = 1 # Texto de ferro: Salto C/ ou C=
ICPQUEBR_SALTOBITO = 2 # Texto de ferro: Salto {
ICPQUEBR_SALTODECD = 3 # Texto de ferro: Salto após C/
ICPQUEBR_SALTONPOS = 4 # Texto de ferro: Salto número de ferros

ICPCENTR_CENTRAD = 0   # Texto de ferros: Centrado
ICPCENTR_ESQUERD = 1   # Texto de ferros: Esquerda
ICPCENTR_DIREITA = 2   # Texto de ferros: Direita
#-----------------------------------------------------------------------------
#    Constantes usadas no DWG
#
IEXMAX      =  1024    # Máximo de pontos de uma poligonal

#-----------------------------------------------------------------------------
#    Classe de desenho
#
class Dwg ():
#
#    Construtor: carrega as bibliotecas e inicializa um desenho vazio
#
    def __init__ (self, pedmv=None):
        self.m_acessol  = None
        self.m_customdl = None
        self.m_eagpar   = None
        self.m_f2dtriaz = None
        self.m_mdwg     = None
        self.m_nlmpdwg  = None
        self.m_nomedwg  = ""
        self.m_icargaok = 0
        self.m_acessol  = TQS.TQSUtil.LoadDll ("ACESSOL.DLL")
        self.m_customdl = TQS.TQSUtil.LoadDll ("CUSTOMDL.DLL")
        self.m_eagpar   = TQS.TQSUtil.LoadDll ("EAGPAR.DLL")
        self.m_f2dtriaz = TQS.TQSUtil.LoadDll ("F2DTRIAZ.DLL")
        self.m_mdwg     = TQS.TQSUtil.LoadDll ("MDWG.DLL")
        self.m_nlmpdwg  = TQS.TQSUtil.LoadDll ("NLMPDWG.DLL")
        self.m_ipofer   = TQS.TQSUtil.LoadDll ("IPOFER.DLL")
        self.m_nv3d     = TQS.TQSUtil.LoadDll ("NV3D.DLL")
        if self.m_acessol != None and self.m_customdl != None and self.m_eagpar != None and self.m_f2dtriaz != None and self.m_mdwg != None and self.m_nlmpdwg != None and self.m_ipofer != None:
            self.m_icargaok = 1
        else:
            return

        self.m_pedmv    = 0
        self.file       = File (self)
        if              pedmv is None:
            self.file.New ()
        else:
            self.m_pedmv= pedmv

        self.draw       = Draw (self)
        self.dim        = Dim (self)
        self.limits     = Limits (self)
        self.iterator   = Iterator (self)
        self.settings   = Settings (self)
        self.levelstable= LevelsTable (self)
        self.blockstable= BlocksTable (self)
        self.xreference = XReference (self)
        self.edit       = Edit (self)
        self.plotting   = Plotting (self)
        self.globalrebar= GlobalRebar (self)
        self.m_acessol.ACL_INIACESSO ()
#
#    Representação deste objeto
#
    def __str__(self):
        msg         = "Class TQSDwg"
        msg         += "\n   self.m_pedmv %x"  % self.m_pedmv
        msg         += "\n   sef.m_nomedwg [" + self.m_nomedwg + "]"
        msg         += "\n   self.m_acessol " + str (self.m_acessol)
        msg         += "\n   self.m_customdl" + str (self.m_customdl)
        msg         += "\n   self.m_eagpar  " + str (self.m_eagpar)
        msg         += "\n   self.m_f2dtriaz" + str (self.m_f2dtriaz)
        msg         += "\n   self.m_mdwg    " + str (self.m_mdwg)
        msg         += "\n   self.m_nlmpdwg " + str (self.m_nlmpdwg)
        msg         += "\n   self.m_ipofer  " + str (self.m_ipofer)
        return         msg

#
#    Inicializa cores e tabela de plotagem
#
    def CarregarCores (self):
        istat          = 0
        paristat       = ctypes.c_int (istat)
        parpedmv       = ctypes.c_void_p (self.m_pedmv)
        self.m_mdwg.g_carregcores (parpedmv, ctypes.byref(paristat))
        self.m_mdwg.tabplt_ini (parpedmv, ctypes.byref(paristat))
        parnomtab      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_mdwg.tabplt_ler (parpedmv, parnomtab, ctypes.byref(paristat))

#-----------------------------------------------------------------------------
#    Comandos relacionados a arquivos
#
class File ():

    def __init__ (self, dwg):
        self.m_dwg  = dwg
#
#    Abre desenho novo SEM_NOME - fecha anterior se aberto
#
    def New (self):
        """
        Inicializa novo desenho para ser salvo com SaveAs
        """
        self.Close ()

        parseed     = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_acessol.ACLSEED (parseed, 0)
        seed        = "%s" % parseed.value.decode(TQS.TQSUtil.CHARSET)
        self.m_dwg.m_nomedwg = "SEM_NOME"
        parnomedwg  = ctypes.c_char_p (self.m_dwg.m_nomedwg.encode(TQS.TQSUtil.CHARSET))
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        istat       = 0
        paristat    = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_desopn (parnomedwg, parseed, None, 
                              ctypes.byref(parpedmv), ctypes.byref(paristat))
        self.m_dwg.m_pedmv = parpedmv.value
        istat       = paristat.value
        if istat != 0:
            TQS.TQSUtil.writef ("Nao abri o desenho " + self.m_nomedwg)
            return

        self.m_dwg.m_mdwg.COTINI ()
        self.m_dwg.m_mdwg.COTIFOR (parpedmv)
        self.m_dwg.m_mdwg.g_extpbl (parpedmv)
        self.m_dwg.CarregarCores ()
#
#    Abre desenho existente
#
    def Open (self, dwgname):
        """
        Abre e carrega desenho existente\n
        Retorna (0) Ok (!=0) Não abriu\n
        dwgname    Nome do desenho
        """
        self.Close ()
        self.m_dwg.m_acessol.ACL_INIACESSO ()
        self.m_dwg.m_nomedwg = dwgname
        parnomedwg  = ctypes.c_char_p (self.m_dwg.m_nomedwg.encode(TQS.TQSUtil.CHARSET))
        istat       = 0
        paristat    = ctypes.c_int (istat)
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_extopn (parnomedwg, ctypes.byref(paristat), 
                              None, ctypes.byref(parpedmv))
        self.m_dwg.m_pedmv = parpedmv.value
        istat       = paristat.value
        if         istat != 0:
            TQS.TQSUtil.writef ("Nao abri o desenho [%s]"% self.m_dwg.m_nomedwg)
        else:
            self.m_dwg.m_mdwg.COTIFOR (parpedmv)
            self.m_dwg.m_mdwg.g_extpbl (parpedmv)
            self.m_dwg.CarregarCores ()
        return        istat


    def Close (self):
        """
        Fecha um desenho, não salva
        """
        if self.m_dwg.m_pedmv != 0:
            par = ctypes.c_void_p (self.m_dwg.m_pedmv)
            self.m_dwg.m_mdwg.g_extclo (par)
        self.m_dwg.m_pedmv = 0


    def Save (self):
        """
        Salva o desenho com nome atual, não fecha o arquivo
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_rectam (parpedmv)
        self.m_dwg.m_mdwg.g_desslvcon (parpedmv)


    def SaveAs (self, dwgname):
        """
        Salva o desenho com o nome fornecido\n
        dwgname <- Nome do desenho a salvar
        """
        self.m_dwg.m_nomedwg = dwgname
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pardwgname  = ctypes.c_char_p (dwgname.encode(TQS.TQSUtil.CHARSET))
        istat       = 0
        paristat    = ctypes.c_int (istat)
        if         dwgname.upper ().find (".DXF") >= 0:
            self.m_dwg.m_mdwg.g_salvarcomodxf (parpedmv, pardwgname, ctypes.byref (paristat))
            istat   = paristat.value
            if        istat != 0:
                TQS.TQSUtil.writef ("Erro salvando DXF: [%s]" % dwgname)
                return
        elif    dwgname.upper ().find (".PDF") >= 0:
            dimsca  = self.m_dwg.settings.scale
            pardimsca = ctypes.c_double (dimsca)
            self.m_dwg.m_mdwg.g_salvarcomopdf (parpedmv, pardwgname, pardimsca, ctypes.byref (paristat))
            istat   = paristat.value
            if        istat != 0:
                TQS.TQSUtil.writef ("Erro salvando PDF: [%s]" % dwgname)
                return
        else:
            self.m_dwg.m_mdwg.g_edmrdn (parpedmv, pardwgname)
            self.m_dwg.m_mdwg.g_rectam (parpedmv)
            self.m_dwg.m_mdwg.g_edmdsn (parpedmv)
            self.m_dwg.m_mdwg.g_desslvcon (parpedmv)


    def Name (self):
        """
        Retorna o nome do desenho atual
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pardwgname  = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_edmdwgfil (parpedmv, pardwgname)
        return      pardwgname.value.decode(TQS.TQSUtil.CHARSET)


    def PurgeBlocks (self):
        """
        Elimina blocos não utilizados do desenho
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_purgeblk (parpedmv)


    def PurgeLevels (self):
        """
        Elimina niveis não utilizados do desenho
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_purgelay (parpedmv)


    def LoadColors (self):
        """
        Carrega a tabela padrão de cores associada ao sistema/subsistema, que devem ser definidos antes
        """
        self.m_dwg.CarregarCores ()


    def IsModified (self):
        """
        Retorna (1) se o desenho foi modificado depois de aberto.
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        istat       = 0
        paristat    = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_modver (parpedmv,  ctypes.byref (paristat))
        istat       = paristat.value
        return      istat


    def IsModifiedAfterCreation (self):
        """
        Retorna (1) se o desenho foi modificado por edição gráfica alguma vez após a sua criação.
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        imodificado = 0
        parimodificado = ctypes.c_int (imodificado)
        self.m_dwg.m_mdwg.g_edmexlerimodificado (parpedmv, ctypes.byref (parimodificado))
        imodificado = parimodificado.value
        return      imodificado


    def IsOutOfProject (self):
        """
        Retorna (1) se o desenho foi retirado do projeto.
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iforadoproj = 0
        pariforadoproj = ctypes.c_int (iforadoproj)
        self.m_dwg.m_mdwg.g_edmexleriforadoproj (parpedmv, ctypes.byref (pariforadoproj))
        iforadoproj = pariforadoproj.value
        return      iforadoproj


    def IsVerified (self):
        """
        Retorna (1) se o desenho foi verificado pelo engenheiro.
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iverificado = 0
        pariverificado = ctypes.c_int (iverificado)
        self.m_dwg.m_mdwg.g_edmexleriverificado (parpedmv, ctypes.byref (pariverificado))
        iverificado = pariverificado.value
        return      iverificado


#-----------------------------------------------------------------------------
#    Comandos inserção de elementos gráficos no desenho
#
class Draw ():

    def __init__ (self, dwg):
        """
        Inicialização da classe de desenho. Unidades usadas: cm e graus.
        """
        self.m_dwg  = dwg

    def Line  (self, x1, y1, x2, y2):
        """
        Linha entre 2 pontos\n
        x1              <- Ponto 1 (cm)\n
        y1              <- Ponto 1 (cm)\n
        x2              <- Ponto 2 (cm)\n
        y2              <- Ponto 2 (cm)
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parx1        = ctypes.c_double (x1)
        pary1        = ctypes.c_double (y1)
        parx2        = ctypes.c_double (x2)
        pary2        = ctypes.c_double (y2)
        self.m_dwg.m_mdwg.g_deslin (parpedmv, 
            ctypes.byref (parx1), ctypes.byref (pary1), 
            ctypes.byref (parx2), ctypes.byref (pary2))

    def Rectangle (self, x1, y1, x2, y2):
        """
        Retângulo entre 2 pontos\n
        x1              <- Canto esquerdo inferior (cm)\n
        y1              <- Canto esquerdo inferior (cm)\n
        x2              <- Canto direito  superior (cm)\n
        y2              <- Canto direito  superior (cm)
        """
        self.PolyStart ()
        self.PolyEnterPoint (x1, y1)
        self.PolyEnterPoint (x2, y1)
        self.PolyEnterPoint (x2, y2)
        self.PolyEnterPoint (x1, y2)
        self.PolyEnterPoint (x1, y1)
        self.Polyline ()

    def PolyStart (self):
        """
        Inicia acumulação de pontos por PolyEnterPoint.\n
        Os pontos acumulados podem ser usados em:\n
            Polyline\n
            PolylineFilled\n
            PolylineCurve
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_despolyiniciar (parpedmv)

    def PolyEnterPoint  (self, x, y):
        """
        Acumula um ponto de uma polyline\n
        x            <- Ponto (cm)\n
        y            <- Ponto (cm)\n
        Os pontos acumulados podem ser usados em:\n
            Polyline\n
            PolylineFilled\n
            PolylineCurve
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parx        = ctypes.c_double (x)
        pary        = ctypes.c_double (y)
        self.m_dwg.m_mdwg.g_despolyentrar (parpedmv, ctypes.byref (parx), ctypes.byref (pary))

    def PolyEnterXY  (self, xy):
        """
        Acumula um vetor de uma polyline\n
        Formato: [ [x1,y1], [x2,y2], ...]\n
        Os pontos acumulados podem ser usados em:\n
            Polyline\n
            PolylineFilled\n
            PolylineCurve
        """
        self.PolyStart ()
        for pt in xy:
            self.PolyEnterPoint (pt [0], pt [1])

    def Polyline  (self):
        """
        Polyline com os pontos acumulados por PolyEnterPoint
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_despolypln (parpedmv)

    def PolylineFilled (self):
        """
        Polyline preenchida com os pontos acumulados por PolyEnterPoint
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_despolyplnp (parpedmv)

    def PolylineCurve (self):
        """
        Polyline curva com os pontos acumulados por PolyEnterPoint
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_despolycur (parpedmv)

    def Arc (self, xc, yc, r, angi, angf):
        """
        Arco por xc,yc raio R e ângulos inicial/final (graus)\n
        xc           <- Abcissa  centro (cm)\n
        yc           <- Ordenada centro (cm)\n
        r            <- Raio (cm)\n
        angi         <- Ângulo inicial (graus), sentido anti-horário\n
        angf         <- Ângulo final (graus), sentido anti-horário\n
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parxc      = ctypes.c_double (xc)
        paryc      = ctypes.c_double (yc)
        parr       = ctypes.c_double (r)
        parangi    = ctypes.c_double (angi)
        parangf    = ctypes.c_double (angf)
        self.m_dwg.m_mdwg.g_desarc (parpedmv,
            ctypes.byref (parxc), ctypes.byref (paryc), ctypes.byref (parr), 
            ctypes.byref (parangi), ctypes.byref (parangf))

    def Circle (self, xc, yc, r):
        """
        Círculo por xc,yc e raio R\n
        xc           <- Centro (cm)\n
        yc           <- Centro (cm)\n
        r            <- Raio (cm)
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parxc      = ctypes.c_double (xc)
        paryc      = ctypes.c_double (yc)
        parr       = ctypes.c_double (r)
        self.m_dwg.m_mdwg.g_descrc (parpedmv, 
            ctypes.byref (parxc), ctypes.byref (paryc), ctypes.byref (parr)) 

    def Text (self, x, y, h, ang, text):
        """
        Têxto em coordenadas, altura e ângulo fornecidos\n
        x            <- Ponto de inserção (cm)\n
        y            <- Ponto de inserção (cm)\n
        h            <- Altura (cm)\n
        ang          <- Ângulo (graus), sentido anti-horário\n
        text         <- Texto a desenhar
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parx        = ctypes.c_double (x)
        pary        = ctypes.c_double (y)
        parh        = ctypes.c_double (h)
        parang      = ctypes.c_double (ang)
        partext     = ctypes.c_char_p (text.encode(TQS.TQSUtil.CHARSET))
        self.m_dwg.m_mdwg.g_desatx (parpedmv, ctypes.byref (parh))
        self.m_dwg.m_mdwg.g_desang (parpedmv, ctypes.byref (parang))
        self.m_dwg.m_mdwg.g_destex (parpedmv, ctypes.byref (parx), 
                                    ctypes.byref (pary), partext)

    def BlockOpen (self, blockname, xbase, ybase):
        """
        Criação de um novo bloco interno.\n
        Elementos gráficos criados a seguir (ex: Line) entrarão dentro do bloco.\n
        blockname    <- Nome do bloco\n
        xbase        <- Base do bloco. Coincidirá com o ponto de inserção.\n
        ybase        <- Base do bloco. 
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parblockname= ctypes.c_char_p (blockname.encode(TQS.TQSUtil.CHARSET))
        parxbase    = ctypes.c_double (xbase)
        parybase    = ctypes.c_double (ybase)
        icond       = 1        # Overlap
        paricond    = ctypes.c_int (icond)
        self.m_dwg.m_mdwg.g_opnblx (parpedmv, parblockname, 
                ctypes.byref (parxbase), ctypes.byref (parybase), ctypes.byref (paricond))

    def BlockClose (self):
        """
        Fim da criação de um bloco interno
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_desfbl (parpedmv)

    def BlockInsert (self, blockname, x, y, escx, escy, ang):
        """
        Inserção de um bloco interno pré-definido.\n
        blockname    <- Nome do bloco\n
        x            <- Ponto de inserção (cm)\n
        y            <- Ponto de inserção (cm)\n
        escx         <- Escala X\n
        escy         <- Escala Y\n
        ang          <- Ângulo de inserção (graus), sentido anti-horário
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parblockname= ctypes.c_char_p (blockname.encode(TQS.TQSUtil.CHARSET))
        parx        = ctypes.c_double (x)
        pary        = ctypes.c_double (y)
        parescx     = ctypes.c_double (escx)
        parescy     = ctypes.c_double (escy)
        parang      = ctypes.c_double (ang)
        self.m_dwg.m_mdwg.g_desins (parpedmv, parblockname, 
                  ctypes.byref (parx), ctypes.byref (pary), 
                  ctypes.byref (parescx), ctypes.byref (parescy), 
                  ctypes.byref (parang))

    def BlockLoadFromDwg  (self, dwgname):
        """
        Carregar um arquivo externo e transformar em bloco interno\n
        dwgname         <- Nome do arquivo de desenho com o bloco\n
        retorna:        -> (0) Se carregou, (1) Se erro
        """
        parpedmv    = ctypes.c_void_p (self.m_dwg.m_pedmv)
        dir        = ""
        pardir     = ctypes.c_char_p (dir.encode(TQS.TQSUtil.CHARSET))
        pardwgname = ctypes.c_char_p (dwgname.encode(TQS.TQSUtil.CHARSET))
        istat      = 0
        paristat   = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_inilbk (parpedmv, pardir, pardwgname, ctypes.byref (paristat))
        istat      = paristat.value
        return     istat

    @property
    def level (self):
        """
        Nível atual de desenho, sempre na forma numérica
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        nivel       = 0
        parnivel    = ctypes.c_int (nivel)
        self.m_dwg.m_mdwg.g_desvnv (parpedmv, ctypes.byref (parnivel))
        nivel       = parnivel.value
        return      nivel

    @level.setter
    def level (self, level):
        """
        Nível atual de desenho, sempre na forma numérica
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        slevel      = level
        if        level is not str:
            slevel  = str (level)
        parlevel    = ctypes.c_char_p (slevel.encode(TQS.TQSUtil.CHARSET))
        nivel       = 0
        parnivel    = ctypes.c_int (nivel)
        self.m_dwg.m_mdwg.g_desnivalfa (parpedmv, parlevel, ctypes.byref (parnivel))
        nivel       = parnivel.value

    @property
    def style (self):
        """
        Estilo atual de desenho ou (-1) para usar o estilo associado ao nível
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iestilo     = 0
        pariestilo  = ctypes.c_int (iestilo)
        self.m_dwg.m_mdwg.g_deslerstl (parpedmv, ctypes.byref (pariestilo))
        iestilo     = pariestilo.value
        return      iestilo
 
    @style.setter
    def style (self, istyle):
        """
        Define o estilo atual de desenho ou (-1) do nível\n
        istyle    Estilo conforme tabela de estilos. (-1) usa estilo do nível
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariestilo  = ctypes.c_int (istyle)
        self.m_dwg.m_mdwg.g_desstl (parpedmv, ctypes.byref (pariestilo))

    @property
    def color (self):
        """
        Cor atual de desenho (1..255) ou (-1) para usar a cor associada ao nível de desenho
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        icor           = 0
        paricor        = ctypes.c_int (icor)
        self.m_dwg.m_mdwg.g_deslercor (parpedmv, ctypes.byref (paricor))
        icor           = paricor.value
        return         icor

    @color.setter
    def color (self, icolor):
        """
        Cor atual de desenho (1..255) ou (-1) para usar a cor associada ao nível de desenho
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        paricor        = ctypes.c_int (icolor)
        self.m_dwg.m_mdwg.g_descor (parpedmv, ctypes.byref (paricor))

    def DwgMix  (self, dwgname, deltax, deltay):
        """
        Misturar um desenho com o atual\n
        dwgname         <- Nome do desenho a misturar\n
        deltax          <- Desloca o desenho misturado em x (cm)\n
        deltay          <- Desloca o desenho misturado em y (cm)\n
        Retorna:        -> (0) Mistura Ok (1) Se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pardwgname  = ctypes.c_char_p (dwgname.encode(TQS.TQSUtil.CHARSET))
        pardeltax   = ctypes.c_double (deltax)
        pardeltay   = ctypes.c_double (deltay)
        istat       = 0
        paristat    = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_inimix (parpedmv, pardwgname, 
                         ctypes.byref (pardeltax), ctypes.byref (pardeltay), 
                         ctypes.byref (paristat))
        istat       = paristat.value
        return      istat

    def XrefInsert  (self, dwgname, deltax, deltay, ang):
        """
        Inserir um desenho de referência externa\n
        dwgname      Nome do desenho\n
        deltax       Deslocamento adicional X\n
        deltay       Deslocamento adicional Y\n
        ang          Ângulo de rotação em graus\n
        Retorna:     (0) Se inseriu (1) Se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pardwgname  = ctypes.c_char_p (dwgname.encode(TQS.TQSUtil.CHARSET))
        parblockname= ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        istat       = 0
        paristat    = ctypes.c_int (istat)
        index       = 0
        parindex    = ctypes.c_int (index)
        self.m_dwg.m_mdwg.refx_acharef (parpedmv, pardwgname, ctypes.byref (parindex))
        index       = parindex.value
        if        index >= 0:
            interna    = 0
            parinterna = ctypes.c_int (interna)
            pardwgname = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
            pedmref    = 0
            parpedmref = ctypes.c_void_p (pedmref)
            ligada     = 0
            parligada  = ctypes.c_int (ligada)
            self.m_dwg.m_mdwg.refx_ler (parpedmv, parindex, ctypes.byref (parinterna),
                                 pardwgname, ctypes.byref (parpedmref), 
                                 ctypes.byref (parligada), parblockname)
            interna    = parinterna.value
            if        interna != 0:
                return    1
            istat     = 0
        else:
            self.m_dwg.m_mdwg.refx_criaexterno (parpedmv, pardwgname, parblockname, 
                                            ctypes.byref (paristat))
            istat     = paristat.value

        if        istat != 0:
            return  istat
        blockname   = parblockname.value.decode(TQS.TQSUtil.CHARSET)
        escx        = 1.
        escy        = 1.
        self.BlockInsert (blockname, deltax, deltay, escx, escy, ang)
        return        istat

#-----------------------------------------------------------------------------
#    Leitura de limites do DWG
#
class Limits ():

    def __init__ (self, dwg):
        self.m_dwg     = dwg

    def FileLimits (self, dwgname):
        """
        Retorna os limites de um desenho sem carrega-lo na memória.\n
        Retorna: xmin, ymin, xmax, ymax, istat=(0) Ok (1) Não leu o arquivo
        """
        pardwgname     = ctypes.c_char_p (dwgname.encode(TQS.TQSUtil.CHARSET))
        xmin           = 0.
        ymin           = 0.
        xmax           = 0.
        ymax           = 0.
        parxmin        = ctypes.c_double (xmin)
        parymin        = ctypes.c_double (ymin)
        parxmax        = ctypes.c_double (xmax)
        parymax        = ctypes.c_double (ymax)
        xmin2          = 0.
        ymin2          = 0.
        xmax2          = 0.
        ymax2          = 0.
        parxmin2       = ctypes.c_double (xmin2)
        parymin2       = ctypes.c_double (ymin2)
        parxmax2       = ctypes.c_double (xmax2)
        parymax2       = ctypes.c_double (ymax2)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_loaext (pardwgname, 
            ctypes.byref (parxmin) , ctypes.byref (parymin), 
            ctypes.byref (parxmax) , ctypes.byref (parymax),
            ctypes.byref (parxmin2), ctypes.byref (parymin2),
            ctypes.byref (parxmax2), ctypes.byref (parymax2), 
            ctypes.byref (paristat))
        xmin           = parxmin.value
        ymin           = parymin.value
        xmax           = parxmax.value
        ymax           = parymax.value
        istat          = paristat.value
        return         xmin, ymin, xmax, ymax, istat

    def DwgLimits (self):
        """
        Le os limites do desenho atual\n
        Retorna: xmin, ymin, xmax, ymax
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        xmin           = 0.
        ymin           = 0.
        xmax           = 0.
        ymax           = 0.
        parxmin        = ctypes.c_double (xmin)
        parymin        = ctypes.c_double (ymin)
        parxmax        = ctypes.c_double (xmax)
        parymax        = ctypes.c_double (ymax)
        self.m_dwg.m_mdwg.g_ledext (parpedmv, 
            ctypes.byref (parxmin) , ctypes.byref (parymin), 
            ctypes.byref (parxmax) , ctypes.byref (parymax))
        xmin           = parxmin.value
        ymin           = parymin.value
        xmax           = parxmax.value
        ymax           = parymax.value
        return         xmin, ymin, xmax, ymax

    def UpdateLimits (self):
        """
        Recalcula os limites do desenho atual
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_rectam (parpedmv)

    def WindowLimits (self):
        """
        Lê a janela inicial do desenho no EAG\n
        Retorna: xmin, ymin, xmax, ymax
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        xmin           = 0.
        ymin           = 0.
        xmax           = 0.
        ymax           = 0.
        parxmin        = ctypes.c_double (xmin)
        parymin        = ctypes.c_double (ymin)
        parxmax        = ctypes.c_double (xmax)
        parymax        = ctypes.c_double (ymax)
        self.m_dwg.m_mdwg.g_letam (parpedmv,  
            ctypes.byref (parxmin) , ctypes.byref (parymin), 
            ctypes.byref (parxmax) , ctypes.byref (parymax))
        xmin           = parxmin.value
        ymin           = parymin.value
        xmax           = parxmax.value
        ymax           = parymax.value
        return         xmin, ymin, xmax, ymax

    def DefineWindowLimits (self, xmin, ymin, xmax, ymax):
        """
        Define a janela inicial do desenho no EAG
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        xmin           = 0.
        ymin           = 0.
        xmax           = 0.
        ymax           = 0.
        parxmin        = ctypes.c_double (xmin)
        parymin        = ctypes.c_double (ymin)
        parxmax        = ctypes.c_double (xmax)
        parymax        = ctypes.c_double (ymax)
        self.m_dwg.m_mdwg.g_defdwv (parpedmv,  
            ctypes.byref (parxmin) , ctypes.byref (parymin), 
            ctypes.byref (parxmax) , ctypes.byref (parymax))

#-----------------------------------------------------------------------------
#    Iteração de elementos no DWG
#
class Iterator ():

    def __init__ (self, dwg):
        self.m_dwg  = dwg
        self.tipoobj = dict ((
            [DWGTYPE_LINE     , "Linha"], 
            [DWGTYPE_TEXT     , "Texto"], 
            [DWGTYPE_POLYLINE , "Polyline"], 
            [DWGTYPE_BLOCK    , "Bloco"], 
            [DWGTYPE_BLOCKEND , "Fim de bloco"],
            [DWGTYPE_CIRCLE   , "Circulo"], 
            [DWGTYPE_ARC      , "Arco"], 
            [DWGTYPE_CURVE    , "Curva"], 
            [DWGTYPE_OBJECT   , "Objeto"],
            [DWGTYPE_OBJECTEND, "Fim de objeto"],
            ))

    def Begin (self):
        """
        Posiciona o desenho para leitura no início
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_extrew (parpedmv)

    def Next (self):
        """
        Lê o próximo elemento\n
        Retorna: tipo iterator.DWGTYPE_xxxx (DWGTYPE_EOF no final)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_extpeg (parpedmv, ctypes.byref (paristat))
        istat          = paristat.value
        itype          = DWGTYPE_EOF
        if             istat == 0:
            itype      = self.itype
        return         itype


    @property
    def itype (self):
        """
        Retorna tipo iterator.DWGTYPE_xxxx do elemento gráfico lido
        """
        itipo          = DWGTYPE_EOF
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iextip".encode(TQS.TQSUtil.CHARSET))
        paritipo       = ctypes.c_int (itipo)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (paritipo))
        itipo          = paritipo.value
        return         itipo

    @property
    def elementName (self):
        """
        Retorna nome do tipo do elemento gráfico lido
        """
        nome           = "Indefinido"
        itipo          = self.itype
        if             itipo in self.tipoobj:
            nome       = self.tipoobj [itipo]
        return         nome

    def SetPosition (self, addr):
        """
        Posiciona para leitura na posição addr
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr        = ctypes.c_void_p (addr)
        self.m_dwg.m_mdwg.g_extpnt (parpedmv, ctypes.byref (pariadr))

    def GetElementReadPosition (self):
        """
        Retorna a posição do último elemento lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        addr           = 0
        pariadr        = ctypes.c_void_p (addr)
        itype          = DWGTYPE_EOF
        paritype       = ctypes.c_int (itype)
        self.m_dwg.m_mdwg.g_extpnr (parpedmv, ctypes.byref (pariadr), 
            ctypes.byref (paritype))
        addr           = pariadr.value
        return         addr

    def GetElementWritePosition (self):
        """
        Retorna a posição do último elemento gravado
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        addr           = 0
        pariadr        = ctypes.c_void_p (addr)
        self.m_dwg.m_mdwg.g_extpng (parpedmv, ctypes.byref (pariadr))
        addr           = pariadr.value
        return         addr

    def GetReadPosition (self):
        """
        Retorna a posição do próximo elemento a ser lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        addr           = 0
        pariadr        = ctypes.c_void_p (addr)
        self.m_dwg.m_mdwg.g_extprr (parpedmv, ctypes.byref (pariadr))
        addr           = pariadr.value
        return         addr

    def GetWritePosition (self):
        """
        Retorna a posição do próximo elemento a ser gravado
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        addr           = 0
        pariadr        = ctypes.c_void_p (addr)
        self.m_dwg.m_mdwg.g_extpnw (parpedmv, ctypes.byref (pariadr))
        addr           = pariadr.value
        return         addr

    def SetBlockPosition (self, blockname):
        """
        Posiciona para a leitura dos elementos internos a um bloco\n
        Retorna: (0) Ok (1) O bloco não existe
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parblockname   = ctypes.c_char_p (blockname.encode(TQS.TQSUtil.CHARSET))
        addr           = 0
        pariadr        = ctypes.c_void_p (addr)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_extpbr (parpedmv, parblockname, ctypes.byref (pariadr), 
                                    ctypes.byref (paristat))
        istat          = paristat.value
        return         istat

    def CopyReadAtribbutes (self):
        """
        Copia os atributos do último elemento lido para uso no próximo elemento a ser gravado
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_descopyatr (parpedmv)

    def GetPolylinePt (self, ipt):
        """
        Retorna as coordenadas x,y de extxy, ponto ipt
        """
        if             ipt < 0 or ipt >= self.xySize:
            TQS.TQSUtil.writef ("Indice invalido de ponto %d/%d" % (ipt, self.xySize))
            return     0., 0.
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extxy".encode(TQS.TQSUtil.CHARSET))
        paript         = ctypes.c_int (ipt)
        x              = 0.
        parx           = ctypes.c_double (x)
        y              = 0.
        pary           = ctypes.c_double (y)
        self.m_dwg.m_mdwg.g_extgra_ler_xy (parpedmv, parnomvar, ctypes.byref (paript), 
                                           ctypes.byref (parx), ctypes.byref (pary))
        x              = parx.value
        y              = pary.value
        return         x, y

    @property
    def x1 (self):
        """
        X1 de linha/texto/inserção de bloco
        """
        x, y           = self.GetPolylinePt (0)
        return         x

    @property
    def y1 (self):
        """
        Y1 de linha/texto/inserção de bloco
        """
        x, y           = self.GetPolylinePt (0)
        return         y

    @property
    def x2 (self):
        """
        X2 de linha
        """
        x, y           = self.GetPolylinePt (1)
        return         x

    @property
    def y2 (self):
        """
        Y2 de linha
        """
        x, y           = self.GetPolylinePt (1)
        return         y

    @property
    def xySize (self):
        """
        Número de pontos de poligonal
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexnp".encode(TQS.TQSUtil.CHARSET))
        np             = 0
        parnp          = ctypes.c_int (np)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (parnp))
        np             = parnp.value
        return         np

    @property
    def xy (self):
        """
        Leitura da matriz de pontos inteira
        """
        np             = self.xySize
        xy             = []
        for            ipt in range (0, np):
            x, y       = self.GetPolylinePt (ipt)
            xy.append  ([x, y])
        return         xy

    @property
    def isFilled (self):
        """
        Retorna (1) se a poligonal atual é tipo preenchida
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        ipreenche      = 0
        paripreenche   = ctypes.c_int (ipreenche)
        self.m_dwg.m_mdwg.g_verpolypre (parpedmv, ctypes.byref (paripreenche))
        ipreenche      = paripreenche.value
        return         ipreenche

    @property
    def xc (self):
        """
        Retorna o centro de arco/círculo
        """
        x, y           = self.GetPolylinePt (0)
        return         x

    @property
    def yc (self):
        """
        Retorna o centro de arco/círculo
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        x, y           = self.GetPolylinePt (0)
        return         y

    @property
    def radius (self):
        """
        Retorna o raio de um arco/círculo
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extlrg".encode(TQS.TQSUtil.CHARSET))
        radiusx        = 0.
        parradius      = ctypes.c_double (radiusx)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parradius))
        radiusx        = parradius.value
        return         radiusx

    @property
    def startAngle (self):
        """
        Retorna o ângulo inicial de um arco (graus)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extalt".encode(TQS.TQSUtil.CHARSET))
        angi           = 0.
        parangi        = ctypes.c_double (angi)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parangi))
        angi           = parangi.value
        return         angi

    @property
    def endAngle (self):
        """
        Retorna o ângulo final de um arco (graus)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extang".encode(TQS.TQSUtil.CHARSET))
        angf           = 0.
        parangf        = ctypes.c_double (angf)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parangf))
        angf           = parangf.value
        return         angf

    @property
    def textHeight (self):
        """
        A altura do último texto lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extalt".encode(TQS.TQSUtil.CHARSET))
        alttxt         = 0.
        paralttxt      = ctypes.c_double (alttxt)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (paralttxt))
        alttxt         = paralttxt.value
        return         alttxt

    @property
    def textAngle (self):
        """
        O ângulo do último texto lido (graus)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extang".encode(TQS.TQSUtil.CHARSET))
        angf           = 0.
        parangf        = ctypes.c_double (angf)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parangf))
        angf           = parangf.value
        return         angf

    @property
    def textLength (self):
        """
        Retorna o número de caracteres do texto lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexnc".encode(TQS.TQSUtil.CHARSET))
        nc             = 0
        parnc          = ctypes.c_int (nc)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (parnc))
        nc             = parnc.value
        return         nc

    @property
    def text (self):
        """
        Retorna o texto lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iextxt".encode(TQS.TQSUtil.CHARSET))
        partxt         = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_extgra_ler_string (parpedmv, parnomvar, partxt)
        return         partxt.value.decode(TQS.TQSUtil.CHARSET)

    @property
    def blockName (self):
        """
        Retorna o nome do bloco inserido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extnomblo".encode(TQS.TQSUtil.CHARSET))
        parnomblo      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_extgra_ler_string (parpedmv, parnomvar, parnomblo)
        return         parnomblo.value.decode(TQS.TQSUtil.CHARSET)

    @property
    def xScale (self):
        """
        Escala X de um bloco inserido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extesx".encode(TQS.TQSUtil.CHARSET))
        escx           = 0.
        parescx        = ctypes.c_double (escx)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parescx))
        escx           = parescx.value
        return         escx

    @property
    def yScale (self):
        """
        Escala Y de um bloco inserido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extesy".encode(TQS.TQSUtil.CHARSET))
        escy           = 0.
        parescy        = ctypes.c_double (escy)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parescy))
        escy           = parescy.value
        return         escy

    @property
    def insertAngle (self):
        """
        Ângulo de um bloco inserido (graus)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extanb".encode(TQS.TQSUtil.CHARSET))
        angrad         = 0.
        parangrad      = ctypes.c_double (angrad)
        self.m_dwg.m_mdwg.g_extgra_ler_double (parpedmv, parnomvar, ctypes.byref (parangrad))
        angrad         = parangrad.value
        return         angrad * TQS.TQSUtil.RADGRAUS

    @property
    def level (self):
        """
        Nível de um elemento lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexil".encode(TQS.TQSUtil.CHARSET))
        nivel          = 0
        parnivel       = ctypes.c_int (nivel)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (parnivel))
        nivel          = parnivel.value
        return         nivel

    @property
    def color (self):
        """
        Cor (0..255) de um elemento lido (considerando o nível)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexcor".encode(TQS.TQSUtil.CHARSET))
        icor           = 0
        paricor        = ctypes.c_int (icor)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (paricor))
        icor           = paricor.value
        return         icor

    @property
    def colorRGB (self):
        """
        Cor RGB opcional de um elemento lido (considerando o nível)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexcorrgb".encode(TQS.TQSUtil.CHARSET))
        icor           = 0
        paricor        = ctypes.c_int (icor)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (paricor))
        icor           = paricor.value
        return         icor

    @property
    def style (self):
        """
        Estilo de um elemento lido  (considerando o nível)
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexstl".encode(TQS.TQSUtil.CHARSET))
        iestil         = 0
        pariestil      = ctypes.c_int (iestil)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (pariestil))
        iestil         = pariestil.value
        return         iestil

    @property
    def levelLock (self):
        """
        (1) se nível do elemento lido travado
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("itravado".encode(TQS.TQSUtil.CHARSET))
        itrava         = 0
        paritrava      = ctypes.c_int (itrava)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (paritrava))
        itrava         = paritrava.value
        return         itrava

    @property
    def captureable (self):
        """
        (1) se o elemento é capturável
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("icaptura".encode(TQS.TQSUtil.CHARSET))
        icaptura       = 0
        paricaptura    = ctypes.c_int (icaptura)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (paricaptura))
        icaptura       = paricaptura.value
        return         icaptura

    @property
    def hasPlotData (self):
        """
        (1) se informações de plotagem independentes para este elemento
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("ivalid".encode(TQS.TQSUtil.CHARSET))
        itabinfo       = 0
        paritabinfo    = ctypes.c_int (itabinfo)
        self.m_dwg.m_mdwg.g_extgra_ler_tabinfo (parpedmv, parnomvar, ctypes.byref (paritabinfo))
        itabinfo       = paritabinfo.value
        return         itabinfo

    @property
    def plotPen (self):
        """
        Pena de plotagem somente se disponível
        """
        ipena          = 0
        if             self.hasPlotData != 0:
            parpedmv   = ctypes.c_void_p (self.m_dwg.m_pedmv)
            parnomvar  = ctypes.c_char_p ("ipena".encode(TQS.TQSUtil.CHARSET))
            paripena   = ctypes.c_int (ipena)
            self.m_dwg.m_mdwg.g_extgra_ler_tabinfo (parpedmv, parnomvar, ctypes.byref (paripena))
            ipena      = paripena.value
        return         ipena

    @property
    def plotWeight (self):
        """
        Peso de plotagem somente se disponível
        """
        ipeso          = 0
        if             self.hasPlotData != 0:
            parpedmv   = ctypes.c_void_p (self.m_dwg.m_pedmv)
            parnomvar  = ctypes.c_char_p ("ipeso".encode(TQS.TQSUtil.CHARSET))
            paripeso   = ctypes.c_int (ipeso)
            self.m_dwg.m_mdwg.g_extgra_ler_tabinfo (parpedmv, parnomvar, ctypes.byref (paripeso))
            ipeso      = paripeso.value
        return         ipeso

    @property
    def plotStyle (self):
        """
        Estilo de plotagem se disponível
        """
        iestil         = 0
        if             self.hasPlotData != 0:
            parpedmv   = ctypes.c_void_p (self.m_dwg.m_pedmv)
            parnomvar  = ctypes.c_char_p ("iestilo".encode(TQS.TQSUtil.CHARSET))
            pariestil  = ctypes.c_int (iestil)
            self.m_dwg.m_mdwg.g_extgra_ler_tabinfo (parpedmv, parnomvar, ctypes.byref (pariestil))
            iestil     = pariestil.value
        return         iestil

    @property
    def plotFont (self):
        """
        Fonte de plotagem se disponível
        """
        ifont          = 0
        if             self.hasPlotData != 0:
            parpedmv   = ctypes.c_void_p (self.m_dwg.m_pedmv)
            parnomvar  = ctypes.c_char_p ("ifonte".encode(TQS.TQSUtil.CHARSET))
            parifont   = ctypes.c_int (ifont)
            self.m_dwg.m_mdwg.g_extgra_ler_tabinfo (parpedmv, parnomvar, ctypes.byref (parifont))
            ifont      = parifont.value
        return         ifont

    @property
    def plotHatch (self):
        """
        Hachura de plotagem se disponível
        """
        ihachura       = 0
        if             self.hasPlotData != 0:
            parpedmv   = ctypes.c_void_p (self.m_dwg.m_pedmv)
            parnomvar  = ctypes.c_char_p ("ihachura".encode(TQS.TQSUtil.CHARSET))
            parihachura= ctypes.c_int (ihachura)
            self.m_dwg.m_mdwg.g_extgra_ler_tabinfo (parpedmv, parnomvar, ctypes.byref (parihachura))
            ihachura   = parihachura.value
        return         ihachura

    @property
    def objectName (self):
        """
        Retorna nome do objeto de desenho lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("nomobj".encode(TQS.TQSUtil.CHARSET))
        parnomeobj     = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_extgra_ler_string (parpedmv, parnomvar, parnomeobj)
        return         parnomeobj.value.decode(TQS.TQSUtil.CHARSET)

    @property
    def objectPointer (self):
        """
        Retorna apontador do objeto de desenho lido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("pntobj".encode(TQS.TQSUtil.CHARSET))
        pntobj         = 0
        parpntobj      = ctypes.c_void_p (pntobj)
        self.m_dwg.m_mdwg.g_extgra_ler_pnt (parpedmv, parnomvar, ctypes.byref (parpntobj))
        return         (parpntobj.value)

    @property
    def smartRebar (self):
        """
        Retorna objeto SmartRebar se o objeto extraído é um ferro inteligente, ou None
        """
        rebar          = None
        itype          = self.itype
        if             itype == DWGTYPE_OBJECT:
            if         self.objectName == "IPOFER":
                ferobjv = self.objectPointer
                rebar   = SmartRebar (self.m_dwg, ferobjv)
        return        rebar

    @property
    def inBlock (self):
        """
        Retorna (1) se o elemento gráfico lido está dentro de um bloco
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("extblc".encode(TQS.TQSUtil.CHARSET))
        inblock        = 0
        parinblock     = ctypes.c_int (inblock)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (parinblock))
        inblock        = parinblock.value
        return         inblock

    @property
    def inXref (self):
        """
        Retorna (1) se o elemento gráfico lido está dentro de uma referência externa
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iexrefext".encode(TQS.TQSUtil.CHARSET))
        inxref         = 0
        parinxref      = ctypes.c_int (inxref)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (parinxref))
        inxref         = parinxref.value
        return         inxref

    @property
    def isOpenObject (self):
        """
        Retorna (1) se o elemento gráfico lido está dentro de um objeto inteligente
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnomvar      = ctypes.c_char_p ("iobjaberto".encode(TQS.TQSUtil.CHARSET))
        inobject       = 0
        parinobject    = ctypes.c_int (inobject)
        self.m_dwg.m_mdwg.g_extgra_ler_int (parpedmv, parnomvar, ctypes.byref (parinobject))
        inobject       = parinobject.value
        return         inobject


#-----------------------------------------------------------------------------
#    Acesso a algumas variáveis globais do DWG
#
class Settings ():

    def __init__ (self, dwg):
        self.m_dwg     = dwg

    def __LerId (self):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iaplic         = 0
        pariaplic      = ctypes.c_int (iaplic)
        isubsis        = 0
        parisubsis     = ctypes.c_int (isubsis)
        itabela        = 0
        paritabela     = ctypes.c_int (itabela)
        self.m_dwg.m_mdwg.g_edmexlerapli (parpedmv, ctypes.byref (pariaplic), 
                          ctypes.byref (parisubsis), ctypes.byref (paritabela))
        iaplic         = pariaplic.value
        isubsis        = parisubsis.value
        return        iaplic, isubsis

    def __AlterarId (self, iaplic, isubsis):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariaplic      = ctypes.c_int (iaplic)
        parisubsis     = ctypes.c_int (isubsis)
        itabela        = 0
        paritabela     = ctypes.c_int (itabela)
        self.m_dwg.m_mdwg.g_edmexgrvapli (parpedmv, ctypes.byref (pariaplic), 
                          ctypes.byref (parisubsis), ctypes.byref (paritabela))
        self.m_dwg.CarregarCores ()

    @property
    def systemId (self):
        """
        Retorna o número do sistema (1..) caixa de propriedades do EAG
        """
        iaplic, isubsis= self.__LerId ()
        return         iaplic

    @systemId.setter
    def systemId (self, isystemid):
        """
        Define o número do sistema (1..) caixa de propriedades do EAG
        """
        iaplic, isubsis= self.__LerId ()
        self.__AlterarId (isystemid, isubsis)

    @property
    def subSystemId (self):
        """
        Retorna o subsistema (1..) caixa de propriedades do EAG
        """
        iaplic, isubsis= self.__LerId ()
        return        isubsis

    @subSystemId.setter
    def subSystemId (self, isubsystem):
        """
        Define o subsistema (1..) caixa de propriedades do EAG
        """
        iaplic, isubsis= self.__LerId ()
        self.__AlterarId (iaplic, isubsystem)

    def __LerEscala (self):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        dimsca         = 0.
        pardimsca      = ctypes.c_double (dimsca)
        dimlfc         = 0.
        pardimlfc      = ctypes.c_double (dimlfc)
        self.m_dwg.m_mdwg.g_edmexleresc (parpedmv, ctypes.byref (pardimsca), 
                                         ctypes.byref (pardimlfc))
        dimsca         = pardimsca.value
        dimlfc         = pardimlfc.value
        return         dimsca, dimlfc

    @property
    def scale (self):
        """
        Retorna valor que divide uma unidade e resulta em centímetros de plotagem
        """
        dimsca, dimlfc = self.__LerEscala ()
        return         dimsca

    @scale.setter
    def scale (self, scaleval):
        """
        Define valor que divide uma unidade e resulta em centímetros de plotagem
        """
        dimsca, dimlfc = self.__LerEscala ()
        dimsca         = scaleval
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pardimsca      = ctypes.c_double (dimsca)
        pardimlfc      = ctypes.c_double (dimlfc)
        self.m_dwg.m_mdwg.g_edmexgrvesc (parpedmv, ctypes.byref (pardimsca), 
                                         ctypes.byref (pardimlfc))

    def __LerBase (self):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        xbas           = 0.
        parxbas        = ctypes.c_double (xbas)
        ybas           = 0.
        parybas        = ctypes.c_double (ybas)
        self.m_dwg.m_mdwg.g_extbas (parpedmv, ctypes.byref (parxbas), ctypes.byref (parybas))
        xbas           = parxbas.value
        ybas           = parybas.value
        return         xbas, ybas

    def __DefBase    (self, xbas, ybas):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parxbas        = ctypes.c_double (xbas)
        parybas        = ctypes.c_double (ybas)
        self.m_dwg.m_mdwg.g_defbsd (parpedmv, ctypes.byref (parxbas), ctypes.byref (parybas))

    @property
    def xBase (self):
        """
        Retorna ponto que coincidirá com o cursor se este desenho for inserido dentro de outro como um bloco, referência ou mistura
        """
        xbas, ybas     = self.__LerBase ()
        return         xbas

    @xBase.setter
    def xBase (self, val):
        """
        Define ponto que coincidirá com o cursor se este desenho for inserido dentro de outro como um bloco, referência ou mistura
        """
        xbas, ybas     = self.__LerBase ()
        self.__DefBase (val, ybas)

    @property
    def yBase (self):
        """
        Ponto que coincidirá com o cursor se este desenho for inserido dentro de outro como um bloco, referência ou mistura
        """
        xbas, ybas     = self.__LerBase ()
        return         ybas

    @yBase.setter
    def yBase (self, val):
        """
        Ponto que coincidirá com o cursor se este desenho for inserido dentro de outro como um bloco, referência ou mistura
        """
        xbas, ybas     = self.__LerBase ()
        self.__DefBase (xbas, val)

    @property
    def blockReadDelimiterMode (self):
        """
        (1) Se os delimitadores DWGTYPE_BLOCK e DWGTYPE_BLOCKEND de inicio e fim de bloco devem ser lidos
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iedcpl         = 0
        pariedcpl      = ctypes.c_int (iedcpl)
        self.m_dwg.m_mdwg.g_extpbller (parpedmv, ctypes.byref (pariedcpl))
        iedcpl         = pariedcpl.value
        return         iedcpl

    @blockReadDelimiterMode.setter
    def blockReadDelimiterMode (self, ival):
        """
        (1) Se os delimitadores DWGTYPE_BLOCK e DWGTYPE_BLOCKEND de inicio e fim de bloco devem ser lidos
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        if             ival == 0:
            self.m_dwg.m_mdwg.g_extibl (parpedmv)
        else:
            self.m_dwg.m_mdwg.g_extpbl (parpedmv)

    @property
    def blockReadElementsMode (self):
        """
        (1) Para ler os elementos dentro do bloco inserido ou (0) apenas para os delimitadores de tipo=4/5
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iedexb         = 0
        pariedexb      = ctypes.c_int (iedexb)
        self.m_dwg.m_mdwg.g_extpbxler (parpedmv, ctypes.byref (pariedexb))
        iedexb         = pariedexb.value
        return         iedexb

    @blockReadElementsMode.setter
    def blockReadElementsMode (self, ival):
        """
        (1) Para ler os elementos dentro do bloco inserido ou (0) apenas para os delimitadores de tipo=4/5
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        if             ival == 0:
            self.m_dwg.m_mdwg.g_extibx (parpedmv)
        else:
            self.m_dwg.m_mdwg.g_extpbx (parpedmv)

    @property
    def levelsReadMode (self):
        """
        (1) Para ler apenas elementos em níveis ligados ou (0) para todos os elementos
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iedily         = 0
        pariedily      = ctypes.c_int (iedily)
        self.m_dwg.m_mdwg.g_extplaler (parpedmv, ctypes.byref (pariedily))
        iedily         = pariedily.value
        return         iedily

    @levelsReadMode.setter
    def levelsReadMode (self, ival):
        """
        (1) Para ler apenas elementos em níveis ligados ou (0) para todos os elementos
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        if             ival == 0:
            self.m_dwg.m_mdwg.g_extila (parpedmv)
        else:
            self.m_dwg.m_mdwg.g_extpla (parpedmv)


    @property
    def captureMode (self):
        """
        (0) Captura definida no gerenciador (1) desligado (2) ligado todo mundo (3) ligados somente nos níveis com captura
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        icaptura       = 0
        paricaptura    = ctypes.c_int (icaptura)
        istcaptura     = 0
        paristcaptura  = ctypes.c_int (istcaptura)
        self.m_dwg.m_mdwg.g_exlercaptura (parpedmv, ctypes.byref (paricaptura), 
                                          ctypes.byref (paristcaptura))
        icaptura       = paricaptura.value
        istcaptura     = paristcaptura.value
        if        istcaptura != 0:
            icaptura   = 1
        return         icaptura

    @levelsReadMode.setter
    def captureMode (self, icaptura):
        """
        (0) Captura definida no gerenciador (1) desligado (2) ligado todo mundo (3) ligados somente nos níveis com captura
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        paricaptura    = ctypes.c_int (icaptura)
        istcaptura     = 0
        paristcaptura  = ctypes.c_int (istcaptura)
        self.m_dwg.m_mdwg.g_exgrvcaptura (parpedmv, paricaptura, paristcaptura)

    def __LerGrade (self):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        igrade         = 0
        parigrade      = ctypes.c_int (igrade)
        grdorx         = 0.
        pargrdorx      = ctypes.c_double (grdorx)
        grdory         = 0.
        pargrdory      = ctypes.c_double (grdory)
        grdesx         = 0.
        pargrdesx      = ctypes.c_double (grdesx)
        grdesy         = 0.
        pargrdesy      = ctypes.c_double (grdesy)
        grdang         = 0.
        pargrdang      = ctypes.c_double (grdang)
        iespacponto    = 0
        pariespacponto = ctypes.c_int (iespacponto)
        igraderubber   = 0
        parigraderubber= ctypes.c_int (igraderubber)
        self.m_dwg.m_mdwg.g_exlerigrade    (parpedmv, ctypes.byref (parigrade),
            ctypes.byref (pargrdorx), ctypes.byref (pargrdory),
            ctypes.byref (pargrdesx), ctypes.byref (pargrdesy),
            ctypes.byref (pargrdang), ctypes.byref (pariespacponto),
            ctypes.byref (parigraderubber))
        igrade         = parigrade.value
        grdorx         = pargrdorx.value
        grdory         = pargrdory.value
        grdesx         = pargrdesx.value
        grdesy         = pargrdesy.value
        grdang         = pargrdang.value
        iespacponto    = pariespacponto.value
        igraderubber   = parigraderubber.value
        return         igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber

    def __DefGrade (self, igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parigrade      = ctypes.c_int (igrade)
        pargrdorx      = ctypes.c_double (grdorx)
        pargrdory      = ctypes.c_double (grdory)
        pargrdesx      = ctypes.c_double (grdesx)
        pargrdesy      = ctypes.c_double (grdesy)
        pargrdang      = ctypes.c_double (grdang)
        pariespacponto = ctypes.c_int (iespacponto)
        parigraderubber= ctypes.c_int (igraderubber)
        self.m_dwg.m_mdwg.g_exgrvigrade    (parpedmv, parigrade,
            pargrdorx, pargrdory, pargrdesx, pargrdesy, pargrdang, pariespacponto,
            parigraderubber)


    @property
    def gridMode (self):
        """
        Retorna (0) vale captura (1) vale grade (2) nem captura nem grade
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        return         igrade

    @gridMode.setter
    def gridMode (self, ival):
        """
        Definir (0) vale captura (1) vale grade (2) nem captura nem grade
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        igrade         = ival
        self.__DefGrade (igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber)

    @property
    def gridOriginX (self):
        """
        Retorna origem da grade X
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        return         grdorx

    @gridOriginX.setter
    def gridOriginX (self, val):
        """
        Definir origem da grade X
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        grdorx         = val
        self.__DefGrade (igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber)

    @property
    def gridOriginY (self):
        """
        Retorna origem da grade Y
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        return         grdory

    @gridOriginY.setter
    def gridOriginY (self, val):
        """
        Define origem da grade Y
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        grdory         = val
        self.__DefGrade (igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber)

    @property
    def gridSpacingX (self):
        """
        Retorna o espaçamento da grade X
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        return         grdesx

    @gridSpacingX.setter
    def gridSpacingX (self, val):
        """
        Define o espaçamento da grade X
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        grdesx         = val
        self.__DefGrade (igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber)

    @property
    def gridSpacingY (self):
        """
        Retorna o espaçamento da grade Y
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        return         grdesy

    @gridSpacingY.setter
    def gridSpacingY (self, val):
        """
        Define o espaçamento da grade Y
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        grdesy         = val
        self.__DefGrade (igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber)

    @property
    def gridAngle (self):
        """
        Retorna o ângulo da grade em graus
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        return         grdang

    @gridAngle.setter
    def gridAngle (self, val):
        """
        Define o ângulo da grade em graus
        """
        igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber = self.__LerGrade ()
        grdang         = val
        self.__DefGrade (igrade, grdorx, grdory, grdesx, grdesy, grdang, iespacponto, igraderubber)


    @property
    def handle_pedmv (self):
        """
        Retorna handle de desenho para uso em outras bibliotecas
        """
        return         self.m_dwg.m_pedmv

    @property
    def originalColorsMode (self):
        """
        (1) se o desenho deve ser plotado com cores originais e não da tabela de plotagem
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iplotcorori    = 0
        pariplotcorori = ctypes.c_int (iplotcorori)
        self.m_dwg.m_mdwg.g_edmexleriplotcorori (parpedmv, ctypes.byref (pariplotcorori))
        iplotcorori    = pariplotcorori.value
        return         iplotcorori

    @originalColorsMode.setter
    def originalColorsMode (self, ival):
        """
        (1) se o desenho deve ser plotado com cores originais e não da tabela de plotagem
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        iplotcorori    = ival
        pariplotcorori = ctypes.c_int (iplotcorori)
        self.m_dwg.m_mdwg.g_edmexgrviplotcorori (parpedmv, pariplotcorori)

    @property
    def comment (self):
        """
        Comentário associado ao desenho
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parcomment     = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_edmexlercoment (parpedmv, parcomment)
        return         parcomment.value.decode(TQS.TQSUtil.CHARSET)

    @comment.setter
    def comment (self, commentx):
        """
        Comentário associado ao desenho
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parcomment     = ctypes.c_char_p (commentx.encode(TQS.TQSUtil.CHARSET))
        self.m_dwg.m_mdwg.g_edmexgrvcoment (parpedmv, parcomment)

    @property
    def revComment (self):
        """
        Comentários da revisão do desenho
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parcomment     = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_edmexlerrevisao (parpedmv, parcomment)
        return         parcomment.value.decode(TQS.TQSUtil.CHARSET)

    @revComment.setter
    def revComment (self, commentx):
        """
        Comentários da revisão do desenho
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parcomment     = ctypes.c_char_p (commentx.encode(TQS.TQSUtil.CHARSET))
        self.m_dwg.m_mdwg.g_edmexgrvrevisao (parpedmv, parcomment)

    @property
    def blueprintMode (self):
        """
        (1) Modo de visualização de plantas
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        ixref          = 0
        parixref       = ctypes.c_int (ixref)
        self.m_dwg.m_mdwg.g_edmexlerxref (parpedmv, ctypes.byref (parixref))
        ixref          = parixref.value
        return         ixref

    @blueprintMode.setter
    def blueprintMode (self, ival):
        """
        (1) Modo de visualização de plantas
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        ixref          = ival
        parixref       = ctypes.c_int (ixref)
        self.m_dwg.m_mdwg.g_edmexgrvxref (parpedmv, parixref)

#-----------------------------------------------------------------------------
#    Acesso à tabela de níveis do DWG
#
class LevelsTable ():

    def __init__ (self, dwg):
        self.m_dwg     = dwg
        self.MAXCARLAY = 256

    def ConvNivel (self, level):
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel         = str (level)
        parsnivel      = ctypes.c_char_p (snivel.encode(TQS.TQSUtil.CHARSET))
        inivel         = 0
        parnivel       = ctypes.c_int (inivel)
        ialfa          = 0
        if             isinstance (level, (int, float)):
            inivel     = level
            parnivel   = ctypes.c_int (inivel)
            if         inivel < 0 or inivel >= self.MAXCARLAY:
                ialfa  = 1
                parnomlay = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
                idesligado = 0
                paridesligado = ctypes.c_int (idesligado)
                inaoexiste = 0
                parinaoexiste = ctypes.c_int (inaoexiste)
                self.m_dwg.m_mdwg.g_onflayx (parpedmv, ctypes.byref (parnivel), parnomlay, 
                              ctypes.byref (paridesligado), ctypes.byref (parinaoexiste))
                iexiste= 1 - parinaoexiste.value
                if     iexiste != 0:
                    parsnivel = parnomlay
        else:
            parsnivel  = ctypes.c_char_p (level.encode(TQS.TQSUtil.CHARSET))
            ialfa      = 1
        if        ialfa== 0:
            self.m_dwg.m_mdwg.g_desniv (parpedmv, ctypes.byref (parnivel))
        else:
            self.m_dwg.m_mdwg.g_desnivalfa (parpedmv, parsnivel, ctypes.byref (parnivel))
        snivel         = parsnivel.value
        inivel         = parnivel.value
        return         snivel, inivel

    @property
    def count (self):
        """
        Retorna o número total de níveis numerados de 0 a N-1.
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        numniveis      = 0
        parnumniveis   = ctypes.c_int (numniveis)
        self.m_dwg.m_mdwg.g_numlay (parpedmv, ctypes.byref (parnumniveis))
        numniveis      = parnumniveis.value
        return         numniveis

    def IsDefined (self, level):
        """
        Retorna (1) se o nível está definido
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        level          = 0
        parlevel       = ctypes.c_int (level)
        parnomlay      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        idesligado     = 0
        paridesligado  = ctypes.c_int (idesligado)
        inaoexiste     = 0
        parinaoexiste  = ctypes.c_int (inaoexiste)
        self.m_dwg.m_mdwg.g_onflayx (parpedmv, ctypes.byref (parlevel), parnomlay, 
               ctypes.byref (paridesligado), ctypes.byref (parinaoexiste))
        iexiste        = 1 - parinaoexiste.value
        return         iexiste

    def GetStyle (self, level):
        """
        Retorna o estilo associado ao nível (-1) estilo default
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        iestilo        = 0
        pariestilo     = ctypes.c_int (iestilo)
        self.m_dwg.m_mdwg.g_extstl (parpedmv, ctypes.byref (parnivel), 
                                    ctypes.byref (pariestilo))
        iestilo        = pariestilo.value
        return         iestilo

    def SetStyle (self, level, ival):
        """
        Define o estilo associado ao nível (-1) estilo default
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        iestilo        = ival + 1
        if             iestilo > 0:
            iestilo    = - iestilo
        pariestilo     = ctypes.c_int (iestilo)
        self.m_dwg.m_mdwg.g_atribestilniv (parpedmv, parnivel, pariestilo)

    def IsOn (self, level):
        """
        Retorna estado ligado (1) ou desligado (0) de um nível
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        parnomlay      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        idesligado     = 0
        paridesligado  = ctypes.c_int (idesligado)
        inaoexiste     = 0
        parinaoexiste  = ctypes.c_int (inaoexiste)
        self.m_dwg.m_mdwg.g_onflayx (parpedmv, ctypes.byref (parnivel), parnomlay, 
                         ctypes.byref (paridesligado), ctypes.byref (parinaoexiste))
        idesligado     = 1 - paridesligado.value
        return         idesligado

    def TurnOn (self, level, ival):
        """
        Define o estado ligado (1) ou desligado (0) de um nível
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        iligado        = ival
        if             iligado != 0:
            self.m_dwg.m_mdwg.g_liglay (parpedmv, ctypes.byref (parnivel))
        else:
            self.m_dwg.m_mdwg.g_deslay (parpedmv, ctypes.byref (parnivel))

    def GetColor (self, level):
        """
        Retorna a cor (0..255) de um nível
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        icor           = 0
        paricor        = ctypes.c_int (icor)
        self.m_dwg.m_mdwg.g_icorly (parpedmv, ctypes.byref (parnivel), 
                          ctypes.byref (paricor))
        icor           = paricor.value
        return         icor

    def SetColor (self, level, ival):
        """
        Define a cor (0..255) de um nível
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        icor           = ival
        paricor        = ctypes.c_int (icor)
        self.m_dwg.m_mdwg.g_corlay (parpedmv, ctypes.byref (parnivel), 
                          ctypes.byref (paricor))

    def GetLock (self, level):
        """
        Retorna o estado de trava de um nível (1) sim (0) não
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        itravado       = 0
        paritravado    = ctypes.c_int (itravado)
        self.m_dwg.m_mdwg.g_lertravanivel (parpedmv, parnivel, ctypes.byref (paritravado))
        itravado       = paritravado.value
        return         itravado

    def SetLock (self, level, ival):
        """
        Leitura/Atribuição do estado de trava de um Nível (1) sim (0) não
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        itravado       = ival
        paritravado    = ctypes.c_int (itravado)
        self.m_dwg.m_mdwg.g_deftravanivel (parpedmv, parnivel, paritravado)

    def GetCapture (self, level):
        """
        Retorna o estado de captura de um nível (1) sim (0) não
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        icaptura       = 0
        paricaptura    = ctypes.c_int (icaptura)
        self.m_dwg.m_mdwg.g_lercapturanivel (parpedmv, parnivel, ctypes.byref (paricaptura))
        icaptura       = paricaptura.value
        return         icaptura

    def SetCapture (self, level, ival):
        """
        Define o estado de captura de um nível (1) sim (0) não
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        parnivel       = ctypes.c_int (nivel)
        icaptura       = ival
        paricaptura    = ctypes.c_int (icaptura)
        self.m_dwg.m_mdwg.g_defcapturanivel (parpedmv, parnivel, paricaptura)

    def Create (self, level):
        """
        Cria um nível numérico/alfanumérico e retorna o correspondente numérico para uso em outros métodos
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        snivel, nivel  = self.ConvNivel (level)
        return         nivel

    def Name (self, level):
        """
        Retorna o nível em formato alfanumérico
        """
        snivel, nivel  = self.ConvNivel (level)
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnivel       = ctypes.c_int (nivel)
        parnomlay      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        idesligado     = 0
        paridesligado  = ctypes.c_int (idesligado)
        inaoexiste     = 0
        parinaoexiste  = ctypes.c_int (inaoexiste)
        self.m_dwg.m_mdwg.g_onflayx (parpedmv, ctypes.byref (parnivel), parnomlay, 
                         ctypes.byref (paridesligado), ctypes.byref (parinaoexiste))
        snivel         = parnomlay.value
        return         snivel.decode(TQS.TQSUtil.CHARSET)

#-----------------------------------------------------------------------------
#    Acesso à tabela de blocos do DWG
#
class BlocksTable ():

    def __init__ (self, dwg):
        self.m_dwg  = dwg

    @property
    def count (self):
        """
        Retorna o número total de blocos definidos
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        numblo         = 0
        parnumblo      = ctypes.c_int (numblo)
        self.m_dwg.m_mdwg.g_iexnbl (parpedmv, ctypes.byref (parnumblo))
        numblo         = parnumblo.value
        return         numblo

    def IsDefined (self, name):
        """
        Retorna (1) se o bloco existe
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parname        = ctypes.c_char_p (name.encode(TQS.TQSUtil.CHARSET))
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_tstblk (parpedmv, parname, ctypes.byref (paristat))
        istat          = paristat.value
        iexiste        = 1 - istat
        return         iexiste
    
    def Name (self, index):
        """
        Retorna o nome do bloco de índice Ibloco = 0..count-1
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        numblo         = self.count
        indblo         = index + 1
        if             index < 0 or index >= numblo: 
            TQS.TQSUtil.writef ("BlocksTable.name: indice invalido: %d/%d" % 
                              (index, numblo))
            return
        parindblo      = ctypes.c_int (indblo)
        parnomblk      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.g_extnbl (parpedmv, ctypes.byref (parindblo), parnomblk)
        return         parnomblk.value.decode(TQS.TQSUtil.CHARSET)

#-----------------------------------------------------------------------------
#    Acesso às referências externas
#
class XReference ():

    def __init__ (self, dwg):
        self.m_dwg     = dwg

    @property
    def count (self):
        """
        Retorna o número de referências externas definidas e inseridas.
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        numelem        = 0
        parnumelem     = ctypes.c_int (numelem)
        self.m_dwg.m_mdwg.refx_numelem (parpedmv, ctypes.byref (parnumelem))
        numelem        = parnumelem.value
        return         numelem

    def Disable (self, ival):
        """
        Defina (1) para inibir a interpretação de referências externas
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        inibepref      = ival
        parinibepref   = ctypes.c_int (inibepref)
        self.m_dwg.m_mdwg.refx_inibe (parpedmv, parinibepref)

    def Read (self, index):
        """
        Lê os dados de uma referência externa efetivamente inserida no desenho (0..count-1)\n
           Retorna:    dwgname, ion, blockname\n
           dwgname     Desenho associado\n
           ion         (1) Se referência ligada\n
           blockname   Nome do bloco de desenho dentro do DWG
        """
        if        index < 0 or index >= self.count:
            TQS.TQSUtil.writef ("XReference::Read índice invalido %d/%d" % 
                              (index, self.count))
            return    "", 0, ""

        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parindex    = ctypes.c_int (index)
        interna        = 0
        parinterna    = ctypes.c_int (interna)
        pardwgname    = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        pedmref        = 0
        parpedmref    = ctypes.c_void_p (pedmref)
        ligada        = 0
        parligada    = ctypes.c_int (ligada)
        parblockname     = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.refx_ler (parpedmv, parindex, ctypes.byref (parinterna),
                                 pardwgname, ctypes.byref (parpedmref), 
                                 ctypes.byref (parligada), parblockname)
        dwgname        = pardwgname.value.decode(TQS.TQSUtil.CHARSET)
        ion        = parligada.value
        blockname    = parblockname.value.decode(TQS.TQSUtil.CHARSET)
        return        dwgname, ion, blockname

    def TurnOn (self, index, ival):
        """
        Defina (1) para ligar a visualização de uma referência externa
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        if        index < 0 or index >= self.count:
            TQS.TQSUtil.writef ("XReference::TurnOn índice invalido %d/%d" % 
                              (index, self.count))
            return
        parindex    = ctypes.c_int (index)
        ligada        = ival
        parligada    = ctypes.c_int (ligada)
        self.m_dwg.m_mdwg.refx_ligada (parpedmv, parindex, parligada)

#-----------------------------------------------------------------------------
#    Modificação de elementos
#
class Edit ():

    def __init__ (self, dwg):
        self.m_dwg      = dwg

    def ModifyLevel (self, addr, level):
        """
        Modifica o nível de um elemento
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        snivel, nivel= self.m_dwg.levelstable.ConvNivel (level)
        parnivel    = ctypes.c_int (nivel)
        self.m_dwg.m_mdwg.g_altely (parpedmv, ctypes.byref (pariadr), ctypes.byref (parnivel))

    def __LerAtribElem (self, addr):
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        icor        = 0
        paricor     = ctypes.c_int (icor)
        icorrgb        = 0
        paricorrgb     = ctypes.c_void_p (icorrgb)
        iestilo        = 0
        pariestilo     = ctypes.c_int (iestilo)
        iespes        = 0
        pariespes     = ctypes.c_int (iespes)
        self.m_dwg.m_mdwg.g_leratribelem (parpedmv, ctypes.byref (pariadr), 
                          ctypes.byref (paricor), ctypes.byref (paricorrgb), 
                          ctypes.byref (pariestilo), ctypes.byref (pariespes))
        icor        = paricor.value
        icorrgb        = paricorrgb.value
        iestilo        = pariestilo.value
        iespes        = pariespes.value
        return        icor, icorrgb, iestilo, iespes

    def __DefAtribElem (self, addr, icor, icorrgb, iestilo, iespes):
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        paricor     = ctypes.c_int (icor)
        paricorrgb     = ctypes.c_void_p (icorrgb)
        pariestilo     = ctypes.c_int (iestilo)
        pariespes     = ctypes.c_int (iespes)
        self.m_dwg.m_mdwg.g_altatrib (parpedmv, ctypes.byref (pariadr), paricor, paricorrgb, 
                          pariestilo, pariespes)

    def ModifyColor (self, addr, icolor):
        """
        Modifica a cor (0..255) de um elemento
        """
        icor, icorrgb, iestilo, iespes = self.__LerAtribElem (addr)
        self.__DefAtribElem (addr, icolor, icorrgb, iestilo, iespes)


    def ModifyStyle (self, addr, istyle):
        """
        Modifica o estilo de um elemento
        """
        icor, icorrgb, iestilo, iespes = self.__LerAtribElem (addr)
        self.__DefAtribElem (addr, icor, icorrgb, istyle, iespes)

    def Erase (self, addr):
        """
        Apaga um elemento\n
        Retorna (!=0) se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        istat        = 0
        paristat     = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_delelm (parpedmv, ctypes.byref (pariadr), ctypes.byref (paristat))
        istat        = paristat.value
        return        istat

    def Recover (self, addr):
        """
        Recupera um elemento apagado\n
        Retorna (!=0) se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        istat        = 0
        paristat     = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_recelm (parpedmv, ctypes.byref (pariadr), ctypes.byref (paristat))
        istat        = paristat.value
        return        istat

    def ModifyPoint (self, addr, index, x, y):
        """
        Modifica as coordenadas de um ponto de um elemento - Indice = 0..np-1\n
        Retorna (!=0) se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        istat        = 0
        paristat     = ctypes.c_int (istat)
        index        = index+1
        parindex     = ctypes.c_int (index)
        parx         = ctypes.c_double (x)
        pary         = ctypes.c_double (y)
        self.m_dwg.m_mdwg.g_altelm (parpedmv, ctypes.byref (pariadr), ctypes.byref (parindex),
                         ctypes.byref (parx), ctypes.byref (pary), ctypes.byref (paristat))
        istat        = paristat.value
        return        istat

    def ModifyText (self, addr, h, ang):
        """
        Modifica altura e ângulo de texto. Para modificar o seu conteúdo é necessário apagar e criar outro.
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        parh         = ctypes.c_double (h)
        parang         = ctypes.c_double (ang)
        self.m_dwg.m_mdwg.g_altatx (parpedmv, ctypes.byref (pariadr), ctypes.byref (parh),
                          ctypes.byref (parang))

    def ModifyArc (self, addr, r, angi, angf):
        """
        Modifica dados de um arco
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        parr         = ctypes.c_double (r)
        parangi         = ctypes.c_double (angi)
        parangf         = ctypes.c_double (angf)
        self.m_dwg.m_mdwg.g_altcir (parpedmv, ctypes.byref (pariadr), ctypes.byref (parr))
        self.m_dwg.m_mdwg.g_altarc (parpedmv, ctypes.byref (pariadr), 
                          ctypes.byref (parangi), ctypes.byref (parangf))

    def ModifyCircle (self, addr, r):
        """
        Modifica dados de um círculo
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        parr         = ctypes.c_double (r)
        self.m_dwg.m_mdwg.g_altcir (parpedmv, ctypes.byref (pariadr), ctypes.byref (parr))

    def ModifyBlock (self, addr, escx, escy, ang):
        """
        Modifica dados de um bloco inserido\n
        Retorna (!=0) se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        parescx         = ctypes.c_double (escx)
        parescy         = ctypes.c_double (escy)
        angrad        = ang * TQS.TQSUtil.GRAUSRAD
        parangrad     = ctypes.c_double (angrad)
        istat        = 0
        paristat     = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_altblk (parpedmv, ctypes.byref (pariadr), ctypes.byref (parangrad),
                          ctypes.byref (parescx), ctypes.byref (parescy), ctypes.byref (paristat))
        istat        = paristat.value
        return        istat

    def Move (self, addr, dx, dy):
        """
        Movimenta um elemento qualquer\n
        Retorna (!=0) se erro
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pariadr     = ctypes.c_void_p (addr)
        pardx         = ctypes.c_double (dx)
        pardy         = ctypes.c_double (dy)
        istat        = 0
        paristat     = ctypes.c_int (istat)
        self.m_dwg.m_mdwg.g_movelm (parpedmv, ctypes.byref (pariadr), ctypes.byref (pardx), 
                          ctypes.byref (pardy), ctypes.byref (paristat))
        istat        = paristat.value
        return        istat

#-----------------------------------------------------------------------------
#    Acesso à tabela de plotagem
#
class Plotting ():

    def __init__ (self, dwg):
        self.m_dwg      = dwg

    def LoadPlottingTable (self):
        """
        Torna disponíveis os dados de tabela de plotagem associados a este desenho\n
        Retorna: o nome da tabela e o status de leitura (!=0) se erro
        """
        istat          = 0
        paristat       = ctypes.c_int (istat)
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_carregcores (parpedmv, ctypes.byref(paristat))
        self.m_dwg.m_mdwg.tabplt_ini (parpedmv, ctypes.byref(paristat))
        parnomtab      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.tabplt_ler (parpedmv, parnomtab, ctypes.byref(paristat))
        istat          = paristat.value
        tabname        = parnomtab.value.decode(TQS.TQSUtil.CHARSET)
        return         tabname, istat

    def AttributeRead (self, nivel):
        """
        Lê os atributos de um determinado nível da tabela de plotagem\n
        Retorna:\n
        pena           Índice da pena\n
        peso           Índice do peso\n
        estilo         Índice do estilo\n
        hachura        Índice da hachura\n
        fonte          Índice do fonte\n
        titulo         Título do nível
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parnivel       = ctypes.c_int (nivel)
        invpen         = 0
        parinvpen      = ctypes.c_int (invpen)
        invpes         = 0
        parinvpes      = ctypes.c_int (invpes)
        invstl         = 0
        parinvstl      = ctypes.c_int (invstl)
        invhac         = 0
        parinvhac      = ctypes.c_int (invhac)
        invtbf         = 0
        parinvtbf      = ctypes.c_int (invtbf)
        self.m_dwg.m_mdwg.tabplt_invpen (parpedmv, parnivel, ctypes.byref (parinvpen))
        self.m_dwg.m_mdwg.tabplt_invpes (parpedmv, parnivel, ctypes.byref (parinvpes))
        self.m_dwg.m_mdwg.tabplt_invstl (parpedmv, parnivel, ctypes.byref (parinvstl))
        self.m_dwg.m_mdwg.tabplt_invhac (parpedmv, parnivel, ctypes.byref (parinvhac))
        self.m_dwg.m_mdwg.tabplt_invtbf (parpedmv, parnivel, ctypes.byref (parinvtbf))
        partitulomsg   = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.tabplt_titulomsg2 (parpedmv, parnivel, partitulomsg)
        invpen         = parinvpen.value
        invpes         = parinvpes.value
        invstl         = parinvstl.value
        invhac         = parinvhac.value
        invtbf         = parinvtbf.value
        titulomsg      = partitulomsg.value.decode(TQS.TQSUtil.CHARSET)
        return         invpen, invpes, invstl, invhac, invtbf, titulomsg


#-----------------------------------------------------------------------------
#    Comandos de cotagem
#
class Dim ():

    def __init__ (self, dwg):
        self.m_dwg     = dwg

    @property
    def dimtxt (self):
        """
        Altura do têxto de cotagem
        """
        dimtxt         = 0.
        pardimtxt      = ctypes.c_double (dimtxt)
        self.m_dwg.m_mdwg.COTTXT_LER (ctypes.byref (pardimtxt))
        dimtxt         = pardimtxt.value
        return         dimtxt

    @dimtxt.setter
    def dimtxt (self, val):
        """
        Altura do têxto de cotagem
        """
        pardimtxt      = ctypes.c_double (val)
        self.m_dwg.m_mdwg.COTTXT (ctypes.byref (pardimtxt))

    @property
    def dimexe (self):
        """
        Extensão da linha de chamada
        """
        dimexe         = 0.
        pardimexe      = ctypes.c_double (dimexe)
        self.m_dwg.m_mdwg.COTEXE_LER (ctypes.byref (pardimexe))
        dimexe         = pardimexe.value
        return         dimexe

    @dimexe.setter
    def dimexe (self, val):
        """
        Extensão da linha de chamada
        """
        pardimexe      = ctypes.c_double (val)
        self.m_dwg.m_mdwg.COTEXE (ctypes.byref (pardimexe))

    @property
    def dimdle (self):
        """
        Extensão da linha de cotagem
        """
        dimdle         = 0.
        pardimdle      = ctypes.c_double (dimdle)
        self.m_dwg.m_mdwg.COTDLE_LER (ctypes.byref (pardimdle))
        dimdle         = pardimdle.value
        return         dimdle

    @dimdle.setter
    def dimdle (self, val):
        """
        Extensão da linha de cotagem
        """
        pardimdle      = ctypes.c_double (val)
        self.m_dwg.m_mdwg.COTDLE (ctypes.byref (pardimdle))

    @property
    def dimexo (self):
        """
        Folga na linha de chamada
        """
        dimexo        = 0.
        pardimexo    = ctypes.c_double (dimexo)
        self.m_dwg.m_mdwg.COTEXO_LER (ctypes.byref (pardimexo))
        dimexo        = pardimexo.value
        return        dimexo

    @dimexo.setter
    def dimexo (self, val):
        """
        Folga na linha de chamada
        """
        pardimexo    = ctypes.c_double (val)
        self.m_dwg.m_mdwg.COTEXO (ctypes.byref (pardimexo))

    @property
    def dimtsz (self):
        """
        Tamanho do símbolo de cotagem
        """
        dimtsz        = 0.
        pardimtsz    = ctypes.c_double (dimtsz)
        self.m_dwg.m_mdwg.COTTSZ_LER (ctypes.byref (pardimtsz))
        dimtsz        = pardimtsz.value
        return        dimtsz

    @dimtsz.setter
    def dimtsz (self, val):
        """
        Tamanho do símbolo de cotagem
        """
        pardimtsz    = ctypes.c_double (val)
        self.m_dwg.m_mdwg.COTTSZ (ctypes.byref (pardimtsz))

    @property
    def dimlfc (self):
        """
        Multiplicador de comprimentos
        """
        dimlfc        = 0.
        pardimlfc    = ctypes.c_double (dimlfc)
        self.m_dwg.m_mdwg.COTLFC_LER (ctypes.byref (pardimlfc))
        dimlfc        = pardimlfc.value
        return        dimlfc

    @dimlfc.setter
    def dimlfc (self, val):
        """
        Multiplicador de comprimentos
        """
        pardimlfc     = ctypes.c_double (val)
        self.m_dwg.m_mdwg.COTLFC (ctypes.byref (pardimlfc))

    @property
    def idmniv (self):
        """
        Nível geral de cotagem
        """
        idmniv        = 0
        paridmniv     = ctypes.c_int (idmniv)
        self.m_dwg.m_mdwg.COTNIVLER (ctypes.byref (paridmniv))
        idmniv        = paridmniv.value
        return        idmniv

    @idmniv.setter
    def idmniv (self, val):
        """
        Nível geral de cotagem
        """
        paridmniv    = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTNIV (ctypes.byref (paridmniv))

    @property
    def idmnic (self):
        """
        Nível da linha de cotagem
        """
        idmnic        = 0
        paridmnic     = ctypes.c_int (idmnic)
        self.m_dwg.m_mdwg.COTNICLER (ctypes.byref (paridmnic))
        idmnic        = paridmnic.value
        return        idmnic

    @idmnic.setter
    def idmnic (self, val):
        """
        Nível da linha de cotagem
        """
        paridmnic      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTNIC (ctypes.byref (paridmnic))

    @property
    def idmnil (self):
        """
        Nível da linha de chamada
        """
        idmnil         = 0
        paridmnil      = ctypes.c_int (idmnil)
        self.m_dwg.m_mdwg.COTNILLER (ctypes.byref (paridmnil))
        idmnil         = paridmnil.value
        return         idmnil

    @idmnil.setter
    def idmnil (self, val):
        """
        Nível da linha de chamada
        """
        paridmnil      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTNIL (ctypes.byref (paridmnil))

    @property
    def idmnib (self):
        """
        Nível do símbolo de cotagem
        """
        idmnib         = 0
        paridmnib      = ctypes.c_int (idmnib)
        self.m_dwg.m_mdwg.COTNIBLER (ctypes.byref (paridmnib))
        idmnib         = paridmnib.value
        return         idmnib

    @idmnib.setter
    def idmnib (self, val):
        """
        Nível do símbolo de cotagem
        """
        paridmnib      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTNIB (ctypes.byref (paridmnib))

    @property
    def idmcim (self):
        """
        (1) Se têxto abaixo da linha de cotagem
        """
        idmcim         = 0
        paridmcim      = ctypes.c_int (idmcim)
        self.m_dwg.m_mdwg.COTCIM_LER (ctypes.byref (paridmcim))
        idmcim         = paridmcim.value
        return         idmcim

    @idmcim.setter
    def idmcim (self, val):
        """
        (1) Se têxto abaixo da linha de cotagem
        """
        paridmcim      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTCIM (ctypes.byref (paridmcim))

    @property
    def idmar5 (self):
        """
        (1) Se medidas arredondadas de 5 em 5
        """
        idmar5         = 0
        paridmar5      = ctypes.c_int (idmar5)
        self.m_dwg.m_mdwg.COTAR5_LER (ctypes.byref (paridmar5))
        idmar5         = paridmar5.value
        return         idmar5

    @idmar5.setter
    def idmar5 (self, val):
        """
        (1) Se medidas arredondadas de 5 em 5
        """
        paridmar5      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTAR5 (ctypes.byref (paridmar5))

    @property
    def dimblk (self):
        """
        Nome do bloco de cotagem (TICK/DOT/ARROW são pré-definidos)
        """
        pardimblk      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.COTBLK_LER (ctypes.byref (pardimblk), 0)
        return         pardimblk.value.decode(TQS.TQSUtil.CHARSET)

    @dimblk.setter
    def dimblk (self, val):
        """
        Nome do bloco de cotagem (TICK/DOT/ARROW são pré-definidos)
        """
        pardimblk      = ctypes.c_char_p (val.encode(TQS.TQSUtil.CHARSET))
        self.m_dwg.m_mdwg.COTBLK (pardimblk, 0)

    @property
    def dimse1 (self):
        """
        (1) Se suprime linha de chamada
        """
        dimse1         = 0
        pardimse1      = ctypes.c_int (dimse1)
        self.m_dwg.m_mdwg.COTLCM_LER (ctypes.byref (pardimse1))
        dimse1         = pardimse1.value
        return         dimse1

    @dimse1.setter
    def dimse1 (self, val):
        """
        (1) Se suprime linha de chamada
        """
        pardimse1      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTLCM (ctypes.byref (pardimse1))

    @property
    def idmaut (self):
        """
        (0) nao (1) auto 2P (2) auto ELM
        """
        idmaut         = 0
        paridmaut      = ctypes.c_int (idmaut)
        self.m_dwg.m_mdwg.COTAUT_LER (ctypes.byref (paridmaut))
        idmaut         = paridmaut.value
        return         idmaut

    @idmaut.setter
    def idmaut (self, val):
        """
        (0) nao (1) auto 2P (2) auto ELM
        """
        paridmaut      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTAUT (ctypes.byref (paridmaut))

    @property
    def idmcot (self):
        """
        (1) Se suprime linha de cotagem
        """
        idmcot         = 0
        paridmcot      = ctypes.c_int (idmcot)
        self.m_dwg.m_mdwg.COTIDMCOT_LER (ctypes.byref (paridmcot))
        idmcot         = paridmcot.value
        return         idmcot

    @idmcot.setter
    def idmcot (self, val):
        """
        (1) Se suprime linha de cotagem
        """
        paridmcot      = ctypes.c_int (val)
        self.m_dwg.m_mdwg.COTIDMCOT (ctypes.byref (paridmcot))

    @property
    def dimtxu (self):
        """
        Texto manual de cotagem
        """
        pardimtxu      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        self.m_dwg.m_mdwg.COTTXU_LER (pardimtxu, 0)
        return         pardimtxu.value.decode(TQS.TQSUtil.CHARSET)

    @dimtxu.setter
    def dimtxu (self, val):
        """
        Texto manual de cotagem
        """
        pardimtxu      = ctypes.c_char_p (val.encode(TQS.TQSUtil.CHARSET))
        self.m_dwg.m_mdwg.COTTXU (pardimtxu, 0)
        self.m_dwg.m_mdwg.COTETX ()

    def Dim3P (self, itipo, x1, y1, x2, y2, x3, y3):
        """
        Cotagem por 3 pontos:\n
        itipo        Direção de cotagem IDHOR/IDVER/IDANG/IDINC\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem\n
        x3           ponto da linha de cotagem\n
        y3           ponto da linha de cotagem
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        paritipo       = ctypes.c_int (itipo)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        parx3          = ctypes.c_double (x3)
        pary3          = ctypes.c_double (y3)
        self.m_dwg.m_mdwg.COTIFOR (parpedmv)
        self.m_dwg.m_mdwg.COT3P    (ctypes.byref(paritipo), 
            ctypes.byref(parx1), ctypes.byref(pary1), 
            ctypes.byref(parx2), ctypes.byref(pary2), 
            ctypes.byref(parx3), ctypes.byref(pary3))
        self.m_dwg.m_mdwg.COTDTX ()

    def DimHorizontal (self, x1, y1, x2, y2, x3, y3):
        """
        Faz cotagem horizontal entre 2 pontos passando pelo terceiro\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem\n
        x3           ponto da linha de cotagem\n
        y3           ponto da linha de cotagem
        """
        self.Dim3P     (IDHOR, x1, y1, x2, y2, x3, y3)

    def DimVertical(self, x1, y1, x2, y2, x3, y3):
        """
        Faz cotagem vertical entre 2 pontos passando pelo terceiro\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem\n
        x3           ponto da linha de cotagem\n
        y3           ponto da linha de cotagem
        """
        self.Dim3P     (IDVER, x1, y1, x2, y2, x3, y3)

    def DimAligned (self, x1, y1, x2, y2, x3, y3):
        """
        Cotagem entre 2 pontos, na direção destes pontos\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem\n
        x3           ponto da linha de cotagem\n
        y3           ponto da linha de cotagem
        """
        self.Dim3P     (IDANG, x1, y1, x2, y2, x3, y3)

    def DimInclined (self, x1, y1, x2, y2, x3, y3, ang):
        """
        Faz cotagem inclinada com ângulo fornecido entre 2 pontos passando pelo terceiro\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem\n
        x3           ponto da linha de cotagem\n
        y3           ponto da linha de cotagem\n
        ang          Ângulo de inclinação, em graus
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        parx3          = ctypes.c_double (x3)
        pary3          = ctypes.c_double (y3)
        parang         = ctypes.c_double (ang)
        self.m_dwg.m_mdwg.COTIFOR (parpedmv)
        self.m_dwg.m_mdwg.COTINC (ctypes.byref(parang), 
            ctypes.byref(parx1), ctypes.byref(pary1), 
            ctypes.byref(parx2), ctypes.byref(pary2), 
            ctypes.byref(parx3), ctypes.byref(pary3))
        self.m_dwg.m_mdwg.COTDTX ()

    def DimContinue (self, x, y):
        """
        Continua última cotagem com ponto adicional\n
        x            Ponto de continuação\n
        y            Ponto de continuação
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parx           = ctypes.c_double (x)
        pary           = ctypes.c_double (y)
        self.m_dwg.m_mdwg.COTIFOR (parpedmv)
        self.m_dwg.m_mdwg.COTCON (ctypes.byref(parx), ctypes.byref(pary))
        self.m_dwg.m_mdwg.COTDTX ()


    def DimRadiusDiameter (self, itip, x1, y1, x2, y2):
        """
        Cotagem de raio ou diâmetro de arco/círculo\n
        itip         (0) Diâmetro (1) Raio\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        paritip        = ctypes.c_int (itip)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        self.m_dwg.m_mdwg.COTIFOR (parpedmv)
        self.m_dwg.m_mdwg.DIMAR2 (ctypes.byref(parx1), ctypes.byref(pary1), 
            ctypes.byref(parx2), ctypes.byref(pary2), ctypes.byref(paritip))


    def DimRadius (self, x1, y1, x2, y2):
        """
        Cotagem de raio de arco/círculo\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem
        """
        itip        = 1
        self.DimRadiusDiameter (itip, x1, y1, x2, y2)

    def DimDiameter (self, x1, y1, x2, y2):
        """
        Cotagem de diâmetro de raio/círculo\n
        x1           Primeiro ponto de cotagem\n
        y1           Primeiro ponto de cotagem\n
        x2           Segundo  ponto de cotagem\n
        y2           Degundo  ponto de cotagem
        """
        itip        = 0
        self.DimRadiusDiameter (itip, x1, y1, x2, y2)

    def DimAngular (self, x1, y1, x2, y2, x3, y3, x4, y4 , xcota, ycota):
        """
        Cotagem de ângulo entre as retas 1-2 passando pelo ponto de cota
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        parx3          = ctypes.c_double (x3)
        pary3          = ctypes.c_double (y3)
        parx4          = ctypes.c_double (x4)
        pary4          = ctypes.c_double (y4)
        parxcota       = ctypes.c_double (xcota)
        parycota       = ctypes.c_double (ycota)
        self.m_dwg.m_mdwg.COTIFOR (parpedmv)
        self.m_dwg.m_mdwg.DIMANG (ctypes.byref(parx1), ctypes.byref(pary1),
            ctypes.byref(parx2), ctypes.byref(pary2), 
            ctypes.byref(parx3), ctypes.byref(pary3),
            ctypes.byref(parx4), ctypes.byref(pary4),
            ctypes.byref(parxcota), ctypes.byref(parycota))

    def DimNote (self):
        """
        Desenho da linha com flecha de nota\n
        Use PolyStart () e PolyEnterPoint (x, y) para a definição dos pontos\n
        Será desenhada a polyline com uma flecha na ponta
        """
        parpedmv     = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_mdwg.g_dsppfl (parpedmv)

#-----------------------------------------------------------------------------
#    Funções globais de posições de ferros - Dentro do Dwg ()
#
class GlobalRebar ():

    def __init__ (self, dwg):
        self.m_dwg      = dwg

    @property
    def firstMark (self):
        """
        Primeira posição para renumeração
        """
        ifirstMark     = 0
        parifirstMark  = ctypes.c_int (ifirstMark)
        self.m_dwg.m_ipofer.IPOFER_POS_LERPRIMEIRA (ctypes.byref (parifirstMark))
        ifirstMark     = parifirstMark.value
        return      ifirstMark
 
    @firstMark.setter
    def firstMark (self, ifirstMark):
        """
        Primeira posição para renumeração
        """
        parifirstMark  = ctypes.c_int (ifirstMark)
        self.m_dwg.m_ipofer.IPOFER_POS_PRIMEIRA (ctypes.byref (parifirstMark))

    def RenumerateMarks (self):
        """
        Renumeração de posições, a partir da primeira posição definida em firstMark.
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        self.m_dwg.m_ipofer.IPOFER_POS_RENUMERAR (ctypes.byref (parpedmv))

    def FreeMark (self):
        """
        Retorna próximo número de posição livre para uso
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        ifreeMark      = 0
        parifreeMark   = ctypes.c_int (ifreeMark)
        self.m_dwg.m_ipofer.IPOFER_POS_PROXLIVRE (ctypes.byref (parpedmv),
                                                  ctypes.byref (parifreeMark))
        ifreeMark      = parifreeMark.value
        return         ifreeMark

#-----------------------------------------------------------------------------
#    Ferros Inteligentes
#    Um objeto para cada ferro criado, associado a um Dwg
#
class SmartRebar ():

    def __init__ (self, dwg, ferobjv=None):
        """
        Inicialização. O primeiro parâmetro é o objeto de desenho. Se o segundo\n
        for fornecido, é um handle C++ para o ferro. O uso é para montar um \n
        objeto SmartRebar na extração de desenhos, a partir de um apontador.
        """
        self.m_dwg      = dwg
        if              ferobjv == None:
            parpedmv        = ctypes.c_void_p (self.m_dwg.m_pedmv)
            self.m_ferobjv  = 0
            parferobjv      = ctypes.c_void_p (self.m_ferobjv)
            istat           = 0
            paristat        = ctypes.c_int (istat)
            self.m_dwg.m_ipofer.IPOFER_CRIARFERRO (ctypes.byref (parpedmv), 
                             ctypes.byref (parferobjv), ctypes.byref (paristat))
            self.m_ferobjv  = parferobjv.value
            istat           = paristat.value
            if              istat != 0:
                self.m_ferobjv = None
        else:
            self.m_ferobjv  = ferobjv

    @property
    def handle_rebar (self):
        """
        Retorna referência a este ferro, que pode ser usado em outro comando.
        """
        return          self.m_ferobjv

    @property
    def uniqueid (self):
        """
        Retorna identificador único de um ferro por desenho
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        iuniqueid      = 0
        pariuniqueid   = ctypes.c_int (iuniqueid)
        self.m_dwg.m_ipofer.IPOFER_IUNIQUEID (ctypes.byref (parferobjv), 
                                              ctypes.byref (pariuniqueid))
        iuniqueid      = pariuniqueid.value
        return         iuniqueid

    @property
    def type (self):
        """
        Tipo de ferro:\n
                    ICPFRT    Ferro reto\n
                    ICPFGN    Ferro genérico\n
                    ICPSTR    Estribo de viga\n
                    ICPSTRGEN Estribo genérico\n
                    ICPGRA    Grampo\n
                    ICPFAIMUL Faixa múltipla (não é ferro)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icftpf         = ICPFRT
        paricftpf      = ctypes.c_int (icftpf)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFTPF (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricftpf))
        icftpf         = paricftpf.value
        return         icftpf
    
    @type.setter
    def type (self, icftpf):
        """
        Tipo de ferro:\n
                    ICPFRT    Ferro reto\n
                    ICPFGN    Ferro genérico\n
                    ICPSTR    Estribo de viga\n
                    ICPSTRGEN Estribo genérico\n
                    ICPGRA    Grampo\n
                    ICPFAIMUL Faixa múltipla (não é ferro)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricftpf      = ctypes.c_int (icftpf)
        self.m_dwg.m_ipofer.IPOFER_ICFTPF (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricftpf))

    @property
    def mark (self):
        """
        Número da posição do ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfpos         = 0
        paricfpos      = ctypes.c_int (icfpos)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFPOS (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfpos))
        icfpos         = paricfpos.value
        return         icfpos

    @mark.setter
    def mark (self, icfpos):
        """
        Número da posição do ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfpos      = ctypes.c_int (icfpos)
        self.m_dwg.m_ipofer.IPOFER_ICFPOS (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfpos))

    @property
    def quantity (self):
        """
        Número de ferros
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfnfr         = 0
        paricfnfr      = ctypes.c_int (icfnfr)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFNFR (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfnfr))
        icfnfr         = paricfnfr.value
        return         icfnfr

    @quantity.setter
    def quantity (self, icfnfr):
        """
        Número de ferros
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfnfr      = ctypes.c_int (icfnfr)
        self.m_dwg.m_ipofer.IPOFER_ICFNFR (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfnfr))

    @property
    def multiplier (self):
        """
        Multiplicador de ferros
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfmul         = 0
        paricfmul      = ctypes.c_int (icfmul)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFMUL (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfmul))
        icfmul         = paricfmul.value
        return         icfmul

    @multiplier.setter
    def multiplier (self, icfmul):
        """
        Multiplicador de ferros
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfmul      = ctypes.c_int (icfmul)
        self.m_dwg.m_ipofer.IPOFER_ICFMUL (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfmul))

    @property
    def diameter (self):
        """
        Bitola do ferro, mm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        cfrbit         = 0.
        parcfrbit      = ctypes.c_double (cfrbit)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRBIT (ctypes.byref (parferobjv), 
                                               ctypes.byref (parcfrbit))
        cfrbit         = parcfrbit.value
        return         cfrbit

    @diameter.setter
    def diameter (self, cfrbit):
        """
        Bitola do ferro, mm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrbit      = ctypes.c_double (cfrbit)
        self.m_dwg.m_ipofer.IPOFER_CFRBIT (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrbit))

    @property
    def spacing (self):
        """
        Espaçamento de ferros, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        cfresp         = 0.
        parcfresp      = ctypes.c_double (cfresp)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRESP (ctypes.byref (parferobjv), 
                                               ctypes.byref (parcfresp))
        cfresp         = parcfresp.value
        return         cfresp

    @spacing.setter
    def spacing (self, cfresp):
        """
        Espaçamento de ferros, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfresp      = ctypes.c_double (cfresp)
        self.m_dwg.m_ipofer.IPOFER_CFRESP (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfresp))

    @property
    def ribbed (self):
        """
        (0) Ferros em lajes maciças\n
        (1) Ferros em lajes nervuradas
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfnrv         = 0
        paricfnrv      = ctypes.c_int (icfnrv)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFNRV (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfnrv))
        icfnrv         = paricfnrv.value
        return         icfnrv

    @ribbed.setter
    def ribbed (self, icfnrv):
        """
        (0) Ferros em lajes maciças\n
        (1) Ferros em lajes nervurada
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfnrv      = ctypes.c_int (icfnrv)
        self.m_dwg.m_ipofer.IPOFER_ICFNRV (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfnrv))

    @property
    def showRibbed (self):
        """
        (0) Não (1) Mostrar status de laje nervurada (C/NERV)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfnes         = 0
        paricfnes      = ctypes.c_int (icfnes)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFNES (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfnes))
        icfnes         = paricfnes.value
        return         icfnes

    @showRibbed.setter
    def showRibbed (self, icfnes):
        """
        (0) Não (1) Mostrar status de laje nervurada (C/NERV)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfnes      = ctypes.c_int (icfnes)
        self.m_dwg.m_ipofer.IPOFER_ICFNES (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfnes))

    @property
    def comment (self):
        """
        Comentário de um ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrobs      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan         = ctypes.c_int (0)
        self.m_dwg.m_ipofer.IPOFER_LER_CFROBS (ctypes.byref (parferobjv), parcfrobs, argfan)
        cfrobs         = parcfrobs.value.decode(TQS.TQSUtil.CHARSET)
        return         cfrobs

    @comment.setter
    def comment (self, cfrobs):
        """
        Comentário de um ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrobs      = ctypes.c_char_p (cfrobs.encode(TQS.TQSUtil.CHARSET))
        argfan         = ctypes.c_int (0)
        self.m_dwg.m_ipofer.IPOFER_CFROBS (ctypes.byref (parferobjv), parcfrobs, argfan)


    def _LerIcgtge (self):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icgtge         = 0
        paricgtge      = ctypes.c_int (icgtge)
        icgtgeneg      = 0
        paricgtgeneg   = ctypes.c_int (icgtgeneg)
        self.m_dwg.m_ipofer.IPOFER_LER_ICGTGE (ctypes.byref (parferobjv), 
                         ctypes.byref (paricgtge), ctypes.byref (paricgtgeneg))
        return         paricgtge.value, paricgtgeneg.value

    def _DefIcgtge (self, icgtge, icgtgeneg):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricgtge      = ctypes.c_int (icgtge)
        paricgtgeneg   = ctypes.c_int (icgtgeneg)
        self.m_dwg.m_ipofer.IPOFER_ICGTGE (ctypes.byref (parferobjv), 
                         ctypes.byref (paricgtge), ctypes.byref (paricgtgeneg))

    @property
    def leftHook (self):
        """
        Tipo de gancho definido à esquerda\n
                    ICPSGA Sem gancho a esquerda\n
                    ICP090 Gancho a 90\n
                    ICP135 Gancho a 135\n
                    ICP180 Gancho a 180
        """
        icgtge, icgtgeneg = self._LerIcgtge ()
        return            icgtge


    @leftHook.setter
    def leftHook (self, icgtge):
        """
        Tipo de gancho definido à esquerda\n
                    ICPSGA Sem gancho a esquerda\n
                    ICP090 Gancho a 90\n
                    ICP135 Gancho a 135\n
                    ICP180 Gancho a 180
        """
        icgtge2, icgtgeneg = self._LerIcgtge ()
        self._DefIcgtge (icgtge, icgtgeneg)

    @property
    def leftHookInvert (self):
        """
        (0) Não (1) Gancho à esquerda invertido
        """
        icgtge, icgtgeneg = self._LerIcgtge ()
        return            icgtgeneg


    @leftHook.setter
    def leftHookInvert (self, icgtgeneg):
        """
        (0) Não (1) Gancho à esquerda invertido
        """
        icgtge, icgtgeneg2 = self._LerIcgtge ()
        self._DefIcgtge (icgtge, icgtgeneg)


    def _LerIcgtgd (self):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icgtgd         = 0
        paricgtgd      = ctypes.c_int (icgtgd)
        icgtgdneg      = 0
        paricgtgdneg   = ctypes.c_int (icgtgdneg)
        self.m_dwg.m_ipofer.IPOFER_LER_ICGTGD (ctypes.byref (parferobjv), 
                         ctypes.byref (paricgtgd), ctypes.byref (paricgtgdneg))
        return         paricgtgd.value, paricgtgdneg.value

    def _DefIcgtgd (self, icgtgd, icgtgdneg):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricgtgd      = ctypes.c_int (icgtgd)
        paricgtgdneg   = ctypes.c_int (icgtgdneg)
        self.m_dwg.m_ipofer.IPOFER_ICGTGD (ctypes.byref (parferobjv), 
                         ctypes.byref (paricgtgd), ctypes.byref (paricgtgdneg))

    @property
    def rightHook (self):
        """
        Tipo de gancho definido à direita\n
                    ICPSGA Sem gancho a direita\n
                    ICP090 Gancho a 90\n
                    ICP135 Gancho a 135\n
                    ICP180 Gancho a 180
        """
        icgtgd, icgtgdneg = self._LerIcgtgd ()
        return            icgtgd


    @rightHook.setter
    def rightHook (self, icgtgd):
        """
        Tipo de gancho definido à direita\n
                    ICPSGA Sem gancho a direita\n
                    ICP090 Gancho a 90\n
                    ICP135 Gancho a 135\n
                    ICP180 Gancho a 180
        """
        icgtgd2, icgtgdneg = self._LerIcgtgd ()
        self._DefIcgtgd (icgtgd, icgtgdneg)

    @property
    def rightHookInvert (self):
        """
        (0) Não (1) Gancho à direita invertido
        """
        icgtgd, icgtgdneg = self._LerIcgtgd ()
        return            icgtgdneg


    @rightHook.setter
    def rightHookInvert (self, icgtgdneg):
        """
        (0) Não (1) Gancho à direita invertido
        """
        icgtgd, icgtgdneg2 = self._LerIcgtgd ()
        self._DefIcgtgd (icgtgd, icgtgdneg)

    @property
    def columnLevel (self):
        """
        Lance de pilar
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        ilance         = 0
        parilance      = ctypes.c_int (ilance)
        self.m_dwg.m_ipofer.IPOFER_LER_LANCE (ctypes.byref (parferobjv), 
                                              ctypes.byref (parilance))
        ilance         = parilance.value
        return         ilance

    @columnLevel.setter
    def columnLevel (self, ilance):
        """
        Lance de pilar
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parilance      = ctypes.c_int (ilance)
        self.m_dwg.m_ipofer.IPOFER_DEFLANCE (ctypes.byref (parferobjv), 
                                             ctypes.byref (parilance))


    @property
    def cover (self):
        """
        Cobrimento, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        cfrreb         = 0.
        parcfrreb      = ctypes.c_double (cfrreb)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRREB (ctypes.byref (parferobjv), 
                                               ctypes.byref (parcfrreb))
        cfrreb         = parcfrreb.value
        return         cfrreb

    @cover.setter
    def cover (self, cfrreb):
        """
        Cobrimento, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrreb      = ctypes.c_double (cfrreb)
        self.m_dwg.m_ipofer.IPOFER_CFRREB (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrreb))

    def RebarLine (self, xins, yins, angle, scale, identify, identifyBends, ipatas, 
                   iexplode, ilevel, iestilo, icolor):
        """
        Entra linha de ferro de qualquer tipo com dados atuais.\n
        Um mesmo ferro pode ser representado por mais de uma linha no desenho.\n
        xins          <- Pt de inserção\n
        yins          <- Pt de inserção\n
        angle         <- Ângulo de inserção graus\n
        scale         <- Escala de inserção\n
        identify      <- (1) Identificar o ferro\n
        identifyBends <- (1) Identificar dobras\n
        ipatas        <- (0) não (1) sim (2) 45° (3) 225° (4) invert\n
                         (0) e (1) vale para ICPFRT, ICPSTR, ICPSTRGEN e ICPGRA\n
                         (2), (3) e (4) valem para ICPFRT\n
        iexplode      <- (1) Explodir se estribo\n
        ilevel        <- Nível  0..255 EAG (-1) default\n
        iestilo       <- Estilo 0..5   EAG (-1) default\n
        icolor        <- Cor    0..255 EAG (-1) default
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parxins        = ctypes.c_double (xins)
        paryins        = ctypes.c_double (yins)
        parangle       = ctypes.c_double (angle)
        parscale       = ctypes.c_double (scale)
        paridentify    = ctypes.c_int (identify)
        paridentifyBend= ctypes.c_int (identifyBends)
        paripatas      = ctypes.c_int (ipatas)
        pariexplode    = ctypes.c_int (iexplode)
        parilevel      = ctypes.c_int (ilevel)
        pariestilo     = ctypes.c_int (iestilo)
        paricolor      = ctypes.c_int (icolor)
        self.m_dwg.m_ipofer.IPOFER_LINHAFER (ctypes.byref (parferobjv), 
            ctypes.byref (parxins), ctypes.byref (paryins), ctypes.byref (parangle), 
            ctypes.byref (parscale), ctypes.byref (paridentify), ctypes.byref (paridentifyBend), 
            ctypes.byref (paripatas), ctypes.byref (pariexplode), ctypes.byref (parilevel), 
            ctypes.byref (pariestilo), ctypes.byref (paricolor))

    def GetInsertionNumber (self):
        """
        Retorna o número de linhas inseridas associadas a um ferro
        """
        parferobjv  = ctypes.c_void_p (self.m_ferobjv)
        numins      = 0
        parnumins   = ctypes.c_int (numins)
        self.m_dwg.m_ipofer.IPOFER_LER_NUMINSER (ctypes.byref (parferobjv), 
                      ctypes.byref (parnumins))
        numins      = parnumins.value
        return      numins

    def GetInsertionData (self, indexins):
        """
        Retorna dados de uma linha inserida\n
        indexins        <- Índice da linha inserida, 0..GetInsertionNumber()-1\n
        Retorna:\n
        xins            -> Ponto de inserção\n
        yins            -> Ponto de inserção\n
        angins          -> Ângulo de inserção\n
        escxy           -> Escala de inserção\n
        identfer        -> (1) Identificar o ferro\n
        identdobr       -> (1) Identifica dobras\n
        ipatas          -> (0) não (1) sim (2) a 45°\n
        iexplodir       -> (1) Se representação explodida\n
        inivel          -> Nível  EAG (-1) default\n
        iestilo         -> Estilo EAG (-1) default\n
        icor            -> Cor    EAG (-1) default
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexins     = ctypes.c_int (indexins)
        xins            = 0.
        parxins         = ctypes.c_double (xins)
        yins            = 0.
        paryins         = ctypes.c_double (yins)
        angins          = 0.
        parangins       = ctypes.c_double (angins)
        escxy           = 0.
        parescxy        = ctypes.c_double (escxy)
        identfer        = 0
        paridentfer     = ctypes.c_int (identfer)
        identdobr       = 0
        paridentdobr    = ctypes.c_int (identdobr)
        ipatas          = 0
        paripatas       = ctypes.c_int (ipatas)
        iexplodir       = 0
        pariexplodir    = ctypes.c_int (iexplodir)
        inivel          = 0
        parinivel       = ctypes.c_int (inivel)
        iestilo         = 0
        pariestilo      = ctypes.c_int (iestilo)
        icor            = 0
        paricor         = ctypes.c_int (icor)
        self.m_dwg.m_ipofer.IPOFER_LER_INSERCAO (ctypes.byref (parferobjv), ctypes.byref (parindexins),
                          ctypes.byref (parxins), ctypes.byref (paryins), ctypes.byref (parangins),
                          ctypes.byref (parescxy), ctypes.byref (paridentfer),
                          ctypes.byref (paridentdobr), ctypes.byref (paripatas),
                          ctypes.byref (pariexplodir), ctypes.byref (parinivel),
                          ctypes.byref (pariestilo), ctypes.byref (paricor))
        xins            = parxins.value
        yins            = paryins.value
        angins          = parangins.value
        escxy           = parescxy.value
        identfer        = paridentfer.value
        identdobr       = paridentdobr.value
        ipatas          = paripatas.value
        iexplodir       = pariexplodir.value
        inivel          = parinivel.value
        iestilo         = pariestilo.value
        icor            = paricor.value
        return          xins, yins, angins, escxy, identfer, identdobr, ipatas, iexplodir, inivel, iestilo, icor

    def GetInsertionPoints (self, indexins):
        """
        Retorna o número de pontos de uma inserção\n
        indexins        <- Índice da linha inserida, 0..GetInsertionNumber()-1\n
        Retorna:\n
        np              -> Número de pontos da linha de ferro\n
        istat           -> (!=0) se não leu
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexins     = ctypes.c_int (indexins)
        np              = 0
        parnp           = ctypes.c_int (np)
        istat           = 0
        paristat        = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.IPOFER_LER_INSERCAOPOLIGNP (ctypes.byref (parferobjv), 
                        ctypes.byref (parindexins), ctypes.byref (parnp),
                        ctypes.byref (paristat))
        np              = parnp.value
        istat           = paristat.value
        return          np, istat

    def GetInsertionPoint (self, indexins, ipt):
        """
        Retorna as coordenadas de um ponto de um ferro inserido\n
        indexins        <- Índice da linha inserida, 0..GetInsertionNumber()-1\n
        ipt             <- Ponto a ler 0..np-1\n
        Retorna:\n
        x               -> Abcissa X\n
        y               -> Ordenada Y\n
        istat           -> (!=0) se não leu
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexins     = ctypes.c_int (indexins)
        paript          = ctypes.c_int (ipt)
        x               = 0.
        parx            = ctypes.c_double (x)
        y               = 0.
        pary            = ctypes.c_double (y)
        istat           = 0
        paristat        = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.IPOFER_LER_INSERCAOPOLIGXY (ctypes.byref (parferobjv), 
                        ctypes.byref (parindexins), ctypes.byref (paript),
                        ctypes.byref (parx), ctypes.byref (pary), ctypes.byref (paristat))
        x               = parx.value
        y               = pary.value
        istat           = paristat.value
        return          x, y, istat

    def SetInsertionData (self, indexins, xins, yins, angins, escxy, identfer, identdobr, \
                          ipatas, iexplodir, inivel, iestilo, icor):
        """
        Redefine dados de uma linha inserida
        indexins        <- Índice da linha inserida, 0..GetInsertionNumber()-1
        xins            <- Ponto de inserção
        yins            <- Ponto de inserção
        angins          <- Ângulo de inserção
        escxy           <- Escala de inserção
        identfer        <- (1) Identificar o ferro
        identdobr       <- (1) Identifica dobras
        ipatas          <- (0) não (1) sim (2) a 45°
        iexplodir       <- (1) Se representação explodida
        inivel          <- Nível  EAG (-1) default
        iestilo         <- Estilo EAG (-1) default
        icor            <- Cor    EAG (-1) default
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexins     = ctypes.c_int (indexins)
        parxins         = ctypes.c_double (xins)
        paryins         = ctypes.c_double (yins)
        parangins       = ctypes.c_double (angins)
        parescxy        = ctypes.c_double (escxy)
        paridentfer     = ctypes.c_int (identfer)
        paridentdobr    = ctypes.c_int (identdobr)
        paripatas       = ctypes.c_int (ipatas)
        pariexplodir    = ctypes.c_int (iexplodir)
        parinivel       = ctypes.c_int (inivel)
        pariestilo      = ctypes.c_int (iestilo)
        paricor         = ctypes.c_int (icor)
        self.m_dwg.m_ipofer.IPOFER_MOD_INSERCAO (ctypes.byref (parferobjv), ctypes.byref (parindexins),
                          ctypes.byref (parxins), ctypes.byref (paryins), ctypes.byref (parangins),
                          ctypes.byref (parescxy), ctypes.byref (paridentfer),
                          ctypes.byref (paridentdobr), ctypes.byref (paripatas),
                          ctypes.byref (pariexplodir), ctypes.byref (parinivel),
                          ctypes.byref (pariestilo), ctypes.byref (paricor))

    def SetInsertionPoint (self, indexins, ipt, x, y):
        """
        Redefine as coordenadas de um ponto de um ferro inserido\n
        indexins        <- Índice da linha inserida, 0..GetInsertionNumber()-1\n
        ipt             <- Ponto a ler 0..np-1\n
        x               <- Abcissa X\n
        y               <- Ordenada Y\n
        Retorna:\n
        istat           -> (!=0) se não leu
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexins     = ctypes.c_int (indexins)
        paript          = ctypes.c_int (ipt)
        parx            = ctypes.c_double (x)
        pary            = ctypes.c_double (y)
        istat           = 0
        paristat        = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.IPOFER_DEF_INSERCAOPOLIGXY (ctypes.byref (parferobjv), 
                        ctypes.byref (parindexins), ctypes.byref (paript),
                        ctypes.byref (parx), ctypes.byref (pary), ctypes.byref (paristat))
        istat           = paristat.value
        return          istat

    @property
    def repeated (self):
        """
        (0) Não (1) ferro repetido
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        irepeated      = 0
        parirepeated   = ctypes.c_int (irepeated)
        self.m_dwg.m_ipofer.IPOFER_LER_REPETIR (ctypes.byref (parferobjv), 
                                                ctypes.byref (parirepeated))
        irepeated      = parirepeated.value
        return         irepeated

    @repeated.setter
    def repeated (self, irepeated):
        """
        (0) Não (1) ferro repetido
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parirepeated   = ctypes.c_int (irepeated)
        self.m_dwg.m_ipofer.IPOFER_REPETIR (ctypes.byref (parferobjv), 
                                            ctypes.byref (parirepeated))

    def _LerRaiosCurv (self):
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        icftpdob        = 0
        cfrrai          = 0.
        icfrai          = 0
        icfraa          = 0
        icfrad          = 0
        icfrcurcotrai   = 0
        icfrcurcotdes   = 0
        icfrcurdestic   = 0
        cfrrcurtamtic   = 0.
        paricftpdob     = ctypes.c_int    (icftpdob)
        parcfrrai       = ctypes.c_double (cfrrai)
        paricfrai       = ctypes.c_int    (icfrai)
        paricfraa       = ctypes.c_int    (icfraa)
        paricfrad       = ctypes.c_int    (icfrad)
        paricfrcurcotrai= ctypes.c_int    (icfrcurcotrai)
        paricfrcurcotdes= ctypes.c_int    (icfrcurcotdes)
        paricfrcurdestic= ctypes.c_int    (icfrcurdestic)
        parcfrrcurtamtic= ctypes.c_double (cfrrcurtamtic)
        self.m_dwg.m_ipofer.IPOFER_LER_RAIOSDECURV (ctypes.byref (parferobjv), 
            ctypes.byref (paricftpdob), ctypes.byref (parcfrrai), ctypes.byref (paricfrai), 
            ctypes.byref (paricfraa), ctypes.byref (paricfrad), ctypes.byref (paricfrcurcotrai), 
            ctypes.byref (paricfrcurcotdes), ctypes.byref (paricfrcurdestic), 
            ctypes.byref (parcfrrcurtamtic))
        icftpdob        = paricftpdob.value
        cfrrai          = parcfrrai.value
        icfrai          = paricfrai.value
        icfraa          = paricfraa.value
        icfrad          = paricfrad.value
        icfrcurcotrai   = paricfrcurcotrai.value
        icfrcurcotdes   = paricfrcurcotdes.value
        icfrcurdestic   = paricfrcurdestic.value
        cfrrcurtamtic   = parcfrrcurtamtic.value
        return           icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic

    def _DefRaiosCurv (self, icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic):
        parferobjv      = ctypes.c_void_p   (self.m_ferobjv)
        paricftpdob     = ctypes.c_int    (icftpdob)
        parcfrrai       = ctypes.c_double (cfrrai)
        paricfrai       = ctypes.c_int    (icfrai)
        paricfraa       = ctypes.c_int    (icfraa)
        paricfrad       = ctypes.c_int    (icfrad)
        paricfrcurcotrai= ctypes.c_int    (icfrcurcotrai)
        paricfrcurcotdes= ctypes.c_int    (icfrcurcotdes)
        paricfrcurdestic= ctypes.c_int    (icfrcurdestic)
        parcfrrcurtamtic= ctypes.c_double (cfrrcurtamtic)
        self.m_dwg.m_ipofer.IPOFER_RAIOSDECURV (ctypes.byref (parferobjv), 
            ctypes.byref (paricftpdob), ctypes.byref (parcfrrai), ctypes.byref (paricfrai), 
            ctypes.byref (paricfraa), ctypes.byref (paricfrad), ctypes.byref (paricfrcurcotrai), 
            ctypes.byref (paricfrcurcotdes), ctypes.byref (paricfrcurdestic), 
            ctypes.byref (parcfrrcurtamtic))

    @property
    def bendType (self):
        """
        Tipo de dobra:\n
            (TQSDwg.ICPTPDOBGAN) Gancho de tração NBR6118:2003 9.4.2.3\n
            (TQSDwg.ICPTPDOBNOP) Nó de pórtico NBR6118:2003 18.2.2
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icftpdob 


    @bendType.setter
    def bendType (self, icftpdob):
        """
        Tipo de dobra:\n
            (TQSDwg.ICPTPDOBGAN) Gancho de tração NBR6118:2003 9.4.2.3\n
            (TQSDwg.ICPTPDOBNOP) Nó de pórtico NBR6118:2003 18.2.2
        """
        icftpdob2, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)

    @property
    def bendRadius (self):
        """
        Raio de dobra atual em cm ou (0) usar em função da bitola
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           cfrrai


    @bendRadius.setter
    def bendRadius (self, cfrrai):
        """
        Raio de dobra atual em cm ou (0) usar em função da bitola
        """
        icftpdob, cfrrai2, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendTotalLengthMode (self):
        """
        Modo de desconto de raios de dobra do comprimento total:\n
            TQSDwg.ICPDEF: Conforme o arquivo de critérios\n
            TQSDwg.ICPSRA: Faces externas sem desconto\n
            TQSDwg.ICPCRA: Comprimento desenvolvido com desconto de raio de dobra\n
            TQSDwg.ICPSMS: Soma simples dos trechos
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icfrai


    @bendTotalLengthMode.setter
    def bendTotalLengthMode (self, icfrai):
        """
        Modo de desconto de raios de dobra do comprimento total:\n
            TQSDwg.ICPDEF: Conforme o arquivo de critérios\n
            TQSDwg.ICPSRA: Faces externas sem desconto\n
            TQSDwg.ICPCRA: Comprimento desenvolvido com desconto de raio de dobra\n
            TQSDwg.ICPSMS: Soma simples dos trechos
        """
        icftpdob, cfrrai, icfrai2, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendRadiusDisplay (self):
        """
        Modo de apresentação dos raios de dobra:\n
            TQSDwg.ICPDEF: Conforme o arquivo de critérios\n
            TQSDwg.ICPMAN: Não mostrar\n
            TQSDwg.ICPAUT: Mostrar
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icfraa


    @bendRadiusDisplay.setter
    def bendRadiusDisplay (self, icfraa):
        """
        Modo de apresentação dos raios de dobra:\n
            TQSDwg.ICPDEF: Conforme o arquivo de critérios\n
            TQSDwg.ICPMAN: Não mostrar\n
            TQSDwg.ICPAUT: Mostrar
        """
        icftpdob, cfrrai, icfrai, icfraa2, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendBendLengthMode (self):
        """
        Modo representação de desconto das dobras:\n
            TQSDwg.ICPDEF:    Conforme o arquivo de critérios\n
            TQSDwg.ICPDOBSRA: Faces externas, sem desconto\n
            TQSDwg.ICPDOBCRA: Desenvolvimento com raios de dobras\n
            TQSDwg.ICPDOBSMS: Comprimento do trecho
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icfrad


    @bendBendLengthMode.setter
    def bendBendLengthMode (self, icfrad):
        """
        Modo representação de desconto das dobras:\n
            TQSDwg.ICPDEF:    Conforme o arquivo de critérios\n
            TQSDwg.ICPDOBSRA: Faces externas, sem desconto\n
            TQSDwg.ICPDOBCRA: Desenvolvimento com raios de dobras\n
            TQSDwg.ICPDOBSMS: Comprimento do trecho
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad2, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendDimRadius (self):
        """
        Cotagem de raio de curvatura\n
            (-1)  Conforme o arquivo de critérios\n
            ( 0)  Não\n
            ( 1)  Sim
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icfrcurcotrai


    @bendDimRadius.setter
    def bendDimRadius (self, icfrcurcotrai):
        """
        Cotagem de raio de curvatura\n
            (-1)  Conforme o arquivo de critérios\n
            ( 0)  Não\n
            ( 1)  Sim
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai2, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendDimPerimeter (self):
        """
        Cotagem de perímetro da curvatura\n
            (-1)  Conforme o arquivo de critérios\n
            ( 0)  Não\n
            ( 1)  Sim
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icfrcurcotdes


    @bendDimPerimeter.setter
    def bendDimPerimeter (self, icfrcurcotdes):
        """
        Cotagem de perímetro da curvatura\n
            (-1)  Conforme o arquivo de critérios\n
            ( 0)  Não\n
            ( 1)  Sim
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes2, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendTickDisplay (self):
        """
        Desenho de tick da cotagem de curvatura\n
            (-1)  Conforme o arquivo de critérios\n
            ( 0)  Não\n
            ( 1)  Sim
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           icfrcurdestic


    @bendTickDisplay.setter
    def bendTickDisplay (self, icfrcurdestic):
        """
        Desenho de tick da cotagem de curvatura\n
            (-1)  Conforme o arquivo de critérios\n
            ( 0)  Não\n
            ( 1)  Sim
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic2, cfrrcurtamtic = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def bendTickSize (self):
        """
        Tamanho do tick da cotagem da curvatura em cm de plotagem
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic = self._LerRaiosCurv ()
        return           cfrrcurtamtic


    @bendTickSize.setter
    def bendTickSize (self, cfrrcurtamtic):
        """
        Tamanho do tick da cotagem da curvatura em cm de plotagem
        """
        icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, icfrcurcotdes, icfrcurdestic, cfrrcurtamtic2 = self._LerRaiosCurv ()
        self._DefRaiosCurv (icftpdob, cfrrai, icfrai, icfraa, icfrad, icfrcurcotrai, 
                       icfrcurcotdes, icfrcurdestic, cfrrcurtamtic)


    @property
    def textHeigth (self):
        """
        Altura do texto de ferros, cm de plotagem
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        cfrtfr         = 0.
        parcfrtfr      = ctypes.c_double (cfrtfr)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRTFR (ctypes.byref (parferobjv), 
                                               ctypes.byref (parcfrtfr))
        cfrtfr         = parcfrtfr.value
        return         cfrtfr

    @textHeigth.setter
    def textHeigth (self, cfrtfr):
        """
        Altura do texto de ferros, cm de plotagem
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrtfr      = ctypes.c_double (cfrtfr)
        self.m_dwg.m_ipofer.IPOFER_CFRTFR (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrtfr))

    @property
    def distributionTextHeigth (self):
        """
        Altura do texto de descrição das faixas de distribuição, cm de plotagem
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        cfrtfai        = 0.
        parcfrtfai     = ctypes.c_double (cfrtfai)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRTFAI (ctypes.byref (parferobjv), 
                                                ctypes.byref (parcfrtfai))
        cfrtfai         = parcfrtfai.value
        return         cfrtfai

    @distributionTextHeigth.setter
    def distributionTextHeigth (self, cfrtfai):
        """
        Altura do texto de descrição das faixas de distribuição, cm de plotagem
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrtfai      = ctypes.c_double (cfrtfai)
        self.m_dwg.m_ipofer.IPOFER_CFRTFAI (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrtfai))


    @property
    def straightBarMainLength (self):
        """
        Comprimento principal de ferro reto, cm
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfrcho        = 0.
        parcfrcho     = ctypes.c_double (cfrcho)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRCHO (ctypes.byref (parferobjv), 
                                                ctypes.byref (parcfrcho))
        cfrcho         = parcfrcho.value
        return         cfrcho

    @straightBarMainLength.setter
    def straightBarMainLength (self, cfrcho):
        """
        Comprimento principal de ferro reto, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrcho      = ctypes.c_double (cfrcho)
        self.m_dwg.m_ipofer.IPOFER_CFRCHO (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrcho))

    @property
    def straightBarLeftLength (self):
        """
        Comprimento da dobra esquerda de ferro reto, cm
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfrdes        = 0.
        parcfrdes     = ctypes.c_double (cfrdes)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRDES (ctypes.byref (parferobjv), 
                                                ctypes.byref (parcfrdes))
        cfrdes         = parcfrdes.value
        return         cfrdes

    @straightBarLeftLength.setter
    def straightBarLeftLength (self, cfrdes):
        """
        Comprimento da dobra esquerda de ferro reto, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrdes      = ctypes.c_double (cfrdes)
        self.m_dwg.m_ipofer.IPOFER_CFRDES (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrdes))

    @property
    def straightBarRightLength (self):
        """
        Comprimento da dobra direita de ferro reto, cm
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfrded        = 0.
        parcfrded     = ctypes.c_double (cfrded)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRDED (ctypes.byref (parferobjv), 
                                                ctypes.byref (parcfrded))
        cfrded         = parcfrded.value
        return         cfrded

    @straightBarRightLength.setter
    def straightBarRightLength (self, cfrded):
        """
        Comprimento da dobra direita de ferro reto, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrded      = ctypes.c_double (cfrded)
        self.m_dwg.m_ipofer.IPOFER_CFRDED (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrded))

    @property
    def straightBarLeftLength2 (self):
        """
        Comprimento da 2a dobra esquerda de ferro reto, cm
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfrde2        = 0.
        parcfrde2     = ctypes.c_double (cfrde2)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRDE2 (ctypes.byref (parferobjv), 
                                                ctypes.byref (parcfrde2))
        cfrde2         = parcfrde2.value
        return         cfrde2

    @straightBarLeftLength2.setter
    def straightBarLeftLength2 (self, cfrde2):
        """
        Comprimento da 2a dobra esquerda de ferro reto, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrde2      = ctypes.c_double (cfrde2)
        self.m_dwg.m_ipofer.IPOFER_CFRDE2 (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrde2))

    @property
    def straightBarRightLength2 (self):
        """
        Comprimento da 2a dobra direita de ferro reto, cm
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfrdd2        = 0.
        parcfrdd2     = ctypes.c_double (cfrdd2)
        self.m_dwg.m_ipofer.IPOFER_LER_CFRDD2 (ctypes.byref (parferobjv), 
                                                ctypes.byref (parcfrdd2))
        cfrdd2         = parcfrdd2.value
        return         cfrdd2

    @straightBarRightLength2.setter
    def straightBarRightLength2 (self, cfrdd2):
        """
        Comprimento da 2a dobra direita de ferro reto, cm
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfrdd2      = ctypes.c_double (cfrdd2)
        self.m_dwg.m_ipofer.IPOFER_CFRDD2 (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfrdd2))


    @property
    def straightBarZone (self):
        """
        Posição de ferro reto:\n
            ICPPOS:  Armadura positiva (face inferior)\n
            ICPNEG:  Armadura negativa (face superior)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfipn         = 0
        paricfipn      = ctypes.c_int (icfipn)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFIPN (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfipn))
        icfipn         = paricfipn.value
        return         icfipn

    @straightBarZone.setter
    def straightBarZone (self, icfipn):
        """
        Posição de ferro reto:\n
            ICPPOS:  Armadura positiva (face inferior)\n
            ICPNEG:  Armadura negativa (face superior)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfipn      = ctypes.c_int (icfipn)
        self.m_dwg.m_ipofer.IPOFER_ICFIPN (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfipn))

    @property
    def straightBarBendType (self):
        """
        Tipo de dobra de um ferro reto:\n
            ICPNSU: dobra normal\n
            ICPDSU: dobra de suspensão\n
            ICPDS2: dobra de suspensão do mesmo lado
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfdsu         = 0
        paricfdsu      = ctypes.c_int (icfdsu)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFDSU (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfdsu))
        icfdsu         = paricfdsu.value
        return         icfdsu

    @straightBarBendType.setter
    def straightBarBendType (self, icfdsu):
        """
        Tipo de dobra de um ferro reto:\n
            ICPNSU: dobra normal\n
            ICPDSU: dobra de suspensão\n
            ICPDS2: dobra de suspensão do mesmo lado
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfdsu      = ctypes.c_int (icfdsu)
        self.m_dwg.m_ipofer.IPOFER_ICFDSU (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfdsu))

    @property
    def straightBarTextDirection (self):
        """
        Direção dos textos de dobras:\n
            (0):  Direção do trecho\n
            (1):  Direção do ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        idirdobr       = 0
        paridirdobr    = ctypes.c_int (idirdobr)
        self.m_dwg.m_ipofer.IPOFER_LER_IDIRDOBR (ctypes.byref (parferobjv), 
                                                 ctypes.byref (paridirdobr))
        idirdobr         = paridirdobr.value
        return         idirdobr

    @straightBarTextDirection.setter
    def straightBarTextDirection (self, idirdobr):
        """
        Direção dos textos de dobras:\n
            (0):  Direção do trecho\n
            (1):  Direção do ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paridirdobr    = ctypes.c_int (idirdobr)
        self.m_dwg.m_ipofer.IPOFER_IDIRDOBR (ctypes.byref (parferobjv), 
                                             ctypes.byref (paridirdobr))

    @property
    def straightBarTextPosition (self):
        """
        Texto principal de ferros:\n
            (0) Não colocar\n
            (1) Acima da linha de ferro\n
            (2) Abaixo da linha de ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        ipostrepri     = 0
        paripostrepri  = ctypes.c_int (ipostrepri)
        self.m_dwg.m_ipofer.IPOFER_LER_IPOSTREPRI (ctypes.byref (parferobjv), 
                                                   ctypes.byref (paripostrepri))
        ipostrepri     = paripostrepri.value
        return         ipostrepri

    @straightBarTextPosition.setter
    def straightBarTextPosition (self, ipostrepri):
        """
        Texto principal de ferros:\n
            (0) Não colocar\n
            (1) Acima da linha de ferro\n
            (2) Abaixo da linha de ferro
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paripostrepri  = ctypes.c_int (ipostrepri)
        self.m_dwg.m_ipofer.IPOFER_IPOSTREPRI (ctypes.byref (parferobjv), 
                                               ctypes.byref (paripostrepri))

    @property
    def straightBarContinuous (self):
        """
        Ferro corrido: (0) Não (1) Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icorrido     = 0
        paricorrido  = ctypes.c_int (icorrido)
        self.m_dwg.m_ipofer.IPOFER_LER_ICORRIDO (ctypes.byref (parferobjv), 
                                                 ctypes.byref (paricorrido))
        icorrido     = paricorrido.value
        return         icorrido

    @straightBarContinuous.setter
    def straightBarContinuous (self, icorrido):
        """
        Ferro corrido: (0) Não (1) Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricorrido    = ctypes.c_int (icorrido)
        self.m_dwg.m_ipofer.IPOFER_ICORRIDO (ctypes.byref (parferobjv), 
                                             ctypes.byref (paricorrido))

    def _LerLuvas (self):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        iluvai         = 0
        pariluvai  = ctypes.c_int (iluvai)
        iluvaf         = 0
        pariluvaf  = ctypes.c_int (iluvaf)
        self.m_dwg.m_ipofer.IPOFER_LER_ILUVAS (ctypes.byref (parferobjv), 
                            ctypes.byref (pariluvai), ctypes.byref (pariluvaf))
        iluvai         = pariluvai.value
        iluvaf         = pariluvaf.value
        return         iluvai, iluvaf

    def _DefLuvas (self, iluvai, iluvaf):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        pariluvai  = ctypes.c_int (iluvai)
        pariluvaf  = ctypes.c_int (iluvaf)
        self.m_dwg.m_ipofer.IPOFER_ILUVAS (ctypes.byref (parferobjv), 
                            ctypes.byref (pariluvai), ctypes.byref (pariluvaf))

    @property
    def startCoupler (self):
        """
        Luva no início da barra (0) Não (1) Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        iluvai, iluvaf = self._LerLuvas ()
        return         iluvai

    @startCoupler.setter
    def startCoupler (self, iluvai):
        """
        Luva no início da barra (0) Não (1) Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        iluvai2, iluvaf = self._LerLuvas ()
        self._DefLuvas (iluvai, iluvaf)

    @property
    def endCoupler (self):
        """
        Luva no fim da barra (0) Não (1) Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        iluvai, iluvaf = self._LerLuvas ()
        return         iluvai

    @endCoupler.setter
    def endCoupler (self, iluvaf):
        """
        Luva no fim da barra (0) Não (1) Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        iluvai, iluvaf2 = self._LerLuvas ()
        self._DefLuvas (iluvai, iluvaf)

    @property
    def mirrorMode (self):
        """
        Espelhamento (0) restrito (1) completo
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        idbresp        = 0
        paridbresp     = ctypes.c_int (idbresp)
        self.m_dwg.m_ipofer.IPOFER_LER_IDBRESP (ctypes.byref (parferobjv), 
                                                ctypes.byref (paridbresp))
        idbresp        = paridbresp.value
        return         idbresp

    @mirrorMode.setter
    def mirrorMode (self, idbresp):
        """
        Espelhamento (0) restrito (1) completo
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paridbresp     = ctypes.c_int (idbresp)
        self.m_dwg.m_ipofer.IPOFER_IDBRESP (ctypes.byref (parferobjv), 
                                            ctypes.byref (paridbresp))


    @property
    def alternatingMode (self):
        """
        Alternância de ferros retos:\n
            ICPSAL: Não\n
            ICPCAL: Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfalt         = 0
        paricfalt      = ctypes.c_int (icfalt)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFALT (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfalt))
        icfalt        = paricfalt.value
        return         icfalt

    @alternatingMode.setter
    def alternatingMode (self, icfalt):
        """
        Alternância de ferros retos:\n
            ICPSAL: Não\n
            ICPCAL: Sim
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfalt      = ctypes.c_int (icfalt)
        self.m_dwg.m_ipofer.IPOFER_ICFALT (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfalt))


    @property
    def alternatingFactor (self):
        """
        Fator de alternância de ferro reto
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfaltf        = 0.
        parcfaltf     = ctypes.c_double (cfaltf)
        self.m_dwg.m_ipofer.IPOFER_LER_CFALTF (ctypes.byref (parferobjv), 
                                               ctypes.byref (parcfaltf))
        cfaltf         = parcfaltf.value
        return         cfaltf

    @alternatingFactor.setter
    def alternatingFactor (self, cfaltf):
        """
        Fator de alternância de ferro reto
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcfaltf      = ctypes.c_double (cfaltf)
        self.m_dwg.m_ipofer.IPOFER_CFALTF (ctypes.byref (parferobjv), 
                                           ctypes.byref (parcfaltf))

    def GenRebarPoint (self, xpt, ypt, zpt, iarc, identbend, indfrt):
        """
        Entra com um ponto de uma poligonal de ferro genérico. \n
        A poligonal será transformada na inserção em IPOFER_LINHAFER.\n
            xpt       <- X\n
            ypt       <- Y\n
            zpt       <- Z\n
            iarc      <- (0) trecho reto (1) centro de arco\n
            identbend <- (0) Não (1) Identificar a dobra\n
            indfrt    <- Índice de trecho principal (-1)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parxpt         = ctypes.c_double (xpt)
        parypt         = ctypes.c_double (ypt)
        parzpt         = ctypes.c_double (zpt)
        pariarc        = ctypes.c_int    (iarc)
        paridentbend   = ctypes.c_int    (identbend)
        parindfrt      = ctypes.c_int    (indfrt)
        self.m_dwg.m_ipofer.IPOFER_PTFERGEN (ctypes.byref (parferobjv), 
            ctypes.byref (parxpt), ctypes.byref (parypt), ctypes.byref (parzpt), 
            ctypes.byref (pariarc), ctypes.byref (paridentbend), ctypes.byref (parindfrt))

    def GetGenRebarPoints (self):
        """
        Retorna o número de pontos da poligonal de ferro genérico
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        numpts          = 0
        parnumpts       = ctypes.c_int (numpts)
        self.m_dwg.m_ipofer.IPOFER_LER_NUMPTFERGEN (ctypes.byref (parferobjv), 
                         ctypes.byref (parnumpts))
        numpts          = parnumpts.value
        return          numpts


    def GetGenRebarPoint (self, indexpoint):
        """
        Retorna um ponto de ferro genérico (em relação ao ponto de inserção)\n
        indexpoint      <- Índice do ponto a ler, 0..GetGenRebarPoints()-1\n
        Retorna:\n
        xpt             -> X\n
        ypt             -> Y\n
        zpt             -> Z\n
        iarco           -> (1) se centro de arco\n
        identdobr       -> (1) p/identificar a dobra\n
        indfrt          -> Índice de trecho equiv ou (-1)
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexpoint   = ctypes.c_int (indexpoint)
        xpt             = 0.
        parxpt          = ctypes.c_double (xpt)
        ypt             = 0.
        parypt          = ctypes.c_double (ypt)
        zpt             = 0.
        parzpt          = ctypes.c_double (zpt)
        iarco           = 0
        pariarco        = ctypes.c_int (iarco)
        identdobr       = 0
        paridentdobr    = ctypes.c_int (identdobr)
        indfrt          = 0
        parindfrt       = ctypes.c_int (indfrt)
        self.m_dwg.m_ipofer.IPOFER_LER_PTFERGEN (ctypes.byref (parferobjv), 
                        ctypes.byref (parindexpoint), ctypes.byref (parxpt),
                        ctypes.byref (parypt), ctypes.byref (parzpt),
                        ctypes.byref (pariarco), ctypes.byref (paridentdobr),
                        ctypes.byref (parindfrt))
        xpt             = parxpt.value
        ypt             = parypt.value
        zpt             = parzpt.value
        iarco           = pariarco.value
        identdobr       = paridentdobr.value
        indfrt          = parindfrt.value
        return          xpt, ypt, zpt, iarco, identdobr, indfrt   

    def SetGenRebarPoint (self, indexpoint, xpt, ypt, zpt, iarco, identdobr, indfrt):
        """
        Redefine um ponto de ferro genérico
        indexpoint      Índice do ponto a ler, 0..GetGenRebarPoints()-1
        xpt             <- X
        ypt             <- Y
        zpt             <- Z
        iarco           <- (1) se centro de arco
        identdobr       <- (1) p/identificar a dobra
        indfrt          <- Índice de trecho equiv ou (-1)
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parindexpoint   = ctypes.c_int (indexpoint)
        parxpt          = ctypes.c_double (xpt)
        parypt          = ctypes.c_double (ypt)
        parzpt          = ctypes.c_double (zpt)
        pariarco        = ctypes.c_int (iarco)
        paridentdobr    = ctypes.c_int (identdobr)
        parindfrt       = ctypes.c_int (indfrt)
        self.m_dwg.m_ipofer.IPOFER_MOD_PTFERGEN (ctypes.byref (parferobjv), 
                        ctypes.byref (parindexpoint), ctypes.byref (parxpt),
                        ctypes.byref (parypt), ctypes.byref (parzpt),
                        ctypes.byref (pariarco), ctypes.byref (paridentdobr),
                        ctypes.byref (parindfrt))

    @property
    def stirrupType (self):
        """
        Tipo de estribo de vigas:\n
            ICPENR  Normal\n
            ICPEFC  Fechado\n
            ICPEAB  Aberto\n
            ICPENC  Normal com largura colaborante
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icftpe         = 0
        paricftpe      = ctypes.c_int (icftpe)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFTPE (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricftpe))
        icftpe     = paricftpe.value
        return         icftpe

    @stirrupType.setter
    def stirrupType (self, icftpe):
        """
        Tipo de estribo de vigas:\n
            ICPENR  Normal\n
            ICPEFC  Fechado\n
            ICPEAB  Aberto\n
            ICPENC  Normal com largura colaborante
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricftpe      = ctypes.c_int (icftpe)
        self.m_dwg.m_ipofer.IPOFER_ICFTPE (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricftpe))


    @property
    def stirrupLegs (self):
        """
        Número de ramos de estribos:\n
            ICPNR2:   Estribo de 2 ramos\n
            ICPNR4:   Estribo de 4 ramos\n
            ICPNR6:   Estribo de 6 ramos\n
            ICPNR4B:  Estribo de 4 ramos config B
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icfnre         = 0
        paricfnre      = ctypes.c_int (icfnre)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFNRE (ctypes.byref (parferobjv), 
                                               ctypes.byref (paricfnre))
        icfnre     = paricfnre.value
        return         icfnre

    @stirrupLegs.setter
    def stirrupLegs (self, icfnre):
        """
        Número de ramos de estribos:\n
            ICPNR2:   Estribo de 2 ramos\n
            ICPNR4:   Estribo de 4 ramos\n
            ICPNR6:   Estribo de 6 ramos\n
            ICPNR4B:  Estribo de 4 ramos config B
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfnre      = ctypes.c_int (icfnre)
        self.m_dwg.m_ipofer.IPOFER_ICFNRE (ctypes.byref (parferobjv), 
                                           ctypes.byref (paricfnre))

    def _LerDadEstrib (self):
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        cfeb           = 0.
        cfeh           = 0.
        cfeb2          = 0.
        cfeh2          = 0.
        cfelce         = 0.
        cfelcd         = 0.
        cfedbr         = 0.
        parcfeb        = ctypes.c_double (cfeb)
        parcfeh        = ctypes.c_double (cfeh)
        parcfeb2       = ctypes.c_double (cfeb2)
        parcfeh2       = ctypes.c_double (cfeh2)
        parcfelce      = ctypes.c_double (cfelce)
        parcfelcd      = ctypes.c_double (cfelcd)
        parcfedbr      = ctypes.c_double (cfedbr)
        self.m_dwg.m_ipofer.IPOFER_LER_DADESTRIB (ctypes.byref (parferobjv), 
            ctypes.byref (parcfeb), ctypes.byref (parcfeh), ctypes.byref (parcfeb2), 
            ctypes.byref (parcfeh2), ctypes.byref (parcfelce), ctypes.byref (parcfelcd), 
            ctypes.byref (parcfedbr))
        cfeb           = parcfeb.value
        cfeh           = parcfeh.value
        cfeb2          = parcfeb2.value
        cfeh2          = parcfeh2.value
        cfelce         = parcfelce.value
        cfelcd         = parcfelcd.value
        cfedbr         = parcfedbr.value
        return         cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr

    def _DefDadEstrib (self, cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr):
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        parcfeb        = ctypes.c_double (cfeb)
        parcfeh        = ctypes.c_double (cfeh)
        parcfeb2       = ctypes.c_double (cfeb2)
        parcfeh2       = ctypes.c_double (cfeh2)
        parcfelce      = ctypes.c_double (cfelce)
        parcfelcd      = ctypes.c_double (cfelcd)
        parcfedbr      = ctypes.c_double (cfedbr)
        self.m_dwg.m_ipofer.IPOFER_DADESTRIB (ctypes.byref (parferobjv), 
            ctypes.byref (parcfeb), ctypes.byref (parcfeh), ctypes.byref (parcfeb2), 
            ctypes.byref (parcfeh2), ctypes.byref (parcfelce), ctypes.byref (parcfelcd), 
            ctypes.byref (parcfedbr))

    @property
    def stirrupSectionWidth (self):
        """
        Largura da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfeb

    @stirrupSectionWidth.setter
    def stirrupSectionWidth (self, cfeb):
        """
        Largura da seção transversal que contém o estribo, cm
        """
        cfebx, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)

    @property
    def stirrupSectionHeight (self):
        """
        Altura da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfeh

    @stirrupSectionHeight.setter
    def stirrupSectionHeight (self, cfeh):
        """
        Altura da seção transversal que contém o estribo, cm
        """
        cfeb, cfehx, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)

    @property
    def stirrupSectionWidth2 (self):
        """
        Largura final da seção transversal variável que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfeb2

    @stirrupSectionWidth2.setter
    def stirrupSectionWidth2 (self, cfeb2):
        """
        Largura final da seção transversal variável que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2x, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)

    @property
    def stirrupSectionHeight2 (self):
        """
        Altura final da seção transversal variável que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfeh2

    @stirrupSectionHeight2.setter
    def stirrupSectionHeight2 (self, cfeh2):
        """
        Altura final da seção transversal variável que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2x, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)

    @property
    def stirrupEffectiveLeftWidth (self):
        """
        Largura esquerda colaborante da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfelce

    @stirrupEffectiveLeftWidth.setter
    def stirrupEffectiveLeftWidth (self, cfelce):
        """
        Largura esquerda colaborante da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelcex, cfelcd, cfedbr = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)

    @property
    def stirrupEffectiveRightWidth (self):
        """
        Largura direita colaborante da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfelcd

    @stirrupEffectiveRightWidth.setter
    def stirrupEffectiveRightWidth (self, cfelcd):
        """
        Largura direita colaborante da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcdx, cfedbr = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)

    @property
    def stirrupSlabBendLength (self):
        """
        Largura direita colaborante da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr = self._LerDadEstrib ()
        return         cfedbr

    @stirrupSlabBendLength.setter
    def stirrupSlabBendLength (self, cfedbr):
        """
        Largura direita colaborante da seção transversal que contém o estribo, cm
        """
        cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbrx = self._LerDadEstrib ()
        self._DefDadEstrib (cfeb, cfeh, cfeb2, cfeh2, cfelce, cfelcd, cfedbr)


    @property
    def stirrupHookLength (self):
        """
        Comprimento da pata de estribos em número de bitolas
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        nfiane        = 0
        parnfiane     = ctypes.c_int (nfiane)
        self.m_dwg.m_ipofer.IPOFER_LER_NFIANE (ctypes.byref (parferobjv), 
                                               ctypes.byref (parnfiane))
        nfiane         = parnfiane.value
        return         nfiane

    @stirrupHookLength.setter
    def stirrupHookLength (self, nfiane):
        """
        Comprimento da pata de estribos em número de bitolas
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parnfiane      = ctypes.c_int (nfiane)
        self.m_dwg.m_ipofer.IPOFER_NFIANE (ctypes.byref (parferobjv), 
                                           ctypes.byref (parnfiane))

    @property
    def stirrupHookType (self):
        """
        Tipo de pata de estribo:\n
            ICPTPPATA45   45 graus\n
            ICPTPPATA90   90 graus
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icftppata      = 0
        paricftppata   = ctypes.c_int (icftppata)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFTPPATA (ctypes.byref (parferobjv), 
                                                  ctypes.byref (paricftppata))
        icftppata      = paricftppata.value
        return         icftppata

    @stirrupHookType.setter
    def stirrupHookType (self, icftppata):
        """
        Tipo de pata de estribo:\n
            ICPTPPATA45   45 graus\n
            ICPTPPATA90   90 graus
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        paricftppata    = ctypes.c_int (icftppata)
        self.m_dwg.m_ipofer.IPOFER_ICFTPPATA (ctypes.byref (parferobjv), 
                                              ctypes.byref (paricftppata))

    @property
    def stirrupInternalLegDiameter (self):
        """
        Bitola mm diferente para estribo interno de 4 ou 6 ramos
        """
        parferobjv    = ctypes.c_void_p (self.m_ferobjv)
        cfaltf        = 0.
        bitstrin     = ctypes.c_double (cfaltf)
        self.m_dwg.m_ipofer.IPOFER_LER_BITSTRIN (ctypes.byref (parferobjv), 
                                               ctypes.byref (bitstrin))
        cfaltf         = bitstrin.value
        return         cfaltf

    @stirrupInternalLegDiameter.setter
    def stirrupInternalLegDiameter (self, cfaltf):
        """
        Bitola mm diferente para estribo interno de 4 ou 6 ramos
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        bitstrin      = ctypes.c_double (cfaltf)
        self.m_dwg.m_ipofer.IPOFER_BITSTRIN (ctypes.byref (parferobjv), 
                                           ctypes.byref (bitstrin))

    @property
    def genericStirrupType (self):
        """
        Tipo de estribo genérico:\n
            ICPEGENFEC: Fechado \n
            ICPEGENABR: Aberto \n
            ICPEGENGRA: Grampo de pilar \n
            ICPEGENCIR: Circular 
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        icftpeg        = 0
        paricftpeg     = ctypes.c_int (icftpeg)
        self.m_dwg.m_ipofer.IPOFER_LER_ICFTPEG (ctypes.byref (parferobjv), 
                                                ctypes.byref (paricftpeg))
        icftpeg        = paricftpeg.value
        return         icftpeg

    @genericStirrupType.setter
    def genericStirrupType (self, icftpeg):
        """
        Tipo de estribo genérico:\n
            ICPEGENFEC: Fechado \n
            ICPEGENABR: Aberto \n
            ICPEGENGRA: Grampo de pilar \n
            ICPEGENCIR: Circular 
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        paricftpeg      = ctypes.c_int (icftpeg)
        self.m_dwg.m_ipofer.IPOFER_ICFTPEG (ctypes.byref (parferobjv), 
                                            ctypes.byref (paricftpeg))


    @property
    def genericStirrupEntryMode (self):
        """
        Modo de definição de estribo genérico:\n
            ICPEGPONTOSLONG:   Pontos longitudinais\n
            ICPEGPONTOSSECA:   Pontos da seção longitudinal\n
            ICPEGPONTOSEXTR:   Pontos externos
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        iestrgenstat    = 0
        pariestrgenstat = ctypes.c_int (iestrgenstat)
        self.m_dwg.m_ipofer.IPOFER_LER_IESTRGENSTAT (ctypes.byref (parferobjv), 
                                                     ctypes.byref (pariestrgenstat))
        iestrgenstat        = pariestrgenstat.value
        return         iestrgenstat

    @genericStirrupEntryMode.setter
    def genericStirrupEntryMode (self, iestrgenstat):
        """
        Modo de definição de estribo genérico:\n
            ICPEGPONTOSLONG:   Pontos longitudinais\n
            ICPEGPONTOSSECA:   Pontos da seção longitudinal\n
            ICPEGPONTOSEXTR:   Pontos externos
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        pariestrgenstat = ctypes.c_int (iestrgenstat)
        self.m_dwg.m_ipofer.IPOFER_IESTRGENSTAT (ctypes.byref (parferobjv), 
                                                 ctypes.byref (pariestrgenstat))

    @property
    def genericStirrupLongDiameter (self):
        """
        Bitola longitudinal mm de referência para a definição dos pontos
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        bitlnest        = 0.
        parbitlnest     = ctypes.c_double (bitlnest)
        self.m_dwg.m_ipofer.IPOFER_LER_BITLESTRGEN (ctypes.byref (parferobjv), 
                                                    ctypes.byref (parbitlnest))
        bitlnest        = parbitlnest.value
        return          bitlnest

    @genericStirrupLongDiameter.setter
    def genericStirrupLongDiameter (self, bitlnest):
        """
        Bitola longitudinal mm de referência para a definição dos pontos
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parbitlnest     = ctypes.c_double (bitlnest)
        self.m_dwg.m_ipofer.IPOFER_BITLESTRGEN (ctypes.byref (parferobjv), 
                                                ctypes.byref (parbitlnest))

    def GenericStirrupPoint (self, xlong, ylong):
        """
        Entrada de um ponto de estribo genérico\n
            - Os pontos são fornecidos no centro da armadura longitudinal\n
            - A bitola de armadura longitudinal é definida por genericStirrupLongDiameter\n
            - No estribo fechado, não fornecer o último ponto
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parxlong       = ctypes.c_double (xlong)
        parylong       = ctypes.c_double (ylong)
        self.m_dwg.m_ipofer.IPOFER_PTESTRGEN (ctypes.byref (parferobjv), 
                         ctypes.byref (parxlong), ctypes.byref (parylong))

    @property
    def circularStirrupRadius (self):
        """
        Raio de estribo circular, cm
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        raioestr        = 0.
        parraioestr     = ctypes.c_double (raioestr)
        self.m_dwg.m_ipofer.IPOFER_LER_RAIOESTR (ctypes.byref (parferobjv), 
                                                 ctypes.byref (parraioestr))
        raioestr        = parraioestr.value
        return          raioestr

    @circularStirrupRadius.setter
    def circularStirrupRadius (self, raioestr):
        """
        Raio de estribo circular, cm
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parraioestr     = ctypes.c_double (raioestr)
        self.m_dwg.m_ipofer.IPOFER_RAIOESTR (ctypes.byref (parferobjv), 
                                             ctypes.byref (parraioestr))

    def StirrupAdditionalCriteria (self, compradgra, igrasck83, igrak77):
        """
        Diversos critérios que modificam o grampo de pilar\n
            compradgra:   Somar valor em cm ao comprimento do grampo de pilar\n
            igrasck83:    Desenho de grampo (0) em S ou (1) C\n
            igrak77:      (1) Soma duas bitolas ao compr de grampo
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parcompradgra  = ctypes.c_double (compradgra)
        parigrasck83   = ctypes.c_int (igrasck83)
        parigrak77     = ctypes.c_int (igrak77)
        self.m_dwg.m_ipofer.IPOFER_COMPRADGRA (ctypes.byref (parferobjv), 
                       ctypes.byref (parcompradgra), ctypes.byref (parigrasck83),
                       ctypes.byref (parigrak77))


    def _LerDadGrampo (self):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        igrdir         = 0
        grclong        = 0.
        grctran        = 0.
        parigrdir      = ctypes.c_int (igrdir)
        pargrclong     = ctypes.c_double (grclong)
        pargrctran     = ctypes.c_double (grctran)
        self.m_dwg.m_ipofer.IPOFER_LER_DADGRAMPO (ctypes.byref (parferobjv),
                         ctypes.byref (parigrdir), ctypes.byref (pargrclong),
                         ctypes.byref (pargrctran))
        igrdir         = parigrdir.value
        grclong        = pargrclong.value
        grctran        = pargrctran.value
        return         igrdir, grclong, grctran

    def _DefDadGrampo (self, igrdir, grclong, grctran):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parigrdir      = ctypes.c_int (igrdir)
        pargrclong     = ctypes.c_double (grclong)
        pargrctran     = ctypes.c_double (grctran)
        self.m_dwg.m_ipofer.IPOFER_DADGRAMPO (ctypes.byref (parferobjv),
                         ctypes.byref (parigrdir), ctypes.byref (pargrclong),
                         ctypes.byref (pargrctran))

    @property
    def crosstiesDirection (self):
        """
        Direção do grampo de vigas (1) esquerda (-1) direita
        """
        igrdir, grclong, grctran = self._LerDadGrampo ()
        return          igrdir

    @crosstiesDirection.setter
    def crosstiesDirection (self, igrdir):
        """
        Direção do grampo de vigas (1) esquerda (-1) direita
        """
        igrdir2, grclong, grctran = self._LerDadGrampo ()
        self._DefDadGrampo (igrdir, grclong, grctran)

    @property
    def crosstiesLongLength (self):
        """
        Comprimento longitudinal do grampo de vigas, em cm
        """
        igrdir, grclong, grctran = self._LerDadGrampo ()
        return          grclong

    @crosstiesLongLength.setter
    def crosstiesLongLength (self, grclong):
        """
        Comprimento longitudinal do grampo de vigas, em cm
        """
        igrdir, grclong2, grctran = self._LerDadGrampo ()
        self._DefDadGrampo (igrdir, grclong, grctran)

    @property
    def crosstiesTransvLength (self):
        """
        Comprimento transversal do grampo de vigas, em
        """
        igrdir, grclong, grctran = self._LerDadGrampo ()
        return          grctran

    @crosstiesTransvLength.setter
    def crosstiesTransvLength (self, grctran):
        """
        Comprimento transversal do grampo de vigas, em
        """
        igrdir, grclong, grctran2 = self._LerDadGrampo ()
        self._DefDadGrampo (igrdir, grclong, grctran)

    def RebarTextDisplaySelection (self, iflnfr, iflpos, iflbit, iflesp, iflcmp, ialign, ibreak):
        """
        Seleciona os textos de identificação a serem mostrados\n
           iflnfr         <- (1) Número de ferros\n
           iflpos         <- (1) Número da posição\n
           iflbit         <- (1) Bitola\n
           iflesp         <- (1) Espaçamento\n
           iflcmp         <- (1) Comprimento\n
           ialign         <- Alinhamento:\n
                               ICPCENTR_CENTRAD: Centrado\n
                               ICPCENTR_ESQUERD: Esquerda\n
                               ICPCENTR_DIREITA: Direita\n
           ibreak         <- Salto de linha:\n
                               ICPQUEBR_SEMQUEBRA: Sem quebra\n
                               ICPQUEBR_SALTOCBCI: Salto C/ ou C=\n
                               ICPQUEBR_SALTOBITO: Salto {\n
                               ICPQUEBR_SALTODECD: Salto após C/\n
                               ICPQUEBR_SALTONPOS: Salto número de ferros
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        pariflnfr      = ctypes.c_int (iflnfr)
        pariflpos      = ctypes.c_int (iflpos)
        pariflbit      = ctypes.c_int (iflbit)
        pariflesp      = ctypes.c_int (iflesp)
        pariflcmp      = ctypes.c_int (iflcmp)
        paricentr      = ctypes.c_int (ialign)
        pariquebr      = ctypes.c_int (ibreak)
        self.m_dwg.m_ipofer.IPOFER_ARM_LAJMNTX (ctypes.byref (parferobjv),
            ctypes.byref (pariflnfr), ctypes.byref (pariflpos), ctypes.byref (pariflbit), 
            ctypes.byref (pariflesp), ctypes.byref (pariflcmp), ctypes.byref (paricentr), 
            ctypes.byref (pariquebr))

    def RebarTextDisplayPosition (self, xtex, ytex, htex, angle, imod, ialign, ibreak):
        """
        Fornece a posição e formatação do texto de identificação\n
            xtex      <- Coordenadas do texto\n
            ytex      <- Coordenadas do texto\n
            htex      <- Altura de texto cm plotados\n
            angle     <- Ângulo do texto em graus\n
            imod      <- (0) normal\n
                         (1) bit/espac para tabela var\n
                         (2) posição\n
                         (3) posição centrada, levant circ\n
            ialign    <- Alinhamento:\n
                               ICPCENTR_CENTRAD: Centrado\n
                               ICPCENTR_ESQUERD: Esquerda\n
                               ICPCENTR_DIREITA: Direita\n
            ibreak    <- Salto de linha:\n
                               ICPQUEBR_SEMQUEBRA: Sem quebra\n
                               ICPQUEBR_SALTOCBCI: Salto C/ ou C=\n
                               ICPQUEBR_SALTOBITO: Salto {\n
                               ICPQUEBR_SALTODECD: Salto após C/\n
                               ICPQUEBR_SALTONPOS: Salto número de ferros
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parxtex        = ctypes.c_double (xtex)
        parytex        = ctypes.c_double (ytex)
        parhtex        = ctypes.c_double (htex)
        parangle       = ctypes.c_double (angle)
        parimod        = ctypes.c_int (imod)
        paricentr      = ctypes.c_int (ialign)
        pariquebr      = ctypes.c_int (ibreak)
        self.m_dwg.m_ipofer.IPOFER_ARM_TEXTOFER (ctypes.byref (parferobjv),
            ctypes.byref (parxtex), ctypes.byref (parytex), ctypes.byref (parhtex), 
            ctypes.byref (parangle), ctypes.byref (parimod), ctypes.byref (paricentr), 
            ctypes.byref (pariquebr))


    def __LerChamAuto (self):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parilinchamauto= ctypes.c_int (0)
        pardistchamauto= ctypes.c_double (0.)
        self.m_dwg.m_ipofer.IPOFER_LER_CHAMAUTO (ctypes.byref (parferobjv),     \
                ctypes.byref (parilinchamauto), ctypes.byref (pardistchamauto))
        ilinchamauto   = parilinchamauto.value
        distchamauto   = pardistchamauto.value
        return          ilinchamauto, distchamauto

    def __DefChamAuto (self, ilinchamauto, distchamauto):
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parilinchamauto= ctypes.c_int (ilinchamauto)
        pardistchamauto= ctypes.c_double (distchamauto)
        self.m_dwg.m_ipofer.IPOFER_CHAMAUTO (ctypes.byref (parferobjv),     \
                        parilinchamauto, pardistchamauto)

    @property
    def leaderLine (self):
        """
        Textos de identificação afastados da linha de ferro podem ter\n
        linha de chamada apontado para o ferro gerada automaticamente.\n
        Defina se quer ou não a linha de chamada:\n
            ( 0)  Não coloca linha de chamada\n
            ( 1)  Será gerada acima da distância definida em leaderLineDistance\n
        """
        ilinchamauto, distchamauto = self.__LerChamAuto ()
        return          ilinchamauto

    @leaderLine.setter
    def leaderLine (self, leaderline):
        """
            ( 0)  Não coloca linha de chamada\n
            ( 1)  Será gerada acima da distância definida em leaderLineDistance\n
        """
        ilinchamauto, distchamauto = self.__LerChamAuto ()
        self.__DefChamAuto (leaderline, distchamauto)

    @property
    def leaderLineDistance (self):
        """
        Distância mínima, em cm de plotagem, do texto identificador para \n
        que a linha de chamada seja gerada.
        """
        ilinchamauto, distchamauto = self.__LerChamAuto ()
        return          distchamauto

    @leaderLineDistance.setter
    def leaderLineDistance (self, leaderlinedistance):
        """
        Distância mínima, em cm de plotagem, do texto identificador para \n
        que a linha de chamada seja gerada.
        """
        ilinchamauto, distchamauto = self.__LerChamAuto ()
        self.__DefChamAuto (ilinchamauto, leaderlinedistance)

    def VariableRebarContoursInit (self):
        """
        Inicializa contornos para a definição de ferros variáveis.
        """
        self.m_dwg.m_ipofer.IPOFER_ARM_INITRNSFP ()

    def VariableRebarOneContourInit (self):
        """
        Inicializa o contorno atual para a definição de ferros variáveis. 
        """
        self.m_dwg.m_ipofer.IPOFER_ARM_TRNSFP_INI ()

    def VariableRebarOneContourPoint (self, x, y):
        """
        Entra um ponto no contorno atual para ferros variáveis.
        """
        parx           = ctypes.c_double (x)
        pary           = ctypes.c_double (y)
        self.m_dwg.m_ipofer.IPOFER_ARM_TRNSFP_ENTRARCOORD (ctypes.byref (parx), 
                                                           ctypes.byref (pary))

    def VariableRebarOneContourEnd (self):
        """
        Finaliza a entrada de pontos no contorno atual para ferros variáveis.
        """
        self.m_dwg.m_ipofer.IPOFER_ARM_TRNSFP_FIM ()

    def VariableRebarMainSegIndex (self, idobravar):
        """
        Define o índice da dobra variável (dobras numeradas a partir de zero).
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paridobravar   = ctypes.c_int (idobravar)
        self.m_dwg.m_ipofer.IPOFER_FERVAR_IDOBRAVAR (ctypes.byref (parferobjv),
                         ctypes.byref (paridobravar))

    def VariableRebarGenerate (self, icfes1, angdist, scale):
        """
        Geração automática de ferros variáveis.\n
        icfes1     <- Número de ferros distribuídos\n
                        ICPE1P: Espaçamentos + 1 ferro\n
                        ICPE1M: Espaçamentos - 1 ferro\n
                        ICPESP: Espaçamentos = Núm de ferros\n
        angdist    <- Ângulo em graus da faixa de distribuição ortogonal ao ferro\n
        scale      <- Escala de inserção\n
        Retorna:\n
        xins       -> Posição X média de inserção do ferro\n
        yins       -> Posição  y inserção ferro médio\n
        meanLength -> Compr do ferro médio cm\n
        angle      -> Ângulo graus do ferro\n
        istat      -> (0) Ok\n
                      (1) Contorno inválido\n
                      (2) O número gerado não bate com o número de espaçamentos\n
                      (3) Espaçamento zero
        """
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        paricfes1      = ctypes.c_int    (icfes1)
        parangdist     = ctypes.c_double (angdist)
        parscale       = ctypes.c_double (scale)
        xins           = 0.
        yins           = 0.
        meanLength     = 0.
        angle          = 0.
        istat          = 0
        parxins        = ctypes.c_double (xins)
        paryins        = ctypes.c_double (yins)
        parmeanLength  = ctypes.c_double (meanLength)
        parangle       = ctypes.c_double (angle)
        paristat       = ctypes.c_int    (istat)
        self.m_dwg.m_ipofer.IPOFER_ARM_FERVAR (ctypes.byref (parferobjv),
            ctypes.byref (paricfes1), ctypes.byref (parangdist), 
            ctypes.byref (parscale), ctypes.byref (parxins), ctypes.byref (paryins), 
            ctypes.byref (parmeanLength), ctypes.byref (parangle), ctypes.byref (paristat))
        xins           = parxins.value
        yins           = paryins.value
        meanLength     = parmeanLength.value
        angle          = parangle.value
        istat          = paristat.value
        return         xins, yins, meanLength, angle, istat


    def VariableRebarQuantity (self):
        """
        Retorna o número de ferros variáveis gerados
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        numfer         = 0
        parnumfer      = ctypes.c_int (numfer)
        self.m_dwg.m_ipofer.IPOFER_ARM_FERVARNUM (ctypes.byref (parferobjv), 
                        ctypes.byref (parnumfer))
        numfer         = parnumfer.value
        return         numfer

    def VariableRebarScheduleInsert (self, xins, yins):
        """
        Insere tabela de ferros variável no desenho
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parxins        = ctypes.c_double (xins)
        paryins        = ctypes.c_double (yins)
        self.m_dwg.m_ipofer.IPOFER_ARM_TABVAR (ctypes.byref (parferobjv),
                        ctypes.byref (parxins), ctypes.byref (paryins))

    def VariableStirrupGenerate (self):
        """
        Gera a lista de comprimentos variáveis de estribos.\n
            - Somente estribos retangulares\n
            - Somente na largura ou altura\n
            - Variação entre cfeb e cfeb2 ou cfeh e cfeh2\n
            - Se ambos zerados, elimina variação de comprimentos\n
            - A quantidade de ferros é calculada pela faixa ou por número fixo\n
            - Se não tem faixa definida, icfes1==ICPE1P
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        self.m_dwg.m_ipofer.IPOFER_FERVAR_GERARESTR (
                       ctypes.byref (parpedmv), ctypes.byref (parferobjv))


    def RebarDistrQuant (self, icfes1, distrLength, spacing):
        """
        Cálculo do número de ferros dado comprimento da faixa e espaçamento. \n
        Conforme critério de espaçamento\n
        icfes1:      <- Número de ferros em função dos espaçamentos\n
                        ICPE1P:  Espaçamentos + 1 ferro\n
                        ICPE1M:  Espaçamentos - 1 ferro\n
                        ICPESP:  Espaçamentos = número de ferros\n
        distrLength: <- Comprimento da faixa de distribuição, cm\n
        spacing:     <- Espaçamento da faixa de distribuição, cm\n

        Retorna:
            iquant   -> Número de ferros calculado
            istat    -> (!=0) se spacing==0.
        """
        paricfes1      = ctypes.c_int (icfes1)
        pardistrLength = ctypes.c_double (distrLength)
        parspacing     = ctypes.c_double (spacing)
        iquant         = 0
        pariquant      = ctypes.c_int (iquant)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.IPOFER_ARM_CALNFR (ctypes.byref (paricfes1), 
            ctypes.byref (pardistrLength), ctypes.byref (parspacing), 
            ctypes.byref (pariquant), ctypes.byref (paristat))
        iquant          = pariquant.value
        istat           = paristat.value
        return          iquant, istat


    def RebarDistrAdd (self, icfes1, angdist, xpt1, ypt1, xpt2, ypt2, xcot, ycot, 
        ifdcotc, iflnfr, iflpos, iflbit, iflesp, ialign, ibreak, ordem, k32vigas, 
        k41vigas, ilinexten, ilinchama, itpponta, spacing, scale):
        """
        Adiciona uma faixa de distribuição ao ferro. \n
        Temos dois tipos de faixas de distribuição:\n
        (a) Embutida em um ferro. Um ferro pode ter várias faixas.\n
            Não é usada em pilares. Uma faixa pertence a um ferro.\n
        (b) Independente do ferro. Uma faixa pode ter vários ferros\n
            Usadas em pilares, onde estribos e grampos partilham faixa única.\n
            Uma faixa é definida primeiro como um ferro tipo ICPFAIMUL. Depois\n
            são definidos os dados de faixas (RebartDistAdd) e depois associados \n
            os ferros ligados à faixa através da rotina RebarDistrLink.\n
        Uma vez que um ferro tem uma ou mais faixas associadas, o número de ferros \n
        passa a ser calculado pela soma dos ferros das faixas.\n
        icfes1:      <- Número de ferros em função dos espaçamentos\n
                        ICPE1P:  Espaçamentos + 1 ferro\n
                        ICPE1M:  Espaçamentos - 1 ferro\n
                        ICPESP:  Espaçamentos = número de ferros\n
        angdist      <- Ângulo em graus da faixa de distribuição ortogonal ao ferro\n
        xpt1         <- Pt1 X\n
        ypt1         <- Pt1 Y\n
        xpt2         <- Pt2 X\n
        ypt2         <- Pt2 Y\n
        xcot         <- X de passagem da linha de cotagem\n
        ycot         <- Y de passagem da linha de cotagem\n
        ifdcotc      <- (1) p/cotar compr da faixa\n
        iflnfr       <- (1) descrever número de ferros\n
        iflpos       <- (1) descrever número da posição\n
        iflbit       <- (1) descrever bitola\n
        iflesp       <- (1) descrever espaçamento\n
        ialign       <- Alinhamento ICPCENTR_xxxxxxx\n
        ibreak       <- Salto de linha ICPQUEBR_xxxxxxxxx\n
        ordem        <- Ordem dos textos ("" padrão)\n
                     "N" Número de ferros\n
                     "n" só o número\n
                     "M" só o multiplicador\n
                     "P" Posição\n
                     "B" Bitola\n
                     "E" Espaçamento\n
                     "C" Comprimento\n
                     "F" Comprimento de faixa\n
        k32vigas     <- Critério K32 CAD/Vigas p/m_ordem==""\n
        k41vigas     <- Critério K41 CAD/Vigas p/m_ordem==""\n
                     (0) não cotar faixa (1) cotar (2) cota e altera Pn\n
        ilinexten    <- (1) linha de extensão automática\n
        ilinchama    <- (1) se linha de chamada\n
        itpponta     <- (0) flexa (1) círculo (2) traço\n
        spacing      <- Espaçamento cm se diferente do ferro\n
        scale        <- Escala de inserção (multiplica todas as dimensões)
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paricfes1      = ctypes.c_int    (icfes1)
        parangdist     = ctypes.c_double (angdist)
        parxpt1        = ctypes.c_double (xpt1)
        parypt1        = ctypes.c_double (ypt1)
        parxpt2        = ctypes.c_double (xpt2)
        parypt2        = ctypes.c_double (ypt2)
        parxcot        = ctypes.c_double (xcot)
        parycot        = ctypes.c_double (ycot)
        parifdcotc     = ctypes.c_int    (ifdcotc)
        pariflnfr      = ctypes.c_int    (iflnfr)
        pariflpos      = ctypes.c_int    (iflpos)
        pariflbit      = ctypes.c_int    (iflbit)
        pariflesp      = ctypes.c_int    (iflesp)
        parialign      = ctypes.c_int    (ialign)
        paribreak      = ctypes.c_int    (ibreak)
        parordem       = ctypes.c_char_p (ordem.encode(TQS.TQSUtil.CHARSET))
        parargfan      = ctypes.c_int    (0)
        park32vigas    = ctypes.c_int    (k32vigas)
        park41vigas    = ctypes.c_int    (k41vigas)
        parilinexten   = ctypes.c_int    (ilinexten)
        parilinchama   = ctypes.c_int    (ilinchama)
        paritpponta    = ctypes.c_int    (itpponta)
        parspacing     = ctypes.c_double (spacing)
        parscale       = ctypes.c_double (scale)
        self.m_dwg.m_ipofer.IPOFER_FAIXADIST (ctypes.byref (parferobjv), ctypes.byref (paricfes1),  
            ctypes.byref (parangdist), ctypes.byref (parxpt1), ctypes.byref (parypt1), 
            ctypes.byref (parxpt2), ctypes.byref (parypt2), ctypes.byref (parxcot), 
            ctypes.byref (parycot), ctypes.byref (parifdcotc), ctypes.byref (pariflnfr), 
            ctypes.byref (pariflpos), ctypes.byref (pariflbit), ctypes.byref (pariflesp), 
            ctypes.byref (parialign), ctypes.byref (paribreak), parordem, parargfan, 
            ctypes.byref (park32vigas), ctypes.byref (park41vigas), ctypes.byref (parilinexten), 
            ctypes.byref (parilinchama), ctypes.byref (paritpponta), ctypes.byref (parspacing), 
            ctypes.byref (parscale))


    def RebarDistrLink (self, rebar):
        """
        Associa um ferro handleRebar à faixa múltipla, que é o objeto atual
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        handleRebar    = rebar.handle_rebar;
        parhandleRebar = ctypes.c_void_p (handleRebar)
        self.m_dwg.m_ipofer.IPOFER_ASSOCFAIXAMULT  (ctypes.byref (parferobjv),
            ctypes.byref (parhandleRebar))


    def GetRebarDistrNum (self):
        """
        Retorna o número de faixas de distribuição
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        numfaixas       = 0
        parnumfaixas    = ctypes.c_int (numfaixas)
        self.m_dwg.m_ipofer.IPOFER_LER_NUMFAIXAS (ctypes.byref (parferobjv), 
                            ctypes.byref (parnumfaixas))
        numfaixas       = parnumfaixas.value
        return          (numfaixas)


    def GetRebarDistrInfo (self, ifaixa):
        """
        Retorna dados de uma faixa de distribuição ifaixa == 0..GetRebarDistrNum()-1\n
        Retorna:\n
        icfes1          Número de ferros distribuídos\n
        angfai          Ângulo da faixa de distribuição sistema global\n
        xpt1            Pt1 X\n
        ypt1            Pt1 Y\n
        xpt2            Pt2 X\n
        ypt2            Pt2 Y\n
        xcot            X de passagem da linha de cotagem\n
        ycot            Y de passagem da linha de cotagem\n
        ifdcotc         (1) p/cotar compr da faixa\n
        iflnfr          (1) descrever número de ferros\n
        iflpos          (1) descrever número da posição\n
        iflbit          (1) descrever bitola\n
        iflesp          (1) descrever espaçamento\n
        icentr          Alinhamento ICPCENTR_xxxxxxx\n
        iquebr          Salto de linha ICPQUEBR_xxxxxxxxx\n
        ordem           Ordem dos textos ("" padrão)\n
                         "N" Número de ferros\n
                         "n" só o número\n
                         "M" só o multiplicador\n
                         "P" Posição\n
                         "B" Bitola\n
                         "E" Espaçamento\n
                         "C" Comprimento\n
                         "F" Comprimento de faixa\n
        k32vigas        Critério K32 CAD/Vigas p/m_ordem==""\n
                        (0) K32=0 (1) K32=1 (2) K32=2\n
        k41vigas        Critério K41 CAD/Vigas p/m_ordem==""\n
                        (0) ñ cotar faixa (1) cotar (2) cota+muda Pn\n
        ilinexten       (1) linha de extensão automática\n
        ilinchama       (1) se linha de chamada\n
        itpponta        (0) flexa (1) círculo (2) traço\n
        espac           Espaçamento cm se dif do ferro\n
        escxy           Escala de inser (multipl dimens)
        """
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parifaixa       = ctypes.c_int (ifaixa)
        icfes1          = 0
        paricfes1       = ctypes.c_int (icfes1)
        angfai          = 0.
        parangfai       = ctypes.c_double (angfai)
        xpt1            = 0.
        parxpt1         = ctypes.c_double (xpt1)
        ypt1            = 0.
        parypt1         = ctypes.c_double (ypt1)
        xpt2            = 0.
        parxpt2         = ctypes.c_double (xpt2)
        ypt2            = 0.
        parypt2         = ctypes.c_double (ypt2)
        xcot            = 0.
        parxcot         = ctypes.c_double (xcot)
        ycot            = 0.
        parycot         = ctypes.c_double (ycot)
        ifdcotc         = 0
        parifdcotc      = ctypes.c_int (ifdcotc)
        iflnfr          = 0
        pariflnfr       = ctypes.c_int (iflnfr)
        iflpos          = 0
        pariflpos       = ctypes.c_int (iflpos)
        iflbit          = 0
        pariflbit       = ctypes.c_int (iflbit)
        iflesp          = 0
        pariflesp       = ctypes.c_int (iflesp)
        icentr          = 0
        paricentr       = ctypes.c_int (icentr)
        iquebr          = 0
        pariquebr       = ctypes.c_int (iquebr)
        parordem        = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan         = ctypes.c_int (0)
        k32vigas        = 0
        park32vigas     = ctypes.c_int (k32vigas)
        k41vigas        = 0
        park41vigas     = ctypes.c_int (k41vigas)
        ilinexten       = 0
        parilinexten    = ctypes.c_int (ilinexten)
        ilinchama       = 0
        parilinchama    = ctypes.c_int (ilinchama)
        itpponta        = 0
        paritpponta     = ctypes.c_int (itpponta)
        espac           = 0.
        parespac        = ctypes.c_double (espac)
        escxy           = 0.
        parescxy        = ctypes.c_double (escxy)
        self.m_dwg.m_ipofer.IPOFER_LER_FAIXADIST (ctypes.byref (parferobjv), 
                            ctypes.byref (parifaixa), ctypes.byref (paricfes1),  
                            ctypes.byref (parangfai), ctypes.byref (parxpt1), ctypes.byref (parypt1), 
                            ctypes.byref (parxpt2), ctypes.byref (parypt2), ctypes.byref (parxcot), 
                            ctypes.byref (parycot), ctypes.byref (parifdcotc), ctypes.byref (pariflnfr), 
                            ctypes.byref (pariflpos), ctypes.byref (pariflbit), ctypes.byref (pariflesp), 
                            ctypes.byref (paricentr), ctypes.byref (pariquebr), parordem, argfan, 
                            ctypes.byref (park32vigas), ctypes.byref (park41vigas), 
                            ctypes.byref (parilinexten), ctypes.byref (parilinchama), 
                            ctypes.byref (paritpponta), ctypes.byref (parespac), 
                            ctypes.byref (parescxy))
        icfes1          = paricfes1.value
        angfai          = parangfai.value
        xpt1            = parxpt1.value
        ypt1            = parypt1.value
        xpt2            = parxpt2.value
        ypt2            = parypt2.value
        xcot            = parxcot.value
        ycot            = parycot.value
        ifdcotc         = parifdcotc.value
        iflnfr          = pariflnfr.value
        iflpos          = pariflpos.value
        iflbit          = pariflbit.value
        iflesp          = pariflesp.value
        icentr          = paricentr.value
        iquebr          = pariquebr.value
        ordem           = parordem.value.decode(TQS.TQSUtil.CHARSET)
        k32vigas        = park32vigas.value
        k41vigas        = park41vigas.value
        ilinexten       = parilinexten.value
        ilinchama       = parilinchama.value
        itpponta        = paritpponta.value
        espac           = parespac.value
        escxy           = parescxy.value
        return          icfes1, angfai, xpt1, ypt1, xpt2, ypt2, xcot, ycot, ifdcotc, iflnfr, \
                        iflpos, iflbit, iflesp, icentr, iquebr, ordem, k32vigas, k41vigas, \
                        ilinexten, ilinchama, itpponta, espac, escxy


    def DimRebarEndPoint (self, insindex, idimpoint, xpt, ypt):
        """
        Cotagem de uma ponta de ferro, com o índice (0..n-1) da linha do ferro.\n
        Um ferro pode ter mais de uma linha definida.\n
            insindex   <- Índice da da linha a cotar (0..)\n
            idimpoint  <- (0)Não (1)cotar 1o ponto (2)cotar pontos 1 e 2\n
            xpt        <- X\n
            ypt        <- Y
        """
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        parinsindex    = ctypes.c_int    (insindex)
        paridimpoint   = ctypes.c_int    (idimpoint)
        parxpt         = ctypes.c_double (xpt)
        parypt         = ctypes.c_double (ypt)
        self.m_dwg.m_ipofer.IPOFER_ENTRARPTCOT (ctypes.byref (parferobjv), 
            ctypes.byref (parinsindex), ctypes.byref (paridimpoint), 
            ctypes.byref (parxpt), ctypes.byref (parypt))

    def RebarMarkIdentify (self, imultiple, xtex, ytex, iflnfr, iflpos, iflbit, iflesp):
        """
        Identificação de uma posição de ferro. Uma ou mais linhas de chamada com \n
        um texto de descrição de ferro. Cada chamada a RebarMarkIdentify\n
        cria uma nova identificação. As chamadas RebarMarkIdentifyPoint em seguida \n
        se referen à última identificação criada.\n
            10 P1                   10 P1\n
              +    2+-->3         + + + + \n
              |    /             /  |  \\ \\\n
              +---+             /   |   \\  \\\n
              0   1             0   1    2    3\n
         (imultiple == 0)      (imultiple == 1)\n
             imultiple <- (0) polig+flexa (1) múltiplas lin\n
             xtex      <- Posição do texto de identificação\n
             ytex      <- Posição do texto de identificação\n
             iflnfr    <- (1) descrever número de ferros\n
             iflpos    <- (1) descrever número da posição\n
             iflbit    <- (1) descrever bitola\n
             iflesp    <- (1) descrever espaçamento
        """
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        parimultiple   = ctypes.c_int    (imultiple)
        parxtex        = ctypes.c_double (xtex)
        parytex        = ctypes.c_double (ytex)
        pariflnfr      = ctypes.c_int    (iflnfr)
        pariflpos      = ctypes.c_int    (iflpos)
        pariflbit      = ctypes.c_int    (iflbit)
        pariflesp      = ctypes.c_int    (iflesp)
        self.m_dwg.m_ipofer.IPOFER_IDENTPOS (ctypes.byref (parferobjv), 
            ctypes.byref (parimultiple), ctypes.byref (parxtex), ctypes.byref (parytex), 
            ctypes.byref (pariflnfr), ctypes.byref (pariflpos), ctypes.byref (pariflbit), 
            ctypes.byref (pariflesp)) 

    def RebarMarkIdentifyPoint (self, xid, yid):
        """
        Entra novo ponto de linha cotagem. O primeiro está na posição de texto.
        """
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        parxid         = ctypes.c_double (xid)
        paryid         = ctypes.c_double (yid)
        self.m_dwg.m_ipofer.IPOFER_IDENTPOS_ENTRARPT (ctypes.byref (parferobjv), 
            ctypes.byref (parxid), ctypes.byref (paryid))

    def AdditionalLineInit (self, inivel, iestilo, icor):
        """
        Abre linha adicional de ferro. Os pontos serão definidos por AdditionalLineInitPoint.\n
        Para abrir nova linha, chame novamente esta rotina.\n
            inivel     <- Nível  EAG (-1) default\n
            iestilo    <- Estilo EAG (-1) default\n
            icor       <- Cor    EAG (-1) default
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        parinivel      = ctypes.c_int  (inivel)
        pariestilo     = ctypes.c_int  (iestilo)
        paricor        = ctypes.c_int  (icor)
        self.m_dwg.m_ipofer.IPOFER_LINADICINICIAR (ctypes.byref (parferobjv), 
            ctypes.byref (parinivel), ctypes.byref (pariestilo), ctypes.byref (paricor)) 

    def AdditionalLineInitPoint (self, xpt, ypt, zpt, iarco):
        """
        Entra ponto na linha adicional aberta.\n
            xpt        <- X\n
            ypt        <- Y\n
            zpt        <- Z\n
            iarco      <- (1) se centro de arco
        """
        parferobjv     = ctypes.c_void_p   (self.m_ferobjv)
        parxpt         = ctypes.c_double (xpt)
        parypt         = ctypes.c_double (ypt)
        parzpt         = ctypes.c_double (zpt)
        pariarco       = ctypes.c_int    (iarco)
        self.m_dwg.m_ipofer.IPOFER_LINADICENTRARPT (ctypes.byref (parferobjv),
            ctypes.byref (parxpt), ctypes.byref (parypt), ctypes.byref (parzpt),
            ctypes.byref (pariarco))


    def DeepCopy (self):
        """
        Retorna uma cópia SmartRebar do objeto atual
        """
        rebardest       = SmartRebar (self.m_dwg)
        parferobjv      = ctypes.c_void_p (self.m_ferobjv)
        parferobjvdest  = ctypes.c_void_p (rebardest.m_ferobjv)
        self.m_dwg.m_ipofer.IPOFER_COPIARDADOSFERRO (ctypes.byref (parferobjv),
            ctypes.byref (parferobjvdest))
        return            rebardest

    def InUse (self):
        """
        Retorna !=0 se a posição do ferro está em uso por outro ferro
        """
        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        inUse          = 0
        parinuse       = ctypes.c_int (inUse)
        self.m_dwg.m_ipofer.IPOFER_POS_EMUSO (ctypes.byref (parpedmv),
            ctypes.byref (parferobjv), ctypes.byref (parinuse))
        inUse          = parinuse.value
        return         inUse

    def RebarScheduleNumDescr (self):
        """
        Retorna o número de descrições de um ferro. Estribos podem gerar duas
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        numdescr       = 0
        parnumdescr    = ctypes.c_int (numdescr)
        self.m_dwg.m_ipofer.IPOFER_EXTTAB_NUMDESCR (ctypes.byref (parferobjv), 
            ctypes.byref (parnumdescr))
        numdescr       = parnumdescr.value
        return         numdescr

    def RebarScheduleInfo (self, idescr):
        """
        Entra idescr - o número da descrição de 0..RebarScheduleNumDescr()-1\n
        Retorna informações de extração de tabela\n
        ipos           Número da posição\n
        bitola         Bitola mm\n
        nfer           Número de ferros\n
        mult           Multiplicador de ferrros\n
        itpcorbar      Tipo de ferro CORBAR\n
        ivar           (1) Se ferro variável\n
        rdval          Raio de dobra\n
        rddsc          Deconto total raio de dobra\n
        compr          Comprimento total sem desconto\n
        igane          Gnch esq ICPSGA/ICP090/ICP135/ICP180\n
        igand          Gnch dir ICPSGA/ICP090/ICP135/ICP180\n
        observ         Observ c/delim\n
        ilance         Lance de pilar\n
        itipo99        (1) Se ferro tipo 99 é estribo\n
        icftppata      Pata de estribo ICPTPPATA45/90\n
        icorrido       (1) Ferro corrido\n
        iluvai         (1) Luva inicial\n
        iluvaf         (1) Luva final
        """
        ipos           = 0
        bitola         = 0.
        nfer           = 0
        mult           = 0
        itpcorbar      = 0
        ivar           = 0
        rdval          = 0.
        rddsc          = 0.
        compr          = 0.
        igane          = 0
        igand          = 0
        observ         = ""
        ilance         = 0
        itipo99        = 0
        icftppata      = 0
        icorrido       = 0
        iluvai         = 0
        iluvaf         = 0

        parpedmv       = ctypes.c_void_p (self.m_dwg.m_pedmv)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        paridescr      = ctypes.c_int    (idescr)
        paripos        = ctypes.c_int    (ipos)
        parbitola      = ctypes.c_double (bitola)
        parnfer        = ctypes.c_int    (nfer)
        parmult        = ctypes.c_int    (mult)
        paritpcorbar   = ctypes.c_int    (itpcorbar)
        parivar        = ctypes.c_int    (ivar)
        parrdval       = ctypes.c_double (rdval)
        parrddsc       = ctypes.c_double (rddsc)
        parcompr       = ctypes.c_double (compr)
        parigane       = ctypes.c_int    (igane)
        parigand       = ctypes.c_int    (igand)
        parobserv      = ctypes.create_string_buffer (TQS.TQSUtil.MAXNCSTR)
        argfan         = ctypes.c_int    (0)
        parilance      = ctypes.c_int    (ilance)
        paritipo99     = ctypes.c_int    (itipo99)
        paricftppata   = ctypes.c_int    (icftppata)
        paricorrido    = ctypes.c_int    (icorrido)
        pariluvai      = ctypes.c_int    (iluvai)
        pariluvaf      = ctypes.c_int    (iluvaf)
        self.m_dwg.m_ipofer.IPOFER_EXTTAB_LERFER (ctypes.byref (parpedmv),
            ctypes.byref (parferobjv), ctypes.byref (paridescr), ctypes.byref (paripos), 
            ctypes.byref (parbitola), ctypes.byref (parnfer), ctypes.byref (parmult), 
            ctypes.byref (paritpcorbar), ctypes.byref (parivar), ctypes.byref (parrdval), 
            ctypes.byref (parrddsc), ctypes.byref (parcompr), ctypes.byref (parigane), 
            ctypes.byref (parigand), parobserv, argfan, ctypes.byref (parilance), 
            ctypes.byref (paritipo99), ctypes.byref (paricftppata), ctypes.byref (paricorrido), 
            ctypes.byref (pariluvai), ctypes.byref (pariluvaf))
        ipos           = paripos.value
        bitola         = parbitola.value
        nfer           = parnfer.value
        mult           = parmult.value
        itpcorbar      = paritpcorbar.value
        ivar           = parivar.value
        rdval          = parrdval.value
        rddsc          = parrddsc.value
        compr          = parcompr.value
        igane          = parigane.value
        igand          = parigand.value
        observ         = parobserv.value.decode(TQS.TQSUtil.CHARSET)
        ilance         = parilance.value
        itipo99        = paritipo99.value
        icftppata      = paricftppata.value
        icorrido       = paricorrido.value
        iluvai         = pariluvai.value
        iluvaf         = pariluvaf.value
        return         ipos, bitola, nfer, mult, itpcorbar, ivar, rdval, rddsc, compr, igane, igand, observ, ilance, itipo99, icftppata, icorrido, iluvai, iluvaf

    def ResetTextPosition (self):
        """
        Reposiciona os textos identificadores do ferro em posição padrão
        """
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        self.m_dwg.m_ipofer.IPOFER_POSICOESPADRAO (ctypes.byref (parferobjv))
#
#       Operações geométricas com ferros
#
    def Move (self, dx, dy):
        """
        Mover um ferro
        dx:             <- Deslocamento X cm
        dy:             <- Deslocamento Y cm
        """
        parpedmv        = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pvistav         = None
        parpvistav      = ctypes.c_void_p (pvistav)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        vardx           = ctypes.c_double (dx)
        vardy           = ctypes.c_double (dy)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.OBJDWG_MOVER (parpedmv, parpvistav, parferobjv, vardx, vardy, \
                            ctypes.byref (paristat))
        istat           = paristat.value


    def Rotate (self, cx, cy, ang):
        """
        Rodar um ferro
        cx:             <- Centro de rotação X cm
        cy:             <- Centro de rotação Y cm
        ang:            <- Ângulo de rotação graus antihorário
        """
        parpedmv        = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pvistav         = None
        parpvistav      = ctypes.c_void_p (pvistav)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        varcx           = ctypes.c_double (cx)
        varcy           = ctypes.c_double (cy)
        varang          = ctypes.c_double (ang)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.OBJDWG_RODAR (parpedmv, parpvistav, parferobjv, 
                            varcx, varcy, varang, ctypes.byref (paristat))


    def Scale (self, cx, cy, escala):
        """
        Escalar um ferro
        cx:             <- Centro de escala X cm
        cy:             <- Centro de escala Y cm
        escala:         <- Valor da escala
        """
        parpedmv        = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pvistav         = None
        parpvistav      = ctypes.c_void_p (pvistav)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        varcx           = ctypes.c_double (cx)
        varcy           = ctypes.c_double (cy)
        varescala       = ctypes.c_double (escala)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.OBJDWG_ESCALAR (parpedmv, parpvistav, parferobjv, 
                            varcx, varcy, varescala, ctypes.byref (paristat))


    def Mirror (self, x1, y1, x2, y2):
        """
        Espelhar um ferro
        x1:             <- Linha de espelho PT 1 cm
        y1:             <- Linha de espelho PT 1 cm
        x2:             <- Linha de espelho PT 2 cm
        y2:             <- Linha de espelho PT 2 cm
        """
        parpedmv        = ctypes.c_void_p (self.m_dwg.m_pedmv)
        pvistav         = None
        parpvistav      = ctypes.c_void_p (pvistav)
        parferobjv     = ctypes.c_void_p (self.m_ferobjv)
        varx1           = ctypes.c_double (x1)
        vary1           = ctypes.c_double (y1)
        varx2           = ctypes.c_double (x2)
        vary2           = ctypes.c_double (y2)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_dwg.m_ipofer.OBJDWG_ESPELHAR (parpedmv, parpvistav, parferobjv, 
                            varx1, vary1, varx2, vary2, ctypes.byref (paristat))


