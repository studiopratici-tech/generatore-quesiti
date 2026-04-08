import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime

st.set_page_config(layout="wide", page_title="Assistente Contabile Ranocchi")

# =============================================================================
# PARSER PDF PIANO DEI CONTI
# =============================================================================
@st.cache_data
def parse_piano_conti(pdf_file):
    """Estrae i conti dal PDF del piano dei conti Ranocchi"""
    conti = {}
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Pattern: CODICE  DESCRIZIONE  Posizione in bilancio
                    pattern = r'(\d{2}\.\d{2}\.\d{3})\s+([A-Z\s\.\']+?)\s+(Patrimoniale\s*(?:attivo|passivo)?|Economico\s*(?:costi|ricavi)?|Conto\s*d\'ordine)'
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        codice, descrizione, posizione = match.groups()
                        conti[codice] = {
                            'desc': descrizione.strip().title(),
                            'posizione': posizione.strip(),
                            'normale': 'dare' if 'attivo' in posizione.lower() or 'costi' in posizione.lower() else 'avere'
                        }
    except Exception as e:
        st.error(f"Errore lettura PDF: {e}")
    return conti

# =============================================================================
# MOTORE DI RICERCA AVANZATO
# =============================================================================
def cerca_conti(query, piano_conti):
    """Cerca conti nel piano dei conti"""
    if not query:
        return {}
    
    query_lower = query.lower()
    risultati = {}
    
    for codice, info in piano_conti.items():
        if (query_lower in codice.lower() or 
            query_lower in info['desc'].lower() or
            query_lower in info['posizione'].lower()):
            risultati[codice] = info
    
    return risultati

def get_badge_natura(posizione):
    """Restituisce badge colorato per la natura del conto"""
    if 'economico' in posizione.lower():
        if 'costi' in posizione.lower():
            return "🔴 Economico - Costi"
        else:
            return "🟢 Economico - Ricavi"
    elif 'patrimoniale' in posizione.lower():
        if 'attivo' in posizione.lower():
            return "🔵 Patrimoniale - Attivo"
        else:
            return "🟣 Patrimoniale - Passivo"
    else:
        return "⚪ Conto d'Ordine"

# =============================================================================
# INTERFACCIA PRINCIPALE
# =============================================================================
def main():
    st.title("📒 Assistente Contabile Intelligente")
    st.markdown("**Piano dei Conti Ranocchi GIS** - Ricerca conti e genera scritture")
    
    # SIDEBAR - Caricamento PDF
    with st.sidebar:
        st.header("📂 Configurazione")
        uploaded_pdf = st.file_uploader("Carica PDF Piano dei Conti", type=["pdf"])
        
        if uploaded_pdf is None:
            st.warning("⚠️ Carica il PDF per iniziare")
            st.stop()
        
        # Parsing PDF
        with st.spinner("🔄 Lettura piano dei conti..."):
            piano_conti = parse_piano_conti(uploaded_pdf)
        
        if not piano_conti:
            st.error("❌ Nessun conto trovato nel PDF")
            st.stop()
        
        st.success(f"✅ {len(piano_conti)} conti caricati")
        st.divider()
        st.info("💡 Cerca per: codice, descrizione o parola chiave")
    
    # MAIN - Ricerca
    st.subheader("🔍 Ricerca Conti")
    query = st.text_input(
        "Inserisci termine di ricerca",
        placeholder="Es: 'banca', '13.09.001', 'autovettura', 'manutenzione'..."
    )
    
    if query:
        risultati = cerca_conti(query, piano_conti)
        
        if not risultati:
            st.info("Nessun risultato trovato")
        else:
            st.success(f"Trovati {len(risultati)} conti")
            
            # Tabella risultati
            dati = []
            for codice, info in sorted(risultati.items()):
                dati.append({
                    "Codice": codice,
                    "Descrizione": info['desc'],
                    "Natura": get_badge_natura(info['posizione']),
                    "Posizione": info['posizione']
                })
            
            df = pd.DataFrame(dati)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Selezione per scrittura
            st.divider()
            st.subheader("📝 Composizione Scrittura")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🔴 Conto DARE**")
                opzioni_dare = [f"{cod} | {info['desc']}" for cod, info in risultati.items()]
                dare_sel = st.selectbox("Seleziona conto DARE", [""] + opzioni_dare, key="dare")
            
            with col2:
                st.write("**🟢 Conto AVERE**")
                opzioni_avere = [f"{cod} | {info['desc']}" for cod, info in risultati.items()]
                avere_sel = st.selectbox("Seleziona conto AVERE", [""] + opzioni_avere, key="avere")
            
            # Input importi
            if dare_sel and avere_sel:
                st.divider()
                col_imp1, col_imp2 = st.columns(2)
                
                with col_imp1:
                    imp_dare = st.number_input("Importo DARE €", min_value=0.0, step=0.01, format="%.2f")
                
                with col_imp2:
                    imp_avere = st.number_input("Importo AVERE €", min_value=0.0, step=0.01, format="%.2f")
                
                # Genera scrittura
                if imp_dare > 0 and imp_avere > 0:
                    # Estrai codici
                    cod_dare = dare_sel.split(" | ")[0]
                    desc_dare = piano_conti[cod_dare]['desc']
                    
                    cod_avere = avere_sel.split(" | ")[0]
                    desc_avere = piano_conti[cod_avere]['desc']
                    
                    # Mostra scrittura
                    st.divider()
                    st.subheader("✅ Scrittura Generata")
                    
                    col_d, col_a = st.columns(2)
                    
                    with col_d:
                        st.write("**DARE**")
                        st.write(f"`{cod_dare}` - {desc_dare}")
                        st.metric("Importo", f"€ {imp_dare:,.2f}")
                    
                    with col_a:
                        st.write("**AVERE**")
                        st.write(f"`{cod_avere}` - {desc_avere}")
                        st.metric("Importo", f"€ {imp_avere:,.2f}")
                    
                    # Verifica pareggio
                    if abs(imp_dare - imp_avere) < 0.01:
                        st.success("✅ Scrittura **BILANCIATA**")
                        
                        # Export CSV
                        csv_data = f"Lato;Codice;Descrizione;Importo\nDARE;{cod_dare};{desc_dare};{imp_dare}\nAVERE;{cod_avere};{desc_avere};{imp_avere}"
                        
                        st.download_button(
                            label="📥 Scarica CSV",
                            data=csv_data,
                            file_name=f"scrittura_{datetime.now().strftime('%d%m%Y')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Scrittura **NON BILANCIATA** - Differenza: € {abs(imp_dare - imp_avere):,.2f}")

if __name__ == "__main__":
    main()
