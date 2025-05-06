from __future__ import annotations
import os
import re
import struct

TQSBUILD_CONCRETE = 0
TQSBUILD_PRECAST = 1
TQSBUILD_ALVEST = 2
TQSBUILD_CONCRETEWALL = 3

TQSFLOOR_CONCRETE = 0
TQSFLOOR_PRECAST = 1
TQSFLOOR_ALVEST = 2
TQSFLOOR_CONCRETEWALL = 3

TQSFLOOR_FUN = 1   # Fundação
TQSFLOOR_SUB = 2   # Subsolo
TQSFLOOR_TER = 3   # Térreo
TQSFLOOR_MEZ = 4   # Mezzanino
TQSFLOOR_TRN = 5   # Transição
TQSFLOOR_PRI = 6   # Primeiro
TQSFLOOR_TIP = 7   # Tipo
TQSFLOOR_COB = 8   # Cobertura
TQSFLOOR_ATI = 9   # Ático
TQSFLOOR_DUP = 10  # Duplex
TQSFLOOR_TRI = 11  # Triplex

class TQSFloor():
    def __init__(self, project: TQSProject, name: str, project_number: int, repetitions: int, project_class: int, height: float):
        self.project = project
        self.name = name
        self.project_number = project_number
        self.repetitions = repetitions
        self.project_class = project_class
        self.height = height
    
    def __repr__(self) -> str:
        return f"TQSFloor[{self.project.name}, {self.project_number}, {self.name}, {self.repetitions}x, {self.project_class}, {self.height}m]"

class TQSProject():
    def __init__(self, project_path: str):
        self.path = project_path
        self.bde_file = f"{project_path}/EDIFICIO.BDE"
        self.bde_content = open(self.bde_file, 'rb').read()
        self.name = os.path.basename(project_path)
        self.directory = os.path.dirname(project_path)
        self.project_type = self.get_project_type()
        self.floor_names = self.get_floor_names()
        self.floors = self.get_floors()
        self.code = self.get_code()
        self._subfolders = None

    @property
    def subfolders(self):
        if self._subfolders is None:
            self._subfolders = self.get_subfolders()

        return self._subfolders
        
    def get_project_type(self) -> int:
        content = open(self.bde_file, 'rb').read()
        typ = content.partition(b'\xCD\xCC\x4C\x3F')[2][12]
        is_pre = content.partition(b'\x13\x9E\xA8\x97')[2][336]
        if typ == 0:
            return 1 if is_pre else 0
        return typ + 1

    def get_subfolders(self) -> list[str]:
        def string_between(string: str, start: str, end: str) -> str:
            return string.partition(start)[2].split(end)[0]
        
        def decode_folder_string(data: bytes) -> list[str]:
            folders = []
            while data:
                num_char = int(data[0])
                folders.append(str(data[4:3+num_char], "cp1252"))
                data = data[4+num_char:]
                if len(folders) >= 8:
                    break
            return folders

        def split_first_list(content: bytes, project_name: str) -> list[str]:
            if b'\x00\x39\x40' in content:
                data = string_between(content, b'\xFC\x07\x00\x00\x36', b'\x00\x39\x40')
            else:
                data = string_between(content, b'\xFC\x07\x00\x00\x36', b'\x66\x66\x66\x66\x66\x66\xF6\x3F')
            data = data.partition(str.encode(project_name, encoding="cp1252"))[2].partition(b'\x01')[2][19:]
            return decode_folder_string(data)

        def split_second_list(content) -> list[str]:
            data = string_between(content, b'\x40\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01', b'\x80')[126:].partition(b'\x01')[2][4:]
            return decode_folder_string(data)

        return [folder for folder in (split_first_list(self.bde_content, self.name) + split_second_list(self.bde_content)) if folder]
    
    def get_code(self) -> str:
        if self.project_type in [0, 1]:
            if str.encode("NB1-78", encoding="cp1252") in self.bde_content:
                return "NB1-78"
            elif str.encode("NBR-6118-2003", encoding="cp1252") in self.bde_content:
                return "NBR-6118:2003"
            elif str.encode("NBR-6118-2014", encoding="cp1252") in self.bde_content:
                return "NBR-6118:2014"
            elif str.encode("CIRSOC-2005", encoding="cp1252") in self.bde_content:
                return "CIRSOC-2005"
            elif str.encode("ACI-318-05", encoding="cp1252") in self.bde_content:
                return "ACI-318-05"
            elif str.encode("ACI-318-14", encoding="cp1252") in self.bde_content:
                return "ACI-318-14"
        elif self.project_type == 2:
            code_number = self.bde_content.partition(b'\x7B\x14\xAE\x47\xE1\x7A\x94\x3F\x33\x33\x33\x33\x33\x33\xF3\x3F')[2][92]
            if code_number == 0:
                return "NBR-10837:1989"
            elif code_number == 1:
                return "NBR-15961-1:2011"
            elif code_number == 2:
                return "NBR-15812-1:2010"
            elif code_number == 3:
                return "NBR-16868-1:2020"
        elif self.project_type == 3:
            return "NBR-16055:2012"

        return "Norma indefinida"
    
    def get_floor_names(self) -> list[str]:
        data = self.bde_content.partition(b'\xFC\x07\x00\x00\x36')[2].partition(b'\xFC\x07\x00\x00\x36')[2].split(b'\x00\x39\x40')[0].partition(str.encode(self.name, encoding="cp1252"))[0]
        return [str(folder, "cp1252") for folder in filter(lambda a: len(a) != 1 or a >= b'\x30', [s for s in data[511:-5].split(b'\x00') if s])]
    
    def get_floors(self) -> list[TQSFloor]:
        content = self.bde_content.partition(b'\xCD\xCC\x4C\x3F')[2][1:]
        return [TQSFloor(self, floor, content[229+i*1850], content[625+i*1850], content[631+i*1850], round((struct.unpack('!f', content[627+i*1850:631+i*1850][::-1])[0]), 3)) for i, floor in enumerate(self.floor_names)]
    
    def as_specific_project(self) -> TQSProject:
        if self.project_type == TQSBUILD_CONCRETE:
            return TQSConcreteProject(self.path)
        elif self.project_type == TQSBUILD_PRECAST:
            return TQSPrecastProject(self.path)
        elif self.project_type == TQSBUILD_ALVEST:
            return TQSAlvestProject(self.path)
        elif self.project_type == TQSBUILD_CONCRETEWALL:
            return TQSConcreteWallProject(self.path)
        else:
            raise ValueError(f"Unknown project type: {self.project_type}")

class TQSAlvestProject(TQSProject):
    def __init__(self, project_path):
        super().__init__(project_path)
        if self.project_type != TQSBUILD_ALVEST:
            raise ValueError("Project is not of type TQSBUILD_ALVEST")

    def get_alvest_block_specs(self) -> list[tuple[float, float, float]]:
        instalv_text = open(f"{self.path}\\INSTALV.DAT", "r").read()
        material_string_section = re.search(r'\s+\d+\s+Quantidade de fbks\/fps na tabela(.+)\d+\s+Material\spré-estabelecido:', instalv_text, re.S)[1]
        material_rows = [list(filter(None, striped_row.split(" "))) for row in material_string_section.split("\n") if (striped_row := row.strip())]

        return [(float(i[0]), float(i[1]), float(i[6])) for i in material_rows]
    
    def get_alvest_load_reduction(self) -> bool:
        carrpor_text = open(f"{self.path}\\ESPACIAL\\CARRPOR.DAT", "r").read()
        return int(re.search(r'(\d+)\s+\/\/\sNúmero\sde\scasos\sordenados', carrpor_text, re.M)[1]) == 9
    
    def get_alvest_grout_specific_weight(self) -> float:
        instalv_text = open(f"{self.path}\\INSTALV.DAT", "r").read()
        return float(re.search(r'^\s*(\d+.?\d*)\s+Peso específico graute', instalv_text, re.M)[1])
    
    def get_alvest_wind_transfer(self) -> int:
        instalv_text = open(f"{self.path}\\INSTALV.DAT", "r").read()
        return int(re.search(r'^\s*(\d+)\s+Transf\. carregs de Ventos', instalv_text, re.M)[1])
    
    def get_alvest_replace_rebar_parameter(self) -> bool:
        inst_alv_path = f"{self.path}\\INSTALV.DAT" 

        for line in open(inst_alv_path, 'r', encoding='cp1252'):
            if "Ferro imposto em paredes" in line:
                return line.strip().split()[0] == "1"

    def set_alvest_replace_rebar_parameter(self, replace: bool) -> None:
        inst_alv_path = f"{self.path}\\INSTALV.DAT" 
        with open(inst_alv_path, 'r', encoding='cp1252') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if "Ferro imposto em paredes" in line:
                lines[i] = f"    {int(replace)}    Ferro imposto em paredes: (0) adicional aopré-congifurado (1) substitue o pré-configurado\n"
                break

        with open(inst_alv_path, 'w', encoding='cp1252') as file:
            file.writelines(lines)

class TQSConcreteProject(TQSProject):
    def __init__(self, project_path):
        super().__init__(project_path)
        if self.project_type != TQSBUILD_CONCRETE:
            raise ValueError("Project is not of type TQSBUILD_CONCRETE")
        
class TQSPrecastProject(TQSProject):
    def __init__(self, project_path):
        super().__init__(project_path)
        if self.project_type != TQSBUILD_PRECAST:
            raise ValueError("Project is not of type TQSBUILD_PRECAST")
        
class TQSConcreteWallProject(TQSProject):
    def __init__(self, project_path):
        super().__init__(project_path)
        if self.project_type != TQSBUILD_CONCRETEWALL:
            raise ValueError("Project is not of type TQSBUILD_CONCRETEWALL")