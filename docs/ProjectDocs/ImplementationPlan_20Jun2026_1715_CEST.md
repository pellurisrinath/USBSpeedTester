# USB Speed Test & Monitor: System Improvements & AI Chatbot Integration
## Updated to Fix Installation Directory Path and Document UI Updates

| Field | Value |
|---|---|
| **Project Name** | USB Speed Utility & Monitor |
| **Document Type** | Implementation Plan (Updated) |
| **Creation Date** | 20 Jun 2026 |
| **Time / Timezone** | 17:15 CEST |
| **Status** | Updated - Draft for Review |

---

## 1. Goal Description

This document outlines the implementation plan to add an integrated AI Chatbot assistant to the **USB Speed Test & Monitor** application, supporting major AI vendors (Ollama, OpenAI, Claude, Gemini, DeepSeek, Groq, OpenRouter), incorporating a static **About** tab inside the dashboard GUI, and resolving the installation directory path bug (fixing typo from `UBSSpeedTest` to `USBSpeedTest`).

The chatbot will assist users in:
- Interpreting write/read benchmarks (e.g. comparing speeds to nominal standards).
- Explaining USB standards (USB 2.0 vs 3.0 vs 3.2 vs 4, Type-A vs Type-C).
- Troubleshooting common USB issues (e.g., slow speeds, drive not detected, formatting advice).
- Automating optimization tips based on current system devices and test history.

---

## 2. Supported AI Vendors & Protocols

To support nearly all major AI providers without bloating the application with external dependencies, the backend will implement three key API protocols using Python's built-in `urllib.request` library:

1. **Ollama Protocol** (Local & Offline):
   - **Target Endpoint**: `http://localhost:11434/api/chat`
   - **Compatible Models**: `llama3`, `mistral`, `gemma2`, `phi3`, etc.
   - **Key Requirement**: No API key. Runs entirely offline.

2. **OpenAI Protocol** (Cloud & OpenAI-Compatible Endpoints):
   - **Compatible Vendors**: 
     - **OpenAI** (e.g., `gpt-4o`, `gpt-3.5-turbo`)
     - **DeepSeek** (using `https://api.deepseek.com/v1` and models like `deepseek-chat`)
     - **Groq** (using `https://api.groq.com/openai/v1` and models like `llama-3.1-70b-versatile`)
     - **OpenRouter** (using `https://openrouter.ai/api/v1` to access hundreds of open-source models)
     - **Mistral AI** (using `https://api.mistral.ai/v1`)
     - **Local/Self-hosted** (LM Studio, LocalAI, etc.)
   - **Key Requirement**: Requires user's API key and customizable Base URL.

3. **Anthropic Claude Protocol**:
   - **Target Endpoint**: `https://api.anthropic.com/v1/messages`
   - **Compatible Models**: `claude-3-5-sonnet-20240620`, `claude-3-haiku-20240307`, etc.
   - **Key Requirement**: Requires Anthropic API Key and `x-api-key` header with version tagging.

4. **Google Gemini Protocol**:
   - **Target Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}`
   - **Compatible Models**: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash-exp`
   - **Key Requirement**: Requires Google AI Studio API key passed as a URL parameter.

---

## 3. User Review Required

> [!WARNING]
> **API Key Storage Safety**: The API keys will be stored in `config.json` inside the application's directory (portable mode) or user data directory (standard mode). If anyone gets access to this file, they can read the API keys. Let us know if you want a basic layer of encryption on the keys, or if plaintext JSON storage is acceptable for your use case.

> [!IMPORTANT]
> **Zero External Python Dependencies**: To keep the packaged PyInstaller executable small and robust, we will implement the AI backend clients using Python's built-in `urllib.request` instead of adding dependency packages like `openai`, `anthropic`, or `ollama`.

---

## 4. Open Questions

1. **Plaintext vs. Obfuscated Keys**: Do you prefer to store the API keys in plain text inside `config.json` or should we perform a basic obfuscation/encryption so they aren't easily readable by opening the JSON file?
2. **Duplicate Code Removal**: May we clean up and delete the redundant files at the root (`main.py`, `speed_test.py`, `usb_detector.py`, `monitor_service.py`) and update `build.bat` to compile `src/main.py` directly?

---

## 5. Proposed Changes

### 5.1 Backend Code additions

#### [NEW] [ai_client.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/modules/ai_client.py)
A lightweight HTTP wrapper class utilizing Python's built-in `urllib.request` to talk to:
- **Ollama API**: `/api/chat` (local, default: `http://localhost:11434`)
- **OpenAI API**: `/v1/chat/completions` (default: `https://api.openai.com`)
- **Claude API**: `/v1/messages` (default: `https://api.anthropic.com`)
- **Gemini API**: `/v1beta/models/...:generateContent` (default: `https://generativelanguage.googleapis.com`)
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
- **[COMPLETED] Bug Fix**: Correct Windows `BASE_DIR` from `C:\\ProgramData\\UBSSpeedTest` to `C:\\ProgramData\\USBSpeedTest`.
- Modify directory resolution logic: Check if the folder where `config.py` is running from is writable. If so, default `BASE_DIR` to the script's root (installed folder). Otherwise, fallback to `C:\ProgramData\USBSpeedTest` or `~/.local/share/usb-speedtest`.

#### [MODIFY] [main.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/main.py)
Expose two new JavaScript-accessible methods in `BackendAPI`:
- `send_chatbot_message(chat_history)`: Extracts current connected devices and recent benchmarks, builds the system prompt context, calls `ai_client.py`, and returns the assistant's reply.
- `test_llm_connection(provider, api_key, model, endpoint)`: Verifies if the selected LLM backend responds successfully.

---

### 5.2 Frontend UI changes

#### [MODIFY] [index.html](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/index.html)
- **AI Chatbot Tab**: Add `<button class="tab-button" data-tab="chatbot"><i class="fas fa-robot"></i> AI Assistant</button>`.
- **AI Chatbot Panel**: Add `<div id="chatbot-tab" class="tab-content">` containing chat feed, input fields, send buttons, and quick actions.
- **[COMPLETED] About Tab**: Add `<button class="tab-button" data-tab="about"><i class="fas fa-info-circle"></i> About</button>` to navigation.
- **[COMPLETED] About Panel**: Add `<div id="about-tab" class="tab-content">` displaying developer information, description, GitHub, and LinkedIn links.
- **Settings Dialog**: Add dropdowns and text inputs for LLM configuration (Provider, API Key, Model ID, Base URL).

#### [MODIFY] [style.css](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/style.css)
- Implement modern, glowing chatbot styles matching the application's glassmorphic dark theme.
  - Markdown pre/code blocks styling.

#### [MODIFY] [app.js](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/app.js)
- Handle switching to the chatbot tab and initializing chat history.
- Capture LLM inputs inside settings, bind save/load logic.
- Implement `sendChat()` function that disables inputs, shows a modern loading animation, calls `send_chatbot_message()` on the backend, and displays the response.
- Add quick prompts injection.

---

### 5.3 Cleanup & Packaging

#### [MODIFY] [build.bat](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/build.bat)
- Fix the PyInstaller command:
  ```bat
  pyinstaller --noconsole --onefile --add-data "gui;gui" src/main.py
  ```

#### [DELETE] Duplicate Root Files (Optional, subject to user feedback)
- `main.py`
- `speed_test.py`
- `usb_detector.py`
- `monitor_service.py`

---

## 6. Verification Plan

### Automated Tests
- Run Python unit tests verifying `ai_client.py` connects correctly to mocked endpoints.
- Check parsing of API payloads from each provider.

### Manual Verification
- **Settings Check**: Save a mock Ollama config, verify it writes directly to `config.json` inside the directory.
- **Connection Test**: Click "Test Connection" in settings and verify response states.
- **Installation Path Verification**: Verify config and reports are written to `C:/ProgramData/USBSpeedTest` instead of the old `UBSSpeedTest` path.
- **About Tab check**: Click "About" tab in app, verify links open in browser and non-technical details are clearly formatted.
- **Chatbot Context**: Trigger a speed test benchmark. Switch to Chatbot tab, click "Analyze my speeds". Verify that the chatbot receives the correct write/read rates and device model.
- **Packaging Build**: Execute `build.bat`, verify that the compiled executable runs properly from `dist` and saves settings to its own local folder.
