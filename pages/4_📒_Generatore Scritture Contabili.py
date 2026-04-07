import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime

st.set_page_config(layout="wide", page_title="Generatore Scritture Contabili | Ranocchi GIS")

# ==============================================================================
# 1. PARSER ROBUSTO PER PDF RANOCCHI GIS
# ==============================================================================
@st.cache_data
def parse_piano_ranocchi(pdf_file):
    """Estrae i conti dal PDF mantenendo il formato esatto della stampa GIS"""
    piano = {}
    with pdfplumber.open(pdf_file) as pdf:
        # Unisce tutto il testo e normalizza spazi/linee
        testo_raw = "\n".join(page.extract_text() or "" for page in pdf.pages)
        testo_pulito = re.sub(r'\s+', ' ', testo_raw)
        
        # Pattern specifico per: | XX.XX.XXX  DESCRIZIONE  Posizione |
        pattern = r'\|?\s*(\d{2}\.\d{2}\.\d{3})\s+(.*?)\s+(Patrimoniale|Economico|Conto\s+d\'ordine)(?:\s+(attivo|passivo|costi|ricavi))?\s*\|?'
        
        for match in re.finditer(pattern, testo_pulito, re.IGNORECASE):
            codice = match.group(1)
            descrizione = match.group(2).strip().title()
            macro = match.group(3).strip()
            dettaglio = match.group(4).strip() if match.group(4) else ""
            posizione = f"{macro} {dettaglio}".strip()
            
            # Determina Dare/Avere in base alla posizione
            pos_lower = posizione.lower()
            normale = 'dare' if any(k in pos_lower for k in ['attivo', 'costi']) else 'avere'
            
            piano[codice] = {
                'desc': descrizione,
                'posizione': posizione,
                'normale': normale
            }
    return piano

# ==============================================================================
# 2. LOGICA OPERATIVA & TEMPLATE
# ==============================================================================
def fmt_conto(codice):
    return f"{codice} - {piano.get(codice, {}).get('desc', '❌ Conto non trovato')}"

def calcola_scrittura(tipo_op, valori):
    dare, avere = [], []
    
    if tipo_op == "FATTURA_ACQUISTO":
        imp = valori['imponibile']
        iva = round(imp * valori['aliquota'] / 100, 2)
        tot = round(imp + iva, 2)
        dare = [
            {'conto': '73.01.013', 'importo': imp},
            {'conto': '28.11.009', 'importo': iva}
        ]
        avere = [{'conto': '49.13.001', 'importo': tot}]
        
    elif tipo_op == "FATTURA_VENDITA":
        imp = valori['imponibile']
        iva = round(imp * valori['aliquota'] / 100, 2)
        tot = round(imp + iva, 2)
        dare = [{'conto': '28.01.001', 'importo': tot}]
        avere = [
            {'conto': '60.01.009', 'importo': imp},
            {'conto': '49.23.009', 'importo': iva}
        ]
        
    elif tipo_op == "STIPENDI":
        lordo = valori['lordo']
        inps_dip = round(lordo * 9.19 / 100, 2)
        irpef = valori['irpef']
        netto = round(lordo - inps_dip - irpef, 2)
        inps_azi = round(lordo * 28.0 / 100, 2)
        
        dare = [
            {'conto': '79.01.005', 'importo': lordo},
            {'conto': '79.03.001', 'importo': inps_azi}
        ]
        avere = [
            {'conto': '49.27.025', 'importo': netto},
            {'conto': '49.23.029', 'importo': irpef},
            {'conto': '49.25.001', 'importo': inps_dip + inps_azi}
        ]
        
    elif tipo_op == "PATRIMONIALE":
        imp = valori['importo']
        dare = [{'conto': valori['conto_dare'], 'importo': imp}]
        avere = [{'conto': valori['conto_avere'], 'importo': imp}]
        
    elif tipo_op == "AMMORTAMENTO":
        quota = valori['quota']
        cespite = valori['cespite']
        fondo = valori['fondo']
        
        # Deducibilità automatica
        if '13.09.001' in cespite: # Auto
            dare = [{'conto': '83.09.001', 'importo': round(quota*0.4, 2)}, 
                    {'conto': '83.11.105', 'importo': round(quota*0.6, 2)}]
        elif '13.09.065' in cespite or '13.09.073' in cespite: # PC/Tel
            dare = [{'conto': '83.09.065', 'importo': round(quota*0.8, 2)},
                    {'conto': '83.11.169', 'importo': round(quota*0.2, 2)}]
        else:
            dare = [{'conto': cespite, 'importo': quota}]
        avere = [{'conto': fondo, 'importo': quota}]
        
    return dare, avere

# ==============================================================================
# 3. INTERFACCIA STREAMLIT
# ==============================================================================
st.title("📒 Generatore Scritture Contabili SRL")

# UPLOAD PDF (OBBLIGATORIO)
uploaded_pdf = st.sidebar.file_uploader("📄 Carica Piano dei Conti (PDF Ranocchi)", type=['pdf'])

if not uploaded_pdf:
    st.warning("⚠️ **Carica il PDF del piano dei conti dalla sidebar per iniziare.**")
    st.stop()

with st.spinner("🔍 Lettura piano dei conti in corso..."):
    piano = parse_piano_ranocchi(uploaded_pdf)

if not piano:
    st.error("❌ Impossibile estrarre conti dal PDF. Verifica che sia una stampa Ranocchi GIS.")
    st.stop()

st.sidebar.success(f"✅ Piano caricato: **{len(piano)} conti**")
st.sidebar.info("📌 Tutte le scritture mostreranno `CODICE - DESCRIZIONE COMPLETA`")

# SELEZIONE OPERAZIONE
st.subheader("🛠️ Tipo di Operazione")
tipo = st.selectbox(
    "Scegli la tipologia per adattare i campi di input",
    ["FATTURA_ACQUISTO", "FATTURA_VENDITA", "STIPENDI", "PATRIMONIALE", "AMMORTAMENTO"],
    format_func=lambda x: {
        "FATTURA_ACQUISTO": "🧾 Fattura Acquisto (con IVA)",
        "FATTURA_VENDITA": "💶 Fattura Vendita (con IVA)",
        "STIPENDI": "👥 Registrazione Stipendi (Lordo→Netto)",
        "PATRIMONIALE": "🏦 Operazione Patrimoniale (Senza IVA)",
        "AMMORTAMENTO": "📉 Quota Ammortamento Cespiti"
    }[x]
)

# INPUT DINAMICI
col1, col2 = st.columns(2)
with col1:
    st.markdown("**💰 Inserimento Importi**")
    if "FATTURA" in tipo:
        imponibile = st.number_input("Imponibile €", min_value=0.0, step=0.01, format="%.2f")
        aliquota = st.selectbox("Aliquota IVA %", [4, 10, 22], index=2)
        valori = {'imponibile': imponibile, 'aliquota': aliquota}
    elif tipo == "STIPENDI":
        lordo = st.number_input("Retribuzione Lorda €", min_value=0.0, step=0.01, format="%.2f")
        irpef = st.number_input("IRPEF Trattenuta €", min_value=0.0, step=0.01, format="%.2f")
        valori = {'lordo': lordo, 'irpef': irpef}
    elif tipo == "PATRIMONIALE":
        importo = st.number_input("Importo Operazione €", min_value=0.0, step=0.01, format="%.2f")
        col_a, col_b = st.columns(2)
        with col_a:
            dare_search = st.selectbox("Conto DARE", sorted(piano.keys()), format_func=fmt_conto)
        with col_b:
            avere_search = st.selectbox("Conto AVERE", sorted(piano.keys()), format_func=fmt_conto)
        valori = {'importo': importo, 'conto_dare': dare_search, 'conto_avere': avere_search}
    elif tipo == "AMMORTAMENTO":
        quota = st.number_input("Quota Annuale €", min_value=0.0, step=0.01, format="%.2f")
        col_c, col_d = st.columns(2)
        with col_c:
            cespite = st.selectbox("Conto Cespite (Costo)", ["83.09.001", "83.09.065", "83.09.073", "83.03.001", "83.07.001"], format_func=fmt_conto)
        with col_d:
            fondo = st.selectbox("Conto Fondo Amm.to", ["16.07.001", "16.07.045", "16.07.053", "16.01.005", "16.07.057"], format_func=fmt_conto)
        valori = {'quota': quota, 'cespite': cespite, 'fondo': fondo}

with col2:
    st.markdown("**📋 Note Operative**")
    note = {
        "FATTURA_ACQUISTO": "DARE: Merci + IVA Credito\nAVERE: Fornitore (Totale documento)",
        "FATTURA_VENDITA": "DARE: Cliente (Totale)\nAVERE: Vendite + IVA Debito",
        "STIPENDI": "Calcolo automatico:\n- Netto = Lordo - INPS dip(9.19%) - IRPEF\n- Oneri Azienda = Lordo * 28%",
        "PATRIMONIALE": "Operazioni senza IVA:\n- Versamento capitale, prestiti soci, riserve",
        "AMMORTAMENTO": "Deducibilità automatica:\n- Auto: 40% deducibile / 60% inded.\n- PC/Tel: 80% deducibile / 20% inded."
    }
    st.code(note[tipo], language="markdown")

# GENERAZIONE & VALIDAZIONE
if st.button("🚀 Genera Scrittura Contabile", type="primary", use_container_width=True):
    dare, avere = calcola_scrittura(tipo, valori)
    tot_dare = sum(r['importo'] for r in dare)
    tot_avere = sum(r['importo'] for r in avere)
    
    c1, c2 = st.columns(2)
    
    def render_tabella(righe, lato):
        df = pd.DataFrame(righe)
        df['Descrizione Completa'] = df['conto'].apply(fmt_conto)
        df = df[['conto', 'Descrizione Completa', 'importo']]
        df.columns = ['Codice', 'Codice - Descrizione', 'Importo €']
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.metric(f"Totale {lato}", f"€ {sum(righe['importo']):,.2f}")
        
    with c1:
        render_tabella(pd.DataFrame(dare), "DARE")
    with c2:
        render_tabella(pd.DataFrame(avere), "AVERE")
        
    # VALIDAZIONE
    if abs(tot_dare - tot_avere) < 0.01:
        st.success("✅ **Scrittura BILANCIATA** (DARE = AVERE)")
        
        # EXPORT CSV
        csv_rows = []
        for r in dare:
            csv_rows.append({'Lato': 'DARE', 'Conto': r['conto'], 'Descrizione': piano[r['conto']]['desc'], 'Importo': r['importo']})
        for r in avere:
            csv_rows.append({'Lato': 'AVERE', 'Conto': r['conto'], 'Descrizione': piano[r['conto']]['desc'], 'Importo': r['importo']})
            
        csv_data = pd.DataFrame(csv_rows).to_csv(index=False, sep=';', decimal=',')
        st.download_button(
            label="📥 Scarica Scrittura (CSV per Ranocchi)",
            data=csv_data,
            file_name=f"scrittura_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.error(f"❌ **NON BILANCIATA** | Differenza: € {abs(tot_dare-tot_avere):,.2f}")
