import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# 1. PIANO DEI CONTI SPIACO (Mappatura estratta dal PDF fornito)
# ==============================================================================
SPIACO = {
    "34.01.001": "Depositi bancari e postali",
    "28.11.009": "Credito IVA",
    "37.01.001": "Ratei attivi",
    "37.01.005": "Risconti attivi",
    "52.01.001": "Ratei passivi",
    "52.01.005": "Risconti passivi",
    "28.15.053": "Crediti per anticipi missioni",
    "13.05.053": "Macchinari / Attrezzature scientifiche",
    "16.05.001": "F.do amm.to attrezzature industriali",
    "19.03.013": "F.do svalut. impianto elettrico",
    "85.15.013": "Svalutazione impianto elettrico",
    "93.17.005": "Perdite su cambi",
    "49.13.001": "Debiti verso fornitori",
    "49.23.009": "Erario c/IVA (Split Payment Istituzionale)",
    "49.23.010": "Erario c/IVA intra/extra UE",
    "49.23.029": "Debiti verso Erario per IRPEF c/liquidazione",
    "49.23.005": "Debiti verso Erario per IRAP",
    "49.25.001": "Debiti verso Istituti di previdenza c/liquidazione",
    "49.27.025": "Debiti verso dipendenti",
    "49.27.041": "Debiti verso altri soggetti privati",
    "46.01.001": "Fondo T.F.R.",
    "73.01.017": "Acquisto materiali di consumo per laboratori",
    "75.01.025": "Utenze e canoni per energia elettrica",
    "75.11.002": "Altri servizi da terzi (Vigilanza/Consulenze)",
    "75.17.033": "Costi per missioni",
    "79.01.005": "Competenze fisse al personale tecnico-amministrativo",
    "79.05.001": "Acc.to fondo TFR",
    "96.01.005": "IRAP (Costo)",
    "71.01.081": "Contributi in conto capitale",
    "71.01.049": "Proventi per donazioni",
    "40.17.001": "Risultato di esercizio (Utile)",
    "40.17.005": "Risultato di esercizio (Perdita)",
    "97.00.000": "Conto Economico (Epilogativo)",
    "55.01.001": "Bilancio di apertura",
    "55.01.005": "Bilancio di chiusura"
}

# ==============================================================================
# 2. GENERATORI SCRITTURE (Basati sul Manuale Tecnico Operativo)
# ==============================================================================
def gen_acquisto_split(imponibile, aliquota_iva=0.22):
    iva = round(imponibile * aliquota_iva, 2)
    return [
        ("34.01.001", "D", imponibile + iva),
        ("49.13.001", "A", imponibile),
        ("49.23.009", "A", iva)
    ]

def gen_acquisto_ue_istituzionale(imponibile, aliquota_iva=0.22):
    iva = round(imponibile * aliquota_iva, 2)
    return [
        ("75.11.002", "D", imponibile + iva),
        ("49.13.001", "A", imponibile),
        ("49.23.010", "A", iva)
    ]

def gen_liquidazione_personale(lordo, irpef, inps, altri):
    netto = round(lordo - irpef - inps - altri, 2)
    return [
        ("79.01.005", "D", lordo),
        ("49.23.029", "A", irpef),
        ("49.25.001", "A", inps),
        ("49.27.041", "A", altri),
        ("49.27.025", "A", netto)
    ]

def gen_pagamento_retribuzioni(netto):
    return [
        ("49.27.025", "D", netto),
        ("34.01.001", "A", netto)
    ]

def gen_versamento_irpef(importo):
    return [
        ("49.23.029", "D", importo),
        ("34.01.001", "A", importo)
    ]

def gen_versamento_irap(importo):
    return [
        ("49.23.005", "D", importo),
        ("34.01.001", "A", importo)
    ]

def gen_accantonamento_tfr(importo):
    return [
        ("79.05.001", "D", importo),
        ("46.01.001", "A", importo)
    ]

def gen_missione_anticipo(importo):
    return [
        ("28.15.053", "D", importo),
        ("34.01.001", "A", importo)
    ]

def gen_missione_rendicontazione(costo_totale, anticipo):
    debito_residuo = round(costo_totale - anticipo, 2)
    return [
        ("75.17.033", "D", costo_totale),
        ("28.15.053", "A", anticipo),
        ("49.27.025", "A", debito_residuo)
    ]

def gen_missione_pagamento_residuo(importo):
    return [
        ("49.27.025", "D", importo),
        ("34.01.001", "A", importo)
    ]

def gen_donazione_cespite(valore):
    return [
        ("13.05.053", "D", valore),
        ("71.01.049", "A", valore)
    ]

def gen_svalutazione_impianto(importo):
    return [
        ("85.15.013", "D", importo),
        ("19.03.013", "A", importo)
    ]

def gen_perdite_su_cambi(importo):
    return [
        ("93.17.005", "D", importo),
        ("49.13.001", "A", importo)
    ]

def gen_chiusura_conto_economico(risultato):
    if risultato >= 0:
        return [
            ("97.00.000", "D", risultato),
            ("40.17.001", "A", risultato)
        ]
    else:
        perdita = abs(risultato)
        return [
            ("40.17.005", "D", perdita),
            ("97.00.000", "A", perdita)
        ]

# Dizionario di configurazione operazioni
OPERAZIONI = {
    "Acquisto Split Payment (Istituzionale)": {
        "gen": gen_acquisto_split,
        "inputs": [("Imponibile €", "imponibile", 1000.00)]
    },
    "Acquisto UE Istituzionale (Licenze Software)": {
        "gen": gen_acquisto_ue_istituzionale,
        "inputs": [("Imponibile €", "imponibile", 1000.00)]
    },
    "Liquidazione Personale T&A": {
        "gen": gen_liquidazione_personale,
        "inputs": [
            ("Retribuzione Lorda €", "lordo", 10000.00),
            ("IRPEF €", "irpef", 2000.00),
            ("INPS €", "inps", 1000.00),
            ("Altre ritenute €", "altri", 200.00)
        ]
    },
    "Pagamento Retribuzioni Nette": {
        "gen": gen_pagamento_retribuzioni,
        "inputs": [("Importo Netto €", "netto", 6800.00)]
    },
    "Versamento Ritenute IRPEF": {
        "gen": gen_versamento_irpef,
        "inputs": [("Importo IRPEF €", "importo", 2000.00)]
    },
    "Versamento IRAP": {
        "gen": gen_versamento_irap,
        "inputs": [("Importo IRAP €", "importo", 850.00)]
    },
    "Accantonamento TFR": {
        "gen": gen_accantonamento_tfr,
        "inputs": [("Importo TFR €", "importo", 3500.00)]
    },
    "Missione: Erogazione Anticipo": {
        "gen": gen_missione_anticipo,
        "inputs": [("Anticipo €", "importo", 1500.00)]
    },
    "Missione: Rendicontazione Finale": {
        "gen": gen_missione_rendicontazione,
        "inputs": [
            ("Costo Totale Missione €", "costo_totale", 1800.00),
            ("Anticipo Già Versato €", "anticipo", 1500.00)
        ]
    },
    "Missione: Pagamento Saldo Residuo": {
        "gen": gen_missione_pagamento_residuo,
        "inputs": [("Saldo da Pagare €", "importo", 300.00)]
    },
    "Donazione Attrezzatura Scientifica": {
        "gen": gen_donazione_cespite,
        "inputs": [("Valore Cespito €", "valore", 40000.00)]
    },
    "Svalutazione Impianto Elettrico": {
        "gen": gen_svalutazione_impianto,
        "inputs": [("Importo Svalutazione €", "importo", 30000.00)]
    },
    "Perdite su Cambi": {
        "gen": gen_perdite_su_cambi,
        "inputs": [("Importo Perdita €", "importo", 197.62)]
    },
    "Chiusura Conto Economico (Utile/Perdita)": {
        "gen": gen_chiusura_conto_economico,
        "inputs": [("Risultato Economico € (negativo per perdita)", "risultato", 1200000.00)]
    }
}

# ==============================================================================
# 3. INTERFACCIA STREAMLIT
# ==============================================================================
def main():
    st.set_page_config(page_title="Generatore Scritture Contabili - Manuale Ateneo", layout="wide")
    st.title("📘 Generatore Scritture Contabili")
    st.markdown("Mappatura automatica Manuale Tecnico Operativo ↔ Piano dei Conti SPIACO")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        op_key = st.selectbox("Seleziona Operazione dal Manuale", list(OPERAZIONI.keys()))
    
    op_config = OPERAZIONI[op_key]
    
    # Raccolta input dinamici
    valori_input = {}
    with col2:
        st.subheader("📝 Parametri")
        for label, key, default_val in op_config["inputs"]:
            valori_input[key] = st.number_input(label, value=default_val, step=0.01, format="%.2f")
    
    if st.button("🔄 Genera Scrittura Contabile", type="primary", use_container_width=True):
        try:
            righe = op_config["gen"](**valori_input)
            
            # Validazione Bilanciamento
            tot_dare = sum(r[2] for r in righe if r[1] == "D")
            tot_avere = sum(r[2] for r in righe if r[1] == "A")
            bilanciata = abs(tot_dare - tot_avere) < 0.01
            
            # Costruzione DataFrame
            dati = []
            for codice, da, importo in righe:
                dati.append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Conto (SPIACO)": codice,
                    "Descrizione Conto": SPIACO.get(codice, "Descrizione non mappata"),
                    "D/A": da,
                    "Dare €": round(importo, 2) if da == "D" else "",
                    "Avere €": round(importo, 2) if da == "A" else ""
                })
            
            df = pd.DataFrame(dati)
            
            # Visualizzazione
            st.divider()
            st.subheader(f"📄 {op_key}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Totale DARE", f"€ {tot_dare:,.2f}")
            with c2:
                st.metric("Totale AVERE", f"€ {tot_avere:,.2f}")
            
            if bilanciata:
                st.success("✅ Scrittura BILANCIATA correttamente.")
                
                # Export CSV
                csv = df.to_csv(index=False, sep=";", decimal=",", encoding="utf-8-sig")
                st.download_button(
                    label="📥 Scarica CSV per Importazione",
                    data=csv,
                    file_name=f"scrittura_{op_key.replace(' ', '_').lower()}.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"❌ Scrittura NON BILANCIATA! Differenza: € {abs(tot_dare - tot_avere):,.2f}")
                
        except Exception as e:
            st.error(f"⚠️ Errore durante la generazione: {e}")

if __name__ == "__main__":
    main()
