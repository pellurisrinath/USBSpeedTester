# 🖥️ USB Speed Test & Monitor — User Interface Tour

> A complete visual walkthrough of every tab and feature in the application.
> All screenshots are taken from the latest release running on Windows 11.

---

## 📋 Table of Contents

| # | Section |
|---|---------|
| 1 | [Devices Tab — Connected Peripherals](#1-devices-tab--connected-peripherals) |
| 2 | [Storage Tab — Disk Space Analysis](#2-storage-tab--disk-space-analysis) |
| 3 | [Speed Test Tab — Benchmark](#3-speed-test-tab--benchmark) |
| 4 | [Comparison Tab — Multi-Device Matrix](#4-comparison-tab--multi-device-matrix) |
| 5 | [HTML Report — Plain Report](#5-html-report--plain-report) |
| 6 | [Reports Tab — Saved Benchmarks](#6-reports-tab--saved-benchmarks) |
| 7 | [AI Assistant — Diagnostics Chatbot](#7-ai-assistant--diagnostics-chatbot) |
| 8 | [Application Settings](#8-application-settings) |

---

## 1. Devices Tab — Connected Peripherals

Lists all connected USB peripherals with their device class, removability, mount point, and driver details (provider, version, date). The **Speed Test** button on each storage card launches a benchmark directly from the device list.

![Devices Tab](images/1_devices_tab.png)

---

## 2. Storage Tab — Disk Space Analysis

High-contrast visual storage bars showing used vs. free capacity, file system type, and total size for every mounted USB drive.

![Storage Tab](images/2_storage_tab.png)

---

## 3. Speed Test Tab — Benchmark

### a) Device & Size Selection
Choose a connected USB storage device and select the test file size (20 MB – 250 MB).

![Speed Test — Selection](images/3_speed_test_tab_a.png)

---

### b) Test In Progress
Real-time progress view showing live write/read throughput as the benchmark runs. Enforces `os.fsync` cache flushing for hardware-accurate (non-RAM-cached) results.

![Speed Test — In Progress](images/3_speed_test_tab_b.png)

---

### c) Results
Completed benchmark results showing sequential write speed, sequential read speed, and latency metrics.

![Speed Test — Results](images/3_speed_test_tab_c.png)

---

### d) Report Preview
In-app HTML report preview generated after each test run, ready to open in the system browser.

![Speed Test — Report Preview](images/3_speed_test_tab_d.png)

---

## 4. Comparison Tab — Multi-Device Matrix

Select multiple previous test runs from the session history to generate a side-by-side comparative performance matrix. All comparison reports are saved automatically to `C:\ProgramData\USBSpeedTest\comparisions\`.

![Comparison Tab](images/4_comparision.png)

---

## 5. HTML Report — Plain Report

A self-contained HTML benchmark report opened in the system browser, displaying full device metadata, driver details, sequential throughput results, and formatted data tables.

![Plain HTML Report](images/5_PlainHTMLReport.png)

---

## 6. Reports Tab — Saved Benchmarks

All saved HTML benchmark and comparison reports listed with timestamps. Click any entry to open the full report directly in your default web browser.

![Reports Tab](images/6_Reports.png)

---

## 7. AI Assistant — Diagnostics Chatbot

A context-aware AI chatbot scoped strictly to USB diagnostics. Supports **Ollama**, **Claude**, **OpenAI**, **Gemini**, **DeepSeek**, **Groq**, and any **OpenAI-compatible** endpoint (e.g. LM Studio). The chatbot automatically injects connected device details and driver information into every query.

### a) Welcome / Initial Prompt
The assistant introduces itself and shows suggested diagnostic queries.

![AI Assistant — Welcome](images/7_AI-Assistant_a.png)

---

### b) Device Specification Query
When asked about device specifications, the AI fetches live driver details from the system and queries DuckDuckGo for hardware specs, then provides an enriched answer.

![AI Assistant — Device Specs](images/7_AI-Assistant_b.png)

---

### c) Slowness Email Template
Ask the AI to draft a slowness report email. The response includes a **📋 Copy** button to copy the message directly to the clipboard.

![AI Assistant — Email Template](images/7_AI-Assistant_c.png)

---

### d) Guardrail Enforcement
Out-of-scope requests (e.g. writing code for unrelated projects, generating images or PDFs) are gracefully rejected. Profanity is filtered and flagged for review.

![AI Assistant — Guardrail](images/7_AI-Assistant_d.png)

---

## 8. Application Settings

Configure monitoring settings (interval, low-disk threshold), default test file size, and the full AI provider setup (provider, API key, endpoint, model). Use **Export Configuration** to save your current settings as a portable `.cfg` file.

![Application Settings](images/8_ApplicationSettings_withAISettings.png)

---

> ← [Back to README](../README.md) &nbsp;|&nbsp; 📋 [CHANGELOG](../CHANGELOG.md) &nbsp;|&nbsp; 📖 [User Guide](User_Guide.md)
