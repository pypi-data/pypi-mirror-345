from tkinter import Menu, filedialog, messagebox

posledni_cesta_ulozeni = None  # globální proměnná

def soubor_menu(root, prepni_na_tvoreni_callback, get_simulator_app):
    """Funkce pro vytvoření záložky 'Soubor' s dynamickým získáním aktuálního simulator_app."""

    def novy_soubor():
        simulator_app = get_simulator_app()
        if simulator_app:
            global posledni_cesta_ulozeni
            if messagebox.askyesno("Uložit soubor", "Chcete před vytvořením nového obvodu uložit změny?"):
                if posledni_cesta_ulozeni:
                    simulator_app.save_circuit(posledni_cesta_ulozeni)
                    simulator_app.current_save_path = posledni_cesta_ulozeni
                    messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{posledni_cesta_ulozeni}")
                else:
                    soubor = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("Obvody", "*.json"), ("Všechny soubory", "*.*")]
                    )
                    if soubor:
                        simulator_app.save_circuit(soubor)
                        simulator_app.current_save_path = soubor
                        messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{soubor}")
                        posledni_cesta_ulozeni = soubor
                    else:
                        if not messagebox.askyesno("Pokračovat bez uložení", "Soubor nebyl uložen.\nOpravdu chcete pokračovat?"):
                            return
            # V každém případě vytvoříme nový
            # Resetujeme pracovní plochu a vytvoříme nový
            simulator_app.reset_circuit()
            prepni_na_tvoreni_callback()
            posledni_cesta_ulozeni = None

    def otevrit_soubor():
        global posledni_cesta_ulozeni
        simulator_app = get_simulator_app()
        soubor = filedialog.askopenfilename(
            filetypes=[("Obvody", "*.json"), ("Všechny soubory", "*.*")]
        )
        if soubor and simulator_app:
            simulator_app.load_circuit(soubor)
            posledni_cesta_ulozeni = soubor  # načtený soubor zapamatujeme

    def ulozit_soubor():
        global posledni_cesta_ulozeni
        simulator_app = get_simulator_app()
        if simulator_app:
            if posledni_cesta_ulozeni:
                simulator_app.save_circuit(posledni_cesta_ulozeni)
                simulator_app.current_save_path = posledni_cesta_ulozeni  # ← přidat tuto řádku
                messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{posledni_cesta_ulozeni}")
            else:
                ulozit_jako()

    def ulozit_jako():
        global posledni_cesta_ulozeni
        simulator_app = get_simulator_app()
        if simulator_app:
            soubor = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Obvody", "*.json"), ("Všechny soubory", "*.*")]
            )
            if soubor:
                simulator_app.save_circuit(soubor)
                simulator_app.current_save_path = soubor  # ← TATO ŘÁDKA
                messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{soubor}")
                posledni_cesta_ulozeni = soubor


    def ukoncit_aplikaci():
        potvrzeni_ukonceni()

    def potvrzeni_ukonceni():
        simulator_app = get_simulator_app()
        if simulator_app:
            global posledni_cesta_ulozeni

            if not simulator_app.modified:
                if messagebox.askyesno("Potvrzení ukončení", "Opravdu chcete ukončit aplikaci?"):
                    root.destroy()
                return

            # Uživatel má neuložené změny
            if messagebox.askyesno("Uložit soubor", "Chcete před ukončením aplikace uložit změny?"):
                if posledni_cesta_ulozeni:
                    simulator_app.save_circuit(posledni_cesta_ulozeni)
                    simulator_app.current_save_path = posledni_cesta_ulozeni
                    messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{posledni_cesta_ulozeni}")
                    root.destroy()
                    return
                else:
                    soubor = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("Obvody", "*.json"), ("Všechny soubory", "*.*")]
                    )
                    if soubor:
                        simulator_app.save_circuit(soubor)
                        simulator_app.current_save_path = soubor
                        messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{soubor}")
                        posledni_cesta_ulozeni = soubor
                        root.destroy()
                        return
                    else:
                        if messagebox.askyesno("Potvrzení ukončení", "Soubor nebyl uložen.\nOpravdu chcete ukončit aplikaci bez uložení?"):
                            root.destroy()
                        return

        # Fallback – když není `simulator_app`
        if messagebox.askyesno("Potvrzení ukončení", "Opravdu chcete ukončit aplikaci?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", potvrzeni_ukonceni)

    soubor_menu_obj = Menu(root, tearoff=0)
    soubor_menu_obj.add_command(label="Nový", command=novy_soubor)
    soubor_menu_obj.add_command(label="Otevřít", command=otevrit_soubor)
    soubor_menu_obj.add_command(label="Uložit", command=ulozit_soubor)
    soubor_menu_obj.add_command(label="Uložit jako", command=ulozit_jako)
    soubor_menu_obj.add_separator()
    soubor_menu_obj.add_command(label="Ukončit", command=ukoncit_aplikaci)

    return soubor_menu_obj

# Umožní volání zvenku přes Aplikace_L.py
def ulozit_soubor_externi(get_simulator_app):
    global posledni_cesta_ulozeni
    simulator_app = get_simulator_app()
    if simulator_app:
        if posledni_cesta_ulozeni:
            simulator_app.save_circuit(posledni_cesta_ulozeni)
            simulator_app.current_save_path = posledni_cesta_ulozeni
            messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{posledni_cesta_ulozeni}")
        else:
            soubor = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Obvody", "*.json"), ("Všechny soubory", "*.*")]
            )
            if soubor:
                simulator_app.save_circuit(soubor)
                simulator_app.current_save_path = soubor
                messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{soubor}")
                posledni_cesta_ulozeni = soubor

def novy_soubor_externi(get_simulator_app, prepni_na_tvoreni_callback):
    simulator_app = get_simulator_app()
    if simulator_app:
        global posledni_cesta_ulozeni

        # Pokud nebyly provedeny změny → rovnou nový obvod
        if not getattr(simulator_app, "modified", True):
            simulator_app.reset_circuit()  # ← tohle musí být tady!
            prepni_na_tvoreni_callback()
            posledni_cesta_ulozeni = None
            return

        # Jinak se zeptáme na uložení
        if messagebox.askyesno("Uložit soubor", "Chcete před vytvořením nového obvodu uložit změny?"):
            if posledni_cesta_ulozeni:
                simulator_app.save_circuit(posledni_cesta_ulozeni)
                simulator_app.current_save_path = posledni_cesta_ulozeni
                messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{posledni_cesta_ulozeni}")
            else:
                soubor = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("Obvody", "*.json"), ("Všechny soubory", "*.*")]
                )
                if soubor:
                    simulator_app.save_circuit(soubor)
                    simulator_app.current_save_path = soubor
                    messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{soubor}")
                    posledni_cesta_ulozeni = soubor
                else:
                    if not messagebox.askyesno("Pokračovat bez uložení", "Soubor nebyl uložen.\nOpravdu chcete pokračovat?"):
                        return

        # Provedeme reset
        simulator_app.reset_circuit()
        prepni_na_tvoreni_callback()
        posledni_cesta_ulozeni = None



