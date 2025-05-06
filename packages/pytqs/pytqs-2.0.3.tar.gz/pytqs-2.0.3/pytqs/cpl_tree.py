from __future__  import annotations

import os
import ctypes
import tkinter as tk
import tkinter.ttk as ttk
from contextlib import suppress

from pytqs.eag_utils import icon

ctypes.windll.shcore.SetProcessDpiAwareness(2)

TREESELECTIONCPL_NOTBUILDINGS = 0
TREESELECTIONCPL_ONLYBUILDINGS = 1

folder_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAd0lEQVQ4jcVTWwrAIAzLhufqdjVv1vZiHfHDIXMP5ocBCSpJU6xLRAQGsI6IieTuUN0uF/tuEJF3h5wRZsZGGj7Pn5FoIrLB3RoGrCRT7RdmwpL8LsEXprYY/BGTueYmqAYjCRZuenPwBr5CnYO5LRSXAUz+jQAOEHuqWL76r+QAAAAASUVORK5CYII="
conc_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAWElEQVQ4jWP8////fwYsgJGxFUXw//9qbMoYmLCKImnCpREGMFyAbjM2Q5EBCzGK8BmO1QBCrhh1wbBzATglkmIjukVwFxBK87hcAzeAXFfgzM5EAQYGBgDqXjK4fqF0TQAAAABJRU5ErkJggg=="
sheet_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAGzSURBVDhPrZPNS5NxHMB36Y/oYIfxzJMoWvnSSRG9BZ2c2UkE2SzXIXV7FpJQBOmuXgSPUpc0HdMyX7aVc27uyUeHL+hybbiVIL42K5KP7Dd8hIGIzC98+MIPPp/T76sjx9FlP1x1dNUmBzVmB7WmHmpM3VQ2vuTeo+dUNNgpr5cpq7dRZrRRarRSWtfO3TOMNm7fb0b3uneA5PYOq9FfhCMJguEInsAibr/K1Ow3Jn0KEzMhPn+dZ9wbFHz0zAkn7YrAanyXqjcqRZ0BCqxe8p+OkW8ZxWBxIbW6kJ44kVpG0JuH0Zs/cKt5SDhaYCWRQm9XWfx5QjD+71KKbF7haIHlxO9MIHlCIPb3Ugo63MLRAuH4IZJ9ATX5H3/0GP9mKrMvoFyeEI4WWIrtY5AVlPgfIfsiR5nIBdx4OCic88CPPQxyiFAshXf9kJn1A7GzxTOkx07haAE1uotBnmdp65jptX0C3w/ETkca+tYofqFQ0qVQYv9CodXDnTaXcLTAwuYOec/meOWMYX27Quf7DbHT5FncPHDM0v9pWdD9zsfNpiHhXN8/yOkn5nwL2dd11TkFioMpAQKhiQ8AAAAASUVORK5CYII="

class CPL():
    def __init__(self, path: str, log = None):
        self.path = path
        self.folder = os.path.dirname(path)
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.log = log

    def content(self) -> list[str]:
        with open(self.path, 'r', encoding='cp1252') as f:
            lines = f.readlines()
        return lines
    
    def get_revision(self) -> int:
        return int(open(self.path, 'r', encoding='cp1252').readlines()[0][118:120].strip())

    def set_revision(self, rev: int):
        with open(self.path, 'r', encoding='cp1252') as f:
            lines = f.readlines()
        lines[0] = f"{lines[0][:118]}{rev}{lines[0][120:]}"
        with open(self.path, 'w', encoding='cp1252') as f:
            f.writelines(lines)

    def increase_revision(self):
        self.set_revision(self.get_revision()+1)

    def decrease_revision(self):
        self.set_revision(self.get_revision()-1)

    def rename(self, new_name: str):
        try:
            with open(self.path, 'r', encoding='cp1252') as f:
                content = f.read()
            content = content.replace(self.name, new_name)
            with open(self.path, 'w', encoding='cp1252') as f:
                f.write(content)
        except Exception as e:
            (self.log.write if self.log else print)(f"- Erro ao editar arquivo CPL! - {str(type(e))[8:-2]}", "red", False)

        try:
            for file_name in os.listdir(self.folder):
                if (self.name in file_name and 
                   ".PDF" not in file_name.upper() and
                   ".DXF" not in file_name.upper() and
                   ".PLT" not in file_name.upper()):
                    new_file_name = file_name.replace(self.name, new_name)
                    old_path = os.path.join(self.folder, file_name)
                    new_path = os.path.join(self.folder, new_file_name)
                    os.rename(old_path, new_path)
        except Exception as e:
            (self.log.write if self.log else print)(f"- Erro ao renomear arquivo {file_name}! - {str(type(e))[8:-2]}", "red", False)

        self.name = new_name
        self.path = os.path.join(self.folder, f"{self.name}.CPL")

    @staticmethod
    def get_cpls(start_folder: str) -> list[CPL]:
        paths = []
        for root, dirs, files in os.walk(start_folder):
            paths.extend(os.path.join(root, file) for file in files if file.upper().endswith(".CPL"))
        return [CPL(path) for path in paths]
    
class CPLTreeApp:
    def __init__(self, tqs_path: str, selection_mode: int, master = None):
        self.tqs_path = tqs_path if os.path.exists(tqs_path) else ''

        self.master = master or tk.Tk()
        self.master.wm_withdraw()
        self.TQS_folder = tk.StringVar(value=self.tqs_path)
        self.selected_folder = tk.StringVar()
        self.selection_mode = selection_mode

        # Icons
        self.img_folder = tk.PhotoImage(data=folder_png_b64, width=20, height=16)
        self.img_conc = tk.PhotoImage(data=conc_png_b64, width=20, height=16)
        self.img_sheet = tk.PhotoImage(data=sheet_png_b64, width=20, height=16)

        self.master.title('Árvore de Plotagem TQS')
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

    def _get_tqs_building_paths(self, path: str, max_depth: int = 3) -> list[str]:
        all_folders = []
        for root, dirs, files in os.walk(path):
            current_depth = root.count(os.sep) - path.count(os.sep)
            if current_depth >= max_depth:
                del dirs[:]
                continue
            all_folders.extend(os.path.join(root, dir) for dir in dirs)

        return [dir for dir in all_folders if (os.path.exists(os.path.join(dir, 'EDIFICIO.BDE')) and self.has_cpl_files(dir))]

    def on_select(self, event):
        """Seleciona um projeto TQS"""
        with suppress(IndexError):
            if parent := self.tree.parent(self.tree.selection()[0]):
                if ((self.selection_mode == TREESELECTIONCPL_NOTBUILDINGS and os.path.basename(self.tree.selection()[0]).endswith(".CPL")) or 
                     self.selection_mode == TREESELECTIONCPL_ONLYBUILDINGS):
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
        projects = self._get_tqs_building_paths(self.tqs_path)
        
        self.tree.delete(*self.tree.get_children())

        # Insere a pasta raiz
        self.tree.insert('', 'end', iid=self.tqs_path, text=self.tqs_path, open=True)
        
        # Insere os projetos TQS
        path_depth = len(self.tqs_path.split(os.path.sep))
        for project in projects:
            project_name = os.path.splitext(os.path.basename(project))[0]
            project_split = project.split(os.path.sep)
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

            self.tree.insert(os.path.dirname(project),'end', project, text=project_name, image=self.img_conc)

        if self.selection_mode == TREESELECTIONCPL_ONLYBUILDINGS:
            return
        
        cpl_files = self.find_cpl_files(self.tqs_path)

        path_dict = {}
        for file_path in cpl_files:
            parts = file_path.replace(self.tqs_path, '').split(os.sep)
            parts = [p for p in parts if p]
            current_level = path_dict
            
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            current_level[parts[-1]] = file_path
        
        self._insert_tree_items(self.tqs_path, path_dict)


    def find_cpl_files(self, path: str) -> list[str]:
        """Encontra todos os arquivos .CPL na estrutura de pastas"""
        cpl_files = []
        for root, dirs, files in os.walk(path):
            cpl_files.extend(os.path.join(root, file) for file in files if file.lower().endswith('.cpl'))
        return cpl_files
    
    def has_cpl_files(self, path: str) -> bool:
        return next((True for _, _, files in os.walk(path) for file in files if file.lower().endswith('.cpl')), False)

    def _insert_tree_items(self, parent, items):
        """Método auxiliar para inserir itens na árvore recursivamente"""
        for name, value in items.items():
            if isinstance(value, dict):
                node_id = os.path.join(parent, name) if parent else name
                if not self.tree.exists(node_id):
                    self.tree.insert(parent, 'end', iid=node_id, text=name, image=self.img_folder)
                self._insert_tree_items(node_id, value)
            else:
                self.tree.insert(parent, 'end', iid=value, text=name, image=self.img_sheet)

    def find_folder(self):
        if projeto := tk.filedialog.askdirectory(mustexist = True, title = "Selecione a pasta de projetos TQS", initialdir = self.tqs_path):
            self.TQS_folder.set(projeto)
            self.update_tree()

def cpl_tree(initialdir: str = 'C:\\TQS', selection_mode = TREESELECTIONCPL_NOTBUILDINGS, master=None) -> str | None:
    cpl_tree_app = CPLTreeApp(initialdir, selection_mode, master)
    return cpl_tree_app.output

def cpl_tree_building(initialdir: str = 'C:\\TQS', master=None) -> str | None:
    cpl_tree_app = CPLTreeApp(initialdir, TREESELECTIONCPL_ONLYBUILDINGS, master)
    return cpl_tree_app.output