# USB Speed Utility & Monitor - User Guide 📖

Welcome to the **USB Speed Utility & Monitor**! This guide is written for regular, non-technical users to help you understand what this application does, how it can help you, and how to use its features.

---

## 🌟 What is this Application?

Think of this tool as a health checkup dashboard for your USB drives (like flash drives, thumb drives, and external hard drives). 

Have you ever wondered:
* *How fast is my USB drive? Why does it take so long to copy photos or documents?*
* *How much storage space is left on my USB drive?*
* *Is my USB drive connected and recognized by my computer?*

This application answers all those questions with a simple, clean, and beautiful interface. It also includes an **AI Assistant** that can help you troubleshoot issues or explain technical terms.

---

## 🛠️ Key Features Explained

### 1. Devices View (Connected Peripherals)
This tab shows you a list of all USB devices connected to your computer. It detects not just storage drives, but also other peripherals like USB keyboards, mice, cameras, and audio devices. 
* *Why it's useful*: If your computer isn't recognizing a device, you can check here to see if the hardware itself is detected.

### 2. Storage View (Space Analysis)
This tab displays a clean bar chart showing how much space you have used and how much free space is left on each connected USB drive.
* *Why it's useful*: Helps you quickly see if you have enough room before copying large files.

### 3. Speed Test View (Performance Benchmarking)
This is the core feature. You can select one of your connected USB drives and choose a file size (like 100MB) to test. The application will write a temporary file to the drive and then read it back, measuring the exact transfer speeds.
* **Write Speed**: How fast files can be saved *to* your USB drive (important when copying files onto it).
* **Read Speed**: How fast files can be read *from* your USB drive (important when copying files from it or watching videos stored on it).
* *Why it's useful*: You can verify if a USB drive is performing at its advertised speed (for example, comparing older, slower USB 2.0 drives against modern, fast USB 3.0/3.1 drives).

### 4. Comparisons View
This tab lets you select different speed tests you have run and compare them side-by-side in a simple chart.
* *Why it's useful*: You can compare your different USB drives to see which one is the fastest, helping you decide which drive to use for important tasks.

### 5. Reports View
Every time you run a speed test, the application automatically saves a detailed report. This tab lets you view a list of all your past tests and open them in your web browser to view, print, or share.

### 6. AI Assistant
We have integrated a helper assistant directly into the app. You can chat with it to:
* Ask how to speed up your USB drives (e.g. formatting options).
* Understand what different file systems (like FAT32, NTFS, exFAT) mean.
* Troubleshoot why a drive is acting slow.
* *Smart features*: The assistant automatically knows about your connected USB drives. If you ask for specifications of your connected USB model, it will search online to look up the manufacturer specs for you.
* *Note*: If you are offline, the assistant will inform you that it cannot connect to fetch online specifications.

---

## 🚦 Quick How-To Instructions

### How to Run a Speed Test:
1. Plug in your USB drive.
2. Open the application and click on the **Speed Test** tab.
3. Select your USB drive from the drop-down menu.
4. Choose a test size (100MB is the default and recommended).
5. Click **Start Test** and wait for the speedometers to complete.
6. Once finished, your results will be shown, and a report will be saved.

### How to Compare Devices:
1. Run a speed test on the devices you want to compare.
2. Go to the **Comparison** tab.
3. Check the boxes next to the test runs you want to compare.
4. Click **Compare Selected** to see them side-by-side.

### How to Use the System Tray (Background Monitoring):
* When you close the main application window, it stays active as a small icon in your taskbar system tray (near the clock, represented by a purple dot).
* The service runs in the background and will show a pop-up alert if any connected USB drive drops below 10% free space, preventing data transfer failures.
* To exit the application completely, right-click the tray icon and select **Exit**.

---

## 🔒 Privacy & Safety
Your files and speed test data are entirely private. The application runs locally on your computer and does not upload your files, benchmark outcomes, or system information to the cloud.
