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

# FONTI DA CITARE
st.markdown("---")
st.subheader("📚 FONTI NORMATIVE E DOTTRINALI")

col1, col2, col3 = st.columns(3)
with col1:
    fonte_gazzetta = st.checkbox("Gazzetta Ufficiale / Normattiva", value=True)
    fonte_eurlex = st.checkbox("Regolamenti UE / EUR-Lex")
    fonte_agenzia_entrate = st.checkbox("Circolari Agenzia delle Entrate", value=True)
    fonte_interpelli_ade = st.checkbox("Risposte Interpello AdE", value=True)
with col2:
    fonte_inps = st.checkbox("Circolari/Messaggi INPS")
    fonte_cassazione = st.checkbox("Massime Cassazione (ufficiali)")
    fonte_regionale = st.checkbox("Normativa Regionale")
with col3:
    fonte_comunale = st.checkbox("Regolamenti Comunali")
    fonte_ivass = st.checkbox("Regolamenti IVASS")
    fonte_altro = st.text_input("Altra fonte specifica", placeholder="Es: Ministero Sviluppo Economico")

st.markdown("---")
st.subheader("📰 BANCHE DATI SPECIALIZZATE")
col1, col2, col3 = st.columns(3)
with col1:
    banco_sole24ore = st.checkbox("Il Sole 24 Ore", value=True)
    banco_edotto = st.checkbox("Edotto")
    banco_fiscalfocus = st.checkbox("Fiscal Focus")
with col2:
    banco_italiaoggi = st.checkbox("Italia Oggi")
    banco_quattroruote = st.checkbox("Quattroruote/Eurotax")
    banco_aci = st.checkbox("ACI")
with col3:
    banco_portale_ade = st.checkbox("Portale Agenzia delle Entrate")
    banco_portale_inps = st.checkbox("Portale INPS")
    banco_altri = st.text_input("Altri portali", placeholder="Es: ENEA, INAIL")

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
    unsplash = st.checkbox("Unsplash", value=True)
    pexels = st.checkbox("Pexels", value=True)
with col2:
    pixabay = st.checkbox("Pixabay")
    freepik = st.checkbox("Freepik (con attribuzione)")
with col3:
    screenshot_proprio = st.checkbox("Screenshot da portali ufficiali")
    nessuna_immagine = st.checkbox("Nessuna immagine")

# STRUTTURA
st.markdown("---")
st.subheader("📐 STRUTTURA E IMPAGINAZIONE")
elementi_struttura = st.multiselect("Sezioni dell'articolo", [
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
], default=[
    "Titolo H1 accattivante + sottotitolo esplicativo",
    "Sommario/esecutivo iniziale (3-5 righe)",
    "Inquadramento normativo di riferimento",
    "Analisi puntuale con citazioni (fonte + articolo + comma + data)",
    "Applicazione pratica con esempi concreti",
    "Conclusioni operative per il lettore"
])

# FORMATTAZIONE
st.markdown("---")
st.subheader("🎨 FORMATTAZIONE PER WIX")
col1, col2 = st.columns(2)
with col1:
    testo_giustificato = st.checkbox("Testo giustificato", value=True)
    paragrafi_brevi = st.checkbox("Paragrafi brevi (3-5 righe)", value=True)
    uso_h2_h3 = st.checkbox("Gerarchia H2/H3 per sottotitoli", value=True)
with col2:
    grassetto_chiave = st.checkbox("Grassetto per concetti chiave", value=True)
    corsivo_tecnico = st.checkbox("Corsivo per termini tecnici", value=True)
    elenchi_minimali = st.checkbox("Elenchi solo se necessari", value=True)

# GENERA ARTICOLO
st.markdown("---")
if st.button("🚀 GENERA PROMPT ARTICOLO PROFESSIONALE", type="primary", use_container_width=True):
    if not titolo_articolo or not categoria:
        st.error("⚠️ Inserisci almeno titolo e categoria!")
    else:
        # RACCOGLI FONTI
        fonti_normative = []
        if fonte_gazzetta: fonti_normative.append("Gazzetta Ufficiale / Normattiva")
        if fonte_eurlex: fonti_normative.append("Regolamenti UE / EUR-Lex")
        if fonte_agenzia_entrate: fonti_normative.append("Circolari Agenzia delle Entrate")
        if fonte_interpelli_ade: fonti_normative.append("Risposte Interpello AdE")
        if fonte_inps: fonti_normative.append("Circolari/Messaggi INPS")
        if fonte_cassazione: fonti_normative.append("Massime Cassazione (ufficiali)")
        if fonte_regionale: fonti_normative.append("Normativa Regionale")
        if fonte_comunale: fonti_normative.append("Regolamenti Comunali")
        if fonte_ivass: fonti_normative.append("Regolamenti IVASS")
        if fonte_altro: fonti_normative.append(fonte_altro)
        
        banche_dati = []
        if banco_sole24ore: banche_dati.append("Il Sole 24 Ore")
        if banco_edotto: banche_dati.append("Edotto")
        if banco_fiscalfocus: banche_dati.append("Fiscal Focus")
        if banco_italiaoggi: banche_dati.append("Italia Oggi")
        if banco_quattroruote: banche_dati.append("Quattroruote/Eurotax")
        if banco_aci: banche_dati.append("ACI")
        if banco_portale_ade: banche_dati.append("Portale Agenzia delle Entrate")
        if banco_portale_inps: banche_dati.append("Portale INPS")
        if banco_altri: banche_dati.append(banco_altri)
        
        piattaforme_img = []
        if unsplash: piattaforme_img.append("Unsplash")
        if pexels: piattaforme_img.append("Pexels")
        if pixabay: piattaforme_img.append("Pixabay")
        if freepik: piattaforme_img.append("Freepik (con attribuzione)")
        if screenshot_proprio: piattaforme_img.append("Screenshot da portali ufficiali")
        
        # COSTRUISCI IL PROMPT
        prompt = f
