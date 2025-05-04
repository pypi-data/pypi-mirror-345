import tkinter as tk
from tkinter import Menu, filedialog, messagebox
import subprocess
import os
import sys
from Logicky_simulator import LogicSimulatorApp
from PIL import Image, ImageTk
from Soubor import soubor_menu
from Soubor import posledni_cesta_ulozeni
from Uceni import uceni_menu  
from McCluskey import mccluskey

simulator_frame = None
simulator_app = None

def ensure_simulator_created():
    global simulator_frame, simulator_app
    if simulator_app is None:
        simulator_frame_create()

def simulator_frame_create():
    global simulator_frame, simulator_app
    if simulator_frame:
        simulator_frame.destroy()
    simulator_frame = tk.Frame(root)
    simulator_frame.pack(fill="both", expand=True)
    simulator_app = LogicSimulatorApp(simulator_frame)

def otevrit_obvod():
    ensure_simulator_created()
    file_path = filedialog.askopenfilename(filetypes=[("Obvody", "*.json")])
    if file_path:
        simulator_app.load_circuit(file_path)

def prepni_na_tvoreni():
    ensure_simulator_created()
    simulator_app.set_create_mode()

def prepni_na_simulaci():
    ensure_simulator_created()
    if simulator_app.gates:
        simulator_app.set_simulate_mode()

def spustit_kar_map():
    script_path = os.path.join(os.path.dirname(__file__), "kar_map.py")
    if os.path.exists(script_path):
        if sys.platform.startswith("win"):
            subprocess.Popen(["python", script_path], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["python3", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("Soubor kar_map.py nenalezen.")

def spustit_mccluskey():
    dialog = tk.Toplevel(root)
    dialog.title("McCluskey minimalizace")
    dialog.geometry("400x280")

    tk.Label(dialog, text="Mintermy (čísla oddělená čárkou):").pack(pady=5)
    entry_minterms = tk.Entry(dialog)
    entry_minterms.insert(0, "0,1,2,5,6,7,8,9,10")
    entry_minterms.pack()

    tk.Label(dialog, text="Počet proměnných:").pack(pady=5)
    entry_vars = tk.Entry(dialog)
    entry_vars.insert(0, "4")
    entry_vars.pack()

    result_box = tk.Text(dialog, height=8)
    result_box.pack(pady=10)

    def vypocet():
        try:
            minterms = list(map(int, entry_minterms.get().split(",")))
            num_vars = int(entry_vars.get())
            expression, implicants = mccluskey(minterms, num_vars)
            vars_str = ','.join([chr(ord('A') + i) for i in range(num_vars)])
            vysledek = f"f({vars_str}) = {expression}\nImplicanty: {', '.join(implicants)}"
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, vysledek)
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    tk.Button(dialog, text="Minimalizuj", command=vypocet).pack(pady=5)

def nova_akce():
    from Soubor import novy_soubor_externi
    novy_soubor_externi(lambda: simulator_app, prepni_na_tvoreni)

def otevrit_akce():
    otevrit_obvod()

def ulozit_akce():
    from Soubor import ulozit_soubor_externi
    ulozit_soubor_externi(lambda: simulator_app)

def show_tooltip(event, text):
    tooltip = tk.Toplevel()
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
    tooltip_label = tk.Label(tooltip, text=text, bg="yellow", relief=tk.SOLID, borderwidth=1)
    tooltip_label.pack()
    tooltip.deiconify()
    event.widget.tooltip = tooltip

def hide_tooltip(event):
    if hasattr(event.widget, 'tooltip'):
        event.widget.tooltip.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("KARLOM_v1")
    root.state("zoomed")

    # 1. Menu bar
    menu_bar = tk.Menu(root)
    menu_bar.add_cascade(label="Soubor", menu=soubor_menu(root, prepni_na_tvoreni, lambda: simulator_app))

    menu_bar.add_cascade(label="Učení", menu=uceni_menu(root))

    zjednoduseni_menu = tk.Menu(menu_bar, tearoff=0)
    zjednoduseni_menu.add_command(label="Karnaughova mapa", command=spustit_kar_map)
    zjednoduseni_menu.add_command(label="McCluskey", command=spustit_mccluskey)
    menu_bar.add_cascade(label="Zjednodušení", menu=zjednoduseni_menu)

    obvod_menu = tk.Menu(menu_bar, tearoff=0)
    obvod_menu.add_command(label="Otevřít", command=otevrit_obvod)
    obvod_menu.add_command(label="Režim tvoření", command=prepni_na_tvoreni)
    obvod_menu.add_command(label="Režim simulace", command=prepni_na_simulaci)
    menu_bar.add_cascade(label="Obvod", menu=obvod_menu)

    root.config(menu=menu_bar)

    # 2. Toolbar hned pod menu
    toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # 3. Simulator Frame (po Toolbaru)
    simulator_frame_create()

    # 4. Toolbar buttons
    BASE_DIR = os.path.dirname(__file__)
    image_path_1 = os.path.join(BASE_DIR, "images", "Novy_obvod.png")
    image_path_2 = os.path.join(BASE_DIR, "images", "Otevrit.png")
    image_path_3 = os.path.join(BASE_DIR, "images", "Ulozit.png")
    image_path_4 = os.path.join(BASE_DIR, "images", "Rezim_tvoreni.jpg")
    image_path_5 = os.path.join(BASE_DIR, "images", "Rezim_simulace.png")

    button_image_1 = ImageTk.PhotoImage(Image.open(image_path_1).resize((20, 20)))
    button_image_2 = ImageTk.PhotoImage(Image.open(image_path_2).resize((20, 20)))
    button_image_3 = ImageTk.PhotoImage(Image.open(image_path_3).resize((20, 20)))
    button_image_4 = ImageTk.PhotoImage(Image.open(image_path_4).resize((20, 20)))
    button_image_5 = ImageTk.PhotoImage(Image.open(image_path_5).resize((20, 20)))

    button_new = tk.Button(toolbar, image=button_image_1, command=nova_akce)
    button_new.pack(side=tk.LEFT, padx=2, pady=2)
    button_new.bind("<Enter>", lambda e: show_tooltip(e, "Nový obvod"))
    button_new.bind("<Leave>", hide_tooltip)

    button_open = tk.Button(toolbar, image=button_image_2, command=otevrit_akce)
    button_open.pack(side=tk.LEFT, padx=2, pady=2)
    button_open.bind("<Enter>", lambda e: show_tooltip(e, "Otevřít"))
    button_open.bind("<Leave>", hide_tooltip)

    button_save = tk.Button(toolbar, image=button_image_3, command=ulozit_akce)
    button_save.pack(side=tk.LEFT, padx=2, pady=2)
    button_save.bind("<Enter>", lambda e: show_tooltip(e, "Uložit"))
    button_save.bind("<Leave>", hide_tooltip)

    button_tvoreni = tk.Button(toolbar, image=button_image_4, command=prepni_na_tvoreni)
    button_tvoreni.pack(side=tk.LEFT, padx=2, pady=2)
    button_tvoreni.bind("<Enter>", lambda e: show_tooltip(e, "Režim tvoření"))
    button_tvoreni.bind("<Leave>", hide_tooltip)

    button_simulace = tk.Button(toolbar, image=button_image_5, command=prepni_na_simulaci)
    button_simulace.pack(side=tk.LEFT, padx=2, pady=2)
    button_simulace.bind("<Enter>", lambda e: show_tooltip(e, "Režim simulace"))
    button_simulace.bind("<Leave>", hide_tooltip)

    def ulozit_klavesou(event=None):
        ulozit_akce()

    root.bind("<Control-s>", ulozit_klavesou)

    # 5. Start aplikace
    root.mainloop()
