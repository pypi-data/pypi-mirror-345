import os
import re
from datetime import datetime
from typing import List

import pandas as pd

from EarthquakesETL.eqmodel.EQInstance import EQInstance, NoApplicableAssessmentException
from EarthquakesETL.eqmodel.EQEvent import EQEvent

DATE_FORMAT = "%m/%d/%Y %H:%M"

class EQPgen:
    # Constantes análogas a B_MORALES, B_ADELI
    B_MORALES = 1
    B_ADELI = 2

    """
    Se encarga de:
      - Leer los eventos desde un archivo de texto.
      - Generar instancias con sus atributos y clases.
      - Guardar los resultados en un archivo ARFF.
    """

    def __init__(self):
        # Valores por defecto
        self.nMorales: int = 50
        self.nAdeli: int = 4
        self.referenceMagnitude: float = 3.0
        self.dayspred: int = 6
        self.classFrom: float = 3.5
        self.classTo: float = 4.0
        self.classStep: float = 0.1
        self.ldX6: int = 7

        # Array con los "cutoffs" discretos. Se llena en generateClassesCutoffs()
        self.classesCutoffs: List[float] = []

        # Umbral característico para los atributos mu y c (Adeli).
        self.chth: float = 0.1

        # Indica si se omite cabecera (event/time) o clases discretas.
        self.noheader: bool = False
        self.noclass: bool = False

        # Ruta de salida
        self.outputFileName: str = "output.arff"

        # Tipo de salida
        self.outputType: str = "attYorch/bM"

        # Arreglos de EQEvent / EQInstance
        self.events: List['EQEvent'] = []
        self.instances: List['EQInstance'] = []

        #Dates
        self.timeFrom: datetime.datetime = None
        self.timeTo: datetime.datetime = None

        self.progress_callback = None

    def readEventsFromDataFrame(self, df: pd.DataFrame) -> None:
        """
        Lee los eventos desde un DataFrame de pandas en lugar de un archivo CSV.
        Crea un array de EQEvent y luego un array de EQInstance.
        """
        loaded_events: List['EQEvent'] = []

        if "mag" in df.columns:
            mag_col = "mag"
        elif "magnitude" in df.columns:
            mag_col = "magnitude"

        self.timeFrom = df["time"].min()
        self.timeTo = df["time"].max()

        for idx, row in df.iterrows():
            dt = row["time"]
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            mag = float(row[mag_col])
            ev = EQEvent(dt, lat, lon, mag)
            loaded_events.append(ev)

        # Se puede aplicar un filtrado según timeFrom y timeTo (si están definidos)
        if self.timeFrom or self.timeTo:
            filtered = []
            for ev in loaded_events:
                if self.timeFrom and ev.time < self.timeFrom:
                    continue
                if self.timeTo and ev.time > self.timeTo:
                    continue
                filtered.append(ev)
            loaded_events = filtered

        self.events = loaded_events
        EQEvent.setEvents(self.events)

        # Crear el array de instancias
        self.instances = []
        for i, ev in enumerate(self.events):
            inst = EQInstance(self.events, i, self)  # se pasa self para que conozca la config
            self.instances.append(inst)

        EQInstance.setInstances(self.instances)

    def writeInstances(self) -> pd.DataFrame:
        """
        Genera un DataFrame a partir de las instancias evaluadas.
        Se incluyen solo aquellas instancias cuyos eventos estén dentro del rango de fechas (timeFrom - timeTo).
        """
        # 1) Obtener el "header ARFF" (como string multilinea).
        datasetName = os.path.splitext(os.path.basename(self.outputFileName))[0]
        arff_text = EQInstance.arffHeader(
            self.outputType,
            self.classesCutoffs,
            datasetName,
            self.dayspred,
            self.noclass,
            self.noheader
        )

        # 2) Extraer nombres de columnas a partir de las líneas que comiencen con "@attribute".
        col_names = []
        lines_arff = arff_text.splitlines()
        for line in lines_arff:
            line = line.strip()
            if line.lower().startswith("@attribute"):
                parts = line.split()
                if len(parts) >= 3:
                    col_name = parts[1].strip("'\"")
                    col_names.append(col_name)

        # 3) Generar las filas a partir de las instancias que cumplen los criterios,
        #    incluyendo el filtro por fecha: solo se procesan instancias cuyo evento esté entre timeFrom y timeTo.
        rows = []
        for i, inst in enumerate(self.instances):
            # Se filtran las instancias según:
            #   - que se hayan evaluado ambos b-values
            #   - y que el tiempo del evento esté dentro del rango (si se ha definido alguno)
            if inst.isAssessed_bAdeli() and inst.isAssessed_bMorales():
                ev_time = inst.event.time
                if self.timeFrom and ev_time < self.timeFrom:
                    continue
                if self.timeTo and ev_time > self.timeTo:
                    continue
                csv_line = inst.toCSV(self.outputType, self.noclass, self.noheader)
                csv_line = re.sub(r',+', ',', csv_line)
                row_values = csv_line.split(",")
                rows.append(row_values)

        # 4) Crear un DataFrame a partir de las filas y los nombres de columnas.
        df = pd.DataFrame(rows, columns=col_names)
        return df


    def assessBvalues(self) -> None:
        """
        Genera b-values de Morales y Adeli.
        """
        for i, inst in enumerate(self.instances):
            try:
                inst.assess_bValueMorales(i, self.nMorales)
            except NoApplicableAssessmentException:
                pass
            try:
                inst.assess_bValueAdeli(i, self.nAdeli)
            except NoApplicableAssessmentException:
                pass
        EQInstance.assess_firstAssessedBvalues()

    def assessBdependentAttributes(self, whichBvalue: int) -> None:
        for inst in self.instances:
            try:
                inst.assessBdependentAttributes(whichBvalue)
            except NoApplicableAssessmentException:
                pass

    def assessBindependentAttributes(self) -> None:
        for inst in self.instances:
            try:
                inst.assessBindependentAttributes()
            except NoApplicableAssessmentException:
                pass

    def assessClasses(self) -> None:
        for inst in self.instances:
            try:
                inst.assessContinuousClass()
                if not self.noclass:
                    inst.assessDiscreteClasses()
            except NoApplicableAssessmentException:
                pass

    def generateClassesCutoffs(self) -> None:
        cutoff = self.classFrom
        vals = []
        while cutoff <= self.classTo + 1e-7:
            vals.append(cutoff)
            cutoff += self.classStep
        self.classesCutoffs = vals

    def assessAll(self) -> None:
        """
        Realiza la secuencia completa:
          - Generar b-values
          - Evaluar atributos dependientes/independientes de b
          - Calcular clases
        """
        total = len(self.instances)

        for i, inst in enumerate(self.instances):
            try:
                self.assessBvalues()
                self.assessBdependentAttributes(EQPgen.B_MORALES)
                self.assessBdependentAttributes(EQPgen.B_ADELI)
                self.assessBindependentAttributes()
                self.assessClasses()
            except NoApplicableAssessmentException:
                pass

            if self.progress_callback:
                self.progress_callback(int((i + 1) * 100 / total))

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        self.generateClassesCutoffs()
        self.readEventsFromDataFrame(df)
        self.assessAll()
        return self.writeInstances()