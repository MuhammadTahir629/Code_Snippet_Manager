import tkinter as tk
import sqlite3

# --- Track selected snippet ID and editing state ---
selected_snippet_id = None
is_editing = False

# --- Colors & Theme ---
DARK_BG = "#1e1e1e"
WIDGET_BG = "#2e2e2e"
ENTRY_BG = "#3c3f41"
HIGHLIGHT = "#00a15c"
TEXT_COLOR = "white"

# --- Create main window ---
window = tk.Tk()
window.title("Code Snippet Manager")
window.geometry("900x700")
window.configure(bg=DARK_BG)

# --- Database Setup ---
conn = sqlite3.connect("snippets.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    code TEXT,
    tags TEXT
)
""")
conn.commit()

# --- Styling Helpers ---
def style_entry(entry):
    entry.config(bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat",
                 font=("Segoe UI", 10), highlightbackground=HIGHLIGHT, highlightthickness=1)

def add_entry_hover_effects(entry):
    def on_enter(e): entry.config(highlightthickness=2)
    def on_leave(e): entry.config(highlightthickness=1)
    def on_focus_in(e): entry.config(bg="#4d4f52")
    def on_focus_out(e): entry.config(bg=ENTRY_BG)

    entry.bind("<Enter>", on_enter)
    entry.bind("<Leave>", on_leave)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def style_label(label):
    label.config(bg=WIDGET_BG, fg=TEXT_COLOR, font=("Segoe UI", 11, "bold"))

def style_button(button):
    button.config(bg="#007848", fg="white", activebackground="#005f36", relief="raised", bd=2,
                  font=("Segoe UI", 10, "bold"), padx=5, pady=3)
    button.bind("<Enter>", lambda e: button.config(bg="#00a15c"))
    button.bind("<Leave>", lambda e: button.config(bg="#007848"))
    button.bind("<ButtonPress-1>", lambda e: button.config(relief="sunken"))
    button.bind("<ButtonRelease-1>", lambda e: button.config(relief="raised"))

def style_text(text_widget):
    text_widget.config(bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat", bd=2,
                       font=("Courier New", 10), highlightbackground=HIGHLIGHT, highlightthickness=1)

def set_fields_state(state):
    title_entry.config(state=state)
    desc_entry.config(state=state)
    code_text.config(state=state)
    tags_entry.config(state=state)

# --- Functions ---
def save_snippet():
    title = title_entry.get()
    description = desc_entry.get()
    code = code_text.get("1.0", tk.END)
    tags = tags_entry.get()

    cursor.execute("INSERT INTO snippets (title, description, code, tags) VALUES (?, ?, ?, ?)",
                   (title, description, code, tags))
    conn.commit()

    clear_fields()
    load_snippets()

def save_changes():
    global selected_snippet_id
    if selected_snippet_id:
        title = title_entry.get()
        description = desc_entry.get()
        code = code_text.get("1.0", tk.END)
        tags = tags_entry.get()

        cursor.execute("""
            UPDATE snippets
            SET title = ?, description = ?, code = ?, tags = ?
            WHERE id = ?
        """, (title, description, code, tags, selected_snippet_id))
        conn.commit()

        clear_fields()
        load_snippets()
        save_changes_button.grid_remove()
        edit_button.grid(row=0, column=1, padx=5)

        global is_editing
        is_editing = False
        selected_snippet_id = None

def enable_editing():
    set_fields_state('normal')
    save_changes_button.grid(row=0, column=2, padx=5)
    edit_button.grid_remove()
    global is_editing
    is_editing = True

def delete_snippet():
    global selected_snippet_id
    if selected_snippet_id:
        cursor.execute("DELETE FROM snippets WHERE id = ?", (selected_snippet_id,))
        conn.commit()
        clear_fields()
        load_snippets()
        selected_snippet_id = None

def clear_fields():
    title_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    code_text.delete("1.0", tk.END)
    tags_entry.delete(0, tk.END)
    set_fields_state('normal')

def load_snippets():
    snippet_listbox.delete(0, tk.END)
    cursor.execute("SELECT id, title FROM snippets")
    for row in cursor.fetchall():
        snippet_listbox.insert(tk.END, f"{row[0]}. {row[1]}")

def show_snippet(event):
    global selected_snippet_id
    selected = snippet_listbox.curselection()
    if selected:
        index = selected[0]
        item = snippet_listbox.get(index)
        snippet_id = item.split(".")[0]
        selected_snippet_id = snippet_id

        cursor.execute("SELECT title, description, code, tags FROM snippets WHERE id=?", (snippet_id,))
        result = cursor.fetchone()

        if result:
            set_fields_state('normal')
            title_entry.delete(0, tk.END)
            title_entry.insert(0, result[0])
            desc_entry.delete(0, tk.END)
            desc_entry.insert(0, result[1])
            code_text.delete("1.0", tk.END)
            code_text.insert("1.0", result[2])
            tags_entry.delete(0, tk.END)
            tags_entry.insert(0, result[3])
            set_fields_state('disabled')
            save_changes_button.grid_remove()
            edit_button.grid(row=0, column=1, padx=5)

# --- Layout Containers ---
main_frame = tk.Frame(window, bg=DARK_BG)
main_frame.pack(fill="both", expand=True)

main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=2)
main_frame.rowconfigure(0, weight=1)

# --- Left Side: Add/Edit Snippet ---
form_frame = tk.LabelFrame(main_frame, text="Add / Edit Snippet", bg=WIDGET_BG, fg=TEXT_COLOR, font=("Segoe UI", 12, "bold"))
form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

title_label = tk.Label(form_frame, text="Snippet Title:")
style_label(title_label)
title_label.pack(pady=(10, 0), anchor="w")

title_entry = tk.Entry(form_frame, width=60)
style_entry(title_entry)
add_entry_hover_effects(title_entry)
title_entry.pack(pady=5)

desc_label = tk.Label(form_frame, text="Description:")
style_label(desc_label)
desc_label.pack(pady=(10, 0), anchor="w")

desc_entry = tk.Entry(form_frame, width=60)
style_entry(desc_entry)
add_entry_hover_effects(desc_entry)
desc_entry.pack(pady=5)

code_label = tk.Label(form_frame, text="Code:")
style_label(code_label)
code_label.pack(pady=(10, 0), anchor="w")

code_text = tk.Text(form_frame, height=10, width=60)
style_text(code_text)
add_entry_hover_effects(code_text)
code_text.pack(pady=5)

tags_label = tk.Label(form_frame, text="Tags (comma-separated):")
style_label(tags_label)
tags_label.pack(pady=(10, 0), anchor="w")

tags_entry = tk.Entry(form_frame, width=60)
style_entry(tags_entry)
add_entry_hover_effects(tags_entry)
tags_entry.pack(pady=5)

# --- Buttons ---
button_frame = tk.Frame(form_frame, bg=WIDGET_BG)
button_frame.pack(pady=10)

save_button = tk.Button(button_frame, text="Save Snippet", command=save_snippet)
style_button(save_button)
save_button.grid(row=0, column=0, padx=5)

edit_button = tk.Button(button_frame, text="Edit Snippet", command=enable_editing)
style_button(edit_button)
edit_button.grid(row=0, column=1, padx=5)

save_changes_button = tk.Button(button_frame, text="Save Changes", command=save_changes)
style_button(save_changes_button)
save_changes_button.grid(row=0, column=2, padx=5)
save_changes_button.grid_remove()

delete_button = tk.Button(button_frame, text="Delete Snippet", command=delete_snippet)
style_button(delete_button)
delete_button.grid(row=0, column=3, padx=5)

# --- Right Side: Saved Snippets List ---
list_frame = tk.LabelFrame(main_frame, text="Saved Snippets", bg=WIDGET_BG, fg=TEXT_COLOR, font=("Segoe UI", 12, "bold"))
list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

listbox_container = tk.Frame(list_frame, bg=WIDGET_BG)
listbox_container.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(listbox_container)
scrollbar.pack(side="right", fill="y")

snippet_listbox = tk.Listbox(listbox_container, width=30, height=25, bg=ENTRY_BG, fg=TEXT_COLOR, relief="flat", bd=2,
                             font=("Segoe UI", 10), selectbackground=HIGHLIGHT, selectforeground="white",
                             yscrollcommand=scrollbar.set)
snippet_listbox.pack(side="left", fill="both", expand=True)
snippet_listbox.bind("<<ListboxSelect>>", show_snippet)

scrollbar.config(command=snippet_listbox.yview)

# --- Load Data ---
load_snippets()

# --- Fade-In Animation ---
def fade_in(window, step=0.05):
    alpha = window.attributes('-alpha')
    if alpha < 1:
        alpha += step
        window.attributes('-alpha', alpha)
        window.after(20, lambda: fade_in(window, step))

window.attributes('-alpha', 0.0)
fade_in(window)

# --- Run App ---
window.mainloop()
