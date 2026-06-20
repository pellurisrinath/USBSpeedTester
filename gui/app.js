/**
 * USB Speed Test Application
 * Main application controller and API bridge
 */

class USBSpeedTestApp {
    constructor() {
        this.api = null;
        this.config = {};
        this.devices = [];
        this.testHistory = [];
        this.selectedCompareIds = new Set();
        this.initialized = false;
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            await this.waitForAPI();
            await this.loadConfig();
            this.setupEventListeners();
            
            // Initial data loads
            await this.loadDevices();
            await this.loadReports();
            
            this.initialized = true;
            this.showToast('Application loaded successfully', 'success');
        } catch (error) {
            console.error('Initialization error:', error);
            this.showToast('Failed to initialize application', 'error');
        }
    }

    /**
     * Wait for PyWebView API to be available
     */
    async waitForAPI() {
        return new Promise((resolve) => {
            const checkAPI = () => {
                if (window.pywebview?.api) {
                    this.api = window.pywebview.api;
                    resolve();
                } else {
                    setTimeout(checkAPI, 100);
                }
            };
            checkAPI();
        });
    }

    /**
     * Load application configuration
     */
    async loadConfig() {
        try {
            const response = await this.api.get_config();
            if (response.success) {
                this.config = response.data;
                // Apply to UI inputs
                const mon = this.config.monitoring || {};
                document.getElementById('mon-enabled-cb').checked = mon.enabled !== false;
                document.getElementById('mon-interval-input').value = mon.check_interval_seconds || 60;
                document.getElementById('mon-threshold-input').value = mon.low_disk_threshold_percent || 10;
                
                const speedTest = this.config.speed_test || {};
                document.getElementById('default-size-select').value = speedTest.default_test_size_mb || 100;
                
                // Load AI Settings
                const ai = this.config.ai_chatbot || {};
                document.getElementById('ai-provider-select').value = ai.provider || 'ollama';
                document.getElementById('ai-key-input').value = ai.api_key || '';
                document.getElementById('ai-model-input').value = ai.model || 'llama3';
                document.getElementById('ai-endpoint-input').value = ai.endpoint || 'http://localhost:11434';
                this.handleAIProviderChange();
            }
        } catch (error) {
            console.warn('Failed to load configuration:', error);
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.closest('.tab-button')));
        });

        // Refresh button
        document.getElementById('refreshBtn')?.addEventListener('click', () => {
            this.loadDevices();
            this.loadReports();
        });

        // Settings button
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.openSettings());
        document.getElementById('closeSettingsBtn')?.addEventListener('click', () => this.closeSettings());
        document.getElementById('saveSettingsBtn')?.addEventListener('click', () => this.saveConfigSettings());
        document.getElementById('exportConfigBtn')?.addEventListener('click', () => this.exportConfigSettings());

        // Chatbot buttons
        document.getElementById('sendChatBtn')?.addEventListener('click', () => this.sendChat());
        document.getElementById('clearChatBtn')?.addEventListener('click', () => this.clearChat());
        document.getElementById('chatInput')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendChat();
            }
        });

        // Device type filter
        document.getElementById('deviceTypeFilter')?.addEventListener('change', (e) => {
            this.filterDevicesByType(e.target.value);
        });

        // Open reports folder button
        document.getElementById('openReportsFolderBtn')?.addEventListener('click', async () => {
            if (this.api) {
                const appInfo = await this.api.get_app_info();
                if (appInfo.success) {
                    const dataDir = appInfo.data.data_directory;
                    const reportsPath = dataDir + (dataDir.includes('\\') ? '\\reports' : '/reports');
                    await this.api.open_path(reportsPath);
                }
            }
        });

        // Open comparisons folder button
        document.getElementById('openComparisonsFolderBtn')?.addEventListener('click', async () => {
            if (this.api) {
                const appInfo = await this.api.get_app_info();
                if (appInfo.success) {
                    const dataDir = appInfo.data.data_directory;
                    const comparisonsPath = dataDir + (dataDir.includes('\\') ? '\\comparisions' : '/comparisions');
                    await this.api.open_path(comparisonsPath);
                }
            }
        });

        // Speed test cancel button
        document.getElementById('cancelBtn')?.addEventListener('click', async () => {
            if (this.api) {
                await this.api.cancel_speed_test();
                this.showToast('Benchmark cancellation requested', 'info');
            }
        });

        // Global function registration so HTML clicks function correctly
        window.runSpeedTestFromCard = (id) => this.switchTabToSpeedTest(id);
        window.openReportFromList = (path) => this.openReport(path);
        window.app = this;

        // Auto-refresh devices list every 5 seconds
        setInterval(() => {
            if (this.initialized && !document.getElementById('progressModal').classList.contains('active')) {
                this.loadDevicesQuietly();
            }
        }, 5000);
    }

    /**
     * Switch between tabs
     */
    switchTab(tabButton) {
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        tabButton.classList.add('active');
        const tabName = tabButton.dataset.tab;
        const tabContent = document.getElementById(`${tabName}-tab`);
        if (tabContent) {
            tabContent.classList.add('active');
        }

        // Action triggers based on active tab
        if (tabName === 'storage') {
            this.renderStorageAnalysis();
        } else if (tabName === 'speedtest') {
            this.renderSpeedTestLayout();
        } else if (tabName === 'comparison') {
            this.renderComparisonPanel();
        } else if (tabName === 'reports') {
            this.loadReports();
        }
    }

    switchTabToSpeedTest(deviceId) {
        const speedtestTabBtn = document.querySelector('.tab-button[data-tab="speedtest"]');
        if (speedtestTabBtn) {
            this.switchTab(speedtestTabBtn);
            // Pre-select device in dropdown
            setTimeout(() => {
                const select = document.getElementById('benchmark-device-select');
                if (select) {
                    select.value = deviceId;
                }
            }, 100);
        }
    }

    /**
     * Load all connected devices (with loading spinner overlay status)
     */
    async loadDevices() {
        this.updateStatusText('Scanning USB controller...');
        await this.loadDevicesQuietly();
    }

    async loadDevicesQuietly() {
        try {
            const response = await this.api.get_all_devices();
            if (response.success) {
                this.devices = response.data.devices;
                this.displayDevices(this.devices);
                this.updateStatusText(`${this.devices.length} USB devices detected`);
                
                // If storage tab is active, refresh it too
                const activeTab = document.querySelector('.tab-button.active')?.dataset.tab;
                if (activeTab === 'storage') {
                    this.renderStorageAnalysis();
                }
            }
        } catch (error) {
            console.error('Error loading devices:', error);
        }
    }

    /**
     * Display devices in the grid
     */
    displayDevices(devices) {
        const grid = document.getElementById('devices-list');
        if (!grid) return;

        grid.innerHTML = '';

        if (devices.length === 0) {
            grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><p>No USB devices detected.</p></div>';
            return;
        }

        devices.forEach(device => {
            const card = document.createElement('div');
            card.className = 'device-card';
            
            let actionHtml = '';
            if (device.device_type === 'STORAGE') {
                actionHtml = `
                    <button class="btn btn-primary" onclick="runSpeedTestFromCard('${device.id}')">
                        <i class="fas fa-tachometer-alt"></i> Speed Test
                    </button>
                `;
            }

            card.innerHTML = `
                <div class="device-icon">${this.getDeviceIcon(device.device_type)}</div>
                <h3 class="device-name">${device.name}</h3>
                <div class="device-info">
                    <div class="device-info-item">
                        <span>Class Type:</span>
                        <strong>${device.device_type}</strong>
                    </div>
                    <div class="device-info-item">
                        <span>Vendor ID:</span>
                        <strong>${device.vendor_id || 'N/A'}</strong>
                    </div>
                    <div class="device-info-item">
                        <span>Removable:</span>
                        <strong>${device.is_removable ? 'Yes' : 'No'}</strong>
                    </div>
                    ${device.mount_point ? `
                    <div class="device-info-item">
                        <span>Mount Path:</span>
                        <strong>${device.mount_point}</strong>
                    </div>
                    ` : ''}
                </div>
                <div class="device-actions">
                    ${actionHtml}
                </div>
            `;
            grid.appendChild(card);
        });
    }

    getDeviceIcon(deviceType) {
        const icons = {
            'STORAGE': '<i class="fas fa-hdd"></i>',
            'AUDIO': '<i class="fas fa-headphones"></i>',
            'CAMERA': '<i class="fas fa-camera"></i>',
            'PRINTER': '<i class="fas fa-print"></i>',
            'INPUT': '<i class="fas fa-keyboard"></i>',
            'MOBILE': '<i class="fas fa-mobile-alt"></i>',
            'GENERIC': '<i class="fas fa-usb"></i>',
        };
        return icons[deviceType] || icons['GENERIC'];
    }

    /**
     * Render Storage Analysis Panel
     */
    renderStorageAnalysis() {
        const panel = document.getElementById('storage-panel');
        if (!panel) return;

        const storageDevices = this.devices.filter(d => d.device_type === 'STORAGE');
        panel.innerHTML = '';

        if (storageDevices.length === 0) {
            panel.innerHTML = '<div class="empty-state"><p>No USB storage devices connected.</p></div>';
            return;
        }

        storageDevices.forEach(dev => {
            const usedPct = dev.total_space_gb > 0 ? (dev.used_space_gb / dev.total_space_gb) * 100 : 0;
            const card = document.createElement('div');
            card.className = 'storage-item-card';
            card.innerHTML = `
                <div class="storage-item-details">
                    <div class="storage-item-title">${dev.name} (${dev.mount_point})</div>
                    <div class="storage-bar-outer">
                        <div class="storage-bar-inner" style="width: ${usedPct}%"></div>
                    </div>
                    <div class="storage-item-meta">
                        <span>File System: <strong>${dev.file_system}</strong></span>
                        <span>${dev.free_space_gb.toFixed(2)} GB Free / ${dev.total_space_gb.toFixed(2)} GB Total</span>
                    </div>
                </div>
                <div class="storage-item-percent">
                    <div class="value">${usedPct.toFixed(0)}%</div>
                    <div class="label">Space Occupied</div>
                </div>
            `;
            panel.appendChild(card);
        });
    }

    /**
     * Render Speed Test Panel Layout
     */
    renderSpeedTestLayout() {
        const panel = document.getElementById('speedtest-panel');
        if (!panel) return;

        const storageDevices = this.devices.filter(d => d.device_type === 'STORAGE');
        let optionsHtml = '';
        storageDevices.forEach(d => {
            optionsHtml += `<option value="${d.id}">${d.name} (${d.mount_point})</option>`;
        });

        if (storageDevices.length === 0) {
            panel.innerHTML = '<div class="empty-state" style="grid-column: 1/-1;"><p>Please connect a USB storage device to run speed tests.</p></div>';
            return;
        }

        panel.innerHTML = `
            <div class="speedtest-controls-card">
                <h3>Benchmark Configuration</h3>
                <div class="form-group" style="margin-top:15px;">
                    <label for="benchmark-device-select">Select USB Drive:</label>
                    <select id="benchmark-device-select">
                        ${optionsHtml}
                    </select>
                </div>
                <div class="form-group">
                    <label for="benchmark-size-select">Test Write/Read File Size:</label>
                    <select id="benchmark-size-select">
                        <option value="20">20 MB (Fast)</option>
                        <option value="50">50 MB</option>
                        <option value="100" selected>100 MB</option>
                        <option value="250">250 MB (Thorough)</option>
                    </select>
                </div>
                <button id="startBenchmarkBtn" class="btn btn-primary" style="margin-top:15px;" onclick="app.triggerSpeedTest()">
                    <i class="fas fa-play"></i> Start Benchmark Test
                </button>
            </div>

            <div class="speedtest-result-display" id="speedtest-result-display">
                <div class="placeholder-text" style="color:var(--color-text-tertiary); font-style:italic;">
                    Configure benchmark parameters and click Start.
                </div>
            </div>
        `;
    }

    async triggerSpeedTest() {
        const deviceId = document.getElementById('benchmark-device-select').value;
        const sizeMb = parseInt(document.getElementById('benchmark-size-select').value);
        
        if (!deviceId) return;
        
        // Show progress overlay modal
        const modal = document.getElementById('progressModal');
        const fill = document.getElementById('progressFill');
        const text = document.getElementById('progressText');
        const stageText = document.getElementById('progressStatusText');
        
        fill.style.width = '0%';
        text.innerText = '0%';
        stageText.innerText = 'Preparing files...';
        modal.classList.add('active');
        
        // Setup global hook for progress callbacks
        window.updateTestProgress = (stage, pct, currentSpeed) => {
            fill.style.width = pct + '%';
            text.innerText = pct + '%';
            stageText.innerText = `${stage === 'write' ? 'Writing' : 'Reading'} test file... (${currentSpeed.toFixed(1)} MB/s)`;
        };

        try {
            const response = await this.api.run_speed_test(deviceId, sizeMb);
            modal.classList.remove('active');
            
            if (response.success) {
                this.showToast('Benchmark speed test completed!', 'success');
                this.renderSpeedTestResults(response.data);
                // Force reload reports
                this.loadReports();
            } else {
                this.showToast('Speed test error: ' + response.error, 'error');
            }
        } catch (e) {
            modal.classList.remove('active');
            this.showToast('Failed to run speed test: ' + e, 'error');
        }
    }

    renderSpeedTestResults(res) {
        const display = document.getElementById('speedtest-result-display');
        if (!display) return;

        display.innerHTML = `
            <div class="test-result-card" style="animation: fadeIn 0.3s ease;">
                <h3 style="font-family:var(--font-primary); font-size:var(--font-size-lg);">${res.device_name}</h3>
                <div class="result-metrics">
                    <div class="metric">
                        <label><i class="fas fa-arrow-down"></i> Read Velocity</label>
                        <value>${res.read_speed_mbps.toFixed(2)} <span style="font-size:12px;">MB/s</span></value>
                    </div>
                    <div class="metric">
                        <label><i class="fas fa-arrow-up"></i> Write Velocity</label>
                        <value>${res.write_speed_mbps.toFixed(2)} <span style="font-size:12px;">MB/s</span></value>
                    </div>
                    <div class="metric" style="grid-column: 1/-1;">
                        <label>Benchmark Technical Specs</label>
                        <span style="font-size:12px; color:var(--color-text-secondary);">
                            Test File: ${res.test_size_mb} MB | Write took: ${res.write_duration_sec.toFixed(1)}s | Read took: ${res.read_duration_sec.toFixed(1)}s
                        </span>
                    </div>
                </div>
                <button class="btn btn-secondary" style="width:100%;" onclick="openReportFromList('${res.report_path.replace(/\\/g, '\\\\')}')">
                    <i class="fas fa-external-link-alt"></i> Open Detailed HTML Report
                </button>
            </div>
        `;
    }

    /**
     * Render Comparison Tab
     */
    async renderComparisonPanel() {
        const panel = document.getElementById('comparison-panel');
        if (!panel) return;

        try {
            const histRes = await this.api.get_test_history();
            if (histRes.success) {
                this.testHistory = histRes.data.tests;
            }
        } catch (e) {
            console.error("Failed to load test history", e);
        }

        panel.innerHTML = '';

        if (this.testHistory.length === 0) {
            panel.innerHTML = '<div class="empty-state"><p>Perform at least one speed test benchmark to see session results.</p></div>';
            return;
        }

        let runsListHtml = '';
        this.testHistory.forEach(run => {
            const isChecked = this.selectedCompareIds.has(run.test_id) ? 'checked' : '';
            runsListHtml += `
                <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(255,255,255,0.02); border:1px solid var(--color-border-light); border-radius:8px; padding:10px var(--spacing-md); margin-bottom:8px;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer;">
                        <input type="checkbox" class="compare-cb" data-id="${run.test_id}" ${isChecked} onchange="app.toggleCompareSelection('${run.test_id}')">
                        <span style="font-size:13px; font-weight:600;">${run.device_name} (${run.device_path})</span>
                    </label>
                    <span style="font-size:11px; color:var(--color-text-secondary);">Read: ${run.read_speed_mbps.toFixed(1)} MB/s | Write: ${run.write_speed_mbps.toFixed(1)} MB/s</span>
                </div>
            `;
        });

        // Compute comparison metrics
        let compTableHtml = '<div class="placeholder-text" style="text-align:center; color:var(--color-text-tertiary); font-style:italic;">Select at least two drives above to build comparison.</div>';
        const selectedRuns = this.testHistory.filter(r => this.selectedCompareIds.has(r.test_id));
        
        if (selectedRuns.length >= 2) {
            let cols = '<th>Performance Metric</th>';
            let rRow = '<td>Read Speed</td>';
            let wRow = '<td>Write Speed</td>';
            let cRow = '<td>Combined Speed</td>';
            let sRow = '<td>File Size</td>';
            
            selectedRuns.forEach((run, idx) => {
                cols += `<th>Run #${idx+1}<br><span style="font-size:9px;color:var(--color-text-secondary);">${run.device_name}</span></th>`;
                rRow += `<td><strong>${run.read_speed_mbps.toFixed(1)} MB/s</strong></td>`;
                wRow += `<td><strong>${run.write_speed_mbps.toFixed(1)} MB/s</strong></td>`;
                cRow += `<td>${(run.read_speed_mbps + run.write_speed_mbps).toFixed(1)} MB/s</td>`;
                sRow += `<td>${run.test_size_mb} MB</td>`;
            });
            
            compTableHtml = `
                <table class="comparison-table-ui" style="margin-top:15px; border-radius:8px; overflow:hidden;">
                    <thead>
                        <tr>${cols}</tr>
                    </thead>
                    <tbody>
                        <tr>${rRow}</tr>
                        <tr>${wRow}</tr>
                        <tr>${cRow}</tr>
                        <tr>${sRow}</tr>
                    </tbody>
                </table>
            `;
        }

        panel.innerHTML = `
            <div style="background:rgba(255,255,255,0.01); border:1px solid var(--color-border); border-radius:12px; padding:20px; margin-bottom:20px;">
                <h3 style="margin-bottom:12px; font-size:var(--font-size-base); font-family:var(--font-primary);">Select Session Benchmarks to Compare</h3>
                ${runsListHtml}
            </div>
            
            <div style="background:rgba(255,255,255,0.01); border:1px solid var(--color-border); border-radius:12px; padding:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="font-size:var(--font-size-base); font-family:var(--font-primary);">Comparison Matrix</h3>
                    ${selectedRuns.length >= 2 ? `
                        <button class="btn btn-primary" style="font-size:12px; padding:6px 12px;" onclick="app.triggerComparisonReport()">
                            <i class="fas fa-file-invoice"></i> Compile Plain HTML Comparison Report
                        </button>
                    ` : ''}
                </div>
                <div style="overflow-x:auto;">
                    ${compTableHtml}
                </div>
            </div>
        `;
    }

    toggleCompareSelection(testId) {
        if (this.selectedCompareIds.has(testId)) {
            this.selectedCompareIds.delete(testId);
        } else {
            this.selectedCompareIds.add(testId);
        }
        this.renderComparisonPanel();
    }

    async triggerComparisonReport() {
        const selected = Array.from(this.selectedCompareIds);
        if (selected.length < 2) return;

        this.showToast('Compiling technical comparison report...', 'info');
        try {
            const response = await this.api.generate_comparison_report(selected);
            if (response.success) {
                this.showToast('Comparison HTML report generated!', 'success');
                await this.api.open_report(response.data.report_path);
            } else {
                this.showToast('Comparison failed: ' + response.error, 'error');
            }
        } catch (e) {
            this.showToast('Error generating comparison: ' + e, 'error');
        }
    }

    /**
     * Reports Tab List loader
     */
    async loadReports() {
        const panel = document.getElementById('reports-panel');
        if (!panel) return;

        try {
            const response = await this.api.get_reports_list(50);
            panel.innerHTML = '';
            
            if (response.success && response.data.reports.length > 0) {
                response.data.reports.forEach(rep => {
                    const row = document.createElement('div');
                    row.className = 'report-item-ui';
                    const sz = (rep.file_size_bytes / 1024).toFixed(0);
                    const isCompare = rep.report_type === 'comparison';
                    
                    row.innerHTML = `
                        <div class="report-item-info">
                            <span class="report-item-title">
                                <i class="${isCompare ? 'fas fa-balance-scale' : 'fas fa-hdd'}" style="color:var(--color-primary); margin-right:8px;"></i>
                                ${rep.file_name}
                            </span>
                            <span class="report-item-meta">Type: ${rep.report_type.toUpperCase()} | Size: ${sz} KB | Created: ${rep.created_timestamp.substring(0,10)}</span>
                        </div>
                        <button class="btn btn-secondary" onclick="openReportFromList('${rep.file_path.replace(/\\/g, '\\\\')}')">
                            <i class="fas fa-folder-open"></i> Open Report
                        </button>
                    `;
                    panel.appendChild(row);
                });
            } else {
                panel.innerHTML = '<div class="empty-state"><p>No generated reports found.</p></div>';
            }
        } catch (e) {
            console.error("Failed to load reports list", e);
        }
    }

    async openReport(path) {
        if (this.api) {
            await this.api.open_report(path);
        }
    }

    /**
     * Settings Actions
     */
    openSettings() {
        this.loadConfig(); // Reload current preferences
        document.getElementById('settingsModal').classList.add('active');
    }

    closeSettings() {
        document.getElementById('settingsModal').classList.remove('active');
    }

    async saveConfigSettings() {
        const monEnabled = document.getElementById('mon-enabled-cb').checked;
        const monInterval = parseInt(document.getElementById('mon-interval-input').value);
        const monThreshold = parseInt(document.getElementById('mon-threshold-input').value);
        const testSize = parseInt(document.getElementById('default-size-select').value);
        
        const payload = {
            "speed_test": {
                "default_test_size_mb": testSize,
                "chunk_size_mb": 10,
                "timeout_seconds": 300,
                "enable_write_test": true,
                "enable_read_test": true
            },
            "monitoring": {
                "enabled": monEnabled,
                "check_interval_seconds": monInterval,
                "low_disk_threshold_percent": monThreshold,
                "enable_notifications": true,
                "ignored_devices": this.config.monitoring?.ignored_devices || []
            },
            "ui": {
                "theme": "dark",
                "auto_refresh_interval_ms": 5000,
                "show_all_devices": true
            },
            "reporting": this.config.reporting || {
                "auto_save": true,
                "include_charts": true,
                "include_device_history": true
            },
            "ai_chatbot": {
                "provider": document.getElementById('ai-provider-select').value,
                "api_key": document.getElementById('ai-key-input').value,
                "model": document.getElementById('ai-model-input').value,
                "endpoint": document.getElementById('ai-endpoint-input').value
            }
        };

        try {
            const response = await this.api.update_config(payload);
            if (response.success) {
                this.showToast('Configuration settings updated successfully', 'success');
                this.closeSettings();
            } else {
                this.showToast('Failed to save configuration: ' + response.error, 'error');
            }
        } catch (e) {
            this.showToast('Error updating configuration: ' + e, 'error');
        }
    }

    async exportConfigSettings() {
        if (!this.api) return;
        try {
            const response = await this.api.export_configuration();
            if (response.success) {
                this.showToast('Configuration exported successfully', 'success');
            } else if (response.error) {
                const err = response.error.toLowerCase();
                if (!err.includes('cancel') && !err.includes('none') && !err.includes('null')) {
                    this.showToast('Failed to export configuration: ' + response.error, 'error');
                }
            }
        } catch (e) {
            this.showToast('Error exporting configuration: ' + e, 'error');
        }
    }

    /**
     * Toast System
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';
        if (type === 'warning') icon = 'exclamation-triangle';

        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Helper Status Updater
     */
    updateStatusText(text) {
        const statusElement = document.getElementById('statusText');
        if (statusElement) {
            statusElement.textContent = text;
        }
    }

    filterDevicesByType(type) {
        if (!type) {
            this.displayDevices(this.devices);
            return;
        }
        const filtered = this.devices.filter(d => d.device_type === type);
        this.displayDevices(filtered);
    }

    /* ============================================
       AI Diagnostics Assistant Client Logic
       ============================================ */

    handleAIProviderChange() {
        const provider = document.getElementById('ai-provider-select').value;
        const keyGroup = document.getElementById('ai-key-group');
        const endpointInput = document.getElementById('ai-endpoint-input');
        const modelInput = document.getElementById('ai-model-input');

        // Show/hide API Key group
        if (provider === 'ollama') {
            keyGroup.style.display = 'none';
        } else {
            keyGroup.style.display = 'block';
        }

        // Auto-fill endpoints & models if empty or default
        const defaultEndpoints = {
            'ollama': 'http://localhost:11434',
            'openai': 'https://api.openai.com',
            'claude': 'https://api.anthropic.com',
            'gemini': 'https://generativelanguage.googleapis.com',
            'custom': 'http://localhost:1234'
        };

        const defaultModels = {
            'ollama': 'llama3',
            'openai': 'gpt-4o',
            'claude': 'claude-3-5-sonnet-20240620',
            'gemini': 'gemini-1.5-flash',
            'custom': 'local-model'
        };

        // If endpoint is empty or matches one of the defaults, update it
        const currentEndpoint = endpointInput.value.trim();
        const isDefaultEndpoint = Object.values(defaultEndpoints).includes(currentEndpoint) || currentEndpoint === '';
        if (isDefaultEndpoint && defaultEndpoints[provider]) {
            endpointInput.value = defaultEndpoints[provider];
        }

        // If model is empty or matches one of the defaults, update it
        const currentModel = modelInput.value.trim();
        const isDefaultModel = Object.values(defaultModels).includes(currentModel) || currentModel === '';
        if (isDefaultModel && defaultModels[provider]) {
            modelInput.value = defaultModels[provider];
        }
    }

    toggleAPIKeyVisibility() {
        const input = document.getElementById('ai-key-input');
        const icon = document.getElementById('ai-key-toggle-icon');
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }

    async testAIConnection() {
        const provider = document.getElementById('ai-provider-select').value;
        const apiKey = document.getElementById('ai-key-input').value.trim();
        const model = document.getElementById('ai-model-input').value.trim();
        const endpoint = document.getElementById('ai-endpoint-input').value.trim();

        if (!model || !endpoint) {
            this.showToast('Model name and Endpoint URL are required.', 'error');
            return;
        }

        const btn = document.getElementById('testAIConnectionBtn');
        const origText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';

        try {
            const response = await this.api.test_llm_connection(provider, apiKey, model, endpoint);
            btn.disabled = false;
            btn.innerHTML = origText;

            if (response.success) {
                this.showToast('Connection Successful! AI replied: ' + response.data.reply, 'success');
            } else {
                this.showToast('Connection Failed: ' + response.error, 'error');
            }
        } catch (e) {
            btn.disabled = false;
            btn.innerHTML = origText;
            this.showToast('Test failed: ' + e, 'error');
        }
    }

    // Chat logic
    getChatHistory() {
        const messages = [];
        const bubbles = document.querySelectorAll('#chatMessages .chat-message');
        bubbles.forEach(b => {
            if (b.id === 'chatTypingIndicator') return;
            const role = b.classList.contains('user') ? 'user' : 'assistant';
            const content = b.querySelector('.message-bubble').innerText;
            messages.push({ role, content });
        });
        return messages;
    }

    async sendChat() {
        const input = document.getElementById('chatInput');
        const text = input.value.trim();
        if (!text) return;

        // Clear input
        input.value = '';

        // Render user message
        this.renderChatMessage('user', text);
        this.showChatTypingIndicator();
        this.scrollChatToBottom();

        try {
            const history = this.getChatHistory();
            const response = await this.api.send_chatbot_message(history);
            
            this.removeChatTypingIndicator();

            if (response.success) {
                this.renderChatMessage('assistant', response.data.reply);
            } else {
                this.renderChatMessage('assistant', '⚠️ Error: ' + response.error);
            }
        } catch (e) {
            this.removeChatTypingIndicator();
            this.renderChatMessage('assistant', '⚠️ Connection error: ' + e);
        }
        this.scrollChatToBottom();
    }

    sendQuickPrompt(promptText) {
        document.getElementById('chatInput').value = promptText;
        this.sendChat();
    }

    renderChatMessage(sender, text) {
        const feed = document.getElementById('chatMessages');
        if (!feed) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (sender === 'user') {
            bubble.innerText = text;
        } else {
            // Render markdown to HTML
            bubble.innerHTML = this.formatMarkdown(text);
            
            // Add action row with copy button
            const actionRow = document.createElement('div');
            actionRow.className = 'message-actions';
            
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-msg-btn';
            copyBtn.title = 'Copy message to clipboard';
            copyBtn.innerHTML = '📋 Copy';
            copyBtn.onclick = (e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(text);
                copyBtn.innerHTML = '✅ Copied!';
                setTimeout(() => copyBtn.innerHTML = '📋 Copy', 2000);
            };
            actionRow.appendChild(copyBtn);
            bubble.appendChild(actionRow);
        }

        msgDiv.appendChild(bubble);
        feed.appendChild(msgDiv);
    }

    showChatTypingIndicator() {
        this.removeChatTypingIndicator();
        
        const feed = document.getElementById('chatMessages');
        const indicator = document.createElement('div');
        indicator.id = 'chatTypingIndicator';
        indicator.className = 'chat-message assistant';
        indicator.innerHTML = `
            <div class="message-bubble" style="padding: 10px 14px;">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        feed.appendChild(indicator);
    }

    removeChatTypingIndicator() {
        const ind = document.getElementById('chatTypingIndicator');
        if (ind) ind.remove();
    }

    clearChat() {
        this.clearChatFeed();
    }

    clearChatFeed() {
        const feed = document.getElementById('chatMessages');
        if (feed) {
            feed.innerHTML = `
                <div class="chat-message assistant">
                    <div class="message-bubble">
                        Hello! I am your AI Diagnostics Assistant. I can help you analyze your USB speed test benchmarks, troubleshoot connectivity issues, or explain hardware specifications.
                    </div>
                </div>
            `;
            this.showToast('Chat history cleared', 'info');
        }
    }

    scrollChatToBottom() {
        const feed = document.getElementById('chatMessages');
        if (feed) {
            feed.scrollTop = feed.scrollHeight;
        }
    }

    formatMarkdown(text) {
        // Obfuscate HTML tags to prevent XSS
        let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        
        // Code Blocks ```code```
        html = html.replace(/```([\s\S]+?)```/g, (match, p1) => {
            return `<pre><code>${p1.trim()}</code></pre>`;
        });
        
        // Inline code `code`
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Bold **text**
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Unordered lists
        html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        
        // Line breaks
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        return `<p>${html}</p>`;
    }
}

// Initialize application on DOM load
document.addEventListener('DOMContentLoaded', () => {
    new USBSpeedTestApp();
});
