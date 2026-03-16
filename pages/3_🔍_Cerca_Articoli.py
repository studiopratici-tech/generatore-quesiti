import streamlit as st
import os
import pdfplumber
from pathlib import Path
import re
import sqlite3
import json
from datetime import datetime
import subprocess
import platform

st.set_page_config(
    page_title="Cerca Articoli", 
    page_icon="📚", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("RICERCA ARTICOLI BANCA DATI")
st.markdown("*Banca dati indicizzata - Ricerca veloce*")
st.markdown("---")

# Percorso - UNITÀ DI RETE Z:
PERCORSO_DEFAULT = r"Z:"
DB_FILE = "indice_articoli.db"

# Sidebar
with st.sidebar:
    st.header("Configurazione")
    percorso = st.text_input("Percorso cartella", value=PERCORSO_DEFAULT)
    
    st.markdown("---")
    
    # Test percorso
    if st.button("Testa Percorso", use_container_width=True):
        if Path(percorso).exists():
            st.success("Cartella accessibile!")
            pdf_count = len(list(Path(percorso).glob("**/*.pdf")))
            st.info(f"PDF trovati: {pdf_count}")
        else:
            st.error("Cartella NON accessibile!")
            st.warning("Verifica che l'unità Z: sia mappata correttamente")
    
    st.markdown("---")
    
    # Info indice
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articoli")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT MAX(data_index) FROM articoli")
            last = cursor.fetchone()[0]
            conn.close()
            st.success(f"**Indice attivo:** {count} articoli")
            st.info(f"Ultimo aggiornamento: {last or 'N/A'}")
        except Exception as e:
            st.warning(f"Indice danneggiato: {str(e)}")
    else:
        st.warning("Nessun indice. Verrà creato alla prima ricerca.")
    
    st.markdown("---")
    
    if st.button("Ricostruisci Indice", type="primary", use_container_width=True):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.success("Indice cancellato! Ricrea alla prossima ricerca.")
            st.rerun()
    
    max_risultati = st.slider("Risultati max", 5, 50, 20)

# Funzione crea database
def crea_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articoli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            percorso TEXT UNIQUE,
            nome TEXT,
            data_modifica TEXT,
            dimensione INTEGER,
            testo TEXT,
            parole_chiave TEXT,
            data_index TEXT
        )
    ''')
    conn.commit()
    return conn

# Funzione estrai testo PDF
def estrai_testo(percorso):
    try:
        testo = ""
        with pdfplumber.open(percorso) as pdf:
            for pagina in pdf.pages[:5]:
                t = pagina.extract_text()
                if t:
                    testo += t + " "
        return testo[:30000]
    except Exception as e:
        return ""

# Funzione aggiorna indice
def aggiorna_indice(conn, percorso_cartella):
    cursor = conn.cursor()
    cartella = Path(percorso_cartella)
    
    if not cartella.exists():
        return 0, "Cartella non trovata"
    
    pdf_files = list(cartella.glob("**/*.pdf"))
    if not pdf_files:
        return 0, "Nessun PDF trovato"
    
    nuovi = 0
    aggiornati = 0
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    for i, pdf in enumerate(pdf_files):
        status.text(f"{pdf.name} ({i+1}/{len(pdf_files)})")
        
        data_mod = datetime.fromtimestamp(pdf.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        dimensione = pdf.stat().st_size
        
        cursor.execute("SELECT data_modifica, dimensione FROM articoli WHERE percorso=?", (str(pdf),))
        esistente = cursor.fetchone()
        
        deve_indicizzare = False
        
        if not esistente:
            deve_indicizzare = True
            nuovi += 1
        elif esistente[0] != data_mod or esistente[1] != dimensione:
            deve_indicizzare = True
            aggiornati += 1
            cursor.execute("DELETE FROM articoli WHERE percorso=?", (str(pdf),))
        
        if deve_indicizzare:
            testo = estrai_testo(str(pdf))
            if testo:
                parole = re.findall(r'\b[a-zA-Zàèìòù]{5,}\b', testo.lower())
                stop = {"articolo", "comma", "legge", "decreto", "circolare", "agenzia", "entrate", "inps", "come", "cosa", "quando", "dove", "perché", "che", "del", "della", "sono", "una", "uno", "con", "per", "tra", "fra"}
                parole_filtrate = [p for p in parole if p not in stop]
                frequenze = {}
                for p in parole_filtrate:
                    frequenze[p] = frequenze.get(p, 0) + 1
                top_parole = dict(sorted(frequenze.items(), key=lambda x: x[1], reverse=True)[:30])
                
                cursor.execute('''
                    INSERT INTO articoli (percorso, nome, data_modifica, dimensione, testo, parole_chiave, data_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (str(pdf), pdf.name, data_mod, dimensione, testo, json.dumps(top_parole), datetime.now().strftime("%Y-%m-%d %H:%M")))
        
        progress_bar.progress((i+1)/len(pdf_files))
    
    conn.commit()
    status.empty()
    progress_bar.empty()
    
    return nuovi + aggiornati, None

# Funzione cerca
def cerca(conn, query, max_risultati=20):
    cursor = conn.cursor()
    parole = [p.lower() for p in re.findall(r'\b[a-zA-Zàèìòù]{4,}\b', query) 
              if p.lower() not in {"articolo", "comma", "legge", "decreto", "circolare", "agenzia", "entrate", "inps", "come", "cosa"}]
    
    if not parole:
        return []
    
    cursor.execute("SELECT id, nome, percorso, data_modifica, dimensione, testo, parole_chiave FROM articoli")
    articoli = cursor.fetchall()
    
    risultati = []
    for art in articoli:
        id_art, nome, percorso, data_mod, dimensione, testo, parole_json = art
        punteggio = 0
        testo_lower = testo.lower() if testo else ""
        nome_lower = nome.lower()
        
        for parola in parole:
            count = testo_lower.count(parola)
            if nome_lower.count(parola) > 0:
                punteggio += 10
            punteggio += count
        
        if punteggio > 0:
            snippet = ""
            for parola in parole[:3]:
                if parola in testo_lower:
                    idx = testo_lower.find(parola)
                    start = max(0, idx-200)
                    end = min(len(testo), idx+400)
                    snippet = testo[start:end].strip()
                    break
            
            for parola in parole:
                snippet = re.sub(f"({parola})", f"**\\1**", snippet, flags=re.IGNORECASE)
            
            risultati.append({
                "nome": nome,
                "percorso": percorso,
                "data_modifica": data_mod,
                "dimensione": round(dimensione/1024, 2),
                "punteggio": punteggio,
                "snippet": snippet + "..." if snippet else ""
            })
    
    risultati.sort(key=lambda x: x["punteggio"], reverse=True)
    return risultati[:max_risultati]

# Funzione per aprire file (OTTIMIZZATA PER UNITÀ Z:)
def apri_file(percorso):
    """Apre un file dall'unità Z: con gestione errori"""
    try:
        # Converti percorso UNC in Z: se necessario
        if percorso.startswith("\\\\SERVER\\public\\Notizie Fiscali e Lavoro"):
            percorso = percorso.replace("\\\\SERVER\\public\\Notizie Fiscali e Lavoro", "Z:")
        
        if not os.path.exists(percorso):
            return False, f"File non trovato: {percorso}"
        
        # Prova ad aprire con os.startfile (ora dovrebbe funzionare con Z:)
        os.startfile(percorso)
        return True, "File aperto con successo!"
                    
    except Exception as e:
        return False, f"Errore apertura: {str(e)}"

# Campo ricerca
query = st.text_input("Cosa cerchi?", placeholder="Es: collegamento POS registratore 2026")

if st.button("CERCA", type="primary"):
    if not query:
        st.warning("Inserisci almeno una parola!")
    else:
        with st.spinner("Ricerca in corso..."):
            conn = crea_db()
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articoli")
            count = cursor.fetchone()[0]
            
            if count == 0:
                st.info("Prima ricerca: Creazione indice in corso (può richiedere 10-30 minuti)...")
                tot, errore = aggiorna_indice(conn, percorso)
                if errore:
                    st.error(errore)
                    st.stop()
                st.success(f"Indice creato! {tot} articoli indicizzati.")
                st.info("Le prossime ricerche saranno velocissime (2-5 secondi)!")
            
            risultati = cerca(conn, query, max_risultati)
            
            if not risultati:
                st.warning("Nessun risultato trovato")
            else:
                st.success(f"Trovati **{len(risultati)}** articoli!")
                
                migliore = risultati[0]
                st.markdown("### Articolo Consigliato")
                
                with st.expander(f"**{migliore['nome']}** (Punteggio: {migliore['punteggio']})", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Data:** {migliore['data_modifica']}")
                        st.markdown(f"**Dimensione:** {migliore['dimensione']} KB")
                    with col2:
                        st.markdown(f"**Percorso:**")
                        st.code(migliore['percorso'], language="text")
                    
                    st.markdown("---")
                    st.markdown("**Anteprima:**")
                    st.markdown(f"> {migliore['snippet']}")
                    
                    st.markdown("---")
                    st.markdown("**Apri file:**")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📂 APRI FILE", key="apri_migliore", type="primary", use_container_width=True):
                            successo, messaggio = apri_file(migliore['percorso'])
                            if successo:
                                st.balloons()
                                st.success(messaggio)
                            else:
                                st.error(messaggio)
                    with col_b:
                        st.info("💡 Se non si apre, copia il percorso e incolla in Esplora File")
                
                if len(risultati) > 1:
                    st.markdown("### Altri risultati")
                    for i, r in enumerate(risultati[1:], 2):
                        with st.expander(f"**{r['nome']}** (Punteggio: {r['punteggio']})", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Data:** {r['data_modifica']}")
                                st.markdown(f"**Dimensione:** {r['dimensione']} KB")
                            with col2:
                                st.markdown(f"**Percorso:**")
                                st.code(r['percorso'], language="text")
                            
                            st.markdown("---")
                            st.markdown(f"**Anteprima:** {r['snippet']}")
                            
                            st.markdown("---")
                            if st.button(f"📂 Apri", key=f"apri_{i}", use_container_width=True):
                                successo, messaggio = apri_file(r['percorso'])
                                if successo:
                                    st.balloons()
                                    st.success(messaggio)
                                else:
                                    st.error(messaggio)
            
            conn.close()

st.markdown("---")
st.markdown("*Ricerca con indice database - Unità Z: mappata*")
