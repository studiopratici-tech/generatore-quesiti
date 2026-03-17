import re
import sys
import pdfplumber
import json
from pathlib import Path

# ==============================================================================
# CONFIGURAZIONE E MAPPATURA ISA (Standard Agenzia delle Entrate)
# ==============================================================================
# I campi del Quadro C sono standardizzati per ogni codice ISA.
# Questa mappa assicura che l'estrazione sia precisa e non dipenda dal layout del PDF.
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
        "fields": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C86", "C87", "C88", "C89", "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97", "C98", "C99", "C100"], 
        # Nota: Semplificato per l'esempio, nella realtà va mappato campo per campo specifico per professionisti
        "context_keywords": ["prestazioni professionali", "studi tecnici", "consulenza", "progettazione", "parcelle"],
        "prompt_template": "Sei un esperto fiscale per professionisti (ISA {code}). Analizza i dati focalizzandoti su: {fields_str}. Considera specificamente: {keywords_str}."
    }
}

def extract_text_from_pdf(pdf_path):
    """Estrae il testo dalle prime 5 pagine del PDF per cercare il codice ISA."""
    try:
        text_content = ""
        with pdfplumber.open(pdf_path) as pdf:
            # Leggiamo solo le prime pagine dove solitamente si trova il codice ISA
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
    # Pattern per codici ISA (es. FM87U, EG50U)
    isa_pattern = r"\b([A-Z]{2}\d{2}[A-Z])\b"
    
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
    
    # Formatta i campi (es. C01-C08 invece di lista lunga)
    # Per brevità nel prompt, mostriamo i range o i primi/ultimi se la lista è lunga
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
    print("="*5Ecco i file pronti per essere caricati su GitHub. Questa soluzione è strutturata in modo professionale: separa la logica (`main.py`) dai dati di configurazione (`isa_config.json`), permettendo di aggiungere nuovi modelli ISA in futuro senza toccare il codice.

### Struttura del Progetto
Crea una cartella e inserisci questi 4 file:

1.  `requirements.txt`
2.  `isa_config.json`
3.  `main.py`
4.  `README.md`

---

### 1. `requirements.txt`
Le librerie necessarie per leggere i PDF.

```text
pdfplumber>=0.10.0

import re
import sys
import pdfplumber
import json
from pathlib import Path

# ==============================================================================
# CONFIGURAZIONE E MAPPATURA ISA (Standard Agenzia delle Entrate)
# ==============================================================================
# I campi del Quadro C sono standardizzati per ogni codice ISA.
# Questa mappa assicura che l'estrazione sia precisa e non dipenda dal layout del PDF.
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
        "fields": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C86", "C87", "C88", "C89", "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97", "C98", "C99", "C100"], 
        # Nota: Semplificato per l'esempio, nella realtà va mappato campo per campo specifico per professionisti
        "context_keywords": ["prestazioni professionali", "studi tecnici", "consulenza", "progettazione", "parcelle"],
        "prompt_template": "Sei un esperto fiscale per professionisti (ISA {code}). Analizza i dati focalizzandoti su: {fields_str}. Considera specificamente: {keywords_str}."
    }
}

def extract_text_from_pdf(pdf_path):
    """Estrae il testo dalle prime 5 pagine del PDF per cercare il codice ISA."""
    try:
        text_content = ""
        with pdfplumber.open(pdf_path) as pdf:
            # Leggiamo solo le prime pagine dove solitamente si trova il codice ISA
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
    # Pattern per codici ISA (es. FM87U, EG50U)
    isa_pattern = r"\b([A-Z]{2}\d{2}[A-Z])\b"
    
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
    
    # Formatta i campi (es. C01-C08 invece di lista lunga)
    # Per brevità nel prompt, mostriamo i range o i primi/ultimi se la lista è lunga
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
    print("="*5Ecco i file pronti per essere caricati su GitHub. Questa soluzione è strutturata in modo professionale: separa la logica (`main.py`) dai dati di configurazione (`isa_config.json`), permettendo di aggiungere nuovi modelli ISA in futuro senza toccare il codice.

### Struttura del Progetto
Crea una cartella e inserisci questi 4 file:

1.  `requirements.txt`
2.  `isa_config.json`
3.  `main.py`
4.  `README.md`

---

### 1. `requirements.txt`
Le librerie necessarie per leggere i PDF.

```text
pdfplumber>=0.10.0

import pdfplumber
import json
import re
import sys
import os

class ISAPromptGenerator:
    def __init__(self, config_path='isa_config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.isa_code = None
        self.pdf_text = ""

    def load_config(self):
        """Carica il database dei modelli ISA"""
        if not os.path.exists(self.config_path):
            print(f"Errore: File di configurazione '{self.config_path}' non trovato.")
            sys.exit(1)
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_text_from_pdf(self, pdf_path):
        """Estrae il testo dal PDF caricato"""
        if not os.path.exists(pdf_path):
            print(f"Errore: File PDF '{pdf_path}' non trovato.")
            sys.exit(1)
        
        print(f"📄 Lettura del file: {pdf_path}...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        self.pdf_text += text
            print("✅ Estrazione testo completata.")
        except Exception as e:
            print(f"❌ Errore nella lettura del PDF: {e}")
            sys.exit(1)

    def detect_isa_code(self):
        """Cerca automaticamente il codice ISA nel testo estratto"""
        # Pattern generico per codici ISA (es. FM87U, EG50U)
        pattern = r'\b([A-Z]{2}\d{3}[A-Z])\b'
        matches = re.findall(pattern, self.pdf_text)
        
        # Filtra solo i codici presenti nel nostro config
        valid_codes = [code for code in matches if code in self.config]
        
        if not valid_codes:
            print("⚠️  Nessun codice ISA riconosciuto nel PDF.")
            print("🔍 Codici trovati nel testo (potenziali):", list(set(matches))[:5])
            sys.exit(1)
        
        # Prende il codice più frequente o il primo valido
        self.isa_code = max(set(valid_codes), key=valid_codes.count)
        print(f"🔍 Codice ISA rilevato: {self.isa_code}")

    def generate_prompt(self):
        """Genera il prompt specifico basato sulla configurazione"""
        if not self.isa_code:
            return

        data = self.config[self.isa_code]
        campi = ", ".join(data['campi_rilevanti'])
        temi = ", ".join(data['temi_prompt'])
        
        prompt = f"""
--- INIZIO PROMPT ISA {self.isa_code} ---
RUOLO: Sei un esperto consulente fiscale specializzato in ISA (Indici Sintetici di Affidabilità).
MODELLO RILEVATO: {self.isa_code} ({data['descrizione']})

ISTRUZIONI SPECIFICHE:
Analizza i dati forniti considerando ESCLUSIVAMENTE i campi del Quadro C rilevanti per questo modello:
[{campi}]

CONTESTO DA PRIORITIZZARE:
Il prompt deve focalizzarsi sui seguenti aspetti merceologici e operativi:
{temi}

NOTE OPERATIVE:
{data['note']}

OUTPUT RICHIESTO:
Genera un'analisi coerente con i parametri specifici del modello {self.isa_code}, ignorando campi non pertinenti (es. non parlare di cantieri se è un commercio).
--- FINE PROMPT ---
"""
        return prompt

    def run(self, pdf_path):
        """Esegue l'intero flusso"""
        self.extract_text_from_pdf(pdf_path)
        self.detect_isa_code()
        prompt = self.generate_prompt()
        
        print("\n" + "="*40)
        print("🚀 PROMPT GENERATO")
        print("="*40 + "\n")
        print(prompt)
        
        # Salva anche in un file di output
        output_file = f"prompt_{self.isa_code}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"\n💾 Prompt salvato in: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilizzo: python main.py <percorso_file.pdf>")
        print("Esempio: python main.py 'FM87U Istruzioni.pdf'")
        sys.exit(1)

    pdf_file = sys.argv[1]
    app = ISAPromptGenerator()
    app.run(pdf_file)
