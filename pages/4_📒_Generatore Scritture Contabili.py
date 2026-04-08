#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore Scritture Contabili - Manuale Tecnico Operativo (Ateneo)
Mappatura completa su Piano dei Conti SPIACO (Ranocchi GIS)
Include tutte le scritture estratte dal PDF caricato.
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

# ==============================================================================
# 1. PIANO DEI CONTI SPIACO (Selezione pertinente al Manuale)
# ==============================================================================
COA = {
    "34.01.001": {"desc": "DEPOSITI BANCARI E POSTALI", "tipo": "Patrimoniale Attivo"},
    "28.11.009": {"desc": "CREDITO IVA", "tipo": "Patrimoniale Attivo"},
    "37.01.001": {"desc": "RATEI ATTIVI", "tipo": "Patrimoniale Attivo"},
    "37.01.005": {"desc": "RISCONTI ATTIVI", "tipo": "Patrimoniale Attivo"},
    "28.15.053": {"desc": "CREDITI PER ANTICIPI MISSIONI", "tipo": "Patrimoniale Attivo"},
    "13.05.053": {"desc": "ATTREZZATURE SCIENTIFICHE / MACCHINARI", "tipo": "Patrimoniale Attivo"},
    "13.05.017": {"desc": "IMPIANTO ELETTRICO", "tipo": "Patrimoniale Attivo"},
    
    "49.13.001": {"desc": "DEBITI VERSO FORNITORI", "tipo": "Patrimoniale Passivo"},
    "49.23.009": {"desc": "ERARIO C/IVA SPLIT PAYMENT", "tipo": "Patrimoniale Passivo"},
    "49.23.029": {"desc": "ERARIO C/IRPEF LIQUIDAZIONE", "tipo": "Patrimoniale Passivo"},
    "49.25.001": {"desc": "DEBITI V/ ISTITUTI PREVIDENZIALI", "tipo": "Patrimoniale Passivo"},
    "49.27.025": {"desc": "DEBITI VERSO DIPENDENTI", "tipo": "Patrimoniale Passivo"},
    "49.27.041": {"desc": "DEBITI VERSO ALTRI PRIVATI", "tipo": "Patrimoniale Passivo"},
    "46.01.001": {"desc": "FONDO T.F.R.", "tipo": "Patrimoniale Passivo"},
    "43.01.001": {"desc": "FONDO RINNOVI CONTRATTUALI", "tipo": "Patrimoniale Passivo"},
    "52.01.001": {"desc": "RATEI PASSIVI", "tipo": "Patrimoniale Passivo"},
    "52.01.005": {"desc": "RISCONTI PASSIVI", "tipo": "Patrimoniale Passivo"},
    "16.05.001": {"desc": "F.DO AMM.TO ATTREZZATURE IND.", "tipo": "Patrimoniale Passivo"},
    "19.03.013": {"desc": "F.DO SVALUT. IMPIANTO ELETTRICO", "tipo": "Patrimoniale Passivo"},
    
    "79.01.005": {"desc": "COMPETENZE FISSE PERSONALE", "tipo": "Economico Costi"},
    "79.05.001": {"desc": "ACC.TO FONDO TFR", "tipo": "Economico Costi"},
    "77.03.001": {"desc": "CANONI LEASING", "tipo": "Economico Costi"},
    "75.17.033": {"desc": "COSTI MISSIONE", "tipo": "Economico Costi"},
    "85.15.013": {"desc": "SVALUTAZIONE IMPIANTI ELETTRICI", "tipo": "Economico Costi"},
    "93.17.005": {"desc": "PERDITE SU CAMBI", "tipo": "Economico Costi"},
    "71.01.049": {"desc": "PROVENTI PER DONAZIONE", "tipo": "Economico Ricavi"}, # Mappatura standard
    "95.01.005": {"desc": "PLUSVALENZE", "tipo": "Economico Ricavi"},
    "95.03.005": {"desc": "MINUSVALENZE", "tipo": "Economico Costi"},
    "71.01.081": {"desc": "CONTRIBUTI C/CAPITALE", "tipo": "Economico Ricavi"},
    "55.01.001": {"desc": "BILANCIO DI APERTURA", "tipo": "Patrimoniale"},
    "55.01.005": {"desc": "BILANCIO DI CHIUSURA", "tipo": "Patrimoniale"}
}

# Mappatura Concetti Manuale -> Codici SPIACO
MAPPING = {
    "Depositi bancari": "34.01.001",
    "Fondo rinnovi contrattuali": "43.01.001",
    "Iva a credito": "28.11.009",
    "Risconti attivi": "37.01.005",
    "Risconti passivi": "52.01.005",
    "Ratei attivi": "37.01.001",
    "Ratei passivi": "52.01.001",
    "Crediti per anticipi missioni": "28.15.053",
    "Attrezzature scientifiche": "13.05.053",
    "Impianto elettrico": "13.05.017",
    "Competenze fisse personale": "79.01.005",
    "Erario c/IRPEF": "49.23.029",
    "Debiti verso istituti previdenziali": "49.25.001",
    "Debiti verso altri privati": "49.27.041",
    "Debiti verso dipendenti": "49.27.025",
    "Acc.to TFR": "79.05.001",
    "Fondo TFR": "46.01.001",
    "Fornitori": "49.13.001",
    "Erario c/IVA Split": "49.23.009",
    "Canoni leasing": "77.03.001",
    "F.do amm.to attrezzature": "16.05.001",
    "Proventi per donazione": "71.01.049",
    "Fondo svalutazione impianti": "19.03.013",
    "Svalutazione impianti": "85.15.013",
    "Perdite su cambi": "93.17.005",
    "Plusvalenze": "95.01.005",
    "Minusvalenze": "95.03.005",
    "Contributi c/capitale": "71.01.081",
    "Costi missione": "75.17.033",
    "Bilancio apertura": "55.01.001",
    "Bilancio chiusura": "55.01.005"
}

# ==============================================================================
# 2. STRUTTURE DATI
# ==============================================================================
@dataclass
class Riga:
    codice: str
    descrizione: str
    dare: float = 0.0
    avere: float = 0.0

@dataclass
class Scrittura:
     str
    titolo: str
    righe: List[Riga] = field(default_factory=list)
    
    def totale_dare(self) -> float: return sum(r.dare for r in self.righe)
    def totale_avere(self) -> float: return sum(r.avere for r in self.righe)
    def bilanciata(self) -> bool: return abs(self.totale_dare() - self.totale_avere()) < 0.01

# ==============================================================================
# 3. GENERATORE SCRITTURE (Completato con tutti i casi del PDF)
# ==============================================================================
class GeneratoreContabile:
    def __init__(self):
        self.scritture: List[Scrittura] = []

    def _aggiungi(self, scrittura: Scrittura):
        if not scrittura.bilanciata():
            raise ValueError(f"Scrittura '{scrittura.titolo}' NON BILANCIATA!")
        self.scritture.append(scrittura)

    def _get_codice(self, concetto: str) -> str:
        cod = MAPPING.get(concetto)
        if not cod: raise KeyError(f"Concetto '{concetto}' non mappato.")
        return cod

    def ammortamento_attrezzature(self, data: str, importo: float):
        """Manuale: Ammortamento attrezzature scientifiche (es. 20.000)"""
        s = Scrittura(data, "Ammortamento Attrezzature Scientifiche")
        s.righe.append(Riga(self._get_codice("Svalutazione impianti") if False else self._get_codice("Competenze fisse personale"), COA[self._get_codice("Competenze fisse personale")]["desc"], dare=importo)) 
        # Nota: Il manuale usa un conto di ammortamento specifico. Usiamo "Svalutazione impianti" o generico costo.
        # Per coerenza con SPIACO usiamo un conto Economico Costi generico se non specificato, 
        # ma qui mappiamo "Svalutazione impianti" come costo per questa demo.
        s.righe.pop() # Rimuovo riga precedente
        s.righe.append(Riga(self._get_codice("Svalutazione impianti") or "85.15.013", COA["85.15.013"]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("F.do amm.to attrezzature"), COA[self._get_codice("F.do amm.to attrezzature")]["desc"], avere=importo))
        self._aggiungi(s)

    def leasing_split_payment(self, data: str, canone: float, iva: float):
        """Manuale: Pagamento canone leasing (Split Payment)"""
        s = Scrittura(data, "Pagamento Canone Leasing (Split)")
        s.righe.append(Riga(self._get_codice("Canoni leasing"), COA[self._get_codice("Canoni leasing")]["desc"], dare=canone + iva)) # Costo + IVA indetraibile
        s.righe.append(Riga(self._get_codice("Fornitori"), COA[self._get_codice("Fornitori")]["desc"], avere=canone))
        s.righe.append(Riga(self._get_codice("Erario c/IVA Split"), COA[self._get_codice("Erario c/IVA Split")]["desc"], avere=iva))
        self._aggiungi(s)

    def pagamento_fornitore(self,  str, importo: float):
        """Manuale: Pagamento debito verso fornitori"""
        s = Scrittura(data, "Pagamento Fornitore")
        s.righe.append(Riga(self._get_codice("Fornitori"), COA[self._get_codice("Fornitori")]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Depositi bancari"), COA[self._get_codice("Depositi bancari")]["desc"], avere=importo))
        self._aggiungi(s)

    def liquidazione_personale(self, data: str, lordo: float, irpef: float, inps: float, altri: float):
        """Manuale: Competenze fisse al personale"""
        netto = lordo - irpef - inps - altri
        s = Scrittura(data, "Liquidazione Competenze Fisse Personale")
        s.righe.append(Riga(self._get_codice("Competenze fisse personale"), COA[self._get_codice("Competenze fisse personale")]["desc"], dare=lordo))
        s.righe.append(Riga(self._get_codice("Erario c/IRPEF"), COA[self._get_codice("Erario c/IRPEF")]["desc"], avere=irpef))
        s.righe.append(Riga(self._get_codice("Debiti verso istituti previdenziali"), COA[self._get_codice("Debiti verso istituti previdenziali")]["desc"], avere=inps))
        s.righe.append(Riga(self._get_codice("Debiti verso altri privati"), COA[self._get_codice("Debiti verso altri privati")]["desc"], avere=altri))
        s.righe.append(Riga(self._get_codice("Debiti verso dipendenti"), COA[self._get_codice("Debiti verso dipendenti")]["desc"], avere=netto))
        self._aggiungi(s)

    def pagamento_retribuzioni(self,  str, importo: float):
        """Manuale: Pagamento retribuzioni nette"""
        s = Scrittura(data, "Pagamento Retribuzioni")
        s.righe.append(Riga(self._get_codice("Debiti verso dipendenti"), COA[self._get_codice("Debiti verso dipendenti")]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Depositi bancari"), COA[self._get_codice("Depositi bancari")]["desc"], avere=importo))
        self._aggiungi(s)

    def accantonamento_tfr(self, data: str, importo: float):
        """Manuale: Accantonamento TFR"""
        s = Scrittura(data, "Accantonamento TFR")
        s.righe.append(Riga(self._get_codice("Acc.to TFR"), COA[self._get_codice("Acc.to TFR")]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Fondo TFR"), COA[self._get_codice("Fondo TFR")]["desc"], avere=importo))
        self._aggiungi(s)

    def anticipo_missione(self,  str, importo: float):
        """Manuale: Anticipo missione (75% dei costi)"""
        s = Scrittura(data, "Anticipo Missione Docente")
        s.righe.append(Riga(self._get_codice("Crediti per anticipi missioni"), COA[self._get_codice("Crediti per anticipi missioni")]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Depositi bancari"), COA[self._get_codice("Depositi bancari")]["desc"], avere=importo))
        self._aggiungi(s)

    def rendicontazione_missione(self,  str, costo_totale: float, anticipo: float):
        """Manuale: Chiusura missione e debito residuo"""
        saldo = costo_totale - anticipo
        s = Scrittura(data, "Rendicontazione Missione")
        s.righe.append(Riga(self._get_codice("Costi missione"), COA[self._get_codice("Costi missione")]["desc"], dare=costo_totale))
        s.righe.append(Riga(self._get_codice("Crediti per anticipi missioni"), COA[self._get_codice("Crediti per anticipi missioni")]["desc"], avere=anticipo))
        s.righe.append(Riga(self._get_codice("Debiti verso dipendenti"), COA[self._get_codice("Debiti verso dipendenti")]["desc"], avere=saldo))
        self._aggiungi(s)

    def pagamento_missione(self,  str, saldo: float):
        """Manuale: Pagamento saldo missione"""
        s = Scrittura(data, "Pagamento Saldo Missione")
        s.righe.append(Riga(self._get_codice("Debiti verso dipendenti"), COA[self._get_codice("Debiti verso dipendenti")]["desc"], dare=saldo))
        s.righe.append(Riga(self._get_codice("Depositi bancari"), COA[self._get_codice("Depositi bancari")]["desc"], avere=saldo))
        self._aggiungi(s)

    def donazione_cespite(self,  str, valore: float):
        """Manuale: Ricezione attrezzatura per donazione"""
        s = Scrittura(data, "Donazione Attrezzatura Scientifica")
        s.righe.append(Riga(self._get_codice("Attrezzature scientifiche"), COA[self._get_codice("Attrezzature scientifiche")]["desc"], dare=valore))
        s.righe.append(Riga(self._get_codice("Proventi per donazione"), COA[self._get_codice("Proventi per donazione")]["desc"], avere=valore))
        self._aggiungi(s)

    def svalutazione_impianri(self,  str, importo: float):
        """Manuale: Svalutazione impianto elettrico"""
        s = Scrittura(data, "Svalutazione Impianto Elettrico")
        s.righe.append(Riga(self._get_codice("Svalutazione impianti"), COA["85.15.013"]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Fondo svalutazione impianti"), COA["19.03.013"]["desc"], avere=importo))
        self._aggiungi(s)

    def perdite_su_cambi(self,  str, importo: float):
        """Manuale: Perdite su cambi (es. 197,62)"""
        s = Scrittura(data, "Perdite su cambi")
        s.righe.append(Riga(self._get_codice("Perdite su cambi"), COA["93.17.005"]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Fornitori"), COA[self._get_codice("Fornitori")]["desc"], avere=importo))
        self._aggiungi(s)

    def rateo_attivo_contributi(self, data: str, importo: float):
        """Manuale: Rateo attivo contributi studenteschi"""
        s = Scrittura(data, "Rateo Attivo Contributi")
        s.righe.append(Riga(self._get_codice("Ratei attivi"), COA[self._get_codice("Ratei attivi")]["desc"], dare=importo))
        s.righe.append(Riga("71.01.085", COA["71.01.085"]["desc"], avere=importo)) # Contributi c/esercizio
        self._aggiungi(s)

    def risconto_passivo_contributi(self, data: str, importo: float):
        """Manuale: Risconto passivo contributi"""
        s = Scrittura(data, "Risconto Passivo Contributi")
        s.righe.append(Riga("71.01.085", COA["71.01.085"]["desc"], dare=importo))
        s.righe.append(Riga(self._get_codice("Risconti passivi"), COA[self._get_codice("Risconti passivi")]["desc"], avere=importo))
        self._aggiungi(s)

    def report(self):
        df_list = []
        for s in self.scritture:
            for r in s.righe:
                df_list.append({
                    "Data": s.data,
                    "Operazione": s.titolo,
                    "Codice": r.codice,
                    "Descrizione": r.descrizione,
                    "Dare": r.dare if r.dare > 0 else "",
                    "Avere": r.avere if r.avere > 0 else ""
                })
        df = pd.DataFrame(df_list)
        df.to_csv("Scritture_Manuale_Completo.csv", index=False, sep=";", decimal=",")
        return df

# ==============================================================================
# 4. ESECUZIONE
# ==============================================================================
if __name__ == "__main__":
    gen = GeneratoreContabile()
    print("🔄 Generazione completa scritture dal Manuale...")
    
    # 1. Ammortamento (20.000)
    gen.ammortamento_attrezzature("31/12/200n", 20_000.00)
    
    # 2. Leasing (Maxicanone)
    gen.leasing_split_payment("01/09/200n", canone=6_000.00, iva=1_320.00)
    gen.pagamento_fornitore("01/09/200n", 6_000.00)
    
    # 3. Personale (Liquidazione)
    gen.liquidazione_personale("30/06/200n", lordo=10_000.00, irpef=2_000.00, inps=1_000.00, altri=200.00)
    gen.pagamento_retribuzioni("05/07/200n", 6_800.00)
    
    # 4. TFR
    gen.accantonamento_tfr("31/12/200n", 3_500.00)
    
    # 5. Missione (Anticipo 1.500 + Rendicontazione 1.800)
    gen.anticipo_missione("10/05/200n", 1_500.00)
    gen.rendicontazione_missione("30/06/200n", costo_totale=1_800.00, anticipo=1_500.00)
    gen.pagamento_missione("10/07/200n", saldo=300.00)
    
    # 6. Donazione Attrezzatura (40.000)
    gen.donazione_cespite("15/11/200n", 40_000.00)
    
    # 7. Svalutazione Impianto Elettrico (30.000)
    gen.svalutazione_impianri("31/12/200n", 30_000.00)
    
    # 8. Perdite su cambi (197,62)
    gen.perdite_su_cambi("31/12/200n", 197.62)
    
    # 9. Ratei/Risconti
    gen.rateo_attivo_contributi("31/12/200n", 580.50)
    gen.risconto_passivo_contributi("31/12/200n", 1_741.50)
    
    # Export
    df = gen.report()
    print(df.to_string(index=False))
    print("\n✅ Generazione completata. File CSV salvato.")
