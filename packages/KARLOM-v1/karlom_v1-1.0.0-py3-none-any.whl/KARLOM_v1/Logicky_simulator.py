import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class LogicGate:
    def __init__(self, app, canvas, x, y, gate_type, move_callback, delete_callback):
        self.app = app
        self.canvas = canvas
        self.gate_type = gate_type
        self.x, self.y = x, y
        self.move_callback = move_callback
        self.delete_callback = delete_callback
        self.value = 0
        self.rect = canvas.create_rectangle(x, y, x+80, y+50, fill="lightgray", tags=("gate", f"gate_{id(self)}"))
        self.text = canvas.create_text(x+40, y+25, text=gate_type, tags=("gate", f"gate_{id(self)}"), anchor="center")
        self.value_text = None
        self.input_nodes = []
        self.output_nodes = []
        self.create_nodes()
        self.bind_events()
        # Přidat ovládání kolečkem myši pro vertikální scroll
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.last_expansion_right = 1000  # výchozí velikost scrollregionu vpravo
        self.last_expansion_bottom = 800  # výchozí velikost scrollregionu dolů

    def create_nodes(self):
        if self.gate_type == "VSTUP":
            self.output_nodes.append(self.canvas.create_oval(self.x+75, self.y+20, self.x+85, self.y+30, fill="black", tags="node"))
        elif self.gate_type == "VÝSTUP":
            self.input_nodes.append(self.canvas.create_oval(self.x-5, self.y+20, self.x+5, self.y+30, fill="black", tags="node"))
        elif self.gate_type == "NOT":
            self.input_nodes.append(self.canvas.create_oval(self.x-5, self.y+20, self.x+5, self.y+30, fill="black", tags="node"))
            self.output_nodes.append(self.canvas.create_oval(self.x+75, self.y+20, self.x+85, self.y+30, fill="black", tags="node"))
        else:
            for i in range(4):
                self.input_nodes.append(self.canvas.create_oval(self.x-5, self.y+5 + i*10, self.x+5, self.y+15 + i*10, fill="black", tags="node"))
            self.output_nodes.append(self.canvas.create_oval(self.x+75, self.y+20, self.x+85, self.y+30, fill="black", tags="node"))

    def bind_events(self):
        tags = [self.rect, self.text]
        if self.value_text:
            tags.append(self.value_text)
        for tag in tags:
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_start_drag)
            self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(tag, "<Button-3>", self.on_right_click)
        self.canvas.tag_bind(tag, "<Double-Button-1>", self.on_double_click)

    def on_start_drag(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def on_drag(self, event):
        if self.app.mode != "create":
            return
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.move(dx, dy)
        self.last_x = event.x
        self.last_y = event.y
        self.move_callback()

    def on_double_click(self, event):
        if self.gate_type not in ("VSTUP", "VÝSTUP"):
            return
        if self.app.mode != "create":
            return

        x, y = self.canvas.coords(self.text)

        self.entry = tk.Entry(self.canvas)
        self.entry.insert(0, self.canvas.itemcget(self.text, "text"))
        self.entry.focus()
        self.entry_window = self.canvas.create_window(self.x + 40, self.y + 25, window=self.entry, anchor="center")

        self.entry.bind("<Return>", self.save_new_label)
        self.entry.bind("<FocusOut>", self.save_new_label)

    def save_new_label(self, event):
        new_text = self.entry.get().strip()
        if not new_text:
            new_text = self.gate_type
        self.canvas.itemconfig(self.text, text=new_text)
        self.canvas.delete(self.entry_window)
        self.entry.destroy()
        self.entry = None

    def on_right_click(self, event):
        if self.app.mode == "create":
            self.delete_callback(self)

    def move(self, dx, dy):
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        if self.value_text:
            self.canvas.move(self.value_text, dx, dy)
        for node in self.input_nodes + self.output_nodes:
            self.canvas.move(node, dx, dy)
        self.x += dx
        self.y += dy

    def delete(self):
        self.canvas.delete(self.rect)
        self.canvas.delete(self.text)
        if self.value_text:
            self.canvas.delete(self.value_text)
        for node in self.input_nodes + self.output_nodes:
            self.canvas.delete(node)

    def toggle_input_value(self):
        if self.gate_type == "VSTUP":
            self.value = 1 - self.value
            if self.app.mode == "simulate":
                self.app.evaluate_all()

    def set_output_color(self):
        color = "red" if self.value == 1 else "lightgray"
        self.canvas.itemconfig(self.rect, fill=color)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # Ochranné meze: nedovolíme úplné opuštění pracovní plochy
        scrollregion = self.canvas.cget("scrollregion")
        left, top, right, bottom = map(int, scrollregion.split())

        max_x = right - 80  # blok je široký 80
        max_y = bottom - 50  # blok je vysoký 50

        new_x = min(new_x, max_x)
        new_y = min(new_y, max_y)

        actual_dx = new_x - self.x
        actual_dy = new_y - self.y

        self.canvas.move(self.rect, actual_dx, actual_dy)
        self.canvas.move(self.text, actual_dx, actual_dy)
        if self.value_text:
            self.canvas.move(self.value_text, actual_dx, actual_dy)
        for node in self.input_nodes + self.output_nodes:
            self.canvas.move(node, actual_dx, actual_dy)

        self.x = new_x
        self.y = new_y

        self.app.maybe_expand_canvas(self.x + 80, self.y + 50)

    def evaluate(self, inputs):
        # Získáme jen skutečně připojené vstupy (ignorujeme nepřipojené)
        inputs = [i for i in inputs if i is not None]

        if self.gate_type == "VSTUP":
            return self.value
        if self.gate_type == "NOT":
            return 0 if inputs and inputs[0] else 1
        if self.gate_type == "AND":
            return int(all(inputs)) if inputs else 0
        if self.gate_type == "OR":
            return int(any(inputs)) if inputs else 0
        if self.gate_type == "XOR":
            return int(sum(inputs) % 2 == 1)
        if self.gate_type == "NAND":
            return int(not all(inputs)) if inputs else 1
        if self.gate_type == "NOR":
            return int(not any(inputs)) if inputs else 1
        if self.gate_type == "NXOR":
            return int(sum(inputs) % 2 == 0)
        return 0

class LogicSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.mode = "create"

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side="top", fill="both", expand=True)

        self.sidebar = tk.Frame(self.main_frame, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Frame pro canvas a scrollbary
        self.canvas_container = tk.Frame(self.main_frame)
        self.canvas_container.pack(side="left", fill="both", expand=True)

        self.h_scroll = tk.Scrollbar(self.canvas_container, orient="horizontal")
        self.h_scroll.pack(side="bottom", fill="x")

        self.v_scroll = tk.Scrollbar(self.canvas_container, orient="vertical")
        self.v_scroll.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.canvas_container, bg="white",
                                xscrollcommand=self.h_scroll.set,
                                yscrollcommand=self.v_scroll.set,
                                scrollregion=(0, 0, 1000, 800))
        self.canvas.pack(side="left", fill="both", expand=True)

        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

        self.bottom_frame = None

        self.create_mode_buttons()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.focus_set()
        self.canvas.tag_bind("node", "<Button-1>", self.on_node_click)

        self.gates = []
        self.connections = []
        self.selected_gate_type = None
        self.connection_start = None
        self.modified = False  # značí, že nejsou žádné neuložené změny
        self.manual_bends = {}
        self.connection_types = {} 

    def menu_save(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON soubory", "*.json")])
        if file_path:
            self.save_circuit(file_path)
            messagebox.showinfo("Uloženo", f"Obvod byl uložen do:\n{file_path}")

    def menu_load(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON soubory", "*.json")])
        if file_path:
            self.load_circuit(file_path)

    def create_mode_buttons(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        ttk.Label(self.sidebar, text="Bloky:").pack(pady=5)
        for gate_type in ["VSTUP", "VÝSTUP", "AND", "OR", "XOR", "NOT", "NAND", "NOR", "NXOR"]:
            ttk.Button(self.sidebar, text=gate_type, command=lambda g=gate_type: self.select_block(g)).pack(fill="x", padx=5, pady=2)

    def select_block(self, gate_type):
        self.selected_gate_type = gate_type

    def set_create_mode(self):
        self.mode = "create"

        if self.bottom_frame:
            self.bottom_frame.destroy()
            self.bottom_frame = None

        self.create_mode_buttons()  # obnovíme tlačítka

        self.sidebar.pack_forget()
        self.canvas_container.pack_forget()
        
        self.sidebar.pack(side="left", fill="y")
        self.canvas_container.pack(side="left", fill="both", expand=True)
        self.main_frame.pack(side="top", fill="both", expand=True)
        
        for gate in self.gates:
            if gate.gate_type == "VSTUP":
                gate.value = 0
                gate.set_output_color()
            else:
                gate.value = 0
                gate.set_output_color()

        for from_id, to_id, lines in self.connections:
            for line in lines:
                self.canvas.itemconfig(line, fill="black")

        self.canvas.config(bg="white")
        self.modified = False

    def reset_circuit(self):
        for gate in self.gates:
            gate.delete()
        self.gates.clear()
        for _, _, lines in self.connections:
            for line in lines:
                self.canvas.delete(line)
        self.connections.clear()
        self.modified = False

    def set_simulate_mode(self):
        self.mode = "simulate"

        self.sidebar.pack_forget()
        self.canvas.pack_forget()
        self.main_frame.pack_forget()

        self.main_frame.pack(side="top", fill="both", expand=True)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.create_bottom_bar()

        self.canvas.config(bg="lightyellow")
        self.selected_gate_type = None
        self.connection_start = None

        self.evaluate_all()

    def create_bottom_bar(self):
        if self.bottom_frame:
            self.bottom_frame.destroy()

        self.bottom_frame = tk.Frame(self.root, height=100)
        self.bottom_frame.pack(side="bottom", fill="x")

        self.bottom_canvas = tk.Canvas(self.bottom_frame, height=100)
        self.bottom_canvas.pack(side="top", fill="x", expand=False)

        self.scrollbar = tk.Scrollbar(self.bottom_frame, orient="horizontal", command=self.bottom_canvas.xview)
        self.scrollbar.pack(side="bottom", fill="x")
        self.bottom_canvas.configure(xscrollcommand=self.scrollbar.set)

        self.bottom_content = tk.Frame(self.bottom_canvas)
        self.bottom_canvas.create_window((0, 0), window=self.bottom_content, anchor="nw")

        self.input_blocks = []
        self.output_blocks = []

        # Řádek pro vstupy (popisek + bloky)
        input_row = tk.Frame(self.bottom_content)
        input_row.pack(side="top", anchor="w", pady=2)
        input_label = tk.Label(input_row, text="Vstupy:", font=("Arial", 10, "bold"))
        input_label.pack(side="left", padx=(5, 10))

        # Řádek pro výstupy (popisek + bloky)
        output_row = tk.Frame(self.bottom_content)
        output_row.pack(side="top", anchor="w", pady=2)
        output_label = tk.Label(output_row, text="Výstupy:", font=("Arial", 10, "bold"))
        output_label.pack(side="left", padx=(5, 10))

        for gate in self.gates:
            if gate.gate_type not in ["VSTUP", "VÝSTUP"]:
                continue

            frame = tk.Frame(bd=1, relief="solid", padx=5, pady=5)
            label = tk.Label(frame, text=self.canvas.itemcget(gate.text, "text"))
            label.pack()

            if gate.gate_type == "VSTUP":
                color = "red" if gate.value else "lightgray"
                frame.config(bg=color)
                frame.bind("<Button-1>", lambda e, g=gate, f=frame: self.toggle_input_from_bar(g, f))
                label.bind("<Button-1>", lambda e, g=gate, f=frame: self.toggle_input_from_bar(g, f))
                frame.pack(in_=input_row, side="left", padx=5)
                self.input_blocks.append((gate, frame))
            else:
                color = "red" if gate.value else "lightblue"
                frame.config(bg=color)
                frame.pack(in_=output_row, side="left", padx=5)
                self.output_blocks.append((gate, frame))

        self.bottom_content.update_idletasks()
        self.bottom_canvas.configure(scrollregion=self.bottom_canvas.bbox("all"))

    def toggle_input_from_bar(self, gate, frame):
        gate.value = 1 - gate.value
        gate.set_output_color()
        color = "red" if gate.value else "lightgray"
        frame.config(bg=color)
        self.evaluate_all()
        self.update_bottom_bar()

    def update_bottom_bar(self):
        for gate, frame in self.input_blocks:
            color = "red" if gate.value else "lightgray"
            frame.config(bg=color)
        for gate, frame in self.output_blocks:
            color = "red" if gate.value else "lightblue"
            frame.config(bg=color)

    # Funkce pro uložení a načtení obvodu
    def save_circuit(self, filepath=None):
        if filepath:
            self.current_save_path = filepath
        elif self.current_save_path:
            filepath = self.current_save_path
        else:
            return
        gates_data = [{"type": gate.gate_type, "x": gate.x, "y": gate.y, "label": self.canvas.itemcget(gate.text, "text")} for gate in self.gates]
        connections_data = []
        for from_id, to_id, _ in self.connections:
            for i, g in enumerate(self.gates):
                if from_id in g.output_nodes:
                    from_gate = i
                    from_node = g.output_nodes.index(from_id)
                if to_id in g.input_nodes:
                    to_gate = i
                    to_node = g.input_nodes.index(to_id)
            connections_data.append({
                "from_gate": from_gate,
                "from_node": from_node,
                "to_gate": to_gate,
                "to_node": to_node
            })
        with open(filepath, "w") as f:
            json.dump({"gates": gates_data, "connections": connections_data}, f, indent=2)
        self.modified = False


    def load_circuit(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
    
        for gate in self.gates:
            gate.delete()
        self.gates.clear()
        for _, _, lines in self.connections:
            for line in lines:
                self.canvas.delete(line)
        self.connections.clear()
    
        for gate_data in data["gates"]:
            gate = LogicGate(self, self.canvas, gate_data["x"], gate_data["y"], gate_data["type"], self.update_connections, self.delete_gate)
            if "label" in gate_data:
                self.canvas.itemconfig(gate.text, text=gate_data["label"])
            self.gates.append(gate)
    
        for conn in data["connections"]:
            from_gate = self.gates[conn["from_gate"]]
            to_gate = self.gates[conn["to_gate"]]
            from_id = from_gate.output_nodes[conn["from_node"]]
            to_id = to_gate.input_nodes[conn["to_node"]]
            self.add_connection(from_id, to_id)
    
        self.adjust_scrollregion_to_fit_gates()  # ← přidat tuto řádku
        self.update_connections()
        self.modified = False

    
    def on_canvas_click(self, event):
        if self.mode == "create":
            if self.selected_gate_type:
                x = self.canvas.canvasx(event.x)
                y = self.canvas.canvasy(event.y)
                x = self.canvas.canvasx(event.x)
                y = self.canvas.canvasy(event.y)
                gate = LogicGate(self, self.canvas, x, y, self.selected_gate_type, self.update_connections, self.delete_gate)
                self.gates.append(gate)
                self.selected_gate_type = None
                self.modified = True
                self.maybe_expand_canvas(event.x + 85, event.y + 100)  # <-- přidáno
            return

        if self.mode == "simulate":
            clicked = event.widget.find_withtag("current")
            if not clicked:
                return
            clicked_id = clicked[0]
            for gate in self.gates:
                if gate.gate_type == "VSTUP" and (gate.rect == clicked_id or gate.text == clicked_id or (gate.value_text and gate.value_text == clicked_id)):
                    gate.toggle_input_value()
                    self.update_bottom_bar()
                    break
                
    def delete_gate(self, gate):
        nodes_to_remove = gate.input_nodes + gate.output_nodes
        to_remove = [c for c in self.connections if c[0] in nodes_to_remove or c[1] in nodes_to_remove]
        for connection in to_remove:
            for line in connection[2]:
                self.canvas.delete(line)
            self.connections.remove(connection)
        gate.delete()
        self.gates.remove(gate)
        self.modified = True 

    def delete_connection(self, lines):
        if self.mode != "create":
            return
        for line in lines:
            self.canvas.delete(line)
        self.connections = [c for c in self.connections if c[2] != lines]
        self.modified = True 

    def on_node_click(self, event):
        if self.mode != "create":
            return

        node_id = event.widget.find_withtag("current")[0]

        if not self.connection_start:
            # Pokud klikám poprvé, node musí být výstupní
            is_output = any(node_id in g.output_nodes for g in self.gates)
            if is_output:
                self.connection_start = (node_id, event.x, event.y)
            return

        from_id, x1, y1 = self.connection_start
        to_id = node_id

        # směr propojení – musí být výstup → vstup
        from_is_output = any(from_id in g.output_nodes for g in self.gates)
        to_is_input = any(to_id in g.input_nodes for g in self.gates)
        if not (from_is_output and to_is_input):
            self.connection_start = None
            return

        # kontrola: vstup už připojen
        for existing in self.connections:
            if existing[1] == to_id:
                self.connection_start = None
                return

        self.add_connection(from_id, to_id)
        self.connection_start = None

    def add_connection(self, from_id, to_id):
        x0, y0 = self.canvas.coords(from_id)[0:2]
        x1, y1 = self.canvas.coords(to_id)[0:2]
        x0c, y0c = x0 + 5, y0 + 5
        x1c, y1c = x1 + 5, y1 + 5

        offset = 20
        lines = []
        conn_type = None

        mid_y = (y0c + y1c) // 2
        mid_x = (x0c + x1c) // 2

        if x1c > x0c:
            line1 = self.canvas.create_line(x0c, y0c, mid_x, y0c, fill="black", width=2)
            line2 = self.canvas.create_line(mid_x, y0c, mid_x, y1c, fill="black", width=2)
            line3 = self.canvas.create_line(mid_x, y1c, x1c, y1c, fill="black", width=2)
            lines = [line1, line2, line3]
            conn_type = 3
        else:
            line1 = self.canvas.create_line(x0c, y0c, x0c + offset, y0c, fill="black", width=2)
            line2 = self.canvas.create_line(x0c + offset, y0c, x0c + offset, mid_y, fill="black", width=2)
            line3 = self.canvas.create_line(x0c + offset, mid_y, x1c - offset, mid_y, fill="black", width=2)
            line4 = self.canvas.create_line(x1c - offset, mid_y, x1c - offset, y1c, fill="black", width=2)
            line5 = self.canvas.create_line(x1c - offset, y1c, x1c, y1c, fill="black", width=2)
            lines = [line1, line2, line3, line4, line5]
            conn_type = 5

        for line in lines:
            self.canvas.tag_bind(line, "<Button-3>", lambda e, l=lines: self.delete_connection(l))

        if conn_type == 3:
            self.canvas.tag_bind(lines[1], "<ButtonPress-1>", lambda e, l=lines[1]: self.on_vertical_drag_start(e, l))
            self.canvas.tag_bind(lines[1], "<B1-Motion>", self.on_vertical_drag)
        elif conn_type == 5:
            for idx in [1, 2, 3]:
                self.canvas.tag_bind(lines[idx], "<ButtonPress-1>", lambda e, l=lines[idx]: self.on_vertical_drag_start(e, l))
                self.canvas.tag_bind(lines[idx], "<B1-Motion>", self.on_vertical_drag)

        self.connections.append((from_id, to_id, lines))
        for line in lines:
            self.manual_bends[line] = None
        self.connection_types[tuple(lines)] = conn_type
        self.modified = True

    def update_connections(self):
        offset = 20
        recreate = []
        to_delete = []

        for from_id, to_id, lines in self.connections:
            x0, y0 = self.canvas.coords(from_id)[0:2]
            x1, y1 = self.canvas.coords(to_id)[0:2]
            x0c, y0c = x0 + 5, y0 + 5
            x1c, y1c = x1 + 5, y1 + 5

            desired_type = 3 if x1c > x0c else 5
            current_type = self.connection_types.get(tuple(lines), desired_type)

            if desired_type != current_type:
                to_delete.append(lines)
                recreate.append((from_id, to_id))
                continue

            mid_y = (y0c + y1c) // 2
            mid_x = (x0c + x1c) // 2

            if len(lines) == 3:
                new_x = mid_x
                if self.manual_bends[lines[1]]:
                    axis, val = self.manual_bends[lines[1]]
                    if axis == 'x':
                        new_x = val
                self.canvas.coords(lines[0], x0c, y0c, new_x, y0c)
                self.canvas.coords(lines[1], new_x, y0c, new_x, y1c)
                self.canvas.coords(lines[2], new_x, y1c, x1c, y1c)

            elif len(lines) == 5:
                x_static_left = x0c + offset
                x_static_right = x1c - offset
                y_static = mid_y

                if self.manual_bends[lines[1]]:
                    axis, val = self.manual_bends[lines[1]]
                    if axis == 'x':
                        x_static_left = val
                if self.manual_bends[lines[2]]:
                    axis, val = self.manual_bends[lines[2]]
                    if axis == 'y':
                        y_static = val
                if self.manual_bends[lines[3]]:
                    axis, val = self.manual_bends[lines[3]]
                    if axis == 'x':
                        x_static_right = val

                self.canvas.coords(lines[0], x0c, y0c, x_static_left, y0c)
                self.canvas.coords(lines[1], x_static_left, y0c, x_static_left, y_static)
                self.canvas.coords(lines[2], x_static_left, y_static, x_static_right, y_static)
                self.canvas.coords(lines[3], x_static_right, y_static, x_static_right, y1c)
                self.canvas.coords(lines[4], x_static_right, y1c, x1c, y1c)

        for lines in to_delete:
            for line in lines:
                self.canvas.delete(line)
                if line in self.manual_bends:
                    del self.manual_bends[line]
            if tuple(lines) in self.connection_types:
                del self.connection_types[tuple(lines)]

        self.connections = [c for c in self.connections if c[2] not in to_delete]

        for from_id, to_id in recreate:
            self.add_connection(from_id, to_id)

    def evaluate_all(self):
        node_values = {}

        # Vstupy
        for gate in self.gates:
            if gate.gate_type == "VSTUP":
                for node in gate.output_nodes:
                    node_values[node] = gate.value
                gate.set_output_color()

        # Propojení
        connection_map = {}
        for from_id, to_id, _ in self.connections:
            connection_map[to_id] = from_id

        # Brány (AND, OR, atd.)
        # Více průchodů pro propagaci hodnot (řeší závislosti mezi branami)
        for _ in range(5):  # počet iterací můžeš upravit
            for gate in self.gates:
                if gate.gate_type in ["VSTUP", "VÝSTUP"]:
                    continue
                inputs = []
                for node in gate.input_nodes:
                    if node in connection_map:
                        source = connection_map[node]
                        inputs.append(node_values.get(source, None))  # pouze připojené
                    else:
                        inputs.append(None)
                gate.value = gate.evaluate(inputs)
                gate.set_output_color()
                for node in gate.output_nodes:
                    node_values[node] = gate.value

        # Výstupy
        for gate in self.gates:
            if gate.gate_type != "VÝSTUP":
                continue
            in_node = gate.input_nodes[0]
            value = 0
            if in_node in connection_map:
                source = connection_map[in_node]
                value = node_values.get(source, 0)
            gate.value = value
            gate.set_output_color()

        # Spoje (barvy)
        for from_id, to_id, lines in self.connections:
            value = node_values.get(from_id, 0)
            color = "red" if value else "black"
            for line in lines:
                self.canvas.itemconfig(line, fill=color)

    def on_vertical_drag(self, event):
        if self.mode != "create":
            return

        drag_id = self.canvas.find_withtag("current")
        if not drag_id:
            return
        drag_id = drag_id[0]

        for from_id, to_id, lines in self.connections:
            if drag_id in lines:
                idx = lines.index(drag_id)
                coords = self.canvas.coords(drag_id)

                if len(coords) == 4:
                    x0, y0, x1, y1 = coords
                    if x0 == x1:  # svislá čára
                        offset_x = event.x - x0
                        new_x = event.x
                        self.canvas.coords(drag_id, new_x, y0, new_x, y1)
                    else:  # vodorovná čára
                        offset_y = event.y - y0
                        new_y = event.y
                        self.canvas.coords(drag_id, x0, new_y, x1, new_y)

                    # Uprav i navazující segmenty:
                    if len(lines) == 3 and idx == 1:
                        self.canvas.coords(lines[0], self.canvas.coords(lines[0])[0], y0, new_x, y0)
                        self.canvas.coords(lines[2], new_x, y1, self.canvas.coords(lines[2])[2], y1)
                        self.manual_bends[lines[1]] = ('x', new_x)

                    elif len(lines) == 5:
                        if idx == 1:  # levá svislá
                            self.canvas.coords(lines[0], self.canvas.coords(lines[0])[0], y0, new_x, y0)
                            self.canvas.coords(lines[2], new_x, self.canvas.coords(lines[2])[1], self.canvas.coords(lines[2])[2], self.canvas.coords(lines[2])[3])
                            self.manual_bends[lines[1]] = ('x', new_x)
                        elif idx == 2:  # vodorovná
                            self.canvas.coords(lines[1], self.canvas.coords(lines[1])[0], self.canvas.coords(lines[1])[1], self.canvas.coords(lines[1])[2], new_y)
                            self.canvas.coords(lines[3], self.canvas.coords(lines[3])[0], new_y, self.canvas.coords(lines[3])[2], self.canvas.coords(lines[3])[3])
                            self.manual_bends[lines[2]] = ('y', new_y)
                        elif idx == 3:  # pravá svislá
                            self.canvas.coords(lines[2], self.canvas.coords(lines[2])[0], self.canvas.coords(lines[2])[1], new_x, self.canvas.coords(lines[2])[3])
                            self.canvas.coords(lines[4], new_x, self.canvas.coords(lines[4])[1], self.canvas.coords(lines[4])[2], self.canvas.coords(lines[4])[3])
                            self.manual_bends[lines[3]] = ('x', new_x)
                break

    def maybe_expand_canvas(self, x, y):
        margin = 100
        block_width = 80
        block_height = 50

        self.canvas.update_idletasks()

        current_region = self.canvas.cget("scrollregion")
        if current_region:
            left, top, right, bottom = map(int, current_region.split())
        else:
            left, top, right, bottom = 0, 0, self.last_expansion_right, self.last_expansion_bottom

        expand_right = False
        expand_bottom = False

        if x + block_width + margin > right:
            self.last_expansion_right = right + self.canvas.winfo_width()
            expand_right = True

        if y + block_height + margin > bottom:
            self.last_expansion_bottom = bottom + self.canvas.winfo_height()
            expand_bottom = True

        if expand_right:
            self.canvas.config(scrollregion=(left, top, self.last_expansion_right, bottom))
        elif expand_bottom:
            self.canvas.config(scrollregion=(left, top, right, self.last_expansion_bottom))

    def adjust_scrollregion_to_fit_gates(self):
            max_x = 1000
            max_y = 800
            for gate in self.gates:
                max_x = max(max_x, gate.x + 80 + 100)  # šířka + okraj
                max_y = max(max_y, gate.y + 50 + 100)  # výška + okraj
            self.last_expansion_right = max_x
            self.last_expansion_bottom = max_y
            self.canvas.config(scrollregion=(0, 0, max_x, max_y))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simulátor logických obvodů se spodní lištou")
    app = LogicSimulatorApp(root)
    root.mainloop()