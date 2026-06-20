# USB Speed Test & Monitor: System Improvements & AI Chatbot Integration
## Updated to Support Broad AI Vendors (Ollama, OpenAI, Claude, Gemini, DeepSeek, Groq, etc.)

| Field | Value |
|---|---|
| **Project Name** | USB Speed Utility & Monitor |
| **Document Type** | Implementation Plan (Updated) |
| **Creation Date** | 20 Jun 2026 |
| **Time / Timezone** | 16:41 CEST |
| **Status** | Updated - Draft for Review |

---

## 1. Goal Description

This document outlines the implementation plan to add an integrated AI Chatbot assistant to the **USB Speed Test & Monitor** application, updated to support the industry's most popular AI vendors (Ollama, OpenAI, Anthropic Claude, Google Gemini, and OpenAI-compatible services like DeepSeek, Groq, and OpenRouter).

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
- Modify directory resolution logic: Check if the folder where `config.py` is running from is writable. If so, default `BASE_DIR` to the script's root (installed folder). Otherwise, fallback to `C:\ProgramData\UBSSpeedTest` or `~/.local/share/usb-speedtest`.

#### [MODIFY] [main.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/main.py)
Expose two new JavaScript-accessible methods in `BackendAPI`:
- `send_chatbot_message(chat_history)`: Extracts current connected devices and recent benchmarks, builds the system prompt context, calls `ai_client.py`, and returns the assistant's reply.
- `test_llm_connection(provider, api_key, model, endpoint)`: Verifies if the selected LLM backend responds successfully.

---

### 5.2 Frontend UI changes

#### [MODIFY] [index.html](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/index.html)
- Add a new tab: `<button class="tab-button" data-tab="chatbot"><i class="fas fa-robot"></i> AI Assistant</button>`.
- Add a tab panel `<div id="chatbot-tab" class="tab-content">` containing:
  - Scrollable chat message area.
  - Quick options: "Analyze My USB Speed Test Results", "Explain USB Types", "Why is my USB Write Speed slow?".
  - User input text area and send button.
- Add fields to the settings modal:
  - Dropdown for **AI Provider** (Ollama, OpenAI, Claude, Gemini, DeepSeek, Groq, OpenRouter, Custom).
  - Text input for **API Key** (masked, with show/hide toggle).
  - Text input for **Model Name** (e.g. `llama3`, `gpt-4o`, `claude-3-5-sonnet`, `gemini-1.5-flash`, `deepseek-chat`).
  - Text input for **Endpoint URL** (pre-populated with default but editable).

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
- **Chatbot Context**: Trigger a speed test benchmark. Switch to Chatbot tab, click "Analyze my speeds". Verify that the chatbot receives the correct write/read rates and device model.
- **Packaging Build**: Execute `build.bat`, verify that the compiled executable runs properly from `dist` and saves settings to its own local folder.
