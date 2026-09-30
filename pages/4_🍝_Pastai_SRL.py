import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# 1. CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(page_title="Pastai SRL", page_icon="🍝", layout="wide")

st.title("🍝 Pastai SRL - Ripartizione Costi per Prodotto e Vaschetta")
st.markdown("Strumento di controllo di gestione basato sulla produzione 2025 e costi attuali.")
st.markdown("---")

# ============================================================
# 2. DATI DI PRODUZIONE 2025 (Fissi, base solida del calcolo)
# ============================================================
# Montignoso (30 prodotti - Linea Senza Glutine)
montignoso_data = {
    'Luogo': ['Montignoso'] * 30,
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

# Grosseto (61 prodotti - Linea Tradizionale)
grosseto_data = {
    'Luogo': ['Grosseto'] * 61,
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

# Unione dei dataframe e calcoli base preliminari
df_mont = pd.DataFrame(montignoso_data)
df_gros = pd.DataFrame(grosseto_data)
df = pd.concat([df_mont, df_gros], ignore_index=True)

# Calcolo automatico del numero di vaschette (Produzione kg / Peso unitario kg)
df['N_Vaschette'] = df['Produzione_2025'] / df['Peso']
df['Coefficiente'] = 1.00  # Default

# ============================================================
# 3. SIDEBAR: INSERIMENTO COSTI (Logica Amministrativa)
# ============================================================
st.sidebar.header(" INSERIMENTO COSTI DAL BILANCIO")
st.sidebar.markdown("Inserisci i valori manualmente. Lascia a 0 le voci non interessate.")
st.sidebar.markdown("---")

# --- 3.1 Annualizzazione ---
st.sidebar.subheader("📅 Periodo di riferimento")
periodo = st.sidebar.selectbox(
    "Il bilancio copre:",
    ["Annuale (x1)", "Semestrale (x2)", "Trimestrale (x4)", "Bimestrale (x6)", "Personalizzato"],
    index=1  # Default su semestrale come il bilancio attuale
)

if periodo == "Personalizzato":
    moltiplicatore = st.sidebar.number_input("Moltiplicatore personalizzato", min_value=0.1, max_value=12.0, value=2.0, step=0.5)
else:
    moltiplicatore_map = {"Annuale (x1)": 1, "Semestrale (x2)": 2, "Trimestrale (x4)": 4, "Bimestrale (x6)": 6}
    moltiplicatore = moltiplicatore_map[periodo]

st.sidebar.info(f" I costi inseriti verranno moltiplicati per **{moltiplicatore}**.")

# --- 3.2 Toggle Modalità di Inserimento ---
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Modalità di inserimento")
modalita_inserimento = st.sidebar.radio(
    "Come vuoi inserire i costi di produzione?",
    [
        "Opzione A: Inserimento diretto per sede (consigliato)",
        "Opzione B: Totale aziendale (ripartizione automatica per kg)"
    ],
    index=0
)

# ============================================================
# 3.3 BLOCCO A: COSTI PER SEDE (con expander)
# ============================================================

# Funzione helper per creare i campi di una sede
def crea_campi_sede(nome_sede, icona):
    st.sidebar.markdown("---")
    with st.sidebar.expander(f"{icona} {nome_sede}", expanded=True):
        st.sidebar.markdown(f"_Costi già attribuiti a {nome_sede}_")
        
        c702 = st.sidebar.number_input(f"702 - Materie prime e imballaggi ({nome_sede})", min_value=0.0, value=0.0, step=1000.0, help="Opzionale - Solo se si vuole il costo pieno completo")
        c704 = st.sidebar.number_input(f"704 - Acquisto materiali vari ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c709 = st.sidebar.number_input(f"709 - Servizi generali-amministrativi ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c713 = st.sidebar.number_input(f"713 - Costi gestione autoveicoli ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c714 = st.sidebar.number_input(f"714 - Manutenzioni ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c715 = st.sidebar.number_input(f"715 - Altri costi per servizi ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c717 = st.sidebar.number_input(f"717 - Costi godimento beni di terzi ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c720 = st.sidebar.number_input(f"720 - Spese per lavoro dipendente ({nome_sede})", min_value=0.0, value=0.0, step=1000.0, help="Opzionale - Solo se si vuole il costo pieno completo")
        c725 = st.sidebar.number_input(f"725 - Ammort. immobilizzazioni immateriali ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c727 = st.sidebar.number_input(f"727 - Ammort. immobilizzazioni materiali ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c735 = st.sidebar.number_input(f"735 - Imposte e tasse ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        c737 = st.sidebar.number_input(f"737/748 - Altri oneri / Straordinari ({nome_sede})", min_value=0.0, value=0.0, step=100.0)
        
        totale_sede = c702 + c704 + c709 + c713 + c714 + c715 + c717 + c720 + c725 + c727 + c735 + c737
        st.sidebar.markdown(f"**Totale {nome_sede}: € {totale_sede:,.2f}**")
        
        return {
            '702': c702, '704': c704, '709': c709, '713': c713,
            '714': c714, '715': c715, '717': c717, '720': c720,
            '725': c725, '727': c727, '735': c735, '737': c737,
            'totale': totale_sede
        }

# Funzione helper per creare i campi del totale aziendale (Opzione B)
def crea_campi_aziendali():
    st.sidebar.markdown("---")
    with st.sidebar.expander("🏢 Costi Totali Aziendali", expanded=True):
        st.sidebar.markdown("_Verranno ripartiti tra le sedi in base ai kg prodotti_")
        
        c702 = st.sidebar.number_input("702 - Materie prime e imballaggi (Totale)", min_value=0.0, value=0.0, step=1000.0)
        c704 = st.sidebar.number_input("704 - Acquisto materiali vari (Totale)", min_value=0.0, value=0.0, step=100.0)
        c709 = st.sidebar.number_input("709 - Servizi generali-amministrativi (Totale)", min_value=0.0, value=0.0, step=100.0)
        c713 = st.sidebar.number_input("713 - Costi gestione autoveicoli (Totale)", min_value=0.0, value=0.0, step=100.0)
        c714 = st.sidebar.number_input("714 - Manutenzioni (Totale)", min_value=0.0, value=0.0, step=100.0)
        c715 = st.sidebar.number_input("715 - Altri costi per servizi (Totale)", min_value=0.0, value=0.0, step=100.0)
        c717 = st.sidebar.number_input("717 - Costi godimento beni di terzi (Totale)", min_value=0.0, value=0.0, step=100.0)
        c720 = st.sidebar.number_input("720 - Spese per lavoro dipendente (Totale)", min_value=0.0, value=0.0, step=1000.0)
        c725 = st.sidebar.number_input("725 - Ammort. immobilizzazioni immateriali (Totale)", min_value=0.0, value=0.0, step=100.0)
        c727 = st.sidebar.number_input("727 - Ammort. immobilizzazioni materiali (Totale)", min_value=0.0, value=0.0, step=100.0)
        c735 = st.sidebar.number_input("735 - Imposte e tasse (Totale)", min_value=0.0, value=0.0, step=100.0)
        c737 = st.sidebar.number_input("737/748 - Altri oneri / Straordinari (Totale)", min_value=0.0, value=0.0, step=100.0)
        
        totale_aziendale = c702 + c704 + c709 + c713 + c714 + c715 + c717 + c720 + c725 + c727 + c735 + c737
        st.sidebar.markdown(f"**Totale Aziendale: € {totale_aziendale:,.2f}**")
        
        return {
            '702': c702, '704': c704, '709': c709, '713': c713,
            '714': c714, '715': c715, '717': c717, '720': c720,
            '725': c725, '727': c727, '735': c735, '737': c737,
            'totale': totale_aziendale
        }

# Inizializzazione variabili
costi_montignoso = None
costi_grosseto = None
costi_aziendali = None

if "Opzione A" in modalita_inserimento:
    costi_montignoso = crea_campi_sede("Montignoso", "🏭")
    costi_grosseto = crea_campi_sede("Grosseto", "🏭")
else:
    costi_aziendali = crea_campi_aziendali()

# ============================================================
# 3.4 BLOCCO B: COSTI COMUNI DA RIPARTIRE (Solo 3 voci)
# ============================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🏢 Blocco B: Costi Comuni da Ripartire")
st.sidebar.markdown("_Trasporti vettore, Interessi passivi, Scontistica promozionale_")

with st.sidebar.expander(" Costi Comuni", expanded=True):
    costo_trasporti_vettore = st.sidebar.number_input(
        "Trasporti a mezzo vettore (715.00002 + 715.00003)",
        min_value=0.0, value=0.0, step=100.0,
        help="Costi di trasporto non attribuibili a una sede specifica"
    )
    costo_interessi_passivi = st.sidebar.number_input(
        "Interessi passivi da finanziarie (740)",
        min_value=0.0, value=0.0, step=100.0,
        help="Interessi su finanziamenti bancari e altri oneri finanziari"
    )
    costo_scontistica = st.sidebar.number_input(
        "Scontistica promozionale (715.01001)",
        min_value=0.0, value=0.0, step=100.0,
        help="Contributi promozionali ai clienti"
    )
    
    totale_costi_comuni = costo_trasporti_vettore + costo_interessi_passivi + costo_scontistica
    st.sidebar.markdown(f"**Totale Costi Comuni: € {totale_costi_comuni:,.2f}**")

# --- Slider per la ripartizione dei costi comuni ---
st.sidebar.markdown("---")
st.sidebar.subheader("️ Chiave di Ripartizione Costi Comuni")
pct_montignoso_comuni = st.sidebar.slider(
    "% Costi Comuni su Montignoso", 
    0, 100, 15,  # Default 15% basato sulla produzione storica
    help="Percentuale dei costi comuni da attribuire a Montignoso"
)
pct_grosseto_comuni = 100 - pct_montignoso_comuni
st.sidebar.info(f"Montignoso: {pct_montignoso_comuni}% | Grosseto: {pct_grosseto_comuni}%")

# ============================================================
# 3.5 CALCOLO TOTALI PER SEDE (Post-Annualizzazione)
# ============================================================
if "Opzione A" in modalita_inserimento:
    # I costi sono già divisi per sede
    totale_costi_montignoso_periodo = costi_montignoso['totale']
    totale_costi_grosseto_periodo = costi_grosseto['totale']
else:
    # I costi sono totali aziendali, li ripartiamo per kg
    totale_aziendale_periodo = costi_aziendali['totale']
    kg_montignoso = df[df['Luogo'] == 'Montignoso']['Produzione_2025'].sum()
    kg_grosseto = df[df['Luogo'] == 'Grosseto']['Produzione_2025'].sum()
    kg_totali = kg_montignoso + kg_grosseto
    
    if kg_totali > 0:
        pct_montignoso_kg = (kg_montignoso / kg_totali) * 100
        pct_grosseto_kg = (kg_grosseto / kg_totali) * 100
    else:
        pct_montignoso_kg = 50
        pct_grosseto_kg = 50
    
    totale_costi_montignoso_periodo = totale_aziendale_periodo * (pct_montignoso_kg / 100)
    totale_costi_grosseto_periodo = totale_aziendale_periodo * (pct_grosseto_kg / 100)

# Aggiungiamo la quota dei costi comuni
budget_montignoso_periodo = totale_costi_montignoso_periodo + (totale_costi_comuni * (pct_montignoso_comuni / 100))
budget_grosseto_periodo = totale_costi_grosseto_periodo + (totale_costi_comuni * (pct_grosseto_comuni / 100))

# Annualizzazione
budget_montignoso = budget_montignoso_periodo * moltiplicatore
budget_grosseto = budget_grosseto_periodo * moltiplicatore
totale_costi_annuali = (totale_costi_montignoso_periodo + totale_costi_grosseto_periodo + totale_costi_comuni) * moltiplicatore

st.sidebar.markdown("---")
st.sidebar.metric("💰 Totale costi inseriti (periodo)", f"€ {(totale_costi_montignoso_periodo + totale_costi_grosseto_periodo + totale_costi_comuni):,.2f}")
st.sidebar.metric("📈 Totale annualizzato", f"€ {totale_costi_annuali:,.2f}")
st.sidebar.divider()
st.sidebar.metric("🏭 Budget Annuo Montignoso", f"€ {budget_montignoso:,.2f}")
st.sidebar.metric("🏭 Budget Annuo Grosseto", f"€ {budget_grosseto:,.2f}")

# ============================================================
# 4. COEFFICIENTE DI COMPLESSITÀ (Logica Interattiva)
# ============================================================
st.subheader("⚙️ 1. Definizione Coefficiente di Complessità")
st.markdown("Modifica il coefficiente direttamente nella tabella. **1.00** = Standard | **1.10** = Leggermente complesso | **1.20** = Complesso | **1.30** = Molto complesso (ripieni)")

# Inizializzazione Session State per persistenza dati durante i rerun
if 'df_coeff' not in st.session_state:
    st.session_state['df_coeff'] = df[['Luogo', 'Articolo', 'Descrizione', 'Peso', 'Produzione_2025', 'Coefficiente']].copy()

# Pulsanti rapidi per pre-compilazione intelligente
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button("🔄 Reset tutti a 1.00"):
        st.session_state['df_coeff']['Coefficiente'] = 1.00
        st.rerun()

with col_btn2:
    if st.button("🟡 Imposta Ripieni a 1.30"):
        parole_ripieni = ['tortello', 'raviolo', 'gnudo', 'tordello', 'pansoti', 'cannelloni', 'cappelletto', 'ravioli']
        mask = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole_ripieni))
        st.session_state['df_coeff'].loc[mask, 'Coefficiente'] = 1.30
        st.rerun()

with col_btn3:
    if st.button("🔵 Pasta Semplice a 1.00"):
        parole_ripieni = ['tortello', 'raviolo', 'gnudo', 'tordello', 'pansoti', 'cannelloni', 'cappelletto', 'ravioli']
        mask_ripieni = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole_ripieni))
        st.session_state['df_coeff'].loc[~mask_ripieni, 'Coefficiente'] = 1.00
        st.rerun()

with col_btn4:
    if st.button("🟢 Gnocchi/Lasagne a 1.10"):
        parole_medie = ['gnocchi', 'gnudi', 'lasagne', 'topetti', 'torta']
        mask = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole_medie))
        st.session_state['df_coeff'].loc[mask, 'Coefficiente'] = 1.10
        st.rerun()

# Data Editor interattivo
column_config = {
    "Coefficiente": st.column_config.SelectboxColumn(
        "Coeff. Complessità",
        help="Seleziona il livello di complessità produttiva",
        options=[1.00, 1.10, 1.20, 1.30],
        default=1.00
    )
}

df_editato = st.data_editor(
    st.session_state['df_coeff'],
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    key="editor_coeff"
)

# Aggiornamento stato e dataframe principale
st.session_state['df_coeff'] = df_editato
df['Coefficiente'] = df_editato['Coefficiente']

# ============================================================
# 5. MOTORE DI CALCOLO (Ripartizione per Sede)
# ============================================================
# Calcolo Produzione Ponderata (Kg * Coefficiente di Complessità)
df['Produzione_Ponderata'] = df['Produzione_2025'] * df['Coefficiente']

# Inizializzazione colonne risultati
df['Quota_Costi'] = 0.0
df['Costo_per_Vaschetta'] = 0.0

# Loop di ripartizione per ogni sede
for sede, budget_sede in [('Montignoso', budget_montignoso), ('Grosseto', budget_grosseto)]:
    mask = df['Luogo'] == sede
    tot_ponderato_sede = df.loc[mask, 'Produzione_Ponderata'].sum()
    
    # Se c'è produzione e budget, ripartisci
    if tot_ponderato_sede > 0 and budget_sede > 0:
        # La quota di costo è proporzionale alla produzione ponderata del prodotto rispetto al totale della sede
        df.loc[mask, 'Quota_Costi'] = (df.loc[mask, 'Produzione_Ponderata'] / tot_ponderato_sede) * budget_sede
        # Il costo per vaschetta è la quota divisa per il numero reale di vaschette
        df.loc[mask, 'Costo_per_Vaschetta'] = df.loc[mask, 'Quota_Costi'] / df.loc[mask, 'N_Vaschette']

# Calcolo costo medio aziendale
totale_vaschette = df['N_Vaschette'].sum()
costo_medio_vaschetta = totale_costi_annuali / totale_vaschette if totale_vaschette > 0 else 0.0

# ============================================================
# 6. DASHBOARD KPI
# ============================================================
st.markdown("---")
st.subheader("📊 2. Risultati della Ripartizione")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Produzione Totale 2025", f"{df['Produzione_2025'].sum():,.2f} kg")
col2.metric("📦 Vaschette Totali", f"{totale_vaschette:,.0f}")
col3.metric("⚖️ Produzione Ponderata", f"{df['Produzione_Ponderata'].sum():,.2f}")
col4.metric("💰 Costo Medio/Vaschetta", f"€ {costo_medio_vaschetta:.4f}" if totale_costi_annuali > 0 else "€ 0,0000")

# ============================================================
# 7. TABELLA DETTAGLIATA E FILTRI
# ============================================================
col_f1, col_f2 = st.columns(2)
with col_f1:
    filtro_sede = st.selectbox("Filtra per Sede", ["Tutte", "Montignoso", "Grosseto"])
with col_f2:
    ricerca = st.text_input(" Cerca prodotto...", "")

df_vis = df.copy()
if filtro_sede != "Tutte":
    df_vis = df_vis[df_vis['Luogo'] == filtro_sede]
if ricerca:
    df_vis = df_vis[df_vis['Descrizione'].str.contains(ricerca, case=False, na=False)]

df_vis = df_vis.sort_values('Quota_Costi', ascending=False)

st.subheader(f"📋 Dettaglio Prodotti ({len(df_vis)} prodotti)")

# Formattazione valori per la tabella
df_table = df_vis.copy()
df_table['Peso_kg'] = df_table['Peso'].map(lambda x: f"{x} kg")
df_table['Produzione'] = df_table['Produzione_2025'].map(lambda x: f"{x:,.2f} kg")
df_table['Vaschette'] = df_table['N_Vaschette'].map(lambda x: f"{x:,.0f}")

# Calcolo % incidenza per sede
def calcola_pct_sede(row):
    mask_sede = df['Luogo'] == row['Luogo']
    tot_ponderato_sede = df.loc[mask_sede, 'Produzione_Ponderata'].sum()
    if tot_ponderato_sede > 0:
        return (row['Produzione_Ponderata'] / tot_ponderato_sede) * 100
    return 0.0

df_table['% Incidenza Sede'] = df_table.apply(calcola_pct_sede, axis=1).map(lambda x: f"{x:.3f}%")
df_table['Quota Costi'] = df_table['Quota_Costi'].map(lambda x: f"€ {x:,.2f}")
df_table['Costo/Vaschetta'] = df_table['Costo_per_Vaschetta'].map(lambda x: f"€ {x:.4f}")

colonne_display = ['Luogo', 'Articolo', 'Descrizione', 'Peso_kg', 'Produzione', 
                   'Vaschette', 'Coefficiente', '% Incidenza Sede', 'Quota Costi', 'Costo/Vaschetta']

st.dataframe(
    df_table[colonne_display].rename(columns={
        'Luogo': 'Sede', 'Articolo': 'Cod.', 'Descrizione': 'Prodotto',
        'Peso_kg': 'Peso', 'Produzione': 'Produz. 2025', 'Vaschette': 'N. Vaschette',
        'Coefficiente': 'Coeff.', '% Incidenza Sede': '% Ripartizione Sede',
        'Quota Costi': 'Quota Costi Assegnata', 'Costo/Vaschetta': 'Costo Gen./Vaschetta'
    }),
    use_container_width=True, hide_index=True
)

# ============================================================
# 8. TOP 20 PRODOTTI
# ============================================================
st.markdown("---")
st.subheader("🏆 Top 20 Prodotti per Volume di Produzione")

top20 = df.nlargest(20, 'Produzione_2025')[['Luogo', 'Articolo', 'Descrizione', 'Produzione_2025']].copy()
top20['Produzione_2025'] = top20['Produzione_2025'].map(lambda x: f"{x:,.2f} kg")

st.dataframe(
    top20.rename(columns={
        'Luogo': 'Sede', 'Articolo': 'Cod.', 'Descrizione': 'Prodotto', 'Produzione_2025': 'Produzione'
    }),
    use_container_width=True, hide_index=True
)

# ============================================================
# 9. FORMULA DI CALCOLO (Spiegazione)
# ============================================================
with st.expander("📐 Vedi formula di calcolo e logica applicata"):
    st.markdown("""
    **Logica di Ripartizione (basata su indicazione Amministrativa):**
    
    1. **Separazione Costi:** I costi di Produzione/Confezionamento vengono attribuiti direttamente alla sede di competenza (Opzione A) o ripartiti per kg (Opzione B). I costi Comuni (Trasporti vettore, Interessi passivi, Scontistica promozionale) vengono ripartiti tra le sedi in base alla percentuale definita dallo slider.
    
    2. **Produzione Ponderata:** Per ogni prodotto: `Produzione (kg) × Coefficiente di Complessità`. Questo permette di caricare più costi sui prodotti che richiedono più lavoro (es. ripieni), anche se pesano uguale ad altri.
    
    3. **Ripartizione per Sede:** I costi totali di ogni sede (Diretti + Quota Comuni) vengono ripartiti sui prodotti di *quella specifica sede* in base alla loro % di Produzione Ponderata.
    
    4. **Costo per Vaschetta:** `Quota Costi Assegnata al Prodotto ÷ Numero Vaschette Prodotte`.
    
    ---
    
    **Esempio pratico:**
    - Se il budget totale di Grosseto (dopo ripartizione comuni) è € 500.000.
    - Il Tortello Maremmano 250g ha una produzione ponderata che rappresenta il 15% del totale di Grosseto.
    - Quota Costi Tortello = 15% × € 500.000 = € 75.000.
    - Se ha prodotto 113.556 vaschette, il Costo per Vaschetta = € 75.000 ÷ 113.556 = **€ 0,6605**.
    """)

# ============================================================
# 10. EXPORT DATI
# ============================================================
st.markdown("---")
st.subheader(" Esporta Dati")

csv = df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
st.download_button(
    label=" Scarica analisi completa in CSV",
    data=csv,
    file_name=f'pastai_costi_{datetime.now().strftime("%Y%m%d")}.csv',
    mime='text/csv'
)

st.markdown("---")
st.caption("Dati produzione 2025 | Inserimento costi manuale | Ripartizione ponderata per sede e complessità")
