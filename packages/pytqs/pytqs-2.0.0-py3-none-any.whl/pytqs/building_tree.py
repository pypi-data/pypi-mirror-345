import os
import ctypes
import tkinter as tk
import tkinter.ttk as ttk
from contextlib import suppress

from pytqs.eag_utils import icon
from pytqs.project import TQSProject, TQSAlvestProject, TQSConcreteProject, TQSPrecastProject, TQSConcreteWallProject, TQSFloor

type TQSSpecificProject = TQSAlvestProject | TQSConcreteProject | TQSPrecastProject | TQSConcreteWallProject

ctypes.windll.shcore.SetProcessDpiAwareness(2)

TREESELECTION_ALL = 0
TREESELECTION_NOTBUILDINGS = 1

folder_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAd0lEQVQ4jcVTWwrAIAzLhufqdjVv1vZiHfHDIXMP5ocBCSpJU6xLRAQGsI6IieTuUN0uF/tuEJF3h5wRZsZGGj7Pn5FoIrLB3RoGrCRT7RdmwpL8LsEXprYY/BGTueYmqAYjCRZuenPwBr5CnYO5LRSXAUz+jQAOEHuqWL76r+QAAAAASUVORK5CYII="
pav_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAX0lEQVQ4jWP8////fwYKACMDQwtFBjCADIABZDYugK6eBd04RsZWkqzH8ML//9X4NaBZwISsiZBmbGqZSHIvFjBqABWiEWwATBOxiQhZPUZKJMsFRFmLy0CKsjMDAwMAVzxe6g2dMM8AAAAASUVORK5CYII="
conc_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAWElEQVQ4jWP8////fwYsgJGxFUXw//9qbMoYmLCKImnCpREGMFyAbjM2Q5EBCzGK8BmO1QBCrhh1wbBzATglkmIjukVwFxBK87hcAzeAXFfgzM5EAQYGBgDqXjK4fqF0TQAAAABJRU5ErkJggg=="
alv_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAVklEQVQ4jWP8////fwYKACMDQwtBA/7/r2ZgZGzFKscCIqYx1ODUnMXQAmdjU8dEifMZqOEF6gYiPptwuYgFFjCEAgsG0NVRNxDJ8cJoShzwlMjAwAAAr+Q8VYuo15UAAAAASUVORK5CYII="
preo_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAhklEQVQ4jc2R3QqAIAxGZ/lc4nsFikLvJb5XLHZhSG626KZz588O2zeDiAgfsFRqzD4YEDf2/o5t55SO6ynGFbj7qYAIIUDOefjkvdcJJEopouxRwI3jnNMJKMiGFKgo6At6kUogbaRRa5UFLSSak9uIqoMZ/UZeC7hx1AIpyOVNBz8UAMAJbZgrNEuSJycAAAAASUVORK5CYII="
parcon_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAxElEQVQ4jY2T0QqDMAxFr913Dftfe5DC9l+VfZd0JHBLjGldXoox9/S0IoB3K6U0u87KzyUAyDmjlAPb9tB1WT6ISvqc2/enPiug1noLsWFZJSPVDWYQG5aSVWY7QMLSHEFsuLUXmDkZkMwXcka7ow3bTLI0GaCeBfnw0ICD6/rtPQ76uhjws/gdLHxq4CF3BrwXBVCZkH8MeNzEy4kgkQENmVODCMKdrYEPd8AIYg2i8AkQQbyBDytYfslLM/gbozAA/AAGK+IJCFNXZQAAAABJRU5ErkJggg=="

class BuildingTreeApp:
    def __init__(self, tqs_path: str, list_pavs: bool, list_subfolders: bool, selection_mode: int,
                 building_filter: list[int] = None, building_code_filter: list[str] = None, master = None):
        self.tqs_path = tqs_path if os.path.exists(tqs_path) else ''
        self.list_pavs = list_pavs
        self.list_subfolders = list_subfolders
        self.building_filter = building_filter
        self.building_code_filter = building_code_filter
        self.selection_mode = selection_mode

        self.master = master or tk.Tk()
        self.master.wm_withdraw()
        self.TQS_folder = tk.StringVar(value=self.tqs_path)
        self.selected_folder = tk.StringVar()

        # Icons
        self.img_folder = tk.PhotoImage(data=folder_png_b64, width=20, height=16)
        self.img_floor = tk.PhotoImage(data=pav_png_b64, width=20, height=16)
        self.img_conc = tk.PhotoImage(data=conc_png_b64, width=20, height=16)
        self.img_alvest = tk.PhotoImage(data=alv_png_b64, width=20, height=16)
        self.img_preo = tk.PhotoImage(data=preo_png_b64, width=20, height=16)
        self.img_parcon = tk.PhotoImage(data=parcon_png_b64, width=20, height=16)

        self.master.title('Árvore de Edifícios TQS')
        self.master.wm_iconbitmap(icon())
        
        # Center the window
        win_width = 700
        win_height = 700
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int((screen_width / 2) - (win_width / 2))
        center_y = int((screen_height / 2) - (win_height / 2))
        self.master.geometry(f'{win_width}x{win_height}+{center_x}+{center_y}')
        self.master.resizable(False, False)
        self.master.attributes('-topmost', True)
        
        #Header
        frame_top = tk.Frame(self.master)
        tk.Label(frame_top,text='Pasta Raiz:').grid(row=0, column=0, sticky='w', pady=5)
        tk.Entry(frame_top, width=30, textvariable=self.TQS_folder).grid(row=0, column=1, sticky='w',padx=5,pady=5)
        tk.Button(frame_top, text='Atualizar', command=self.update_tree, width=10).grid(row=0, column=2, sticky='w',padx=3,pady=5)
        tk.Button(frame_top, text='Encontra Pasta', command=self.find_folder, width=14).grid(row=0, column=3, sticky='w',pady=5)
        frame_top.pack()


        # Árvore de Edifícios
        ttk.Style().configure('Treeview', rowheight=25)
        
        tree_frame = tk.Frame(self.master)
        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode="browse")
        ybar = tk.Scrollbar(tree_frame,orient=tk.VERTICAL, command=self.tree.yview)
        self.update_tree()
        self.tree.configure(yscroll=ybar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        ybar.pack(side=tk.RIGHT,fill=tk.Y)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Seleção
        frame_bottom = tk.Frame(self.master)
        tk.Label(frame_bottom,text='Seleção Atual:').pack(side='left', fill='x', expand=False)
        tk.Entry(frame_bottom, width=50, state='disabled', textvariable=self.selected_folder).pack(side='right',fill='x',expand=True)
        frame_bottom.pack()

        # Botão Ok
        tk.Button(self.master, text='Selecionar', command=self.finish_selection, width=10).pack(side=tk.BOTTOM, padx=5, pady=5)
        
        # Variável de saída
        self.output = None

        self.master.wm_deiconify()
        self.master.wait_window()

    def _get_tqs_projects(self, path: str, max_depth: int = 3) -> list[TQSProject]:
        all_folders = []
        for root, dirs, files in os.walk(path):
            current_depth = root.count(os.sep) - path.count(os.sep)
            if current_depth >= max_depth:
                del dirs[:]
                continue
            all_folders.extend(os.path.join(root, dir) for dir in dirs)
        tqs_buildings = [TQSProject(dir) for dir in all_folders if os.path.exists(os.path.join(dir, 'EDIFICIO.BDE'))]
    
        return [project for project in tqs_buildings if (not self.building_filter or project.project_type in self.building_filter) and 
                                                        (not self.building_code_filter or project.code in self.building_code_filter)]

    def project_type_image(self, project: TQSProject) -> tk.PhotoImage:
        """Retorna a imagem correspondente ao tipo de projeto"""
        images = {0: self.img_conc, 1: self.img_preo, 2: self.img_alvest, 3: self.img_parcon}
        return images.get(project.project_type, self.img_conc)
        
    def list_tqs_subfolders(self, projects: list[TQSProject]):
        for project in projects:
            for subfolder in project.subfolders:
                self.tree.insert(project.path, "end", os.path.join(project.path, subfolder), text=subfolder, image=self.img_folder)

    def list_tqs_floors(self, projects: list[TQSProject]):
        for project in projects:
            for floor in reversed(project.floor_names):
                self.tree.insert(project.path, "end", os.path.join(project.path, floor), text=floor, image=self.img_floor)


    def on_select(self, event):
        """Seleciona um projeto TQS"""
        with suppress(IndexError):
            if parent := self.tree.parent(self.tree.selection()[0]):
                if (self.selection_mode == TREESELECTION_ALL or 
                   (self.selection_mode == TREESELECTION_NOTBUILDINGS and (parent != self.tqs_path))):
                    
                    self.selected_folder.set(os.path.basename(self.tree.selection()[0]))
                    return
            self.selected_folder.set("")
    
    def finish_selection(self):
        try:
            self.output = self.tree.selection()[0] if self.selected_folder.get() else None
        except IndexError:
            self.output = None
        self.master.destroy()


    def update_tree(self):
        """Atualiza a árvore de edifícios"""
        self.tqs_path = os.path.normpath(self.TQS_folder.get())
        projects = self._get_tqs_projects(self.tqs_path)
        
        self.tree.delete(*self.tree.get_children())

        # Insere a pasta raiz
        self.tree.insert('', 'end', iid=self.tqs_path, text=self.tqs_path, open=True)
        
        # Insere os projetos TQS
        path_depth = len(self.tqs_path.split(os.path.sep))
        for project in projects:
            project_split = project.path.split(os.path.sep)
            project_depth = len(project_split)
            for i in range(project_depth):
                if i < path_depth:
                    continue
                current_folder = '\\'
                current_folder = current_folder.join(project_split[:i])
                if self.tree.exists(current_folder):
                    continue
                else:
                    self.tree.insert(os.path.dirname(current_folder),
                    'end',
                    current_folder,
                    text=os.path.basename(current_folder),
                    image=self.img_folder)

            self.tree.insert(project.directory,'end', project.path, text=project.name, image=self.project_type_image(project))
        
        if self.list_subfolders:
            self.list_tqs_subfolders(projects)

        if self.list_pavs:
            self.list_tqs_floors(projects)

    def find_folder(self):
        if projeto := tk.filedialog.askdirectory(mustexist = True, title = "Selecione a pasta de projetos TQS", initialdir = self.tqs_path):
            self.TQS_folder.set(projeto)
            self.update_tree()

def building_tree(initialdir: str = 'C:\\TQS', list_pavs: bool = True, list_subfolders: bool = True, selection_mode: int = TREESELECTION_ALL, 
                  building_filter: list[int] = None, building_code_filter: list[str] = None, master=None) -> str | None:
    building_tree_app = BuildingTreeApp(initialdir, list_pavs, list_subfolders, selection_mode, building_filter, building_code_filter, master)
    return building_tree_app.output

def building_tree_project(initialdir: str = 'C:\\TQS', building_filter: list[int] = None, 
                          building_code_filter: list[str] = None, master=None) -> TQSSpecificProject | None:
    building_path = BuildingTreeApp(initialdir, False, False, TREESELECTION_ALL, building_filter, building_code_filter, master).output
    return TQSProject(building_path).as_specific_project() if building_path else None

def building_tree_floor(initialdir: str = 'C:\\TQS', building_filter: list[int] = None, 
                          building_code_filter: list[str] = None, master=None) -> TQSFloor | None:
    if floor_path := BuildingTreeApp(initialdir, True, False, TREESELECTION_NOTBUILDINGS, building_filter, building_code_filter, master).output:
        building = TQSProject(os.path.dirname(floor_path))
        return [floor for floor in building.floors if floor.name == os.path.basename(floor_path)][0]
    return None