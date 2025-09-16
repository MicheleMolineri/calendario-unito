from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import json
from datetime import datetime
from calendar_manager import UniversityCalendarManager


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Estrai session_id dal path (/api/ical/<session_id>) oppure dalla query (?session_id=...)
            session_id = None
            parsed = urlparse(self.path)
            # Prova a leggere da path segment
            parts = parsed.path.strip('/').split('/')  # es: ['api','ical','<session_id>']
            if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'ical':
                candidate = parts[2]
                if candidate:
                    session_id = candidate
            # Fallback: query string
            if not session_id:
                qs = parse_qs(parsed.query)
                session_id = (qs.get('session_id') or [None])[0]
            if not session_id:
                self.send_error_response('Session ID richiesto', 400)
                return
            
            # Prima controlla se esiste già un calendario filtrato
            file_path = f'/tmp/{session_id}_filtered.ics'
            config_file = f'/tmp/{session_id}_config.json'
            
            # Se non esiste il calendario o la configurazione, prova ad aggiornarlo
            if not os.path.exists(file_path) or not os.path.exists(config_file):
                self.send_error_response('Calendario non trovato. Rigenera il calendario.', 404)
                return
            
            # Carica la configurazione per aggiornamenti automatici
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                calendar_url = config.get('calendar_url')
                selected_courses = config.get('selected_courses', [])
                
                if calendar_url and selected_courses:
                    # Aggiorna il calendario se necessario (ogni volta per ora)
                    manager = UniversityCalendarManager(calendar_url)
                    calendar_data = manager.download_calendar()
                    
                    if calendar_data:
                        calendar = manager.parse_calendar(calendar_data)
                        if calendar:
                            # Crea calendario filtrato aggiornato
                            filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)
                            
                            # Salva il calendario aggiornato
                            with open(file_path, 'wb') as f:
                                f.write(filtered_calendar.to_ical())
                            
                            # Aggiorna il timestamp
                            config['last_update'] = datetime.now().isoformat()
                            with open(config_file, 'w', encoding='utf-8') as f:
                                json.dump(config, f, indent=2, ensure_ascii=False)
            except:
                # Se fallisce l'aggiornamento, usa il file esistente
                pass
            
            # Leggi e servi il file calendario
            with open(file_path, 'rb') as f:
                calendar_data = f.read()
            
            # Servi il file ICS per la sottoscrizione
            self.send_response(200)
            self.send_header('Content-Type', 'text/calendar; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(calendar_data)))
            self.end_headers()
            self.wfile.write(calendar_data)
            
        except Exception as e:
            self.send_error_response(f'Errore nel servire il calendario: {str(e)}', 500)
    
    def send_error_response(self, message, status_code):
        """Invia una risposta di errore"""
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))