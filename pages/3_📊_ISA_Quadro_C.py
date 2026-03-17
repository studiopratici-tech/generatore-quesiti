import streamlit as st
import pdfplumber
import re
import tempfile
import os

st.set_page_config(page_title="IT ISA Prompt Generator", layout="wide")

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

def find_isa_code(text):
    """Trova il codice ISA nel testo"""
    # Pattern per codici ISA: 2 lettere + 2-3 numeri + 1 lettera
    pattern = r"\b([A-Z]{2}\d{2,3}[A-Z])\b"
    matches = re.findall(pattern, text)
    
    # Ritorna il primo codice ISA valido trovato
    if matches:
        return matches[0]
    return None

def extract_quadro_c_fields(text):
    """Estrae i campi del Quadro C dal testo del PDF"""
    # Cerca pattern come C01, C02, C10, C100, ecc.
    fields = re.findall(r'\bC(\d{2,3})\b', text)
    # Converte in formato C01, C02, ecc. e rimuove duplicati
    unique_fields = sorted(set([f"C{int(f):02d}" for f in fields]))
    return unique_fields[:50]  # Limita a 50 campi max

def extract_keywords_from_text(text, isa_code):
    """Estrae parole chiave rilevanti dal PDF"""
    # Cerca sezioni rilevanti nel testo
    keywords = []
    
    # Parole comuni ISA da cercare
    common_terms = [
        "commercio", "vendita", "negozio", "ambulante",
        "costruzioni", "edilizia", "lavori", "cantieri",
        "professionista", "studi", "consulenza", "servizi",
        "manifatturiero", "produzione", "trasformazione",
        "alberghi", "ristoranti", "turismo",
        "trasporti", "logistica",
        "agricoltura", "coltivazioni"
    ]
    
    text_lower = text.lower()
    for term in common_terms:
        if term in text_lower:
            keywords.append(term)
    
    return list(set(keywords))[:15]  # Max 15 keywords

def generate_universal_prompt(isa_code, fields, keywords, description=""):
    """Genera un prompt universale per qualsiasi ISA"""
    
    if not description:
        description = f"Modello ISA {isa_code}"
    
    fields_str = ", ".join(fields) if fields else "Campi del Quadro C da identificare"
    keywords_str = ", ".join(keywords) if keywords else "settori di attività"
    
    prompt = f"""
╔══════════════════════════════════════════════════════════════╗
║           PROMPT ISA {isa_code} - ANALISI FISCALE            ║
╚══════════════════════════════════════════════════════════════╝

RUOLO:
Sei un esperto consulente fiscale specializzato in ISA (Indici Sintetici di Affidabilità) con focus sul modello {isa_code}.

MODELLO DI RIFERIMENTO:
{description}

CAMPI DEL QUADRO C DA ANALIZZARE:
{fields_str}

CONTESTO OPERATIVO E SETTORIALE:
{keywords_str}

ISTRUZIONI SPECIFICHE:
1. Analizza i dati forniti considerando ESCLUSIVAMENTE i parametri del modello {isa_code}
2. Valuta la coerenza tra i campi del Quadro C compilati
3. Identifica eventuali anomalie o incongruenze
4. Considera le specificità del settore: {keywords_str}
5. Ignora completamente parametri di altri modelli ISA

OUTPUT RICHIESTO:
- Analisi dettagliata dei campi rilevanti
- Valutazione della coerenza interna
- Eventuali criticità riscontrate
- Raccomandazioni specifiche per il modello {isa_code}
"""
    return prompt

# UI Principale
st.title("🇮🇹 IT ISA Prompt Generator")
st.markdown("Carica il PDF delle istruzioni ISA per generare automaticamente un prompt specifico")

uploaded_file = st.file_uploader("📄 Carica file PDF delle istruzioni ISA", type=['pdf'])

if uploaded_file is not None:
    with st.spinner('🔍 Analisi del PDF in corso...'):
        # Estrai testo
        text_content = extract_text_from_pdf(uploaded_file)
        
        if text_content:
            # Trova codice ISA
            isa_code = find_isa_code(text_content)
            
            if isa_code:
                st.success(f"✅ Codice ISA rilevato dal PDF: **{isa_code}**")
                
                # Estrai campi Quadro C
                with st.spinner('📋 Estrazione campi Quadro C...'):
                    fields = extract_quadro_c_fields(text_content)
                
                # Estrai keywords
                with st.spinner('🎯 Identificazione settore...'):
                    keywords = extract_keywords_from_text(text_content, isa_code)
                
                # Mostra info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Campi Quadro C trovati", len(fields))
                with col2:
                    st.metric("Parole chiave identificate", len(keywords))
                
                # Espandi per vedere dettagli
                with st.expander("🔍 Vedi dettagli estratti"):
                    st.write("**Campi Quadro C:**")
                    st.write(fields)
                    st.write("**Parole chiave:**")
                    st.write(keywords)
                
                # Genera prompt
                with st.spinner('🤖 Generazione prompt...'):
                    prompt = generate_universal_prompt(
                        isa_code=isa_code,
                        fields=fields,
                        keywords=keywords
                    )
                
                st.subheader(" Prompt Generato")
                st.code(prompt, language='text')
                
                # Download
                st.download_button(
                    label="📥 Scarica Prompt (.txt)",
                    data=prompt,
                    file_name=f"prompt_{isa_code}.txt",
                    mime="text/plain",
                    type="primary"
                )
            else:
                st.error("❌ Nessun codice ISA trovato nel PDF")
                st.info("Assicurati che il PDF contenga un codice ISA valido (es. FM87U, EG50U, DM28U, ecc.)")
        else:
            st.error("❌ Errore nella lettura del PDF")
else:
    st.info("👆 Carica un PDF per iniziare")
    st.markdown("""
    **Come funziona:**
    1. Carica il PDF delle istruzioni ISA
    2. L'app rileva automaticamente il codice (es. DM28U)
    3. Estrae i campi del Quadro C dal documento
    4. Identifica il settore di attività
    5. Genera un prompt specifico e pronto all'uso
    """)
