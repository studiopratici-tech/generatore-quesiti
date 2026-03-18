import streamlit as st
import pdfplumber
import re
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="ISA - Compilazione Quadro C", layout="wide", page_icon="📊")

# MAPPATURA DETTAGLIATA PER OGNI ISA - Basata sulle istruzioni ufficiali
ISA_MAPPING = {
    "EG50U": {
        "descrizione": "Intonacatura, rivestimento, tinteggiatura ed altri lavori di completamento",
        "campi": {
            "C01-C28": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Specializzazione per tipologia di lavoro",
                "parole_chiave": {
                    "C01": ["tinteggiatura", "verniciatura", "pittura", "imbiancatura"],
                    "C02": ["verniciatura industriale", "trattamenti protettivi"],
                    "C03": ["decorazioni", "affreschi", "stucchi decorativi"],
                    "C04": ["posa parati", "carta da parati", "rivestimenti tessili"],
                    "C05": ["posa vetrate", "installazione specchi"],
                    "C06": ["piastrellatura", "posa marmo"],
                    "C07": ["posa parquet", "pavimenti legno"],
                    "C08": ["posa moquette", "pavimenti tessili"],
                    "C09": ["posa cotto", "pavimenti cotto"],
                    "C10": ["posa graniglia", "pavimenti graniglia"],
                    "C11": ["posa PVC", "pavimenti PVC"],
                    "C12": ["posa linoleum", "pavimenti linoleum"],
                    "C13": ["levigatura", "lucidatura pavimenti"],
                    "C14": ["intonacatura", "rasatura", "civile", "scagliola"],
                    "C15": ["vetrocemento", "mattoni vetro"],
                    "C16": ["cartongesso", "contropareti", "controsoffitti lastre"],
                    "C17": ["soffitti sospesi", "pannelli fonoassorbenti"],
                    "C18": ["muratura interna", "tramezzi", "tamponature"],
                    "C19": ["muratura esterna", "facciate"],
                    "C20": ["pulizia pareti", "sabbiatura facciate"],
                    "C21": ["impermeabilizzazione", "coibentazione", "cappotto termico", "guaine"],
                    "C22": ["pavimentazione stradale", "asfalto", "bitume"],
                    "C23": ["opera incerta", "selciati", "muri a secco", "pietra naturale"],
                    "C24": ["grondaie", "pluviali", "lattoneria"],
                    "C25": ["resina", "pavimenti resina", "fibre carbonio"],
                    "C26": ["sottofondi", "massetti", "preparazione sottofondi"],
                    "C27": ["lavori completamento"],
                    "C28": ["altri lavori finitura"]
                },
                "controlli": [
                    "Verificare che C01+C02+...+C28 = 100% (tolleranza 0,1%)",
                    "Segnalare fatture con descrizione ambigua tra più categorie (es. tinteggiatura vs verniciatura)",
                    "Controllare che ogni fattura sia allocata a una e una sola categoria",
                    "Verificare coerenza tra descrizione fattura e categoria assegnata"
                ]
            },
            "C29": {
                "tipo": "percentuale",
                "descrizione": "Lavori acquisiti in subappalto",
                "parole_chiave": ["subappalto", "contratto subappalto", "autorizzazione subappalto", "CIG"],
                "controlli": [
                    "Verificare presenza esplicita di 'subappalto' in fattura o contratto",
                    "Non confondere con C32 (lavori affidati a terzi)",
                    "Controllare che fatture subappalto abbiano CIG se lavori pubblici"
                ]
            },
            "C30": {
                "tipo": "percentuale",
                "descrizione": "Produzione conto terzi (solo se >50% da un committente)",
                "controlli": [
                    "Compilare SOLO se un committente >50% ricavi totali",
                    "Verificare concentrazione fatture da singolo committente",
                    "Se <=50% lasciare vuoto"
                ]
            },
            "C31-C32": {
                "tipo": "percentuali",
                "vincolo": "C31+C32 = 100%",
                "descrizione": "Modalità realizzazione",
                "controlli": [
                    "C31 = lavori realizzati con mezzi propri (default 100% se non diversamente specificato)",
                    "C32 = lavori concessi in appalto/subappalto a terzi",
                    "NON confondere C29 (lavori acquisiti in subappalto) con C32 (lavori affidati a terzi)",
                    "Verificare che C31+C32 = 100%"
                ]
            },
            "C33-C35": {
                "tipo": "luogo",
                "descrizione": "Luogo svolgimento attività (Regione, Comune, Provincia)",
                "controlli": [
                    "Identificare Comune con maggior ricavo",
                    "Cercare in fattura: 'presso cantiere di [Comune]', 'in [Località]', 'sito in [Indirizzo]'",
                    "Se assente, usare Comune committente (segnalare come ambiguo)",
                    "Verificare coerenza con indirizzo fatture"
                ]
            },
            "C36-C41": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Localizzazione geografica rispetto a C34",
                "controlli": [
                    "C36 = Nel Comune di C34",
                    "C37 = Resto della Provincia (escluso C34)",
                    "C38 = Resto della Regione (esclusa Provincia C34)",
                    "C39 = Fuori Regione (Italia)",
                    "C40 = Estero UE",
                    "C41 = Estero Extra-UE",
                    "Verificare che C36+C37+C38+C39+C40+C41 = 100%",
                    "Per ogni fattura identificare Comune esecuzione e allocare correttamente"
                ]
            },
            "C42": {
                "tipo": "importo",
                "descrizione": "Costi per lavori a terzi",
                "controlli": [
                    "NON COMPILARE con sole fatture emesse (servono fatture acquisto)",
                    "Segnalare: 'Dato non disponibile - servono fatture di acquisto'"
                ]
            },
            "C43": {
                "tipo": "importo",
                "descrizione": "Split Payment (Art.17-ter)",
                "parole_chiave": ["Art.17-ter", "scissione pagamenti", "Pubblica Amministrazione"],
                "controlli": [
                    "Sommare imponibili con Art.17-ter o 'scissione pagamenti'",
                    "Verificare committente = Pubblica Amministrazione",
                    "Controllare coerenza con totale fatture PA"
                ]
            },
            "C44": {
                "tipo": "importo",
                "descrizione": "Reverse Charge (Art.17 c.6)",
                "parole_chiave": ["Art.17 c.6", "N6.3", "subappalto edile", "Art.17 c.6 lett. a-ter"],
                "controlli": [
                    "Sommare imponibili con Art.17 c.6 o N6.3",
                    "Verificare presenza reverse charge in fattura",
                    "Controllare coerenza con fatture subappalto edile"
                ]
            },
            "C45": {
                "tipo": "importo",
                "descrizione": "Ritenute Art.25 D.L. 78/2010",
                "parole_chiave": ["ritenuta acconto", "bonifico parlante", "ristrutturazioni"],
                "controlli": [
                    "Inserire solo se esplicitamente indicato in fattura",
                    "Verificare presenza 'ritenuta acconto' o 'bonifico parlante'",
                    "Controllare coerenza con ristrutturazioni edilizie"
                ]
            },
            "C46-C47": {
                "tipo": "percentuali",
                "vincolo": "C46+C47 = 100%",
                "descrizione": "Ambito attività",
                "parole_chiave": {
                    "C46": ["nuova costruzione", "edilizia nuova", "prima casa nuova"],
                    "C47": ["manutenzione straordinaria", "ristrutturazione", "restauro", "risanamento conservativo", "recupero", "Art.3 DPR 380/2001"]
                },
                "controlli": [
                    "Verificare che C46+C47 = 100%",
                    "In edilizia leggera, maggior parte lavori è C47 (verificare attentamente)",
                    "Segnalare fatture senza specificazione nuova vs recupero",
                    "Classificare come C47 se descrizione ambigua (manutenzione > nuove costruzioni)"
                ]
            }
        },
        "ambiguita_comuni": [
            "Distinguere tinteggiatura (C01) da verniciatura industriale (C02)",
            "Identificare luogo esecuzione se non esplicito in fattura",
            "Classificare nuova costruzione (C46) vs recupero (C47) - verificare descrizioni",
            "Verificare regime IVA (ordinario vs split payment vs reverse charge)",
            "Subappalto non esplicitato ma possibile (cliente = impresa edile + CIG)"
        ]
    },
    "EG69U": {
        "descrizione": "Costruzioni edili",
        "campi": {
            "C01-C07": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Ambito attività",
                "parole_chiave": {
                    "C01": ["edilizia abitativa pubblica", "nuova costruzione pubblica", "riqualificazione pubblica"],
                    "C02": ["edilizia abitativa privata", "nuova costruzione privata"],
                    "C03": ["edilizia non abitativa privata", "capannoni", "uffici", "negozi"],
                    "C04": ["lavori pubblici", "opere infrastrutturali", "autostrade", "ferrovie"],
                    "C05": ["riqualificazione recupero edifici privati", "manutenzione", "restauro", "ristrutturazione"],
                    "C06": ["lavori complementari", "impermeabilizzazioni", "stuccature", "isolamento"],
                    "C07": ["calcestruzzo preconfezionato", "produzione stabilimento"]
                },
                "controlli": [
                    "Verificare che C01+C02+C03+C04+C05+C06+C07 = 100%",
                    "C01 include manutenzione edilizia abitativa pubblica",
                    "C04 include manutenzione opere infrastrutturali",
                    "C05 NON include recupero edifici pubblici (va in C01 o C04)"
                ]
            },
            "C08-C28": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Specializzazione lavori",
                "controlli": [
                    "Verificare che C08+C09+...+C28 = 100%",
                    "Allocare ogni fattura a una specializzazione specifica"
                ]
            },
            "C30-C32": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Modalità acquisizione lavori",
                "controlli": [
                    "C30 = appalto da committenti pubblici/privati",
                    "C31 = subappalto da committenti/appaltatori",
                    "C32 = esecuzione propria promozione",
                    "Verificare C30+C31+C32 = 100%",
                    "Non includere lavori acquisiti ma non iniziati"
                ]
            },
            "C36-C41": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Localizzazione geografica",
                "controlli": [
                    "Verificare C36+C37+C38+C39+C40+C41 = 100%",
                    "C36 = Comune C34, C37 = resto provincia, C38 = resto regione"
                ]
            },
            "C42": {
                "tipo": "importo",
                "descrizione": "Split Payment",
                "parole_chiave": ["Art.17-ter", "scissione pagamenti", "PA"],
                "controlli": ["Verificare fatture verso PA con split payment"]
            },
            "C43": {
                "tipo": "importo",
                "descrizione": "Reverse Charge",
                "parole_chiave": ["Art.17 c.6", "N6.3", "subappalto edile"],
                "controlli": ["Verificare reverse charge in fatture subappalto"]
            },
            "C46-C49": {
                "tipo": "importo",
                "descrizione": "Rimanenze",
                "controlli": [
                    "Verificare coerenza con bilancio",
                    "C46-C47 = lavori in corso durata non ultrannuale",
                    "C48-C49 = prodotti finiti"
                ]
            }
        }
    },
    "FM87U": {
        "descrizione": "Commercio al dettaglio altri prodotti",
        "campi": {
            "C01-C08": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Modalità di vendita",
                "controlli": [
                    "Verificare C01+C02+...+C08 = 100%",
                    "C09 <= C08 (negozio automatizzato)"
                ]
            },
            "C13-C22": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Settori merceologici",
                "controlli": [
                    "Verificare C13+C14+...+C22 = 100%",
                    "Consultare Tabella Settori Merceologici istruzioni",
                    "Allocare ogni prodotto a settore corretto"
                ]
            }
        }
    },
    "EG37U": {
        "descrizione": "Bar, gelateria, pasticceria",
        "campi": {
            "C01-C05": {
                "tipo": "importo",
                "descrizione": "Dati aggio/ricavo fisso",
                "controlli": [
                    "Separare aggio da ricavi ordinari",
                    "Verificare coerenza con Quadro F"
                ]
            },
            "C06": {
                "tipo": "importo",
                "descrizione": "Proventi apparecchi",
                "controlli": ["Verificare documentazione apparecchi"]
            },
            "C07-C18": {
                "tipo": "percentuali",
                "vincolo": "C07+C08+C09+C10+C17+C18 = 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare somme percentuali"]
            },
            "C19-C27": {
                "tipo": "percentuali",
                "descrizione": "Tipologia prodotti",
                "controlli": [
                    "Somma C19-C27 deve coincidere con somma C07-C10",
                    "Verificare coerenza"
                ]
            },
            "C33": {
                "tipo": "importo",
                "descrizione": "Energia elettrica (Kwh)",
                "controlli": ["Verificare coerenza con bollette"]
            },
            "E01": {
                "tipo": "importo",
                "descrizione": "Consumo caffè (Kg)",
                "controlli": ["Verificare coerenza con acquisti"]
            }
        }
    },
    "EG36U": {
        "descrizione": "Ristorazione commerciale",
        "campi": {
            "C01-C05": {
                "tipo": "importo",
                "descrizione": "Dati aggio/ricavo fisso",
                "controlli": ["Separare aggio da ricavi ordinari"]
            },
            "C07-C16": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C07+C08+...+C16 = 100%"]
            },
            "C20-C25": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Acquisti cibi e bevande",
                "controlli": [
                    "Verificare C20+C21+...+C25 = 100%",
                    "Coerenza con fatture acquisto"
                ]
            },
            "C27": {
                "tipo": "percentuale",
                "descrizione": "Rimanenze bevande alcoliche",
                "controlli": ["Verificare coerenza con inventario"]
            }
        }
    },
    "DG66U": {
        "descrizione": "Software house, IT",
        "campi": {
            "C01-C21": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Attività svolta",
                "controlli": [
                    "Verificare C01+C02+...+C21 = 100%",
                    "C01 NON include App (va in C19)",
                    "C19 include App + prodotti multimediali"
                ]
            },
            "C22": {
                "tipo": "percentuale",
                "descrizione": "Committente principale (>30%)",
                "controlli": ["Compilare solo se >30% ricavi"]
            },
            "C23": {
                "tipo": "numero",
                "descrizione": "Contabilità elaborate",
                "controlli": ["Solo se attività elaborazione dati"]
            },
            "C24": {
                "tipo": "numero",
                "descrizione": "Buste paga elaborate",
                "controlli": ["Solo se attività elaborazione dati"]
            }
        }
    },
    "DG33U": {
        "descrizione": "Servizi estetici e benessere",
        "campi": {
            "C01-C11": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C01+C02+...+C11 = 100%"]
            },
            "C12": {
                "tipo": "flag",
                "descrizione": "Franchising/affiliazione",
                "controlli": ["Verificare contratto franchising"]
            },
            "C13": {
                "tipo": "importo",
                "descrizione": "Costi franchisor",
                "controlli": ["Verificare coerenza con C12"]
            },
            "C14": {
                "tipo": "importo",
                "descrizione": "Ricavi postazioni",
                "controlli": ["Verificare contratti postazioni"]
            }
        }
    },
    "EG34U": {
        "descrizione": "Servizi acconciatura",
        "campi": {
            "C02-C10": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C02+C03+...+C10 = 100%"]
            },
            "C11": {
                "tipo": "numero",
                "descrizione": "Addetti estetista/visagista",
                "controlli": ["Verificare coerenza con personale"]
            },
            "C12": {
                "tipo": "importo",
                "descrizione": "Ricavi postazioni",
                "controlli": ["Verificare contratti"]
            },
            "C13": {
                "tipo": "importo",
                "descrizione": "Costi postazioni terzi",
                "controlli": ["Verificare fatture"]
            }
        }
    },
    "EG75U": {
        "descrizione": "Installazione impianti",
        "campi": {
            "C01-C25": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Specializzazione impianti",
                "controlli": ["Verificare C01+C02+...+C25 = 100%"]
            },
            "C26-C29": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia servizio",
                "controlli": ["Verificare C26+C27+C28+C29 = 100%"]
            },
            "C36-C40": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Area territoriale",
                "controlli": ["Verificare C36+C37+C38+C39+C40 = 100%"]
            },
            "C42-C43": {
                "tipo": "percentuali",
                "vincolo": "C42+C43 = 100%",
                "descrizione": "Ambito attività (nuovo vs recupero)",
                "controlli": ["Verificare C42+C43 = 100%"]
            }
        }
    },
    "EG40U": {
        "descrizione": "Locazione, compravendita immobili",
        "campi": {
            "C01-C14": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C01+C02+...+C14 = 100%"]
            },
            "C47-C54": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Localizzazione immobili",
                "controlli": ["Verificare C47+C48+...+C54 = 100%"]
            },
            "C56": {
                "tipo": "importo",
                "descrizione": "Split Payment",
                "controlli": ["Verificare fatture PA"]
            },
            "C57": {
                "tipo": "importo",
                "descrizione": "Reverse Charge",
                "controlli": ["Verificare reverse charge"]
            }
        }
    },
    "EG61U": {
        "descrizione": "Intermediari commercio e servizi",
        "campi": {
            "C23-C44": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Area esercizio attività",
                "controlli": ["Verificare C23+C24+...+C44 = 100%"]
            },
            "C45-C54": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Settori merceologici",
                "controlli": [
                    "Verificare C45+C46+...+C54 = 100%",
                    "Consultare Tabella Settori Merceologici"
                ]
            }
        }
    },
    "EG99U": {
        "descrizione": "Altri servizi a imprese e famiglie",
        "campi": {
            "C01-C07": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C01+C02+...+C07 = 100%"]
            },
            "C08": {
                "tipo": "percentuale",
                "descrizione": "Committente principale (>50%)",
                "controlli": ["Compilare solo se >50%"]
            }
        }
    },
    "EK02U": {
        "descrizione": "Studi di ingegneria",
        "campi": {
            "C01-C34": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia prestazioni",
                "controlli": ["Verificare C01+C02+...+C34 = 100%"]
            },
            "C35-C38": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Macro aree specialistiche",
                "controlli": ["Verificare C35+C36+C37+C38 = 100%"]
            },
            "C39": {
                "tipo": "percentuale",
                "descrizione": "Committente principale (>50%)",
                "controlli": ["Compilare solo se >50%"]
            },
            "C40": {
                "tipo": "percentuale",
                "descrizione": "Attività presso committente",
                "controlli": ["C40 <= C39"]
            }
        }
    },
    "EK19U": {
        "descrizione": "Attività paramediche",
        "campi": {
            "C01-C04": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia prestazioni",
                "controlli": ["Verificare C01+C02+C03+C04 = 100%"]
            },
            "C17": {
                "tipo": "percentuale",
                "descrizione": "Committente principale (>50%)",
                "controlli": ["Compilare solo se >50%"]
            }
        }
    },
    "EM01A": {
        "descrizione": "Commercio al dettaglio alimentare",
        "campi": {
            "C01-C05": {
                "tipo": "importo",
                "descrizione": "Dati aggio/ricavo fisso",
                "controlli": ["Separare aggio da ricavi ordinari"]
            },
            "C06-C14": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Modalità di vendita",
                "controlli": ["Verificare C06+C07+...+C14 = 100%"]
            },
            "C20-C47": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia offerta",
                "controlli": ["Verificare C20+C21+...+C47 = 100%"]
            }
        }
    },
    "EM05U": {
        "descrizione": "Commercio abbigliamento",
        "campi": {
            "C01-C11": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Modalità vendita",
                "controlli": ["Verificare C01+C02+...+C11 = 100%"]
            },
            "C12-C23": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Prodotti",
                "controlli": ["Verificare C12+C13+...+C23 = 100%"]
            },
            "C24-C29": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Fascia qualitativa",
                "controlli": ["Verificare C24+C25+C26+C27+C28+C29 = 100%"]
            },
            "C30-C33": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Modalità acquisto",
                "controlli": ["Verificare C30+C31+C32+C33 = 100%"]
            }
        }
    },
    "EM11U": {
        "descrizione": "Commercio ferramenta, termoidraulica, materiali da costruzione",
        "campi": {
            "C01-C18": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Prodotti venduti",
                "controlli": ["Verificare C01+C02+...+C18 = 100%"]
            },
            "C19-C28": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia vendita",
                "controlli": ["Verificare C19+C20+...+C28 = 100%"]
            }
        }
    },
    "EM43U": {
        "descrizione": "Commercio macchine agricole e giardinaggio",
        "campi": {
            "C01-C10": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia vendita",
                "controlli": ["Verificare C01+C02+...+C10 = 100%"]
            },
            "C11-C22": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia offerta",
                "controlli": ["Verificare C11+C12+...+C22 = 100%"]
            }
        }
    },
    "EM85U": {
        "descrizione": "Commercio prodotti tabacco",
        "campi": {
            "C01-C05": {
                "tipo": "importo",
                "descrizione": "Dati aggio/ricavo fisso",
                "controlli": ["Separare aggio da ricavi ordinari"]
            },
            "C06": {
                "tipo": "importo",
                "descrizione": "Proventi apparecchi",
                "controlli": ["Verificare documentazione"]
            },
            "C07-C09": {
                "tipo": "importo",
                "descrizione": "Ricavi per tipologia",
                "controlli": ["Verificare coerenza con totale"]
            }
        }
    },
    "DM28U": {
        "descrizione": "Commercio tessuti, filati, merceria",
        "campi": {
            "C01-C08": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Modalità vendita",
                "controlli": ["Verificare C01+C02+...+C08 = 100%"]
            },
            "C12-C29": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia offerta",
                "controlli": ["Verificare C12+C13+...+C29 = 100%"]
            },
            "C30-C33": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Fascia qualitativa",
                "controlli": ["Verificare C30+C31+C32+C33 = 100%"]
            }
        }
    },
    "DM80U": {
        "descrizione": "Commercio carburanti",
        "campi": {
            "C01-C05": {
                "tipo": "importo",
                "descrizione": "Dati aggio/ricavo fisso",
                "controlli": ["Separare aggio da ricavi ordinari"]
            },
            "C06-C11": {
                "tipo": "quantità",
                "descrizione": "Quantità erogate",
                "controlli": ["Verificare coerenza con registro"]
            },
            "C12-C17": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C12+C13+...+C17 = 100%"]
            }
        }
    },
    "DG76U": {
        "descrizione": "Ristorazione collettiva",
        "campi": {
            "C01-C09": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C01+C02+...+C09 = 100%"]
            },
            "C10": {
                "tipo": "numero",
                "descrizione": "Numero pasti erogati",
                "controlli": ["Verificare coerenza con contratti"]
            }
        }
    },
    "DG91U": {
        "descrizione": "Servizi finanziari e assicurativi",
        "campi": {
            "C02-C15": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C02+C03+...+C15 = 100%"]
            },
            "C16-C19": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Rami assicurazioni",
                "controlli": ["Verificare C16+C17+C18+C19 = 100%"]
            },
            "C46-C51": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia finanziamento",
                "controlli": ["Verificare C46+C47+...+C51 = 100%"]
            }
        }
    },
    "DD02U": {
        "descrizione": "Produzione prodotti farinacei",
        "campi": {
            "C02-C07": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia clientela",
                "controlli": ["Verificare C02+C03+...+C07 = 100%"]
            },
            "C08-C26": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Prodotti ottenuti",
                "controlli": ["Verificare C08+C09+...+C26 = 100%"]
            },
            "C27-C28": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Vendite (scontrini vs fatture)",
                "controlli": ["Verificare C27+C28 = 100%"]
            }
        }
    },
    "EG31U": {
        "descrizione": "Revisione/manutenzione autoveicoli",
        "campi": {
            "C01-C08": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia attività",
                "controlli": ["Verificare C01+C02+...+C08 = 100%"]
            },
            "C09-C12": {
                "tipo": "percentuali",
                "vincolo": "somma 100%",
                "descrizione": "Tipologia veicolo",
                "controlli": ["Verificare C09+C10+C11+C12 = 100%"]
            },
            "C15-C17": {
                "tipo": "importo",
                "descrizione": "Spese terzi",
                "controlli": ["Verificare coerenza con fatture"]
            },
            "C19": {
                "tipo": "numero",
                "descrizione": "Numero revisioni",
                "controlli": ["Verificare coerenza con registro"]
            }
        }
    }
}

st.title("📊 ISA - Compilazione Quadro C")
st.markdown("Carica il PDF delle istruzioni ISA per generare il prompt di compilazione")

uploaded_file = st.file_uploader("📄 Carica PDF istruzioni ISA", type=['pdf'])

if uploaded_file is not None:
    with st.spinner('🔍 Analisi del PDF in corso...'):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            text_content = ""
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages[:5]:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
            
            os.unlink(tmp_path)
            
            pattern = r'\b([A-Z]{2}\d{2,3}[A-Z])\b'
            matches = re.findall(pattern, text_content)
            
            isa_code = None
            for match in matches:
                if match in ISA_MAPPING:
                    isa_code = match
                    break
            
            if isa_code:
                st.success(f"✅ Codice ISA rilevato: **{isa_code}**")
                
                data = ISA_MAPPING[isa_code]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Settore", data.get('descrizione', 'N/A'))
                with col2:
                    st.metric("Campi Quadro C", sum(len(v.get('campi', {})) if isinstance(v.get('campi'), dict) else 1 for v in [data]))
                
                # Genera prompt operativo
                prompt = f"""
RUOLO E OBIETTIVO
Ruolo: Agisci come un Consulente Fiscale Senior specializzato in ISA (Indici Sintetici di Affidabilità Fiscale), con competenza specifica sul codice attività {isa_code}: "{data['descrizione']}".
Obiettivo: Compilare con precisione assoluta il Quadro C – Elementi specifici dell'attività del modello {isa_code} per il periodo d'imposta 2025, estraendo i dati esclusivamente dalla documentazione fornita e applicando rigorosamente le regole del modello {isa_code}.

FASE 1: ESTRATTORE DATI – Revenue Recognition e Pulizia
1.1 Tipologia Documento e Segno
Codice | Tipo | Trattamento nel calcolo
TD01 | Fattura | Importo positivo (+)
TD04 | Nota di Credito | Importo negativo (–) → storno ricavo originale
Altri | Ignorare o segnalare | Non considerare nel calcolo

1.2 Campi da estrarre per ogni documento
Per ogni fattura/nota di credito, estrai e memorizza:
- Numero documento (es. 1-PA, 34-PA)
- Data documento (formato DD-MM-YYYY)
- Imponibile IVA → Usa il campo "Totale imponibile" (MAI il "Totale documento" che include IVA)
- Aliquota/Natura IVA e Riferimento normativo (es. Art.17 c.6, Art.17-ter, N6.3, 22%)
- Descrizione prestazioni → Testo completo per classificazione attività
- Luogo di esecuzione → Cerca nel testo: "presso cantiere di [Comune]", "in [Località]", "sito in [Indirizzo]". Se assente, usa il Comune del cessionario/committente.
- Committente → Denominazione, Codice Fiscale/Partita IVA, Comune
- Eventuali riferimenti a regimi speciali → Cerca: "subappalto", "reverse charge", "split payment", "ritenuta"

1.3 Calcolo Totale Ricavi Netto
Totale Ricavi Netto = Σ(Imponibili TD01) + Σ(Imponibili TD04 con segno negativo)

Attenzione: Le note di credito devono stornare la stessa categoria/luogo della fattura originale.

FASE 2: CLASSIFICAZIONE PER CAMPI QUADRO C - {isa_code}
"""
                
                # Aggiungi istruzioni specifiche per ogni campo
                for campo, info in data.get('campi', {}).items():
                    prompt += f"""
{campo} - {info.get('descrizione', 'N/A')}
Tipo: {info.get('tipo', 'N/A')}
"""
                    if info.get('vincolo'):
                        prompt += f"Vincolo: {info['vincolo']}\n"
                    if info.get('parole_chiave'):
                        if isinstance(info['parole_chiave'], dict):
                            for subcampo, keywords in info['parole_chiave'].items():
                                prompt += f"  {subcampo}: {', '.join(keywords)}\n"
                        else:
                            prompt += f"Parole chiave: {', '.join(info['parole_chiave']) if isinstance(info['parole_chiave'], list) else info['parole_chiave']}\n"
                    if info.get('controlli'):
                        prompt += "Controlli:\n"
                        for ctrl in info['controlli']:
                            prompt += f"  - {ctrl}\n"
                    prompt += "\n"
                
                # Aggiungi sezione ambiguità
                if data.get('ambiguita_comuni'):
                    prompt += """
FASE 3: SEGNALAZIONE PROATTIVA DELLE AMBIGUITÀ
Prima di compilare il Quadro C, analizzare ogni fattura e segnalare esplicitamente in una sezione dedicata:

NOTE E CRITICITÀ – FATTURE DA VERIFICARE
"""
                    for amb in data['ambiguita_comuni']:
                        prompt += f"- {amb}\n"
                    
                    prompt += """
Categorie di segnalazione obbligatorie:
1. Classificazione incerta - "Fattura [N.]: la descrizione '[testo]' potrebbe appartenere a più categorie. Ho classificato in [X] per [motivazione], ma richiede verifica umana."
2. Luogo di esecuzione non esplicito - "Fattura [N.]: non è indicato il cantiere/luogo di lavorazione. Ho assunto il Comune del committente ([Comune]), ma verificare."
3. Regime IVA dubbio - "Fattura [N.]: il riferimento normativo '[testo]' è parziale/ambiguo. Ho trattato come [regime], ma confermare."
4. Note di credito da riconciliare - "Nota di credito [N.]: storna la fattura [X]. Verificare allocazione originale."
5. Dati mancanti - "Campo [CXX]: non compilabile con i soli dati disponibili. Segnalare necessità documentazione integrativa."

FASE 4: VALIDAZIONE FINALE E OUTPUT
4.1 Controlli di coerenza obbligatori
Prima di restituire il risultato, verificare:
"""
                
                # Aggiungi controlli di validazione specifici
                for campo, info in data.get('campi', {}).items():
                    if info.get('vincolo'):
                        prompt += f"- {info['vincolo']}\n"
                
                prompt += """
- Gli importi di regimi IVA speciali sono coerenti con le fatture
- Le note di credito sono state applicate come storni (non come nuovi ricavi)
- Nessun campo è stato compilato con dati inventati o dedotti senza evidenza

4.2 Formato di output richiesto
- TABELLA RIEPILOGATIVA con tutti i campi compilati
- Per ogni riga: Valore + [N. fatture incluse]
- ANALISI DI COERENZA interna
- SEGNALAZIONE CRITICITÀ con priorità (alta/media/bassa)
- CHECKLIST PRE-INVIO completata

ISTRUZIONE FINALE DI SAFETY CHECK
Se una fattura presenta anche solo un dubbio ragionevole su classificazione, localizzazione, regime fiscale o ambito di attività, NON forzare una classificazione certa. Segnalala nella sezione 'NOTE E CRITICITÀ' e, solo se strettamente necessario per la compilazione, indica l'ipotesi più probabile specificando chiaramente che è un'assunzione da validare. In ambito ISA: meglio una segnalazione in più che un errore in dichiarazione.
"""
                
                st.subheader("🤖 Prompt Generato")
                st.code(prompt, language='text')
                
                st.download_button(
                    label="📥 Scarica Prompt (.txt)",
                    data=prompt,
                    file_name=f"prompt_{isa_code}_quadro_c.txt",
                    mime="text/plain",
                    type="primary"
                )
                
            else:
                st.warning("⚠️ Nessun codice ISA riconosciuto nel PDF")
                if matches:
                    st.write(f"Codici trovati nel testo: {list(set(matches))[:10]}")
                
        except Exception as e:
            st.error(f"❌ Errore durante l'analisi: {str(e)}")
            st.exception(e)
else:
    st.info("👆 Carica un PDF per iniziare")
