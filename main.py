#!/usr/bin/env python3
"""
Entry point semplice per Railway
"""

import os
from app import app

if __name__ == "__main__":
    # Per Railway, usa la porta dall'ambiente o 8080 come default
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Avvio server su porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

