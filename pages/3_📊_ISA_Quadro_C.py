import streamlit as st
import pdfplumber
import re
import tempfile
import os
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="ISA - Compilazione Quadro C", layout="wide", page_icon="📊")

# =============================================================================
# REGOLE GENERALI (valide per TUTTI gli ISA) - NON dipendono dal PDF
# =============================================================================
GENERAL_RULES = """
REGOLE GENERALI DI COMPILAZIONE (valide per ogni ISA):
1. REVENUE RECOGNITION:
   - TD01 (Fattura): importo imponibile → positivo (+)
   - TD04 (Nota di credito): importo imponibile → negativo (–) come storno
   - Mai usare "Totale documento" (include IVA), sempre "Totale imponibile"

2. REGIMI IVA SPECIALI:
   - Split Payment (Art.17-ter): cercare "Art.17-ter", "scissione pagamenti", committente = PA
   - Reverse Charge (Art.17 c.6): cercare "Art.17 c.6", "N6.3", "subappalto edile", "lett. a-ter"
   - Ritenute Art.25 D.L. 78/2010: cercare "ritenuta acconto", "bonifico parlante", "ristrutturazioni"

3. LOCALIZZAZIONE:
   - Cercare nel testo: "presso cantiere di [Comune]", "in [Località]", "sito in [Indirizzo]"
   - Se assente: usare Comune del committente → SEGNALARE come ambiguo
   - Area territoriale: C36=Comune domicilio, C37=resto provincia, C38=resto regione, C39=Italia, C40=UE, C41=Extra-UE

4. NOTE DI CREDITO:
   - Devono stornare la STESSA categoria/luogo della fattura originale
   - Verificare coerenza temporale e descrittiva

5. SAFETY FIRST:
   - Se una fattura presenta anche solo un dubbio ragionevole → NON forzare classificazione
   - Segnalare in "NOTE E CRITICITÀ" con priorità (alta/media/bassa)
   - Meglio una segnalazione in più che un errore in dichiarazione
"""

# =============================================================================
# PARSER DINAMICO: estrae regole dal PDF caricato
# =============================================================================
def parse_isa_instructions(pdf_path):
    """
    Estrae struttura Quadro C dalle istruzioni ISA PDF.
    Restituisce dict con: campi, vincoli, descrizioni, parole_chiave, ambiguità.
    """
    result = {
        "isa_code": None,
        "descrizione": None,
        "campi": defaultdict(dict),
        "vincoli": [],
        "ambiguita_comuni": []
    }
    
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content += extracted + "\n"
    
    # 1. Estrai codice ISA
    pattern = r'\b([A-Z]{2}\d{2,3}[A-Z]?)\b'
    matches = re.findall(pattern, text_content)
    for match in matches:
        if match not in ['DPR', 'TUIR', 'IVA', 'CIG', 'PA', 'UE']:
            result["isa_code"] = match
            break
    
    # 2. Estrai descrizione attività (dopo il codice ISA)
    if result["isa_code"]:
        desc_pattern = rf'{result["isa_code"]}\s*\n?\s*([^\n•\n]+?)(?=\n\n|Il modello|PERIODO)'
        desc_match = re.search(desc_pattern, text_content, re.IGNORECASE)
        if desc_match:
            result["descrizione"] = desc_match.group(1).strip()
    
    # 3. Estrai sezioni Quadro C e campi
    # Cerca pattern: "nei righi da CXX a CYY" o "nel rigo CXX"
    section_pattern = r'(?:nei righi da|nel rigo)\s+(C\d+)(?:\s*a\s+(C\d+))?.*?(?=\n\n|–\s*nel|\Z)'
    
    for match in re.finditer(section_pattern, text_content, re.DOTALL):
        start_field = match.group(1)
        end_field = match.group(2)
        
        # Estrai descrizione della sezione
        section_text = match.group(0)
        
        # Estrai vincolo "somma 100%"
        if "100" in section_text and ("somma" in section_text.lower() or "totale" in section_text.lower() or "pari" in section_text):
            if end_field:
                result["vincoli"].append(f"{start_field}+...+{end_field} = 100%")
            else:
                result["vincoli"].append(f"{start_field} = 100% (se unico)")
        
        # Popola i campi
        if end_field:
            start_num = int(re.search(r'\d+', start_field).group())
            end_num = int(re.search(r'\d+', end_field).group())
            for i in range(start_num, end_num + 1):
                field_code = f"C{i:02d}"
                result["campi"][field_code]["section"] = f"{start_field}-{end_field}"
        else:
            result["campi"][start_field]["section"] = start_field
    
    # 4. Estrai descrizioni specifiche per campo (pattern: "– nel rigo CXX, ...")
    field_desc_pattern = r'–\s*nel rigo\s+(C\d+),?\s*(.+?)(?=\n\s*–\s*nel rigo|\n\s*Il totale|\n\s*Qualora|\Z)'
    
    for match in re.finditer(field_desc_pattern, text_content, re.DOTALL):
        field_code = match.group(1)
        description = match.group(2).strip()
        # Pulisci descrizione da riferimenti normativi lunghi
        description = re.sub(r'\(.*?D\.?P\.?R\.?.*?\)', '', description).strip()
        description = re.sub(r'\(.*?art\.?.*?\)', '', description).strip()
        
        result["campi"][field_code]["descrizione"] = description
        
        # Estrai parole chiave dalla descrizione per classificazione
        keywords = re.findall(r'"([^"]+)"', description)
        if keywords:
            result["campi"][field_code]["parole_chiave"] = keywords
    
    # 5. Estrai vincoli espliciti ("Il totale... deve risultare pari a 100")
    constraint_pattern = r'Il totale delle percentuali.*?(C\d+).*?(C\d+).*?100'
    for match in re.finditer(constraint_pattern, text_content):
        c1, c2 = match.group(1), match.group(2)
        result["vincoli"].append(f"{c1}+{c2} = 100%")
    
    # 6. Estrai note su ambiguità frequenti (sezioni con "Ad esempio", "Si precisa", ecc.)
    ambiguity_patterns = [
        r'(?:Ad esempio|Si precisa|Nell\'ambito).*?(riqualificazione|manutenzione|ristrutturazione|nuova costruzione).*?(?=\n\n|\.)',
        r'(?:attenzione|verificare|non confondere).*?(subappalto|reverse charge|split payment)',
    ]
    for pattern in ambiguity_patterns:
        for match in re.finditer(pattern, text_content, re.IGNORECASE):
            note = match.group(0).strip()
            if len(note) < 200:  # Evita blocchi troppo lunghi
                result["ambiguita_comuni"].append(note)
    
    # 7. Aggiungi ambiguità specifiche per EG75U (manutenzione ordinaria/straordinaria)
    if result["isa_code"] == "EG75U":
        result["ambiguita_comuni"].extend([
            "Distinguere manutenzione ordinaria (C27) da straordinaria/riqualificazione (C43) - verificare se intervento modifica caratteristiche prestazionali o solo ripristino",
            "Localizzazione: se fattura non indica cantiere, usare Comune committente ma segnalare ambiguità",
            "Subappalto (C30) vs lavori affidati a terzi: verificare se l'impresa è esecutrice diretta o coordinatrice"
        ])
    
    # 8. Aggiungi ambiguità per DG76U (catering vs mense)
    if result["isa_code"] == "DG76U":
        result["ambiguita_comuni"].extend([
            "Distinguere catering continuativo (C02) da banqueting non continuativo (C03) - verificare contratto: durata, luogo, tipologia evento",
            "Mense (C01): solo se preparazione e consumo nello stesso luogo; se veicolato → catering"
        ])
    
    return result


# =============================================================================
# GENERATORE PROMPT DINAMICO
# =============================================================================
def generate_dynamic_prompt(isa_data, general_rules=GENERAL_RULES):
    """
    Costruisce prompt con:
    - Regole generali (sempre valide)
    - Regole specifiche estratte dal PDF
    - Istruzioni di safety
    """
    isa_code = isa_data.get("isa_code", "UNKNOWN")
    descrizione = isa_data.get("descrizione", "Attività non specificata")
    
    prompt = f"""
🎯 RUOLO E OBIETTIVO
Ruolo: Agisci come un Consulente Fiscale Senior specializzato in ISA (Indici Sintetici di Affidabilità Fiscale), con competenza specifica sul codice attività {isa_code}: "{descrizione}".
Obiettivo: Compilare con precisione assoluta il Quadro C – Elementi specifici dell'attività del modello {isa_code} per il periodo d'imposta 2025, estraendo i dati esclusivamente dalla documentazione fornita e applicando rigorosamente le regole estratte dalle istruzioni ufficiali caricate.

{general_rules}

📋 REGOLE SPECIFICHE ESTRATTE DAL MODELLO {isa_code}
"""
    
    # Aggiungi campi estratti dal PDF
    if isa_data["campi"]:
        prompt += "\nCAMPI QUADRO C DA COMPILARE:\n"
        for campo, info in isa_data["campi"].items():
            desc = info.get("descrizione", "Descrizione non estratta - verificare istruzioni")
            section = info.get("section", "")
            keywords = info.get("parole_chiave", [])
            
            prompt += f"\n{campo}"
            if section and section != campo:
                prompt += f" [{section}]"
            prompt += f": {desc}"
            if keywords:
                prompt += f"\n  → Parole chiave per classificazione: {', '.join(keywords)}"
    
    # Aggiungi vincoli estratti
    if isa_data["vincoli"]:
        prompt += "\n\n⚠️ VINCOLI OBBLIGATORI (estratti dalle istruzioni):\n"
        for vincolo in isa_data["vincoli"]:
            prompt += f"- {vincolo}\n"
    
    # Aggiungi sezione ambiguità
    if isa_data["ambiguita_comuni"]:
        prompt += """
🔍 AMBIGUITÀ FREQUENTI PER QUESTO ISA (estratte + esperienza):
"""
        for amb in isa_data["ambiguita_comuni"]:
            prompt += f"- {amb}\n"
    
    # Template per segnalazione criticità
    prompt += """
🚨 FORMATO SEGNALAZIONE CRITICITÀ (obbligatorio per ogni dubbio):
Per ogni fattura con classificazione incerta, usare questo template:

[CRITICITÀ - PRIORITÀ: ALTA/MEDIA/BASSA]
Fattura N. [XXX] del [DD-MM-YYYY]
Problema: [descrizione breve]
Ipotesi di classificazione: [campo proposto] + [motivazione]
Dati mancanti per certezza: [cosa servirebbe]
Raccomandazione: [verificare con cliente / chiedere documentazione / assumere con cautela]

📤 FORMATO OUTPUT FINALE RICHIESTO:
1. TABELLA RIEPILOGATIVA Quadro C compilato (Campo | Valore | N. fatture incluse)
2. ANALISI DI COERENZA (verifica vincoli, somme percentuali, regimi IVA)
3. SEGNALAZIONE CRITICITÀ (usando template sopra)
4. CHECKLIST PRE-INVIO:
   - [ ] Tutti i vincoli di somma % rispettati (tolleranza 0,1%)
   - [ ] Note di credito applicate come storni (non nuovi ricavi)
   - [ ] Regimi IVA (split/reverse) coerenti con fatture
   - [ ] Localizzazioni allocate correttamente (C36-C40)
   - [ ] Ambiguità segnalate, non nascoste

💡 ISTRUZIONE FINALE DI SAFETY:
Se una fattura presenta anche solo un dubbio ragionevole su:
- classificazione attività (es. ordinaria vs straordinaria)
- localizzazione esecuzione
- regime IVA applicabile
- ambito (nuova costruzione vs recupero)
→ NON forzare una classificazione certa. Segnalala nella sezione 'CRITICITÀ' e, solo se strettamente necessario, indica l'ipotesi più probabile specificando chiaramente: "ASSUNZIONE DA VALIDARE". In ambito ISA: meglio una segnalazione in più che un errore in dichiarazione.
"""
    
    return prompt


# =============================================================================
# INTERFACCIA STREAMLIT (mantenuta, con upgrade)
# =============================================================================
st.title("📊 ISA - Compilazione Quadro C")
st.markdown("Carica le **Istruzioni ISA** e il **Modello Quadro C** per generare un prompt contestuale e preciso")

# Upload multiplo: istruzioni + modello
uploaded_files = st.file_uploader(
    "📄 Carica PDF: Istruzioni ISA + Modello Quadro C", 
    type=['pdf'],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner('🔍 Analisi PDF in corso...'):
        try:
            # Processa ogni file caricato
            parsed_data = None
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Prova a parsare
                temp_result = parse_isa_instructions(tmp_path)
                
                # Se troviamo un codice ISA valido, usiamo questo parsing
                if temp_result["isa_code"] and not parsed_data:
                    parsed_data = temp_result
                elif parsed_data and temp_result["isa_code"]:
                    # Merge se entrambi hanno dati utili
                    for k in ["campi", "vincoli", "ambiguita_comuni"]:
                        if isinstance(parsed_data.get(k), dict) and isinstance(temp_result.get(k), dict):
                            parsed_data[k].update(temp_result[k])
                        elif isinstance(parsed_data.get(k), list) and isinstance(temp_result.get(k), list):
                            parsed_data[k].extend(temp_result[k])
                
                os.unlink(tmp_path)
            
            if parsed_data and parsed_data["isa_code"]:
                st.success(f"✅ Codice ISA rilevato: **{parsed_data['isa_code']}**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Settore", parsed_data.get('descrizione', 'N/A')[:50] + "..." if len(str(parsed_data.get('descrizione', ''))) > 50 else parsed_data.get('descrizione', 'N/A'))
                with col2:
                    st.metric("Campi estratti", len(parsed_data["campi"]))
                with col3:
                    st.metric("Vincoli trovati", len(parsed_data["vincoli"]))
                
                # Anteprima regole estratte (debug/trasparenza)
                with st.expander("🔍 Anteprima regole estratte dal PDF"):
                    st.write("**Campi Quadro C identificati:**")
                    for campo, info in list(parsed_data["campi"].items())[:10]:
                        st.write(f"- {campo}: {info.get('descrizione', 'N/A')[:100]}...")
                    
                    if parsed_data["vincoli"]:
                        st.write("\n**Vincoli:**")
                        for v in parsed_data["vincoli"]:
                            st.write(f"- {v}")
                
                # Genera prompt dinamico
                prompt = generate_dynamic_prompt(parsed_data)
                
                st.subheader("🤖 Prompt Generato (dinamico da PDF)")
                st.code(prompt, language='text')
                
                st.download_button(
                    label="📥 Scarica Prompt (.txt)",
                    data=prompt,
                    file_name=f"prompt_{parsed_data['isa_code']}_quadro_c_dynamic.txt",
                    mime="text/plain",
                    type="primary"
                )
                
            else:
                st.warning("⚠️ Nessun codice ISA riconosciuto nei PDF caricati")
                # Mostra anteprima testo per debug
                with st.expander("🔧 Debug: anteprima testo estratto"):
                    st.text("Carica file con nome contenente codice ISA (es. EG75U) e verifica che le istruzioni contengano 'Quadro C'")
                
        except Exception as e:
            st.error(f"❌ Errore durante l'analisi: {str(e)}")
            st.exception(e)
else:
    st.info("👆 Carica almeno un PDF (Istruzioni ISA e/o Modello Quadro C) per iniziare")
    st.markdown("""
    💡 **Suggerimenti per upload ottimale**:
    - Carica sia `EG75U Istruzioni.pdf` che `EG75U Modello.pdf` per estrazione completa
    - Il nome del file dovrebbe contenere il codice ISA (es. `EG75U`, `DG76U`)
    - Le istruzioni devono contenere la sezione "Quadro C – Elementi specifici dell'attività"
    """)
