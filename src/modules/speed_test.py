import os
import time
import datetime
import sys
from pathlib import Path

# Try to import from parent config if running as package
try:
    from config import REPORTS_DIR, COMPARISONS_DIR
except ImportError:
    # Fallback to local import relative to folder structure
    sys.path.append(str(Path(__file__).parent.parent))
    from config import REPORTS_DIR, COMPARISONS_DIR

def perform_speed_test(mount_point, test_file_size_mb=50, progress_callback=None):
    """
    Performs write and read speed tests on the specified mount point.
    test_file_size_mb: size of test file in megabytes.
    progress_callback: function that takes (stage, percentage, speed_estimate)
    """
    test_file_path = os.path.join(mount_point, ".usb_speed_test_temp")
    chunk_size = 1024 * 1024  # 1MB chunks
    total_bytes = test_file_size_mb * chunk_size
    
    # Generate dummy data (1MB of random-like data once)
    dummy_chunk = os.urandom(chunk_size)
    
    # Write test
    write_start_time = time.perf_counter()
    bytes_written = 0
    
    try:
        if progress_callback:
            progress_callback("write", 0, 0)
            
        with open(test_file_path, "wb", buffering=0) as f:
            for i in range(test_file_size_mb):
                f.write(dummy_chunk)
                # Force flush to disk
                f.flush()
                os.fsync(f.fileno())
                bytes_written += chunk_size
                elapsed = time.perf_counter() - write_start_time
                current_speed = (bytes_written / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                if progress_callback:
                    progress_callback("write", int((i + 1) / test_file_size_mb * 100), current_speed)
                    
        write_duration = time.perf_counter() - write_start_time
        write_speed = (bytes_written / (1024 * 1024)) / write_duration
        
    except Exception as e:
        if os.path.exists(test_file_path):
            try: os.remove(test_file_path)
            except: pass
        raise Exception(f"Write test failed: {e}")
        
    # Read test
    read_start_time = time.perf_counter()
    bytes_read = 0
    
    try:
        if progress_callback:
            progress_callback("read", 0, 0)
            
        with open(test_file_path, "rb") as f:
            for i in range(test_file_size_mb):
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                bytes_read += len(chunk)
                elapsed = time.perf_counter() - read_start_time
                current_speed = (bytes_read / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                if progress_callback:
                    progress_callback("read", int((i + 1) / test_file_size_mb * 100), current_speed)
                    
        read_duration = time.perf_counter() - read_start_time
        read_speed = (bytes_read / (1024 * 1024)) / read_duration
        
    except Exception as e:
        raise Exception(f"Read test failed: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            try:
                os.remove(test_file_path)
            except Exception as e:
                print(f"Warning: could not remove temp file: {e}")
                
    return {
        "write_speed": round(write_speed, 2),
        "read_speed": round(read_speed, 2),
        "write_duration": round(write_duration, 2),
        "read_duration": round(read_duration, 2),
        "test_size_mb": test_file_size_mb
    }

def generate_html_report(device_info, volume_info, results):
    """
    Generates a detailed, premium HTML report of the speed test and disk space.
    Saves it to the platform-specific reports folder config.REPORTS_DIR.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Calculate percentage space
    used_pct = round((volume_info["used"] / volume_info["total"]) * 100, 1) if volume_info["total"] > 0 else 0
    free_pct = round(100 - used_pct, 1)
    
    total_gb = round(volume_info["total"] / (1024**3), 2)
    used_gb = round(volume_info["used"] / (1024**3), 2)
    free_gb = round(volume_info["free"] / (1024**3), 2)
    
    # Target directory from configuration
    report_dir = str(REPORTS_DIR)
        
    safe_model_name = "".join([c if c.isalnum() else "_" for c in device_info["model"]])
    report_filename = f"report_{safe_model_name}_{file_timestamp}.html"
    report_path = os.path.join(report_dir, report_filename)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USB Speed Test Report - {device_info['model']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0d0e15;
            --card-bg: rgba(22, 24, 37, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-color: #e2e8f0;
            --text-muted: #94a3b8;
            --primary: #8b5cf6;
            --primary-glow: rgba(139, 92, 246, 0.3);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.3);
            --info: #06b6d4;
            --warning: #f59e0b;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Outfit', sans-serif;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .container::before {{
            content: '';
            position: absolute;
            top: -100px;
            left: -100px;
            width: 300px;
            height: 300px;
            background: var(--primary-glow);
            filter: blur(100px);
            border-radius: 50%;
            z-index: 0;
            pointer-events: none;
        }}
        
        .container::after {{
            content: '';
            position: absolute;
            bottom: -100px;
            right: -100px;
            width: 300px;
            height: 300px;
            background: var(--success-glow);
            filter: blur(100px);
            border-radius: 50%;
            z-index: 0;
            pointer-events: none;
        }}
        
        .header {{
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 24px;
            margin-bottom: 30px;
        }}
        
        .title-area h1 {{
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 30%, var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .title-area p {{
            font-size: 14px;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        
        .timestamp {{
            font-size: 14px;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.04);
            padding: 8px 16px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}
        
        .grid {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
        }}
        
        .card h2 {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .speed-meters {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}
        
        .speed-box {{
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            border: 1px solid var(--border-color);
            position: relative;
        }}
        
        .speed-box.read {{
            border-color: rgba(6, 182, 212, 0.2);
        }}
        
        .speed-box.write {{
            border-color: rgba(139, 92, 246, 0.2);
        }}
        
        .speed-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }}
        
        .speed-value {{
            font-size: 28px;
            font-weight: 800;
        }}
        
        .speed-box.read .speed-value {{
            color: var(--info);
        }}
        
        .speed-box.write .speed-value {{
            color: var(--primary);
        }}
        
        .speed-unit {{
            font-size: 12px;
            font-weight: 400;
            color: var(--text-muted);
            margin-left: 2px;
        }}
        
        .space-chart-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
        }}
        
        .progress-ring {{
            position: relative;
            width: 120px;
            height: 120px;
        }}
        
        .progress-ring-circle {{
            transition: stroke-dashoffset 0.35s;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }}
        
        .chart-label {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}
        
        .chart-pct {{
            font-size: 20px;
            font-weight: 800;
            color: #fff;
        }}
        
        .chart-desc {{
            font-size: 10px;
            color: var(--text-muted);
            text-transform: uppercase;
        }}
        
        .space-details {{
            margin-top: 16px;
            width: 100%;
        }}
        
        .space-row {{
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        
        .space-row span:first-child {{
            color: var(--text-muted);
        }}
        
        .space-row span:last-child {{
            font-weight: 600;
        }}
        
        .dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }}
        
        .dot.used {{ background-color: var(--primary); }}
        .dot.free {{ background-color: var(--success); }}
        
        .device-info-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin-top: 10px;
            position: relative;
            z-index: 1;
        }}
        
        .device-info-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .device-info-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .device-info-table td:first-child {{
            color: var(--text-muted);
            width: 40%;
        }}
        
        .device-info-table td:last-child {{
            font-weight: 600;
            color: #fff;
            text-align: right;
        }}
        
        .footer {{
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 30px;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title-area">
                <h1>USB Speed Test Report</h1>
                <p>Detailed performance and storage health report</p>
            </div>
            <div class="timestamp">{timestamp}</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                    Performance Metrics
                </h2>
                <div class="speed-meters">
                    <div class="speed-box read">
                        <div class="speed-label">Read Speed</div>
                        <div class="speed-value">{results['read_speed']}<span class="speed-unit">MB/s</span></div>
                    </div>
                    <div class="speed-box write">
                        <div class="speed-label">Write Speed</div>
                        <div class="speed-value">{results['write_speed']}<span class="speed-unit">MB/s</span></div>
                    </div>
                </div>
                <div style="margin-top: 16px; font-size: 13px; color: var(--text-muted); text-align: center;">
                    Tested with a {results['test_size_mb']}MB file. Write took {results['write_duration']}s, Read took {results['read_duration']}s.
                </div>
            </div>
            
            <div class="card">
                <h2>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/></svg>
                    Storage Allocation
                </h2>
                <div class="space-chart-container">
                    <div class="progress-ring">
                        <svg width="120" height="120">
                            <circle stroke="rgba(255,255,255,0.03)" stroke-width="12" fill="transparent" r="50" cx="60" cy="60"/>
                            <circle stroke="url(#gradient)" stroke-width="12" stroke-dasharray="314.16" stroke-dashoffset="{314.16 - (314.16 * used_pct / 100)}" stroke-linecap="round" fill="transparent" r="50" cx="60" cy="60" class="progress-ring-circle"/>
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="var(--primary)"/>
                                    <stop offset="100%" stop-color="var(--info)"/>
                                </linearGradient>
                            </defs>
                        </svg>
                        <div class="chart-label">
                            <div class="chart-pct">{used_pct}%</div>
                            <div class="chart-desc">Used</div>
                        </div>
                    </div>
                    
                    <div class="space-details">
                        <div class="space-row">
                            <span><span class="dot used"></span>Used Space</span>
                            <span>{used_gb} GB</span>
                        </div>
                        <div class="space-row">
                            <span><span class="dot free"></span>Free Space</span>
                            <span>{free_gb} GB</span>
                        </div>
                        <div class="space-row" style="border-top: 1px solid var(--border-color); padding-top: 8px; margin-top: 8px;">
                            <span>Total Capacity</span>
                            <span>{total_gb} GB</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-bottom: 0;">
            <h2 style="border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 12px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
                Peripheral Details
            </h2>
            <table class="device-info-table">
                <tr>
                    <td>Device Model</td>
                    <td>{device_info['model']}</td>
                </tr>
                <tr>
                    <td>Serial Number</td>
                    <td>{device_info['serial']}</td>
                </tr>
                <tr>
                    <td>Mount Point</td>
                    <td>{volume_info['mount_point']}</td>
                </tr>
                <tr>
                    <td>File System</td>
                    <td>{volume_info['file_system'] or 'N/A'}</td>
                </tr>
                <tr>
                    <td>Storage ID</td>
                    <td>{device_info['id']}</td>
                </tr>
            </table>
        </div>
        
        <div class="footer">
            <span>USB Speed Test &amp; Monitoring Utility</span>
            <span>Saved at: {report_path}</span>
        </div>
    </div>
</body>
</html>
"""
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return report_path

def generate_comparison_html_report(test_runs):
    """
    Generates a detailed, plain-white HTML comparison report for multiple speed test runs.
    Saves it to the platform-specific reports folder config.REPORTS_DIR.
    """
    if not test_runs:
        return None
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Locate fastest read, fastest write, and overall winner
    fastest_read = max(test_runs, key=lambda t: t["results"]["read_speed"])
    fastest_write = max(test_runs, key=lambda t: t["results"]["write_speed"])
    fastest_overall = max(test_runs, key=lambda t: t["results"]["read_speed"] + t["results"]["write_speed"])
    
    # Target directory from configuration
    report_dir = str(COMPARISONS_DIR)
        
    report_filename = f"compare_report_{file_timestamp}.html"
    report_path = os.path.join(report_dir, report_filename)
    
    # Build comparison table columns dynamically
    table_headers = "".join([f"<th>Run #{i+1}: {run['device']['model']}</th>" for i, run in enumerate(test_runs)])
    
    read_speeds_row = "".join([f"<td><strong>{run['results']['read_speed']} MB/s</strong></td>" for run in test_runs])
    write_speeds_row = "".join([f"<td><strong>{run['results']['write_speed']} MB/s</strong></td>" for run in test_runs])
    combined_speeds_row = "".join([f"<td>{round(run['results']['read_speed'] + run['results']['write_speed'], 2)} MB/s</td>" for run in test_runs])
    
    test_sizes_row = "".join([f"<td>{run['results']['test_size_mb']} MB</td>" for run in test_runs])
    read_dur_row = "".join([f"<td>{run['results']['read_duration']} s</td>" for run in test_runs])
    write_dur_row = "".join([f"<td>{run['results']['write_duration']} s</td>" for run in test_runs])
    
    mount_points_row = "".join([f"<td>{run['volume']['mount_point']}</td>" for run in test_runs])
    file_systems_row = "".join([f"<td>{run['volume']['file_system']}</td>" for run in test_runs])
    serials_row = "".join([f"<td>{run['device']['serial']}</td>" for run in test_runs])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USB Performance Comparison Report</title>
    <style>
        body {{
            background-color: #ffffff;
            color: #111111;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            line-height: 1.5;
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        h1 {{
            font-size: 28px;
            border-bottom: 2px solid #111111;
            padding-bottom: 10px;
            margin-bottom: 5px;
        }}
        
        .meta {{
            font-size: 14px;
            color: #666666;
            margin-bottom: 30px;
        }}
        
        .winner-panel {{
            border: 2px solid #111111;
            padding: 20px;
            margin-bottom: 30px;
            background-color: #f9f9f9;
        }}
        
        .winner-panel h2 {{
            margin-top: 0;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 8px;
        }}
        
        .winner-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }}
        
        .winner-box {{
            border-left: 3px solid #111111;
            padding-left: 15px;
        }}
        
        .winner-box h3 {{
            margin: 0 0 5px 0;
            font-size: 14px;
            color: #555555;
            text-transform: uppercase;
        }}
        
        .winner-name {{
            font-size: 16px;
            font-weight: bold;
        }}
        
        .winner-val {{
            font-size: 20px;
            font-weight: 800;
            margin-top: 5px;
        }}
        
        table.comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            margin-bottom: 40px;
        }}
        
        table.comparison-table th, table.comparison-table td {{
            border: 1px solid #dddddd;
            padding: 12px 15px;
            text-align: left;
        }}
        
        table.comparison-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        table.comparison-table tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        
        table.comparison-table tr.header-row th {{
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #111111;
        }}
        
        .footer {{
            border-top: 1px solid #cccccc;
            padding-top: 15px;
            font-size: 12px;
            color: #666666;
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
        }}
    </style>
</head>
<body>
    <h1>USB Performance Comparison Report</h1>
    <div class="meta">Generated on {timestamp} | Save Path: {report_path}</div>
    
    <div class="winner-panel">
        <h2>Performance Benchmarks Leaderboard</h2>
        <div class="winner-grid">
            <div class="winner-box">
                <h3>Fastest Read Speed</h3>
                <div class="winner-name">{fastest_read['device']['model']}</div>
                <div class="winner-val">{fastest_read['results']['read_speed']} MB/s</div>
            </div>
            
            <div class="winner-box">
                <h3>Fastest Write Speed</h3>
                <div class="winner-name">{fastest_write['device']['model']}</div>
                <div class="winner-val">{fastest_write['results']['write_speed']} MB/s</div>
            </div>
            
            <div class="winner-box">
                <h3>Overall Champion</h3>
                <div class="winner-name">{fastest_overall['device']['model']}</div>
                <div class="winner-val">{round(fastest_overall['results']['read_speed'] + fastest_overall['results']['write_speed'], 2)} MB/s</div>
            </div>
        </div>
    </div>
    
    <h2>Side-by-Side Comparison Metrics</h2>
    <table class="comparison-table">
        <thead>
            <tr class="header-row">
                <th>Metric / Parameter</th>
                {table_headers}
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Read Throughput Speed</strong></td>
                {read_speeds_row}
            </tr>
            <tr>
                <td><strong>Write Throughput Speed</strong></td>
                {write_speeds_row}
            </tr>
            <tr>
                <td><strong>Combined Speed (Total Bandwidth)</strong></td>
                {combined_speeds_row}
            </tr>
            <tr>
                <td>Benchmark Test File Size</td>
                {test_sizes_row}
            </tr>
            <tr>
                <td>Read Test Duration</td>
                {read_dur_row}
            </tr>
            <tr>
                <td>Write Test Duration</td>
                {write_dur_row}
            </tr>
            <tr>
                <td>Mount Point Drive</td>
                {mount_points_row}
            </tr>
            <tr>
                <td>File System Label</td>
                {file_systems_row}
            </tr>
            <tr>
                <td>Serial Number</td>
                {serials_row}
            </tr>
        </tbody>
    </table>
    
    <div class="footer">
        <span>USB Speed Test &amp; Monitoring Utility</span>
        <span>Saved at: {report_path}</span>
    </div>
</body>
</html>
"""
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return report_path
