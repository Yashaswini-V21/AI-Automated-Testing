"""
Yash AI Agent - Main Application Entry Point
Automated Website Testing Using Natural Language
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agent.workflow import TestAgentWorkflow
from agent.simple_parser import SimpleParser
from agent.code_generator import CodeGenerator
from agent.executor import TestExecutor
from agent.recording_manager import get_recording_manager
from agent.report_analyzer import get_report_analyzer
import json
from datetime import datetime
from fpdf import FPDF
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the AI agent workflow
agent_workflow = TestAgentWorkflow()

@app.route('/')
def index():
    """Serve the main landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the main dashboard"""
    return render_template('dashboard_modern.html')

@app.route('/api/test', methods=['POST'])
def run_test():
    """
    API endpoint to run tests based on natural language instructions
    """
    try:
        data = request.get_json()
        user_instruction = data.get('instruction', '')
        target_url = data.get('url', 'http://localhost:5000/test_site')
        browser_type = data.get('browser', 'chromium')
        headless = data.get('headless', True)
        
        # Extract URL from instruction if present
        import re
        url_match = re.search(r'(https?://[^\s,]+|(?:www\.)?[a-z0-9-]+\.(?:com|org|net|io)(?:/[^\s,]*)?)', user_instruction, re.IGNORECASE)
        if url_match:
            extracted_url = url_match.group(0)
            if not extracted_url.startswith('http'):
                extracted_url = 'https://' + extracted_url
            target_url = extracted_url
        
        print(f"\n[API] Received test request:")
        print(f"  - URL: {target_url}")
        print(f"  - Instruction: {user_instruction}")
        print(f"  - Browser: {browser_type}")
        print(f"  - Headless: {headless}")
        
        if not user_instruction:
            return jsonify({
                'success': False,
                'error': 'No instruction provided'
            }), 400
        
        # SIMPLE DIRECT EXECUTION - NO COMPLEX WORKFLOW
        print(f"[API] Parsing instruction...")
        parser = SimpleParser()
        actions = parser.parse(user_instruction)
        print(f"[API] Parsed {len(actions)} actions")
        
        print(f"[API] Generating code...")
        generator = CodeGenerator()
        code = generator.generate(actions, target_url, browser_type=browser_type, headless=headless)
        print(f"[API] Code generated")
        
        print(f"[API] Executing test...")
        executor = TestExecutor()
        execution = executor.execute(code)
        print(f"[API] Execution status: {execution.get('status')}")
        
        # Build result
        if execution.get('status') == 'success':
            results = execution.get('results', {})
            passed = results.get('passed', [])
            failed = results.get('failed', [])
            
            # Calculate totals based on actions
            total_steps = len(actions)
            passed_count = len(passed)
            failed_count = len(failed)
            
            # If no passed/failed recorded, assume all passed if no errors
            if passed_count == 0 and failed_count == 0 and total_steps > 0:
                passed_count = total_steps
            
            success_rate = (passed_count / max(total_steps, 1)) * 100
            
            print(f"[API] Results - Total: {total_steps}, Passed: {passed_count}, Failed: {failed_count}")
            
            result = {
                'success': True,
                'url': target_url,
                'browser': browser_type,
                'headless': headless,
                'actions': actions,
                'total_steps': total_steps,
                'passed': passed_count,
                'failed': failed_count,
                'success_rate': success_rate,
                'passed_tests': passed,
                'failed_tests': failed,
                'generated_code': code,
                'execution_status': 'completed',
                'screenshots': results.get('screenshots', [])
            }
        else:
            result = {
                'success': False,
                'error': execution.get('error', 'Unknown error'),
                'actions': actions,
                'total_steps': 0,
                'passed': 0,
                'failed': 0,
                'success_rate': 0
            }
        
        print(f"[API] Test completed: {result.get('success', False)}")
        
        # Save report
        report_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f'reports/report_{report_id}.json'
        os.makedirs('reports', exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return jsonify({
            'success': True,
            'data': result,
            'report_id': report_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports/<report_id>')
def get_report(report_id):
    """Get a specific test report"""
    try:
        report_path = f'reports/report_{report_id}.json'
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            return jsonify({
                'success': True,
                'data': report_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports')
def list_reports():
    """List all available test reports"""
    try:
        os.makedirs('reports', exist_ok=True)
        reports = []
        for filename in os.listdir('reports'):
            if filename.endswith('.json'):
                report_id = filename.replace('report_', '').replace('.json', '')
                reports.append({
                    'id': report_id,
                    'filename': filename
                })
        return jsonify({
            'success': True,
            'data': reports
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test_site')
def test_site():
    """Serve a sample test website"""
    return render_template('test_site.html')

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Generate PDF report from test results"""
    try:
        data = request.json
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, 'QA-Pilot Agent - Test Report', 0, 1, 'C')
        pdf.ln(5)
        
        # Timestamp
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Test Summary Box
        pdf.set_fill_color(240, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Test Summary', 0, 1, 'L', True)
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Total Steps:', 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, str(data.get('total_steps', 0)), 0, 1)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Passed:', 0, 0)
        pdf.set_text_color(0, 150, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, str(data.get('passed', 0)), 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Failed:', 0, 0)
        pdf.set_text_color(200, 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, str(data.get('failed', 0)), 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Success Rate:', 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, f"{data.get('success_rate', 0):.1f}%", 0, 1)
        pdf.ln(10)
        
        # Test Configuration
        if 'url' in data:
            pdf.set_fill_color(245, 245, 250)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Test Configuration', 0, 1, 'L', True)
            pdf.ln(2)
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(40, 6, 'URL:', 0, 0)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, str(data.get('url', 'N/A')), 0, 1)
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(40, 6, 'Browser:', 0, 0)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, str(data.get('browser', 'chromium')).upper(), 0, 1)
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(40, 6, 'Mode:', 0, 0)
            pdf.set_font('Arial', 'B', 10)
            mode = 'Headless' if data.get('headless', False) else 'Visible'
            pdf.cell(0, 6, mode, 0, 1)
            pdf.ln(8)
        
        # Test Steps
        if data.get('actions'):
            pdf.set_fill_color(240, 250, 240)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Planned Test Steps', 0, 1, 'L', True)
            pdf.ln(2)
            
            for idx, action in enumerate(data['actions'], 1):
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f"Step {idx}: {action.get('type', '').upper()}", 0, 1)
                pdf.set_font('Arial', '', 9)
                pdf.multi_cell(0, 5, f"  {action.get('description', 'N/A')}")
                pdf.ln(2)
        
        # Passed Tests
        if data.get('passed_tests'):
            pdf.ln(5)
            pdf.set_fill_color(230, 255, 230)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(0, 120, 0)
            pdf.cell(0, 8, 'Passed Tests', 0, 1, 'L', True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            
            for test in data['passed_tests']:
                pdf.set_font('Arial', 'B', 10)
                pdf.set_text_color(0, 150, 0)
                pdf.cell(0, 6, f"Step {test.get('step', 'N/A')}: {test.get('action', 'N/A')}", 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 9)
                pdf.multi_cell(0, 5, f"  {test.get('description', 'Completed successfully')}")
                pdf.ln(2)
        
        # Failed Tests
        if data.get('failed_tests'):
            pdf.ln(5)
            pdf.set_fill_color(255, 230, 230)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 8, 'Failed Tests', 0, 1, 'L', True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            
            for test in data['failed_tests']:
                pdf.set_font('Arial', 'B', 10)
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 6, f"Step {test.get('step', 'N/A')}: {test.get('action', 'N/A')}", 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 9)
                pdf.multi_cell(0, 5, f"  {test.get('description', 'Failed')}")
                if test.get('error'):
                    pdf.set_text_color(150, 0, 0)
                    pdf.multi_cell(0, 5, f"  Error: {test['error']}")
                    pdf.set_text_color(0, 0, 0)
                pdf.ln(2)
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, 'Generated by Yash AI Agent - Automated Testing Platform', 0, 1, 'C')
        
        # Output PDF
        pdf_output = io.BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_report_{timestamp}.pdf"
        
        return send_file(
            pdf_output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# API ENDPOINTS FOR RECORDINGS AND ANALYZER
# ============================================================================

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all recordings"""
    try:
        manager = get_recording_manager()
        recordings = manager.list_recordings()
        return jsonify({
            'success': True,
            'data': recordings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recordings/<recording_id>', methods=['GET'])
def get_recording(recording_id):
    """Get specific recording"""
    try:
        manager = get_recording_manager()
        recording = manager.get_recording(recording_id)
        
        if recording:
            return jsonify({
                'success': True,
                'data': recording
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Recording not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recordings/<recording_id>/download', methods=['GET'])
def download_recording(recording_id):
    """Download recording as JSON"""
    try:
        manager = get_recording_manager()
        recording = manager.get_recording(recording_id)
        
        if not recording:
            return jsonify({
                'success': False,
                'error': 'Recording not found'
            }), 404
        
        # Create JSON file
        json_data = json.dumps(recording, indent=2)
        json_bytes = io.BytesIO(json_data.encode('utf-8'))
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=f"{recording_id}.json"
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recordings/<recording_id>', methods=['DELETE'])
def delete_recording(recording_id):
    """Delete a recording"""
    try:
        manager = get_recording_manager()
        success = manager.delete_recording(recording_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Recording deleted'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Recording not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyzer/generate', methods=['POST'])
def generate_analysis_report():
    """Generate comprehensive analysis report"""
    try:
        data = request.get_json()
        include_recording = data.get('include_recording', False)
        
        # Prepare test data
        test_data = {
            'url': data.get('url'),
            'instruction': data.get('instruction'),
            'stats': data.get('stats', {}),
            'steps': data.get('steps', []),
            'screenshots': data.get('screenshots', []),
            'recording_id': data.get('recording_id'),
            'recording_duration': data.get('recording_duration'),
            'event_count': data.get('event_count'),
            'recording_status': data.get('recording_status')
        }
        
        analyzer = get_report_analyzer()
        report_paths = analyzer.generate_comprehensive_report(test_data, include_recording)
        
        return jsonify({
            'success': True,
            'data': report_paths
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyzer/reports', methods=['GET'])
def list_analysis_reports():
    """List all generated reports"""
    try:
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.startswith('report_'):
                filepath = os.path.join(reports_dir, filename)
                stat = os.stat(filepath)
                
                report_id = filename.split('.')[0]
                file_ext = filename.split('.')[-1]
                
                reports.append({
                    'report_id': report_id,
                    'filename': filename,
                    'format': file_ext,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        # Group by report_id
        grouped = {}
        for report in reports:
            rid = report['report_id']
            if rid not in grouped:
                grouped[rid] = {
                    'report_id': rid,
                    'created': report['created'],
                    'formats': {}
                }
            grouped[rid]['formats'][report['format']] = {
                'filename': report['filename'],
                'size': report['size']
            }
        
        return jsonify({
            'success': True,
            'data': list(grouped.values())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyzer/download/<report_id>/<format>', methods=['GET'])
def download_analysis_report(report_id, format):
    """Download specific report format"""
    try:
        filename = f"{report_id}.{format}"
        filepath = os.path.join('reports', filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        mimetype_map = {
            'pdf': 'application/pdf',
            'html': 'text/html',
            'json': 'application/json'
        }
        
        return send_file(
            filepath,
            mimetype=mimetype_map.get(format, 'application/octet-stream'),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('reports', exist_ok=True)
    os.makedirs('recordings', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/screenshots', exist_ok=True)
    
    print("[*] QA-Pilot Agent Starting...")
    print("[*] Access the application at: http://localhost:5000")
    print("[*] Sample test site available at: http://localhost:5000/test_site")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
