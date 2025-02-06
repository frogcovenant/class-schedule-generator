import pandas as pd
import numpy as np
import csv

from itertools import product
from datetime import datetime as dt, timedelta

from Materia import Materia
from Schedule import Schedule


# Herramientas
# Check if a combination of class options has overlapping schedules
def is_valid_schedule(combination):
    for i in range(len(combination)):
        for j in range(i + 1, len(combination)):
            if combination[i].overlaps(combination[j]):
                return False
    return True

# Generate all valid schedules


def generate_schedules(required_courses, optional_courses):
  # @todo: implementar validaciones para álgebra e introduccción a la ingeniería
    required_combinations = product(
        *[course.options for course in required_courses])
    optional_combinations = product(
        *[course.options for course in optional_courses])

    valid_schedules = []

    for req_comb in required_combinations:
        # revisa si el horario se empalma
        if is_valid_schedule(req_comb):
            for opt_comb in optional_combinations:
                full_comb = req_comb + opt_comb
                if is_valid_schedule(full_comb):
                    valid_schedules.append(full_comb)
    return valid_schedules


def get_course_options(df, materia):
    opciones = []

    filtered_df = df[df['Nombre de la Materia'] == materia]

    for _, row in filtered_df.iterrows():
        horario = None
        if pd.notnull(row['Horario']):
            try:
                horario = Schedule(row['Horario'])
            except ValueError as e:
                print(f"Error parsing schedule {row['Horario']}: {e}")

        opciones.append(Materia(
            no_clase=row['No. Clase'] if pd.notnull(
                row['No. Clase']) else 'NA',
            seccion=row['Sección'],
            nombre=row['Nombre de la Materia'],
            horario=horario
        ))

    return opciones


def get_combinations_no_repeated_course_no_overlaps(elements, M):
    # print(f"OPCIONES DE HORARIO: \n{elements} ")
    # all_combinations = combinations(elements, M)
    # unique_combinations = [
    #     combo for combo in all_combinations
    #     if len(set(element.nombre for element in combo)) == M and
    #        all(not combo[i].horario.overlaps(combo[j].horario) for i in range(M) for j in range(i + 1, M))
    # ]
    # return unique_combinations

    # this uses generators to avoid performance issues
    # Stack to keep track of (start_index, current_combination)
    stack = [(0, [])]
    while stack:
        start, current_combo = stack.pop()

        if len(current_combo) == M:
            if len(set(element.nombre for element in current_combo)) == M and \
               all(not current_combo[i].horario.overlaps(current_combo[j].horario) for i in range(M) for j in range(i + 1, M)):
                yield tuple(current_combo)
            continue

        for i in range(start, len(elements)):
            stack.append((i + 1, current_combo + [elements[i]]))


def save_schedules_to_csv(major, semester, schedules, filename):
    fieldnames = [course.name for course in schedules[0]]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for schedule in schedules:
            writer.writerow([option.option_id for option in schedule])


def schedule_to_df(schedules):
    time_slots = []
    start = '07:00'
    end = '22:00'
    interval = 30
    current_time = dt.strptime(start, '%H:%M')
    end_time = dt.strptime(end, '%H:%M')

    while current_time <= end_time:
        time_slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=interval)

    # días según la planta
    days_of_week = ['lu', 'ma', 'mi', 'ju', 'vi']

    # cuadrícula vacía para el horario
    grid = np.empty((len(time_slots), len(days_of_week)), dtype=object)
    grid[:] = ''

    # marcar los espacios ocupados en la cuadrícula
    for schedule in schedules:
        for day, hours in schedule.horario.days.items():
            start_time, end_time = hours
            start_index = time_slots.index(start_time.strftime('%H:%M'))
            end_index = time_slots.index(end_time.strftime('%H:%M'))
            day_index = days_of_week.index(day)
            grid[start_index:end_index,
                 day_index] = f"{schedule.nombre} [{schedule.seccion}]"

    # crear un dataframe para visualizar la cuadrícula
    df_grid = pd.DataFrame(grid, index=time_slots, columns=days_of_week)
    return df_grid
