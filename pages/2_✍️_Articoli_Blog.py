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
        placeholder="Breve sintesi per Google. Es: Guida completa al collegamento POS e registratore di cassa: procedura passo-passo, adempimenti, sanzioni.",
        height=70)
with col2:
    parole_chiave = st.text_area("Parole chiave SEO (separate da virgola)", 
        placeholder="collegamento POS registratore di cassa, adempimenti 2026, guida pratica")
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
st.markdown("*Seleziona le fonti da utilizzare e citare*")

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
    fonte_comunale = st.checkbox("Regolamenti Comunali")
with col3:
    fonte_ivass = st.checkbox("Regolamenti IVASS")
    fonte_consap = st.checkbox("Norme CONSAP")
    fonte_altro = st.text_input("Altra fonte specifica", placeholder="Es: Ministero Sviluppo Economico")

st.markdown("---")
st.subheader("📰 BANCHE DATI E PORTALI SPECIALIZZATI")
col1, col2, col3 = st.columns(3)
with col1:
    banco_sole24ore = st.checkbox("Il Sole 24 Ore (dottrina/prassi)", value=True)
    banco_edotto = st.checkbox("Edotto (guide/approfondimenti)")
    banco_fiscalfocus = st.checkbox("Fiscal Focus (analisi tecniche)")
with col2:
    banco_italiaoggi = st.checkbox("Italia Oggi (news/normativa)")
    banco_quattroruote = st.checkbox("Quattroruote/Eurotax (settore auto)")
    banco_aci = st.checkbox("ACI (dati tecnici/tariffe)")
with col3:
    banco_portale_ade = st.checkbox("Portale Agenzia delle Entrate (guide operative)")
    banco_portale_inps = st.checkbox("Portale INPS (procedure)")
    banco_altri = st.text_area("Altri portali/banche dati", placeholder="Es: ENEA, INAIL, Camere di Commercio...")

# IMMAGINI E CONTENUTI VISIVI
st.markdown("---")
st.subheader("🖼️ IMMAGINI E CONTENUTI VISIVI")
col1, col2 = st.columns(2)
with col1:
    tipo_contenuto = st.radio("Tipo di articolo", [
        "Articolo normativo/dottrinale (poche immagini)",
        "Guida pratica/procedurale (immagini esplicative)",
        "Approfondimento tecnico (grafici/tabelle)",
        "News breve (1 immagine di contesto)"
    ])
with col2:
    if "procedurale" in tipo_contenuto or "tecnica" in tipo_contenuto:
        immagini_procedurali = st.checkbox("Richiedi immagini procedurali passo-passo", value=True)
        termini_ricerca_custom = st.text_input("Termini specifici per ricerca immagini", 
            placeholder="Es: 'POS collegato registratore di cassa', 'schermata portale AdE'")

# PIATTAFORME IMMAGINI
if tipo_contenuto != "Articolo normativo/dottrinale (poche immagini)":
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
        screenshot_proprio = st.checkbox("Screenshot da portali ufficiali (fair use)")
        nessuna_immagine = st.checkbox("Nessuna immagine")

# STRUTTURA E IMPAGINAZIONE
st.markdown("---")
st.subheader("📐 STRUTTURA E IMPAGINAZIONE")
st.markdown("*Seleziona gli elementi da includere nell'articolo*")

elementi_struttura = st.multiselect("Sezioni dell'articolo", [
    "Titolo H1 accattivante + sottotitolo esplicativo",
    "Sommario/esecutivo iniziale (3-5 righe)",
    "Indice/indice dei contenuti (per articoli lunghi)",
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

# FORMATTAZIONE WIX
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
        if fonte_consap: fonti_normative.append("Norme CONSAP")
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
        prompt = f"""
✍️ ARTICOLO PROFESSIONALE PER STUDIO PRATICI — www.studiopratici.com
═══════════════════════════════════════════════════════════════════════

📋 METADATI EDITORIALI
Titolo: {titolo_articolo}
Categoria: {categoria}
Autore: {autore or 'Redazione Studio Pratici'}
Data pubblicazione: {data_pubblicazione or 'Da definire'}
Target: {target}
Tono: {tono}
Lunghezza: {lunghezza_articolo}

🔍 OTTIMIZZAZIONE SEO
Meta descrizione: {meta_descrizione or 'Da definire (max 160 caratteri)'}
Parole chiave: {parole_chiave or 'Da definire'}

📚 FONTI NORMATIVE DA UTILIZZARE (SOLO QUESTE)
{chr(10).join(['✓ ' + f for f in fonti_normative]) if fonti_normative else '✓ Fonti normative certe e verificabili'}

📰 BANCHE DATI E DOTTRINA AUTORIZZATA
{chr(10).join(['✓ ' + b for b in banche_dati]) if banche_dati else '✓ Dottrina da portali specializzati (Sole 24 Ore, Edotto, Fiscal Focus, Italia Oggi)'}

Formato citazione OBBLIGATORIO:
• Normativa: [Fonte] [Tipo atto] n.[X] del [data], art.[Y], comma [Z]
  Es: Agenzia delle Entrate, Circolare n. 9/E del 14/02/2024, art. 1, comma 54
• Interpelli: [Organo] Risposta Interpello n.[X] del [data]
  Es: Agenzia delle Entrate, Risposta Interpello n. 123 del 15/03/2024
• Cassazione: Cass. [Sezione] n.[X] del [data] (massima ufficiale)
  Es: Cass. Civ. Sez. Trib. n. 12345 del 10/05/2024
• Dottrina: [Autore], "[Titolo]", [Testata], [Data]
  Es: Rossi M., "Nuove scadenze fiscali", Il Sole 24 Ore, 20/01/2024

📐 STRUTTURA RICHIESTA DELL'ARTICOLO
{chr(10).join(['• ' + s for s in elementi_struttura])}

🎨 IMPAGINAZIONE E FORMATTAZIONE (WIX-READY)
• Testo giustificato: {('SÌ' if testo_giustificato else 'NO')}
• Paragrafi: {('brevi (3-5 righe)' if paragrafi_brevi else 'standard')}
• Gerarchia titoli: {('H1 > H2 > H3' if uso_h2_h3 else 'H1 > H2')}
• Evidenziazioni: {('grassetto per concetti chiave, corsivo per termini tecnici' if grassetto_chiave else 'minime')}
• Elenchi: {('solo se strettamente necessari' if elenchi_minimali else 'liberi')}

🖼️ GESTIONE IMMAGINI E CONTENUTI VISIVI
Tipo articolo: {tipo_contenuto}
{"✓ IMMAGINI PROCEDURALI RICHIESTE" if 'procedurale' in tipo_contenuto or 'tecnica' in tipo_contenuto else "✓ POche immagini (solo di contesto)"}

ISTRUZIONI SPECIFICHE PER LE IMMAGINI:
"""

        if 'procedurale' in tipo_contenuto or 'tecnica' in tipo_contenuto:
            prompt += f"""
1. ANALISI DEL CONTENUTO:
   • Identifica i passaggi operativi che richiedono illustrazione visiva
   • Per ogni passaggio critico, valuta se un'immagine può migliorare la comprensione
   • Esempio: "Guida collegamento POS e registratore di cassa" → servono immagini che mostrano:
     - Il POS e il registratore di cassa
     - I cavi/connessioni (USB, Ethernet, WiFi)
     - Le schermate di configurazione
     - Il procedimento passo-passo

2. RICERCA IMMAGINI PERTINENTI:
   • Piattaforme autorizzate: {', '.join(piattaforme_img) if piattaforme_img else 'Unsplash, Pexels'}
   • Termini di ricerca: "{termini_ricerca_custom if 'termini_ricerca_custom' in locals() and termini_ricerca_custom else titolo_articolo}"
   • Cerca immagini che mostrino ESPPLICITAMENTE il procedimento/operazione
   
3. CRITERI DI SELEZIONE:
   • PERTINENZA: L'immagine deve mostrare ESATTAMENTE ciò che descrive il testo
   • QUALITÀ: Alta risoluzione, professionale, leggibile
   • ATTUALITÀ: Dispositivi/software recenti (non obsoleti)
   • LICENZA: Solo royalty-free o fair use per screenshot portali ufficiali
   
4. SE NON TROVI IMMAGINI PERTINENTI:
   • NON inserire immagini generiche o decorative
   • Scrivi: "[IMMAGINE: descrivi cosa servirebbe ma non è stata trovata]"
   • Suggerisci: "Scattare screenshot proprio o creare grafica ad hoc"
   
5. DIDASCALIE OBBLIGATORIE:
   • Ogni immagine deve avere didascalia descrittiva e SEO-friendly
   • Formato: "Fig. X - [Descrizione breve ma completa]"
   • Esempio: "Fig. 1 - Collegamento cavo USB tra POS e registratore di cassa"

"""
        else:
            prompt += """
1. IMMAGINI MINIMALI:
   • Solo 1-2 immagini di contesto/introduzione
   • Evita immagini decorative superflue
   • Priorità a: concetti astratti, simboli professionali, infografiche

"""

        prompt += f"""
2. FONTI CONSENTITE: {', '.join(piattaforme_img) if piattaforme_img else 'Unsplash, Pexels, Pixabay'}

═══════════════════════════════════════════════════════════════════════
🎯 ISTRUZIONI VINCOLANTI PER LA REDAZIONE
═══════════════════════════════════════════════════════════════════════

1. FONTI E COPYRIGHT - RISPETTO ASSOLUTO
   ✓ Usa SOLO fonti normative certe e pubblicamente accessibili
   ✓ Cita SEMPRE: fonte, numero, data, articolo, comma
   ✓ Per interpelli: cita solo risposte ufficiali AdE/INPS/Ministeri
   ✓ Per dottrina: cita autore, testata, data (Sole 24 Ore, Edotto, Fiscal Focus, Italia Oggi)
   
   ✗ VIETATO:
   • Copiare testi integrali protetti da copyright
   • Parafrasare senza attribuzione
   • Usare "si ritiene che", "prassi consolidata" senza fonte certa
   • Citare sentenze senza numero/data/sezione

2. STILE DI SCRITTURA PROFESSIONALE
   • Adatta il linguaggio al target: {target}
   • Tono: {tono}
   • Usa connettivi logici: "pertanto", "di conseguenza", "inoltre", "tuttavia"
   • Struttura discorsiva ma organizzata (evita muri di testo)
   • Spiega il PERCHÉ normativo, non solo il COSA

3. RIGORE NORMATIVO
   • Inquadra sempre il contesto prima dell'analisi
   • Se la norma è ambigua/lacunosa, dichiaralo ESPPLICITAMENTE
   • Per zone grigie: indica organo competente per interpello
   • NON esprimere opinioni personali non supportate da fonti

4. APPLICAZIONE PRATICA E PROCEDURE
   • Traduci la norma in indicazioni OPERATIVE per il lettore
   • Se guida procedurale: step-by-step numerati e chiari
   • Indica: scaden
