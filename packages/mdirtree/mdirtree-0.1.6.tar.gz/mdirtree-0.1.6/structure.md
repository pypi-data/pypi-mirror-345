secure_credentials/
├── .env                     # Zmienne środowiskowe
├── .gitignore              # Ignorowane pliki
├── README.md               # Dokumentacja
├── pyproject.toml          # Konfiguracja projektu
├── credentials_metadata.yaml # Metadane poświadczeń
├── requirements.txt        # Zależności
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── credentials_manager.py     # Główny manager
│   │   ├── encryption.py             # Szyfrowanie
│   │   ├── validators.py             # Walidatory
│   │   └── rotator.py               # Rotacja credentials
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                  # Klasa bazowa
│   │   ├── env_provider.py          # Provider dla .env
│   │   ├── keyring_provider.py      # Provider dla system keyring
│   │   ├── firefox_provider.py      # Provider dla Firefox
│   │   ├── keepass_provider.py      # Provider dla KeePass
│   │   └── bitwarden_provider.py    # Provider dla Bitwarden
│   │
│   ├── automation/
│   │   ├── __init__.py
│   │   ├── browser.py               # Zarządzanie przeglądarką
│   │   ├── login_automator.py       # Automatyzacja logowania
│   │   └── session_manager.py       # Zarządzanie sesjami
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Konfiguracja logowania
│       └── security.py              # Narzędzia bezpieczeństwa
│
├── tests/
│   ├── __init__.py
│   ├── test_credentials_manager.py
│   ├── test_providers.py
│   └── test_automation.py
│
└── examples/
    ├── __init__.py
    ├── stripe_login.py
    └── aws_login.py