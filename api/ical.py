from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
import json
from calendar_manager import UniversityCalendarManager

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            cfg_param = qs.get('cfg', [None])[0]

            if not cfg_param:
                self.send_error_response('Configurazione mancante', 400)
                return

            # Decodifica la configurazione da base64
            try:
                # Aggiungi padding se necessario
                cfg_json = base64.urlsafe_b64decode(cfg_param + '===').decode('utf-8')
                cfg = json.loads(cfg_json)
                calendar_url = cfg.get('url')
                selected_courses = cfg.get('corsi', [])
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                self.send_error_response(f'Configurazione non valida: {e}', 400)
                return

            if not calendar_url or not selected_courses:
                self.send_error_response('URL calendario o corsi mancanti nella configurazione', 400)
                return

            # Processa il calendario
            manager = UniversityCalendarManager(calendar_url)
            calendar_data = manager.download_calendar()
            if not calendar_data:
                self.send_error_response('Impossibile scaricare il calendario originale', 502)
                return
            
            calendar = manager.parse_calendar(calendar_data)
            filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)
            
            # Servi il calendario filtrato
            data = filtered_calendar.to_ical()
            self.send_response(200)
            self.send_header('Content-Type', 'text/calendar; charset=utf-8')
            # Cache per 1 ora per non sovraccaricare il server di origine
            self.send_header('Cache-Control', 'public, max-age=3600, s-maxage=3600')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except Exception as e:
            self.send_error_response(f'Errore nel servire il calendario: {str(e)}', 500)

    def send_error_response(self, message, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))