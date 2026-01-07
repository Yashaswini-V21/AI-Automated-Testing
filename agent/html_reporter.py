"""
HTML Report Generator Module
Generates professional HTML reports with charts and statistics
"""

from typing import Dict, List
from datetime import datetime
import os


def generate_html_report(test_results: List[Dict], statistics: Dict, 
                         output_path: str = 'test_report.html'):
    """
    Generate an HTML test report with charts and statistics
    
    Args:
        test_results: List of test result dictionaries
        statistics: Statistics dictionary from TestReporter
        output_path: Path where the HTML report will be saved
    """
    
    # Calculate data for charts
    passed = statistics['passed']
    failed = statistics['failed']
    skipped = statistics['skipped']
    
    # Generate test rows HTML
    test_rows = ""
    for idx, result in enumerate(test_results, 1):
        status_class = result['status']
        status_icon = {
            'pass': '✓',
            'fail': '✗',
            'skip': '○'
        }.get(status_class, '?')
        
        error_msg = result.get('error_message', '-') or '-'
        if len(error_msg) > 100:
            error_msg = error_msg[:97] + '...'
            
        test_rows += f"""
        <tr class="{status_class}">
            <td>{idx}</td>
            <td>{result['test_name']}</td>
            <td><span class="status-badge {status_class}">{status_icon} {result['status'].upper()}</span></td>
            <td>{result['execution_time']:.2f}s</td>
            <td class="error-cell">{error_msg}</td>
        </tr>
        """
    
    # Generate error counts HTML
    error_rows = ""
    if statistics['error_counts']:
        for error_type, count in sorted(statistics['error_counts'].items(), 
                                       key=lambda x: x[1], reverse=True):
            error_rows += f"""
            <tr>
                <td>{error_type}</td>
                <td>{count}</td>
            </tr>
            """
    else:
        error_rows = "<tr><td colspan='2'>No errors recorded</td></tr>"
    
    # HTML template with inline CSS and Chart.js
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.95em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .summary-card .label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .summary-card.total .value {{ color: #667eea; }}
        .summary-card.passed .value {{ color: #10b981; }}
        .summary-card.failed .value {{ color: #ef4444; }}
        .summary-card.skipped .value {{ color: #f59e0b; }}
        .summary-card.time .value {{ color: #8b5cf6; font-size: 2em; }}
        
        .charts-section {{
            padding: 40px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .chart-container h2 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
        }}
        
        .table-section {{
            padding: 40px;
        }}
        
        .table-section h2 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.5em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: #667eea;
            color: white;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
        }}
        
        tbody tr {{
            border-bottom: 1px solid #e5e7eb;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .status-badge.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-badge.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .status-badge.skip {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .error-cell {{
            max-width: 300px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .charts-section {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Execution Report</h1>
            <p class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <div class="label">Total Tests</div>
                <div class="value">{statistics['total_tests']}</div>
            </div>
            <div class="summary-card passed">
                <div class="label">Passed</div>
                <div class="value">{passed}</div>
                <div class="label">{statistics['pass_rate']:.1f}%</div>
            </div>
            <div class="summary-card failed">
                <div class="label">Failed</div>
                <div class="value">{failed}</div>
                <div class="label">{statistics['fail_rate']:.1f}%</div>
            </div>
            <div class="summary-card skipped">
                <div class="label">Skipped</div>
                <div class="value">{skipped}</div>
                <div class="label">{statistics['skip_rate']:.1f}%</div>
            </div>
            <div class="summary-card time">
                <div class="label">Total Time</div>
                <div class="value">{statistics['total_execution_time']:.1f}s</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h2>📊 Test Results Distribution</h2>
                <canvas id="resultsChart"></canvas>
            </div>
            <div class="chart-container">
                <h2>📈 Success Rate</h2>
                <canvas id="successChart"></canvas>
            </div>
        </div>
        
        <div class="table-section">
            <h2>📋 Detailed Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Time</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
                    {test_rows}
                </tbody>
            </table>
        </div>
        
        <div class="table-section">
            <h2>🐛 Error Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Error Type</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
                    {error_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Report generated by Yash AI Testing Agent</p>
        </div>
    </div>
    
    <script>
        // Results Distribution Chart
        const resultsCtx = document.getElementById('resultsChart').getContext('2d');
        new Chart(resultsCtx, {{
            type: 'bar',
            data: {{
                labels: ['Passed', 'Failed', 'Skipped'],
                datasets: [{{
                    label: 'Number of Tests',
                    data: [{passed}, {failed}, {skipped}],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: [
                        'rgb(16, 185, 129)',
                        'rgb(239, 68, 68)',
                        'rgb(245, 158, 11)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Success Rate Chart
        const successCtx = document.getElementById('successChart').getContext('2d');
        new Chart(successCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Passed', 'Failed', 'Skipped'],
                datasets: [{{
                    data: [{passed}, {failed}, {skipped}],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: 'white',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    
    # Save the report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return os.path.abspath(output_path)
