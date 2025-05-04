import tkinter as tk
from itertools import product

def generate_truth_table(num_vars):
    rows = list(product([0, 1], repeat=num_vars))
    return [[*row, 0] for row in rows]

def generate_kmap(num_vars):
    if num_vars == 2:
        return [[0, 1], [2, 3]]
    elif num_vars == 3:
        return [[0, 2, 6, 4], [1, 3, 7, 5]]
    else:
        return [[0, 1, 3, 2], [4, 5, 7, 6], [12, 13, 15, 14], [8, 9, 11, 10]]

def update_kmap(truth_table, kmap, num_vars, kmap_buttons):
    for row in truth_table:
        index = int("".join(map(str, row[:-1])), 2)
        for r, row_vals in enumerate(kmap):
            if index in row_vals:
                row_idx, col_idx = r, row_vals.index(index)
                kmap_buttons[row_idx][col_idx].config(text=str(row[-1]))
                break

def toggle_output_cell(r, c, truth_table, truth_buttons, kmap, num_vars, kmap_buttons):
    current = truth_table[r][c]
    new_val = {0: 1, 1: 'X', 'X': 0}[current]
    truth_table[r][c] = new_val
    truth_buttons[r][c].config(text=str(new_val))
    update_kmap(truth_table, kmap, num_vars, kmap_buttons)

def reset_truth_table(truth_table, truth_buttons, kmap, num_vars, kmap_buttons):
    for r, row in enumerate(truth_table):
        truth_table[r][-1] = 0
        truth_buttons[r][-1].config(text="0")
    update_kmap(truth_table, kmap, num_vars, kmap_buttons)

def find_prime_implicants(truth_table, num_vars):
    ones_positions = [idx for idx, row in enumerate(truth_table) if row[-1] == 1]
    dc_positions = [idx for idx, row in enumerate(truth_table) if row[-1] == 'X']
    valid_positions = ones_positions + dc_positions

    if not ones_positions:
        return "0", []

    variables = [chr(65 + i) for i in range(num_vars)]

    def index_to_binary(index):
        return list(format(index, f'0{num_vars}b'))


    def combine_terms(term1, term2):
        diff = 0
        combined = []
        for a, b in zip(term1, term2):
            if a != b:
                diff += 1
                combined.append('-')
            else:
                combined.append(a)
        return combined if diff == 1 else None

    terms = [(index_to_binary(i), frozenset([i]), False) for i in ones_positions] + \
            [(index_to_binary(i), frozenset([i]), True) for i in dc_positions]

    prime_implicants = set()
    while True:
        new_terms = []
        used = set()
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                combined = combine_terms(terms[i][0], terms[j][0])
                if combined:
                    new_terms.append((combined, terms[i][1] | terms[j][1], terms[i][2] and terms[j][2]))
                    used.add(i)
                    used.add(j)
        for idx, term in enumerate(terms):
            if idx not in used and not term[2]:  # only keep non-don't care terms
                prime_implicants.add((tuple(term[0]), term[1]))
        if not new_terms:
            break
        terms = new_terms

    prime_to_minterms = {}
    for term, covered_set in prime_implicants:
        covered = []
        for idx in ones_positions:
            binary = index_to_binary(idx)
            if all(t == '-' or t == str(b) for t, b in zip(term, binary)):
                covered.append(idx)
        if covered:
            prime_to_minterms[term] = covered

    essential_primes = set()
    uncovered = set(ones_positions)

    while True:
        added = False
        for m in list(uncovered):
            covering = [pi for pi, cover in prime_to_minterms.items() if m in cover]
            if len(covering) == 1:
                essential_primes.add(covering[0])
                uncovered -= set(prime_to_minterms[covering[0]])
                added = True
        if not added:
            break

    while uncovered:
        best_pi = None
        best_cover = []
        for pi, cover in prime_to_minterms.items():
            if pi in essential_primes:
                continue
            current_cover = [m for m in cover if m in uncovered]
            if len(current_cover) > len(best_cover):
                best_cover = current_cover
                best_pi = pi

        if best_pi:
            essential_primes.add(best_pi)
            uncovered -= set(prime_to_minterms[best_pi])
        else:
            break

    final_terms = []
    for term in essential_primes:
        minimized_term = "".join(
            f"{variables[i]}̅" if bit == '0' else f"{variables[i]}" if bit == '1' else ""
            for i, bit in enumerate(term)
        )
        if minimized_term:
            final_terms.append(minimized_term)

    return (" + ".join(sorted(final_terms)) if final_terms else "0"), []

def show_minimized_expression(truth_table, num_vars, result_label):
    minimized_expression = find_prime_implicants(truth_table, num_vars)
    result_label.config(text=f"Minimalizovaná rovnice: Y = {minimized_expression[0]}")

def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

def create_ui(main_frame, num_vars):
    for widget in main_frame.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))

    frame_main = tk.Frame(scrollable_frame)
    frame_main.pack(fill=tk.BOTH, expand=True)

    truth_table = generate_truth_table(num_vars)
    kmap = generate_kmap(num_vars)

    truth_frame = tk.Frame(frame_main)
    truth_frame.pack()

    variables = [chr(65 + i) for i in range(num_vars)]
    header = ["#"] + variables + [" ", "Y"]
    for c, label in enumerate(header):
        tk.Label(truth_frame, text=label, width=5, height=2, font=("Arial", 10, "bold")).grid(row=0, column=c)

    truth_buttons = []
    for r, row in enumerate(truth_table):
        row_buttons = []
        tk.Label(truth_frame, text=str(r), width=5, height=2, font=("Arial", 8)).grid(row=r+1, column=0)
        for c, val in enumerate(row):
            real_col = c + 1 if c < num_vars else c + 2
            if c == len(row) - 1:
                btn = tk.Button(truth_frame, text=str(val), width=5, height=2,
                                command=lambda r=r, c=c: toggle_output_cell(r, c, truth_table, truth_buttons, kmap, num_vars, kmap_buttons))
            else:
                btn = tk.Button(truth_frame, text=str(val), width=5, height=2,
                                state="disabled", disabledforeground="black")
            btn.grid(row=r+1, column=real_col)
            row_buttons.append(btn)
        truth_buttons.append(row_buttons)

    kmap_frame = tk.Frame(frame_main)
    kmap_frame.pack()

    row_labels = ["A̅B̅", "A̅B", "AB", "AB̅"] if num_vars == 4 else ["C̅", "C"] if num_vars == 3 else ["A̅", "A"]
    col_labels = ["C̅D̅", "C̅D", "CD", "CD̅"] if num_vars == 4 else ["A̅B̅", "A̅B", "AB", "AB̅"] if num_vars == 3 else ["B̅", "B"]

    tk.Label(kmap_frame, text=" ").grid(row=0, column=0)
    for c, label in enumerate(col_labels):
        tk.Label(kmap_frame, text=label, width=5, height=2).grid(row=0, column=c + 1)

    kmap_buttons = []
    for r, label in enumerate(row_labels):
        tk.Label(kmap_frame, text=label, width=5, height=2).grid(row=r + 1, column=0)
        row_buttons = []
        for c in range(len(col_labels)):
            btn = tk.Button(kmap_frame, text="0", width=5, height=2)
            btn.grid(row=r + 1, column=c + 1)
            row_buttons.append(btn)
        kmap_buttons.append(row_buttons)

    result_label = tk.Label(frame_main, text="", font=("Arial", 12, "bold"))
    result_label.pack()
    button_frame = tk.Frame(frame_main)
    button_frame.pack()

    minimize_button = tk.Button(button_frame, text="Minimalizovat", command=lambda: show_minimized_expression(truth_table, num_vars, result_label))
    minimize_button.pack(side=tk.LEFT, padx=5)

    reset_button = tk.Button(button_frame, text="Resetovat", command=lambda: reset_truth_table(truth_table, truth_buttons, kmap, num_vars, kmap_buttons))
    reset_button.pack(side=tk.LEFT, padx=5)

    update_kmap(truth_table, kmap, num_vars, kmap_buttons)

def main():
    root = tk.Tk()
    root.title("Řešení Karnaughovy mapy")
    root.geometry("600x600")

    menu = tk.Menu(root)
    root.config(menu=menu)

    table_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Vyber proměnné", menu=table_menu)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    table_menu.add_command(label="2 proměnné", command=lambda: create_ui(main_frame, 2))
    table_menu.add_command(label="3 proměnné", command=lambda: create_ui(main_frame, 3))
    table_menu.add_command(label="4 proměnné", command=lambda: create_ui(main_frame, 4))

    root.mainloop()

if __name__ == "__main__":
    main()
