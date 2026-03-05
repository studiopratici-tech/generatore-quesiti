import streamlit as st

st.set_page_config(page_title="Quesiti Assicurativi", page_icon="🛡️", layout="wide")

st.title("🛡️ QUESITI ASSICURATIVI — SISTEMA NORM-ONLY")
st.markdown("*RCA, RC Professionale, Danni, Vita, Tutela Legale + Tecnici Auto*")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    data = st.date_input("📅 Data", value=None)
with col2:
    operatore = st.text_input("✍️ A cura di")
with col3:
    riferimento = st.text_input("📁 Riferimento")

st.markdown("---")
st.subheader("👥 FIGURE DA ATTIVARE")

# SEZIONE 1: PROFESSIONISTI ASSICURATIVI
with st.expander("📊 PROFESSIONISTI ASSICURATIVI", expanded=True):
    col1, col2, col3 = st.columns(3)
    assicurativa = {
        "Esperto Assicurazioni RCA/Danni": col1.checkbox("Esperto RCA/Danni"),
        "Esperto Previdenza/Vita": col2.checkbox("Esperto Previdenza/Vita"),
        "Esperto Danni Generici": col3.checkbox("Esperto Danni Generici"),
        "Perito Assicurativo": col1.checkbox("Perito Assicurativo"),
        "Liquidatore Sinistri": col2.checkbox("Liquidatore Sinistri"),
        "Esperto IVASS": col3.checkbox("Esperto IVASS"),
        "Broker Assicurativo": col1.checkbox("Broker Assicurativo"),
        "Agente di Assicurazione": col2.checkbox("Agente di Assicurazione"),
        "Esperto RC Professionale": col3.checkbox("Esperto RC Professionale"),
        "Esperto Tutela Legale": col1.checkbox("Esperto Tutela Legale"),
        "Esperto D&O": col2.checkbox("Esperto D&O"),
        "Esperto Cyber Risk": col3.checkbox("Esperto Cyber Risk"),
    }

# SEZIONE 2: TECNICI SETTORE AUTO (NUOVO!)
with st.expander("🚗 TECNICI SETTORE AUTO", expanded=True):
    col1, col2, col3 = st.columns(3)
    tecnici_auto = {
        "Carrozziere/Perito Danni Auto": col1.checkbox("Carrozziere/Perito Danni Auto"),
        "Meccanico/Perito Meccanico": col2.checkbox("Meccanico/Perito Meccanico"),
        "Perito Valutazione Veicoli": col3.checkbox("Perito Valutazione Veicoli"),
        "Esperto Allestimenti/Accessori": col1.checkbox("Esperto Allestimenti/Accessori"),
        "Esperto Veicoli Elettrici/Ibridi": col2.checkbox("Esperto Veicoli Elettrici/Ibridi"),
        "Esperto Veicoli Storici/Epoca": col3.checkbox("Esperto Veicoli Storici/Epoca"),
        "Esperto Veicoli Commerciali": col1.checkbox("Esperto Veicoli Commerciali"),
        "Esperto Veicoli Noleggio/Flotte": col2.checkbox("Esperto Veicoli Noleggio/Flotte"),
    }

# SEZIONE 3: FONTI TECNICHE E VALUTATIVE (NUOVO!)
with st.expander("📚 FONTI TECNICHE E VALUTATIVE", expanded=False):
    col1, col2, col3 = st.columns(3)
    fonti_tecniche = {
        "Quattroruote/Valutazioni": col1.checkbox("Quattroruote (valutazioni)"),
        "Automobile Club d'Italia (ACI)": col2.checkbox("ACI (dati tecnici/tariffe)"),
        "Eurotax/Blue Book": col3.checkbox("Eurotax/Blue Book"),
        "Listini Case Madri": col1.checkbox("Listini Case Madri"),
        "Riviste Settore Auto": col2.checkbox("Riviste specializzate settore auto"),
        "Portali Usato Certificato": col3.checkbox("Portali usato certificato"),
        "Perizie CTU/CTP": col1.checkbox("Perizie CTU/CTP giudiziarie"),
        "Banca Dati Sinistri ANIA": col2.checkbox("Banca Dati Sinistri ANIA"),
    }

# RACCOGLI TUTTE LE FIGURE SELEZIONATE
figure_selezionate = []
for categoria in [assicurativa, tecnici_auto, fonti_tecniche]:
    for figura, selezionato in categoria.items():
        if selezionato:
            figure_selezionate.append(figura)

# ALTRE FIGURE
col1, col2 = st.columns(2)
with col1:
    altra = st.checkbox("Aggiungi figura/fonte non in elenco")
with col2:
    if altra:
        specifica = st.text_input("Specifica:")
        if specifica:
            figure_selezionate.append(specifica)

# TIPOLOGIA SINISTRO/POLIZZA
st.markdown("---")
st.subheader("📋 TIPOLOGIA")
tipologia = st.selectbox("Seleziona la tipologia", [
    "Sinistro RCA - Danni a veicoli",
    "Sinistro RCA - Danni a persone",
    "Sinistro RCA - Dinamica controversa",
    "Valutazione pre-sinistro veicolo",
    "Valutazione danni/riparazione",
    "Veicolo con allestimenti/accessori",
    "Veicolo elettrico/ibrido",
    "Veicolo storico/epoca",
    "Veicolo commerciale/trasporto",
    "Polizza RC Professionale",
    "Polizza Tutela Legale",
    "Infortunio/Malattia conducente",
    "D&O Claim",
    "Cyber Risk/Data Breach",
    "Altro"
])

# DOMANDA
st.markdown("---")
st.subheader("❓ DOMANDA")
domanda = st.text_area("Descrivi il quesito", height=120,
    placeholder="Es: Sinistro RCA con veicolo allestito con accessori aftermarket. Il perito della compagnia non li ha valutati nel danno. Quali riferimenti per il riconoscimento del valore?")

# CONTESTO ASSICURATIVO + TECNICO AUTO
st.markdown("---")
st.subheader("📌 CONTESTO")
col1, col2 = st.columns(2)
with col1:
    compagnia = st.text_input("Compagnia Assicurativa")
    polizza_n = st.text_input("Numero Polizza")
    targa_veicolo = st.text_input("Targa veicolo (opzionale)", placeholder="Solo se utile")
    marca_modello = st.text_input("Marca/Modello veicolo")
with col2:
    anno_immatricolazione = st.number_input("Anno immatricolazione", min_value=1900, max_value=2026, step=1)
    km_veicolo = st.number_input("Chilometraggio (km)", min_value=0, step=1000)
    allestimenti = st.text_area("Allestimenti/Accessori rilevanti", placeholder="Es: impianto GPL, cerchi lega, interni pelle...")
    gia_denunciato = st.checkbox("Sinistro già denunciato")

# DATI SINISTRO
st.markdown("---")
st.subheader("📍 DATI SINISTRO")
col1, col2, col3 = st.columns(3)
with col1:
    data_sinistro = st.date_input("Data sinistro", value=None)
with col2:
    luogo_sinistro = st.text_input("Luogo sinistro", placeholder="Città/provincia")
with col3:
    dinamica_breve = st.text_input("Dinamica (breve)", placeholder="Es: tamponamento, incrocio...")

# URGENZA E OUTPUT
col1, col2 = st.columns(2)
with col1:
    urgenza = st.selectbox("Urgenza", ["Normale", "Entro 48h", "Oggi"])
with col2:
    output_pdf = st.checkbox("Richiesta output PDF formattato")

# GENERA PROMPT
st.markdown("---")
if st.button("🚀 GENERA PROMPT ASSICURATIVO", type="primary", use_container_width=True):
    if not figure_selezionate or not domanda:
        st.error("⚠️ Seleziona almeno una figura/fonte e scrivi la domanda!")
    else:
        prompt = f"""
🔷 QUESITO ASSICURATIVO CERTO — SISTEMA NORM-ONLY

📋 DATI GENERALI
Data: {data} | Operatore: {operatore} | Riferimento: {riferimento}
Tipologia: {tipologia}

👥 FIGURE E FONTI DA ATTIVARE
{chr(10).join(['  ▸ ' + fig for fig in figure_selezionate])}

❓ DOMANDA
{domanda}

📌 CONTESTO TECNICO-ASSICURATIVO
• Compagnia: {compagnia or 'Non specificato'}
• Polizza n.: {polizza_n or 'Non specificato'}
• Veicolo: {marca_modello} ({anno_immatricolazione}) - {km_veicolo or 'N/A'} km
• Targa: {targa_veicolo or 'Non inserita'}
• Allestimenti/Accessori: {allestimenti or 'Nessuno specificato'}
• Luogo sinistro: {luogo_sinistro or 'Non specificato'}
• Dinamica: {dinamica_breve or 'Non specificata'}
• Data sinistro: {data_sinistro or 'Non specificata'}
• Già denunciato: {'Sì' if gia_denunciato else 'No'}
• Urgenza: {urgenza}
• Output PDF: {'Richiesto' if output_pdf else 'Non richiesto'}

🎯 ISTRUZIONI VINCOLANTI
Sei un professionista senior specializzato in diritto assicurativo e valutazione tecnica veicoli.

▌ FONTI NORMATIVE E TECNICHE (SOLO QUESTE)
✓ Codice Assicurazioni Private (D.Lgs. 209/2005)
✓ Regolamenti IVASS ufficiali
✓ Condizioni Generali di Polizza (se fornite o reperibili)
✓ Norme CONSAP per RCA
✓ Circolari ANIA ufficiali
✓ Cassazione: massime ufficiali su responsabilità/liquidazione
✓ Fonti tecniche auto: Quattroruote, Eurotax, ACI, listini case madri (solo edizioni ufficiali)
✓ Riviste specializzate: solo articoli firmati da esperti con fonti verificabili

Formato citazione normativa: [Fonte] [Tipo] n.[X] del [data], art.[Y], c.[Z]
Formato citazione tecnica: [Fonte] [Edizione/Data], pag./tab. [rif.]

▌ STILE DI RISPOSTA
• Italiano discorsivo, come parere scritto tra colleghi dello studio
• Struttura: sintesi iniziale → inquadramento normativo/tecnico → applicazione al caso → riferimenti pratici
• Evita elenchi puntati se non strettamente necessari (es. commi di legge, voci di tariffa)

▌ ELEMENTI SPECIFICI RCA + VALUTAZIONE AUTO
• Se rilevante: analizza dinamica del sinistro, concorso di colpa, franchigie, massimali
• Se rilevante: valuta il veicolo pre-sinistro con fonti tecniche certificate (Quattroruote, Eurotax, ACI)
• Se rilevante: considera allestimenti/accessori aftermarket solo se documentati e normativamente riconoscibili
• Se rilevante: cita articoli specifici delle Condizioni Generali su "valore a nuovo", "deprezzamento", "accessori"
• Se rilevante: indica procedura di liquidazione, tempistiche IVASS, modulistica CONSAP

▌ ONESTÀ INTELLETTUALE
• Norma, polizza o fonte tecnica ambigua? Dichiaralo esplicitamente
• NO "si ritiene che", "prassi di mercato", "orientamento prevalente" senza fonte certa
• Zone grigie? Indica organo competente per reclamo/interpello (IVASS, Arbitro Assicurazioni, Giudice)
• Dati tecnici mancanti (es. quotazione veicolo)? Indica dove reperirli ufficialmente

▌ STRUTTURA OBBLIGATORIA
1. Riferimenti normativi e tecnici (fonte + articolo/voce + data/edizione)
2. Applicazione al caso (SOLO se normativamente/certamente fondata)
3. Parere degli Esperti/Fonti Attivate (uno per figura/fonte selezionata)
4. Lacune normative, contrattuali o tecniche (esplicitamente dichiarate)
5. [Se richiesto] Output PDF: impaginazione professionale con logo studio, margini 2cm, font Times/Helvetica

▌ DIVIETO ASSOLUTO
✗ Opinioni personali o valutazioni "a occhio"
✗ "Prassi di mercato" senza fonte documentata
✗ Interpretazioni creative delle Condizioni di Polizza o delle quotazioni tecniche
✗ Risposta senza certezza normativa, contrattuale o tecnica verificabile

✅ RISPONDI ORA AL QUESITO ASSICURATIVO
"""
        st.success("✅ Prompt generato!")
        st.code(prompt, language="markdown")
        st.download_button(
            label="📥 Scarica .txt",
            data=prompt,
            file_name=f"quesito_ass_{data}_{riferimento or 'senza_rif'}.txt",
            mime="text/plain",
            use_container_width=True
        )
