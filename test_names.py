#!/usr/bin/env python3
"""
Script di test per verificare l'estrazione dei nomi dei corsi
"""

from calendar_manager import UniversityCalendarManager

def test_course_names():
    """Testa l'estrazione dei nomi dei corsi"""
    
    # URL del calendario UNITO
    calendar_url = "https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f"
    
    # Crea il manager
    manager = UniversityCalendarManager(calendar_url)
    
    print("🔍 Test estrazione nomi corsi...")
    print("=" * 60)
    
    # Scarica il calendario
    calendar_data = manager.download_calendar()
    if not calendar_data:
        print("❌ Errore nel download del calendario")
        return
    
    # Parsifica il calendario
    calendar = manager.parse_calendar(calendar_data)
    if not calendar:
        print("❌ Errore nel parsing del calendario")
        return
    
    # Estrai i corsi
    courses = manager.extract_courses(calendar)
    
    print(f"📚 Corsi trovati: {len(courses)}")
    print("=" * 60)
    
    # Mostra i primi eventi di ogni corso per vedere i nomi completi
    for course_name, events in sorted(courses.items()):
        print(f"📖 {course_name}")
        print(f"   📅 {len(events)} eventi")
        if events:
            print(f"   📍 {events[0]['location']}")
            print(f"   👨‍🏫 {events[0]['description']}")
        print()

if __name__ == "__main__":
    test_course_names()