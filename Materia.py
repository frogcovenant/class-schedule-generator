class Materia:
    def __init__(self, seccion, nombre,  horario, no_clase='NA',):
        self.no_clase = no_clase
        self.seccion = seccion
        self.nombre = nombre
        self.horario = horario

    def __repr__(self) -> str:
        return f"{self.seccion} - {self.nombre} [{self.no_clase}]: {self.horario}"
