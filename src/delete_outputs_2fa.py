#!/usr/bin/env python3
"""
Veilige verwijdering van gegenereerde output mappen met 2-factor authenticatie.

Werking:
- Bij eerste run wordt er een verwijder-wachtwoord en een TOTP-secret aangemaakt (in `secrets/`).
- Voeg de TOTP-secret toe aan een authenticator-app (bijv. Google Authenticator).
- Voor verwijderen is zowel het wachtwoord als een geldige TOTP-code nodig.

Gebruik:
    python src/delete_outputs_2fa.py [--path docs/output] [--dry-run]

LET OP: dit script verwijdert bestanden permanent. Volg de prompts zorgvuldig.
"""
from __future__ import annotations
import argparse
import getpass
import hashlib
import json
import os
import shutil
import stat
import sys
import hmac
from pathlib import Path

try:
    import pyotp
except Exception:
    print("Fout: 'pyotp' is niet geïnstalleerd. Voer uit: pip install pyotp")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "output"
SECRETS_DIR = PROJECT_ROOT / "secrets"
PASS_FILE = SECRETS_DIR / "delete_pass.json"
TOTP_FILE = SECRETS_DIR / "2fa_secret.txt"

PBKDF_ITER = 200_000


def ensure_secrets_dir():
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        SECRETS_DIR.chmod(0o700)
    except Exception:
        pass


def save_passphrase_hash(passphrase: str):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, PBKDF_ITER)
    data = {
        "salt": salt.hex(),
        "dk": dk.hex(),
        "iter": PBKDF_ITER,
    }
    with open(PASS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)
    try:
        PASS_FILE.chmod(0o600)
    except Exception:
        pass


def verify_passphrase(passphrase: str) -> bool:
    if not PASS_FILE.exists():
        return False
    data = json.loads(PASS_FILE.read_text(encoding="utf-8"))
    salt = bytes.fromhex(data["salt"])
    dk_stored = bytes.fromhex(data["dk"])
    dk = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, data.get("iter", PBKDF_ITER))
    return hmac.compare_digest(dk, dk_stored)


def save_totp_secret(secret: str):
    with open(TOTP_FILE, "w", encoding="utf-8") as f:
        f.write(secret)
    try:
        TOTP_FILE.chmod(0o600)
    except Exception:
        pass


def load_totp_secret() -> str | None:
    if not TOTP_FILE.exists():
        return None
    return TOTP_FILE.read_text(encoding="utf-8").strip()


def setup_interactive():
    print("Geen 2FA-configuratie gevonden — setup starten.")
    while True:
        pw1 = getpass.getpass("Stel een verwijder-wachtwoord in (minimaal 8 tekens): ")
        if len(pw1) < 8:
            print("Wachtwoord te kort, probeer opnieuw.")
            continue
        pw2 = getpass.getpass("Bevestig wachtwoord: ")
        if pw1 != pw2:
            print("Wachtwoorden komen niet overeen, probeer opnieuw.")
            continue
        break
    ensure_secrets_dir()
    save_passphrase_hash(pw1)

    secret = pyotp.random_base32()
    save_totp_secret(secret)
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name="intake-delete", issuer_name="IntakeProjecten")
    print("")
    print("=== 2FA setup voltooid ===")
    print("Voeg de volgende secret toe aan je authenticator (bijv. Google Authenticator):")
    print(f"Secret: {secret}")
    print("")
    print("Of gebruik deze URI (QR-generators kunnen deze verwerken):")
    print(uri)
    print("")
    print("Bewaar de secret veilig. Na setup vereist het script je wachtwoord + de TOTP-code voor verwijdering.")


def list_targets(path: Path):
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    # list immediate children (folders/files) to avoid accidental top-level deletion
    children = sorted([p for p in path.iterdir()])
    return children


def rmtree_force(path: Path):
    def onerror(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
        except Exception:
            pass
        try:
            func(p)
        except Exception as e:
            print(f"Fout bij verwijderen {p}: {e}")

    if path.is_dir():
        shutil.rmtree(path, onerror=onerror)
    else:
        try:
            path.unlink()
        except Exception as e:
            onerror(path.unlink, path, None)


def main():
    parser = argparse.ArgumentParser(description="Verwijder output met 2-factor authenticatie")
    parser.add_argument("--path", type=str, default=str(DEFAULT_OUTPUT), help="Pad naar verwijderbare output (standaard: docs/output)")
    parser.add_argument("--dry-run", action="store_true", help="Toon wat verwijderd zou worden, verwijder niets")
    parser.add_argument("--yes", action="store_true", help="Bevestig zonder extra prompt (gebruiken met zorg)")
    parser.add_argument("--test-pass", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--test-totp", type=str, help=argparse.SUPPRESS)
    args = parser.parse_args()

    target = Path(args.path)

    # Setup indien nodig
    if not PASS_FILE.exists() or not TOTP_FILE.exists():
        setup_interactive()

    # Vraag om wachtwoord (of gebruik test flags wanneer expliciet toegestaan via env)
    ALLOW_TEST = os.environ.get("ALLOW_TEST", "0") == "1"
    if args.test_pass and args.test_totp and ALLOW_TEST:
        pw = args.test_pass
        code = args.test_totp
        # verify both
        if not verify_passphrase(pw):
            print("Fout wachtwoord (test-mode).")
            sys.exit(1)
        secret = load_totp_secret()
        if not secret:
            print("TOTP-secret ontbreekt. Run setup opnieuw.")
            sys.exit(1)
        totp = pyotp.TOTP(secret)
        if not totp.verify(code, valid_window=1):
            print("Ongeldige of verlopen test-TOTP code.")
            sys.exit(1)
    else:
        for attempt in range(3):
            pw = getpass.getpass("Voer verwijder-wachtwoord in: ")
            if verify_passphrase(pw):
                break
            print("Fout wachtwoord.")
        else:
            print("Te veel foutieve pogingen. Stop.")
            sys.exit(1)

        secret = load_totp_secret()
        if not secret:
            print("TOTP-secret ontbreekt. Run setup opnieuw.")
            sys.exit(1)

        code = input("Voer 6-cijferige TOTP-code in van je authenticator: ").strip()
        totp = pyotp.TOTP(secret)
        if not totp.verify(code, valid_window=1):
            print("Ongeldige of verlopen code.")
            sys.exit(1)

    # Toon doelen
    targets = list_targets(target)
    if not targets:
        print(f"Niets gevonden op {target}")
        sys.exit(0)

    print("\nGevonden items:")
    for p in targets:
        print(" - ", p)

    if args.dry_run:
        print("\nDry-run: er wordt niets verwijderd.")
        sys.exit(0)

    if not args.yes:
        confirm = input("Weet je zeker dat je deze items permanent wilt verwijderen? [j/N]: ")
        if confirm.lower() not in ("j", "ja", "y", "yes"):
            print("Annuleren...")
            sys.exit(0)

    # Voer verwijdering uit
    for p in targets:
        print(f"Verwijderen: {p} ...")
        try:
            rmtree_force(p)
            print("   Verwijderd")
        except Exception as e:
            print(f"   Fout: {e}")

    print("Klaar.")


if __name__ == "__main__":
    main()
