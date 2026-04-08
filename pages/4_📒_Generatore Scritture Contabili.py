import streamlit as st
import pandas as pd
import re
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAZIONE PAGINA
# ==============================================================================
st.set_page_config(layout="wide", page_title="Generatore Contabile Professionale")

# ==============================================================================
# 2. DATABASE PIANO DEI CONTI (Estratto dal PDF fornito)
# ==============================================================================
# Inserisco il testo grezzo per permettere all'app di funzionare "out-of-the-box"
# In produzione, questo verrebbe letto da st.file_uploader
PDF_TEXT_SOURCE = """
01.01.001 SOCI C/SOTTOSCRIZIONE Patrimoniale attivo
01.01.021 SOCI C/DECIMI RICHIAMATI Patrimoniale attivo
04.01.001 SPESE DI IMPIANTO Patrimoniale attivo
04.01.009 SPESE DI COSTITUZIONE Patrimoniale attivo
04.01.013 SPESE DI FUSIONE Patrimoniale attivo
04.01.017 SPESE DI SCISSIONE Patrimoniale attivo
04.01.049 SPESE DI ORGANIZZAZIONE Patrimoniale attivo
04.05.001 BREVETTI INDUSTRIALI Patrimoniale attivo
04.05.013 SOFTWARE SPECIFICO Patrimoniale attivo
04.09.001 AVVIAMENTO Patrimoniale attivo
07.09.001 F.DO AMM.TO AVVIAMENTO Patrimoniale passivo
13.01.001 TERRENO Patrimoniale attivo
13.03.001 FABBRICATI CIVILI Patrimoniale attivo
13.03.005 FABBRICATI INDUSTRIALI Patrimoniale attivo
13.05.009 IMPIANTO ELETTRICO Patrimoniale attivo
13.09.001 AUTOVETTURE Patrimoniale attivo
13.09.005 AUTOCARRI Patrimoniale attivo
13.09.017 AUTOVETTURE PROFESSIONISTA Patrimoniale attivo
13.09.025 AUTOVETTURE USO PROMISCUO DIPENDENTE Patrimoniale attivo
13.09.061 MACCHINE D ' UFFICIO ELETTRONICHE Patrimoniale attivo
13.09.065 COMPUTER ED ACCESSORI Patrimoniale attivo
13.09.069 TELEFONIA FISSA Patrimoniale attivo
13.09.073 TELEFONIA MOBILE Patrimoniale attivo
13.09.077 MOBILI Patrimoniale attivo
13.09.081 ARREDI Patrimoniale attivo
16.01.005 F.DO AMM.TO FABBRICATI CIVILI Patrimoniale passivo
16.07.001 F.DO AMM.TO AUTOVETTURE Patrimoniale passivo
16.07.005 F.DO AMM.TO AUTOCARRI Patrimoniale passivo
16.07.045 F.DO AMM.TO COMPUTER ED ACCESSORI Patrimoniale passivo
16.07.053 F.DO AMM.TO TELEFONIA MOBILE Patrimoniale passivo
16.07.057 F.DO AMM.TO MOBILI Patrimoniale passivo
22.01.001 PARTECIPAZIONE CONTROLLATA A Patrimoniale attivo
22.25.017 BTP Patrimoniale attivo
25.01.001 MATERIE PRIME Patrimoniale attivo
25.07.005 MERCI Patrimoniale attivo
28.01.001 CLIENTE Patrimoniale attivo
28.01.005 EFFETTI ATTIVI Patrimoniale attivo
28.01.009 EFFETTI ATTIVI ALLO SCONTO Patrimoniale attivo
28.03.001 FONDO SVALUTAZIONE CREDITI(TASSATO) Patrimoniale passivo
28.11.001 CREDITO IRES Patrimoniale attivo
28.11.005 CREDITO IRAP Patrimoniale attivo
28.11.009 CREDITO IVA Patrimoniale attivo
28.11.049 ERARIO C/RIT. SUBITE Patrimoniale attivo
34.01.001 BANCA C/C A Patrimoniale attivo
34.01.005 BANCA C/C B Patrimoniale attivo
34.05.001 CASSA CONTANTI Patrimoniale attivo
37.01.001 RATEI ATTIVI Patrimoniale attivo
37.01.005 RISCONTI ATTIVI Patrimoniale attivo
40.01.001 CAPITALE SOCIALE Patrimoniale passivo
40.07.001 RISERVA LEGALE Patrimoniale passivo
40.13.010 RISERVA CONTRIBUTI IN CONTO CAPITALE Patrimoniale passivo
40.13.033 RISERVA DA AVANZO DI FUSIONE Patrimoniale passivo
40.15.001 UTILE D'ESERCIZIO PRECEDENTI Patrimoniale passivo
40.17.001 UTILE D'ESERCIZIO Patrimoniale passivo
40.17.005 PERDITE ESERCIZIO Patrimoniale attivo
43.01.001 FONDO TRATT. QUIESC. E OBBLIGHI SIMILI Patrimoniale passivo
46.01.001 FONDO T.F.R. Patrimoniale passivo
49.05.021 SOCIO A C/FINANZIAMENTO INFRUTTIFERO Patrimoniale passivo
49.07.033 MUTUO IPOTECARIO((ENTRO ES.SUC.)) Patrimoniale passivo
49.07.037 BANCA C/FINANZIAMENTI Patrimoniale passivo
49.13.001 FORNITORE Patrimoniale passivo
49.23.001 ERARIO C/IRES Patrimoniale passivo
49.23.005 ERARIO C/IRAP Patrimoniale passivo
49.23.009 ERARIO C/IVA Patrimoniale passivo
49.23.010 ERARIO C/IVA RATEIZZATO Patrimoniale passivo
49.23.029 ERARIO C/RIT. FISCALI LAVOR. DIPENDENTI Patrimoniale passivo
49.23.033 ERARIO C/RIT. FISCALI COLLAB. A PROGETTO Patrimoniale passivo
49.23.039 ERARIO C/RIT. FISCALI LAVOR. AUTONOMI Patrimoniale passivo
49.25.001 DEBITO V./ INPS LAVORO DIPENDENTE Patrimoniale passivo
49.25.005 DEBITO V./ INAIL Patrimoniale passivo
49.25.013 DEBITO V./ ENASARCO Patrimoniale passivo
49.27.001 DEBITI V/AMMINISTRATORI Patrimoniale passivo
49.27.025 DIPENDENTI C/RETRIBUZIONI Patrimoniale passivo
49.27.045 DIPENDENTI C/FERIE DA LIQUIDARE Patrimoniale passivo
52.01.001 RATEI PASSIVI Patrimoniale passivo
52.01.005 RISCONTI PASSIVI Patrimoniale passivo
58.01.001 FIDEIUSSIONI PRESTATE A CONTROLLATE Conto d'ordine
60.01.001 RICAVI DA CESSIONI DI BENI Economico ricavi
60.01.005 RICAVI DA PRESTAZIONE DI SERVIZI Economico ricavi
60.01.009 MERCI C/VENDITE Economico ricavi
60.01.037 CANONI DI LOCAZIONE IMMOBILI Economico ricavi
71.01.001 CANONI DI LOCAZIONE FABBRICATI Economico ricavi
71.01.053 RISARCIMENTO DANNI Economico ricavi
71.01.081 CONTRIB. C/CAPITALE Economico ricavi
71.01.085 CONTRIB. C/ESERCIZIO Economico ricavi
73.01.001 MATERIE PRIME C/ACQUISTI Economico costi
73.01.013 MERCI C/ACQUISTI Economico costi
73.01.037 FABBRICATI CIVILI C/ACQUISTI Economico costi
73.09.006 CARBUR. E LUBR. Economico costi
73.09.042 CARBUR. E LUBR. NON DEDUCIBILI Economico costi
73.09.045 CANCELLERIA E STAMPATI Economico costi
73.09.077 BENI< EURO 516 Economico costi
75.01.025 ENERGIA ELETTRICA Economico costi
75.01.033 GAS RISCALDAMENTO Economico costi
75.01.041 CONSULENZE TECNICHE Economico costi
75.05.001 MANUT. FABBRICATI Economico costi
75.05.105 MANUT. AUTOVETTURE Economico costi
75.05.106 MANUT. AUTOVETTURE NON DEDUCIBILI Economico costi
75.05.145 MANUT. COMPUTER ED ACCESSORI Economico costi
75.11.002 CONSULENZE Economico costi
75.11.005 CONSULENZE LEGALI Economico costi
75.11.017 COMPENSI AMMINISTRATORE Economico costi
75.11.021 CONTR. INPS AMMINISTRATORI Economico costi
75.11.073 COMPENSI PER COLLAB. A PROGETTO Economico costi
75.11.090 COMPENSI OCCASIONALI Economico costi
75.11.113 SPESE TELEFONICHE Economico costi
75.11.117 SPESE TELEFONICHE NON DEDUCIBILI Economico costi
75.13.037 SPESE DI PUBBLICITA' Economico costi
75.17.033 VIAGGI(FERROVIA, AEREO, AUTO ECC.) Economico costi
75.17.041 SPESE DI RAPPRESENTANZA Economico costi
75.17.081 SPESE PER SERVIZI BANCARI Economico costi
77.01.009 CANONE LOCAZIONE FABBRICATI CIVILI Economico costi
77.03.105 CANONE LEASING AUTOV. Economico costi
77.05.061 CANONE NOLEGGIO AUTOV. Economico costi
79.01.005 STIPENDI IMPIEGATI Economico costi
79.01.009 STIPENDI DIRIGENTI Economico costi
79.03.001 ONERI INPS Economico costi
79.03.005 ONERI INAIL Economico costi
79.05.001 ACC.TO FONDO TFR Economico costi
81.01.009 AMM.TO SPESE DI COSTITUZIONE Economico costi
81.05.013 AMM.TO SOFTWARE SPECIFICO Economico costi
83.03.001 AMM.TO FABBRICATI CIVILI Economico costi
83.09.001 AMM.TO AUTOVETTURE Economico costi
83.09.065 AMM.TO COMPUTER ED ACCESSORI Economico costi
83.09.073 AMM.TO TELEFONIA MOBILE Economico costi
83.09.077 AMM.TO MOBILI Economico costi
83.11.105 AMM.TO INDED. AUTOVETTURE Economico costi
83.11.169 AMM.TO INDED. COMPUTER ED ACCESSORI Economico costi
83.11.177 AMM.TO INDED. TELEFONIA MOBILE Economico costi
92.01.001 IMPOSTA DI BOLLO Economico costi
92.01.005 IMU Economico costi
92.01.037 TASSE PROP. AUTOV. Economico costi
92.01.082 TASSE PROP. AUTOVEICOLO INDED. Economico costi
92.01.113 MULTE E AMMENDE Economico costi
93.15.021 INTERESSI PASS. SUI DEBITI VERSO BANCHE Economico costi
93.15.025 INTERESSI PASS. MUTUI Economico costi
96.01.001 IRES Economico costi
96.01.005 IRAP Economico costi
95.01.005 PLUSVALENZE IMMOBILIZ. MATERIALI Economico ricavi
95.03.005 MINUSV. IMMOBILIZ. MATERIALI Economico costi
"""

@st.cache_data
def parse_piano_conti(raw_text):
    """Parsa il testo grezzo e crea il dizionario dei conti"""
    piano = {}
    # Pattern migliorato per catturare "Patrimoniale attivo/passivo" o "Economico costi/ricavi"
    pattern = r'(\d{2}\.\d{2}\.\d{3})\s+(.*?)\s+(Patrimoniale\s*(?:attivo|passivo)?|Economico\s*(?:costi|ricavi)?|Conto\s*d\'ordine)\s*$'
    
    lines = raw_text.strip().split('\n')
    for line in lines:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            codice, descrizione, posizione = match.groups()
            posizione = posizione.strip()
            
            # Determina "Normale" contabile
            pos_lower = posizione.lower()
            normale = 'dare' if any(k in pos_lower for k in ['attivo', 'costi']) else 'avere'
            
            piano[codice] = {
                'desc': descrizione.strip().title(),
                'posizione': posizione,
                'normale': normale
            }
    return piano

# Inizializzazione Piano dei Conti
PIANO_CONTI = parse_piano_conti(PDF_TEXT_SOURCE)

# ==============================================================================
# 3. DEFINIZIONE OPERAZIONI (DATABASE MASSIVO)
# ==============================================================================
# Ogni operazione definisce quali conti muovere e da dove prendere l'importo
OPERAZIONI_DB = [
    # === DOCUMENTI COMMERCIALI ===
    {
        "id": "ACQUISTO_FATTURA", "nome": " Acquisto Merce/Services (Fattura)", "cat": "Acquisti",
        "tipo_input": "IVA",
        "righe": [
            {"lato": "DARE", "conto": "73.01.013", "importo_source": "imponibile", "desc": "Merci c/acquisti"},
            {"lato": "DARE", "conto": "28.11.009", "importo_source": "iva", "desc": "Credito IVA"},
            {"lato": "AVERE", "conto": "49.13.001", "importo_source": "totale", "desc": "Fornitore"}
        ]
    },
    {
        "id": "VENDITA_FATTURA", "nome": "💶 Vendita Merce/Services (Fattura)", "cat": "Vendite",
        "tipo_input": "IVA",
        "righe": [
            {"lato": "DARE", "conto": "28.01.001", "importo_source": "totale", "desc": "Cliente"},
            {"lato": "AVERE", "conto": "60.01.009", "importo_source": "imponibile", "desc": "Merci c/vendite"},
            {"lato": "AVERE", "conto": "49.23.009", "importo_source": "iva", "desc": "Erario c/IVA"}
        ]
    },
    {
        "id": "REVERSE_CHARGE", "nome": "⚡ Reverse Charge (Art. 17 c.6)", "cat": "Estero/Particolari",
        "tipo_input": "IVA",
        "righe": [
            {"lato": "DARE", "conto": "73.01.013", "importo_source": "imponibile", "desc": "Merci c/acquisti"},
            {"lato": "DARE", "conto": "28.11.009", "importo_source": "iva", "desc": "Credito IVA (Integrazione)"},
            {"lato": "AVERE", "conto": "49.13.001", "importo_source": "imponibile", "desc": "Fornitore Estero"},
            {"lato": "AVERE", "conto": "49.23.009", "importo_source": "iva", "desc": "Erario c/IVA (Autofattura)"}
        ]
    },
    {
        "id": "SPLIT_PAYMENT", "nome": "✂️ Split Payment (PA - Art. 17-ter)", "cat": "Vendite",
        "tipo_input": "IVA",
        "righe": [
            {"lato": "DARE", "conto": "28.01.001", "importo_source": "imponibile", "desc": "Cliente (Netto)"},
            {"lato": "DARE", "conto": "28.11.009", "importo_source": "iva", "desc": "Credito IVA (Scissione)"},
            {"lato": "AVERE", "conto": "60.01.009", "importo_source": "imponibile", "desc": "Merci c/vendite"},
            {"lato": "AVERE", "conto": "49.23.009", "importo_source": "iva", "desc": "Erario c/IVA"}
        ]
    },
    
    # === PAGAMENTI E INCASSI ===
    {
        "id": "PAG_FORNITORE", "nome": "💸 Pagamento Fornitore", "cat": "Liquidità",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "49.13.001", "importo_source": "importo", "desc": "Fornitore"},
            {"lato": "AVERE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"}
        ]
    },
    {
        "id": "INC_CLIENTE", "nome": "💵 Incasso Cliente", "cat": "Liquidità",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"},
            {"lato": "AVERE", "conto": "28.01.001", "importo_source": "importo", "desc": "Cliente"}
        ]
    },

    # === PERSONALE ===
    {
        "id": "COMPETENZA_STIPENDI", "nome": "👥 Competenza Stipendi (Lordo -> Netto)", "cat": "Personale",
        "tipo_input": "STIPENDI",
        "righe": [
            {"lato": "DARE", "conto": "79.01.005", "importo_source": "lordo", "desc": "Stipendi impiegati"},
            {"lato": "DARE", "conto": "79.03.001", "importo_source": "inps_azi", "desc": "Oneri INPS azienda"},
            {"lato": "AVERE", "conto": "49.27.025", "importo_source": "netto", "desc": "Dipendenti c/retribuzioni"},
            {"lato": "AVERE", "conto": "49.23.029", "importo_source": "irpef", "desc": "Erario c/ritenute"},
            {"lato": "AVERE", "conto": "49.25.001", "importo_source": "totale_inps", "desc": "Debito INPS (Dip+Azi)"}
        ]
    },
    {
        "id": "COMPENSO_AMMINISTRATORE", "nome": "🎓 Compenso Amministratore (20%)", "cat": "Personale",
        "tipo_input": "RITENUTA",
        "righe": [
            {"lato": "DARE", "conto": "75.11.017", "importo_source": "compenso", "desc": "Compensi amministratore"},
            {"lato": "AVERE", "conto": "49.27.001", "importo_source": "netto", "desc": "Debiti v/amministratori"},
            {"lato": "AVERE", "conto": "49.23.039", "importo_source": "ritenuta", "desc": "Erario c/rit. lav. aut."}
        ]
    },

    # === IMMOBILIZZAZIONI & AMMORTAMENTI ===
    {
        "id": "AMM_AUTO", "nome": " Ammortamento Auto (40% Ded.)", "cat": "Immobilizzazioni",
        "tipo_input": "AMMORTAMENTO",
        "deducibilita": 0.4,
        "conto_ded": "83.09.001", "conto_ind": "83.11.105", "conto_fondo": "16.07.001",
        "righe": [
            {"lato": "DARE", "conto": "placeholder", "importo_source": "quota_ded", "desc": "Amm.to Auto (Ded.)"},
            {"lato": "DARE", "conto": "placeholder", "importo_source": "quota_ind", "desc": "Amm.to Auto (Inded.)"},
            {"lato": "AVERE", "conto": "placeholder", "importo_source": "totale_quota", "desc": "F.do Amm.to Auto"}
        ]
    },
    {
        "id": "AMM_PC", "nome": "💻 Ammortamento Computer/Tel (80% Ded.)", "cat": "Immobilizzazioni",
        "tipo_input": "AMMORTAMENTO",
        "deducibilita": 0.8,
        "conto_ded": "83.09.065", "conto_ind": "83.11.169", "conto_fondo": "16.07.045",
        "righe": [
            {"lato": "DARE", "conto": "placeholder", "importo_source": "quota_ded", "desc": "Amm.to PC (Ded.)"},
            {"lato": "DARE", "conto": "placeholder", "importo_source": "quota_ind", "desc": "Amm.to PC (Inded.)"},
            {"lato": "AVERE", "conto": "placeholder", "importo_source": "totale_quota", "desc": "F.do Amm.to PC"}
        ]
    },
    {
        "id": "AMM_STD", "nome": "🏢 Ammortamento Standard (Fabbricati/Mobili)", "cat": "Immobilizzazioni",
        "tipo_input": "AMMORTAMENTO_STD",
        "righe": [
            {"lato": "DARE", "conto": "placeholder", "importo_source": "quota", "desc": "Costo Amm.to"},
            {"lato": "AVERE", "conto": "placeholder", "importo_source": "quota", "desc": "Fondo Amm.to"}
        ]
    },

    # === TRIBUTI E TASSE ===
    {
        "id": "LIQUIDAZIONE_IVA", "nome": "🏛️ Liquidazione IVA a Debito", "cat": "Tributi",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "49.23.009", "importo_source": "importo", "desc": "Erario c/IVA"},
            {"lato": "AVERE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"}
        ]
    },
    {
        "id": "IMU_BOLLO", "nome": " Pagamento IMU / Bolli", "cat": "Tributi",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "92.01.005", "importo_source": "importo", "desc": "IMU/Bolli"},
            {"lato": "AVERE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"}
        ]
    },

    # === PATRIMONIO E STRAORDINARI ===
    {
        "id": "COSTITUZIONE", "nome": "🏦 Costituzione Società (Versamento)", "cat": "Patrimonio",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"},
            {"lato": "AVERE", "conto": "40.01.001", "importo_source": "importo", "desc": "Capitale Sociale"}
        ]
    },
    {
        "id": "PRESTITO_SOCIO", "nome": "🤝 Finanziamento Socio (Infruttifero)", "cat": "Patrimonio",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"},
            {"lato": "AVERE", "conto": "49.05.021", "importo_source": "importo", "desc": "Socio c/finanziamento"}
        ]
    },
    {
        "id": "PLUSVALENZA", "nome": "📈 Plusvalenza Ordinaria", "cat": "Straordinari",
        "tipo_input": "SECCO",
        "righe": [
            {"lato": "DARE", "conto": "34.01.001", "importo_source": "importo", "desc": "Banca c/c"},
            {"lato": "AVERE", "conto": "95.01.005", "importo_source": "importo", "desc": "Plusvalenze Immobilizzazioni"}
        ]
    }
]

# ==============================================================================
# 4. FUNZIONI DI SUPPORTO
# ==============================================================================

def get_descrizione(codice):
    info = PIANO_CONTI.get(codice, {})
    return info.get('desc', '❌ Conto non trovato')

def get_posizione(codice):
    info = PIANO_CONTI.get(codice, {})
    return info.get('posizione', 'N/A')

def fmt_conto(codice):
    return f"{codice} - {get_descrizione(codice)}"

def calcola_scrittura(opzione, input_data):
    """Genera le righe contabili basate sui dati inseriti"""
    righe = []
    
    # Logica specifica per ammortamenti con deducibilità parziale
    if 'AMMORTAMENTO' in opzione['tipo_input'] and 'deducibilita' in opzione:
        quota = input_data.get('quota', 0)
        ded_pct = opzione['deducibilita']
        quota_ded = round(quota * ded_pct, 2)
        quota_ind = round(quota * (1 - ded_pct), 2)
        
        valori_calcolati = {
            'quota_ded': quota_ded,
            'quota_ind': quota_ind,
            'totale_quota': quota
        }
        
        for riga in opzione['righe']:
            if riga['conto'] == 'placeholder':
                # Sostituisce i placeholder con i conti reali
                if riga['lato'] == 'DARE' and 'Ded' in riga['desc']:
                    codice_reale = opzione['conto_ded']
                elif riga['lato'] == 'DARE' and 'Inded' in riga['desc']:
                    codice_reale = opzione['conto_ind']
                else:
                    codice_reale = opzione['conto_fondo']
                
                importo = valori_calcolati[riga['importo_source']]
                righe.append({
                    'lato': riga['lato'],
                    'conto': codice_reale,
                    'descrizione': get_descrizione(codice_reale),
                    'importo': importo
                })
        return righe

    # Logica standard per tutte le altre
    elif opzione['tipo_input'] == 'IVA':
        imp = input_data.get('imponibile', 0)
        iva = round(imp * input_data.get('aliquota', 22) / 100, 2)
        tot = imp + iva
        mapping = {'imponibile': imp, 'iva': iva, 'totale': tot}
        
    elif opzione['tipo_input'] == 'STIPENDI':
        lordo = input_data.get('lordo', 0)
        inps_dip = round(lordo * 0.0919, 2)
        irpef = input_data.get('irpef', 0)
        netto = round(lordo - inps_dip - irpef, 2)
        inps_azi = round(lordo * 0.28, 2) # Stima media
        
        mapping = {
            'lordo': lordo,
            'inps_azi': inps_azi,
            'netto': netto,
            'irpef': irpef,
            'totale_inps': round(inps_dip + inps_azi, 2)
        }
        
    elif opzione['tipo_input'] == 'RITENUTA':
        comp = input_data.get('compenso', 0)
        ritenuta = round(comp * 0.20, 2)
        netto = comp - ritenuta
        mapping = {'compenso': comp, 'netto': netto, 'ritenuta': ritenuta}
        
    elif opzione['tipo_input'] == 'AMMORTAMENTO_STD':
        quota = input_data.get('quota', 0)
        mapping = {'quota': quota}
        # Qui l'utente deve selezionare i conti manualmente
        for riga in opzione['righe']:
            if riga['conto'] == 'placeholder':
                codice_reale = input_data.get(f'sel_{riga["lato"]}', '')
                importo = mapping[riga['importo_source']]
                righe.append({
                    'lato': riga['lato'],
                    'conto': codice_reale,
                    'descrizione': get_descrizione(codice_reale),
                    'importo': importo
                })
        return righe

    else: # SECCO
        imp = input_data.get('importo', 0)
        mapping = {'importo': imp}

    # Generazione righe per operazioni standard
    for riga in opzione['righe']:
        importo = mapping.get(riga['importo_source'], 0)
        if importo > 0:
            righe.append({
                'lato': riga['lato'],
                'conto': riga['conto'],
                'descrizione': get_descrizione(riga['conto']),
                'importo': round(importo, 2)
            })
            
    return righe

# ==============================================================================
# 5. INTERFACCIA UTENTE
# ==============================================================================

def main():
    st.title("📒 Generatore Scritture Contabili SRL")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Piano dei Conti Caricato")
        st.success(f"✅ {len(PIANO_CONTI)} conti estratti")
        
        # Search
        q = st.text_input("🔍 Cerca conto...", placeholder="Es. banca, iva, auto")
        if q:
            risultati = [c for c, info in PIANO_CONTI.items() if q.lower() in info['desc'].lower()]
            for c in risultati[:10]:
                st.write(f"`{c}` - {PIANO_CONTI[c]['desc']}")

    # Main Content
    st.subheader("1. Seleziona Operazione")
    
    # Raggruppa per categoria
    categorie = sorted(list({op['cat'] for op in OPERAZIONI_DB}))
    cat_sel = st.selectbox("Categoria", categorie)
    
    ops = [op for op in OPERAZIONI_DB if op['cat'] == cat_sel]
    op_sel = st.selectbox("Operazione", ops, format_func=lambda x: x['nome'])
    
    if op_sel:
        st.divider()
        st.subheader("2. Inserisci Dati")
        
        input_data = {}
        tipo = op_sel['tipo_input']
        
        # Generazione Input Dinamici
        if tipo == "IVA":
            col1, col2 = st.columns(2)
            input_data['imponibile'] = col1.number_input("Imponibile €", min_value=0.0, step=0.01)
            input_data['aliquota'] = col2.selectbox("Aliquota IVA %", [4, 10, 22], index=2)
            
        elif tipo == "STIPENDI":
            col1, col2 = st.columns(2)
            input_data['lordo'] = col1.number_input("Retribuzione Lorda €", min_value=0.0, step=0.01)
            input_data['irpef'] = col2.number_input("IRPEF Stimata €", min_value=0.0, step=0.01)
            st.info("Oneri Azienda stimati al 28%")
            
        elif tipo == "RITENUTA":
            input_data['compenso'] = st.number_input("Compenso Lordo €", min_value=0.0, step=0.01)
            st.info("Ritenuta applicata: 20%")
            
        elif tipo == "AMMORTAMENTO":
            input_data['quota'] = st.number_input("Quota Annuale Totale €", min_value=0.0, step=0.01)
            ded = op_sel['deducibilita'] * 100
            st.info(f"Deducibilità automatica: {int(ded)}% (Il sistema scriverà automaticamente sui conti Deducibili e Indeducibili)")
            
        elif tipo == "AMMORTAMENTO_STD":
            col1, col2, col3 = st.columns([1, 2, 2])
            input_data['quota'] = col1.number_input("Quota €", min_value=0.0, step=0.01)
            # Selectboxes per conti custom
            lista_conti = sorted(PIANO_CONTI.keys())
            input_data['sel_DARE'] = col2.selectbox("Conto DARE (Amm.to)", lista_conti, format_func=fmt_conto)
            input_data['sel_AVERE'] = col3.selectbox("Conto AVERE (Fondo)", lista_conti, format_func=fmt_conto)
            
        else: # SECCO
            input_data['importo'] = st.number_input("Importo €", min_value=0.0, step=0.01)
            
        st.divider()
        
        # Genera Scrittura
        if st.button("🚀 Genera Scrittura Contabile", type="primary", use_container_width=True):
            righe = calcola_scrittura(op_sel, input_data)
            
            if not righe:
                st.warning("⚠️ Inserisci un importo maggiore di zero")
            else:
                # Validazione
                tot_dare = sum(r['importo'] for r in righe if r['lato'] == 'DARE')
                tot_avere = sum(r['importo'] for r in righe if r['lato'] == 'AVERE')
                
                col1, col2 = st.columns(2)
                
                # Tabella DARE
                df_dare = pd.DataFrame([r for r in righe if r['lato'] == 'DARE'])
                with col1:
                    st.write("🔴 **DARE**")
                    if not df_dare.empty:
                        # Aggiungi colonna formattata
                        df_dare['Dettagli'] = df_dare['conto'] + " - " + df_dare['descrizione']
                        st.dataframe(df_dare[['Dettagli', 'importo']].rename(columns={'importo': '€'}), hide_index=True)
                    st.metric("Totale Dare", f"€ {tot_dare:,.2f}")
                
                # Tabella AVERE
                df_avere = pd.DataFrame([r for r in righe if r['lato'] == 'AVERE'])
                with col2:
                    st.write("🟢 **AVERE**")
                    if not df_avere.empty:
                        df_avere['Dettagli'] = df_avere['conto'] + " - " + df_avere['descrizione']
                        st.dataframe(df_avere[['Dettagli', 'importo']].rename(columns={'importo': '€'}), hide_index=True)
                    st.metric("Totale Avere", f"€ {tot_avere:,.2f}")
                
                # Feedback Finale
                if abs(tot_dare - tot_avere) < 0.01:
                    st.success("✅ Scrittura BILANCIATA (DARE = AVERE)")
                    
                    # Export
                    csv = pd.DataFrame(righe).to_csv(index=False, sep=';', decimal=',')
                    st.download_button(
                        label="📥 Scarica CSV",
                        data=csv,
                        file_name=f"scrittura_{op_sel['id']}_{datetime.now().strftime('%d%m')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"❌ NON BILANCIATA! Differenza: € {abs(tot_dare - tot_avere):,.2f}")

if __name__ == "__main__":
    main()
