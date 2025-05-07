import warnings
def combina_cpp_and_py(cpp_code: str, py_code: str, use_double: bool=True) -> str:
    """
    Ensure that no "\'''" or "\""\"" in your c++ code and no "#endif" in your python code.
    """
    if '"""' in cpp_code or "'''" in cpp_code:
        warnings.warn("the code may be wrong due to the \'\'\' or \"\"\" in cpp_code",
                      SyntaxWarning)
    if '#endif' in py_code:
        warnings.warn("the code may be wrong due to '#endif' in py_code",
                      SyntaxWarning)
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
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title)
    return file_path

def read_file(file_path):
    if not file_path:
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
    """
    Open the file and combine to new file.
    First open cpp then py.
    If the system is not windows, it may doesn't work.
    """
    import tkinter as tk
    from tkinter import messagebox
    
    cpp_path = select_file("Choose cpp file")
    if not cpp_path:
        return
    
    py_path = select_file("Choose py file")
    if not py_path:
        return
    
    cpp_code = read_file(cpp_path)
    py_code = read_file(py_path)
    
    if cpp_code is None or py_code is None:
        messagebox.showerror("Error", "Cannot read the file.")
        return
    
    combined_code = combina_cpp_and_py(cpp_code, py_code, use_double)
    
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
        
