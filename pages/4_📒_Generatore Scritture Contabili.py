import streamlit as st
import pdfplumber
import pandas as pd
import re
from decimal import Decimal

st.set_page_config(page_title="Partita Doppia → SPIACO", layout="wide")
st.title("📘 Estrattore Scritture Contabili → Piano SPIACO")

# ==============================================================================
# 1. MAPPATURA MANUALE → SPIACO (completa per i conti più frequenti del manuale)
# ==============================================================================
MAPPATURA_SPIACO = {
    "clienti": "28.01.001", "clienti c/vendite": "28.01.001", "crediti vs. clienti": "28.01.001",
    "crediti vs fornitori": "49.13.001", "fornitore": "49.13.001", "fornitori": "49.13.001",
    "debiti vs. fornitori": "49.13.001", "fatture da emettere": "28.01.037", "fatture da ricevere": "49.13.005",
    "iva a debito": "49.23.013", "iva vendite": "49.23.013", "iva su vendite": "49.23.013",
    "iva a credito": "28.11.017", "iva acquisti": "28.11.017", "iva su acquisti": "28.11.017",
    "banca": "34.01.001", "banca c/c": "34.01.001", "cassa": "34.05.001", "cassa contanti": "34.05.001",
    "assegni": "34.03.001", "cassa assegni": "34.03.001",
    "merci c/vendite": "60.01.001", "ricavi c/vendite": "60.01.001", "prodotti c/vendite": "60.01.001",
    "merci c/acquisti": "73.01.013", "merci conto acquisti": "73.01.013",
    "spese di trasporto": "75.01.005", "oneri bancari": "92.01.001", "commissioni bancarie": "93.15.061",
    "impianti": "13.05.053", "macchinari": "13.05.053", "automezzi": "13.09.001",
    "f.do ammortamento": "16.00.000", "ammortamento": "83.00.000",
    "capitale sociale": "40.01.001", "riserva legale": "40.07.001", "utile d'esercizio": "40.17.001",
    "perdita d'esercizio": "40.17.005", "dividendi": "49.27.089",
    "interessi attivi": "93.13.001", "interessi passivi": "93.15.001",
    "crediti finanziari": "22.23.001", "debiti finanziari": "49.09.001",
    "salari e stipendi": "79.01.001", "oneri sociali": "79.03.001", "personale c/retribuzioni": "49.27.025",
    "fondo tfr": "46.01.001", "inps c/contributi": "49.25.001", "erario c/ritenute": "49.23.029",
    "resI su acquisti": "73.03.001", "resI su vendite": "60.01.101",
    "sconti attivi": "60.01.089", "sconti passivi": "92.01.137",
    "abbuoni attivi": "60.01.093", "abbuoni passivi": "92.01.141",
    "arrotondamenti attivi": "71.01.073", "arrotondamenti passivi": "92.01.145"
}

def risolvi_spiaco(nome):
    nome_pulito = nome.strip().lower()
    if nome_pulito in MAPPATURA_SPIACO:
        return MAPPATURA_SPIACO[nome_pulito]
    for chiave, codice in MAPPATURA_SPIACO.items():
        if chiave in nome_pulito or nome_pulito in chiave:
            return codice
    return "00.00.000"

# ==============================================================================
# 2. PARSING PDF (regex adattata al formato del manuale Toriello)
# ==============================================================================
def estrai_scritture(pdf_file):
    entries = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            # Cerca blocchi che iniziano con "Data" o conti seguiti da importi
            # Pattern: [Data] [Conto Dare] a [Conto Avere] [Importo] \n [Conto] [Importo] ...
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            i = 0
            while i < len(lines):
                line = lines[i]
                # Riconosce inizio scrittura: "Data ... a ..." oppure "Diversi a ..." oppure "X a Y ..."
                if re.match(r'^(data\s+)?[a-zàèéìòù ]+\s+a\s+[a-zàèéìòù ]+', line, re.IGNORECASE) or \
                   re.match(r'^diversi a ', line, re.IGNORECASE):
                    
                    # Estrae la descrizione della data/operazione
                    descrizione = re.sub(r'^(data\s+)?', '', line).split(' a ')[0].strip()
                    parti = line.split(' a ')
                    dare_conto = parti[0].strip()
                    avere_conto_e_importo = parti[1].strip()
                    
                    dare_righe = []
                    avere_righe = []
                    
                    # Prima riga Dare (se non è "Diversi")
                    if dare_conto.lower() != "diversi":
                        dare_righe.append(dare_conto)
                    
                    # Prima riga Avere + eventuale importo inline
                    match_imp = re.search(r'([\d\.]+,\d{2})$', avere_conto_e_importo)
                    if match_imp:
                        importo = Decimal(match_imp.group(1).replace('.', '').replace(',', '.'))
                        avere_righe.append((avere_conto_e_importo[:match_imp.start()].strip(), importo))
                    else:
                        avere_righe.append(avere_conto_e_importo)
                    
                    # Raccoglie le righe successive fino a una riga vuota o nuova "Data" o "Nota"
                    i += 1
                    while i < len(lines):
                        r = lines[i]
                        if not r or r.lower().startswith(('data ', 'nota ', 'emessa ', 'pagata ', 'incassata ')):
                            break
                        # Se la riga contiene un importo italiano
                        m = re.search(r'([\d\.]+,\d{2})$', r)
                        if m:
                            imp = Decimal(m.group(1).replace('.', '').replace(',', '.'))
                            nome_conto = r[:m.start()].strip()
                            # Logica semplice: se il primo importo era in Avere, i successivi sono alternati o tutti Avere
                            # Nel manuale, dopo "X a Y Importo", le righe successive sono i dettagli di Y (Avere)
                            avere_righe.append((nome_conto, imp))
                        i += 1
                    
                    entries.append({
                        "descrizione": descrizione,
                        "dare": dare_righe,
                        "avere": avere_righe
                    })
                i += 1
    return entries

def costruisci_tabella(entries):
    rows = []
    for idx, e in enumerate(entries, 1):
        dare_total = Decimal('0')
        avere_total = Decimal('0')
        
        for c in e["dare"]:
            rows.append({"Nr": idx, "Tipo": "DARE", "Conto Manuale": c, "Codice SPIACO": risolvi_spiaco(c), "Importo": 0})
            
        for nome, imp in e["avere"]:
            rows.append({"Nr": idx, "Tipo": "AVERE", "Conto Manuale": nome, "Codice SPIACO": risolvi_spiaco(nome), "Importo": imp})
            avere_total += imp
            
    return pd.DataFrame(rows)

# ==============================================================================
# 3. INTERFACCIA STREAMLIT
# ==============================================================================
with st.sidebar:
    st.header("📤 Caricamento PDF")
    manuale = st.file_uploader("1. Manuale Partita Doppia", type="pdf")
    spiaco = st.file_uploader("2. Piano SPIACO (opzionale)", type="pdf")
    processa = st.button("🔍 Estrai e Mappa", type="primary")

if processa and manuale:
    with st.spinner("📖 Lettura PDF e riconoscimento scritture..."):
        try:
            entries = estrai_scritture(manuale)
            if not entries:
                st.warning("⚠️ Nessuna scrittura automatica trovata. Il formato PDF potrebbe richiedere un parser specifico. Controlla il manuale.")
            else:
                df = costruisci_tabella(entries)
                st.success(f"✅ Trovate {len(entries)} scritture contabili")
                
                st.subheader("📊 Anteprima Scritture")
                st.dataframe(df, use_container_width=True, height=400)
                
                # Validazione
                st.subheader("🔍 Verifica Quadratura")
                for nr in df["Nr"].unique():
                    sub = df[df["Nr"] == nr]
                    d = sub[sub["Tipo"]=="DARE"]["Importo"].sum()
                    a = sub[sub["Tipo"]=="AVERE"]["Importo"].sum()
                    if abs(d - a) > Decimal("0.01"):
                        st.error(f"❌ Scrittura {nr} NON quadrata: Dare={d:.2f} ≠ Avere={a:.2f}")
                    else:
                        st.success(f"✅ Scrittura {nr} quadrata: {d:.2f}")
                        
                # Export
                csv = df.to_csv(index=False, sep=";").encode('utf-8')
                st.download_button("📥 Scarica CSV", data=csv, file_name="scritture_spiaco.csv", mime="text/csv")
        except Exception as ex:
            st.error(f"🚨 Errore durante l'elaborazione: {str(ex)}")
else:
    st.info("👈 Carica il PDF del Manuale nella sidebar e premi 'Estrai e Mappa'.")
