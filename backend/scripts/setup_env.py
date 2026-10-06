"""Create per-install secrets without displaying them or replacing existing keys."""
import secrets
from pathlib import Path

from cryptography.fernet import Fernet


def main() -> None:
    target = Path(__file__).resolve().parents[1] / ".env"
    try:
        with target.open("x", encoding="utf-8") as file:
            file.write(f"ENCRYPTION_KEY={Fernet.generate_key().decode('ascii')}\n")
            file.write(f"EMAIL_LOOKUP_KEY={secrets.token_hex(32)}\n")
        target.chmod(0o600)
        print("Created backend/.env with unique keys. Keep this file private and backed up.")
    except FileExistsError:
        print("backend/.env already exists; existing keys were preserved.")


if __name__ == "__main__":
    main()
