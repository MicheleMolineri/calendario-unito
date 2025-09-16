# 🚀 GUIDA DEPLOYMENT VERCEL

## Metodo 1: Deploy via GitHub (CONSIGLIATO)

### Passo 1: Crea Repository GitHub
1. Vai su [github.com](https://github.com) e crea un nuovo repository
2. Chiamalo ad esempio `calendario-unito-vercel`
3. Mantienilo pubblico o privato (a tua scelta)

### Passo 2: Upload dei File
1. Scarica tutti i file da questa cartella `vercel-app/`
2. Caricali nel repository GitHub (puoi farlo via web interface)

**File da caricare:**
```
- api/analyze_calendar.py
- api/create_permanent_link.py  
- api/download.py
- api/generate_calendar.py
- api/ical.py
- public/index.html
- calendar_manager.py
- requirements.txt
- vercel.json
- README.md
```

### Passo 3: Connetti a Vercel
1. Vai su [vercel.com](https://vercel.com)
2. Clicca "Sign Up" e accedi con GitHub
3. Clicca "New Project"
4. Seleziona il repository `calendario-unito-vercel`
5. Clicca "Deploy"

### Passo 4: Configurazione (Automatica)
Vercel rileverà automaticamente:
- ✅ Funzioni Python in `/api`
- ✅ File statici in `/public`  
- ✅ Configurazione da `vercel.json`

### Passo 5: Test
Una volta completato il deploy:
1. Vercel ti darà un URL tipo `https://calendario-unito-vercel.vercel.app`
2. Vai al tuo URL
3. Testa l'applicazione!

---

## Metodo 2: Deploy Manuale via Vercel CLI

### Prerequisiti
```bash
# Installa Node.js da nodejs.org
# Poi installa Vercel CLI:
npm install -g vercel
```

### Deploy
```bash
cd vercel-app
vercel login
vercel
```

---

## 🔧 Personalizzazioni

### Dominio Personalizzato
1. In Vercel Dashboard > Settings > Domains
2. Aggiungi il tuo dominio
3. Configura DNS come richiesto

### Variabili d'Ambiente
Se vuoi aggiungere configurazioni:
1. Vercel Dashboard > Settings > Environment Variables
2. Aggiungi le tue variabili

### Monitoring
- Vercel Dashboard > Functions
- Vercel Dashboard > Analytics

---

## 📊 Limiti Piano Gratuito

- ✅ 100 GB-ore di compute/mese 
- ✅ 100 MB limite funzione
- ✅ 10 secondi timeout
- ✅ Domini .vercel.app gratuiti
- ✅ Certificati SSL automatici

**Per il tuo uso: PERFETTO! 🎉**

---

## 🆘 Risoluzione Problemi

### Errore "Module not found"
- Controlla che `requirements.txt` sia presente
- Verifica che i moduli siano nelle versioni corrette

### Errore 500 nelle funzioni
- Controlla i log in Vercel Dashboard
- Le eccezioni Python vengono mostrate nei log

### File non trovati
- Assicurati che tutti i file siano nel repository
- Controlla che la struttura sia corretta

---

## 🎯 Prossimi Passi

1. **Deploy su Vercel** ✅
2. **Testa l'applicazione**
3. **Condividi l'URL con i tuoi colleghi!**
4. **Goditi il calendario filtrato!** 🎉

---

**URL di esempio finale:**
`https://tuo-nome-calendario-unito.vercel.app`