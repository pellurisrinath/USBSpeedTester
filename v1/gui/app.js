// State management
let selectedDevice = null;
let testRunning = false;
let sessionReports = [];

// DOM Elements
const refreshBtn = document.getElementById('refresh-devices');
const storageList = document.getElementById('storage-list');
const peripheralList = document.getElementById('peripheral-list');
const serviceToggle = document.getElementById('service-toggle');
const selectedDeviceInfo = document.getElementById('selected-device-info');
const startTestBtn = document.getElementById('start-test-btn');
const testSizeSelect = document.getElementById('test-size');

const readMeter = document.getElementById('read-meter');
const writeMeter = document.getElementById('write-meter');
const readVal = document.getElementById('read-val');
const writeVal = document.getElementById('write-val');

const testProgressArea = document.getElementById('test-progress-area');
const testStage = document.getElementById('test-stage');
const testPct = document.getElementById('test-pct');
const testProgressBar = document.getElementById('test-progress-bar');
const reportsList = document.getElementById('reports-list');

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let color = '#0ea5e9'; // info blue
    if (type === 'success') color = '#10b981';
    if (type === 'error') color = '#ef4444';
    
    toast.innerHTML = `
        <span style="color: ${color}">●</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Format bytes
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Initialize and setup Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Refresh button
    refreshBtn.addEventListener('click', scanDevices);
    
    // Service toggle
    serviceToggle.addEventListener('change', (e) => {
        if (window.pywebview && window.pywebview.api) {
            window.pywebview.api.toggle_monitoring_service(e.target.checked)
                .then(status => {
                    const text = status ? "Background Monitor Active" : "Background Monitor Inactive";
                    document.querySelector('.status-text').innerText = text;
                    document.querySelector('.status-dot').className = `status-dot ${status ? 'active' : 'inactive'}`;
                    showToast(status ? "Monitoring service enabled." : "Monitoring service disabled.", 'info');
                });
        }
    });

    // Start speed test
    startTestBtn.addEventListener('click', runSpeedTest);

    // Initial scan after API loads
    setTimeout(scanDevices, 1000);
});

// Scan connected USB devices
function scanDevices() {
    if (!window.pywebview || !window.pywebview.api) {
        showToast("Backend API not connected yet.", "error");
        return;
    }
    
    refreshBtn.disabled = true;
    refreshBtn.classList.add('spinning');
    
    // List storage devices
    window.pywebview.api.get_storage_devices()
        .then(devices => {
            renderStorageDevices(devices);
            refreshBtn.disabled = false;
            refreshBtn.classList.remove('spinning');
        })
        .catch(err => {
            showToast("Failed to scan storage devices: " + err, "error");
            refreshBtn.disabled = false;
            refreshBtn.classList.remove('spinning');
        });

    // List other peripherals
    window.pywebview.api.get_peripherals()
        .then(peripherals => {
            renderPeripherals(peripherals);
        })
        .catch(err => {
            console.error("Failed to scan peripherals:", err);
        });
}

function renderStorageDevices(devices) {
    storageList.innerHTML = '';
    
    if (devices.length === 0) {
        storageList.innerHTML = `
            <div class="empty-state">
                <p>No USB storage devices detected</p>
            </div>
        `;
        selectedDevice = null;
        updateSelectedDisplay();
        return;
    }
    
    devices.forEach(dev => {
        const item = document.createElement('div');
        item.className = `device-item ${selectedDevice && selectedDevice.id === dev.id ? 'selected' : ''}`;
        
        let volumesHtml = '';
        if (dev.volumes && dev.volumes.length > 0) {
            dev.volumes.forEach(vol => {
                const usedPct = vol.total > 0 ? (vol.used / vol.total) * 100 : 0;
                volumesHtml += `
                    <div class="volume-item">
                        <div class="volume-meta">
                            <span class="volume-letter">${vol.mount_point} (${vol.label || 'No Label'})</span>
                            <span>${vol.file_system}</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-fill" style="width: ${usedPct}%"></div>
                        </div>
                        <div class="device-space">
                            ${formatBytes(vol.free)} free / ${formatBytes(vol.total)} total
                        </div>
                    </div>
                `;
            });
        } else {
            volumesHtml = `<div class="empty-state" style="padding: 10px; margin-top:8px;">No mounted volumes found</div>`;
        }
        
        item.innerHTML = `
            <div class="device-header">
                <span class="device-name">${dev.model}</span>
                <span class="device-badge">USB</span>
            </div>
            <div style="font-size:11px; color:var(--text-muted); margin-bottom:5px;">S/N: ${dev.serial || 'N/A'}</div>
            ${volumesHtml}
        `;
        
        item.addEventListener('click', () => {
            // Select device
            document.querySelectorAll('.device-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            selectedDevice = dev;
            updateSelectedDisplay();
        });
        
        storageList.appendChild(item);
    });
}

function renderPeripherals(peripherals) {
    peripheralList.innerHTML = '';
    
    if (peripherals.length === 0) {
        peripheralList.innerHTML = `
            <div class="empty-state">
                <p>No other peripherals found</p>
            </div>
        `;
        return;
    }
    
    peripherals.forEach(per => {
        const item = document.createElement('div');
        item.className = 'peripheral-item';
        
        item.innerHTML = `
            <div class="peripheral-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
                </svg>
            </div>
            <div class="peripheral-info">
                <div class="peripheral-name">${per.name}</div>
                <div class="peripheral-class">${per.class}</div>
            </div>
        `;
        peripheralList.appendChild(item);
    });
}

function updateSelectedDisplay() {
    if (!selectedDevice) {
        selectedDeviceInfo.innerHTML = `<span class="placeholder-text">No drive selected</span>`;
        startTestBtn.disabled = true;
        return;
    }
    
    const volumeCount = selectedDevice.volumes ? selectedDevice.volumes.length : 0;
    const mountInfo = volumeCount > 0 ? selectedDevice.volumes[0].mount_point : 'No Mount';
    
    selectedDeviceInfo.innerHTML = `
        <div class="selected-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
                <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
            </svg>
        </div>
        <div class="selected-details">
            <div class="selected-name">${selectedDevice.model}</div>
            <div class="selected-path">Path: ${mountInfo}</div>
        </div>
    `;
    
    // Enable start test only if we have a mounted volume
    startTestBtn.disabled = volumeCount === 0 || testRunning;
}

// Set speedometer radial visual values
function updateMeter(type, val) {
    const maxSpeed = 150.0; // 150 MB/s cap for the progress visualization
    const percentage = Math.min(val / maxSpeed, 1.0);
    const circumference = 2 * Math.PI * 40; // 251.2
    const offset = circumference - (percentage * circumference);
    
    if (type === 'read') {
        readMeter.style.strokeDashoffset = offset;
        readVal.innerText = val.toFixed(2);
    } else {
        writeMeter.style.strokeDashoffset = offset;
        writeVal.innerText = val.toFixed(2);
    }
}

// Function called by python backend to update progress bar
window.updateTestProgress = function(stage, pct, currentSpeed) {
    testStage.innerText = stage === 'write' ? 'Writing Test File...' : 'Reading Test File...';
    testPct.innerText = pct + '%';
    testProgressBar.style.width = pct + '%';
    
    if (stage === 'write') {
        updateMeter('write', currentSpeed);
    } else {
        updateMeter('read', currentSpeed);
    }
};

function runSpeedTest() {
    if (testRunning || !selectedDevice || !selectedDevice.volumes || selectedDevice.volumes.length === 0) return;
    
    const volume = selectedDevice.volumes[0];
    const sizeMb = parseInt(testSizeSelect.value);
    
    testRunning = true;
    startTestBtn.disabled = true;
    testProgressArea.style.opacity = '1';
    
    updateMeter('read', 0);
    updateMeter('write', 0);
    
    showToast(`Starting speed test on ${volume.mount_point} (${sizeMb}MB)...`, 'info');
    
    window.pywebview.api.run_speed_test(selectedDevice.id, volume.mount_point, sizeMb)
        .then(response => {
            testRunning = false;
            startTestBtn.disabled = false;
            
            if (response.success) {
                const res = response.results;
                updateMeter('read', res.read_speed);
                updateMeter('write', res.write_speed);
                
                testStage.innerText = "Speed Test Completed!";
                testPct.innerText = "100%";
                testProgressBar.style.width = "100%";
                
                showToast("Speed test completed successfully!", "success");
                
                // Add report to lists
                addReportToList(response.report_path, selectedDevice.model, res.read_speed, res.write_speed);
                
                // Track for comparison
                trackTestRun(selectedDevice, volume, res);
                
                // Refresh device details
                scanDevices();
            } else {
                testStage.innerText = "Test Failed";
                showToast("Speed test failed: " + response.error, "error");
            }
        })
        .catch(err => {
            testRunning = false;
            startTestBtn.disabled = false;
            testStage.innerText = "Test Error";
            showToast("Error executing speed test: " + err, "error");
        });
}

// Global array tracking technical test runs for comparison
let allTestRuns = [];

function trackTestRun(device, volume, results) {
    const run = {
        device: { model: device.model, serial: device.serial || 'N/A', id: device.id },
        volume: { mount_point: volume.mount_point, file_system: volume.file_system || 'N/A' },
        results: results
    };
    
    // Add to session runs
    allTestRuns.push(run);
    
    if (allTestRuns.length >= 2) {
        document.getElementById('comparison-card').style.display = 'flex';
        renderComparisonTable();
    }
}

function renderComparisonTable() {
    const container = document.getElementById('comparison-table-container');
    if (allTestRuns.length === 0) {
        container.innerHTML = `<div class="empty-state"><p>Perform speed tests on different drives to compare.</p></div>`;
        return;
    }
    
    let headers = '<th>Metric</th>';
    let readRow = '<td>Read Speed</td>';
    let writeRow = '<td>Write Speed</td>';
    let combinedRow = '<td>Combined</td>';
    let pathRow = '<td>Mount Point</td>';
    
    allTestRuns.forEach((run, index) => {
        headers += `<th>Run #${index + 1}<br><span style="font-size:10px;color:var(--text-muted);">${run.device.model}</span></th>`;
        readRow += `<td><strong>${run.results.read_speed} MB/s</strong></td>`;
        writeRow += `<td><strong>${run.results.write_speed} MB/s</strong></td>`;
        combinedRow += `<td>${(run.results.read_speed + run.results.write_speed).toFixed(2)} MB/s</td>`;
        pathRow += `<td>${run.volume.mount_point}</td>`;
    });
    
    container.innerHTML = `
        <table class="comparison-table-ui">
            <thead>
                <tr>${headers}</tr>
            </thead>
            <tbody>
                <tr>${readRow}</tr>
                <tr>${writeRow}</tr>
                <tr>${combinedRow}</tr>
                <tr>${pathRow}</tr>
            </tbody>
        </table>
    `;
}

// Bind Comparison Report button
document.getElementById('generate-comparison-report-btn').addEventListener('click', () => {
    if (allTestRuns.length < 2) {
        showToast("Need at least 2 test runs to generate comparison report.", "warning");
        return;
    }
    
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.generate_comparison_report(allTestRuns)
            .then(res => {
                if (res.success) {
                    showToast("Technical comparison report generated successfully!", "success");
                    openReport(res.report_path);
                } else {
                    showToast("Failed to generate report: " + res.error, "error");
                }
            })
            .catch(err => {
                showToast("Error generating comparison report: " + err, "error");
            });
    }
});

function addReportToList(path, model, read, write) {
    // Save to list
    const report = { path, model, read, write, date: new Date().toLocaleTimeString() };
    sessionReports.unshift(report);
    
    renderReports();
}

function renderReports() {
    reportsList.innerHTML = '';
    
    if (sessionReports.length === 0) {
        reportsList.innerHTML = `
            <div class="empty-state">
                <p>No reports generated in this session yet.</p>
            </div>
        `;
        return;
    }
    
    sessionReports.forEach((rep, idx) => {
        const item = document.createElement('div');
        item.className = 'report-item';
        
        item.innerHTML = `
            <div class="report-info">
                <span class="report-title">${rep.model}</span>
                <span class="report-meta">Read: ${rep.read} MB/s | Write: ${rep.write} MB/s | ${rep.date}</span>
            </div>
            <button class="report-btn" onclick="openReport('${rep.path.replace(/\\/g, '\\\\')}')">Open Report</button>
        `;
        reportsList.appendChild(item);
    });
}

// Function to call python to open the generated HTML report in browser
window.openReport = function(path) {
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.open_html_report(path)
            .then(res => {
                if (!res) {
                    showToast("Failed to open report file.", "error");
                }
            });
    }
};
