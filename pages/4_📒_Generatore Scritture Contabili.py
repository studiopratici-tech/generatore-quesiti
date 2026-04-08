import csv
import random
import datetime

# ==============================================================================
# CONFIGURAZIONE E MAPPATURA PIANO DEI CONTI SPIACO
# ==============================================================================

# Mappatura basata sul file SPIACO_260323082320.pdf fornito
SPIACO = {
    # PATRIMONIALI / FINANZIARI
    "BANCA": {"codice": "34.01.001", "descrizione": "BANCA C/C A", "tipo": "Attivo"},
    "CASSA": {"codice": "34.05.001", "descrizione": "CASSA CONTANTI", "tipo": "Attivo"},
    "CLIENTI": {"codice": "28.01.001", "descrizione": "CLIENTE", "tipo": "Attivo"},
    "FORNITORI": {"codice": "49.13.001", "descrizione": "FORNITORE", "tipo": "Passivo"},
    "CREDITI_DIVERSI": {"codice": "28.15.125", "descrizione": "CREDITI DIVERSI", "tipo": "Attivo"},
    "DEBITI_DIVERSI": {"codice": "49.27.113", "descrizione": "DEBITI DIVERSI", "tipo": "Passivo"},
    "ERARIO_IVA_DEB": {"codice": "49.23.013", "descrizione": "ERARIO C/IVA VENDITE", "tipo": "Passivo"},
    "ERARIO_IVA_CRED": {"codice": "28.11.017", "descrizione": "ERARIO C/IVA ACQUISTI", "tipo": "Attivo"},
    "ERARIO_IRAP": {"codice": "49.23.005", "descrizione": "ERARIO C/IRAP", "tipo": "Passivo"},
    "ERARIO_IRES": {"codice": "49.23.001", "descrizione": "ERARIO C/IRES", "tipo": "Passivo"},
    
    # CE / COSTI
    "MERCI_ACQ": {"codice": "73.01.013", "descrizione": "MERCI C/ACQUISTI", "tipo": "Costo"},
    "SPESE_TRASPORTO": {"codice": "75.01.005", "descrizione": "TRASPORTI", "tipo": "Costo"},
    "SPESE_TEL": {"codice": "75.11.113", "descrizione": "SPESE TELEFONICHE", "tipo": "Costo"},
    "SPESE_BANCARIE": {"codice": "92.01.001", "descrizione": "IMPOSTA DI BOLLO", "tipo": "Costo"}, # O 93.15.086 SPESE DIVERSE BANCARIE
    "MANUTENZIONI": {"codice": "75.05.181", "descrizione": "MANUTENZIONI E RIPARAZIONI", "tipo": "Costo"},
    "SALARI": {"codice": "79.01.001", "descrizione": "SALARI", "tipo": "Costo"},
    "ONERI_SOCIALI": {"codice": "79.03.001", "descrizione": "ONERI INPS", "tipo": "Costo"},
    "AMMORTAMENTO_AUTO": {"codice": "83.09.001", "descrizione": "AMM.TO AUTOVETTURE", "tipo": "Costo"},
    "AMMORTAMENTO_PC": {"codice": "83.09.065", "descrizione": "AMM.TO COMPUTER ED ACCESSORI", "tipo": "Costo"},
    
    # CE / RICAVI
    "MERCI_VEND": {"codice": "60.01.001", "descrizione": "RICAVI DA CESSIONI DI BENI", "tipo": "Ricavo"},
    "PROVENTI_DIVERSI": {"codice": "71.01.049", "descrizione": "RICAVI ACCESSORI DIVERSI", "tipo": "Ricavo"},
    
    # ALTRO
    "FONDO_AMM_AUTO": {"codice": "16.07.001", "descrizione": "F.DO AMM.TO AUTOVETTURE", "tipo": "Rettifica"},
    "FONDO_AMM_PC": {"codice": "16.07.045", "descrizione": "F.DO AMM.TO COMPUTER ED ACCESSORI", "tipo": "Rettifica"},
    "FONDO_TFR": {"codice": "46.01.001", "descrizione": "FONDO T.F.R.", "tipo": "Passivo"},
}

# Generatori di dati casuali per variare le scritture
NOMI_FORNITORI = ["FORNITORE ALFA S.P.A.", "LOGISTICA BETA SRL", "ENERGIA GAMMA SPA", "TELECOM DELTA SRL"]
NOMI_CLIENTI = ["CLIENTE ROSSI SRL", "DISTRIBUZIONE BIANCHI", "IMPORT EXPORT VERDI", "SERVIZI NERI SPA"]
DESCRIZIONI_SPEDIZIONI = ["Spedizione merci", "Trasporto nazionale", "Corriere espresso"]
DESCRIZIONI_UTENZE = ["Bolletta Elettricità", "Gas metano", "Fibra ottica mensile"]

scritture = []
id_scrittura = 1

def aggiungi_riga(data, dare_avere, codice, descrizione, importo, ref_scrittura, desc_op):
    global id_scrittura
    # Se è una nuova operazione, incrementiamo ID o usiamo ref
    if ref_scrittura: id = ref_scrittura
    else: 
        id = id_scrittura
        id_scrittura += 1
    
    # Determina se dare o avere in base al tipo di conto e al lato (semplificato per CSV)
    # Nel CSV finale avremo colonne: Data, Dare/Avere, Codice, Descrizione, Importo, Rif
    
    dare = importo if dare_avere == "DARE" else 0.00
    avere = importo if dare_avere == "AVERE" else 0.00
    
    scritture.append([data, dare_avere, codice, descrizione, dare, avere, desc_op, id])

# ==============================================================================
# GENERATORE DI SCRITTURE (LOOP SIMULAZIONE ANNO)
# ==============================================================================

# 1. ACQUISTI MERCI (Frequenza: ~200)
data_base = datetime.date(2024, 1, 15)
for i in range(150):
    dt = data_base + datetime.timedelta(days=i*2)
    importo_netto = round(random.uniform(500, 5000), 2)
    importo_iva = round(importo_netto * 0.22, 2)
    importo_tot = importo_netto + importo_iva
    forn = random.choice(NOMI_FORNITORI)
    rif = f"FATT.{2000+i} DEL {dt.strftime('%d/%m')}"
    
    # Contropartita Fornitore (Avere)
    aggiungi_riga(dt, "AVERE", SPIACO["FORNITORI"]["codice"], f"{SPIACO['FORNITORI']['descrizione']} - {forn}", importo_tot, None, f"Ricevuta {rif}")
    # Conto Costo (Dare)
    aggiungi_riga(dt, "DARE", SPIACO["MERCI_ACQ"]["codice"], SPIACO["MERCI_ACQ"]["descrizione"], importo_netto, rif, "Acquisto Merci")
    # IVA Credito (Dare)
    aggiungi_riga(dt, "DARE", SPIACO["ERARIO_IVA_CRED"]["codice"], SPIACO["ERARIO_IVA_CRED"]["descrizione"], importo_iva, rif, "IVA Acquisti")

# 2. VENDITE MERCI (Frequenza: ~200)
for i in range(150):
    dt = data_base + datetime.timedelta(days=i*2 + 5)
    importo_netto = round(random.uniform(1000, 8000), 2)
    importo_iva = round(importo_netto * 0.22, 2)
    importo_tot = importo_netto + importo_iva
    cli = random.choice(NOMI_CLIENTI)
    rif = f"FATT.V/{1000+i}"
    
    # Contropartita Cliente (Dare)
    aggiungi_riga(dt, "DARE", SPIACO["CLIENTI"]["codice"], f"{SPIACO['CLIENTI']['descrizione']} - {cli}", importo_tot, None, f"Emissione {rif}")
    # Conto Ricavo (Avere)
    aggiungi_riga(dt, "AVERE", SPIACO["MERCI_VEND"]["codice"], SPIACO["MERCI_VEND"]["descrizione"], importo_netto, rif, "Vendita Merci")
    # IVA Debito (Avere)
    aggiungi_riga(dt, "AVERE", SPIACO["ERARIO_IVA_DEB"]["codice"], SPIACO["ERARIO_IVA_DEB"]["descrizione"], importo_iva, rif, "IVA Vendite")

# 3. SPESE DI SERVIZIO E ACQUISTI VARI (Frequenza: ~100)
servizi = [
    {"codice": "SPESE_TEL", "desc": "Bolletta Telefonica"},
    {"codice": "SPESE_TRASPORTO", "desc": "Spedizione Corriere"},
    {"codice": "MANUTENZIONI", "desc": "Riparazione Macchinario"}
]

for i in range(100):
    dt = data_base + datetime.timedelta(days=i*3)
    serv = random.choice(servizi)
    importo = round(random.uniform(100, 1000), 2)
    iva = round(importo * 0.22, 2)
    tot = importo + iva
    rif = f"SPESA/{i}"
    
    aggiungi_riga(dt, "AVERE", SPIACO["BANCA"]["codice"], SPIACO["BANCA"]["descrizione"], tot, None, f"Pagamento {serv['desc']}")
    aggiungi_riga(dt, "DARE", SPIACO[serv["codice"]]["codice"], SPIACO[serv["codice"]]["descrizione"], importo, rif, serv["desc"])
    aggiungi_riga(dt, "DARE", SPIACO["ERARIO_IVA_CRED"]["codice"], SPIACO["ERARIO_IVA_CRED"]["descrizione"], iva, rif, "IVA Servizio")

# 4. INCASSI E PAGAMENTI (Frequenza: ~150)
for i in range(100):
    # Pagamento Fornitore
    dt = data_base + datetime.timedelta(days=i*4)
    importo = round(random.uniform(1000, 5000), 2)
    rif = f"PAG.FOR.{i}"
    aggiungi_riga(dt, "DARE", SPIACO["FORNITORI"]["codice"], SPIACO["FORNITORI"]["descrizione"], importo, None, f"Saldo fornitore {rif}")
    aggiungi_riga(dt, "AVERE", SPIACO["BANCA"]["codice"], SPIACO["BANCA"]["descrizione"], importo, rif, "Pagamento Banca")

for i in range(50):
    # Incasso Cliente
    dt = data_base + datetime.timedelta(days=i*5 + 10)
    importo = round(random.uniform(2000, 10000), 2)
    rif = f"INC.CLI.{i}"
    aggiungi_riga(dt, "DARE", SPIACO["BANCA"]["codice"], SPIACO["BANCA"]["descrizione"], importo, None, f"Ricevuto da cliente {rif}")
    aggiungi_riga(dt, "AVERE", SPIACO["CLIENTI"]["codice"], SPIACO["CLIENTI"]["descrizione"], importo, rif, "Incasso Banca")

# 5. CHIUSURE E ASSESTAMENTI (Stipendi, Ammortamenti, TFR) - ~50

# Stipendi (Mensili)
for mese in range(1, 13):
    dt = datetime.date(2024, mese, 27)
    lordo = 30000.00
    netto = 22000.00
    ritenute = 8000.00
    
    rif = f"BUSTA.PAGA.{mese}"
    aggiungi_riga(dt, "DARE", SPIACO["SALARI"]["codice"], SPIACO["SALARI"]["descrizione"], lordo, None, f"Competenza Stipendio {mese}")
    aggiungi_riga(dt, "DARE", SPIACO["ONERI_SOCIALI"]["codice"], SPIACO["ONERI_SOCIALI"]["descrizione"], 10000.00, None, f"Oneri Azienda {mese}")
    aggiungi_riga(dt, "AVERE", SPIACO["DEBITI_DIVERSI"]["codice"], "DEBITI VS DIPENDENTI", netto, rif, "Netto a pagare")
    aggiungi_riga(dt, "AVERE", SPIACO["ERARIO_IRES"]["codice"], "ERARIO C/RITENUTE LAVORO DIP.", 5000.00, rif, "Ritenute Irpef")
    aggiungi_riga(dt, "AVERE", SPIACO["ONERI_SOCIALI"]["codice"], "ONERI INPS DIPENDENTE", 3000.00, rif, "INPS a carico dip.")

# TFR (Annuale)
aggiungi_riga(datetime.date(2024, 12, 31), "DARE", "79.05.001", "ACC.TO FONDO TFR", 3500.00, "TFR.ANN", "Accantonamento TFR")
aggiungi_riga(datetime.date(2024, 12, 31), "AVERE", SPIACO["FONDO_TFR"]["codice"], SPIACO["FONDO_TFR"]["descrizione"], 3500.00, "TFR.ANN", "Fondo TFR")

# Ammortamenti (Annuale)
aggiungi_riga(datetime.date(2024, 12, 31), "DARE", SPIACO["AMMORTAMENTO_AUTO"]["codice"], SPIACO["AMMORTAMENTO_AUTO"]["descrizione"], 4500.00, "AMM.AUTO", "Ammortamento Auto")
aggiungi_riga(datetime.date(2024, 12, 31), "AVERE", SPIACO["FONDO_AMM_AUTO"]["codice"], SPIACO["FONDO_AMM_AUTO"]["descrizione"], 4500.00, "AMM.AUTO", "Fondo Amm. Auto")

aggiungi_riga(datetime.date(2024, 12, 31), "DARE", SPIACO["AMMORTAMENTO_PC"]["codice"], SPIACO["AMMORTAMENTO_PC"]["descrizione"], 800.00, "AMM.PC", "Ammortamento PC")
aggiungi_riga(datetime.date(2024, 12, 31), "AVERE", SPIACO["FONDO_AMM_PC"]["codice"], SPIACO["FONDO_AMM_PC"]["descrizione"], 800.00, "AMM.PC", "Fondo Amm. PC")

# Liquidazione IVA Trimestrale (Esempio Q4)
aggiungi_riga(datetime.date(2024, 12, 31), "DARE", SPIACO["ERARIO_IVA_DEB"]["codice"], SPIACO["ERARIO_IVA_DEB"]["descrizione"], 15000.00, "LIQ.IVA", "Giroconto IVA Vendite")
aggiungi_riga(datetime.date(2024, 12, 31), "AVERE", SPIACO["ERARIO_IVA_CRED"]["codice"], SPIACO["ERARIO_IVA_CRED"]["descrizione"], 15000.00, "LIQ.IVA", "Giroconto IVA Acquisti")


# ==============================================================================
# SALVATAGGIO SU CSV
# ==============================================================================
filename = "600_Scritture_SPIACO.csv"
with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow([
        "Data", "Dare_Avere", "Codice_SPIACO", "Descrizione_Conto", 
        "Importo_Dare", "Importo_Avere", "Riferimento", "Descrizione_Operazione"
    ])
    for riga in sorted(scritture, key=lambda x: (x[7], x[0])): # Ordina per ID scrittura e Data
        writer.writerow(riga)

print(f"✅ Creato con successo: {filename}")
print(f"📊 Totale righe generate: {len(scritture)}")
