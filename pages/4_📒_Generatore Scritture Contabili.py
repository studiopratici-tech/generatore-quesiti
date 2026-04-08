#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestore Scritture Contabili - Manuale Partita Doppia + Piano dei Conti SPIACO
Validazione partita doppia, mappatura codici, esportazione CSV/JSON.
"""

import csv
import json
import re
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from decimal import Decimal, getcontext

# Precisione contabile italiana
getcontext().prec = 12

@dataclass
class RigaContabile:
    codice_sp: str
    descrizione: str
    importo: Decimal

@dataclass
class ScritturaContabile:
    data: str
    descrizione: str
    dare: List[RigaContabile] = field(default_factory=list)
    avere: List[RigaContabile] = field(default_factory=list)

    def totale_dare(self) -> Decimal:
        return sum(r.importo for r in self.dare)

    def totale_avere(self) -> Decimal:
        return sum(r.importo for r in self.avere)

    def e_quadrata(self) -> bool:
        return abs(self.totale_dare() - self.totale_avere()) < Decimal("0.01")

# ==============================================================================
# 1. MAPPATURA MANUALE -> SPIACO (da completare con tutti i conti del manuale)
# ==============================================================================
MAPPATURA_CONTI: Dict[str, str] = {
    # Clienti e Crediti
    "Clienti": "28.01.001", "Clienti c/vendite": "28.01.001", "Crediti vs. clienti": "28.01.001",
    "Crediti vs fornitori": "28.01.001", "Fatture da emettere": "28.01.037",
    
    # Fornitori e Debiti
    "Fornitore": "49.13.001", "Fornitori": "49.13.001", "Debiti vs. fornitori": "49.13.001",
    "Debiti vs fornitori": "49.13.001", "Fatture da ricevere": "49.13.005",
    
    # IVA
    "IVA a debito": "49.23.013", "IVA ns. debito": "49.23.013", "IVA su vendite": "49.23.013",
    "IVA a credito": "28.11.017", "IVA ns. credito": "28.11.017", "IVA su acquisti": "28.11.017",
    "IVA indetraibile": "92.01.025", "Erario c/IVA": "49.23.009",
    
    # Tesoreria
    "Banca": "34.01.001", "Banca c/c": "34.01.001", "Cassa": "34.05.001", "Cassa contanti": "34.05.001",
    "Assegni": "34.03.001", "Cassa assegni": "34.03.001",
    
    # Ricavi e Costi
    "Merci c/vendite": "60.01.001", "Ricavi c/vendite": "60.01.001", "Prodotti c/vendite": "60.01.001",
    "Merci c/acquisti": "73.01.013", "Merci conto acquisti": "73.01.013", "Merci c/acquisti esteri": "73.01.013",
    "Spese di trasporto": "75.01.005", "Oneri bancari": "92.01.001", "Commissioni bancarie": "93.15.061",
    
    # Immobilizzazioni e Ammortamenti
    "Impianti": "13.05.053", "Macchinari": "13.05.053", "Automezzi": "13.09.001",
    "F.do ammortamento": "16.00.000", "Ammortamento": "83.00.000",
    
    # Patrimonio e Utili
    "Capitale sociale": "40.01.001", "Riserva legale": "40.07.001", "Utile d'esercizio": "40.17.001",
    "Perdita d'esercizio": "40.17.005", "Dividendi": "49.27.089",
    
    # Finanziari
    "Interessi attivi": "93.13.001", "Interessi passivi": "93.15.001",
    "Crediti finanziari": "22.23.001", "Debiti finanziari": "49.09.001",
    
    # Personale
    "Salari e stipendi": "79.01.001", "Oneri sociali": "79.03.001", "Personale c/retribuzioni": "49.27.025",
    "Fondo TFR": "46.01.001", "INPS c/contributi": "49.25.001", "Erario c/ritenute": "49.23.029"
}

# Mappatura inversa per reportistica
MAPPATURA_INVERSA = {v: k for k, v in MAPPATURA_CONTI.items()}

def risolvi_codice_spiaco(nome_conto_manuale: str) -> str:
    """Restituisce il codice SPIACO più probabile. Se non trovato, cerca per keyword."""
    nome_pulito = nome_conto_manuale.strip().lower()
    if nome_pulito in {k.lower(): v for k, v in MAPPATURA_CONTI.items()}:
        return MAPPATURA_CONTI[nome_conto_manuale]
    
    # Fallback euristico (da affinare in produzione)
    for chiave, codice in MAPPATURA_CONTI.items():
        if chiave.lower() in nome_pulito or nome_pulito in chiave.lower():
            return codice
    return "00.00.000"  # Codice non mappato

def valida_scrittura(scrittura: ScritturaContabile) -> Tuple[bool, str]:
    if not scrittura.e_quadrata():
        diff = scrittura.totale_dare() - scrittura.totale_avere()
        return False, f"Scrittura non quadrata: differenza {diff:.2f}"
    return True, "OK"

def esporta_csv(scritture: List[ScritturaContabile], path: str):
    with open(path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            "Data", "Descrizione", "Dare/Avere", "Codice_SPIACO", 
            "Descrizione_Conto", "Importo", "Stato"
        ])
        for s in scritture:
            ok, msg = valida_scrittura(s)
            stato = "VALIDA" if ok else f"ERRORE: {msg}"
            for riga in s.dare:
                writer.writerow([s.data, s.descrizione, "DARE", riga.codice_sp, riga.descrizione, riga.importo, stato])
            for riga in s.avere:
                writer.writerow([s.data, s.descrizione, "AVERE", riga.codice_sp, riga.descrizione, riga.importo, stato])
    print(f"✅ Esportate {len(scritture)} scritture in {path}")

def esporta_json(scritture: List[ScritturaContabile], path: str):
    data = []
    for s in scritture:
        ok, _ = valida_scrittura(s)
        data.append({
            "data": s.data,
            "descrizione": s.descrizione,
            "quadrata": ok,
            "dare": [{"codice": r.codice_sp, "conto": r.descrizione, "importo": float(r.importo)} for r in s.dare],
            "avere": [{"codice": r.codice_sp, "conto": r.descrizione, "importo": float(r.importo)} for r in s.avere]
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Esportato JSON in {path}")

# ==============================================================================
# ESEMPIO DI UTILIZZO (sostituire con dati estratti dal PDF)
# ==============================================================================
if __name__ == "__main__":
    # Esempio tratto dal manuale: Acquisto merci €10.000 + IVA 20%
    s1 = ScritturaContabile(
        data="2024-01-15",
        descrizione="Acquisto merci da fornitore Alfa"
    )
    s1.dare.append(RigaContabile(risolvi_codice_spiaco("Merci c/acquisti"), "Merci c/acquisti", Decimal("10000.00")))
    s1.dare.append(RigaContabile(risolvi_codice_spiaco("IVA su acquisti"), "IVA su acquisti", Decimal("2000.00")))
    s1.avere.append(RigaContabile(risolvi_codice_spiaco("Fornitore"), "Debiti vs fornitori", Decimal("12000.00")))

    # Esempio 2: Vendita con sconto cassa
    s2 = ScritturaContabile(
        data="2024-01-20",
        descrizione="Vendita merci con sconto cassa 2%"
    )
    s2.dare.append(RigaContabile(risolvi_codice_spiaco("Clienti"), "Crediti vs clienti", Decimal("1176.00")))
    s2.dare.append(RigaContabile(risolvi_codice_spiaco("Sconti passivi"), "Sconti passivi", Decimal("24.00")))
    s2.avere.append(RigaContabile(risolvi_codice_spiaco("Merci c/vendite"), "Ricavi da cessione beni", Decimal("1000.00")))
    s2.avere.append(RigaContabile(risolvi_codice_spiaco("IVA a debito"), "IVA vendite", Decimal("200.00")))

    scritture = [s1, s2]
    
    # Validazione e report
    for s in scritture:
        ok, msg = valida_scrittura(s)
        print(f"📄 {s.descrizione} -> {'✅' if ok else '❌'} {msg}")
        
    esporta_csv(scritture, "scritture_partita_doppia.csv")
    esporta_json(scritture, "scritture_partita_doppia.json")
