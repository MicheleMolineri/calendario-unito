from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import hashlib
from calendar_manager import UniversityCalendarManager

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            calendar_url = data.get('calendar_url', '').strip()
            
            selected_courses = data.get('selected_courses') # Può essere None se si analizza solo

            if not calendar_url:
                self.send_error_response({'error': 'URL del calendario richiesto'}, 400)
                return

            manager = UniversityCalendarManager(calendar_url)
            
            # Scarica e analizza il calendario
            calendar_data = manager.download_calendar()
            if not calendar_data:
                self.send_error_response({'error': 'Impossibile scaricare il calendario'}, 400)
                return

            calendar = manager.parse_calendar(calendar_data)
            if not calendar:
                self.send_error_response({'error': 'Formato calendario non valido'}, 400)
                return

            # Se non sono stati forniti corsi, siamo in modalità "analisi"
            if selected_courses is None:
                courses_list = manager.summarize_courses(calendar)
                session_id = hashlib.md5(calendar_url.encode()).hexdigest()
                
                # Salva il calendario originale per dopo
                temp_file = f'/tmp/{session_id}_calendar.txt'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(calendar_data)

                response_data = {
                    'success': True,
                    'courses': courses_list,
                    'session_id': session_id,
                    'calendar_url': calendar_url
                }
                self.send_success_response(response_data)
                return

            # Se sono stati forniti i corsi, siamo in modalità "generazione"
            if not selected_courses:
                self.send_error_response({'error': 'Nessun corso selezionato'}, 400)
                return

            session_id = data.get('session_id')
            if not session_id:
                 self.send_error_response({'error': 'ID sessione mancante'}, 400)
                 return

            filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)
            output_path = f'/tmp/{session_id}_filtered.ics'
            with open(output_path, 'wb') as f:
                f.write(filtered_calendar.to_ical())

            response_data = {
                'success': True,
                'download_url': f'/api/download?session_id={session_id}',
                'session_id': session_id
            }
            self.send_success_response(response_data)

        except Exception as e:
            self.send_error_response({'error': f'Errore: {str(e)}'}, 500)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, data, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))