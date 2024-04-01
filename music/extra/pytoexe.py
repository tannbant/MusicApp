import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from cx_Freeze import setup, Executable
import os


def select_script_file():
    script_file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    if script_file_path:
        script_entry.delete(0, tk.END)
        script_entry.insert(0, script_file_path)


def select_output_dir():
    output_dir_path = filedialog.askdirectory()
    if output_dir_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_dir_path)


def convert_to_exe():
    script_path = script_entry.get()
    output_dir = output_entry.get()

    if not script_path or not output_dir:
        messagebox.showerror("Error", "Please select script file and output directory.")
        return

    base = None
    if os.name == "nt":
        base = "Win32GUI"

    setup(
        name="YourAppName",
        version="1.0",
        description="Description of your app",
        options={"build_exe": {"includes": [], "include_files": []}},
        executables=[Executable(script_path, base=base)]
    )

    build_dir = os.path.join(output_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    os.system("python setup.py build")
    messagebox.showinfo("Success", "Conversion completed successfully!")


# GUI setup
root = tk.Tk()
root.title("Python to Exe Converter")

script_label = tk.Label(root, text="Select Python script:")
script_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

script_entry = tk.Entry(root, width=50)
script_entry.grid(row=0, column=1, padx=5, pady=5)

script_button = tk.Button(root, text="Browse", command=select_script_file)
script_button.grid(row=0, column=2, padx=5, pady=5)

output_label = tk.Label(root, text="Select output directory:")
output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)

output_button = tk.Button(root, text="Browse", command=select_output_dir)
output_button.grid(row=1, column=2, padx=5, pady=5)

convert_button = tk.Button(root, text="Convert to Exe", command=convert_to_exe)
convert_button.grid(row=2, column=1, padx=5, pady=10)

root.mainloop()
