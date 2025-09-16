#!/usr/bin/env python3
"""
Test locale per verificare che le funzioni serverless funzionino
"""

import sys
import json
from unittest.mock import Mock

# Simula una richiesta HTTP
def simulate_request(endpoint, method="POST", data=None):
    """Simula una richiesta HTTP alle funzioni serverless"""
    
    # Mock del request handler
    class MockHandler:
        def __init__(self):
            self.response_code = None
            self.headers = {}
            self.body = b""
            
        def send_response(self, code):
            self.response_code = code
            
        def send_header(self, key, value):
            self.headers[key] = value
            
        def end_headers(self):
            pass
            
        def send_cors_headers(self):
            self.headers['Access-Control-Allow-Origin'] = '*'
            
        def wfile_write(self, data):
            self.body = data
    
    try:
        if endpoint == "analyze_calendar":
            from api.analyze_calendar import handler
            
            mock_handler = MockHandler()
            mock_handler.headers = {'Content-Length': str(len(json.dumps(data).encode()))}
            mock_handler.rfile = Mock()
            mock_handler.rfile.read.return_value = json.dumps(data).encode()
            mock_handler.path = "/api/analyze_calendar"
            
            # Sostituisci il metodo wfile.write
            original_write = handler.wfile.write if hasattr(handler, 'wfile') else None
            handler_instance = handler()
            handler_instance.headers = mock_handler.headers
            handler_instance.rfile = mock_handler.rfile
            handler_instance.send_response = mock_handler.send_response
            handler_instance.send_header = mock_handler.send_header
            handler_instance.end_headers = mock_handler.end_headers
            handler_instance.send_cors_headers = mock_handler.send_cors_headers
            
            # Simula wfile.write
            def mock_write(data):
                mock_handler.body = data
            handler_instance.wfile = Mock()
            handler_instance.wfile.write = mock_write
            
            if method == "POST":
                handler_instance.do_POST()
            
            return {
                'status_code': mock_handler.response_code,
                'headers': mock_handler.headers,
                'body': mock_handler.body.decode('utf-8') if mock_handler.body else None
            }
            
    except Exception as e:
        return {
            'status_code': 500,
            'headers': {},
            'body': f"Errore nel test: {str(e)}"
        }

if __name__ == "__main__":
    print("🧪 Test delle funzioni serverless...")
    
    # Test 1: Analisi calendario
    test_data = {
        "calendar_url": "https://unito.prod.up.cineca.it/api/FiltriICal/impegniICal?id=68a470316e83cc00195a4a8f"
    }
    
    print("\n📅 Test analyze_calendar...")
    result = simulate_request("analyze_calendar", "POST", test_data)
    print(f"Status: {result['status_code']}")
    print(f"Headers: {result['headers']}")
    
    if result['body']:
        try:
            body_json = json.loads(result['body'])
            if body_json.get('success'):
                print(f"✅ Successo! Trovati {body_json.get('total_courses', 0)} corsi")
            else:
                print(f"❌ Errore: {body_json.get('error', 'Errore sconosciuto')}")
        except:
            print(f"Risposta: {result['body'][:200]}...")
    
    print("\n✅ Test completato!")