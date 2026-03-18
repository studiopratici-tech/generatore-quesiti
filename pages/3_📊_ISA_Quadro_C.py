import streamlit as st
import pdfplumber
import re
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="ISA - Compilazione Quadro C", layout="wide")

# MAPPATURA ISA DIRETTAMENTE NEL CODICE (NESSUN JSON!)
ISA_MAPPING = {
    "DD02U": {
        "descrizione": "Produzione prodotti farinacei",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28"],
        "documenti_richiesti": ["Bilancio", "Registro produzione", "Distinta vendite"],
        "note": "Percentuali produzione devono sommare 100%"
    },
    "DG33U": {
        "descrizione": "Servizi estetici e benessere fisico",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14"],
        "documenti_richiesti": ["Bilancio", "Listino tariffe", "Contratti franchising"],
        "note": "Includere costi franchisor se applicabile"
    },
    "DG66U": {
        "descrizione": "Software house, IT, riparazione macchine ufficio",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26"],
        "documenti_richiesti": ["Bilancio", "Contratti clienti", "Registro interventi"],
        "note": "Specificare numero contabilità/buste paga se applicabile"
    },
    "DG76U": {
        "descrizione": "Ristorazione collettiva catering, mense",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"],
        "documenti_richiesti": ["Bilancio", "Registro pasti erogati", "Contratti catering"],
        "note": "Indicare numero totale pasti erogati"
    },
    "DG91U": {
        "descrizione": "Servizi finanziari e assicurativi",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51"],
        "documenti_richiesti": ["Bilancio", "Portafoglio prodotti", "Registro polizze"],
        "note": "Distinguere impresa vs lavoro autonomo"
    },
    "DM28U": {
        "descrizione": "Commercio tessuti, filati, merceria",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36"],
        "documenti_richiesti": ["Bilancio", "Registro vendite", "Distinta prodotti"],
        "note": "Percentuali modalità vendita e tipologia offerta 100%"
    },
    "DM80U": {
        "descrizione": "Commercio carburanti",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"],
        "documenti_richiesti": ["Bilancio", "Registro erogazioni", "Dati aggio/ricavo fisso"],
        "note": "Separare dati aggio da ricavi ordinari"
    },
    "EG31U": {
        "descrizione": "Revisione/manutenzione autoveicoli",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19"],
        "documenti_richiesti": ["Bilancio", "Registro controlli", "Distinta interventi"],
        "note": "Indicare numero controlli revisione effettuati"
    },
    "EG34U": {
        "descrizione": "Servizi acconciatura parrucchieri",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13"],
        "documenti_richiesti": ["Bilancio", "Listino tariffe", "Contratti franchising"],
        "note": "Percentuali tipologia attività 100%"
    },
    "EG36U": {
        "descrizione": "Ristorazione commerciale",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28"],
        "documenti_richiesti": ["Bilancio", "Registro pasti", "Distinta acquisti cibi/bevande"],
        "note": "Percentuali acquisti cibi/bevande 100%"
    },
    "EG37U": {
        "descrizione": "Bar, gelateria, pasticceria",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34"],
        "documenti_richiesti": ["Bilancio", "Registro consumi", "Listino prezzi"],
        "note": "Indicare consumo caffè Kg e energia Kwh"
    },
    "EG40U": {
        "descrizione": "Locazione, valorizzazione, compravendita immobili",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
        "documenti_richiesti": ["Bilancio", "Contratti locazione/vendita", "Dati catastali"],
        "note": "Localizzazione geografica immobili 100%"
    },
    "EG50U": {
        "descrizione": "Intonacatura, tinteggiatura, lavori completamento edifici",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47"],
        "documenti_richiesti": ["Bilancio", "Fatture", "DURC", "Localizzazioni cantieri"],
        "note": "Specializzazione localizzazione geografica 100%"
    },
    "EG61U": {
        "descrizione": "Intermediari commercio e servizi",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58"],
        "documenti_richiesti": ["Bilancio", "Mandati", "Registro provvigioni"],
        "note": "Settori merceologici e area geografica 100%"
    },
    "EG69U": {
        "descrizione": "Costruzioni edili",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53"],
        "documenti_richiesti": ["Bilancio", "Fatture", "Cantieri", "DURC", "Localizzazioni geografiche"],
        "note": "Multiple percentuali devono sommare 100%"
    },
    "EG75U": {
        "descrizione": "Installazione impianti elettrici, idraulici",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43"],
        "documenti_richiesti": ["Bilancio", "Contratti", "Cantieri"],
        "note": "Specializzazione area territoriale 100%"
    },
    "EG99U": {
        "descrizione": "Altri servizi a imprese e famiglie",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09"],
        "documenti_richiesti": ["Bilancio", "Contratti servizi"],
        "note": "Percentuali tipologia attività 100%"
    },
    "EK02U": {
        "descrizione": "Studi di ingegneria",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40"],
        "documenti_richiesti": ["Bilancio", "Incarichi professionali"],
        "note": "Distinguere impresa vs lavoro autonomo"
    },
    "EK19U": {
        "descrizione": "Attività professionali paramediche",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20"],
        "documenti_richiesti": ["Bilancio", "Prestazioni sanitarie"],
        "note": "Distinguere impresa vs lavoro autonomo"
    },
    "EM01A": {
        "descrizione": "Commercio al dettaglio alimentare",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49"],
        "documenti_richiesti": ["Bilancio", "Registro corrispettivi"],
        "note": "Separare dati aggio da ricavi ordinari"
    },
    "EM05U": {
        "descrizione": "Commercio abbigliamento",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37"],
        "documenti_richiesti": ["Bilancio", "Registro vendite", "Distinta prodotti"],
        "note": "Percentuali modalità vendita e prodotti 100%"
    },
    "EM11U": {
        "descrizione": "Commercio ferramenta, termoidraulica, materiali da costruzione",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32"],
        "documenti_richiesti": ["Bilancio", "Registro vendite"],
        "note": "Percentuali prodotti e tipologia vendita 100%"
    },
    "EM43U": {
        "descrizione": "Commercio macchine agricole e giardinaggio",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "documenti_richiesti": ["Bilancio", "Registro vendite"],
        "note": "Percentuali tipologia vendita e offerta 100%"
    },
    "EM85U": {
        "descrizione": "Commercio prodotti tabacco",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12"],
        "documenti_richiesti": ["Bilancio", "Dati aggio/ricavo fisso", "Registro vendite"],
        "note": "Separare dati aggio da ricavi ordinari"
    },
    "FM87U": {
        "descrizione": "Commercio al dettaglio altri prodotti",
        "quadro_c": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "documenti_richiesti": ["Bilancio", "Registro corrispettivi", "Distinta settori merceologici"],
        "note": "Percentuali modalità vendita e settori merceologici 100%"
    }
}

st.title("📊 ISA - Compilazione Quadro C")
st.markdown("Carica il PDF delle istruzioni ISA per generare il prompt di compilazione")

uploaded_file = st.file_uploader("📄 Carica PDF istruzioni ISA", type=['pdf'])

if uploaded_file is not None:
    with st.spinner('🔍 Analisi del PDF in corso...'):
        try:
            # Estrai testo
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            text_content = ""
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages[:5]:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
            
            os.unlink(tmp_path)
            
            # Trova codice ISA
            pattern = r'\b([A-Z]{2}\d{2,3}[A-Z])\b'
            matches = re.findall(pattern, text_content)
            
            isa_code = None
            for match in matches:
                if match in ISA_MAPPING:
                    isa_code = match
                    break
            
            if isa_code:
                st.success(f"✅ Codice ISA rilevato: **{isa_code}**")
                
                data = ISA_MAPPING[isa_code]
                
                # Mostra info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Settore", data.get('descrizione', 'N/A'))
                with col2:
                    st.metric("Campi Quadro C", len(data.get('quadro_c', [])))
                
                st.write("**📋 Campi da compilare:**")
                st.write(", ".join(data.get('quadro_c', [])))
                
                st.write("**📎 Documenti richiesti:**")
                for doc in data.get('documenti_richiesti', []):
                    st.write(f"📄 {doc}")
                
                # Genera prompt
                fields_str = ", ".join(data.get('quadro_c', []))
                docs_str = "\n".join([f"📄 {doc}" for doc in data.get('documenti_richiesti', [])])
                note = data.get('note', '')
                desc = data.get('descrizione', '')
                
                prompt = f"""
╔══════════════════════════════════════════════════════════════╗
║         COMPILAZIONE QUADRO C - ISA {isa_code}                  ║
║         {desc}
╚══════════════════════════════════════════════════════════════╝

📌 MODELLO ISA: {isa_code}
📋 SETTORE: {desc}

⚠️ **ATTENZIONE**

Questo prompt riguarda **ESCLUSIVAMENTE la compilazione del Quadro C**.

❌ **NON** fornire dati da altri quadri (A, B, D, E, F, H)
❌ **NON** inventare valori
❌ **NON** procedere senza documentazione

✅ **DEVI** fornire SOLO i dati del Quadro C
✅ **DEVI** avere documentazione a supporto
✅ **DEVI** essere preciso nei valori

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 **DOCUMENTI DA ALLEGARE (PDF)**:

{docs_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **CAMPI DEL QUADRO C DA COMPILARE**:

{fields_str}

**TOTALE CAMPI: {len(data.get('quadro_c', []))}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️ **ISTRUZIONI PER LA COMPILAZIONE**:

Per **CIASCUN CAMPO** del Quadro C, fornisci:

┌─────────────────────────────────────────────────────┐
│ CAMPO: C##                                           │
│ VALORE: [inserire valore numerico]                  │
│ FONTE DOCUMENTALE: [es. Bilancio 2024 pag. X]      │
│ DESCRIZIONE: [breve descrizione]                    │
│ NOTE: [eventuali criticità]                         │
│ COERENZA: [✓ coerente / ⚠️ da verificare]         │
└─────────────────────────────────────────────────────┘

**RIPETERE PER TUTTI I {len(data.get('quadro_c', []))} CAMPI**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **REGOLE SPECIFICHE PER {isa_code}**:

{note}

**IMPORTANTE**: Le percentuali devono sommare **100%** dove richiesto.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **CONTROLLI DI COERENZA**:

□ Tutte le percentuali sommano 100%
□ I valori sono coerenti con la documentazione
□ Non ci sono duplicazioni
□ I dati sono congrui con il settore
□ Eventuali anomalie sono giustificate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **OUTPUT FINALE RICHIESTO**:

1. **TABELLA RIEPILOGATIVA** con tutti i campi compilati
2. **ANALISI DI COERENZA** interna
3. **SEGNALAZIONE CRITICITÀ** o valori anomali
4. **CHECKLIST PRE-INVIO** completata

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **NOTE IMPORTANTI**:

- Utilizza **SOLO** i dati dalla documentazione allegata
- **CITA SEMPRE** la fonte documentale
- **SEGNALA** se un campo non può essere compilato
- I quadri A, B, D, E, F, H sono gestiti dal consulente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **PROCEDI CON L'ANALISI DEI DOCUMENTI E LA COMPILAZIONE**.

══════════════════════════════════════════════════════════════
"""
                
                st.subheader("🤖 Prompt Generato")
                st.code(prompt, language='text')
                
                st.download_button(
                    label="📥 Scarica Prompt (.txt)",
                    data=prompt,
                    file_name=f"prompt_{isa_code}_quadro_c.txt",
                    mime="text/plain",
                    type="primary"
                )
            else:
                st.warning("⚠️ Nessun codice ISA riconosciuto nel PDF")
                st.write(f"Codici trovati: {list(set(matches))[:10]}")
                
        except Exception as e:
            st.error(f"❌ Errore: {e}")
            st.exception(e)
else:
    st.info("👆 Carica un PDF per iniziare")
