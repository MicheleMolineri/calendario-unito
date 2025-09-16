# Gestore Calendario Universitario

Questo script Python ti permette di scaricare, filtrare e mantenere aggiornato il tuo calendario universitario, selezionando solo le materie che ti interessano.

## 🚀 Funzionalità

- ✅ **Download automatico** del calendario dall'URL universitario
- ✅ **Visualizzazione** di tutti i corsi disponibili
- ✅ **Selezione interattiva** dei corsi di interesse
- ✅ **Filtraggio** del calendario per includere solo le materie scelte
- ✅ **Rilevamento automatico** degli aggiornamenti
- ✅ **Esportazione** in formato ICS compatibile con tutti i calendar app
- ✅ **Aggiornamento automatico** programmabile

## 📋 Requisiti

- Python 3.7 o superiore
- Connessione internet per scaricare il calendario

## 🛠️ Installazione

1. **Clona o scarica** questo progetto
2. **Naviga** nella cartella del progetto:
   ```bash
   cd CalendarUni
   ```
3. **Attiva l'ambiente virtuale** (già configurato):
   ```bash
   source .venv/bin/activate  # su macOS/Linux
   # oppure
   .venv\Scripts\activate     # su Windows
   ```

Le dipendenze (`requests` e `icalendar`) sono già installate nell'ambiente virtuale.

## 📖 Utilizzo

### Prima configurazione (modalità interattiva)

```bash
python calendar_manager.py <URL_DEL_TUO_CALENDARIO>
```

**Esempio:**
```bash
python calendar_manager.py https://unito.edu/calendario/ics/calendario.ics
```

Lo script ti mostrerà:
1. Tutti i corsi disponibili nel calendario
2. Un'interfaccia per selezionare quelli che ti interessano
3. Salverà le tue preferenze e creerà il calendario filtrato

### Modalità di selezione

Quando ti viene chiesto di selezionare i corsi, puoi usare:

- **Numeri singoli**: `1,3,5,7`
- **Intervalli**: `1-5` (seleziona dal corso 1 al 5)
- **Combinazioni**: `1,3-7,10,15-20`
- **Tutti**: `all`
- **Nessuno**: `none`

### Aggiornamento automatico

```bash
python calendar_manager.py <URL_CALENDARIO> --auto-update
```

Questo comando:
- Controlla se ci sono modifiche nel calendario universitario
- Aggiorna automaticamente il tuo calendario filtrato se necessario
- Mantiene le tue preferenze di corsi selezionati

### Script di aggiornamento automatico

Per aggiornamenti ancora più automatici:

```bash
python auto_update.py <URL_CALENDARIO>
```

Opzioni disponibili:
- `--force`: Forza l'aggiornamento anche se non necessario
- `--quiet`: Modalità silenziosa (mostra solo errori)

## 📁 File generati

Dopo l'esecuzione, troverai questi file:

- **`filtered_calendar.ics`**: Il tuo calendario filtrato (da importare nelle app)
- **`calendar_config.json`**: Le tue preferenze e configurazioni
- **`calendar_cache.pkl`**: Cache per ottimizzazioni (opzionale)

## 📱 Importazione del calendario

Il file `filtered_calendar.ics` può essere importato in:

- **Google Calendar**: Impostazioni → Importa ed esporta → Seleziona file
- **Apple Calendar**: File → Importa → Seleziona file
- **Outlook**: File → Apri ed esporta → Importa/Esporta
- **Altre app**: Qualsiasi applicazione che supporta il formato ICS

## ⚡ Aggiornamento automatico programmato

### Opzione 1: Cron (macOS/Linux)

Crea uno script cron:
```bash
python auto_update.py setup --setup-cron
```

Poi aggiungi al crontab:
```bash
crontab -e
```

Aggiungi una di queste righe:
```bash
# Aggiorna ogni ora
0 * * * * /path/to/CalendarUni/update_calendar.sh

# Aggiorna ogni 30 minuti
*/30 * * * * /path/to/CalendarUni/update_calendar.sh
```

### Opzione 2: Esecuzione manuale periodica

Semplicemente esegui periodicamente:
```bash
python auto_update.py <URL_CALENDARIO>
```

## 🔧 Personalizzazione

### Modifica il parsing dei nomi dei corsi

Se il tuo calendario ha un formato particolare, puoi modificare la funzione `extract_course_name()` in `calendar_manager.py`:

```python
def extract_course_name(self, summary: str, description: str) -> str:
    # Personalizza questa funzione in base al formato del tuo calendario
    course_name = summary.strip()
    
    # Esempi di personalizzazione:
    # Rimuovi prefissi: "CORSO: Matematica" → "Matematica"
    if course_name.startswith("CORSO: "):
        course_name = course_name[7:]
    
    # Rimuovi suffissi: "Matematica - A.A. 2024" → "Matematica"
    course_name = course_name.split(' - ')[0]
    
    return course_name.strip()
```

## 📊 Esempio di utilizzo

```bash
# Prima volta: configurazione interattiva
$ python calendar_manager.py https://unito.edu/calendar.ics

============================================================
GESTORE CALENDARIO UNIVERSITARIO
============================================================

Scaricando calendario da: https://unito.edu/calendar.ics

============================================================
CORSI DISPONIBILI NEL CALENDARIO
============================================================

 1. Analisi Matematica I (15 eventi)
 2. Fisica Generale I (12 eventi)
 3. Chimica Generale (8 eventi)
 4. Informatica di Base (10 eventi)
 5. Inglese Scientifico (6 eventi)

Totale: 5 corsi trovati

============================================================
SELEZIONE CORSI
============================================================
Inserisci i numeri dei corsi che ti interessano.
Puoi inserire:
- Numeri singoli: 1,3,5
- Intervalli: 1-5
- Combinazioni: 1,3-7,10
- 'all' per selezionare tutti
- 'none' per non selezionare nessuno

Inserisci la tua selezione: 1,2,4

Corsi selezionati: 3
- Analisi Matematica I
- Fisica Generale I
- Informatica di Base

Confermi la selezione? (s/n): s

Calendario filtrato salvato in: filtered_calendar.ics

Processo completato! Calendario filtrato con 3 corsi.
```

## 🆘 Risoluzione problemi

### Errore "Import could not be resolved"
Le dipendenze sono già installate nell'ambiente virtuale. Assicurati di averlo attivato:
```bash
source .venv/bin/activate
```

### Errore di download del calendario
- Verifica che l'URL sia corretto e accessibile
- Controlla la connessione internet
- Alcuni calendari potrebbero richiedere autenticazione

### Calendario vuoto o nessun corso trovato
- Il formato del calendario potrebbe essere diverso
- Personalizza la funzione `extract_course_name()` nel codice

### Aggiornamenti non rilevati
- Lo script confronta l'hash del contenuto del calendario
- Se le modifiche sono solo nei metadati, potrebbe non rilevarle
- Usa `--force` per forzare l'aggiornamento

## 🤝 Supporto

Se hai problemi o suggerimenti:
1. Controlla che l'URL del calendario sia corretto
2. Verifica che il formato sia ICS standard
3. Prova a eseguire `python example_usage.py` per vedere un esempio

## 📄 Licenza

Questo progetto è open source. Puoi modificarlo e adattarlo alle tue esigenze.