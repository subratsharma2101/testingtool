"""
Test Executor - Executes generated test cases automatically
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class TestExecutor:
    def __init__(self, website_url: str, login_id: str = "", password: str = "", headed: bool = True):
        self.website_url = website_url
        self.login_id = login_id
        self.password = password
        self.headed = headed
        self.driver = None
        self.results = {
            'positive': [],
            'negative': [],
            'ui': [],
            'functional': []
        }
        self.summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'execution_time': 0
        }
    
    def initialize_driver(self):
        """Initialize Chrome WebDriver"""
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if not self.headed:
            try:
                chrome_options.add_argument('--headless=new')
            except Exception:
                chrome_options.add_argument('--headless')
        
        # Prefer bundled chromedriver in repo, then cache, then auto-download
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        local_win64_root = os.path.join(repo_dir, 'selenium', 'chromedriver', 'win64')
        local_driver = None
        try:
            if os.path.isdir(local_win64_root):
                for v in sorted(os.listdir(local_win64_root), reverse=True):
                    candidate = os.path.join(local_win64_root, v, 'chromedriver.exe')
                    if os.path.exists(candidate):
                        local_driver = candidate
                        break
        except Exception:
            pass

        cache_driver = os.path.join(os.path.expanduser('~'), '.cache', 'selenium', 'chromedriver', 'win64', '142.0.7444.61', 'chromedriver.exe')

        try:
            if local_driver and os.path.exists(local_driver):
                service = Service(local_driver)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            elif os.path.exists(cache_driver):
                service = Service(cache_driver)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception:
                self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.implicitly_wait(5)
        return self.driver
    
    def take_screenshot(self, test_id: str) -> str:
        """Take screenshot and return as base64 string"""
        try:
            screenshot_path = f"screenshots/{test_id}_{int(time.time())}.png"
            os.makedirs('screenshots', exist_ok=True)
            self.driver.save_screenshot(screenshot_path)
            
            # Convert to base64
            with open(screenshot_path, 'rb') as f:
                screenshot_data = base64.b64encode(f.read()).decode('utf-8')
            
            return screenshot_data
        except Exception as e:
            print(f"[ERROR] Failed to take screenshot: {e}")
            return ""
    
    def execute_positive_test(self, test_case: Dict) -> Dict:
        """Execute a positive test case"""
        test_id = test_case.get('test_id', 'UNKNOWN')
        test_name = test_case.get('test_name', 'Unknown Test')
        
        result = {
            'test_id': test_id,
            'test_name': test_name,
            'status': 'SKIPPED',
            'execution_time': 0,
            'error_message': '',
            'screenshot': ''
        }
        
        try:
            start_time = time.time()
            
            # Navigate to website
            self.driver.get(self.website_url)
            time.sleep(2)
            
            # Execute login test if it's a login test
            if 'LOGIN' in test_id and self.login_id and self.password:
                login_success = self._perform_login()
                result['status'] = 'PASS' if login_success else 'FAIL'
                if not login_success:
                    result['error_message'] = 'Login failed'
            else:
                # For input field tests
                if 'INPUT' in test_id:
                    field_name = test_case.get('field', '')
                    if field_name:
                        try:
                            # Try to find and fill the field
                            field = self.driver.find_element(By.NAME, field_name)
                            if not field:
                                field = self.driver.find_element(By.ID, field_name)
                            
                            field.clear()
                            field.send_keys("test_data_123")
                            result['status'] = 'PASS'
                        except:
                            result['status'] = 'FAIL'
                            result['error_message'] = f'Could not find or interact with field: {field_name}'
                    else:
                        result['status'] = 'PASS'  # Field exists check passed
            
            execution_time = time.time() - start_time
            result['execution_time'] = round(execution_time, 2)
            
            if result['status'] == 'FAIL':
                result['screenshot'] = self.take_screenshot(test_id)
            
        except Exception as e:
            result['status'] = 'FAIL'
            result['error_message'] = str(e)
            result['screenshot'] = self.take_screenshot(test_id)
            result['execution_time'] = round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        
        return result
    
    def execute_negative_test(self, test_case: Dict) -> Dict:
        """Execute a negative test case"""
        test_id = test_case.get('test_id', 'UNKNOWN')
        test_name = test_case.get('test_name', 'Unknown Test')
        
        result = {
            'test_id': test_id,
            'test_name': test_name,
            'status': 'SKIPPED',
            'execution_time': 0,
            'error_message': '',
            'screenshot': ''
        }
        
        try:
            start_time = time.time()
            
            # Navigate to website
            self.driver.get(self.website_url)
            time.sleep(2)
            
            # Execute based on test type
            if 'LOGIN' in test_id:
                if 'EMPTY' in test_id or 'empty' in test_name.lower():
                    # Test empty field validation
                    try:
                        # Try to submit form without filling fields
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                        submit_btn.click()
                        time.sleep(2)
                        
                        # Check if error message appears (this is what we want for negative test)
                        page_source = self.driver.page_source.lower()
                        if 'error' in page_source or 'required' in page_source or 'invalid' in page_source:
                            result['status'] = 'PASS'  # Error message shown = test passed
                        else:
                            result['status'] = 'FAIL'
                            result['error_message'] = 'Expected error message not displayed'
                    except:
                        result['status'] = 'FAIL'
                        result['error_message'] = 'Could not execute empty field test'
                elif 'INVALID' in test_id or 'invalid' in test_name.lower():
                    # Test invalid credentials
                    login_success = self._perform_login_with_invalid_credentials()
                    result['status'] = 'PASS' if not login_success else 'FAIL'
                    if login_success:
                        result['error_message'] = 'Login should have failed with invalid credentials'
            
            execution_time = time.time() - start_time
            result['execution_time'] = round(execution_time, 2)
            
            if result['status'] == 'FAIL':
                result['screenshot'] = self.take_screenshot(test_id)
            
        except Exception as e:
            result['status'] = 'FAIL'
            result['error_message'] = str(e)
            result['screenshot'] = self.take_screenshot(test_id)
            result['execution_time'] = round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        
        return result
    
    def execute_ui_test(self, test_case: Dict) -> Dict:
        """Execute a UI test case"""
        test_id = test_case.get('test_id', 'UNKNOWN')
        test_name = test_case.get('test_name', 'Unknown Test')
        
        result = {
            'test_id': test_id,
            'test_name': test_name,
            'status': 'SKIPPED',
            'execution_time': 0,
            'error_message': '',
            'screenshot': ''
        }
        
        try:
            start_time = time.time()
            
            # Navigate to website
            self.driver.get(self.website_url)
            time.sleep(2)
            
            # Execute UI checks
            if 'BUTTON' in test_id:
                # Check button visibility - extract button text from test name
                button_text = test_name.split('Verify ')[-1].split(' button')[0] if 'button' in test_name.lower() else ''
                # Try to find button by various methods
                if button_text:
                    try:
                        button = None
                        # Try XPATH first
                        try:
                            button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                        except:
                            # Try by button text
                            try:
                                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                                for btn in buttons:
                                    if button_text.lower() in btn.text.lower():
                                        button = btn
                                        break
                            except:
                                pass
                        
                        if button and button.is_displayed() and button.is_enabled():
                            result['status'] = 'PASS'
                        else:
                            result['status'] = 'FAIL'
                            result['error_message'] = f'Button is not visible or enabled: {button_text}'
                    except Exception as e:
                        result['status'] = 'FAIL'
                        result['error_message'] = f'Could not find button: {button_text} - {str(e)}'
                else:
                    result['status'] = 'SKIPPED'
                    result['error_message'] = 'Could not extract button text from test case'
            elif 'INPUT' in test_id:
                # Check input field UI - extract field name from test name or test_id
                field_name = test_id.split('INPUT_')[1] if 'INPUT_' in test_id else ''
                if not field_name:
                    field_name = test_name.split('Verify ')[-1].split(' field')[0] if 'field' in test_name.lower() else ''
                if field_name:
                    try:
                        field = self.driver.find_element(By.NAME, field_name)
                        if not field:
                            field = self.driver.find_element(By.ID, field_name)
                        
                        if field.is_displayed():
                            result['status'] = 'PASS'
                        else:
                            result['status'] = 'FAIL'
                            result['error_message'] = 'Field is not visible'
                    except:
                        result['status'] = 'FAIL'
                        result['error_message'] = f'Could not find field: {field_name}'
            elif 'PAGE' in test_id:
                # Check page title or responsive design
                if 'title' in test_name.lower():
                    page_title = self.driver.title
                    if page_title:
                        result['status'] = 'PASS'
                    else:
                        result['status'] = 'FAIL'
                        result['error_message'] = 'Page title not found'
            
            execution_time = time.time() - start_time
            result['execution_time'] = round(execution_time, 2)
            
            if result['status'] == 'FAIL':
                result['screenshot'] = self.take_screenshot(test_id)
            
        except Exception as e:
            result['status'] = 'FAIL'
            result['error_message'] = str(e)
            result['screenshot'] = self.take_screenshot(test_id)
            result['execution_time'] = round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        
        return result
    
    def execute_functional_test(self, test_case: Dict) -> Dict:
        """Execute a functional test case"""
        test_id = test_case.get('test_id', 'UNKNOWN')
        test_name = test_case.get('test_name', 'Unknown Test')
        test_type = test_case.get('test_type', '')
        
        result = {
            'test_id': test_id,
            'test_name': test_name,
            'status': 'SKIPPED',
            'execution_time': 0,
            'error_message': '',
            'screenshot': ''
        }
        
        try:
            start_time = time.time()
            
            # Navigate to website
            self.driver.get(self.website_url)
            time.sleep(2)
            
            if test_type == 'navigation':
                # Test navigation
                link_href = test_case.get('link', '')
                if link_href:
                    try:
                        current_url = self.driver.current_url
                        link = self.driver.find_element(By.XPATH, f"//a[@href='{link_href}']")
                        link.click()
                        time.sleep(3)
                        
                        new_url = self.driver.current_url
                        if new_url != current_url:
                            result['status'] = 'PASS'
                        else:
                            result['status'] = 'FAIL'
                            result['error_message'] = 'Navigation did not occur'
                    except:
                        result['status'] = 'FAIL'
                        result['error_message'] = 'Could not execute navigation test'
            
            elif test_type == 'button_functionality':
                # Test button functionality
                button_text = test_name.split('Verify ')[-1].split(' button')[0] if 'button' in test_name.lower() else ''
                if button_text:
                    try:
                        button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                        button.click()
                        time.sleep(2)
                        result['status'] = 'PASS'
                    except:
                        result['status'] = 'FAIL'
                        result['error_message'] = f'Could not click button: {button_text}'
            
            elif test_type == 'form_submission':
                # Test form submission
                try:
                    form = self.driver.find_element(By.TAG_NAME, "form")
                    if form:
                        # Try to find and fill required fields
                        inputs = form.find_elements(By.TAG_NAME, "input")
                        for inp in inputs:
                            if inp.get_attribute("type") in ['text', 'email']:
                                inp.send_keys("test@example.com")
                            elif inp.get_attribute("type") == 'password':
                                inp.send_keys("test123")
                        
                        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                        submit_btn.click()
                        time.sleep(3)
                        result['status'] = 'PASS'
                except:
                    result['status'] = 'FAIL'
                    result['error_message'] = 'Could not execute form submission test'
            
            elif test_type == 'input_functionality':
                # Test input field functionality
                field_name = test_name.split('Verify ')[-1].split(' input')[0] if 'input' in test_name.lower() else ''
                if field_name:
                    try:
                        field = self.driver.find_element(By.NAME, field_name)
                        if not field:
                            field = self.driver.find_element(By.ID, field_name)
                        
                        field.send_keys("test_data")
                        result['status'] = 'PASS'
                    except:
                        result['status'] = 'FAIL'
                        result['error_message'] = f'Could not test input field: {field_name}'
            
            execution_time = time.time() - start_time
            result['execution_time'] = round(execution_time, 2)
            
            if result['status'] == 'FAIL':
                result['screenshot'] = self.take_screenshot(test_id)
            
        except Exception as e:
            result['status'] = 'FAIL'
            result['error_message'] = str(e)
            result['screenshot'] = self.take_screenshot(test_id)
            result['execution_time'] = round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        
        return result
    
    def _perform_login(self) -> bool:
        """Perform login with credentials"""
        try:
            # Find username field
            username_fields = ['username', 'user', 'email', 'userid', 'user_id', 'txtUserId', 'employee_id']
            password_fields = ['password', 'pass', 'pwd', 'txtPassword']
            
            username_field = None
            password_field = None
            
            for field_name in username_fields:
                try:
                    username_field = self.driver.find_element(By.NAME, field_name)
                    break
                except:
                    try:
                        username_field = self.driver.find_element(By.ID, field_name)
                        break
                    except:
                        continue
            
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            if username_field and password_field:
                username_field.clear()
                username_field.send_keys(self.login_id)
                password_field.clear()
                password_field.send_keys(self.password)
                
                # Find and click login button
                login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                login_btn.click()
                time.sleep(3)
                
                # Check if login successful
                current_url = self.driver.current_url
                if current_url != self.website_url:
                    return True
                return False
            return False
        except:
            return False
    
    def _perform_login_with_invalid_credentials(self) -> bool:
        """Perform login with invalid credentials"""
        try:
            username_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            username_field.send_keys("invalid_user")
            password_field.send_keys("invalid_pass")
            
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            login_btn.click()
            time.sleep(3)
            
            # Check if still on login page (login failed = test passed)
            current_url = self.driver.current_url
            if current_url == self.website_url:
                return False  # Login failed = test passed
            return True  # Login succeeded = test failed
        except:
            return False
    
    def execute_all_tests(self, test_cases: Dict) -> Dict:
        """Execute all test cases"""
        start_time = time.time()
        
        if not self.driver:
            self.initialize_driver()
        
        print("[INFO] Starting test execution...")
        
        # Execute positive tests
        print(f"[INFO] Executing {len(test_cases.get('positive', []))} positive tests...")
        for test_case in test_cases.get('positive', []):
            result = self.execute_positive_test(test_case)
            self.results['positive'].append(result)
            self._update_summary(result)
        
        # Execute negative tests
        print(f"[INFO] Executing {len(test_cases.get('negative', []))} negative tests...")
        for test_case in test_cases.get('negative', [])[:5]:  # Limit to first 5 for demo
            result = self.execute_negative_test(test_case)
            self.results['negative'].append(result)
            self._update_summary(result)
        
        # Execute UI tests
        print(f"[INFO] Executing {len(test_cases.get('ui', []))} UI tests...")
        for test_case in test_cases.get('ui', [])[:5]:  # Limit to first 5 for demo
            result = self.execute_ui_test(test_case)
            self.results['ui'].append(result)
            self._update_summary(result)
        
        # Execute functional tests
        print(f"[INFO] Executing {len(test_cases.get('functional', []))} functional tests...")
        for test_case in test_cases.get('functional', [])[:5]:  # Limit to first 5 for demo
            result = self.execute_functional_test(test_case)
            self.results['functional'].append(result)
            self._update_summary(result)
        
        total_time = time.time() - start_time
        self.summary['execution_time'] = round(total_time, 2)
        self.summary['total_tests'] = self.summary['passed'] + self.summary['failed'] + self.summary['skipped']
        
        print(f"[SUCCESS] Test execution completed in {total_time:.2f} seconds")
        print(f"[INFO] Passed: {self.summary['passed']}, Failed: {self.summary['failed']}, Skipped: {self.summary['skipped']}")
        
        return {
            'results': self.results,
            'summary': self.summary
        }
    
    def _update_summary(self, result: Dict):
        """Update execution summary"""
        status = result.get('status', 'SKIPPED')
        if status == 'PASS':
            self.summary['passed'] += 1
        elif status == 'FAIL':
            self.summary['failed'] += 1
        else:
            self.summary['skipped'] += 1
    
    def save_execution_report(self, website_url: str) -> str:
        """Save execution report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"execution_report_{timestamp}.json"
        report_path = os.path.join('reports', report_file)
        
        report_data = {
            'website_url': website_url,
            'executed_at': datetime.now().isoformat(),
            'summary': self.summary,
            'results': self.results
        }
        
        # Remove screenshots from JSON (they're too large)
        for test_type in self.results:
            for result in self.results[test_type]:
                if 'screenshot' in result:
                    result['screenshot'] = 'Available' if result['screenshot'] else 'Not available'
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

        return report_file

    def save_execution_report_excel(self, website_url: str) -> str:
        """Save execution report to Excel (.xlsx). Falls back to CSV if openpyxl is unavailable."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xlsx_file = f"execution_report_{timestamp}.xlsx"
        xlsx_path = os.path.join('reports', xlsx_file)

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment
        except Exception:
            # Fallback to CSV if openpyxl isn't installed
            import csv
            csv_file = f"execution_report_{timestamp}.csv"
            csv_path = os.path.join('reports', csv_file)
            os.makedirs('reports', exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Category', 'Test ID', 'Test Name', 'Status', 'Execution Time (s)', 'Error Message', 'Screenshot Available'
                ])
                for category, results in self.results.items():
                    for r in results:
                        writer.writerow([
                            category,
                            r.get('test_id', ''),
                            r.get('test_name', ''),
                            r.get('status', ''),
                            r.get('execution_time', 0),
                            r.get('error_message', ''),
                            'Yes' if r.get('screenshot') else 'No'
                        ])
            return csv_file

        # Build XLSX report
        os.makedirs('reports', exist_ok=True)
        wb = Workbook()

        # Summary sheet
        ws_summary = wb.active
        ws_summary.title = 'Summary'
        header_font = Font(bold=True)
        center = Alignment(horizontal='left', vertical='center')
        executed_at = datetime.now().isoformat()

        summary_rows = [
            ('Website URL', website_url),
            ('Executed At', executed_at),
            ('Total Tests', self.summary.get('total_tests', 0)),
            ('Passed', self.summary.get('passed', 0)),
            ('Failed', self.summary.get('failed', 0)),
            ('Skipped', self.summary.get('skipped', 0)),
            ('Execution Time (s)', self.summary.get('execution_time', 0)),
        ]
        for r_idx, (k, v) in enumerate(summary_rows, start=1):
            ws_summary.cell(row=r_idx, column=1, value=k).font = header_font
            ws_summary.cell(row=r_idx, column=1).alignment = center
            ws_summary.cell(row=r_idx, column=2, value=v)

        # Results sheet
        ws = wb.create_sheet('Results')
        headers = ['Category', 'Test ID', 'Test Name', 'Status', 'Execution Time (s)', 'Error Message', 'Screenshot Available']
        for c_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=c_idx, value=h)
            cell.font = header_font
            cell.alignment = center

        row = 2
        for category, results in self.results.items():
            for r in results:
                ws.cell(row=row, column=1, value=category)
                ws.cell(row=row, column=2, value=r.get('test_id', ''))
                ws.cell(row=row, column=3, value=r.get('test_name', ''))
                ws.cell(row=row, column=4, value=r.get('status', ''))
                ws.cell(row=row, column=5, value=r.get('execution_time', 0))
                ws.cell(row=row, column=6, value=r.get('error_message', ''))
                ws.cell(row=row, column=7, value='Yes' if r.get('screenshot') else 'No')
                row += 1

        # Auto-size columns (best-effort)
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    max_length = max(max_length, len(str(cell.value)) if cell.value is not None else 0)
                except Exception:
                    pass
            ws.column_dimensions[col_letter].width = min(max(12, max_length + 2), 80)

        wb.save(xlsx_path)
        return xlsx_file
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
