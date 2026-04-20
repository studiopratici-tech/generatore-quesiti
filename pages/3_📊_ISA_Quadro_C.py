import streamlit as st
import pdfplumber
import re
import tempfile
import os
from collections import defaultdict

st.set_page_config(page_title="ISA - Compilazione Quadro C PRO", layout="wide", page_icon="📊")

# =============================================================================
# REGOLE GENERALI (valide per TUTTI gli ISA)
# =============================================================================
GENERAL_RULES = """
REGOLE GENERALI DI COMPILAZIONE (valide per ogni ISA):
1. REVENUE RECOGNITION:
   - TD01 (Fattura): importo imponibile → positivo (+)
   - TD04 (Nota di credito): importo imponibile → negativo (–) come storno
   - Mai usare "Totale documento" (include IVA), sempre "Totale imponibile"

2. REGIMI IVA SPECIALI:
   - Split Payment (Art.17-ter): cercare "Art.17-ter", "scissione pagamenti", committente = PA
   - Reverse Charge (Art.17 c.6): cercare "Art.17 c.6", "N6.3", "subappalto edile"
   - Ritenute Art.25 D.L. 78/2010: cercare "ritenuta acconto", "bonifico parlante"

3. SAFETY FIRST:
   - Se una fattura presenta anche solo un dubbio ragionevole → NON forzare classificazione
   - Segnalare in "NOTE E CRITICITÀ" con priorità (alta/media/bassa)
   - Meglio una segnalazione in più che un errore in dichiarazione
"""

# =============================================================================
# PARSER MODELLO: VERSIONE OTTIMIZZATA PER LAYOUT A SEZIONI (universale)
# =============================================================================
def parse_modello(pdf_path):
    result = {
        "isa_code": None,
        "campi": defaultdict(dict),
        "vincoli_modello": []
    }
    
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content += extracted + "\n"
    
    # Estrai codice ISA
    pattern = r'\b([A-Z]{2}\d{2,3}[A-Z]?)\b'
    matches = re.findall(pattern, text_content)
    for match in matches:
        if match not in ['DPR', 'TUIR', 'IVA', 'CIG', 'PA', 'UE', 'DDT', 'SAT']:
            result["isa_code"] = match
            break
    
    # 🎯 ESTRAGGO CAMPI C## CERCANDO NEL TESTO COMPLETO
    # Strategia: per ogni C## trovato, cerco il testo descrittivo nelle vicinanze
    
    # Trova tutte le occorrenze di C## nel testo con la loro posizione
    all_codes = [f"C{i:02d}" for i in range(1, 44)]
    
    for code in all_codes:
        # Cerca il codice nel testo
        code_pattern = rf'\b{re.escape(code)}\b'
        matches = list(re.finditer(code_pattern, text_content, re.IGNORECASE))
        
        if not matches:
            continue
        
        # Per ogni occorrenza del codice, cerca la descrizione dopo di esso
        for match in matches:
            # Prendi il testo DOPO il codice (fino a 300 caratteri)
            start_pos = match.end()
            end_pos = min(start_pos + 300, len(text_content))
            after_code = text_content[start_pos:end_pos]
            
            # Estrai la prima frase significativa dopo il codice
            # Ignora %, numeri, "TOT", "Sezione", ecc.
            lines = after_code.split('\n')
            description_parts = []
            
            for line in lines:
                line = line.strip()
                
                # Salta linee vuote o troppo corte
                if not line or len(line) < 5:
                    continue
                
                # Salta linee che sono solo numeri, %, separatori
                if re.match(r'^[\d\s,.\-()%|]+$', line):
                    continue
                
                # Salta header/sezioni
                if any(kw in line.upper() for kw in [
                    'SEZIONE', 'TOT', 'RICAVI', 'PERCENTUALE', 
                    'MODALITÀ', 'TIPOLOGIA', 'QUADRO', 'CAMPO',
                    'AREA', 'AMBITO', 'PRODUZIONE'
                ]):
                    continue
                
                # Trovato testo valido!
                description_parts.append(line)
                
                # Se abbiamo abbastanza testo, fermati
                if len(' '.join(description_parts)) > 20:
                    break
            
            # Costruisci descrizione finale
            if description_parts:
                description = ' '.join(description_parts)
                description = re.sub(r'\s+', ' ', description)  # Normalizza spazi
                description = re.sub(r'[\|\-]', ' ', description)
                description = description.strip(".,;:()")
                
                # Salva solo se significativo (>15 caratteri)
                if len(description) >= 15:
                    result["campi"][code]["descrizione"] = description
                    result["campi"][code]["estratto_da_pdf"] = True
                    break  # Usa la prima occorrenza valida
    
    # Estrai vincoli dal modello
    if "TOT" in text_content and "100" in text_content:
        if "C01" in text_content and "C25" in text_content:
            result["vincoli_modello"].append("C01+C02+...+C25 = 100% (Specializzazione)")
        if "C26" in text_content and "C30" in text_content:
            result["vincoli_modello"].append("C26+C27+C28+C29+C30 = 100% (Tipologia servizio)")
        if "C37" in text_content and "C40" in text_content:
            result["vincoli_modello"].append("C37+C38+C39+C40 = 100% (Area svolgimento)")
        if "C41" in text_content and "C43" in text_content:
            result["vincoli_modello"].append("C41+C42+C43 = 100% (Ambito attività)")
    
    return result

# =============================================================================
# PARSER ISTRUZIONI: estrae REGOLE e VINCOLI di compilazione
# =============================================================================
def parse_istruzioni(pdf_path):
    result = {
        "vincoli_istruzioni": [],
        "ambiguita_comuni": [],
        "note_compilazione": []
    }
    
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content += extracted + "\n"
    
    constraint_patterns = [
        r'Il totale.*?percentuali.*?(C\d+).*?(C\d+).*?100',
        r'totale.*?pari a 100',
        r'deve risultare pari a 100',
    ]
    for pattern in constraint_patterns:
        for match in re.finditer(pattern, text_content, re.IGNORECASE):
            result["vincoli_istruzioni"].append("Somma percentuali = 100%")
    
    ambiguity_patterns = [
        r'(?:Ad esempio|Si precisa|Nell\'ambito).*?(riqualificazione|manutenzione|ristrutturazione|nuova costruzione).*?(?=\n\n|\.)',
        r'(?:attenzione|verificare|non confondere).*?(subappalto|reverse charge|split payment)',
    ]
    for pattern in ambiguity_patterns:
        for match in re.finditer(pattern, text_content, re.IGNORECASE):
            note = match.group(0).strip()
            if len(note) < 250:
                result["ambiguita_comuni"].append(note)
    
    if "EG75U" in text_content:
        result["ambiguita_comuni"].extend([
            "⚠️ CRITICO: Distinguere manutenzione (C27) da riqualificazione/recupero (C43) - C27 = ripristino funzionalità esistente, C43 = miglioramento prestazionale (art.3 DPR 380/2001)",
            "Localizzazione: se fattura non indica cantiere, usare Comune committente ma segnalare ambiguità",
            "Subappalto (C30): solo se lavori acquisiti da altra impresa, NON confondere con lavori affidati a terzi"
        ])
    
    if "DG76U" in text_content:
        result["ambiguita_comuni"].extend([
            "Distinguere catering continuativo (C02) da banqueting non continuativo (C03) - verificare contratto: durata, luogo, tipologia evento",
            "Mense (C01): solo se preparazione e consumo nello stesso luogo; se veicolato → catering"
        ])
    
    return result

# =============================================================================
# VALIDATORE OUTPUT AI (controllo matematico automatico)
# =============================================================================
def validate_ai_output(ai_text: str) -> dict:
    """Verifica che le somme percentuali siano corrette e tutti i campi siano presenti."""
    errors = []
    warnings = []
    import re
    # Cerca pattern tipo: | C01 | Descrizione | 25,5% |
    pattern = r'\|\s*(C\d{2})\s*\|.*?\|\s*([\d,]+)%\s*\|'
    matches = re.findall(pattern, ai_text)
    
    sections = {
        "C01-C25 (Specializzazione)": [float(v.replace(',', '.')) for k, v in matches if 1 <= int(k[1:]) <= 25],
        "C26-C30 (Tipologia Servizio)": [float(v.replace(',', '.')) for k, v in matches if 26 <= int(k[1:]) <= 30],
        "C37-C40 (Area Svolgimento)": [float(v.replace(',', '.')) for k, v in matches if 37 <= int(k[1:]) <= 40],
        "C41-C43 (Ambito Attività)": [float(v.replace(',', '.')) for k, v in matches if 41 <= int(k[1:]) <= 43]
    }
    
    for name, values in sections.items():
        if not values:
            warnings.append(f"⚠️ {name}: nessun dato estratto o formato tabella non riconosciuto")
        else:
            total = sum(values)
            if abs(total - 100.0) > 0.1:
                errors.append(f"❌ {name}: somma = {total:.2f}% (deve essere 100% ±0,1%)")
                
    expected_fields = [f"C{i:02d}" for i in range(1, 44)]
    found_fields = [m[0] for m in matches]
    missing = set(expected_fields) - set(found_fields)
    if missing:
        warnings.append(f"⚠️ Campi non trovati nell'output: {', '.join(sorted(missing))}")
        
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

# =============================================================================
# GENERATORE PROMPT DINAMICO (VERSIONE CORRETTA E COMPLETA)
# =============================================================================
def generate_dynamic_prompt(modello_data, istruzioni_data, general_rules=GENERAL_RULES):
    isa_code = modello_data.get("isa_code") or istruzioni_data.get("isa_code", "UNKNOWN")
    
    prompt = f"""
🎯 RUOLO E OBIETTIVO
Ruolo: Agisci come un Consulente Fiscale Senior specializzato in ISA (Indici Sintetici di Affidabilità Fiscale), con competenza specifica sul codice attività {isa_code}.
Obiettivo: Compilare con precisione assoluta il Quadro C – Elementi specifici dell'attività del modello {isa_code} per il periodo d'imposta 2025.

⚠️ METODOLOGIA DI LAVORO OBBLIGATORIA (3 FASI)
NON procedere direttamente alla compilazione. Devi seguire tassativamente queste 3 fasi in ordine:
FASE 1: ANALISI ESPLORATIVA DEI DOCUMENTI ALLEGATI
FASE 2: PROPOSTA DI MAPPATURA (Dizionario Descrizioni → Campi C)
FASE 3: COMPILAZIONE FINALE E VALIDAZIONE

⛔ ISTRUZIONE OPERATIVA CRITICA (DA SEGUIRE ALLA LETTERA)
Il file allegato contiene decine di pagine di fatture. È SEVERAMENTE VIETATO fare stime, estrapolazioni, campionature o raggruppamenti preventivi.

📦 PROTOCOLLO DOCUMENTI LUNGHI (>30 PAGINE):
Se il file allegato supera le 30 pagine, DEVI dividerlo mentalmente in blocchi da 20 pagine:
1. Analizza blocco 1 (pag 1-20) → crea registro parziale
2. Analizza blocco 2 (pag 21-40) → aggiorna registro
3. Continua fino all'ultima pagina
4. SOLO ALLA FINE unifica tutti i registri e calcola le percentuali totali
NON provare a tenere tutto in memoria contemporaneamente. Lavora a blocchi sequenziali.

RIPARTI DA CAPO NELL'ANALISI E SEGUI QUESTO PROTOCOLLO SEQUENZIALE:
1. SCANSIONE FATTURA PER FATTURA: Analizza ogni singola fattura in ordine, dalla prima all'ultima pagina.
2. LETTURA INTEGRALE: Per OGNI fattura, leggi la DESCRIZIONE COMPLETA della prestazione (non fermarti alle prime parole o ai codici articolo).
3. CLASSIFICAZIONE SINGOLA: Per ogni fattura, decidila tassativamente e assegnala a UNO specifico campo C## del Quadro C.
4. REGISTRO INTERMEDIO: Tieni traccia esplicita di ogni assegnazione (es. "Fatt. 102 → C27 | Fatt. 103 → C01 | ...").
5. AGGREGAZIONE FINALE: SOLO dopo aver processato TUTTE le fatture una per una, calcola i totali imponibili per campo e le relative percentuali sui ricavi.

Se il modello salta fatture, fa medie approssimative o raggruppa a priori, l'output sarà considerato NON VALIDO.
Devi dimostrare di aver letto ogni riga prima di compilare la tabella finale.

{general_rules}

📋 CAMPI QUADRO C (estratti dal MODELLO {isa_code})
"""
    
    # Aggiungi campi estratti dal MODELLO
    if modello_data["campi"]:
        prompt += "\n| Campo | Descrizione Ufficiale |\n|-------|-------------|\n"
        for campo in sorted(modello_data["campi"].keys()):
            desc = modello_data["campi"][campo].get("descrizione", "Descrizione non estratta - verificare modello")
            prompt += f"| {campo} | {desc} |\n"
    else:
        prompt += "\n⚠️ Nessun campo estratto dal Modello. Verificare che il PDF contenga la tabella Quadro C.\n"
    
    # Aggiungi vincoli
    all_vincoli = modello_data.get("vincoli_modello", []) + istruzioni_data.get("vincoli_istruzioni", [])
    if all_vincoli:
        prompt += "\n⚠️ VINCOLI OBBLIGATORI (estratti da Modello + Istruzioni):\n"
        for vincolo in all_vincoli:
            prompt += f"- {vincolo}\n"
    
    # =============================================================================
    # ISTRUZIONI ANALITICHE DETTAGLIATE (IL CUORE DELLA RICHIESTA)
    # =============================================================================
    prompt += """
🔍 FASE 1: ANALISI ESPLORATIVA DEI DOCUMENTI ALLEGATI (FATTURE + BILANCIO)
Prima di classificare, devi analizzare il contenuto dei file allegati e produrre le seguenti tabelle:

1.1 ANALISI FREQUENZA DESCRIZIONI FATTURE
Estrai tutte le descrizioni dalle fatture allegate. Raggruppa le descrizioni simili.
Crea una tabella con:
| Descrizione Ricorrente | Varianti Trovate | N. Fatture | Imponibile Totale | % sul Totale |
|------------------------|------------------|------------|-----------------|--------------|

1.2 ANALISI LOCALIZZAZIONE GEOGRAFICA
Se il Quadro C richiede dati territoriali (es. C36-C40 per EG75U), estrai TUTTI i comuni indicati nelle fatture:
| Comune | N. Fatture | Imponibile Totale | % sul Totale | Note |
|--------|------------|-----------------|--------------|------|

1.3 ANALISI REGIMI IVA SPECIALI
| Regime | N. Fatture | Imponibile Totale | Riferimento Normativo Trovato |
|--------|------------|-----------------|-------------------------------|

🗺️ FASE 2: PROPOSTA DI MAPPATURA (Dizionario Descrizioni → Campi C)
PRIMA di compilare i valori, devi proporre esplicitamente come intendi classificare ogni gruppo di descrizioni nella FASE 1.

Per ogni "Descrizione Ricorrente" identificata nella Fase 1.1, indica:
| Descrizione Ricorrente | Campo Quadro C Proposto | Motivazione della Classificazione | Livello di Certezza |
|------------------------|------------------------|-----------------------------------|---------------------|

⚠️ Se una descrizione potrebbe appartenere a più campi, segnala come "INCERTA" e proponi l'ipotesi più prudente.

📊 FASE 3: COMPILAZIONE FINALE E VALIDAZIONE (ESECUZIONE OBBLIGATORIA)
⛔ PROTOCOLLO SEQUENZIALE FATTURA PER FATTURA:
1. SCANSIONE LINEARE: Leggi OGNI fattura dalla prima all'ultima pagina. Non saltarne nessuna.
2. ASSEGNAZIONE SINGOLA: Per ogni fattura, leggi la descrizione INTERA e assegnala a UNO solo campo C##.
3. REGISTRO VISIBILE: Mostra esplicitamente TUTTE le fatture processate in una tabella completa. Non tralasciarne nessuna.
4. AGGREGAZIONE: SOLO dopo aver classificato TUTTE le fatture, calcola i totali e le percentuali.

📋 FORMATO OUTPUT RICHIESTO (RISPETTALO ALLA LETTERA):

1️⃣ REGISTRO COMPLETO DI TUTTE LE FATTURE
⚠️ DEVI elencare OGNI SINGOLA FATTURA processata, senza eccezioni.
| N. Fattura | Data | Imponibile € | Descrizione Completa | Campo C## | Motivazione Breve |
|------------|------|--------------|---------------------|-----------|-------------------|
| [NR] | [DATA] | [IMPORTO] | [TESTO INTEGRALE] | [CXX] | [Motivo] |
(...elenca TUTTE le fatture, nessuna esclusa...)

2️⃣ TABELLA RIEPILOGATIVA QUADRO C (COMPILA TUTTI I CAMPI C01-C43)
⚠️ REGOLA MATEMATICA: C01+C02+...+C25 DEVE fare ESATTAMENTE 100%. Stessa regola per C26-C30, C37-C40, C41-C43.
| Campo | Descrizione | Imponibile Totale € | % sui Ricavi | N. Fatture |
|-------|-------------|---------------------|--------------|------------|
| C01 | ... | 0,00 | 0% | 0 |
...
| TOT C01-C25 | | [IMPORTO] | 100,0% ✅ | [NUM] |

3️⃣ GIUSTIFICAZIONE ANALITICA OBBLIGATORIA
Per OGNI campo C## con valore >0%, elenca TUTTE le fatture che lo compongono:
[C27 - Manutenzione | 45% | € 225.000 | 67 fatture]
- Fatt. 102 del 15/01 - € 5.000 - "Sostituzione caldaia..."
(...elenca TUTTE le fatture assegnate a questo campo)

4️⃣ SEGNALAZIONE CRITICITÀ (Template Obbligatorio)
[CRITICITÀ - PRIORITÀ: ALTA/MEDIA/BASSA]
Fattura N. [XXX] del [DD-MM-YYYY]
Problema: [descrizione breve]
Classificazione adottata: [campo C##] + [motivazione tecnica]
Dati mancanti per certezza: [cosa servirebbe]

5️⃣ CHECKLIST PRE-INVIO (DICHIARA ESPLICITAMENTE)
- [ ] Tutte le fatture allegate sono state lette e classificate (nessuna esclusa)
- [ ] Somma C01+...+C25 = [X]% (Target: 100% ±0,1%) ✅/❌
- [ ] Somma C26+...+C30 = [X]% (Target: 100% ±0,1%) ✅/❌
- [ ] Somma C37+...+C40 = [X]% (Target: 100% ±0,1%) ✅/❌
- [ ] Somma C41+C42+C43 = [X]% (Target: 100% ±0,1%) ✅/❌
- [ ] Note di credito applicate come storni negativi
- [ ] Regimi IVA (C32, C33, C34) identificati e separati correttamente

6️⃣ SINTESI FINALE PER EXPORT WORD (LAYOUT ORIZZONTALE)
Genera una sezione conclusiva strutturata ESATTAMENTE così, pronta per conversione in .docx con orientamento orizzontale:

📄 REPORT EXECUTIVO - RISULTANZE ISA [CODICE_ISA]
• LACUNE EMERSE NEL QUADRO C: [elenco puntato delle principali criticità di compilazione, es. "Mancata allocazione geografica in X fatture", "Concentrazione eccessiva su C28 per descrizioni generiche", "Storni non correttamente allineati"]
• PROBLEMI FATTURA PER FATTURA (solo criticità ALTA/MEDIA): 
  | N. Fattura | Data | Imp. € | Criticità rilevata | Azione richiesta |
  |------------|------|--------|-------------------|------------------|
  | [NR] | [DD.MM.AAAA] | [X.XXX,XX] | [descrizione breve] | [cosa verificare/correggere] |
• RISCHIO COMPLESSIVO: [BASSO/MEDIO/ALTO] + motivazione tecnica in max 2 righe
• AZIONI CORRETTIVE/RACCOMANDAZIONI: [elenco puntato di interventi pratici per migliorare la documentazione, allineare i campi, correggere errori prima dell'invio]
• NOTE PER IL CONSULENTE: [osservazioni finali operative, non tecniche]

⚠️ REGOLE FORMATTAZIONE WORD-READY:
- Usa SOLO markdown pulito (niente HTML, niente blocchi codice)
- Mantieni tabelle compatte (max 5 colonne, righe brevi)
- Usa elenchi puntati diretti, niente frasi lunghe
- Ogni titolo di sezione in grassetto, spaziatura uniforme
- Output pronto per copia-incolla diretto in documento Word .docx a pagina orizzontale (margini stretti, font compatto)

💡 ISTRUZIONE FINALE DI SAFETY:
Se una fattura presenta anche solo un dubbio ragionevole su classificazione, localizzazione, regime IVA o ambito di attività → NON forzare una classificazione certa. Segnalala nella sezione 'CRITICITÀ' e, solo se strettamente necessario, indica l'ipotesi più probabile specificando chiaramente: "ASSUNZIONE DA VALIDARE". In ambito ISA: meglio una segnalazione in più che un errore in dichiarazione.
"""
    
    return prompt

# =============================================================================
# INTERFACCIA STREAMLIT
# =============================================================================
st.title("📊 ISA - Compilazione Quadro C PRO")
st.markdown("Carica **Modello + Istruzioni + Documenti Aziendali** per un'analisi completa e tracciabile")

col1, col2, col3 = st.columns(3)

with col1:
    uploaded_modello = st.file_uploader(
        "📄 1. MODELLO Quadro C (PDF)", 
        type=['pdf'],
        help="Il file con la tabella visiva dei campi (es. EG75U Modello.pdf)"
    )

with col2:
    uploaded_istruzioni = st.file_uploader(
        "📄 2. ISTRUZIONI ISA (PDF)", 
        type=['pdf'],
        help="Il file con le regole di compilazione (es. EG75U Istruzioni.pdf)"
    )

with col3:
    uploaded_docs = st.file_uploader(
        "📁 3. FATTURE + BILANCIO (PDF)", 
        type=['pdf'],
        accept_multiple_files=True,
        help="Fatture emesse, bilancio, registri IVA (opzionali ma consigliati per analisi completa)"
    )

if uploaded_modello or uploaded_istruzioni:
    with st.spinner('🔍 Analisi PDF in corso...'):
        try:
            modello_data = {"isa_code": None, "campi": {}, "vincoli_modello": []}
            istruzioni_data = {"vincoli_istruzioni": [], "ambiguita_comuni": []}
            
            # Processa MODELLO
            if uploaded_modello:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_modello.getvalue())
                    tmp_path = tmp_file.name
                modello_data = parse_modello(tmp_path)
                os.unlink(tmp_path)
                st.success(f"✅ Modello elaborato: {len(modello_data['campi'])} campi estratti")
            
            # Processa ISTRUZIONI
            if uploaded_istruzioni:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_istruzioni.getvalue())
                    tmp_path = tmp_file.name
                istruzioni_data = parse_istruzioni(tmp_path)
                os.unlink(tmp_path)
                st.success(f"✅ Istruzioni elaborate: {len(istruzioni_data.get('ambiguita_comuni', []))} note estratte")
            
            # Verifica codice ISA
            isa_code = modello_data.get("isa_code") or "UNKNOWN"
            
            if isa_code != "UNKNOWN":
                st.info(f"🎯 Codice ISA rilevato: **{isa_code}**")
            
            # Anteprima dati estratti
            with st.expander("🔍 Anteprima dati estratti da Modello/Istruzioni"):
                st.write("**Campi dal Modello:**")
                for campo, info in list(modello_data["campi"].items())[:15]:
                    st.write(f"- {campo}: {info.get('descrizione', 'N/A')[:100]}...")
                
                if modello_data.get("vincoli_modello"):
                    st.write("\n**Vincoli dal Modello:**")
                    for v in modello_data["vincoli_modello"]:
                        st.write(f"- {v}")
                
                if istruzioni_data.get("ambiguita_comuni"):
                    st.write("\n**Ambiguità dalle Istruzioni:**")
                    for a in istruzioni_data["ambiguita_comuni"]:
                        st.write(f"- {a}")
            
            if uploaded_docs:
                st.info(f"📁 {len(uploaded_docs)} documenti aziendali caricati per l'analisi (fatture/bilancio)")
            
                       # Genera prompt
            prompt = generate_dynamic_prompt(modello_data, istruzioni_data)
            
            st.subheader("🤖 Prompt Generato (Analisi in 3 Fasi)")
            st.code(prompt, language='text')
            
            # 🔍 VALIDATORE AUTOMATICO (dopo che l'AI risponde, l'utente incollerà qui la risposta)
            st.markdown("---")
            st.subheader("✅ Validazione Output AI")
            st.info("Dopo aver ricevuto la risposta dall'AI, incolla il testo qui sotto per verificare automaticamente errori matematici")
            
            ai_response = st.text_area(
                "Incolla qui la risposta completa dell'AI",
                height=300,
                placeholder="L'AI risponderà con tabelle e giustificazioni..."
            )
            
            if ai_response:
                validation = validate_ai_output(ai_response)
                
                if validation["errors"]:
                    st.error("❌ ERRORI RILEVATI (correggere prima di procedere):")
                    for error in validation["errors"]:
                        st.error(error)
                else:
                    st.success("✅ Nessun errore matematico rilevato!")
                
                if validation["warnings"]:
                    st.warning("⚠️ AVVISI:")
                    for warning in validation["warnings"]:
                        st.warning(warning)
                
                # Download validato
                if validation["valid"]:
                    st.download_button(
                        label="📥 Scarica Output Validato (.txt)",
                        data=ai_response,
                        file_name=f"quadro_c_{isa_code}_validato.txt",
                        mime="text/plain"
                    )
            
            st.download_button(
                label="📥 Scarica Prompt (.txt)",
                data=prompt,
                file_name=f"prompt_{isa_code}_quadro_c_analitico.txt",
                mime="text/plain",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"❌ Errore durante l'analisi: {str(e)}")
            st.exception(e)
else:
    st.info("👆 Carica almeno il MODELLO per iniziare")
    st.markdown("""
    💡 **Flusso ottimale**:
    1. Carica `EG75U Modello.pdf` → estrae campi C01-C43 con descrizioni
    2. Carica `EG75U Istruzioni.pdf` → estrae vincoli e regole di compilazione
    3. Carica `Fatture_2025.pdf` + `Bilancio.pdf` → il prompt chiederà analisi frequenza e mappatura
    
    🎯 **Il prompt generato obbligherà l'LLM a**:
    - Fare lista delle descrizioni più frequenti nelle fatture
    - Proporre dove classificarle (Campo C) PRIMA di compilare
    - Estrarre lista comuni per campi territoriali
    - Segnalare ogni ambiguità prima della compilazione finale
    """)
