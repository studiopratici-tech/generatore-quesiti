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
        "News Normative"
    ])

st.markdown("---")

# TITOLO E SEO
st.subheader("🎯 TITOLO E SEO")
col1, col2 = st.columns(2)
with col1:
    titolo_articolo = st.text_input("Titolo dell'articolo", placeholder="Es: Nuove scadenze fiscali 2026: cosa cambia per i professionisti")
    meta_descrizione = st.text_area("Meta descrizione (max 160 caratteri)", 
        placeholder="Breve sintesi per Google. Es: Guida alle nuove scadenze fiscali 2026 per professionisti: adempimenti, termini, sanzioni.",
        height=70)
with col2:
    parole_chiave = st.text_area("Parole chiave SEO (separate da virgola)", 
        placeholder="scadenze fiscali 2026, professionisti, adempimenti, Agenzia delle Entrate")
    lunghezza_articolo = st.selectbox("Lunghezza stimata", ["Breve (500-800 parole)", "Medio (800-1500 parole)", "Lungo (1500-2500 parole)"])

# TARGET E TONO
st.markdown("---")
st.subheader("👥 TARGET E STILE")
col1, col2 = st.columns(2)
with col1:
    target = st.selectbox("Destinatari", [
        "Professionisti dello studio (tecnico)",
        "Clienti dello studio (chiaro ma professionale)",
        "Pubblico generale (divulgativo)",
        "Misto (professionisti + clienti)"
    ])
with col2:
    tono = st.selectbox("Tono di voce", [
        "Tecnico-normativo (preciso, citazioni puntuali)",
        "Professionale-discorsivo (chiaro ma autorevole)",
        "Divulgativo (semplice, esempi pratici)",
        "Ibrido (tecnico + spiegazioni accessibili)"
    ])

# FONTI DA CITARE
st.markdown("---")
st.subheader("📚 FONTI NORMATIVE DA UTILIZZARE")
col1, col2, col3 = st.columns(3)
with col1:
    fonte_gazzetta = st.checkbox("Gazzetta Ufficiale / Normattiva")
    fonte_eurlex = st.checkbox("Regolamenti UE / EUR-Lex")
    fonte_agenzia_entrate = st.checkbox("Circolari Agenzia delle Entrate")
with col2:
    fonte_inps = st.checkbox("Circolari INPS")
    fonte_cassazione = st.checkbox("Massime Cassazione (ufficiali)")
    fonte_regionale = st.checkbox("Normativa Regionale")
with col3:
    fonte_comunale = st.checkbox("Regolamenti Comunali")
    fonte_ivass = st.checkbox("Regolamenti IVASS")
    fonte_altro = st.text_input("Altra fonte specifica", placeholder="Es: Il Sole 24 Ore, Fiscal Focus")

# IMMAGINI ROYALTY-FREE
st.markdown("---")
st.subheader("🖼️ IMMAGINI (ROYALTY-FREE)")
col1, col2 = st.columns(2)
with col1:
    suggerisci_immagini = st.checkbox("Suggerisci immagini royalty-free")
    tipo_immagine = st.selectbox("Tipo immagine", [
        "Concettuale (es: bilancia, documenti, calendario)",
        "Professionale (es: ufficio, professionista al lavoro)",
        "Tecnica (es: grafici, tabelle, flowchart)",
        "Nessuna immagine"
    ])
with col2:
    if suggerisci_immagini:
        piattaforme = st.multiselect("Piattaforme preferite", [
            "Unsplash", "Pexels", "Pixabay", "Freepik (con attribuzione)"
        ], default=["Unsplash", "Pexels"])
        termini_ricerca = st.text_input("Termini di ricerca immagine", 
            placeholder="Es: tax calendar, professional office, legal documents")

# STRUTTURA ARTICOLI
st.markdown("---")
st.subheader("📐 STRUTTURA RICHIESTA")
struttura = st.multiselect("Seleziona le sezioni da includere", [
    "Titolo accattivante + sottotitolo",
    "Sommario/esecutivo iniziale (3-4 righe)",
    "Inquadramento normativo di riferimento",
    "Analisi puntuale con citazioni (fonte + articolo + comma + data)",
    "Applicazione pratica al caso tipo",
    "Prassi operative e suggerimenti procedurali",
    "Eventuali lacune o zone grigie (dichiarate esplicitamente)",
    "Conclusioni operative per il lettore",
    "Box 'Da ricordare' con punti chiave",
    "Riferimenti normativi completi in fondo"
], default=[
    "Titolo accattivante + sottotitolo",
    "Sommario/esecutivo iniziale (3-4 righe)",
    "Inquadramento normativo di riferimento",
    "Analisi puntuale con citazioni (fonte + articolo + comma + data)",
    "Applicazione pratica al caso tipo",
    "Conclusioni operative per il lettore"
])

# GENERA ARTICOLO
st.markdown("---")
if st.button("🚀 GENERA PROMPT ARTICOLO", type="primary", use_container_width=True):
    if not titolo_articolo or not categoria:
        st.error("⚠️ Inserisci almeno titolo e categoria!")
    else:
        # COSTRUISCI IL PROMPT
        fonti_attive = []
        if fonte_gazzetta: fonti_attive.append("Gazzetta Ufficiale / Normattiva")
        if fonte_eurlex: fonti_attive.append("Regolamenti UE / EUR-Lex")
        if fonte_agenzia_entrate: fonti_attive.append("Circolari Agenzia delle Entrate")
        if fonte_inps: fonti_attive.append("Circolari INPS")
        if fonte_cassazione: fonti_attive.append("Massime Cassazione (ufficiali)")
        if fonte_regionale: fonti_attive.append("Normativa Regionale")
        if fonte_comunale: fonti_attive.append("Regolamenti Comunali")
        if fonte_ivass: fonti_attive.append("Regolamenti IVASS")
        if fonte_altro: fonti_attive.append(fonte_altro)
        
        prompt = f"""
✍️ ARTICOLO PROFESSIONALE PER STUDIO PRATICI — www.studiopratici.com

📋 METADATI
Titolo: {titolo_articolo}
Categoria: {categoria}
Autore: {autore or 'Redazione Studio Pratici'}
Data pubblicazione: {data_pubblicazione or 'Da definire'}
Target: {target}
Tono: {tono}
Lunghezza: {lunghezza_articolo}

🔍 SEO
Meta descrizione: {meta_descrizione or 'Da definire (max 160 caratteri)'}
Parole chiave: {parole_chiave or 'Da definire'}

📚 FONTI NORMATIVE DA CITARE (SOLO QUESTE)
{chr(10).join(['✓ ' + f for f in fonti_attive]) if fonti_attive else '✓ Fonti normative certe e verificabili (Gazzetta Ufficiale, Normattiva, EUR-Lex, Cassazione, siti .gov.it)'}

Formato citazione obbligatorio: [Fonte] [Tipo atto] n.[X] del [data], art.[Y], comma [Z]
Esempio: Agenzia delle Entrate, Circolare n. 9/E del 14/02/2024, art. 1, comma 54

📐 STRUTTURA RICHIESTA
{chr(10).join(['• ' + s for s in struttura])}

🎯 ISTRUZIONI VINCOLANTI PER LA REDAZIONE

1. FONTI E COPYRIGHT
   ✓ Usa SOLO fonti normative certe e pubblicamente accessibili
   ✓ Cita sempre: fonte, numero, data, articolo, comma
   ✓ NON copiare testi integrali: parafrasa con attribuzione
   ✓ Per sentenze: cita solo massime ufficiali Cassazione, non il testo integrale
   ✓ Per articoli di dottrina: cita autore, testata, data, link se disponibile
   ✓ Rispetta il diritto d'autore: citazioni brevi e finalizzate a commento/critica

2. STILE DI SCRITTURA
   • Italiano chiaro e professionale, adatto al target selezionato
   • Evita gergo eccessivo se il target non è tecnico
   • Usa connettivi logici: "pertanto", "di conseguenza", "inoltre"
   • Struttura discorsiva: evita elenchi puntati se non necessari

3. CONTENUTO NORMATIVO
   • Inquadra sempre il contesto normativo prima dell'analisi
   • Spiega il PERCHÉ della norma, non solo il COSA
   • Se la norma è ambigua o lacunosa, dichiaralo esplicitamente
   • Non usare "si ritiene che", "prassi consolidata" senza fonte certa

4. APPLICAZIONE PRATICA
   • Traduci la norma in indicazioni operative per il lettore
   • Se rilevante: indica scadenze, modulistica, portali ufficiali
   • Suggerisci procedure verificabili (es: "accedere al portale Agenzia delle Entrate con SPID")

5. IMMAGINI (se richieste)
   • Suggerisci SOLO immagini royalty-free da: {', '.join(piattaforme) if suggerisci_immagini and piattaforme else 'Unsplash, Pexels, Pixabay'}
   • Fornisci termini di ricerca specifici: "{termini_ricerca}" se specificato
   • Indica sempre la licenza (es: "Unsplash License — libera per uso commerciale")
   • Suggerisci didascalie descrittive e SEO-friendly

6. SEO E FORMATTAZIONE WIX
   • Usa H1 per il titolo, H2 per le sezioni principali, H3 per sottosezioni
   • Inserisci parole chiave in modo naturale (non keyword stuffing)
   • Meta descrizione: max 160 caratteri, accattivante, con CTA implicito
   • Lunghezza paragrafi: 3-5 righe per leggibilità mobile
   • Usa grassetto per concetti chiave, corsivo per termini tecnici

7. DIVIETO ASSOLUTO
   ✗ Opinioni personali non supportate da fonti
   ✗ "Si ritiene che", "prassi comune" senza citazione certa
   ✗ Copia-incolla di testi protetti da copyright
   ✗ Immagini senza licenza chiara o attribuzione richiesta
   ✗ Informazioni non verificate o datate

✅ OUTPUT RICHIESTO
Redigi l'articolo completo, pronto per l'editor Wix, con:
- Titolo H1 + sottotitolo
- Sommario iniziale (3-4 righe)
- Corpo articolo con sezioni H2/H3
- Citazioni normative nel formato indicato
- Box "Da ricordare" (se selezionato)
- Riferimenti normativi completi in fondo
- Suggerimenti immagini con termini di ricerca e licenza (se richiesto)
- Meta descrizione e parole chiave per SEO

L'articolo deve sembrare scritto da un professionista senior dello studio, autorevole ma accessibile.
"""
        
        st.success("✅ Prompt articolo generato!")
        st.code(prompt, language="markdown")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Scarica articolo .txt",
                data=prompt,
                file_name=f"articolo_{categoria.replace(' ', '_')}_{data_pubblicazione}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.info("💡 Copia il testo e incollalo in ChatGPT. L'output sarà pronto per Wix!")

# SIDEBAR
with st.sidebar:
    st.header("ℹ️ Come usare questa pagina")
    st.markdown("""
    ### Per creare articoli professionali:
    
    1. **Compila i metadati** (titolo, categoria, autore, data)
    
    2. **Definisci SEO** (meta descrizione, parole chiave)
    
    3. **Scegli target e tono** (tecnico, divulgativo, misto)
    
    4. **Seleziona le fonti** normative da citare
    
    5. **(Opzionale) Attiva suggerimenti immagini** royalty-free
    
    6. **Scegli la struttura** dell'articolo
    
    7. **Clicca "Genera Prompt"** e copia in ChatGPT
    
    ---
    
    ### 📋 PROTOCOLLO COPYRIGHT
    
    Questo generatore vincola l'AI a:
    - Citare fonti, non copiare testi
    - Usare solo massime ufficiali Cassazione
    - Parafrasare con attribuzione
    - Suggerire solo immagini royalty-free
    
    ---
    
    ### 🌐 OUTPUT WIX-READY
    
    L'articolo generato è formattato per:
    - Editor Wix (H1/H2/H3, paragrafi brevi)
    - SEO (meta description, parole chiave)
    - Mobile-first (leggibilità)
    """)
    
    st.markdown("---")
    st.markdown("**Versione:** v1.0_2026-03")
    st.markdown("**Sito:** www.studiopratici.com")
