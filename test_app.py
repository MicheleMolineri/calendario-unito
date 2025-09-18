#!/usr/bin/env python3
"""
Test suite per l'applicazione calendario universitario
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch, mock_open
import sys

# Aggiungi il percorso del progetto per importare i moduli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calendar_manager import UniversityCalendarManager
from auto_update import load_config, should_check_for_updates, auto_update_calendar


class TestUniversityCalendarManager(unittest.TestCase):
    """Test per la classe UniversityCalendarManager"""

    def setUp(self):
        """Setup per ogni test"""
        self.test_url = "https://example.com/calendar.ics"
        self.manager = UniversityCalendarManager(self.test_url)

    def tearDown(self):
        """Pulizia dopo ogni test"""
        # Rimuovi file di test se esistono
        for filename in ["calendar_config.json", "calendar_cache.pkl", "filtered_calendar.ics"]:
            if os.path.exists(filename):
                os.remove(filename)

    @patch('requests.get')
    def test_download_calendar_success(self, mock_get):
        """Test download calendario riuscito"""
        mock_response = Mock()
        mock_response.text = "BEGIN:VCALENDAR\nEND:VCALENDAR"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.manager.download_calendar()
        self.assertEqual(result, "BEGIN:VCALENDAR\nEND:VCALENDAR")
        mock_get.assert_called_once_with(self.test_url, timeout=30)

    @patch.object(UniversityCalendarManager, 'download_calendar')
    def test_download_calendar_failure(self, mock_download):
        """Test download calendario fallito"""
        mock_download.return_value = None

        result = self.manager.download_calendar()
        self.assertIsNone(result)

    def test_parse_calendar_valid(self):
        """Test parsing calendario valido"""
        calendar_data = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Test Course - Test Event
DTSTART:20240101T100000
DTEND:20240101T110000
END:VEVENT
END:VCALENDAR"""

        calendar = self.manager.parse_calendar(calendar_data)
        self.assertIsNotNone(calendar)

    def test_parse_calendar_invalid(self):
        """Test parsing calendario invalido"""
        calendar_data = "INVALID DATA"

        calendar = self.manager.parse_calendar(calendar_data)
        self.assertIsNone(calendar)

    def test_extract_course_name(self):
        """Test estrazione nome corso"""
        # Test formato "SIGLA - NOME"
        summary = "LFT - LINGUAGGI E FORMALI E TRADUTTORI"
        result = self.manager.extract_course_name(summary, "")
        self.assertEqual(result, "LFT - LINGUAGGI E FORMALI E TRADUTTORI")

        # Test formato semplice
        summary = "MATEMATICA"
        result = self.manager.extract_course_name(summary, "")
        self.assertEqual(result, "MATEMATICA")

    def test_calculate_hash(self):
        """Test calcolo hash"""
        data = "test data"
        hash1 = self.manager.calculate_hash(data)
        hash2 = self.manager.calculate_hash(data)
        self.assertEqual(hash1, hash2)

        # Hash diversi per dati diversi
        hash3 = self.manager.calculate_hash("different data")
        self.assertNotEqual(hash1, hash3)

    def test_load_save_config(self):
        """Test caricamento e salvataggio configurazione"""
        # Test configurazione di default
        config = self.manager.load_config()
        self.assertIn("selected_courses", config)
        self.assertIn("last_update", config)

        # Test salvataggio e caricamento
        test_config = {
            "selected_courses": ["Course 1", "Course 2"],
            "last_update": "2024-01-01T00:00:00",
            "calendar_hash": "testhash"
        }

        self.manager.config = test_config
        self.manager.save_config()

        # Carica nuova istanza per verificare
        new_manager = UniversityCalendarManager(self.test_url)
        loaded_config = new_manager.load_config()

        self.assertEqual(loaded_config["selected_courses"], ["Course 1", "Course 2"])
        self.assertEqual(loaded_config["calendar_hash"], "testhash")


class TestAutoUpdate(unittest.TestCase):
    """Test per le funzioni di auto-update"""

    def setUp(self):
        """Setup per ogni test"""
        self.test_config = {
            "calendar_url": "https://example.com/calendar.ics",
            "selected_courses": ["Course 1"],
            "last_update": "2024-01-01T00:00:00",
            "calendar_hash": "oldhash"
        }

    def tearDown(self):
        """Pulizia dopo ogni test"""
        if os.path.exists("calendar_config.json"):
            os.remove("calendar_config.json")

    def test_load_config_exists(self):
        """Test caricamento configurazione esistente"""
        # Crea file di configurazione di test
        with open("calendar_config.json", "w") as f:
            json.dump(self.test_config, f)

        config = load_config("calendar_config.json")
        self.assertEqual(config["calendar_url"], "https://example.com/calendar.ics")

    def test_load_config_not_exists(self):
        """Test caricamento configurazione non esistente"""
        config = load_config("nonexistent.json")
        self.assertIsNone(config)

    def test_should_check_for_updates_force(self):
        """Test controllo aggiornamenti forzato"""
        result = should_check_for_updates(self.test_config, force=True)
        self.assertTrue(result)

    def test_should_check_for_updates_recent(self):
        """Test controllo aggiornamenti recente"""
        # Imposta last_update a ora corrente
        recent_config = self.test_config.copy()
        recent_config["last_update"] = datetime.now().isoformat()

        result = should_check_for_updates(recent_config, force=False)
        self.assertFalse(result)

    def test_should_check_for_updates_old(self):
        """Test controllo aggiornamenti vecchio"""
        # Configurazione con last_update vecchio
        old_config = self.test_config.copy()
        old_config["last_update"] = "2020-01-01T00:00:00"  # Molto vecchio

        result = should_check_for_updates(old_config, force=False)
        self.assertTrue(result)

    @patch('calendar_manager.UniversityCalendarManager')
    def test_auto_update_calendar_no_config(self, mock_manager_class):
        """Test auto-update senza configurazione"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        # Simula mancanza configurazione
        with patch('auto_update.load_config', return_value=None):
            result = auto_update_calendar("https://example.com/calendar.ics", verbose=False)
            self.assertFalse(result)

    @patch('calendar_manager.UniversityCalendarManager')
    def test_auto_update_calendar_download_failure(self, mock_manager_class):
        """Test auto-update con fallimento download"""
        mock_manager = Mock()
        mock_manager.download_calendar.return_value = None
        mock_manager_class.return_value = mock_manager

        with patch('auto_update.load_config', return_value=self.test_config):
            result = auto_update_calendar("https://example.com/calendar.ics", verbose=False)
            self.assertFalse(result)


class TestFlaskApp(unittest.TestCase):
    """Test per l'applicazione Flask"""

    def setUp(self):
        """Setup per ogni test"""
        from app import app
        self.app = app
        self.client = self.app.test_client()

    def test_index_route(self):
        """Test route index"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_analyze_calendar_no_url(self):
        """Test analyze calendar senza URL"""
        response = self.client.post('/api/analyze_calendar',
                                  json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_calendar_info_route(self):
        """Test route calendar info"""
        response = self.client.get('/api/calendar_info')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('supported_formats', data)


if __name__ == '__main__':
    # Crea directory di test se necessario
    if not os.path.exists('temp_calendars'):
        os.makedirs('temp_calendars')

    # Esegui i test
    unittest.main(verbosity=2)