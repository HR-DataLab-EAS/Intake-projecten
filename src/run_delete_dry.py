#!/usr/bin/env python3
"""Runner to execute delete_outputs_2fa.py non-interactively for dry-run tests."""
import pyotp
import runpy
import sys
from pathlib import Path

secret_file = Path('secrets') / '2fa_secret.txt'
if not secret_file.exists():
    print('TOTP secret not found. Create secrets first or run setup interactively.')
    sys.exit(1)
secret = secret_file.read_text().strip()
code = pyotp.TOTP(secret).now()
# Provide test-pass and test-totp; ALLOW_TEST must be set in the environment when running.
sys.argv = ['delete_outputs_2fa.py', '--dry-run', '--test-pass', 'TestDelete123!', '--test-totp', code]
runpy.run_path('src/delete_outputs_2fa.py', run_name='__main__')
