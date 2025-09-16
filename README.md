# 📅 Calendario UNITO - Versione Vercel

Versione serverless dell'applicazione per filtrare il calendario universitario di UNITO, ottimizzata per il deployment su Vercel.

## 🚀 Deployment su Vercel

### Prerequisiti
- Account Vercel (gratuito su [vercel.com](https://vercel.com))
- Vercel CLI (opzionale)


### Deploy Automatico via GitHub
1. Fai push di questa cartella su un repository GitHub
2. Connetti il repository a Vercel
3. Deploy automatico!

### Deploy via Vercel CLI

1. **Installa Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   cd vercel-app
   vercel
   ```

4. **Deploy in produzione:**
   ```bash
   vercel --prod
   ```

## 📁 Struttura

```
vercel-app/
├── api/                              # Funzioni serverless
│   ├── analyze_calendar.py          # Analizza calendario
│   ├── generate_calendar.py         # Genera calendario filtrato
│   ├── download.py                  # Download calendario
│   ├── create_permanent_link.py     # Crea link iCal
│   └── ical.py                      # Endpoint iCal per sottoscrizioni
├── public/
│   └── index.html                   # Frontend web
├── calendar_manager.py              # Logica calendario (serverless)
├── requirements.txt                 # Dipendenze Python
├── vercel.json                      # Configurazione Vercel
└── README.md                        # Questo file
```

## 🔧 Configurazione

Il file `vercel.json` configura:
- Routing delle API e rewrites
- Runtime Python 3.12 (aggiornabile alle versioni supportate da Vercel)
- Gestione file statici
- CORS automatico

## 🌟 Funzionalità

- ✅ Analisi calendario UNITO
- ✅ Filtro corsi personalizzato
- ✅ Download calendario .ics
- ✅ Link iCal per sincronizzazione automatica
- ✅ Interfaccia web moderna
- ✅ Completamente serverless
- ✅ Gratuito su Vercel

## 📝 Come Usare

1. Vai all'URL del tuo deployment Vercel
2. Inserisci l'URL del calendario UNITO
3. Seleziona i corsi
4. Scarica o crea link permanente

## 🔗 Link Utili

- [Vercel Docs](https://vercel.com/docs)
- [Python su Vercel](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

## 🆚 Differenze dalla Versione Flask

- **Serverless**: Nessun server sempre attivo
- **Scalabilità**: Auto-scaling automatico
- **Costi**: Gratuito per uso personale
- **Performance**: Cold start possibili
- **Storage**: File temporanei in /tmp