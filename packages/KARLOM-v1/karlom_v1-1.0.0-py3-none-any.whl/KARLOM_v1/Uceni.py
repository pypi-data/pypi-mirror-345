from tkinter import Tk, Canvas, Frame, Button, Label, Menu, Toplevel
from itertools import product  

def otevrit_okno_funkce(root, funkce_nazev, operace, default_vystup=0, pocet_vstupu=2):
    vstupy_stavy = {}  
    propojeni_grafika = {}  
    radky_tabulky = []
    
    def prepnout_vstup(event, index):
        aktualni_stav = vstupy_stavy[index]
        novy_stav = 1 if aktualni_stav == 0 else 0
        vstupy_stavy[index] = novy_stav
        barva = "red" if novy_stav == 1 else "lightgray"
        canvas.itemconfig(vstupy_grafika[index], fill=barva)
        for line in propojeni_grafika[index]:
            canvas.itemconfig(line, fill=barva)
        aktualizovat_logickou_operaci()
    
    def zobraz_tabulku_a_grafiku(vstupy):
        for widget in frame_tabulky.winfo_children():  
            widget.destroy()
        header = [chr(65 + i) for i in range(vstupy)] + ["Y"]
        for col, text in enumerate(header):
            Label(frame_tabulky, text=text, borderwidth=1, relief="solid", width=10).grid(row=0, column=col)
        
        radky_tabulky.clear()
        
        for row, kombinace in enumerate(product([0, 1], repeat=vstupy)):
            radek = []
            for col, hodnota in enumerate(kombinace):
                lbl = Label(frame_tabulky, text=str(hodnota), borderwidth=1, relief="solid", width=10)
                lbl.grid(row=row+1, column=col)
                radek.append(lbl)
            vystup = operace(*kombinace)
            lbl_vystup = Label(frame_tabulky, text=str(vystup), borderwidth=1, relief="solid", width=10)
            lbl_vystup.grid(row=row+1, column=vstupy)
            radek.append(lbl_vystup)
            radky_tabulky.append(radek)
        
        vykreslit_schématický_návrh(vstupy)
        aktualizovat_logickou_operaci()
    
    def aktualizovat_logickou_operaci():
        hodnoty = [vstupy_stavy[i] for i in sorted(vstupy_stavy)]
        vysledek = operace(*hodnoty)
        
        barva = "red" if vysledek == 1 else "lightgray"
        canvas.itemconfig(gate_grafika, fill=barva)
        canvas.itemconfig(vystup_grafika, fill=barva)

        for i, stav in enumerate(hodnoty):
            nova_barva = "red" if stav == 1 else "gray"
            for line in propojeni_grafika[i]:
                canvas.itemconfig(line, fill=nova_barva)
        
        vystup_barva = "red" if vysledek == 1 else "gray"
        for line in propojeni_grafika['vystup']:
            canvas.itemconfig(line, fill=vystup_barva)
        
        for radek in radky_tabulky:
            radek_barva = "white"
            if hodnoty == [int(lbl.cget("text")) for lbl in radek[:-1]]:
                radek_barva = "lightcoral"
            for lbl in radek:
                lbl.config(bg=radek_barva)
    
    def vykreslit_schématický_návrh(vstupy):
        canvas.delete("all")
        vstupy_pozice = [(50, 50 + i * 50) for i in range(vstupy)]
        gate_x, gate_y = 200, 95
        vystup_pozice = (350, 120)

        global vstupy_grafika, gate_grafika, vystup_grafika
        vstupy_grafika = {}
        propojeni_grafika.clear()

        for i, (x, y) in enumerate(vstupy_pozice):
            rect = canvas.create_rectangle(x, y, x + 50, y + 50, fill="lightgray")
            canvas.create_text(x + 25, y + 25, text=chr(65 + i))
            vstupy_grafika[i] = rect
            vstupy_stavy[i] = 0
            canvas.tag_bind(rect, "<Button-1>", lambda event, index=i: prepnout_vstup(event, index))
            
            propojeni_grafika[i] = [
                canvas.create_line(x + 50, y + 25, x + 100, y + 25, width=2, fill="gray"),
                canvas.create_line(x + 100, y + 25, x + 100, gate_y + 25 + i * 20, width=2, fill="gray"),
                canvas.create_line(x + 100, gate_y + 25 + i * 20, gate_x, gate_y + 25 + i * 20, width=2, fill="gray")
            ]
        
        gate_grafika = canvas.create_rectangle(gate_x, gate_y, gate_x + 100, gate_y + 100, fill="red" if default_vystup else "lightgray")
        canvas.create_text(gate_x + 50, gate_y + 50, text=funkce_nazev)
        
        propojeni_grafika['vystup'] = [
            canvas.create_line(gate_x + 100, gate_y + 50, gate_x + 125, gate_y + 50, width=2, fill="gray"),
            canvas.create_line(gate_x + 125, gate_y + 50, gate_x + 125, vystup_pozice[1] + 25, width=2, fill="gray"),
            canvas.create_line(gate_x + 125, vystup_pozice[1] + 25, vystup_pozice[0], vystup_pozice[1] + 25, width=2, fill="gray")
        ]
        vystup_grafika = canvas.create_rectangle(vystup_pozice[0], vystup_pozice[1], vystup_pozice[0] + 50, vystup_pozice[1] + 50, fill="lightgray")
        canvas.create_text(vystup_pozice[0] + 25, vystup_pozice[1] + 25, text="Y")
    
    top = Toplevel(root)
    top.title(f"{funkce_nazev} - Výběr vstupů")
    top.geometry("600x500")
    frame_tabulky = Frame(top)
    frame_tabulky.pack()
    canvas = Canvas(top, width=400, height=250, bg="white")
    canvas.pack()

    if funkce_nazev == "NOT":
        zobraz_tabulku_a_grafiku(1)
    else:
        button_frame = Frame(top)
        button_frame.pack()
        for vstupy in [2, 3, 4]:
            Button(button_frame, text=f"{vstupy} vstupy", command=lambda v=vstupy: zobraz_tabulku_a_grafiku(v)).pack(side="left", padx=5)

def uceni_menu(root):
    menu = Menu(root, tearoff=0)
    menu.add_command(label="AND", command=lambda: otevrit_okno_funkce(root, "AND", lambda *args: int(all(args))))
    menu.add_command(label="OR", command=lambda: otevrit_okno_funkce(root, "OR", lambda *args: int(any(args))))
    menu.add_command(label="XOR", command=lambda: otevrit_okno_funkce(root, "XOR", lambda *args: int(sum(args) % 2)))
    menu.add_command(label="NAND", command=lambda: otevrit_okno_funkce(root, "NAND", lambda *args: int(not all(args)), 1))
    menu.add_command(label="NOR", command=lambda: otevrit_okno_funkce(root, "NOR", lambda *args: int(not any(args)), 1))
    menu.add_command(label="NXOR", command=lambda: otevrit_okno_funkce(root, "NXOR", lambda *args: int(not (sum(args) % 2)), 1))
    menu.add_command(label="NOT", command=lambda: otevrit_okno_funkce(root, "NOT", lambda x: int(not x), 1, 1))

    return menu

if __name__ == "__main__":
    root = Tk()
    root.title("Logický simulátor")
    root.geometry("800x600")
    menu = uceni_menu(root)
    root.config(menu=menu)
    root.mainloop()
