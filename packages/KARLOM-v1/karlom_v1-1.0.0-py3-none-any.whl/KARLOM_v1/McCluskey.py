import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product

def count_ones(term):
    return term.count('1')

def combine_terms(a, b):
    diff = 0
    combined = []
    for x, y in zip(a, b):
        if x != y:
            diff += 1
            combined.append('-')
        else:
            combined.append(x)
    return ''.join(combined) if diff == 1 else None

def get_prime_implicants(minterms, num_vars):
    terms = sorted(set(format(m, f'0{num_vars}b') for m in minterms))
    unchecked = [(t, [int(t, 2)]) for t in terms]
    prime_implicants = []
    while unchecked:
        new_unchecked = []
        used = set()
        for i in range(len(unchecked)):
            for j in range(i + 1, len(unchecked)):
                comb = combine_terms(unchecked[i][0], unchecked[j][0])
                if comb:
                    combined_minterms = sorted(set(unchecked[i][1] + unchecked[j][1]))
                    new_unchecked.append((comb, combined_minterms))
                    used.update([i, j])
        for k, item in enumerate(unchecked):
            if k not in used:
                prime_implicants.append(item)
        seen = set()
        unique_new = []
        for term in new_unchecked:
            key = (term[0], tuple(term[1]))
            if key not in seen:
                seen.add(key)
                unique_new.append(term)
        unchecked = unique_new
    return prime_implicants

def get_pi_chart(prime_implicants, minterms):
    chart = {m: [] for m in minterms}
    for pi, covers in prime_implicants:
        for m in covers:
            if m in chart:
                chart[m].append(pi)
    return chart

def get_essential_pis(chart):
    essential = set()
    for m, pis in chart.items():
        if len(pis) == 1:
            essential.add(pis[0])
    return list(essential)

def term_to_expression(term, var_names):
    expr = ''
    for bit, var in zip(term, var_names):
        if bit == '1': expr += var
        elif bit == '0': expr += var + "'"
    return expr or '1'

def solve_with_petrick(chart, essential, minterms, var_names):
    remaining = set(m for m in minterms if not any(pi in essential for pi in chart[m]))
    if not remaining:
        return essential
    covers = []
    for m in remaining:
        covers.append(chart[m])
    all_combos = product(*covers)
    unique_combos = []
    seen = set()
    for combo in all_combos:
        uniq = tuple(sorted(set(combo)))
        if uniq not in seen:
            seen.add(uniq)
            unique_combos.append(uniq)

    # Vyber nejkratší kombinaci podle délky logického výrazu
    def combo_length(combo):
        exprs = [term_to_expression(t, var_names) for t in combo]
        return sum(len(e) for e in exprs), exprs

    best = min(unique_combos, key=combo_length)
    return list(sorted(set(essential).union(best)))

def mccluskey(minterms, num_vars):
    var_names = [chr(ord('A') + i) for i in range(num_vars)]
    prime_implicants = get_prime_implicants(minterms, num_vars)
    chart = get_pi_chart(prime_implicants, minterms)
    essential = get_essential_pis(chart)
    final_pis = solve_with_petrick(chart, essential, minterms, var_names)
    expression = ' + '.join(term_to_expression(t, var_names) for t in final_pis)
    return expression, final_pis

# === GUI ===
def minimize_action():
    try:
        minterms = list(map(int, entry_minterms.get().strip().split(',')))
        num_vars = int(entry_vars.get().strip())
        if any(m >= 2 ** num_vars for m in minterms):
            raise ValueError("Některý minterm přesahuje rozsah proměnných.")
        simplified, implicants = mccluskey(minterms, num_vars)
        var_names = [chr(ord('A') + i) for i in range(num_vars)]
        expr = f"f({', '.join(var_names)}) = {simplified}"
        imp_list = '\n'.join(sorted(implicants))
        text_result.config(state='normal')
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, expr + "\n\nPoužité prime implicanty:\n" + imp_list)
        text_result.config(state='disabled')
    except Exception as e:
        messagebox.showerror("Chyba", f"Nastala chyba: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quine-McCluskey Minimalizace")
    root.geometry("580x420")
    root.resizable(False, False)
    
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Zadej minterm hodnoty (oddělené čárkou):").pack(anchor="w")
    entry_minterms = ttk.Entry(frame, width=60)
    entry_minterms.insert(0, "0,1,2,5,6,7,8,9,10")
    entry_minterms.pack(pady=5)
    
    ttk.Label(frame, text="Počet vstupních proměnných:").pack(anchor="w")
    entry_vars = ttk.Entry(frame, width=10)
    entry_vars.insert(0, "4")
    entry_vars.pack(pady=5)
    
    ttk.Button(frame, text="Minimalizovat", command=minimize_action).pack(pady=10)
    
    text_result = tk.Text(frame, height=10, font=("Courier", 13), state='disabled', bg="#f8f8f8")
    text_result.pack(fill="both", expand=True, pady=5)
    
    root.mainloop()
