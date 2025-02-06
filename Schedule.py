from datetime import datetime as dt


class Schedule:
    def __init__(self, schedule_str):
        self.days = {
            "Lu": ['inicio', 'fin'],
            "Ma": ['inicio', 'fin'],
            "Mi": ['inicio', 'fin'],
            "Ju": ['inicio', 'fin']
        }
        self.days = self.parse_schedule(schedule_str)
        if self.days == None:
            print(schedule_str)

    def parse_schedule(self, schedule_str: str):
        # REGLAS
        # 1- Los dias siempre van antes que la hora
        # 2- La hora de inicio siempre va antes que la hora fin
        # 3- Los horarios siempre son H:MM o HH:MM
        # 4- Los dias pueden ser Lu, Ma, Mi, Ju o Vi
        # 5- Puede haber mas de un dia para un horario (todos los dias van antes que el horario)
        # 6- Puede haber horarios distintos para cada dia (cada uno debe tener cumplir con todas las reglas anteriores)
        # 7- Cualquier separador o espacio adicional se va a ignorar

        # EJEMPLOS
        # DD, DD HH:MM - HH:MM
        # Ma, Ju 19:00 - 22:00

        # DD HH:MM - HH:MM
        # Ma 15:00 - 17:00

        # DD, DD, DD, DD HH:MM - HH:MM
        # Lu, Ma, Mi, Ju 13:00 - 15:00

        # DD HH:MM, DD HH:MM-HH:MM
        # Ma 14:30-18:00, Mi 19:00-20:30

        # DD HH:MM - HH:MM | DD HH:MM - HH:MM
        # Ju 11:00 - 13:00 | Vi 9:00 - 11:00

        # PSEUDO CODIGO
        # 1- iteramos hasta encontrar dos caracteres alfabeticos
        #    -> guardamos los 2 caracteres como string en la lista de days
        # 2- regresamos paso 1 hasta encontrar dos puntos
        # 3- revisamos si n-1 o n-2 son numeros
        #    -> se guarda como hora inicio
        # 4- revisamos los 2 siguientes caracteres
        #    -> se guarda como minutos inicio
        # 5- buscamos hasta encontrar dos puntos
        # 6- revisamos si n-1 o n-2 son numeros
        #    -> se guarda como hora fin
        # 7- revisamos los 2 siguientes caracteres
        #    -> se guarda como minutos fin
        # 8- guardamos horario
        # 9- regresamos al paso 1 hasta terminar con la string

        if len(schedule_str) < 12:
            return None

        days = {}
        current_days = []
        hora_inicio, minutos_inicio, hora_fin, minutos_fin = None, None, None, None
        prev_from_last = schedule_str[0]
        last = schedule_str[1]

        for character in f"{schedule_str[2::]} ":
            # 1- iteramos hasta encontrar dos caracteres alfabeticos
            if prev_from_last.isalpha() and last.isalpha():
                # guardamos los 2 caracteres como string en la lista de days
                current_day = f"{prev_from_last}{last}".lower()
                current_days.append(current_day)
            # 2- seguimos iterando hasta encontrar dos puntos
            elif character == ':' and hora_inicio == None:
                # 3- revisamos si n-1 o n+1 y n-2 son numeros
                if f"{prev_from_last}{last}".isdigit():
                    # se guarda como hora inicio
                    hora_inicio = int(f"{prev_from_last}{last}")
                elif last.isdigit():
                    # se guarda como hora inicio
                    hora_inicio = int(last)
            # 4- revisamos los 2 siguientes caracteres
            elif f"{prev_from_last}{last}".isdigit() and minutos_inicio == None:
                # se guarda como minutos inicio
                minutos_inicio = int(f"{prev_from_last}{last}")
            # 5- buscamos hasta encontrar dos puntos
            elif character == ':':
                # 6- revisamos si n-1 o n+1 y n-2 son numeros
                if f"{prev_from_last}{last}".isdigit():
                    # se guarda como hora fin
                    hora_fin = int(f"{prev_from_last}{last}")
                elif last.isdigit():
                    # se guarda como hora fin
                    hora_fin = int(last)
            # 7- revisamos los 2 siguientes caracteres
            elif f"{prev_from_last}{last}".isdigit():
                # se guarda como minutos fin
                minutos_fin = int(f"{prev_from_last}{last}")

            # 8- guardamos horario
            if minutos_fin != None:
                for day in current_days:
                    start_time_str = f"{hora_inicio}:{minutos_inicio}"
                    end_time_str = f"{hora_fin}:{minutos_fin}"
                    days[day] = [dt.strptime(start_time_str.strip(), '%H:%M'), dt.strptime(
                        end_time_str.strip(), '%H:%M')]

                # 9- regresamos al paso 1 hasta terminar con la string (importante resetear las variables para generar nuevo horario)
                current_days = []
                hora_inicio, minutos_inicio, hora_fin, minutos_fin = None, None, None, None

            # actualizamos variables para la siguiente iteracion
            prev_from_last = last
            last = character

        return days

    def overlaps(self, other):
        # Check if any day overlaps
        common_days = set(self.days.keys()) & set(other.days.keys())
        if not common_days:
            return False

        # Check if the times overlap for each specific day (consider that other might not have values for that day)
        check = False
        for day, hours in self.days.items():
            default_hours = [dt.strptime(
                '23:00', '%H:%M'), dt.strptime('4:00', '%H:%M')]
            if hours[0] < other.days.get(day, default_hours)[1] and hours[1] > other.days.get(day, default_hours)[0]:
                check = True
        return check

    def __repr__(self):
        out = ''
        for day, hours in self.days.items():
            start_time_str = hours[0].strftime('%H:%M')
            end_time_str = hours[1].strftime('%H:%M')
            out += f"{day} {start_time_str} - {end_time_str}\n"
        return out
