import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# PIANO DEI CONTI (estratto dal PDF)
PIANO_CONTI = {
    "73.01.013": "Merci c/acquisti",
    "28.11.009": "Credito IVA",
    "49.13.001": "Fornitore",
    "60.01.009": "Merci c/vendite",
    "49.23.009": "Erario c/IVA",
    "28.01.001": "Cliente",
    "34.01.001": "Banca c/c",
    "79.01.005": "Stipendi impiegati",
    "79.03.001": "Oneri INPS",
    "49.27.025": "Dipendenti c/retribuzioni",
    "49.23.029": "Erario c/rit. fiscali",
    "49.25.001": "Debito v/INPS",
    # ... aggiungi tutti gli altri conti dal PDF
}

# TEMPLATE OPERAZIONI AUTOMATICHE
OPERAZIONI = {
    "Acquisto merce con fattura": {
        "dare": ["73.01.013", "28.11.009"],  # Merci + IVA
        "avere": ["49.13.001"],  # Fornitore
        "note": "Imponibile a merci, IVA a credito, totale a fornitore"
    },
    "Vendita merce con fattura": {
        "dare": ["28.01.001"],  # Cliente
        "avere": ["60.01.009", "49.23.009"],  # Vendite + IVA debito
        "note": "Totale a cliente, imponibile a vendite, IVA a debito"
    },
    "Pagamento fornitore": {
        "dare": ["49.13.001"],  # Fornitore
        "avere": ["34.01.001"],  # Banca
        "note": "Senza IVA"
    },
    "Incasso cliente": {
        "dare": ["34.01.001"],  # Banca
        "avere": ["28.01.001"],  # Cliente
        "note": "Senza IVA"
    },
    "Registrazione stipendi": {
        "dare": ["79.01.005", "79.03.001"],  # Stipendi + Oneri azienda
        "avere": ["49.27.025", "49.23.029", "49.25.001"],  # Netto + Ritenute + INPS
        "note": "Inserire lordo, calcolare netto e trattenute"
    },
    "Versamento capitale sociale": {
        "dare": ["34.01.001"],  # Banca
        "avere": ["40.01.001"],  # Capitale sociale
        "note": "Senza IVA"
    },
}

st.title("📒 Generatore AUTOMATICO Scritture Contabili")

# Selezione operazione
operazione = st.selectbox("Tipo di operazione", list(OPERAZIONI.keys()))

if operazione:
    template = OPERAZIONI[operazione]
    
    st.info(f"📋 **Conti preimpostati:**\n"
            f"DARE: {', '.join([f'{c} - {PIANO_CONTI[c]}' for c in template['dare']])}\n"
            f"AVERE: {', '.join([f'{c} - {PIANO_CONTI[c]}' for c in template['avere']])}\n\n"
            f"📝 {template['note']}")
    
    # Input importi
    col1, col2 = st.columns(2)
    with col1:
        if "IVA" in operazione:
            imponibile = st.number_input("Imponibile €", min_value=0.0, step=0.01)
            aliquota = st.number_input("Aliquota IVA %", value=22.0)
            iva = imponibile * aliquota / 100
            totale = imponibile + iva
            st.metric("Totale documento", f"€ {totale:,.2f}")
        else:
            importo = st.number_input("Importo €", min_value=0.0, step=0.01)
    
    with col2:
        data = st.date_input("Data", datetime.now())
        causale = st.text_input("Causale", placeholder="Es: Fattura n. 123")
    
    if st.button("🚀 Genera Scrittura", type="primary"):
        # Genera scrittura automatica
        righe = []
        
        if "IVA" in operazione:
            # Distribuzione importi per DARE
            for i, conto in enumerate(template['dare']):
                if '28.11.009' in conto:  # IVA
                    importo = iva
                else:
                    importo = imponibile
                righe.append({
                    'Lato': 'DARE',
                    'Conto': conto,
                    'Descrizione': PIANO_CONTI[conto],
                    'Importo': round(importo, 2)
                })
            
            # Distribuzione importi per AVERE
            for i, conto in enumerate(template['avere']):
                if '49.23.009' in conto:  # IVA debito
                    importo = iva
                elif '49.13.001' in conto:  # Fornitore
                    importo = totale
                else:
                    importo = imponibile
                righe.append({
                    'Lato': 'AVERE',
                    'Conto': conto,
                    'Descrizione': PIANO_CONTI[conto],
                    'Importo': round(importo, 2)
                })
        else:
            # Operazioni senza IVA
            for conto in template['dare']:
                righe.append({
                    'Lato': 'DARE',
                    'Conto': conto,
                    'Descrizione': PIANO_CONTI[conto],
                    'Importo': round(importo if 'importo' in locals() else imponibile, 2)
                })
            for conto in template['avere']:
                righe.append({
                    'Lato': 'AVERE',
                    'Conto': conto,
                    'Descrizione': PIANO_CONTI[conto],
                    'Importo': round(importo if 'importo' in locals() else imponibile, 2)
                })
        
        df = pd.DataFrame(righe)
        
        # Visualizza
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("DARE")
            st.dataframe(df[df['Lato']=='DARE'][['Conto','Descrizione','Importo']], hide_index=True)
            st.write(f"**Totale DARE: € {df[df['Lato']=='DARE']['Importo'].sum():,.2f}**")
        with col2:
            st.subheader("AVERE")
            st.dataframe(df[df['Lato']=='AVERE'][['Conto','Descrizione','Importo']], hide_index=True)
            st.write(f"**Totale AVERE: € {df[df['Lato']=='AVERE']['Importo'].sum():,.2f}**")
        
        # Verifica pareggio
        dare_tot = df[df['Lato']=='DARE']['Importo'].sum()
        avere_tot = df[df['Lato']=='AVERE']['Importo'].sum()
        
        if abs(dare_tot - avere_tot) < 0.01:
            st.success("✅ Scrittura BILANCIATA")
        else:
            st.error(f"❌ NON BILANCIATA (diff: € {abs(dare_tot-avere_tot):,.2f})")
