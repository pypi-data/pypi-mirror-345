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
#   TQSExec.py          Execução do TQS em batch 
#-----------------------------------------------------------------------------
import ctypes
from TQS import TQSUtil
#-----------------------------------------------------------------------------
#       Classe Task: uma tarefa a ser executada
#
class Task ():
    TASK_NONE               =  0
    TASK_FOLDER             =  1
    TASK_ROOTFOLDER         =  2
    TASK_GLOBALPROC         =  3
    TASK_LOADSREPORT        =  4 
    TASK_SLABDRAWINGS       =  5
    TASK_LATTICESLABS       =  6
    TASK_COMPOSITESLABS     =  7
    TASK_REBARSCHEDULE      =  8
    TASK_STAIRS             =  9
    TASK_FLOORPLANDRAWINGS  = 10
    TASK_PRECASTDRAWINGS    = 11
    TASK_PRECASTBEAMS       = 12
    TASK_PRECASTFOUNDATIONS = 13
    TASK_PRECASTCOLUMNS     = 14
    TASK_PRECASTCORBELS     = 15
    TASK_PRECASTMATERIALS   = 16     
    TASK_STRUCTURALREPORT   = 17     

    def __init__ (self):
        """
        Classe mãe das tarefas
        """
        self.m_itask         = self.TASK_NONE
#-----------------------------------------------------------------------------
#       Pasta atual do edifício
#
class TaskFolder (Task):
#
#       Tipo da pasta escolhida
#
    FOLDER_FRAMES         = 0           # Pasta Espacial
    FOLDER_COLUMNS        = 1           # Pasta Pilares
    FOLDER_FOUNDATIONS    = 2           # Pasta Fundacoes
    FOLDER_FLOORS         = 3           # Pasta do pavimento
    FOLDER_GENERAL        = 4           # Pasta Gerais
    FOLDER_INFRASTRUCTURE = 5           # Pasta Infraestrutura
#
#       Subpasta de plantas
#
    SUBFOLDER_NONE        = 0           # Pasta do pavimento
    SUBFOLDER_BEAMS       = 1           # Subpasta vigas
    SUBFOLDER_STAIRS      = 2           # Subpasta escadas

    def __init__ (self, 
            buildingName, 
            folderType = FOLDER_FRAMES, 
            folderName = "", 
            subFolder  = SUBFOLDER_NONE):
        """
        Define a pasta atual do edifício\n
        buildingName        Nome do edifício\n
        folderType          Pasta tipo FOLDER_xxx\n
        folderName          Nome da pasta (string) para FOLDER_FLOORS\n
        subFolder           Subpasta tipo SUBFOLDER_xxxx para FOLDER_FLOORS
        """
        super().__init__()
        self.m_itask         = self.TASK_FOLDER
        self.m_buildingName  = buildingName
        self.m_folderType    = folderType
        self.m_folderName    = folderName
        self.m_subFolder     = subFolder

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        tipos           = ["ESPACIAL", "PILAR", "FUNDAC", "", "GERAIS", "SISE"] #!NTR
        subtipos        = ["", "VIGAS", "ESCADAS"]                              #!NTR
        script          = "EDIFICIO '" + self.m_buildingName + "' " + tipos [self.m_folderType]#!NTR
        if              (self.m_folderType == self.FOLDER_FLOORS):
            script      += " '" + self.m_folderName + "'" 
        if              (self.m_subFolder != self.SUBFOLDER_NONE):
            script      += " " + subtipos [self.m_subFolder-1] 
        return          (script)

#-----------------------------------------------------------------------------
#       Raiz do edifício
#
class TaskRootFolder (Task):

    def __init__ (self, rootfolder):
        """
        Define a pasta raiz de edifícios
        """
        super().__init__()
        self.m_itask         = self.TASK_ROOTFOLDER
        self.m_rootfolder    = rootfolder

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        return          "ARVORE '" + self.m_rootfolder + "'"   #!NTR

#-----------------------------------------------------------------------------
#       Processamento Global
#
class TaskGlobalProc (Task):

    def __init__ (self, 
            floorPlan = 2,
            floorDraw = 0,
            slabs = 0,
            beams = 1,
            columnsData = 1,
            columns = 0,
            columnsReport = 1,
            gridModel = 1,
            gridDraw = 1,
            gridExtr = 1,
            gridAnalysis = 1,
            gridBeamsTrnsf = 0,
            gridSlabsTrnsf = 1,
            gridNonLinear = 0,
            frameModel = 1,
            frameAnalysis = 1,
            frameBeamsTrnsf = 1,
            frameColumnsTrnsf = 1,
            foundations = 0,
            stairs = 0,
            fire = 0,
            precastPhases = 0,
            ):
        """
        Processamento global conforme parâmetros escolhidos\n
        floorPlan         (0) Não (1) Extrair plantas (2) Extrair e processar\n
        floorDraw         (0) Não (1) Desenhar formas\n
        slabs             (0) Não (1) Esforços (2) Esforços e desenho\n
        beams             (0) Não (1) Esforços (2) Dimensionamento, detalhamento (3) E desenho\n
        columnsData       (0) Não (1) gravação de dados de pilares\n
        columns           (0) Não (1) Dimensionamento, detalhamento (2) E desenho\n
        columnsReport     (0) Não (1) Relatório geral de pilares\n
        gridModel         (0) Não (1) Geração do modelo\n
        gridDraw          (0) Não (1) Desenho de dados de grelha\n
        gridExtr          (0) Não (1) Extração do desenho\n
        gridAnalysis      (0) Não (1) Análise de esforços\n
        gridBeamsTrnsf    (0) Não (1) Transferência de esforços para vigas\n
        gridSlabsTrnsf    (0) Não (1) Transferência de esforços para lajes\n
        gridNonLinear     (0) Não (1) Análise não linear\n
        frameModel        (0) Não (1) Geração do modelo\n
        frameAnalysis     (0) Não (1) Análise de esforços\n
        frameBeamsTrnsf   (0) Não (1) Transferência de esforços para vigas\n
        frameColumnsTrnsf (0) Não (1) Transferência de esforços para pilares\n
        foundations       (0) Não (1) Dimensonamento, detalhamento (2) E desenho\n
        stairs            (0) Não (1) Dimensonamento, detalhamento e desenho\n
        fire              (0) Não (1) Verificação à incêndio\n
        precastPhases     (0) Não (1) Pré-moldados: Todas as etapas construtivas
        """
        super().__init__()
        self.m_itask         = self.TASK_GLOBALPROC
        self.m_floorPlan       = floorPlan       
        self.m_floorDraw       = floorDraw       
        self.m_slabs           = slabs           
        self.m_beams           = beams           
        self.m_columnsData     = columnsData     
        self.m_columns         = columns         
        self.m_columnsReport   = columnsReport   
        self.m_gridModel       = gridModel       
        self.m_gridDraw        = gridDraw        
        self.m_gridExtr        = gridExtr        
        self.m_gridAnalysis    = gridAnalysis    
        self.m_gridBeamsTrnsf  = gridBeamsTrnsf  
        self.m_gridSlabsTrnsf  = gridSlabsTrnsf  
        self.m_gridNonLinear   = gridNonLinear   
        self.m_frameModel      = frameModel      
        self.m_frameAnalysis   = frameAnalysis   
        self.m_frameBeamsTrnsf = frameBeamsTrnsf 
        self.m_frameColumnsTrnsf=frameColumnsTrnsf       
        self.m_foundations     = foundations     
        self.m_stairs          = stairs          
        self.m_fire            = fire            
        self.m_precastPhases   = precastPhases   

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          =  "PROC"                                               #!NTR
        script          += " FORMAS %d %d" % (self.m_floorPlan, self.m_floorDraw)#!NTR
        script          += " LAJES %d" % (self.m_slabs)                         #!NTR
        script          += " VIGAS %d" % (self.m_beams)                         #!NTR
        script          += " PILARES %d %d %d" % (self.m_columnsData, self.m_columns, #!NTR
                             self.m_columnsReport)
        script          += " GRELHAS %d %d %d %d %d %d %d" % (                  #!NTR
                            self.m_gridModel, self.m_gridDraw,
                            self.m_gridExtr, self.m_gridAnalysis, self.m_gridBeamsTrnsf, 
                            self.m_gridSlabsTrnsf, self.m_gridNonLinear)
        script          += " PORTICO %d %d %d %d" % (self.m_frameModel, self.m_frameAnalysis, #!NTR
                            self.m_frameBeamsTrnsf, self.m_frameColumnsTrnsf)
        script          += " FUNDAC %d" % (self.m_foundations)                  #!NTR
        if              (self.m_stairs != 0):
            script      += " ESCADAS"                                           #!NTR
        if              (self.m_fire != 0):
            script      += " INCENDIO"                                          #!NTR
        if              (self.m_precastPhases != 0):
            script      += " ETAPAS"                                            #!NTR
        return          script


#-----------------------------------------------------------------------------
#       Planta de cargas
#
class TaskLoadsReport (Task):

    def __init__ (self):
        """
        Planta de cargas PORLID.DWG
        """
        super().__init__()
        self.m_itask         = self.TASK_LOADSREPORT

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "PORLID"                                        #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Desenho de lajes
#
class TaskSlabDrawings (Task):

    def __init__ (self,
        rebartop=1,
        rebarbot=1,
        rebarpunch=1,
        rebarshear=1,
        forcestop=1,
        forcesbot=1,
        forcespunch=1,
        forcesshear=1
            ): 
        """
        Desenhos de lajes\n
        rebartop        (0) Não (1) Ferros positivos\n
        rebarbot        (0) Não (1) Ferros negativos\n
        rebarpunch      (0) Não (1) Ferros de punção\n
        rebarshear      (0) Não (1) Ferros de cisalhamento\n
        forcestop       (0) Não (1) Faixas positivos\n
        forcesbot       (0) Não (1) Faixas negativos\n
        forcespunch     (0) Não (1) Faixas de punção\n
        forcesshear     (0) Não (1) Faixas de cisalhamento
        """
        super().__init__()
        self.m_itask            = self.TASK_SLABDRAWINGS
        self.m_rebartop         = rebartop   
        self.m_rebarbot         = rebarbot   
        self.m_rebarpunch       = rebarpunch 
        self.m_rebarshear       = rebarshear 
        self.m_forcestop        = forcestop  
        self.m_forcesbot        = forcesbot  
        self.m_forcespunch      = forcespunch
        self.m_forcesshear      = forcesshear

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DESLAJ %d %d %d %d %d %d %d %d" % (           #!NTR
                         self.m_rebartop, self.m_rebarbot, self.m_rebarpunch, 
                         self.m_rebarshear, self.m_forcestop, 
                         self.m_forcesbot, self.m_forcespunch, self.m_forcesshear)
        return          script

#-----------------------------------------------------------------------------
#       Desenho de lajes treliçadas
#
class TaskLatticeSlabs (Task):

    def __init__ (self,
        latticeList = 1,
        latticeBeams = 1,
        rebarList = 1,
        fillingList = 1
            ): 
        """
        Desenhos de lajes treliçadas\n
        latticeList     (0) Não (1) Tabela de vigotas treliçadas\n
        latticeBeams    (0) Não (1) Planta de fabricação de vigotas\n
        rebarList       (0) Não (1) Tabela de ferros complementares\n
        fillingList     (0) Não (1) Tabela de enchimentos
        """
        super().__init__()
        self.m_itask            = self.TASK_LATTICESLABS
        self.m_latticeList      = latticeList 
        self.m_latticeBeams     = latticeBeams
        self.m_rebarList        = rebarList   
        self.m_fillingList      = fillingList  

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DESLAJTRE %d %d %d %d" % (                    #!NTR
                         self.m_latticeList, self.m_latticeBeams, 
                         self.m_rebarList, self.m_fillingList)
        return          script

#-----------------------------------------------------------------------------
#       Desenho de lajes mistas nervuradas
#
class TaskCompositeSlabs (Task):

    def __init__ (self): 
        """
        Desenhos de lajes mistas nervuradas
        """
        super().__init__()
        self.m_itask         = self.TASK_COMPOSITESLABS


    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DESLAJMISNER"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Tabela de ferros com todos os desenhos
#
class TaskRebarSchedule (Task):

    def __init__ (self): 
        """
        Tabela de ferros com todos os desenhos de armadura do edifício
        """
        super().__init__()
        self.m_itask         = self.TASK_REBARSCHEDULE

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "TABFERTODOSDWG"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Processamento de escadas
#
class TaskStairs (Task):

    def __init__ (self): 
        """
        Dimensionamento, detalhamento e desenho de escadas
        """
        super().__init__()
        self.m_itask         = self.TASK_STAIRS

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "ESCADAS"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Desenho de formas
#
class TaskFloorPlanDrawings (Task):

    def __init__ (self,
            floor = 1,
            columns = 1,
            slabs = 1,
            slabsDims = 1,
            beams = 1,
            loads = 1,
            sections = 1
            ): 
        """
        Desenho de formas\n
        floor           (0) Não (1) Planta de formas\n
        columns         (0) Não (1) Planta de pilares\n
        slabs           (0) Não (1) Verificação de nós de lajes\n
        slabsDims       (0) Não (1) Verificação de medidas de lajes\n
        beams           (0) Não (1) Nós e cargas em vigas\n
        loads           (0) Não (1) Cargas em lajes\n
        sections        (0) Não (1) Cortes do edifício
        """
        super().__init__()
        self.m_itask            = self.TASK_FLOORPLANDRAWINGS
        self.m_floor            = floor    
        self.m_columns          = columns  
        self.m_slabs            = slabs    
        self.m_slabsDims        = slabsDims
        self.m_beams            = beams    
        self.m_loads            = loads    
        self.m_sections         = sections 

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DESFOR %d %d %d %d %d %d %d" % (                              #!NTR
                         self.m_floor, self.m_columns, self.m_slabs, self.m_slabsDims, 
                         self.m_beams, self.m_loads, self.m_sections)
        return          script

#-----------------------------------------------------------------------------
#       Desenhos de pré-moldados
#
class TaskPreCastDrawings (Task):
    def __init__ (self): 
        """
        Desenho de pré-moldados
        """
        super().__init__()
        self.m_itask         = self.TASK_PRECASTDRAWINGS

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DESPRE"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Transferência de esforços para cálculo de vigas pré-moldadas
#
class TaskPreCastBeams (Task):
    def __init__ (self): 
        """
        Transferência de esforços para cálculo de vigas pré-moldadas
        """
        super().__init__()
        self.m_itask         = self.TASK_PRECASTBEAMS

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "TRNPREVIG"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Transferência de esforços para cálculo de fundações pré-moldadas
#
class TaskPreCastFoundations (Task):
    def __init__ (self): 
        """
        Transferência de esforços para cálculo de fundações pré-moldadas
        """
        super().__init__()
        self.m_itask         = self.TASK_PRECASTFOUNDATIONS

def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "TRNPREFUN"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Dimensionamento, detalhamento e desenho de pilares pré-moldados
#
class TaskPreCastColumns (Task):
    def __init__ (self): 
        """
        Dimensionamento, detalhamento e desenho de pilares pré-moldados
        """
        super().__init__()
        self.m_itask         = self.TASK_PRECASTCOLUMNS

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DIMPILPRE"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Processamento de consolos pré-moldaddos
#
class TaskPreCastCorbels (Task):
    def __init__ (self): 
        """
        Dimensionamento, detalhamento e desenho de consolos pré-moldados
        """
        super().__init__()
        self.m_itask         = self.TASK_PRECASTCORBELS

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "DIMCONPRE"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Quantitativos de pré-moldados
#
class TaskPreCastMaterials (Task):
    def __init__ (self): 
        """
        Quantitativos de pré-moldados
        """
        super().__init__()
        self.m_itask         = self.TASK_PRECASTMATERIALS

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "QUANTPRE"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Resumo Estutural
#
class TaskStructuralReport (Task):
    def __init__ (self): 
        """
        Resumo Estrutural
        """
        super().__init__()
        self.m_itask         = self.TASK_STRUCTURALREPORT

    def Script (self):
        """
        Retorna o script para execução no gerenciador
        """
        script          = "RESEST"                                #!NTR
        return          script

#-----------------------------------------------------------------------------
#       Classe que controla a excecução do TQS com o script fornecido
#
class Job ():
    """
    Controla a execução do TQS com um script de comandos fornecido
    """

    def __init__ (self): 
        """
        """
        self.listaexec = []

    def EnterTask (self, task):
        """
        Acumula uma tarefa da classe Task para execução
        """
        self.listaexec.append (task)

    def Execute (self):
        """
        Executa os comandos acumulados, chama o TQS e sai no final
        """
        nomarq          = "GERENCIADOR.DAT"
        file            = open(nomarq, 'w')
        for              task in self.listaexec:
            file.write  ("%s\n" % task.Script ())
        file.close      ()
        command         = "TQS.EXE -RLST -CMD:" + nomarq
        TQSUtil.ExecTqs (command)


