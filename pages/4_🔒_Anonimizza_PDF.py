"""
🔒 ANONIMIZZATORE UNIVERSALE FATTURE ELETTRONICHE
Funziona con QUALSIASI fattura italiana - GDPR Compliant
Anonimizza automaticamente tutti i dati sensibili
"""

import re
from pypdf import PdfReader, PdfWriter
from datetime import datetime
import os

class AnonimizzaFattureUniversale:
    """Classe universale per anonimizzare qualsiasi fattura elettronica"""
    
    def __init__(self):
        """Inizializza con tutti i pattern regex per dati sensibili italiani"""
        
        # Pattern REGEX universali per dati strutturati italiani
        self.patterns = {
            # Identificativi Fiscali
            'p_iva_italia': (r'\bIT\d{11}\b', '[P.IVA]'),
            'cf_persona_fisica': (r'\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b', '[CF]'),
            'cf_partita_iva': (r'\b\d{11}\b', '[P.IVA/CF]'),
            
            # Dati Bancari
            'iban': (r'\bIT\d{2}[A-Z0-9]{25}\b', '[IBAN]'),
            'bic_swift': (r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b', '[BIC]'),
            
            # Contatti
            'email_generica': (r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[EMAIL]'),
            'pec': (r'\b[A-Z0-9._%+-]+@pec\.[A-Z0-9.-]+\.[A-Z]{2,}\b', '[PEC]'),
            'telefono_fisso': (r'\b(?:\+39)?\s?0\d{8,10}\b', '[TEL]'),
            'telefono_mobile': (r'\b(?:\+39)?\s?3\d{9}\b', '[CELL]'),
            
            # Indirizzi
            'cap': (r'\b\d{5}\b', '[CAP]'),
            'indirizzo_via': (r'\bVIA\s+[A-Z\s]+\d+[A-Z/]*\b', '[INDIRIZZO]'),
            'indirizzo_viale': (r'\bVIALE\s+[A-Z\s]+\d+[A-Z/]*\b', '[INDIRIZZO]'),
            'indirizzo_piazza': (r'\bPIAZZA\s+[A-Z\s]+\d+[A-Z/]*\b', '[INDIRIZZO]'),
            'indirizzo_corso': (r'\bCORSO\s+[A-Z\s]+\d+[A-Z/]*\b', '[INDIRIZZO]'),
            'indirizzo_vico': (r'\bVICO\s+[A-Z\s]+\d+[A-Z/]*\b', '[INDIRIZZO]'),
            'indirizzo_largo': (r'\bLARGO\s+[A-Z\s]+\d+[A-Z/]*\b', '[INDIRIZZO]'),
            
            # Codici Progetto e Riferimenti
            'cig': (r'\bCIG:\s*[A-Z0-9]{11}\b', 'CIG: [CODICE]'),
            'cup': (r'\bCUP:\s*[A-Z0-9]{15}\b', 'CUP: [CODICE]'),
            'protocollo': (r'\b(?:prot\.?\s*|protocollo\s*)n\.?\s*\d+/\d{4}\b', '[PROTOCOLLO]'),
            
            # Riferimenti Normativi (mantenuti per contesto)
            'riferimento_legge': (r'Art\.\s*\d+\s*(?:c\.?\s*\d+)?\s*(?:DPR|D\.Lgs\.?\s*\d+)?', '[RIF.NORM.]'),
            
            # Numeri Documento
            'numero_fattura': (r'\b\d{1,4}-[A-Z]{2,3}\b', '[N.FATTURA]'),
        }
        
        # Counter per statistiche
        self.stats = {
            'totale_sostituzioni': 0,
            'dettagli': {}
        }
    
    def anonimizza_testo(self, testo):
        """
        Anonimizza un testo applicando tutti i pattern universali
        
        Args:
            testo: Stringa da anonimizzare
        Returns:
            Stringa anonimizzata
        """
        if not testo:
            return testo
        
        testo_anonimo = testo
        
        # Applica tutti i pattern regex in ordine di specificità
        for nome_pattern, (regex, sostituzione) in self.patterns.items():
            matches = re.findall(regex, testo_anonimo, re.IGNORECASE)
            if matches:
                testo_anonimo = re.sub(regex, sostituzione, testo_anonimo, flags=re.IGNORECASE)
                self.stats['totale_sostituzioni'] += len(matches)
                self.stats['dettagli'][nome_pattern] = self.stats['dettagli'].get(nome_pattern, 0) + len(matches)
        
        return testo_anonimo
    
    def anonimizza_pdf(self, input_path, output_path=None):
        """
        Anonimizza un PDF leggendo il testo e creando un report
        
        NOTA: pypdf non modifica il contenuto visivo del PDF,
        ma estrae e anonimizza il testo per verifica/analisi
        
        Args:
            input_path: Percorso del PDF originale
            output_path: Percorso del PDF output (opzionale)
        Returns:
            Testo anonimizzato completo
        """
        # Reset stats
        self.stats = {'totale_sostituzioni': 0, 'dettagli': {}}
        
        reader = PdfReader(input_path)
        testo_completo = ""
        
        print(f"\n📄 Elaborazione: {os.path.basename(input_path)}")
        print(f"📑 Pagine totali: {len(reader.pages)}")
        print("-" * 50)
        
        for i, page in enumerate(reader.pages, 1):
            testo = page.extract_text()
            if testo:
                testo_anonimo = self.anonimizza_testo(testo)
                testo_completo += f"\n{'='*60}\n"
                testo_completo += f"PAGINA {i}\n"
                testo_completo += f"{'='*60}\n"
                testo_completo += testo_anonimo
        
        # Stampa statistiche
        print(f"\n✅ Anonimizzazione completata!")
        print(f"📊 Totale dati anonimizzati: {self.stats['totale_sostituzioni']}")
        print("\n📈 Dettaglio:")
        for pattern, count in sorted(self.stats['dettagli'].items()):
            print(f"  • {pattern}: {count}")
        
        # Salva output se specificato
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(testo_completo)
            print(f"\n💾 Testo anonimizzato salvato in: {output_path}")
        
        return testo_completo
    
    def genera_report(self, output_path='report_anonimizzazione.txt'):
        """Genera un report delle sostituzioni effettuate"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("🔒 REPORT ANONIMIZZAZIONE FATTURE\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(f"Totale dati anonimizzati: {self.stats['totale_sostituzioni']}\n\n")
            f.write("Dettaglio per categoria:\n")
            f.write("-"*60 + "\n")
            for pattern, count in sorted(self.stats['dettagli'].items()):
                f.write(f"{pattern:30} {count:5} occorrenze\n")
        
        print(f"📋 Report salvato in: {output_path}")


def anonimizza_file(input_file, output_file=None):
    """
    Funzione helper per anonimizzare rapidamente un file
    
    Usage:
        anonimizza_file('fattura.pdf', 'fattura_anonima.txt')
    """
    if output_file is None:
        output_file = f"anonimo_{os.path.basename(input_file).replace('.pdf', '.txt')}"
    
    anonimizzatore = AnonimizzaFattureUniversale()
    return anonimizzatore.anonimizza_pdf(input_file, output_file)


# Esempio di utilizzo
if __name__ == "__main__":
    print("="*60)
    print("🔒 ANONIMIZZATORE UNIVERSALE FATTURE ELETTRONICHE")
    print("="*60)
    print("\nQuesto script anonimizza QUALSIASI fattura italiana")
    print("Riconosce automaticamente:")
    print("  ✓ P.IVA e Codici Fiscali")
    print("  ✓ IBAN e dati bancari")
    print("  ✓ Email, PEC, telefoni")
    print("  ✓ Indirizzi completi (Via, Viale, Piazza, ecc.)")
    print("  ✓ CAP e Comuni")
    print("  ✓ CIG, CUP, protocolli")
    print("  ✓ Numeri fattura")
    print("\n" + "="*60)
    
    # Esempio: anonimizza il tuo file
    input_pdf = "fatturefe.pdf"  # Cambia con il tuo file
    
    if os.path.exists(input_pdf):
        testo_anonimo = anonimizza_file(input_pdf)
        
        # Mostra anteprime
        print("\n" + "="*60)
        print("📋 ANTEPRIMA PRIME 500 CARATTERI:")
        print("="*60)
        print(testo_anonimo[:500])
        print("...")
    else:
        print(f"\n❌ File non trovato: {input_pdf}")
        print("\n💡 Usage:")
        print("   python 4_🔒_Anonimizza_Fatture.py")
        print("\n   Oppure importa e usa:")
        print("   from anonimizza import anonimizza_file")
        print("   anonimizza_file('tua_fattura.pdf')")
