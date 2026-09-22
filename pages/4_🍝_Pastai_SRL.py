import streamlit as st
import pandas as pd
import io

# Configurazione della pagina
st.set_page_config(page_title="Ripartizione Costi Pastai SRL", layout="wide")

st.title("📊 Ripartizione Costi Generali per Prodotto e Vaschetta")
st.markdown("Inserisci i costi generali e carica il file di produzione per ottenere l'incidenza unitaria.")

# --- 1. INPUT DEI COSTI ---
st.sidebar.header("⚙️ Parametri di Costo")
modalita_ripartizione = st.sidebar.radio(
    "Modalità di ripartizione:",
    ("Unica (Aziendale)", "Separata per Sede (Consigliata)")
)

costo_generale_azienda = 0.0
costo_generale_montignoso = 0.0
costo_generale_grosseto = 0.0

if modalita_ripartizione == "Unica (Aziendale)":
    costo_generale_azienda = st.sidebar.number_input("Costi Generali Totali Aziendali (€)", min_value=0.0, value=100000.0, step=1000.0)
else:
    st.sidebar.markdown("##### Costi Specifici per Sede")
    costo_generale_montignoso = st.sidebar.number_input("Costi Generali Montignoso (€)", min_value=0.0, value=40000.0, step=1000.0)
    costo_generale_grosseto = st.sidebar.number_input("Costi Generali Grosseto (€)", min_value=0.0, value=60000.0, step=1000.0)

# --- 2. CARICAMENTO DATI ---
st.sidebar.header("📁 Caricamento Dati")
uploaded_file = st.sidebar.file_uploader("Carica il file Excel di produzione (opzionale)", type=["xlsx", "csv"])

# Dati di default (estratti dai tuoi file) per test immediato
default_data = {
    'Luogo_Produzione': ['Montignoso', 'Montignoso', 'Grosseto', 'Grosseto', 'Grosseto'],
    'Articolo': ["'9707", "'9700", "'1009", "'2010", "'2001"],
    'Descrizione_Articolo': [
        'Tortello Ricotta e Spinaci Senza Glutine - 250g',
        'Picio Senza Glutine - Confezione 250g',
        'Picio Maremmano 250g',
        'Tortello Maremmano - Confezione 250g',
        'Tortello Maremmano - Confezione 1000g'
    ],
    'Peso': [0.25, 0.25, 0.25, 0.25, 1.0],
    'Totale_2025': [6061.00, 5678.75, 34814.00, 28389.00, 17409.00]
}

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        # Pulizia base delle colonne necessarie
        df = df[['Luogo_Produzione', 'Articolo', 'Descrizione_Articolo', 'Peso', 'Totale_2025']].dropna(subset=['Totale_2025'])
    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
        df = pd.DataFrame(default_data)
else:
    st.info("Nessun file caricato. Vengono mostrati i dati di esempio (Top 5 prodotti). Carica il file Excel completo per l'analisi totale.")
    df = pd.DataFrame(default_data)

# --- 3. MOTORE DI CALCOLO ---
# Calcolo numero di vaschette/confezioni
df['Numero_Vaschette'] = df['Totale_2025'] / df['Peso']

# Calcolo ripartizione
if modalita_ripartizione == "Unica (Aziendale)":
    totale_kg = df['Totale_2025'].sum()
    df['Perc_Incidenza'] = df['Totale_2025'] / totale_kg
    df['Costo_Ripartito'] = df['Perc_Incidenza'] * costo_generale_azienda
else:
    # Ripartizione per sede
    df['Costo_Ripartito'] = 0.0
    df['Perc_Incidenza'] = 0.0
    
    for sede in ['Montignoso', 'Grosseto']:
        mask = df['Luogo_Produzione'] == sede
        if df[mask]['Totale_2025'].sum() > 0:
            costo_sede = costo_generale_montignoso if sede == 'Montignoso' else costo_generale_grosseto
            kg_sede = df[mask]['Totale_2025'].sum()
            
            df.loc[mask, 'Perc_Incidenza'] = df.loc[mask, 'Totale_2025'] / kg_sede
            df.loc[mask, 'Costo_Ripartito'] = df.loc[mask, 'Perc_Incidenza'] * costo_sede

# Calcolo costo per vaschetta
df['Costo_Generale_per_Vaschetta'] = df['Costo_Ripartito'] / df['Numero_Vaschette']

# --- 4. VISUALIZZAZIONE RISULTATI ---
st.markdown("### 📈 Risultati della Ripartizione")

# Formattazione della tabella per la visualizzazione
df_visual = df.copy()
df_visual['Peso'] = df_visual['Peso'].map(lambda x: f"{x} kg")
df_visual['Totale_2025'] = df_visual['Totale_2025'].map(lambda x: f"{x:,.2f} kg")
df_visual['Numero_Vaschette'] = df_visual['Numero_Vaschette'].map(lambda x: f"{x:,.0f}")
df_visual['Perc_Incidenza'] = df_visual['Perc_Incidenza'].map(lambda x: f"{x:.2%}")
df_visual['Costo_Ripartito'] = df_visual['Costo_Ripartito'].map(lambda x: f"€ {x:,.2f}")
df_visual['Costo_Generale_per_Vaschetta'] = df_visual['Costo_Generale_per_Vaschetta'].map(lambda x: f"€ {x:.4f}")

# Rinominare colonne per chiarezza
df_visual = df_visual.rename(columns={
    'Luogo_Produzione': 'Sede',
    'Articolo': 'Cod.',
    'Descrizione_Articolo': 'Prodotto',
    'Peso': 'Peso Unit.',
    'Totale_2025': 'Prod. Totale 2025',
    'Numero_Vaschette': 'N. Vaschette Prod.',
    'Perc_Incidenza': '% Incidenza',
    'Costo_Ripartito': 'Quota Costi Generali',
    'Costo_Generale_per_Vaschetta': 'Costo Gen. / Vaschetta'
})

st.dataframe(df_visual, use_container_width=True, hide_index=True)

# --- 5. EXPORT ---
st.markdown("### 💾 Esporta i Dati")
csv = df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
st.download_button(
    label="📥 Scarica ripartizione completa in CSV",
    data=csv,
    file_name='ripartizione_costi_pastai.csv',
    mime='text/csv',
)
