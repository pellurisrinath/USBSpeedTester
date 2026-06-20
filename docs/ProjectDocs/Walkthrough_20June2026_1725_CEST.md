# Walkthrough: AI Chatbot Integration & UI Enhancements

This document summarizes the changes implemented to integrate the **AI Diagnostics Assistant** and static **About** panel into the USB Speed Test & Monitor application.

---

## Changes Implemented

### 1. Backend Client & Protocol Wrappers
*   **`src/modules/ai_client.py` [NEW]**: A clean, zero-dependency HTTP client wrapper that handles the request and response mapping for multiple LLM providers:
    *   **Ollama (Local)**: Maps queries to `/api/chat`.
    *   **OpenAI & Compatible APIs (DeepSeek, Groq, OpenRouter, Mistral)**: Maps queries to `/v1/chat/completions` with bearer authorization headers.
    *   **Anthropic Claude**: Maps queries to `/v1/messages` with `x-api-key` and version headers.
    *   **Google Gemini**: Maps queries to `/v1beta/models/{model}:generateContent` with custom request structure mapping.
*   **`src/config.py` [MODIFY]**:
    *   Added `ai_chatbot` settings default structure.
    *   Resolved Windows base path typo, updating path from `UBSSpeedTest` to `USBSpeedTest`.
    *   Added **Portable Mode Check**: The application checks if the local running folder is writable. If so, it stores configuration locally in the installed folder; otherwise, it falls back to `%ProgramData%\USBSpeedTest`.
*   **`src/main.py` [MODIFY]**:
    *   Added `send_chatbot_message(chat_history)` to BackendAPI: Collects currently connected devices and recent session benchmarks to inject as system context, providing personalized diagnostics.
    *   Added `test_llm_connection(provider, api_key, model, endpoint)` to BackendAPI: Allows the user to click a test button in Settings to verify endpoints are responding correctly.

### 2. Frontend Interface & UI Controls
*   **`gui/index.html` [MODIFY]**:
    *   Added **AI Assistant** tab button and chat interface panel (message feed, quick prompts, text input).
    *   Added **About** tab button and panel presenting application description, developed by info, GitHub repository URL, and LinkedIn links.
    *   Added **AI Settings Form** to the Application Settings modal, with a dropdown to select the provider, API Key (hidden with a password eye toggle), Model ID, and API Endpoint URL.
*   **`gui/style.css` [MODIFY]**:
    *   Styled the chat bubbles (user aligned right with gradient, assistant aligned left with glassmorphic styling).
    *   Styled markdown text formatting inside messages (code blocks, lists, bold).
    *   Added a smooth bouncing typing indicator loading animation.
*   **`gui/app.js` [MODIFY]**:
    *   Bound settings fields to load/save configuration payloads.
    *   Created input validation, password eye toggling, and connection tester bridges.
    *   Created `sendChat()`, `sendQuickPrompt()`, and clear chat feed controllers.
    *   Implemented a custom lightweight regex markdown-to-HTML parser (`formatMarkdown()`).

---

## Security Scan Results
A full regex and entropy-based security scan was executed across all modified files.
*   **Result**: No hardcoded API keys, private keys, passwords, or tokens are present in the code.

---

## Verification Run
*   Python syntax compilation was checked and verified for all modified scripts.
*   A custom unit test was executed to confirm correct class structures.
