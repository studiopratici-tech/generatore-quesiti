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
# PARSER MODELLO UNIVERSALE (Zero Hardcode, Legge Griglie ISA)
# =============================================================================
def parse_modello(pdf_path):
    import pdfplumber
    import re
    from collections import defaultdict

    result = {
        "isa_code": None,
        "campi": defaultdict(dict),
        "vincoli_modello": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        # 1. Raccogli tutte le parole con coordinate da TUTTE le pagine
        all_words = []
        for page in pdf.pages:
            words = page.extract_words(
                x_tolerance=3, 
                y_tolerance=3, 
                extra_attrs=["top", "bottom", "x0", "x1", "page_number"]
            )
            if words:
                all_words.extend(words)
            
            # Rileva codice modello (es. EG75U)
            if not result["isa_code"]:
                page_text = page.extract_text() or ""
                match = re.search(r'Modello\s+([A-Z]{2}\d{2,3}[A-Z]?)', page_text, re.I)
                if match:
                    result["isa_code"] = match.group(1).upper()

        if not all_words:
            return result

        # 2. Identifica tutti i codici C## e il loro centro X
        code_columns = []
        for w in all_words:
            txt = w["text"].strip()
            if re.match(r'^C\d{2}$', txt):
                x_center = (w["x0"] + w["x1"]) / 2
                # Evita duplicati (tieni solo la prima occorrenza per codice)
                if not any(c["code"] == txt for c in code_columns):
                    code_columns.append({
                        "code": txt,
                        "x_center": x_center,
                        "y_start": w["top"],
                        "desc_words": []
                    })

        # 3. Assegna ogni parola alla colonna (codice) più vicina orizzontalmente
        #    e verticalmente sotto di esso, ignorando header e numeri puri
        for w in all_words:
            txt = w["text"].strip()
            if not txt:
                continue
                
            # Ignora codici stessi, percentuali, valori numerici, separatori
            if re.match(r'^(C\d{2}|TOT|%=?|,00|\d+[,.]?\d*|[|\-]+)$', txt):
                continue
                
            # Ignora parole che sono chiaramente titoli di sezione/header
            if len(txt) < 20 and any(kw in txt.upper() for kw in [
                "SEZIONE", "QUADRO", "PERCENTUALE", "RICAVI", "MODALITÀ", 
                "TIPOLOGIA", "AREA", "AMBITO", "PRODUZIONE", "ALTRI ELEMENTI"
            ]):
                continue

            w_x = (w["x0"] + w["x1"]) / 2
            w_y = w["top"]
            
            # Trova la colonna più vicina in X (tolleranza 50px)
            closest_col = None
            min_x_dist = float('inf')
            for col in code_columns:
                x_dist = abs(col["x_center"] - w_x)
                if x_dist < min_x_dist:
                    min_x_dist = x_dist
                    closest_col = col
            
            # Assegna solo se siamo nella stessa colonna E sotto il codice
            if closest_col and min_x_dist < 50 and w_y >= closest_col["y_start"] - 5:
                closest_col["desc_words"].append(txt)

        # 4. Costruisci le descrizioni finali
        for col in code_columns:
            # Filtra rumore residuo e unisci
            clean_words = [w for w in col["desc_words"] if not re.match(r'^[%\d,.\-()]+$', w)]
            description = " ".join(clean_words).strip()
            description = re.sub(r'\s+', ' ', description)  # Normalizza spazi multipli
            description = description.strip(".,;:")

            # Salva solo se la descrizione ha senso (>5 caratteri)
            if len(description) > 5:
                result["campi"][col["code"]]["descrizione"] = description
                result["campi"][col["code"]]["estratto_da_pdf"] = True
            else:
                # Fallback dinamico (mai hardcoded)
                result["campi"][col["code"]]["descrizione"] = f"Campo {col['code']} - descrizione non rilevata nel layout"
                result["campi"][col["code"]]["estratto_da_pdf"] = False

        # 5. Rileva automaticamente vincoli di somma (es. "TOT=100%")
        full_text = " ".join(w["text"] for w in all_words)
        if "TOT" in full_text and "100" in full_text:
            result["vincoli_modello"].append("Presenza vincolo di somma (TOT=100%) rilevato. Verificare raggruppamenti logici.")

    # Ordina alfabeticamente/numericamente per output pulito
    result["campi"] = dict(sorted(result["campi"].items()))
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
    
    # Estrai vincoli espliciti
    constraint_patterns = [
        r'Il totale.*?percentuali.*?(C\d+).*?(C\d+).*?100',
        r'totale.*?pari a 100',
        r'deve risultare pari a 100',
    ]
    for pattern in constraint_patterns:
        for match in re.finditer(pattern, text_content, re.IGNORECASE):
            result["vincoli_istruzioni"].append(f"Somma percentuali = 100%")
    
    # Estrai note su ambiguità
    ambiguity_patterns = [
        r'(?:Ad esempio|Si precisa|Nell\'ambito).*?(riqualificazione|manutenzione|ristrutturazione|nuova costruzione).*?(?=\n\n|\.)',
        r'(?:attenzione|verificare|non confondere).*?(subappalto|reverse charge|split payment)',
    ]
    for pattern in ambiguity_patterns:
        for match in re.finditer(pattern, text_content, re.IGNORECASE):
            note = match.group(0).strip()
            if len(note) < 250:
                result["ambiguita_comuni"].append(note)
    
    # Aggiungi ambiguità specifiche
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
# GENERATORE PROMPT DINAMICO (VERSIONE ANALITICA COMPLETA)
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
Estrai tutte le descrizioni dalle fatture allegate. Raggruppa le descrizioni simili (es. "sostituzione caldaia", "cambio caldaia", "sostituzione generatore termico" → stesso gruppo).
Crea una tabella con:
| Descrizione Ricorrente | Varianti Trovate | N. Fatture | Imponibile Totale | % sul Totale |
|------------------------|------------------|------------|-----------------|--------------|
| es. Sostituzione Caldaia | "cambio caldaia", "sostituzione generatore" | 15 | € 45.000 | 12% |
| es. Riparazione Guasti | "riparazione", "intervento urgente", "pronto intervento" | 23 | € 18.000 | 5% |

1.2 ANALISI LOCALIZZAZIONE GEOGRAFICA
Se il Quadro C richiede dati territoriali (es. C36-C40 per EG75U), estrai TUTTI i comuni indicati nelle fatture:
| Comune | N. Fatture | Imponibile Totale | % sul Totale | Note (es. "cantiere esplicito" vs "solo sede committente") |
|--------|------------|-----------------|--------------|-----------------------------------------------------------|
| Milano | 45 | € 200.000 | 60% | Cantiere esplicito in 30 fatture |
| Roma | 12 | € 50.000 | 15% | Solo sede committente (ambiguo) |

1.3 ANALISI REGIMI IVA SPECIALI
| Regime | N. Fatture | Imponibile Totale | Riferimento Normativo Trovato |
|--------|------------|-----------------|-------------------------------|
| Split Payment | 5 | € 80.000 | Art.17-ter, "scissione pagamenti" |
| Reverse Charge | 8 | € 120.000 | Art.17 c.6, "N6.3" |
| Ritenuta Acconto | 10 | € 45.000 | Art.25 D.L. 78/2010, "bonifico parlante" |

🗺️ FASE 2: PROPOSTA DI MAPPATURA (Dizionario Descrizioni → Campi C)
PRIMA di compilare i valori, devi proporre esplicitamente come intendi classificare ogni gruppo di descrizioni nella FASE 1.

Per ogni "Descrizione Ricorrente" identificata nella Fase 1.1, indica:
| Descrizione Ricorrente | Campo Quadro C Proposto | Motivazione della Classificazione | Livello di Certezza |
|------------------------|------------------------|-----------------------------------|---------------------|
| Sostituzione Caldaia | C27 (Manutenzione) | Intervento su impianto esistente senza miglioramento prestazionale | ALTA |
| Installazione Nuovo Impianto | C26 (Installazione) | Impianto ex-novo in edificio di nuova costruzione | ALTA |
| Ristrutturazione Bagno | C43 (Riqualificazione) | Rientra in art.3 DPR 380/2001 lett. c) | MEDIA (verificare titolo edilizio) |

⚠️ Se una descrizione potrebbe appartenere a più campi (es. "lavori idraulici" generico), segnala come "INCERTA" e proponi l'ipotesi più prudente specificando cosa servirebbe per certezza.

📊 FASE 3: COMPILAZIONE FINALE E VALIDAZIONE
Solo dopo aver completato le Fasi 1 e 2, procedi con:

3.1 TABELLA RIEPILOGATIVA QUADRO C
| Campo | Valore (% o Importo) | N. Fatture Incluse | Riferimento Fasi 1-2 |
|-------|---------------------|-------------------|---------------------|
| C27 | 45% | 67 | Gruppo "Manutenzione" da Fase 2 |
| C26 | 35% | 23 | Gruppo "Installazione" da Fase 2 |

3.2 ANALISI DI COERENZA
- Verifica vincoli di somma (es. C01+...+C09 = 100%)
- Verifica coerenza tra Fasi 1-2-3 (nessuna fattura esclusa o doppia)
- Verifica regimi IVA speciali (C32, C33, C34 se presenti)

3.3 SEGNALAZIONE CRITICITÀ (Template Obbligatorio)
Per ogni dubbio residuo:
[CRITICITÀ - PRIORITÀ: ALTA/MEDIA/BASSA]
Fattura N. [XXX] del [DD-MM-YYYY]
Problema: [descrizione breve]
Ipotesi di classificazione: [campo proposto] + [motivazione]
Dati mancanti per certezza: [cosa servirebbe]
Raccomandazione: [verificare con cliente / chiedere documentazione]

3.4 CHECKLIST PRE-INVIO
- [ ] Tutte le fatture allegate sono state classificate (nessuna esclusa)
- [ ] Tutti i vincoli di somma % rispettati (tolleranza 0,1%)
- [ ] Note di credito applicate come storni (non nuovi ricavi)
- [ ] Regimi IVA (split/reverse) coerenti con fatture
- [ ] Localizzazioni allocate correttamente (se richiesto dal modello)
- [ ] Ambiguità segnalate, non nascoste

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
