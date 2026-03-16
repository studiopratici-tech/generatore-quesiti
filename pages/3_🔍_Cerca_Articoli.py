import streamlit as st
import os
import pdfplumber
from pathlib import Path
from datetime import datetime
import re

# Configurazione pagina
st.set_page_config(
    page_title="🔍 Q&A Banca Dati", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 ASSISTENTE INTELLIGENTE BANCA DATI")
st.markdown("*Inserisci un quesito e trova la risposta negli articoli esistenti*")
st.markdown("---")

# Percorso default cartella condivisa
PERCORSO_DEFAULT = "\\SERVER\public\Notizie Fiscali e Lavoro"

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurazione")
    
    percorso_cartella = st.text_input(
        "📁 Percorso cartella PDF",
        value=PERCORSO_DEFAULT,
        help="Cartella con gli articoli PDF"
    )
    
    st.markdown("---")
    
    modalità = st.radio(
        "Modalità risposta",
        ["Suggerisci articolo + sintesi", "Solo elenco articoli", "Risposta dettagliata"],
        help="Come vuoi la risposta"
    )
    
    max_articoli = st.slider(
        "Numero massimo articoli da analizzare",
        min_value=1,
        max_value=20,
        value=5
    )
    
    st.markdown("---")
    
    if st.button("🔄 Ricarica Indice", type="primary", use_container_width=True):
        if 'cache_articoli' in st.session_state:
            del st.session_state['cache_articoli']
        st.success("✅ Indice ricaricato!")
        st.rerun()

# Funzione estrazione testo PDF
@st.cache_data(show_spinner=False)
def estrai_testo_pdf(percorso_file):
    """Estrae testo completo da un file PDF"""
    try:
        testo_completo = ""
        with pdfplumber.open(percorso_file) as pdf:
            for pagina in pdf.pages:
                testo = pagina.extract_text()
                if testo:
                    testo_completo += testo + "\n"
        
        return {
            "testo": testo_completo,
            "pagine": len(pdf.pages),
            "errore": None
        }
    except Exception as e:
        return {
            "testo": "",
            "pagine": 0,
            "errore": str(e)
        }

# Funzione scansione cartella
@st.cache_data(show_spinner="🔍 Indicizzazione articoli in corso...")
def scansiona_cartella(percorso):
    """Scansiona la cartella e indicizza tutti i PDF"""
    articoli = []
    cartella = Path(percorso)
    
    if not cartella.exists():
        return None, "❌ Cartella non trovata! Verifica il percorso."
    
    pdf_files = list(cartella.glob("**/*.pdf"))
    
    if not pdf_files:
        return None, f"⚠️ Nessun file PDF trovato in {percorso}"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, pdf_file in enumerate(pdf_files):
        status_text.text(f"📄 {pdf_file.name} ({i+1}/{len(pdf_files)})")
        
        risultato = estrai_testo_pdf(pdf_file)
        nome_file = pdf_file.name
        data_modifica = datetime.fromtimestamp(pdf_file.stat().st_mtime)
        
        # Estrai parole chiave dal testo (prime 500 parole)
        testo_breve = risultato["testo"][:2000].lower()
        parole_chiave = re.findall(r'\b[a-zA-ZàèìòùÀÈÌÒÙ]{4,}\b', testo_breve)
        parole_frequenti = {}
        for parola in parole_chiave:
            if parola not in ["articolo", "comma", "legge", "decreto", "circolare", "agenzia", "entrate", "inps"]:
                parole_frequenti[parola] = parole_frequenti.get(parola, 0) + 1
        
        articoli.append({
            "nome": nome_file,
            "percorso": str(pdf_file),
            "percorso_relativo": str(pdf_file.relative_to(cartella)),
            "data_modifica": data_modifica.strftime("%Y-%m-%d"),
            "testo_completo": risultato["testo"],
            "testo_breve": testo_breve,
            "lunghezza": len(risultato["testo"]),
            "pagine": risultato["pagine"],
            "parole_chiave": dict(sorted(parole_frequenti.items(), key=lambda x: x[1], reverse=True)[:20]),
            "errore": risultato["errore"]
        })
        
        progress_bar.progress((i + 1) / len(pdf_files))
    
    status_text.empty()
    progress_bar.empty()
    
    return articoli, None

# Funzione per calcolare rilevanza articolo rispetto al quesito
def calcola_rilevanza(testo_articolo, quesito):
    """Calcola punteggio di rilevanza basato su parole chiave e contesto"""
    quesito_clean = quesito.lower()
    testo_clean = testo_articolo.lower()
    
    # Estrai parole significative dal quesito
    parole_quesito = [p.strip() for p in re.findall(r'\b[a-zA-ZàèìòùÀÈÌÒÙ]{4,}\b', quesito_clean) 
                      if p not in ["articolo", "comma", "legge", "decreto", "circolare", "agenzia", "entrate", "inps", "come", "cosa", "quando", "dove", "perché"]]
    
    if not parole_quesito:
        return 0
    
    punteggio = 0
    occorrenze = {}
    
    for parola in parole_quesito:
        count = testo_clean.count(parola)
        occorrenze[parola] = count
        # Punteggio pesato: più parole trovate = più rilevante
        punteggio += count * (10 if len(parola) > 6 else 5)
    
    # Bonus se il quesito appare come frase nel testo
    if quesito_clean in testo_clean:
        punteggio += 50
    
    # Bonus se parole chiave consecutive appaiono vicine
    for i in range(len(parole_quesito) - 1):
        if f"{parole_quesito[i]} {parole_quesito[i+1]}" in testo_clean:
            punteggio += 20
    
    return punteggio, occorrenze

# Funzione per estrarre snippet pertinente
def estrai_snippet_pertinente(testo, quesito, lunghezza=400):
    """Estrae il paragrafo più pertinente alla domanda"""
    testo_lower = testo.lower()
    quesito_lower = quesito.lower()
    
    # Trova la posizione della prima parola chiave del quesito
    parole_chiave = [p for p in re.findall(r'\b[a-zA-ZàèìòùÀÈÌÒÙ]{4,}\b', quesito_lower) 
                     if len(p) > 4 and p not in ["articolo", "comma", "legge", "decreto"]]
    
    if not parole_chiave:
        return testo[:lunghezza] + "..."
    
    # Cerca il contesto migliore
    miglior_pos = -1
    miglior_punteggio = 0
    
    for parola in parole_chiave[:5]:  # Prime 5 parole chiave
        idx = testo_lower.find(parola)
        if idx != -1:
            # Conta quante parole chiave sono vicine a questa posizione
            contesto_start = max(0, idx - 200)
            contesto_end = min(len(testo), idx + 200)
            contesto = testo_lower[contesto_start:contesto_end]
            
            punteggio_locale = sum(1 for pk in parole_chiave if pk in contesto)
            
            if punteggio_locale > miglior_punteggio:
                miglior_punteggio = punteggio_locale
                miglior_pos = idx
    
    if miglior_pos != -1:
        start = max(0, miglior_pos - 200)
        end = min(len(testo), miglior_pos + lunghezza)
        return testo[start:end].strip() + "..."
    
    return testo[:lunghezza] + "..."

# Funzione per generare risposta sintetica basata sull'articolo
def genera_sintesi_risposta(articolo, quesito):
    """Genera una breve sintesi della risposta basata sul contenuto dell'articolo"""
    testo = articolo["testo_completo"]
    
    # Cerca frasi che potrebbero contenere la risposta
    frasi_rilevanti = []
    
    # Pattern per trovare affermazioni normative
    pattern_norma = r'[^.!?]*?(?:deve|obbligo|è necessario|si applica|ai sensi|secondo|in base a)[^.!?]*?[.!?]'
    matches = re.findall(pattern_norma, testo, re.IGNORECASE)
    
    for match in matches[:5]:  # Prime 5 frasi normative
        if any(parola in match.lower() for parola in quesito.lower().split() if len(parola) > 4):
            frasi_rilevanti.append(match.strip())
    
    if frasi_rilevanti:
        return "• " + "\n• ".join(frasi_rilevanti[:3])
    
    # Fallback: estrai primo paragrafo pertinente
    snippet = estrai_snippet_pertinente(testo, quesito, lunghezza=300)
    return snippet.replace('\n', ' ')

# Campo di ricerca principale
quesito = st.text_area(
    "❓ Inserisci il tuo quesito o argomento",
    placeholder="Es: Come si collega il POS al registratore di cassa dal 2026?\nOppure: Quali sono gli obblighi per la trasmissione telematica dei corrispettivi?",
    height=100
)

# Mostra info cartella
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📁 Cartella", "Configurata" if percorso_cartella else "Non impostata")
with col2:
    if 'cache_articoli' in st.session_state:
        st.metric("📄 Articoli indicizzati", len(st.session_state.cache_articoli))
    else:
        st.metric("📄 Articoli indicizzati", "0")
with col3:
    st.metric("🔍 Modalità", modalità)

# Bottone cerca
if st.button("🚀 CERCA RISPOSTA", type="primary", use_container_width=True):
    if not quesito:
        st.warning("⚠️ Inserisci almeno un quesito da cercare!")
    else:
        with st.spinner("🔍 Analisi banca dati in corso..."):
            # Scansiona cartella
            if 'cache_articoli' not in st.session_state:
                articoli, errore = scansiona_cartella(percorso_cartella)
                if errore:
                    st.error(errore)
                    st.stop()
                st.session_state.cache_articoli = articoli
            else:
                articoli = st.session_state.cache_articoli
            
            if not articoli:
                st.error("Nessun articolo trovato nella cartella!")
            else:
                # Calcola rilevanza per ogni articolo
                risultati = []
                
                for articolo in articoli:
                    if articolo["errore"]:
                        continue
                    
                    punteggio, occorrenze = calcola_rilevanza(articolo["testo_breve"], quesito)
                    
                    if punteggio > 0:
                        risultati.append({
                            **articolo,
                            "punteggio": punteggio,
                            "occorrenze": occorrenze,
                            "snippet": estrai_snippet_pertinente(articolo["testo_completo"], quesito),
                            "sintesi": genera_sintesi_risposta(articolo, quesito)
                        })
                
                # Ordina per rilevanza
                risultati.sort(key=lambda x: x["punteggio"], reverse=True)
                risultati = risultati[:max_articoli]
                
                # Mostra risultati
                if risultati:
                    st.success(f"✅ Trovati **{len(risultati)}** articoli pertinenti!")
                    
                    # 🏆 ARTICOLO MIGLIORE (in evidenza)
                    migliore = risultati[0]
                    st.markdown("### 🏆 ARTICOLO CONSIGLIATO")
                    
                    with st.expander(f"📄 **{migliore['nome']}** (Punteggio: {migliore['punteggio']})", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**📅 Data:** {migliore['data_modifica']}")
                            st.markdown(f"**📄 Pagine:** {migliore['pagine']}")
                            st.markdown(f"**📏 Lunghezza:** {migliore['lunghezza']} caratteri")
                        with col2:
                            st.markdown("**🔑 Parole chiave trovate:**")
                            for parola, count in list(migliore['occorrenze'].items())[:5]:
                                st.text(f"  • '{parola}': {count} occorrenze")
                        
                        st.markdown("---")
                        
                        if modalità == "Risposta dettagliata":
                            st.markdown("**💡 Risposta basata sull'articolo:**")
                            st.info(migliore["sintesi"])
                        
                        st.markdown("**📖 Anteprima contenuto pertinente:**")
                        st.markdown(f"> {migliore['snippet']}")
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📍 Percorso:**")
                            st.code(migliore['percorso_relativo'], language="text")
                        with col2:
                            if st.button("📂 Apri file", key="apri_migliore", use_container_width=True):
                                try:
                                    os.startfile(migliore['percorso'])
                                except:
                                    st.error("Impossibile aprire. Copia il percorso e apri manualmente.")
                    
                    # 📋 ALTRI ARTICOLI PERTINENTI
                    if len(risultati) > 1:
                        st.markdown("### 📋 Altri articoli pertinenti")
                        
                        for i, risultato in enumerate(risultati[1:], 2):
                            with st.expander(f"📄 {risultato['nome']} (Punteggio: {risultato['punteggio']})", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**📅 Data:** {risultato['data_modifica']}")
                                    st.markdown(f"**📄 Pagine:** {risultato['pagine']}")
                                with col2:
                                    st.markdown("**🔑 Parole chiave:**")
                                    for parola, count in list(risultato['occorrenze'].items())[:3]:
                                        st.text(f"  • '{parola}': {count}")
                                
                                if modalità in ["Suggerisci articolo + sintesi", "Risposta dettagliata"]:
                                    st.markdown("---")
                                    st.markdown("**💡 Sintesi:**")
                                    st.markdown(risultato["sintesi"])
                                
                                st.markdown("---")
                                st.markdown(f"**📍 Percorso:** `{risultato['percorso_relativo']}`")
                                
                                if st.button(f"📂 Apri", key=f"apri_{i}"):
                                    try:
                                        os.startfile(risultato['percorso'])
                                    except:
                                        st.info("Copia il percorso e apri manualmente")
                
                else:
                    st.warning("⚠️ Nessun articolo pertinente trovato.")
                    st.info("💡 Suggerimenti:\n- Prova con parole chiave più specifiche\n- Verifica che gli articoli nella cartella trattino l'argomento\n- Controlla il percorso della cartella")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 <b>Assistente Intelligente Banca Dati</b> | Analisi semantica PDF</p>
    <p>Supporta: quesiti normativi, procedurali, fiscali, lavorativi</p>
</div>
""", unsafe_allow_html=True)
