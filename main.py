import csv
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from collections import defaultdict
from random import shuffle

from tools import get_course_options, get_combinations_no_repeated_course_no_overlaps, schedule_to_df

WINDOW_TITLE = 'Seleccionar archivos'
OK_BUTTON_TEXT = 'Generar horarios'
BROWSE_BUTTON_TEXT = 'Examinar'
FILES_DESCRIPTIONS = ['Archivo de planta:', 'Archivo de planes:']
DEBUG_MODE = True


def errorMessage(message):
    messagebox.askretrycancel(message)

def create_schedule_options(planes_path, planta_df):
    N = 10
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
        # obtener las materias del plan de estudios
        for course in value['required']:
            course_options = get_course_options(planta_df, course)
            semester_options.extend(course_options)
            if len(course_options):
                actual_count_of_required_courses_with_schedules += 1

        # for course in value['optional']:
        #   course_options = get_course_options(planta_df, course)
        #   semester_options.extend(course_options)

        # random shuffle to the options so that each time we get different ones in different order
        shuffle(semester_options)
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
            print(e)
    
    # Sort dictionary by the course name without the class section and by highest to lowest value
    sorted_counts = sorted(counts.items(), key=lambda x: ("".join(x[0].split()[1::]),x[1]), reverse=True)

    # Write to a text file
    with open("Out/occurrences.txt", "w", encoding="utf-8") as file:
        for key, value in sorted_counts:
            file.write(f"{key}: {value}\n")


def showFileSelector():
    selected_files = []

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
        nonlocal selected_files
        selected_files = [file_vars[i].get() for i in range(len(FILES_DESCRIPTIONS))]
        root.destroy()

    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Quieres cerrar el programa?"):
            root.destroy()

    root = tk.Tk()
    root.title(WINDOW_TITLE)

    file_vars = [tk.StringVar() for _ in range(len(FILES_DESCRIPTIONS))]

    for i, desc in enumerate(FILES_DESCRIPTIONS):
        tk.Label(root, text=desc).grid(row=i, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(root, textvariable=file_vars[i], width=50, state='readonly').grid(row=i, column=1, padx=5, pady=5)
        tk.Button(root, text=BROWSE_BUTTON_TEXT, command=lambda i=i: select_file(i)).grid(row=i, column=2, padx=5, pady=5)

    ok_button = tk.Button(root, text=OK_BUTTON_TEXT, command=on_ok, state=tk.DISABLED)
    ok_button.grid(row=len(FILES_DESCRIPTIONS), column=0, columnspan=3, pady=10)


    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

    return selected_files

def explorer_on_file(url):
    """ opens a windows explorer window """
    os.startfile(url)


def main():
    if DEBUG_MODE:
        planta_path = "Files/Planta/agosto/Planta 2025-1 (1248) - Planta.csv"
        planes_path = "Files/Planes/agosto/primer semestre - plan.csv"

        df = pd.read_csv(planta_path, encoding='utf-8')

        # Para no tomar horarios repetidos, usar CP y SC
        planta_df = df[df['SC - Sección Combinada'] != 'CH']
        planta_df.rename(columns={'ID\nCOURSE': 'ID COURSE'},  inplace=True)

        create_schedule_options(planes_path, planta_df)
        explorer_on_file("Out")
        
    else:
        files = showFileSelector()
        # ARCHIVOS
        if len(files) > 0:
            planta_path = files[0]
            planes_path = files[1]

            
            df = pd.read_csv(planta_path, encoding='utf-8')

            # Para no tomar horarios repetidos, usar CP y SC
            planta_df = df[df['SC - Sección Combinada'] != 'CH']
            planta_df.rename(columns={'ID\nCOURSE': 'ID COURSE'},  inplace=True)

            create_schedule_options(planes_path, planta_df)
            explorer_on_file("Out")
    
    



if __name__ == "__main__":
    main()
