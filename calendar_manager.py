#!/usr/bin/env python3
"""
Script per gestire il calendario universitario
Permette di scaricare, visualizzare, filtrare e aggiornare automaticamente
il calendario delle lezioni universitarie.
"""

import requests
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Set
from icalendar import Calendar, Event
import pickle


class UniversityCalendarManager:
    def __init__(self, calendar_url: str, config_file: str = "calendar_config.json"):
        """
        Inizializza il gestore del calendario universitario
        
        Args:
            calendar_url: URL del calendario universitario
            config_file: File di configurazione per salvare le preferenze
        """
        self.calendar_url = calendar_url
        self.config_file = config_file
        self.cache_file = "calendar_cache.pkl"
        self.filtered_calendar_file = "filtered_calendar.ics"
        
        # Carica la configurazione esistente
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Carica la configurazione dal file JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Configurazione di default
        return {
            "selected_courses": [],
            "last_update": None,
            "calendar_hash": None,
            "auto_update": True
        }
    
    def save_config(self):
        """Salva la configurazione nel file JSON"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def download_calendar(self) -> str:
        """
        Scarica il calendario dall'URL fornito
        
        Returns:
            Contenuto del calendario come stringa
        """
        try:
            print(f"Scaricando calendario da: {self.calendar_url}")
            response = requests.get(self.calendar_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Errore durante il download del calendario: {e}")
            return None
    
    def parse_calendar(self, calendar_data: str) -> Calendar:
        """
        Parsifica il calendario ICS
        
        Args:
            calendar_data: Dati del calendario in formato stringa
            
        Returns:
            Oggetto Calendar parsificato
        """
        try:
            return Calendar.from_ical(calendar_data)
        except Exception as e:
            print(f"Errore durante il parsing del calendario: {e}")
            return None
    
    def extract_courses(self, calendar: Calendar) -> Dict[str, List[Dict]]:
        """
        Estrae tutti i corsi dal calendario
        
        Args:
            calendar: Oggetto Calendar
            
        Returns:
            Dizionario con i corsi e i relativi eventi
        """
        courses = {}
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                # Estrai informazioni dell'evento
                summary = str(component.get('summary', ''))
                description = str(component.get('description', ''))
                location = str(component.get('location', ''))
                start_time = component.get('dtstart').dt
                end_time = component.get('dtend').dt
                
                # Estrai il nome del corso (di solito è nella summary)
                course_name = self.extract_course_name(summary, description)
                
                if course_name not in courses:
                    courses[course_name] = []
                
                event_info = {
                    'summary': summary,
                    'description': description,
                    'location': location,
                    'start': start_time,
                    'end': end_time,
                    'component': component
                }
                
                courses[course_name].append(event_info)
        
        return courses
    
    def extract_course_name(self, summary: str, description: str) -> str:
        """
        Estrae il nome del corso dal summary o description
        Questa funzione può essere personalizzata in base al formato del calendario
        """
        # Rimuovi caratteri comuni e normalizza
        course_name = summary.strip()
        
        # Per il calendario UNITO, il formato è: "SIGLA - NOME COMPLETO"
        # Esempio: "LFT - LINGUAGGI E FORMALI E TRADUTTORI"
        if ' - ' in course_name:
            parts = course_name.split(' - ', 1)  # Split solo al primo " - "
            if len(parts) >= 2:
                sigla = parts[0].strip()
                nome_completo = parts[1].strip()
                
                # Pulisci il nome completo rimuovendo eventuali informazioni aggiuntive
                # Rimuovi tutto dopo "(" se presente
                nome_completo = nome_completo.split('(')[0].strip()
                
                # Restituisci il formato "SIGLA - NOME COMPLETO"
                return f"{sigla} - {nome_completo}"
            else:
                # Se non riesce a fare split, usa solo la sigla
                return parts[0].strip()
        else:
            # Se non c'è " - ", probabilmente è già in formato corto
            course_name = course_name.split('(')[0].strip()  # Rimuovi eventuali parentesi
            return course_name
        
        return course_name.strip()
    
    def display_available_courses(self, courses: Dict[str, List[Dict]]):
        """
        Mostra tutti i corsi disponibili
        
        Args:
            courses: Dizionario dei corsi estratti
        """
        print("\n" + "="*60)
        print("CORSI DISPONIBILI NEL CALENDARIO")
        print("="*60)
        
        sorted_courses = sorted(courses.keys())
        for i, course_name in enumerate(sorted_courses, 1):
            num_events = len(courses[course_name])
            print(f"{i:2d}. {course_name} ({num_events} eventi)")
        
        print(f"\nTotale: {len(sorted_courses)} corsi trovati")
    
    def select_courses_interactive(self, courses: Dict[str, List[Dict]]) -> List[str]:
        """
        Permette all'utente di selezionare i corsi di interesse
        
        Args:
            courses: Dizionario dei corsi disponibili
            
        Returns:
            Lista dei nomi dei corsi selezionati
        """
        self.display_available_courses(courses)
        
        print("\n" + "="*60)
        print("SELEZIONE CORSI")
        print("="*60)
        print("Inserisci i numeri dei corsi che ti interessano.")
        print("Puoi inserire:")
        print("- Numeri singoli: 1,3,5")
        print("- Intervalli: 1-5")
        print("- Combinazioni: 1,3-7,10")
        print("- 'all' per selezionare tutti")
        print("- 'none' per non selezionare nessuno")
        
        sorted_courses = sorted(courses.keys())
        
        while True:
            try:
                selection = input("\nInserisci la tua selezione: ").strip().lower()
                
                if selection == 'all':
                    return sorted_courses
                elif selection == 'none':
                    return []
                
                # Parsing della selezione
                selected_indices = set()
                parts = selection.split(',')
                
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # Intervallo
                        start, end = map(int, part.split('-'))
                        selected_indices.update(range(start, end + 1))
                    else:
                        # Numero singolo
                        selected_indices.add(int(part))
                
                # Converti indici in nomi dei corsi
                selected_courses = []
                for index in selected_indices:
                    if 1 <= index <= len(sorted_courses):
                        selected_courses.append(sorted_courses[index - 1])
                
                if selected_courses:
                    print(f"\nCorsi selezionati: {len(selected_courses)}")
                    for course in selected_courses:
                        print(f"- {course}")
                    
                    confirm = input("\nConfermi la selezione? (s/n): ").strip().lower()
                    if confirm in ['s', 'si', 'y', 'yes']:
                        return selected_courses
                else:
                    print("Nessun corso valido selezionato.")
                    
            except (ValueError, IndexError) as e:
                print(f"Formato non valido. Riprova. ({e})")
    
    def create_filtered_calendar(self, original_calendar: Calendar, 
                                selected_courses: List[str]) -> Calendar:
        """
        Crea un nuovo calendario con solo i corsi selezionati
        
        Args:
            original_calendar: Calendario originale
            selected_courses: Lista dei corsi da includere
            
        Returns:
            Nuovo calendario filtrato
        """
        # Crea un nuovo calendario
        filtered_cal = Calendar()
        
        # Aggiungi le proprietà di base del calendario
        filtered_cal.add('prodid', '-//CalendarUni//Filtered Calendar//EN')
        filtered_cal.add('version', '2.0')
        
        # Aggiungi solo gli eventi dei corsi selezionati
        events_added = 0
        for component in original_calendar.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary', ''))
                course_name = self.extract_course_name(summary, '')
                
                if course_name in selected_courses:
                    # Crea una copia pulita dell'evento
                    new_event = component.copy()
                    filtered_cal.add_component(new_event)
                    events_added += 1
        
        print(f"Eventi aggiunti al calendario filtrato: {events_added}")
        return filtered_cal
    
    def save_filtered_calendar(self, filtered_calendar: Calendar):
        """
        Salva il calendario filtrato su file
        
        Args:
            filtered_calendar: Calendario filtrato da salvare
        """
        try:
            with open(self.filtered_calendar_file, 'wb') as f:
                f.write(filtered_calendar.to_ical())
            print(f"\nCalendario filtrato salvato in: {self.filtered_calendar_file}")
        except Exception as e:
            print(f"Errore durante il salvataggio: {e}")
    
    def calculate_hash(self, data: str) -> str:
        """Calcola l'hash MD5 dei dati del calendario"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def check_for_updates(self) -> bool:
        """
        Verifica se ci sono aggiornamenti nel calendario
        
        Returns:
            True se ci sono aggiornamenti, False altrimenti
        """
        calendar_data = self.download_calendar()
        if not calendar_data:
            return False
        
        current_hash = self.calculate_hash(calendar_data)
        
        if self.config.get("calendar_hash") != current_hash:
            print("Rilevato aggiornamento nel calendario!")
            self.config["calendar_hash"] = current_hash
            self.config["last_update"] = datetime.now().isoformat()
            return True
        
        print("Nessun aggiornamento rilevato.")
        return False
    
    def run_interactive(self):
        """Esegue lo script in modalità interattiva"""
        print("="*60)
        print("GESTORE CALENDARIO UNIVERSITARIO")
        print("="*60)
        
        # Scarica il calendario
        calendar_data = self.download_calendar()
        if not calendar_data:
            print("Impossibile scaricare il calendario. Verifica l'URL.")
            return
        
        # Parsifica il calendario
        calendar = self.parse_calendar(calendar_data)
        if not calendar:
            print("Impossibile parsificare il calendario.")
            return
        
        # Estrai i corsi
        courses = self.extract_courses(calendar)
        if not courses:
            print("Nessun corso trovato nel calendario.")
            return
        
        # Mostra i corsi e permetti la selezione
        selected_courses = self.select_courses_interactive(courses)
        
        if selected_courses:
            # Salva la configurazione
            self.config["selected_courses"] = selected_courses
            self.config["calendar_hash"] = self.calculate_hash(calendar_data)
            self.config["last_update"] = datetime.now().isoformat()
            self.save_config()
            
            # Crea e salva il calendario filtrato
            filtered_calendar = self.create_filtered_calendar(calendar, selected_courses)
            self.save_filtered_calendar(filtered_calendar)
            
            print(f"\nProcesso completato! Calendario filtrato con {len(selected_courses)} corsi.")
        else:
            print("\nNessun corso selezionato. Processo annullato.")
    
    def auto_update(self):
        """Aggiorna automaticamente il calendario se necessario"""
        if not self.config.get("selected_courses"):
            print("Nessuna configurazione trovata. Esegui prima la configurazione interattiva.")
            return
        
        if self.check_for_updates():
            calendar_data = self.download_calendar()
            calendar = self.parse_calendar(calendar_data)
            filtered_calendar = self.create_filtered_calendar(
                calendar, self.config["selected_courses"]
            )
            self.save_filtered_calendar(filtered_calendar)
            self.save_config()
            print("Calendario aggiornato automaticamente!")
        else:
            print("Calendario già aggiornato.")


def main():
    """Funzione principale"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python calendar_manager.py <URL_CALENDARIO> [--auto-update]")
        print("\nEsempio:")
        print("python calendar_manager.py https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f")
        print("python calendar_manager.py https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f --auto-update")
        return
    
    calendar_url = sys.argv[1]
    auto_update_mode = "--auto-update" in sys.argv
    
    manager = UniversityCalendarManager(calendar_url)
    
    if auto_update_mode:
        manager.auto_update()
    else:
        manager.run_interactive()


if __name__ == "__main__":
    main()