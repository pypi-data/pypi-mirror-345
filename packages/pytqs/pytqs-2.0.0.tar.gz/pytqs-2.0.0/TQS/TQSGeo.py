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
#    TQSGeo.PY    27-10-2020 Rotinas de geometria analítica
#-----------------------------------------------------------------------------
import math
import tkinter.messagebox
import TQS.TQSUtil

#-----------------------------------------------------------------------------
#   Algumas constantes
#
glb_delprec     = 0.001            # precisão para igualar 2 pontos    
glb_delang      = 0.001            # precisão para igualar ângulos    
glb_delgeoint    = 0.01            # tolerância de arctangente em geoint

#-----------------------------------------------------------------------------
def SetPrecision (delx):
    """
    Define a precisão para igualar pontos
    """
    global             glb_delprec
    glb_delprec        = delx

def SetAnglePrecision (delx):
    """
    Define a precisão para igualar ângulos
    """
    global             glb_delang
    glb_delang         = delx


def Equals (x1, y1, x2, y2):
    """
    Retorna (1) se 2 pontos iguais dentro da precisão
    """
    global             glb_delprec
    if                 math.fabs (x1 - x2) < glb_delprec and math.fabs (y1 - y2) < glb_delprec:
        return         1
    else:
        return         0

def Distance (x1, y1, x2, y2):
    """
    Retorna a distância entre dois pontos
    """
    return             math.sqrt ((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))

def LineCoefficients (x1, y1, x2, y2):
    """
    Retorna os coeficientes a,b,c da reta 1-2
    """
    a                  = y2 - y1
    b                  = x1 - x2
    c                  = x2*y1 - x1*y2
    return             a, b, c

def DistancePointLine (x1line, y1line, x2line, y2line, xpoint, ypoint):
    """
    Retorna a distância entre uma reta e um ponto
    """
    a, b, c            = LineCoefficients (x1line, y1line, x2line, y2line)
    div                = math.sqrt (a*a + b*b)
    global             glb_delprec
    if                 math.fabs (div) < glb_delprec:
        return         0.
    dpr                = math.fabs (a*xpoint + b*ypoint + c)/div
    return            dpr


def Angle2p (x1, y1, x2, y2):
    """
    Ângulo entre 2 pontos 0..360 graus
    """
    global             glb_delprec
    global             glb_delang
    if                 math.fabs (x2 - x1) + math.fabs (y2 - y1) < glb_delprec:
        return         0.
    if                 math.fabs (x2 - x1)  > glb_delprec:
        ang            = math.atan ((y2-y1) / (x2-x1))
    else:
        if              y2 > y1:
            ang        = TQS.TQSUtil.PI / 2.
        else:
            ang        = -TQS.TQSUtil.PI / 2.
    
    if                 ang < -glb_delang:
        if             y2 > y1:
            ang        = ang + TQS.TQSUtil.PI
    elif               ang > glb_delang:
        if             y2 < y1:
            ang        = ang + TQS.TQSUtil.PI
    else:
        if             x2 < x1:
            ang        = ang + TQS.TQSUtil.PI
   
    if                 ang < 0.:
        ang            = ang + 2.*TQS.TQSUtil.PI
    elif               ang > 2.*TQS.TQSUtil.PI:
        ang            = ang - 2.*TQS.TQSUtil.PI
  
    return             ang*180./TQS.TQSUtil.PI


def Angle2r (x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Ângulo entre as retas 1-2 e 3-4 0..180 graus
    """
    global             glb_delprec
    ang                = TQS.TQSUtil.PI
    ux                 = x2 - x1
    uy                 = y2 - y1
    umod               = Distance (x1, y1, x2, y2)
    if                 math.fabs (umod) < glb_delprec:
        return         ang*180./TQS.TQSUtil.PI
    
    vx                 = x4 - x3
    vy                 = y4 - y3
    vmod               = Distance (x3, y3, x4, y4)
    if                 math.fabs (vmod) < glb_delprec:
        return         ang*180./TQS.TQSUtil.PI

    arco               = (ux*vx + uy*vy) / (umod*vmod)
    if                 arco >  1.:
        arco           = 1.
    if                 arco < -1.:
        arco           = -1.
    ang                = math.acos (arco)

    return             ang*180./TQS.TQSUtil.PI

def NormalizeAngle (angle):
    """
    Retorna um ângulo normalizado entre 0 e 360 graus
    """
    global             glb_delang
    while              angle < 0.:
        angle          += 360.
    while              angle > 360.:
        angle          -= 360.
    if                 math.fabs (angle - 360.) < glb_delang:
        angle          = 0.
    return             angle

def _VerificarVetoresIguais (vecx, vecy):
    if                 len (vecx) != len (vecy) or len (vecx) == 0:
        tkinter.messagebox.showerror(title="Vetores vecx e vecy de dimensões diferentes",
                                         message="TQSGeo")
        return         1
    else:
        return         0

def Area (vecx, vecy):
    """
    Área dos vetores vecx[] e vecy [] com sinal
    """

    if                 _VerificarVetoresIguais (vecx, vecy):
        return

    area               = 0.
    npt                = len (vecx)
    if                npt == 0:
        return         0.
    x1                = vecx [0]
    y1                = vecy [0]
    npt               = len (vecx)
    for               i in range (0, npt):
        j             = i + 1
        if            j >= npt:
            j         = 0
        x2            = vecx [j]
        y2            = vecy [j]
        deltax        = x2 - x1
        area          = area + (y2 + y1)*deltax
        x1            = x2
        y1            = y2

    area              = area / 2.
    return            area

def Perimeter (vecx, vecy):
    """
    Perímetro de vecx[] e vecy []
    """
    if                 _VerificarVetoresIguais (vecx, vecy):
        return
    perim              = 0.
    npt                = len (vecx)
    if                 npt == 0:
        return         0.
    npt                = len (vecx)
    x1                 = vecx [0]
    y1                 = vecy [0]
    for                i in range (0, npt-1):
        j              = i + 1
        x2             = vecx [j]
        y2             = vecy [j]
        perim          += Distance (x1, y1, x2, y2)
        x1             = x2
        y1             = y2

    return             perim

def GravityCenter (vecx, vecy):
    """
    Retorna x,y do centro de gravidade e a área (com sinal) de vecx[] e vecy[]
    """
    if                 _VerificarVetoresIguais (vecx, vecy):
        return
    xgg                = 0.
    ygg                = 0.
    areac              = 0.
    xg                 = 0.
    yg                 = 0.
    area               = 0.
    npt                = len (vecx)
    if                 npt == 0:
        return         0., 0., 0.

    global             glb_delprec
    difx               = 0.
    dify               = 0.
    for                i in range (0, npt-1):
        difx           += math.fabs (vecx [i] - vecx [i+1])
        dify           += math.fabs (vecy [i] - vecy [i+1])

    if                 difx < glb_delprec or dify < glb_delprec:
        return         0., 0., 0.

    x1                 = vecx [0]
    y1                 = vecy [0]
    for                i in range (0, npt):
        j              = i + 1
        if             j >= npt:
            j          = 0
        x2             = vecx [j]
        y2             = vecy [j]
        deltax         = x2 - x1
        deltay         = y2 - y1
        arear          = y1    *deltax*0.5
        areat          = deltay*deltax*0.5
        area           = area   + (y2 + y1)*deltax
        xg             = xg     + (x1 + x2)*arear +  (x1 + 2./3.*deltax)*areat
        yg             = yg     +  y1      *arear +  (y1 + 1./3.*deltay)*areat
        x1             = x2
        y1             = y2

    area               = area / 2.
    if                 math.fabs (area) < glb_delprec:
        return
    xg                 = xg / area
    yg                 = yg / area
    areac              = area
    xgg                = xg
    ygg                = yg
    return             xgg, ygg, areac


def PointInSegment (x, y, x1, y1, x2, y2):
    """
    Retorna (1) se o ponto x,y, contido na reta 1-2, está contido no segmento de reta 1-2\n
    O ponto x,y é projetado em 1-2 antes do teste
    """
    global             glb_delprec
    x, y               = Projection (x1, y1, x2, y2, x, y)
    insegment          = 1
    if                 math.fabs (x-x1) < glb_delprec and math.fabs (y-y1) < glb_delprec:
        return         insegment
   
    if                 math.fabs (x-x2) < glb_delprec and math.fabs (y-y2) < glb_delprec:
        return         insegment

    dis1               = math.fabs (x2 - x1)
    dis2               = math.fabs (y2 - y1)
    if                 dis1 > dis2:
        if             dis1 < glb_delprec:
            insegment  = 0
        if            (x2 - x)*(x - x1) < 0:
            insegment  = 0
    else:
        if             dis2  < glb_delprec:
            insegment  = 0
        if             (y2-y) * (y-y1) < 0:
            insegment  = 0
   
    return             insegment


def IntersectionByCoefs (a, b, c, d, e, f):
    """
    Retorna x, y, istat da intersecção da reta 1 (coeficientes a,b e c) e\n
    a reta 2 (coeficientes d, e, f). istat != 0 se não houve intersecção.
    """
    global             glb_delgeoint
    x                  = 0.
    y                  = 0.
    istat              = 1
    d1                 = math.sqrt (a*a + b*b)
    d2                 = math.sqrt (d*d + e*e)
    if                 d1 == 0. or d2 == 0.:
        return         x, y, istat
    vx1                = b / d1
    vy1                = a / d1
    vx2                = e / d2
    vy2                = d / d2
    if                 math.fabs (vx1-vx2) < glb_delgeoint and math.fabs (vy1-vy2) < glb_delgeoint:
        return         x, y, istat
    if                 math.fabs (vx1+vx2) < glb_delgeoint and math.fabs (vy1+vy2) < glb_delgeoint:
        return         x, y, istat
    div                = e*a - d*b
    if                 div == 0.:
        return         x, y, istat
    x                  = (f*b -  c*e) / div
    y                  = (d*c  - f*a) / div
    istat              = 0
    return             x, y, istat

def Intersection2r (x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Retorna x, y, istat da intersecção da reta 1 (x1, y1, x2, y2) e\n
    a reta 2 (x3, y3, x4, y4). istat != 0 se não houve intersecção.
    """
    a, b, c            = LineCoefficients (x1, y1, x2, y2)
    d, e, f            = LineCoefficients (x3, y3, x4, y4)
    x, y, istat        = IntersectionByCoefs (a, b, c, d, e, f)
    return             x, y, istat


def IntersectionSegment (x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Retorna x, y, istat da intersecção da reta 1 (x1, y1, x2, y2) e\n
    a reta 2 (x3, y3, x4, y4). A intersecção tem que acontecer dentro\n
    dos segmentos 1-2 e 3-4. istat != 0 se não houve intersecção.
    """
    x, y, istat        = Intersection2r (x1, y1, x2, y2, x3, y3, x4, y4)
    if                 istat != 0:
        return         x, y, istat
    if                 not PointInSegment (x, y, x1, y1, x2, y2):
        return         x, y, 1
    if                 not PointInSegment (x, y, x3, y3, x4, y4):
        return         x, y, 1
    istat              = 0
    return             x, y, istat


def Projection (x1, y1, x2, y2, xp, yp):
    """
    Projeta o ponto xp,yp na reta 1-2. Retorna x,y, o ponto projetado
    """
    a, b, c            = LineCoefficients (x1, y1, x2, y2)
    d                  = -b
    e                  = a
    f                  = -d*xp -e*yp
    x, y, istat        = IntersectionByCoefs (a, b, c, d, e, f)
    if                 istat != 0:
        x              = xp
        y              = yp

    return             x, y

def ParallelPoint (x1, y1, x2, y2, dist):
    """
    Calcula o ponto P sobre uma reta ortogonal a 1-2 passando por 2 e uma \n
    distância positiva à direita de 1-2. Retorna o ponto xp,yp
    """
    vetmod             = Distance (x1, y1, x2, y2)
    global             glb_delprec
    if                 vetmod < glb_delprec:
        px             = x1
        py             = y1
    else:
        vx             = (y2 - y1)/vetmod
        vy             = (x1 - x2)/vetmod
        px             =  x2 + vx*dist
        py             =  y2 + vy*dist

    return             px, py

def ParallelLine (x1, y1, x2, y2, dist):
    """
    Calcula o a reta paralela a a 1-2 a uma distância positiva à direita de 1-2. \n
    Retorna a reta xp1, yp1, xp2, yp2
    """
    xp2, yp2           = ParallelPoint (x1, y1, x2, y2, dist)
    xp1, yp1           = ParallelPoint (x2, y2, x1, y1, -dist)
    return             xp1, yp1, xp2, yp2


def ParallelPolyline (vecx, vecy, dist):
    """
    Calcula paralela a vecx,vecy a uma distancia fornecida, positiva à direita das retas
    """
    if                 _VerificarVetoresIguais (vecx, vecy):
        return

    global             glb_delprec
    ifecha             = 0
    npt                = len (vecx)
    if                 math.fabs (vecx[0] - vecx[npt-1]) < glb_delprec and math.fabs (vecy[0] - vecy[npt-1]) < glb_delprec:
        ifecha         = 1
    xtrab1             = []    # matriz de trabalho p/paralelas     
    ytrab1             = []    # o trecho i e formado pelos pontos
    xtrab2             = []    # 1 inicial e 2 final
    ytrab2             = [] 
    for                i in range (0, npt-1):
        xtrab1.append  (vecx [i  ])
        ytrab1.append  (vecy [i  ])
        xtrab2.append  (vecx [i+1])
        ytrab2.append  (vecy [i+1])
   
    for                i in range (0, npt-1):
        x1, y1, x2, y2 = ParallelLine (xtrab1 [i], ytrab1 [i], xtrab2 [i], ytrab2 [i], dist)
        xtrab1 [i]     = x1
        ytrab1 [i]     = y1
        xtrab2 [i]     = x2
        ytrab2 [i]     = y2
   
    for                i in range (0, npt-1):
        j              = i - 1
        if             j < 0:
            j          = npt-2
        k              = i + 1
        if             k >= npt-1:
            k          = 0
        istat1         = 1
        istat2         = 1
        if             ifecha != 0 or i > 0:
            x1, y1, istat1 = Intersection2r (xtrab1 [j], ytrab1 [j], xtrab2 [j], ytrab2 [j],
                                             xtrab1 [i], ytrab1 [i], xtrab2 [i], ytrab2 [i])
        if             ifecha != 0 or  i < npt-2:
            x2, y2, istat2 =  Intersection2r (xtrab1 [i], ytrab1 [i], xtrab2 [i], ytrab2 [i],
                                              xtrab1 [k], ytrab1 [k], xtrab2 [k], ytrab2 [k])
        if             istat1 == 0:
            xtrab1 [i] = x1
            ytrab1 [i] = y1
        if             istat2 == 0:
            xtrab2 [i] = x2
            ytrab2 [i] = y2
   
    for                i in range (0, npt-1):
        vecx [i]       = xtrab1 [i]
        vecy [i]       = ytrab1 [i]
   
    vecx [npt-1]       = xtrab2 [npt-2]
    vecy [npt-1]       = ytrab2 [npt-2]


def Limits (vecx, vecy):
    """
    Retorna os limites xmin, ymin, xmax, ymax dos vetores vecx, vecy
    """
    if                 _VerificarVetoresIguais (vecx, vecy):
        return
    ambda             = 1.e32
    xmax               = -ambda
    ymax               = -ambda
    xmin               =  ambda
    ymin               =  ambda
    np                 = len (vecx)
    for                i in range (0, np):
        if            vecx [i] < xmin:
            xmin       = vecx [i]
        if            vecy [i] < ymin:
            ymin       = vecy [i]
        if            vecx [i] > xmax:
            xmax       = vecx [i]
        if            vecy [i] > ymax:
            ymax       = vecy [i]
    return             xmin, ymin, xmax, ymax


def VectorProduct (x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Retorna o produto vetorial do vetor 1-2 por 3-4
    """
    ux                 = x2 - x1
    uy                 = y2 - y1
    vx                 = x4 - x3
    vy                 = y4 - y3
    return             ux*vy - uy*vx

def PointProduct (x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Retorna o produto pontual do vetor 1-2 por 3-4
    """
    ux                 = x2 - x1
    uy                 = y2 - y1
    vx                 = x4 - x3
    vy                 = y4 - y3
    return             ux*vx + uy*vy

def Versor (x1, y1, x2, y2):
    """
    Retorna o versor vx,vy do vetor 1-2
    """
    dis                = Distance (x1, y1, x2, y2)
    global             glb_delprec
    if                 dis < glb_delprec:
        return         0., 0.
    vx                = (x2 - x1)/dis
    vy                = (y2 - y1)/dis
    return            vx, vy

def PointInArea (x, y, vecx, vecy):
    """
    Verifica se o ponto x,y esta dentro da poligonal vecx, vecy\n
    Retorna (1) se estiver.
    """
    inarea             = 0
    if                 _VerificarVetoresIguais (vecx, vecy):
        return         inarea

    xmin, ymin, xmax, ymax = Limits (vecx, vecy)
    global             glb_delprec
    delx                = glb_delprec
    inarea             = 0
    if                 x < xmin - delx or x > xmax + delx or y < ymin - delx or y > ymax + delx:
        return         inarea
    npc                = len (vecx)
    numtre             = npc-1
    if                 math.fabs (vecx [0] - vecx [numtre]) > delx or math.fabs (vecy [0] - vecy [numtre]) > delx:
        numtre         += 1
    angtot             = 0.
    for                i in range (0, numtre):
        x1             = vecx [i]
        y1             = vecy [i]
        if             i < npc-1:
            x2         = vecx [i+1]
            y2         = vecy [i+1]
        else:
            x2         = vecx [0]
            y2         = vecy [0]
        if             math.fabs(x-x1) < delx and math.fabs(y-y1) < delx:
            inarea     = 1
            return

        xp, yp         = Projection (x1, y1, x2, y2, x, y)
        if             Distance (x, y, xp, yp) < delx:
            if         PointInSegment (xp, yp, x1, y1, x2, y2):
                inarea = 1
                return inarea
        ang            = 180. - Angle2r (x1, y1, x, y, x, y, x2, y2)
        if             VectorProduct (x1, y1, x, y, x, y, x2, y2) > 0.:
            ang        = -ang
        angtot         = angtot + ang
   
    if                 math.fabs (math.fabs (angtot) - 360.) < delx:
        inarea         = 1
    else:
        inarea         = 0
  
    return             inarea


glb_a = 0.        # Usados no espelhamento
glb_b = 0.        # Usados no espelhamento
glb_c = 0.        # Usados no espelhamento
glb_d = 0.        # Usados no espelhamento
glb_e = 0.        # Usados no espelhamento

def MirrorInit (x1, y1, x2, y2):
    """
    Define a linha de espelhamento 1-2 que será usada pela função Mirror\n
    Retorna o ângulo original e o final de espelhamento da reta 1-2 em graus
    """
    global             glb_a, glb_b, glb_c, glb_d, glb_e
    glb_a, glb_b, glb_c = LineCoefficients (x1, y1, x2, y2)
    glb_d              = -glb_b
    glb_e              = glb_a
    angog              = Angle2p (x1, y1, x2, y2)
    angg               = 180. + 2.*angog
    angg               = NormalizeAngle (angg)
    return             angog, angg

def Mirror (xe, ye):
    """
    Retorna o ponto xe,ye espelhado pela linha definida em MirrorInit
    """
    global             glb_a, glb_b, glb_c, glb_d, glb_e
    x3                 = xe
    y3                 = ye;
    f		       = -glb_d*x3 -glb_e*y3
    x, y, istat        = IntersectionByCoefs (glb_a, glb_b, glb_c, glb_d, glb_e, f)
    if                 istat != 0:
        return         0., 0.
    xe                 = x3 + 2.*(x - x3)
    ye                 = y3 + 2.*(y - y3)
    return             xe, ye

def Rotate (x, y, ang, orgx, orgy):
    """
    Retorna o ponto x,y rodado por ang graus em torno de orgx,orgy
    """
    angr               = ang * TQS.TQSUtil.PI/180.
    xx                 = x - orgx
    yy                 = y - orgy
    cosang             = math.cos (angr)
    sinang             = math.sin (angr)
    x                  = orgx + xx*cosang - yy*sinang
    y                  = orgy + xx*sinang + yy*cosang
    return             x, y


