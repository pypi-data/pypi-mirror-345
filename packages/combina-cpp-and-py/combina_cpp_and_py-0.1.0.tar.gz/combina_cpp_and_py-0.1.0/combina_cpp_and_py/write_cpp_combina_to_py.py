def combina_cpp_and_py(cpp_code: str, py_code: str, use_double: bool=True) -> str:
    if use_double:
        return f'''#if false
r"""
#endif
{cpp_code}
#if false
"""
{py_code}
#endif'''
    return f"""#if false
r'''
#endif
{cpp_code}
#if false
'''
{py_code}
#endif"""

def select_file(title):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.askopenfilename(title=title)
    return file_path

def read_file(file_path):
    if not file_path:  # 用户取消选择
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(content):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="save the combine code file",
        defaultextension=".py",
        filetypes=[("Python files", "*.py"), ("Cpp files", "*.cpp"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)        
        return True
    return False

def main(use_double=True):
    import tkinter as tk
    from tkinter import messagebox
    
    # 选择C++文件
    cpp_path = select_file("Choose cpp file")
    if not cpp_path:
        return
    
    # 选择Python文件
    py_path = select_file("Choose py file")
    if not py_path:
        return
    
    # 读取文件内容
    cpp_code = read_file(cpp_path)
    py_code = read_file(py_path)
    
    if cpp_code is None or py_code is None:
        messagebox.showerror("Error", "Cannot read the file.")
        return
    
    # 合并代码
    combined_code = combina_cpp_and_py(cpp_code, py_code, use_double)
    
    # 保存结果
    if save_file(combined_code):
        messagebox.showinfo("Success", "The code has been combined！")
    else:
        messagebox.showwarning("Cancel", "Saving has been canceled.")

if __name__ == '__main__':
    while True:
        a = input("Use double?(Y/n)")
        if a == 'Y':
            main(True)
            break
        elif a == 'n':
            main(False)
            break
        else:
            print('Invalid input!')
        
