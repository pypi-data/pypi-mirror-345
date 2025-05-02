import math

from EarthquakesETL.eqmodel.EQEvent import EQEvent

class EQBDerivedAttributes:
    """Atributos de los eventos que dependen de un valor b (bAdeli o bMorales)."""

    def __init__(self, instance: 'EQInstance', whichBvalue: int):
        """
        :param instance: Instancia de EQInstance relacionada.
        :param whichBvalue: Indica el tipo de b-value (EQPgen.B_MORALES o EQPgen.B_ADELI).
        """
        self.instance = instance
        self.whichBvalue = whichBvalue

        # Atributos x1, x2, x3, x4, x5, x7 (Yorch) y eta, deltaM, aAdeli (Adeli)
        self.x1: float = 0.0
        self.x2: float = 0.0
        self.x3: float = 0.0
        self.x4: float = 0.0
        self.x5: float = 0.0
        self.x7: float = 0.0
        self.eta: float = 0.0
        self.deltaM: float = 0.0
        self.aAdeli: float = 0.0

    def assessAttributes(self) -> None:
        from EarthquakesETL.eqmodel.EQInstance import NoApplicableAssessmentException
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        Evalúa todos los atributos dependientes del b-value.
        Lanza NoApplicableAssessmentException si no se cumple alguna condición previa.
        """
        # Comprobamos si el b-value en cuestión ya ha sido evaluado
        if (self.whichBvalue == EQPgen.B_ADELI and not self.instance.isAssessed_bAdeli()) \
           or (self.whichBvalue == EQPgen.B_MORALES and not self.instance.isAssessed_bMorales()):
            raise NoApplicableAssessmentException()

        # Vamos evaluando atributo por atributo
        self.assess_x1()
        self.assess_x2()
        self.assess_x3()
        self.assess_x4()
        self.assess_x5()
        self.assess_x7()
        self.assess_aAdeli()
        self.assess_eta()
        self.assess_deltaM()

    def assess_x1(self) -> None:
        from EarthquakesETL.eqmodel.EQInstance import EQInstance, NoApplicableAssessmentException
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        x1 = b(i) - b(i-4)
        Verifica que haya suficientes instancias desde que se evaluó el primer b.
        """
        currentIndex = self.instance.getEventIndex()
        # Chequeamos que existan al menos 4 instancias evaluadas con el b-value en uso
        # (i.e. currentIndex - primer índice evaluado >= 4)
        if (self.whichBvalue == EQPgen.B_ADELI and
            currentIndex - EQInstance.firstAssessedBAdeli < 4) \
           or (self.whichBvalue == EQPgen.B_MORALES and
               currentIndex - EQInstance.firstAssessedBMorales < 4):
            raise NoApplicableAssessmentException()

        if self.whichBvalue == EQPgen.B_ADELI:
            self.x1 = self.instance.getbAdeli() \
                      - EQInstance.getInstance(currentIndex - 4).getbAdeli()
        else:  # B_MORALES
            self.x1 = self.instance.getbMorales() \
                      - EQInstance.getInstance(currentIndex - 4).getbMorales()

    def assess_x2(self) -> None:
        from EarthquakesETL.eqmodel.EQInstance import EQInstance, NoApplicableAssessmentException
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        x2 = b(i-4) - b(i-8)
        """
        currentIndex = self.instance.getEventIndex()
        if (self.whichBvalue == EQPgen.B_ADELI and
            currentIndex - EQInstance.firstAssessedBAdeli < 8) \
           or (self.whichBvalue == EQPgen.B_MORALES and
               currentIndex - EQInstance.firstAssessedBMorales < 8):
            raise NoApplicableAssessmentException()

        if self.whichBvalue == EQPgen.B_ADELI:
            self.x2 = (EQInstance.getInstance(currentIndex - 4).getbAdeli()
                       - EQInstance.getInstance(currentIndex - 8).getbAdeli())
        else:  # B_MORALES
            self.x2 = (EQInstance.getInstance(currentIndex - 4).getbMorales()
                       - EQInstance.getInstance(currentIndex - 8).getbMorales())

    def assess_x3(self) -> None:
        from EarthquakesETL.eqmodel.EQInstance import EQInstance, NoApplicableAssessmentException
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        x3 = b(i-8) - b(i-12)
        """
        currentIndex = self.instance.getEventIndex()
        if (self.whichBvalue == EQPgen.B_ADELI and
            currentIndex - EQInstance.firstAssessedBAdeli < 12) \
           or (self.whichBvalue == EQPgen.B_MORALES and
               currentIndex - EQInstance.firstAssessedBMorales < 12):
            raise NoApplicableAssessmentException()

        if self.whichBvalue == EQPgen.B_ADELI:
            self.x3 = (EQInstance.getInstance(currentIndex - 8).getbAdeli()
                       - EQInstance.getInstance(currentIndex - 12).getbAdeli())
        else:
            self.x3 = (EQInstance.getInstance(currentIndex - 8).getbMorales()
                       - EQInstance.getInstance(currentIndex - 12).getbMorales())

    def assess_x4(self) -> None:
        from EarthquakesETL.eqmodel.EQInstance import EQInstance, NoApplicableAssessmentException
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        x4 = b(i-12) - b(i-16)
        """
        currentIndex = self.instance.getEventIndex()
        if (self.whichBvalue == EQPgen.B_ADELI and
            currentIndex - EQInstance.firstAssessedBAdeli < 16) \
           or (self.whichBvalue == EQPgen.B_MORALES and
               currentIndex - EQInstance.firstAssessedBMorales < 16):
            raise NoApplicableAssessmentException()

        if self.whichBvalue == EQPgen.B_ADELI:
            self.x4 = (EQInstance.getInstance(currentIndex - 12).getbAdeli()
                       - EQInstance.getInstance(currentIndex - 16).getbAdeli())
        else:
            self.x4 = (EQInstance.getInstance(currentIndex - 12).getbMorales()
                       - EQInstance.getInstance(currentIndex - 16).getbMorales())

    def assess_x5(self) -> None:
        from EarthquakesETL.eqmodel.EQInstance import EQInstance, NoApplicableAssessmentException
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        x5 = b(i-16) - b(i-20)
        """
        currentIndex = self.instance.getEventIndex()
        if (self.whichBvalue == EQPgen.B_ADELI and
            currentIndex - EQInstance.firstAssessedBAdeli < 20) \
           or (self.whichBvalue == EQPgen.B_MORALES and
               currentIndex - EQInstance.firstAssessedBMorales < 20):
            raise NoApplicableAssessmentException()

        if self.whichBvalue == EQPgen.B_ADELI:
            self.x5 = (EQInstance.getInstance(currentIndex - 16).getbAdeli()
                       - EQInstance.getInstance(currentIndex - 20).getbAdeli())
        else:
            self.x5 = (EQInstance.getInstance(currentIndex - 16).getbMorales()
                       - EQInstance.getInstance(currentIndex - 20).getbMorales())

    def assess_x7(self) -> None:
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        x7 = 10^(-3 * b)
        """
        if self.whichBvalue == EQPgen.B_ADELI:
            self.x7 = 10 ** (-3 * self.instance.getbAdeli())
        else:  # B_MORALES
            self.x7 = 10 ** (-3 * self.instance.getbMorales())

    def assess_aAdeli(self) -> None:
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        Calcula 'aAdeli' según la lógica:
            a = 1/n * Σ [ b * M(i) + log10(N) ]
        donde N es el número de eventos con magnitud >= M(i).
        En Java se usaba la misma fórmula tanto para bAdeli como bMorales,
        ajustando n.
        """
        currentIndex = self.instance.getEventIndex()
        if self.whichBvalue == EQPgen.B_ADELI:
            n = self.instance.eqagen.nAdeli
            b = self.instance.getbAdeli()
        else:
            n = self.instance.eqagen.nMorales
            b = self.instance.getbMorales()

        tmp = 0.0
        for i in range(n, 0, -1):
            mag_i = EQEvent.getEvent(currentIndex - i).getMagnitude()
            tmp += b * mag_i
            # Contar cuántos eventos tienen magnitud >= M(i)
            N = 0
            for j in range(n, 0, -1):
                if EQEvent.getEvent(currentIndex - j).getMagnitude() >= mag_i:
                    N += 1
            tmp += math.log10(N)

        self.aAdeli = tmp / n

    def assess_eta(self) -> None:
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        Calcula 'eta' según la lógica:
            eta = 1/(n-1) * Σ [ (log10(N) - aAdeli + b * M(i))^2 ]
        """
        currentIndex = self.instance.getEventIndex()
        if self.whichBvalue == EQPgen.B_ADELI:
            n = self.instance.eqagen.nAdeli
            b = self.instance.bAdeli
        else:
            n = self.instance.eqagen.nMorales
            b = self.instance.bMorales

        self.eta = 0.0
        for i in range(n, 0, -1):
            mag_i = EQEvent.getEvent(currentIndex - i).getMagnitude()
            # Hallamos N
            N = 0
            for j in range(n, 0, -1):
                if EQEvent.getEvent(currentIndex - j).getMagnitude() >= mag_i:
                    N += 1

            aux = math.log10(N) - self.aAdeli + b * mag_i
            self.eta += (aux * aux)

        if n > 1:
            self.eta /= (n - 1)

    def assess_deltaM(self) -> None:
        from EarthquakesETL.eqmodel.EQPgen import EQPgen
        """
        deltaM = (max(M en últimos n eventos) ) - (aAdeli / b)
        """
        currentIndex = self.instance.getEventIndex()
        if self.whichBvalue == EQPgen.B_ADELI:
            n = self.instance.eqagen.nAdeli
            b = self.instance.bAdeli
        else:
            n = self.instance.eqagen.nMorales
            b = self.instance.bMorales

        expected = (self.aAdeli / b) if b != 0 else 0
        # Máxima magnitud de los últimos n eventos
        max_mag = EQEvent.getEvent(currentIndex - n).getMagnitude()
        for i in range(n - 1, 0, -1):
            mag_i = EQEvent.getEvent(currentIndex - i).getMagnitude()
            if mag_i > max_mag:
                max_mag = mag_i

        self.deltaM = max_mag - expected

    # Getters / setters (opcionales, según tu estilo Python)
    def getX1(self) -> float:
        return self.x1

    def setX1(self, val: float) -> None:
        self.x1 = val

    def getX2(self) -> float:
        return self.x2

    def setX2(self, val: float) -> None:
        self.x2 = val

    def getX3(self) -> float:
        return self.x3

    def setX3(self, val: float) -> None:
        self.x3 = val

    def getX4(self) -> float:
        return self.x4

    def setX4(self, val: float) -> None:
        self.x4 = val

    def getX5(self) -> float:
        return self.x5

    def setX5(self, val: float) -> None:
        self.x5 = val

    def getX7(self) -> float:
        return self.x7

    def setX7(self, val: float) -> None:
        self.x7 = val

    def getEta(self) -> float:
        return self.eta

    def setEta(self, val: float) -> None:
        self.eta = val

    def getDeltaM(self) -> float:
        return self.deltaM

    def setDeltaM(self, val: float) -> None:
        self.deltaM = val

    def getaAdeli(self) -> float:
        return self.aAdeli

    def setaAdeli(self, val: float) -> None:
        self.aAdeli = val

    def __str__(self) -> str:
        return (f"EQBDerAtt{{whichB={self.whichBvalue}, x1={self.x1}, x2={self.x2}, "
                f"x3={self.x3}, x4={self.x4}, x5={self.x5}, x7={self.x7}, "
                f"eta={self.eta}, deltaM={self.deltaM}, aAdeli={self.aAdeli}}}")