from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from calendar_manager import UniversityCalendarManager


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Leggi il body della richiesta
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            session_id = data.get('session_id')
            selected_courses = data.get('selected_courses', [])
            calendar_url = data.get('calendar_url')
            
            if not session_id or not selected_courses:
                self.send_error_response({'error': 'Dati mancanti per la generazione'}, 400)
                return
            
            # Recupera i dati del calendario salvati in /tmp; fallback: scarica di nuovo dall'URL
            temp_file = f'/tmp/{session_id}_calendar.txt'
            calendar_data = None
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    calendar_data = f.read()
            
            # Crea manager e processa
            manager = UniversityCalendarManager(calendar_url)
            # Se manca il file temporaneo, prova a scaricare nuovamente usando l'URL
            if not calendar_data and calendar_url:
                try:
                    calendar_data = manager.download_calendar()
                except Exception as _:
                    pass
            if not calendar_data:
                self.send_error_response({'error': 'Impossibile ottenere il calendario. Riprova.'}, 400)
                return

            calendar = manager.parse_calendar(calendar_data)
            
            # Crea calendario filtrato
            filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)
            
            # Salva il calendario filtrato in /tmp
            output_path = f'/tmp/{session_id}_filtered.ics'
            
            with open(output_path, 'wb') as f:
                f.write(filtered_calendar.to_ical())
            
            # Salva anche la configurazione per link permanenti
            permanent_config = {
                'calendar_url': calendar_url,
                'selected_courses': selected_courses,
                'created_at': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
            
            config_file = f'/tmp/{session_id}_config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(permanent_config, f, indent=2, ensure_ascii=False)
            
            response_data = {
                'success': True,
                'download_url': f'/api/download?session_id={session_id}',
                'filename': f'calendario_filtrato_{datetime.now().strftime("%Y%m%d")}.ics',
                'selected_courses_count': len(selected_courses),
                'session_id': session_id
            }
            
            self.send_success_response(response_data)
            
        except Exception as e:
            self.send_error_response({'error': f'Errore durante la generazione: {str(e)}'}, 500)
    
    def do_OPTIONS(self):
        """Gestisce le richieste OPTIONS per CORS"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_success_response(self, data):
        """Invia una risposta di successo"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, data, status_code):
        """Invia una risposta di errore"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_cors_headers(self):
        """Invia gli header CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')