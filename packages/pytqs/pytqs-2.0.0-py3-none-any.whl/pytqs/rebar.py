
from __future__ import annotations
from TQS.TQSDwg import SmartRebar
from TQS import TQSDwg
from pygeometry2d import XY
from pytqs.drawning import TQSDrawning


class Rebar():
    """
    Classe auxiliar para armações no TQS.
    """
    #TQSDwg.ICPFRT - Ferro reto
    #TQSDwg.ICPFGN - Ferro genérico
    #TQSDwg.ICPSTR - Estribo
    #TQSDwg.ICPGRA - Grampo de vigas
    #TQSDwg.ICPSTRGEN - Estribo genérico, pilar
    #TQSDwg.ICPFAIMUL - Faixa múltipla – a ser associada com outros ferros

    #mark - Número da posição do ferro
    #quantity - Número de ferros
    #multiplier - Multiplicador de ferros
    #diameter - Bitola do ferro, mm
    #spacing - Espaçamento de ferros, cm
    #ribbed - (0) Em geral (1) Em lajes nervuradas
    #showRibbed - (0) Não (1) Mostrar status de laje nervurada (C/NERV)
    #comment - Comentário de um ferro (texto que aparece com a descrição do ferro)
    #leftHook - Tipo de gancho à esquerda, uma das constantes a seguir: TQSDwg.ICPSGA - Sem gancho; TQSDwg.ICP090 - Gancho a 90 graus; TQSDwg.ICP135 - Gancho a 135 graus; TQSDwg.ICP180 - Gancho a 180 graus.
    #leftHookInvert - (1) Gancho à esquerda invertido
    #rightHook - Tipo de gancho à direita, uma das constantes a seguir: TQSDwg.ICPSGA - Sem gancho; TQSDwg.ICP090 - Gancho a 90 graus; TQSDwg.ICP135 - Gancho a 135 graus; TQSDwg.ICP180 - Gancho a 180 graus.
    #rightHookInvert - (1) Gancho à direita invertido
    #columnLevel - Número de lance de pilar
    #cover - Cobrimento, cm. Usado para remontar estribos tipo ICPENR/ICPEFC/ICPEAB/ICPENC.

    def __init__(self, position: int, quantity: int, diameter: float, cover: float, spacing: float = 0, multiplier: int = 1):
        self.position = position
        self.quantity = quantity
        self.multiplier = multiplier
        self.diameter = diameter
        self.cover = cover
        self.spacing = spacing
        self.smart_rebar = None

    def round_spacing(self, distribution_length: float):
        self.spacing = min([10, 12, 14, 15, 16, 18, 20, 12.5, 9, 8, 22], key=lambda x: abs(x - distribution_length/(self.quantity - 1)))
    
    def __smart_rebar(self, dwg: TQSDrawning):
        self.smart_rebar = SmartRebar(dwg.dwg)
        self.smart_rebar.mark = self.position
        self.smart_rebar.quantity = self.quantity                 
        self.smart_rebar.multiplier = self.multiplier                 
        self.smart_rebar.diameter = self.diameter              
        self.smart_rebar.spacing = self.spacing                
        self.smart_rebar.cover = self.cover      
        self.smart_rebar.bendRadiusDisplay = TQSDwg.ICPMAN

    def to_straight_rebar (self, dwg: TQSDrawning, main_length: float, right_length: float = 0, left_length: float = 0, right_length2: float  = 0, left_length2: float = 0, zone: int = TQSDwg.ICPPOS, 
                        bend_type: int = TQSDwg.ICPNSU, text_direction: int = 0, text_position: int = 1, continuous: int = 0, mirror_mode: int = 1) -> Rebar:
        
        self.__smart_rebar(dwg)
        self.smart_rebar.type = TQSDwg.ICPFRT
        self.smart_rebar.straightBarMainLength = main_length
        self.smart_rebar.straightBarRightLength = right_length
        self.smart_rebar.straightBarLeftLength = left_length
        self.smart_rebar.straightBarRightLength2 = right_length2
        self.smart_rebar.straightBarLeftLength2 = left_length2
        self.smart_rebar.straightBarZone = zone # TQSDwg.ICPPOS -> Armadura positiva; TQSDwg.ICPNEG -> Armadura negativa
        self.smart_rebar.straightBarBendType = bend_type # TQSDwg.ICPNSU -> Dobra normal; TQSDwg.ICPDSU -> Dobra de suspensão;TQSDwg.ICPDS2 -> Dobra de suspensão do mesmo lado
        self.smart_rebar.straightBarTextDirection = text_direction # 0 -> Direção do trecho; 1 -> Direção do ferro
        self.smart_rebar.straightBarTextPosition = text_position # 0 -> Não colocar; 1 -> Acima da linha de ferro; 2 -> Abaixo da linha de ferro
        self.smart_rebar.straightBarContinuous = continuous #Ferro Corrido (0) Não (1) Sim
        self.smart_rebar.mirrorMode = mirror_mode #Espelhamento (0) restrito (1) completo
        
        self.smart_rebar.startCoupler = 0 #Luva no início da barra (0) Não (1) Sim
        self.smart_rebar.endCoupler = 0 #Luva no fim da barra (0) Não (1) Sim
        self.smart_rebar.alternatingMode = TQSDwg.ICPSAL #Alternância de ferros retos: TQSDwg.ICPSAL -> Não; TQSDwg.ICPCAL -> Sim
        self.smart_rebar.alternatingFactor = 0 #Fator de alternância de ferro reto

        return self
    
    def to_stirrup(self, dwg: TQSDrawning, dim_x: float, dim_y: float, typ: int = TQSDwg.ICPENR, legs: int = TQSDwg.ICPNR2, hook_type: int = TQSDwg.ICPTPPATA45, hook_length: int = 0) -> Rebar:   
        
        self.__smart_rebar(dwg)
        self.smart_rebar.type = TQSDwg.ICPSTR
        self.smart_rebar.stirrupType = typ     # Tipo de estribo
        self.smart_rebar.stirrupLegs = legs    # Número de ramos
        self.smart_rebar.stirrupHookType = hook_type # Tipo de gancho
        self.smart_rebar.stirrupHookLength = hook_length  # Tamanho dos ganchos em número de diâmetros
        self.smart_rebar.stirrupSectionWidth = dim_x      # Base da seção
        self.smart_rebar.stirrupSectionHeight = dim_y     # Altura da seção
        self.smart_rebar.stirrupSectionWidth2 = 0         # Base max seção var de min/max
        self.smart_rebar.stirrupSectionHeight2 = 0        # Altura max idem
        self.smart_rebar.stirrupEffectiveLeftWidth = 0    # Largura colab a esquerda
        self.smart_rebar.stirrupEffectiveRightWidth = 0   # Largura colab a direita
        self.smart_rebar.stirrupSlabBendLength   = 0      # Dobra do estribo na laje

        return self
    
    def insert_rebar_line(self, point: XY, identify_rebar: int, identify_bend: int, identify_hook: int, angle: float = 0, scale: float = 1, 
                          explode: int = 0, layer: int = -1, style: int = -1, color: int = -1) -> Rebar:
        """
        Entra linha de ferro de qualquer tipo com dados atuais.
        Um mesmo ferro pode ser representado por mais de uma linha no desenho.
        point         <- Ponto de inserção
        angle         <- Ângulo de inserção graus
        scale         <- Escala de inserção
        identify_rebar<- (1) Identificar o ferro
        identify_bend <- (1) Identificar dobras
        identify_hook <- (0) não (1) sim (2) 45░ (3) 225░ (4) invert
                         (0) e (1) vale para ICPFRT, ICPSTR, ICPSTRGEN e ICPGRA
                         (2), (3) e (4) valem para ICPFRT
        explode      <- (1) Explodir se estribo
        layer        <- Nível  0..255 EAG (-1) default
        style        <- Estilo 0..5   EAG (-1) default
        color        <- Cor    0..255 EAG (-1) default
        """
        self.smart_rebar.RebarLine(point.x, point.y, angle, scale, identify_rebar, identify_bend, identify_hook, explode, layer, style, color)
        return self
    
    def identify (self, insertion_point: XY, inumber: int = 1, iposition: int = 1, idiameter: int = 0,  ispacing: int = 0) -> Rebar:
        self.smart_rebar.RebarMarkIdentify(0, insertion_point.x, insertion_point.y, inumber, iposition, idiameter, ispacing)
        return self
    
    def stirrup_distribution_line(self, point1: XY, point2: XY, line_offset: float, order) -> Rebar:
        angle = 0 if abs((point1-point2).x) >= abs((point1-point2).y) else 90
        
        ifdcotc = 0   #(1) p/cotar compr da faixa
        iflnfr = 1    #(1) descrever número de ferros
        iflpos = 1    #(1) descrever número da posição
        iflbit = 0    #(1) descrever bitola
        iflesp = 0    #(1) descrever espaçamento
        ilinexten = 1 #(1) linha de extensão automática
        ilinchama = 0 #(1) se linha de chamada
        itpponta = 0  #(0) flexa (1) círculo (2) traço
        spacing = (abs((point1-point2).x) if angle == 0 else abs((point1-point2).y)) / (self.smart_rebar.quantity - 1) #Espaçamento cm se diferente do ferro
        scale = 1     #Escala de inserção (multiplica todas as dimensões)
        
        # icfes1 <- Número de ferros em função dos espaçamentos
        #           ICPE1P:  Espaçamentos + 1 ferro
        #           ICPE1M:  Espaçamentos - 1 ferro
        #           ICPESP:  Espaçamentos = número de ferros
        icfes1 = TQSDwg.ICPE1P

        #icentr <- Alinhamento
        #           ICPCENTR_CENTRAD: Centrado
        #           ICPCENTR_ESQUERD: Esquerda
        #           ICPCENTR_DIREITA: Direita
        icentr = TQSDwg.ICPCENTR_CENTRAD

        #ibreak <- Salto de linha:
        #          ICPQUEBR_SEMQUEBRA: Sem quebra
        #          ICPQUEBR_SALTOCBCI: Salto C/ ou C=
        #          ICPQUEBR_SALTOBITO: Salto {
        #          ICPQUEBR_SALTODECD: Salto após C/
        #          ICPQUEBR_SALTONPOS: Salto número de ferros
        iquebr = TQSDwg.ICPQUEBR_SEMQUEBRA
        
        # ordem <- Ordem dos textos ("" padrão) "N" = Número de ferros; "n" só o número; "M" só o multiplicador; "P" Posição; "B" Bitola; "E" Espaçamento; "C" Comprimento; "F" Comprimento de faixa
        order = order

        k32vigas           = 0 #Critério K32 CAD/Vigas p/m_ordem=="" (0) não cotar faixa (1) cotar (2) cota e altera Pn
        k41vigas           = 0 #Critério K32 CAD/Vigas p/m_ordem=="" (0) não cotar faixa (1) cotar (2) cota e altera Pn
        
        line_point = XY.mid_point(point2, point1) + ((point2-point1).perpendicular().normalize() * line_offset)

        self.smart_rebar.RebarDistrAdd (icfes1, angle, point1.x, point1.y, point2.x, point2.y, line_point.x, line_point.y, 
            ifdcotc, iflnfr, iflpos, iflbit, iflesp, icentr, iquebr, order, k32vigas, 
            k41vigas, ilinexten, ilinchama, itpponta, spacing, scale)

        return self
    
    @staticmethod
    def negative_distribution_line(smart_rebar: SmartRebar, point1: XY, point2: XY, line_offset: float, order: str = "", breakpoint: int = TQSDwg.ICPQUEBR_SEMQUEBRA):
        angle = 0 if abs((point1-point2).x) >= abs((point1-point2).y) else 90
        
        ifdcotc = 0   #(1) p/cotar compr da faixa
        iflnfr = 1    #(1) descrever número de ferros
        iflpos = 1    #(1) descrever número da posição
        iflbit = 1    #(1) descrever bitola
        iflesp = 1    #(1) descrever espaçamento
        ilinexten = 0 #(1) linha de extensão automática
        ilinchama = 1 #(1) se linha de chamada
        itpponta = 0  #(0) flexa (1) círculo (2) traço
        scale = 1     #Escala de inserção (multiplica todas as dimensões)
        
        # icfes1 <- Número de ferros em função dos espaçamentos
        #           ICPE1P:  Espaçamentos + 1 ferro
        #           ICPE1M:  Espaçamentos - 1 ferro
        #           ICPESP:  Espaçamentos = número de ferros
        icfes1 = TQSDwg.ICPE1P

        #icentr <- Alinhamento
        #           ICPCENTR_CENTRAD: Centrado
        #           ICPCENTR_ESQUERD: Esquerda
        #           ICPCENTR_DIREITA: Direita
        icentr = TQSDwg.ICPCENTR_CENTRAD

        #ibreak <- Salto de linha:
        #          ICPQUEBR_SEMQUEBRA: Sem quebra
        #          ICPQUEBR_SALTOCBCI: Salto C/ ou C=
        #          ICPQUEBR_SALTOBITO: Salto {
        #          ICPQUEBR_SALTODECD: Salto após C/
        #          ICPQUEBR_SALTONPOS: Salto número de ferros
        iquebr = breakpoint
        
        # ordem <- Ordem dos textos ("" padrão) "N" = Número de ferros; "n" só o número; "M" só o multiplicador; "P" Posição; "B" Bitola; "E" Espaçamento; "C" Comprimento; "F" Comprimento de faixa
        text_order = order
        
        k32vigas           = 0 #Critério K32 CAD/Vigas p/m_ordem=="" (0) não cotar faixa (1) cotar (2) cota e altera Pn
        k41vigas           = 0 #Critério K32 CAD/Vigas p/m_ordem=="" (0) não cotar faixa (1) cotar (2) cota e altera Pn
        
        line_point = XY.mid(point2, point1) + ((point2-point1).perpendicular().normalize() * line_offset)

        smart_rebar.RebarDistrAdd (icfes1, angle, point1.x, point1.y, point2.x, point2.y, line_point.x, line_point.y, 
            ifdcotc, iflnfr, iflpos, iflbit, iflesp, icentr, iquebr, text_order, k32vigas, 
            k41vigas, ilinexten, ilinchama, itpponta, smart_rebar.spacing, scale)