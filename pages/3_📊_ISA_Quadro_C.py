import streamlit as st
import pdfplumber
import re
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="ISA - Compilazione Quadro C", layout="wide", page_icon="📊")

# MAPPATURA ISA - Database completo
ISA_MAPPING = {
    "DD02U": {
        "descrizione": "Produzione prodotti farinacei",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28"],
        "documenti": ["Bilancio", "Registro produzione", "Distinta vendite"],
        "note": "Percentuali produzione devono sommare 100%",
        "controlli": ["Verificare coerenza volumi produzione", "Controllare corrispondenza con vendite"]
    },
    "DG33U": {
        "descrizione": "Servizi estetici e benessere fisico",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14"],
        "documenti": ["Bilancio", "Listino tariffe", "Contratti franchising"],
        "note": "Includere costi franchisor se applicabile",
        "controlli": ["Verificare tariffe applicate", "Controllare costi franchising"]
    },
    "DG66U": {
        "descrizione": "Software house, IT, riparazione macchine ufficio",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26"],
        "documenti": ["Bilancio", "Contratti clienti", "Registro interventi"],
        "note": "Specificare numero contabilità/buste paga se applicabile",
        "controlli": ["Verificare numero contabilità elaborate", "Controllare buste paga elaborate"]
    },
    "DG76U": {
        "descrizione": "Ristorazione collettiva (catering, mense)",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"],
        "documenti": ["Bilancio", "Registro pasti erogati", "Contratti catering"],
        "note": "Indicare numero totale pasti erogati",
        "controlli": ["Verificare numero pasti erogati", "Controllare contratti attivi"]
    },
    "DG91U": {
        "descrizione": "Servizi finanziari e assicurativi",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51"],
        "documenti": ["Bilancio", "Portafoglio prodotti", "Registro polizze"],
        "note": "Distinguere impresa vs lavoro autonomo",
        "controlli": ["Verificare categoria reddituale", "Controllare portafoglio prodotti"]
    },
    "DM28U": {
        "descrizione": "Commercio tessuti, filati, merceria",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36"],
        "documenti": ["Bilancio", "Registro vendite", "Distinta prodotti"],
        "note": "Percentuali modalità vendita e tipologia offerta = 100%",
        "controlli": ["Verificare somme percentuali = 100%", "Controllare fascia qualitativa offerta"]
    },
    "DM80U": {
        "descrizione": "Commercio carburanti",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"],
        "documenti": ["Bilancio", "Registro erogazioni", "Dati aggio/ricavo fisso"],
        "note": "Separare dati aggio da ricavi ordinari",
        "controlli": ["Verificare separazione aggio/ricavi", "Controllare quantità erogate"]
    },
    "EG31U": {
        "descrizione": "Revisione/manutenzione autoveicoli",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19"],
        "documenti": ["Bilancio", "Registro controlli", "Distinta interventi"],
        "note": "Indicare numero controlli revisione effettuati",
        "controlli": ["Verificare numero revisioni", "Controllare spese terzi"]
    },
    "EG34U": {
        "descrizione": "Servizi acconciatura (parrucchieri)",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13"],
        "documenti": ["Bilancio", "Listino tariffe", "Contratti franchising"],
        "note": "Percentuali tipologia attività = 100%",
        "controlli": ["Verificare tariffe servizi", "Controllare consumi energia"]
    },
    "EG36U": {
        "descrizione": "Ristorazione commerciale",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28"],
        "documenti": ["Bilancio", "Registro pasti", "Distinta acquisti cibi/bevande"],
        "note": "Percentuali acquisti cibi/bevande = 100%",
        "controlli": ["Verificare acquisti cibi/bevande", "Controllare posti a sedere"]
    },
    "EG37U": {
        "descrizione": "Bar, gelateria, pasticceria",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34"],
        "documenti": ["Bilancio", "Registro consumi", "Listino prezzi"],
        "note": "Indicare consumo caffè (Kg) e energia (Kwh)",
        "controlli": ["Verificare consumo caffè", "Controllare energia elettrica"]
    },
    "EG40U": {
        "descrizione": "Locazione, valorizzazione, compravendita immobili",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
        "documenti": ["Bilancio", "Contratti locazione/vendita", "Dati catastali"],
        "note": "Localizzazione geografica immobili = 100%",
        "controlli": ["Verificare contratti attivi", "Controllare localizzazione immobili"]
    },
    "EG50U": {
        "descrizione": "Intonacatura, tinteggiatura, lavori completamento edifici",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47"],
        "documenti": ["Bilancio", "Fatture", "DURC", "Localizzazioni cantieri"],
        "note": "Specializzazione + localizzazione geografica = 100%",
        "controlli": ["Verificare DURC regolare", "Controllare localizzazione cantieri", "Verificare reverse charge"]
    },
    "EG61U": {
        "descrizione": "Intermediari commercio e servizi",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58"],
        "documenti": ["Bilancio", "Mandati", "Registro provvigioni"],
        "note": "Settori merceologici e area geografica = 100%",
        "controlli": ["Verificare mandati attivi", "Controllare provvigioni"]
    },
    "EG69U": {
        "descrizione": "Costruzioni edili",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53"],
        "documenti": ["Bilancio", "Fatture", "Cantieri", "DURC", "Localizzazioni geografiche"],
        "note": "Multiple percentuali devono sommare 100% (ambito, specializzazione, acquisizione, localizzazione)",
        "controlli": ["Verificare DURC regolare", "Controllare localizzazione cantieri", "Verificare reverse charge", "Controllare split payment"]
    },
    "EG75U": {
        "descrizione": "Installazione impianti elettrici, idraulici",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43"],
        "documenti": ["Bilancio", "Contratti", "Cantieri"],
        "note": "Specializzazione + area territoriale = 100%",
        "controlli": ["Verificare contratti attivi", "Controllare area territoriale"]
    },
    "EG99U": {
        "descrizione": "Altri servizi a imprese e famiglie",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09"],
        "documenti": ["Bilancio", "Contratti servizi"],
        "note": "Percentuali tipologia attività = 100%",
        "controlli": ["Verificare tipologia servizi", "Controllare contratti"]
    },
    "EK02U": {
        "descrizione": "Studi di ingegneria",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40"],
        "documenti": ["Bilancio", "Incarichi professionali"],
        "note": "Distinguere impresa vs lavoro autonomo",
        "controlli": ["Verificare categoria reddituale", "Controllare incarichi professionali"]
    },
    "EK19U": {
        "descrizione": "Attività paramediche",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20"],
        "documenti": ["Bilancio", "Prestazioni sanitarie"],
        "note": "Distinguere impresa vs lavoro autonomo",
        "controlli": ["Verificare categoria reddituale", "Controllare prestazioni"]
    },
    "EM01A": {
        "descrizione": "Commercio al dettaglio alimentare",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49"],
        "documenti": ["Bilancio", "Registro corrispettivi"],
        "note": "Separare dati aggio da ricavi ordinari",
        "controlli": ["Verificare superficie vendita", "Controllare tipologia esercizio"]
    },
    "EM05U": {
        "descrizione": "Commercio abbigliamento",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37"],
        "documenti": ["Bilancio", "Registro vendite", "Distinta prodotti"],
        "note": "Percentuali modalità vendita e prodotti = 100%",
        "controlli": ["Verificare fascia qualitativa", "Controllare modalità acquisto"]
    },
    "EM11U": {
        "descrizione": "Commercio ferramenta, termoidraulica, materiali da costruzione",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32"],
        "documenti": ["Bilancio", "Registro vendite"],
        "note": "Percentuali prodotti e tipologia vendita = 100%",
        "controlli": ["Verificare prodotti venduti", "Controllare tipologia vendita"]
    },
    "EM43U": {
        "descrizione": "Commercio macchine agricole e giardinaggio",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "documenti": ["Bilancio", "Registro vendite"],
        "note": "Percentuali tipologia vendita e offerta = 100%",
        "controlli": ["Verificare tipologia vendita", "Controllare offerta prodotti"]
    },
    "EM85U": {
        "descrizione": "Commercio prodotti tabacco",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12"],
        "documenti": ["Bilancio", "Dati aggio/ricavo fisso", "Registro vendite"],
        "note": "Separare dati aggio da ricavi ordinari",
        "controlli": ["Verificare aggio tabacchi", "Controllare proventi giochi"]
    },
    "FM87U": {
        "descrizione": "Commercio al dettaglio altri prodotti",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "documenti": ["Bilancio", "Registro corrispettivi", "Distinta settori merceologici"],
        "note": "Percentuali modalità vendita e settori merceologici = 100%",
        "controlli": ["Verificare settori merceologici", "Controllare modalità vendita"]
    }
}

st.title("📊 ISA - Compilazione Quadro C")
st.markdown("Carica il PDF delle istruzioni ISA per generare il prompt di compilazione")

# Upload file
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
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Settore", data.get('descrizione', 'N/A'))
                with col2:
                    st.metric("Campi Quadro C", len(data.get('campi', [])))
                with col3:
                    st.metric("Controlli richiesti", len(data.get('controlli', [])))
                
                # Documenti richiesti
                st.subheader("📎 Documenti Richiesti")
                for doc in data.get('documenti', []):
                    st.write(f"✓ {doc}")
                
                # Controlli di validazione
                st.subheader("⚠️ Controlli di Validazione Obbligatori")
                for controllo in data.get('controlli', []):
                    st.warning(f"🔍 {controllo}")
                
                # Note specifiche
                if data.get('note'):
                    st.info(f"📌 **Nota importante:** {data.get('note')}")
                
                # Campi da compilare
                st.subheader("📋 Campi del Quadro C da Compilare")
                st.write(", ".join(data.get('campi', [])))
                
                # Genera prompt
                fields_str = ", ".join(data.get('campi', []))
                docs_str = "\n".join([f"- {doc}" for doc in data.get('documenti', [])])
                controlli_str = "\n".join([f"□ {ctrl}" for ctrl in data.get('controlli', [])])
                note = data.get('note', '')
                desc = data.get('descrizione', '')
                
                prompt = f"""
================================================================================
                    COMPILAZIONE QUADRO C - ISA {isa_code}
                    {desc}
================================================================================

MODELLO ISA: {isa_code}
SETTORE: {desc}
DATA GENERAZIONE: {datetime.now().strftime('%d/%m/%Y %H:%M')}

================================================================================
                         DOCUMENTAZIONE RICHIESTA
================================================================================

{docs_str}

================================================================================
                         CAMPI QUADRO C DA COMPILARE
================================================================================

{fields_str}

TOTALE CAMPI: {len(data.get('campi', []))}

================================================================================
                      ISTRUZIONI COMPILAZIONE
================================================================================

Per CIASCUN CAMPO del Quadro C elencato sopra, fornire:

CAMPO: C##
VALORE: [inserire valore numerico o percentuale]
FONTE DOCUMENTALE: [es. Bilancio 2024 pag. X / Fattura n. Y]
DESCRIZIONE: [breve descrizione del dato]
NOTE: [eventuali criticità o osservazioni]
COERENZA: [coerente / da verificare / anomalo]

RIPETERE PER TUTTI I {len(data.get('campi', []))} CAMPI

================================================================================
                      CONTROLLI DI VALIDAZIONE
================================================================================

{controlli_str}

NOTE SPECIFICHE: {note}

IMPORTANTE: Le percentuali devono sommare esattamente 100% dove richiesto

================================================================================
                      GESTIONE DATI INCERTI O DUBBI
================================================================================

In caso di dati incerti, dubbi o non documentabili:

1. SEGNALARE ESPLICITAMENTE il campo interessato
2. INDICARE il motivo dell'incertezza (mancanza documentazione, dati 
   contraddittori, stime necessarie)
3. FORNIRE una stima motivata con indicazione del margine di errore
4. DOCUMENTARE ogni assunzione fatta
5. RICHIEDERE documentazione integrativa se necessaria

ESEMPIO SEGNAZIONE DATO INCERTO:

CAMPO: C15
STATO: DATO INCERTO - DA VERIFICARE
MOTIVO: Mancanza fatture fornitori per il mese di dicembre
STIMA: Euro 15.000 (margine errore +/- 10%)
AZIONE RICHIESTA: Richiedere estratto conto bancario dicembre

================================================================================
                      CHECKLIST PRE-INVIO
================================================================================

□ Tutti i campi obbligatori compilati
□ Documentazione a supporto disponibile per ogni valore
□ Percentuali sommano 100% dove richiesto
□ Coerenza interna verificata tra i vari campi
□ Dati congrui con il settore di attività
□ Eventuali anomalie giustificate e documentate
□ Dati incerti segnalati esplicitamente
□ Controlli di validazione effettuati
□ Reverse charge verificato (se applicabile)
□ DURC regolare (se applicabile)

================================================================================
                      OUTPUT FINALE RICHIESTO
================================================================================

Al termine della compilazione fornire:

1. TABELLA RIEPILOGATIVA con tutti i campi compilati
2. ANALISI DI COERENZA interna tra i vari campi
3. SEGNALAZIONE CRITICITÀ con indicazione priorità (alta/media/bassa)
4. ELENCO DOCUMENTI MANCANTI (se presenti)
5. CHECKLIST PRE-INVIO completata
6. NOTE OPERATIVE per il consulente

================================================================================
                      NOTE IMPORTANTI
================================================================================

- Utilizzare SOLO dati dalla documentazione allegata
- CITARE SEMPRE la fonte documentale per ogni campo
- SEGNALARE se un campo non può essere compilato per mancanza dati
- I quadri A, B, D, E, F, H sono gestiti separatamente dal consulente
- In caso di dubbi, richiedere chiarimenti prima di procedere

================================================================================
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
                
                # Sezione controlli aggiuntivi
                st.subheader("🔍 Controlli Aggiuntivi Raccomandati")
                st.markdown("""
**Prima di procedere con la compilazione definitiva:**

1. **Verificare congruenza ricavi** - Confrontare con anni precedenti
2. **Controllare coerenza costi** - Verificare percentuali rispetto ai ricavi
3. **Analizzare variazioni significative** - Giustificare scostamenti >10%
4. **Verificare documentazione** - Assicurarsi che ogni dato sia supportato
5. **Controllare adempimenti** - DURC, versamenti IVA, ritenute
                """)
                
            else:
                st.warning("⚠️ Nessun codice ISA riconosciuto nel PDF")
                if matches:
                    st.write(f"Codici trovati nel testo: {list(set(matches))[:10]}")
                    st.info("💡 Verificare che il codice ISA sia tra quelli supportati dal sistema")
                
        except Exception as e:
            st.error(f"❌ Errore durante l'analisi: {str(e)}")
            st.exception(e)
else:
    st.info("👆 Carica un PDF per iniziare")
    
    st.markdown("""
    ---
    ### Come utilizzare questa applicazione:
    
    1. **Carica il PDF** delle istruzioni ISA del modello da compilare
    2. **Attendi l'analisi** automatica del documento
    3. **Verifica i controlli** di validazione richiesti
    4. **Scarica il prompt** per guidare la compilazione
    
    **Modelli supportati:** DD02U, DG33U, DG66U, DG76U, DG91U, DM28U, DM80U, 
    EG31U, EG34U, EG36U, EG37U, EG40U, EG50U, EG61U, EG69U, EG75U, EG99U, 
    EK02U, EK19U, EM01A, EM05U, EM11U, EM43U, EM85U, FM87U
    """)
