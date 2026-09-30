import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ============================================================
# 1. CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(page_title="🍝 Pastai SRL", page_icon="🍝", layout="wide")

st.title("🍝 Pastai SRL - Ripartizione Costi per Prodotto e Vaschetta")
st.markdown("Strumento di controllo di gestione basato sulla produzione 2025 e costi attuali.")
st.markdown("---")

# ============================================================
# 2. DATI DI PRODUZIONE 2025 (Fissi)
# ============================================================
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

df_mont = pd.DataFrame(montignoso_data)
df_gros = pd.DataFrame(grosseto_data)
df = pd.concat([df_mont, df_gros], ignore_index=True)

df['N_Vaschette'] = df['Produzione_2025'] / df['Peso']
df['Coefficiente'] = 1.00

# ============================================================
# 3. SIDEBAR: CONTROLLI ESSENZIALI
# ============================================================
st.sidebar.header("💰 INSERIMENTO COSTI")
st.sidebar.markdown("---")

st.sidebar.subheader("📅 Periodo di riferimento")
periodo = st.sidebar.selectbox(
    "Il bilancio copre:",
    ["Annuale (x1)", "Semestrale (x2)", "Trimestrale (x4)", "Bimestrale (x6)", "Personalizzato"],
    index=1
)

if periodo == "Personalizzato":
    moltiplicatore = st.sidebar.number_input("Moltiplicatore personalizzato", min_value=0.1, max_value=12.0, value=2.0, step=0.5)
else:
    moltiplicatore_map = {"Annuale (x1)": 1, "Semestrale (x2)": 2, "Trimestrale (x4)": 4, "Bimestrale (x6)": 6}
    moltiplicatore = moltiplicatore_map[periodo]

st.sidebar.info(f"📌 I costi inseriti verranno moltiplicati per **{moltiplicatore}**.")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Modalità di inserimento")
modalita_inserimento = st.sidebar.radio(
    "Come vuoi inserire i costi?",
    [
        "Opzione A: Inserimento diretto per sede",
        "Opzione B: Totale aziendale (ripartizione per kg)"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏢 Costi Comuni da Ripartire")
st.sidebar.markdown("_Trasporti vettore, Interessi passivi, Scontistica_")

costo_trasporti_vettore = st.sidebar.number_input("Trasporti a mezzo vettore", min_value=0.0, value=0.0, step=100.0)
costo_interessi_passivi = st.sidebar.number_input("Interessi passivi da finanziarie", min_value=0.0, value=0.0, step=100.0)
costo_scontistica = st.sidebar.number_input("Scontistica promozionale", min_value=0.0, value=0.0, step=100.0)

totale_costi_comuni = costo_trasporti_vettore + costo_interessi_passivi + costo_scontistica

st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Ripartizione Costi Comuni")
pct_montignoso_comuni = st.sidebar.slider("% Costi Comuni su Montignoso", 0, 100, 15)
pct_grosseto_comuni = 100 - pct_montignoso_comuni
st.sidebar.info(f"Montignoso: {pct_montignoso_comuni}% | Grosseto: {pct_grosseto_comuni}%")

# ============================================================
# 4. CORPO PRINCIPALE: INSERIMENTO COSTI PER SEDE
# ============================================================
st.subheader(" Inserimento Costi per Sede")
st.markdown("Inserisci i valori dal bilancio analitico. Lascia a 0 le voci non interessate.")

costi_montignoso = None
costi_grosseto = None
costi_aziendali = None

if "Opzione A" in modalita_inserimento:
    with st.expander("🏭 SEDE MONTIGNOSO", expanded=False):
        st.markdown("_Costi già attribuiti a Montignoso_")
        col1, col2 = st.columns(2)
        with col1:
            m_702 = st.number_input("702 - Materie prime e imballaggi", min_value=0.0, value=0.0, step=1000.0, key="m_702")
            m_704 = st.number_input("704 - Acquisto materiali vari", min_value=0.0, value=0.0, step=100.0, key="m_704")
            m_709 = st.number_input("709 - Servizi generali-amministrativi", min_value=0.0, value=0.0, step=100.0, key="m_709")
            m_713 = st.number_input("713 - Costi gestione autoveicoli", min_value=0.0, value=0.0, step=100.0, key="m_713")
            m_714 = st.number_input("714 - Manutenzioni", min_value=0.0, value=0.0, step=100.0, key="m_714")
            m_715 = st.number_input("715 - Altri costi per servizi", min_value=0.0, value=0.0, step=100.0, key="m_715")
        with col2:
            m_717 = st.number_input("717 - Costi godimento beni di terzi", min_value=0.0, value=0.0, step=100.0, key="m_717")
            m_720 = st.number_input("720 - Spese per lavoro dipendente", min_value=0.0, value=0.0, step=1000.0, key="m_720")
            m_725 = st.number_input("725 - Ammort. immobilizzazioni immateriali", min_value=0.0, value=0.0, step=100.0, key="m_725")
            m_727 = st.number_input("727 - Ammort. immobilizzazioni materiali", min_value=0.0, value=0.0, step=100.0, key="m_727")
            m_735 = st.number_input("735 - Imposte e tasse", min_value=0.0, value=0.0, step=100.0, key="m_735")
            m_737 = st.number_input("737/748 - Altri oneri / Straordinari", min_value=0.0, value=0.0, step=100.0, key="m_737")
        
        totale_montignoso = m_702 + m_704 + m_709 + m_713 + m_714 + m_715 + m_717 + m_720 + m_725 + m_727 + m_735 + m_737
        st.markdown(f"**💰 Totale Montignoso: € {totale_montignoso:,.2f}**")
        costi_montignoso = {'totale': totale_montignoso}

    with st.expander("🏭 SEDE GROSSETO", expanded=False):
        st.markdown("_Costi già attribuiti a Grosseto_")
        col1, col2 = st.columns(2)
        with col1:
            g_702 = st.number_input("702 - Materie prime e imballaggi", min_value=0.0, value=0.0, step=1000.0, key="g_702")
            g_704 = st.number_input("704 - Acquisto materiali vari", min_value=0.0, value=0.0, step=100.0, key="g_704")
            g_709 = st.number_input("709 - Servizi generali-amministrativi", min_value=0.0, value=0.0, step=100.0, key="g_709")
            g_713 = st.number_input("713 - Costi gestione autoveicoli", min_value=0.0, value=0.0, step=100.0, key="g_713")
            g_714 = st.number_input("714 - Manutenzioni", min_value=0.0, value=0.0, step=100.0, key="g_714")
            g_715 = st.number_input("715 - Altri costi per servizi", min_value=0.0, value=0.0, step=100.0, key="g_715")
        with col2:
            g_717 = st.number_input("717 - Costi godimento beni di terzi", min_value=0.0, value=0.0, step=100.0, key="g_717")
            g_720 = st.number_input("720 - Spese per lavoro dipendente", min_value=0.0, value=0.0, step=1000.0, key="g_720")
            g_725 = st.number_input("725 - Ammort. immobilizzazioni immateriali", min_value=0.0, value=0.0, step=100.0, key="g_725")
            g_727 = st.number_input("727 - Ammort. immobilizzazioni materiali", min_value=0.0, value=0.0, step=100.0, key="g_727")
            g_735 = st.number_input("735 - Imposte e tasse", min_value=0.0, value=0.0, step=100.0, key="g_735")
            g_737 = st.number_input("737/748 - Altri oneri / Straordinari", min_value=0.0, value=0.0, step=100.0, key="g_737")
        
        totale_grosseto = g_702 + g_704 + g_709 + g_713 + g_714 + g_715 + g_717 + g_720 + g_725 + g_727 + g_735 + g_737
        st.markdown(f"**💰 Totale Grosseto: € {totale_grosseto:,.2f}**")
        costi_grosseto = {'totale': totale_grosseto}

else:
    with st.expander("🏢 COSTI TOTALI AZIENDALI", expanded=False):
        st.markdown("_Verranno ripartiti tra le sedi in base ai kg prodotti_")
        col1, col2 = st.columns(2)
        with col1:
            a_702 = st.number_input("702 - Materie prime e imballaggi", min_value=0.0, value=0.0, step=1000.0, key="a_702")
            a_704 = st.number_input("704 - Acquisto materiali vari", min_value=0.0, value=0.0, step=100.0, key="a_704")
            a_709 = st.number_input("709 - Servizi generali-amministrativi", min_value=0.0, value=0.0, step=100.0, key="a_709")
            a_713 = st.number_input("713 - Costi gestione autoveicoli", min_value=0.0, value=0.0, step=100.0, key="a_713")
            a_714 = st.number_input("714 - Manutenzioni", min_value=0.0, value=0.0, step=100.0, key="a_714")
            a_715 = st.number_input("715 - Altri costi per servizi", min_value=0.0, value=0.0, step=100.0, key="a_715")
        with col2:
            a_717 = st.number_input("717 - Costi godimento beni di terzi", min_value=0.0, value=0.0, step=100.0, key="a_717")
            a_720 = st.number_input("720 - Spese per lavoro dipendente", min_value=0.0, value=0.0, step=1000.0, key="a_720")
            a_725 = st.number_input("725 - Ammort. immobilizzazioni immateriali", min_value=0.0, value=0.0, step=100.0, key="a_725")
            a_727 = st.number_input("727 - Ammort. immobilizzazioni materiali", min_value=0.0, value=0.0, step=100.0, key="a_727")
            a_735 = st.number_input("735 - Imposte e tasse", min_value=0.0, value=0.0, step=100.0, key="a_735")
            a_737 = st.number_input("737/748 - Altri oneri / Straordinari", min_value=0.0, value=0.0, step=100.0, key="a_737")
        
        totale_aziendale = a_702 + a_704 + a_709 + a_713 + a_714 + a_715 + a_717 + a_720 + a_725 + a_727 + a_735 + a_737
        st.markdown(f"**💰 Totale Aziendale: € {totale_aziendale:,.2f}**")
        costi_aziendali = {'totale': totale_aziendale}

# ============================================================
# 5. CALCOLO TOTALI PER SEDE
# ============================================================
if "Opzione A" in modalita_inserimento:
    totale_costi_montignoso_periodo = costi_montignoso['totale']
    totale_costi_grosseto_periodo = costi_grosseto['totale']
else:
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

budget_montignoso_periodo = totale_costi_montignoso_periodo + (totale_costi_comuni * (pct_montignoso_comuni / 100))
budget_grosseto_periodo = totale_costi_grosseto_periodo + (totale_costi_comuni * (pct_grosseto_comuni / 100))

budget_montignoso = budget_montignoso_periodo * moltiplicatore
budget_grosseto = budget_grosseto_periodo * moltiplicatore
totale_costi_annuali = (totale_costi_montignoso_periodo + totale_costi_grosseto_periodo + totale_costi_comuni) * moltiplicatore

# ============================================================
# 6. COEFFICIENTE DI COMPLESSITÀ
# ============================================================
st.markdown("---")
st.subheader("⚙️ Coefficiente di Complessità")
st.markdown("Modifica il coefficiente direttamente nella tabella. **1.00** = Standard | **1.10** = Leggermente complesso | **1.20** = Complesso | **1.30** = Molto complesso (ripieni)")

if 'df_coeff' not in st.session_state:
    st.session_state['df_coeff'] = df[['Luogo', 'Articolo', 'Descrizione', 'Peso', 'Produzione_2025', 'Coefficiente']].copy()

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button(" Reset tutti a 1.00"):
        st.session_state['df_coeff']['Coefficiente'] = 1.00
        st.rerun()

with col_btn2:
    if st.button(" Imposta Ripieni a 1.30"):
        parole_ripieni = ['tortello', 'raviolo', 'gnudo', 'tordello', 'pansoti', 'cannelloni', 'cappelletto', 'ravioli']
        mask = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole_ripieni))
        st.session_state['df_coeff'].loc[mask, 'Coefficiente'] = 1.30
        st.rerun()

with col_btn3:
    if st.button(" Pasta Semplice a 1.00"):
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

st.session_state['df_coeff'] = df_editato
df['Coefficiente'] = df_editato['Coefficiente']

# ============================================================
# 7. MOTORE DI CALCOLO
# ============================================================
df['Produzione_Ponderata'] = df['Produzione_2025'] * df['Coefficiente']

df['Quota_Costi'] = 0.0
df['Costo_per_Vaschetta'] = 0.0

for sede, budget_sede in [('Montignoso', budget_montignoso), ('Grosseto', budget_grosseto)]:
    mask = df['Luogo'] == sede
    tot_ponderato_sede = df.loc[mask, 'Produzione_Ponderata'].sum()
    
    if tot_ponderato_sede > 0 and budget_sede > 0:
        df.loc[mask, 'Quota_Costi'] = (df.loc[mask, 'Produzione_Ponderata'] / tot_ponderato_sede) * budget_sede
        df.loc[mask, 'Costo_per_Vaschetta'] = df.loc[mask, 'Quota_Costi'] / df.loc[mask, 'N_Vaschette']

totale_vaschette = df['N_Vaschette'].sum()
costo_medio_vaschetta = totale_costi_annuali / totale_vaschette if totale_vaschette > 0 else 0.0

# ============================================================
# 8. DASHBOARD KPI
# ============================================================
st.markdown("---")
st.subheader("📊 Risultati della Ripartizione")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Produzione Totale 2025", f"{df['Produzione_2025'].sum():,.2f} kg")
col2.metric("📦 Vaschette Totali", f"{totale_vaschette:,.0f}")
col3.metric("⚖️ Produzione Ponderata", f"{df['Produzione_Ponderata'].sum():,.2f}")
col4.metric(" Costo Medio/Vaschetta", f"€ {costo_medio_vaschetta:.4f}" if totale_costi_annuali > 0 else "€ 0,0000")

# ============================================================
# 9. GRAFICI ANALITICI (NOVITÀ)
# ============================================================
if totale_costi_annuali > 0:
    st.markdown("---")
    st.subheader("📈 Analisi Grafica dei Costi")
    
    # --- GRAFICO 1: TORTA - Distribuzione Costi tra Sedi ---
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.markdown("##### 🥧 Distribuzione Costi tra Sedi")
        fig_torta = go.Figure(data=[go.Pie(
            labels=['Montignoso', 'Grosseto'],
            values=[budget_montignoso, budget_grosseto],
            hole=0.4,
            marker_colors=['#FF6B6B', '#4ECDC4'],
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent:.1%}<br>€ %{value:,.0f}',
            hovertemplate='%{label}: € %{value:,.2f} (%{percent:.1%})<extra></extra>'
        )])
        fig_torta.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            font=dict(size=12)
        )
        st.plotly_chart(fig_torta, use_container_width=True)
    
    # --- GRAFICO 2: BARRE - Top 10 Prodotti per Costo/Vaschetta ---
    with col_graf2:
        st.markdown("##### 📊 Top 10 Prodotti per Costo/Vaschetta")
        top10_costo = df.nlargest(10, 'Costo_per_Vaschetta')[['Descrizione', 'Costo_per_Vaschetta', 'Luogo']].copy()
        top10_costo['Descrizione_breve'] = top10_costo['Descrizione'].str[:30] + '...'
        
        fig_barre = px.bar(
            top10_costo,
            x='Descrizione_breve',
            y='Costo_per_Vaschetta',
            color='Luogo',
            color_discrete_map={'Montignoso': '#FF6B6B', 'Grosseto': '#4ECDC4'},
            text='Costo_per_Vaschetta',
            hover_data={'Descrizione': True, 'Luogo': True, 'Costo_per_Vaschetta': ':.4f'}
        )
        fig_barre.update_traces(texttemplate='€ %{text:.4f}', textposition='outside')
        fig_barre.update_layout(
            xaxis_title='',
            yaxis_title='€ per vaschetta',
            height=400,
            margin=dict(t=20, b=80, l=20, r=20),
            showlegend=True,
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig_barre, use_container_width=True)
    
    # --- GRAFICO 3: BARRE ORIZZONTALI - Confronto Sedi ---
    st.markdown("---")
    st.markdown("#####  Confronto Produzione e Costi tra Sedi")
    
    kg_mont = df[df['Luogo'] == 'Montignoso']['Produzione_2025'].sum()
    kg_gros = df[df['Luogo'] == 'Grosseto']['Produzione_2025'].sum()
    vasch_mont = df[df['Luogo'] == 'Montignoso']['N_Vaschette'].sum()
    vasch_gros = df[df['Luogo'] == 'Grosseto']['N_Vaschette'].sum()
    prod_mont = len(df[df['Luogo'] == 'Montignoso'])
    prod_gros = len(df[df['Luogo'] == 'Grosseto'])
    costo_medio_mont = budget_montignoso / vasch_mont if vasch_mont > 0 else 0
    costo_medio_gros = budget_grosseto / vasch_gros if vasch_gros > 0 else 0
    
    fig_confronto = go.Figure()
    
    # Produzione kg
    fig_confronto.add_trace(go.Bar(
        name='Produzione (kg)',
        x=['Montignoso', 'Grosseto'],
        y=[kg_mont, kg_gros],
        marker_color='#FFB6C1',
        yaxis='y'
    ))
    
    # Costo medio per vaschetta
    fig_confronto.add_trace(go.Bar(
        name='Costo medio/vaschetta (€)',
        x=['Montignoso', 'Grosseto'],
        y=[costo_medio_mont, costo_medio_gros],
        marker_color='#87CEEB',
        yaxis='y2'
    ))
    
    fig_confronto.update_layout(
        barmode='group',
        height=400,
        yaxis=dict(title='Kg prodotti', side='left'),
        yaxis2=dict(title='€ per vaschetta', overlaying='y', side='right'),
        margin=dict(t=20, b=20, l=60, r=60),
        showlegend=True
    )
    st.plotly_chart(fig_confronto, use_container_width=True)

else:
    st.info(" Inserisci i costi nella sidebar per visualizzare i grafici analitici.")

# ============================================================
# 10. TABELLA DETTAGLIATA
# ============================================================
st.markdown("---")
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

st.subheader(f"📋 Dettaglio Prodotti ({len(df_vis)} prodotti)")

df_table = df_vis.copy()
df_table['Peso_kg'] = df_table['Peso'].map(lambda x: f"{x} kg")
df_table['Produzione'] = df_table['Produzione_2025'].map(lambda x: f"{x:,.2f} kg")
df_table['Vaschette'] = df_table['N_Vaschette'].map(lambda x: f"{x:,.0f}")

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
# 11. TOP 20 PRODOTTI
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
# 12. FORMULA DI CALCOLO
# ============================================================
with st.expander("📐 Vedi formula di calcolo e logica applicata"):
    st.markdown("""
    **Logica di Ripartizione:**
    
    1. **Separazione Costi:** I costi di Produzione/Confezionamento vengono attribuiti direttamente alla sede di competenza (Opzione A) o ripartiti per kg (Opzione B). I costi Comuni (Trasporti vettore, Interessi passivi, Scontistica promozionale) vengono ripartiti tra le sedi in base alla percentuale definita dallo slider.
    
    2. **Produzione Ponderata:** Per ogni prodotto: `Produzione (kg) × Coefficiente di Complessità`.
    
    3. **Ripartizione per Sede:** I costi totali di ogni sede (Diretti + Quota Comuni) vengono ripartiti sui prodotti di *quella specifica sede* in base alla loro % di Produzione Ponderata.
    
    4. **Costo per Vaschetta:** `Quota Costi Assegnata al Prodotto ÷ Numero Vaschette Prodotte`.
    """)

# ============================================================
# 13. EXPORT
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
st.caption("Dati produzione 2025 | Inserimento costi manuale | Ripartizione ponderata per sede e complessità")
