import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil

class FoldersCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folders Copy")
        self.data_file = "folders_data.json"
        self.editing_item = None
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Treeview
        self.tree = ttk.Treeview(self.main_frame, columns=("Name", "Target", "Source", "Source->Target", "Target->Source"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Target", text="Target Directory")
        self.tree.heading("Source", text="Source Directory")
        self.tree.heading("Source->Target", text="Source->Target")
        self.tree.heading("Target->Source", text="Target->Source")
        self.tree.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind double click event for inline editing
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=4, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.edit_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Execute", command=self.execute_copy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.close_app).pack(side=tk.LEFT, padx=5)
        
        # Load saved data
        self.load_data()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        
        if region == "cell" and item:
            # Get column number (1-based index)
            col_num = int(column[1]) - 1
            
            if col_num == 0:  # Name column
                self.edit_cell(item, col_num)
            elif col_num in [1, 2]:  # Target or Source directory
                self.browse_and_update(item, col_num)
            elif col_num in [3, 4]:  # Direction radio buttons
                self.toggle_direction(item, col_num)

    def edit_cell(self, item, column):
        # Get current value
        current_value = self.tree.item(item)['values'][column]
        
        # Create entry widget
        entry = ttk.Entry(self.tree)
        entry.insert(0, current_value)
        
        # Calculate position
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
        
        # Position entry widget
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        def save_edit(event=None):
            new_value = entry.get()
            values = list(self.tree.item(item)['values'])
            values[column] = new_value
            self.tree.item(item, values=values)
            entry.destroy()
        
        entry.focus_set()
        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)

    def browse_and_update(self, item, column):
        directory = filedialog.askdirectory()
        if directory:
            values = list(self.tree.item(item)['values'])
            values[column] = directory
            self.tree.item(item, values=values)

    def toggle_direction(self, item, column):
        values = list(self.tree.item(item)['values'])
        current_value = values[column]
        
        if current_value == "Yes":
            # 如果当前是Yes，点击后变为No
            values[column] = "No"
            self.tree.item(item, values=values)
        else:
            # 如果当前是No，点击后需要检查文件
            source_dir = values[2]  # Source directory
            target_dir = values[1]  # Target directory
            
            # 确定是哪个方向并进行相应的检查
            is_source_to_target = (column == 3)
            if self.compare_directories(source_dir, target_dir, is_source_to_target):
                # 用户确认或没有更新的文件，设置为Yes
                values[3] = "No"  # Reset Source->Target
                values[4] = "No"  # Reset Target->Source
                values[column] = "Yes"
                self.tree.item(item, values=values)

    def add_item(self):
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Add Item")
        # 确保窗口置顶的设置
        self.edit_window.transient(self.root)
        self.edit_window.grab_set()
        self.edit_window.focus_set()
        self.edit_window.resizable(False, False)
        self.create_edit_form()
        
    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Item")
        # 确保窗口置顶的设置
        self.edit_window.transient(self.root)
        self.edit_window.grab_set()
        self.edit_window.focus_set()
        self.edit_window.resizable(False, False)
        
        item = self.tree.item(selected[0])
        self.create_edit_form(item['values'])

    def compare_directories(self, source_dir, target_dir, source_to_target=True):
        """比较两个目录中文件的修改时间"""
        if not (os.path.exists(source_dir) and os.path.exists(target_dir)):
            return True  # 如果有目录不存在，允许复制
        
        newer_files_found = False
        check_dir = target_dir if source_to_target else source_dir
        
        # 遍历源目录中的所有文件
        for root, _, files in os.walk(source_dir):
            relative_path = os.path.relpath(root, source_dir)
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, relative_path, file)
                
                # 如果目标文件存在，比较修改时间
                if os.path.exists(target_file):
                    source_time = os.path.getmtime(source_file)
                    target_time = os.path.getmtime(target_file)
                    
                    # 检查是否有更新的文件
                    if source_to_target and target_time > source_time:
                        newer_files_found = True
                        break
                    elif not source_to_target and source_time > target_time:
                        newer_files_found = True
                        break
                    
            if newer_files_found:
                break
            
        if newer_files_found:
            direction = "目标文件夹" if source_to_target else "源文件夹"
            message = f"{direction} ({check_dir}) 中的文件更新，确定覆盖吗？"
            return messagebox.askyesno("确认覆盖", message)
        
        return True

    def create_edit_form(self, values=None):
        form = ttk.Frame(self.edit_window, padding="10")
        form.grid(row=0, column=0)
        
        # 在窗口关闭时释放grab
        self.edit_window.protocol("WM_DELETE_WINDOW", lambda: self.on_edit_window_close())
        
        # Name
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=tk.W)
        name_var = tk.StringVar(value=values[0] if values else "")
        name_entry = ttk.Entry(form, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Target Directory
        ttk.Label(form, text="Target Directory:").grid(row=1, column=0, sticky=tk.W)
        target_var = tk.StringVar(value=values[1] if values else "")
        target_entry = ttk.Entry(form, textvariable=target_var)
        target_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(form, text="Browse", command=lambda: self.browse_directory(target_var)).grid(row=1, column=2)
        
        # Source Directory
        ttk.Label(form, text="Source Directory:").grid(row=2, column=0, sticky=tk.W)
        source_var = tk.StringVar(value=values[2] if values else "")
        source_entry = ttk.Entry(form, textvariable=source_var)
        source_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(form, text="Browse", command=lambda: self.browse_directory(source_var)).grid(row=2, column=2)
        
        # Save button
        ttk.Button(form, text="Save",
                  command=lambda: self.save_item(name_var.get(), 
                                               target_var.get(), 
                                               source_var.get(),
                                               False,  # source_target 默认为 No
                                               False,  # target_source 默认为 No
                                               values)).grid(row=5, column=1, pady=10)

    def browse_directory(self, var):
        directory = filedialog.askdirectory(parent=self.edit_window)  # 指定父窗口
        if directory:
            var.set(directory)

    def on_edit_window_close(self):
        self.edit_window.grab_release()
        self.edit_window.destroy()
        
    def save_item(self, name, target, source, source_target, target_source, old_values=None):
        if not all([name, target, source]):
            messagebox.showwarning("Warning", "Name, Target and Source fields are required")
            return
            
        values = [
            name,
            target,
            source,
            "Yes" if source_target else "No",
            "Yes" if target_source else "No"
        ]
        
        if old_values:
            selected = self.tree.selection()[0]
            self.tree.item(selected, values=values)
        else:
            self.tree.insert("", tk.END, values=values)
            
        self.edit_window.destroy()
        
    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            self.tree.delete(selected)
            
    def save_data(self):
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            data.append({
                'name': values[0],
                'target': values[1],
                'source': values[2],
                'source_to_target': values[3] == "Yes",
                'target_to_source': values[4] == "Yes"
            })
            
        with open(self.data_file, 'w') as f:
            json.dump(data, f)
            
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    self.tree.insert("", tk.END, values=[
                        item['name'],
                        item['target'],
                        item['source'],
                        "Yes" if item.get('source_to_target', False) else "No",
                        "Yes" if item.get('target_to_source', False) else "No"
                    ])
        except FileNotFoundError:
            pass
            
    def execute_copy(self):
        total_items = len(self.tree.get_children())
        copied_items = 0
        failed_items = []
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            source_to_target = values[3]
            target_to_source = values[4]
            
            if source_to_target == target_to_source == "No":
                continue
                
            source_dir = values[2]
            target_dir = values[1]
            item_name = values[0]
            
            try:
                if source_to_target == "Yes":
                    self.copy_directory(source_dir, target_dir)
                elif target_to_source == "Yes":
                    self.copy_directory(target_dir, source_dir)
                copied_items += 1
            except Exception as e:
                failed_items.append((item_name, str(e)))
        
        # 显示复制完成的结果
        if failed_items:
            error_message = "以下项目复制失败:\n"
            for name, error in failed_items:
                error_message += f"- {name}: {error}\n"
            messagebox.showerror("复制完成", f"成功复制 {copied_items} 个目录\n{error_message}")
        else:
            if copied_items > 0:
                messagebox.showinfo("复制完成", f"成功复制 {copied_items} 个目录")
            else:
                messagebox.showinfo("提示", "没有需要复制的目录")
                
    def copy_directory(self, src, dst):
        if not os.path.exists(src):
            raise Exception("源目录不存在")
            
        try:
            # 遍历源目录中的所有文件和文件夹
            for root, dirs, files in os.walk(src):
                # 计算目标路径
                relative_path = os.path.relpath(root, src)
                dst_dir = os.path.join(dst, relative_path)
                
                # 创建目标目录（如果不存在）
                os.makedirs(dst_dir, exist_ok=True)
                
                # 复制文件
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_dir, file)
                    
                    # 如果目标文件存在，尝试删除
                    if os.path.exists(dst_file):
                        try:
                            os.chmod(dst_file, 0o777)  # 尝试更改文件权限
                            os.remove(dst_file)
                        except:
                            pass
                    
                    # 复制文件
                    try:
                        shutil.copy2(src_file, dst_file)
                    except PermissionError:
                        # 如果复制失败，再试一次
                        try:
                            os.chmod(os.path.dirname(dst_file), 0o777)  # 更改目录权限
                            shutil.copy2(src_file, dst_file)
                        except:
                            raise Exception(f"文件 {file} 被占用，无法复制")
                            
        except Exception as e:
            raise Exception(f"复制失败: {str(e)}")
            
    def close_app(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FoldersCopyApp(root)
    root.mainloop()