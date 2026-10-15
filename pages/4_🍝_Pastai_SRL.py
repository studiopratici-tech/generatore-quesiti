import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# 1. CONFIGURAZIONE E CSS
# ============================================================
st.set_page_config(page_title="Pastai SRL", page_icon="🍝", layout="wide")

st.markdown("""
<style>
    [data-testid="stMetricValue"] { color: #D32F2F; font-size: 1.8rem; }
    h1 { color: #D32F2F; }
    h2 { color: #B71C1C; }
    .stButton > button { background-color: #D32F2F; color: white; border-radius: 8px; }
    .stButton > button:hover { background-color: #B71C1C; }
</style>
""", unsafe_allow_html=True)

st.title("🍝 Pastai SRL - Ripartizione Costi per Prodotto e Vaschetta")
st.markdown("Strumento di controllo di gestione con doppia base di ripartizione (2025 e 2026).")
st.markdown("---")

# ============================================================
# 2. DATI PRODUZIONE 2025
# ============================================================
montignoso_2025 = {
    'Luogo': ['Montignoso'] * 30,
    'Articolo': ["'9700","'9701","'9703","'9704","'9705","'9706","'9707","'9708","'9709","'9710",
                 "'9750","'9751","'9752","'9753","'9755","'9756","'9758","'9759","'9760","'9761",
                 "'9763","'9764","'9765","'9766","'9767","'9768","'9769","'9770","'9771","'9772"],
    'Descrizione': ['Picio Senza Glutine - 250g','Tagliatelle Senza Glutine - 250g','Spaghetti Chitarra SG - 250g',
        'Trenette Senza Glutine - 250g','Taiarin Senza Glutine - 250g','Raviolo Genovese SG - 250g',
        'Tortello Ricotta Spinaci SG - 250g','Pansoti Senza Glutine - 250g','Gnudo SG Lavorato a mano - 200g',
        'Tordello Carne SG - 250g','Pansoti Salsa Noci SG - 200g','Trenette Pesto SG - 200g',
        'Tortello RS Ragu SG - 200g','Gnudo Burro Salvia SG - 200g','Picio Ragu SG - 180g',
        'Sfoglia Lasagna SG - 250g','Lasagne Bolognese SG - 200g','Trofie Senza Glutine - 250g',
        'Trofie Pesto - 200g','Trofie Pesto SG - 180g','Taglierini Ragu SG - 180g','Tortello RS Ragu SG - 180g',
        'Tortello RS Burro Salvia SG - 180g','Pansoti Noci SG - 180g','Tordello Carne Ragu SG - 180g',
        'Lasagne Bolognese SG - 250g','Torta Bietole SG - 200g','Torta Zucchine SG - 200g',
        'Trenette Pesto SG - 180g','Ravioli Genovese Ragu SG - 180g'],
    'Peso': [0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.2,0.25,0.2,0.2,0.2,0.2,0.18,0.25,0.2,0.25,0.2,0.18,
             0.18,0.18,0.18,0.18,0.18,0.25,0.2,0.2,0.18,0.25],
    'Kg': [5678.75,1263.75,22.00,2905.25,868.75,2708.00,6061.00,3395.00,3064.80,2732.25,62.00,40.00,178.20,
           138.20,48.96,713.50,115.40,3263.00,70.00,9.00,8.10,10.80,4.50,1.98,4.68,8.50,193.20,204.80,1.98,1.50]
}

grosseto_2025 = {
    'Luogo': ['Grosseto'] * 61,
    'Articolo': ["'1001","'1003","'1005","'1007","'1009","'1101","'1109","'1110","'1111","'1113","'1121","'1141",
        "'1151","'1153","'1154","'1183","'1184","'1201","'1202","'1501","'1505","'1507","'1602","'1611","'1701",
        "'1803","'1804","'2001","'2003","'2004","'2005","'2010","'2012","'2013","'2014","'2016","'2071","'2082",
        "'2086","'2087","'2501","'2511","'4005","'4009","'4011","'4016","'4018","'4021","'4022","'4035","'4050",
        "'4053","'4055","'4056","'4057","'4058","'5001","'5004","'5005","'5007","'5008"],
    'Descrizione': ['Picio Maremmano - 1000g','Picio Maremmano - 500g','Nero Picio Seppia - 1kg','Sfoglia Lasagne - 250g',
        'Picio Maremmano - 250g','Tagliatelle - 1kg','Tagliatelle - 250g','Pappardelle - 250g','Pappardelle - 1kg',
        'Taglierini - 250g','Taglierini - 1kg','Sfoglia Lasagne - 1kg','Spaghetti Chitarra - 1kg',
        'Spaghetti Chitarra Surg - 1kg','Spaghetti Chitarra - 250g','Tonnarelli - 250g','Picio Nero Seppia - 250g',
        'Gnocchi Patate - 1kg','Gnocchi Patate - 400g','Picio Maremmano Surg - 1kg','Nero Picio Seppia Surg - 1kg',
        'Taglierino Nero Seppia Surg - 1kg','Taglierini Surg - 1kg','Pappardelle Surg - 1kg','Gnocchi Surg - 1kg',
        'Tortello Sorano - 250g','Gnudi Sorano - 200g','Tortello Maremmano - 1kg','Cannelloni RS - 250g',
        'Il Bufalino - 250g','Tortello Maremmano - 500g','Tortello Maremmano - 250g','Gnudo Maremma - 200g',
        'Gnudo Maremmano - 500g','Gnudo Maremmano - 1kg','Il Bufalino - 1kg','Tortello Funghi Porcini - 1kg',
        'Butterino Tordello Carne - 1kg','Butterino Tordello Carne - 250g','Tortello Funghi Porcini - 250g',
        'Tortello Maremmano Surg - 1kg','Gnudo Maremmano Surg - 1kg','Taiarin - 1kg','Lasagne Stordellate Verdi - 1kg',
        'Lasagne Stordellate - 1kg','Topetti Patate - 400g','Tagliatelle Verdi - 1kg','Taglierino Nero Seppia - 1kg',
        'Taglierini Nero Seppia - 250g','Tordello Apuano - 500g','Cappelletto - 250g','Tagliatelle Apuane - 250g',
        'Taiarin - 250g','Tagliatelle Verdi - 250g','Lasagne Stordellate Verdi - 250g','Lasagne Stordellate - 250g',
        'Tordello Apuano - 1kg','Raviolo Ravan - 200g','Tortello RS - 1kg','Tortello RS - 250g','Tordello Apuano Lavorato - 250g'],
    'Peso': [1,0.5,1,0.25,0.25,1,0.25,0.25,1,0.25,1,1,1,1,0.25,0.25,0.25,1,0.4,1,1,1,1,1,1,0.25,0.2,1,0.25,0.25,
             0.5,0.25,0.2,0.5,1,1,1,1,0.25,0.25,1,1,1,1,1,0.4,1,1,0.25,0.5,0.25,0.25,0.25,0.25,0.25,0.25,1,0.2,1,0.25,0.25],
    'Kg': [14400.00,3844.00,92.25,101.75,34814.00,2196.00,4403.50,3992.25,1463.00,264.25,796.00,18.00,1059.00,
           690.00,916.50,1392.50,938.25,3287.00,12271.20,5435.00,60.00,122.00,3.00,145.00,130.00,1089.00,387.60,
           17409.00,2388.00,50.25,3353.50,28389.00,11410.00,248.50,1444.00,239.00,73.00,468.00,1944.00,44.50,
           2025.00,120.00,2.00,79.00,3.00,1093.60,80.00,254.00,2124.25,471.50,1381.75,147.50,3018.50,793.75,
           4634.25,1265.00,1168.00,136.20,329.00,8814.50,10607.75]
}

# ============================================================
# 3. DATI PRODUZIONE 2026 (gen-lug, reali)
# ============================================================
montignoso_2026 = {
    'Luogo': ['Montignoso'] * 39,
    'Articolo': ["'9700","'9701","'9703","'9704","'9705","'9706","'9707","'9708","'9709","'9710",
                 "'9750","'9751","'9752","'9753","'9755","'9756","'9758","'9759","'9760","'9761",
                 "'9762","'9763","'9764","'9765","'9766","'9767","'9768","'9769","'9770","'9771",
                 "'9772","'9800","'9801","'9802","'9803","'9804","'9806","'9807","'9813"],
    'Descrizione': ['Picio Senza Glutine - 250g','Tagliatelle Senza Glutine - 250g','Spaghetti Chitarra SG - 250g',
        'Trenette Senza Glutine - 250g','Taiarin Senza Glutine - 250g','Raviolo Genovese SG - 250g',
        'Tortello Ricotta Spinaci SG - 250g','Pansoti Senza Glutine - 250g','Gnudo SG Lavorato a mano - 200g',
        'Tordello Carne SG - 250g','Pansoti Salsa Noci SG - 200g','Trenette Pesto SG - 200g',
        'Tortello RS Ragu SG - 200g','Gnudo Burro Salvia SG - 200g','Picio Ragu SG - 180g',
        'Sfoglia Lasagna SG - 250g','Lasagne Bolognese SG - 200g','Trofie Senza Glutine - 250g',
        'Trofie Pesto - 200g','Trofie Pesto SG - 180g','Pici Ragu SG Surg - 180g','Taglierini Ragu SG - 180g',
        'Tortello RS Ragu SG - 180g','Tortello RS Burro Salvia SG - 180g','Pansoti Noci SG - 180g',
        'Tordello Carne Ragu SG - 180g','Lasagne Bolognese SG - 250g','Torta Bietole SG - 200g',
        'Torta Zucchine SG - 200g','Trenette Pesto SG - 180g','Ravioli Genovese Ragu SG - 180g',
        'Lasagne Bolognese Surg SG - 250g','Trofie Pesto Surg SG - 180g','Tortello RS Burro Surg SG - 180g',
        'Pansoti Noci Surg SG - 180g','Tordello Ragu Surg SG - 180g','Gnudo Burro Salvia Surg SG - 180g',
        'Taglierini Ragu Surg SG - 180g','Lasagne Pesto SG - 250g'],
    'Peso': [0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.2,0.25,0.2,0.2,0.2,0.2,0.18,0.25,0.2,0.25,0.2,0.18,
             0.18,0.18,0.18,0.18,0.18,0.18,0.25,0.2,0.2,0.18,0.25,0.25,0.18,0.18,0.18,0.18,0.2,0.25,0.25],
    'Kg': [2987.25,899,10.25,1002.25,777,2451,3335.75,2827,1590.20,1202.25,1.2,0.4,15,77.8,1.98,555.25,9.4,
           3879.50,12.6,78.84,18,28.26,103.5,29.16,11.7,18.72,247.25,966.6,900.6,19.44,7,40,14.4,7.2,14.4,
           7.2,11.2,14,0.25]
}

grosseto_2026 = {
    'Luogo': ['Grosseto'] * 63,
    'Articolo': ["'1001","'1003","'1005","'1007","'1009","'1101","'1109","'1110","'1111","'1113","'1121","'1141",
        "'1151","'1153","'1154","'1183","'1184","'1201","'1202","'1501","'1505","'1507","'1602","'1611","'1701",
        "'1803","'1804","'2001","'2003","'2004","'2005","'2010","'2012","'2013","'2014","'2016","'2071","'2082",
        "'2086","'2087","'2501","'2511","'4005","'4009","'4011","'4016","'4018","'4021","'4022","'4030","'4035",
        "'4036","'4050","'4053","'4055","'4056","'4057","'4058","'5001","'5004","'5005","'5007","'5008"],
    'Descrizione': ['Picio Maremmano - 1000g','Picio Maremmano - 500g','Nero Picio Seppia - 1kg','Sfoglia Lasagne - 250g',
        'Picio Maremmano - 250g','Tagliatelle - 1kg','Tagliatelle - 250g','Pappardelle - 250g','Pappardelle - 1kg',
        'Taglierini - 250g','Taglierini - 1kg','Sfoglia Lasagne - 1kg','Spaghetti Chitarra - 1kg',
        'Spaghetti Chitarra Surg - 1kg','Spaghetti Chitarra - 250g','Tonnarelli - 250g','Picio Nero Seppia - 250g',
        'Gnocchi Patate - 1kg','Gnocchi Patate - 400g','Picio Maremmano Surg - 1kg','Nero Picio Seppia Surg - 1kg',
        'Taglierino Nero Seppia Surg - 1kg','Taglierini Surg - 1kg','Pappardelle Surg - 1kg','Gnocchi Surg - 1kg',
        'Tortello Sorano - 250g','Gnudi Sorano - 200g','Tortello Maremmano - 1kg','Cannelloni RS - 250g',
        'Il Bufalino - 250g','Tortello Maremmano - 500g','Tortello Maremmano - 250g','Gnudo Maremma - 200g',
        'Gnudo Maremmano - 500g','Gnudo Maremmano - 1kg','Il Bufalino - 1kg','Tortello Funghi Porcini - 1kg',
        'Butterino Tordello Carne - 1kg','Butterino Tordello Carne - 250g','Tortello Funghi Porcini - 250g',
        'Tortello Maremmano Surg - 1kg','Gnudo Maremmano Surg - 1kg','Taiarin - 1kg','Lasagne Stordellate Verdi - 1kg',
        'Lasagne Stordellate - 1kg','Topetti Patate - 400g','Tagliatelle Verdi - 1kg','Taglierino Nero Seppia - 1kg',
        'Taglierini Nero Seppia - 250g','Tagliatelle - 500g','Tordello Apuano - 500g','Tortello RS - 500g',
        'Cappelletto - 250g','Tagliatelle Apuane - 250g','Taiarin - 250g','Tagliatelle Verdi - 250g',
        'Lasagne Stordellate Verdi - 250g','Lasagne Stordellate - 250g','Tordello Apuano - 1kg','Raviolo Ravan - 200g',
        'Tortello RS - 1kg','Tortello RS - 250g','Tordello Apuano Lavorato - 250g'],
    'Peso': [1,0.5,1,0.25,0.25,1,0.25,0.25,1,0.25,1,1,1,1,0.25,0.25,0.25,1,0.4,1,1,1,1,1,1,0.25,0.2,1,0.25,0.25,
             0.5,0.25,0.2,0.5,1,1,1,1,0.25,0.25,1,1,1,1,1,0.4,1,1,0.25,0.5,0.5,0.5,0.25,0.25,0.25,0.25,0.25,0.25,
             1,0.2,1,0.25,0.25],
    'Kg': [8872,2651,64.5,30.75,19906.25,1706,2553.50,1912.25,956,125.5,735,34,1214,185,575.5,653,406,2582,7176,
           2599,60,36,39,20,129,595,168,9547,1381.50,0.25,225.5,17901,7050.20,233.5,870,60,29,273,1022,16.75,
           1215,160,56,42,4,280.8,3,149,1065.75,6,353,54,566,112.25,1676.50,541.25,2966.25,733,872,95,730,
           4528.25,6208.25]
}

# Costruzione dataframe
df25 = pd.concat([pd.DataFrame(montignoso_2025), pd.DataFrame(grosseto_2025)], ignore_index=True)
df26 = pd.concat([pd.DataFrame(montignoso_2026), pd.DataFrame(grosseto_2026)], ignore_index=True)

df25['N_Vaschette'] = df25['Kg'] / df25['Peso']
df26['N_Vaschette'] = df26['Kg'] / df26['Peso']
df25['Coefficiente'] = 1.00
df26['Coefficiente'] = 1.00

# ============================================================
# 4. SIDEBAR
# ============================================================
st.sidebar.header("💰 INSERIMENTO COSTI")
st.sidebar.markdown("---")

st.sidebar.subheader("🗓️ Base di Ripartizione")
base_scelta = st.sidebar.radio(
    "Seleziona la base di calcolo:",
    ["Base 2025 (storica)", "Base 2026 (reale gen-lug)", "Confronto 2025 vs 2026"],
    index=0
)

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

if "2026" in base_scelta:
    mesi_2026 = st.sidebar.slider("Mesi di riferimento 2026", 1, 12, 7, help="I dati 2026 coprono gen-lug (7 mesi). L'app proietta le vaschette su base annua.")
    fattore_proiezione = 12 / mesi_2026
else:
    fattore_proiezione = 1

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Modalità di inserimento")
modalita_inserimento = st.sidebar.radio(
    "Come vuoi inserire i costi?",
    ["Opzione A: Inserimento diretto per sede", "Opzione B: Totale aziendale (ripartizione per kg)"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏢 Costi Comuni da Ripartire")
costo_trasporti_vettore = st.sidebar.number_input("Trasporti a mezzo vettore", min_value=0.0, value=0.0, step=100.0)
costo_interessi_passivi = st.sidebar.number_input("Interessi passivi da finanziarie", min_value=0.0, value=0.0, step=100.0)
costo_scontistica = st.sidebar.number_input("Scontistica promozionale", min_value=0.0, value=0.0, step=100.0)
totale_costi_comuni = costo_trasporti_vettore + costo_interessi_passivi + costo_scontistica

st.sidebar.subheader("⚖️ Ripartizione Costi Comuni")
pct_montignoso_comuni = st.sidebar.slider("% Costi Comuni su Montignoso", 0, 100, 15)
pct_grosseto_comuni = 100 - pct_montignoso_comuni

# ============================================================
# 5. INSERIMENTO COSTI PER SEDE
# ============================================================
st.subheader("🏭 Inserimento Costi per Sede")

def crea_campi_sede(prefisso, nome):
    with st.expander(f"🏭 SEDE {nome}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            c702 = st.number_input(f"702 - Materie prime ({nome})", min_value=0.0, value=0.0, step=1000.0, key=f"{prefisso}_702")
            c704 = st.number_input(f"704 - Materiali vari ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_704")
            c709 = st.number_input(f"709 - Servizi generali ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_709")
            c713 = st.number_input(f"713 - Autoveicoli ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_713")
            c714 = st.number_input(f"714 - Manutenzioni ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_714")
            c715 = st.number_input(f"715 - Altri servizi ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_715")
        with col2:
            c717 = st.number_input(f"717 - Godimento beni ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_717")
            c720 = st.number_input(f"720 - Lavoro dipendente ({nome})", min_value=0.0, value=0.0, step=1000.0, key=f"{prefisso}_720")
            c725 = st.number_input(f"725 - Ammort. immat. ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_725")
            c727 = st.number_input(f"727 - Ammort. mat. ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_727")
            c735 = st.number_input(f"735 - Imposte e tasse ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_735")
            c737 = st.number_input(f"737/748 - Altri oneri ({nome})", min_value=0.0, value=0.0, step=100.0, key=f"{prefisso}_737")
        totale = c702+c704+c709+c713+c714+c715+c717+c720+c725+c727+c735+c737
        st.markdown(f"**💰 Totale {nome}: € {totale:,.2f}**")
        return totale

def crea_campi_aziendali():
    with st.expander("🏢 COSTI TOTALI AZIENDALI", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            c702 = st.number_input("702 - Materie prime (Tot)", min_value=0.0, value=0.0, step=1000.0, key="a_702")
            c704 = st.number_input("704 - Materiali vari (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_704")
            c709 = st.number_input("709 - Servizi generali (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_709")
            c713 = st.number_input("713 - Autoveicoli (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_713")
            c714 = st.number_input("714 - Manutenzioni (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_714")
            c715 = st.number_input("715 - Altri servizi (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_715")
        with col2:
            c717 = st.number_input("717 - Godimento beni (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_717")
            c720 = st.number_input("720 - Lavoro dipendente (Tot)", min_value=0.0, value=0.0, step=1000.0, key="a_720")
            c725 = st.number_input("725 - Ammort. immat. (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_725")
            c727 = st.number_input("727 - Ammort. mat. (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_727")
            c735 = st.number_input("735 - Imposte e tasse (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_735")
            c737 = st.number_input("737/748 - Altri oneri (Tot)", min_value=0.0, value=0.0, step=100.0, key="a_737")
        totale = c702+c704+c709+c713+c714+c715+c717+c720+c725+c727+c735+c737
        st.markdown(f"**💰 Totale Aziendale: € {totale:,.2f}**")
        return totale

if "Opzione A" in modalita_inserimento:
    tot_mont = crea_campi_sede("m", "MONTIGNOSO")
    tot_gros = crea_campi_sede("g", "GROSSETO")
    tot_mont_periodo, tot_gros_periodo = tot_mont, tot_gros
else:
    tot_aziendale = crea_campi_aziendali()
    # Ripartizione per kg sulla base attiva
    df_base = df25 if "2025" in base_scelta else df26
    kg_m = df_base[df_base['Luogo']=='Montignoso']['Kg'].sum()
    kg_g = df_base[df_base['Luogo']=='Grosseto']['Kg'].sum()
    kg_tot = kg_m + kg_g
    if kg_tot > 0:
        tot_mont_periodo = tot_aziendale * (kg_m / kg_tot)
        tot_gros_periodo = tot_aziendale * (kg_g / kg_tot)
    else:
        tot_mont_periodo = tot_gros_periodo = tot_aziendale / 2

# Budget per sede (periodo + comuni)
budget_mont_periodo = tot_mont_periodo + (totale_costi_comuni * pct_montignoso_comuni / 100)
budget_gros_periodo = tot_gros_periodo + (totale_costi_comuni * pct_grosseto_comuni / 100)
budget_mont = budget_mont_periodo * moltiplicatore
budget_gros = budget_gros_periodo * moltiplicatore
totale_costi_annuali = (tot_mont_periodo + tot_gros_periodo + totale_costi_comuni) * moltiplicatore

# ============================================================
# 6. COEFFICIENTE DI COMPLESSITÀ (condiviso tra basi)
# ============================================================
st.markdown("---")
st.subheader("⚙️ Coefficiente di Complessità")
st.markdown("**1.00** = Standard | **1.10** = Leggermente complesso | **1.20** = Complesso | **1.30** = Molto complesso (ripieni)")

# Unione articoli unici per il gestore coefficienti
df_coeff_base = pd.concat([df25[['Articolo','Descrizione']], df26[['Articolo','Descrizione']]]).drop_duplicates('Articolo')
if 'df_coeff' not in st.session_state:
    df_coeff_base['Coefficiente'] = 1.00
    st.session_state['df_coeff'] = df_coeff_base.copy()

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    if st.button("🔄 Reset tutti a 1.00"):
        st.session_state['df_coeff']['Coefficiente'] = 1.00
        st.rerun()
with col_btn2:
    if st.button("🟡 Imposta Ripieni a 1.30"):
        parole = ['tortello','raviolo','gnudo','tordello','pansoti','cannelloni','cappelletto','ravioli']
        mask = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole))
        st.session_state['df_coeff'].loc[mask, 'Coefficiente'] = 1.30
        st.rerun()
with col_btn3:
    if st.button("🔵 Pasta Semplice a 1.00"):
        parole = ['tortello','raviolo','gnudo','tordello','pansoti','cannelloni','cappelletto','ravioli']
        mask = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole))
        st.session_state['df_coeff'].loc[~mask, 'Coefficiente'] = 1.00
        st.rerun()
with col_btn4:
    if st.button("🟢 Gnocchi/Lasagne a 1.10"):
        parole = ['gnocchi','gnudi','lasagne','topetti','torta']
        mask = st.session_state['df_coeff']['Descrizione'].str.lower().str.contains('|'.join(parole))
        st.session_state['df_coeff'].loc[mask, 'Coefficiente'] = 1.10
        st.rerun()

df_editato = st.data_editor(
    st.session_state['df_coeff'],
    column_config={"Coefficiente": st.column_config.SelectboxColumn("Coeff.", options=[1.00,1.10,1.20,1.30], default=1.00)},
    use_container_width=True, hide_index=True, num_rows="fixed", key="editor_coeff"
)
st.session_state['df_coeff'] = df_editato

# Applica coefficienti a entrambe le basi
map_coeff = df_editato.set_index('Articolo')['Coefficiente']
df25['Coefficiente'] = df25['Articolo'].map(map_coeff).fillna(1.00)
df26['Coefficiente'] = df26['Articolo'].map(map_coeff).fillna(1.00)

# ============================================================
# 7. MOTORE DI CALCOLO (funzione riutilizzabile)
# ============================================================
def calcola_base(df, budget_m, budget_g, fattore_proj):
    df = df.copy()
    df['Produzione_Ponderata'] = df['Kg'] * df['Coefficiente']
    df['Vaschette_Proiettate'] = df['N_Vaschette'] * fattore_proj
    df['Quota_Costi'] = 0.0
    df['Costo_per_Vaschetta'] = 0.0
    for sede, budget in [('Montignoso', budget_m), ('Grosseto', budget_g)]:
        mask = df['Luogo'] == sede
        tot_pond = df.loc[mask, 'Produzione_Ponderata'].sum()
        if tot_pond > 0 and budget > 0:
            df.loc[mask, 'Quota_Costi'] = (df.loc[mask, 'Produzione_Ponderata'] / tot_pond) * budget
            df.loc[mask, 'Costo_per_Vaschetta'] = df.loc[mask, 'Quota_Costi'] / df.loc[mask, 'Vaschette_Proiettate'].replace(0, pd.NA)
    df['Costo_per_Vaschetta'] = df['Costo_per_Vaschetta'].fillna(0)
    return df

res25 = calcola_base(df25, budget_mont, budget_gros, 1)
res26 = calcola_base(df26, budget_mont, budget_gros, fattore_proiezione)

# Selezione base attiva
if "2025" in base_scelta:
    df_attivo, label_base = res25, "2025"
elif "2026" in base_scelta:
    df_attivo, label_base = res26, "2026"
else:
    df_attivo, label_base = res25, "2025 (con confronto)"

totale_vaschette = df_attivo['Vaschette_Proiettate'].sum()
costo_medio = totale_costi_annuali / totale_vaschette if totale_vaschette > 0 else 0

# ============================================================
# 8. KPI
# ============================================================
st.markdown("---")
st.subheader(f"📊 Risultati della Ripartizione - Base {label_base}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Produzione Totale", f"{df_attivo['Kg'].sum():,.2f} kg")
col2.metric("📦 Vaschette", f"{totale_vaschette:,.0f}")
col3.metric("⚖️ Produzione Ponderata", f"{df_attivo['Produzione_Ponderata'].sum():,.2f}")
col4.metric("💰 Costo Medio/Vaschetta", f"€ {costo_medio:.4f}" if totale_costi_annuali > 0 else "€ 0,0000")

if totale_costi_annuali > 0:
    max_idx = df_attivo['Costo_per_Vaschetta'].idxmax()
    min_idx = df_attivo['Costo_per_Vaschetta'].idxmin()
    st.info(f"💡 **Insight:** Prodotto più costoso: **{df_attivo.loc[max_idx,'Descrizione']}** (€ {df_attivo.loc[max_idx,'Costo_per_Vaschetta']:.4f}). Più efficiente: **{df_attivo.loc[min_idx,'Descrizione']}** (€ {df_attivo.loc[min_idx,'Costo_per_Vaschetta']:.4f}).")

# ============================================================
# 9. CONFRONTO 2025 vs 2026
# ============================================================
if "Confronto" in base_scelta:
    st.markdown("---")
    st.subheader("🔄 Confronto 2025 vs 2026 (a parità di costi inseriti)")
    st.caption("Mostra come il cambio di mix produttivo impatta sul costo/vaschetta, mantenendo fissi i costi inseriti.")

    cmp = df25[['Articolo','Descrizione','Luogo','Kg','N_Vaschette','Costo_per_Vaschetta']].merge(
        df26[['Articolo','Kg','N_Vaschette','Costo_per_Vaschetta']], on='Articolo', how='outer',
        suffixes=('_2025','_2026'))
    cmp = cmp.fillna(0)
    cmp['Var_Kg'] = cmp['Kg_2026'] - cmp['Kg_2025']
    cmp['Var_%'] = cmp.apply(lambda r: (r['Var_Kg']/r['Kg_2025']*100) if r['Kg_2025']>0 else 100, axis=1)
    cmp['Delta_Costo'] = cmp['Costo_per_Vaschetta_2026'] - cmp['Costo_per_Vaschetta_2025']
    cmp = cmp.sort_values('Var_Kg', ascending=False)

    k1, k2, k3 = st.columns(3)
    k1.metric("Kg 2025", f"{cmp['Kg_2025'].sum():,.0f}")
    k2.metric("Kg 2026 (gen-lug)", f"{cmp['Kg_2026'].sum():,.0f}")
    k3.metric("Variazione", f"{cmp['Var_Kg'].sum():+,.0f} kg")

    cmp_show = cmp[['Descrizione','Luogo','Kg_2025','Kg_2026','Var_%','Costo_per_Vaschetta_2025','Costo_per_Vaschetta_2026','Delta_Costo']].copy()
    cmp_show['Var_%'] = cmp_show['Var_%'].map(lambda x: f"{x:+.1f}%")
    cmp_show['Costo 2025'] = cmp_show['Costo_per_Vaschetta_2025'].map(lambda x: f"€ {x:.4f}")
    cmp_show['Costo 2026'] = cmp_show['Costo_per_Vaschetta_2026'].map(lambda x: f"€ {x:.4f}")
    cmp_show['Delta'] = cmp_show['Delta_Costo'].map(lambda x: f"{x:+.4f}")
    st.dataframe(cmp_show[['Descrizione','Luogo','Kg_2025','Kg_2026','Var_%','Costo 2025','Costo 2026','Delta']].rename(
        columns={'Descrizione':'Prodotto','Luogo':'Sede','Kg_2025':'Kg 2025','Kg_2026':'Kg 2026'}),
        use_container_width=True, hide_index=True)

# ============================================================
# 10. TABELLA DETTAGLIATA BASE ATTIVA
# ============================================================
st.markdown("---")
col_f1, col_f2 = st.columns(2)
with col_f1:
    filtro_sede = st.selectbox("Filtra per Sede", ["Tutte", "Montignoso", "Grosseto"])
with col_f2:
    ricerca = st.text_input("🔍 Cerca prodotto...", "")

df_vis = df_attivo.copy()
if filtro_sede != "Tutte":
    df_vis = df_vis[df_vis['Luogo'] == filtro_sede]
if ricerca:
    df_vis = df_vis[df_vis['Descrizione'].str.contains(ricerca, case=False, na=False)]
df_vis = df_vis.sort_values('Quota_Costi', ascending=False)

st.subheader(f"📋 Dettaglio Prodotti Base {label_base} ({len(df_vis)} prodotti)")

def semaforo(row):
    if row['Costo_per_Vaschetta'] == 0: return "⚪"
    elif row['Costo_per_Vaschetta'] < costo_medio * 0.7: return "🟢"
    elif row['Costo_per_Vaschetta'] < costo_medio * 1.3: return "🟡"
    else: return "🔴"

df_vis = df_vis.copy()
df_vis['Semaforo'] = df_vis.apply(semaforo, axis=1)
df_table = df_vis.copy()
df_table['Peso_kg'] = df_table['Peso'].map(lambda x: f"{x} kg")
df_table['Produzione'] = df_table['Kg'].map(lambda x: f"{x:,.2f} kg")
df_table['Vaschette'] = df_table['Vaschette_Proiettate'].map(lambda x: f"{x:,.0f}")
df_table['% Sede'] = df_table.apply(lambda r: (r['Produzione_Ponderata']/df_attivo[df_attivo['Luogo']==r['Luogo']]['Produzione_Ponderata'].sum()*100) if df_attivo[df_attivo['Luogo']==r['Luogo']]['Produzione_Ponderata'].sum()>0 else 0, axis=1).map(lambda x: f"{x:.3f}%")
df_table['Quota'] = df_table['Quota_Costi'].map(lambda x: f"€ {x:,.2f}")
df_table['Costo/Vasch'] = df_table['Costo_per_Vaschetta'].map(lambda x: f"€ {x:.4f}")

st.dataframe(df_table[['Semaforo','Luogo','Articolo','Descrizione','Peso_kg','Produzione','Vaschette','Coefficiente','% Sede','Quota','Costo/Vasch']].rename(
    columns={'Semaforo':'Livello','Luogo':'Sede','Articolo':'Cod.','Descrizione':'Prodotto','Peso_kg':'Peso',
             'Produzione':f'Produz. {label_base}','Vaschette':'N. Vaschette','Coefficiente':'Coeff.',
             '% Sede':'% Ripart. Sede','Quota':'Quota Costi','Costo/Vasch':'Costo Gen./Vaschetta'}),
    use_container_width=True, hide_index=True)

# ============================================================
# 11. EXPORT
# ============================================================
st.markdown("---")
st.subheader("💾 Esporta Dati")
csv = df_attivo.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
st.download_button(label="📥 Scarica analisi completa in CSV", data=csv,
    file_name=f'pastai_costi_base{label_base}_{datetime.now().strftime("%Y%m%d")}.csv', mime='text/csv')

st.markdown("---")
st.caption("Dati produzione 2025 e 2026 | Inserimento costi manuale | Doppia base di ripartizione")
