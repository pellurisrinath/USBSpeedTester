# USB Speed Test & Monitor: System Improvements & AI Chatbot Integration

This document outlines the proposed improvements and implementation plan to add an integrated AI Chatbot assistant to the **USB Speed Test & Monitor** application, along with general codebase improvements.

The chatbot will assist users in:
- Interpreting write/read benchmarks (e.g. comparing speeds to nominal standards).
- Explaining USB standards (USB 2.0 vs 3.0 vs 3.2 vs 4, Type-A vs Type-C).
- Troubleshooting common USB issues (e.g., slow speeds, drive not detected, formatting advice).
- Automating optimization tips based on current system devices and test history.

---

## Codebase Architecture & Key Improvements

1. **Integrated AI Chatbot Tab**:
   - A dedicated tab in the navigation layout called **AI Assistant**.
   - A modern chat interface with message bubbles, typing indicators, quick-prompt buttons, and markdown code formatting.
   
2. **Flexible LLM Provider Configuration**:
   - Support for **Ollama (Local)**, **Claude (Anthropic)**, **OpenAI (ChatGPT)**, and **Custom OpenAI-compatible Endpoints** (such as LM Studio, LocalAI, or custom cloud endpoints).
   - Input fields in the **Settings Dialog** for Provider, API Key, Model ID, and API Endpoint URL.
   
3. **Context-Aware Chatting**:
   - When sending a user query, the Python backend automatically appends a system context containing:
     - Currently connected USB storage and peripheral devices.
     - Recent speed test benchmark outcomes in the current session.
     
4. **Local Configuration Storage ("Installed Directory" / Portable Mode)**:
   - Config will be loaded from a `config.json` inside the application's running folder (installed directory) if writable (portable mode).
   - If not writable (e.g. if installed in `C:\Program Files` without Admin rights), it will fallback to the user data folder `C:\ProgramData\UBSSpeedTest` to avoid permission errors.
   - Sensitive API keys can be saved in plaintext (as requested) or optionally run through a lightweight base64/rot13 obfuscation to prevent casual shoulder-surfing.
   
5. **Codebase Cleanup (Deduplication)**:
   - The project currently has duplicate files in the root folder (`main.py`, `speed_test.py`, etc.) and inside `src/`. PyInstaller spec runs `src/main.py`, but `build.bat` runs root `main.py`.
   - We propose to clean this up so that all configurations and builds point consistently to `src/main.py`.

---

## User Review Required

> [!WARNING]
> **API Key Storage Safety**: The API keys will be stored in `config.json` inside the application's directory (portable mode) or user data directory (standard mode). If anyone gets access to this file, they can read the API keys. Let us know if you want a basic layer of encryption on the keys, or if plaintext JSON storage is acceptable for your use case.

> [!IMPORTANT]
> **Zero External Python Dependencies**: To keep the packaged PyInstaller executable small and robust, we will implement the AI backend clients using Python's built-in `urllib.request` instead of adding dependency packages like `openai`, `anthropic`, or `ollama`.

---

## Open Questions

1. **Plaintext vs. Obfuscated Keys**: Do you prefer to store the API keys in plain text inside `config.json` or should we perform a basic obfuscation/encryption so they aren't easily readable by opening the JSON file?
2. **Duplicate Code Removal**: May we clean up and delete the redundant files at the root (`main.py`, `speed_test.py`, `usb_detector.py`, `monitor_service.py`) and update `build.bat` to compile `src/main.py` directly?

---

## Proposed Changes

### 1. Backend Code additions

#### [NEW] [ai_client.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/modules/ai_client.py)
A lightweight HTTP wrapper class utilizing Python's built-in `urllib.request` to talk to:
- **Ollama API**: `/api/chat` (local, default: `http://localhost:11434`)
- **OpenAI API**: `/v1/chat/completions` (default: `https://api.openai.com`)
- **Claude API**: `/v1/messages` (default: `https://api.anthropic.com`)
- **Custom endpoint**: `/v1/chat/completions` or any custom API spec.

#### [MODIFY] [config.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/config.py)
- Incorporate AI configuration defaults:
  ```json
  "ai_chatbot": {
      "provider": "ollama",
      "api_key": "",
      "model": "llama3",
      "endpoint": "http://localhost:11434"
  }
  ```
- Modify directory resolution logic: Check if the folder where `config.py` is running from is writable. If so, default `BASE_DIR` to the script's root (installed folder). Otherwise, fallback to `C:\ProgramData\UBSSpeedTest` or `~/.local/share/usb-speedtest`.

#### [MODIFY] [main.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/main.py)
Expose two new JavaScript-accessible methods in `BackendAPI`:
- `send_chatbot_message(chat_history)`: Extracts current connected devices and recent benchmarks, builds the system prompt context, calls `ai_client.py`, and returns the assistant's reply.
- `test_llm_connection(provider, api_key, model, endpoint)`: Verifies if the selected LLM backend responds successfully.

---

### 2. Frontend UI changes

#### [MODIFY] [index.html](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/index.html)
- Add a new tab: `<button class="tab-button" data-tab="chatbot"><i class="fas fa-robot"></i> AI Assistant</button>`.
- Add a tab panel `<div id="chatbot-tab" class="tab-content">` containing:
  - Scrollable chat message area.
  - Quick options: "Analyze My USB Speed Test Results", "Explain USB Types", "Why is my USB Write Speed slow?".
  - User input text area and send button.
- Add fields to the settings modal:
  - Dropdown for **AI Provider** (Ollama, Claude, OpenAI, Custom).
  - Text input for **API Key** (masked, with show/hide toggle).
  - Text input for **Model Name** (e.g. `llama3`, `gpt-4o`, `claude-3-5-sonnet`).
  - Text input for **Endpoint URL** (pre-populated with default but editable).

#### [MODIFY] [style.css](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/style.css)
- Implement modern, glowing chatbot styles matching the application's glassmorphic dark theme:
  - User bubbles (colored accent gradient, right aligned).
  - AI bubbles (subtle dark blue container, left aligned).
  - Input field styling with a glowing border and a paper-plane send button.
  - Markdown pre/code blocks styling.

#### [MODIFY] [app.js](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/app.js)
- Handle switching to the chatbot tab and initializing chat history.
- Capture LLM inputs inside settings, bind save/load logic.
- Implement `sendChat()` function that disables inputs, shows a modern loading animation, calls `send_chatbot_message()` on the backend, and displays the response.
- Add quick prompts injection.

---

### 3. Cleanup & Packaging

#### [MODIFY] [build.bat](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/build.bat)
- Fix the PyInstaller command:
  ```bat
  pyinstaller --noconsole --onefile --add-data "gui;gui" src/main.py
  ```
- Change `main.spec` and root spec references to clean up output.

#### [DELETE] Duplicate Root Files (Optional, subject to user feedback)
- `main.py`
- `speed_test.py`
- `usb_detector.py`
- `monitor_service.py`

---

## Verification Plan

### Automated Tests
- Run Python unit tests verifying `ai_client.py` connects correctly to mocked endpoints.
- Check parsing of API payloads from each provider.

### Manual Verification
- **Settings Check**: Save a mock Ollama config, verify it writes directly to `config.json` inside the directory.
- **Connection Test**: Click "Test Connection" in settings and verify response states.
- **Chatbot Context**: Trigger a speed test benchmark. Switch to Chatbot tab, click "Analyze my speeds". Verify that the chatbot receives the correct write/read rates and device model.
- **Packaging Build**: Execute `build.bat`, verify that the compiled executable runs properly from `dist` and saves settings to its own local folder.
