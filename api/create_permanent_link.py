from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import base64


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Leggi il body della richiesta
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            session_id = data.get('session_id')
            calendar_url = data.get('calendar_url')
            selected_courses = data.get('selected_courses', [])
            
            if not all([session_id, calendar_url, selected_courses]):
                self.send_error_response({'error': 'Dati mancanti'}, 400)
                return
            
            # Salva la configurazione permanente per aggiornamenti automatici
            permanent_config = {
                'calendar_url': calendar_url,
                'selected_courses': selected_courses,
                'created_at': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
            
            config_file = f'/tmp/{session_id}_config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(permanent_config, f, indent=2, ensure_ascii=False)
            
            # Estrai l'host dalla richiesta per generare URL assoluti
            host = self.headers.get('Host', 'localhost')
            protocol = 'https' if 'vercel' in host else 'http'
            
            base_url = f"{protocol}://{host}"

            # Encoda la configurazione come fallback stateless nel link (base64 url-safe)
            cfg_payload = {
                'calendar_url': calendar_url,
                'selected_courses': selected_courses
            }
            cfg_str = json.dumps(cfg_payload, separators=(',', ':'))
            cfg_enc = base64.urlsafe_b64encode(cfg_str.encode('utf-8')).decode('ascii')

            # Link iCal con session_id e fallback cfg
            ical_url = f"{base_url}/api/ical/{session_id}?cfg={cfg_enc}"
            
            response_data = {
                'success': True,
                'ical_url': ical_url,
                'webcal_url': ical_url.replace('http://', 'webcal://').replace('https://', 'webcal://'),
                'instructions': [
                    'Copia il link iCal/webcal',
                    'Incollalo nel tuo client calendario preferito',
                    'Il calendario si aggiornerà automaticamente'
                ]
            }
            
            self.send_success_response(response_data)
            
        except Exception as e:
            self.send_error_response({'error': f'Errore nella creazione del link: {str(e)}'}, 500)
    
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