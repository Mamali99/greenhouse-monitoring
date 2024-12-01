# Greenhouse Tomato Monitoring System

Ein IoT-basiertes System zur Überwachung und Analyse von Tomatenpflanzen in Gewächshäusern mittels Computer Vision und Machine Learning.

## Features

- Automatische Bildaufnahme via Raspberry Pi Kamera
- Echtzeit-Analyse des Reifegrads von Tomaten
- Integration mit Cumulocity IoT Platform
- ML-basierte Erkennung von reifen und unreifen Tomaten
- Automatisches Upload von analysierten Bildern

## Projektstruktur

```
greenhouse-monitoring/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── tomato_analyzer.py
├── c8y_Startstream.py
└── c8y_Startstream
```

## Voraussetzungen

- Raspberry Pi mit Kamera
- Python 3.7+
- thin-edge.io Installation
- Cumulocity IoT Plattform Zugang

## Installation

1. Repository klonen:
```bash
git clone https://github.com/[IHR-USERNAME]/greenhouse-monitoring.git
cd greenhouse-monitoring
```

2. Python-Abhängigkeiten installieren:
```bash
sudo -H pip3 install -r requirements.txt
```

3. Konfiguration einrichten:
```bash
# .env.example zu .env kopieren und anpassen
cp .env.example .env
nano .env  # Fügen Sie hier Ihre Credentials ein
```

4. Berechtigungen einrichten:
```bash
sudo adduser tedge video
sudo usermod -a -G video tedge
```

5. Dateien kopieren:
```bash
sudo cp config/c8y_Startstream /etc/tedge/operations/c8y/
sudo cp src/c8y_Startstream.py /bin/
sudo cp .env /etc/tedge/.env
```

6. Berechtigungen setzen:
```bash
sudo chmod 644 /etc/tedge/operations/c8y/c8y_Startstream
sudo chmod 555 /bin/c8y_Startstream.py
sudo chmod 600 /etc/tedge/.env
```

## Konfiguration

1. Erstellen Sie eine `.env` Datei mit folgenden Variablen:
```
C8Y_BASEURL=ihre-url
C8Y_TENANT_ID=ihr-tenant
C8Y_USERNAME=ihr-username
C8Y_PASSWORD=ihr-password
WORKDIR=/etc/tedge
```

2. SmartRest2.0 Template in Cumulocity erstellen:
- ID: `greenhousewebcam`
- Response ID: `541`
- Name: `c8y_Startstream`

## Verwendung

1. Verbindung mit Cumulocity überprüfen:
```bash
sudo tedge disconnect c8y
sudo tedge connect c8y
```

2. Operation via REST API starten:
```bash
curl --location '[url]/devicecontrol/operations/' \
--header 'Authorization: Basic [credentials]' \
--header 'Content-Type: application/json' \
--data '{
  "deviceId": "[device-id]",
  "c8y_Startstream": {
    "parameters": {
      "timeout_minutes": "5"
    }
  }
}'
```

## Entwicklung

- Branch für neue Features: `feature/[feature-name]`
- Branch für Bugfixes: `fix/[bug-name]`
- Hauptbranch: `main`

## Sicherheitshinweise

- Niemals sensible Daten (Credentials, API Keys etc.) in Git committen
- `.env` Dateien sind in `.gitignore` aufgeführt
- Regelmäßige Überprüfung der Dependencies auf Sicherheitsupdates

## Lizenz

[Ihre gewählte Lizenz]

## Autor

[Ihr Name]