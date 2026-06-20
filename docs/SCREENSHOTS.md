# 📸 USB Speed Test & Monitor — Screenshots

A visual tour of every tab and feature in the application.

---

## 1. Devices Tab — Connected Peripherals

Lists all connected USB peripherals with device class, removability, mount point, and driver details.

![Devices Tab](images/1_devices_tab.png)

---

## 2. Storage Tab — Disk Space Analysis

High-contrast visual storage bars showing occupied vs. free capacity for every mounted USB drive.

![Storage Tab](images/2_storage_tab.png)

---

## 3. Speed Test Tab — Benchmark

### a) Device & size selection
Select a connected USB storage device and choose the test file size (20 MB – 250 MB).

![Speed Test — Selection](images/3_speed_test_tab_a.png)

### b) Test in progress
Real-time speedometer showing live write/read throughput during the benchmark.

![Speed Test — In Progress](images/3_speed_test_tab_b.png)

### c) Results
Completed benchmark results showing sequential write speed, read speed, and latency.

![Speed Test — Results](images/3_speed_test_tab_c.png)

### d) Report preview
In-app HTML report preview generated after each test run.

![Speed Test — Report Preview](images/3_speed_test_tab_d.png)

---

## 4. Comparison Tab — Multi-Device Matrix

Select multiple test session runs to generate a side-by-side comparative performance matrix.

![Comparison Tab](images/4_comparision.png)

---

## 5. HTML Report — Plain Report

A generated HTML benchmark report opened in the system browser, showing full device details, throughput charts, and test metadata.

![Plain HTML Report](images/5_PlainHTMLReport.png)

---

## 6. Reports Tab — Saved Benchmarks

All saved HTML benchmark reports listed with timestamps. Click any report to open it directly in your browser.

![Reports Tab](images/6_Reports.png)

---

## 7. AI Assistant — Diagnostics Chatbot

Context-aware chatbot powered by your local or cloud LLM, scoped strictly to USB diagnostics.

### a) Welcome / initial prompt
![AI Assistant — Welcome](images/7_AI-Assistant_a.png)

### b) Device specification query
The AI fetches live device driver details from the system and searches DuckDuckGo for hardware specs.

![AI Assistant — Device Specs](images/7_AI-Assistant_b.png)

### c) Slowness email template
Ask the AI to draft a slowness report email — the response includes a **📋 Copy** button.

![AI Assistant — Email Template](images/7_AI-Assistant_c.png)

### d) Guardrail enforcement
Out-of-scope requests are gracefully rejected with a scope explanation.

![AI Assistant — Guardrail](images/7_AI-Assistant_d.png)

---

## 8. Application Settings — AI Configuration

Configure the AI provider (Ollama, Claude, OpenAI, Gemini, DeepSeek, Groq), endpoint, model, and export your full configuration.

![Application Settings](images/8_ApplicationSettings_withAISettings.png)

---

> 📁 All screenshot source files are located in [`docs/images/`](images/).
