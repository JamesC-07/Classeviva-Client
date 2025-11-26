# Classeviva Client

Un'applicazione desktop per visualizzare voti, medie e statistiche dal registro elettronico ClasseViva.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Kivy](https://img.shields.io/badge/kivy-2.3.1-green.svg)

## Caratteristiche

- Accesso con credenziali ClasseViva
- Lista completa dei voti con dettagli (materia, tipo, data, note)
- Calcolo automatico delle medie divise per Q1 e Q2
- Grafici per analizzare l'andamento scolastico:
  - Statistiche generali (totale voti, numero materie, medie per quadrimestre)
  - Media per materia con grafico a barre
  - Distribuzione dei voti

## Installazione

### Requisiti
- Python 3.8 o superiore
- pip (gestore pacchetti Python)

### 1. Clona il repository
```bash
git clone https://github.com/JamesC-07/Classeviva-Client.git
cd classeviva-client
```

### 2. Installa le dipendenze
```bash
pip install kivy
pip install classeviva
```

Oppure:
```bash
pip install -r requirements.txt
```

### 3. Avvia l'applicazione
```bash
python classeviva_app.py
```
