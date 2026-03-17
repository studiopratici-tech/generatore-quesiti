import streamlit as st
import pdfplumber
import re
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="ISA Universal Prompt Generator", layout="wide")

def extract_text_from_pdf(uploaded_file):
    """Estrae tutto il testo dal PDF"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        text_content = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n"
        
        os.unlink(tmp_path)
        return text_content
    except Exception as e:
        return None

def identify_fields_to_compile(text, isa_code):
    """Identifica i campi del Quadro C da compilare per questo specifico ISA"""
    fields = []
    
    # Cerca pattern C01, C02, ecc. nel testo delle istruzioni
    pattern = r'\bC(\d{2,3})\b'
    matches = re.findall(pattern, text)
    
    # Converte in formato standard e rimuove duplicati
    unique_fields = sorted(set([f"C{int(f):02d}" for f in matches]))
    
    # Filtra solo i campi rilevanti (di solito fino a C100)
    for field in unique_fields:
        field_num = int(field[1:])
        if 1 <= field_num <= 100:  # Campi C01-C100
            fields.append(field)
    
    return fields

def extract_compilation_rules(text, isa_code):
    """Estrae le regole specifiche di compilazione dal PDF"""
    rules = []
    
    # Cerca sezioni con "istruzioni", "note", "compilazione"
    text_lower = text.lower()
    
    # Pattern per trovare istruzioni specifiche
    instruction_patterns = [
        r'compilare.*?se.*?(?:campo|rigo).*?(?:\d+|[A-Z])',
        r'indicare.*?nel.*?campo.*?C\d+',
        r'non compilare.*?(?:se|nel caso)',
        r'obbligatorio.*?(?:per|se)',
        r'campo.*?C\d+.*?(?:deve|va).*?(?:compilato|inserito)'
    ]
    
    for pattern in instruction_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        rules.extend(matches)
    
    # Rimuovi duplicati e limita
    unique_rules = list(set(rules))[:20]
    
    return unique_rules

def extract_sector_info(text):
    """Estrae informazioni sul settore dal PDF"""
    keywords = []
    
    # Cerca il titolo/descrizione del modello
    title_patterns = [
        r'indice sintetico.*?(?:di affidabilità)?\s*(?:-|\n)\s*(.+?)(?:\n|$)',
        r'modello.*?ISA.*?(?:-|\n)\s*(.+?)(?:\n|$)',
        r'(commercio|edilizia|professioni|manifatturiero|servizi|trasporti|turismo|agricoltura)'
    ]
    
    for pattern in title_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend(matches)
    
    return list(set(keywords))[:10]

def generate_universal_compilation_prompt(isa_code, fields, rules, sector_info, fatturato=None):
    """Genera un prompt UNIVERSALE per la compilazione del Quadro C"""
    
    fields_str = ", ".join(fields) if fields else "Campi da identificare"
    
    # Sezione fatturato se fornito
    fatturato_section = ""
    if fatturato:
        fatturato_section = f"""
📊 DATI AZIENDALI:
Fatturato dichiarato: € {fatturato:,.2f}
Anno di riferimento: {datetime.now().year - 1}
"""
    
    # Regole specifiche se presenti
    rules_section = ""
    if rules:
        rules_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 ISTRUZIONI SPECIFICHE DAL MODELLO {isa_code}:

{chr(10).join(f"• {rule}" for rule in rules[:10])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    prompt = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║           GUIDA UNIVERSALE COMPILAZIONE QUADRO C                         ║
║                     ISA {isa_code}                                        ║
══════════════════════════════════════════════════════════════════════════╝

{fatturato_section}
🎯 MODELLO DI RIFERIMENTO:
Codice ISA: {isa_code}
Settore: {', '.join(sector_info) if sector_info else 'Da identificare'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CAMPI DEL QUADRO C DA COMPILARE:

{fields_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️ ISTRUZIONI UNIVERSALI DI COMPILAZIONE:

Per CIASCUN campo del Quadro C elencato sopra, segui queste regole:

1️⃣ **ANALISI DEL CAMPO**
   - Leggi attentamente la descrizione del campo nelle istruzioni ISA
   - Verifica se il campo è OBBLIGATORIO per il tuo modello
   - Controlla se ci sono condizioni specifiche per la compilazione

2️⃣ **RACCOLTA DATI**
   - Individua il dato corretto dalla contabilità
   - Verifica la coerenza con altri campi compilati
   - Controlla che il valore sia congruo con il fatturato

3️⃣ **COMPILAZIONE**
   - Inserisci il valore numerico ESATTO (senza migliaia separatori)
   - Usa decimali solo se richiesti (di solito 2 cifre)
   - Se il campo non è applicabile, lascia vuoto o inserisci 0

4️⃣ **VERIFICA COERENZA**
   - Controlla che la somma dei campi sia coerente
   - Verifica che non ci siano duplicazioni
   - Assicurati che i valori siano proporzionati al fatturato

{rules_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 FORMATO DI RISPOSTA RICHIESTO:

Per ogni campo, compila seguendo questo schema:

┌─────────────────────────────────────────────────────────────┐
│ CAMPO: C01                                                   │
│ DESCRIZIONE: [breve descrizione dal manuale]                │
│ VALORE: [inserire valore numerico]                          │
│ NOTE: [eventuali note o criticità]                          │
│ FONTI DATI: [da quale documento/conto deriva]               │
└─────────────────────────────────────────────────────────────┘

Ripeti per TUTTI i campi elencati.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CONTROLLI FINALI OBBLIGATORI:

□ Tutti i campi obbligatori sono compilati
□ I valori sono coerenti con il fatturato dichiarato
□ Non ci sono duplicazioni di ricavi/costi
□ Le percentuali sono congrue con il settore
□ Eventuali anomalie sono giustificate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OUTPUT FINALE ATTESO:

Al termine della compilazione, fornirai:

1. TABELLA RIEPILOGATIVA con tutti i campi compilati
2. ANALISI DI COERENZA interna tra i vari campi
3. SEGNALAZIONE CRITICITÀ o valori anomali
4. SUGGERIMENTI per ottimizzare la compilazione
5. CHECKLIST di controllo pre-invio

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 NOTE IMPORTANTI:
- Questo prompt è valido per QUALSIASI modello ISA
- Adatta le istruzioni specifiche al tuo settore
- In caso di dubbi, fai riferimento al manuale ufficiale
- Conserva sempre documentazione a supporto

══════════════════════════════════════════════════════════════════════════
"""
    return prompt

# UI Principale
st.title("🌍 ISA Universal Prompt Generator")
st.markdown("Genera prompt universali per la compilazione del Quadro C di **QUALSIASI** modello ISA")

# Input utente
col1, col2 = st.columns(2)

with col1:
    isa_code = st.text_input("🔢 Codice ISA", placeholder="es. FM87U, EG50U, DM28U...").upper()

with col2:
    fatturato = st.number_input("💰 Fatturato annuale (€)", min_value=0.0, step=1000.0, format="%.2f")

uploaded_file = st.file_uploader("📄 Carica PDF istruzioni ISA", type=['pdf'])

if isa_code and uploaded_file:
    with st.spinner('🔍 Analisi del modello ISA in corso...'):
        # Estrai testo dal PDF
        text_content = extract_text_from_pdf(uploaded_file)
        
        if text_content:
            # Analizza il PDF
            with st.spinner('📋 Identificazione campi da compilare...'):
                fields = identify_fields_to_compile(text_content, isa_code)
            
            with st.spinner('📖 Estrazione regole specifiche...'):
                rules = extract_compilation_rules(text_content, isa_code)
            
            with st.spinner('🎯 Identificazione settore...'):
                sector_info = extract_sector_info(text_content)
            
            # Mostra risultati analisi
            st.success(f"✅ Analisi completata per ISA {isa_code}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Campi identificati", len(fields))
            with col2:
                st.metric("Regole estratte", len(rules))
            with col3:
                st.metric("Parole chiave settore", len(sector_info))
            
            # Espandi per vedere dettagli
            with st.expander("🔍 Vedi dettagli analisi"):
                st.write("**Campi del Quadro C:**")
                st.write(fields)
                st.write("**Regole specifiche:**")
                for rule in rules:
                    st.write(f"• {rule}")
                st.write("**Settore:**")
                st.write(sector_info)
            
            # Genera prompt
            with st.spinner('🤖 Generazione prompt universale...'):
                prompt = generate_universal_compilation_prompt(
                    isa_code=isa_code,
                    fields=fields,
                    rules=rules,
                    sector_info=sector_info,
                    fatturato=fatturato if fatturato > 0 else None
                )
            
            st.subheader("📝 Prompt Generato")
            st.code(prompt, language='text')
            
            # Download
            st.download_button(
                label="📥 Scarica Prompt (.txt)",
                data=prompt,
                file_name=f"ISA_{isa_code}_Guida_Compilazione_QuadroC.txt",
                mime="text/plain",
                type="primary"
            )
            
            st.info("💡 Questo prompt è universale e può essere usato per qualsiasi modello ISA!")
        else:
            st.error("❌ Errore nella lettura del PDF")
elif not isa_code:
    st.warning("⚠️ Inserisci il codice ISA per continuare")
elif not uploaded_file:
    st.warning("⚠️ Carica il PDF delle istruzioni ISA")

# Sidebar
with st.sidebar:
    st.header("Come funziona")
    st.markdown("""
    1. **Inserisci** il codice ISA del modello
    2. **Carica** il PDF delle istruzioni
    3. **Opzionale:** Inserisci il fatturato
    4. **Ottieni** un prompt universale per la compilazione
    """)
    
    st.markdown("---")
    st.info("💡 Il prompt generato funziona per QUALSIASI modello ISA!")
