import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

st.set_page_config(page_title="Generatore Scritture Contabili SRL - Piano Ranocchi", layout="wide", page_icon="📒")

# ==============================================================================
# PIANO DEI CONTI RANOCCHI GIS COMPLETO ED ESPANSO
# ==============================================================================
PIANO_CONTI_COMPLETO = {
    # PATRIMONIALE ATTIVO - CREDITI VERSO SOCI
    "01.01.001": {"desc": "Soci c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "capitale"},
    "01.01.005": {"desc": "Soci a c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "capitale"},
    "01.01.009": {"desc": "Soci b c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "capitale"},
    "01.01.021": {"desc": "Soci c/decimi richiamati", "tipo": "patrimoniale_attivo", "normale": "dare", "categoria": "capitale"},
    
    # IMMOBILIZZAZIONI IMMATERIALI
    "04.01.001": {"desc": "Spese di impianto", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "costi_pluriennali"},
    "04.01.005": {"desc": "Spese di ampliamento", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "costi_pluriennali"},
    "04.01.009": {"desc": "Spese di costituzione", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "costi_pluriennali"},
    "04.01.013": {"desc": "Spese di fusione", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "costi_pluriennali"},
    "04.05.001": {"desc": "Brevetti industriali", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.05.005": {"desc": "Diritti d'autore", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.05.009": {"desc": "Know-how", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.05.013": {"desc": "Software specifico", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.07.001": {"desc": "Concessioni", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.07.005": {"desc": "Licenze", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.07.009": {"desc": "Marchi", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "diritti"},
    "04.09.001": {"desc": "Avviamento", "tipo": "immobilizzazioni_immateriali", "normale": "dare", "categoria": "avviamento"},
    
    # IMMOBILIZZAZIONI MATERIALI - FABBRICATI
    "13.03.001": {"desc": "Fabbricati civili", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "immobili"},
    "13.03.005": {"desc": "Fabbricati industriali", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "immobili"},
    "13.03.009": {"desc": "Fabbricati commerciali", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "immobili"},
    "13.05.009": {"desc": "Impianto elettrico", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "impianti"},
    "13.05.013": {"desc": "Impianto idraulico", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "impianti"},
    "13.05.017": {"desc": "Impianto telefonico", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "impianti"},
    "13.05.021": {"desc": "Impianto d'allarme", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "impianti"},
    "13.05.025": {"desc": "Impianto antincendio", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "impianti"},
    "13.07.001": {"desc": "Attrezzature industriali", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "attrezzature"},
    "13.07.005": {"desc": "Attrezzature commerciali", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "attrezzature"},
    "13.09.001": {"desc": "Autovetture", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "automezzi"},
    "13.09.005": {"desc": "Autocarri", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "automezzi"},
    "13.09.009": {"desc": "Motoveicoli", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "automezzi"},
    "13.09.065": {"desc": "Computer ed accessori", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "attrezzature"},
    "13.09.077": {"desc": "Mobili", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "arredi"},
    "13.09.081": {"desc": "Arredi", "tipo": "immobilizzazioni_materiali", "normale": "dare", "categoria": "arredi"},
    
    # FONDI AMMORTAMENTO
    "16.01.005": {"desc": "F.do amm.to fabbricati civili", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi"},
    "16.03.009": {"desc": "F.do amm.to impianto elettrico", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi"},
    "16.07.001": {"desc": "F.do amm.to autovetture", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi"},
    "16.07.045": {"desc": "F.do amm.to computer ed accessori", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi"},
    "16.07.057": {"desc": "F.do amm.to mobili", "tipo": "fondo_ammortamento", "normale": "avere", "categoria": "fondi"},
    
    # RIMANENZE
    "25.07.005": {"desc": "Merci", "tipo": "rimanenze", "normale": "dare", "categoria": "magazzino"},
    
    # CREDITI COMMERCIALI
    "28.01.001": {"desc": "Cliente", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti"},
    "28.01.005": {"desc": "Effetti attivi", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti"},
    "28.01.037": {"desc": "Fatture da emettere", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti"},
    "28.01.055": {"desc": "Carte di credito", "tipo": "crediti_commerciali", "normale": "dare", "categoria": "clienti"},
    
    # CREDITI TRIBUTARI
    "28.11.009": {"desc": "Credito IVA", "tipo": "crediti_tributari", "normale": "dare", "categoria": "iva"},
    "28.11.021": {"desc": "Erario c/acconto IRES", "tipo": "crediti_tributari", "normale": "dare", "categoria": "imposte"},
    "28.11.025": {"desc": "Erario c/acconto IRAP", "tipo": "crediti_tributari", "normale": "dare", "categoria": "imposte"},
    "28.11.029": {"desc": "Erario c/acconto IVA", "tipo": "crediti_tributari", "normale": "dare", "categoria": "iva"},
    "28.11.049": {"desc": "Erario c/rit. subite", "tipo": "crediti_tributari", "normale": "dare", "categoria": "ritenute"},
    "28.11.081": {"desc": "Credito IVA annuale a rimborso", "tipo": "crediti_tributari", "normale": "dare", "categoria": "iva"},
    
    # CREDITI VERSO ALTRI
    "28.15.045": {"desc": "Soci c/prelevamento", "tipo": "crediti_versaltri", "normale": "dare", "categoria": "soci"},
    "28.15.053": {"desc": "Dipendenti c/anticipi su retrib.", "tipo": "crediti_versaltri", "normale": "dare", "categoria": "personale"},
    "28.15.061": {"desc": "Dipendenti c/prestiti", "tipo": "crediti_versaltri", "normale": "dare", "categoria": "personale"},
    "28.15.069": {"desc": "Amministratori c/anticipi", "tipo": "crediti_versaltri", "normale": "dare", "categoria": "amministratori"},
    "28.15.085": {"desc": "Caparre a fornitori", "tipo": "crediti_versaltri", "normale": "dare", "categoria": "fornitori"},
    
    # LIQUIDITA'
    "34.01.001": {"desc": "Banca c/c A", "tipo": "liquidita", "normale": "dare", "categoria": "banca"},
    "34.01.005": {"desc": "Banca c/c B", "tipo": "liquidita", "normale": "dare", "categoria": "banca"},
    "34.01.009": {"desc": "Banca c/c C", "tipo": "liquidita", "normale": "dare", "categoria": "banca"},
    "34.01.045": {"desc": "Posta c/c", "tipo": "liquidita", "normale": "dare", "categoria": "banca"},
    "34.05.001": {"desc": "Cassa contanti", "tipo": "liquidita", "normale": "dare", "categoria": "cassa"},
    
    # PATRIMONIO NETTO
    "40.01.001": {"desc": "Capitale sociale", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "capitale"},
    "40.07.001": {"desc": "Riserva legale", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "riserve"},
    "40.13.010": {"desc": "Riserva contributi in conto capitale", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "riserve"},
    "40.15.001": {"desc": "Utile esercizi precedenti", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "riserve"},
    "40.17.001": {"desc": "Utile d'esercizio", "tipo": "patrimonio_netto", "normale": "avere", "categoria": "risultato"},
    "40.17.005": {"desc": "Perdita esercizio", "tipo": "patrimonio_netto", "normale": "dare", "categoria": "risultato"},
    
    # FONDI
    "46.01.001": {"desc": "Fondo T.F.R.", "tipo": "fondi", "normale": "avere", "categoria": "fondi"},
    
    # DEBITI COMMERCIALI
    "49.13.001": {"desc": "Fornitore", "tipo": "debiti_commerciali", "normale": "avere", "categoria": "fornitori"},
    "49.13.005": {"desc": "Fatture da ricevere", "tipo": "debiti_commerciali", "normale": "avere", "categoria": "fornitori"},
    "49.13.009": {"desc": "Rappresentanti c/provv. da liquidare", "tipo": "debiti_commerciali", "normale": "avere", "categoria": "fornitori"},
    
    # DEBITI TRIBUTARI
    "49.23.001": {"desc": "Erario c/IRES", "tipo": "debiti_tributari", "normale": "avere", "categoria": "imposte"},
    "49.23.005": {"desc": "Erario c/IRAP", "tipo": "debiti_tributari", "normale": "avere", "categoria": "imposte"},
    "49.23.009": {"desc": "Erario c/IVA", "tipo": "debiti_tributari", "normale": "avere", "categoria": "iva"},
    "49.23.029": {"desc": "Erario c/rit. fiscali lav. dipendenti", "tipo": "debiti_tributari", "normale": "avere", "categoria": "ritenute"},
    "49.23.033": {"desc": "Erario c/rit. fiscali collab. a progetto", "tipo": "debiti_tributari", "normale": "avere", "categoria": "ritenute"},
    "49.23.037": {"desc": "Erario c/rit. fiscali collab. occas.", "tipo": "debiti_tributari", "normale": "avere", "categoria": "ritenute"},
    "49.23.039": {"desc": "Erario c/rit. fiscali lav. autonomi", "tipo": "debiti_tributari", "normale": "avere", "categoria": "ritenute"},
    
    # DEBITI PREVIDENZIALI
    "49.25.001": {"desc": "Debito v/ INPS lavoro dipendente", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inps"},
    "49.25.003": {"desc": "Debito v/ INPS lavoro autonomo", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inps"},
    "49.25.005": {"desc": "Debito v/ INAIL", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inail"},
    "49.25.009": {"desc": "Debito v/ ENPDAI", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inps"},
    "49.25.013": {"desc": "Debito v/ ENASARCO", "tipo": "debiti_previdenziali", "normale": "avere", "categoria": "inps"},
    
    # DEBITI FINANZIARI
    "49.07.033": {"desc": "Mutuo ipotecario", "tipo": "debiti_finanziari", "normale": "avere", "categoria": "finanziamenti"},
    "49.07.037": {"desc": "Banca c/finanziamenti", "tipo": "debiti_finanziari", "normale": "avere", "categoria": "finanziamenti"},
    "49.07.039": {"desc": "Mutuo chirografario", "tipo": "debiti_finanziari", "normale": "avere", "categoria": "finanziamenti"},
    
    # DEBITI VERSO PERSONALE
    "49.27.001": {"desc": "Debiti v/amministratori", "tipo": "debiti_personale", "normale": "avere", "categoria": "amministratori"},
    "49.27.025": {"desc": "Dipendenti c/retribuzioni", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale"},
    "49.27.041": {"desc": "Collaboratori c/compensi", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale"},
    "49.27.045": {"desc": "Dipendenti c/ferie da liquidare", "tipo": "debiti_personale", "normale": "avere", "categoria": "personale"},
    "49.27.089": {"desc": "Soci c/dividendi", "tipo": "debiti_personale", "normale": "avere", "categoria": "soci"},
    
    # RICAVI
    "60.01.001": {"desc": "Ricavi da cessioni di beni", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite"},
    "60.01.005": {"desc": "Ricavi da prestazione di servizi", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite"},
    "60.01.009": {"desc": "Merci c/vendite", "tipo": "economico_ricavi", "normale": "avere", "categoria": "vendite"},
    "60.01.037": {"desc": "Canoni di locazione immobili", "tipo": "economico_ricavi", "normale": "avere", "categoria": "affitti"},
    "60.01.041": {"desc": "Canoni locazione altri cespiti", "tipo": "economico_ricavi", "normale": "avere", "categoria": "affitti"},
    
    # ALTRI RICAVI
    "71.01.001": {"desc": "Canoni di locazione fabbricati", "tipo": "altri_ricavi", "normale": "avere", "categoria": "affitti"},
    "71.01.029": {"desc": "Provvigioni attive", "tipo": "altri_ricavi", "normale": "avere", "categoria": "proventi"},
    "71.01.053": {"desc": "Risarcimento danni", "tipo": "altri_ricavi", "normale": "avere", "categoria": "proventi"},
    "71.01.081": {"desc": "Contrib. c/capitale", "tipo": "altri_ricavi", "normale": "avere", "categoria": "contributi"},
    "71.01.085": {"desc": "Contrib. c/esercizio", "tipo": "altri_ricavi", "normale": "avere", "categoria": "contributi"},
    
    # ACQUISTI
    "73.01.001": {"desc": "Materie prime c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti"},
    "73.01.013": {"desc": "Merci c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti"},
    "73.01.017": {"desc": "Materiale di consumo c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti"},
    "73.01.021": {"desc": "Imballaggi c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "acquisti"},
    "73.01.037": {"desc": "Fabbricati civili c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili"},
    "73.01.041": {"desc": "Fabbricati ind.li c/acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili"},
    
    # ALTRI ACQUISTI
    "73.09.006": {"desc": "Carburanti e lubrificanti", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi"},
    "73.09.045": {"desc": "Cancelleria e stampati", "tipo": "economico_costi", "normale": "dare", "categoria": "ufficio"},
    "73.09.053": {"desc": "Trasporti su acquisti", "tipo": "economico_costi", "normale": "dare", "categoria": "logistica"},
    "73.09.069": {"desc": "Abbigliamento del personale", "tipo": "economico_costi", "normale": "dare", "categoria": "personale"},
    "73.09.077": {"desc": "Beni < Euro 516", "tipo": "economico_costi", "normale": "dare", "categoria": "piccoli_beni"},
    
    # SERVIZI - COSTI INDUSTRIALI
    "75.01.005": {"desc": "Trasporti", "tipo": "economico_costi", "normale": "dare", "categoria": "logistica"},
    "75.01.025": {"desc": "Energia elettrica", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.01.026": {"desc": "Energia elettrica ind. 50%", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.01.028": {"desc": "Energia elettrica ind. 80%", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.01.033": {"desc": "Gas riscaldamento", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.01.037": {"desc": "Acqua", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.01.041": {"desc": "Consulenze tecniche", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    
    # MANUTENZIONI
    "75.05.001": {"desc": "Manut. fabbricati", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni"},
    "75.05.005": {"desc": "Manut. fabbricati civili", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni"},
    "75.05.017": {"desc": "Manutenzioni impianti e macchinari", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni"},
    "75.05.029": {"desc": "Manut. impianto elettrico", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni"},
    "75.05.033": {"desc": "Manut. impianto idraulico", "tipo": "economico_costi", "normale": "dare", "categoria": "manutenzioni"},
    "75.05.105": {"desc": "Manut. autovetture", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi"},
    "75.05.145": {"desc": "Manut. computer ed accessori", "tipo": "economico_costi", "normale": "dare", "categoria": "attrezzature"},
    "75.05.149": {"desc": "Manut. telefonia fissa", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.05.153": {"desc": "Manut. telefonia mobile", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.05.157": {"desc": "Manut. mobili", "tipo": "economico_costi", "normale": "dare", "categoria": "arredi"},
    "75.05.161": {"desc": "Manut. arredi", "tipo": "economico_costi", "normale": "dare", "categoria": "arredi"},
    
    # COSTI AMMINISTRATIVI
    "75.11.001": {"desc": "Consulenze amministrative", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.11.002": {"desc": "Consulenze", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.11.005": {"desc": "Consulenze legali", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.11.009": {"desc": "Consulenze notarili", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.11.013": {"desc": "Spese tenuta contabilità/paghe", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.11.017": {"desc": "Compensi amministratore", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori"},
    "75.11.021": {"desc": "Contr. INPS amministratori", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori"},
    "75.11.033": {"desc": "Compensi C.D.A.", "tipo": "economico_costi", "normale": "dare", "categoria": "amministratori"},
    "75.11.065": {"desc": "Compensi al collegio sindacale", "tipo": "economico_costi", "normale": "dare", "categoria": "sindaci"},
    "75.11.073": {"desc": "Compensi per collab. a progetto", "tipo": "economico_costi", "normale": "dare", "categoria": "collaboratori"},
    "75.11.077": {"desc": "Contr. INPS collab. a progetto", "tipo": "economico_costi", "normale": "dare", "categoria": "collaboratori"},
    "75.11.090": {"desc": "Compensi occasionali", "tipo": "economico_costi", "normale": "dare", "categoria": "collaboratori"},
    "75.11.113": {"desc": "Spese telefoniche", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.11.114": {"desc": "Spese telefonia mobile", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.11.116": {"desc": "Spese telefoniche prom. 80% ind.", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.11.117": {"desc": "Spese telefoniche non deducibili", "tipo": "economico_costi", "normale": "dare", "categoria": "utenze"},
    "75.11.133": {"desc": "Spese varie amministrative", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    
    # COSTI COMMERCIALI
    "75.13.009": {"desc": "Provvigioni a intermediari", "tipo": "economico_costi", "normale": "dare", "categoria": "vendite"},
    "75.13.021": {"desc": "Contr. ENASARCO", "tipo": "economico_costi", "normale": "dare", "categoria": "vendite"},
    "75.13.037": {"desc": "Spese di pubblicità", "tipo": "economico_costi", "normale": "dare", "categoria": "marketing"},
    "75.13.045": {"desc": "Mostre e fiere", "tipo": "economico_costi", "normale": "dare", "categoria": "marketing"},
    
    # ASSICURAZIONI
    "75.15.001": {"desc": "Assicurazioni", "tipo": "economico_costi", "normale": "dare", "categoria": "assicurazioni"},
    "75.15.005": {"desc": "Assicurazioni auto", "tipo": "economico_costi", "normale": "dare", "categoria": "automezzi"},
    "75.15.061": {"desc": "Assicurazioni immobili", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili"},
    
    # SPESE PER SERVIZI VARI
    "75.17.001": {"desc": "Servizi di vigilanza", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.17.009": {"desc": "Spese di pulizia esterni", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.17.013": {"desc": "Spese di pulizia interni", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.17.033": {"desc": "Viaggi (ferrovia, aereo, auto ecc.)", "tipo": "economico_costi", "normale": "dare", "categoria": "trasferte"},
    "75.17.038": {"desc": "Pedaggi autostradali", "tipo": "economico_costi", "normale": "dare", "categoria": "trasferte"},
    "75.17.041": {"desc": "Spese di rappresentanza", "tipo": "economico_costi", "normale": "dare", "categoria": "rappresentanza"},
    "75.17.045": {"desc": "Mensa aziend.appalt.ta a terzi/buoni pasto", "tipo": "economico_costi", "normale": "dare", "categoria": "personale"},
    "75.17.049": {"desc": "Costi per buoni pasto", "tipo": "economico_costi", "normale": "dare", "categoria": "personale"},
    "75.17.065": {"desc": "Ricerca, addestramento e formazione", "tipo": "economico_costi", "normale": "dare", "categoria": "personale"},
    "75.17.077": {"desc": "Servizio smaltimento rifiuti", "tipo": "economico_costi", "normale": "dare", "categoria": "servizi"},
    "75.17.081": {"desc": "Spese per servizi bancari", "tipo": "economico_costi", "normale": "dare", "categoria": "banca"},
    "75.17.082": {"desc": "Commissioni factoring", "tipo": "economico_costi", "normale": "dare", "categoria": "banca"},
    "75.17.093": {"desc": "Costi condominio", "tipo": "economico_costi", "normale": "dare", "categoria": "immobili"},
    
    # CANONI DI LOCAZIONE
    "77.01.009": {"desc": "Canone locazione fabbricati civili", "tipo": "economico_costi", "normale": "dare", "categoria": "affitti"},
    "77.01.013": {"desc": "Canone locazione fabbricati industriali", "tipo": "economico_costi", "normale": "dare", "categoria": "affitti"},
    "77.01.017": {"desc": "Canone locazione fabbricati commerciali", "tipo": "economico_costi", "normale": "dare", "categoria": "affitti"},
    "77.01.037": {"desc": "Canone locazione macchinari", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi"},
    
    # CANONI DI LEASING
    "77.03.105": {"desc": "Canone leasing autov.", "tipo": "economico_costi", "normale": "dare", "categoria": "leasing"},
    "77.03.157": {"desc": "Canone leasing computer", "tipo": "economico_costi", "normale": "dare", "categoria": "leasing"},
    
    # CANONI DI NOLEGGIO
    "77.05.061": {"desc": "Canone noleggio autov.", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi"},
    "77.05.129": {"desc": "Canone noleggio computer ed accessori", "tipo": "economico_costi", "normale": "dare", "categoria": "noleggi"},
    
    # COSTO PERSONALE - SALARI E STIPENDI
    "79.01.001": {"desc": "Salari", "tipo": "costo_personale", "normale": "dare", "categoria": "personale"},
    "79.01.005": {"desc": "Stipendi impiegati", "tipo": "costo_personale", "normale": "dare", "categoria": "personale"},
    "79.01.009": {"desc": "Stipendi dirigenti", "tipo": "costo_personale", "normale": "dare", "categoria": "personale"},
    "79.01.013": {"desc": "Trasferte impiegati", "tipo": "costo_personale", "normale": "dare", "categoria": "personale"},
    "79.01.021": {"desc": "Premi impiegati", "tipo": "costo_personale", "normale": "dare", "categoria": "personale"},
    
    # ONERI SOCIALI
    "79.03.001": {"desc": "Oneri INPS", "tipo": "costo_personale", "normale": "dare", "categoria": "inps"},
    "79.03.005": {"desc": "Oneri INAIL", "tipo": "costo_personale", "normale": "dare", "categoria": "inail"},
    
    # TRATTAMENTO DI FINE RAPPORTO
    "79.05.001": {"desc": "Acc.to fondo TFR", "tipo": "costo_personale", "normale": "dare", "categoria": "tfr"},
    "79.05.005": {"desc": "Quota TFR maturata nell'anno", "tipo": "costo_personale", "normale": "dare", "categoria": "tfr"},
    
    # AMMORTAMENTI
    "81.01.009": {"desc": "Amm.to spese di costituzione", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.03.001": {"desc": "Amm.to fabbricati civili", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.05.009": {"desc": "Amm.to impianto elettrico", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.05.013": {"desc": "Amm.to impianto idraulico", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.09.001": {"desc": "Amm.to autovetture", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.09.065": {"desc": "Amm.to computer ed accessori", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.09.077": {"desc": "Amm.to mobili", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    "83.09.081": {"desc": "Amm.to arredi", "tipo": "ammortamenti", "normale": "dare", "categoria": "ammortamenti"},
    
    # ONERI DIVERSI DI GESTIONE
    "92.01.001": {"desc": "Imposta di bollo", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse"},
    "92.01.005": {"desc": "IMU", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse"},
    "92.01.037": {"desc": "Tasse prop. autov.", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse"},
    "92.01.085": {"desc": "Diritti CCIAA", "tipo": "oneri_diversi", "normale": "dare", "categoria": "tasse"},
    "92.01.097": {"desc": "Perdite su crediti", "tipo": "oneri_diversi", "normale": "dare", "categoria": "svalutazioni"},
    "92.01.105": {"desc": "Abbonamenti riviste e giornali", "tipo": "oneri_diversi", "normale": "dare", "categoria": "servizi"},
    "92.01.113": {"desc": "Multe e ammende", "tipo": "oneri_diversi", "normale": "dare", "categoria": "sanzioni"},
    "92.01.121": {"desc": "Omaggi a clienti e articoli promozionali", "tipo": "oneri_diversi", "normale": "dare", "categoria": "marketing"},
    "92.01.144": {"desc": "Erogaz. liberali", "tipo": "oneri_diversi", "normale": "dare", "categoria": "liberalita"},
    
    # PROVENTI FINANZIARI
    "93.13.001": {"desc": "Interessi att. c/c bancari", "tipo": "proventi_finanziari", "normale": "avere", "categoria": "finanza"},
    
    # ONERI FINANZIARI
    "93.15.021": {"desc": "Interessi pass. sui debiti verso banche", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "finanza"},
    "93.15.025": {"desc": "Interessi pass. mutui", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "finanza"},
    "93.15.081": {"desc": "Commissione max scoperto", "tipo": "oneri_finanziari", "normale": "dare", "categoria": "banca"},
    
    # IMPOSTE
    "96.01.001": {"desc": "IRES", "tipo": "imposte", "normale": "dare", "categoria": "imposte"},
    "96.01.005": {"desc": "IRAP", "tipo": "imposte", "normale": "dare", "categoria": "imposte"},
}

# ==============================================================================
# TEMPLATE OPERAZIONI CONTABILI COMPLETE
# ==============================================================================
OPERAZIONI_CONTABILI = {
    "COSTITUZIONE_SOCIETA": {
        "nome": "Costituzione società - versamento capitale",
        "descrizione": "Versamento capitale sociale in banca",
        "conti_suggeriti": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["40.01.001"]   # Capitale sociale
        },
        "note": "Indicare l'importo del capitale sociale versato"
    },
    "ACQUISTO_MERCE_FATTURA": {
        "nome": "Acquisto merce con fattura",
        "descrizione": "Ricezione fattura acquisto merci da fornitore",
        "conti_suggeriti": {
            "dare": ["73.01.013", "28.11.009"],  # Merci c/acquisti + IVA credito
            "avere": ["49.13.001"]  # Fornitore
        },
        "note": "Specificare se IVA 22%, 10%, 4% o altra aliquota"
    },
    "VENDITA_MERCE_FATTURA": {
        "nome": "Vendita merce con fattura",
        "descrizione": "Emissione fattura vendita merci a cliente",
        "conti_suggeriti": {
            "dare": ["28.01.001"],  # Cliente
            "avere": ["60.01.009", "49.23.009"]  # Merci c/vendite + IVA debito
        },
        "note": "Specificare aliquota IVA applicata"
    },
    "PAGAMENTO_FORNITORE_BONIFICO": {
        "nome": "Pagamento fornitore tramite bonifico",
        "descrizione": "Saldo fattura fornitore con bonifico bancario",
        "conti_suggeriti": {
            "dare": ["49.13.001"],  # Fornitore
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Indicare numero fattura e data pagamento"
    },
    "INCASSO_CLIENTE_BONIFICO": {
        "nome": "Incasso da cliente tramite bonifico",
        "descrizione": "Ricezione pagamento da cliente su c/c",
        "conti_suggeriti": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["28.01.001"]  # Cliente
        },
        "note": "Indicare causale del bonifico"
    },
    "ACQUISTO_CESPITE": {
        "nome": "Acquisto bene strumentale (cespite)",
        "descrizione": "Acquisto autovettura, computer, macchinari, ecc.",
        "conti_suggeriti": {
            "dare": ["13.09.001", "28.11.009"],  # Autovetture + IVA (esempio)
            "avere": ["49.13.001"]  # Fornitore
        },
        "note": "Specificare tipo di bene: autovettura (13.09.001), computer (13.09.065), mobili (13.09.077), ecc."
    },
    "AMMORTAMENTO_CESPITE": {
        "nome": "Ammortamento cespite annuale",
        "descrizione": "Registrazione quota ammortamento",
        "conti_suggeriti": {
            "dare": ["83.09.001"],  # Amm.to autovetture (esempio)
            "avere": ["16.07.001"]  # F.do amm.to autovetture
        },
        "note": "Indicare quota annuale di ammortamento calcolata"
    },
    "REGISTRAZIONE_STIPENDI": {
        "nome": "Registrazione stipendi dipendenti",
        "descrizione": "Competenza stipendi, INPS e ritenute",
        "conti_suggeriti": {
            "dare": ["79.01.005", "79.03.001"],  # Stipendi + Oneri INPS azienda
            "avere": ["49.27.025", "49.23.029", "49.25.001"]  # Dipendenti c/retrib + Ritenute + INPS
        },
        "note": "Specificare: lordo stipendio, ritenute IRPEF, INPS dipendente, INPS azienda"
    },
    "PAGAMENTO_STIPENDI": {
        "nome": "Pagamento stipendi ai dipendenti",
        "descrizione": "Bonifico stipendi netti ai dipendenti",
        "conti_suggeriti": {
            "dare": ["49.27.025"],  # Dipendenti c/retribuzioni
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Importo netto da pagare ai dipendenti"
    },
    "ACCANTONAMENTO_TFR": {
        "nome": "Accantonamento TFR",
        "descrizione": "Quota TFR maturata nell'esercizio",
        "conti_suggeriti": {
            "dare": ["79.05.001"],  # Acc.to fondo TFR
            "avere": ["46.01.001"]  # Fondo TFR
        },
        "note": "Calcolare quota TFR secondo normativa"
    },
    "COMPENSO_AMMINISTRATORE": {
        "nome": "Compenso amministratore",
        "descrizione": "Registrazione compenso amministratore con ritenuta",
        "conti_suggeriti": {
            "dare": ["75.11.017"],  # Compensi amministratore
            "avere": ["49.27.001", "49.23.039"]  # Debiti v/amministratori + Ritenuta 20%
        },
        "note": "Applicare ritenuta d'acconto 20% sul compenso"
    },
    "CANONE_AFFITTO": {
        "nome": "Canone di locazione/affitto",
        "descrizione": "Pagamento canone affitto immobile",
        "conti_suggeriti": {
            "dare": ["77.01.009", "28.11.009"],  # Canone locazione + IVA (se dovuta)
            "avere": ["49.13.001"]  # Fornitore/Locatore
        },
        "note": "Verificare se soggetto a IVA o esente"
    },
    "UTENZE": {
        "nome": "Utenze (luce, gas, acqua, telefono)",
        "descrizione": "Pagamento bollette utenze",
        "conti_suggeriti": {
            "dare": ["75.01.025", "75.01.033", "75.01.037", "75.11.113", "28.11.009"],  # Energia/Gas/Acqua/Telefono + IVA
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Specificare tipologia: energia elettrica (75.01.025), gas (75.01.033), acqua (75.01.037), telefono (75.11.113)"
    },
    "CARBURANTE": {
        "nome": "Carburante e lubrificanti",
        "descrizione": "Acquisto carburante per automezzi",
        "conti_suggeriti": {
            "dare": ["73.09.006", "28.11.009"],  # Carburanti + IVA
            "avere": ["34.01.001"]  # Banca c/c o cassa
        },
        "note": "Verificare deducibilità (40% autovetture, 100% autocarri)"
    },
    "MANUTENZIONE_AUTO": {
        "nome": "Manutenzione autovetture",
        "descrizione": "Riparazioni, gomme, tagliando auto",
        "conti_suggeriti": {
            "dare": ["75.05.105", "28.11.009"],  # Manut. autovetture + IVA
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Deducibilità 40% per autovetture, 100% per autocarri"
    },
    "ASSICURAZIONE": {
        "nome": "Polizza assicurativa",
        "descrizione": "Pagamento premio assicurazione",
        "conti_suggeriti": {
            "dare": ["75.15.001", "75.15.005"],  # Assicurazioni generiche o auto
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Specificare tipo: auto (75.15.005), immobili (75.15.061), altro (75.15.001)"
    },
    "PUBBLICITA": {
        "nome": "Spese di pubblicità e marketing",
        "descrizione": "Google Ads, Facebook Ads, brochure, fiere",
        "conti_suggeriti": {
            "dare": ["75.13.037", "28.11.009"],  # Spese pubblicità + IVA
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Includere anche partecipazione a fiere (75.13.045)"
    },
    "VIAGGI_TRASFERTA": {
        "nome": "Viaggi e trasferte",
        "descrizione": "Biglietti treno/aereo, hotel, pasti trasferta",
        "conti_suggeriti": {
            "dare": ["75.17.033", "28.11.009"],  # Viaggi + IVA
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Specificare se trasferta nazionale o estera"
    },
    "CANCELLERIA": {
        "nome": "Cancelleria e materiale d'ufficio",
        "descrizione": "Acquisto carta, penne, stampati, ecc.",
        "conti_suggeriti": {
            "dare": ["73.09.045", "28.11.009"],  # Cancelleria + IVA
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Per beni < 516€ usare 73.09.077"
    },
    "CONSULENZE": {
        "nome": "Consulenze professionali",
        "descrizione": "Commercialista, avvocato, consulenti vari",
        "conti_suggeriti": {
            "dare": ["75.11.002", "75.11.005", "28.11.009"],  # Consulenze + IVA
            "avere": ["49.13.001", "49.23.039"]  # Fornitore + Ritenuta (se professionista)
        },
        "note": "Applicare ritenuta 20% se professionista soggetto a ritenuta"
    },
    "INTERESSI_PASSIVI_MUTUO": {
        "nome": "Interessi passivi su mutuo",
        "descrizione": "Quota interessi su mutuo bancario",
        "conti_suggeriti": {
            "dare": ["93.15.025"],  # Interessi passivi mutui
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Separare quota capitale da quota interessi"
    },
    "COMMISSIONI_BANCARIE": {
        "nome": "Commissioni e spese bancarie",
        "descrizione": "Spese conto corrente, bonifici, ecc.",
        "conti_suggeriti": {
            "dare": ["75.17.081", "92.01.001"],  # Spese bancarie + bolli
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Includere imposta di bollo 34,20€ se dovuta"
    },
    "VERSAMENTO_RITENUTE_F24": {
        "nome": "Versamento ritenute e contributi (F24)",
        "descrizione": "Pagamento ritenute IRPEF e contributi INPS",
        "conti_suggeriti": {
            "dare": ["49.23.029", "49.25.001"],  # Ritenute + INPS
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Versare entro il 16 del mese successivo"
    },
    "LIQUIDAZIONE_IVA": {
        "nome": "Liquidazione IVA periodica",
        "descrizione": "Versamento IVA a debito o recupero credito",
        "conti_suggeriti": {
            "dare": ["49.23.009"],  # Erario c/IVA (se debito)
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Calcolare: IVA vendite - IVA acquisti = IVA da versare/recuperare"
    },
    "ACCANTONAMENTO_IMPOSTE": {
        "nome": "Accantonamento imposte (IRES/IRAP)",
        "descrizione": "Accantonamento imposte di esercizio",
        "conti_suggeriti": {
            "dare": ["96.01.001", "96.01.005"],  # IRES + IRAP
            "avere": ["49.23.001", "49.23.005"]  # Erario c/IRES + Erario c/IRAP
        },
        "note": "Calcolare in base all'utile di esercizio"
    },
    "REVERSE_CHARGE": {
        "nome": "Reverse charge (art. 17 c.6)",
        "descrizione": "Acquisto con inversione contabile",
        "conti_suggeriti": {
            "dare": ["73.01.013", "28.11.009"],  # Merci + IVA credito
            "avere": ["49.13.001", "49.23.009"]  # Fornitore + IVA debito
        },
        "note": "Integrare fattura con autofattura o annotazione"
    },
    "SPLIT_PAYMENT": {
        "nome": "Split payment (PA - art. 17-ter)",
        "descrizione": "Vendita a PA con scissione pagamenti",
        "conti_suggeriti": {
            "dare": ["28.01.001", "28.11.009"],  # Cliente + IVA credito
            "avere": ["60.01.009", "49.23.009"]  # Vendite + IVA debito
        },
        "note": "L'IVA viene versata dalla PA, non dal cliente"
    },
    "PERDITA_CREDITI": {
        "nome": "Perdita su crediti",
        "descrizione": "Svalutazione crediti inesigibili",
        "conti_suggeriti": {
            "dare": ["92.01.097", "28.11.009"],  # Perdite su crediti + storno IVA
            "avere": ["28.01.001"]  # Cliente
        },
        "note": "Stornare IVA solo se ricorrono i requisiti (fallimento, ecc.)"
    },
    "RISARCIMENTO_DANNI": {
        "nome": "Risarcimento danni ricevuto",
        "descrizione": "Incasso risarcimento assicurativo o altro",
        "conti_suggeriti": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["71.01.053"]  # Risarcimento danni
        },
        "note": "Generalmente non soggetto a IVA"
    },
    "CONTRIBUTO_CONTO_CAPITALE": {
        "nome": "Contributo in conto capitale",
        "descrizione": "Contributo pubblico o privato in conto capitale",
        "conti_suggeriti": {
            "dare": ["34.01.001"],  # Banca c/c
            "avere": ["71.01.081", "40.13.010"]  # Contributo + Riserva
        },
        "note": "Iscritto a patrimonio netto (riserva contributi)"
    },
    "LEASING_CANONE": {
        "nome": "Canone leasing",
        "descrizione": "Pagamento canone leasing",
        "conti_suggeriti": {
            "dare": ["77.03.157", "93.15.025", "28.11.009"],  # Canone + interessi + IVA
            "avere": ["34.01.001"]  # Banca c/c
        },
        "note": "Separare quota capitale, quota interessi e IVA"
    },
}

# ==============================================================================
# FUNZIONI DI SUPPORTO
# ==============================================================================
def get_conto_info(codice_conto):
    """Recupera informazioni complete sul conto"""
    return PIANO_CONTI_COMPLETO.get(codice_conto, {})

def cerca_conti(parola_chiave):
    """Cerca conti nel piano dei conti per parola chiave"""
    risultati = []
    parola_chiave = parola_chiave.lower()
    
    for codice, info in PIANO_CONTI_COMPLETO.items():
        if (parola_chiave in info['desc'].lower() or 
            parola_chiave in info['categoria'].lower() or
            parola_chiave in info['tipo'].lower()):
            risultati.append({
                'codice': codice,
                'descrizione': info['desc'],
                'tipo': info['tipo'],
                'categoria': info['categoria'],
                'normale': info['normale']
            })
    
    return risultati

def genera_suggerimenti_contabili(descrizione_operazione):
    """Genera suggerimenti di conti basati sulla descrizione"""
    suggerimenti = []
    descrizione_lower = descrizione_operazione.lower()
    
    # Logica di suggerimento basata su parole chiave
    if any(word in descrizione_lower for word in ['fattura', 'acquisto', 'merce', 'fornitore']):
        suggerimenti.append({
            'tipo': 'operazione',
            'nome': 'Acquisto merce',
            'conti': ['73.01.013', '28.11.009', '49.13.001'],
            'descrizione': 'Merci c/acquisti + IVA credito + Fornitore'
        })
    
    if any(word in descrizione_lower for word in ['vendita', 'cliente', 'ricavo']):
        suggerimenti.append({
            'tipo': 'operazione',
            'nome': 'Vendita merce',
            'conti': ['28.01.001', '60.01.009', '49.23.009'],
            'descrizione': 'Cliente + Merci c/vendite + IVA debito'
        })
    
    if any(word in descrizione_lower for word in ['stipendio', 'salario', 'dipendente', 'busta paga']):
        suggerimenti.append({
            'tipo': 'operazione',
            'nome': 'Stipendi',
            'conti': ['79.01.005', '79.03.001', '49.27.025', '49.23.029', '49.25.001'],
            'descrizione': 'Stipendi + Oneri INPS + Dipendenti c/retrib + Ritenute + INPS'
        })
    
    if any(word in descrizione_lower for word in ['bonifico', 'pagamento', 'incasso']):
        suggerimenti.append({
            'tipo': 'operazione',
            'nome': 'Movimentazione bancaria',
            'conti': ['34.01.001', '49.13.001', '28.01.001'],
            'descrizione': 'Banca c/c + Fornitore/Cliente'
        })
    
    if any(word in descrizione_lower for word in ['auto', 'macchina', 'veicolo', 'carburante', 'benzina']):
        suggerimenti.append({
            'tipo': 'conto',
            'nome': 'Automezzi e carburante',
            'conti': ['13.09.001', '73.09.006', '75.05.105'],
            'descrizione': 'Autovetture + Carburanti + Manutenzione auto'
        })
    
    if any(word in descrizione_lower for word in ['computer', 'pc', 'software', 'telefono']):
        suggerimenti.append({
            'tipo': 'conto',
            'nome': 'Attrezzature e utenze',
            'conti': ['13.09.065', '75.11.113', '75.11.114'],
            'descrizione': 'Computer + Telefonia fissa + Telefonia mobile'
        })
    
    if any(word in descrizione_lower for word in ['affitto', 'locazione', 'canone']):
        suggerimenti.append({
            'tipo': 'conto',
            'nome': 'Affitti e leasing',
            'conti': ['77.01.009', '77.03.105'],
            'descrizione': 'Canone locazione + Canone leasing'
        })
    
    if any(word in descrizione_lower for word in ['iva', 'imposta', 'tassa', 'f24']):
        suggerimenti.append({
            'tipo': 'conto',
            'nome': 'Imposte e tasse',
            'conti': ['28.11.009', '49.23.009', '96.01.001', '96.01.005'],
            'descrizione': 'Credito IVA + Erario c/IVA + IRES + IRAP'
        })
    
    return suggerimenti

def valida_scrittura(dare, avere):
    """Valida che la scrittura sia bilanciata"""
    tot_dare = sum(riga.get('importo', 0) for riga in dare)
    tot_avere = sum(riga.get('importo', 0) for riga in avere)
    
    return {
        'bilanciata': abs(tot_dare - tot_avere) < 0.01,
        'totale_dare': tot_dare,
        'totale_avere': tot_avere,
        'differenza': abs(tot_dare - tot_avere)
    }

# ==============================================================================
# INTERFACCIA STREAMLIT
# ==============================================================================
st.title("📒 Generatore Scritture Contabili SRL")
st.markdown("""
**Generatore avanzato di scritture contabili** basato sul **Piano dei Conti Ranocchi GIS**.
Supporta operazioni con e senza importi, suggerimenti intelligenti e validazione automatica.
""")

# Sidebar - Selezione modalità
with st.sidebar:
    st.header("📋 Modalità di Inserimento")
    modalita = st.radio(
        "Come vuoi generare la scrittura?",
        ["📝 Descrizione testuale", "📋 Operazione predefinita", "🔍 Ricerca conti", "✍️ Inserimento manuale conti"],
        help="Scegli la modalità più adatta alle tue esigenze"
    )
    
    st.markdown("---")
    st.info("""
    **Funzionalità:**
    - ✅ Suggerimenti automatici
    - ✅ Validazione DARE = AVERE
    - ✅ Piano conti Ranocchi completo
    - ✅ Export CSV
    - ✅ Operazioni con/senza importi
    """)

scrittura_generata = None
note_operative = []

# ==============================================================================
# MODALITÀ 1: DESCRIZIONE TESTUALE
# ==============================================================================
if modalita == "📝 Descrizione testuale":
    st.header("📝 Inserimento Descrizione Operazione")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        descrizione = st.text_area(
            "Descrivi l'operazione contabile",
            placeholder="Es: Pagamento fattura n. 123 del fornitore Rossi di € 1.220 (€ 1.000 + IVA 22%) tramite bonifico bancario",
            height=100
        )
    
    with col2:
        con_importi = st.checkbox("Con importi", value=True)
    
    if descrizione:
        # Genera suggerimenti
        suggerimenti = genera_suggerimenti_contabili(descrizione)
        
        if suggerimenti:
            st.subheader("💡 Suggerimenti rilevati:")
            for sug in suggerimenti:
                with st.expander(f"📌 {sug['nome']}"):
                    st.write(f"**Conti suggeriti:** {', '.join(sug['conti'])}")
                    st.write(f"**Descrizione:** {sug['descrizione']}")
        
        # Mostra template operazioni simili
        st.subheader("📋 Operazioni simili disponibili:")
        for key, op in OPERAZIONI_CONTABILI.items():
            if any(word in descrizione.lower() for word in op['nome'].lower().split()):
                st.write(f"✅ **{op['nome']}**: {op['descrizione']}")
                st.write(f"   Conti: DARE {op['conti_suggeriti']['dare']} - AVERE {op['conti_suggeriti']['avere']}")
                st.write(f"   Note: {op['note']}")
                st.markdown("---")
    
    # Input manuali
    if con_importi:
        st.markdown("---")
        st.subheader("💰 Inserimento Importi")
        col1, col2, col3 = st.columns(3)
        with col1:
            imponibile = st.number_input("Imponibile €", min_value=0.0, step=0.01, format="%.2f")
        with col2:
            aliquota_iva = st.number_input("Aliquota IVA %", min_value=0, max_value=100, value=22)
        with col3:
            if imponibile > 0:
                iva = imponibile * (aliquota_iva / 100)
                totale = imponibile + iva
                st.metric("Totale", f"€ {totale:,.2f}")
                st.write(f"IVA: € {iva:,.2f}")

# ==============================================================================
# MODALITÀ 2: OPERAZIONE PREDEFINITA
# ==============================================================================
elif modalita == "📋 Operazione predefinita":
    st.header("📋 Selezione Operazione Contabile")
    
    # Raggruppa operazioni per categoria
    categorie = {
        "Costituzione e Capitale": ["COSTITUZIONE_SOCIETA"],
        "Acquisti e Vendite": ["ACQUISTO_MERCE_FATTURA", "VENDITA_MERCE_FATTURA", "REVERSE_CHARGE", "SPLIT_PAYMENT"],
        "Pagamenti e Incassi": ["PAGAMENTO_FORNITORE_BONIFICO", "INCASSO_CLIENTE_BONIFICO"],
        "Personale": ["REGISTRAZIONE_STIPENDI", "PAGAMENTO_STIPENDI", "ACCANTONAMENTO_TFR", "COMPENSO_AMMINISTRATORE"],
        "Immobilizzazioni": ["ACQUISTO_CESPITE", "AMMORTAMENTO_CESPITE", "LEASING_CANONE"],
        "Gestione Corrente": ["CANONE_AFFITTO", "UTENZE", "CARBURANTE", "MANUTENZIONE_AUTO", "ASSICURAZIONE", "CANCELLERIA", "CONSULENZE", "PUBBLICITA", "VIAGGI_TRASFERTA"],
        "Tributi": ["LIQUIDAZIONE_IVA", "ACCANTONAMENTO_IMPOSTE", "VERSAMENTO_RITENUTE_F24"],
        "Finanza": ["INTERESSI_PASSIVI_MUTUO", "COMMISSIONI_BANCARIE"],
        "Varie": ["PERDITA_CREDITI", "RISARCIMENTO_DANNI", "CONTRIBUTO_CONTO_CAPITALE"]
    }
    
    categoria_selezionata = st.selectbox("Categoria", list(categorie.keys()))
    operazioni_categoria = categorie[categoria_selezionata]
    
    operazione_selezionata = st.selectbox(
        "Operazione",
        operazioni_categoria,
        format_func=lambda x: OPERAZIONI_CONTABILI[x]['nome']
    )
    
    if operazione_selezionata:
        op_info = OPERAZIONI_CONTABILI[operazione_selezionata]
        
        st.info(f"**Descrizione:** {op_info['descrizione']}")
        st.write(f"**Note operative:** {op_info['note']}")
        
        # Mostra conti suggeriti
        col1, col2 = st.columns(2)
        with col1:
            st.write("**DARE:**")
            for conto in op_info['conti_suggeriti']['dare']:
                info = get_conto_info(conto)
                st.write(f"• {conto} - {info.get('desc', 'N/A')}")
        
        with col2:
            st.write("**AVERE:**")
            for conto in op_info['conti_suggeriti']['avere']:
                info = get_conto_info(conto)
                st.write(f"• {conto} - {info.get('desc', 'N/A')}")
        
        # Input importi
        st.markdown("---")
        st.subheader("💰 Inserimento Importi")
        con_importi = st.checkbox("Inserisci importi", value=True)
        
        if con_importi:
            col1, col2, col3 = st.columns(3)
            with col1:
                imponibile = st.number_input("Imponibile €", min_value=0.0, step=0.01, format="%.2f", key="imp_op_predef")
            with col2:
                aliquota_iva = st.number_input("Aliquota IVA %", min_value=0, max_value=100, value=22, key="iva_op_predef")
            with col3:
                if imponibile > 0:
                    iva = imponibile * (aliquota_iva / 100)
                    totale = imponibile + iva
                    st.metric("Totale", f"€ {totale:,.2f}")

# ==============================================================================
# MODALITÀ 3: RICERCA CONTI
# ==============================================================================
elif modalita == "🔍 Ricerca conti":
    st.header("🔍 Ricerca nel Piano dei Conti")
    
    ricerca = st.text_input("Cerca conto per descrizione, categoria o tipo", placeholder="Es: autovettura, banca, IVA, stipendio...")
    
    if ricerca:
        risultati = cerca_conti(ricerca)
        
        if risultati:
            st.write(f"Trovati {len(risultati)} conti:")
            
            # Mostra in tabella
            df_risultati = pd.DataFrame(risultati)
            st.dataframe(df_risultati, use_container_width=True)
            
            # Permetti selezione multipla
            conti_selezionati = st.multiselect(
                "Seleziona i conti da utilizzare",
                options=[r['codice'] for r in risultati],
                format_func=lambda x: f"{x} - {next((r['descrizione'] for r in risultati if r['codice'] == x), 'N/A')}"
            )
            
            if conti_selezionati:
                st.write("**Conti selezionati:**")
                for conto in conti_selezionati:
                    info = get_conto_info(conto)
                    st.write(f"• {conto} - {info['desc']} ({info['normale']})")

# ==============================================================================
# MODALITÀ 4: INSERIMENTO MANUALE CONTI
# ==============================================================================
elif modalita == "✍️ Inserimento manuale conti":
    st.header("✍️ Inserimento Manuale Scrittura")
    
    st.subheader("DARE")
    dare_conti = []
    num_righe_dare = st.number_input("Numero righe DARE", min_value=1, max_value=10, value=1)
    
    for i in range(num_righe_dare):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            conto_dare = st.text_input(f"Conto DARE {i+1}", placeholder="Es: 73.01.013", key=f"dare_conto_{i}")
        with col2:
            desc_dare = st.text_input(f"Descrizione {i+1}", placeholder="Descrizione", key=f"dare_desc_{i}")
        with col3:
            imp_dare = st.number_input(f"Importo {i+1}", min_value=0.0, step=0.01, format="%.2f", key=f"dare_imp_{i}")
        
        if conto_dare:
            dare_conti.append({
                'conto': conto_dare,
                'descrizione': desc_dare or get_conto_info(conto_dare).get('desc', ''),
                'importo': imp_dare
            })
    
    st.subheader("AVERE")
    avere_conti = []
    num_righe_avere = st.number_input("Numero righe AVERE", min_value=1, max_value=10, value=1)
    
    for i in range(num_righe_avere):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            conto_avere = st.text_input(f"Conto AVERE {i+1}", placeholder="Es: 49.13.001", key=f"avere_conto_{i}")
        with col2:
            desc_avere = st.text_input(f"Descrizione {i+1}", placeholder="Descrizione", key=f"avere_desc_{i}")
        with col3:
            imp_avere = st.number_input(f"Importo {i+1}", min_value=0.0, step=0.01, format="%.2f", key=f"avere_imp_{i}")
        
        if conto_avere:
            avere_conti.append({
                'conto': conto_avere,
                'descrizione': desc_avere or get_conto_info(conto_avere).get('desc', ''),
                'importo': imp_avere
            })

# ==============================================================================
# VISUALIZZAZIONE E VALIDAZIONE
# ==============================================================================
st.markdown("---")
st.header("📊 Riepilogo Scrittura Contabile")

if 'operazione_selezionata' in locals() and operazione_selezionata:
    # Genera scrittura da operazione predefinita
    op_info = OPERAZIONI_CONTABILI[operazione_selezionata]
    
    if 'imponibile' in locals() and imponibile > 0:
        iva = imponibile * (aliquota_iva / 100)
        totale = imponibile + iva
        
        dare = []
        avere = []
        
        for conto in op_info['conti_suggeriti']['dare']:
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
        
        for conto in op_info['conti_suggeriti']['avere']:
            info = get_conto_info(conto)
            if '49.23.009' in conto:  # IVA debito
                importo = iva
            elif '49.13.001' in conto or '34.01.001' in conto:  # Fornitore o Banca
                importo = totale
            else:
                importo = imponibile
            avere.append({
                'conto': conto,
                'descrizione': info.get('desc', ''),
                'importo': round(importo, 2)
            })
        
        validazione = valida_scrittura(dare, avere)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("DARE")
            df_dare = pd.DataFrame(dare)
            st.dataframe(df_dare, use_container_width=True, hide_index=True)
            st.metric("Totale DARE", f"€ {validazione['totale_dare']:,.2f}")
        
        with col2:
            st.subheader("AVERE")
            df_avere = pd.DataFrame(avere)
            st.dataframe(df_avere, use_container_width=True, hide_index=True)
            st.metric("Totale AVERE", f"€ {validazione['totale_avere']:,.2f}")
        
        if validazione['bilanciata']:
            st.success("✅ Scrittura BILANCIATA (DARE = AVERE)")
        else:
            st.error(f"❌ Scrittura NON BILANCIATA (differenza: € {validazione['differenza']:,.2f})")
        
        # Note operative
        st.info(f"📝 **Note:** {op_info['note']}")
        
        # Download CSV
        csv_data = "Lato,Conto,Descrizione,Importo\n"
        for riga in dare:
            csv_data += f"DARE,{riga['conto']},{riga['descrizione']},{riga['importo']}\n"
        for riga in avere:
            csv_data += f"AVERE,{riga['conto']},{riga['descrizione']},{riga['importo']}\n"
        
        st.download_button(
            label="📥 Scarica Scrittura (CSV)",
            data=csv_data,
            file_name=f"scrittura_{operazione_selezionata}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
### 📚 Piano dei Conti Ranocchi GIS - Sezioni Principali

| Sezione | Codici | Descrizione |
|---------|--------|-------------|
| **Patrimoniale Attivo** | 01-34 | Crediti, immobilizzazioni, liquidità |
| **Patrimonio Netto** | 40 | Capitale, riserve, utili |
| **Patrimoniale Passivo** | 46-49 | Fondi, debiti commerciali/tributari/finanziari |
| **Economico Ricavi** | 60-71 | Vendite, altri ricavi e proventi |
| **Economico Costi** | 73-79 | Acquisti, servizi, personale |
| **Ammortamenti** | 81-83 | Quote ammortamento |
| **Oneri/Proventi** | 92-96 | Imposte, oneri finanziari, straordinari |

**Supporto:** Per assistenza sulla classificazione contabile, consultare il commercialista.
""")
