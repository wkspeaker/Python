import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime

last_col = 'Name'
reverse = False

def list_files(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files_info = [(f, datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(directory, f))).strftime('%Y-%m-%d %H:%M:%S'), os.path.splitext(f)[1], round(os.path.getsize(os.path.join(directory, f)) / 1048576, 2)) for f in files]
    return sorted(files_info, key=lambda x: x[0])  # initially sorted by name

def delete_files(directory, files):
    for file in files:
        os.remove(os.path.join(directory, file))

def select_directory():
    global directory
    directory = filedialog.askdirectory()
    refresh_directory()

def refresh_directory():
    files = list_files(directory)
    file_tree.delete(*file_tree.get_children())
    for file in files:
        file_tree.insert('', 'end', values=file)
    file_tree.heading(last_col, command=lambda: treeview_sort_column(file_tree, last_col, not reverse))
    treeview_sort_column(file_tree, last_col, reverse)

def delete_selected_files():
    global directory
    selected_files = file_tree.selection()
    selected_files = [file_tree.item(i)['values'][0] for i in selected_files]
    delete_files(directory, selected_files)
    messagebox.showinfo("Info", "Selected files have been deleted.")
    refresh_directory()

def treeview_sort_column(tv, col, rev):
    global last_col, reverse
    last_col = col
    reverse = rev
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

root = tk.Tk()
root.title("Please select a folder and review the files to delete")

directory_button = tk.Button(root, text="Select Directory", command=select_directory)
directory_button.pack()

file_tree = ttk.Treeview(root, columns=('Name', 'Modified Date', 'Extension', 'Size'), show='headings')
file_tree.heading('Name', text='Name', command=lambda: treeview_sort_column(file_tree, 'Name', False))
file_tree.heading('Modified Date', text='Modified Date', command=lambda: treeview_sort_column(file_tree, 'Modified Date', False))
file_tree.heading('Extension', text='Extension', command=lambda: treeview_sort_column(file_tree, 'Extension', False))
file_tree.heading('Size', text='Size (MB)', command=lambda: treeview_sort_column(file_tree, 'Size', False))

vsb = ttk.Scrollbar(root, orient="vertical", command=file_tree.yview)
hsb = ttk.Scrollbar(root, orient="horizontal", command=file_tree.xview)
file_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

file_tree.pack(side='left', fill='both', expand=True)
vsb.pack(side='right', fill='y')
hsb.pack(side='bottom', fill='x')

delete_button = tk.Button(root, text="Delete Selected Files", command=delete_selected_files)
delete_button.pack()

root.mainloop()