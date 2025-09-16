#!/usr/bin/env python3
"""
Script per l'aggiornamento automatico del calendario universitario
Può essere eseguito periodicamente (es. con cron) per mantenere
il calendario sempre aggiornato
"""

import os
import sys
import json
from datetime import datetime, timedelta
from calendar_manager import UniversityCalendarManager


def load_config(config_file="calendar_config.json"):
    """Carica la configurazione salvata"""
    if not os.path.exists(config_file):
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def should_check_for_updates(config, force=False):
    """
    Determina se è il momento di controllare gli aggiornamenti
    
    Args:
        config: Configurazione caricata
        force: Forza il controllo anche se non è il momento
    
    Returns:
        True se deve controllare, False altrimenti
    """
    if force:
        return True
    
    if not config or not config.get("last_update"):
        return True
    
    # Controlla ogni ora per default
    last_update = datetime.fromisoformat(config["last_update"])
    time_diff = datetime.now() - last_update
    
    return time_diff > timedelta(hours=1)


def auto_update_calendar(calendar_url, force=False, verbose=True):
    """
    Aggiorna automaticamente il calendario se necessario
    
    Args:
        calendar_url: URL del calendario
        force: Forza l'aggiornamento
        verbose: Mostra output dettagliato
    
    Returns:
        True se il calendario è stato aggiornato, False altrimenti
    """
    if verbose:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Controllo aggiornamenti calendario...")
    
    # Carica la configurazione esistente
    config = load_config()
    
    if not config or not config.get("selected_courses"):
        if verbose:
            print("Errore: Nessuna configurazione trovata.")
            print("Esegui prima: python calendar_manager.py <URL_CALENDARIO>")
        return False
    
    # Controlla se è il momento di aggiornare
    if not should_check_for_updates(config, force):
        if verbose:
            print("Aggiornamento non necessario (controllato di recente).")
        return False
    
    # Crea il manager e controlla aggiornamenti
    manager = UniversityCalendarManager(calendar_url)
    manager.config = config
    
    try:
        # Scarica e verifica il calendario
        calendar_data = manager.download_calendar()
        if not calendar_data:
            if verbose:
                print("Errore: Impossibile scaricare il calendario.")
            return False
        
        # Calcola l'hash e confronta
        current_hash = manager.calculate_hash(calendar_data)
        
        if config.get("calendar_hash") != current_hash:
            if verbose:
                print("Aggiornamento rilevato! Aggiornamento del calendario filtrato...")
            
            # Parsifica e crea il calendario filtrato
            calendar = manager.parse_calendar(calendar_data)
            if not calendar:
                if verbose:
                    print("Errore: Impossibile parsificare il calendario.")
                return False
            
            # Crea il calendario filtrato
            filtered_calendar = manager.create_filtered_calendar(
                calendar, config["selected_courses"]
            )
            
            # Salva il calendario aggiornato
            manager.save_filtered_calendar(filtered_calendar)
            
            # Aggiorna la configurazione
            config["calendar_hash"] = current_hash
            config["last_update"] = datetime.now().isoformat()
            manager.config = config
            manager.save_config()
            
            if verbose:
                print("Calendario aggiornato con successo!")
            return True
        else:
            if verbose:
                print("Nessun aggiornamento necessario.")
            
            # Aggiorna solo il timestamp
            config["last_update"] = datetime.now().isoformat()
            manager.config = config
            manager.save_config()
            return False
            
    except Exception as e:
        if verbose:
            print(f"Errore durante l'aggiornamento: {e}")
        return False


def create_cron_script():
    """Crea uno script bash per l'esecuzione con cron"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, "update_calendar.sh")
    
    # Leggi l'URL dalla configurazione se disponibile
    config = load_config()
    calendar_url = "YOUR_CALENDAR_URL_HERE"
    
    if config and hasattr(config, 'calendar_url'):
        calendar_url = config['calendar_url']
    
    script_content = f"""#!/bin/bash
# Script per l'aggiornamento automatico del calendario universitario
# Aggiungi questo al crontab per eseguirlo periodicamente

cd "{current_dir}"
source .venv/bin/activate
python auto_update.py "{calendar_url}" >> calendar_update.log 2>&1
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Rendi eseguibile
        os.chmod(script_path, 0o755)
        
        print(f"Script cron creato: {script_path}")
        print("\nPer configurare l'aggiornamento automatico:")
        print("1. Modifica l'URL nel file update_calendar.sh")
        print("2. Aggiungi al crontab:")
        print(f"   # Aggiorna ogni ora")
        print(f"   0 * * * * {script_path}")
        print(f"   # Oppure ogni 30 minuti")
        print(f"   */30 * * * * {script_path}")
        
    except Exception as e:
        print(f"Errore nella creazione dello script cron: {e}")


def main():
    """Funzione principale"""
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python auto_update.py <URL_CALENDARIO> [opzioni]")
        print("\nOpzioni:")
        print("  --force      Forza l'aggiornamento anche se non necessario")
        print("  --quiet      Modalità silenziosa (solo errori)")
        print("  --setup-cron Crea script per cron")
        print("\nEsempi:")
        print("  python auto_update.py https://university.edu/calendar.ics")
        print("  python auto_update.py https://university.edu/calendar.ics --force")
        print("  python auto_update.py setup --setup-cron")
        return
    
    if sys.argv[1] == "setup" and "--setup-cron" in sys.argv:
        create_cron_script()
        return
    
    calendar_url = sys.argv[1]
    force = "--force" in sys.argv
    verbose = "--quiet" not in sys.argv
    
    success = auto_update_calendar(calendar_url, force, verbose)
    
    # Exit code per script esterni
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()