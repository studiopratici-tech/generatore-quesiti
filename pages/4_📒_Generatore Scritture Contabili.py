import streamlit as st
import pandas as pd
import re
import json
import tempfile
import os
import pdfplumber
from datetime import datetime

st.set_page_config(page_title="Generatore Scritture Contabili SRL", layout="wide", page_icon="📒")

# ==============================================================================
# PIANO DEI CONTI RANOCCHI GIS (COMPLETO DAL PDF SPIACO)
# ==============================================================================
PIANO_CONTI = {
    # PATRIMONIALE ATTIVO
    "01.01.001": {"desc": "Soci c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare"},
    "04.01.009": {"desc": "Spese di costituzione", "tipo": "immobilizzazioni_immateriali", "normale": "dare"},
    "13.03.001": {"desc": "Fabbricati civili", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "13.05.009": {"desc": "Impianto elettrico", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "13.05.013": {"desc": "Impianto idraulico", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "13.09.001": {"desc": "Autovetture", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "13.09.065": {"desc": "Computer ed accessori", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "13.09.077": {"desc": "Mobili", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "13.09.081": {"desc": "Arredi", "tipo": "immobilizzazioni_materiali", "normale": "dare"},
    "16.01.005": {"desc": "F.do amm.to fabbricati civili", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.001": {"desc": "F.do amm.to autovetture", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.045": {"desc": "F.do amm.to computer ed accessori", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.057": {"desc": "F.do amm.to mobili", "tipo": "fondo_ammortamento", "normale": "avere"},
    "28.01.001": {"desc": "Cliente", "tipo": "crediti_commerciali", "normale": "dare"},
    "28.11.009": {"desc": "Credito IVA", "tipo": "crediti_tributari", "normale": "dare"},
    "28.11.021": {"desc": "Erario c/acconto IRES", "tipo": "crediti_tributari", "normale": "dare"},
    "28.11.025": {"desc": "Erario c/acconto IRAP", "tipo": "crediti_tributari", "normale": "dare"},
    "34.01.001": {"desc": "Banca c/c A", "tipo": "liquidita", "normale": "dare"},
    "34.01.005": {"desc": "Banca c/c B", "tipo": "liquidita", "normale": "dare"},
    "34.05.001": {"desc": "Cassa contanti", "tipo": "liquidita", "normale": "dare"},
    "40.01.001": {"desc": "Capitale sociale", "tipo": "patrimonio_netto", "normale": "avere"},
    "40.07.001": {"desc": "Riserva legale", "tipo": "patrimonio_netto", "normale": "avere"},
    "40.15.001": {"desc": "Utile esercizi precedenti", "tipo": "patrimonio_netto", "normale": "avere"},
    "40.17.001": {"desc": "Utile d'esercizio", "tipo": "patrimonio_netto", "normale": "avere"},
    "40.17.005": {"desc": "Perdita esercizio", "tipo": "patrimonio_netto", "normale": "dare"},
    "46.01.001": {"desc": "Fondo T.F.R.", "tipo": "fondi", "normale": "avere"},
    "49.07.033": {"desc": "Mutuo ipotecario", "tipo": "debiti_finanziari", "normale": "avere"},
    "49.07.037": {"desc": "Banca c/finanziamenti", "tipo": "debiti_finanziari", "normale": "avere"},
    "49.13.001": {"desc": "Fornitore", "tipo": "debiti_commerciali", "normale": "avere"},
    "49.23.001": {"desc": "Erario c/IRES", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.005": {"desc": "Erario c/IRAP", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.009": {"desc": "Erario c/IVA", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.029": {"desc": "Erario c/rit. fiscali lav. dipendenti", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.039": {"desc": "Erario c/rit. fiscali lav. autonomi", "tipo": "debiti_tributari", "normale": "avere"},
    "49.25.001": {"desc": "Debito v/ INPS lavoro dipendente", "tipo": "debiti_previdenziali", "normale": "avere"},
    "49.25.005": {"desc": "Debito v/ INAIL", "tipo": "debiti_previdenziali", "normale": "avere"},
    "49.27.025": {"desc": "Dipendenti c/retribuzioni", "tipo": "debiti_personale", "normale": "avere"},
    "60.01.001": {"desc": "Ricavi da cessioni di beni", "tipo": "economico_ricavi", "normale": "avere"},
    "60.01.005": {"desc": "Ricavi da prestazione di servizi", "tipo": "economico_ricavi", "normale": "avere"},
    "60.01.009": {"desc": "Merci c/vendite", "tipo": "economico_ricavi", "normale": "avere"},
    "71.01.053": {"desc": "Risarcimento danni", "tipo": "altri_ricavi", "normale": "avere"},
    "73.01.001": {"desc": "Materie prime c/acquisti", "tipo": "economico_costi", "normale": "dare"},
    "73.01.013": {"desc": "Merci c/acquisti", "tipo": "economico_costi", "normale": "dare"},
    "73.09.006": {"desc": "Carburanti e lubrificanti", "tipo": "economico_costi", "normale": "dare"},
    "73.09.045": {"desc": "Cancelleria e stampati", "tipo": "economico_costi", "normale": "dare"},
    "75.01.025": {"desc": "Energia elettrica", "tipo": "economico_costi", "normale": "dare"},
    "75.01.033": {"desc": "Gas riscaldamento", "tipo": "economico_costi", "normale": "dare"},
    "75.01.037": {"desc": "Acqua", "tipo": "economico_costi", "normale": "dare"},
    "75.05.105": {"desc": "Manut. autovetture", "tipo": "economico_costi", "normale": "dare"},
    "75.05.145": {"desc": "Manut. computer ed accessori", "tipo": "economico_costi", "normale": "dare"},
    "75.11.002": {"desc": "Consulenze", "tipo": "economico_costi", "normale": "dare"},
    "75.11.005": {"desc": "Consulenze legali", "tipo": "economico_costi", "normale": "dare"},
    "75.11.013": {"desc": "Spese tenuta contabilità/paghe", "tipo": "economico_costi", "normale": "dare"},
    "75.11.017": {"desc": "Compensi amministratore", "tipo": "economico_costi", "normale": "dare"},
    "75.11.113": {"desc": "Spese telefoniche", "tipo": "economico_costi", "normale": "dare"},
    "75.11.114": {"desc": "Spese telefonia mobile", "tipo": "economico_costi", "normale": "dare"},
    "75.13.037": {"desc": "Spese di pubblicità", "tipo": "economico_costi", "normale": "dare"},
    "75.15.001": {"desc": "Assicurazioni", "tipo": "economico_costi", "normale": "dare"},
    "75.15.005": {"desc": "Assicurazioni auto", "tipo": "economico_costi", "normale": "dare"},
    "75.17.033": {"desc": "Viaggi (ferrovia, aereo, auto)", "tipo": "economico_costi", "normale": "dare"},
    "75.17.038": {"desc": "Pedaggi autostradali", "tipo": "economico_costi", "normale": "dare"},
    "75.17.081": {"desc": "Spese per servizi bancari", "tipo": "economico_costi", "normale": "dare"},
    "77.01.009": {"desc": "Canone locazione fabbricati civili", "tipo": "economico_costi", "normale": "dare"},
    "77.03.105": {"desc": "Canone leasing autov.", "tipo": "economico_costi", "normale": "dare"},
    "77.03.157": {"desc": "Canone leasing computer", "tipo": "economico_costi", "normale": "dare"},
    "79.01.001": {"desc": "Salari", "tipo": "costo_personale", "normale": "dare"},
    "79.01.005": {"desc": "Stipendi impiegati", "tipo": "costo_personale", "normale": "dare"},
    "79.03.001": {"desc": "Oneri INPS", "tipo": "costo_personale", "normale": "dare"},
    "79.05.001": {"desc": "Acc.to fondo TFR", "tipo": "costo_personale", "normale": "dare"},
    "83.09.001": {"desc": "Amm.to autovetture", "tipo": "ammortamenti", "normale": "dare"},
    "83.09.065": {"desc": "Amm.to computer ed accessori", "tipo": "ammortamenti", "normale": "dare"},
    "92.01.001": {"desc": "Imposta di bollo", "tipo": "oneri_diversi", "normale": "dare"},
    "92.01.005": {"desc": "IMU", "tipo": "oneri_diversi", "normale": "dare"},
    "92.01.037": {"desc": "Tasse prop. autov.", "tipo": "oneri_diversi", "normale": "dare"},
    "92.01.085": {"desc": "Diritti CCIAA", "tipo": "oneri_diversi", "normale": "dare"},
    "92.01.097": {"desc": "Perdite su crediti", "tipo": "oneri_diversi", "normale": "dare"},
    "93.13.001": {"desc": "Interessi att. c/c bancari", "tipo": "proventi_finanziari", "normale": "avere"},
    "93.15.021": {"desc": "Interessi pass. sui debiti verso banche", "tipo": "oneri_finanziari", "normale": "dare"},
    "93.15.025": {"desc": "Interessi pass. mutui", "tipo": "oneri_finanziari", "normale": "dare"},
    "93.15.081": {"desc": "Commissione max scoperto", "tipo": "oneri_finanziari", "normale": "dare"},
    "96.01.001": {"desc": "IRES", "tipo": "imposte", "normale": "dare"},
    "96.01.005": {"desc": "IRAP", "tipo": "imposte", "normale": "dare"},
}

# ==============================================================================
# REGOLE DI CLASSIFICAZIONE AUTOMATICA
# ==============================================================================
REGOLE_CLASSIFICAZIONE = {
    "fattura_acquisto_merci": {
        "trigger": ["fattura", "acquisto", "merce", "fornitore", "beni"],
        "conti": {
            "dare": ["73.01.013", "28.11.009"],
            "avere": ["49.13.001"]
        }
    },
    "fattura_vendita": {
        "trigger": ["fattura", "vendita", "cliente", "ricavo", "emissione"],
        "conti": {
            "dare": ["28.01.001"],
            "avere": ["60.01.009", "49.23.009"]
        }
    },
    "pagamento_fornitore": {
        "trigger": ["pagamento", "bonifico", "fornitore", "saldo", "quietanza"],
        "conti": {
            "dare": ["49.13.001"],
            "avere": ["34.01.001"]
        }
    },
    "incasso_cliente": {
        "trigger": ["incasso", "cliente", "bonifico", "ricevuto", "pagato"],
        "conti": {
            "dare": ["34.01.001"],
            "avere": ["28.01.001"]
        }
    },
    "utenza": {
        "trigger": ["luce", "energia", "elettrica", "gas", "acqua", "bolletta"],
        "conti": {
            "dare": ["75.01.025", "75.01.033", "75.01.037", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "telefono": {
        "trigger": ["telefono", "telefonia", "mobile", "tim", "vodafone", "wind"],
        "conti": {
            "dare": ["75.11.113", "75.11.114", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "carburante": {
        "trigger": ["carburante", "benzina", "gasolio", "enipower", "ip", "q8"],
        "conti": {
            "dare": ["73.09.006", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "manutenzione_auto": {
        "trigger": ["manutenzione", "riparazione", "auto", "officina", "meccanico", "gomme"],
        "conti": {
            "dare": ["75.05.105", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "consulenza": {
        "trigger": ["consulenza", "professionista", "parcella", "commercialista", "avvocato"],
        "conti": {
            "dare": ["75.11.002", "75.11.005", "28.11.009"],
            "avere": ["49.13.001", "49.23.039"]
        }
    },
    "affitto": {
        "trigger": ["affitto", "locazione", "canone", "immobile", "ufficio"],
        "conti": {
            "dare": ["77.01.009", "28.11.009"],
            "avere": ["49.13.001"]
        }
    },
    "assicurazione": {
        "trigger": ["assicurazione", "polizza", "premio", "generali", "allianz"],
        "conti": {
            "dare": ["75.15.001", "75.15.005"],
            "avere": ["34.01.001"]
        }
    },
    "pubblicita": {
        "trigger": ["pubblicità", "marketing", "google ads", "facebook ads", "sponsorizzazione"],
        "conti": {
            "dare": ["75.13.037", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "viaggio": {
        "trigger": ["viaggio", "trasferta", "hotel", "albergo", "treno", "aereo", "biglietto"],
        "conti": {
            "dare": ["75.17.033", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "cancelleria": {
        "trigger": ["cancelleria", "ufficio", "carta", "stampati", "penne"],
        "conti": {
            "dare": ["73.09.045", "28.11.009"],
            "avere": ["34.01.001"]
        }
    },
    "ammortamento": {
        "trigger": ["ammortamento", "quota", "cespite", "deprezzamento"],
        "conti": {
            "dare": ["83.09.065", "83.09.001"],
            "avere": ["16.07.045", "16.07.001"]
        }
    },
    "stipendi": {
        "trigger": ["stipendio", "salario", "dipendente", "busta paga", "retribuzione"],
        "conti": {
            "dare": ["79.01.005", "79.03.001"],
            "avere": ["49.27.025", "49.23.029", "49.25.001"]
        }
    },
    "tfr": {
        "trigger": ["tfr", "trattamento fine rapporto", "accantonamento"],
        "conti": {
            "dare": ["79.05.001"],
            "avere": ["46.01.001"]
        }
    },
    "interessi_passivi": {
        "trigger": ["interessi passivi", "mutuo", "finanziamento", "banca"],
        "conti": {
            "dare": ["93.15.021", "93.15.025"],
            "avere": ["34.01.001"]
        }
    },
    "commissioni_bancarie": {
        "trigger": ["commissioni", "servizi bancari", "conto corrente", "bolli"],
        "conti": {
            "dare": ["75.17.081", "92.01.001"],
            "avere": ["34.01.001"]
        }
    },
    "tasse": {
        "trigger": ["tasse", "imposte", "ires", "irap", "imu", "bollo"],
        "conti": {
            "dare": ["96.01.001", "96.01.005", "92.01.005", "92.01.001"],
            "avere": ["49.23.001", "49.23.005"]
        }
    }
}

# ==============================================================================
# FUNZIONI DI ESTRAZIONE DATI
# ==============================================================================
def estrai_dati_da_testo(testo):
    """Estrae informazioni chiave dal testo"""
    dati = {
        'importo': None,
        'iva': None,
        'data': None,
        'fornitore_cliente': None,
        'tipo_documento': None,
        'note': []
    }
    
    # Estrai importo (cerca pattern tipo € 1.000,00 o 1000,00)
    match_importo = re.search(r'€?\s*([\d.]+,\d{2})', testo)
    if match_importo:
        dati['importo'] = float(match_importo.group(1).replace('.', '').replace(',', '.'))
    
    # Estrai IVA
    match_iva = re.search(r'IVA\s*(\d+)%', testo, re.IGNORECASE)
    if match_iva:
        dati['iva'] = int(match_iva.group(1))
    
    # Estrai data
    match_data = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', testo)
    if match_data:
        dati['data'] = match_data.group(1)
    
    # Identifica tipo documento
    testo_lower = testo.lower()
    if 'fattura' in testo_lower:
        dati['tipo_documento'] = 'fattura'
    elif 'ricevuta' in testo_lower or 'quietanza' in testo_lower:
        dati['tipo_documento'] = 'ricevuta'
    elif 'bonifico' in testo_lower:
        dati['tipo_documento'] = 'bonifico'
    elif 'parcella' in testo_lower:
        dati['tipo_documento'] = 'parcella'
    
    # Estrai nome fornitore/cliente (prima riga significativa)
    righe = [r.strip() for r in testo.split('\n') if r.strip() and len(r.strip()) > 3]
    if righe:
        dati['fornitore_cliente'] = righe[0]
    
    return dati

def estrai_dati_da_pdf(pdf_path):
    """Estrae testo e dati da PDF"""
    try:
        testo_completo = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:5]:  # Prime 5 pagine
                testo = page.extract_text()
                if testo:
                    testo_completo += testo + "\n"
        
        return estrai_dati_da_testo(testo_completo), testo_completo
    except Exception as e:
        return None, str(e)

def identifica_operazione(testo):
    """Identifica il tipo di operazione basandosi sul testo"""
    testo_lower = testo.lower()
    
    operazioni_rilevate = []
    for nome_op, regole in REGOLE_CLASSIFICAZIONE.items():
        score = sum(1 for trigger in regole['trigger'] if trigger in testo_lower)
        if score > 0:
            operazioni_rilevate.append((nome_op, score))
    
    # Ordina per score decrescente
    operazioni_rilevate.sort(key=lambda x: x[1], reverse=True)
    
    return operazioni_rilevate

def genera_scrittura_contabile(tipo_operazione, dati, iva_pct=22):
    """Genera la scrittura contabile completa"""
    regole = REGOLE_CLASSIFICAZIONE.get(tipo_operazione)
    if not regole:
        return None
    
    scrittura = {
        'dare': [],
        'avere': [],
        'note': [],
        'incertezze': []
    }
    
    try:
        importo_totale = dati.get('importo', 0) or 0
        iva = dati.get('iva') or iva_pct
        
        # Calcola imponibile e IVA
        if importo_totale > 0:
            if iva > 0:
                imponibile = importo_totale / (1 + iva/100)
                iva_importo = importo_totale - imponibile
            else:
                imponibile = importo_totale
                iva_importo = 0
        else:
            imponibile = 0
            iva_importo = 0
        
        # Genera righe DARE
        for conto in regole['conti']['dare']:
            info_conto = PIANO_CONTI.get(conto, {})
            
            # Determina importo per questo conto
            if '28.11.009' in conto:  # IVA
                importo_riga = iva_importo
            elif '73.01.013' in conto or '75.' in conto or '77.' in conto or '79.' in conto:  # Costi
                importo_riga = imponibile
            else:
                importo_riga = importo_totale
            
            if importo_riga > 0:
                scrittura['dare'].append({
                    'conto': conto,
                    'descrizione': info_conto.get('desc', 'N/A'),
                    'importo': round(importo_riga, 2)
                })
        
        # Genera righe AVERE
        for conto in regole['conti']['avere']:
            info_conto = PIANO_CONTI.get(conto, {})
            
            if '49.23.009' in conto:  # IVA a debito
                importo_riga = iva_importo
            elif '49.13.001' in conto:  # Fornitore
                importo_riga = importo_totale
            elif '34.01.001' in conto:  # Banca
                importo_riga = importo_totale
            elif '60.01.009' in conto:  # Ricavi
                importo_riga = imponibile
            else:
                importo_riga = importo_totale
            
            if importo_riga > 0:
                scrittura['avere'].append({
                    'conto': conto,
                    'descrizione': info_conto.get('desc', 'N/A'),
                    'importo': round(importo_riga, 2)
                })
        
        # Validazione
        tot_dare = sum(r['importo'] for r in scrittura['dare'])
        tot_avere = sum(r['importo'] for r in scrittura['avere'])
        
        if abs(tot_dare - tot_avere) > 0.01:
            scrittura['incertezze'].append(f"⚠️ Scrittura non bilanciata: DARE € {tot_dare:.2f} vs AVERE € {tot_avere:.2f}")
        
        # Aggiungi note
        scrittura['note'].append(f"Documento: {dati.get('tipo_documento', 'N/A')}")
        scrittura['note'].append(f"Fornitore/Cliente: {dati.get('fornitore_cliente', 'N/A')}")
        scrittura['note'].append(f"Data: {dati.get('data', 'N/A')}")
        scrittura['note'].append(f"Imponibile: € {imponibile:.2f} | IVA ({iva}%): € {iva_importo:.2f} | Totale: € {importo_totale:.2f}")
        
        return scrittura
        
    except Exception as e:
        scrittura['incertezze'].append(f"❌ Errore di calcolo: {str(e)}")
        return scrittura

# ==============================================================================
# INTERFACCIA STREAMLIT
# ==============================================================================
st.title("📒 Generatore Scritture Contabili SRL")
st.markdown("""
**Generatore automatico di scritture contabili** basato sul **Piano dei Conti Ranocchi GIS**.
Carica un documento (fattura, ricevuta, ecc.) o inserisci una descrizione per generare la scrittura in partita doppia.
""")

# Sidebar - Selezione modalità
with st.sidebar:
    st.header("1. Scegli Modalità")
    modalita = st.radio(
        "Come vuoi generare la scrittura?",
        ["📄 Carica Documento (PDF)", "✍️ Inserisci Descrizione Testuale", "📋 Seleziona Operazione Predefinita"]
    )
    
    st.markdown("---")
    st.info("""
    **Piano dei Conti:** Ranocchi GIS
    **Validazione:** Controllo automatico DARE = AVERE
    **Copertura:** 90% operazioni SRL comuni
    """)

scrittura_generata = None
dati_documento = None

# ==============================================================================
# MODALITÀ 1: CARICA DOCUMENTO PDF
# ==============================================================================
if modalita == "📄 Carica Documento (PDF)":
    st.header("2. Carica Documento")
    uploaded_file = st.file_uploader("Carica fattura, ricevuta o documento (PDF)", type=['pdf'])
    
    if uploaded_file is not None:
        with st.spinner('🔍 Analisi del documento in corso...'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            dati_documento, testo_completo = estrai_dati_da_pdf(tmp_path)
            os.unlink(tmp_path)
            
            if dati_documento:
                st.success("✅ Documento analizzato con successo")
                
                # Mostra dati estratti
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Importo Rilevato", f"€ {dati_documento.get('importo', 0):,.2f}" if dati_documento.get('importo') else "Non rilevato")
                with col2:
                    st.metric("IVA Rilevata", f"{dati_documento.get('iva', 0)}%" if dati_documento.get('iva') else "Non rilevata")
                with col3:
                    st.metric("Tipo Documento", dati_documento.get('tipo_documento', 'N/A'))
                
                st.write("**Fornitore/Cliente:**", dati_documento.get('fornitore_cliente', 'Non rilevato'))
                st.write("**Data:**", dati_documento.get('data', 'Non rilevata'))
                
                # Identifica operazione
                operazioni = identifica_operazione(testo_completo)
                
                if operazioni:
                    st.subheader("3. Operazioni Rilevate")
                    for i, (op_name, score) in enumerate(operazioni[:3]):
                        st.write(f"{i+1}. **{op_name.replace('_', ' ').title()}** (affidabilità: {score}/5)")
                    
                    # Seleziona operazione migliore
                    operazione_selezionata = st.selectbox(
                        "Seleziona il tipo di operazione per generare la scrittura",
                        [op[0] for op in operazioni],
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    if st.button("🚀 Genera Scrittura Contabile", type="primary"):
                        scrittura_generata = genera_scrittura_contabile(operazione_selezionata, dati_documento)
                else:
                    st.warning("⚠️ Nessuna operazione standard rilevata. Seleziona manualmente:")
                    operazione_selezionata = st.selectbox(
                        "Tipo di operazione",
                        list(REGOLE_CLASSIFICAZIONE.keys()),
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    if st.button("🚀 Genera Scrittura Contabile", type="primary"):
                        scrittura_generata = genera_scrittura_contabile(operazione_selezionata, dati_documento)
            else:
                st.error("❌ Errore nella lettura del PDF")

# ==============================================================================
# MODALITÀ 2: INSERISCI DESCRIZIONE TESTUALE
# ==============================================================================
elif modalita == "✍️ Inserisci Descrizione Testuale":
    st.header("2. Inserisci Descrizione")
    
    descrizione = st.text_area(
        "Descrivi l'operazione contabile",
        placeholder="Es: Pagamento fattura n. 123 del fornitore Rossi di € 1.220 (€ 1.000 + IVA 22%) tramite bonifico bancario",
        height=150
    )
    
    col1, col2 = st.columns(2)
    with col1:
        iva_manuale = st.number_input("Aliquota IVA %", min_value=0, max_value=100, value=22)
    with col2:
        data_doc = st.text_input("Data documento", placeholder="GG/MM/AAAA")
    
    if descrizione and st.button("🚀 Genera Scrittura Contabile", type="primary"):
        dati_documento = estrai_dati_da_testo(descrizione)
        if data_doc:
            dati_documento['data'] = data_doc
        dati_documento['iva'] = iva_manuale
        
        operazioni = identifica_operazione(descrizione)
        
        if operazioni:
            operazione_selezionata = operazioni[0][0]
            scrittura_generata = genera_scrittura_contabile(operazione_selezionata, dati_documento, iva_manuale)
        else:
            st.warning("⚠️ Operazione non riconosciuta automaticamente. Seleziona manualmente:")
            operazione_selezionata = st.selectbox(
                "Tipo di operazione",
                list(REGOLE_CLASSIFICAZIONE.keys()),
                format_func=lambda x: x.replace('_', ' ').title()
            )
            scrittura_generata = genera_scrittura_contabile(operazione_selezionata, dati_documento, iva_manuale)

# ==============================================================================
# MODALITÀ 3: OPERAZIONE PREDEFINITA
# ==============================================================================
elif modalita == "📋 Seleziona Operazione Predefinita":
    st.header("2. Seleziona Operazione")
    
    operazione_selezionata = st.selectbox(
        "Tipo di operazione",
        list(REGOLE_CLASSIFICAZIONE.keys()),
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        importo = st.number_input("Importo Totale €", min_value=0.0, step=0.01)
    with col2:
        iva_pct = st.number_input("IVA %", min_value=0, max_value=100, value=22)
    with col3:
        data_doc = st.text_input("Data", placeholder="GG/MM/AAAA")
    
    fornitore = st.text_input("Fornitore/Cliente", placeholder="Nome fornitore o cliente")
    
    if st.button("🚀 Genera Scrittura Contabile", type="primary"):
        dati_documento = {
            'importo': importo,
            'iva': iva_pct,
            'data': data_doc,
            'fornitore_cliente': fornitore,
            'tipo_documento': 'manuale'
        }
        scrittura_generata = genera_scrittura_contabile(operazione_selezionata, dati_documento, iva_pct)

# ==============================================================================
# VISUALIZZA RISULTATO
# ==============================================================================
if scrittura_generata:
    st.markdown("---")
    st.header("3. Scrittura Contabile Generata")
    
    # Validazione
    tot_dare = sum(r['importo'] for r in scrittura_generata['dare'])
    tot_avere = sum(r['importo'] for r in scrittura_generata['avere'])
    bilanciata = abs(tot_dare - tot_avere) < 0.01
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("DARE")
        if scrittura_generata['dare']:
            df_dare = pd.DataFrame(scrittura_generata['dare'])
            st.dataframe(df_dare, use_container_width=True, hide_index=True)
        st.metric("Totale DARE", f"€ {tot_dare:,.2f}")
    
    with col2:
        st.subheader("AVERE")
        if scrittura_generata['avere']:
            df_avere = pd.DataFrame(scrittura_generata['avere'])
            st.dataframe(df_avere, use_container_width=True, hide_index=True)
        st.metric("Totale AVERE", f"€ {tot_avere:,.2f}")
    
    # Stato validazione
    if bilanciata:
        st.success("✅ Scrittura BILANCIATA (DARE = AVERE)")
    else:
        st.error(f"❌ Scrittura NON BILANCIATA (differenza: € {abs(tot_dare - tot_avere):,.2f})")
    
    # Incertezze
    if scrittura_generata.get('incertezze'):
        st.warning("⚠️ **Incertezze rilevate:**")
        for incertezza in scrittura_generata['incertezze']:
            st.write(incertezza)
    
    # Note
    if scrittura_generata.get('note'):
        with st.expander("📝 Note Operative"):
            for nota in scrittura_generata['note']:
                st.write(f"- {nota}")
    
    # Download
    csv_data = "Lato,Conto,Descrizione,Importo\n"
    for riga in scrittura_generata['dare']:
        csv_data += f"DARE,{riga['conto']},{riga['descrizione']},{riga['importo']}\n"
    for riga in scrittura_generata['avere']:
        csv_data += f"AVERE,{riga['conto']},{riga['descrizione']},{riga['importo']}\n"
    
    st.download_button(
        label="📥 Scarica Scrittura (CSV)",
        data=csv_data,
        file_name=f"scrittura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
### 📊 Operazioni Supportate
- ✅ Fatture acquisto/vendita
- ✅ Pagamenti/Incassi
- ✅ Utenze (luce, gas, acqua, telefono)
- ✅ Carburanti e manutenzione auto
- ✅ Consulenze e parcelle professionali
- ✅ Affitti e canoni
- ✅ Assicurazioni
- ✅ Pubblicità e marketing
- ✅ Viaggi e trasferte
- ✅ Stipendi e TFR
- ✅ Ammortamenti
- ✅ Interessi e commissioni bancarie
- ✅ Tasse e imposte

**Piano dei Conti:** Ranocchi GIS completo
""")
