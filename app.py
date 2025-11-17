from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
from smart_test_engine import SmartTestEngine
from test_executor import TestExecutor
from recording_manager import RecordingManager
from smart_api_engine import SmartApiEngine
from api_test_executor import ApiTestExecutor
from report_history import add_entry as log_history_entry, get_history as get_history_entries

app = Flask(__name__)
CORS(app)
recording_manager = RecordingManager()

# Configuration
app.config['UPLOAD_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs('reports', exist_ok=True)
os.makedirs('screenshots', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/generate-tests', methods=['POST'])
def generate_tests():
    """API endpoint to generate test cases"""
    engine = None
    try:
        data = request.json
        website_url = data.get('website_url', '').strip()
        login_id = data.get('login_id', '').strip()
        password = data.get('password', '').strip()
        headed = bool(data.get('headed', True))
        
        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        # Initialize test engine
        engine = SmartTestEngine(website_url, login_id, password, headed=headed)
        
        # Generate all test cases
        result = engine.generate_all_tests()
        
        # Save report
        report_file = engine.save_report()
        
        response_payload = {
            'success': True,
            'test_cases': result,
            'report_file': report_file,
            'summary': {
                'total_tests': sum(len(tests) for tests in result.values()),
                'positive': len(result.get('positive', [])),
                'negative': len(result.get('negative', [])),
                'ui': len(result.get('ui', [])),
                'functional': len(result.get('functional', []))
            }
        }
        log_history_entry({
            'type': 'ui_generation',
            'website_url': website_url,
            'summary': response_payload['summary'],
            'report_file': report_file
        })
        return jsonify(response_payload)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if engine:
            engine.close()

@app.route('/api/analyze-website', methods=['POST'])
def analyze_website():
    """API endpoint to analyze website structure"""
    engine = None
    try:
        data = request.json
        website_url = data.get('website_url', '').strip()
        
        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        engine = SmartTestEngine(website_url, '', '', headed=True)
        engine.initialize_driver()
        elements = engine.analyze_website()
        
        return jsonify({
            'success': True,
            'elements': elements
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if engine:
            engine.close()

@app.route('/api/test-login', methods=['POST'])
def test_login():
    """API endpoint to test login functionality"""
    engine = None
    try:
        data = request.json
        website_url = data.get('website_url', '').strip()
        login_id = data.get('login_id', '').strip()
        password = data.get('password', '').strip()
        headed = bool(data.get('headed', True))
        
        if not all([website_url, login_id, password]):
            return jsonify({'error': 'Website URL, Login ID, and Password are required'}), 400
        
        engine = SmartTestEngine(website_url, login_id, password, headed=headed)
        engine.initialize_driver()
        engine.analyze_website()
        login_result = engine.perform_login()
        
        return jsonify({
            'success': login_result,
            'message': 'Login successful' if login_result else 'Login failed'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if engine:
            engine.close()

@app.route('/api/download-report/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated test report"""
    try:
        report_path = os.path.join('reports', filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-tests', methods=['POST'])
def execute_tests():
    """API endpoint to execute test cases"""
    executor = None
    try:
        data = request.json
        website_url = data.get('website_url', '').strip()
        login_id = data.get('login_id', '').strip()
        password = data.get('password', '').strip()
        headed = bool(data.get('headed', True))
        test_cases = data.get('test_cases', {})
        
        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        if not test_cases:
            return jsonify({'error': 'Test cases are required'}), 400
        
        # Initialize test executor
        executor = TestExecutor(website_url, login_id, password, headed=headed)
        
        # Execute all tests
        execution_results = executor.execute_all_tests(test_cases)
        
        # Save execution reports (JSON + Excel/CSV)
        report_file = executor.save_execution_report(website_url)
        excel_report_file = executor.save_execution_report_excel(website_url)
        
        response_payload = {
            'success': True,
            'results': execution_results['results'],
            'summary': execution_results['summary'],
            'report_file': report_file,
            'excel_report_file': excel_report_file
        }
        log_history_entry({
            'type': 'ui_execution',
            'website_url': website_url,
            'summary': execution_results['summary'],
            'report_file': report_file,
            'excel_report_file': excel_report_file
        })
        return jsonify(response_payload)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if executor:
            executor.close()

@app.route('/api/generate-and-execute', methods=['POST'])
def generate_and_execute():
    """API endpoint to generate and execute test cases"""
    engine = None
    executor = None
    try:
        data = request.json
        website_url = data.get('website_url', '').strip()
        login_id = data.get('login_id', '').strip()
        password = data.get('password', '').strip()
        headed = bool(data.get('headed', True))
        
        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        # Step 1: Generate test cases
        engine = SmartTestEngine(website_url, login_id, password, headed=headed)
        test_cases = engine.generate_all_tests()
        generation_report = engine.save_report()
        generation_summary = {
            'total_tests': sum(len(tests) for tests in test_cases.values()),
            'positive': len(test_cases.get('positive', [])),
            'negative': len(test_cases.get('negative', [])),
            'ui': len(test_cases.get('ui', [])),
            'functional': len(test_cases.get('functional', []))
        }
        log_history_entry({
            'type': 'ui_generation',
            'website_url': website_url,
            'summary': generation_summary,
            'report_file': generation_report
        })
        engine.close()
        engine = None
        
        # Step 2: Execute test cases
        executor = TestExecutor(website_url, login_id, password, headed=headed)
        execution_results = executor.execute_all_tests(test_cases)
        execution_report = executor.save_execution_report(website_url)
        execution_excel_report = executor.save_execution_report_excel(website_url)
        log_history_entry({
            'type': 'ui_execution',
            'website_url': website_url,
            'summary': execution_results['summary'],
            'report_file': execution_report,
            'excel_report_file': execution_excel_report
        })
        executor.close()
        executor = None
        
        return jsonify({
            'success': True,
            'test_cases': test_cases,
            'execution_results': execution_results['results'],
            'summary': {
                'generation': generation_summary,
                'execution': execution_results['summary']
            },
            'reports': {
                'generation_report': generation_report,
                'execution_report': execution_report,
                'execution_excel_report': execution_excel_report
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if engine:
            engine.close()
        if executor:
            executor.close()

@app.route('/api/api-tests/generate', methods=['POST'])
def generate_api_tests():
    """Generate API tests from an OpenAPI specification."""
    try:
        data = request.json or {}
        base_url = data.get('base_url', '').strip()
        spec_source = data.get('spec', '').strip()

        if not base_url or not spec_source:
            return jsonify({'error': 'API Base URL and OpenAPI spec are required'}), 400

        engine = SmartApiEngine(base_url, spec_source)
        test_cases = engine.generate_tests()
        report_file = engine.save_report()

        response_payload = {
            'success': True,
            'test_cases': test_cases,
            'summary': engine.get_summary(),
            'report_file': report_file
        }
        log_history_entry({
            'type': 'api_generation',
            'website_url': base_url,
            'summary': response_payload['summary'],
            'report_file': report_file
        })
        return jsonify(response_payload)
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/api-tests/execute', methods=['POST'])
def execute_api_tests():
    """Execute generated API test cases."""
    try:
        data = request.json or {}
        base_url = data.get('base_url', '').strip()
        test_cases = data.get('test_cases', [])

        if not base_url:
            return jsonify({'error': 'API Base URL is required'}), 400
        if not test_cases:
            return jsonify({'error': 'API test cases are required'}), 400

        executor = ApiTestExecutor(base_url)
        execution_results = executor.execute_tests(test_cases)
        report_file = executor.save_execution_report()

        response_payload = {
            'success': True,
            'results': execution_results,
            'report_file': report_file
        }
        log_history_entry({
            'type': 'api_execution',
            'website_url': base_url,
            'summary': execution_results['summary'],
            'report_file': report_file
        })
        return jsonify(response_payload)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-history', methods=['GET'])
def get_run_history():
    """Return recent generation/execution activity."""
    try:
        history = get_history_entries()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start a manual recording session."""
    try:
        data = request.json or {}
        website_url = data.get('website_url', '').strip()

        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400

        status = recording_manager.start_session(website_url)
        return jsonify({
            'success': True,
            'recording': status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop the current recording session."""
    if not recording_manager.is_active():
        return jsonify({'error': 'No active recording session'}), 400

    try:
        result = recording_manager.stop_session()
        return jsonify({
            'success': True,
            'recording': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recording/status', methods=['GET'])
def recording_status():
    """Return current recording status."""
    try:
        status = recording_manager.get_status()
        return jsonify({
            'success': True,
            'recording': status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
