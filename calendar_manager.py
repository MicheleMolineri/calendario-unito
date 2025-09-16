#!/usr/bin/env python3
"""
Script per gestire il calendario universitario - Versione Serverless per Vercel
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
import tempfile


class UniversityCalendarManager:
    def __init__(self, calendar_url: str, temp_dir: str = None):
        """
        Inizializza il gestore del calendario universitario per ambiente serverless
        
        Args:
            calendar_url: URL del calendario universitario
            temp_dir: Directory temporanea per i file (per serverless)
        """
        self.calendar_url = calendar_url
        self.temp_dir = temp_dir or tempfile.gettempdir()
        
    def download_calendar(self) -> str:
        """
        Scarica il calendario dall'URL fornito
        
        Returns:
            Contenuto del calendario come stringa
        """
        try:
            headers = {
                'User-Agent': 'calendario-unito/1.0 (+https://vercel.app) Python-requests',
                'Accept': 'text/calendar, text/plain, */*'
            }
            # Timeout: (connect, read) kept under Vercel Hobby 10s limit
            response = requests.get(self.calendar_url, headers=headers, timeout=(5, 5))
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Errore durante il download del calendario: {e}")
    
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
            raise Exception(f"Errore durante il parsing del calendario: {e}")
    
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
        
        return filtered_cal
    
    def calculate_hash(self, data: str) -> str:
        """Calcola l'hash MD5 dei dati del calendario"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()