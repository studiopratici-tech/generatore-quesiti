import streamlit as st

st.set_page_config(page_title="✍️ Articoli Blog", page_icon="✍️", layout="wide")

st.title("✍️ GENERATORE ARTICOLI PROFESSIONALI")
st.markdown("*Per www.studiopratici.com — Contenuti tecnici, normativi, SEO-ready*")
st.markdown("---")

# DATI ARTICLE
col1, col2, col3 = st.columns(3)
with col1:
    data_pubblicazione = st.date_input("📅 Data pubblicazione", value=None)
with col2:
    autore = st.text_input("✍️ Autore", placeholder="Nome cognome o 'Redazione Studio Pratici'")
with col3:
    categoria = st.selectbox("📁 Categoria", [
        "Tributario e Fiscale",
        "Diritto del Lavoro",
        "Sentenze e Massime Cassazione",
        "Assicurazioni e RCA",
        "Normativa Regionale/Comunale",
        "Approfondimenti Tecnici",
        "News Normative",
        "Guide Pratiche Operative"
    ])

st.markdown("---")

# TITOLO E SEO
st.subheader("🎯 TITOLO E SEO")
col1, col2 = st.columns(2)
with col1:
    titolo_articolo = st.text_input("Titolo dell'articolo", placeholder="Es: Guida pratica al collegamento POS e registratore di cassa 2026")
    meta_descrizione = st.text_area("Meta descrizione (max 160 caratteri)", 
        placeholder="Breve sintesi per Google",
        height=70)
with col2:
    parole_chiave = st.text_area("Parole chiave SEO (separate da virgola)", 
        placeholder="collegamento POS registratore di cassa, adempimenti 2026")
    lunghezza_articolo = st.selectbox("Lunghezza stimata", ["Breve (600-1000 parole)", "Medio (1000-1800 parole)", "Lungo (1800-3000 parole)", "Guida completa (3000+ parole)"])

# TARGET E TONO
st.markdown("---")
st.subheader("👥 TARGET E STILE")
col1, col2 = st.columns(2)
with col1:
    target = st.selectbox("Destinatari", [
        "Professionisti dello studio (tecnico-specialistico)",
        "Clienti dello studio (professionale ma accessibile)",
        "Pubblico generale (divulgativo)",
        "Misto (professionisti + clienti)"
    ])
with col2:
    tono = st.selectbox("Tono di voce", [
        "Tecnico-normativo (preciso, citazioni puntuali)",
        "Professionale-discorsivo (chiaro ma autorevole)",
        "Pratico-operativo (guide passo-passo, esempi)",
        "Ibrido (tecnico + spiegazioni accessibili)"
    ])

# FONTI NORMATIVE PRIMARIE
st.markdown("---")
st.subheader("📚 FONTI NORMATIVE PRIMARIE")
st.markdown("*Seleziona le fonti giuridiche da utilizzare e citare*")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🇮🇹 NAZIONALI**")
    fonte_costituzione = st.checkbox("Costituzione Italiana")
    fonte_codice_civile = st.checkbox("Codice Civile")
    fonte_gazzetta = st.checkbox("Gazzetta Ufficiale / Normattiva")
    fonte_decreti_legge = st.checkbox("Decreti Legge / Decreti Legislativi")
    fonte_leggi_regionali = st.checkbox("Leggi Regionali")
    fonte_regolamenti_comunali = st.checkbox("Regolamenti Comunali")
    
with col2:
    st.markdown("**🇪🇺 EUROPEE**")
    fonte_trattati_ue = st.checkbox("Trattati UE")
    fonte_regolamenti_ue = st.checkbox("Regolamenti UE")
    fonte_direttive_ue = st.checkbox("Direttive UE")
    fonte_eurlex = st.checkbox("EUR-Lex (banca dati UE)")
    fonte_gu_ue = st.checkbox("Gazzetta Ufficiale UE")
    
with col3:
    st.markdown("**⚖️ GIURISPRUDENZA**")
    fonte_cassazione_civile = st.checkbox("Cassazione Civile")
    fonte_cassazione_penale = st.checkbox("Cassazione Penale")
    fonte_cassazione_lavoro = st.checkbox("Cassazione Lavoro")
    fonte_cassazione_tributaria = st.checkbox("Cassazione Tributaria")
    fonte_corte_costituzionale = st.checkbox("Corte Costituzionale")
    fonte_corte_conti = st.checkbox("Corte dei Conti")

# CIRCOLARI E INTERPELLI
st.markdown("---")
st.subheader("📰 CIRCOLARI E INTERPELLI UFFICIALI")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**AGENZIE FISCALI**")
    fonte_agenzia_entrate_circ = st.checkbox("Circolari Agenzia delle Entrate")
    fonte_agenzia_entrate_interpello = st.checkbox("Risposte Interpello AdE")
    fonte_agenzia_dogane = st.checkbox("Circolari Agenzia Dogane")
    fonte_agenzia_entrate_riscossione = st.checkbox("Circolari Agenzia Entrate-Riscossione")
    
with col2:
    st.markdown("**ENTE PREVIDENZIALI**")
    fonte_inps_circolari = st.checkbox("Circolari INPS")
    fonte_inps_messaggi = st.checkbox("Messaggi INPS")
    fonte_inail = st.checkbox("Circolari INAIL")
    
with col3:
    st.markdown("**ALTRI ENTI**")
    fonte_ivass = st.checkbox("Regolamenti/Circolari IVASS")
    fonte_consap = st.checkbox("Norme/Comunicazioni CONSAP")
    fonte_ministero_sviluppo = st.checkbox("Circolari MISE")
    fonte_ministero_lavoro = st.checkbox("Circolari Ministero del Lavoro")

# BANCHE DATI E RIVISTE
st.markdown("---")
st.subheader("📚 BANCHE DATI E RIVISTE SPECIALIZZATE")
st.markdown("*Seleziona le fonti dottrinali e tecniche autorizzate*")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📊 TRIBUTARIO E FISCALE**")
    banco_sole24ore = st.checkbox("Il Sole 24 Ore")
    banco_edotto = st.checkbox("Edotto (Wolters Kluwer)")
    banco_fiscalfocus = st.checkbox("Fiscal Focus")
    banco_italiaoggi_fisco = st.checkbox("Italia Oggi - Sezione Fiscale")
    banco_praticafiscale = st.checkbox("Pratica Fiscale")
    banco_rass_tributaria = st.checkbox("Rassegna Tributaria")
    
with col2:
    st.markdown("**⚖️ LAVORO E PREVIDENZA**")
    banco_lavoro_wk = st.checkbox("Lavoro in Wolters Kluwer")
    banco_guida_lavoro = st.checkbox("Guida al Lavoro (Sole 24 Ore)")
    banco_bollettino_adapt = st.checkbox("Bollettino ADAPT")
    banco_rivista_diritto_lavoro = st.checkbox("Rivista di Diritto del Lavoro")
    banco_previdenza_sociale = st.checkbox("Previdenza Sociale")
    
with col3:
    st.markdown("**🏢 CIVILE E SOCIETARIO**")
    banco_vita_notarile = st.checkbox("Vita Notarile")
    banco_societa_wk = st.checkbox("Società (Wolters Kluwer)")
    banco_diritto_societa = st.checkbox("Diritto delle Società")
    banco_rivista_notarile = st.checkbox("Rivista Notarile")

# SETTORI SPECIFICI
st.markdown("---")
st.subheader("🚗 SETTORI SPECIFICI")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**AUTO E TRASPORTI**")
    banco_quattroruote = st.checkbox("Quattroruote")
    banco_eurotax = st.checkbox("Eurotax/Blue Book")
    banco_aci_tecnico = st.checkbox("ACI (dati tecnici)")
    banco_mit = st.checkbox("Ministero Infrastrutture e Trasporti")
    
with col2:
    st.markdown("**IMMOBILIARE ED EDILIZIA**")
    banco_tecno_borsa = st.checkbox("Tecno Borsa (OMI)")
    banco_agenzia_entr_territorio = st.checkbox("Agenzia Entrate-Territorio")
    banco_edilizia_wk = st.checkbox("Edilizia (Wolters Kluwer)")
    banco_cnce = st.checkbox("CNCE (prezzi edili)")
    
with col3:
    st.markdown("**AMBIENTE ED ENERGIA**")
    banco_enea = st.checkbox("ENEA (schede tecniche)")
    banco_gse = st.checkbox("GSE (guide incentivi)")
    banco_arpa = st.checkbox("ARPA (dati ambientali)")
    banco_ministero_ambiente = st.checkbox("Ministero della Transizione Ecologica")

# PORTALI ISTITUZIONALI
st.markdown("---")
st.subheader("🌐 PORTALI ISTITUZIONALI E PROCEDURE")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**PORTALI FISCALI**")
    banco_portale_ade = st.checkbox("Portale Agenzia delle Entrate")
    banco_fisconline = st.checkbox("Fisconline/Entratel")
    banco_cassetto_fiscale = st.checkbox("Cassetto Fiscale")
    banco_fatture_corrispettivi = st.checkbox("Portale Fatture e Corrispettivi")
    
with col2:
    st.markdown("**PORTALI PREVIDENZIALI**")
    banco_portale_inps = st.checkbox("Portale INPS")
    banco_sedile_inps = st.checkbox("Sedile INPS (consultazione)")
    banco_flussi_uniemens = st.checkbox("Flussi UniEmens")
    banco_posizione_assicurativa = st.checkbox("Posizione Assicurativa")
    
with col3:
    st.markdown("**ALTRI PORTALI**")
    banco_portale_impresa = st.checkbox("Portale Impresa (Registro Imprese)")
    banco_comunicazioni_obbligatorie = st.checkbox("Comunicazioni Obbligatorie (CO)")
    banco_sistema_tessera_sanitaria = st.checkbox("Sistema Tessera Sanitaria")
    banco_pec = st.checkbox("Portali PEC")
    banco_spid_cns = st.checkbox("Guide SPID/CNS")

# ALTRE FONTI
st.markdown("---")
st.subheader("📝 ALTRE FONTI SPECIFICHE")
altre_fonti = st.text_area("Inserisci altre fonti non elencate (una per riga)", 
    placeholder="Es: Banca d'Italia\nCONSOB\nGarante Privacy\n...\n(Lascia vuoto se non serve)")

# IMMAGINI
st.markdown("---")
st.subheader("🖼️ IMMAGINI E CONTENUTI VISIVI")
tipo_contenuto = st.radio("Tipo di articolo", [
    "Articolo normativo/dottrinale (poche immagini)",
    "Guida pratica/procedurale (immagini esplicative)",
    "Approfondimento tecnico (grafici/tabelle)",
    "News breve (1 immagine di contesto)"
])

immagini_procedurali = False
termini_ricerca_custom = ""
if "procedurale" in tipo_contenuto or "tecnica" in tipo_contenuto:
    immagini_procedurali = st.checkbox("Richiedi immagini procedurali passo-passo", value=True)
    termini_ricerca_custom = st.text_input("Termini specifici per ricerca immagini", 
        placeholder="Es: POS collegato registratore di cassa")

st.markdown("---")
st.subheader("📸 FONTI IMMAGINI ROYALTY-FREE")
col1, col2, col3 = st.columns(3)
with col1:
    unsplash = st.checkbox("Unsplash")
    pexels = st.checkbox("Pexels")
with col2:
    pixabay = st.checkbox("Pixabay")
    freepik = st.checkbox("Freepik (con attribuzione)")
with col3:
    screenshot_proprio = st.checkbox("Screenshot da portali ufficiali")
    nessuna_immagine = st.checkbox("Nessuna immagine")

# INIZIALIZZA SESSION STATE (per mantenere le selezioni tra i rerun)
if 'struttura_articolo' not in st.session_state:
    st.session_state.struttura_articolo = []

# STRUTTURA
st.markdown("---")
st.subheader("📐 STRUTTURA E IMPAGINAZIONE")
elementi_struttura = st.multiselect(
    "Sezioni dell'articolo", 
    [
        "Titolo H1 accattivante + sottotitolo esplicativo",
        "Sommario/esecutivo iniziale (3-5 righe)",
        "Indice dei contenuti (per articoli lunghi)",
        "Inquadramento normativo di riferimento",
        "Analisi puntuale con citazioni (fonte + articolo + comma + data)",
        "Applicazione pratica con esempi concreti",
        "Procedura operativa passo-passo (se guida)",
        "Immagini esplicative con didascalie (se pertinenti)",
        "Box 'Cosa cambia' o 'Novità'",
        "Box 'Da ricordare' con punti chiave",
        "Prassi operative e suggerimenti procedurali",
        "Eventuali lacune o zone grigie (dichiarate esplicitamente)",
        "FAQ (domande frequenti)",
        "Conclusioni operative per il lettore",
        "Riferimenti normativi completi in fondo",
        "Link utili e approfondimenti"
    ],
    default=st.session_state.struttura_articolo,  # ← Usa session state invece di default fisso
    key="key_struttura"
)

# SALVA LO STATO
st.session_state.struttura_articolo = elementi_struttura

# FORMATTAZIONE COMPLETA
st.markdown("---")
st.subheader("🎨 FORMATTAZIONE PER WIX")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📝 TIPOGRAFIA**")
    testo_giustificato = st.checkbox("Testo giustificato")
    paragrafi_brevi = st.checkbox("Paragrafi brevi (3-5 righe)")
    
    tipo_font = st.selectbox(
        "Tipo di carattere",
        [
            "Arial/Helvetica (sans-serif, moderno)",
            "Times New Roman (serif, tradizionale)",
            "Georgia (serif, web-friendly)",
            "Verdana (sans-serif, leggibile)",
            "Calibri (modern, pulito)",
            "Roboto (Google Fonts, moderno)",
            "Open Sans (web, versatile)",
            "Lato (professionale)",
            "Montserrat (elegante)",
            "Playfair Display (serif, elegante)"
        ],
        index=0
    )
    
with col2:
    st.markdown("**📏 DIMENSIONI**")
    dimensione_font = st.selectbox(
        "Dimensione carattere corpo testo",
        [
            "Piccola (10-11pt) - per articoli densi",
            "Normale (12pt) - standard web",
            "Media (13-14pt) - più leggibile",
            "Grande (15-16pt) - massima leggibilità"
        ],
        index=1
    )
    
    interlinea = st.selectbox(
        "Interlinea",
        [
            "Singola (1.0) - compatta",
            "1.15 - leggermente ariosa",
            "1.5 - standard leggibilità",
            "Doppia (2.0) - massima leggibilità"
        ],
        index=2
    )
    
with col3:
    st.markdown("**📑 STRUTTURA TITOLI**")
    gerarchia_titoli = st.radio(
        "Livelli di sottotitoli",
        [
            "H1 > H2 (solo titoli principali)",
            "H1 > H2 > H3 (titoli + sottotitoli)",
            "H1 > H2 > H3 > H4 (struttura completa)"
        ],
        index=1
    )
    
    uso_h2_h3 = st.checkbox("Gerarchia H2/H3 per sottotitoli")

st.markdown("---")
st.subheader("🎨 STILI E EVIDENZIAZIONI")
col1, col2 = st.columns(2)
with col1:
    grassetto_chiave = st.checkbox("Grassetto per concetti chiave")
    corsivo_tecnico = st.checkbox("Corsivo per termini tecnici")
    elenchi_minimali = st.checkbox("Elenchi solo se necessari")
    box_evidenziazione = st.checkbox("Box colorati per avvisi/novità")
with col2:
    numerazione_sezioni = st.checkbox("Numerazione sezioni (1., 1.1, 1.1.1)")
    citazioni_evidenziate = st.checkbox("Citazioni normative in box separati")
    link_ipertestuali = st.checkbox("Link attivi nel testo")
    note_piè_pagina = st.checkbox("Note a piè di pagina")

# GENERA ARTICOLO
st.markdown("---")
if st.button("🚀 GENERA PROMPT ARTICOLO PROFESSIONALE", type="primary", use_container_width=True):
    if not titolo_articolo or not categoria:
        st.error("⚠️ Inserisci almeno titolo e categoria!")
    else:
        # RACCOGLI FONTI
        fonti_normative = []
        if fonte_costituzione: fonti_normative.append("Costituzione Italiana")
        if fonte_codice_civile: fonti_normative.append("Codice Civile")
        if fonte_gazzetta: fonti_normative.append("Gazzetta Ufficiale / Normattiva")
        if fonte_decreti_legge: fonti_normative.append("Decreti Legge / Decreti Legislativi")
        if fonte_leggi_regionali: fonti_normative.append("Leggi Regionali")
        if fonte_regolamenti_comunali: fonti_normative.append("Regolamenti Comunali")
        if fonte_trattati_ue: fonti_normative.append("Trattati UE")
        if fonte_regolamenti_ue: fonti_normative.append("Regolamenti UE")
        if fonte_direttive_ue: fonti_normative.append("Direttive UE")
        if fonte_eurlex: fonti_normative.append("EUR-Lex")
        if fonte_gu_ue: fonti_normative.append("Gazzetta Ufficiale UE")
        if fonte_cassazione_civile: fonti_normative.append("Cassazione Civile")
        if fonte_cassazione_penale: fonti_normative.append("Cassazione Penale")
        if fonte_cassazione_lavoro: fonti_normative.append("Cassazione Lavoro")
        if fonte_cassazione_tributaria: fonti_normative.append("Cassazione Tributaria")
        if fonte_corte_costituzionale: fonti_normative.append("Corte Costituzionale")
        if fonte_corte_conti: fonti_normative.append("Corte dei Conti")
        
        circolari_interpelli = []
        if fonte_agenzia_entrate_circ: circolari_interpelli.append("Circolari Agenzia delle Entrate")
        if fonte_agenzia_entrate_interpello: circolari_interpelli.append("Risposte Interpello AdE")
        if fonte_agenzia_dogane: circolari_interpelli.append("Circolari Agenzia Dogane")
        if fonte_agenzia_entrate_riscossione: circolari_interpelli.append("Circolari Agenzia Entrate-Riscossione")
        if fonte_inps_circolari: circolari_interpelli.append("Circolari INPS")
        if fonte_inps_messaggi: circolari_interpelli.append("Messaggi INPS")
        if fonte_inail: circolari_interpelli.append("Circolari INAIL")
        if fonte_ivass: circolari_interpelli.append("Circolari IVASS")
        if fonte_consap: circolari_interpelli.append("Norme CONSAP")
        if fonte_ministero_sviluppo: circolari_interpelli.append("Circolari MISE")
        if fonte_ministero_lavoro: circolari_interpelli.append("Circolari Ministero del Lavoro")
        
        banche_dati = []
        if banco_sole24ore: banche_dati.append("Il Sole 24 Ore")
        if banco_edotto: banche_dati.append("Edotto (Wolters Kluwer)")
        if banco_fiscalfocus: banche_dati.append("Fiscal Focus")
        if banco_italiaoggi_fisco: banche_dati.append("Italia Oggi - Sezione Fiscale")
        if banco_praticafiscale: banche_dati.append("Pratica Fiscale")
        if banco_rass_tributaria: banche_dati.append("Rassegna Tributaria")
        if banco_lavoro_wk: banche_dati.append("Lavoro in Wolters Kluwer")
        if banco_guida_lavoro: banche_dati.append("Guida al Lavoro (Sole 24 Ore)")
        if banco_bollettino_adapt: banche_dati.append("Bollettino ADAPT")
        if banco_rivista_diritto_lavoro: banche_dati.append("Rivista di Diritto del Lavoro")
        if banco_previdenza_sociale: banche_dati.append("Previdenza Sociale")
        if banco_vita_notarile: banche_dati.append("Vita Notarile")
        if banco_societa_wk: banche_dati.append("Società (Wolters Kluwer)")
        if banco_diritto_societa: banche_dati.append("Diritto delle Società")
        if banco_rivista_notarile: banche_dati.append("Rivista Notarile")
        if banco_quattroruote: banche_dati.append("Quattroruote")
        if banco_eurotax: banche_dati.append("Eurotax/Blue Book")
        if banco_aci_tecnico: banche_dati.append("ACI (dati tecnici)")
        if banco_mit: banche_dati.append("Ministero Infrastrutture e Trasporti")
        if banco_tecno_borsa: banche_dati.append("Tecno Borsa (OMI)")
        if banco_agenzia_entr_territorio: banche_dati.append("Agenzia Entrate-Territorio")
        if banco_edilizia_wk: banche_dati.append("Edilizia (Wolters Kluwer)")
        if banco_cnce: banche_dati.append("CNCE (prezzi edili)")
        if banco_enea: banche_dati.append("ENEA")
        if banco_gse: banche_dati.append("GSE")
        if banco_arpa: banche_dati.append("ARPA")
        if banco_ministero_ambiente: banche_dati.append("Ministero della Transizione Ecologica")
        
        portali = []
        if banco_portale_ade: portali.append("Portale Agenzia delle Entrate")
        if banco_fisconline: portali.append("Fisconline/Entratel")
        if banco_cassetto_fiscale: portali.append("Cassetto Fiscale")
        if banco_fatture_corrispettivi: portali.append("Portale Fatture e Corrispettivi")
        if banco_portale_inps: portali.append("Portale INPS")
        if banco_sedile_inps: portali.append("Sedile INPS")
        if banco_flussi_uniemens: portali.append("Flussi UniEmens")
        if banco_posizione_assicurativa: portali.append("Posizione Assicurativa")
        if banco_portale_impresa: portali.append("Portale Impresa")
        if banco_comunicazioni_obbligatorie: portali.append("Comunicazioni Obbligatorie (CO)")
        if banco_sistema_tessera_sanitaria: portali.append("Sistema Tessera Sanitaria")
        if banco_pec: portali.append("Portali PEC")
        if banco_spid_cns: portali.append("Guide SPID/CNS")
        
        piattaforme_img = []
        if unsplash: piattaforme_img.append("Unsplash")
        if pexels: piattaforme_img.append("Pexels")
        if pixabay: piattaforme_img.append("Pixabay")
        if freepik: piattaforme_img.append("Freepik (con attribuzione)")
        if screenshot_proprio: piattaforme_img.append("Screenshot da portali ufficiali")
        
        if altre_fonti:
            fonti_custom = [f.strip() for f in altre_fonti.split('\n') if f.strip()]
            banche_dati.extend(fonti_custom)
        
        # COSTRUISCI IL PROMPT
        prompt = "✍️ ARTICOLO PROFESSIONALE PER STUDIO PRATICI — www.studiopratici.com\n\n"
        prompt += "📋 METADATI EDITORIALI\n"
        prompt += f"Titolo: {titolo_articolo}\n"
        prompt += f"Categoria: {categoria}\n"
        prompt += f"Autore: {autore or 'Redazione Studio Pratici'}\n"
        prompt += f"Data pubblicazione: {data_pubblicazione or 'Da definire'}\n"
        prompt += f"Target: {target}\n"
        prompt += f"Tono: {tono}\n"
        prompt += f"Lunghezza: {lunghezza_articolo}\n\n"
        
        prompt += "🔍 OTTIMIZZAZIONE SEO\n"
        prompt += f"Meta descrizione: {meta_descrizione or 'Da definire (max 160 caratteri)'}\n"
        prompt += f"Parole chiave: {parole_chiave or 'Da definire'}\n\n"
        
        prompt += "📚 FONTI NORMATIVE PRIMARIE DA UTILIZZARE\n"
        prompt += "=" * 65 + "\n"
        
        if fonti_normative:
            prompt += "FONTI GIURIDICHE:\n"
            for f in fonti_normative:
                prompt += f"✓ {f}\n"
        
        if circolari_interpelli:
            prompt += "\nCIRCOLARI E INTERPELLI:\n"
            for c in circolari_interpelli:
                prompt += f"✓ {c}\n"
        
        if banche_dati:
            prompt += "\nBANCHE DATI E DOTTRINA:\n"
            for b in banche_dati:
                prompt += f"✓ {b}\n"
        
        if portali:
            prompt += "\nPORTALI ISTITUZIONALI:\n"
            for p in portali:
                prompt += f"✓ {p}\n"
        
        prompt += "\nFORMATO CITAZIONE OBBLIGATORIO:\n\n"
        prompt += "📌 NORMATIVA NAZIONALE:\n"
        prompt += "   • Legge n.[X] del [data], art.[Y], comma [Z]\n"
        prompt += "     Es: Legge n. 190 del 06/11/2012, art. 1, comma 54\n"
        prompt += "   • D.Lgs. n.[X] del [data], art.[Y], comma [Z]\n"
        prompt += "     Es: D.Lgs. n. 209 del 07/09/2005 (Codice Assicurazioni), art. 141\n"
        prompt += "   • D.L. n.[X] del [data], convertito in L. n.[Y] del [data]\n"
        prompt += "     Es: D.L. n. 34 del 30/04/2019, convertito in L. n. 58 del 28/06/2019\n\n"
        
        prompt += "📌 NORMATIVA EUROPEA:\n"
        prompt += "   • Regolamento (UE) n.[X]/[anno] del [data], art.[Y]\n"
        prompt += "     Es: Regolamento (UE) 2016/679 (GDPR), art. 6\n"
        prompt += "   • Direttiva [anno]/[numero]/UE del [data], art.[Y]\n"
        prompt += "     Es: Direttiva 2014/49/UE del 16/04/2014, art. 3\n\n"
        
        prompt += "📌 GIURISPRUDENZA:\n"
        prompt += "   • Cass. [Sezione] n.[X] del [data]\n"
        prompt += "     Es: Cass. Civ. Sez. Trib. n. 12345 del 10/05/2024\n"
        prompt += "   • Corte Cost. sentenza n.[X] del [data]\n"
        prompt += "     Es: Corte Cost. sentenza n. 123 del 15/06/2024\n"
        prompt += "   • Cons. Stato Sez. [X] n.[Y] del [data]\n"
        prompt += "     Es: Cons. Stato Sez. IV n. 4567 del 20/03/2024\n\n"
        
        prompt += "📌 CIRCOLARI E INTERPELLI:\n"
        prompt += "   • [Organo], Circolare n.[X] del [data]\n"
        prompt += "     Es: Agenzia delle Entrate, Circolare n. 9/E del 14/02/2024\n"
        prompt += "   • [Organo], Risposta Interpello n.[X] del [data]\n"
        prompt += "     Es: Agenzia delle Entrate, Risposta Interpello n. 123 del 15/03/2024\n"
        prompt += "   • INPS, Messaggio n.[X] del [data]\n"
        prompt += "     Es: INPS, Messaggio n. 1234 del 20/04/2024\n\n"
        
        prompt += "📌 DOTTRINA E RIVISTE:\n"
        prompt += "   • [Autore], \"[Titolo articolo]\", [Rivista], [Data], pag. [X]\n"
        prompt += "     Es: Rossi M., \"Nuove scadenze fiscali\", Il Sole 24 Ore, 20/01/2024, pag. 15\n\n"
        
        prompt += "📐 STRUTTURA RICHIESTA DELL'ARTICOLO\n"
        for s in elementi_struttura:
            prompt += f"• {s}\n"
        prompt += "\n"
        
        prompt += "🎨 IMPAGINAZIONE E FORMATTAZIONE (WIX-READY)\n"
        prompt += "=" * 65 + "\n\n"
        
        prompt += f"📝 TIPOGRAFIA:\n"
        prompt += f"• Font: {tipo_font}\n"
        prompt += f"• Dimensione corpo testo: {dimensione_font}\n"
        prompt += f"• Interlinea: {interlinea}\n"
        prompt += f"• Allineamento: {'Giustificato' if testo_giustificato else 'A sinistra'}\n"
        prompt += f"• Lunghezza paragrafi: {'Brevi (3-5 righe)' if paragrafi_brevi else 'Standard'}\n\n"
        
        prompt += f"📑 STRUTTURA TITOLI:\n"
        prompt += f"• Gerarchia: {gerarchia_titoli}\n"
        prompt += f"• Numerazione sezioni: {'SÌ (1., 1.1, 1.1.1)' if numerazione_sezioni else 'NO'}\n"
        prompt += f"• Uso H2/H3: {'Attivo' if uso_h2_h3 else 'Solo H2'}\n\n"
        
        prompt += f"🎨 STILI E EVIDENZIAZIONI:\n"
        prompt += f"• Grassetto: {'Concetti chiave' if grassetto_chiave else 'Minimo'}\n"
        prompt += f"• Corsivo: {'Termini tecnici' if corsivo_tecnico else 'Minimo'}\n"
        prompt += f"• Elenchi: {'Solo se necessari' if elenchi_minimali else 'Liberi'}\n"
        prompt += f"• Box evidenziazione: {'SÌ (avvisi, novità, attenzione)' if box_evidenziazione else 'NO'}\n"
        prompt += f"• Citazioni in box: {'SÌ' if citazioni_evidenziate else 'NO'}\n"
        prompt += f"• Link attivi: {'SÌ' if link_ipertestuali else 'NO'}\n"
        prompt += f"• Note piè pagina: {'SÌ' if note_piè_pagina else 'NO'}\n\n"
        
        prompt += "🖼️ GESTIONE IMMAGINI E CONTENUTI VISIVI\n"
        prompt += f"Tipo articolo: {tipo_contenuto}\n"
        
        if immagini_procedurali:
            prompt += "✓ IMMAGINI PROCEDURALI RICHIESTE\n\n"
            prompt += "ISTRUZIONI SPECIFICHE PER LE IMMAGINI:\n"
            prompt += "1. ANALISI DEL CONTENUTO:\n"
            prompt += "   • Identifica i passaggi operativi che richiedono illustrazione visiva\n"
            prompt += "   • Per ogni passaggio critico, valuta se un'immagine può migliorare la comprensione\n"
            prompt += "   • Esempio: 'Guida collegamento POS e registratore di cassa' → servono immagini che mostrino:\n"
            prompt += "     - Il POS e il registratore di cassa\n"
            prompt += "     - I cavi/connessioni (USB, Ethernet, WiFi)\n"
            prompt += "     - Le schermate di configurazione\n"
            prompt += "     - Il procedimento passo-passo\n\n"
            prompt += "2. RICERCA IMMAGINI PERTINENTI:\n"
            prompt += f"   • Piattaforme autorizzate: {', '.join(piattaforme_img) if piattaforme_img else 'Unsplash, Pexels'}\n"
            prompt += f"   • Termini di ricerca: '{termini_ricerca_custom if termini_ricerca_custom else titolo_articolo}'\n"
            prompt += "   • Cerca immagini che mostrino ESPLICITAMENTE il procedimento/operazione\n\n"
            prompt += "3. CRITERI DI SELEZIONE:\n"
            prompt += "   • PERTINENZA: L'immagine deve mostrare ESATTAMENTE ciò che descrive il testo\n"
            prompt += "   • QUALITÀ: Alta risoluzione, professionale, leggibile\n"
            prompt += "   • ATTUALITÀ: Dispositivi/software recenti (non obsoleti)\n"
            prompt += "   • LICENZA: Solo royalty-free o fair use per screenshot portali ufficiali\n\n"
            prompt += "4. SE NON TROVI IMMAGINI PERTINENTI:\n"
            prompt += "   • NON inserire immagini generiche o decorative\n"
            prompt += "   • Scrivi: '[IMMAGINE: descrivi cosa servirebbe ma non è stata trovata]'\n"
            prompt += "   • Suggerisci: 'Scattare screenshot proprio o creare grafica ad hoc'\n\n"
            prompt += "5. DIDASCALIE OBBLIGATORIE:\n"
            prompt += "   • Ogni immagine deve avere didascalia descrittiva e SEO-friendly\n"
            prompt += "   • Formato: 'Fig. X - [Descrizione breve ma completa]'\n"
            prompt += "   • Esempio: 'Fig. 1 - Collegamento cavo USB tra POS e registratore di cassa'\n"
        else:
            prompt += "✓ Poche immagini (solo di contesto)\n\n"
            prompt += "1. IMMAGINI MINIMALI:\n"
            prompt += "   • Solo 1-2 immagini di contesto/introduzione\n"
            prompt += "   • Evita immagini decorative superflue\n"
            prompt += "   • Priorità a: concetti astratti, simboli professionali, infografiche\n\n"
        
        prompt += f"2. FONTI CONSENTITE: {', '.join(piattaforme_img) if piattaforme_img else 'Unsplash, Pexels, Pixabay'}\n\n"
        
        prompt += "=" * 65 + "\n"
        prompt += "🎯 ISTRUZIONI VINCOLANTI PER LA REDAZIONE\n"
        prompt += "=" * 65 + "\n\n"
        
        prompt += "1. FONTI E COPYRIGHT - RISPETTO ASSOLUTO\n"
        prompt += "   ✓ Usa SOLO fonti normative certe e pubblicamente accessibili\n"
        prompt += "   ✓ Cita SEMPRE: fonte, numero, data, articolo, comma\n"
        prompt += "   ✓ Per interpelli: cita solo risposte ufficiali AdE/INPS/Ministeri\n"
        prompt += "   ✓ Per dottrina: cita autore, testata, data (Sole 24 Ore, Edotto, Fiscal Focus, Italia Oggi)\n\n"
        prompt += "   ✗ VIETATO:\n"
        prompt += "   • Copiare testi integrali protetti da copyright\n"
        prompt += "   • Parafrasare senza attribuzione\n"
        prompt += "   • Usare 'si ritiene che', 'prassi consolidata' senza fonte certa\n"
        prompt += "   • Citare sentenze senza numero/data/sezione\n\n"
        
        prompt += "2. STILE DI SCRITTURA PROFESSIONALE\n"
        prompt += f"   • Adatta il linguaggio al target: {target}\n"
        prompt += f"   • Tono: {tono}\n"
        prompt += "   • Usa connettivi logici: 'pertanto', 'di conseguenza', 'inoltre', 'tuttavia'\n"
        prompt += "   • Struttura discorsiva ma organizzata (evita muri di testo)\n"
        prompt += "   • Spiega il PERCHÉ normativo, non solo il COSA\n\n"
        
        prompt += "3. RIGORE NORMATIVO\n"
        prompt += "   • Inquadra sempre il contesto prima dell'analisi\n"
        prompt += "   • Se la norma è ambigua/lacunosa, dichiaralo ESPPLICITAMENTE\n"
        prompt += "   • Per zone grigie: indica organo competente per interpello\n"
        prompt += "   • NON esprimere opinioni personali non supportate da fonti\n\n"
        
        prompt += "4. APPLICAZIONE PRATICA E PROCEDURE\n"
        prompt += "   • Traduci la norma in indicazioni OPERATIVE per il lettore\n"
        prompt += "   • Se guida procedurale: step-by-step numerati e chiari\n"
        prompt += "   • Indica: scadenze, modulistica, portali ufficiali, credenziali necessarie\n"
        prompt += "   • Per portali: specifica se serve SPID/CNS e link ufficiale\n\n"
        
        prompt += "5. SEO E OTTIMIZZAZIONE WIX\n"
        prompt += "   • H1: titolo principale (una sola volta)\n"
        prompt += "   • H2: sezioni principali (2-4 nell'articolo)\n"
        prompt += "   • H3: sottosezioni (se necessario)\n"
        prompt += "   • Meta descrizione: max 160 caratteri, accattivante, con CTA implicito\n"
        prompt += "   • Parole chiave: inserite in modo naturale (no keyword stuffing)\n"
        prompt += "   • URL slug: suggerisci versione SEO-friendly (es. 'guida-collegamento-pos-registratore-2026')\n\n"
        
        prompt += "6. FORMATTAZIONE TESTO GIUSTIFICATO\n"
        prompt += "   • Paragrafi brevi: 3-5 righe per leggibilità mobile\n"
        prompt += "   • Grassetto: solo per concetti chiave/normativi importanti\n"
        prompt += "   • Corsivo: termini tecnici/stranieri/non comuni\n"
        prompt += "   • Elenchi: SOLO se strettamente necessari (max 3-4 punti)\n"
        prompt += "   • Box evidenziazione: per 'Da ricordare', 'Novità', 'Attenzione'\n\n"
        
        prompt += "7. DIVIETO ASSOLUTO\n"
        prompt += "   ✗ Opinioni personali non supportate da fonti certe\n"
        prompt += "   ✗ 'Si ritiene che', 'prassi comune', 'orientamento prevalente' senza citazione\n"
        prompt += "   ✗ Copia-incolla di testi protetti da copyright\n"
        prompt += "   ✗ Immagini senza licenza chiara o attribuzione richiesta\n"
        prompt += "   ✗ Informazioni non verificate, datate o incerte\n"
        prompt += "   ✗ Link a siti non ufficiali o non attendibili\n\n"
        
        prompt += "=" * 65 + "\n"
        prompt += "✅ OUTPUT RICHIESTO - ARTICOLO PRONTO PER WIX\n"
        prompt += "=" * 65 + "\n\n"
        
        prompt += "Redigi l'articolo COMPLETO seguendo questa struttura:\n\n"
        prompt += "1. METADATI SEO (in fondo, per il redattore)\n"
        prompt += "   • Titolo H1: [titolo ottimizzato]\n"
        prompt += "   • Meta descrizione: [max 160 caratteri]\n"
        prompt += "   • Parole chiave: [lista]\n"
        prompt += "   • URL slug suggerito: [versione SEO-friendly]\n"
        prompt += f"   • Categoria: {categoria}\n"
        prompt += "   • Tempo di lettura stimato: [calcola in base alla lunghezza]\n\n"
        
        prompt += "2. CORPO ARTICOLO (pronto per copia-incolla in Wix)\n"
        prompt += "   • Titolo H1 + sottotitolo\n"
        prompt += "   • Sommario/esecutivo iniziale\n"
        prompt += "   • Inquadramento normativo di riferimento\n"
        prompt += "   • Corpo principale con sezioni H2/H3\n"
        prompt += "   • Citazioni normative nel formato indicato\n"
        prompt += "   • Immagini con didascalie (SOLO se pertinenti e trovate)\n"
        prompt += "   • Applicazione pratica con esempi concreti\n"
        prompt += "   • Conclusioni operative per il lettore\n"
        prompt += "   • Riferimenti normativi completi in fondo\n\n"
        
        prompt += "3. NOTE PER IL REDATTORE (in fondo)\n"
        prompt += "   • Suggerimenti immagini mancanti (se applicabile)\n"
        prompt += "   • Link utili da inserire\n"
        prompt += "   • Eventuali aggiornamenti futuri da monitorare\n\n"
        
        prompt += "L'articolo deve essere:\n"
        prompt += "✓ Professionalmente impeccabile\n"
        prompt += "✓ Normativamente certo (fonti citate)\n"
        prompt += "✓ Praticamente utile (indicazioni operative)\n"
        prompt += "✓ SEO-optimized (pronto per Wix)\n"
        prompt += "✓ Visivamente chiaro (immagini SOLO se pertinenti)\n"

        st.success("✅ Prompt articolo professionale generato!")
        st.code(prompt, language="markdown")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Scarica prompt .txt",
                data=prompt,
                file_name=f"articolo_{categoria.replace(' ', '_').lower()}_{data_pubblicazione}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.info("💡 Copia il prompt e incollalo in Claude o ChatGPT. L'output sarà pronto per Wix!")

# SIDEBAR INFO
with st.sidebar:
    st.header("ℹ️ Come usare questo generatore")
    st.markdown("""
    ### Per creare articoli professionali:
    
    1. **Compila metadati** (titolo, categoria, autore, data)
    
    2. **Definisci SEO** (meta descrizione, parole chiave)
    
    3. **Scegli target e tono** (tecnico, pratico, divulgativo)
    
    4. **Seleziona fonti** normative e banche dati
    
    5. **Specifica tipo articolo** (normativo vs procedurale)
    
    6. **Per guide pratiche:** attiva immagini procedurali
    
    7. **Scegli struttura** e formattazione Wix
    
    8. **Genera prompt** e copia in Claude/ChatGPT
    
    ---
    
    ### 📋 PROTOCOLLO COPYRIGHT
    
    Questo generatore vincola l'AI a:
    - Citare fonti, NON copiare testi
    - Usare solo massime ufficiali Cassazione
    - Parafrasare con attribuzione
    - Immagini SOLO se pertinenti (altrimenti niente)
    
    ---
    
    ### 🌐 OUTPUT WIX-READY
    
    L'articolo generato è formattato per:
    - Editor Wix (H1/H2/H3, testo giustificato)
    - SEO (meta description, slug, parole chiave)
    - Mobile-first (paragrafi brevi)
    - Professionale (citazioni puntuali)
    
    ---
    
    ### 🎯 IMMAGINI PROCEDURALI
    
    Per guide pratiche (es. "collegamento POS"):
    - L'AI cerca immagini PERTINENTI
    - Se non trova: NON mette immagini decorative
    - Suggerisce cosa servirebbe
    - Indica come crearle (screenshot/foto)
    """)
    
    st.markdown("---")
    st.markdown("**Versione:** v3.0_2026-03")
    st.markdown("**Sito:** www.studiopratici.com")
    st.markdown("**Ottimizzato per:** Claude + ChatGPT")
    st.markdown("**Fonti:** 100+ banche dati e riviste specializzate")
