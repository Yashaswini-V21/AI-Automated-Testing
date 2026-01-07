"""
Report Analyzer Module
Generates comprehensive downloadable reports in multiple formats
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from fpdf import FPDF
import base64


class ReportAnalyzer:
    """Generates and manages test reports in multiple formats"""
    
    def __init__(self, reports_dir: str = 'reports'):
        """Initialize report analyzer"""
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)
    
    def generate_comprehensive_report(self, test_data: Dict, 
                                     include_recording: bool = False) -> Dict:
        """
        Generate comprehensive report in all formats
        
        Args:
            test_data: Test execution data
            include_recording: Whether to include recording data
            
        Returns:
            Dictionary with paths to generated reports
        """
        report_id = f"report_{int(datetime.now().timestamp())}"
        
        # Generate all formats
        pdf_path = self.generate_pdf_report(test_data, report_id, include_recording)
        html_path = self.generate_html_report(test_data, report_id, include_recording)
        json_path = self.generate_json_report(test_data, report_id, include_recording)
        
        return {
            'report_id': report_id,
            'pdf': pdf_path,
            'html': html_path,
            'json': json_path,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_pdf_report(self, test_data: Dict, report_id: str, 
                           include_recording: bool = False) -> str:
        """Generate PDF report"""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 24)
        pdf.set_text_color(67, 97, 238)
        pdf.cell(0, 15, 'Test Execution Report', 0, 1, 'C')
        pdf.ln(5)
        
        # Timestamp
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Summary Box
        pdf.set_fill_color(245, 247, 250)
        pdf.rect(10, pdf.get_y(), 190, 50, 'F')
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, 'Test Summary', 0, 1, 'L')
        pdf.ln(2)
        
        # Test details
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 7, f"Test URL:", 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, test_data.get('url', 'N/A'), 0, 1)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 7, f"Instruction:", 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, test_data.get('instruction', 'N/A'))
        
        pdf.ln(5)
        
        # Statistics
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Statistics:', 0, 1)
        
        stats = test_data.get('stats', {})
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 7, 'Total Steps:', 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, str(stats.get('total_steps', 0)), 0, 1)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 7, 'Passed:', 0, 0)
        pdf.set_text_color(0, 150, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, str(stats.get('passed', 0)), 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 7, 'Failed:', 0, 0)
        pdf.set_text_color(200, 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, str(stats.get('failed', 0)), 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 7, 'Execution Time:', 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, f"{stats.get('execution_time', 0):.2f}s", 0, 1)
        
        pdf.ln(10)
        
        # Test Steps
        if 'steps' in test_data and test_data['steps']:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Test Steps:', 0, 1)
            
            for i, step in enumerate(test_data['steps'], 1):
                status = step.get('status', 'unknown')
                if status == 'passed':
                    pdf.set_text_color(0, 150, 0)
                    symbol = '[PASS]'
                else:
                    pdf.set_text_color(200, 0, 0)
                    symbol = '[FAIL]'
                
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f"{i}. {symbol} {step.get('description', 'N/A')}", 0, 1)
                pdf.set_text_color(0, 0, 0)
        
        # Screenshots section
        if include_recording and 'screenshots' in test_data:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Screenshots', 0, 1)
            pdf.ln(5)
            
            for i, screenshot in enumerate(test_data['screenshots'][:5], 1):
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 7, f"Screenshot {i}: {screenshot.get('description', '')}", 0, 1)
                pdf.ln(3)
        
        # Recording info
        if include_recording and test_data.get('recording_id'):
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Recording Information', 0, 1)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 11)
            pdf.cell(0, 7, f"Recording ID: {test_data['recording_id']}", 0, 1)
            pdf.cell(0, 7, f"Duration: {test_data.get('recording_duration', 0):.2f}s", 0, 1)
        
        # Save PDF
        filename = f"{report_id}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        pdf.output(filepath)
        
        return filepath
    
    def generate_html_report(self, test_data: Dict, report_id: str,
                            include_recording: bool = False) -> str:
        """Generate HTML report with detailed visualization"""
        
        stats = test_data.get('stats', {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {report_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
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
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
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
        }}
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .summary-card.total .value {{ color: #667eea; }}
        .summary-card.passed .value {{ color: #10b981; }}
        .summary-card.failed .value {{ color: #ef4444; }}
        .content-section {{
            padding: 40px;
        }}
        .content-section h2 {{
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .test-step {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .test-step.passed {{ border-left-color: #10b981; }}
        .test-step.failed {{ border-left-color: #ef4444; }}
        .screenshot-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .screenshot-item {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }}
        .screenshot-item img {{
            width: 100%;
            border-radius: 4px;
            margin-bottom: 10px;
        }}
        .recording-section {{
            background: #e7f5ff;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Execution Report</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            <p>Report ID: {report_id}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <div class="label">Total Steps</div>
                <div class="value">{stats.get('total_steps', 0)}</div>
            </div>
            <div class="summary-card passed">
                <div class="label">Passed</div>
                <div class="value">{stats.get('passed', 0)}</div>
            </div>
            <div class="summary-card failed">
                <div class="label">Failed</div>
                <div class="value">{stats.get('failed', 0)}</div>
            </div>
            <div class="summary-card">
                <div class="label">Execution Time</div>
                <div class="value">{stats.get('execution_time', 0):.2f}s</div>
            </div>
        </div>
        
        <div class="content-section">
            <h2>📋 Test Details</h2>
            <p><strong>URL:</strong> {test_data.get('url', 'N/A')}</p>
            <p><strong>Instruction:</strong> {test_data.get('instruction', 'N/A')}</p>
        </div>
        
        <div class="content-section">
            <h2>🔍 Test Steps</h2>
"""
        
        # Add test steps
        if 'steps' in test_data:
            for i, step in enumerate(test_data['steps'], 1):
                status = step.get('status', 'unknown')
                html_content += f"""
            <div class="test-step {status}">
                <strong>Step {i}:</strong> {step.get('description', 'N/A')}
                <br><small>Status: {status.upper()}</small>
            </div>
"""
        
        # Add screenshots if included
        if include_recording and 'screenshots' in test_data and test_data['screenshots']:
            html_content += """
        </div>
        <div class="content-section">
            <h2>📸 Screenshots</h2>
            <div class="screenshot-gallery">
"""
            for i, screenshot in enumerate(test_data['screenshots'], 1):
                if screenshot.get('data'):
                    html_content += f"""
                <div class="screenshot-item">
                    <img src="data:image/png;base64,{screenshot['data'][:100]}..." alt="Screenshot {i}">
                    <p><small>{screenshot.get('description', f'Screenshot {i}')}</small></p>
                </div>
"""
            html_content += """
            </div>
"""
        
        # Add recording info
        if include_recording and test_data.get('recording_id'):
            html_content += f"""
        </div>
        <div class="content-section">
            <h2>🎬 Recording</h2>
            <div class="recording-section">
                <p><strong>Recording ID:</strong> {test_data['recording_id']}</p>
                <p><strong>Duration:</strong> {test_data.get('recording_duration', 0):.2f}s</p>
                <p><strong>Events Captured:</strong> {test_data.get('event_count', 0)}</p>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML
        filename = f"{report_id}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_json_report(self, test_data: Dict, report_id: str,
                            include_recording: bool = False) -> str:
        """Generate JSON report"""
        
        report_data = {
            'report_id': report_id,
            'timestamp': datetime.now().isoformat(),
            'test_url': test_data.get('url'),
            'instruction': test_data.get('instruction'),
            'statistics': test_data.get('stats', {}),
            'steps': test_data.get('steps', []),
            'screenshots': [],
            'recording': None
        }
        
        # Add screenshots (with limited data for size)
        if include_recording and 'screenshots' in test_data:
            for screenshot in test_data['screenshots']:
                report_data['screenshots'].append({
                    'id': screenshot.get('id'),
                    'timestamp': screenshot.get('timestamp'),
                    'description': screenshot.get('description'),
                    'data_available': bool(screenshot.get('data'))
                })
        
        # Add recording info
        if include_recording and test_data.get('recording_id'):
            report_data['recording'] = {
                'id': test_data['recording_id'],
                'duration': test_data.get('recording_duration'),
                'event_count': test_data.get('event_count'),
                'status': test_data.get('recording_status')
            }
        
        # Save JSON
        filename = f"{report_id}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filepath


# Singleton instance
_analyzer = None

def get_report_analyzer() -> ReportAnalyzer:
    """Get singleton report analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ReportAnalyzer()
    return _analyzer
