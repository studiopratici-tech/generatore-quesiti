import streamlit as st
import pdfplumber
import re
import tempfile
import os

# Configurazione pagina - DEVE essere la prima cosa
st.set_page_config(page_title="ISA Prompt Generator", layout="wide")

# Cache per la mappatura ISA
@st.cache_data
def get_isa_mapping():
    return {
        "FM87U": {
            "desc": "Commercio al dettaglio e ambulanti",
            "fields": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"],
            "keywords": ["negozio", "ambulante", "marketplace", "vendita"]
        },
        "EG50U": {
            "desc": "Costruzioni edili",
            "fields": ["C01", "C02", "C29", "C44"],
            "keywords": ["tinteggiatura", "intonaco", "subappalto", "reverse charge"]
        },
        "EK02U": {
            "desc": "Studi tecnici",
            "fields": ["C01", "C02", "C03"],
            "keywords": ["prestazioni professionali", "consulenza"]
        }
    }

def extract_isa_code(text):
    """Estrae il codice ISA dal testo"""
    pattern = r"\b([A-Z]{2}\d{2,3}[A-Z])\b"
    matches = re.findall(pattern, text)
    return matches

def process_pdf(uploaded_file):
    """Processa il PDF e estrae il testo"""
    try:
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
        return text_content
    except Exception as e:
        st.error(f"Errore nella lettura del PDF: {e}")
        return None

# UI Principale
st.title("🇮🇹 ISA Prompt Generator")
st.markdown("Carica il PDF delle istruzioni ISA per generare un prompt specifico")

# Upload file
uploaded_file = st.file_uploader("📄 Carica file PDF", type=['pdf'])

if uploaded_file is not None:
    with st.spinner('🔍 Analisi del PDF in corso...'):
        # Estrai testo
        text_content = process_pdf(uploaded_file)
        
        if text_content:
            # Trova codici ISA
            isa_codes = extract_isa_code(text_content)
            mapping = get_isa_mapping()
            
            # Cerca codice valido
            detected_isa = None
            for code in isa_codes:
                if code in mapping:
                    detected_isa = code
                    break
            
            if detected_isa:
                st.success(f"✅ Codice ISA rilevato: **{detected_isa}**")
                
                isa_info = mapping[detected_isa]
                st.info(f"📋 {isa_info['desc']}")
                
                # Genera prompt
                prompt = f"""
Sei un esperto fiscale specializzato in ISA {detected_isa}.

📌 CAMPI RILEVANTI DEL QUADRO C:
{', '.join(isa_info['fields'])}

🎯 CONTESTO OPERATIVO:
{', '.join(isa_info['keywords'])}

ISTRUZIONI:
Analizza i dati forniti considerando ESCLUSIVAMENTE i parametri specifici del modello {detected_isa}, ignorando elementi non pertinenti ad altri settori.
"""
                
                st.subheader("🤖 Prompt Generato")
                st.code(prompt, language='text')
                
                # Bottone download
                st.download_button(
                    label="📥 Scarica Prompt (.txt)",
                    data=prompt,
                    file_name=f"prompt_{detected_isa}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("⚠️ Nessun codice ISA riconosciuto nel PDF")
                with st.expander("Vedi codici trovati"):
                    st.write(list(set(isa_codes))[:10])
else:
    st.info("👆 Carica un PDF per iniziare")

# Sidebar con info
with st.sidebar:
    st.header("Informazioni")
    st.write("Questa app estrae automaticamente il codice ISA dai PDF e genera prompt specifici.")
    st.markdown("---")
    st.write("Codici supportati:")
    for code in get_isa_mapping().keys():
        st.write(f"- {code}")
