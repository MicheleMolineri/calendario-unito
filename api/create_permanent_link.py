from http.server import BaseHTTPRequestHandler
import json
import base64
from urllib.parse import urlparse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            calendar_url = data.get('calendar_url')
            selected_courses = data.get('selected_courses', [])
            
            if not all([calendar_url, selected_courses]):
                self.send_error_response({'error': 'Dati mancanti'}, 400)
                return
            
            # Estrai l'host dalla richiesta per generare URL assoluti
            host = self.headers.get('Host', 'localhost')
            # La X-Forwarded-Proto ci dice il protocollo originale usato dal client
            protocol = self.headers.get('X-Forwarded-Proto', 'http')
            base_url = f"{protocol}://{host}"

            # Encoda la configurazione come parametro URL (base64 url-safe)
            cfg_payload = {
                'url': calendar_url,
                'corsi': selected_courses
            }
            cfg_str = json.dumps(cfg_payload, separators=(',', ':'))
            cfg_enc = base64.urlsafe_b64encode(cfg_str.encode('utf-8')).decode('ascii').rstrip('=')

            # Link iCal con la configurazione encodata
            ical_url = f"{base_url}/api/ical?cfg={cfg_enc}"
            
            response_data = {
                'success': True,
                'ical_url': ical_url,
                'webcal_url': ical_url.replace('http://', 'webcal://').replace('https://', 'webcal://'),
            }
            
            self.send_success_response(response_data)
            
        except Exception as e:
            self.send_error_response({'error': f'Errore nella creazione del link: {str(e)}'}, 500)

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