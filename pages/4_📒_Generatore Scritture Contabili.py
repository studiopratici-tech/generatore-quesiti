#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema di Generazione Scritture Contabili - Università
Basato sul Manuale Tecnico Operativo
"""

import json
from datetime import datetime
from typing import List, Dict, Tuple

class PianoDeiConti:
    """Gestione del piano dei conti caricato dal PDF"""
    
    def __init__(self):
        self.conti = self._carica_piano_dei_conti()
    
    def _carica_piano_dei_conti(self) -> Dict[str, dict]:
        """Carica il piano dei conti dal PDF"""
        return {
            # ATTIVITÀ PATRIMONIALI
            "01.01.001": {"descrizione": "SOCI C/SOTTOSCRIZIONE", "tipo": "Patrimoniale attivo"},
            "04.00.000": {"descrizione": "IMMOBILIZZAZIONI IMMATERIALI", "tipo": "Patrimoniale"},
            "04.01.001": {"descrizione": "SPESE DI IMPIANTO", "tipo": "Patrimoniale attivo"},
            "04.05.001": {"descrizione": "BREVETTI INDUSTRIALI", "tipo": "Patrimoniale attivo"},
            "04.07.001": {"descrizione": "CONCESSIONI", "tipo": "Patrimoniale attivo"},
            "04.07.005": {"descrizione": "LICENZE", "tipo": "Patrimoniale attivo"},
            "04.07.009": {"descrizione": "MARCHI", "tipo": "Patrimoniale attivo"},
            "04.07.013": {"descrizione": "SOFTWARE GENERICO", "tipo": "Patrimoniale attivo"},
            "04.09.001": {"descrizione": "AVVIAMENTO", "tipo": "Patrimoniale attivo"},
            "04.11.001": {"descrizione": "IMMOBILIZZAZIONI IMMATERIALI IN CORSO", "tipo": "Patrimoniale attivo"},
            "04.11.017": {"descrizione": "FORNITORE C/ACCONTI PER IMMOB. IMM.", "tipo": "Patrimoniale attivo"},
            "04.13.001": {"descrizione": "COSTO DIRITTO DI USUFRUTTO", "tipo": "Patrimoniale attivo"},
            "13.00.000": {"descrizione": "IMMOBILIZZAZIONI MATERIALI", "tipo": "Patrimoniale"},
            "13.01.001": {"descrizione": "TERRENO", "tipo": "Patrimoniale attivo"},
            "13.03.001": {"descrizione": "FABBRICATI CIVILI", "tipo": "Patrimoniale attivo"},
            "13.03.005": {"descrizione": "FABBRICATI INDUSTRIALI", "tipo": "Patrimoniale attivo"},
            "13.05.009": {"descrizione": "IMPIANTO ELETTRICO", "tipo": "Patrimoniale attivo"},
            "13.05.053": {"descrizione": "MACCHINARI", "tipo": "Patrimoniale attivo"},
            "13.07.001": {"descrizione": "ATTREZZATURE INDUSTRIALI", "tipo": "Patrimoniale attivo"},
            "13.07.013": {"descrizione": "STAMPI", "tipo": "Patrimoniale attivo"},
            "13.09.001": {"descrizione": "AUTOVETTURE", "tipo": "Patrimoniale attivo"},
            "13.09.065": {"descrizione": "COMPUTER ED ACCESSORI", "tipo": "Patrimoniale attivo"},
            "13.09.077": {"descrizione": "MOBILI", "tipo": "Patrimoniale attivo"},
            "13.11.001": {"descrizione": "IMMOBILIZZAZIONI MATERIALI IN CORSO", "tipo": "Patrimoniale attivo"},
            "13.11.077": {"descrizione": "FORNITORE C/ACCONTI PER IMMOB. MATERIALI", "tipo": "Patrimoniale attivo"},
            
            # FONDI AMMORTAMENTO
            "07.00.000": {"descrizione": "F.DI AMM.TO IMMOBILIZZAZIONI IMMATERIALI", "tipo": "Patrimoniale passivo"},
            "07.05.001": {"descrizione": "F.DO AMM.TO BREVETTI INDUSTRIALI", "tipo": "Patrimoniale passivo"},
            "07.07.009": {"descrizione": "F.DO AMM.TO MARCHI", "tipo": "Patrimoniale passivo"},
            "07.07.013": {"descrizione": "F.DO AMM.TO SOFTWARE GENERICI", "tipo": "Patrimoniale passivo"},
            "16.00.000": {"descrizione": "F.DI AMM.TO IMMOBILIZZAZIONI MATERIALI", "tipo": "Patrimoniale"},
            "16.01.005": {"descrizione": "F.DO AMM.TO FABBRICATI CIVILI", "tipo": "Patrimoniale passivo"},
            "16.03.009": {"descrizione": "F.DO AMM.TO IMPIANTO ELETTRICO", "tipo": "Patrimoniale passivo"},
            "16.05.001": {"descrizione": "F.DO AMM.TO ATTREZZATURE INDUSTRIALI", "tipo": "Patrimoniale passivo"},
            "16.07.001": {"descrizione": "F.DO AMM.TO AUTOVETTURE", "tipo": "Patrimoniale passivo"},
            "16.07.045": {"descrizione": "F.DO AMM.TO COMPUTER ED ACCESSORI", "tipo": "Patrimoniale passivo"},
            "16.07.057": {"descrizione": "F.DO AMM.TO MOBILI", "tipo": "Patrimoniale passivo"},
            
            # CREDITI
            "22.00.000": {"descrizione": "IMMOBILIZZAZIONI FINANZIARIE", "tipo": "Patrimoniale"},
            "22.17.001": {"descrizione": "CRED. V/CONTROLLATA A", "tipo": "Patrimoniale attivo"},
            "22.23.001": {"descrizione": "CREDITI V. ALTRE IMPRESE A", "tipo": "Patrimoniale attivo"},
            "28.00.000": {"descrizione": "CREDITI", "tipo": "Patrimoniale"},
            "28.01.001": {"descrizione": "CLIENTE", "tipo": "Patrimoniale"},
            "28.11.001": {"descrizione": "CREDITO IRES", "tipo": "Patrimoniale attivo"},
            "28.11.009": {"descrizione": "ERARIO C/IVA", "tipo": "Patrimoniale"},
            "28.15.001": {"descrizione": "CREDITO INAIL C/CONGUAGLIO", "tipo": "Patrimoniale attivo"},
            "28.15.053": {"descrizione": "DIPENDENTI C/ANTICIPI SU RETRIB.", "tipo": "Patrimoniale attivo"},
            
            # DISPONIBILITÀ LIQUIDE
            "34.00.000": {"descrizione": "DISPONIBILITA' LIQUIDE", "tipo": "Patrimoniale"},
            "34.01.001": {"descrizione": "BANCA C/C A", "tipo": "Patrimoniale"},
            "34.01.005": {"descrizione": "BANCA C/C B", "tipo": "Patrimoniale"},
            "34.01.041": {"descrizione": "BANCA C/C VINCOLATO", "tipo": "Patrimoniale attivo"},
            "34.01.045": {"descrizione": "POSTA C/C", "tipo": "Patrimoniale"},
            "34.05.001": {"descrizione": "CASSA CONTANTI", "tipo": "Patrimoniale attivo"},
            
            # RATEI E RISCONTI
            "37.00.000": {"descrizione": "RATEI E RISCONTI", "tipo": "Patrimoniale"},
            "37.01.001": {"descrizione": "RATEI ATTIVI", "tipo": "Patrimoniale attivo"},
            "37.01.005": {"descrizione": "RISCONTI ATTIVI", "tipo": "Patrimoniale attivo"},
            
            # PATRIMONIO NETTO
            "40.00.000": {"descrizione": "PATRIMONIO NETTO", "tipo": "Patrimoniale"},
            "40.01.001": {"descrizione": "CAPITALE SOCIALE", "tipo": "Patrimoniale passivo"},
            "40.07.001": {"descrizione": "RISERVA LEGALE", "tipo": "Patrimoniale passivo"},
            "40.13.001": {"descrizione": "RISERVA STRAORDINARIA(DI UTILI)", "tipo": "Patrimoniale passivo"},
            "40.15.001": {"descrizione": "UTILE D'ESERCIZIO PRECEDENTI", "tipo": "Patrimoniale passivo"},
            "40.17.001": {"descrizione": "UTILE D'ESERCIZIO", "tipo": "Patrimoniale passivo"},
            "40.17.005": {"descrizione": "PERDITE ESERCIZIO", "tipo": "Patrimoniale attivo"},
            
            # FONDI PER RISCHI E ONERI
            "43.00.000": {"descrizione": "FONDI PER RISCHI E ONERI", "tipo": "Patrimoniale"},
            "43.01.001": {"descrizione": "FONDO TRATT. QUIESC. E OBBLIGHI SIMILI", "tipo": "Patrimoniale passivo"},
            "43.03.001": {"descrizione": "F.DO RISCHI SU CAMBI", "tipo": "Patrimoniale passivo"},
            "43.03.005": {"descrizione": "F.DO RISCHI PER CONTROVERSIE LEGALI", "tipo": "Patrimoniale passivo"},
            "43.03.033": {"descrizione": "F.DO GARANZIA PRODOTTI", "tipo": "Patrimoniale passivo"},
            
            # TFR
            "46.00.000": {"descrizione": "TRATTAMENTO TFR", "tipo": "Patrimoniale"},
            "46.01.001": {"descrizione": "FONDO T.F.R.", "tipo": "Patrimoniale passivo"},
            
            # DEBITI
            "49.00.000": {"descrizione": "DEBITI", "tipo": "Patrimoniale"},
            "49.07.001": {"descrizione": "BANCA C/ANTICIPI FATTURE A", "tipo": "Patrimoniale passivo"},
            "49.07.033": {"descrizione": "MUTUO IPOTECARIO((ENTRO ES.SUC.))", "tipo": "Patrimoniale passivo"},
            "49.07.037": {"descrizione": "BANCA C/FINANZIAMENTI", "tipo": "Patrimoniale passivo"},
            "49.11.001": {"descrizione": "ANTICIPI DA CLIENTI", "tipo": "Patrimoniale passivo"},
            "49.13.001": {"descrizione": "FORNITORE", "tipo": "Patrimoniale"},
            "49.13.005": {"descrizione": "FATTURE DA RICEVERE", "tipo": "Patrimoniale passivo"},
            "49.23.001": {"descrizione": "ERARIO C/IRES", "tipo": "Patrimoniale"},
            "49.23.009": {"descrizione": "ERARIO C/IVA", "tipo": "Patrimoniale"},
            "49.23.029": {"descrizione": "ERARIO C/RIT. FISCALI LAVOR. DIPENDENTI", "tipo": "Patrimoniale passivo"},
            "49.25.001": {"descrizione": "DEBITO V./ INPS LAVORO DIPENDENTE", "tipo": "Patrimoniale"},
            "49.25.005": {"descrizione": "DEBITO V./ INAIL", "tipo": "Patrimoniale passivo"},
            "49.27.025": {"descrizione": "DIPENDENTI C/RETRIBUZIONI", "tipo": "Patrimoniale passivo"},
            "49.27.045": {"descrizione": "DIPENDENTI C/FERIE DA LIQUIDARE", "tipo": "Patrimoniale passivo"},
            
            # RATEI E RISCONTI PASSIVI
            "52.00.000": {"descrizione": "RATEI E RISCONTI", "tipo": "Patrimoniale"},
            "52.01.001": {"descrizione": "RATEI PASSIVI", "tipo": "Patrimoniale passivo"},
            "52.01.005": {"descrizione": "RISCONTI PASSIVI", "tipo": "Patrimoniale passivo"},
            
            # RICAVI
            "60.00.000": {"descrizione": "RICAVI DELLE VENDITE E DELLE PRESTAZIONI", "tipo": "Economico"},
            "60.01.001": {"descrizione": "RICAVI DA CESSIONI DI BENI", "tipo": "Economico ricavi"},
            "60.01.005": {"descrizione": "RICAVI DA PRESTAZIONE DI SERVIZI", "tipo": "Economico ricavi"},
            "60.01.009": {"descrizione": "MERCI C/VENDITE", "tipo": "Economico ricavi"},
            "60.01.013": {"descrizione": "PRODOTTI FINITI C/VENDITE", "tipo": "Economico ricavi"},
            
            # VARIAZIONE RIMANENZE
            "63.00.000": {"descrizione": "VAR. RIM. PROD. IN CORSO LAV.SEM. FINITI", "tipo": "Economico"},
            "63.01.001": {"descrizione": "RIM. FIN. PRODOTTI IN CORSO DI LAVORAZ.", "tipo": "Economico ricavi"},
            "63.03.001": {"descrizione": "RIM. INIZ. PRODOTTI IN CORSO DI LAVORAZ.", "tipo": "Economico costi"},
            
            # INCREMENTI IMMOBILIZZAZIONI
            "69.00.000": {"descrizione": "INCREMENTI DI IMMOBILIZ. LAVORI INTERNI", "tipo": "Economico"},
            "69.01.001": {"descrizione": "COSTRUZ. INTER. IMMOB. IMMATERIALI", "tipo": "Economico ricavi"},
            "69.01.037": {"descrizione": "COSTRUZ. INTER. IMMOB. MATERIALI", "tipo": "Economico ricavi"},
            
            # ALTRI RICAVI
            "71.00.000": {"descrizione": "ALTRI RICAVI E PROVENTI", "tipo": "Economico"},
            "71.01.001": {"descrizione": "CANONI DI LOCAZIONE FABBRICATI", "tipo": "Economico ricavi"},
            "71.01.029": {"descrizione": "PROVVIGIONI ATTIVE", "tipo": "Economico ricavi"},
            "71.01.053": {"descrizione": "RISARCIMENTO DANNI", "tipo": "Economico ricavi"},
            "71.01.081": {"descrizione": "CONTRIB. C/CAPITALE", "tipo": "Economico ricavi"},
            "71.01.085": {"descrizione": "CONTRIB. C/ESERCIZIO", "tipo": "Economico ricavi"},
            
            # ACQUISTI
            "73.00.000": {"descrizione": "MATERIE PRIME, SUSS., DI CONSUMO, MERCI", "tipo": "Economico"},
            "73.01.001": {"descrizione": "MATERIE PRIME C/ACQUISTI", "tipo": "Economico costi"},
            "73.01.013": {"descrizione": "MERCI C/ACQUISTI", "tipo": "Economico costi"},
            "73.01.017": {"descrizione": "MATERIALE DI CONSUMO C/ACQUISTI", "tipo": "Economico costi"},
            "73.03.001": {"descrizione": "MATERIE PRIME C/RESI", "tipo": "Economico ricavi"},
            "73.05.001": {"descrizione": "MATERIE PRIME C/SCONTI", "tipo": "Economico ricavi"},
            "73.09.001": {"descrizione": "MATERIALI PER MANUTENZIONI", "tipo": "Economico costi"},
            "73.09.045": {"descrizione": "CANCELLERIA E STAMPATI", "tipo": "Economico costi"},
            "73.09.053": {"descrizione": "TRASPORTI SU ACQUISTI", "tipo": "Economico costi"},
            
            # COSTI PER SERVIZI
            "75.00.000": {"descrizione": "COSTI PER SERVIZI", "tipo": "Economico"},
            "75.01.001": {"descrizione": "SERVIZI PER ACQUISTI", "tipo": "Economico costi"},
            "75.01.005": {"descrizione": "TRASPORTI", "tipo": "Economico costi"},
            "75.01.025": {"descrizione": "ENERGIA ELETTRICA", "tipo": "Economico costi"},
            "75.01.041": {"descrizione": "CONSULENZE TECNICHE", "tipo": "Economico costi"},
            "75.05.001": {"descrizione": "MANUT. FABBRICATI", "tipo": "Economico costi"},
            "75.05.017": {"descrizione": "MANUTENZIONI IMPIANTIE MACCHINARI", "tipo": "Economico costi"},
            "75.05.065": {"descrizione": "MANUT. MACCHINARI", "tipo": "Economico costi"},
            "75.05.105": {"descrizione": "MANUT. AUTOVETTURE", "tipo": "Economico costi"},
            "75.05.145": {"descrizione": "MANUT. COMPUTER ED ACCESSORI", "tipo": "Economico costi"},
            "75.11.001": {"descrizione": "CONSULENZE AMMINISTRATIVE", "tipo": "Economico costi"},
            "75.11.017": {"descrizione": "COMPENSI AMMINISTRATORE", "tipo": "Economico costi"},
            "75.11.073": {"descrizione": "COMPENSI PER COLLAB. A PROGETTO", "tipo": "Economico costi"},
            "75.11.113": {"descrizione": "SPESE TELEFONICHE", "tipo": "Economico costi"},
            "75.13.009": {"descrizione": "PROVVIGIONI A INTERMEDIARI", "tipo": "Economico costi"},
            "75.13.037": {"descrizione": "SPESE DI PUBBLICITA", "tipo": "Economico costi"},
            "75.15.001": {"descrizione": "ASSICURAZIONI", "tipo": "Economico costi"},
            "75.15.005": {"descrizione": "ASSICURAZIONI AUTO", "tipo": "Economico costi"},
            "75.17.009": {"descrizione": "SPESE DI PULIZIA ESTERNI", "tipo": "Economico costi"},
            "75.17.033": {"descrizione": "VIAGGI(FERROVIA, AEREO, AUTO ECC.)", "tipo": "Economico costi"},
            "75.17.041": {"descrizione": "SPESE DI RAPPRESENTANZA", "tipo": "Economico costi"},
            "75.17.081": {"descrizione": "SPESE PER SERVIZI BANCARI", "tipo": "Economico costi"},
            
            # CANONI DI LOCAZIONE E LEASING
            "77.00.000": {"descrizione": "COSTI PER GODIMENTO DI BENI DI TERZI", "tipo": "Economico"},
            "77.01.001": {"descrizione": "CANONE LOCAZIONE TERRENO AGRICOLO", "tipo": "Economico costi"},
            "77.01.009": {"descrizione": "CANONE LOCAZIONE FABBRICATI CIVILI", "tipo": "Economico costi"},
            "77.03.001": {"descrizione": "CANONI LEASING", "tipo": "Economico costi"},
            "77.05.001": {"descrizione": "CANONI NOLEGGIO", "tipo": "Economico costi"},
            "77.07.001": {"descrizione": "ROYALTIES", "tipo": "Economico costi"},
            
            # COSTO DEL PERSONALE
            "79.00.000": {"descrizione": "COSTO PER IL PERSONALE", "tipo": "Economico"},
            "79.01.001": {"descrizione": "SALARI", "tipo": "Economico costi"},
            "79.01.005": {"descrizione": "STIPENDI IMPIEGATI", "tipo": "Economico costi"},
            "79.03.001": {"descrizione": "ONERI INPS", "tipo": "Economico costi"},
            "79.03.005": {"descrizione": "ONERI INAIL", "tipo": "Economico costi"},
            "79.05.001": {"descrizione": "ACC.TO FONDO TFR", "tipo": "Economico costi"},
            "79.05.005": {"descrizione": "QUOTA TFR MATURATA NELL'ANNO", "tipo": "Economico costi"},
            
            # AMMORTAMENTI
            "81.00.000": {"descrizione": "AMMOR.TO DELLE IMMOBILIZ. IMMATERIALI", "tipo": "Economico"},
            "81.01.001": {"descrizione": "AMM.TO SPESE DI IMPIANTO", "tipo": "Economico costi"},
            "81.05.001": {"descrizione": "AMM.TO BREVETTI INDUSTRIALI", "tipo": "Economico costi"},
            "81.07.001": {"descrizione": "AMM.TO CONCESSIONI", "tipo": "Economico costi"},
            "81.07.005": {"descrizione": "AMM.TO LICENZE", "tipo": "Economico costi"},
            "81.07.009": {"descrizione": "AMM.TO MARCHI", "tipo": "Economico costi"},
            "81.07.013": {"descrizione": "AMM.TO SOFTWARE GENERICO", "tipo": "Economico costi"},
            "81.09.001": {"descrizione": "AMM.TO AVVIAMENTO", "tipo": "Economico costi"},
            
            "83.00.000": {"descrizione": "AMMORTAMENTO DELLE IMMOBILIZ. MATERIALI", "tipo": "Economico"},
            "83.03.001": {"descrizione": "AMM.TO FABBRICATI CIVILI", "tipo": "Economico costi"},
            "83.05.001": {"descrizione": "AMM.TO IMPIANTI GENERICI", "tipo": "Economico costi"},
            "83.05.009": {"descrizione": "AMM.TO IMPIANTO ELETTRICO", "tipo": "Economico costi"},
            "83.07.001": {"descrizione": "AMM.TO ATTREZZATURE INDUSTRIALI", "tipo": "Economico costi"},
            "83.09.001": {"descrizione": "AMM.TO AUTOVETTURE", "tipo": "Economico costi"},
            "83.09.065": {"descrizione": "AMM.TO COMPUTER ED ACCESSORI", "tipo": "Economico costi"},
            "83.09.077": {"descrizione": "AMM.TO MOBILI", "tipo": "Economico costi"},
            
            # SVALUTAZIONI
            "85.00.000": {"descrizione": "ALTRE SVALUTAZIONI DELLE IMMOBILIZ.", "tipo": "Economico"},
            "85.05.001": {"descrizione": "SVALUT. BREVETTI INDUSTRIALI", "tipo": "Economico costi"},
            "85.07.009": {"descrizione": "SVALUT. MARCHI", "tipo": "Economico costi"},
            "85.13.009": {"descrizione": "SVALUT. FABBRICATI CIVILI", "tipo": "Economico costi"},
            "85.15.009": {"descrizione": "SVALUT. IMPIANTO ELETTRICO", "tipo": "Economico costi"},
            "85.17.009": {"descrizione": "SVALUT. ATTREZZATURE INDUSTRIALI", "tipo": "Economico costi"},
            "85.18.001": {"descrizione": "SVALUT. AUTOVETTURE", "tipo": "Economico costi"},
            
            # VARIAZIONE RIMANENZE MATERIALI
            "89.00.000": {"descrizione": "VAR. RIM. M/PRIME,SUSSID.,DI CONS.,MERCI", "tipo": "Economico"},
            "89.01.001": {"descrizione": "RIM. INIZ. MATERIE PRIME", "tipo": "Economico costi"},
            "89.01.013": {"descrizione": "RIM. INIZ. MERCI", "tipo": "Economico costi"},
            "89.02.001": {"descrizione": "RIM. FIN. MATERIE PRIME", "tipo": "Economico ricavi"},
            "89.02.013": {"descrizione": "RIM. FIN. MERCI", "tipo": "Economico ricavi"},
            
            # ACCANTONAMENTI
            "90.00.000": {"descrizione": "ACCANTONAMENTI PER RISCHI", "tipo": "Economico"},
            "90.01.001": {"descrizione": "ACC.TO F/RISC. COLL. MESSA IN FUNZ.BENI", "tipo": "Economico costi"},
            "90.01.005": {"descrizione": "ACC.TO F.DO RISCHIO DI GARANZIA", "tipo": "Economico costi"},
            "90.01.033": {"descrizione": "ACC.TO F/RISCHI CONTR. LEGALI IN CORSO", "tipo": "Economico costi"},
            
            # ONERI DIVERSI
            "92.00.000": {"descrizione": "ONERI DIVERSI DI GESTIONE", "tipo": "Economico"},
            "92.01.001": {"descrizione": "IMPOSTA DI BOLLO", "tipo": "Economico costi"},
            "92.01.005": {"descrizione": "IMU", "tipo": "Economico costi"},
            "92.01.013": {"descrizione": "IMPOSTA DI REGISTRO", "tipo": "Economico costi"},
            "92.01.025": {"descrizione": "IVA INDETRAIBILE", "tipo": "Economico costi"},
            "92.01.037": {"descrizione": "TASSE PROP. AUTOV.", "tipo": "Economico costi"},
            "92.01.097": {"descrizione": "PERDITE SU CREDITI", "tipo": "Economico costi"},
            "92.01.105": {"descrizione": "ABBONAMENTI RIVISTE E GIORNALI", "tipo": "Economico costi"},
            "92.01.113": {"descrizione": "MULTE E AMMENDE", "tipo": "Economico costi"},
            
            # PROVENTI E ONERI FINANZIARI
            "93.00.000": {"descrizione": "C) PROVENTI E ONERI FINANZIARI", "tipo": "Economico"},
            "93.01.001": {"descrizione": "DIVIDENDI DA IMPR. CONTROLL.(SOGG.IRES)", "tipo": "Economico ricavi"},
            "93.07.001": {"descrizione": "INTERESSI V/IMPR. CONTROLLATE", "tipo": "Economico ricavi"},
            "93.09.001": {"descrizione": "INTERESSI SU BOT", "tipo": "Economico ricavi"},
            "93.09.005": {"descrizione": "INTERESSI SU BTP", "tipo": "Economico ricavi"},
            "93.13.001": {"descrizione": "INTERESSI ATT. C/C BANCARI", "tipo": "Economico ricavi"},
            "93.13.057": {"descrizione": "SCONTI FINANZIARI ATTIVI", "tipo": "Economico ricavi"},
            "93.15.001": {"descrizione": "INTERESSI PASS. V/IMPR. CONTROLLATE", "tipo": "Economico costi"},
            "93.15.021": {"descrizione": "INTERESSI PASS. SUI DEBITI VERSO BANCHE", "tipo": "Economico costi"},
            "93.15.025": {"descrizione": "INTERESSI PASS. MUTUI", "tipo": "Economico costi"},
            "93.15.061": {"descrizione": "SCONTI E ALTRI ONERI FINANZIARI", "tipo": "Economico costi"},
            "93.15.081": {"descrizione": "COMMISSIONE MAX SCOPERTO", "tipo": "Economico costi"},
            "93.17.001": {"descrizione": "UTILI SU CAMBI", "tipo": "Economico ricavi"},
            "93.17.005": {"descrizione": "PERDITE SU CAMBI", "tipo": "Economico costi"},
            
            # RETTIFICHE VALORE ATTIVITÀ FINANZIARIE
            "94.00.000": {"descrizione": "D ) RETTIFICHE DI VALORE ATT. FINANZIARIE", "tipo": "Economico"},
            "94.01.001": {"descrizione": "RIV. PART. IMPR. COLLEGATE", "tipo": "Economico ricavi"},
            "94.07.001": {"descrizione": "SVAL. PART. IMPR. COLLEGATE", "tipo": "Economico costi"},
            
            # PROVENTI E ONERI STRAORDINARI
            "95.00.000": {"descrizione": "E) PROVENTI E ONERI STRAORDINARI:", "tipo": "Economico"},
            "95.01.001": {"descrizione": "PLUSVALENZE IMMOBILIZ. IMMATERIALI", "tipo": "Economico ricavi"},
            "95.01.005": {"descrizione": "PLUSVALENZE IMMOBILIZ. MATERIALI", "tipo": "Economico ricavi"},
            "95.01.041": {"descrizione": "SOPRAVV. ATTIVE", "tipo": "Economico ricavi"},
            "95.03.001": {"descrizione": "MINUSV. IMMOBILIZ. IMMATERIALI", "tipo": "Economico costi"},
            "95.03.005": {"descrizione": "MINUSV. IMMOBILIZ. MATERIALI", "tipo": "Economico costi"},
            "95.03.045": {"descrizione": "SOPRAVV. PASSIVE", "tipo": "Economico costi"},
            
            # IMPOSTE
            "96.00.000": {"descrizione": "20) IMPOSTE CORRENTI, DIFFERITE E ANTIC.", "tipo": "Economico"},
            "96.01.001": {"descrizione": "IRES", "tipo": "Economico costi"},
            "96.01.005": {"descrizione": "IRAP", "tipo": "Economico costi"},
        }
    
    def get_conto(self, codice: str) -> dict:
        """Restituisce i dati del conto"""
        return self.conti.get(codice, {"descrizione": "CONTO NON TROVATO", "tipo": ""})
    
    def exists(self, codice: str) -> bool:
        """Verifica se il conto esiste"""
        return codice in self.conti


class ScritturaContabile:
    """Rappresenta una scrittura contabile"""
    
    def __init__(self, data: str, descrizione: str):
        self.data = data
        self.descrizione = descrizione
        self.righe: List[Dict] = []
    
    def aggiungi_riga(self, conto: str, dare_ave: str, importo: float, piano_conti: PianoDeiConti):
        """Aggiunge una riga alla scrittura"""
        if not piano_conti.exists(conto):
            raise ValueError(f"Conto {conto} non esiste nel piano dei conti!")
        
        self.righe.append({
            "conto": conto,
            "descrizione": piano_conti.get_conto(conto)["descrizione"],
            "dare_ave": dare_ave,
            "importo": importo
        })
    
    def verifica_bilanciamento(self) -> bool:
        """Verifica se la scrittura è bilanciata"""
        totale_dare = sum(r["importo"] for r in self.righe if r["dare_ave"] == "D")
        totale_ave = sum(r["importo"] for r in self.righe if r["dare_ave"] == "A")
        return abs(totale_dare - totale_ave) < 0.01
    
    def stampa(self):
        """Stampa la scrittura formattata"""
        print(f"\n{'='*80}")
        print(f"Data: {self.data}")
        print(f"Descrizione: {self.descrizione}")
        print(f"{'='*80}")
        print(f"{'Conto':<12} {'Descrizione':<50} {'D/A':<4} {'Importo':>12}")
        print(f"{'-'*80}")
        
        for riga in self.righe:
            print(f"{riga['conto']:<12} {riga['descrizione']:<50} {riga['dare_ave']:<4} {riga['importo']:>12,.2f}")
        
        print(f"{'-'*80}")
        totale_dare = sum(r["importo"] for r in self.righe if r["dare_ave"] == "D")
        totale_ave = sum(r["importo"] for r in self.righe if r["dare_ave"] == "A")
        print(f"{'TOTALE DARE':<68} {totale_dare:>12,.2f}")
        print(f"{'TOTALE AVERE':<68} {totale_ave:>12,.2f}")
        
        if self.verifica_bilanciamento():
            print("✓ Scrittura BILANCIATA")
        else:
            print("✗ Scrittura NON BILANCIATA!")
        print(f"{'='*80}\n")


class GeneratoreScritture:
    """Genera scritture contabili per diverse operazioni"""
    
    def __init__(self):
        self.piano_conti = PianoDeiConti()
        self.scritture: List[ScritturaContabile] = []
    
    def acquisto_immobilizzazione_materiale(self, data: str, conto_immobilizzazione: str, 
                                          importo_imponibile: float, iva_percentuale: float = 22.0,
                                          split_payment: bool = False):
        """Genera scrittura per acquisto immobilizzazione materiale"""
        importo_iva = importo_imponibile * (iva_percentuale / 100)
        importo_totale = importo_imponibile + importo_iva
        
        descrizione_op = f"Acquisto immobilizzazione - {self.piano_conti.get_conto(conto_immobilizzazione)['descrizione']}"
        if split_payment:
            descrizione_op += " (Split Payment)"
            
        scrittura = ScritturaContabile(data, descrizione_op)
        
        if split_payment:
            # Split payment: Il costo è al netto, l'IVA viene gestita tramite compensazione Erario
            scrittura.aggiungi_riga(conto_immobilizzazione, "D", importo_imponibile, self.piano_conti)
            scrittura.aggiungi_riga("28.11.009", "D", importo_iva, self.piano_conti)  # IVA a credito (Split)
            scrittura.aggiungi_riga("49.13.001", "A", importo_imponibile, self.piano_conti)  # Debiti v/fornitori (Netto)
            scrittura.aggiungi_riga("49.23.009", "A", importo_iva, self.piano_conti)  # Erario c/IVA (Debito compensato)
        else:
            # IVA ordinaria
            scrittura.aggiungi_riga(conto_immobilizzazione, "D", importo_totale, self.piano_conti)
            scrittura.aggiungi_riga("49.13.001", "A", importo_totale, self.piano_conti)  # Debiti v/fornitori
        
        self.scritture.append(scrittura)
        return scrittura
    
    def pagamento_fornitore(self, data: str, importo: float):
        """Genera scrittura per pagamento fornitore"""
        scrittura = ScritturaContabile(data, "Pagamento fornitore")
        scrittura.aggiungi_riga("49.13.001", "D", importo, self.piano_conti)  # Debiti v/fornitori
        scrittura.aggiungi_riga("34.01.001", "A", importo, self.piano_conti)  # Banca c/c
        self.scritture.append(scrittura)
        return scrittura
    
    def ammortamento(self, data: str, conto_ammortamento: str, conto_fondo_ammortamento: str, importo: float):
        """Genera scrittura per ammortamento"""
        scrittura = ScritturaContabile(data, f"Ammortamento - {self.piano_conti.get_conto(conto_ammortamento)['descrizione']}")
        scrittura.aggiungi_riga(conto_ammortamento, "D", importo, self.piano_conti)
        scrittura.aggiungi_riga(conto_fondo_ammortamento, "A", importo, self.piano_conti)
        self.scritture.append(scrittura)
        return scrittura
    
    def acquisto_materiali_consumo(self, data: str, importo_imponibile: float, iva_percentuale: float = 22.0,
                                   split_payment: bool = False):
        """Genera scrittura per acquisto materiali di consumo"""
        importo_iva = importo_imponibile * (iva_percentuale / 100)
        importo_totale = importo_imponibile + importo_iva
        
        scrittura = ScritturaContabile(data, "Acquisto materiali di consumo")
        
        if split_payment:
            # Split Payment logic corretta
            scrittura.aggiungi_riga("73.01.017", "D", importo_imponibile, self.piano_conti)  # Materiali consumo (Netto)
            scrittura.aggiungi_riga("28.11.009", "D", importo_iva, self.piano_conti)  # IVA a credito
            scrittura.aggiungi_riga("49.13.001", "A", importo_imponibile, self.piano_conti)  # Debiti v/fornitori
            scrittura.aggiungi_riga("49.23.009", "A", importo_iva, self.piano_conti)  # Erario c/IVA
        else:
            scrittura.aggiungi_riga("73.01.017", "D", importo_totale, self.piano_conti)
            scrittura.aggiungi_riga("49.13.001", "A", importo_totale, self.piano_conti)
        
        self.scritture.append(scrittura)
        return scrittura
    
    def liquidazione_stipendi(self, data: str, importo_lordo: float, ritenute_irpef: float, 
                             contributi_inps_dipendente: float, contributi_inail: float = 0):
        """Genera scrittura per liquidazione stipendi"""
        importo_netto = importo_lordo - ritenute_irpef - contributi_inps_dipendente
        
        scrittura = ScritturaContabile(data, "Liquidazione stipendi")
        
        # Dare: Stipendi Lordi
        scrittura.aggiungi_riga("79.01.005", "D", importo_lordo, self.piano_conti)
        
        # Dare: Oneri INAIL a carico azienda (se presenti)
        if contributi_inail > 0:
            scrittura.aggiungi_riga("79.03.005", "D", contributi_inail, self.piano_conti)
        
        # Avere: Netto al dipendente
        scrittura.aggiungi_riga("49.27.025", "A", importo_netto, self.piano_conti)
        
        # Avere: Ritenute IRPEF
        scrittura.aggiungi_riga("49.23.029", "A", ritenute_irpef, self.piano_conti)
        
        # Avere: Contributi INPS dipendente
        scrittura.aggiungi_riga("49.25.001", "A", contributi_inps_dipendente, self.piano_conti)
        
        # Avere: Debito INAIL
        if contributi_inail > 0:
            scrittura.aggiungi_riga("49.25.005", "A", contributi_inail, self.piano_conti)
        
        self.scritture.append(scrittura)
        return scrittura
    
    def accantonamento_tfr(self, data: str, importo: float):
        """Genera scrittura per accantonamento TFR"""
        scrittura = ScritturaContabile(data, "Accantonamento TFR")
        scrittura.aggiungi_riga("79.05.001", "D", importo, self.piano_conti)  # Acc.to fondo TFR
        scrittura.aggiungi_riga("46.01.001", "A", importo, self.piano_conti)  # Fondo TFR
        self.scritture.append(scrittura)
        return scrittura
    
    def fattura_da_ricevere(self, data: str, conto_costo: str, importo_imponibile: float, 
                           iva_percentuale: float = 22.0, split_payment: bool = False):
        """Genera scrittura per fatture da ricevere"""
        importo_iva = importo_imponibile * (iva_percentuale / 100)
        importo_totale = importo_imponibile + importo_iva
        
        scrittura = ScritturaContabile(data, f"Fatture da ricevere - {self.piano_conti.get_conto(conto_costo)['descrizione']}")
        
        if split_payment:
            scrittura.aggiungi_riga(conto_costo, "D", importo_imponibile, self.piano_conti)
            scrittura.aggiungi_riga("28.11.009", "D", importo_iva, self.piano_conti)
            scrittura.aggiungi_riga("49.13.005", "A", importo_imponibile, self.piano_conti)  # Fatture da ricevere
            scrittura.aggiungi_riga("49.23.009", "A", importo_iva, self.piano_conti)
        else:
            scrittura.aggiungi_riga(conto_costo, "D", importo_totale, self.piano_conti)
            scrittura.aggiungi_riga("49.13.005", "A", importo_totale, self.piano_conti)
        
        self.scritture.append(scrittura)
        return scrittura
    
    def vendita_servizi(self, data: str, importo_imponibile: float, iva_percentuale: float = 22.0):
        """Genera scrittura per vendita servizi"""
        importo_iva = importo_imponibile * (iva_percentuale / 100)
        importo_totale = importo_imponibile + importo_iva
        
        scrittura = ScritturaContabile(data, "Vendita servizi")
        scrittura.aggiungi_riga("28.01.001", "D", importo_totale, self.piano_conti)  # Crediti v/clienti
        scrittura.aggiungi_riga("60.01.005", "A", importo_imponibile, self.piano_conti)  # Ricavi servizi
        scrittura.aggiungi_riga("49.23.009", "A", importo_iva, self.piano_conti)  # Erario c/IVA
        self.scritture.append(scrittura)
        return scrittura
    
    def incasso_credito(self, data: str, importo: float):
        """Genera scrittura per incasso credito"""
        scrittura = ScritturaContabile(data, "Incasso credito")
        scrittura.aggiungi_riga("34.01.001", "D", importo, self.piano_conti)  # Banca c/c
        scrittura.aggiungi_riga("28.01.001", "A", importo, self.piano_conti)  # Crediti v/clienti
        self.scritture.append(scrittura)
        return scrittura
    
    def risconto_attivo(self, data: str, conto_costo: str, importo: float):
        """Genera scrittura per risconto attivo"""
        scrittura = ScritturaContabile(data, f"Risconto attivo - {self.piano_conti.get_conto(conto_costo)['descrizione']}")
        scrittura.aggiungi_riga("37.01.005", "D", importo, self.piano_conti)  # Risconti attivi
        scrittura.aggiungi_riga(conto_costo, "A", importo, self.piano_conti)
        self.scritture.append(scrittura)
        return scrittura
    
    def risconto_passivo(self, data: str, conto_ricavo: str, importo: float):
        """Genera scrittura per risconto passivo"""
        scrittura = ScritturaContabile(data, f"Risconto passivo - {self.piano_conti.get_conto(conto_ricavo)['descrizione']}")
        scrittura.aggiungi_riga(conto_ricavo, "D", importo, self.piano_conti)
        scrittura.aggiungi_riga("52.01.005", "A", importo, self.piano_conti)  # Risconti passivi
        self.scritture.append(scrittura)
        return scrittura
    
    def rateo_attivo(self, data: str, conto_ricavo: str, importo: float):
        """Genera scrittura per rateo attivo"""
        scrittura = ScritturaContabile(data, f"Rateo attivo - {self.piano_conti.get_conto(conto_ricavo)['descrizione']}")
        scrittura.aggiungi_riga("37.01.001", "D", importo, self.piano_conti)  # Ratei attivi
        scrittura.aggiungi_riga(conto_ricavo, "A", importo, self.piano_conti)
        self.scritture.append(scrittura)
        return scrittura
    
    def rateo_passivo(self, data: str, conto_costo: str, importo: float):
        """Genera scrittura per rateo passivo"""
        scrittura = ScritturaContabile(data, f"Rateo passivo - {self.piano_conti.get_conto(conto_costo)['descrizione']}")
        scrittura.aggiungi_riga(conto_costo, "D", importo, self.piano_conti)
        scrittura.aggiungi_riga("52.01.001", "A", importo, self.piano_conti)  # Ratei passivi
        self.scritture.append(scrittura)
        return scrittura
    
    def accantonamento_fondo_rischi(self, data: str, descrizione: str, conto_accantonamento: str, 
                                   conto_fondo: str, importo: float):
        """Genera scrittura per accantonamento a fondo rischi"""
        scrittura = ScritturaContabile(data, f"Accantonamento {descrizione}")
        scrittura.aggiungi_riga(conto_accantonamento, "D", importo, self.piano_conti)
        scrittura.aggiungi_riga(conto_fondo, "A", importo, self.piano_conti)
        self.scritture.append(scrittura)
        return scrittura
    
    def plusvalenza(self, data: str, conto_immobilizzazione: str, conto_fondo_ammortamento: str, 
                   valore_netto_contabile: float, prezzo_vendita: float, costo_storico: float):
        """Genera scrittura per plusvalenza da alienazione"""
        # Valore netto contabile = Costo Storico - Fondo Ammortamento
        # Per semplificare, assumiamo che valore_netto_contabile sia il valore da stornare dal fondo
        # e costo_storico sia il valore da stornare dal cespite.
        
        plusvalenza = prezzo_vendita - valore_netto_contabile
        
        scrittura = ScritturaContabile(data, f"Plusvalenza da alienazione")
        
        # Dare: Crediti diversi (Prezzo di vendita)
        scrittura.aggiungi_riga("28.15.001", "D", prezzo_vendita, self.piano_conti)
        
        # Dare: Fondo Ammortamento (Storno fondo accumulato)
        # Nota: Qui servirebbe il saldo del fondo, assumiamo sia passato correttamente o calcolato
        # Per questo esempio, assumiamo valore_netto_contabile sia il netto, quindi il fondo è (Costo - Netto)
        fondo_da_stornare = costo_storico - valore_netto_contabile
        if fondo_da_stornare > 0:
            scrittura.aggiungi_riga(conto_fondo_ammortamento, "D", fondo_da_stornare, self.piano_conti)
            
        # Avere: Immobilizzazione (Storno costo storico)
        scrittura.aggiungi_riga(conto_immobilizzazione, "A", costo_storico, self.piano_conti)
        
        # Avere: Plusvalenza
        if plusvalenza > 0:
            scrittura.aggiungi_riga("95.01.005", "A", plusvalenza, self.piano_conti)
        elif plusvalenza < 0:
            # Se c'è una minusvalenza, va a Dare
            scrittura.aggiungi_riga("95.03.005", "D", abs(plusvalenza), self.piano_conti)
            
        self.scritture.append(scrittura)
        return scrittura
    
    def stampa_tutte_scritture(self):
        """Stampa tutte le scritture generate"""
        print(f"\n{'#'*80}")
        print(f"# TOTALE SCRITTURE GENERATE: {len(self.scritture)}")
        print(f"{'#'*80}\n")
        
        for scrittura in self.scritture:
            scrittura.stampa()
    
    def esporta_json(self, filename: str = "scritture_contabili.json"):
        """Esporta le scritture in formato JSON"""
        dati = {
            "data_generazione": datetime.now().isoformat(),
            "totale_scritture": len(self.scritture),
            "scritture": []
        }
        
        for scrittura in self.scritture:
            dati_scrittura = {
                "data": scrittura.data,
                "descrizione": scrittura.descrizione,
                "righe": scrittura.righe,
                "bilanciata": scrittura.verifica_bilanciamento()
            }
            dati["scritture"].append(dati_scrittura)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dati, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Scritture esportate in {filename}")


def demo_completa():
    """Dimostrazione completa del funzionamento"""
    print("="*80)
    print(" SISTEMA DI GENERAZIONE SCRITTURE CONTABILI - UNIVERSITÀ")
    print(" Basato sul Manuale Tecnico Operativo")
    print("="*80)
    
    generatore = GeneratoreScritture()
    
    print("\n[1] Acquisto immobilizzazioni materiali (Split Payment)")
    generatore.acquisto_immobilizzazione_materiale(
        data="2024-03-15",
        conto_immobilizzazione="13.09.065",  # Computer ed accessori
        importo_imponibile=10000.00,
        iva_percentuale=22.0,
        split_payment=True
    )
    
    print("[2] Acquisto materiali di consumo (Split Payment)")
    generatore.acquisto_materiali_consumo(
        data="2024-03-20",
        importo_imponibile=5000.00,
        iva_percentuale=22.0,
        split_payment=True
    )
    
    print("[3] Liquidazione stipendi (Con INAIL)")
    generatore.liquidazione_stipendi(
        data="2024-03-31",
        importo_lordo=50000.00,
        ritenute_irpef=12500.00,
        contributi_inps_dipendente=4500.00,
        contributi_inail=500.00
    )
    
    print("[4] Accantonamento TFR")
    generatore.accantonamento_tfr(
        data="2024-03-31",
        importo=3703.70
    )
    
    print("[5] Ammortamento immobilizzazioni")
    generatore.ammortamento(
        data="2024-12-31",
        conto_ammortamento="83.09.065",  # Amm.to computer
        conto_fondo_ammortamento="16.07.045",  # Fondo amm.to computer
        importo=2500.00
    )
    
    print("[6] Vendita servizi")
    generatore.vendita_servizi(
        data="2024-04-10",
        importo_imponibile=15000.00,
        iva_percentuale=22.0
    )
    
    print("[7] Fatture da ricevere (Split Payment)")
    generatore.fattura_da_ricevere(
        data="2024-12-31",
        conto_costo="75.11.001",  # Consulenze amministrative
        importo_imponibile=8000.00,
        iva_percentuale=22.0,
        split_payment=True
    )
    
    print("[8] Risconti attivi")
    generatore.risconto_attivo(
        data="2024-12-31",
        conto_costo="77.03.001",  # Canoni leasing
        importo=3000.00
    )
    
    print("[9] Risconti passivi")
    generatore.risconto_passivo(
        data="2024-12-31",
        conto_ricavo="71.01.085",  # Contributi c/esercizio
        importo=5000.00
    )
    
    print("[10] Ratei attivi")
    generatore.rateo_attivo(
        data="2024-12-31",
        conto_ricavo="93.13.001",  # Interessi attivi c/c
        importo=1200.00
    )
    
    print("[11] Ratei passivi")
    generatore.rateo_passivo(
        data="2024-12-31",
        conto_costo="77.01.009",  # Canoni locazione
        importo=2000.00
    )
    
    print("[12] Accantonamento fondo rischi")
    generatore.accantonamento_fondo_rischi(
        data="2024-12-31",
        descrizione="Fondo rischi contenzioso",
        conto_accantonamento="90.01.033",  # Acc.to rischi legali
        conto_fondo="43.03.005",  # Fondo rischi controversie
        importo=10000.00
    )
    
    # Stampa tutte le scritture
    generatore.stampa_tutte_scritture()
    
    # Esporta in JSON
    generatore.esporta_json("scritture_contabili.json")
    
    return generatore

if __name__ == "__main__":
    generatore = demo_completa()
    
    print("\n" + "="*80)
    print(" OPERAZIONI DISPONIBILI:")
    print("="*80)
    print("1. Acquisto immobilizzazione materiale")
    print("2. Acquisto materiali di consumo")
    print("3. Liquidazione stipendi")
    print("4. Accantonamento TFR")
    print("5. Ammortamento")
    print("6. Vendita servizi")
    print("7. Fatture da ricevere")
    print("8. Risconto attivo/passivo")
    print("9. Rateo attivo/passivo")
    print("10. Accantonamento fondo rischi")
    print("="*80)
