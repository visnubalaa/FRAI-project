# Clinic Visitor Sorter — Completed Prototype

A student project prototype that classifies complaints for a college nurse queue. It is **not a diagnosis or medical triage system**. A nurse must review all records. Keyword safety checks are incomplete and must not be relied on during emergencies.

## Features
- Streamlit dashboard and complaint entry form
- AI classification using Google Gemini API or local Ollama (`llama3.2`)
- Strict JSON validation (exact fields, allowed categories/priorities, summary <= 12 words)
- One retry; neutral fallback (`other`, `today`) on repeated errors
- Python red-flag keyword override to `see_now` and category route validation
- Local JSON queue, review/pending status, category/priority filters, CSV export
- English/Tamil/Tanglish prompt instructions

## Folder structure
```
clinic-sorter/
  app.py                 # Streamlit UI
  classifier.py           # AI, validation, fallback, safety, route-check
  storage.py              # Local queue persistence
  test_classifier.py      # Unit tests
  requirements.txt
  .env.example
  data/                  # Queue JSON created at runtime
```

## Run in VS Code (Windows)
1. Extract this project ZIP and open the `clinic-sorter` folder in VS Code.
2. Open Terminal → New Terminal.
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal and activate again. Or use Command Prompt: `\.venv\Scripts\activate.bat`.
4. Install packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. **Gemini option:** Copy `.env.example` to `.env`, replace `your_api_key_here` with your key from Google AI Studio, and save. Keep `.env` private; never commit it.
6. Start the application:
   ```powershell
   streamlit run app.py
   ```
   Streamlit will show a local URL (usually `http://localhost:8501`) and open the page in your browser.
7. In the sidebar, choose **New Complaint**, select Gemini or Ollama, enter a complaint and submit.

## Ollama option (local model)
1. Install Ollama from https://ollama.com/download.
2. In a terminal, download the model:
   ```powershell
   ollama pull llama3.2
   ```
3. Ensure Ollama is running, then select **Ollama (local)** in the app.

## Tests
Run:
```powershell
python -m unittest test_classifier.py -v
```
Tests cover validation, invalid category routing and red-flag priority override. They do not call an AI API.

## Classification contract
Categories: `injury`, `fever_cold`, `stomach`, `pain`, `allergy`, `other`.
Priorities: `see_now`, `today`, `routine`.
Fallback after two failures: category `other`, priority `today`, summary `Symptoms reported; nurse review needed.`
Every original complaint is preserved for the nurse. Red-flag keyword matches override priority to `see_now`, even when AI fallback is used. The red-flag keyword list is only a limited prototype and cannot safely rule out urgent symptoms.

## Data and privacy
Records are saved locally in `data/queue.json`. The app has no login, encryption, role-based access or secure multi-user deployment. Do not deploy publicly or store identifiable health information without institutional approval, proper security and consent arrangements. Delete test records before demos if they contain personal details.
