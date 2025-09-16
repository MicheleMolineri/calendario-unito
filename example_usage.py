#!/usr/bin/env python3
"""
Script di esempio per utilizzare il gestore del calendario universitario
"""

from calendar_manager import UniversityCalendarManager


def example_usage():
    """Esempio di utilizzo dello script"""
    
    # URL di esempio - sostituisci con il tuo URL del calendario
    calendar_url = "https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f"
    
    print("="*60)
    print("ESEMPIO DI UTILIZZO DEL GESTORE CALENDARIO")
    print("="*60)
    
    print("\n1. CONFIGURAZIONE INIZIALE")
    print("-" * 30)
    print("Per utilizzare lo script, sostituisci l'URL di esempio con il tuo:")
    print(f"URL attuale: {calendar_url}")
    print("\nPoi esegui:")
    print("python calendar_manager.py <TUO_URL_CALENDARIO>")
    
    print("\n2. FUNZIONALITÀ PRINCIPALI")
    print("-" * 30)
    print("✓ Scarica automaticamente il calendario dall'URL")
    print("✓ Mostra tutti i corsi disponibili")
    print("✓ Permette di selezionare solo i corsi di interesse")
    print("✓ Crea un calendario filtrato (file .ics)")
    print("✓ Rileva automaticamente gli aggiornamenti")
    print("✓ Mantiene le tue preferenze salvate")
    
    print("\n3. MODALITÀ DI UTILIZZO")
    print("-" * 30)
    print("Modalità interattiva (prima volta):")
    print("  python calendar_manager.py <URL_CALENDARIO>")
    print("\nAggiornamento automatico:")
    print("  python calendar_manager.py <URL_CALENDARIO> --auto-update")
    
    print("\n4. FILE GENERATI")
    print("-" * 30)
    print("- calendar_config.json: Configurazione e corsi selezionati")
    print("- filtered_calendar.ics: Calendario filtrato da importare")
    print("- calendar_cache.pkl: Cache per ottimizzazioni (opzionale)")
    
    print("\n5. IMPORTAZIONE DEL CALENDARIO")
    print("-" * 30)
    print("Il file 'filtered_calendar.ics' può essere importato in:")
    print("- Google Calendar")
    print("- Apple Calendar")
    print("- Outlook")
    print("- Qualsiasi app che supporti il formato ICS")


def demo_with_sample_data():
    """Dimostra il funzionamento con dati di esempio"""
    
    print("\n" + "="*60)
    print("DEMO CON DATI DI ESEMPIO")
    print("="*60)
    
    # Crea dati di esempio
    sample_calendar_data = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//University//Calendar//EN
BEGIN:VEVENT
UID:math101-001@university.edu
DTSTART:20240916T090000Z
DTEND:20240916T110000Z
SUMMARY:Matematica I - Lezione
DESCRIPTION:Corso di Matematica I
LOCATION:Aula A1
RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR
END:VEVENT
BEGIN:VEVENT
UID:phys101-001@university.edu
DTSTART:20240917T140000Z
DTEND:20240917T160000Z
SUMMARY:Fisica I - Laboratorio
DESCRIPTION:Laboratorio di Fisica I
LOCATION:Lab F2
RRULE:FREQ=WEEKLY;BYDAY=TU,TH
END:VEVENT
BEGIN:VEVENT
UID:chem101-001@university.edu
DTSTART:20240918T100000Z
DTEND:20240918T120000Z
SUMMARY:Chimica Generale
DESCRIPTION:Corso base di chimica
LOCATION:Aula C3
RRULE:FREQ=WEEKLY;BYDAY=WE
END:VEVENT
END:VCALENDAR"""
    
    print("Questo è un esempio di come lo script elaborerebbe un calendario con:")
    print("- Matematica I (3 lezioni/settimana)")
    print("- Fisica I (2 laboratori/settimana)")  
    print("- Chimica Generale (1 lezione/settimana)")
    
    print("\nLo script ti permetterebbe di:")
    print("1. Vedere tutti i corsi disponibili")
    print("2. Selezionare solo quelli che ti interessano (es. solo Matematica e Fisica)")
    print("3. Generare un calendario personalizzato")
    print("4. Mantenerlo aggiornato automaticamente")


if __name__ == "__main__":
    example_usage()
    demo_with_sample_data()