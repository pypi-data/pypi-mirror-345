from __future__ import annotations
from tkinter import filedialog, Tk
from TQS.TQSJan import Window
from TQS.TQSEag import Eag, EAG_RUBLINEAR, EAG_RUBNAO, EAG_RUBRET_NAOPREEN 
from TQS import TQSEag
from tempfile import NamedTemporaryFile
from base64 import b64decode

from pytqs.drawning import TQSDrawning, TQSElementList, Line

def hex_to_rgb(hex_string: str):
  return tuple(int(hex_string.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

def icon() -> str:
    iconb64 = \
        '''
        AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAgBAAAAAAAAAAAAAAAAAAAAAAAAAQEAAQTTUTNVcyEjhTJQ43SmF5N088
        JTdTKgA3Uy4JN1MzDjdTJQU3Uy4gN0pmfTdTOBc3Uy4AN1MuBTdTOBM3UxwAN088PDdPXW83Uy4FN1MzDjdTMw43UzgcN1gcADdPU103T09TN1Mq
        ADdTLgk3UzMJN1IuDjhSHQo1ECAQEE42GTTkiSPm7oYT9eLNtvHhzbjy64cZ8uuFFPLriBry7IIO8uqMI/Lg3Njy5MGb8uyIG/LsiyLy7I0m8uyB
        CfLplTny4eHh8umpYvLshhXy7JEr8uyRLfLtgg3y5q9y8uDh4fLpmD3y64MP8uuHGfLrhhbx7oMM9dy3juZKYoQ0Uy4JN+6ED/Lv0K3/7N/R/vaT
        Jf/2ihH/9o4c//aJEP/2jx7/6+HX/+3StP/3jBb/95Ij//eVKv/3ihL/9Jcx/+vo5f/zvYH/94UJ//aRIf/3mDD/+IgN//GwaP/q7PD/9KhU//eH
        DP/2jRr/9o0Z//eFB/7xx5n/4eHh8lM4FzdTHAA34sis8evg0//0kyf99IkT/vSNG/70iBH+9I0c/unf1P7q1Lv+9IgQ/vSLGP71kyr+9YsX/vKV
        L/7p5+X+8L6G/vWKE/70jBn+9I8g/vWGDP7vrGL+5+zz/vGoV/71iA/+9Iwa/vSMGf71hAf+7MGS/err6//pljnxUyAAN0pheTfh08Ty9pkx//WN
        Gv70jBv/9IoV//SOHf/q3dD/6tW9//SJE//0ihT/9JIm//aSJP/zmjf/6ubj//HAiv/2jBf/9ZMo//SMGv/1hQj/8Kxg/+fs8v/xqlv/9owW//SN
        HP/0jRr/9YYL/+3Ajf/n6+/+9Js5/+yBC/JTMxM3T0EzN+yRLfL3kSH/9I4f/vSMGf/0jh3/6tvK/+rXwv/0ihX/9ZAf//WUKv/2lSr/9J08/+rl
        3//wwo//9osV//WVLP/0kyj/9ogP//GtYv/n7fP/8atf//aMGP/0kSP/9I4d//WIDv/uvYf/5+zw//KcPf73ixP/7I8o8lMzCTdTLgU37I0k8veV
        Kf/0jhz+9I0c/+rYxP/q28r/9ZEi//WTJv/1mDH/9pMl//SbOf/q5N3/8MWW//aMFv/1li3/9Zo2//eQH//xqlz/5+zy//GtY//2ixb/9ZYs//SR
        I//1iA//7rqB/+ft8//yo0v/9Y4a/veZMv/skCryUzMON1MzDjfslDDy9pIj//SMGP7q1r//6t3O//SLF//1kCD/9Zkz//aVK//1mjf/6+Tc//DF
        l//1hgz/9ZUr//WbN//3lSn/8qxe/+js8f/wr2j/9owX//WZMv/0liz/9YgO/++3ev/n7vb/8aBG//WJEP/1mDL+95kw/+2QKvJTMxM3UzwcN+yP
        KPL3jBb/6tO6/une0v/0jBr/9IkR//WVK//3mjX/9Zo3/+zj2f/wyp//9YYM//WSJf/1lSz/9o0Y//OnU//q7/T/8LBp//aJEv/1mzb/9Zkz//WI
        D//vtHT/5+72//GiS//1hAf/9JEj//abN/75ly7/5ruM8kpheTdTLgk364UV8u3Rsv/p4dj+9I8h//WNGv/1lSz/9ZIl//WYM//u4tX/8c6n//WK
        FP/1lCn/9ZYu//WMGf/zpE7/7PD0//C1c//1hgv/9JQp//WbNf/1ixT/77Jt/+jw+P/xplP/9ogO//WUKv/1lSr/9pAg/vDHm//j3tnyUzMON08c
        ADfhy7Dy6uTd/+uOJ/7tjB//7ZIt/+yKHv/riyH/7+LU/+7Prv/rfgX/7Ioe/+2RK//rhRT/7Z9J/+/09//rtHf/7H0C/+uHGf/riBr/64IO/+yt
        Z//r9Pz/6qZa/+2GE//tki3/7I4m/+uDEP/swJH+7eji/+OKKPJPHAA3T2F0N9vNu/Ldexf/2WsA/tp0Av/bdQP/3X8W/+rWwP/mxJz/2GgA/9hu
        Af/ZcAH/2nIA/+GUPf/t6eX/4KZn/9hlAP/ZcAL/2W8C/9lrAP/jpF//6uzt/92VR//YZgD/2XMC/9p1BP/bdQP/5LR//+fe0v7dfBj/0WUA8kou
        CTdPXWs32r6e8uC4iv/fvJT+4LyS/+C5jf/o1sH/8/b6/+jCl//mwJb/58Sb/+XBmP/kvZP/7unj/+/r5v/kuov/5cGZ/+XAmP/kv5X/5MGZ/+/x
        8//r4NP/4baG/+K/mP/ivZT/4buQ/+LDoP/u8/n/6M+z/uS6iv/bu5TyT0EzN09KSjfh5evy7PP8/+rx+P7t9Pv/7/b9//H0+P/x8PD/9/3+//n/
        ///2/f//8/n///T7///x8vP/7/Dw//L5///x+P//8vn///P5///x9///7u7u//Hz9P/x+f//7fT7/+30+//s8vr/7fP5//Dv7//x9fj+9Pv//+ft
        9PJPU1M3T09PN+De3vLq6Of/6efm/uzr6f/49/b////////////29fT/9PLx//Lw7//x8O7/8e/t//z7+////////Pv5//z7+f/49vT/9/b0//v6
        +P/29vX/7Ozr//Ty8P/8+vj/9/X0//j39f/7+fj/7+/v/+7t7f7y8e//4uDg81JSUjhPT0834ODg8urq6v/p6en++vr6/8HBwf98fHz/e3t7/8zM
        zP/6+vr/8fHx//T09P/6+vr/s7Oz/1tbW/8+Pj7/TU1N/6Ghof+0tLT/QkJC/21tbf/4+Pj/2dnZ/3BwcP87Ozv/PT09/3Z2dv/V1dX/8PDw/u3t
        7f/j4+PzYmJiPE9PTzff39/y7Ozs/+7u7v77+/v/zMzM/wMDA/8XFxf/29vb//j4+P/y8vL/+/v7/2xsbP8AAAD/JCQk/2JiYv8/Pz//AgIC/wQE
        BP8ICAj/NTU1/8vLy/8ZGRn/BAQE/0VFRf9BQUH/AgIC/xkZGf/Hx8f+8fHx/+Pj4/RtbW0/T09PN+Hh4fLx8fH/8PDw/vX19f/y8vL/EhIS/zMz
        M//5+fn/7+/v//////+ZmZn/AAAA/1xcXP/e3t7/3Nzc/5OTk/8CAgL/AAAA/2FhYf/X19f/PT09/wAAAP/IyMj////////////CwsL/AAAA/1xc
        XP74+Pj/4uLi9HJyckFPT0835eXl8vLy8v/w8PD+9vb2/+vr6/8NDQ3/Kysr//Pz8//09PT/9/f3/y0tLf8AAAD/7e3t/5qamv8BAQH/BAQE/4OD
        g/87Ozv/AAAA/9vb2//Nzc3/ODg4/9bW1v///////////9fX1/8AAAD/PDw8/vb29v/i4uL0bW1tP09PTzfm5uby8vLy//Dw8P719fX/6enp/w0N
        Df8sLCz/8/Pz//v7+//c3Nz/AAAA/zQ0NP/5+fn/+vr6/+fn5//n5+f//////3l5ef8AAAD/oqKi///////19fX/5eXl/7y8vP+FhYX/Kioq/wAA
        AP9vb2/+/f39/+Dg4PNfX187T09PN+bm5vLz8/P/8PDw/vLy8v/p6en/DQ0N/ywsLP/z8/P//Pz8/9bW1v8AAAD/Pj4+//r6+v/29vb//f39//f3
        9///////hISE/wAAAP+bm5v//////5iYmP8eHh7/AAAA/wEBAf8AAAD/UFBQ/+bm5v7x8fH/4eHh81VVVTlPT0835+fn8vLy8v/u7u7+8PDw/+jo
        6P8NDQ3/Kysr//Hx8f/19fX/6+vr/xEREf8gICD/7u7u//Pz8//29vb/8PDw//////9oaGj/AAAA/8XFxf/Gxsb/AAAA/wYGBv9HR0f/iIiI/8PD
        w//39/f/7+/v/u3t7f/j4+PzXFxcOlNTUzfl5eXy7u7u/+jo6P75+fn/8PDw/w4ODv8vLy///v7+//b29v/39/f/YGBg/wAAAP+vr6////////Pz
        8///////8PDw/xcXF/8YGBj//////46Ojv8AAAD/pqam////////////0NDQ/09PT//b29v+7+/v/+Li4vNfX187T09PN+Dg4PL09PT/WVlZ/pSU
        lP+lpaX/CAgI/x8fH/+1tbX/f39//3Fxcf/s7Oz/GRkZ/wsLC/+enp7/2NjY/8bGxv8/Pz//AAAA/6mpqf//////tra2/wAAAP9lZWX/0tLS/8nJ
        yf9bW1v/AAAA/5ubm/77+/v/4ODg81lZWTlPT0833t7e8vj4+P9ISEj+AQEB/xISEv8XFxf/FhYW/xQUFP8AAAD/ampq///////b29v/S0tL/wAA
        AP8JCQn/AAAA/yEhIf+1tbX//////+/v7//6+vr/i4uL/wYGBv8FBQX/AwMD/wsLC/+Kior/8PDw/uzs7P/g4ODzT09PN09PTzfg4ODy7Ozs/+bm
        5v7m5ub/5ubm/+bm5f/n5ub/6enp/+rq6f/u7u7/8PDw//f39///////4+Pj/8bGxv/W1tb/+/v7//7+/v/w8PD/7+/v/+7u7v/8/Pz/5eXl/729
        vf/BwcH/6Ojn//r6+v/q6ur+6urq/+Dg4PJPT083T09PN+Dg3/Lq6un/6+vq/u7t7f/v7u7/7+/v//Dw7//x8fH/8vLy//Lx8f/w8O//7u7t//Lx
        8f/9/f3////////////29vX/7u7t/+/v7v/v7u7/7u3t/+rq6f/w7+//9/b2//X19P/s6+v/5eXk/+jo5/7q6un/4ODf8k9PTzdPT0834OHk8urs
        7//o6uz+6evu/+rs7v/r7O//7O7x/+3v8v/t7/L/7vDy/+/x9P/09vn/9/n8//X3+f/09vj/9Pb5//Dy9f/v8fT/7/H0/+7w8//t7/H/7O3v/+rr
        7f/n6ev/5+nr/+fq7P/o6u3/6Ons/urs7v/g4eTyT09PN1U/JDnSj0Lz25RF/9qSQf3YijL+2o02/t2UQv7dkDr+3Y00/t+SO/7imUf+5JtJ/uSV
        Pv7kkzn+5pdA/uecRv7nlz7+55Y8/uiXPf7plzz+6ppA/uuaQf7snET+7qVU/u+qXf7vpVP+755D/vCcP/7xoUj99KhV/+meTfFPMxM3Wz0aO9B2
        EvTZeg//13gO/td0Bf/Zeg//2XUF/9hvAP/acwL/3n0Q/+CAFf/gfQ7/33YB/+J8Cf/kfw7/5HsH/+V5Av/mewP/6HwF/+qBDP/tiRn/7osc/++N
        H//ylC3/85Mp//KHEf/zhAr/9YkS//eSI/76lCX/74se8lMqADdTPBw3yHcb6NF/IvXQfyTx0Hob8s91EPLNbwTy0HIJ8tN8GvLVfh7y1n8e8tZ7
        FvLXfBby2X8Z8tl7EfLZeAzy23oO8t1/GfLfhSLy4Yop8uGMLPLjiify5Iwp8uaRM/LlhRry5oIS8ueGGvLpjyry65As8e6SLvXjiyvmTiwFNBAQ
        ABBIKwo1TTISOEouDjdKKgU3RiUAN0olADdKKgk3Si4ON0oqCTdKLgk3Si4JN0oqCTdKKgU3SioAN0oqBTdPKgU3TzMTN08zEzdPLg43Ty4JN08u
        DjdPMw43TzMON08qBTdPLgk3UzMON1MzDjdTMw43UjcSOFI1EzUQEAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
        '''
    with NamedTemporaryFile(suffix=".ico", delete=False) as tmp:
        icondata = b64decode(iconb64)
        tmp.write(icondata)
    return tmp.name

def get_file_path (title: str, filetypes: list[tuple[str, str]], initialdir: str ="") -> str:
    """
    Retorna o caminho para um arquivo.

    Abre uma janela do tkinter pedindo para o usuário selecionar um arquivo.

    Args:
        title (str) : Título da janela tkinter.
        filetypes (list) : Lista de formatos de arquivo aceitos. Ex:[("Arquivo PDF", "*.pdf"), ("Arquivo Word", "*.docx")]
        initialdir (str) : Diretório inicial.

    Returns:
        Caminho do arquivo selecionado.
    """
    window = Tk()
    window.withdraw()
    window.wm_iconbitmap(icon())
    window.wm_attributes('-topmost', 1)
    file_path = filedialog.askopenfilename(parent=window, initialdir=initialdir, title=title, filetypes=filetypes)
    window.destroy()

    return file_path

def select(tqsjan: Window, msg, selection_type= TQSEag.EAG_INORM) -> TQSElementList:
    eag = Eag.GetEag()
    eag.exec.Command("ID_ORTOGONAL")
    eag.exec.Command("ID_ORTOGONAL")
    addr, x, y, np, istat = eag.locate.Select(tqsjan, msg, selection_type)
    return TQSDrawning(dwg = tqsjan.dwg).filter({"addr": [addr]}) if istat == 0 else TQSElementList()

def select_multiple(tqsjan: Window, msg: str, selection_type= TQSEag.EAG_INORM) -> TQSElementList:
    eag = Eag.GetEag()
    eag.exec.Command("ID_ORTOGONAL")
    eag.exec.Command("ID_ORTOGONAL")
    eag.locate.Select(tqsjan, msg, selection_type)
    if eag.locate.BeginSelection(tqsjan) == 1:
        return TQSElementList()
    element_list = []
    while (element := eag.locate.NextSelection(tqsjan)):
        element_list.append(element)
    return TQSDrawning(dwg = tqsjan.dwg).filter({"addr": element_list})

def get_vector(tqsjan: Window, msg1: str = "Selecione o primeiro ponto: ", msg2: str = "Selecione o segundo ponto: ", rubber_line: bool = True) -> Line:
    eag = Eag.GetEag()
    _, x1, y1 = eag.locate.GetPoint(tqsjan, msg1)
    _, x2, y2 = eag.locate.GetSecondPoint(tqsjan, x1, y1, EAG_RUBLINEAR if rubber_line else EAG_RUBNAO, EAG_RUBRET_NAOPREEN, msg2)

    return Line(x1, y1, x2, y2)