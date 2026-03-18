import streamlit as st
import json
import pdfplumber
import re
import tempfile
import os
from pathlib import Path

st.set_page_config(page_title="ISA Quadro C", layout="wide")

# Carica il mapping
@st.cache_data
def load_isa_mapping():
    try:
        with open('isa_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Errore nel caricamento di isa_mapping.json: {e}")
        return {}

isa_mapping = load_isa_mapping()

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
                if match in isa_mapping:
                    isa_code = match
                    break
            
            if isa_code:
                st.success(f"✅ Codice ISA rilevato: **{isa_code}**")
                
                data = isa_mapping[isa_code]
                
                # Mostra info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Settore", data.get('descrizione', 'N/A'))
                with col2:
                    st.metric("Campi Quadro C", len(data.get('quadro_c', [])))
                
                st.write("**📋 Campi da compilare:**")
                st.write(", ".join(data.get('quadro_c', [])))
                
                st.write("**📎 Documenti richiesti:**")
                for doc in data.get('documenti_richiesti', []):
                    st.write(f"📄 {doc}")
                
                # Genera prompt
                prompt = f"""
╔══════════════════════════════════════════════════════════════╗
║         COMPILAZIONE QUADRO C - ISA {isa_code}                  ║
║         {data.get('descrizione', '')}
╚══════════════════════════════════════════════════════════════╝

📌 MODELLO ISA: {isa_code}
📋 SETTORE: {data.get('descrizione', '')}

⚠️ **ATTENZIONE**

Questo prompt riguarda **ESCLUSIVAMENTE la compilazione del Quadro C**.

❌ **NON** fornire dati da altri quadri (A, B, D, E, F, H)
❌ **NON** inventare valori
❌ **NON** procedere senza documentazione

✅ **DEVI** fornire SOLO i dati del Quadro C
✅ **DEVI** avere documentazione a supporto
✅ **DEVI** essere preciso nei valori

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 **DOCUMENTI DA ALLEGARE (PDF)**:

{chr(10).join([f"📄 {doc}" for doc in data.get('documenti_richiesti', [])])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **CAMPI DEL QUADRO C DA COMPILARE**:

{', '.join(data.get('quadro_c', []))}

**TOTALE CAMPI: {len(data.get('quadro_c', []))}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️ **ISTRUZIONI PER LA COMPILAZIONE**:

Per **CIASCUN CAMPO** del Quadro C, fornisci:

┌─────────────────────────────────────────────────────┐
│ CAMPO: C##                                           │
│ VALORE: [inserire valore numerico]                  │
│ FONTE DOCUMENTALE: [es. Bilancio 2024 pag. X]      │
│ DESCRIZIONE: [breve descrizione]                    │
│ NOTE: [eventuali criticità]                         │
│ COERENZA: [✓ coerente / ⚠️ da verificare]         │
└─────────────────────────────────────────────────────┘

**RIPETERE PER TUTTI I {len(data.get('quadro_c', []))} CAMPI**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **REGOLE SPECIFICHE PER {isa_code}**:

{data.get('note', '')}

**IMPORTANTE**: Le percentuali devono sommare **100%** dove richiesto.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **CONTROLLI DI COERENZA**:

□ Tutte le percentuali sommano 100%
□ I valori sono coerenti con la documentazione
□ Non ci sono duplicazioni
□ I dati sono congrui con il settore
□ Eventuali anomalie sono giustificate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **OUTPUT FINALE RICHIESTO**:

1. **TABELLA RIEPILOGATIVA** con tutti i campi compilati
2. **ANALISI DI COERENZA** interna
3. **SEGNALAZIONE CRITICITÀ** o valori anomali
4. **CHECKLIST PRE-INVIO** completata

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **NOTE IMPORTANTI**:

- Utilizza **SOLO** i dati dalla documentazione allegata
- **CITA SEMPRE** la fonte documentale
- **SEGNALA** se un campo non può essere compilato
- I quadri A, B, D, E, F, H sono gestiti dal consulente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **PROCEDI CON L'ANALISI DEI DOCUMENTI E LA COMPILAZIONE**.

══════════════════════════════════════════════════════════════
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
                st.write(f"Codici trovati: {list(set(matches))[:10]}")
                
        except Exception as e:
            st.error(f"❌ Errore: {e}")
            st.exception(e)
else:
    st.info("👆 Carica un PDF per iniziare")
