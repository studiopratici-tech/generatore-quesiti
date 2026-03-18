import streamlit as st
import pdfplumber
import re
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="ISA - Compilazione Quadro C", layout="wide", page_icon="📊")

ISA_MAPPING = {
    "DD02U": {
        "descrizione": "Produzione prodotti farinacei",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28"],
        "documenti": ["Bilancio", "Registro produzione", "Distinta vendite"],
        "controlli": [
            "Verificare che C01-C07 (tipologia clientela) sommino 100%",
            "Verificare che C08-C26 (prodotti ottenuti) sommino 100%",
            "Verificare che C27-C28 (vendite scontrini/fatture) sommino 100%",
            "Controllare coerenza tra produzione dichiarata e vendite"
        ]
    },
    "DG33U": {
        "descrizione": "Servizi estetici e benessere fisico",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14"],
        "documenti": ["Bilancio", "Listino tariffe", "Contratti franchising"],
        "controlli": [
            "Verificare che C01-C11 (tipologia attività) sommino 100%",
            "Controllare se C12 (franchising) è compilato e verificare contratto",
            "Verificare coerenza C13 (costi franchisor) con C12",
            "Controllare che C14 (ricavi postazioni) sia coerente con numero operatori"
        ]
    },
    "DG66U": {
        "descrizione": "Software house, IT, riparazione macchine ufficio",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26"],
        "documenti": ["Bilancio", "Contratti clienti", "Registro interventi"],
        "controlli": [
            "Verificare che C01-C21 (attività svolta) sommino 100%",
            "Se C22 > 30%, verificare concentrazione committente principale",
            "Se C23 compilato, verificare numero contabilità elaborate",
            "Se C24 compilato, verificare numero buste paga elaborate",
            "Controllare coerenza C25 (interventi su segnalazione terzi) con fatture"
        ]
    },
    "DG76U": {
        "descrizione": "Ristorazione collettiva (catering, mense)",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"],
        "documenti": ["Bilancio", "Registro pasti erogati", "Contratti catering"],
        "controlli": [
            "Verificare che C01-C09 (tipologia attività) sommino 100%",
            "Verificare coerenza C10 (numero pasti) con contratti e fatture",
            "Controllare che numero pasti sia coerente con ricavi dichiarati"
        ]
    },
    "DG91U": {
        "descrizione": "Servizi finanziari e assicurativi",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51"],
        "documenti": ["Bilancio", "Portafoglio prodotti", "Registro polizze"],
        "controlli": [
            "Verificare categoria reddituale (impresa vs lavoro autonomo)",
            "Verificare che C02 + C06-C15 sommino 100%",
            "Se C16-C19 compilati, verificare che sommino 100%",
            "Verificare coerenza C20 (compagnie mandanti) con contratti",
            "Verificare coerenza C21 (numero polizze) con registro"
        ]
    },
    "DM28U": {
        "descrizione": "Commercio tessuti, filati, merceria",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36"],
        "documenti": ["Bilancio", "Registro vendite", "Distinta prodotti"],
        "controlli": [
            "Verificare che C01-C08 (modalità vendita) sommino 100%",
            "Verificare che C12-C29 (tipologia offerta) sommino 100%",
            "Verificare che C30-C33 (fascia qualitativa) sommino 100%",
            "Se C34 compilato (franchising), verificare contratto",
            "Se C35 compilato (gruppo acquisto), verificare documentazione",
            "Verificare coerenza C36 (costi franchisor) con C34"
        ]
    },
    "DM80U": {
        "descrizione": "Commercio carburanti",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"],
        "documenti": ["Bilancio", "Registro erogazioni", "Dati aggio/ricavo fisso"],
        "controlli": [
            "Verificare separazione C01-C05 (aggio) da altri ricavi",
            "Verificare coerenza C06-C11 (quantità erogate) con registro",
            "Verificare che C12-C17 (tipologia attività) sommino 100%",
            "Controllare coerenza C18 (deduzione forfetaria) con normativa"
        ]
    },
    "EG31U": {
        "descrizione": "Revisione/manutenzione autoveicoli",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19"],
        "documenti": ["Bilancio", "Registro controlli", "Distinta interventi"],
        "controlli": [
            "Verificare che C01-C08 (tipologia attività) sommino 100%",
            "Verificare che C09-C12 (tipologia veicolo) sommino 100%",
            "Verificare coerenza C15-C17 (spese terzi) con fatture",
            "Verificare coerenza C18 (acquisto oli/lubrificanti) con fatture",
            "Verificare coerenza C19 (numero revisioni) con registro"
        ]
    },
    "EG34U": {
        "descrizione": "Servizi acconciatura (parrucchieri)",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13"],
        "documenti": ["Bilancio", "Listino tariffe", "Contratti franchising"],
        "controlli": [
            "Verificare che C02-C10 (tipologia attività) sommino 100%",
            "Verificare coerenza C11 (numero estetiste/visagiste) con personale",
            "Verificare coerenza C12 (ricavi postazioni) con contratti",
            "Verificare coerenza C13 (costi postazioni terzi) con fatture"
        ]
    },
    "EG36U": {
        "descrizione": "Ristorazione commerciale",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28"],
        "documenti": ["Bilancio", "Registro pasti", "Distinta acquisti cibi/bevande"],
        "controlli": [
            "Verificare separazione C01-C05 (aggio) da altri ricavi",
            "Verificare che C07-C16 (tipologia attività) sommino 100%",
            "Verificare coerenza C17 (banchetti) con fatture",
            "Verificare che C20-C25 (acquisti cibi/bevande) sommino 100%",
            "Verificare coerenza C26 (costi lavanderia) con fatture",
            "Verificare coerenza C27 (rimanenze alcolici) con inventario",
            "Se C28 compilato (franchising), verificare costi con contratto"
        ]
    },
    "EG37U": {
        "descrizione": "Bar, gelateria, pasticceria",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34"],
        "documenti": ["Bilancio", "Registro consumi", "Listino prezzi"],
        "controlli": [
            "Verificare separazione C01-C05 (aggio) da altri ricavi",
            "Verificare coerenza C06 (proventi apparecchi) con documentazione",
            "Verificare che C07-C18 (tipologia attività) sommino 100%",
            "Verificare che C19-C27 (tipologia prodotti) coincidano con C07-C10",
            "Verificare coerenza C28-C29 (elementi contabili) con bilancio",
            "Verificare coerenza C33 (energia Kwh) con bollette",
            "Verificare coerenza E01 (consumo caffè Kg) con acquisti"
        ]
    },
    "EG40U": {
        "descrizione": "Locazione, valorizzazione, compravendita immobili",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
        "documenti": ["Bilancio", "Contratti locazione/vendita", "Dati catastali"],
        "controlli": [
            "Verificare che C01-C14 (tipologia attività) sommino 100%",
            "Verificare che C47-C54 (localizzazione immobili) sommino 100%",
            "Verificare coerenza C56 (split payment) con fatture PA",
            "Verificare coerenza C57 (reverse charge) con fatture",
            "Verificare coerenza C59-C62 (rimanenze) con bilancio",
            "Verificare coerenza C65-C66 (cambio destinazione) con scritture"
        ]
    },
    "EG50U": {
        "descrizione": "Intonacatura, tinteggiatura, lavori completamento edifici",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47"],
        "documenti": ["Bilancio", "Fatture", "DURC", "Localizzazioni cantieri"],
        "controlli": [
            "Verificare che C01-C28 (specializzazione) sommino 100%",
            "Verificare che C31-C32 (modalità realizzazione) sommino 100%",
            "Verificare che C36-C41 (localizzazione) sommino 100%",
            "Verificare che C46-C47 (ambito attività) sommino 100%",
            "Verificare coerenza C43 (split payment) con fatture PA",
            "Verificare coerenza C44 (reverse charge) con fatture",
            "Verificare regolarità DURC per tutti i cantieri"
        ]
    },
    "EG61U": {
        "descrizione": "Intermediari commercio e servizi",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58"],
        "documenti": ["Bilancio", "Mandati", "Registro provvigioni"],
        "controlli": [
            "Verificare che C23-C44 (area esercizio) sommino 100%",
            "Verificare che C45-C54 (settori merceologici) sommino 100%",
            "Verificare coerenza C55 (deduzione forfetaria) con TUIR",
            "Verificare coerenza C56 (vendite subagenti) con registri",
            "Verificare coerenza C57 (carburanti) con fatture",
            "Verificare coerenza C58 (numero subagenti) con contratti"
        ]
    },
    "EG69U": {
        "descrizione": "Costruzioni edili",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53"],
        "documenti": ["Bilancio", "Fatture", "Cantieri", "DURC", "Localizzazioni geografiche"],
        "controlli": [
            "Verificare che C01-C07 (ambito attività) sommino 100%",
            "Verificare che C08-C28 (specializzazione) sommino 100%",
            "Verificare che C30-C32 (acquisizione lavori) sommino 100%",
            "Verificare che C36-C41 (localizzazione) sommino 100%",
            "Verificare coerenza C42 (split payment) con fatture PA",
            "Verificare coerenza C43 (reverse charge) con fatture",
            "Verificare coerenza C46-C49 (rimanenze) con bilancio",
            "Verificare regolarità DURC per tutti i cantieri"
        ]
    },
    "EG75U": {
        "descrizione": "Installazione impianti elettrici, idraulici",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43"],
        "documenti": ["Bilancio", "Contratti", "Cantieri"],
        "controlli": [
            "Verificare che C01-C25 (specializzazione) sommino 100%",
            "Verificare che C26-C29 (tipologia servizio) sommino 100%",
            "Verificare che C36-C40 (area territoriale) sommino 100%",
            "Verificare che C42-C43 (ambito attività) sommino 100%",
            "Verificare coerenza C32 (split payment) con fatture PA",
            "Verificare coerenza C33 (reverse charge) con fatture"
        ]
    },
    "EG99U": {
        "descrizione": "Altri servizi a imprese e famiglie",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09"],
        "documenti": ["Bilancio", "Contratti servizi"],
        "controlli": [
            "Verificare che C01-C07 (tipologia attività) sommino 100%",
            "Verificare categoria reddituale (impresa vs lavoro autonomo)",
            "Se C08 > 50%, verificare concentrazione committente",
            "Se cooperativa, verificare coerenza C09 (ristorni) con bilancio"
        ]
    },
    "EK02U": {
        "descrizione": "Studi di ingegneria",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40"],
        "documenti": ["Bilancio", "Incarichi professionali"],
        "controlli": [
            "Verificare che C01-C34 (tipologia prestazioni) sommino 100%",
            "Verificare che C35-C38 (macro aree specialistiche) sommino 100%",
            "Se C39 > 50%, verificare concentrazione committente",
            "Verificare che C40 <= C39"
        ]
    },
    "EK19U": {
        "descrizione": "Attività paramediche",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20"],
        "documenti": ["Bilancio", "Prestazioni sanitarie"],
        "controlli": [
            "Verificare che C01-C04 (tipologia prestazioni) sommino 100%",
            "Verificare categoria reddituale (impresa vs lavoro autonomo)",
            "Se C17 > 50%, verificare concentrazione committente",
            "Verificare coerenza C18-C20 con tipologia attività"
        ]
    },
    "EM01A": {
        "descrizione": "Commercio al dettaglio alimentare",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49"],
        "documenti": ["Bilancio", "Registro corrispettivi"],
        "controlli": [
            "Verificare separazione C01-C05 (aggio) da altri ricavi",
            "Verificare che C06-C14 (modalità vendita) sommino 100%",
            "Verificare che C20-C47 (tipologia offerta) sommino 100%",
            "Verificare coerenza C48-C49 (tipologia prodotti) con C20-C47"
        ]
    },
    "EM05U": {
        "descrizione": "Commercio abbigliamento",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37"],
        "documenti": ["Bilancio", "Registro vendite", "Distinta prodotti"],
        "controlli": [
            "Verificare che C01-C11 (modalità vendita) sommino 100%",
            "Verificare che C12-C23 (prodotti) sommino 100%",
            "Verificare che C24-C29 (fascia qualitativa) sommino 100%",
            "Verificare che C30-C33 (modalità acquisto) sommino 100%",
            "Verificare coerenza C34-C37 con documentazione"
        ]
    },
    "EM11U": {
        "descrizione": "Commercio ferramenta, termoidraulica, materiali da costruzione",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32"],
        "documenti": ["Bilancio", "Registro vendite"],
        "controlli": [
            "Verificare che C01-C18 (prodotti) sommino 100%",
            "Verificare che C19-C28 (tipologia vendita) sommino 100%",
            "Verificare coerenza C29-C30 con personale vendita",
            "Verificare coerenza C31-C32 (modalità organizzativa) con contratti"
        ]
    },
    "EM43U": {
        "descrizione": "Commercio macchine agricole e giardinaggio",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "documenti": ["Bilancio", "Registro vendite"],
        "controlli": [
            "Verificare che C01-C10 (tipologia vendita) sommino 100%",
            "Verificare che C11-C22 (tipologia offerta) sommino 100%"
        ]
    },
    "EM85U": {
        "descrizione": "Commercio prodotti tabacco",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12"],
        "documenti": ["Bilancio", "Dati aggio/ricavo fisso", "Registro vendite"],
        "controlli": [
            "Verificare separazione C01-C05 (aggio) da altri ricavi",
            "Verificare coerenza C06 (proventi apparecchi) con documentazione",
            "Verificare coerenza C07-C09 con ricavi totali",
            "Verificare coerenza C10 (sigarette elettroniche) con vendite",
            "Verificare coerenza C11-C12 (costi servizi) con fatture"
        ]
    },
    "FM87U": {
        "descrizione": "Commercio al dettaglio altri prodotti",
        "campi": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "documenti": ["Bilancio", "Registro corrispettivi", "Distinta settori merceologici"],
        "controlli": [
            "Verificare che C01-C08 (modalità vendita) sommino 100%",
            "Verificare che C13-C22 (settori merceologici) sommino 100%",
            "Verificare coerenza C09 (negozio automatizzato) <= C08"
        ]
    }
}

st.title("📊 ISA - Compilazione Quadro C")
st.markdown("Carica il PDF delle istruzioni ISA per generare il prompt di compilazione")

uploaded_file = st.file_uploader("📄 Carica PDF istruzioni ISA", type=['pdf'])

if uploaded_file is not None:
    with st.spinner('🔍 Analisi del PDF in corso...'):
        try:
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
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Settore", data.get('descrizione', 'N/A'))
                with col2:
                    st.metric("Campi Quadro C", len(data.get('campi', [])))
                with col3:
                    st.metric("Controlli richiesti", len(data.get('controlli', [])))
                
                st.subheader("📎 Documenti Richiesti")
                for doc in data.get('documenti', []):
                    st.write(f"✓ {doc}")
                
                st.subheader("⚠️ Controlli di Validazione Quadro C")
                for controllo in data.get('controlli', []):
                    st.warning(f"🔍 {controllo}")
                
                if data.get('note'):
                    st.info(f"📌 **Nota importante:** {data.get('note')}")
                
                st.subheader("📋 Campi del Quadro C da Compilare")
                st.write(", ".join(data.get('campi', [])))
                
                fields_str = ", ".join(data.get('campi', []))
                docs_str = "\n".join([f"- {doc}" for doc in data.get('documenti', [])])
                controlli_str = "\n".join([f"□ {ctrl}" for ctrl in data.get('controlli', [])])
                note = data.get('note', '')
                desc = data.get('descrizione', '')
                
                prompt = f"""
COMPILAZIONE QUADRO C - ISA {isa_code}
{desc}

MODELLO ISA: {isa_code}
SETTORE: {desc}
DATA GENERAZIONE: {datetime.now().strftime('%d/%m/%Y %H:%M')}

DOCUMENTAZIONE RICHIESTA

{docs_str}

CAMPI QUADRO C DA COMPILARE

{fields_str}

TOTALE CAMPI: {len(data.get('campi', []))}

ISTRUZIONI COMPILAZIONE

Per CIASCUN CAMPO del Quadro C elencato sopra, fornire:

CAMPO: C##
VALORE: [inserire valore numerico o percentuale]
FONTE DOCUMENTALE: [es. Bilancio 2024 pag. X / Fattura n. Y]
DESCRIZIONE: [breve descrizione del dato]
NOTE: [eventuali criticità o osservazioni]
COERENZA: [coerente / da verificare / anomalo]

RIPETERE PER TUTTI I {len(data.get('campi', []))} CAMPI

CONTROLLI DI VALIDAZIONE

{controlli_str}

NOTE SPECIFICHE: {note}

IMPORTANTE: Le percentuali devono sommare esattamente 100% dove richiesto

GESTIONE DATI INCERTI O DUBBI

In caso di dati incerti, dubbi o non documentabili:

1. SEGNALARE ESPLICITAMENTE il campo interessato
2. INDICARE il motivo dell'incertezza (mancanza documentazione, dati contraddittori, stime necessarie)
3. FORNIRE una stima motivata con indicazione del margine di errore
4. DOCUMENTARE ogni assunzione fatta
5. RICHIEDERE documentazione integrativa se necessaria

ESEMPIO SEGNAZIONE DATO INCERTO:

CAMPO: C15
STATO: DATO INCERTO - DA VERIFICARE
MOTIVO: Mancanza fatture fornitori per il mese di dicembre
STIMA: Euro 15.000 (margine errore +/- 10%)
AZIONE RICHIESTA: Richiedere estratto conto bancario dicembre

CHECKLIST PRE-INVIO

□ Tutti i campi obbligatori compilati
□ Documentazione a supporto disponibile per ogni valore
□ Percentuali sommano 100% dove richiesto
□ Coerenza interna verificata tra i vari campi
□ Dati congrui con il settore di attività
□ Eventuali anomalie giustificate e documentate
□ Dati incerti segnalati esplicitamente
□ Controlli di validazione effettuati

OUTPUT FINALE RICHIESTO

Al termine della compilazione fornire:

1. TABELLA RIEPILOGATIVA con tutti i campi compilati
2. ANALISI DI COERENZA interna tra i vari campi
3. SEGNALAZIONE CRITICITÀ con indicazione priorità (alta/media/bassa)
4. ELENCO DOCUMENTI MANCANTI (se presenti)
5. CHECKLIST PRE-INVIO completata
6. NOTE OPERATIVE per il consulente

NOTE IMPORTANTI

- Utilizzare SOLO dati dalla documentazione allegata
- CITARE SEMPRE la fonte documentale per ogni campo
- SEGNALARE se un campo non può essere compilato per mancanza dati
- I quadri A, B, D, E, F, H sono gestiti separatamente dal consulente
- In caso di dubbi, richiedere chiarimenti prima di procedere
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
