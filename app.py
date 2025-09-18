#!/usr/bin/env python3
"""
Applicazione Flask per la gestione del calendario universitario
Interfaccia web moderna per selezionare e filtrare i corsi
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect
import os
import json
import base64
from datetime import datetime
import hashlib
from calendar_manager import UniversityCalendarManager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configurazione cartella upload
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'temp_calendars')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crea cartella se non esiste
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/api/analyze_calendar', methods=['POST'])
def analyze_calendar():
    """Analizza calendario"""
    try:
        data = request.get_json()
        calendar_url = data.get('calendar_url', '').strip()

        if not calendar_url:
            return jsonify({'error': 'URL richiesto'}), 400

        manager = UniversityCalendarManager(calendar_url)
        calendar_data = manager.download_calendar()

        if not calendar_data:
            return jsonify({'error': 'Impossibile scaricare calendario'}), 400

        calendar = manager.parse_calendar(calendar_data)
        if not calendar:
            return jsonify({'error': 'Formato calendario non valido'}), 400

        courses = manager.extract_courses(calendar)
        if not courses:
            return jsonify({'error': 'Nessun corso trovato'}), 400

        courses_list = []
        for course_name, events in courses.items():
            courses_list.append({
                'name': course_name,
                'events_count': len(events),
                'location': events[0]['location'] if events and events[0]['location'] else 'N/A'
            })

        courses_list.sort(key=lambda x: x['name'])

        session_id = hashlib.md5(calendar_url.encode()).hexdigest()
        temp_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_calendar.txt')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(calendar_data)

        return jsonify({
            'success': True,
            'courses': courses_list,
            'total_courses': len(courses_list),
            'session_id': session_id,
            'calendar_url': calendar_url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_calendar', methods=['POST'])
def generate_calendar():
    """Genera calendario filtrato"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        selected_courses = data.get('selected_courses', [])
        calendar_url = data.get('calendar_url')

        if not session_id or not selected_courses:
            return jsonify({'error': 'Dati mancanti'}), 400

        temp_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_calendar.txt')
        if not os.path.exists(temp_file):
            return jsonify({'error': 'Sessione scaduta'}), 400

        with open(temp_file, 'r', encoding='utf-8') as f:
            calendar_data = f.read()

        manager = UniversityCalendarManager(calendar_url)
        calendar = manager.parse_calendar(calendar_data)
        filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)

        output_filename = f'{session_id}_filtered.ics'
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        with open(output_path, 'wb') as f:
            f.write(filtered_calendar.to_ical())

        return jsonify({
            'success': True,
            'download_url': f'/download/{session_id}',
            'filename': f'calendario_filtrato_{datetime.now().strftime("%Y%m%d")}.ics'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<session_id>')
def download_calendar(session_id):
    """Download calendario"""
    filename = f'{session_id}_filtered.ics'
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return "File non trovato", 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f'calendario_unito_filtrato_{datetime.now().strftime("%Y%m%d")}.ics',
        mimetype='text/calendar'
    )

@app.route('/api/create_permanent_link', methods=['POST'])
def create_permanent_link():
    """Crea link iCal permanente"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        calendar_url = data.get('calendar_url')
        selected_courses = data.get('selected_courses', [])

        if not all([session_id, calendar_url, selected_courses]):
            return jsonify({'error': 'Dati mancanti'}), 400

        # Verifica che la sessione esista
        temp_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_calendar.txt')
        if not os.path.exists(temp_file):
            return jsonify({'error': 'Sessione scaduta'}), 400

        # Genera URL di base
        base_url = request.host_url.rstrip('/')

        # Encoda la configurazione
        cfg_payload = {
            'session_id': session_id,
            'url': calendar_url,
            'corsi': selected_courses
        }
        cfg_str = json.dumps(cfg_payload, separators=(',', ':'))
        cfg_enc = base64.urlsafe_b64encode(cfg_str.encode('utf-8')).decode('ascii').rstrip('=')

        # Link iCal
        ical_url = f"{base_url}/api/ical?cfg={cfg_enc}"
        webcal_url = ical_url.replace('http://', 'webcal://').replace('https://', 'webcal://')

        return jsonify({
            'success': True,
            'ical_url': ical_url,
            'webcal_url': webcal_url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ical')
def serve_ical():
    """Servi calendario iCal aggiornato"""
    try:
        cfg_param = request.args.get('cfg')
        if not cfg_param:
            return "Configurazione mancante", 400

        # Decodifica configurazione
        try:
            cfg_json = base64.urlsafe_b64decode(cfg_param + '===').decode('utf-8')
            cfg = json.loads(cfg_json)
            session_id = cfg.get('session_id')
            calendar_url = cfg.get('url')
            selected_courses = cfg.get('corsi', [])
        except Exception as e:
            return f"Configurazione non valida: {e}", 400

        if not all([session_id, calendar_url, selected_courses]):
            return "Parametri mancanti nella configurazione", 400

        # Scarica sempre calendario fresco (non usare cache sessione)
        print(f"Downloading fresh calendar from: {calendar_url}")
        manager = UniversityCalendarManager(calendar_url)
        calendar_data = manager.download_calendar()
        if not calendar_data:
            return "Impossibile scaricare calendario", 502

        # Processa calendario
        calendar = manager.parse_calendar(calendar_data)
        if not calendar:
            return "Formato calendario non valido", 400

        filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)

        # Servi calendario
        data = filtered_calendar.to_ical()
        response = app.response_class(
            data,
            mimetype='text/calendar; charset=utf-8'
        )
        # Cache minima per aggiornamenti rapidi
        response.headers.set('Cache-Control', 'public, max-age=300, s-maxage=300')  # 5 minuti
        response.headers.set('ETag', hashlib.md5(data).hexdigest())
        response.headers.set('Last-Modified', datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        return response

    except Exception as e:
        print(f"Error serving iCal: {e}")
        return f"Errore: {str(e)}", 500

@app.route('/api/ical/refresh/<path:cfg>')
def force_refresh_ical(cfg):
    """Forza aggiornamento calendario iCal"""
    try:
        # Reindirizza all'endpoint normale con parametro refresh
        return redirect(f'/api/ical?cfg={cfg}&refresh=true')
    except Exception as e:
        return f"Errore: {str(e)}", 500

@app.route('/health')
def health():
    """Health check"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)