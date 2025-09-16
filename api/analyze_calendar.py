from http.server import BaseHTTPRequestHandler
import json
import hashlib
import tempfile
import os
from calendar_manager import UniversityCalendarManager
import time


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            t0 = time.time()
            # Leggi il body della richiesta
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            calendar_url = data.get('calendar_url', '').strip()
            
            if not calendar_url:
                self.send_error_response({'error': 'URL del calendario richiesto'}, 400)
                return
            
            # Crea manager temporaneo
            manager = UniversityCalendarManager(calendar_url)
            
            # Scarica e analizza il calendario
            calendar_data = manager.download_calendar()
            if not calendar_data:
                self.send_error_response({'error': 'Impossibile scaricare il calendario dall\'URL fornito'}, 400)
                return
            
            # Parsifica il calendario
            calendar = manager.parse_calendar(calendar_data)
            if not calendar:
                self.send_error_response({'error': 'Formato calendario non valido'}, 400)
                return
            
            # Estrai corsi (versione leggera e veloce)
            courses_list = manager.summarize_courses(calendar)
            if not courses_list:
                self.send_error_response({'error': 'Nessun corso trovato nel calendario'}, 400)
                return
            
            # Genera session ID
            session_id = hashlib.md5(calendar_url.encode()).hexdigest()
            
            # Salva temporaneamente i dati del calendario in /tmp per Vercel
            temp_file = f'/tmp/{session_id}_calendar.txt'
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(calendar_data)
            
            response_data = {
                'success': True,
                'courses': courses_list,
                'total_courses': len(courses_list),
                'session_id': session_id,
                'calendar_url': calendar_url,
                'elapsed': round(time.time() - t0, 2)
            }
            
            self.send_success_response(response_data)
            
        except Exception as e:
            self.send_error_response({'error': f'Errore durante l\'analisi: {str(e)}'}, 500)
    
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