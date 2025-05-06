import tkinter as tk

widgets = {} 

def make_window(window_name):
    root = tk.Tk()
    root.title(window_name)
    return root

def make_label(label_text="Hello World", label_height=2, label_width=30, label_number=None):
    label = tk.Label(
        text=label_text,
        font=("Arial", 15),
        bg="lightgray",
        height=label_height,
        width=label_width
    )
    label.grid(row=label_number + 1, column=0)
    widgets[f"label_{label_number}"] = label 
    return label

def make_button(button_text="Click Me", button_height=2, button_width=30, button_number=None, button_command=None):
    button = tk.Button(
        text=button_text,
        font=("Arial", 15),
        bg="lightgray",
        height=button_height,
        width=button_width,
        activebackground="blue",
        activeforeground="black",
        command=button_command if button_command else lambda: print("Button clicked!")
    )
    button.grid(row=button_number + 1, column=0)
    widgets[f"button_{button_number}"] = button 
    return button

def make_entry(entry_text="Enter text here", entry_width=30, entry_number=None):
    entry = tk.Entry(
        font=("Arial", 15),
        bg="lightgray",
        width=entry_width
    )
    entry.insert(0, entry_text)  
    entry.grid(row=entry_number + 1, column=0)
    widgets[f"entry_{entry_number}"] = entry 
    return entry

def get_output(entry_number):
    entry = widgets.get(f"entry_{entry_number}")
    if entry:
        return entry.get()
    return None

def last_code():
    tk.mainloop()