import re
import sys
import pdfplumber
import json
from pathlib import Path

# ==============================================================================
# CONFIGURAZIONE E MAPPATURA ISA (Standard Agenzia delle Entrate)
# ==============================================================================
ISA_MAPPING = {
    "FM87U": {
        "desc": "Commercio al dettaglio e ambulanti",
        "fields": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "context_keywords": ["negozio", "ambulante", "marketplace", "vendita al dettaglio", "settori merceologici", "ecommerce"],
        "prompt_template": "Sei un esperto fiscale per il commercio (ISA {code}). Analizza i dati focalizzandoti su: {fields_str}. Considera specificamente: {keywords_str}."
    },
    "EG50U": {
        "desc": "Costruzioni edili e installazioni",
        "fields": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C44"],
        "context_keywords": ["tinteggiatura", "intonaco", "subappalto", "reverse charge", "cantiere", "edilizia", "ristrutturazione"],
        "prompt_template": "Sei un esperto fiscale per l'edilizia (ISA {code}). Analizza i dati focalizzandoti su: {fields_str}. Considera specificamente: {keywords_str}."
    },
    "EK02U": {
        "desc": "Studi tecnici e professionisti",
        "fields": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        "context_keywords": ["prestazioni professionali", "studi tecnici", "consulenza", "progettazione", "parcelle"],
        "prompt_template": "Sei un esperto fiscale per professionisti (ISA {code}). Analizza i dati focalizzandoti su: {fields_str}. Considera specificamente: {keywords_str}."
    }
}

def extract_text_from_pdf(pdf_path):
    """Estrae il testo dalle prime 5 pagine del PDF per cercare il codice ISA."""
    try:
        text_content = ""
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_read = min(5, len(pdf.pages))
            for i in range(pages_to_read):
                page = pdf.pages[i]
                text_content += page.extract_text() or ""
        return text_content
    except Exception as e:
        print(f"Errore nella lettura del PDF: {e}")
        return ""

def identify_isa_code(pdf_path, text_content):
    """Identifica il codice ISA dal testo o dal nome del file."""
    isa_pattern = r"\b([A-Z]{2}\d{2,3}[A-Z])\b"
    
    # 1. Cerca nel testo estratto
    matches = re.findall(isa_pattern, text_content)
    for match in matches:
        if match in ISA_MAPPING:
            return match
            
    # 2. Fallback: Cerca nel nome del file
    filename = Path(pdf_path).stem.upper()
    match_file = re.search(isa_pattern, filename)
    if match_file and match_file.group(1) in ISA_MAPPING:
        return match_file.group(1)
        
    return None

def generate_prompt(isa_code):
    """Genera il prompt specifico basandosi sulla mappatura."""
    config = ISA_MAPPING[isa_code]
    
    fields_str = ", ".join(config['fields'][:10])
    if len(config['fields']) > 10:
        fields_str += f"... (e altri {len(config['fields'])-10} campi specifici)"
    
    keywords_str = ", ".join(config['context_keywords'])
    
    prompt = config['prompt_template'].format(
        code=isa_code,
        fields_str=fields_str,
        keywords_str=keywords_str
    )
    
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Utilizzo: python isa_prompt_engine.py <percorso_file_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"Errore: Il file {pdf_path} non esiste.")
        sys.exit(1)

    print(f"🔍 Analisi del file: {pdf_path}...")
    
    # 1. Estrazione testo
    text = extract_text_from_pdf(pdf_path)
    
    # 2. Identificazione Codice ISA
    isa_code = identify_isa_code(pdf_path, text)
    
    if not isa_code:
        print("❌ Impossibile identificare il codice ISA nel PDF o nel nome file.")
        print("Assicurati che il file si chiami es. 'FM87U_Istruzioni.pdf' o contenga il codice nelle prime pagine.")
        sys.exit(1)
        
    print(f"✅ Codice ISA Identificato: {isa_code}")
    print(f"📋 Descrizione: {ISA_MAPPING[isa_code]['desc']}")
    
    # 3. Generazione Prompt
    final_prompt = generate_prompt(isa_code)
    
    print("\n" + "="*50)
    print("🤖 PROMPT GENERATO PER L'AI")
    print("="*50)
    print(final_prompt)
    print("="*50)

if __name__ == "__main__":
    main()
