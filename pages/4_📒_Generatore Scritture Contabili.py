import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Tuple

st.set_page_config(layout="wide", page_title="Generatore Scritture Contabili | Ranocchi GIS")

# ==============================================================================
# 1. PARSER PDF RANOCCHI GIS (ROBUSTO)
# ==============================================================================
@st.cache_data
def parse_piano_ranocchi(pdf_file):
    piano = {}
    with pdfplumber.open(pdf_file) as pdf:
        testo = "\n".join(page.extract_text() or "" for page in pdf.pages)
        testo_pulito = re.sub(r'\s+', ' ', testo)
        
        pattern = r'(\d{2}\.\d{2}\.\d{3})\s+(.*?)\s+(Patrimoniale|Economico|Conto\s+d\'ordine)(?:\s+(attivo|passivo|costi|ricavi))?'
        for m in re.finditer(pattern, testo_pulito, re.IGNORECASE):
            cod, desc, macro, det = m.groups()
            pos = f"{macro} {det or ''}".strip()
            piano[cod] = {
                'desc': desc.strip().title(),
                'posizione': pos,
                'normale': 'dare' if any(k in pos.lower() for k in ['attivo', 'costi']) else 'avere'
            }
    return piano

# ==============================================================================
# 2. CONFIGURAZIONE INPUT & CALCOLI
# ==============================================================================
INPUT_CONFIG = {
    "FATTURA_IVA": {
        "label": "🧾 Fattura con IVA",
        "campi": [
            {"nome": "imponibile", "label": "Imponibile €", "type": "currency"},
            {"nome": "aliquota", "label": "Aliquota IVA %", "type": "percent", "default": 22, "options": [0, 4, 10, 22]}
        ],
        "calcola": lambda v: {
            "imponibile": v['imponibile'],
            "iva": round(v['imponibile'] * v['aliquota'] / 100, 2),
            "totale": round(v['imponibile'] * (1 + v['aliquota']/100), 2)
        }
    },
    "STIPENDI_LORDO": {
        "label": "👥 Competenza Stipendi (Lordo → Netto)",
        "campi": [
            {"nome": "lordo", "label": "Retribuzione Lorda €", "type": "currency"},
            {"nome": "irpef", "label": "IRPEF Trattenuta €", "type": "currency"},
            {"nome": "addizionali", "label": "Addizionali €", "type": "currency", "default": 0}
        ],
        "calcola": lambda v: {
            "lordo": v['lordo'],
            "inps_dip": round(v['lordo'] * 0.0919, 2),
            "irpef": v['irpef'],
            "addizionali": v.get('addizionali', 0),
            "netto": round(v['lordo'] - (v['lordo']*0.0919) - v['irpef'] - v.get('addizionali',0), 2),
            "inps_azi": round(v['lordo'] * 0.28, 2),
            "totale_azi": round(v['lordo'] + (v['lordo']*0.28), 2)
        }
    },
    "COMPENSO_RITENUTA": {
        "label": "🎓 Compenso Professionista (con Ritenuta)",
        "campi": [
            {"nome": "compenso", "label": "Compenso Lordo €", "type": "currency"},
            {"nome": "ritenuta_pct", "label": "Ritenuta %", "type": "percent", "default": 20, "options": [0, 20, 23]}
        ],
        "calcola": lambda v: {
            "compenso": v['compenso'],
            "ritenuta": round(v['compenso'] * v['ritenuta_pct'] / 100, 2),
            "netto": round(v['compenso'] - (v['compenso'] * v['ritenuta_pct'] / 100), 2)
        }
    },
    "PATRIMONIALE": {
        "label": "🏦 Operazione Patrimoniale (Senza IVA)",
        "campi": [{"nome": "importo", "label": "Importo €", "type": "currency"}],
        "calcola": lambda v: {"importo": v['importo']}
    },
    "AMMORTAMENTO": {
        "label": "📉 Quota Ammortamento",
        "campi": [{"nome": "quota", "label": "Quota Annuale €", "type": "currency"}],
        "calcola": lambda v: {"quota": v['quota']}
    },
    "LIQUIDAZIONE_IVA": {
        "label": "🏛️ Liquidazione IVA Periodica",
        "campi": [{"nome": "iva_da_versare", "label": "IVA a Debito (da versare) €", "type": "currency"}],
        "calcola": lambda v: {"iva_da_versare": v['iva_da_versare']}
    },
    "FINANZIARIO": {
        "label": "💳 Interessi / Commissioni Bancarie",
        "campi": [{"nome": "importo", "label": "Importo €", "type": "currency"}],
        "calcola": lambda v: {"importo": v['importo']}
    }
}

# ==============================================================================
# 3. DATABASE OPERAZIONI (40+ TEMPLATE)
# ==============================================================================
OPERAZIONI = {
    # === ACQUISTI & VENDITE ===
    "ACQ_MERCI": {"nome": "Acquisto Merci (Fattura Fornitore)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "73.01.013", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "49.13.001", "a": "totale"}]},
    "VEND_MERCI": {"nome": "Vendita Merci (Fattura Cliente)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "28.01.001", "a": "totale"}],
        "avere": [{"c": "60.01.009", "a": "imponibile"}, {"c": "49.23.009", "a": "iva"}]},
    "ACQ_SERVIZI": {"nome": "Acquisto Servizi/Consulenze", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.11.002", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "49.13.001", "a": "totale"}]},
    "VEND_SERVIZI": {"nome": "Vendita Servizi/Prestazioni", "tipo": "FATTURA_IVA",
        "dare": [{"c": "28.01.001", "a": "totale"}],
        "avere": [{"c": "60.01.005", "a": "imponibile"}, {"c": "49.23.009", "a": "iva"}]},
    "ACQ_BENI_STRUMENTALI": {"nome": "Acquisto Bene Strumentale (es. PC, Auto)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "13.09.065", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "49.13.001", "a": "totale"}]},
    "REVERSE_CHARGE": {"nome": "Reverse Charge (Autofattura)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "73.01.013", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "49.13.001", "a": "imponibile"}, {"c": "49.23.009", "a": "iva"}]},
    
    # === PAGAMENTI & INCASSI ===
    "PAG_FORNITORE": {"nome": "Pagamento Fornitore (Bonifico)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "49.13.001", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "INC_CLIENTE": {"nome": "Incasso Cliente (Bonifico)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "34.01.001", "a": "importo"}], "avere": [{"c": "28.01.001", "a": "importo"}]},
    "PAG_CASSA": {"nome": "Pagamento in Contanti/Cassa", "tipo": "PATRIMONIALE",
        "dare": [{"c": "49.13.001", "a": "importo"}], "avere": [{"c": "34.05.001", "a": "importo"}]},
    "INC_CARTA": {"nome": "Incasso Carta di Credito/POS", "tipo": "PATRIMONIALE",
        "dare": [{"c": "28.01.055", "a": "importo"}], "avere": [{"c": "28.01.001", "a": "importo"}]},
    
    # === PERSONALE ===
    "STIPENDI_COMP": {"nome": "Competenza Stipendi Dipendenti", "tipo": "STIPENDI_LORDO",
        "dare": [{"c": "79.01.005", "a": "lordo"}, {"c": "79.03.001", "a": "inps_azi"}],
        "avere": [{"c": "49.27.025", "a": "netto"}, {"c": "49.23.029", "a": "irpef"}, 
                  {"c": "49.25.001", "a": "inps_dip"}, {"c": "49.25.005", "a": "inps_azi"}]},
    "PAG_STIPENDI": {"nome": "Pagamento Stipendi (Bonifico)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "49.27.025", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "TFR_ACCANT": {"nome": "Accantonamento TFR", "tipo": "PATRIMONIALE",
        "dare": [{"c": "79.05.001", "a": "importo"}], "avere": [{"c": "46.01.001", "a": "importo"}]},
    "COMP_AMM": {"nome": "Compenso Amministratore (con Ritenuta)", "tipo": "COMPENSO_RITENUTA",
        "dare": [{"c": "75.11.017", "a": "compenso"}],
        "avere": [{"c": "49.27.001", "a": "netto"}, {"c": "49.23.039", "a": "ritenuta"}]},
    "COMP_COLL": {"nome": "Compenso Collaboratore/Co.Co.Pro.", "tipo": "COMPENSO_RITENUTA",
        "dare": [{"c": "75.11.073", "a": "compenso"}],
        "avere": [{"c": "49.27.041", "a": "netto"}, {"c": "49.23.033", "a": "ritenuta"}]},
    "PAG_RITENUTE": {"nome": "Versamento Ritenute (F24)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "49.23.029", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "PAG_INPS": {"nome": "Versamento Contributi INPS (F24)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "49.25.001", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    
    # === IMMOBILIZZAZIONI & AMMORTAMENTI ===
    "AMM_AUTO": {"nome": "Ammortamento Autovettura (40% ded.)", "tipo": "AMMORTAMENTO",
        "dare": [{"c": "83.09.001", "a": "quota"}, {"c": "83.11.105", "a": "quota_ind"}],
        "avere": [{"c": "16.07.001", "a": "quota"}]},
    "AMM_PC": {"nome": "Ammortamento Computer/Telefonia (80% ded.)", "tipo": "AMMORTAMENTO",
        "dare": [{"c": "83.09.065", "a": "quota"}, {"c": "83.11.169", "a": "quota_ind"}],
        "avere": [{"c": "16.07.045", "a": "quota"}]},
    "AMM_FABBRICATO": {"nome": "Ammortamento Fabbricato", "tipo": "AMMORTAMENTO",
        "dare": [{"c": "83.03.001", "a": "quota"}], "avere": [{"c": "16.01.005", "a": "quota"}]},
    "CAN_LEASING": {"nome": "Canone Leasing (Auto/PC)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "77.03.105", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "CAN_NOLEGGIO": {"nome": "Canone Noleggio Operativo", "tipo": "FATTURA_IVA",
        "dare": [{"c": "77.05.061", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
        
    # === GESTIONE CORRENTE ===
    "UTENZE": {"nome": "Utenze (Luce/Gas/Acqua/Telefono)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.01.025", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "AFFITTO": {"nome": "Canone Affitto Immobile", "tipo": "FATTURA_IVA",
        "dare": [{"c": "77.01.009", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "ASSICURAZIONE": {"nome": "Premio Assicurativo (Auto/RC)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.15.005", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "MANUT_AUTO": {"nome": "Manutenzione Auto/Gomme/Tagliando", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.05.105", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "CARBURANTE": {"nome": "Acquisto Carburante", "tipo": "FATTURA_IVA",
        "dare": [{"c": "73.09.006", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "CANCELLERIA": {"nome": "Cancelleria/Materiale Ufficio", "tipo": "FATTURA_IVA",
        "dare": [{"c": "73.09.045", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "VIAGGI": {"nome": "Viaggi/Trasferte (Hotel/Biglietti)", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.17.033", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "PUBBLICITA": {"nome": "Spese Pubblicità/Marketing", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.13.037", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "PULIZIE": {"nome": "Servizi di Pulizia", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.17.013", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
    "CONDOMINIO": {"nome": "Spese Condominiali", "tipo": "FATTURA_IVA",
        "dare": [{"c": "75.17.093", "a": "imponibile"}, {"c": "28.11.009", "a": "iva"}],
        "avere": [{"c": "34.01.001", "a": "totale"}]},
        
    # === TRIBUTI & IMPOSTE ===
    "LIQ_IVA": {"nome": "Liquidazione IVA a Debito", "tipo": "LIQUIDAZIONE_IVA",
        "dare": [{"c": "49.23.009", "a": "iva_da_versare"}], "avere": [{"c": "34.01.001", "a": "iva_da_versare"}]},
    "ACC_IRES_IRAP": {"nome": "Accantonamento IRES/IRAP", "tipo": "PATRIMONIALE",
        "dare": [{"c": "96.01.001", "a": "importo"}, {"c": "96.01.005", "a": "importo"}],
        "avere": [{"c": "49.23.001", "a": "importo"}, {"c": "49.23.005", "a": "importo"}]},
    "PAG_IMU": {"nome": "Pagamento IMU/TASI", "tipo": "PATRIMONIALE",
        "dare": [{"c": "92.01.005", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "BOLLI_TASSE": {"nome": "Imposte di Bollo/Tasse CCIAA", "tipo": "PATRIMONIALE",
        "dare": [{"c": "92.01.001", "a": "importo"}, {"c": "92.01.085", "a": "importo"}],
        "avere": [{"c": "34.01.001", "a": "importo"}]},
        
    # === FINANZIARIO & PATRIMONIO ===
    "INT_PASSIVI": {"nome": "Interessi Passivi Bancari/Mutuo", "tipo": "FINANZIARIO",
        "dare": [{"c": "93.15.021", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "COMM_BANCARIE": {"nome": "Commissioni/Spese Bancarie", "tipo": "FINANZIARIO",
        "dare": [{"c": "75.17.081", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "COSTITUZIONE": {"nome": "Costituzione Società (Versamento Capitale)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "34.01.001", "a": "importo"}], "avere": [{"c": "40.01.001", "a": "importo"}]},
    "VERS_SOCI": {"nome": "Versamento/Aumento Capitale Soci", "tipo": "PATRIMONIALE",
        "dare": [{"c": "34.01.001", "a": "importo"}], "avere": [{"c": "40.13.025", "a": "importo"}]},
    "PRESTITO_SOCIO": {"nome": "Prestito/Finanziamento Socio", "tipo": "PATRIMONIALE",
        "dare": [{"c": "34.01.001", "a": "importo"}], "avere": [{"c": "49.05.021", "a": "importo"}]},
    "RIMBORSO_SOCIO": {"nome": "Rimborso Finanziamento Socio", "tipo": "PATRIMONIALE",
        "dare": [{"c": "49.05.021", "a": "importo"}], "avere": [{"c": "34.01.001", "a": "importo"}]},
    "UTILI_PREC": {"nome": "Storno Utile Esercizio Precedente", "tipo": "PATRIMONIALE",
        "dare": [{"c": "40.17.001", "a": "importo"}], "avere": [{"c": "40.15.001", "a": "importo"}]},
    "DISTRIB_DIVIDENDI": {"nome": "Distribuzione Dividendi ai Soci", "tipo": "PATRIMONIALE",
        "dare": [{"c": "40.17.001", "a": "importo"}], "avere": [{"c": "49.27.089", "a": "importo"}]},
    "MINUSVALENZA": {"nome": "Minusvalenza Straordinaria", "tipo": "PATRIMONIALE",
        "dare": [{"c": "95.03.005", "a": "importo"}], "avere": [{"c": "13.09.001", "a": "importo"}]},
    "PLUSVALENZA": {"nome": "Plusvalenza Straordinaria", "tipo": "PATRIMONIALE",
        "dare": [{"c": "34.01.001", "a": "importo"}], "avere": [{"c": "95.01.005", "a": "importo"}]},
    "SVAL_CREDITI": {"nome": "Svalutazione Crediti (Fondo Rischi)", "tipo": "PATRIMONIALE",
        "dare": [{"c": "87.01.001", "a": "importo"}], "avere": [{"c": "28.03.001", "a": "importo"}]},
}

# ==============================================================================
# 4. LOGICA GENERAZIONE
# ==============================================================================
def fmt_conto(codice):
    return f"{codice} - {piano.get(codice, {}).get('desc', '❌ Conto non trovato')}"

def genera_scrittura(op_code, valori):
    op = OPERAZIONI[op_code]
    cfg = INPUT_CONFIG[op['tipo']]
    calcoli = cfg['calcola'](valori)
    
    # Gestione ammortamenti con quota indeducibile
    if op_code in ["AMM_AUTO", "AMM_PC"]:
        quota = calcoli['quota']
        pct_ind = 0.6 if op_code == "AMM_AUTO" else 0.2
        calcoli['quota_ind'] = round(quota * pct_ind, 2)
        calcoli['quota'] = round(quota * (1 - pct_ind), 2)
        
    dare, avere = [], []
    for riga in op['dare']:
        dare.append({'conto': riga['c'], 'importo': round(calcoli.get(riga['a'], 0), 2)})
    for riga in op['avere']:
        avere.append({'conto': riga['c'], 'importo': round(calcoli.get(riga['a'], 0), 2)})
        
    return dare, avere, calcoli

# ==============================================================================
# 5. INTERFACCIA STREAMLIT
# ==============================================================================
st.title("📒 Generatore Scritture Contabili SRL")

uploaded_pdf = st.sidebar.file_uploader("📄 Carica Piano dei Conti (PDF)", type=['pdf'])
if not uploaded_pdf:
    st.warning("⚠️ Carica il PDF dalla sidebar per iniziare."); st.stop()

with st.spinner("🔍 Lettura piano dei conti..."):
    piano = parse_piano_ranocchi(uploaded_pdf)
if not piano:
    st.error("❌ Impossibile estrarre conti. Verifica il PDF."); st.stop()

st.sidebar.success(f"✅ {len(piano)} conti caricati")

# Selezione Operazione
cat_filter = st.selectbox("📂 Categoria Operazione", 
    ["Tutte"] + sorted(list({op['tipo'] for op in OPERAZIONI.values()})),
    format_func=lambda x: {
        "Tutte": "📋 Tutte le Operazioni", "FATTURA_IVA": "🧾 Fatture con IVA", 
        "STIPENDI_LORDO": "👥 Personale & Stipendi", "COMPENSO_RITENUTA": "🎓 Compensi Professionisti",
        "PATRIMONIALE": "🏦 Patrimonio & Pagamenti", "AMMORTAMENTO": "📉 Ammortamenti Cespiti",
        "LIQUIDAZIONE_IVA": "🏛️ Tributi & IVA", "FINANZIARIO": "💳 Finanziario & Bancario"
    }.get(x, x))

ops = {k:v for k,v in OPERAZIONI.items() if cat_filter == "Tutte" or v['tipo'] == cat_filter}
op_code = st.selectbox("📝 Seleziona Operazione", list(ops.keys()), format_func=lambda x: ops[x]['nome'])

# Input Dinamici
if op_code:
    cfg = INPUT_CONFIG[ops[op_code]['tipo']]
    st.subheader(f"💰 {cfg['label']}")
    
    valori = {}
    cols = st.columns(len(cfg['campi']))
    for i, campo in enumerate(cfg['campi']):
        with cols[i]:
            k = f"{op_code}_{campo['nome']}"
            if campo['type'] == 'currency':
                valori[campo['nome']] = st.number_input(campo['label'], min_value=0.0, step=0.01, format="%.2f", key=k)
            elif campo['type'] == 'percent':
                valori[campo['nome']] = st.selectbox(campo['label'], options=campo.get('options', [0, 20, 23]), index=0, key=k)
                
    if st.button("🚀 Genera Scrittura", type="primary", use_container_width=True):
        dare, avere, calc = genera_scrittura(op_code, valori)
        tot_d = sum(r['importo'] for r in dare)
        tot_a = sum(r['importo'] for r in avere)
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**DARE**")
            df_d = pd.DataFrame(dare)
            df_d['Descrizione'] = df_d['conto'].apply(fmt_conto)
            st.dataframe(df_d[['conto', 'Descrizione', 'importo']].rename(columns={'importo':'Importo €'}), hide_index=True)
            st.metric("Totale Dare", f"€ {tot_d:,.2f}")
            
        with c2:
            st.write("**AVERE**")
            df_a = pd.DataFrame(avere)
            df_a['Descrizione'] = df_a['conto'].apply(fmt_conto)
            st.dataframe(df_a[['conto', 'Descrizione', 'importo']].rename(columns={'importo':'Importo €'}), hide_index=True)
            st.metric("Totale Avere", f"€ {tot_a:,.2f}")
            
        if abs(tot_d - tot_a) < 0.01:
            st.success("✅ Scrittura BILANCIATA (DARE = AVERE)")
            
            # Export CSV
            csv_rows = []
            for r in dare: csv_rows.append({'Lato':'DARE', 'Conto':r['conto'], 'Descrizione':piano[r['conto']]['desc'], 'Importo':r['importo']})
            for r in avere: csv_rows.append({'Lato':'AVERE', 'Conto':r['conto'], 'Descrizione':piano[r['conto']]['desc'], 'Importo':r['importo']})
            
            st.download_button(
                label="📥 Scarica CSV (Ranocchi Compatible)",
                data=pd.DataFrame(csv_rows).to_csv(index=False, sep=';', decimal=','),
                file_name=f"scrittura_{op_code}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error(f"❌ NON BILANCIATA | Diff: € {abs(tot_d-tot_a):,.2f}")
