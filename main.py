import csv
import os
import shutil
import random
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from collections import defaultdict
from random import shuffle
from pathlib import Path

from IntegerEntry import IntegerEntry
from tools import get_course_options, get_combinations_no_repeated_course_no_overlaps, schedule_to_df


WINDOW_TITLE = 'Seleccionar archivos'
OK_BUTTON_TEXT = 'Generar horarios'
BROWSE_BUTTON_TEXT = 'Examinar'
DELETE_BUTTON_TEXT = 'Borrar archivos'
FILES_DESCRIPTIONS = ['Archivo de planta:', 'Archivo de planes:']
DEBUG_MODE = True
OUT_PATH = 'Out/'
MAX_OPTIONS_PER_COURSE = 5


def errorMessage(message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    retry = messagebox.askretrycancel(
        "Error", message)  # Show the error message
    root.destroy()  # Destroy the root window after messagebox closes

    if retry:
        start_GUI()  # try again


def create_schedule_options(planes_path, planta_df, N):
    # Initialize the dictionary
    planes_academicos = defaultdict(lambda: {"required": [], "optional": []})

    # Read the CSV file
    with open(planes_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            major = row['Carrera']
            semester = int(row['SEM'])
            plan = row['Descripción']
            is_optional = row['OPTATIVA'] == 'OPTATIVO'

            # Add course to the appropriate list
            if is_optional:
                planes_academicos[(major, semester)]["optional"].append(plan)
            else:
                planes_academicos[(major, semester)]["required"].append(plan)

    # Initialize the dictionary to store options
    options = defaultdict(list)

    # Assuming planta_df is your DataFrame containing course information
    for [major, semester], value in planes_academicos.items():
        semester_options = []
        actual_count_of_required_courses_with_schedules = 0

        random.seed(hash(f"{major}-{semester}"))  # Semilla basada en el semestre

        # obtener las materias del plan de estudios
        for course in value['required']:
            course_options = get_course_options(planta_df, course)

            # random shuffle to the options so that each time we get different ones in different order
            shuffle(course_options)

            semester_options.extend(course_options[:MAX_OPTIONS_PER_COURSE])
            if len(course_options):
                actual_count_of_required_courses_with_schedules += 1

        # for course in value['optional']:
        #   course_options = get_course_options(planta_df, course)
        #   semester_options.extend(course_options)

        all_posibles_schedules = get_combinations_no_repeated_course_no_overlaps(
            semester_options, actual_count_of_required_courses_with_schedules)
        options[f"{major} - {semester}"] = []

        for i in range(N):
            try:
                options[f"{major} - {semester}"].append(
                    next(all_posibles_schedules))
            except:
                i -= 1

    counts = dict()
    # Example to print the dictionary
    for key, value in options.items():
        try:
            horarios = [schedule_to_df(schedules) for schedules in value]

            for v in value:
                for s in v:
                    course_key = f"{s.seccion} {s.nombre}"
                    counts[course_key] = counts.get(course_key, 0) + 1

            # Check if horarios is empty or contains only empty dataframes
            if all(df.empty for df in horarios):
                message = f"No se pudo obtener horarios para {key}"
                raise ValueError(message)

            # Create an ExcelWriter object
            with pd.ExcelWriter(f"Out/OPCIONES PARA {key}.xlsx") as writer:
                # Write each dataframe to a separate sheet
                for idx, df in enumerate(horarios, start=1):
                    # Sheet names like Sheet1, Sheet2, etc.
                    sheet_name = f'Sheet{idx}'
                    df.to_excel(writer, sheet_name=sheet_name, index=True)

        except Exception as e:
            errorMessage(str(e))  # Show error popup

    # Sort dictionary by the course name without the class section and by highest to lowest value
    sorted_counts = sorted(counts.items(), key=lambda x: (
        "".join(x[0].split()[1::]), x[1]), reverse=True)

    # Write to a text file
    with open("Out/occurrences.txt", "w", encoding="utf-8") as file:
        for key, value in sorted_counts:
            file.write(f"{key}: {value}\n")


def showFileSelector():
    selected_files = []
    n_value = 5
    was_error = False

    def select_file(index):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_vars[index].set(file_path)
            validate_selection()

    def validate_selection():
        if all(file_vars[i].get() for i in range(len(FILES_DESCRIPTIONS))):
            ok_button.config(state=tk.NORMAL)
        else:
            ok_button.config(state=tk.DISABLED)

    def on_ok():
        nonlocal selected_files, was_error
        selected_files = [file_vars[i].get()
                          for i in range(len(FILES_DESCRIPTIONS))]
        nonlocal n_value
        if n_entry.get() != "":
            n_value = int(n_entry.get())
        root.destroy()

        if n_value <= 0:
            was_error = True
            errorMessage("Ingresa un valor válido para los horarios")

    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Quieres cerrar el programa?"):
            root.destroy()

    def on_delete():
        for _, dirs, files in os.walk(OUT_PATH):
            for f in files:
                os.unlink(os.path.join(_, f))
            for d in dirs:
                shutil.rmtree(os.path.join(_, d))

        # Update the button state after deleting files
        if not os.listdir(OUT_PATH):  # Check if the folder is empty
            delete_button.config(state=tk.DISABLED)

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.focus()

    file_vars = [tk.StringVar() for _ in range(len(FILES_DESCRIPTIONS))]

    for i, desc in enumerate(FILES_DESCRIPTIONS):
        tk.Label(root, text=desc).grid(
            row=i, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(root, textvariable=file_vars[i], width=50, state='readonly').grid(
            row=i, column=1, padx=5, pady=5)
        tk.Button(root, text=BROWSE_BUTTON_TEXT, command=lambda i=i: select_file(
            i)).grid(row=i, column=2, padx=5, pady=5)

    n_entry = IntegerEntry(root, width=25)
    ok_button = tk.Button(root, text=OK_BUTTON_TEXT,
                          command=on_ok, state=tk.DISABLED)
    delete_button = tk.Button(root, text=DELETE_BUTTON_TEXT, command=on_delete)

    # Only if there are files available to delete
    if not os.listdir(OUT_PATH):
        delete_button.config(state=tk.DISABLED)

    delete_button.grid(row=len(FILES_DESCRIPTIONS)+2,
                       column=0, columnspan=3, pady=10)

    # place widgets on grid
    n_entry.grid(row=len(FILES_DESCRIPTIONS), column=0,
                 columnspan=3, pady=5, padx=3)
    ok_button.grid(row=len(FILES_DESCRIPTIONS)+1,
                   column=0, columnspan=3, pady=10)
    delete_button.grid(row=len(FILES_DESCRIPTIONS)+2,
                       column=0, columnspan=3, pady=10)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

    if was_error:
        return None, None
    return selected_files, n_value


def explorer_on_file(url):
    """ opens a windows explorer window """
    os.startfile(url)


def start_GUI():
    files, N = showFileSelector()
    # ARCHIVOS
    if files and len(files) > 0:
        planta_path = files[0]
        planes_path = files[1]

        df = pd.read_csv(planta_path, encoding='utf-8')

        # Para no tomar horarios repetidos, usar CP y SC
        planta_df = df[df['SC - Sección Combinada'] != 'CH']
        planta_df.rename(columns={'ID\nCOURSE': 'ID COURSE'},  inplace=True)

        create_schedule_options(planes_path, planta_df, N)
        explorer_on_file("Out")


def main():
    # Crea la carpeta de Out si es que no existe
    Path(OUT_PATH).mkdir(parents=True, exist_ok=True)

    if DEBUG_MODE:
        N = 5
        planta_path = "Files/Planta/agosto/Planta 2025-1 (1248) - Planta.csv"
        planes_path = "Files/Planes/agosto/primer semestre - plan.csv"

        df = pd.read_csv(planta_path, encoding='utf-8')

        # Para no tomar horarios repetidos, usar CP y SC
        planta_df = df[df['SC - Sección Combinada'] != 'CH']
        planta_df.rename(columns={'ID\nCOURSE': 'ID COURSE'},  inplace=True)

        create_schedule_options(planes_path, planta_df, N)
        explorer_on_file("Out")
    else:
        start_GUI()


if __name__ == "__main__":
    main()
