# 🔗 Come Creare e Usare i Link iCal

## 📅 Cos'è un Link iCal?

Un link iCal è un URL che permette di **sottoscrivere** a un calendario, mantenendolo sempre aggiornato automaticamente. È molto più comodo del download di file perché:

- ✅ **Aggiornamento automatico**: Il calendario si aggiorna da solo
- ✅ **Sincronizzazione**: Funziona su tutti i tuoi dispositivi
- ✅ **Sempre aggiornato**: Ricevi le modifiche dell'università in tempo reale
- ✅ **Zero manutenzione**: Non devi scaricare file continuamente

## 🚀 Come Creare un Link iCal

### **Metodo 1: Interfaccia Web (Raccomandato)**

1. **Avvia il server**:
   ```bash
   cd /Users/michele/Desktop/UNITO/CalendarUni
   source .venv/bin/activate
   python app.py
   ```

2. **Vai su** http://localhost:5001

3. **Segui i passaggi**:
   - Inserisci l'URL del calendario UNITO
   - Seleziona i corsi di interesse
   - Clicca su "**Crea Link iCal**"

4. **Copia il link** WebCal generato

### **Metodo 2: Script di Test**

```bash
cd /Users/michele/Desktop/UNITO/CalendarUni
source .venv/bin/activate
python test_ical.py
```

## 📱 Come Usare il Link iCal

### **🍎 Apple Calendar (iPhone/iPad/Mac)**

**Su iPhone/iPad:**
1. Copia il link **WebCal**
2. Vai su **Impostazioni** → **Calendario** → **Account**
3. **Aggiungi Account** → **Altro** → **Aggiungi Calendario Sottoscritto**
4. Incolla il link WebCal

**Su Mac:**
1. Apri **Calendar**
2. **File** → **Nuova Sottoscrizione Calendario**
3. Incolla il link WebCal

### **📧 Google Calendar**

1. Vai su [calendar.google.com](https://calendar.google.com)
2. Sul lato sinistro, clicca **"+"** accanto a "Altri calendari"
3. Seleziona **"Da URL"**
4. Incolla il link **iCal (HTTP)**
5. Clicca **"Aggiungi calendario"**

### **🖥️ Microsoft Outlook**

**Outlook Desktop:**
1. **File** → **Gestione Account** → **Impostazioni Account**
2. Scheda **"Calendari Internet"** → **Nuovo**
3. Incolla il link iCal

**Outlook Web:**
1. Vai sul calendario online
2. **Aggiungi calendario** → **Da web**
3. Incolla il link iCal

### **📱 Android**

1. Copia il link **WebCal**
2. Apri il **browser** e incolla il link
3. Seleziona **"Aggiungi al Calendario"** quando richiesto
4. Oppure usa un'app calendario che supporta WebCal

## 🔧 Formato dei Link

Il sistema genera due tipi di link:

### **Link iCal (HTTP/HTTPS)**
```
http://localhost:5001/ical/54cad958b7aa3be5966f192ff2c51e7b
```
- Per Google Calendar, Outlook Web
- Funziona nei browser

### **Link WebCal**
```
webcal://localhost:5001/ical/54cad958b7aa3be5966f192ff2c51e7b
```
- Per Apple Calendar, app native
- Si apre automaticamente nell'app calendario

## ⚡ Aggiornamento Automatico

### **Come Funziona**
- Il server controlla periodicamente il calendario UNITO
- Se ci sono modifiche, aggiorna automaticamente il tuo calendario filtrato
- I client calendario sincronizzano le modifiche

### **Configurazione Aggiornamenti**

Puoi anche aggiornare manualmente:
```bash
curl http://localhost:5001/api/update_ical/54cad958b7aa3be5966f192ff2c51e7b
```

## 🛠️ Configurazione Server per Produzione

### **Per Rendere Accessibile da Internet**

1. **Modifica la porta** in `app.py` se necessario
2. **Configura il firewall** per aprire la porta
3. **Usa un dominio** o IP pubblico
4. **Considera HTTPS** per maggiore sicurezza

Esempio con dominio:
```python
app.run(debug=False, host='0.0.0.0', port=80)
```

I link diventerebbero:
```
http://tuodominio.com/ical/session_id
webcal://tuodominio.com/ical/session_id
```

## 🔒 Sicurezza e Privacy

- I link iCal sono **pubblici** ma **non facilmente indovinabili**
- Ogni sessione ha un **ID univoco** (hash MD5)
- I file temporanei vengono **puliti automaticamente**
- Non condividere i link iCal se non necessario

## 🧹 Manutenzione

### **Pulizia File Temporanei**
```bash
curl http://localhost:5001/cleanup
```

### **Verifica Link Attivi**
```bash
ls /Users/michele/Desktop/UNITO/CalendarUni/temp_calendars/
```

## ❓ Risoluzione Problemi

### **Link Non Funziona**
- Verifica che il server sia in esecuzione
- Controlla che il file session_id esista
- Prova a rigenerare il calendario

### **Calendario Non Si Aggiorna**
- Forza la sincronizzazione nell'app calendario
- Controlla la connessione internet
- Verifica che l'URL UNITO sia ancora valido

### **Errore 404**
- Il link potrebbe essere scaduto
- Rigenera il calendario e crea un nuovo link

## 📋 Esempi Completi

### **Creazione Link via API**

```bash
# 1. Analizza calendario
curl -X POST http://localhost:5001/api/analyze_calendar \
  -H "Content-Type: application/json" \
  -d '{"calendar_url": "https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f"}'

# 2. Genera calendario filtrato
curl -X POST http://localhost:5001/api/generate_calendar \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "selected_courses": ["LFT - LINGUAGGI E FORMALI E TRADUTTORI"], "calendar_url": "URL"}'

# 3. Crea link permanente
curl -X POST http://localhost:5001/api/create_permanent_link \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "calendar_url": "URL", "selected_courses": ["CORSO1", "CORSO2"]}'
```

---

🎓 **Il tuo calendario UNITO personalizzato è ora sempre aggiornato e sincronizzato su tutti i dispositivi!**