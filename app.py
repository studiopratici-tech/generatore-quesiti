import streamlit as st

# CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Generatore Quesiti Norm-Only", layout="wide", page_icon="📋")

# TITOLO
st.title("📋 GENERATORE QUESITI NORMATIVI CERTI")
st.markdown("**Sistema NORM-ONLY** - Solo fonti certe, zero interpretazioni")
st.markdown("---")

# DATA E OPERATORE
col1, col2, col3 = st.columns(3)
with col1:
    data = st.date_input("📅 Data", value=None)
with col2:
    operatore = st.text_input("✍️ A cura di")
with col3:
    riferimento = st.text_input("📁 Riferimento")

st.markdown("---")

# FIGURE PROFESSIONALI - TUTTE LE CATEGORIE
st.subheader("👥 FIGURE DA ATTIVARE")
st.markdown("*Seleziona tutte le figure professionali rilevanti per il quesito*")

# CATEGORIA 1: LEGALE - AVVOCATI
with st.expander("⚖️ LEGALE - AVVOCATI", expanded=False):
    col1, col2, col3 = st.columns(3)
    legale = {
        "Avvocato Civilista": col1.checkbox("Avvocato Civilista"),
        "Avvocato Penalista": col2.checkbox("Avvocato Penalista"),
        "Avvocato Giuslavorista": col3.checkbox("Avvocato Giuslavorista"),
        "Avvocato Amministrativista": col1.checkbox("Avvocato Amministrativista"),
        "Avvocato Tributarista": col2.checkbox("Avvocato Tributarista"),
        "Avvocato Internazionalista": col3.checkbox("Avvocato Internazionalista"),
        "Avvocato Familiare": col1.checkbox("Avvocato Familiare"),
        "Avvocato Immigrazione": col2.checkbox("Avvocato Immigrazione"),
        "Avvocato Bancario/Finanziario": col3.checkbox("Avvocato Bancario/Finanziario"),
    }

# CATEGORIA 2: FISCALITÀ E LAVORO
with st.expander("💼 FISCALITÀ E LAVORO", expanded=False):
    col1, col2, col3 = st.columns(3)
    fiscalita = {
        "Commercialista Tributarista": col1.checkbox("Commercialista Tributarista"),
        "Commercialista Internazionalista": col2.checkbox("Commercialista Internazionalista"),
        "Consulente del Lavoro": col3.checkbox("Consulente del Lavoro"),
        "Ragioniere Esperto Contabile": col1.checkbox("Ragioniere Esperto Contabile"),
        "Revisore Legale dei Conti": col2.checkbox("Revisore Legale dei Conti"),
        "Responsabile Antiriciclaggio": col3.checkbox("Responsabile Antiriciclaggio"),
        "Esperto di Redazione Bilanci": col1.checkbox("Esperto di Redazione Bilanci"),
    }

# CATEGORIA 3: TECNICA ED EDILIZIA
with st.expander("🏗️ TECNICA ED EDILIZIA", expanded=False):
    col1, col2, col3 = st.columns(3)
    tecnica = {
        "Geometra/Perito Edile": col1.checkbox("Geometra/Perito Edile"),
        "Architetto/Pianificatore": col2.checkbox("Architetto/Pianificatore"),
        "Ingegnere Civile/Strutturista": col3.checkbox("Ingegnere Civile/Strutturista"),
        "Ingegnere Industriale/Impiantista": col1.checkbox("Ingegnere Industriale/Impiantista"),
        "Perito Industriale": col2.checkbox("Perito Industriale"),
        "Perito Agrario": col3.checkbox("Perito Agrario"),
        "Perito Chimico": col1.checkbox("Perito Chimico"),
        "Perito Elettrotecnico": col2.checkbox("Perito Elettrotecnico"),
        "Coordinatore Sicurezza Cantieri": col3.checkbox("Coordinatore Sicurezza Cantieri"),
    }

# CATEGORIA 4: SANITARIA
with st.expander("🏥 SANITARIA", expanded=False):
    col1, col2, col3 = st.columns(3)
    sanitaria = {
        "Medico FNOMCeO/ENPAM": col1.checkbox("Medico FNOMCeO/ENPAM"),
        "Medico Legale": col2.checkbox("Medico Legale"),
        "Farmacista/Esperto AIFA": col3.checkbox("Farmacista/Esperto AIFA"),
        "Infermiere": col1.checkbox("Infermiere"),
        "Tecnico Sanitario TSRM": col2.checkbox("Tecnico Sanitario TSRM"),
        "Psicologo/Psicoterapeuta": col3.checkbox("Psicologo/Psicoterapeuta"),
        "Veterinario": col1.checkbox("Veterinario"),
        "Ostetrica": col2.checkbox("Ostetrica"),
    }

# CATEGORIA 5: SINDACALE
with st.expander("🤝 SINDACALE", expanded=False):
    col1, col2, col3 = st.columns(3)
    sindacale = {
        "Sindacalista CGIL": col1.checkbox("Sindacalista CGIL"),
        "Sindacalista CISL": col2.checkbox("Sindacalista CISL"),
        "Sindacalista UIL": col3.checkbox("Sindacalista UIL"),
        "Sindacalista UGL": col1.checkbox("Sindacalista UGL"),
        "Sindacalista Professionisti Autonomi": col2.checkbox("Sindacalista Professionisti Autonomi"),
        "Sindacalista Agricolo": col3.checkbox("Sindacalista Agricolo"),
    }

# CATEGORIA 6: ASSICURATIVA E FINANZIARIA
with st.expander("🛡️ ASSICURATIVA E FINANZIARIA", expanded=False):
    col1, col2, col3 = st.columns(3)
    assicurativa = {
        "Esperto Assicurazioni RCA/Danni": col1.checkbox("Esperto Assicurazioni RCA/Danni"),
        "Esperto Previdenza/Assicurazioni Vita": col2.checkbox("Esperto Previdenza/Assicurazioni Vita"),
        "Esperto Assicurazioni Danni Generici": col3.checkbox("Esperto Assicurazioni Danni Generici"),
        "Consulente Finanziario OCF": col1.checkbox("Consulente Finanziario OCF"),
        "Promotore Finanziario": col2.checkbox("Promotore Finanziario"),
        "Esperto Fiscalità Strumenti Finanziari": col3.checkbox("Esperto Fiscalità Strumenti Finanziari"),
        "Esperto Credito al Consumo": col1.checkbox("Esperto Credito al Consumo"),
    }

# CATEGORIA 7: DIGITALE E PRIVACY
with st.expander("💻 DIGITALE E PRIVACY", expanded=False):
    col1, col2, col3 = st.columns(3)
    digitale = {
        "Data Protection Officer (Privacy)": col1.checkbox("Data Protection Officer (Privacy)"),
        "Esperto Diritto Digitale/ICT": col2.checkbox("Esperto Diritto Digitale/ICT"),
        "Esperto Proprietà Intellettuale": col3.checkbox("Esperto Proprietà Intellettuale"),
        "Esperto Cybersecurity Normativa": col1.checkbox("Esperto Cybersecurity Normativa"),
        "Esperto Normativa E-Commerce": col2.checkbox("Esperto Normativa E-Commerce"),
    }

# CATEGORIA 8: NOTARILE E GIUSTIZIA
with st.expander("⚖️ NOTARILE E GIUSTIZIA", expanded=False):
    col1, col2, col3 = st.columns(3)
    notarile = {
        "Notaio": col1.checkbox("Notaio"),
        "Mediatore Civile/Commerciale": col2.checkbox("Mediatore Civile/Commerciale"),
        "Arbitro Rituale/Irrituale": col3.checkbox("Arbitro Rituale/Irrituale"),
        "Esperto Normativa Giudice di Pace": col1.checkbox("Esperto Normativa Giudice di Pace"),
    }

# CATEGORIA 9: IMMOBILIARE
with st.expander("🏠 IMMOBILIARE", expanded=False):
    col1, col2, col3 = st.columns(3)
    immobiliare = {
        "Agente Mediazione Immobiliare": col1.checkbox("Agente Mediazione Immobiliare"),
        "Amministratore di Condominio": col2.checkbox("Amministratore di Condominio"),
        "Tecnico Certificatore Energetico": col3.checkbox("Tecnico Certificatore Energetico"),
    }

# CATEGORIA 10: TRASPORTI E LOGISTICA
with st.expander("🚚 TRASPORTI E LOGISTICA", expanded=False):
    col1, col2, col3 = st.columns(3)
    trasporti = {
        "Consulente Trasporti e Logistica": col1.checkbox("Consulente Trasporti e Logistica"),
        "Responsabile Merci Pericolose ADR": col2.checkbox("Responsabile Merci Pericolose ADR"),
        "Spedizioniere Internazionale": col3.checkbox("Spedizioniere Internazionale"),
    }

# CATEGORIA 11: TURISMO E ALIMENTARE
with st.expander("🍽️ TURISMO E ALIMENTARE", expanded=False):
    col1, col2, col3 = st.columns(3)
    turismo = {
        "Consulente Turismo e Agenzie Viaggi": col1.checkbox("Consulente Turismo e Agenzie Viaggi"),
        "Responsabile Sicurezza Alimentare HACCP": col2.checkbox("Responsabile Sicurezza Alimentare HACCP"),
        "Esperto Somministrazione Alimenti e Bevande": col3.checkbox("Esperto Somministrazione Alimenti e Bevande"),
    }

# CATEGORIA 12: AMBIENTE E SICUREZZA
with st.expander("🌍 AMBIENTE E SICUREZZA", expanded=False):
    col1, col2, col3 = st.columns(3)
    ambiente = {
        "RSPP": col1.checkbox("RSPP"),
        "Responsabile Gestione Ambientale": col2.checkbox("Responsabile Gestione Ambientale"),
        "Energy Manager Normativo": col3.checkbox("Energy Manager Normativo"),
    }

# CATEGORIA 13: FORMAZIONE E ISTRUZIONE
with st.expander("🎓 FORMAZIONE E ISTRUZIONE", expanded=False):
    col1, col2, col3 = st.columns(3)
    formazione = {
        "Consulente Formazione Professionale": col1.checkbox("Consulente Formazione Professionale"),
        "Responsabile Privacy Settore Istruzione": col2.checkbox("Responsabile Privacy Settore Istruzione"),
        "Esperto Programmi UE Erasmus+": col3.checkbox("Esperto Programmi UE Erasmus+"),
    }

# CATEGORIA 14: INTERNAZIONALE E DOGANALE
with st.expander("🌍 INTERNAZIONALE E DOGANALE", expanded=False):
    col1, col2, col3 = st.columns(3)
    internazionale = {
        "Esperto Doganale e Scambi Internazionali": col1.checkbox("Esperto Doganale e Scambi Internazionali"),
        "Consulente Export e Internazionalizzazione": col2.checkbox("Consulente Export e Internazionalizzazione"),
        "Traduttore Giurato/Esperto Legalizzazione": col3.checkbox("Traduttore Giurato/Esperto Legalizzazione"),
    }

# RACCOGLI TUTTE LE FIGURE SELEZIONATE
figure_selezionate = []
for categoria in [legale, fiscalita, tecnica, sanitaria, sindacale, assicurativa, digitale, notarile, immobiliare, trasporti, turismo, ambiente, formazione, internazionale]:
    for figura, selezionato in categoria.items():
        if selezionato:
            figure_selezionate.append(figura)

# ALTRE FIGURE NON IN ELENCO
st.markdown("---")
st.subheader("📌 ALTRE FIGURE")
col1, col2 = st.columns(2)
with col1:
    altra_figura = st.checkbox("Aggiungi figura non in elenco")
with col2:
    if altra_figura:
        specifica_figura = st.text_input("Specifica il nome della figura:")
        if specifica_figura:
            figure_selezionate.append(specifica_figura)

# DOMANDA
st.markdown("---")
st.subheader("❓ DOMANDA")
domanda = st.text_area("Scrivi la tua domanda come se parlassi a un collega", height=150, placeholder="Esempio: Un medico in regime forfettario percepisce compensi da ASL come MMG. L'ASL deve emettere CU 2026? Con quale codice?")
# CONTESTO
st.markdown("---")
st.subheader("📌 CONTESTO UTILE")
col1, col2 = st.columns(2)
with col1:
    soggetto = st.text_input("Soggetto interessato", placeholder="es. medico forfettario, SRL, dipendente...")
    periodo = st.text_input("Periodo di riferimento", placeholder="es. redditi 2025, CU 2026...")
with col2:
    documenti = st.text_input("Documenti disponibili", placeholder="es. circolare AdE, interpello, contratto...")
    urgenza = st.selectbox("Urgenza", ["Normale", "Entro 48h", "Oggi"])

# GENERA PROMPT
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    genera_button = st.button("🚀 GENERA PROMPT COMPLETO", type="primary", use_container_width=True)

if genera_button:
    if not figure_selezionate:
        st.error("⚠️ Seleziona almeno una figura professionale!")
    elif not domanda:
        st.error("⚠️ Scrivi almeno la domanda!")
    else:
        # COSTRUISCI IL PROMPT COMPLETO
        prompt = f"""
🔷 QUESITO NORMATIVO CERTO — SISTEMA NORM-ONLY

📋 DATI GENERALI
Data: {data}
Operatore: {operatore}
Riferimento: {riferimento}

👥 FIGURE DA ATTIVARE
{chr(10).join(['  ▸ ' + fig for fig in figure_selezionate])}

❓ DOMANDA
{domanda}

📌 CONTESTO
• Soggetto: {soggetto if soggetto else 'Non specificato'}
• Periodo: {periodo if periodo else 'Non specificato'}
• Documenti: {documenti if documenti else 'Non specificato'}
• Urgenza: {urgenza}

🎯 ISTRUZIONI VINCOLANTI PER LA RISPOSTA
Sei un professionista senior che risponde a un quesito dello studio.


▌ 1. FONTI NORMATIVE (SOLO QUESTE)
   ✓ Leggi/decreti: Gazzetta Ufficiale, Normattiva
   ✓ Regolamenti UE: Gazzetta Ufficiale UE, EUR-Lex
   ✓ Circolari ufficiali: siti .gov.it, .agenziaentrate.gov.it, .inps.it
   ✓ Risposte interpello: solo se vincolanti per il caso
   ✓ Provvedimenti: con numero, data, fonte certa
   ✓ Cassazione: solo massime ufficiali, non contrastanti
   ✓ Norme Regionali: per quesiti apertura attività
   ✓ Pareri autorevoli: Il Sole 24 Ore, Fiscal Focus
   
   📐 Formato citazione: [Fonte] [Tipo] n.[X] del [data], art.[Y], c.[Z]
   💡 Esempio: AdE, Circolare n. 9/E del 14/02/2024, art. 1, c. 54


▌ 2. STILE DI RISPOSTA
   • Italiano chiaro e discorsivo (come a un collega)
   • Evita elenchi se non strettamente necessari
   • Struttura ideale: sintesi → ragionamento → riferimenti pratici
   • Suggerimenti procedurali: indica passaggi per portali ufficiali 
     (Agenzia delle Entrate, INPS, Regioni) solo se verificati e necessari per il parere
   • Riporta il pezzo dell'articolo della norma che ci interessa, oltre al riferimento normativo
   • Fai sempre esempi esplicativi (se citi il contratto di locazione trasitoria fai esempi sui requisti per la transitorietà di modo che l'interlocutore possa capire)
   • Esprimi pareri articolati basandoti sui professionisti chiamati in causa
   • Se l’interlocutore richiede un PDF, generalo in formato A4, margini 2 cm, testo giustificato, interlinea singola (leading 13–14), font professionale (Times/Helvetica), titoli numerati in grassetto (dimensione carattere 22)con spazio tra paragrafi, citazioni normative nel formato “[GU] Legge n.X del XX/XX/XXXX, art.X, c.X”, eventuali tabelle entro i margini con intestazioni in grassetto, struttura: Titolo → Oggetto → Riferimenti normativi → Regola generale → Applicazione al caso → Parere degli Esperti Chiamati in Causa → Esempi → Conseguenze giuridiche → Conclusione → Villafranca in Lunigiana e Firma, con impaginazione pulita e professionale senza testo fuori margine.
   

▌ 3. ONESTÀ INTELLETTUALE
   • Norma ambigua o assente? → Dichiaralo esplicitamente
   • NO "si ritiene che" senza fonte certa
   • Zone grigie? → Indica organo per interpello vincolante
   • Quesito incompleto? → Poni domande mirate prima di rispondere
   • Necessità di procedure a mezzo di portali? → Spiegale nel dettaglio, con esempi pratici, specifica se servono strumenti come SPID o CNS. Cita i portali con il loro link e verifica che sia corretto


▌ 4. PROFONDITÀ
   • Spiega il PERCHÉ normativo, non solo il cosa
   • Meglio 15 righe chiare che 3 criptiche
   • Sviscera tutto l'argomento in ogni sua sfumatura significativa per il quesito posto (Esempio: se ti chiedono se è lecito pagare l'anticipo TFR in contanti menziona i requisiti per richiedere l'anticipo TFR)
   • Poni domande, se lo ritieni opportuno, per offrire una risposta completa e puntuale (Esempio: ti viene menzionato la liceità di un pagamento in contanti. Chiedi se il pagamento in contanti eccede il limite normativo per essere considerato legale ovvero nel 2026 sino a € 5.000,00)


▌ 5. STRUTTURA OBBLIGATORIA
   1. Riferimenti normativi (fonte + articolo + comma + data)
   2. Applicazione al caso (SOLO se normativamente certa)
   3. Lacune normative (esplicitamente dichiarate)
   4. [Opzionale] Tabella sintesi solo se normata (entro i margini con intestazioni in grassetto)


▌ 6. DIVIETO ASSOLUTO
   ✗ Opinioni personali
   ✗ "Si ritiene che", "prassi comune", "orientamento prevalente"
   ✗ Norme ibride senza gerarchia certa
   ✗ Risposta senza certezza normativa


✅ RISPONDI ORA AL QUESITO
"""
        # MOSTRA IL PROMPT GENERATO
        st.success("✅ Prompt generato con successo!")
        st.markdown("**Copia il prompt qui sotto e incollalo in ChatGPT:**")
        st.code(prompt, language="markdown")
        
        # PULSANTI DOWNLOAD E COPIA
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Scarica come file .txt",
                data=prompt,
                file_name=f"quesito_{data}_{riferimento.replace(' ', '_') if riferimento else 'senza_rif'}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.info("💡 Seleziona il testo nel box nero sopra, copia (Ctrl+C) e incolla in ChatGPT")

# SIDEBAR CON ISTRUZIONI
with st.sidebar:
    st.header("ℹ️ Come usare questa app")
    st.markdown("""
    ### 5 PASSAGGI SEMPLICI
    
    1. **Compila i dati** in alto (data, operatore, riferimento)
    
    2. **Seleziona le figure** professionali rilevanti (espandi le categorie)
    
    3. **Scrivi la domanda** in modo chiaro e completo
    
    4. **Compila il contesto** (opzionale ma consigliato)
    
    5. **Clicca "Genera Prompt"** e copia il risultato in ChatGPT
    
    ---
    
    ### 📋 PROTOCOLLO NORM-ONLY
    
    Questa app genera prompt che vincolano l'AI a:
    - Usare SOLO fonti normative certe
    - Citare sempre fonte, numero, data, articolo
    - Dichiarare esplicitamente le lacune normative
    - NON esprimere opinioni personali
    - Nel caso in cui si richieda la necessità di citare un parere autorevole deve provenire da specialisti quali "Il Sole 24 Ore", "Edotto", "Fiscal Focus" e altri similari
    - Nel caso in qui il quesito richieda aspetti tecnici procedurali che comprendano l'utilizzo di portali siano essi Nazionali (Agenzia Entrate, INPS, ecc.), Regionali o Comunali specifica il portale, le istruzioni e eventuali link
    
    ---
    
    ### 🔧 SUPPORTO
    
    Se hai problemi o servono modifiche, contatta l'amministratore.
    """)
    
    st.markdown("---")
    st.markdown("**Versione:** v1.0_2026-03")
    st.markdown("**Studio:** [Studio Pratici]")

# FOOTER
st.markdown("---")

st.markdown("*Sistema NORM-Only - Solo fonti certe, zero interpretazioni | Versione 1.0*")



















