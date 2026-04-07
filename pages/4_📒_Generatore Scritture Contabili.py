import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime

st.set_page_config(page_title="Generatore Scritture Contabili", layout="wide")

# =============================================================================
# PARSING PDF PIANO DEI CONTI
# =============================================================================
@st.cache_data
def parse_piano_conti(pdf_file):
    """Estrae i conti dal PDF del piano dei conti"""
    conti = {}
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Pattern: CODICE  DESCRIZIONE  POSIZIONE
                pattern = r'(\d{2}\.\d{2}\.\d{3})\s+([A-Z\s\.\']+?)\s+(Patrimoniale\s*(?:attivo|passivo)?|Economico\s*(?:costi|ricavi)?|Conto\s*d\'ordine)'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    codice, descrizione, posizione = match.groups()
                    conti[codice] = {
                        'desc': descrizione.strip().title(),
                        'posizione': posizione.strip(),
                        'normale': 'dare' if 'attivo' in posizione.lower() or 'costi' in posizione.lower() else 'avere'
                    }
    return conti

# =============================================================================
# INTERFACCIA PRINCIPALE
# =============================================================================
st.title("📒 Generatore Scritture Contabili SRL")

# Upload PDF
uploaded_pdf = st.sidebar.file_uploader("📄 Carica PDF Piano dei Conti", type=['pdf'])

if uploaded_pdf is None:
    st.warning("⚠️ Carica il PDF del piano dei conti dalla sidebar per iniziare")
    st.stop()

# Parsing
with st.spinner('Caricamento piano dei conti...'):
    piano_conti = parse_piano_conti(uploaded_pdf)
    
if not piano_conti:
    st.error("❌ Nessun conto trovato nel PDF. Verifica il formato.")
    st.stop()

st.sidebar.success(f"✅ {len(piano_conti)} conti caricati")

# =============================================================================
# GENERAZIONE SCRITTURA
# =============================================================================
st.header("✍️ Nuova Scrittura Contabile")

col1, col2 = st.columns(2)

with col1:
    st.subheader("DARE")
    dare_conti = []
    num_dare = st.number_input("Righe DARE", min_value=1, max_value=5, value=1)
    for i in range(num_dare):
        codice = st.selectbox(f"Conto DARE {i+1}", 
                             sorted(piano_conti.keys()),
                             format_func=lambda x: f"{x} - {piano_conti[x]['desc']}",
                             key=f"dare_{i}")
        importo = st.number_input(f"Importo {i+1}", min_value=0.0, step=0.01, key=f"imp_dare_{i}")
        if codice and importo > 0:
            dare_conti.append({'conto': codice, 'desc': piano_conti[codice]['desc'], 'importo': importo})

with col2:
    st.subheader("AVERE")
    avere_conti = []
    num_avere = st.number_input("Righe AVERE", min_value=1, max_value=5, value=1)
    for i in range(num_avere):
        codice = st.selectbox(f"Conto AVERE {i+1}",
                             sorted(piano_conti.keys()),
                             format_func=lambda x: f"{x} - {piano_conti[x]['desc']}",
                             key=f"avere_{i}")
        importo = st.number_input(f"Importo {i+1}", min_value=0.0, step=0.01, key=f"imp_avere_{i}")
        if codice and importo > 0:
            avere_conti.append({'conto': codice, 'desc': piano_conti[codice]['desc'], 'importo': importo})

# =============================================================================
# VISUALIZZAZIONE E VALIDAZIONE
# =============================================================================
if st.button("✅ Genera Scrittura", type="primary"):
    tot_dare = sum(r['importo'] for r in dare_conti)
    tot_avere = sum(r['importo'] for r in avere_conti)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**DARE**")
        if dare_conti:
            df_dare = pd.DataFrame(dare_conti)
            st.dataframe(df_dare, hide_index=True, use_container_width=True)
        st.metric("Totale DARE", f"€ {tot_dare:,.2f}")
    
    with col2:
        st.write("**AVERE**")
        if avere_conti:
            df_avere = pd.DataFrame(avere_conti)
            st.dataframe(df_avere, hide_index=True, use_container_width=True)
        st.metric("Totale AVERE", f"€ {tot_avere:,.2f}")
    
    # Validazione
    if abs(tot_dare - tot_avere) < 0.01:
        st.success("✅ Scrittura BILANCIATA")
        
        # Export CSV
        csv_data = "Lato;Conto;Descrizione;Importo\n"
        for r in dare_conti:
            csv_data += f"DARE;{r['conto']};{r['desc']};{r['importo']:.2f}\n"
        for r in avere_conti:
            csv_data += f"AVERE;{r['conto']};{r['desc']};{r['importo']:.2f}\n"
        
        st.download_button(
            label="📥 Scarica CSV",
            data=csv_data,
            file_name=f"scrittura_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.error(f"❌ Scrittura NON BILANCIATA (diff: € {abs(tot_dare - tot_avere):,.2f})")

# Info
with st.expander("📊 Info Piano dei Conti Caricato"):
    st.write(f"**Totale conti:** {len(piano_conti)}")
    st.write("**Prime 10 voci:**")
    for i, (codice, info) in enumerate(list(piano_conti.items())[:10]):
        st.write(f"- {codice}: {info['desc']} ({info['normale']})")
