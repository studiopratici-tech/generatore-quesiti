import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(page_title="Pastai SRL", page_icon="🍝", layout="wide")

st.title("🍝 Pastai SRL - Ripartizione Costi Generali per Prodotto e Vaschetta")
st.markdown("Inserisci i costi generali dal bilancio e ottieni l'incidenza unitaria su ogni prodotto.")
st.markdown("---")

# ============================================================
# DATI PRODUZIONE 2025 - MONTIGNOSO
# ============================================================
montignoso_data = {
    'Luogo': ['Montignoso']*30,
    'Articolo': ["'9700", "'9701", "'9703", "'9704", "'9705", "'9706", "'9707", "'9708", 
                 "'9709", "'9710", "'9750", "'9751", "'9752", "'9753", "'9755", "'9756",
                 "'9758", "'9759", "'9760", "'9761", "'9763", "'9764", "'9765", "'9766",
                 "'9767", "'9768", "'9769", "'9770", "'9771", "'9772"],
    'Descrizione': [
        'Picio Senza Glutine - 250g', 'Tagliatelle Senza Glutine - 250g',
        'Spaghetti Chitarra SG - 250g', 'Trenette Senza Glutine - 250g',
        'Taiarin Senza Glutine - 250g', 'Raviolo Genovese SG - 250g',
        'Tortello Ricotta Spinaci SG - 250g', 'Pansoti Senza Glutine - 250g',
        'Gnudo SG Lavorato a mano - 200g', 'Tordello Carne SG - 250g',
        'Pansoti Salsa Noci SG - 200g', 'Trenette Pesto SG - 200g',
        'Tortello RS Ragù SG - 200g', 'Gnudo Burro Salvia SG - 200g',
        'Picio Ragù SG - 180g', 'Sfoglia Lasagna SG - 250g',
        'Lasagne Bolognese SG - 200g', 'Trofie Senza Glutine - 250g',
        'Trofie Pesto - 200g', 'Trofie Pesto SG - 180g',
        'Taglierini Ragù SG - 180g', 'Tortello RS Ragù SG - 180g',
        'Tortello RS Burro Salvia SG - 180g', 'Pansoti Noci SG - 180g',
        'Tordello Carne Ragù SG - 180g', 'Lasagne Bolognese SG - 250g',
        'Torta Bietole SG - 200g', 'Torta Zucchine SG - 200g',
        'Trenette Pesto SG - 180g', 'Ravioli Genovese Ragù SG - 180g'
    ],
    'Peso': [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.2, 0.25, 
             0.2, 0.2, 0.2, 0.2, 0.18, 0.25, 0.2, 0.25, 0.2, 0.18,
             0.18, 0.18, 0.18, 0.18, 0.18, 0.25, 0.2, 0.2, 0.18, 0.25],
    'Produzione_2025': [5678.75, 1263.75, 22.00, 2905.25, 868.75, 2708.00, 6061.00, 3395.00,
                        3064.80, 2732.25, 62.00, 40.00, 178.20, 138.20, 48.96, 713.50,
                        115.40, 3263.00, 70.00, 9.00, 8.10, 10.80, 4.50, 1.98,
                        4.68, 8.50, 193.20, 204.80, 1.98, 1.50]
}

# ============================================================
# DATI PRODUZIONE 2025 - GROSSETO
# ============================================================
grosseto_data = {
    'Luogo': ['Grosseto']*61,
    'Articolo': ["'1001", "'1003", "'1005", "'1007", "'1009", "'1101", "'1109", "'1110", "'1111", "'1113",
                 "'1121", "'1141", "'1151", "'1153", "'1154", "'1183", "'1184", "'1201", "'1202", "'1501",
                 "'1505", "'1507", "'1602", "'1611", "'1701", "'1803", "'1804", "'2001", "'2003", "'2004",
                 "'2005", "'2010", "'2012", "'2013", "'2014", "'2016", "'2071", "'2082", "'2086", "'2087",
                 "'2501", "'2511", "'4005", "'4009", "'4011", "'4016", "'4018", "'4021", "'4022", "'4035",
                 "'4050", "'4053", "'4055", "'4056", "'4057", "'4058", "'5001", "'5004", "'5005", "'5007", "'5008"],
    'Descrizione': [
        'Picio Maremmano - 1000g', 'Picio Maremmano - 500g', 'Nero Picio Seppia - 1kg',
        'Sfoglia Lasagne - 250g', 'Picio Maremmano - 250g', 'Tagliatelle - 1kg',
        'Tagliatelle - 250g', 'Pappardelle - 250g', 'Pappardelle - 1kg',
        'Taglierini - 250g', 'Taglierini - 1kg', 'Sfoglia Lasagne - 1kg',
        'Spaghetti Chitarra - 1kg', 'Spaghetti Chitarra Surg. - 1kg',
        'Spaghetti Chitarra - 250g', 'Tonnarelli - 250g', 'Picio Nero Seppia - 250g',
        'Gnocchi Patate - 1kg', 'Gnocchi Patate - 400g', 'Picio Maremmano Surg. - 1kg',
        'Nero Picio Seppia Surg. - 1kg', 'Taglierino Nero Seppia Surg. - 1kg',
        'Taglierini Surg. - 1kg', 'Pappardelle Surg. - 1kg', 'Gnocchi Surg. - 1kg',
        'Tortello Sorano - 250g', 'Gnudi Sorano - 200g', 'Tortello Maremmano - 1kg',
        'Cannelloni RS - 250g', 'Il Bufalino - 250g', 'Tortello Maremmano - 500g',
        'Tortello Maremmano - 250g', 'Gnudo Maremma - 200g', 'Gnudo Maremmano - 500g',
        'Gnudo Maremmano - 1kg', 'Il Bufalino - 1kg', 'Tortello Funghi Porcini - 1kg',
        'Butterino Tordello Carne - 1kg', 'Butterino Tordello Carne - 250g',
        'Tortello Funghi Porcini - 250g', 'Tortello Maremmano Surg. - 1kg',
        'Gnudo Maremmano Surg. - 1kg', 'Taiarin - 1kg', 'Lasagne Stordellate Verdi - 1kg',
        'Lasagne Stordellate - 1kg', 'Topetti Patate - 400g', 'Tagliatelle Verdi - 1kg',
        'Taglierino Nero Seppia - 1kg', 'Taglierini Nero Seppia - 250g',
        'Tordello Apuano - 500g', 'Cappelletto - 250g', 'Tagliatelle Apuane - 250g',
        'Taiarin - 250g', 'Tagliatelle Verdi - 250g', 'Lasagne Stordellate Verdi - 250g',
        'Lasagne Stordellate - 250g', 'Tordello Apuano - 1kg', 'Raviolo Ravan - 200g',
        'Tortello RS - 1kg', 'Tortello RS - 250g', 'Tordello Apuano Lavorato - 250g'
    ],
    'Peso': [1, 0.5, 1, 0.25, 0.25, 1, 0.25, 0.25, 1, 0.25, 1, 1, 1, 1, 0.25, 0.25, 0.25, 1, 0.4, 1,
             1, 1, 1, 1, 1, 0.25, 0.2, 1, 0.25, 0.25, 0.5, 0.25, 0.2, 0.5, 1, 1, 1, 1, 0.25, 0.25,
             1, 1, 1, 1, 1, 0.4, 1, 1, 0.25, 0.5, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 1, 0.2, 1, 0.25, 0.25],
    'Produzione_2025': [14400.00, 3844.00, 92.25, 101.75, 34814.00, 2196.00, 4403.50, 3992.25, 1463.00, 264.25,
                        796.00, 18.00, 1059.00, 690.00, 916.50, 1392.50, 938.25, 3287.00, 12271.20, 5435.00,
                        60.00, 122.00, 3.00, 145.00, 130.00, 1089.00, 387.60, 17409.00, 2388.00, 50.25,
                        3353.50, 28389.00, 11410.00, 248.50, 1444.00, 239.00, 73.00, 468.00, 1944.00, 44.50,
                        2025.00, 120.00, 2.00, 79.00, 3.00, 1093.60, 80.00, 254.00, 2124.25, 471.50,
                        1381.75, 147.50, 3018.50, 793.75, 4634.25, 1265.00, 1168.00, 136.20, 329.00, 8814.50, 10607.75]
}

# Unisci i dati
df_mont = pd.DataFrame(montignoso_data)
df_gros = pd.DataFrame(grosseto_data)
df = pd.concat([df_mont, df_gros], ignore_index=True)

# Calcoli fissi sui dati di produzione
df['N_Vaschette'] = df['Produzione_2025'] / df['Peso']
totale_kg = df['Produzione_2025'].sum()
totale_vaschette = df['N_Vaschette'].sum()
df['Perc_Produzione'] = (df['Produzione_2025'] / totale_kg) * 100

# ============================================================
# SIDEBAR - INSERIMENTO MANUALE COSTI DAL BILANCIO
# ============================================================
st.sidebar.header("💰 INSERIMENTO COSTI DAL BILANCIO")
st.sidebar.markdown("Inserisci i valori manualmente dal Conto Economico. Lascia a 0 le voci che non vuoi ripartire.")
st.sidebar.markdown("---")

# --- ANNUALIZZAZIONE ---
st.sidebar.subheader("📅 Periodo di riferimento")
periodo = st.sidebar.selectbox(
    "Il bilancio copre:",
    ["Annuale (x1)", "Semestrale (x2)", "Trimestrale (x4)", "Bimestrale (x6)", "Personalizzato"],
    index=1  # Default su semestrale
)

if periodo == "Personalizzato":
    moltiplicatore = st.sidebar.number_input(
        "Moltiplicatore personalizzato",
        min_value=0.1,
        max_value=12.0,
        value=2.0,
        step=0.5,
        help="Es: 2 per semestre, 4 per trimestre, 6 per bimestre, 12 per mensile"
    )
else:
    moltiplicatore_map = {
        "Annuale (x1)": 1,
        "Semestrale (x2)": 2,
        "Trimestrale (x4)": 4,
        "Bimestrale (x6)": 6
    }
    moltiplicatore = moltiplicatore_map[periodo]

st.sidebar.info(f"📌 I costi inseriti verranno moltiplicati per **{moltiplicatore}** per ottenere il totale annuo.")

# --- COSTI INDUSTRIALI ---
st.sidebar.markdown("---")
st.sidebar.subheader(" Costi Industriali")

costo_materiali_vari = st.sidebar.number_input(
    "704 - Acquisto materiali vari",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Manutenzione, pulizia, cancelleria, indumenti..."
)

costo_servizi = st.sidebar.number_input(
    "709 - Servizi generali-amministrativi",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Acqua, luce, gas, consulenze, telefonia, pasti, software..."
)

costo_auto = st.sidebar.number_input(
    "713 - Costi gestione autoveicoli",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Carburanti, leasing, noleggio, assicurazioni..."
)

costo_manutenzioni = st.sidebar.number_input(
    "714 - Manutenzioni",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Manutenzione beni propri e auto"
)

costi_altri_servizi = st.sidebar.number_input(
    "715 - Altri costi per servizi",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Trasporti, pubblicità, provvigioni, contributi..."
)

costo_godimento_beni = st.sidebar.number_input(
    "717 - Costi godimento beni di terzi",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Fitti passivi, noleggio impianti, licenze software..."
)

costo_ammortamenti_imm = st.sidebar.number_input(
    "725 - Ammort. immobilizzazioni immateriali",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Software, marchi, know-how..."
)

costo_ammortamenti_mat = st.sidebar.number_input(
    "727 - Ammort. immobilizzazioni materiali",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Fabbricati, impianti, macchinari..."
)

costo_imposte_tasse = st.sidebar.number_input(
    "735 - Imposte e tasse",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="TARI, diritti camerali, concessioni..."
)

costo_altri_oneri = st.sidebar.number_input(
    "737 - Altri oneri di gestione",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Abbuoni, arrotondamenti passivi..."
)

costi_straordinari = st.sidebar.number_input(
    "748 - Oneri straordinari",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Sopravvenienze passive..."
)

# --- COSTI DIRETTI (OPZIONALI) ---
st.sidebar.markdown("---")
st.sidebar.subheader(" Costi Diretti (opzionali)")
st.sidebar.markdown("_Inserire solo se si vuole ottenere il costo pieno completo_")

costo_materie_prime = st.sidebar.number_input(
    "702 - Materie prime, sussidi, imballaggi",
    min_value=0.0,
    value=0.0,
    step=1000.0,
    help="Materie prime, materiali di consumo, imballaggi, merci..."
)

costo_personale = st.sidebar.number_input(
    "720 - Spese per lavoro dipendente",
    min_value=0.0,
    value=0.0,
    step=1000.0,
    help="Stipendi, oneri sociali, TFR, trasferte..."
)

# --- COSTI FINANZIARI E FISCALI (OPZIONALI) ---
st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Costi Finanziari e Fiscali (opzionali)")
st.sidebar.markdown("_Di solito esclusi dalla ripartizione industriale_")

costi_finanziari = st.sidebar.number_input(
    "740 - Interessi e oneri finanziari",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="Interessi passivi, commissioni bancarie, factoring..."
)

imposte_reddito = st.sidebar.number_input(
    "750 - Imposte sul reddito",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help="IRES, IRAP..."
)

altre_spese = st.sidebar.number_input(
    "762 - Altre spese",
    min_value=0.0,
    value=0.0,
    step=10.0,
    help="Manutenzioni auto indeducibili..."
)

# --- CALCOLO TOTALE ---
totale_costi_inseriti = (
    costo_materiali_vari + costo_servizi + costo_auto + costo_manutenzioni +
    costi_altri_servizi + costo_godimento_beni + costo_ammortamenti_imm +
    costo_ammortamenti_mat + costo_imposte_tasse + costo_altri_oneri +
    costi_straordinari +
    costo_materie_prime + costo_personale +
    costi_finanziari + imposte_reddito + altre_spese
)

totale_costi_annuali = totale_costi_inseriti * moltiplicatore

st.sidebar.markdown("---")
st.sidebar.metric("💰 Totale costi inseriti", f"€ {totale_costi_inseriti:,.2f}")
st.sidebar.metric("📈 Totale annualizzato (x" + str(moltiplicatore) + ")", f"€ {totale_costi_annuali:,.2f}")

# --- OPZIONI RIPARTIZIONE ---
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Opzioni Ripartizione")

modalita = st.sidebar.radio(
    "Base di ripartizione:",
    ["Su produzione totale (kg)", "Per sede separata"],
    index=0
)

if modalita == "Per sede separata":
    st.sidebar.markdown("_Ripartisci i costi tra le due sedi_")
    pct_montignoso = st.sidebar.slider(
        "% costi su Montignoso", 
        0, 100, 15,
        help="Percentuale dei costi totali da attribuire a Montignoso"
    )
    pct_grosseto = 100 - pct_montignoso
    st.sidebar.info(f"Montignoso: {pct_montignoso}% | Grosseto: {pct_grosseto}%")

# ============================================================
# CALCOLO RIPARTIZIONE
# ============================================================
if totale_costi_annuali > 0:
    if modalita == "Su produzione totale (kg)":
        df['Quota_Costi'] = (df['Perc_Produzione'] / 100) * totale_costi_annuali
    else:
        df['Quota_Costi'] = 0.0
        for sede, pct in [('Montignoso', pct_montignoso), ('Grosseto', pct_grosseto)]:
            mask = df['Luogo'] == sede
            tot_sede = df.loc[mask, 'Produzione_2025'].sum()
            quota_sede = totale_costi_annuali * (pct / 100)
            df.loc[mask, 'Quota_Costi'] = (df.loc[mask, 'Produzione_2025'] / tot_sede) * quota_sede
    
    df['Costo_per_Vaschetta'] = df['Quota_Costi'] / df['N_Vaschette']
    costo_medio_vaschetta = totale_costi_annuali / totale_vaschette
else:
    df['Quota_Costi'] = 0.0
    df['Costo_per_Vaschetta'] = 0.0
    costo_medio_vaschetta = 0.0

# ============================================================
# DASHBOARD KPI
# ============================================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Produzione Totale 2025", f"{totale_kg:,.2f} kg")
col2.metric(" Vaschette Totali", f"{totale_vaschette:,.0f}")
col3.metric(" Prodotti", f"{len(df)}")
col4.metric("💰 Costo Medio/Vaschetta", f"€ {costo_medio_vaschetta:.4f}" if totale_costi_annuali > 0 else "€ 0,0000")

st.markdown("---")

# ============================================================
# FILTRI
# ============================================================
col_f1, col_f2 = st.columns(2)
with col_f1:
    filtro_sede = st.selectbox("Filtra per Sede", ["Tutte", "Montignoso", "Grosseto"])
with col_f2:
    ricerca = st.text_input("🔍 Cerca prodotto...", "")

df_vis = df.copy()
if filtro_sede != "Tutte":
    df_vis = df_vis[df_vis['Luogo'] == filtro_sede]
if ricerca:
    df_vis = df_vis[df_vis['Descrizione'].str.contains(ricerca, case=False, na=False)]

df_vis = df_vis.sort_values('Quota_Costi', ascending=False)

# ============================================================
# TABELLA COMPLETA PRODOTTI
# ============================================================
st.subheader(f"📋 Dettaglio Prodotti ({len(df_vis)} prodotti)")

df_table = df_vis.copy()
df_table['Peso_kg'] = df_table['Peso'].map(lambda x: f"{x} kg")
df_table['Produzione'] = df_table['Produzione_2025'].map(lambda x: f"{x:,.2f} kg")
df_table['Vaschette'] = df_table['N_Vaschette'].map(lambda x: f"{x:,.0f}")
df_table['% Produzione'] = df_table['Perc_Produzione'].map(lambda x: f"{x:.3f}%")
df_table['Quota Costi'] = df_table['Quota_Costi'].map(lambda x: f"€ {x:,.2f}")
df_table['Costo/Vaschetta'] = df_table['Costo_per_Vaschetta'].map(lambda x: f"€ {x:.4f}")

colonne_display = ['Luogo', 'Articolo', 'Descrizione', 'Peso_kg', 'Produzione', 
                   'Vaschette', '% Produzione', 'Quota Costi', 'Costo/Vaschetta']

st.dataframe(
    df_table[colonne_display].rename(columns={
        'Luogo': 'Sede',
        'Articolo': 'Cod.',
        'Descrizione': 'Prodotto',
        'Peso_kg': 'Peso',
        'Produzione': 'Produz. 2025',
        'Vaschette': 'N. Vaschette',
        '% Produzione': '% Prod.',
        'Quota Costi': 'Quota Costi Generali',
        'Costo/Vaschetta': 'Costo Gen./Vaschetta'
    }),
    use_container_width=True,
    hide_index=True
)

# ============================================================
# TOP 20 PRODOTTI
# ============================================================
st.markdown("---")
st.subheader(" Top 20 Prodotti per Volume")

top20 = df.nlargest(20, 'Produzione_2025')[['Luogo', 'Articolo', 'Descrizione', 
                                            'Produzione_2025', 'Perc_Produzione']].copy()
top20['Produzione_2025'] = top20['Produzione_2025'].map(lambda x: f"{x:,.2f} kg")
top20['Perc_Produzione'] = top20['Perc_Produzione'].map(lambda x: f"{x:.3f}%")

st.dataframe(
    top20.rename(columns={
        'Luogo': 'Sede',
        'Articolo': 'Cod.',
        'Descrizione': 'Prodotto',
        'Produzione_2025': 'Produzione',
        'Perc_Produzione': '% sul Totale'
    }),
    use_container_width=True,
    hide_index=True
)

# ============================================================
# FORMULA DI CALCOLO
# ============================================================
with st.expander("📐 Vedi formula di calcolo"):
    st.markdown("""
    **Come funziona la ripartizione:**
    
    1. **Numero Vaschette** = Produzione (kg) ÷ Peso unitario (kg)
    
    2. **% Produzione** = (Produzione Prodotto ÷ Produzione Totale) × 100
    
    3. **Quota Costi** = % Produzione × Totale Costi Generali annualizzati
    
    4. **Costo per Vaschetta** = Quota Costi ÷ Numero Vaschette
    
    ---
    
    **Esempio pratico:**
    - Tortello Maremmano 250g: 28.389 kg → 113.556 vaschette
    - % Produzione: 12,13%
    - Se inserisci € 150.000 di costi annualizzati → Quota = € 18.195
    - Costo per Vaschetta = € 0,1602
    """)

# ============================================================
# EXPORT
# ============================================================
st.markdown("---")
st.subheader("💾 Esporta Dati")

csv = df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
st.download_button(
    label="📥 Scarica analisi completa in CSV",
    data=csv,
    file_name=f'pastai_costi_{datetime.now().strftime("%Y%m%d")}.csv',
    mime='text/csv'
)

st.markdown("---")
st.caption("Dati produzione 2025 | Inserimento costi manuale dal bilancio")
