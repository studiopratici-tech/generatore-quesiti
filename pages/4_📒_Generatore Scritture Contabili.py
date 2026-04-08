import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
import unicodedata

st.set_page_config(layout="wide", page_title="Assistente Contabile Ranocchi | Studio Pratici")

# ==============================================================================
# 1. CONFIGURAZIONE & SINONIMI PER LA RICERCA
# ==============================================================================
SYNONYMS = {
    "luce": ["energia", "elettrica", "illuminazione", "bolletta", "utenza"],
    "auto": ["autovettura", "veicolo", "macchina", "automobile", "car", "macchinario"],
    "manutenzione": ["manut", "riparazione", "riparaz", "guasto", "assistenza", "tagliando"],
    "telefono": ["telefonia", "telefono", "cellulare", "mobile", "fisso", "voip", "sim"],
    "affitto": ["locazione", "canone", "fitto", "affitto", "noleggio"],
    "commercialista": ["consulenza", "amministrazione", "contabilità", "ragioniere", "commercialista", "tenuta"],
    "tasse": ["imu", "tassa", "bollo", "imposta", "tributo", "cciaa", "registro"],
    "stipendio": ["personale", "dipendente", "salario", "retribuzione", "busta paga", "operaio", "impiegato"],
    "computer": ["pc", "informatica", "hardware", "software", "notebook", "server", "macchina ufficio"],
    "benzina": ["carburante", "carbur", "gasolio", "benzina", "lubrificante", "rifornimento"],
    "assicurazione": ["polizza", "rc", "rischio", "copertura", "sinistro"],
    "banca": ["conto", "bonifico", "c/c", "finanziamento", "mutuo", "interessi passivi"],
    "iva": ["imposta", "credito", "debito", "liquidazione", "acconto", "split", "reverse"],
    "cliente": ["fattura attiva", "credito v/clienti", "incasso", "vendita"],
    "fornitore": ["fattura passiva", "debito v/fornitori", "pagamento", "acquisto"]
}

# ==============================================================================
# 2. PARSER PDF ROBUSTO
# ==============================================================================
@st.cache_data
def parse_piano_conti(pdf_file):
    """Estrae i conti dal PDF gestendo il formato esatto della stampa Ranocchi"""
    accounts = {}
    try:
        with pdfplumber.open(pdf_file) as pdf:
            full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        
        # Pulizia base: rimuove caratteri speciali e normalizza spazi
        clean_text = re.sub(r'[|\\n\r\t]', ' ', full_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Pattern: 13.09.001 AUTOVETTURE Patrimoniale attivo
        pattern = r'(\d{2}\.\d{2}\.\d{3})\s+(.*?)\s+(Patrimoniale|Economico|Conto\s+d\'ordine)\s+(attivo|passivo|costi|ricavi)?'
        
        for match in re.finditer(pattern, clean_text, re.IGNORECASE):
            code, desc, macro, detail = match.groups()
            detail = detail.strip() if detail else ""
            natura = f"{macro.strip()} {detail}".strip()
            
            # Pre-elaborazione per ricerca veloce
            desc_norm = unicodedata.normalize('NFKD', desc).encode('ASCII', 'ignore').decode().lower()
            tokens = set(re.sub(r'[^a-z0-9 ]', '', desc_norm).split())
            
            accounts[code] = {
                "desc": desc.strip(),
                "natura": natura,
                "macro": macro.strip(),
                "tokens": tokens
            }
    except Exception as e:
        st.error(f"Errore lettura PDF: {e}")
        return {}
        
    return accounts

# ==============================================================================
# 3. MOTORE DI RICERCA AVANZATO
# ==============================================================================
def search_accounts(query, accounts_db):
    if not query or not accounts_db:
        return []
    
    q = query.lower().strip()
    # Espansione query con sinonimi
    expanded_tokens = set(q.split())
    for key, syns in SYNONYMS.items():
        if key in q or any(q.startswith(s[:3]) for s in syns):
            expanded_tokens.update(syns)
            
    results = []
    for code, info in accounts_db.items():
        score = 0
        
        # Match esatto codice
        if q in code:
            score += 100
        # Match descrizione esatta o parziale
        if q in info["desc"].lower():
            score += 50
        # Match per token/sinonimi
        overlap = expanded_tokens & info["tokens"]
        if overlap:
            score += len(overlap) * 10
            
        # Boost per corrispondenze parziali forti
        if any(token in info["desc"].lower() for token in expanded_tokens):
            score += 5
            
        if score > 0:
            results.append((code, info, score))
            
    # Ordina per rilevanza
    results.sort(key=lambda x: x[2], reverse=True)
    return [(c, i) for c, i, _ in results[:25]]  # Top 25 risultati

def get_natura_badge(macro):
    """Restituisce HTML/Markdown per evidenziare la natura contabile"""
    if "economico" in macro.lower():
        return "🟠 **Economico**"
    elif "patrimoniale" in macro.lower():
        return "🟢 **Patrimoniale**"
    elif "conto d'ordine" in macro.lower():
        return "🔵 **Conto d'Ordine**"
    return "⚪ Altro"

# ==============================================================================
# 4. INTERFACCIA UTENTE
# ==============================================================================
def main():
    st.title("📒 Assistente Contabile Intelligente (Ranocchi GIS)")
    st.markdown("Cerca un'operazione o una parola chiave. Il sistema troverà i conti corretti distinguendo chiaramente tra **Patrimoniali** e **Economici**.")

    # SIDEBAR: Caricamento PDF
    with st.sidebar:
        st.header("📂 Caricamento Piano dei Conti")
        uploaded_pdf = st.file_uploader("Carica il PDF della stampa Ranocchi", type=["pdf"])
        
        if uploaded_pdf:
            with st.spinner("🔍 Analisi del PDF in corso..."):
                piano_conti = parse_piano_conti(uploaded_pdf)
            if piano_conti:
                st.success(f"✅ Piano caricato: {len(piano_conti)} conti estratti")
                st.divider()
                st.caption("💡 Suggerimento: usa parole come *'luce'*, *'manutenzione'*, *'auto'*, *'stipendi'*")
            else:
                st.error("❌ Nessun conto trovato. Verifica che il PDF sia una stampa Ranocchi valida.")
                st.stop()
        else:
            st.warning("⚠️ Carica il PDF per iniziare.")
            st.stop()

    # MAIN: Ricerca
    st.subheader("🔎 Ricerca Conti")
    query = st.text_input("Descrivi l'operazione o inserisci il codice (es. 'Bolletta luce', 'Manutenzione auto', '13.09.001')", placeholder="Scrivi qui...")
    
    if query:
        risultati = search_accounts(query, piano_conti)
        
        if not risultati:
            st.info("Nessun risultato trovato. Prova con un termine più generico o un codice.")
            return
            
        st.success(f"Trovati {len(risultati)} conti pertinenti.")
        
        # Preparazione DataFrame per visualizzazione
        data = []
        for code, info in risultati:
            data.append({
                "Codice": code,
                "Descrizione": info["desc"],
                "Natura": get_natura_badge(info["macro"]),
                "Macro": info["macro"]
            })
        df_res = pd.DataFrame(data)
        
        # Visualizzazione tabella
        st.dataframe(df_res[["Codice", "Descrizione", "Natura"]], use_container_width=True, hide_index=True)
        
        # SELEZIONE DARE / AVERE
        st.divider()
        st.subheader("📝 Composizione Scrittura")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🔴 Seleziona Conto DARE (Debito)**")
            dare_options = [f"{r['Codice']} | {r['Descrizione']}" for _, r in df_res.iterrows()]
            dare_sel = st.selectbox("Conto DARE", [""] + dare_options, label_visibility="collapsed")
            
        with col2:
            st.write("**🟢 Seleziona Conto AVERE (Credito)**")
            avere_options = [f"{r['Codice']} | {r['Descrizione']}" for _, r in df_res.iterrows()]
            avere_sel = st.selectbox("Conto AVERE", [""] + avere_options, label_visibility="collapsed")
            
        # INPUT IMPORTI
        if dare_sel and avere_sel:
            st.divider()
            st.subheader("💰 Inserimento Importi")
            col_imp1, col_imp2 = st.columns(2)
            with col_imp1:
                imp_dare = st.number_input("Importo DARE €", min_value=0.0, step=0.01, format="%.2f", key="imp_d")
            with col_imp2:
                imp_avere = st.number_input("Importo AVERE €", min_value=0.0, step=0.01, format="%.2f", key="imp_a")
                
            # GENERAZIONE OUTPUT
            if imp_dare > 0 and imp_avere > 0:
                # Pulizia selezione
                cod_dare = dare_sel.split(" | ")[0]
                desc_dare = dare_sel.split(" | ")[1]
                cod_avere = avere_sel.split(" | ")[0]
                desc_avere = avere_sel.split(" | ")[1]
                
                # Costruzione righe
                righe = [
                    {"Lato": "DARE", "Codice": cod_dare, "Descrizione": desc_dare, "Importo €": imp_dare},
                    {"Lato": "AVERE", "
