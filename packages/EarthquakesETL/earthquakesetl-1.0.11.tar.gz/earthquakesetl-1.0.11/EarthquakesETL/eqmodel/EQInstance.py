import math
from typing import List, Optional

from EarthquakesETL.eqmodel.EQBDerivedAttributes import EQBDerivedAttributes

class NoApplicableAssessmentException(Exception):
    pass


class EQInstance:
    """
    Esta clase representa una 'instancia' que incluye atributos para predecir futuros sismos.
    Se evalúan valores b (b-values) según diferentes metodologías (Morales, Adeli).
    """

    # Atributos de clase (estáticos en Java)
    events: List['EQEvent'] = []
    instances: List['EQInstance'] = []
    firstAssessedBMorales: int = -1
    firstAssessedBAdeli: int = -1

    def __init__(self, events: List['EQEvent'], eventIndex: int, eqagen: 'EQPgen'):
        """
        Constructor de la instancia.
        :param events: lista de EQEvent
        :param eventIndex: índice del evento en la lista
        :param eqagen: referencia al generador/gestor de configuración
        """
        # Referencia a la lista de eventos y configuración
        self.events = events
        self.eventIndex = eventIndex
        self.event = events[eventIndex]
        self.eqagen = eqagen

        # Atributos para los valores b y control de si han sido calculados
        self.bAdeli: float = 0.0
        self.bMorales: float = 0.0
        self.assessed_bAdeli: bool = False
        self.assessed_bMorales: bool = False

        # Atributos derivados que dependen de b
        self.bdatt_morales: Optional['EQBDerivedAttributes'] = None
        self.bdatt_adeli: Optional['EQBDerivedAttributes'] = None

        # Atributos independientes de b
        self.x6: float = 0.0
        self.T: List[float] = []
        self.Mmean: float = 0.0
        self.dE12: float = 0.0
        self.mu: List[float] = []
        self.c: List[float] = []

        # Clase continua y discretas
        self.theClass: float = 0.0
        self.discreteClasses: List[bool] = [False] * len(eqagen.classesCutoffs)

    def assess_bValueMorales(self, eventIndex: int, nLast: int) -> None:
        """
        Evalúa el valor b según la metodología 'Morales'.
        Lanza NoApplicableAssessmentException si no hay suficientes eventos.
        """
        if eventIndex < nLast:
            raise NoApplicableAssessmentException()

        acumulado = 0.0
        # Se suman las magnitudes de los últimos nLast eventos
        for i in range(eventIndex - nLast + 1, eventIndex + 1):
            acumulado += self.events[i].magnitude

        # Fórmula de Morales
        self.bMorales = 1.0 / (
            math.log(10.0) * ((acumulado / nLast) - self.eqagen.referenceMagnitude)
        )

        self.assessed_bMorales = True

    def assess_bValueAdeli(self, eventIndex: int, nLast: int) -> None:
        """
        Evalúa el valor b según la metodología 'Adeli'.
        Lanza NoApplicableAssessmentException si no hay suficientes eventos.
        """
        if eventIndex < nLast:
            raise NoApplicableAssessmentException()

        numerador = 0.0
        denominador = 0.0
        aux = 0.0
        mag_suma = 0.0
        Ns_suma = 0.0

        # Cálculo del denominador (parte estadística)
        for i in range(nLast):
            mag = self.events[eventIndex - i].magnitude
            denominador += mag
            aux += (mag * mag)

        aux *= nLast
        denominador = (denominador * denominador) - aux

        # Cálculo del numerador
        for i in range(nLast):
            m_i = self.events[eventIndex - i].magnitude
            # Contamos cuántos eventos en la ventana tienen magnitud >= m_i
            N = 0
            for j in range(nLast):
                if self.events[eventIndex - j].magnitude >= m_i:
                    N += 1

            numerador += (m_i * math.log10(N))
            mag_suma += m_i
            Ns_suma += math.log10(N)

        numerador *= nLast
        num2 = mag_suma * Ns_suma
        numerador -= num2

        b = 0.0
        if denominador == 0:
            b = 1.0
        else:
            b = numerador / denominador

        if math.isnan(b) or math.isinf(b):
            b = 1.0

        self.bAdeli = b
        self.assessed_bAdeli = True

    def assessBdependentAttributes(self, whichBvalue: int) -> None:
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        Evalúa los atributos que dependen del valor b (Morales o Adeli).
        whichBvalue puede ser EQPgen.B_MORALES o EQPgen.B_ADELI.
        """
        if whichBvalue == EQPgen.B_MORALES:
            self.bdatt_morales = EQBDerivedAttributes(self, whichBvalue)
            self.bdatt_morales.assessAttributes()
        elif whichBvalue == EQPgen.B_ADELI:
            self.bdatt_adeli = EQBDerivedAttributes(self, whichBvalue)
            self.bdatt_adeli.assessAttributes()

    def assessBindependentAttributes(self) -> None:
        """
        Evalúa los atributos que no dependen del valor b.
        """
        self.assess_x6()
        self.assess_T()
        self.assess_Mmean()
        self.assess_dE12()
        self.assess_mu()
        self.assess_c()

    def assess_x6(self) -> None:
        """
        Calcula x6: la magnitud máxima en los últimos ldX6 días previos.
        """
        ldX6 = self.eqagen.ldX6
        self.x6 = 0.0

        i = self.eventIndex - 1
        while i >= 0 and (self.event.difference(self.events[i]) <= ldX6):
            if self.events[i].magnitude > self.x6:
                self.x6 = self.events[i].magnitude
            i -= 1

    def assess_T(self) -> None:
        """
        Calcula el vector T (uno por cada cutoff), usando la n de Adeli.
        """
        if self.eventIndex < self.eqagen.nAdeli:
            raise NoApplicableAssessmentException()

        cutoffs = self.eqagen.classesCutoffs
        self.T = [self._assess_T_cutoff(c) for c in cutoffs]

    def _assess_T_cutoff(self, cutoff: float) -> float:
        """
        Cálculo de T para un cutoff dado.
        T se define como la diferencia (en días) entre eventos al encontrar nAdeli eventos
        cuyas magnitudes superan el cutoff.
        """
        n = self.eqagen.nAdeli
        m = 0
        t1 = self.eventIndex
        tn = self.eventIndex - n

        i = self.eventIndex - 1
        while i >= 0 and m < n:
            if self.events[i].magnitude > cutoff:
                m += 1
                if m == 1:
                    tn = i
                t1 = i
            i -= 1

        # Valor de T: diferencia de tiempos entre el evento 'tn' y 't1'
        return self.events[tn].difference(self.events[t1])

    def assess_Mmean(self) -> None:
        """
        Cálculo de la media de magnitudes en los últimos nAdeli eventos.
        """
        n = self.eqagen.nAdeli
        suma = 0.0
        for i in range(self.eventIndex - n, self.eventIndex):
            suma += self.events[i].magnitude

        self.Mmean = suma / n

    def assess_dE12(self) -> None:
        """
        Cálculo de la energía acumulada (en raíz cuadrada) durante los últimos nAdeli eventos,
        normalizada por la diferencia de tiempo.
        """
        n = self.eqagen.nAdeli
        suma = 0.0
        for i in range(self.eventIndex - n, self.eventIndex + 1):
            # 10^(11.8 + 1.5 * M)
            val = math.pow(10, 11.8 + 1.5 * self.events[i].magnitude)
            suma += math.sqrt(val)

        # Dividimos por la diferencia entre el último y el primero en esa ventana
        delta_dias = self.events[self.eventIndex].difference(
            self.events[self.eventIndex - n]
        )
        self.dE12 = suma / delta_dias if delta_dias != 0 else 0.0

    def assess_mu(self) -> None:
        """
        Cálculo de mu para cada cutoff.
        """
        if self.eventIndex < self.eqagen.nAdeli:
            raise NoApplicableAssessmentException()

        cutoffs = self.eqagen.classesCutoffs
        self.mu = [self._assess_mu_cutoff(c) for c in cutoffs]

    def _assess_mu_cutoff(self, cutoff: float) -> float:
        """
        Se calcula la media de las diferencias temporales entre eventos 'característicos'
        (magnitud cercana al cutoff).
        """
        n = self.eqagen.nAdeli
        chth = self.eqagen.chth
        nch = 0
        t = -1
        res = 0.0

        for i in range(self.eventIndex - n, self.eventIndex):
            if abs(self.events[i].magnitude - cutoff) <= chth:
                nch += 1
                if nch > 1:
                    res += self.events[i].difference(self.events[t])
                t = i

        if nch > 1:
            res /= (nch - 1)

        return res

    def assess_c(self) -> None:
        """
        Cálculo de c para cada cutoff, depende de mu (que debe estar evaluado).
        """
        if self.eventIndex < self.eqagen.nAdeli:
            raise NoApplicableAssessmentException()

        cutoffs = self.eqagen.classesCutoffs
        self.c = [
            self._assess_c_cutoff(cutoff, idx) for idx, cutoff in enumerate(cutoffs)
        ]

    def _assess_c_cutoff(self, cutoff: float, cutoffIndex: int) -> float:
        """
        Para un cutoff, calcula la desviación típica (normalizada por mu) de las
        diferencias temporales entre eventos 'característicos'.
        """
        n = self.eqagen.nAdeli
        chth = self.eqagen.chth
        nch = 0
        t = -1
        res = 0.0

        for i in range(self.eventIndex - n, self.eventIndex):
            if abs(self.events[i].magnitude - cutoff) <= chth:
                nch += 1
                if nch > 1:
                    delta = self.events[i].difference(self.events[t]) - self.mu[cutoffIndex]
                    res += (delta * delta)
                t = i

        if nch > 1:
            res = math.sqrt(res / (nch - 1))
            if self.mu[cutoffIndex] != 0.0:
                res /= self.mu[cutoffIndex]
            else:
                res = 0.0

        return res

    def assessContinuousClass(self) -> None:
        """
        Evalúa la 'clase continua' (theClass), buscando la máxima magnitud
        dentro de un rango de días a futuro (dayspred).
        """
        dayspred = self.eqagen.dayspred
        self.theClass = 0.0

        i = self.eventIndex + 1
        while i < len(self.events) and (self.events[i].difference(self.event) <= dayspred):
            if self.events[i].magnitude > self.theClass:
                self.theClass = self.events[i].magnitude
            i += 1

    def assessDiscreteClasses(self) -> None:
        """
        Marca cada clase discreta (true/false) según los cutoffs establecidos.
        """
        cutoffs = self.eqagen.classesCutoffs
        for i in range(len(cutoffs)):
            self.discreteClasses[i] = (self.theClass >= cutoffs[i])

    @staticmethod
    def getInstance(instanceIndex: int) -> 'EQInstance':
        return EQInstance.instances[instanceIndex]

    @staticmethod
    def getEvent(eventIndex: int) -> 'EQEvent':
        return EQInstance.events[eventIndex]

    @staticmethod
    def setInstances(instances: List['EQInstance']):
        EQInstance.instances = instances

    def getEventIndex(self) -> int:
        return self.eventIndex

    def getbAdeli(self) -> float:
        return self.bAdeli

    def setbAdeli(self, bAdeli: float) -> None:
        self.bAdeli = bAdeli

    def getbMorales(self) -> float:
        return self.bMorales

    def setbMorales(self, bMorales: float) -> None:
        self.bMorales = bMorales

    def getX6(self) -> float:
        return self.x6

    def setX6(self, x6: float) -> None:
        self.x6 = x6

    def getT(self) -> List[float]:
        return self.T

    def setT(self, T: List[float]) -> None:
        self.T = T

    def getMmean(self) -> float:
        return self.Mmean

    def setMmean(self, Mmean: float) -> None:
        self.Mmean = Mmean

    def getdE12(self) -> float:
        return self.dE12

    def setdE12(self, dE12: float) -> None:
        self.dE12 = dE12

    def getMu(self) -> List[float]:
        return self.mu

    def getMuByCutoff(self, cutoff: float) -> float:
        cutoffs = self.eqagen.classesCutoffs
        for i, cval in enumerate(cutoffs):
            if abs(cval - cutoff) < 0.0001:
                return self.mu[i]
        # Si no coincide exactamente, se retorna algo por defecto:
        return 0.0

    def setMu(self, mu: List[float]) -> None:
        self.mu = mu

    def getC(self) -> List[float]:
        return self.c

    def setC(self, c: List[float]) -> None:
        self.c = c

    def getTheClass(self) -> float:
        return self.theClass

    def setTheClass(self, theClass: float) -> None:
        self.theClass = theClass

    def getDiscreteClasses(self) -> List[bool]:
        return self.discreteClasses

    def setEvents(self, events: List['EQEvent']) -> None:
        self.events = events

    def isAssessed_bAdeli(self) -> bool:
        return self.assessed_bAdeli

    def setAssessed_bAdeli(self, val: bool) -> None:
        self.assessed_bAdeli = val

    def isAssessed_bMorales(self) -> bool:
        return self.assessed_bMorales

    def setAssessed_bMorales(self, val: bool) -> None:
        self.assessed_bMorales = val

    def __str__(self):
        return (
            f"EQInstance{{bAdeli={self.bAdeli}, bMorales={self.bMorales}, "
            f"ass_bAdeli={self.assessed_bAdeli}, ass_bMorales={self.assessed_bMorales}, "
            f"x6={self.x6}, T={self.T}, Mmean={self.Mmean}, dE12={self.dE12}, "
            f"mu={self.mu}, c={self.c}, bdep-Morales={self.bdatt_morales}, "
            f"bdep-Adeli={self.bdatt_adeli}, theClass={self.theClass}, "
            f"discreteClasses={self.discreteClasses}}}"
        )

    @staticmethod
    def assess_firstAssessedBvalues() -> None:
        """
        Busca los primeros índices (en 'instances') donde se evaluaron bAdeli y bMorales.
        """
        i = 0
        EQInstance.firstAssessedBMorales = -1
        EQInstance.firstAssessedBAdeli = -1
        while i < len(EQInstance.instances) and (
            EQInstance.firstAssessedBMorales == -1 or EQInstance.firstAssessedBAdeli == -1
        ):
            if EQInstance.firstAssessedBAdeli == -1 and EQInstance.instances[i].assessed_bAdeli:
                EQInstance.firstAssessedBAdeli = i
            if EQInstance.firstAssessedBMorales == -1 and EQInstance.instances[i].assessed_bMorales:
                EQInstance.firstAssessedBMorales = i
            i += 1

    def toCSV(self, outputType: str, noclass: bool, noheader: bool) -> str:
        """
        Genera una cadena CSV con los atributos seleccionados.
        :param outputType: lista separada por comas (ej. "attYorch/bM,attAdeli/bM")
        :param noclass: si es True, no se incluye la clase discreta
        :param noheader: si es True, no incluye atributos de encabezado (índice, tiempo, etc.)
        """
        aux = outputType.split(",")
        res = ""

        # Si no se omite el encabezado, agregamos índice de evento y tiempo
        if not noheader:
            res = f"{self.eventIndex},'{self.event.getTimeToString()}',"

        partes = []
        for item in aux:
            if item == "attYorch/bM" and self.bdatt_morales:
                x1 = self.bdatt_morales.x1
                x2 = self.bdatt_morales.x2
                x3 = self.bdatt_morales.x3
                x4 = self.bdatt_morales.x4
                x5 = self.bdatt_morales.x5
                x7 = self.bdatt_morales.x7
                partes.append(f"{x1},{x2},{x3},{x4},{x5},{self.x6},{x7}")

            elif item == "attYorch/bA" and self.bdatt_adeli:
                x1 = self.bdatt_adeli.x1
                x2 = self.bdatt_adeli.x2
                x3 = self.bdatt_adeli.x3
                x4 = self.bdatt_adeli.x4
                x5 = self.bdatt_adeli.x5
                x7 = self.bdatt_adeli.x7
                partes.append(f"{x1},{x2},{x3},{x4},{x5},{self.x6},{x7}")

            elif item == "attAdeli/bM" and self.bdatt_morales:
                aAdeli = self.bdatt_morales.aAdeli
                eta = self.bdatt_morales.eta
                deltaM = self.bdatt_morales.deltaM
                partes.append(
                    f"{self._getAllTs()},{self.Mmean},{self.dE12},{self.bMorales},"
                    f"{aAdeli},{eta},{deltaM},{self._getAllmus()},{self._getAllcs()}"
                )

            elif item == "attAdeli/bA" and self.bdatt_adeli:
                aAdeli = self.bdatt_adeli.aAdeli
                eta = self.bdatt_adeli.eta
                deltaM = self.bdatt_adeli.deltaM
                partes.append(
                    f"{self._getAllTs()},{self.Mmean},{self.dE12},{self.bAdeli},"
                    f"{aAdeli},{eta},{deltaM},{self._getAllmus()},{self._getAllcs()}"
                )
            # Se pueden agregar más casos si hay más tipos de salida definidos

        # Unimos las partes
        res += ",".join(partes) + ","

        # Clase continua
        res += str(self.theClass)

        # Clases discretas
        if not noclass:
            for val in self.discreteClasses:
                res += "," + ("1" if val else "0")

        # Remplazo de -Infinity, Infinity por "0.0" (según Java)
        res = res.replace("-Infinity", "0.0").replace("Infinity", "0.0")
        return res

    def _getAllTs(self) -> str:
        return ",".join(str(t) for t in self.T)

    def _getAllmus(self) -> str:
        return ",".join(str(m) for m in self.mu)

    def _getAllcs(self) -> str:
        return ",".join(str(ci) for ci in self.c)

    """
    private static String getHeaderOfVectorAttribute (float [] cutoffs, DecimalFormat df, String name, String suffix) {
        String res = "";
        for (int i = 0; i < cutoffs.length; i++) {
            res += "@attribute " + name + df.format(cutoffs[i]).replace(',', '.') + suffix + " numeric\n";
        }
        return res;
    }
    """


    @staticmethod
    def arffHeader(
        outputType: str,
        cutoffs: List[float],
        datasetName: str,
        dayspred: int,
        noclass: bool,
        noheader: bool
    ) -> str:
        """
        Genera un encabezado de archivo ARFF.
        Nota: Usa métodos auxiliares como getHeaderOfVectorAttribute,
        que en Java formateaban cadenas. Aquí hacemos una aproximación.
        """

        res = (f"@relation EQP_{datasetName}_"
               f"prediction-horizon-{dayspred}days\n\n")

        aux = outputType.split(",")
        if not noheader:
            res += "@attribute event integer\n@attribute time string\n"

        def getHeaderOfVectorAttribute(cutoffs: List[float], name: str, suffix: str) -> str:
            lines = []
            for co in cutoffs:
                # Similar a DecimalFormat("#.##") => redondear a 2 decimales
                co_str = f"{co:.2f}".replace(",", ".")
                lines.append(f"@attribute {name}{co_str}{suffix} numeric\n")
            return "".join(lines)

        for item in aux:
            if item == "attYorch/bM":
                res += (
                    "@attribute x1_bM numeric\n@attribute x2_bM numeric\n"
                    "@attribute x3_bM numeric\n@attribute x4_bM numeric\n"
                    "@attribute x5_bM numeric\n@attribute x6_indep_bM numeric\n"
                    "@attribute x7_bM numeric\n"
                )
            elif item == "attYorch/bA":
                res += (
                    "@attribute x1_bA numeric\n@attribute x2_bA numeric\n"
                    "@attribute x3_bA numeric\n@attribute x4_bA numeric\n"
                    "@attribute x5_bA numeric\n@attribute x6_indep_bA numeric\n"
                    "@attribute x7_bA numeric\n"
                )
            elif item == "attAdeli/bM":
                res += getHeaderOfVectorAttribute(cutoffs, "T", "_indep_bM")
                res += ("@attribute Mmean_indep_bM numeric\n"
                        "@attribute dE12_indep_bM numeric\n"
                        "@attribute bM numeric\n"
                        "@attribute a_bM numeric\n"
                        "@attribute eta_bM numeric\n"
                        "@attribute deltaM_bM numeric\n")
                res += getHeaderOfVectorAttribute(cutoffs, "mu", "_indep_bM")
                res += getHeaderOfVectorAttribute(cutoffs, "c", "_indep_bM")

            elif item == "attAdeli/bA":
                res += getHeaderOfVectorAttribute(cutoffs, "T", "_indep_bA")
                res += ("@attribute Mmean_indep_bA numeric\n"
                        "@attribute dE12_indep_bA numeric\n"
                        "@attribute bA numeric\n"
                        "@attribute a_bA numeric\n"
                        "@attribute eta_bA numeric\n"
                        "@attribute deltaM_bA numeric\n")
                res += getHeaderOfVectorAttribute(cutoffs, "mu", "_indep_bA")
                res += getHeaderOfVectorAttribute(cutoffs, "c", "_indep_bA")

        res += "@attribute continuousClass numeric\n"
        if not noclass:
            for co in cutoffs:
                co_str = f"{co:.2f}".replace(",", ".")
                res += f"@attribute class{co_str} {{0,1}}\n"

        res += "\n@data\n"
        return res