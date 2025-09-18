#!/usr/bin/env python3
"""
Applicazione Flask per la gestione del calendario universitario
Interfaccia web moderna per selezionare e filtrare i corsi
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_cors import CORS
import os
import json
import tempfile
from datetime import datetime
import hashlib
from calendar_manager import UniversityCalendarManager

# Carica variabili d'ambiente da .env se presente (solo per sviluppo)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv non installato, usa solo variabili d'ambiente di sistema

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'CHIAVE_SEGRETISSIMISIMISSIMISSIMISSIMISS!MI!ZZIMà@')
# CORS(app)  # Removed for Railway

# Configurazione per Railway e altri ambienti
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'temp_calendars'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crea cartella se non esiste (con gestione errori per Railway)
try:
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print(f"✅ Cartella creata: {UPLOAD_FOLDER}")
    else:
        print(f"✅ Cartella esistente: {UPLOAD_FOLDER}")
except Exception as e:
    print(f"⚠️  Errore creazione cartella {UPLOAD_FOLDER}: {e}")
    # Fallback alla cartella temporanea del sistema
    import tempfile
    UPLOAD_FOLDER = tempfile.gettempdir()
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    print(f"🔄 Uso cartella temporanea: {UPLOAD_FOLDER}")

# Configurazione server (solo per sviluppo locale)
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5001))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Avvio del server Flask...")
    print("📅 Gestore Calendario Universitario")
    print(f"🌐 Server attivo su: http://{HOST}:{PORT}")
    print("📝 Premi Ctrl+C per fermare il server")
    
    app.run(debug=DEBUG, host=HOST, port=PORT)


@app.route('/health')
def health():
    """Health check"""
    return 'OK'

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')


@app.route('/api/analyze_calendar', methods=['POST'])
def analyze_calendar():
    """
    Analizza il calendario dall'URL fornito e restituisce i corsi disponibili
    """
    try:
        data = request.get_json()
        calendar_url = data.get('calendar_url', '').strip()
        
        if not calendar_url:
            return jsonify({'error': 'URL del calendario richiesto'}), 400
        
        # Crea manager temporaneo
        manager = UniversityCalendarManager(calendar_url)
        
        # Scarica e analizza il calendario
        calendar_data = manager.download_calendar()
        if not calendar_data:
            return jsonify({'error': 'Impossibile scaricare il calendario dall\'URL fornito'}), 400
        
        # Parsifica il calendario
        calendar = manager.parse_calendar(calendar_data)
        if not calendar:
            return jsonify({'error': 'Formato calendario non valido'}), 400
        
        # Estrai i corsi
        courses = manager.extract_courses(calendar)
        if not courses:
            return jsonify({'error': 'Nessun corso trovato nel calendario'}), 400
        
        # Prepara i dati per la risposta
        courses_list = []
        for course_name, events in courses.items():
            courses_list.append({
                'name': course_name,
                'events_count': len(events),
                'first_event': str(events[0]['start']) if events else 'N/A',
                'location': events[0]['location'] if events and events[0]['location'] else 'N/A'
            })
        
        # Ordina per nome
        courses_list.sort(key=lambda x: x['name'])
        
        # Salva temporaneamente i dati del calendario per uso successivo
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
        return jsonify({'error': f'Errore durante l\'analisi: {str(e)}'}), 500


@app.route('/api/generate_calendar', methods=['POST'])
def generate_calendar():
    """
    Genera e salva il calendario filtrato con i corsi selezionati
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        selected_courses = data.get('selected_courses', [])
        calendar_url = data.get('calendar_url')
        
        if not session_id or not selected_courses:
            return jsonify({'error': 'Dati mancanti per la generazione'}), 400
        
        # Recupera i dati del calendario salvati
        temp_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_calendar.txt')
        if not os.path.exists(temp_file):
            return jsonify({'error': 'Sessione scaduta. Ricarica il calendario.'}), 400
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            calendar_data = f.read()
        
        # Crea manager e processa
        manager = UniversityCalendarManager(calendar_url)
        calendar = manager.parse_calendar(calendar_data)
        
        # Crea calendario filtrato
        filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)
        
        # Salva il calendario filtrato
        output_filename = f'{session_id}_filtered.ics'
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(filtered_calendar.to_ical())
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{session_id}',
            'filename': f'calendario_filtrato_{datetime.now().strftime("%Y%m%d")}.ics',
            'selected_courses_count': len(selected_courses)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante la generazione: {str(e)}'}), 500


@app.route('/download/<session_id>')
def download_calendar(session_id):
    """
    Download del calendario filtrato
    """
    try:
        filename = f'{session_id}_filtered.ics'
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            flash('File non trovato. Rigenera il calendario.', 'error')
            return redirect(url_for('index'))
        
        # Nome file per il download
        download_name = f'calendario_unito_filtrato_{datetime.now().strftime("%Y%m%d")}.ics'
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='text/calendar'
        )
        
    except Exception as e:
        flash(f'Errore durante il download: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/ical/<session_id>')
def ical_link(session_id):
    """
    Link iCal per sottoscrizione automatica del calendario
    Controlla automaticamente se ci sono aggiornamenti prima di servire il file
    """
    try:
        filename = f'{session_id}_filtered.ics'
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        config_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_config.json')

        # Se esiste la configurazione permanente, controlla aggiornamenti
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                calendar_url = config.get('calendar_url')
                selected_courses = config.get('selected_courses', [])
                last_update = config.get('last_update')

                # Controlla se è passato più di 1 ora dall'ultimo aggiornamento
                if last_update:
                    last_update_time = datetime.fromisoformat(last_update)
                    time_diff = datetime.now() - last_update_time

                    if time_diff.total_seconds() > 3600:  # 1 ora
                        print(f"Controllo aggiornamenti per sessione {session_id}...")

                        # Crea manager e controlla aggiornamenti
                        manager = UniversityCalendarManager(calendar_url)
                        calendar_data = manager.download_calendar()

                        if calendar_data:
                            # Calcola hash del nuovo calendario
                            current_hash = hashlib.md5(calendar_data.encode('utf-8')).hexdigest()
                            saved_hash = config.get('calendar_hash')

                            if current_hash != saved_hash:
                                print(f"Aggiornamento rilevato per sessione {session_id}, rigenero calendario...")

                                # Parsifica e crea calendario aggiornato
                                calendar = manager.parse_calendar(calendar_data)
                                if calendar:
                                    filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)

                                    # Salva calendario aggiornato
                                    with open(file_path, 'wb') as f:
                                        f.write(filtered_calendar.to_ical())

                                    # Aggiorna configurazione
                                    config['calendar_hash'] = current_hash
                                    config['last_update'] = datetime.now().isoformat()
                                    with open(config_file, 'w', encoding='utf-8') as f:
                                        json.dump(config, f, indent=2, ensure_ascii=False)

                                    print(f"Calendario aggiornato per sessione {session_id}")
            except Exception as e:
                print(f"Errore durante controllo aggiornamenti per {session_id}: {e}")

        if not os.path.exists(file_path):
            return jsonify({'error': 'Calendario non trovato'}), 404

        # Serve il file ICS direttamente per la sottoscrizione
        return send_file(
            file_path,
            mimetype='text/calendar',
            as_attachment=False  # Non come download ma come contenuto diretto
        )

    except Exception as e:
        return jsonify({'error': f'Errore nel servire il calendario: {str(e)}'}), 500


@app.route('/api/create_permanent_link', methods=['POST'])
def create_permanent_link():
    """
    Crea un link permanente per il calendario filtrato che si aggiorna automaticamente
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        calendar_url = data.get('calendar_url')
        selected_courses = data.get('selected_courses', [])
        
        if not all([session_id, calendar_url, selected_courses]):
            return jsonify({'error': 'Dati mancanti'}), 400
        
        # Salva la configurazione permanente per aggiornamenti automatici
        permanent_config = {
            'calendar_url': calendar_url,
            'selected_courses': selected_courses,
            'created_at': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat()
        }
        
        config_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(permanent_config, f, indent=2, ensure_ascii=False)
        
        # URL base del server (modifica se necessario)
        base_url = request.host_url.rstrip('/')
        ical_url = f"{base_url}/ical/{session_id}"
        
        return jsonify({
            'success': True,
            'ical_url': ical_url,
            'webcal_url': ical_url.replace('http://', 'webcal://').replace('https://', 'webcal://'),
            'instructions': [
                'Copia il link iCal/webcal',
                'Incollalo nel tuo client calendario preferito',
                'Il calendario si aggiornerà automaticamente'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nella creazione del link: {str(e)}'}), 500


@app.route('/api/calendar_info')
def calendar_info():
    """
    Informazioni sui formati supportati e esempi
    """
    return jsonify({
        'supported_formats': ['ICS', 'iCal'],
        'example_urls': [
            'https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=...',
            'https://university.edu/calendar.ics'
        ],
        'instructions': [
            'Inserisci l\'URL del calendario universitario',
            'Seleziona i corsi che ti interessano',
            'Scarica il calendario filtrato',
            'Importa il file in Google Calendar, Apple Calendar, Outlook, ecc.'
        ]
    })


@app.route('/api/update_ical/<session_id>')
def update_ical_calendar(session_id):
    """
    Aggiorna automaticamente il calendario iCal se necessario
    """
    try:
        config_file = os.path.join(UPLOAD_FOLDER, f'{session_id}_config.json')
        
        if not os.path.exists(config_file):
            return jsonify({'error': 'Configurazione non trovata'}), 404
        
        # Carica la configurazione
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        calendar_url = config.get('calendar_url')
        selected_courses = config.get('selected_courses', [])
        
        if not calendar_url or not selected_courses:
            return jsonify({'error': 'Configurazione incompleta'}), 400
        
        # Crea manager e scarica calendario aggiornato
        manager = UniversityCalendarManager(calendar_url)
        calendar_data = manager.download_calendar()
        
        if not calendar_data:
            return jsonify({'error': 'Impossibile scaricare il calendario'}), 500
        
        calendar = manager.parse_calendar(calendar_data)
        if not calendar:
            return jsonify({'error': 'Impossibile parsificare il calendario'}), 500
        
        # Crea calendario filtrato aggiornato
        filtered_calendar = manager.create_filtered_calendar(calendar, selected_courses)
        
        # Salva il calendario aggiornato
        output_filename = f'{session_id}_filtered.ics'
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(filtered_calendar.to_ical())
        
        # Aggiorna il timestamp nella configurazione
        config['last_update'] = datetime.now().isoformat()
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'last_update': config['last_update'],
            'message': 'Calendario aggiornato con successo'
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nell\'aggiornamento: {str(e)}'}), 500


@app.route('/cleanup')
def cleanup_temp_files():
    """
    Pulizia file temporanei (per manutenzione)
    """
    try:
        import glob
        import time
        
        # Rimuovi file più vecchi di 7 giorni (per i link permanenti)
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        files_removed = 0
        
        for file_path in glob.glob(os.path.join(UPLOAD_FOLDER, '*')):
            if os.path.getmtime(file_path) < cutoff_time:
                # Non rimuovere i file di configurazione dei link permanenti
                if not file_path.endswith('_config.json'):
                    os.remove(file_path)
                    files_removed += 1
        
        return jsonify({
            'success': True,
            'files_removed': files_removed,
            'message': f'Rimossi {files_removed} file temporanei'
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante la pulizia: {str(e)}'}), 500


if __name__ == '__main__':
    print("🚀 Avvio del server Flask...")
    print("📅 Gestore Calendario Universitario")
    print(f"🌐 Server attivo su: http://{HOST}:{PORT}")
    print("📝 Premi Ctrl+C per fermare il server")
    
    app.run(debug=DEBUG, host=HOST, port=PORT)