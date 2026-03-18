#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISA Universal Prompt Generator
Genera prompt per compilazione Quadro C per tutti i 25 modelli ISA
"""

import json
import re
import sys
import pdfplumber
from pathlib import Path
from datetime import datetime

class ISAPromptGenerator:
    def __init__(self, mapping_path='isa_mapping.json'):
        self.mapping_path = mapping_path
        self.mapping = self.load_mapping()
        self.isa_code = None
        self.pdf_text = ""
    
    def load_mapping(self):
        """Carica il database dei 25 modelli ISA"""
        if not Path(self.mapping_path).exists():
            print(f"❌ Errore: File '{self.mapping_path}' non trovato.")
            sys.exit(1)
        with open(self.mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_text_from_pdf(self, pdf_path):
        """Estrae testo dal PDF delle istruzioni ISA"""
        if not Path(pdf_path).exists():
            print(f"❌ Errore: File PDF '{pdf_path}' non trovato.")
            sys.exit(1)
        
        print(f"📄 Lettura PDF: {pdf_path}...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        self.pdf_text += text + "\n"
            print("✅ Estrazione testo completata.")
        except Exception as e:
            print(f"❌ Errore lettura PDF: {e}")
            sys.exit(1)
    
    def detect_isa_code(self, pdf_path):
        """Identifica il codice ISA dal PDF o nome file"""
        pattern = r'\b([A-Z]{2}\d{2,3}[A-Z])\b'
        
        matches = re.findall(pattern, self.pdf_text)
        for match in matches:
            if match in self.mapping:
                self.isa_code = match
                print(f"🔍 Codice ISA rilevato nel PDF: {self.isa_code}")
                return
        
        filename = Path(pdf_path).stem.upper()
        match_file = re.search(pattern, filename)
        if match_file and match_file.group(1) in self.mapping:
            self.isa_code = match_file.group(1)
            print(f"🔍 Codice ISA rilevato dal nome file: {self.isa_code}")
            return
        
        print("❌ Nessun codice ISA riconosciuto.")
        print(f"📋 Codici trovati: {list(set(matches))[:10]}")
        sys.exit(1)
    
    def generate_quadro_c_prompt(self):
        """Genera prompt ESCLUSIVO per compilazione Quadro C"""
        if not self.isa_code:
            return
        
        data = self.mapping[self.isa_code]
        fields = data['quadro_c']
        docs = data['documenti_richiesti']
        note = data['note']
        desc = data['descrizione']
        
        fields_str = ", ".join(fields)
        docs_str = "\n".join([f"  📄 {doc}" for doc in docs])
        
        prompt = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              COMPILAZIONE QUADRO C - ISA {self.isa_code}                    ║
║                    {desc}
╚══════════════════════════════════════════════════════════════════════════╝

📌 MODELLO ISA: {self.isa_code}
📋 DESCRIZIONE: {desc}
📅 DATA GENERAZIONE: {datetime.now().strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **ATTENZIONE - LEGGERE PRIMA DI PROCEDERE**

Questo prompt riguarda **ESCLUSIVAMENTE la compilazione del Quadro C**.

❌ **NON** fornire dati da altri quadri (A, B, D, E, F, H) - quelli li gestiamo noi
❌ **NON** inventare valori o fare stime
❌ **NON** procedere senza documentazione a supporto

✅ **DEVI** fornire SOLO i dati del Quadro C elencati sotto
✅ **DEVI** avere documentazione a supporto per ogni valore
✅ **DEVI** essere preciso nei valori numerici e percentuali

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 **DOCUMENTI DA ALLEGARE (PDF)**:

{docs_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **CAMPI DEL QUADRO C DA COMPILARE**:

{fields_str}

**TOTALE CAMPI: {len(fields)}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️ **ISTRUZIONI PER LA COMPILAZIONE**:

Per **CIASCUN CAMPO** del Quadro C elencato sopra, fornisci:

┌─────────────────────────────────────────────────────────────────────┐
│ CAMPO: C##                                                           │
│ VALORE: [inserire valore numerico o percentuale]                    │
│ FONTE DOCUMENTALE: [es. Bilancio 2024 pag. X / Fattura n. Y]       │
│ DESCRIZIONE: [breve descrizione di cosa rappresenta il dato]        │
│ NOTE: [eventuali criticità, anomalie o osservazioni]                │
│ COERENZA: [✓ coerente / ⚠️ da verificare / ✗ anomalo]              │
└─────────────────────────────────────────────────────────────────────┘

**RIPETERE QUESTO SCHEMA PER TUTTI I {len(fields)} CAMPI**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **REGOLE SPECIFICHE PER {self.isa_code}**:

{note}

**IMPORTANTE**: Le percentuali indicate nei campi del Quadro C devono 
sommaare esattamente **100%** dove richiesto dalle istruzioni ISA.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **CONTROLLI DI COERENZA OBBLIGATORI**:

□ Tutte le percentuali sommano 100% (dove richiesto)
□ I valori sono coerenti con la documentazione allegata
□ Non ci sono duplicazioni di ricavi/costi
□ I dati sono congrui con il settore {desc}
□ Eventuali anomalie sono giustificate e documentate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **OUTPUT FINALE RICHIESTO**:

Al termine della compilazione, fornirai:

1. **TABELLA RIEPILOGATIVA** con tutti i {len(fields)} campi compilati
2. **ANALISI DI COERENZA** interna tra i vari campi
3. **SEGNALAZIONE CRITICITÀ** o valori anomali riscontrati
4. **CHECKLIST PRE-INVIO** completata

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **NOTE IMPORTANTI**:

- Questo prompt è specifico per il modello **ISA {self.isa_code}**
- Utilizza **SOLO** i dati estratti dalla documentazione allegata
- **CITA SEMPRE** la fonte documentale per ogni campo
- **SEGNALA** se un campo non può essere compilato per mancanza dati
- I quadri A, B, D, E, F, H sono gestiti separatamente dal consulente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **PROCEDI CON L'ANALISI DEI DOCUMENTI ALLEGATI E LA COMPILAZIONE 
DEL QUADRO C SECONDO LE ISTRUZIONI SOPRA**.

══════════════════════════════════════════════════════════════════════════
"""
        return prompt
    
    def run(self, pdf_path):
        """Esegue l'intero flusso"""
        self.extract_text_from_pdf(pdf_path)
        self.detect_isa_code(pdf_path)
        
        print(f"\n✅ ISA Identificato: {self.isa_code}")
        print(f"📋 {self.mapping[self.isa_code]['descrizione']}")
        print(f"📊 Campi Quadro C: {len(self.mapping[self.isa_code]['quadro_c'])}")
        
        prompt = self.generate_quadro_c_prompt()
        
        print("\n" + "="*70)
        print("🤖 PROMPT GENERATO")
        print("="*70 + "\n")
        print(prompt)
        
        output_file = f"prompt_{self.isa_code}_quadro_c.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"\n💾 Prompt salvato in: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilizzo: python main.py <percorso_file.pdf>")
        print("Esempio: python main.py 'EG50U_Istruzioni.pdf'")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    app = ISAPromptGenerator()
    app.run(pdf_file)
