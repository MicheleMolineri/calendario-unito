#!/usr/bin/env python3
"""
Script per testare e utilizzare i link iCal
"""

import requests
import json

def test_ical_functionality():
    """Testa la funzionalità iCal"""
    
    base_url = "http://localhost:5001"
    
    print("🔗 Test funzionalità iCal")
    print("=" * 50)
    
    # Simula la creazione di un calendario e link iCal
    print("1. Analizza calendario...")
    
    # Primo step: analizza calendario
    analyze_response = requests.post(f"{base_url}/api/analyze_calendar", 
                                   json={"calendar_url": "https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f"})
    
    if analyze_response.status_code == 200:
        analyze_data = analyze_response.json()
        session_id = analyze_data['session_id']
        courses = analyze_data['courses']
        
        print(f"✅ Trovati {len(courses)} corsi")
        
        # Seleziona alcuni corsi di esempio
        selected_courses = [course['name'] for course in courses[:3]]  # Primi 3 corsi
        print(f"📚 Corsi selezionati: {', '.join(selected_courses)}")
        
        # Secondo step: genera calendario
        print("2. Genera calendario filtrato...")
        generate_response = requests.post(f"{base_url}/api/generate_calendar",
                                        json={
                                            "session_id": session_id,
                                            "selected_courses": selected_courses,
                                            "calendar_url": analyze_data['calendar_url']
                                        })
        
        if generate_response.status_code == 200:
            print("✅ Calendario generato")
            
            # Terzo step: crea link iCal permanente
            print("3. Crea link iCal...")
            link_response = requests.post(f"{base_url}/api/create_permanent_link",
                                        json={
                                            "session_id": session_id,
                                            "calendar_url": analyze_data['calendar_url'],
                                            "selected_courses": selected_courses
                                        })
            
            if link_response.status_code == 200:
                link_data = link_response.json()
                
                print("✅ Link iCal creato!")
                print(f"🔗 Link HTTP: {link_data['ical_url']}")
                print(f"📱 Link WebCal: {link_data['webcal_url']}")
                
                # Testa il link iCal
                print("4. Testa il link iCal...")
                ical_response = requests.get(link_data['ical_url'])
                
                if ical_response.status_code == 200:
                    print("✅ Link iCal funzionante!")
                    
                    # Conta gli eventi nel calendario
                    ical_content = ical_response.text
                    event_count = ical_content.count('BEGIN:VEVENT')
                    print(f"📅 Eventi nel calendario iCal: {event_count}")
                    
                    print("\n" + "=" * 50)
                    print("🎉 SUCCESSO! Link iCal creato e testato")
                    print("=" * 50)
                    print("\n📋 Come utilizzare:")
                    print(f"1. Copia questo link: {link_data['webcal_url']}")
                    print("2. Aprilo nel tuo browser o client calendario")
                    print("3. Il calendario si aggiornerà automaticamente")
                    
                    return link_data
                else:
                    print(f"❌ Errore nel test del link iCal: {ical_response.status_code}")
            else:
                print(f"❌ Errore nella creazione del link: {link_response.status_code}")
                print(link_response.text)
        else:
            print(f"❌ Errore nella generazione: {generate_response.status_code}")
            print(generate_response.text)
    else:
        print(f"❌ Errore nell'analisi: {analyze_response.status_code}")
        print(analyze_response.text)
    
    return None


def create_ical_instructions():
    """Crea le istruzioni per l'uso dei link iCal"""
    
    instructions = """
📱 COME USARE I LINK iCAL
========================

🍎 Apple Calendar (iPhone/iPad/Mac):
1. Copia il link WebCal
2. Apri Impostazioni → Calendario → Account
3. Aggiungi Account → Altro → Aggiungi Calendario Sottoscritto
4. Incolla il link WebCal

📧 Google Calendar:
1. Vai su calendar.google.com
2. Sul lato sinistro, clicca su "+" accanto a "Altri calendari"
3. Seleziona "Da URL"
4. Incolla il link iCal (HTTP)

🖥️ Outlook:
1. Apri Outlook
2. File → Gestione Account → Impostazioni Account
3. Scheda "Calendari Internet" → Nuovo
4. Incolla il link iCal

📱 Dispositivi Android:
1. Copia il link WebCal
2. Apri il browser e incolla il link
3. Seleziona "Aggiungi al Calendario" quando richiesto

⚡ VANTAGGI dei link iCal:
- ✅ Aggiornamento automatico
- ✅ Sincronizzazione su tutti i dispositivi
- ✅ Non occupa spazio di archiviazione
- ✅ Sempre la versione più recente
"""
    
    print(instructions)


if __name__ == "__main__":
    print("🚀 Assicurati che il server Flask sia in esecuzione su http://localhost:5001")
    input("Premi Enter per continuare...")
    
    # Testa la funzionalità
    result = test_ical_functionality()
    
    if result:
        print("\n" * 2)
        create_ical_instructions()
    else:
        print("\n❌ Test fallito. Verifica che il server Flask sia in esecuzione.")