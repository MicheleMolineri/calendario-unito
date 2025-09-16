from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import os
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parsifica la query string
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            session_id = query_params.get('session_id', [None])[0]
            
            if not session_id:
                self.send_error_response('Session ID richiesto', 400)
                return
            
            # Controlla se il file esiste
            file_path = f'/tmp/{session_id}_filtered.ics'
            
            if not os.path.exists(file_path):
                self.send_error_response('File non trovato. Rigenera il calendario.', 404)
                return
            
            # Leggi il file
            with open(file_path, 'rb') as f:
                calendar_data = f.read()
            
            # Nome file per il download
            download_name = f'calendario_unito_filtrato_{datetime.now().strftime("%Y%m%d")}.ics'
            
            # Invia il file
            self.send_response(200)
            self.send_header('Content-Type', 'text/calendar')
            self.send_header('Content-Disposition', f'attachment; filename="{download_name}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(calendar_data)))
            self.end_headers()
            self.wfile.write(calendar_data)
            
        except Exception as e:
            self.send_error_response(f'Errore durante il download: {str(e)}', 500)
    
    def send_error_response(self, message, status_code):
        """Invia una risposta di errore"""
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))