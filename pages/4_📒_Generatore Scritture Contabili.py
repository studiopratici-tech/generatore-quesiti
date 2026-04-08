import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import io

# ==============================================================================
# CONFIGURAZIONE
# ==============================================================================
st.set_page_config(layout="wide", page_title="Generatore Contabile Professionale | Ranocchi GIS", page_icon="")

# ==============================================================================
# 1. PARSER PDF & CLASSIFICATORE PIANO DEI CONTI
# ==============================================================================
@st.cache_data(ttl=3600)
def parse_piano_conti(pdf_file) -> Dict[str, Dict]:
    """Estrae e classifica tutti i conti dal PDF Ranocchi"""
    conti = {}
    try:
        with pdfplumber.open(pdf_file) as pdf:
            testo_completo = "\n".join(page.extract_text() or "" for page in pdf.pages)
        
        # Pulizia base
        testo = re.sub(r'\s+', ' ', testo_completo)
        
        # Pattern robusto per: CODICE  DESCRIZIONE  POSIZIONE
        pattern = r'(\d{2}\.\d{2}\.\d{3})\s+(.*?)\s+(Patrimoniale\s*(?:attivo|passivo)?|Economico\s*(?:costi|ricavi)?|Conto\s*d\'ordine)'
        
        for m in re.finditer(pattern, testo, re.IGNORECASE):
            codice, descrizione, posizione = m.groups()
            posizione = posizione.strip()
            
            # Classificazione automatica
            pos_lower = posizione.lower()
            if 'patrimoniale' in pos_lower:
                tipo_bilancio = 'Patrimoniale'
                sotto_tipo = 'Attivo' if 'attivo' in pos_lower else 'Passivo'
                normale = 'dare' if 'attivo' in pos_lower else 'avere'
            elif 'economico' in pos_lower:
                tipo_bilancio = 'Economico'
                sotto_tipo = 'Costi' if 'costi' in pos_lower else 'Ricavi'
                normale = 'dare' if 'costi' in pos_lower else 'avere'
            else:
                tipo_bilancio = 'Conto d\'Ordine'
                sotto_tipo = 'Ordine'
                normale = 'dare'
            
            # Macro-categoria per regole contabili
            macro = _determina_macro_categoria(codice, descrizione)
            
            conti[codice] = {
                'descrizione': descrizione.strip().title(),
                'tipo_bilancio': tipo_bilancio,
                'sotto_tipo': sotto_tipo,
                'normale': normale,
                'macro': macro,
                'posizione': posizione
            }
    except Exception as e:
        st.error(f"Errore parsing PDF: {e}")
    return conti

def _determina_macro_categoria(codice: str, desc: str) -> str:
    """Mappa codice/descrizione a macro-categoria contabile"""
    prefix = codice[:2]
    desc_lower = desc.lower()
    
    if prefix in ['01']: return 'crediti_soci'
    if prefix in ['04', '07', '10']: return 'imm_materiali'
    if prefix in ['13', '16', '19']: return 'imm_materiali'
    if prefix in ['22', '25', '28', '31', '34']: return 'attivita_circolanti'
    if prefix in ['40']: return 'patrimonio_netto'
    if prefix in ['43', '46', '49']: return 'passivita_fondi_debiti'
    if prefix in ['58']: return 'conti_ordine'
    if prefix in ['60', '71', '93', '94', '95']: return 'ricavi_proventi'
    if prefix in ['73', '75', '77', '79', '81', '83', '85', '87', '89', '90', '91', '92', '96']: return 'costi_oneri'
    if 'f.do amm' in desc_lower or 'amm.to' in desc_lower: return 'ammortamenti'
    if 'iva' in desc_lower: return 'iva'
    if 'tfr' in desc_lower: return 'tfr'
    return 'altro'

# ==============================================================================
# 2. REGISTRO OPERAZIONI CONCRETE (60+ CASI)
# ==============================================================================
REGISTRO_OPERAZIONI = [
    # === DOCUMENTI COMMERCIALI ===
    {"id": "ACQ_MERCI_IT", "nome": "Acquisto merci Italia (Fattura)", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Imponibile + IVA 22%/10%/4%. Contropartita: Fornitore.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "totale"}]},
    {"id": "VEND_MERCI_IT", "nome": "Vendita merci Italia (Fattura)", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Totale a cliente. Imponibile a ricavi + IVA a debito.",
     "dare": [{"macro": "attivita_circolanti", "a": "totale"}],
     "avere": [{"macro": "ricavi_proventi", "a": "imponibile"}, {"macro": "iva", "a": "iva"}]},
    {"id": "ACQ_SERVIZI_IT", "nome": "Acquisto servizi/consulenze Italia", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Conto costo servizi + IVA credito. Fornitore AVERE.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "totale"}]},
    {"id": "VEND_SERVIZI_IT", "nome": "Vendita servizi/prestazioni Italia", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Cliente DARE totale. Ricavi servizi AVERE imponibile + IVA debito.",
     "dare": [{"macro": "attivita_circolanti", "a": "totale"}],
     "avere": [{"macro": "ricavi_proventi", "a": "imponibile"}, {"macro": "iva", "a": "iva"}]},
    {"id": "REVERSE_CHARGE", "nome": "Reverse Charge (Art. 17 c.6 DPR 633/72)", "cat": "Estero/Particolari",
     "tipo_input": "IVA", "note": "Integrazione fattura estera. IVA si compensa nello stesso periodo.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "imponibile"}, {"macro": "iva", "a": "iva"}]},
    {"id": "SPLIT_PAYMENT", "nome": "Split Payment PA (Art. 17-ter)", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Vendita a PA. IVA versata dal committente, ma contabilizzata normalmente.",
     "dare": [{"macro": "attivita_circolanti", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "ricavi_proventi", "a": "imponibile"}, {"macro": "iva", "a": "iva"}]},
    {"id": "NOTA_CREDITO_ACQ", "nome": "Nota di credito ricevuta (storno acquisto)", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Storno costo e IVA credito. Fornitore DARE.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "totale"}],
     "avere": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}]},
    {"id": "NOTA_CREDITO_VEND", "nome": "Nota di credito emessa (storno vendita)", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Storno ricavo e IVA debito. Cliente AVERE.",
     "dare": [{"macro": "ricavi_proventi", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "ACQ_BENI_STRUMENTALI", "nome": "Acquisto bene strumentale (Auto/PC/Impianto)", "cat": "Immobilizzazioni",
     "tipo_input": "IVA_CESPITE", "note": "Specifica tipo cespite. IVA credito deducibile in base alla natura.",
     "dare": [{"macro": "imm_materiali", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "totale"}]},
    {"id": "RESO_ACQUISTO", "nome": "Reso merci a fornitore", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Storno debito fornitore e IVA credito precedentemente registrata.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "totale"}],
     "avere": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}]},
    {"id": "RESO_VENDITA", "nome": "Reso merci da cliente", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Storno credito cliente e IVA debito precedentemente registrata.",
     "dare": [{"macro": "ricavi_proventi", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "SCONTO_IN_FATTURA_ACQ", "nome": "Sconto incondizionato in fattura acquisto", "cat": "Acquisti/Vendite",
     "tipo_input": "IVA", "note": "Imponibile già netto. IVA calcolata sul netto.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "totale"}]},
    {"id": "ACCONTO_FORNITORE", "nome": "Acconto versato a fornitore", "cat": "Liquidità",
     "tipo_input": "SECCO", "note": "Anticipo non soggetto a IVA (se non fatturato). Conto transitorio.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "PAGAMENTO_FORNITORE", "nome": "Pagamento fornitore (Bonifico/Assegno)", "cat": "Liquidità",
     "tipo_input": "SECCO", "note": "Estinzione debito. Nessun impatto economico diretto.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "INCASSO_CLIENTE", "nome": "Incasso da cliente (Bonifico/Assegno)", "cat": "Liquidità",
     "tipo_input": "SECCO", "note": "Estinzione credito. Nessun impatto economico diretto.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "INCASSO_CARTA_POS", "nome": "Incasso POS/Carta di credito", "cat": "Liquidità",
     "tipo_input": "SECCO", "note": "Accredito netto dopo commissioni. Commissioni spesate separatamente.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "COMMISSIONI_BANCARIE", "nome": "Commissioni/Spese bancarie/POS", "cat": "Finanziario",
     "tipo_input": "SECCO", "note": "Costo finanziario. Di norma senza IVA o con IVA esente.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "INTERESSI_PASSIVI_BANCA", "nome": "Interessi passivi bancari/Mutuo", "cat": "Finanziario",
     "tipo_input": "SECCO", "note": "Oneri finanziari. Contropartita banca o debito mutuo.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "INTERESSI_ATTIVI_BANCA", "nome": "Interessi attivi bancari", "cat": "Finanziario",
     "tipo_input": "SECCO", "note": "Proventi finanziari. Contropartita banca.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "ricavi_proventi", "a": "importo"}]},
    {"id": "VERSAMENTO_CAPITALE", "nome": "Versamento capitale sociale", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Aumento liquidità e capitale. Operazione patrimoniale pura.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "patrimonio_netto", "a": "importo"}]},
    {"id": "VERSAMENTO_RISERVA", "nome": "Versamento soci a riserva/utile", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Conferimento senza aumento capitale. Riserva indisponibile o disponibile.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "patrimonio_netto", "a": "importo"}]},
    {"id": "PRESTITO_SOCIO", "nome": "Finanziamento socio (fruttifero/infruttifero)", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Debito verso socio. Da restituire. Non è capitale.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "importo"}]},
    {"id": "RIMBORSO_PRESTITO_SOCIO", "nome": "Rimborso finanziamento socio", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Estinzione debito verso socio.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "DISTRIBUZIONE_UTILI", "nome": "Distribuzione utili/dividendi ai soci", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Utile → Debito verso soci → Pagamento. Ritenuta 26% se applicabile.",
     "dare": [{"macro": "patrimonio_netto", "a": "importo"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "importo"}]},
    {"id": "COSTITUZIONE_SOCIETA", "nome": "Costituzione società (Atto notarile)", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Capitale sociale + Eventuali sovrapprezzi. Banca/Debito v/soci.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "patrimonio_netto", "a": "importo"}]},
    {"id": "COMPETENZA_STIPENDI", "nome": "Competenza stipendi (Lordo → Netto)", "cat": "Personale",
     "tipo_input": "STIPENDI", "note": "Calcolo automatico: Netto, IRPEF, INPS dip/azi, TFR.",
     "dare": [{"macro": "costi_oneri", "a": "lordo"}, {"macro": "costi_oneri", "a": "inps_azi"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "netto"}, {"macro": "passivita_fondi_debiti", "a": "irpef"}, {"macro": "passivita_fondi_debiti", "a": "inps_tot"}]},
    {"id": "PAGAMENTO_STIPENDI", "nome": "Pagamento stipendi netti", "cat": "Personale",
     "tipo_input": "SECCO", "note": "Estinzione debito verso dipendenti.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "VERSAMENTO_IRPEF_INPS", "nome": "Versamento IRPEF trattenute + INPS (F24)", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Pagamento ritenute operate e contributi dovuti.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "COMPENSO_AMMINISTRATORE", "nome": "Compenso amministratore (con ritenuta 20%)", "cat": "Personale",
     "tipo_input": "RITENUTA", "note": "Compenso - Ritenuta 20% = Netto. Eventuale IVA esente.",
     "dare": [{"macro": "costi_oneri", "a": "compenso"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "netto"}, {"macro": "passivita_fondi_debiti", "a": "ritenuta"}]},
    {"id": "COMPENSO_PROFESSIONISTA", "nome": "Compenso professionista esterno (Fattura/Ritenuta)", "cat": "Servizi",
     "tipo_input": "PROF", "note": "Imponibile + IVA (se dovuta) - Ritenuta 20% = Pagamento.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "netto"}, {"macro": "passivita_fondi_debiti", "a": "ritenuta"}, {"macro": "iva", "a": "iva"}]},
    {"id": "COMPENSO_CO_CO_PRO", "nome": "Compenso collaboratore (Co.Co.Pro/Progetto)", "cat": "Personale",
     "tipo_input": "RITENUTA", "note": "Ritenuta 20% + Contributi INPS gestione separata.",
     "dare": [{"macro": "costi_oneri", "a": "compenso"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "netto"}, {"macro": "passivita_fondi_debiti", "a": "ritenuta"}]},
    {"id": "COMPENSO_OCCASIONALE", "nome": "Compenso occasionale (<5000€ o >5000€)", "cat": "Personale",
     "tipo_input": "OCCASIONALE", "note": "Ritenuta 20% se >5000€ cumulativi. Marca da bollo 2€ se >77,47€.",
     "dare": [{"macro": "costi_oneri", "a": "compenso"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "netto"}, {"macro": "passivita_fondi_debiti", "a": "ritenuta"}]},
    {"id": "TFR_ACCANTONAMENTO", "nome": "Accantonamento TFR (Quota anno)", "cat": "Personale",
     "tipo_input": "SECCO", "note": "Costo competenza → Fondo TFR.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "importo"}]},
    {"id": "TFR_EROGAZIONE", "nome": "Erogazione TFR a dipendente cessato", "cat": "Personale",
     "tipo_input": "SECCO", "note": "Utilizzo fondo TFR. Tassazione separata (gestita in dichiarazione).",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "AMMORTAMENTO_AUTO", "nome": "Ammortamento autovettura (40% ded.)", "cat": "Immobilizzazioni",
     "tipo_input": "AMM_DED", "note": "Split automatico: 40% deducibile, 60% indeducibile.",
     "dare": [{"macro": "ammortamenti", "a": "quota_ded"}, {"macro": "ammortamenti", "a": "quota_ind"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "totale_quota"}]},
    {"id": "AMMORTAMENTO_PC_TEL", "nome": "Ammortamento PC/Telefonia (80% ded.)", "cat": "Immobilizzazioni",
     "tipo_input": "AMM_DED", "note": "Split automatico: 80% deducibile, 20% indeducibile.",
     "dare": [{"macro": "ammortamenti", "a": "quota_ded"}, {"macro": "ammortamenti", "a": "quota_ind"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "totale_quota"}]},
    {"id": "AMMORTAMENTO_STD", "nome": "Ammortamento cespite standard (Fabbricati/Mobili/Impianti)", "cat": "Immobilizzazioni",
     "tipo_input": "AMM_STD", "note": "Quota intera deducibile. Fondo ammortamento AVERE.",
     "dare": [{"macro": "ammortamenti", "a": "quota"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "quota"}]},
    {"id": "PLUSVALENZA_CESPITE", "nome": "Plusvalenza da cessione/rottamazione cespite", "cat": "Straordinario",
     "tipo_input": "PLUS_MINUS", "note": "Prezzo cessione - Valore netto contabile = Plusvalenza (Ricavo).",
     "dare": [{"macro": "attivita_circolanti", "a": "prezzo"}, {"macro": "passivita_fondi_debiti", "a": "fondo_amm"}],
     "avere": [{"macro": "imm_materiali", "a": "costo_storico"}, {"macro": "ricavi_proventi", "a": "plusvalenza"}]},
    {"id": "MINUSVALENZA_CESPITE", "nome": "Minusvalenza da cessione/rottamazione cespite", "cat": "Straordinario",
     "tipo_input": "PLUS_MINUS", "note": "Valore netto contabile - Prezzo cessione = Minusvalenza (Costo).",
     "dare": [{"macro": "attivita_circolanti", "a": "prezzo"}, {"macro": "passivita_fondi_debiti", "a": "fondo_amm"}, {"macro": "costi_oneri", "a": "minusvalenza"}],
     "avere": [{"macro": "imm_materiali", "a": "costo_storico"}]},
    {"id": "SVALUTAZIONE_CREDITI", "nome": "Svalutazione crediti (Fondo rischi)", "cat": "Rettifiche",
     "tipo_input": "SECCO", "note": "Accantonamento prudenziale per inesigibilità presunta.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "importo"}]},
    {"id": "UTILIZZO_SVALUTAZIONE", "nome": "Utilizzo fondo svalutazione (Inesigibilità certa)", "cat": "Rettifiche",
     "tipo_input": "SECCO", "note": "Storno credito e fondo. Eventuale perdita residua a CE.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo_fondo"}, {"macro": "costi_oneri", "a": "residuo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale_credito"}]},
    {"id": "RIVALUTAZIONE_SVALUTAZIONE", "nome": "Ripresa di valore (Venuti meno motivi svalutazione)", "cat": "Rettifiche",
     "tipo_input": "SECCO", "note": "Storno fondo fino al costo storico. Provento a CE.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "ricavi_proventi", "a": "importo"}]},
    {"id": "RATEO_ATTIVO", "nome": "Rateo attivo (Ricavo/Credito di competenza maturato)", "cat": "Assestamento",
     "tipo_input": "SECCO", "note": "Integrazione ricavo non ancora fatturato/incassato.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "ricavi_proventi", "a": "importo"}]},
    {"id": "RATEO_PASSIVO", "nome": "Rateo passivo (Costo/Debito di competenza maturato)", "cat": "Assestamento",
     "tipo_input": "SECCO", "note": "Integrazione costo non ancora fatturato/pagato.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "RISCONTO_ATTIVO", "nome": "Risconto attivo (Costo pagato anticipatamente)", "cat": "Assestamento",
     "tipo_input": "SECCO", "note": "Storno costo a quota competenza futura. Attivo SP.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "costi_oneri", "a": "importo"}]},
    {"id": "RISCONTO_PASSIVO", "nome": "Risconto passivo (Ricavo incassato anticipatamente)", "cat": "Assestamento",
     "tipo_input": "SECCO", "note": "Storno ricavo a quota competenza futura. Passivo SP.",
     "dare": [{"macro": "ricavi_proventi", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "LIQUIDAZIONE_IVA_DEBITO", "nome": "Liquidazione IVA periodica (A debito)", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Versamento differenza IVA vendite - IVA acquisti.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "LIQUIDAZIONE_IVA_CREDITO", "nome": "Liquidazione IVA periodica (A credito)", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Recupero credito IVA. Compensazione o rimborso.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "iva", "a": "importo"}]},
    {"id": "ACCONTO_IRES_IRAP", "nome": "Versamento acconti IRES/IRAP (F24)", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Pagamento acconti su imposte correnti.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "SALDO_IRES_IRAP", "nome": "Saldo IRES/IRAP (F24)", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Pagamento saldo imposte esercizio.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "IMU_TASI_TOSAP", "nome": "Pagamento IMU/TASI/TOSAP/Canone", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Imposte locali su immobili/occupazioni.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "IMPOSTA_BOLLO_REGISTRO", "nome": "Imposta di bollo/registro/notaio", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Oneri tributari vari.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "CANONE_AFFITTO", "nome": "Canone affitto immobile (con IVA se dovuta)", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Conto costo locazione + IVA credito. Pagamento a locatore.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "UTENZE_LUCE_GAS_ACQUA", "nome": "Utenze (Luce/Gas/Acqua/Telefono)", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Conto costo utenza + IVA credito. Pagamento a gestore.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "ASSICURAZIONE_RCA_AUTO", "nome": "Polizza assicurativa (Auto/RC/Infortuni)", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Costo premio + IVA credito (se dovuta). Esente in alcuni casi.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "MANUTENZIONE_ORDINARIA", "nome": "Manutenzione ordinaria/riparazione", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Spesato interamente a CE. Non incrementa cespite.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "MANUTENZIONE_STRAORDINARIA", "nome": "Manutenzione straordinaria (Incremento cespite)", "cat": "Immobilizzazioni",
     "tipo_input": "IVA", "note": "Va ad incremento valore cespite. Ammortizzato sulla vita residua.",
     "dare": [{"macro": "imm_materiali", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "LEASING_CANONE", "nome": "Canone leasing (Metodo patrimoniale)", "cat": "Immobilizzazioni",
     "tipo_input": "IVA", "note": "Canone spesato a CE. Riscatto finale capitalizzato.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "LEASING_RISCATTO", "nome": "Riscatto leasing finale", "cat": "Immobilizzazioni",
     "tipo_input": "IVA", "note": "Capitalizzazione bene. IVA sul riscatto.",
     "dare": [{"macro": "imm_materiali", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "NOLEGGIO_OPERATIVO", "nome": "Canone noleggio operativo", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Spesa periodica. Nessun capitale da riscattare.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "CARBURANTE_AUTO", "nome": "Carburante/Lubrificanti automezzi", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Deducibilità 40% (auto) / 100% (autocarri). IVA indetraibile proporzionale.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "VIAGGI_TRASFERTA", "nome": "Spese viaggio/trasferta (Hotel/Biglietti/Pasti)", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Deducibilità 100% se documentate e inerenti. IVA credito.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "PUBBLICITA_MARKETING", "nome": "Spese pubblicità/marketing/fiere", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Costo interamente deducibile. IVA credito.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "SPESE_RAPPRESENTANZA", "nome": "Spese di rappresentanza", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Deducibili entro limiti di legge. IVA credito.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "CANCELLERIA_UFFICIO", "nome": "Cancelleria/materiale d'ufficio/consumabili", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Costo deducibile. IVA credito.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "BENI_MINUTI", "nome": "Acquisto beni < 516,46€ (Immediate expensing)", "cat": "Gestione Corrente",
     "tipo_input": "IVA", "note": "Spesati immediatamente. Non capitalizzati.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}, {"macro": "iva", "a": "iva"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale"}]},
    {"id": "PROVVIGIONI_AGENTI", "nome": "Provvigioni a agenti/rappresentanti (con ENASARCO)", "cat": "Personale",
     "tipo_input": "PROVVIGIONE", "note": "Imponibile - Ritenuta 23% + Contributo ENASARCO.",
     "dare": [{"macro": "costi_oneri", "a": "imponibile"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "netto"}, {"macro": "passivita_fondi_debiti", "a": "ritenuta"}, {"macro": "passivita_fondi_debiti", "a": "enasarco"}]},
    {"id": "CONTRIBUTO_ENASARCO", "nome": "Versamento ENASARCO (F24)", "cat": "Tributi",
     "tipo_input": "SECCO", "note": "Pagamento contributo previdenziale agenti.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "EROGAZIONE_LIBERALE", "nome": "Erogazione liberale/donazione (Deducibile/Indeducibile)", "cat": "Straordinario",
     "tipo_input": "SECCO", "note": "Costo non inerente. Deducibile entro limiti art. 100 TUIR.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "attivita_circolanti", "a": "importo"}]},
    {"id": "RISARCIMENTO_DANNI_INCASSATO", "nome": "Incasso risarcimento danni/assicurativo", "cat": "Straordinario",
     "tipo_input": "SECCO", "note": "Provento non imponibile IVA (se risarcitorio).",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "ricavi_proventi", "a": "importo"}]},
    {"id": "PERDITA_SU_CREDITI", "nome": "Perdita su crediti inesigibili (Fallimento/Procedure)", "cat": "Straordinario",
     "tipo_input": "SECCO", "note": "Storno credito e IVA (se ricorrono presupposti art. 26 DPR 633).",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "fondo"}, {"macro": "costi_oneri", "a": "residuo"}, {"macro": "iva", "a": "iva_stornata"}],
     "avere": [{"macro": "attivita_circolanti", "a": "totale_credito"}]},
    {"id": "CHIUSURA_COSTI_A_CE", "nome": "Chiusura conti economici Costi → Conto Economico", "cat": "Chiusura Esercizio",
     "tipo_input": "SECCO", "note": "Storno tutti i costi a CE. Utile/Perdita preliminare.",
     "dare": [{"macro": "ricavi_proventi", "a": "totale_costi"}],
     "avere": [{"macro": "costi_oneri", "a": "totale_costi"}]},
    {"id": "CHIUSURA_RICAVI_A_CE", "nome": "Chiusura conti economici Ricavi → Conto Economico", "cat": "Chiusura Esercizio",
     "tipo_input": "SECCO", "note": "Storno tutti i ricavi a CE. Determinazione risultato.",
     "dare": [{"macro": "ricavi_proventi", "a": "totale_ricavi"}],
     "avere": [{"macro": "ricavi_proventi", "a": "totale_ricavi"}]},
    {"id": "CHIUSURA_CE_A_UTILE", "nome": "Chiusura CE → Utile/Perdita d'esercizio", "cat": "Chiusura Esercizio",
     "tipo_input": "SECCO", "note": "Saldo CE → Patrimonio Netto.",
     "dare": [{"macro": "ricavi_proventi", "a": "risultato"}],
     "avere": [{"macro": "patrimonio_netto", "a": "risultato"}]},
    {"id": "DESTINAZIONE_UTILE", "nome": "Destinazione utile (Riserve/Legale/Dividendi)", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Utile → Riserva legale/Statutaria/Dividendi.",
     "dare": [{"macro": "patrimonio_netto", "a": "importo"}],
     "avere": [{"macro": "patrimonio_netto", "a": "importo"}]},
    {"id": "COPERTURA_PERDITA", "nome": "Copertura perdita (Riserve/Utili pregressi)", "cat": "Patrimonio",
     "tipo_input": "SECCO", "note": "Perdita → Riserve indisponibili/Utili pregressi.",
     "dare": [{"macro": "patrimonio_netto", "a": "importo"}],
     "avere": [{"macro": "patrimonio_netto", "a": "importo"}]},
    {"id": "VARIAZIONE_VALUTA_ATTIVO", "nome": "Differenza cambio favorevole (Attivo)", "cat": "Finanziario",
     "tipo_input": "SECCO", "note": "Rivalutazione crediti/liquidità in valuta.",
     "dare": [{"macro": "attivita_circolanti", "a": "importo"}],
     "avere": [{"macro": "ricavi_proventi", "a": "importo"}]},
    {"id": "VARIAZIONE_VALUTA_PASSIVO", "nome": "Differenza cambio sfavorevole (Passivo)", "cat": "Finanziario",
     "tipo_input": "SECCO", "note": "Svalutazione debiti in valuta.",
     "dare": [{"macro": "costi_oneri", "a": "importo"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "importo"}]},
    {"id": "FUSIONE_INCORPORAZIONE", "nome": "Fusione per incorporazione (Avanzo/Disavanzo)", "cat": "Straordinario",
     "tipo_input": "SECCO", "note": "Apporto patrimonio netto incorporata → Capitale/Riserve.",
     "dare": [{"macro": "attivita_circolanti", "a": "attivi"}, {"macro": "costi_oneri", "a": "disavanzo"}],
     "avere": [{"macro": "passivita_fondi_debiti", "a": "passivi"}, {"macro": "patrimonio_netto", "a": "capitale"}, {"macro": "patrimonio_netto", "a": "avanzo"}]},
    {"id": "SCISSIONE", "nome": "Scissione proporzionale/non proporzionale", "cat": "Straordinario",
     "tipo_input": "SECCO", "note": "Trasferimento ramo aziendale. Contabilizzazione differenziata.",
     "dare": [{"macro": "passivita_fondi_debiti", "a": "passivi_ceduti"}, {"macro": "patrimonio_netto", "a": "patrimonio_ceduto"}],
     "avere": [{"macro": "attivita_circolanti", "a": "attivi_ceduti"}, {"macro": "imm_materiali", "a": "cespiti_ceduti"}]}
]

# ==============================================================================
# 3. MOTORE DI CALCOLO & GENERAZIONE
# ==============================================================================
def calcola_importi(tipo_input: str, valori: Dict) -> Dict:
    """Calcola tutti gli importi derivati in base al tipo di operazione"""
    res = {}
    try:
        if tipo_input == "IVA":
            imp = valori.get('imponibile', 0)
            aliquota = valori.get('aliquota', 22)
            res['imponibile'] = imp
            res['iva'] = round(imp * aliquota / 100, 2)
            res['totale'] = round(imp + res['iva'], 2)
        elif tipo_input == "IVA_CESPITE":
            imp = valori.get('imponibile', 0)
            aliquota = valori.get('aliquota', 22)
            res['imponibile'] = imp
            res['iva'] = round(imp * aliquota / 100, 2)
            res['totale'] = round(imp + res['iva'], 2)
        elif tipo_input == "STIPENDI":
            lordo = valori.get('lordo', 0)
            irpef = valori.get('irpef', 0)
            addizionali = valori.get('addizionali', 0)
            inps_dip_pct = valori.get('inps_dip_pct', 9.19)
            inps_azi_pct = valori.get('inps_azi_pct', 28.0)
            
            inps_dip = round(lordo * inps_dip_pct / 100, 2)
            inps_azi = round(lordo * inps_azi_pct / 100, 2)
            netto = round(lordo - inps_dip - irpef - addizionali, 2)
            
            res['lordo'] = lordo
            res['inps_azi'] = inps_azi
            res['netto'] = netto
            res['irpef'] = irpef + addizionali
            res['inps_tot'] = round(inps_dip + inps_azi, 2)
        elif tipo_input == "RITENUTA":
            comp = valori.get('compenso', 0)
            aliquota = valori.get('aliquota', 20)
            res['compenso'] = comp
            res['ritenuta'] = round(comp * aliquota / 100, 2)
            res['netto'] = round(comp - res['ritenuta'], 2)
        elif tipo_input == "PROF":
            imp = valori.get('imponibile', 0)
            aliquota = valori.get('aliquota', 22)
            ritenuta = valori.get('ritenuta', 20)
            res['imponibile'] = imp
            res['iva'] = round(imp * aliquota / 100, 2)
            res['ritenuta'] = round(imp * ritenuta / 100, 2)
            res['netto'] = round(imp - res['ritenuta'], 2)
            res['totale'] = round(imp + res['iva'], 2)
        elif tipo_input == "OCCASIONALE":
            comp = valori.get('compenso', 0)
            applica_rit = valori.get('applica_ritenuta', False)
            res['compenso'] = comp
            res['ritenuta'] = round(comp * 0.20, 2) if applica_rit else 0
            res['netto'] = round(comp - res['ritenuta'], 2)
        elif tipo_input == "PROVVIGIONE":
            imp = valori.get('imponibile', 0)
            res['imponibile'] = imp
            res['ritenuta'] = round(imp * 0.23, 2)
            res['enasarco'] = round(imp * 0.04, 2) # 4% a carico agente, 4% a carico azienda (semplificato)
            res['netto'] = round(imp - res['ritenuta'], 2)
        elif tipo_input in ["AMM_DED", "AMM_STD"]:
            quota = valori.get('quota', 0)
            if tipo_input == "AMM_DED":
                tipo_cespite = valori.get('tipo_cespite', 'AUTO')
                ded_pct = 0.4 if tipo_cespite == 'AUTO' else 0.8
                res['quota_ded'] = round(quota * ded_pct, 2)
                res['quota_ind'] = round(quota * (1 - ded_pct), 2)
                res['totale_quota'] = quota
            else:
                res['quota'] = quota
        elif tipo_input == "PLUS_MINUS":
            prezzo = valori.get('prezzo', 0)
            costo = valori.get('costo_storico', 0)
            fondo = valori.get('fondo_amm', 0)
            vnc = costo - fondo
            if prezzo > vnc:
                res['prezzo'] = prezzo
                res['fondo_amm'] = fondo
                res['costo_storico'] = costo
                res['plusvalenza'] = round(prezzo - vnc, 2)
            else:
                res['prezzo'] = prezzo
                res['fondo_amm'] = fondo
                res['costo_storico'] = costo
                res['minusvalenza'] = round(vnc - prezzo, 2)
        elif tipo_input == "SECCO":
            res['importo'] = valori.get('importo', 0)
    except Exception as e:
        st.error(f"Errore calcolo: {e}")
    return res

def cerca_conto_per_macro(coa: Dict, macro: str, esclusi: List[str] = None) -> Optional[str]:
    """Trova il primo conto valido per una macro-categoria"""
    esclusi = esclusi or []
    for cod, info in coa.items():
        if info['macro'] == macro and cod not in esclusi:
            return cod
    return None

def genera_scrittura(op: Dict, coa: Dict, calcoli: Dict) -> Tuple[List[Dict], List[Dict], str]:
    """Genera righe DARE e AVERE dinamicamente"""
    dare = []
    avere = []
    note_tecnica = op['note']
    
    try:
        for riga in op['dare']:
            codice = cerca_conto_per_macro(coa, riga['macro'])
            if codice:
                importo = calcoli.get(riga['a'], 0)
                if importo > 0:
                    dare.append({'conto': codice, 'descrizione': coa[codice]['descrizione'], 'importo': importo, 'natura': coa[codice]['tipo_bilancio']})
                    
        for riga in op['avere']:
            codice = cerca_conto_per_macro(coa, riga['macro'])
            if codice:
                importo = calcoli.get(riga['a'], 0)
                if importo > 0:
                    avere.append({'conto': codice, 'descrizione': coa[codice]['descrizione'], 'importo': importo, 'natura': coa[codice]['tipo_bilancio']})
    except Exception as e:
        note_tecnica += f"\n⚠️ Errore generazione: {e}"
        
    return dare, avere, note_tecnica

# ==============================================================================
# 4. INTERFACCIA STREAMLIT PROFESSIONALE
# ==============================================================================
def main():
    st.title("📊 Generatore Contabile Professionale | Ranocchi GIS")
    st.markdown("Motore dinamico per scritture contabili complesse. Carica il piano dei conti, seleziona il caso concreto, genera ed esporta.")
    
    # SIDEBAR
    with st.sidebar:
        st.header("📂 Piano dei Conti Ranocchi")
        uploaded_pdf = st.file_uploader("Carica PDF Piano dei Conti", type=["pdf"])
        
        if not uploaded_pdf:
            st.warning("⚠️ Carica il PDF per iniziare.")
            st.stop()
            
        with st.spinner("🔍 Parsing piano dei conti..."):
            coa = parse_piano_conti(uploaded_pdf)
            
        if not coa:
            st.error("❌ Nessun conto estratto. Verifica il formato PDF.")
            st.stop()
            
        st.success(f"✅ {len(coa)} conti caricati")
        st.divider()
        
        # Statistiche COA
        patrimoniali = sum(1 for v in coa.values() if v['tipo_bilancio'] == 'Patrimoniale')
        economici = sum(1 for v in coa.values() if v['tipo_bilancio'] == 'Economico')
        st.metric("Patrimoniali", patrimoniali)
        st.metric("Economici", economici)
        
        st.divider()
        st.info("💡 Ogni operazione mostra la natura contabile dei conti e la logica applicata.")

    # MAIN
    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        cats = sorted(list({op['cat'] for op in REGISTRO_OPERAZIONI}))
        cat_sel = st.selectbox("Categoria Operazione", ["Tutte"] + cats)
    with col_search:
        search = st.text_input("Cerca operazione", placeholder="Es: reverse charge, ammortamento auto, stipendi...")
        
    ops_filtrate = [op for op in REGISTRO_OPERAZIONI if (cat_sel == "Tutte" or op['cat'] == cat_sel) and (not search or search.lower() in op['nome'].lower())]
    
    if not ops_filtrate:
        st.warning("Nessuna operazione trovata.")
        return
        
    op_sel = st.selectbox("Seleziona operazione contabile", ops_filtrate, format_func=lambda x: f"{x['nome']} ({x['cat']})")
    
    if op_sel:
        st.info(f"📋 **{op_sel['nome']}**\n{op_sel['note']}")
        
        # INPUT DINAMICI
        st.subheader("💰 Parametri Operazione")
        tipo = op_sel['tipo_input']
        valori = {}
        
        cols = st.columns(3)
        idx = 0
        def next_col():
            nonlocal idx
            c = cols[idx % 3]
            idx += 1
            return c
            
        with next_col():
            if tipo in ["IVA", "IVA_CESPITE", "PROF"]:
                valori['imponibile'] = st.number_input("Imponibile €", min_value=0.0, step=0.01, format="%.2f")
            elif tipo == "STIPENDI":
                valori['lordo'] = st.number_input("Retribuzione Lorda €", min_value=0.0, step=0.01, format="%.2f")
            elif tipo in ["RITENUTA", "OCCASIONALE", "PROVVIGIONE"]:
                valori['compenso'] = st.number_input("Compenso/Imponibile €", min_value=0.0, step=0.01, format="%.2f")
            elif tipo in ["AMM_DED", "AMM_STD"]:
                valori['quota'] = st.number_input("Quota Ammortamento €", min_value=0.0, step=0.01, format="%.2f")
            elif tipo == "PLUS_MINUS":
                valori['prezzo'] = st.number_input("Prezzo Cessione €", min_value=0.0, step=0.01, format="%.2f")
                valori['costo_storico'] = st.number_input("Costo Storico €", min_value=0.0, step=0.01, format="%.2f")
                valori['fondo_amm'] = st.number_input("Fondo Ammortamento €", min_value=0.0, step=0.01, format="%.2f")
            elif tipo == "SECCO":
                valori['importo'] = st.number_input("Importo €", min_value=0.0, step=0.01, format="%.2f")
                
        with next_col():
            if tipo in ["IVA", "IVA_CESPITE", "PROF"]:
                valori['aliquota'] = st.selectbox("Aliquota IVA %", [0, 4, 10, 22], index=3)
            elif tipo == "STIPENDI":
                valori['irpef'] = st.number_input("IRPEF Trattenuta €", min_value=0.0, step=0.01, format="%.2f")
                valori['addizionali'] = st.number_input("Addizionali €", min_value=0.0, step=0.01, format="%.2f", value=0.0)
            elif tipo == "RITENUTA":
                valori['aliquota'] = st.selectbox("Ritenuta %", [0, 20, 23], index=1)
            elif tipo == "AMM_DED":
                valori['tipo_cespite'] = st.selectbox("Tipo Cespite", ["AUTO", "PC_TEL"])
                
        # GENERAZIONE
        if st.button("🚀 Genera Scrittura Contabile", type="primary", use_container_width=True):
            calcoli = calcola_importi(tipo, valori)
            dare, avere, note_tec = genera_scrittura(op_sel, coa, calcoli)
            
            tot_dare = sum(r['importo'] for r in dare)
            tot_avere = sum(r['importo'] for r in avere)
            
            col1, col2 = st.columns(2)
            
            def render_tabella(righe, lato, colore):
                if not righe:
                    st.write(f"⚪ Nessun conto {lato} generato")
                    return pd.DataFrame()
                df = pd.DataFrame(righe)
                df['Dettaglio'] = df.apply(lambda r: f"`{r['conto']}` - {r['descrizione']} ({'🟢' if r['natura']=='Patrimoniale' else '🟠'} {r['natura']})", axis=1)
                st.subheader(f"{colore} {lato}")
                st.dataframe(df[['Dettaglio', 'importo']].rename(columns={'importo': 'Importo €'}), hide_index=True, use_container_width=True)
                return df
                
            df_d = render_tabella(dare, "DARE", "🔴")
            df_a = render_tabella(avere, "AVERE", "🟢")
            
            col1.metric("Totale DARE", f"€ {tot_dare:,.2f}")
            col2.metric("Totale AVERE", f"€ {tot_avere:,.2f}")
            
            if abs(tot_dare - tot_avere) < 0.01:
                st.success("✅ **Scrittura BILANCIATA** (DARE = AVERE)")
                
                # EXPORT
                csv_rows = []
                for r in dare: csv_rows.append({'Lato':'DARE', 'Conto':r['conto'], 'Descrizione':r['descrizione'], 'Importo':r['importo'], 'Natura':r['natura']})
                for r in avere: csv_rows.append({'Lato':'AVERE', 'Conto':r['conto'], 'Descrizione':r['descrizione'], 'Importo':r['importo'], 'Natura':r['natura']})
                
                csv_data = pd.DataFrame(csv_rows).to_csv(index=False, sep=';', decimal=',')
                st.download_button(
                    label="📥 Scarica CSV (Compatibile Ranocchi GIS)",
                    data=csv_data,
                    file_name=f"scrittura_{op_sel['id']}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.error(f"❌ **NON BILANCIATA** | Differenza: € {abs(tot_dare-tot_avere):,.2f}")
                
            st.divider()
            st.markdown(f"📖 **Note tecniche:**\n{note_tec}")

if __name__ == "__main__":
    main()
