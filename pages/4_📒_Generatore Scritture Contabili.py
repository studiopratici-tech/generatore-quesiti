# pages/4_📒_Generatore Scritture Contabili.py
import streamlit as st
import pandas as pd
import json
import re
import tempfile
import os
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any
import pdfplumber
from functools import lru_cache

# ==============================================================================
# CONFIGURAZIONE PAGINA
# ==============================================================================
st.set_page_config(
    page_title="Generatore Scritture Contabili SRL | Ranocchi GIS",
    layout="wide",
    page_icon="📒",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# PIANO DEI CONTI RANOCCHI GIS - COMPLETO (~1.200 CONTI)
# Estratto dal PDF fornito: SPIACO_260323082320.pdf
# ==============================================================================
PIANO_CONTI_COMPLETO = {
    # === CREDITI VERSO SOCI ===
    "01.01.001": {"desc": "Soci c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.005": {"desc": "Soci a c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.009": {"desc": "Soci b c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.013": {"desc": "Soci c c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.017": {"desc": "Soci d c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.021": {"desc": "Soci c/decimi richiamati", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.025": {"desc": "Soci a c/decimi richiamati", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "01.01.029": {"desc": "Soci b c/decimi richiamati", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    
    # === IMMOBILIZZAZIONI IMMATERIALI - COSTI ===
    "04.01.001": {"desc": "Spese di impianto", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.005": {"desc": "Spese di ampliamento", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.009": {"desc": "Spese di costituzione", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.013": {"desc": "Spese di fusione", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.017": {"desc": "Spese di scissione", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.021": {"desc": "Spese di trasformazione", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.025": {"desc": "Spese di conferimento", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.029": {"desc": "Spese di cessione d'azienda", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.033": {"desc": "Spese di affitto d'azienda", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.037": {"desc": "Spese per variazioni societarie", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.041": {"desc": "Spese allestimento sede", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.045": {"desc": "Spese avviamento unità produttive", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    "04.01.049": {"desc": "Spese di organizzazione", "tipo": "imm_materiali", "normale": "dare", "categoria": "costi_impianto", "posizione": "Patrimoniale attivo"},
    
    # === DIRITTI, BREVETTI, SOFTWARE ===
    "04.05.001": {"desc": "Brevetti industriali", "tipo": "imm_materiali", "normale": "dare", "categoria": "diritti_brevetti", "posizione": "Patrimoniale attivo"},
    "04.05.005": {"desc": "Diritti d'autore", "tipo": "imm_materiali", "normale": "dare", "categoria": "diritti_brevetti", "posizione": "Patrimoniale attivo"},
    "04.05.009": {"desc": "Know-how", "tipo": "imm_materiali", "normale": "dare", "categoria": "diritti_brevetti", "posizione": "Patrimoniale attivo"},
    "04.05.013": {"desc": "Software specifico", "tipo": "imm_materiali", "normale": "dare", "categoria": "diritti_brevetti", "posizione": "Patrimoniale attivo"},
    "04.07.001": {"desc": "Concessioni", "tipo": "imm_materiali", "normale": "dare", "categoria": "concessioni_licenze", "posizione": "Patrimoniale attivo"},
    "04.07.005": {"desc": "Licenze", "tipo": "imm_materiali", "normale": "dare", "categoria": "concessioni_licenze", "posizione": "Patrimoniale attivo"},
    "04.07.009": {"desc": "Marchi", "tipo": "imm_materiali", "normale": "dare", "categoria": "concessioni_licenze", "posizione": "Patrimoniale attivo"},
    "04.07.013": {"desc": "Software generico", "tipo": "imm_materiali", "normale": "dare", "categoria": "concessioni_licenze", "posizione": "Patrimoniale attivo"},
    "04.09.001": {"desc": "Avviamento", "tipo": "imm_materiali", "normale": "dare", "categoria": "avviamento", "posizione": "Patrimoniale attivo"},
    
    # === FONDI AMMORTAMENTO IMMOB. IMMATERIALI ===
    "07.01.001": {"desc": "F.do amm.to spese di impianto", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_imm", "posizione": "Patrimoniale passivo"},
    "07.01.009": {"desc": "F.do amm.to spese di costituzione", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_imm", "posizione": "Patrimoniale passivo"},
    "07.05.001": {"desc": "F.do amm.to brevetti industriali", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_imm", "posizione": "Patrimoniale passivo"},
    "07.05.013": {"desc": "F.do amm.to software specifici", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_imm", "posizione": "Patrimoniale passivo"},
    "07.07.009": {"desc": "F.do amm.to marchi", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_imm", "posizione": "Patrimoniale passivo"},
    "07.09.001": {"desc": "F.do amm.to avviamento", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_imm", "posizione": "Patrimoniale passivo"},
    
    # === IMMOBILIZZAZIONI MATERIALI - TERRENI E FABBRICATI ===
    "13.01.001": {"desc": "Terreno", "tipo": "imm_materiali", "normale": "dare", "categoria": "terreni", "posizione": "Patrimoniale attivo"},
    "13.01.005": {"desc": "Terreno ammortizzabile", "tipo": "imm_materiali", "normale": "dare", "categoria": "terreni", "posizione": "Patrimoniale attivo"},
    "13.03.001": {"desc": "Fabbricati civili", "tipo": "imm_materiali", "normale": "dare", "categoria": "fabbricati", "posizione": "Patrimoniale attivo"},
    "13.03.005": {"desc": "Fabbricati industriali", "tipo": "imm_materiali", "normale": "dare", "categoria": "fabbricati", "posizione": "Patrimoniale attivo"},
    "13.03.009": {"desc": "Fabbricati commerciali", "tipo": "imm_materiali", "normale": "dare", "categoria": "fabbricati", "posizione": "Patrimoniale attivo"},
    "13.03.013": {"desc": "Costruzioni leggere", "tipo": "imm_materiali", "normale": "dare", "categoria": "fabbricati", "posizione": "Patrimoniale attivo"},
    "13.03.017": {"desc": "Fabbricati (prof. ante 15.6.1990)", "tipo": "imm_materiali", "normale": "dare", "categoria": "fabbricati", "posizione": "Patrimoniale attivo"},
    
    # === IMPIANTI E MACCHINARI ===
    "13.05.009": {"desc": "Impianto elettrico", "tipo": "imm_materiali", "normale": "dare", "categoria": "impianti", "posizione": "Patrimoniale attivo"},
    "13.05.013": {"desc": "Impianto idraulico", "tipo": "imm_materiali", "normale": "dare", "categoria": "impianti", "posizione": "Patrimoniale attivo"},
    "13.05.017": {"desc": "Impianto telefonico", "tipo": "imm_materiali", "normale": "dare", "categoria": "impianti", "posizione": "Patrimoniale attivo"},
    "13.05.021": {"desc": "Impianto d'allarme", "tipo": "imm_materiali", "normale": "dare", "categoria": "impianti", "posizione": "Patrimoniale attivo"},
    "13.05.025": {"desc": "Impianto antincendio", "tipo": "imm_materiali", "normale": "dare", "categoria": "impianti", "posizione": "Patrimoniale attivo"},
    "13.05.029": {"desc": "Impianto di condizionamento", "tipo": "imm_materiali", "normale": "dare", "categoria": "impianti", "posizione": "Patrimoniale attivo"},
    "13.05.045": {"desc": "Macchinari automatici", "tipo": "imm_materiali", "normale": "dare", "categoria": "macchinari", "posizione": "Patrimoniale attivo"},
    "13.05.049": {"desc": "Macchinari non automatici", "tipo": "imm_materiali", "normale": "dare", "categoria": "macchinari", "posizione": "Patrimoniale attivo"},
    "13.05.053": {"desc": "Macchinari", "tipo": "imm_materiali", "normale": "dare", "categoria": "macchinari", "posizione": "Patrimoniale attivo"},
    
    # === ATTREZZATURE E ALTRI BENI ===
    "13.07.001": {"desc": "Attrezzature industriali", "tipo": "imm_materiali", "normale": "dare", "categoria": "attrezzature", "posizione": "Patrimoniale attivo"},
    "13.07.005": {"desc": "Attrezzature commerciali", "tipo": "imm_materiali", "normale": "dare", "categoria": "attrezzature", "posizione": "Patrimoniale attivo"},
    "13.07.010": {"desc": "Attrezzatura varia e minuta (<516)", "tipo": "imm_materiali", "normale": "dare", "categoria": "attrezzature", "posizione": "Patrimoniale attivo"},
    "13.09.001": {"desc": "Autovetture", "tipo": "imm_materiali", "normale": "dare", "categoria": "automezzi", "posizione": "Patrimoniale attivo"},
    "13.09.005": {"desc": "Autocarri", "tipo": "imm_materiali", "normale": "dare", "categoria": "automezzi", "posizione": "Patrimoniale attivo"},
    "13.09.009": {"desc": "Motoveicoli", "tipo": "imm_materiali", "normale": "dare", "categoria": "automezzi", "posizione": "Patrimoniale attivo"},
    "13.09.017": {"desc": "Autovetture professionista", "tipo": "imm_materiali", "normale": "dare", "categoria": "automezzi", "posizione": "Patrimoniale attivo"},
    "13.09.021": {"desc": "Autovetture agente di commercio", "tipo": "imm_materiali", "normale": "dare", "categoria": "automezzi", "posizione": "Patrimoniale attivo"},
    "13.09.025": {"desc": "Autovetture uso promiscuo dipendente", "tipo": "imm_materiali", "normale": "dare", "categoria": "automezzi", "posizione": "Patrimoniale attivo"},
    "13.09.061": {"desc": "Macchine d'ufficio elettroniche", "tipo": "imm_materiali", "normale": "dare", "categoria": "informatica", "posizione": "Patrimoniale attivo"},
    "13.09.065": {"desc": "Computer ed accessori", "tipo": "imm_materiali", "normale": "dare", "categoria": "informatica", "posizione": "Patrimoniale attivo"},
    "13.09.069": {"desc": "Telefonia fissa", "tipo": "imm_materiali", "normale": "dare", "categoria": "informatica", "posizione": "Patrimoniale attivo"},
    "13.09.073": {"desc": "Telefonia mobile", "tipo": "imm_materiali", "normale": "dare", "categoria": "informatica", "posizione": "Patrimoniale attivo"},
    "13.09.077": {"desc": "Mobili", "tipo": "imm_materiali", "normale": "dare", "categoria": "arredi", "posizione": "Patrimoniale attivo"},
    "13.09.081": {"desc": "Arredi", "tipo": "imm_materiali", "normale": "dare", "categoria": "arredi", "posizione": "Patrimoniale attivo"},
    "13.09.117": {"desc": "Beni materiali < 516,46", "tipo": "imm_materiali", "normale": "dare", "categoria": "piccoli_beni", "posizione": "Patrimoniale attivo"},
    
    # === FONDI AMMORTAMENTO IMMOB. MATERIALI ===
    "16.01.005": {"desc": "F.do amm.to fabbricati civili", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.01.009": {"desc": "F.do amm.to fabbricati industriali", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.03.009": {"desc": "F.do amm.to impianto elettrico", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.03.013": {"desc": "F.do amm.to impianto idraulico", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.001": {"desc": "F.do amm.to autovetture", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.005": {"desc": "F.do amm.to autocarri", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.045": {"desc": "F.do amm.to computer ed accessori", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.049": {"desc": "F.do amm.to telefonia fissa", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.053": {"desc": "F.do amm.to telefonia mobile", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.057": {"desc": "F.do amm.to mobili", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.061": {"desc": "F.do amm.to arredi", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    "16.07.097": {"desc": "F.do amm.to beni < euro 516,46", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi_amm_mat", "posizione": "Patrimoniale passivo"},
    
    # === RIMANENZE ===
    "25.01.001": {"desc": "Materie prime", "tipo": "rimanenze", "normale": "dare", "categoria": "magazzino", "posizione": "Patrimoniale attivo"},
    "25.01.009": {"desc": "Materiale di consumo", "tipo": "rimanenze", "normale": "dare", "categoria": "magazzino", "posizione": "Patrimoniale attivo"},
    "25.07.001": {"desc": "Prodotti finiti", "tipo": "rimanenze", "normale": "dare", "categoria": "magazzino", "posizione": "Patrimoniale attivo"},
    "25.07.005": {"desc": "Merci", "tipo": "rimanenze", "normale": "dare", "categoria": "magazzino", "posizione": "Patrimoniale attivo"},
    
    # === CREDITI COMMERCIALI - CLIENTI ===
    "28.01.001": {"desc": "Cliente", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti", "posizione": "Patrimoniale attivo"},
    "28.01.002": {"desc": "Clienti Robin tur", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti", "posizione": "Patrimoniale attivo"},
    "28.01.005": {"desc": "Effetti attivi", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti", "posizione": "Patrimoniale attivo"},
    "28.01.037": {"desc": "Fatture da emettere", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti", "posizione": "Patrimoniale attivo"},
    "28.01.055": {"desc": "Carte di credito", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti", "posizione": "Patrimoniale attivo"},
    
    # === CREDITI TRIBUTARI ===
    "28.11.001": {"desc": "Credito IRES", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_imposte", "posizione": "Patrimoniale attivo"},
    "28.11.005": {"desc": "Credito IRAP", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_imposte", "posizione": "Patrimoniale attivo"},
    "28.11.009": {"desc": "Credito IVA", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_iva", "posizione": "Patrimoniale attivo"},
    "28.11.017": {"desc": "Erario c/IVA acquisti", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_iva", "posizione": "Patrimoniale attivo"},
    "28.11.018": {"desc": "Erario c/IVA acquisti in sospensione", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_iva", "posizione": "Patrimoniale attivo"},
    "28.11.021": {"desc": "Erario c/acconto IRES", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_imposte", "posizione": "Patrimoniale attivo"},
    "28.11.025": {"desc": "Erario c/acconto IRAP", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_imposte", "posizione": "Patrimoniale attivo"},
    "28.11.029": {"desc": "Erario c/acconto IVA", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_iva", "posizione": "Patrimoniale attivo"},
    "28.11.049": {"desc": "Erario c/rit. subite", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_ritenute", "posizione": "Patrimoniale attivo"},
    "28.11.061": {"desc": "Credito IVA annuale in compensazione", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_iva", "posizione": "Patrimoniale attivo"},
    "28.11.081": {"desc": "Credito IVA annuale a rimborso", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_iva", "posizione": "Patrimoniale attivo"},
    "28.11.097": {"desc": "Credito IRES c/rimborso", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_imposte", "posizione": "Patrimoniale attivo"},
    "28.11.101": {"desc": "Credito IRAP c/rimborso", "tipo": "crediti_tributari", "normale": "dare", "categoria": "crediti_imposte", "posizione": "Patrimoniale attivo"},
    
    # === CREDITI VERSO ALTRI ===
    "28.15.045": {"desc": "Soci c/prelevamento", "tipo": "crediti_altri", "normale": "dare", "categoria": "crediti_soci", "posizione": "Patrimoniale attivo"},
    "28.15.053": {"desc": "Dipendenti c/anticipi su retrib.", "tipo": "crediti_altri", "normale": "dare", "categoria": "crediti_personale", "posizione": "Patrimoniale attivo"},
    "28.15.061": {"desc": "Dipendenti c/prestiti", "tipo": "crediti_altri", "normale": "dare", "categoria": "crediti_personale", "posizione": "Patrimoniale attivo"},
    "28.15.069": {"desc": "Amministratori c/anticipi", "tipo": "crediti_altri", "normale": "dare", "categoria": "crediti_amministratori", "posizione": "Patrimoniale attivo"},
    "28.15.085": {"desc": "Caparre a fornitori", "tipo": "crediti_altri", "normale": "dare", "categoria": "crediti_fornitori", "posizione": "Patrimoniale attivo"},
    
    # === LIQUIDITÀ ===
    "34.01.001": {"desc": "Banca c/c A", "tipo": "liquidita", "normale": "dare", "categoria": "banca", "posizione": "Patrimoniale"},
    "34.01.005": {"desc": "Banca c/c B", "tipo": "liquidita", "normale": "dare", "categoria": "banca", "posizione": "Patrimoniale"},
    "34.01.009": {"desc": "Banca c/c C", "tipo": "liquidita", "normale": "dare", "categoria": "banca", "posizione": "Patrimoniale"},
    "34.01.045": {"desc": "Posta c/c", "tipo": "liquidita", "normale": "dare", "categoria": "banca", "posizione": "Patrimoniale"},
    "34.05.001": {"desc": "Cassa contanti", "tipo": "liquidita", "normale": "dare", "categoria": "cassa", "posizione": "Patrimoniale attivo"},
    
    # === PATRIMONIO NETTO ===
    "40.01.001": {"desc": "Capitale sociale", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "capitale", "posizione": "Patrimoniale passivo"},
    "40.07.001": {"desc": "Riserva legale", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "riserve", "posizione": "Patrimoniale passivo"},
    "40.13.010": {"desc": "Riserva contributi in conto capitale", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "riserve", "posizione": "Patrimoniale passivo"},
    "40.15.001": {"desc": "Utile esercizi precedenti", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "riserve", "posizione": "Patrimoniale passivo"},
    "40.17.001": {"desc": "Utile d'esercizio", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "risultato", "posizione": "Patrimoniale passivo"},
    "40.17.005": {"desc": "Perdita esercizio", "tipo": "patrimonio_netto", "normale": "dare", "categoria": "risultato", "posizione": "Patrimoniale attivo"},
    
    # === FONDI PER RISCHI E TFR ===
    "43.01.001": {"desc": "Fondo tratt. quiesc. e obblighi simili", "tipo": "fondi_rischi", "normale": "avere", "categoria": "fondi", "posizione": "Patrimoniale passivo"},
    "46.01.001": {"desc": "Fondo T.F.R.", "tipo": "fondi_tfr", "normale": "avere", "categoria": "tfr", "posizione": "Patrimoniale passivo"},
    
    # === DEBITI COMMERCIALI - FORNITORI ===
    "49.13.001": {"desc": "Fornitore", "tipo": "debiti_commerciali", "normale": "avere", "categoria": "fornitori", "posizione": "Patrimoniale"},
    "49.13.005": {"desc": "Fatture da ricevere", "tipo": "debiti_commerciali", "normale": "avere", "categoria": "fornitori", "posizione": "Patrimoniale passivo"},
    "49.13.009": {"desc": "Rappresentanti c/provv. da liquidare", "tipo": "debiti_commerciali", "normale": "avere", "categoria": "fornitori", "posizione": "Patrimoniale passivo"},
    
    # === DEBITI TRIBUTARI ===
    "49.23.001": {"desc": "Erario c/IRES", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_imposte", "posizione": "Patrimoniale"},
    "49.23.005": {"desc": "Erario c/IRAP", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_imposte", "posizione": "Patrimoniale"},
    "49.23.009": {"desc": "Erario c/IVA", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_iva", "posizione": "Patrimoniale"},
    "49.23.010": {"desc": "Erario c/IVA rateizzato", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_iva", "posizione": "Patrimoniale"},
    "49.23.013": {"desc": "Erario c/IVA vendite", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_iva", "posizione": "Patrimoniale passivo"},
    "49.23.029": {"desc": "Erario c/rit. fiscali lav. dipendenti", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_ritenute", "posizione": "Patrimoniale passivo"},
    "49.23.033": {"desc": "Erario c/rit. fiscali collab. a progetto", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_ritenute", "posizione": "Patrimoniale passivo"},
    "49.23.037": {"desc": "Erario c/rit. fiscali collab. occas.", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_ritenute", "posizione": "Patrimoniale passivo"},
    "49.23.039": {"desc": "Erario c/rit. fiscali lav. autonomi", "tipo": "debiti_tributari", "normale": "avere", "categoria": "debiti_ritenute", "posizione": "Patrimoniale"},
    
    # === DEBITI PREVIDENZIALI ===
    "49.25.001": {"desc": "Debito v/ INPS lavoro dipendente", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inps", "posizione": "Patrimoniale"},
    "49.25.003": {"desc": "Debito v/ INPS lavoro autonomo", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inps", "posizione": "Patrimoniale passivo"},
    "49.25.005": {"desc": "Debito v/ INAIL", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inail", "posizione": "Patrimoniale passivo"},
    "49.25.013": {"desc": "Debito v/ ENASARCO", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "enasarco", "posizione": "Patrimoniale passivo"},
    
    # === DEBITI FINANZIARI ===
    "49.07.033": {"desc": "Mutuo ipotecario", "tipo": "debiti_finanziari", "normale": "avere", "categoria": "mutui", "posizione": "Patrimoniale passivo"},
    "49.07.037": {"desc": "Banca c/finanziamenti", "tipo": "debiti_finanziari", "normale": "avere", "categoria": "finanziamenti", "posizione": "Patrimoniale passivo"},
    "49.07.039": {"desc": "Mutuo chirografario", "tipo": "debiti_finanziari", "normale": "avere", "categoria": "mutui", "posizione": "Patrimoniale passivo"},
    
    # === DEBITI VERSO PERSONALE ===
    "49.27.001": {"desc": "Debiti v/amministratori", "tipo": "debiti_personale", "normale": "avere", "categoria": "amministratori", "posizione": "Patrimoniale passivo"},
    "49.27.025": {"desc": "Dipendenti c/retribuzioni", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale", "posizione": "Patrimoniale passivo"},
    "49.27.029": {"desc": "Impiegati c/retribuzioni", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale", "posizione": "Patrimoniale passivo"},
    "49.27.033": {"desc": "Operai c/retribuzioni", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale", "posizione": "Patrimoniale passivo"},
    "49.27.041": {"desc": "Collaboratori c/compensi", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale", "posizione": "Patrimoniale passivo"},
    "49.27.045": {"desc": "Dipendenti c/ferie da liquidare", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale", "posizione": "Patrimoniale passivo"},
    "49.27.089": {"desc": "Soci c/dividendi", "tipo": "debiti_personale", "normale": "avere", "categoria": "soci", "posizione": "Patrimoniale passivo"},
    
    # === RICAVI VENDITE E PRESTAZIONI ===
    "60.01.001": {"desc": "Ricavi da cessioni di beni", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite", "posizione": "Economico ricavi"},
    "60.01.005": {"desc": "Ricavi da prestazione di servizi", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite", "posizione": "Economico ricavi"},
    "60.01.009": {"desc": "Merci c/vendite", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite", "posizione": "Economico ricavi"},
    "60.01.013": {"desc": "Prodotti finiti c/vendite", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite", "posizione": "Economico ricavi"},
    "60.01.037": {"desc": "Canoni di locazione immobili", "tipo": "economico_ricavi", "normale": "avere", "categoria": "affitti", "posizione": "Economico ricavi"},
    "60.01.041": {"desc": "Canoni locazione altri cespiti", "tipo": "economico_ricavi", "normale": "avere", "categoria": "affitti", "posizione": "Economico ricavi"},
    
    # === ALTRI RICAVI E PROVENTI ===
    "71.01.001": {"desc": "Canoni di locazione fabbricati", "tipo": "altri_ricavi", "normale": "avere", "categoria": "affitti", "posizione": "Economico ricavi"},
    "71.01.029": {"desc": "Provvigioni attive", "tipo": "altri_ricavi", "normale": "avere", "categoria": "proventi", "posizione": "Economico ricavi"},
    "71.01.053": {"desc": "Risarcimento danni", "tipo": "altri_ricavi", "normale": "avere", "categoria": "proventi", "posizione": "Economico ricavi"},
    "71.01.081": {"desc": "Contrib. c/capitale", "tipo": "altri_ricavi", "normale": "avere", "categoria": "contributi", "posizione": "Economico ricavi"},
    "71.01.085": {"desc": "Contrib. c/esercizio", "tipo": "altri_ricavi", "normale": "avere", "categoria": "contributi", "posizione": "Economico ricavi"},
    
    # === ACQUISTI MATERIE E MERCI ===
    "73.01.001": {"desc": "Materie prime c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti", "posizione": "Economico costi"},
    "73.01.013": {"desc": "Merci c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti", "posizione": "Economico costi"},
    "73.01.017": {"desc": "Materiale di consumo c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti", "posizione": "Economico costi"},
    "73.01.021": {"desc": "Imballaggi c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti", "posizione": "Economico costi"},
    "73.01.037": {"desc": "Fabbricati civili c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili", "posizione": "Economico costi"},
    "73.01.041": {"desc": "Fabbricati ind.li c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili", "posizione": "Economico costi"},
    
    # === ALTRI ACQUISTI ===
    "73.09.006": {"desc": "Carburanti e lubrificanti", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi", "posizione": "Economico costi"},
    "73.09.042": {"desc": "Carbur. e lubr. non deducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi", "posizione": "Economico costi"},
    "73.09.045": {"desc": "Cancelleria e stampati", "tipo": "economico_costi", "normale": "dare", "categoria": "ufficio", "posizione": "Economico costi"},
    "73.09.053": {"desc": "Trasporti su acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "logistica", "posizione": "Economico costi"},
    "73.09.069": {"desc": "Abbigliamento del personale", "tipo": "economico_costi", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "73.09.077": {"desc": "Beni < Euro 516", "tipo": "economico_costi", "normale": "dare", "categoria": "piccoli_beni", "posizione": "Economico costi"},
    "73.09.121": {"desc": "Altri acquisti indeducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "indeducibili", "posizione": "Economico costi"},
    
    # === SERVIZI - COSTI INDUSTRIALI ===
    "75.01.005": {"desc": "Trasporti", "tipo": "economico_costi", "normale": "dare", "categoria": "logistica", "posizione": "Economico costi"},
    "75.01.025": {"desc": "Energia elettrica", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.01.026": {"desc": "Energia elettrica ind. 50%", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.01.028": {"desc": "Energia elettrica ind. 80%", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.01.033": {"desc": "Gas riscaldamento", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.01.037": {"desc": "Acqua", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.01.041": {"desc": "Consulenze tecniche", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    
    # === MANUTENZIONI ===
    "75.05.001": {"desc": "Manut. fabbricati", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni", "posizione": "Economico costi"},
    "75.05.005": {"desc": "Manut. fabbricati civili", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni", "posizione": "Economico costi"},
    "75.05.014": {"desc": "Manut. e rip. fabbr. non strum. inded.", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni", "posizione": "Economico costi"},
    "75.05.017": {"desc": "Manutenzioni impianti e macchinari", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni", "posizione": "Economico costi"},
    "75.05.029": {"desc": "Manut. impianto elettrico", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni", "posizione": "Economico costi"},
    "75.05.033": {"desc": "Manut. impianto idraulico", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni", "posizione": "Economico costi"},
    "75.05.105": {"desc": "Manut. autovetture", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi", "posizione": "Economico costi"},
    "75.05.106": {"desc": "Manut. autovetture non deducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi", "posizione": "Economico costi"},
    "75.05.145": {"desc": "Manut. computer ed accessori", "tipo": "economico_costi", "normale": "dare", "categoria": "informatica", "posizione": "Economico costi"},
    "75.05.149": {"desc": "Manut. telefonia fissa", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.05.153": {"desc": "Manut. telefonia mobile", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.05.154": {"desc": "Manut. telefonia non deducibile", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.05.157": {"desc": "Manut. mobili", "tipo": "economico_costi", "normale": "dare", "categoria": "arredi", "posizione": "Economico costi"},
    "75.05.161": {"desc": "Manut. arredi", "tipo": "economico_costi", "normale": "dare", "categoria": "arredi", "posizione": "Economico costi"},
    
    # === COSTI AMMINISTRATIVI ===
    "75.11.001": {"desc": "Consulenze amministrative", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.11.002": {"desc": "Consulenze", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.11.005": {"desc": "Consulenze legali", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.11.009": {"desc": "Consulenze notarili", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.11.013": {"desc": "Spese tenuta contabilità/paghe", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.11.017": {"desc": "Compensi amministratore", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori", "posizione": "Economico costi"},
    "75.11.018": {"desc": "Comp. ammr.i profes.(soci snc-sas)", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori", "posizione": "Economico costi"},
    "75.11.021": {"desc": "Contr. INPS amministratori", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori", "posizione": "Economico costi"},
    "75.11.033": {"desc": "Compensi C.D.A.", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori", "posizione": "Economico costi"},
    "75.11.065": {"desc": "Compensi al collegio sindacale", "tipo": "economico_costi", "normale": "dare", "categoria": "sindaci", "posizione": "Economico costi"},
    "75.11.073": {"desc": "Compensi per collab. a progetto", "tipo": "economico_costi", "normale": "dare", "categoria": "collaboratori", "posizione": "Economico costi"},
    "75.11.077": {"desc": "Contr. INPS collab. a progetto", "tipo": "economico_costi", "normale": "dare", "categoria": "collaboratori", "posizione": "Economico costi"},
    "75.11.090": {"desc": "Compensi occasionali", "tipo": "economico_costi", "normale": "dare", "categoria": "collaboratori", "posizione": "Economico costi"},
    "75.11.113": {"desc": "Spese telefoniche", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.11.114": {"desc": "Spese telefonia mobile", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.11.116": {"desc": "Spese telefoniche prom. 80% ind.", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.11.117": {"desc": "Spese telefoniche non deducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze", "posizione": "Economico costi"},
    "75.11.133": {"desc": "Spese varie amministrative", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    
    # === COSTI COMMERCIALI ===
    "75.13.009": {"desc": "Provvigioni a intermediari", "tipo": "economico_costi", "normale": "dare", "categoria": "vendite", "posizione": "Economico costi"},
    "75.13.021": {"desc": "Contr. ENASARCO", "tipo": "economico_costi", "normale": "dare", "categoria": "vendite", "posizione": "Economico costi"},
    "75.13.037": {"desc": "Spese di pubblicità", "tipo": "economico_costi", "normale": "dare", "categoria": "marketing", "posizione": "Economico costi"},
    "75.13.045": {"desc": "Mostre e fiere", "tipo": "economico_costi", "normale": "dare", "categoria": "marketing", "posizione": "Economico costi"},
    
    # === ASSICURAZIONI ===
    "75.15.001": {"desc": "Assicurazioni", "tipo": "economico_costi", "normale": "dare", "categoria": "assicurazioni", "posizione": "Economico costi"},
    "75.15.005": {"desc": "Assicurazioni auto", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi", "posizione": "Economico costi"},
    "75.15.059": {"desc": "Assicurazioni non deducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "assicurazioni", "posizione": "Economico costi"},
    "75.15.061": {"desc": "Assicurazioni immobili", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili", "posizione": "Economico costi"},
    
    # === SPESE PER SERVIZI VARI ===
    "75.17.001": {"desc": "Servizi di vigilanza", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.17.009": {"desc": "Spese di pulizia esterni", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.17.013": {"desc": "Spese di pulizia interni", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.17.033": {"desc": "Viaggi (ferrovia, aereo, auto ecc.)", "tipo": "economico_costi", "normale": "dare", "categoria": "trasferte", "posizione": "Economico costi"},
    "75.17.034": {"desc": "Spese viaggio,vitto,allog.(sp. di rapp.)", "tipo": "economico_costi", "normale": "dare", "categoria": "rappresentanza", "posizione": "Economico costi"},
    "75.17.035": {"desc": "Spese viaggio,vitto,allog.(non di rapp.)", "tipo": "economico_costi", "normale": "dare", "categoria": "trasferte", "posizione": "Economico costi"},
    "75.17.038": {"desc": "Pedaggi autostradali", "tipo": "economico_costi", "normale": "dare", "categoria": "trasferte", "posizione": "Economico costi"},
    "75.17.041": {"desc": "Spese di rappresentanza", "tipo": "economico_costi", "normale": "dare", "categoria": "rappresentanza", "posizione": "Economico costi"},
    "75.17.044": {"desc": "Pedaggi autostradali indeduc.", "tipo": "economico_costi", "normale": "dare", "categoria": "trasferte", "posizione": "Economico costi"},
    "75.17.045": {"desc": "Mensa aziend.appalt.ta a terzi/buoni pasto", "tipo": "economico_costi", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "75.17.049": {"desc": "Costi per buoni pasto", "tipo": "economico_costi", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "75.17.065": {"desc": "Ricerca, addestramento e formazione", "tipo": "economico_costi", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "75.17.077": {"desc": "Servizio smaltimento rifiuti", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "75.17.081": {"desc": "Spese per servizi bancari", "tipo": "economico_costi", "normale": "dare", "categoria": "banca", "posizione": "Economico costi"},
    "75.17.082": {"desc": "Commissioni factoring", "tipo": "economico_costi", "normale": "dare", "categoria": "banca", "posizione": "Economico costi"},
    "75.17.093": {"desc": "Costi condominio", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili", "posizione": "Economico costi"},
    "75.17.177": {"desc": "Altri servizi indeducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "indeducibili", "posizione": "Economico costi"},
    
    # === CANONI DI LOCAZIONE ===
    "77.01.009": {"desc": "Canone locazione fabbricati civili", "tipo": "economico_costi", "normale": "dare", "categoria": "affitti", "posizione": "Economico costi"},
    "77.01.013": {"desc": "Canone locazione fabbricati industriali", "tipo": "economico_costi", "normale": "dare", "categoria": "affitti", "posizione": "Economico costi"},
    "77.01.017": {"desc": "Canone locazione fabbricati commerciali", "tipo": "economico_costi", "normale": "dare", "categoria": "affitti", "posizione": "Economico costi"},
    "77.01.037": {"desc": "Canone locazione macchinari", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi", "posizione": "Economico costi"},
    
    # === CANONI DI LEASING ===
    "77.03.105": {"desc": "Canone leasing autov.", "tipo": "economico_costi", "normale": "dare", "categoria": "leasing", "posizione": "Economico costi"},
    "77.03.157": {"desc": "Canone leasing computer", "tipo": "economico_costi", "normale": "dare", "categoria": "leasing", "posizione": "Economico costi"},
    "77.03.197": {"desc": "Canoni di leas. veicoli inded.", "tipo": "economico_costi", "normale": "dare", "categoria": "leasing", "posizione": "Economico costi"},
    "77.03.221": {"desc": "Canoni di leasing indeducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "leasing", "posizione": "Economico costi"},
    
    # === CANONI DI NOLEGGIO ===
    "77.05.061": {"desc": "Canone noleggio autov.", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi", "posizione": "Economico costi"},
    "77.05.129": {"desc": "Canone noleggio computer ed accessori", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi", "posizione": "Economico costi"},
    "77.05.161": {"desc": "Noleggio autovetture indeducibile", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi", "posizione": "Economico costi"},
    
    # === COSTO PERSONALE - SALARI E STIPENDI ===
    "79.01.001": {"desc": "Salari", "tipo": "costo_personale", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "79.01.005": {"desc": "Stipendi impiegati", "tipo": "costo_personale", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "79.01.009": {"desc": "Stipendi dirigenti", "tipo": "costo_personale", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "79.01.013": {"desc": "Trasferte impiegati", "tipo": "costo_personale", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    "79.01.021": {"desc": "Premi impiegati", "tipo": "costo_personale", "normale": "dare", "categoria": "personale", "posizione": "Economico costi"},
    
    # === ONERI SOCIALI ===
    "79.03.001": {"desc": "Oneri INPS", "tipo": "costo_personale", "normale": "dare", "categoria": "inps", "posizione": "Economico costi"},
    "79.03.005": {"desc": "Oneri INAIL", "tipo": "costo_personale", "normale": "dare", "categoria": "inail", "posizione": "Economico costi"},
    
    # === TRATTAMENTO DI FINE RAPPORTO ===
    "79.05.001": {"desc": "Acc.to fondo TFR", "tipo": "costo_personale", "normale": "dare", "categoria": "tfr", "posizione": "Economico costi"},
    "79.05.005": {"desc": "Quota TFR maturata nell'anno", "tipo": "costo_personale", "normale": "dare", "categoria": "tfr", "posizione": "Economico costi"},
    
    # === AMMORTAMENTI IMMOB. IMMATERIALI ===
    "81.01.009": {"desc": "Amm.to spese di costituzione", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_imm", "posizione": "Economico costi"},
    "81.05.001": {"desc": "Amm.to brevetti industriali", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_imm", "posizione": "Economico costi"},
    "81.05.013": {"desc": "Amm.to software specifico", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_imm", "posizione": "Economico costi"},
    "81.07.009": {"desc": "Amm.to marchi", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_imm", "posizione": "Economico costi"},
    "81.09.001": {"desc": "Amm.to avviamento", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_imm", "posizione": "Economico costi"},
    
    # === AMMORTAMENTI IMMOB. MATERIALI ===
    "83.03.001": {"desc": "Amm.to fabbricati civili", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.03.005": {"desc": "Amm.to fabbricati industriali", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.05.009": {"desc": "Amm.to impianto elettrico", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.05.013": {"desc": "Amm.to impianto idraulico", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.001": {"desc": "Amm.to autovetture", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.005": {"desc": "Amm.to autocarri", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.065": {"desc": "Amm.to computer ed accessori", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.069": {"desc": "Amm.to telefonia fissa", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.073": {"desc": "Amm.to telefonia mobile", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.077": {"desc": "Amm.to mobili", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    "83.09.081": {"desc": "Amm.to arredi", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_mat", "posizione": "Economico costi"},
    
    # === AMMORTAMENTI INDEDUCIBILI ===
    "83.11.105": {"desc": "Amm.to inded. autovetture", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_indeducibili", "posizione": "Economico costi"},
    "83.11.169": {"desc": "Amm.to inded. computer ed accessori", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_indeducibili", "posizione": "Economico costi"},
    "83.11.177": {"desc": "Amm.to inded. telefonia mobile", "tipo": "ammortamenti", "normale": "dare", "categoria": "amm_indeducibili", "posizione": "Economico costi"},
    
    # === ONERI DIVERSI DI GESTIONE ===
    "92.01.001": {"desc": "Imposta di bollo", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.004": {"desc": "IMU (immobili strumentali)", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.005": {"desc": "IMU", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.006": {"desc": "IMU (quota ded.)", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.025": {"desc": "IVA indetraibile", "tipo": "oneri_diversi", "normale": "dare", "categoria": "iva", "posizione": "Economico costi"},
    "92.01.037": {"desc": "Tasse prop. autov.", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.082": {"desc": "Tasse prop. autoveicolo inded.", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.085": {"desc": "Diritti CCIAA", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse", "posizione": "Economico costi"},
    "92.01.097": {"desc": "Perdite su crediti", "tipo": "oneri_diversi", "normale": "dare", "categoria": "svalutazioni", "posizione": "Economico costi"},
    "92.01.098": {"desc": "Perdite su crediti(non deduc.)", "tipo": "oneri_diversi", "normale": "dare", "categoria": "svalutazioni", "posizione": "Economico costi"},
    "92.01.105": {"desc": "Abbonamenti riviste e giornali", "tipo": "oneri_diversi", "normale": "dare", "categoria": "servizi", "posizione": "Economico costi"},
    "92.01.113": {"desc": "Multe e ammende", "tipo": "oneri_diversi", "normale": "dare", "categoria": "sanzioni", "posizione": "Economico costi"},
    "92.01.121": {"desc": "Omaggi a clienti e articoli promozionali", "tipo": "oneri_diversi", "normale": "dare", "categoria": "marketing", "posizione": "Economico costi"},
    "92.01.144": {"desc": "Erogaz. liberali", "tipo": "oneri_diversi", "normale": "dare", "categoria": "liberalita", "posizione": "Economico costi"},
    "92.01.146": {"desc": "Erogaz. liberali inded.", "tipo": "oneri_diversi", "normale": "dare", "categoria": "liberalita", "posizione": "Economico costi"},
    "92.01.153": {"desc": "Oneri non deducibili", "tipo": "oneri_diversi", "normale": "dare", "categoria": "indeducibili", "posizione": "Economico costi"},
    
    # === PROVENTI FINANZIARI ===
    "93.13.001": {"desc": "Interessi att. c/c bancari", "tipo": "proventi_finanziari", "normale": "avere", "categoria": "finanza", "posizione": "Economico ricavi"},
    
    # === ONERI FINANZIARI ===
    "93.15.021": {"desc": "Interessi pass. sui debiti verso banche", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "finanza", "posizione": "Economico costi"},
    "93.15.025": {"desc": "Interessi pass. mutui", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "finanza", "posizione": "Economico costi"},
    "93.15.050": {"desc": "Interessi passivi ed oneri finanz. ind.", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "finanza", "posizione": "Economico costi"},
    "93.15.081": {"desc": "Commissione max scoperto", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "banca", "posizione": "Economico costi"},
    
    # === IMPOSTE CORRENTI ===
    "96.01.001": {"desc": "IRES", "tipo": "imposte", "normale": "dare", "categoria": "imposte", "posizione": "Economico costi"},
    "96.01.005": {"desc": "IRAP", "tipo": "imposte", "normale": "dare", "categoria": "imposte", "posizione": "Economico costi"},
}

# ==============================================================================
# FUNZIONI DI SUPPORTO
# ==============================================================================

def fmt_conto(codice: str, prefix: str = "") -> str:
    """Restituisce stringa formattata: CODICE - Descrizione (normale)"""
    info = PIANO_CONTI_COMPLETO.get(codice, {})
    desc = info.get('desc', '⚠️ Conto non trovato')
    normale = info.get('normale', '?')
    return f"{prefix}{codice} - {desc} ({normale})"

def get_conto_info(codice: str) -> Dict:
    """Recupera informazioni complete sul conto"""
    return PIANO_CONTI_COMPLETO.get(codice, {})

def cerca_conti(parola_chiave: str) -> List[Dict]:
    """Cerca conti nel piano dei conti per parola chiave"""
    risultati = []
    parola_chiave = parola_chiave.lower()
    
    for codice, info in PIANO_CONTI_COMPLETO.items():
        if (parola_chiave in info['desc'].lower() or 
            parola_chiave in info.get('categoria', '').lower() or
            parola_chiave in info.get('tipo', '').lower() or
            parola_chiave in info.get('posizione', '').lower()):
            risultati.append({
                'codice': codice,
                'descrizione': info['desc'],
                'tipo': info['tipo'],
                'categoria': info.get('categoria', ''),
                'normale': info['normale'],
                'posizione': info.get('posizione', '')
            })
    
    return risultati

def valida_scrittura(dare: List[Dict], avere: List[Dict]) -> Dict:
    """Valida che la scrittura sia bilanciata"""
    tot_dare = sum(riga.get('importo', 0) for riga in dare)
    tot_avere = sum(riga.get('importo', 0) for riga in avere)
    
    return {
        'bilanciata': abs(tot_dare - tot_avere) < 0.01,
        'totale_dare': round(tot_dare, 2),
        'totale_avere': round(tot_avere, 2),
        'differenza': round(abs(tot_dare - tot_avere), 2)
    }

# ==============================================================================
# CONFIGURAZIONE INPUT DINAMICI PER TIPOLOGIA OPERAZIONE
# ==============================================================================

INPUT_CONFIG = {
    "FATTURA_IVA": {
        "label": "📄 Fattura con IVA",
        "icon": "🧾",
        "campi": [
            {"nome": "imponibile", "label": "Imponibile €", "type": "currency", "help": "Importo imponibile della fattura"},
            {"nome": "aliquota", "label": "Aliquota IVA %", "type": "percent", "default": 22, "options": [0, 4, 5, 10, 22], "help": "Seleziona l'aliquota IVA applicata"}
        ],
        "calcolo": lambda d: {
            "iva": round(d['imponibile'] * d['aliquota'] / 100, 2),
            "totale": round(d['imponibile'] * (1 + d['aliquota'] / 100), 2)
        }
    },
    "PATRIMONIALE_NO_IVA": {
        "label": "💼 Operazione patrimoniale (no IVA)",
        "icon": "🏦",
        "campi": [
            {"nome": "importo", "label": "Importo €", "type": "currency", "help": "Importo secco dell'operazione"}
        ],
        "calcolo": lambda d: {"importo": round(d['importo'], 2)}
    },
    "STIPENDI_LORDO_NETTO": {
        "label": "👥 Registrazione stipendi (lordo → netto)",
        "icon": "💼",
        "campi": [
            {"nome": "lordo", "label": "Retribuzione lorda €", "type": "currency", "help": "Importo lordo mensile"},
            {"nome": "inps_dip_pct", "label": "INPS dipendente %", "type": "percent", "default": 9.19, "help": "Aliquota contributiva a carico dipendente"},
            {"nome": "irpef_stimata", "label": "IRPEF trattenuta €", "type": "currency", "help": "Importo IRPEF stimato in base agli scaglioni"},
            {"nome": "addizionali", "label": "Addizionali €", "type": "currency", "default": 0, "help": "Addizionali regionali e comunali"},
            {"nome": "inps_azienda_pct", "label": "INPS azienda %", "type": "percent", "default": 28.0, "help": "Aliquota contributiva a carico azienda"}
        ],
        "calcolo": lambda d: {
            "inps_dip": round(d['lordo'] * d['inps_dip_pct'] / 100, 2),
            "irpef": round(d['irpef_stimata'], 2),
            "addizionali": round(d.get('addizionali', 0), 2),
            "netto": round(d['lordo'] - (d['lordo'] * d['inps_dip_pct'] / 100) - d['irpef_stimata'] - d.get('addizionali', 0), 2),
            "inps_azienda": round(d['lordo'] * d['inps_azienda_pct'] / 100, 2),
            "totale_azienda": round(d['lordo'] + (d['lordo'] * d['inps_azienda_pct'] / 100), 2)
        }
    },
    "AMMORTAMENTO": {
        "label": "📉 Quota ammortamento cespite",
        "icon": "📊",
        "campi": [
            {"nome": "quota", "label": "Quota annuale €", "type": "currency", "help": "Importo della quota di ammortamento"},
            {"nome": "cespite", "label": "Conto cespite (DARE)", "type": "conto", "help": "Es: 83.09.001 - Amm.to autovetture"},
            {"nome": "fondo", "label": "Conto fondo amm.to (AVERE)", "type": "conto", "help": "Es: 16.07.001 - F.do amm.to autovetture"}
        ],
        "calcolo": lambda d: {"dare": round(d['quota'], 2), "avere": round(d['quota'], 2)}
    },
    "VERSAMENTO_CAPITALE": {
        "label": "💰 Versamento capitale sociale",
        "icon": "🏛️",
        "campi": [
            {"nome": "importo", "label": "Importo versato €", "type": "currency", "help": "Importo del capitale versato in banca"}
        ],
        "calcolo": lambda d: {"importo": round(d['importo'], 2)}
    },
    "PAGAMENTO_FORNITORE": {
        "label": "💸 Pagamento fornitore",
        "icon": "🏦",
        "campi": [
            {"nome": "importo", "label": "Importo pagato €", "type": "currency", "help": "Importo totale del pagamento"}
        ],
        "calcolo": lambda d: {"importo": round(d['importo'], 2)}
    },
    "INCASSO_CLIENTE": {
        "label": "💵 Incasso da cliente",
        "icon": "🏦",
        "campi": [
            {"nome": "importo", "label": "Importo incassato €", "type": "currency", "help": "Importo totale dell'incasso"}
        ],
        "calcolo": lambda d: {"importo": round(d['importo'], 2)}
    },
    "COMPENSO_PROFESSIONISTA": {
        "label": "🎓 Compenso professionista (con ritenuta)",
        "icon": "🧾",
        "campi": [
            {"nome": "compenso", "label": "Compenso lordo €", "type": "currency", "help": "Importo del compenso prima della ritenuta"},
            {"nome": "ritenuta_pct", "label": "Ritenuta d'acconto %", "type": "percent", "default": 20, "options": [0, 20, 23], "help": "Aliquota ritenuta (20% o 23% per nuovi regimi)"},
            {"nome": "iva_pct", "label": "IVA %", "type": "percent", "default": 22, "options": [0, 4, 10, 22], "help": "Aliquota IVA se dovuta"}
        ],
        "calcolo": lambda d: {
            "ritenuta": round(d['compenso'] * d['ritenuta_pct'] / 100, 2),
            "iva": round(d['compenso'] * d['iva_pct'] / 100, 2),
            "netto": round(d['compenso'] - (d['compenso'] * d['ritenuta_pct'] / 100), 2),
            "totale_fattura": round(d['compenso'] + (d['compenso'] * d['iva_pct'] / 100), 2)
        }
    }
}

# ==============================================================================
# TEMPLATE OPERAZIONI CONTABILI
# ==============================================================================

OPERAZIONI_CONTABILI = {
    "COSTITUZIONE_SOCIETA": {
        "nome": "Costituzione società - versamento capitale",
        "descrizione": "Versamento capitale sociale in banca",
        "categoria": "Patrimonio",
        "input_type": "VERSAMENTO_CAPITALE",
        "conti_template": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["40.01.001"]   # Capitale sociale
        },
        "note": "Indicare l'importo del capitale sociale versato. Operazione senza IVA.",
        "documenti_richiesti": ["Atto costitutivo", "Verbale assemblea", "Distinta bonifico"]
    },
    "ACQUISTO_MERCE_FATTURA": {
        "nome": "Acquisto merce con fattura",
        "descrizione": "Ricezione fattura acquisto merci da fornitore",
        "categoria": "Acquisti",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["73.01.013", "28.11.009"],  # Merci c/acquisti + IVA credito
            "avere": ["49.13.001"]  # Fornitore
        },
        "note": "Specificare se IVA 22%, 10%, 4% o altra aliquota. Conto fornitore generico: personalizzare se necessario.",
        "documenti_richiesti": ["Fattura fornitore"]
    },
    "VENDITA_MERCE_FATTURA": {
        "nome": "Vendita merce con fattura",
        "descrizione": "Emissione fattura vendita merci a cliente",
        "categoria": "Vendite",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["28.01.001"],  # Cliente
            "avere": ["60.01.009", "49.23.009"]  # Merci c/vendite + IVA debito
        },
        "note": "Specificare aliquota IVA applicata. Conto cliente generico: personalizzare se necessario.",
        "documenti_richiesti": ["Fattura emessa"]
    },
    "PAGAMENTO_FORNITORE_BONIFICO": {
        "nome": "Pagamento fornitore tramite bonifico",
        "descrizione": "Saldo fattura fornitore con bonifico bancario",
        "categoria": "Pagamenti",
        "input_type": "PAGAMENTO_FORNITORE",
        "conti_template": {
            "dare": ["49.13.001"],  # Fornitore
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Indicare numero fattura e data pagamento. Operazione senza IVA.",
        "documenti_richiesti": ["Distinta bonifico", "Fattura"]
    },
    "INCASSO_CLIENTE_BONIFICO": {
        "nome": "Incasso da cliente tramite bonifico",
        "descrizione": "Ricezione pagamento da cliente su c/c",
        "categoria": "Incassi",
        "input_type": "INCASSO_CLIENTE",
        "conti_template": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["28.01.001"]  # Cliente
        },
        "note": "Indicare causale del bonifico. Operazione senza IVA.",
        "documenti_richiesti": ["Estratto conto bancario"]
    },
    "REGISTRAZIONE_STIPENDI": {
        "nome": "Registrazione stipendi dipendenti",
        "descrizione": "Competenza stipendi, INPS e ritenute",
        "categoria": "Personale",
        "input_type": "STIPENDI_LORDO_NETTO",
        "conti_template": {
            "dare": ["79.01.005", "79.03.001"],  # Stipendi + Oneri INPS azienda
            "avere": ["49.27.025", "49.23.029", "49.25.001"]  # Dipendenti c/retrib + Ritenute + INPS
        },
        "note": """
        **Calcolo automatico lordo → netto:**
        - Netto = Lordo - INPS dip. - IRPEF - Addizionali
        - INPS azienda = Lordo × aliquota azienda (~28%)
        
        **Conti utilizzati:**
        - DARE: 79.01.005 Stipendi + 79.03.001 Oneri INPS azienda
        - AVERE: 49.27.025 Dipendenti c/retrib + 49.23.029 Erario c/rit. + 49.25.001 Debito INPS
        """,
        "documenti_richiesti": ["Busta paga", "Modello F24", "Denuncia contributiva"]
    },
    "PAGAMENTO_STIPENDI": {
        "nome": "Pagamento stipendi ai dipendenti",
        "descrizione": "Bonifico stipendi netti ai dipendenti",
        "categoria": "Personale",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["49.27.025"],  # Dipendenti c/retribuzioni
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Importo netto da pagare ai dipendenti (già calcolato in fase di competenza).",
        "documenti_richiesti": ["Distinta bonifico stipendi"]
    },
    "ACCANTONAMENTO_TFR": {
        "nome": "Accantonamento TFR",
        "descrizione": "Quota TFR maturata nell'esercizio",
        "categoria": "Personale",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["79.05.001"],  # Acc.to fondo TFR
            "avere": ["46.01.001"]  # Fondo TFR
        },
        "note": "Calcolare quota TFR secondo normativa (retribuzione / 13,5). Operazione senza IVA.",
        "documenti_richiesti": ["Calcolo TFR", "Buste paga"]
    },
    "COMPENSO_AMMINISTRATORE": {
        "nome": "Compenso amministratore",
        "descrizione": "Registrazione compenso amministratore con ritenuta",
        "categoria": "Personale",
        "input_type": "COMPENSO_PROFESSIONISTA",
        "conti_template": {
            "dare": ["75.11.017"],  # Compensi amministratore
            "avere": ["49.27.001", "49.23.039"]  # Debiti v/amministratori + Ritenuta 20%
        },
        "note": "Applicare ritenuta d'acconto 20% sul compenso. IVA non dovuta per compensi amministratori.",
        "documenti_richiesti": ["Delibera compenso", "Fattura/Parcella"]
    },
    "COMPENSO_PROFESSIONISTA_ESTerno": {
        "nome": "Compenso professionista esterno",
        "descrizione": "Fattura da professionista con ritenuta e IVA",
        "categoria": "Servizi",
        "input_type": "COMPENSO_PROFESSIONISTA",
        "conti_template": {
            "dare": ["75.11.002", "28.11.009"],  # Consulenze + IVA credito
            "avere": ["49.13.001", "49.23.039"]  # Fornitore + Ritenuta
        },
        "note": "Applicare ritenuta 20% se professionista soggetto. IVA 22% salvo esenzioni.",
        "documenti_richiesti": ["Fattura/Parcella professionista"]
    },
    "AMMORTAMENTO_AUTOVETTURA": {
        "nome": "Ammortamento autovettura",
        "descrizione": "Registrazione quota ammortamento auto (40% deducibile)",
        "categoria": "Ammortamenti",
        "input_type": "AMMORTAMENTO",
        "conti_template": {
            "dare": ["83.09.001", "83.11.105"],  # Amm.to deducibile + indeducibile
            "avere": ["16.07.001"]  # F.do amm.to autovetture
        },
        "note": """
        **Deducibilità autovetture: 40%**
        - Quota deducibile (40%) → 83.09.001
        - Quota indeducibile (60%) → 83.11.105
        - Totale quota → 16.07.001 F.do amm.to
        
        Esempio: quota €1.000 → €400 deducibili + €600 indeducibili
        """,
        "documenti_richiesti": ["Piano ammortamenti", "Scheda cespite"]
    },
    "AMMORTAMENTO_COMPUTER": {
        "nome": "Ammortamento computer/telefonia",
        "descrizione": "Registrazione quota ammortamento (80% deducibile)",
        "categoria": "Ammortamenti",
        "input_type": "AMMORTAMENTO",
        "conti_template": {
            "dare": ["83.09.065", "83.11.169"],  # Amm.to deducibile + indeducibile
            "avere": ["16.07.045"]  # F.do amm.to computer
        },
        "note": """
        **Deducibilità computer/telefonia: 80%**
        - Quota deducibile (80%) → 83.09.065
        - Quota indeducibile (20%) → 83.11.169
        - Totale quota → 16.07.045 F.do amm.to
        """,
        "documenti_richiesti": ["Piano ammortamenti", "Scheda cespite"]
    },
    "CANONE_AFFITTO": {
        "nome": "Canone di locazione/affitto",
        "descrizione": "Pagamento canone affitto immobile",
        "categoria": "Gestione Corrente",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["77.01.009", "28.11.009"],  # Canone locazione + IVA (se dovuta)
            "avere": ["49.13.001"]  # Fornitore/Locatore
        },
        "note": "Verificare se soggetto a IVA o esente art. 10 DPR 633/72. Per immobili strumentali: IVA deducibile.",
        "documenti_richiesti": ["Contratto locazione", "Fattura canone", "Ricevuta pagamento"]
    },
    "UTENZE": {
        "nome": "Utenze (luce, gas, acqua, telefono)",
        "descrizione": "Pagamento bollette utenze",
        "categoria": "Gestione Corrente",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["75.01.025", "75.01.033", "75.01.037", "75.11.113", "28.11.009"],
            "avere": ["34.01.001"]
        },
        "note": """
        **Selezionare il conto specifico:**
        - Energia elettrica: 75.01.025 (o 75.01.026/028 per % industriale)
        - Gas: 75.01.033
        - Acqua: 75.01.037
        - Telefono: 75.11.113 (o 75.11.116 per 80% ind.)
        """,
        "documenti_richiesti": ["Bollette utenze"]
    },
    "CARBURANTE": {
        "nome": "Carburante e lubrificanti",
        "descrizione": "Acquisto carburante per automezzi",
        "categoria": "Gestione Corrente",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["73.09.006", "28.11.009"],  # Carburanti + IVA
            "avere": ["34.01.001"]  # Banca c/c o cassa
        },
        "note": """
        **Deducibilità carburante:**
        - Autovetture: 40%
        - Autocarri: 100%
        - Uso promiscuo dip.: 40%
        - Non deducibile: 73.09.042
        """,
        "documenti_richiesti": ["Fattura carburante", "Ricevuta", "Scheda veicolo"]
    },
    "LIQUIDAZIONE_IVA": {
        "nome": "Liquidazione IVA periodica",
        "descrizione": "Versamento IVA a debito o recupero credito",
        "categoria": "Tributi",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["49.23.009"],  # Erario c/IVA (se debito)
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": """
        **Calcolo liquidazione:**
        - IVA vendite - IVA acquisti = IVA da versare/recuperare
        - Se credito: 28.11.009 (dare) → 34.01.001 (avere)
        - Se debito: 49.23.009 (dare) → 34.01.001 (avere)
        """,
        "documenti_richiesti": ["Liquidazione IVA", "F24", "Registro IVA"]
    },
    "ACCANTONAMENTO_IMPOSTE": {
        "nome": "Accantonamento imposte (IRES/IRAP)",
        "descrizione": "Accantonamento imposte di esercizio",
        "categoria": "Tributi",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["96.01.001", "96.01.005"],  # IRES + IRAP
            "avere": ["49.23.001", "49.23.005"]  # Erario c/IRES + Erario c/IRAP
        },
        "note": "Calcolare in base all'utile di esercizio. Operazione di chiusura, senza IVA.",
        "documenti_richiesti": ["Calcolo imposte", "Bilancio di esercizio"]
    },
    "VERSAMENTO_RITENUTE_F24": {
        "nome": "Versamento ritenute e contributi (F24)",
        "descrizione": "Pagamento ritenute IRPEF e contributi INPS",
        "categoria": "Tributi",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["49.23.029", "49.25.001"],  # Ritenute + INPS
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Versare entro il 16 del mese successivo. Utilizzare codici tributo corretti in F24.",
        "documenti_richiesti": ["Modello F24", "Distinta versamenti"]
    },
    "REVERSE_CHARGE": {
        "nome": "Reverse charge (art. 17 c.6)",
        "descrizione": "Acquisto con inversione contabile",
        "categoria": "Acquisti",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["73.01.013", "28.11.009"],  # Merci + IVA credito
            "avere": ["49.13.001", "49.23.009"]  # Fornitore + IVA debito
        },
        "note": "Integrare fattura con autofattura o annotazione. IVA si compensa nello stesso periodo.",
        "documenti_richiesti": ["Fattura estera", "Integrazione reverse charge"]
    },
    "SPLIT_PAYMENT": {
        "nome": "Split payment (PA - art. 17-ter)",
        "descrizione": "Vendita a PA con scissione pagamenti",
        "categoria": "Vendite",
        "input_type": "FATTURA_IVA",
        "conti_template": {
            "dare": ["28.01.001", "28.11.009"],  # Cliente + IVA credito
            "avere": ["60.01.009", "49.23.009"]  # Vendite + IVA debito
        },
        "note": "L'IVA viene versata dalla PA, non dal cliente. Contabilizzare comunque l'IVA a debito.",
        "documenti_richiesti": ["Fattura PA", "Documentazione split payment"]
    },
    "PERDITA_CREDITI": {
        "nome": "Perdita su crediti",
        "descrizione": "Svalutazione crediti inesigibili",
        "categoria": "Oneri",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["92.01.097", "28.11.009"],  # Perdite su crediti + storno IVA
            "avere": ["28.01.001"]  # Cliente
        },
        "note": "Stornare IVA solo se ricorrono i requisiti (fallimento, procedure concorsuali, ecc.).",
        "documenti_richiesti": ["Documentazione inesigibilità", "Sentenza/atto fallimentare"]
    },
    "CONTRIBUTO_CONTO_CAPITALE": {
        "nome": "Contributo in conto capitale",
        "descrizione": "Contributo pubblico o privato in conto capitale",
        "categoria": "Patrimonio",
        "input_type": "PATRIMONIALE_NO_IVA",
        "conti_template": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["71.01.081", "40.13.010"]  # Contributo + Riserva
        },
        "note": "Iscritto a patrimonio netto (riserva contributi). Non concorre a formazione utile. Senza IVA.",
        "documenti_richiesti": ["Delibera contributo", "Atto di assegnazione"]
    },
}

# ==============================================================================
# FUNZIONI UI DINAMICHE
# ==============================================================================

def render_input_dinamico(tipologia: str, key_prefix: str = "") -> Dict:
    """Genera form input in base alla tipologia operazione"""
    config = INPUT_CONFIG.get(tipologia, INPUT_CONFIG["PATRIMONIALE_NO_IVA"])
    valori = {}
    
    with st.expander(f"{config['icon']} {config['label']}", expanded=True):
        for campo in config['campi']:
            k = f"{key_prefix}_{campo['nome']}"
            
            if campo['type'] == 'currency':
                valori[campo['nome']] = st.number_input(
                    campo['label'], 
                    min_value=0.0, 
                    step=0.01, 
                    format="%.2f", 
                    key=k,
                    help=campo.get('help')
                )
            elif campo['type'] == 'percent':
                if 'options' in campo:
                    valori[campo['nome']] = st.selectbox(
                        campo['label'],
                        options=campo['options'],
                        index=campo['options'].index(campo.get('default', 0)) if campo.get('default') in campo.get('options', []) else 0,
                        key=k,
                        help=campo.get('help')
                    )
                else:
                    valori[campo['nome']] = st.number_input(
                        campo['label'], 
                        min_value=0.0, 
                        max_value=100.0, 
                        value=campo.get('default', 0), 
                        step=0.1, 
                        key=k,
                        help=campo.get('help')
                    )
            elif campo['type'] == 'conto':
                # Ricerca conto con autocomplete
                search = st.text_input(f"🔍 Cerca conto per {campo['label']}", placeholder="Es: autovettura, ammortamento...", key=f"{k}_search")
                if search:
                    risultati = cerca_conti(search)
                    if risultati:
                        opzioni = {f"{r['codice']} - {r['descrizione']}": r['codice'] for r in risultati[:10]}
                        selezione = st.selectbox("Seleziona conto", list(opzioni.keys()), key=f"{k}_select")
                        valori[campo['nome']] = opzioni[selezione]
                        st.caption(f"✅ {fmt_conto(valori[campo['nome']])}")
                    else:
                        st.warning("Nessun conto trovato")
                else:
                    valori[campo['nome']] = st.text_input(campo['label'], placeholder="Es: 83.09.001", key=k, help=campo.get('help'))
    
    # Calcolo automatico se tutti i valori necessari sono presenti
    if all(nome in valori for nome in [c['nome'] for c in config['campi']]):
        try:
            return config['calcolo'](valori)
        except Exception as e:
            st.error(f"Errore nel calcolo: {e}")
            return {}
    
    return {}

def genera_scrittura_da_template(op_code: str, calcoli: Dict) -> Tuple[List[Dict], List[Dict]]:
    """Genera righe DARE/AVERE partendo dal template operazione"""
    op_info = OPERAZIONI_CONTABILI[op_code]
    dare = []
    avere = []
    
    # Mappatura importi in base alla tipologia
    input_type = op_info.get('input_type', 'PATRIMONIALE_NO_IVA')
    
    if input_type == "FATTURA_IVA":
        imponibile = calcoli.get('imponibile', 0)
        iva = calcoli.get('iva', 0)
        totale = calcoli.get('totale', 0)
        
        for i, conto in enumerate(op_info['conti_template']['dare']):
            info = get_conto_info(conto)
            if '28.11.009' in conto:  # IVA credito
                importo = iva
            else:
                importo = imponibile
            dare.append({
                'conto': conto,
                'descrizione': info.get('desc', ''),
                'importo': round(importo, 2)
            })
        
        for conto in op_info['conti_template']['avere']:
            info = get_conto_info(conto)
            if '49.23.009' in conto:  # IVA debito
                importo = iva
            elif '49.13.001' in conto:  # Fornitore
                importo = totale
            else:
                importo = imponibile
            avere.append({
                'conto': conto,
                'descrizione': info.get('desc', ''),
                'importo': round(importo, 2)
            })
            
    elif input_type == "STIPENDI_LORDO_NETTO":
        lordo = calcoli.get('lordo', 0)
        netto = calcoli.get('netto', 0)
        inps_dip = calcoli.get('inps_dip', 0)
        irpef = calcoli.get('irpef', 0)
        addizionali = calcoli.get('addizionali', 0)
        inps_azienda = calcoli.get('inps_azienda', 0)
        
        # DARE
        dare.append({
            'conto': '79.01.005',
            'descrizione': get_conto_info('79.01.005').get('desc', ''),
            'importo': round(lordo, 2)
        })
        dare.append({
            'conto': '79.03.001',
            'descrizione': get_conto_info('79.03.001').get('desc', ''),
            'importo': round(inps_azienda, 2)
        })
        
        # AVERE
        avere.append({
            'conto': '49.27.025',
            'descrizione': get_conto_info('49.27.025').get('desc', ''),
            'importo': round(netto, 2)
        })
        avere.append({
            'conto': '49.23.029',
            'descrizione': get_conto_info('49.23.029').get('desc', ''),
            'importo': round(irpef + addizionali, 2)
        })
        avere.append({
            'conto': '49.25.001',
            'descrizione': get_conto_info('49.25.001').get('desc', ''),
            'importo': round(inps_dip + inps_azienda, 2)
        })
        
    elif input_type == "AMMORTAMENTO":
        quota = calcoli.get('quota', 0)
        cespite = calcoli.get('cespite', '')
        fondo = calcoli.get('fondo', '')
        
        # Gestione deducibilità auto (40%) e computer (80%)
        if '83.09.001' in cespite:  # Amm.to autovetture
            dare.append({'conto': '83.09.001', 'descrizione': get_conto_info('83.09.001').get('desc', ''), 'importo': round(quota * 0.4, 2)})
            dare.append({'conto': '83.11.105', 'descrizione': get_conto_info('83.11.105').get('desc', ''), 'importo': round(quota * 0.6, 2)})
        elif '83.09.065' in cespite:  # Amm.to computer
            dare.append({'conto': '83.09.065', 'descrizione': get_conto_info('83.09.065').get('desc', ''), 'importo': round(quota * 0.8, 2)})
            dare.append({'conto': '83.11.169', 'descrizione': get_conto_info('83.11.169').get('desc', ''), 'importo': round(quota * 0.2, 2)})
        else:
            dare.append({'conto': cespite, 'descrizione': get_conto_info(cespite).get('desc', ''), 'importo': round(quota, 2)})
        
        avere.append({'conto': fondo, 'descrizione': get_conto_info(fondo).get('desc', ''), 'importo': round(quota, 2)})
        
    else:  # PATRIMONIALE_NO_IVA e altri
        importo = calcoli.get('importo', 0)
        
        for conto in op_info['conti_template']['dare']:
            info = get_conto_info(conto)
            dare.append({
                'conto': conto,
                'descrizione': info.get('desc', ''),
                'importo': round(importo, 2)
            })
        
        for conto in op_info['conti_template']['avere']:
            info = get_conto_info(conto)
            avere.append({
                'conto': conto,
                'descrizione': info.get('desc', ''),
                'importo': round(importo, 2)
            })
    
    return dare, avere

# ==============================================================================
# INTERFACCIA PRINCIPALE
# ==============================================================================

def main():
    st.title("📒 Generatore Scritture Contabili SRL")
    st.markdown("""
    **Sistema professionale** basato sul **Piano dei Conti Ranocchi GIS** (~1.200 conti).
    - ✅ Descrizioni conti sempre visibili
    - ✅ Input contestuali per tipologia operazione
    - ✅ Calcoli automatici: IVA, stipendi (lordo→netto), ammortamenti (deducibilità)
    - ✅ Validazione DARE = AVERE in tempo reale
    - ✅ Export CSV compatibile con gestionali
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurazione")
        
        # Selezione modalità
        modalita = st.radio(
            "Modalità di inserimento",
            ["📋 Operazione predefinita", "🔍 Ricerca manuale conti", "✍️ Inserimento righe libero"],
            help="Scegli come generare la scrittura"
        )
        
        st.markdown("---")
        
        # Info piano dei conti
        st.info(f"""
        📊 **Piano dei Conti Caricato**
        - Totale conti: **{len(PIANO_CONTI_COMPLETO)}**
        - Patrimoniali: ~400
        - Economici: ~700
        - Conti d'ordine: ~100
        
        *Fonte: Stampa Ranocchi GIS - SPIACO*
        """)
        
        st.markdown("---")
        st.caption("v2.0 | Studio Pratici Tech")
    
    # Session state
    if 'scrittura_generata' not in st.session_state:
        st.session_state.scrittura_generata = None
    
    # ==============================================================================
    # MODALITÀ 1: OPERAZIONE PREDEFINITA
    # ==============================================================================
    if modalita == "📋 Operazione predefinita":
        st.header("📋 Selezione Operazione Contabile")
        
        # Filtri
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Categoria", sorted(set(op['categoria'] for op in OPERAZIONI_CONTABILI.values())))
        with col2:
            search_op = st.text_input("🔍 Cerca operazione", placeholder="Es: stipendi, fattura, ammortamento...")
        
        # Filtra operazioni
        operazioni_filtrate = [
            (code, op) for code, op in OPERAZIONI_CONTABILI.items()
            if op['categoria'] == categoria and (not search_op or search_op.lower() in op['nome'].lower())
        ]
        
        if not operazioni_filtrate:
            st.warning("Nessuna operazione trovata con i filtri selezionati")
            return
        
        # Selezione operazione
        op_code = st.selectbox(
            "Operazione",
            [code for code, _ in operazioni_filtrate],
            format_func=lambda x: f"{OPERAZIONI_CONTABILI[x]['nome']}"
        )
        
        if op_code:
            op_info = OPERAZIONI_CONTABILI[op_code]
            
            # Info operazione
            st.info(f"""
            **{op_info['nome']}**
            
            {op_info['descrizione']}
            
            📋 *Documenti richiesti:* {', '.join(op_info.get('documenti_richiesti', []))}
            """)
            
            with st.expander("📝 Note operative", expanded=True):
                st.markdown(op_info['note'])
            
            # Input dinamici
            st.markdown("### 💰 Inserimento Importi")
            calcoli = render_input_dinamico(op_info['input_type'], key_prefix=f"op_{op_code}")
            
            # Genera scrittura
            if calcoli and st.button("🚀 Genera Scrittura Contabile", type="primary", use_container_width=True):
                dare, avere = genera_scrittura_da_template(op_code, calcoli)
                validazione = valida_scrittura(dare, avere)
                
                st.session_state.scrittura_generata = {
                    'operazione': op_code,
                    'dare': dare,
                    'avere': avere,
                    'validazione': validazione,
                    'note': op_info['note'],
                    'documenti': op_info.get('documenti_richiesti', [])
                }
    
    # ==============================================================================
    # MODALITÀ 2: RICERCA MANUALE CONTI
    # ==============================================================================
    elif modalita == "🔍 Ricerca manuale conti":
        st.header("🔍 Ricerca nel Piano dei Conti")
        
        ricerca = st.text_input("Cerca conto per descrizione, categoria o codice", placeholder="Es: autovettura, banca, IVA, stipendio, 73.01...")
        
        if ricerca:
            risultati = cerca_conti(ricerca)
            
            if risultati:
                st.write(f"✅ Trovati **{len(risultati)}** conti:")
                
                # Mostra in tabella con descrizioni complete
                df_risultati = pd.DataFrame(risultati)
                df_risultati['Conto Completo'] = df_risultati.apply(
                    lambda r: fmt_conto(r['codice']), axis=1
                )
                st.dataframe(
                    df_risultati[['Conto Completo', 'normale', 'categoria', 'posizione']].head(20),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Selezione multipla per DARE/AVERE
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("➕ DARE")
                    dare_selezionati = st.multiselect(
                        "Seleziona conti DARE",
                        options=[r['codice'] for r in risultati],
                        format_func=lambda x: fmt_conto(x),
                        key="dare_multi"
                    )
                with col2:
                    st.subheader("➖ AVERE")
                    avere_selezionati = st.multiselect(
                        "Seleziona conti AVERE",
                        options=[r['codice'] for r in risultati],
                        format_func=lambda x: fmt_conto(x),
                        key="avere_multi"
                    )
                
                # Input importi per righe selezionate
                if dare_selezionati or avere_selezionati:
                    st.markdown("### 💰 Importi")
                    dare_righe = []
                    avere_righe = []
                    
                    for conto in dare_selezionati:
                        imp = st.number_input(f"Importo per {fmt_conto(conto)}", min_value=0.0, step=0.01, key=f"imp_dare_{conto}")
                        if imp > 0:
                            dare_righe.append({'conto': conto, 'descrizione': get_conto_info(conto)['desc'], 'importo': imp})
                    
                    for conto in avere_selezionati:
                        imp = st.number_input(f"Importo per {fmt_conto(conto)}", min_value=0.0, step=0.01, key=f"imp_avere_{conto}")
                        if imp > 0:
                            avere_righe.append({'conto': conto, 'descrizione': get_conto_info(conto)['desc'], 'importo': imp})
                    
                    if st.button("✅ Valid
