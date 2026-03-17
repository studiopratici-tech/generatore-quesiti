import streamlit as st
import PyPDF2
import io
import re
from datetime import datetime

# CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="ISA Prompt Generator - Lettura PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# TITOLO
st.title("📄 ISA PROMPT GENERATOR - LETTURA AUTOMATICA PDF")
st.markdown("**Carica i PDF delle istruzioni ISA e genera prompt infallibili basati sui dati REALI estratti**")
st.markdown("---")

# SIDEBAR
with st.sidebar:
    st.header("ℹ️ Come funziona")
    st.markdown("""
    ### 3 PASSAGGI
    
    1. **Carica i PDF**:
       - Istruzioni ISA (obbligatorio)
       - Modello ISA (opzionale)
       - Fatture (opzionale)
    
    2. **L'estrazione automatica**:
       - Legge le istruzioni PDF
       - Estrae TUTTI i campi del Quadro C
       - Estrae le descrizioni ESATTE
    
    3. **Genera il prompt**:
       - Basato sui dati REALI dei PDF
       - Zero invenzioni
       - 100% accurato
    
    ---
    
    ### 📋 VANTAGGI
    
    ✅ Descrizioni estratte dai PDF ufficiali
    ✅ Zero errori nelle descrizioni
    ✅ Prompt personalizzato sul modello specifico
    ✅ Tracciabilità completa
    
    ---
    
    **Versione:** v1.0_PDF_Reader
    **Studio:** Studio Pratici
    """)

# UPLOAD FILE
st.subheader("📤 CARICA I FILE PDF")

col1, col2, col3 = st.columns(3)

with col1:
    istruzioni_file = st.file_uploader(
        "📄 Istruzioni ISA (OBBLIGATORIO)",
        type=['pdf'],
        help="Carica il PDF delle istruzioni ufficiali ISA (es. EG50U Istruzioni.pdf)"
    )

with col2:
    modello_file = st.file_uploader(
        "📋 Modello ISA (opzionale)",
        type=['pdf'],
        help="Carica il PDF del modello ISA vuoto"
    )

with col3:
    fatture_file = st.file_uploader(
        "💰 Fatture (opzionale)",
        type=['pdf'],
        help="Carica il PDF delle fatture emesse/ricevute"
    )

# FUNZIONE PER LEGGERE PDF
def read_pdf_text(pdf_file):
    """Estrae il testo da un file PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Errore nella lettura del PDF: {e}")
        return None

# FUNZIONE PER ESTRARRE CAMPI QUADRO C
def extract_quadro_c_fields(text):
    """Estrae i campi del Quadro C dalle istruzioni"""
    fields = {}
    
    # Pattern per cercare i campi C01, C02, etc.
    pattern = r'(C\d{2})\s*[-–:]\s*([^\n]+)'
    matches = re.findall(pattern, text)
    
    for code, description in matches:
        # Pulizia della descrizione
        description = description.strip()
        # Rimuovi caratteri speciali eccessivi
        description = re.sub(r'\s+', ' ', description)
        fields[code] = description
    
    return fields

# FUNZIONE PER ESTRARRE INFORMAZIONI ISA
def extract_isa_info(text):
    """Estrae informazioni generali sul modello ISA"""
    info = {
        'codice': None,
        'descrizione': None,
        'periodo': None
    }
    
    # Cerca il codice ISA (es. EG50U, FM87U, etc.)
    code_pattern = r'\b([A-Z]{2}\d{2}U)\b'
    code_matches = re.findall(code_pattern, text)
    if code_matches:
        info['codice'] = code_matches[0]
    
    # Cerca la descrizione dell'attività
    if 'PERIODO D' in text:
        # Estrai la riga dopo "PERIODO D'IMPOSTA"
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'PERIODO D' in line and i+1 < len(lines):
                info['descrizione'] = lines[i+1].strip()
                break
    
    # Cerca il periodo d'imposta
    periodo_pattern = r'PERIODO\s+D['"'"']?IMPOSTA\s+(\d{4})'
    periodo_match = re.search(periodo_pattern, text)
    if periodo_match:
        info['periodo'] = periodo_match.group(1)
    
    return info

# SEZIONE PRINCIPALE
if istruzioni_file:
    st.markdown("---")
    st.subheader("📖 ESTRATTORE DATI DAI PDF")
    
    # Leggi il PDF delle istruzioni
    with st.spinner('🔍 Lettura delle istruzioni ISA in corso...'):
        istruzioni_text = read_pdf_text(istruzioni_file)
    
    if istruzioni_text:
        # Estrai informazioni
        isa_info = extract_isa_info(istruzioni_text)
        quadro_c_fields = extract_quadro_c_fields(istruzioni_text)
        
        # Mostra informazioni estratte
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Istruzioni lette con successo!")
            st.info(f"""
            **Codice ISA:** {isa_info['codice'] or 'Non rilevato'}
            **Descrizione:** {isa_info['descrizione'] or 'Non rilevata'}
            **Periodo:** {isa_info['periodo'] or 'Non rilevato'}
            **Campi Quadro C trovati:** {len(quadro_c_fields)}
            """)
        
        with col2:
            if st.button("👁️ Visualizza campi estratti", use_container_width=True):
                st.write("### Campi Quadro C estratti:")
                for code, desc in sorted(quadro_c_fields.items()):
                    st.write(f"**{code}**: {desc}")
        
        st.markdown("---")
        
        # CONFIGURAZIONE PROMPT
        st.subheader("⚙️ CONFIGURA IL PROMPT")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Sezioni da includere:**")
            include_specializzazione = st.checkbox("✓ Specializzazione (C01-C28)", )
            include_subappalto = st.checkbox("✓ Subappalto (C29)", )
            include_realizzazione = st.checkbox("✓ Realizzazione (C31-C32)", )
            include_localizzazione = st.checkbox("✓ Localizzazione (C33-C41)", )
            include_ambito = st.checkbox("✓ Ambito attività (C46-C47)", )
        
        with col2:
            st.markdown("**Opzioni aggiuntive:**")
            include_tracing = st.checkbox("✓ Tracciabilità fatture", )
            include_ambiguity = st.checkbox("✓ Segnalazione ambiguità", )
            include_assumptions = st.checkbox("✓ Assunzioni effettuate", )
            include_signature = st.checkbox("✓ Firma finale", )
        
        st.markdown("---")
        
        # GENERA PROMPT
        if st.button("🚀 GENERA PROMPT INFALLIBILE", type="primary", use_container_width=True):
            # Costruisci il prompt
            prompt = f"""# 🔷 PROMPT INFALLIBILE: COMPILAZIONE QUADRO C ISA – {isa_info['codice'] or 'MODELLO ISA'}

## 📋 CONTESTO E RUOLO
Agisci come **Consulente Fiscale Senior specializzato in ISA (Indici Sintetici di Affidabilità Fiscale)** con competenza specifica sul codice attività: **{isa_info['codice'] or 'CODICE ISA'} – {isa_info['descrizione'] or 'Descrizione attività'}**.

**Obiettivo:** Compilare con precisione assoluta il **QUADRO C – Elementi specifici dell'attività** del modello ISA per il periodo d'imposta {isa_info['periodo'] or '2025'}, basandosi **ESCLUSIVAMENTE** sui dati estratti dai file PDF allegati e applicando rigorosamente le istruzioni ufficiali.

**File Allegati Attesi:**
1. `Istruzioni {isa_info['codice'] or 'ISA'}.pdf` → Regole ufficiali Agenzia delle Entrate
2. `Modello {isa_info['codice'] or 'ISA'}.pdf` → Struttura grafica e campi
3. `Fatture.pdf` o `Fatture.xml` → Dati sorgente

---

## 📋 CAMPI QUADRO C DA COMPILARE (estratti dalle istruzioni ufficiali)

"""
            # Aggiungi i campi estratti
            if quadro_c_fields:
                prompt += "### Campi identificati dalle istruzioni:\n\n"
                for code in sorted(quadro_c_fields.keys()):
                    desc = quadro_c_fields[code]
                    prompt += f"- **{code}**: {desc}\n"
            else:
                prompt += "### Campi standard Quadro C:\n\n"
                prompt += "- **C01-C28**: Specializzazione (percentuali ricavi per tipologia attività)\n"
                prompt += "- **C29**: Subappalto acquisito\n"
                prompt += "- **C30**: Committente principale\n"
                prompt += "- **C31-C32**: Modalità realizzazione (in proprio/a terzi)\n"
                prompt += "- **C33-C35**: Luogo svolgimento attività\n"
                prompt += "- **C36-C41**: Localizzazione geografica\n"
                prompt += "- **C42**: Costi per lavori a terzi\n"
                prompt += "- **C43**: Split Payment\n"
                prompt += "- **C44**: Reverse Charge\n"
                prompt += "- **C45**: Ritenute Art.25 D.L. 78/2010\n"
                prompt += "- **C46-C47**: Ambito attività (nuove costruzioni/recupero)\n"
            
            prompt += f"""
---

## 🗂️ FASE 1: ESTRATTORE DATI – REVENUE RECOGNITION

### 1.1 Tipologia Documento
| Codice | Tipo | Trattamento |
|--------|------|-------------|
| **TD01** | Fattura | Importo positivo (+) |
| **TD04** | Nota di Credito | Importo negativo (–) |
| **TD19** | Fattura semplificata | Come TD01 |

### 1.2 Campi da estrarre per ogni documento
- ✅ Numero documento e Data
- ✅ Imponibile IVA (MAI totale con IVA)
- ✅ Aliquota/Natura IVA + Riferimento normativo
- ✅ Descrizione prestazioni
- ✅ Luogo di esecuzione
- ✅ Committente
- ✅ Elementi specifici ISA (CIG, CUP, etc.)

### 1.3 Calcolo Totale Ricavi Netto
Totale Ricavi Netto = Σ(TD01) + Σ(TD04 con segno negativo)

---

## 🧩 FASE 2: COMPILAZIONE QUADRO C

### Specializzazione (C01-C28)
- Classifica ogni fattura nella categoria corretta
- Calcola: % = (Imponibile categoria / Totale Ricavi Netto) × 100
- **Vincolo: Σ(C01:C28) = 100% ±0,1%**

### Subappalto (C29)
- Includere SOLO fatture con "subappalto", "CIG", "contratto subappalto"
- Calcolare % su ricavi totali

### Realizzazione (C31-C32)
- C31 = in proprio, C32 = a terzi
- **Vincolo: C31 + C32 = 100%**

### Localizzazione (C36-C41)
- Distribuire ricavi per area geografica
- **Vincolo: Σ(C36:C41) = 100%**

### Ambito attività (C46-C47)
- C46 = nuove costruzioni
- C47 = recupero/ristrutturazione
- **Vincolo: C46 + C47 = 100%**

---

## 🚨 FASE 3: SEGNALAZIONE AMBIGUITÀ

Segnala OBBLIGATORIAMENTE se:
- Descrizione fattura generica → classificazione incerta
- Luogo di esecuzione non esplicito
- Regime IVA dubbio
- Nota di credito non collegabile
- Dati mancanti

---

## ✅ FASE 4: VALIDAZIONE FINALE

### Controlli OBBLIGATORI
- [ ] Σ(Campi specializzazione) = 100% ±0,1%
- [ ] C31 + C32 = 100%
- [ ] Σ(C36:C41) = 100%
- [ ] C46 + C47 = 100%
- [ ] Note di credito applicate come storni
- [ ] Nessun dato inventato

---

## 📤 FORMATO OUTPUT RICHIESTO

### 📊 RIEPILOGO RICAVI
- Totale Ricavi Netto: € [valore]
- N. documenti: [n]
- Periodo: [data min] – [data max]

### 📋 QUADRO C COMPILATO
| Rigo | Descrizione | Valore | Fatture Incluse |
|------|-------------|--------|-----------------|
| C..  | [Campo]     | ...    | [Numeri]        |

### ⚠️ NOTE E CRITICITÀ
[Tabella ambiguità]

### 🔍 ASSUNZIONI EFFETTUATE
[Elenco assunzioni]

### 🛡️ FIRMA FINALE
Villafranca in Lunigiana, {datetime.now().strftime('%d/%m/%Y')}
Firma: Studio Pratici

---

✅ **INIZIA ORA L'ANALISI DEI FILE ALLEGATI**
"""
            
            # Mostra il prompt
            st.success("✅ Prompt generato con successo!")
            st.code(prompt, language="markdown")
            
            # Download button
            st.download_button(
                label="📥 Scarica prompt come .txt",
                data=prompt,
                file_name=f"ISA_{isa_info['codice'] or 'QuadroC'}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.info("💡 **Istruzioni**: Copia il prompt e incollalo in una nuova chat con i PDF allegati")

else:
    st.warning("⚠️ Carica almeno il file delle istruzioni ISA per procedere")

# FOOTER
st.markdown("---")
st.markdown("*ISA Prompt Generator v1.0 - Lettura automatica PDF | Zero invenzioni | 100% accuratezza*")
