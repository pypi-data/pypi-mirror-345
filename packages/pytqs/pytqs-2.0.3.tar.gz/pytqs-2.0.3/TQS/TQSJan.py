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
#    TQSJan.PY         Módulo para mostrar desenhos TQS em uma janela Windows
#-----------------------------------------------------------------------------
import math
import ctypes
import TQS.TQSUtil
import TQS.TQSDwg

#-----------------------------------------------------------------------------
#    Constantes de VISTA.H
#
VIS_DESEN              = 0        # Display e desenho
VIS_DESENNAO           = 1        # Display sem desenho

VIS_DLEXISTE           = 0        # criar e usar display list
VIS_DLINATIVA          = 1        # nao existe displau list

VIS_DLINS              = 0        # Insere na display list
VIS_DLDEL              = 1        # Deleta da display list
VIS_DLIGNORE           = 2        # Nao insere na display list

VIS_DISPORI            = 0        # Desenhar na cor original
VIS_DISPFOR            = 1        # Desenhar na cor fornecida
VIS_DISPAPAG           = 2        # Desenhar apagando
VIS_DISPXOR            = 3        # Desenhar em XOR
VIS_DISPNAO            = 4        # Nao desenhar

VIS_SISLOC             = 0        # Sistema local normal
VIS_SISGIR             = 1        # Sistema local a 90^

VIS_TABPLT             = 0        # Usa tabela de plotagem
VIS_TABNAO             = 1        # Nao usa tabela de plotagem

VIS_TEXLENTO           = 0        # texto lento
VIS_TEXRAPIDO          = 1        # texto rapido

VIS_CURLENTA           = 0        # curva lenta
VIS_CURRAPIDA          = 1        # curva rapida

VIS_GRADESEM           = 0        # Se grade
VIS_GRADECOM           = 1        # Com grade

VIS_IACEND             = 0        # Acende elemento
VIS_IAPAGA             = 1        # Apaga  elemento
VIS_INVERT             = (-1)     # Inverte elemento

VIS_BLONAO             = 0        # Display normal
VIS_BLOSIM             = 1        # Display exclusivo de um bloco

COR_PRETA              = 0        # Cor padrão EAG 0..255
COR_VERMELHA           = 1        # Cor padrão EAG 0..255
COR_AMARELA            = 2        # Cor padrão EAG 0..255
COR_VERDE              = 3        # Cor padrão EAG 0..255
COR_AZULCLARA          = 4        # Cor padrão EAG 0..255
COR_AZULESCURA         = 5        # Cor padrão EAG 0..255
COR_ROXA               = 6        # Cor padrão EAG 0..255
COR_BRANCA             = 7        # Cor padrão EAG 0..255
COR_CINZA              = 8        # Cor padrão EAG 0..255
COR_VERMELHAFRACA      = 9        # Cor padrão EAG 0..255
COR_MARROM             = 10       # Cor padrão EAG 0..255
COR_VERDEFRACA         = 11       # Cor padrão EAG 0..255
COR_AZULCLARAFRACA     = 12       # Cor padrão EAG 0..255
COR_AZULESCURAFRACA    = 13       # Cor padrão EAG 0..255
COR_ROXAFRACA          = 14       # Cor padrão EAG 0..255
COR_BRANCAFRACA        = 15       # Cor padrão EAG 0..255
COR_MAXCORES           = (COR_BRANCAFRACA+1)

VIS_STL_CONTINUO       = 0        # ___________
VIS_STL_TRACO          = 1        # _ _ _ _ _ _
VIS_STL_PONTO          = 2        # . . . . . .
VIS_STL_TRACOPONTO     = 3        # _ . _ . _ .
VIS_STL_TRACOPONTOPONTO= 4        # _ . . _ . .
VIS_STL_MINITRACO      = 5        # - - - - - -

RUB_LINEAR             = 0        # Rubberband linear
RUB_RETANG             = 1        # Rubberband retangular
RUB_NAO                = 2        # Sem rubberband
RUB_PANDIN             = 3        # Caso particular: pan dinamico

RUBRET_NAOPREEN        = 0        # Não preenche rubber retangular
RUBRET_JANW            = 1        # Preenche como janela W
RUBRET_JANC            = 2        # Preenche como janela C
RUBRET_JANUSR          = 3        # Preenche como W (direita) ou C (esquerda)

INP_ENTER              = 0        # apertou ENTER
INP_ESCAPE             = 1        # apertou ESCAPE
INP_MOUSE              = 2        # Botao do mouse
INP_TECLA              = 3        # Uma tecla
INP_MOVE               = 4        # O mouse simplesmente se moveu
#-----------------------------------------------------------------------------
class Window ():

    KEY_F8             = 347
    KEY_F9             = 348
    KEY_F10            = 349
    KEY_F11            = 350
    KEY_SHIFT          = 306
    KEY_ALT            = 307
    KEY_CTRL           = 308

    def __init__ (self, hwnd, dwg, pvistav=None):
        """
        Inicialização - dois modos:\n
        Window (hwnd, dwg) - Dado que existe DWG e Janela aberta, cria objeto\n
        Window (None, None, pvistav) - A vista já existe, obtém objeto
        """
        self.m_pvistav   = 0
        self.m_acessol  = TQS.TQSUtil.LoadDll ("ACESSOL.DLL")
        self.m_eagvista = TQS.TQSUtil.LoadDll ("EAGVISTA.DLL")
        self.m_entr     = TQS.TQSUtil.LoadDll ("EAGENTRD.DLL")
        self.m_eagpar   = TQS.TQSUtil.LoadDll ("EAGPAR.DLL")
        self.m_acessol.ACL_INIACESSO ()
        if              pvistav is None:
            self.m_eagvista.vis_inicia ()
            self.m_entr.inp_inicia ()
            self.m_hWnd     = hwnd
            self.m_dwg      = dwg
            self._CreateView()
        else:
            self.m_pvistav  = pvistav
            parpvistav     = ctypes.c_void_p (self.m_pvistav)
            self.m_hWnd     = 0
            parhwnd         = ctypes.c_void_p (self.m_hWnd)
            pedmv           = 0
            parpedmv       = ctypes.c_void_p (pedmv)
            self.m_eagvista.vis_lerhandles (parpvistav, ctypes.byref(parhwnd), ctypes.byref(parpedmv))
            self.m_hWnd     = parhwnd.value
            pedmv           = parpedmv.value
            self.m_dwg      = TQS.TQSDwg.Dwg (pedmv)

        self._LimparBotoes ()
        self._iortogonal = 0
#
#    Limpa botões para interepretar KeyDown
#
    def _LimparBotoes (self):
        self.m_ikey_ishif   = 0
        self.m_ikey_alt     = 0
        self.m_ikey_ctrl    = 0

#
#    Criacao da vista default englobando o desenho atual
#
    def _CreateView (self):
        self.m_dwg.limits.UpdateLimits ()
        xmin, ymin, xmax, ymax = self.m_dwg.limits.DwgLimits ()
        deltax          = (xmax - xmin) * 0.05
        deltay          = (ymax - ymin) * 0.05
        npsuav          = 0
        isuprdata       = 0
        parnpsuav       = ctypes.c_int (npsuav)
        parisuprdata    = ctypes.c_int (isuprdata)
        self.m_eagpar.plotdes_lerparam (ctypes.byref(parnpsuav), ctypes.byref(parisuprdata))
        icorfund        = 0
        paricorfund     = ctypes.c_int (icorfund)
        self.m_eagpar.eagpar_lercorfund (ctypes.byref(paricorfund))
        parhwnd         = ctypes.c_void_p (self.m_hWnd)
        paridlist       = ctypes.c_int (VIS_DLINATIVA)
        parpvistav      = ctypes.c_void_p (self.m_pvistav)
        self.m_eagvista.vis_inijan (parhwnd, paridlist, parnpsuav, paricorfund,
                            ctypes.byref (parpvistav))
        self.m_pvistav   = parpvistav.value
        parpedmv        = ctypes.c_void_p (self.m_dwg.settings.handle_pedmv)
        parxmin         = ctypes.c_double (xmin - deltax)
        parymin         = ctypes.c_double (ymin - deltay)
        parxmax         = ctypes.c_double (xmax + deltax)
        parymax         = ctypes.c_double (ymax + deltay)
        self.m_eagvista.vis_defjan (parpvistav, parpedmv, parxmin, parymin, parxmax, parymax)

#------------------------------------------------------------------------------
#    Métodos e propriedades
#
    @property
    def dwg (self):
        """
        Retorna objeto Dwg() associado à esta vista
        """
        return         self.m_dwg

    def DestroyView (self):
        """
        Destroi e desaloca vista
        """
        if             self.m_pvistav != None:
            parpvistav  = ctypes.c_void_p (self.m_pvistav)
            self.m_eagvista.vis_fimjan (parpvistav)
        self.m_pvistav = None
        self.vis_fim   ()


    def ChangeDwg (self, dwg):
        """
        Alterar o DWG associado a uma janela
        """
        self.m_dwg      = dwg
        if             self.m_pvistav != None:
            parpvistav  = ctypes.c_void_p (self.m_pvistav)
            self.m_eagvista.vis_fimjan (parpvistav)
        _CreateView (self)


    def SetWindow (self, xmin, ymin, xmax, ymax):
        """
        Define a janela atual
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parpedmv       = ctypes.c_void_p (self.m_dwg.settings.handle_pedmv)
        parxmin        = ctypes.c_double (xmin)
        parymin        = ctypes.c_double (ymin)
        parxmax        = ctypes.c_double (xmax)
        parymax        = ctypes.c_double (ymax)
        self.m_eagvista.vis_defjan (parpvistav, parpedmv,
             parxmin, parymin, parxmax, parymax)

    def GetWindow (self):
        """
        Retorna xmin, ymin, xmax, ymax da janela atual
        """
        xmin           = 0.
        ymin           = 0.
        xmax           = 0.
        ymax           = 0.
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parxmin        = ctypes.c_double (xmin)
        parymin        = ctypes.c_double (ymin)
        parxmax        = ctypes.c_double (xmax)
        parymax        = ctypes.c_double (ymax)
        self.m_eagvista.vis_lerjan (parpvistav, ctypes.byref (parxmin),
             ctypes.byref (parymin), ctypes.byref (parxmax), ctypes.byref (parymax))
        xmin           = parxmin.value
        ymin           = parymin.value
        xmax           = parxmax.value
        ymax           = parymax.value
        return         xmin, ymin, xmax, ymax

    def WorldToScreen (self, x, y):
        """
        Converte coordenadas x,y do mundo real para coordenadas de tela.
        Retorna ix,iy
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parx           = ctypes.c_double (x)
        pary           = ctypes.c_double (y)
        ix             = 0
        iy             = 0
        parix          = ctypes.c_int (ix)
        pariy          = ctypes.c_int (iy)
        self.m_eagvista.vis_wndwts (parpvistav, parx, pary, ctypes.byref (parix),
                                    ctypes.byref (pariy))
        ix             = parix.value
        iy             = pariy.value
        return         ix, iy

    def ScreenToWorld (self, ix, iy):
        """
        Converte coordenadas ix,iy de tela para coordenadas do mundo real.\n
        Retorna x,y
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parix          = ctypes.c_int (ix)
        pariy          = ctypes.c_int (iy)
        x              = 0.
        y              = 0.
        parx           = ctypes.c_double (x)
        pary           = ctypes.c_double (y)
        self.m_eagvista.vis_wndstw (parpvistav, parix, pariy, ctypes.byref (parx),
                                    ctypes.byref (pary))
        x             = parx.value
        y             = pary.value
        return         x, y


    def Regen (self):
        """
        Regera o desenho na janela windows
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        self.m_eagvista.vis_viregn (parpvistav)


    def Window2P (self, x1, y1, x2, y2):
        """
        Redefine a janela atual do desenho por 2 pontos
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        self.m_eagvista.vis_vijanl2p (parpvistav, parx1, pary1, parx2, pary2)

    def WindowScale (self, scale):
        """
        Redefine a janela atual afastando por uma escala
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parscale       = ctypes.c_double (scale)
        self.m_eagvista.vis_vizom2 (parpvistav, parscale)

    def WindowPan (self, vx, vy):
        """
        Movimenta a janela atual por um vetor
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parx1          = ctypes.c_double (0.)
        pary1          = ctypes.c_double (0.)
        parx2          = ctypes.c_double (vx)
        pary2          = ctypes.c_double (vy)
        self.m_eagvista.vis_vipan2p (parpvistav, parx1, pary1, parx2, pary2)

    def GetPoint (self):
        """
        Retorna x,y,istat de um ponto
        istat != 0 se o usuário apertou <Esc>
        """
        x, y, istat    = self._PrimPonto (0)
        return         x, y, istat


    def GetPointRubberBand (self, x1, y1):
        """
        Retorna x,y,istat de um ponto, ligando linha elástica com x1,y1\n
        istat != 0 se o usuário apertou <Esc>
        """
        x2, y2, istat  = self._SeguPonto (x1, y1, RUB_LINEAR)
        return         x2, y2, istat


    @property
    def orthogonal (self):
        """
        Modo ortogonal (1) ou normal (0)
        """
        return             self._iortogonal

    @orthogonal.setter
    def orthogonal (self, iorto):
        """
        Modo ortogonal (1) ou normal (0)
        """
        self._iortogonal   = iorto


#
#    Entra o primeiro ponto de 2 pedindo para o usuario (imod=0) ou
#    na posicao atual do cursor (imod=1)
#    Retorna x,y,istat
#
    def _PrimPonto (self, imod, posxy = [0., 0.]):
        if             imod != 0:
            x, y       = self.ScreenToWorld (posxy [0], posxy [1])
            return     x, y, 0
        irub           = RUB_NAO
        iortogonal     = 0
        x1             = 0.
        y1             = 0.
        x2             = 0.
        y2             = 0.
        itpmsg         = 0
        imudou         = 0
        ibotao         = 0
        nclient        = 0

        parpvistav     = ctypes.c_void_p   (self.m_pvistav)
        parirub        = ctypes.c_int    (irub)
        pariortogonal  = ctypes.c_int    (iortogonal)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        paritpmsg      = ctypes.c_int    (itpmsg)
        parimudou      = ctypes.c_int    (imudou)
        paribotao      = ctypes.c_int    (ibotao)
        parnclient     = ctypes.c_int    (nclient)
        self.m_entr.inp_getptpar (parpvistav, parirub, pariortogonal, parx1, pary1,
            ctypes.byref(parx2), ctypes.byref(pary2), ctypes.byref(paritpmsg),
            ctypes.byref(parimudou), ctypes.byref(paribotao), ctypes.byref(parnclient))
        x2             = parx2.value
        y2             = pary2.value
        itpmsg         = paritpmsg.value
        imudou         = parimudou.value
        ibotao         = paribotao.value
        nclient        = parnclient.value
        if             imudou != 0:
             return    0., 0, 1
        return         x2, y2, 0


    def _SeguPonto (self, x1, y1, irub):
#
#    Pega o segundo ponto, com rubberband linear ou retangular
#    Retorna x,y,istat
#
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parirub        = ctypes.c_int    (irub)
        pariortogonal  = ctypes.c_int  (self._iortogonal)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        x2             = 0.
        y2             = 0.
        itpmsg         = 0
        imudou         = 0
        ibotao         = 0
        nclient        = 0
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        paritpmsg      = ctypes.c_int    (itpmsg)
        parimudou      = ctypes.c_int    (imudou)
        paribotao      = ctypes.c_int    (ibotao)
        parnclient     = ctypes.c_int    (nclient)
        self.m_entr.inp_getptpar (parpvistav, parirub, pariortogonal,
            parx1, pary1, ctypes.byref(parx2), ctypes.byref(pary2),
            ctypes.byref(paritpmsg), ctypes.byref(parimudou),
            ctypes.byref(paribotao), ctypes.byref(parnclient))
        x2             = parx2.value
        y2             = pary2.value
        itpmsg         = paritpmsg.value
        imudou         = parimudou.value
        ibotao         = paribotao.value
        nclient        = parnclient.value
        if             itpmsg != INP_MOUSE or imudou != 0 or ibotao != 1 or nclient != 0:
            return     0., 0., 1
        if             self._iortogonal != 0:
            if         math.fabs (x2 - x1) > math.fabs (y2 - y1):
                y2     = y1
            else:
                x2     = x1
        return         x2, y2, 0


    def Zoom2P (self, imod, posxy=[0.,0.]):
        """
        Janela por 2 pontos\n
        imod == (0) 2 pontos (1) cursor + segundo ponto\n
        posxy = [x, y] primeiro ponto para imod == 1
        """
        x1, y1, istat  = self._PrimPonto (imod, posxy)
        if             istat != 0:
            return
        x2, y2, istat  = self._SeguPonto (x1, y1, RUB_RETANG)
        if             istat != 0:
            return
        parpvistav     = ctypes.c_void_p   (self.m_pvistav)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        self.m_eagvista.vis_vijanl2p (parpvistav, parx1, pary1, parx2, pary2)

    def ZoomTotal (self):
        """
        Zoom total do desenho atual
        """
        self.m_dwg.limits.UpdateLimits ()
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        self.m_eagvista.vis_viengl (parpvistav)

    def ZoomPan (self, imod, irub, posxy=[0.,0.]):
        """
        Faz Pan com 1 ou 2 pontos:\n
        imod    (0) Lê do usuário (1) usa posxy\n
        irub    RUB_LINEAR, RUB_RETANG, RUB_NAO, RUB_PANDIN\n
        posxy   [ix, iy] Posição do cursos na janela
        """
        x1, y1, istat = self._PrimPonto (imod, posxy)
        if      istat != 0:
            return
        x2, y2, istat = self._SeguPonto (x1, y1, irub)
        if      istat != 0:
            return
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parx1          = ctypes.c_double (x1)
        pary1          = ctypes.c_double (y1)
        parx2          = ctypes.c_double (x2)
        pary2          = ctypes.c_double (y2)
        self.m_eagvista.vis_vipan2p (parpvistav, parx1, pary1, parx2, pary2)


    def ZoomOut (self):
        """
        Afasta a visualização por um fator de escala de 0.5
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        scale          = 0.5
        parscale       = ctypes.c_double (scale)
        self.m_eagvista.vis_vizom2 (parpvistav, parscale)


    def ZoomPrevious (self):
        """
        Mostra a janela anterior\n
        Retorna istat != 0 se não há mais janelas
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        istat          = 0
        paristat       = ctypes.c_int (istat)
        self.m_eagvista.vis_vijant (parpvistav, ctypes.byref(paristat))
        istat          = paristat.value
        return         istat

#------------------------------------------------------------------------------
#    Eventos
#
    def OnPaint (self, hdc):
        """
        Regera o desenho na janela windows em um evento PAINT
        """
        parpvistav     = ctypes.c_void_p (self.m_pvistav)
        parhdc         = ctypes.c_void_p (hdc)
        self.m_eagvista.vis_inidc (parpvistav, parhdc)
        self.m_eagvista.vis_viregndc (parpvistav)
        self.m_eagvista.vis_fimdc (parpvistav)


    def OnSize (self, cx, cy):
        """
        Chamar quando a janela mudar de tamanho
        """
        if             self.m_pvistav != None:
            parpvistav  = ctypes.c_void_p (self.m_pvistav)
            self.m_eagvista.vis_resizejan (parpvistav)


    def OnKey (self, ikeycode, posxy):
        """
        Processa eventos EVT_KEY_DOWN (wxPython) com GetKeyCode\n
        <F8>          Janela por 2 pontos\n
        <Shift> <F8>  Janela total\n
        <Ctrl>  <F8>  Janela anterior\n
        <Alt>   <F8>  Deslocamento de janela\n
        <F11>         Zoom out\n
        <F10>         Liga/desliga ortogonal
        """
        if             ikeycode == Window.KEY_F8:
            if         self.m_ikey_ishif != 0:
                self.ZoomTotal ()
                self._LimparBotoes ()

            elif       self.m_ikey_alt != 0:
                self.ZoomPan (1, RUB_LINEAR, posxy)
                self._LimparBotoes ()

            elif       self.m_ikey_ctrl != 0:
                self.ZoomPrevious ()
                self._LimparBotoes ()

            else:
                self.Zoom2P (1, posxy)
                self._LimparBotoes ()

        elif           ikeycode == Window.KEY_F10:
            self.orthogonal = 1 - self.orthogonal
        elif           ikeycode == Window.KEY_F11:
            self.ZoomOut ()
            self._LimparBotoes ()

        elif           ikeycode == Window.KEY_SHIFT:
            self.m_ikey_ishif = 1
        elif           ikeycode == Window.KEY_ALT:
            self.m_ikey_alt   = 1
        elif           ikeycode == Window.KEY_CTRL:
            self.m_ikey_ctrl    = 1


    def OnMouseMiddle (self, posxy):
        """
        Trata botão do meio do mouse
        """
        self.ZoomPan   (1, RUB_PANDIN, posxy)



    def OnWheel (self, idelta, posxy):
        """
        Processa N deslocamentos do rolete do mouse
        """

        FATROSCA       = 1.1;                    # Zoom por passo
        escala         = FATROSCA ** float (-idelta)
        xmin, ymin, xmax, ymax = self.GetWindow ()
        xp, yp         = self.ScreenToWorld (posxy [0], posxy [1])
        xmin           = xp + (xmin - xp)*escala
        ymin           = yp + (ymin - yp)*escala
        xmax           = xp + (xmax - xp)*escala
        ymax           = yp + (ymax - yp)*escala
        self.SetWindow (xmin, ymin, xmax, ymax)
        self.Regen     ()

