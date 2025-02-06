import pandas as pd
import csv

from collections import defaultdict
from random import shuffle

from tools import get_course_options, get_combinations_no_repeated_course_no_overlaps, schedule_to_df


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

    # Convert defaultdict to regular dictionary if needed
    # courses = dict(courses)

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

        # random suffle to the options so that each time we get different ones in different order
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
        # print(f"{major} - {semester}\n {options[f'{major} - {semester}']}\n")

    # Example to print the dictionary
    for key, value in options.items():
        try:
            horarios = [schedule_to_df(schedules) for schedules in value]
            # Check if horarios is empty or contains only empty dataframes
            if all(df.empty for df in horarios):
                raise ValueError(f"No se pudo obtener horarios para {key}")

            # Create an ExcelWriter object
            with pd.ExcelWriter(f"Out/OPCIONES PARA {key}.xlsx") as writer:
                # Write each dataframe to a separate sheet
                for idx, df in enumerate(horarios, start=1):
                    # Sheet names like Sheet1, Sheet2, etc.
                    sheet_name = f'Sheet{idx}'
                    df.to_excel(writer, sheet_name=sheet_name, index=True)

        except Exception as e:
            print(e)


def main():
    # ARCHIVOS
    planes_path = "Files\plan (primer semestre)_enero.csv"
    planta_path = "Files\Planta 2025-2 (1252) - Planta.csv"
    df = pd.read_csv(planta_path, encoding='utf-8')

    # Para no tomar horarios repetidos, usar CP y SC
    planta_df = df[df['SC - Sección Combinada'] != 'CH']
    planta_df.rename(columns={'ID\nCOURSE': 'ID COURSE'},  inplace=True)

    create_schedule_options(planes_path, planta_df)


if __name__ == "__main__":
    main()
