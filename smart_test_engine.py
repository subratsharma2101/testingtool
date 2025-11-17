from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Any

class SmartTestEngine:
    def __init__(self, website_url: str, login_id: str, password: str, headed: bool = True):
        self.website_url = website_url
        self.login_id = login_id
        self.password = password
        self.headed = headed
        self.driver = None
        self.detected_elements = {}
        self.test_cases = {
            'positive': [],
            'negative': [],
            'ui': [],
            'functional': []
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
        chrome_options.add_argument('--remote-allow-origins=*')
        if not self.headed:
            try:
                chrome_options.add_argument('--headless=new')
            except Exception:
                chrome_options.add_argument('--headless')
        else:
            # Keep headed Chrome window open for easier debugging/visibility
            chrome_options.add_experimental_option('detach', True)
        
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
            print(f"Warning: ChromeDriver initialization fallback: {e}")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception:
                # Last resort - system PATH
                self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.implicitly_wait(10)
        return self.driver
    
    def analyze_website(self):
        """Analyze website and detect all elements"""
        print("[INFO] Analyzing website structure...")
        self.driver.get(self.website_url)
        time.sleep(3)
        
        detected = {
            'forms': [],
            'input_fields': [],
            'buttons': [],
            'links': [],
            'images': [],
            'dropdowns': [],
            'checkboxes': [],
            'radio_buttons': [],
            'textareas': [],
            'iframes': [],
            'tables': [],
            'page_title': self.driver.title,
            'current_url': self.driver.current_url
        }
        
        # Detect Input Fields
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                try:
                    input_type = (inp.get_attribute("type") or "text").lower()
                    input_name = inp.get_attribute("name") or inp.get_attribute("id") or "unnamed"
                    placeholder = inp.get_attribute("placeholder") or ""
                    field_meta = {
                        'type': input_type,
                        'name': input_name,
                        'id': inp.get_attribute("id"),
                        'placeholder': placeholder,
                        'required': inp.get_attribute("required") is not None,
                        'class': inp.get_attribute("class")
                    }
                    detected['input_fields'].append(field_meta)
                    
                    if input_type == 'checkbox':
                        detected['checkboxes'].append({
                            'name': input_name,
                            'id': field_meta['id'],
                            'label': inp.get_attribute("aria-label") or placeholder or input_name
                        })
                    elif input_type == 'radio':
                        detected['radio_buttons'].append({
                            'name': input_name,
                            'id': field_meta['id'],
                            'label': inp.get_attribute("aria-label") or placeholder or input_name
                        })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting inputs: {e}")

        # Detect Textareas
        try:
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for area in textareas:
                try:
                    area_name = area.get_attribute("name") or area.get_attribute("id") or "textarea"
                    field_meta = {
                        'type': 'textarea',
                        'name': area_name,
                        'id': area.get_attribute("id"),
                        'placeholder': area.get_attribute("placeholder") or "",
                        'required': area.get_attribute("required") is not None,
                        'class': area.get_attribute("class")
                    }
                    detected['textareas'].append(field_meta)
                    detected['input_fields'].append(field_meta)
                except:
                    continue
        except Exception as e:
            print(f"Error detecting textareas: {e}")
        
        # Detect Buttons
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            buttons += self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            buttons += self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']")
            buttons += self.driver.find_elements(By.CSS_SELECTOR, "a[class*='button'], a[class*='btn']")
            
            seen_buttons = set()
            for btn in buttons:
                try:
                    btn_text = btn.text.strip() or btn.get_attribute("value") or btn.get_attribute("aria-label") or "Button"
                    btn_id = btn.get_attribute("id") or ""
                    
                    if btn_id in seen_buttons:
                        continue
                    seen_buttons.add(btn_id)
                    
                    detected['buttons'].append({
                        'text': btn_text,
                        'id': btn_id,
                        'class': btn.get_attribute("class"),
                        'type': btn.get_attribute("type") or "button",
                        'tag': btn.tag_name
                    })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting buttons: {e}")
        
        # Detect Links
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            seen_links = set()
            for link in links[:30]:
                try:
                    href = link.get_attribute("href")
                    link_text = link.text.strip()
                    if href and (link_text or href not in seen_links):
                        seen_links.add(href)
                        detected['links'].append({
                            'text': link_text or href,
                            'href': href
                        })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting links: {e}")
        
        # Detect Forms
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            for form in forms:
                try:
                    detected['forms'].append({
                        'action': form.get_attribute("action") or "",
                        'method': form.get_attribute("method") or "get",
                        'id': form.get_attribute("id")
                    })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting forms: {e}")
        
        # Detect Dropdowns
        try:
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            for select in selects:
                try:
                    detected['dropdowns'].append({
                        'name': select.get_attribute("name") or select.get_attribute("id"),
                        'id': select.get_attribute("id")
                    })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting dropdowns: {e}")

        # Detect Iframes
        try:
            frames = self.driver.find_elements(By.TAG_NAME, "iframe")
            for idx, frame in enumerate(frames[:10]):
                try:
                    detected['iframes'].append({
                        'id': frame.get_attribute("id") or f"iframe_{idx + 1}",
                        'name': frame.get_attribute("name"),
                        'src': frame.get_attribute("src")
                    })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting iframes: {e}")

        # Detect Tables
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for idx, table in enumerate(tables[:10]):
                try:
                    headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th") if th.text.strip()]
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    detected['tables'].append({
                        'id': table.get_attribute("id") or f"table_{idx + 1}",
                        'headers': headers[:8],
                        'row_count': len(rows)
                    })
                except:
                    continue
        except Exception as e:
            print(f"Error detecting tables: {e}")
        
        self.detected_elements = detected
        return detected
    
    def find_login_fields(self):
        """Intelligently find login fields"""
        login_keywords = ['username', 'user', 'email', 'login', 'userid', 'user_id', 'usr', 'emailid']
        password_keywords = ['password', 'pass', 'pwd', 'passwd']
        
        username_field = None
        password_field = None
        login_button = None
        
        # Find username field
        for inp in self.detected_elements['input_fields']:
            if inp['type'] in ['text', 'email']:
                name_lower = inp['name'].lower()
                id_lower = (inp['id'] or "").lower()
                placeholder_lower = inp['placeholder'].lower()
                
                if any(keyword in name_lower or keyword in id_lower or keyword in placeholder_lower 
                       for keyword in login_keywords):
                    username_field = inp
                    break
        
        # Find password field
        for inp in self.detected_elements['input_fields']:
            if inp['type'] == 'password':
                password_field = inp
                break
        
        # Find login button
        login_btn_keywords = ['login', 'sign in', 'submit', 'log in', 'signin']
        for btn in self.detected_elements['buttons']:
            btn_text_lower = btn['text'].lower()
            if any(keyword in btn_text_lower for keyword in login_btn_keywords):
                login_button = btn
                break
        
        return username_field, password_field, login_button
    
    def perform_login(self):
        """Perform login automatically"""
        print("[INFO] Attempting to login...")
        
        username_field, password_field, login_button = self.find_login_fields()
        
        if not username_field:
            print("[ERROR] Could not find username field")
            return False
        
        if not password_field:
            print("[ERROR] Could not find password field")
            return False
        
        try:
            # Enter username
            if username_field['id']:
                username_elem = self.driver.find_element(By.ID, username_field['id'])
            elif username_field['name']:
                username_elem = self.driver.find_element(By.NAME, username_field['name'])
            else:
                username_elem = self.driver.find_element(By.CSS_SELECTOR, f"input[type='{username_field['type']}']")
            
            username_elem.clear()
            username_elem.send_keys(self.login_id)
            print(f"[SUCCESS] Entered username: {self.login_id}")
            time.sleep(1)
            
            # Enter password
            if password_field['id']:
                password_elem = self.driver.find_element(By.ID, password_field['id'])
            elif password_field['name']:
                password_elem = self.driver.find_element(By.NAME, password_field['name'])
            else:
                password_elem = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            password_elem.clear()
            password_elem.send_keys(self.password)
            print("[SUCCESS] Entered password")
            time.sleep(1)
            
            # Click login button
            if login_button and login_button['id']:
                login_elem = self.driver.find_element(By.ID, login_button['id'])
            elif login_button:
                try:
                    login_elem = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{login_button['text'][:20]}')]")
                except:
                    login_elem = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            else:
                login_elem = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            
            login_elem.click()
            print("[SUCCESS] Clicked login button")
            time.sleep(3)
            
            # Check if login successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if current_url != self.website_url or 'dashboard' in page_source or 'welcome' in page_source or 'home' in page_source:
                print(f"[SUCCESS] Login appears successful! Current URL: {current_url}")
                return True
            else:
                # Check for error messages
                error_indicators = ['error', 'invalid', 'incorrect', 'failed']
                if any(indicator in page_source for indicator in error_indicators):
                    print("[WARNING] Login may have failed - error indicators found")
                    return False
                else:
                    print("[WARNING] Login status unclear")
                    return True
                
        except Exception as e:
            print(f"[ERROR] Login failed: {str(e)}")
            return False
    
    def generate_positive_test_cases(self):
        """Generate positive test cases"""
        print("[INFO] Generating positive test cases...")
        
        # Login positive test - navigate back to original page first
        if self.login_id and self.password:
            if self.driver:
                # Navigate back to original URL in case we're on a different page
                try:
                    self.driver.get(self.website_url)
                    time.sleep(2)
                except:
                    pass
            login_success = self.perform_login() if self.driver else False
            self.test_cases['positive'].append({
                'test_id': 'POS_LOGIN_001',
                'test_name': 'Valid Login Test',
                'description': 'Verify user can login with valid credentials',
                'steps': [
                    f'Navigate to {self.website_url}',
                    f'Enter username: {self.login_id}',
                    'Enter password: [hidden]',
                    'Click login button',
                    'Verify successful login'
                ],
                'expected_result': 'User should be logged in successfully',
                'status': 'PASS' if login_success else 'FAIL',
                'priority': 'High'
            })
        
        # Form field positive tests
        for inp in self.detected_elements['input_fields']:
            if inp['type'] not in ['password', 'hidden', 'submit', 'button']:
                self.test_cases['positive'].append({
                    'test_id': f"POS_INPUT_{inp['name'].replace(' ', '_')}",
                    'test_name': f"Valid input in {inp['name']} field",
                    'description': f'Verify {inp["name"]} field accepts valid input',
                    'steps': [
                        f"Locate field: {inp['name']}",
                        'Enter valid test data',
                        'Verify input is accepted'
                    ],
                    'expected_result': 'Field should accept valid input',
                    'field': inp['name'],
                    'priority': 'Medium'
                })
        
        # Dropdown positive tests
        for dropdown in self.detected_elements.get('dropdowns', []):
            if not dropdown:
                continue
            label = dropdown.get('name') or dropdown.get('id') or "dropdown"
            sanitized = self._sanitize_identifier(label)
            self.test_cases['positive'].append({
                'test_id': f"POS_DROPDOWN_{sanitized}",
                'test_name': f"Valid selection in {label} dropdown",
                'description': f'Ensure dropdown {label} accepts valid selections',
                'steps': [
                    f"Locate dropdown: {label}",
                    'Open dropdown options',
                    'Select a valid option',
                    'Verify selection is applied'
                ],
                'expected_result': 'Dropdown should update value with selected option',
                'field': label,
                'priority': 'Medium'
            })
        
        print(f"[SUCCESS] Generated {len(self.test_cases['positive'])} positive test cases")
    
    def generate_negative_test_cases(self):
        """Generate negative test cases"""
        print("[INFO] Generating negative test cases...")
        
        # Login negative tests
        negative_scenarios = [
            {
                'test_id': 'NEG_LOGIN_001',
                'test_name': 'Login with empty username',
                'description': 'Verify error message when username is empty',
                'steps': [
                    'Navigate to login page',
                    'Leave username field empty',
                    'Enter password',
                    'Click login button'
                ],
                'expected_result': 'Error message should be displayed',
                'priority': 'High'
            },
            {
                'test_id': 'NEG_LOGIN_002',
                'test_name': 'Login with empty password',
                'description': 'Verify error message when password is empty',
                'steps': [
                    'Navigate to login page',
                    'Enter username',
                    'Leave password field empty',
                    'Click login button'
                ],
                'expected_result': 'Error message should be displayed',
                'priority': 'High'
            },
            {
                'test_id': 'NEG_LOGIN_003',
                'test_name': 'Login with invalid credentials',
                'description': 'Verify error message for invalid credentials',
                'steps': [
                    'Navigate to login page',
                    'Enter invalid username: invalid_user',
                    'Enter invalid password: invalid_pass',
                    'Click login button'
                ],
                'expected_result': 'Invalid credentials error should be displayed',
                'priority': 'High'
            },
            {
                'test_id': 'NEG_LOGIN_004',
                'test_name': 'Login with SQL injection attempt',
                'description': 'Verify system handles SQL injection attempts',
                'steps': [
                    'Navigate to login page',
                    'Enter username: admin\' OR \'1\'=\'1',
                    'Enter password: test',
                    'Click login button'
                ],
                'expected_result': 'SQL injection should be blocked',
                'priority': 'Critical'
            },
            {
                'test_id': 'NEG_LOGIN_005',
                'test_name': 'Login with XSS attempt',
                'description': 'Verify system handles XSS attacks',
                'steps': [
                    'Navigate to login page',
                    'Enter username: <script>alert("XSS")</script>',
                    'Enter password: test',
                    'Click login button'
                ],
                'expected_result': 'XSS attack should be prevented',
                'priority': 'Critical'
            }
        ]
        
        self.test_cases['negative'].extend(negative_scenarios)
        
        # Input field negative tests
        for inp in self.detected_elements['input_fields']:
            if inp['required']:
                self.test_cases['negative'].append({
                    'test_id': f"NEG_INPUT_{inp['name'].replace(' ', '_')}_EMPTY",
                    'test_name': f"Empty {inp['name']} field test",
                    'description': f'Verify {inp["name"]} field validation for empty input',
                    'steps': [
                        f"Leave {inp['name']} field empty",
                        'Submit form',
                        'Verify validation error'
                    ],
                    'expected_result': 'Validation error should be displayed',
                    'priority': 'Medium'
                })
            
            # Boundary value tests
            if inp['type'] in ['text', 'number', 'email']:
                self.test_cases['negative'].append({
                    'test_id': f"NEG_INPUT_{inp['name'].replace(' ', '_')}_BOUNDARY",
                    'test_name': f"Boundary value test for {inp['name']}",
                    'description': f'Test {inp["name"]} with boundary values',
                    'steps': [
                        f"Enter very long text in {inp['name']} field",
                        'Submit form',
                        'Verify validation'
                    ],
                    'expected_result': 'Field should handle boundary values correctly',
                    'priority': 'Medium'
                })
        
        # Security payload tests for text inputs
        security_inputs = [
            inp for inp in self.detected_elements['input_fields']
            if inp['type'] in ['text', 'email', 'search', 'textarea', 'url']
        ]
        payloads = [
            ('SQLI', "SQL injection attempt", "admin' OR '1'='1"),
            ('XSS', "XSS script injection", '<script>alert(\"XSS\")</script>')
        ]
        for inp in security_inputs[:10]:
            label = inp['name'] or inp['id'] or "field"
            sanitized = self._sanitize_identifier(label)
            for suffix, description, payload in payloads:
                self.test_cases['negative'].append({
                    'test_id': f"NEG_SECURITY_{sanitized}_{suffix}",
                    'test_name': f"{description} in {label}",
                    'description': f'Test how {label} handles {description.lower()} payloads',
                    'steps': [
                        f"Locate field: {label}",
                        f"Enter payload: {payload}",
                        'Submit the enclosing form or action',
                        'Observe application response'
                    ],
                    'expected_result': 'Application should reject or sanitize the malicious payload',
                    'priority': 'Critical',
                    'field': inp['name'],
                    'field_id': inp['id'],
                    'malicious_payload': payload
                })
        
        print(f"[SUCCESS] Generated {len(self.test_cases['negative'])} negative test cases")
    
    def generate_ui_test_cases(self):
        """Generate UI test cases"""
        print("[INFO] Generating UI test cases...")
        
        # Button UI tests
        for btn in self.detected_elements['buttons']:
            self.test_cases['ui'].append({
                'test_id': f"UI_BUTTON_{btn['text'].replace(' ', '_').replace('/', '_')[:30]}",
                'test_name': f"Verify {btn['text']} button is visible",
                'description': f'Check if {btn["text"]} button is displayed correctly',
                'steps': [
                    f"Locate button: {btn['text']}",
                    'Verify button is visible',
                    'Verify button is clickable',
                    'Verify button styling is consistent'
                ],
                'expected_result': 'Button should be visible, clickable, and properly styled',
                'priority': 'Medium'
            })
        
        # Input field UI tests
        for inp in self.detected_elements['input_fields']:
            if inp['type'] not in ['hidden', 'submit']:
                self.test_cases['ui'].append({
                    'test_id': f"UI_INPUT_{inp['name'].replace(' ', '_')}",
                    'test_name': f"Verify {inp['name']} field UI",
                    'description': f'Check UI of {inp["name"]} input field',
                    'steps': [
                        f"Locate field: {inp['name']}",
                        'Verify field is visible',
                        'Verify placeholder text is displayed (if applicable)',
                        'Verify field styling is consistent',
                        'Verify field is properly aligned'
                    ],
                    'expected_result': 'Field should be properly styled, visible, and aligned',
                    'priority': 'Medium'
                })
        
        # Checkbox UI tests
        for checkbox in self.detected_elements.get('checkboxes', []):
            label = checkbox.get('label') or checkbox.get('name') or "Checkbox"
            sanitized = self._sanitize_identifier(label)
            self.test_cases['ui'].append({
                'test_id': f"UI_CHECKBOX_{sanitized}",
                'test_name': f"Verify {label} checkbox visibility",
                'description': f'Ensure {label} checkbox is visible, aligned, and toggleable',
                'steps': [
                    f"Locate checkbox: {label}",
                    'Verify checkbox is visible',
                    'Toggle checkbox on and off',
                    'Verify state changes correctly'
                ],
                'expected_result': 'Checkbox should be visible and reflect user interaction',
                'priority': 'Medium'
            })
        
        # Radio button UI tests
        for radio in self.detected_elements.get('radio_buttons', []):
            label = radio.get('label') or radio.get('name') or "Radio option"
            sanitized = self._sanitize_identifier(label)
            self.test_cases['ui'].append({
                'test_id': f"UI_RADIO_{sanitized}",
                'test_name': f"Verify {label} radio option",
                'description': f'Ensure radio option {label} is visible and selectable',
                'steps': [
                    f"Locate radio option: {label}",
                    'Verify option is visible',
                    'Select the option and verify other options respond appropriately'
                ],
                'expected_result': 'Radio option should be selectable and mutually exclusive',
                'priority': 'Medium'
            })
        
        # Iframe UI tests
        for frame in self.detected_elements.get('iframes', []):
            frame_label = frame.get('id') or frame.get('name') or frame.get('src') or "iframe"
            sanitized = self._sanitize_identifier(frame_label)
            self.test_cases['ui'].append({
                'test_id': f"UI_IFRAME_{sanitized}",
                'test_name': f"Verify iframe {frame_label} visibility",
                'description': f'Ensure iframe {frame_label} loads correctly',
                'steps': [
                    f"Locate iframe: {frame_label}",
                    'Verify iframe is visible',
                    'Verify iframe content loads without errors'
                ],
                'expected_result': 'Iframe content should be accessible and visible',
                'priority': 'Low'
            })
        
        # Page UI tests
        self.test_cases['ui'].append({
            'test_id': 'UI_PAGE_001',
            'test_name': 'Verify page title',
            'description': 'Check if page title is displayed correctly',
            'steps': [
                'Load the page',
                'Verify page title is present',
                'Verify page title is meaningful'
            ],
            'expected_result': f'Page title should be: {self.detected_elements.get("page_title", "N/A")}',
            'priority': 'Low'
        })
        
        self.test_cases['ui'].append({
            'test_id': 'UI_PAGE_002',
            'test_name': 'Verify responsive design',
            'description': 'Check if page is responsive on different screen sizes',
            'steps': [
                'Open page on desktop',
                'Resize browser to mobile size',
                'Verify layout adjusts properly',
                'Verify all elements are accessible'
            ],
            'expected_result': 'Page should be responsive and usable on all screen sizes',
            'priority': 'High'
        })
        
        print(f"[SUCCESS] Generated {len(self.test_cases['ui'])} UI test cases")
    
    def generate_functional_test_cases(self):
        """Generate functional test cases"""
        print("[INFO] Generating functional test cases...")
        
        # Navigation tests
        for link in self.detected_elements['links'][:15]:
            self.test_cases['functional'].append({
                'test_id': f"FUNC_NAV_{link['text'].replace(' ', '_').replace('/', '_')[:25]}",
                'test_name': f"Verify navigation to {link['text']}",
                'description': f'Test navigation functionality for {link["text"]} link',
                'steps': [
                    f"Navigate to page: {self.website_url}",
                    f"Locate and click on link: {link['text']}",
                    'Wait for page to load',
                    'Verify page navigation occurs',
                    'Verify new page URL is correct',
                    'Verify page loads without errors',
                    'Verify page content is displayed',
                    'Verify no broken links or missing resources'
                ],
                'expected_result': 'Page should navigate successfully without errors and display correct content',
                'link': link['href'],
                'priority': 'Medium',
                'test_type': 'navigation'
            })
        
        # Button functionality tests
        for btn in self.detected_elements['buttons']:
            if btn['text'].lower() not in ['login', 'submit']:  # Skip login as it's already tested
                self.test_cases['functional'].append({
                    'test_id': f"FUNC_BTN_{btn['text'].replace(' ', '_').replace('/', '_')[:25]}",
                    'test_name': f"Verify {btn['text']} button functionality",
                    'description': f'Test functionality of {btn["text"]} button',
                    'steps': [
                        f"Navigate to page: {self.website_url}",
                        f"Locate button: {btn['text']}",
                        'Verify button is visible and enabled',
                        f"Click button: {btn['text']}",
                        'Wait for action to complete',
                        'Verify expected action occurs',
                        'Verify no error messages are displayed',
                        'Verify page state changes if applicable'
                    ],
                    'expected_result': 'Button should perform expected action without errors',
                    'priority': 'Medium',
                    'test_type': 'button_functionality'
                })
        
        # Form submission tests
        for form in self.detected_elements['forms']:
            self.test_cases['functional'].append({
                'test_id': f"FUNC_FORM_{form.get('id', 'unknown')}",
                'test_name': f"Verify form submission functionality",
                'description': f'Test form submission for form: {form.get("id", "Unknown")}',
                'steps': [
                    f"Navigate to page: {self.website_url}",
                    'Locate the form',
                    'Fill all required fields with valid data',
                    'Verify all fields are filled correctly',
                    'Submit the form',
                    'Wait for form submission to complete',
                    'Verify form submission is successful',
                    'Verify appropriate response is received',
                    'Verify success message or redirect occurs'
                ],
                'expected_result': 'Form should submit successfully with proper validation',
                'priority': 'High',
                'test_type': 'form_submission'
            })
        
        # Input field functionality tests
        for inp in self.detected_elements['input_fields']:
            if inp['type'] not in ['hidden', 'submit', 'button', 'password']:
                self.test_cases['functional'].append({
                    'test_id': f"FUNC_INPUT_{inp['name'].replace(' ', '_')}",
                    'test_name': f"Verify {inp['name']} input field functionality",
                    'description': f'Test input functionality for {inp["name"]} field',
                    'steps': [
                        f"Navigate to page: {self.website_url}",
                        f"Locate input field: {inp['name']}",
                        'Verify field is visible and enabled',
                        'Enter test data in the field',
                        'Verify data is accepted',
                        'Verify field validation works',
                        'Verify field formatting if applicable'
                    ],
                    'expected_result': 'Input field should accept and process data correctly',
                    'priority': 'Medium',
                    'test_type': 'input_functionality'
                })
        
        # Dropdown functionality tests
        for dd in self.detected_elements['dropdowns']:
            self.test_cases['functional'].append({
                'test_id': f"FUNC_DROPDOWN_{dd.get('name', 'unknown').replace(' ', '_')}",
                'test_name': f"Verify dropdown {dd.get('name', 'Unknown')} functionality",
                'description': f'Test dropdown functionality for {dd.get("name", "Unknown")}',
                'steps': [
                    f"Navigate to page: {self.website_url}",
                    f"Locate dropdown: {dd.get('name', 'Unknown')}",
                    'Click on dropdown to open',
                    'Verify dropdown options are displayed',
                    'Select an option from dropdown',
                    'Verify selected option is displayed',
                    'Verify dropdown value is updated'
                ],
                'expected_result': 'Dropdown should allow selection and update value correctly',
                'priority': 'Medium',
                'test_type': 'dropdown_functionality'
            })
        
        # Table validation tests
        for table in self.detected_elements.get('tables', []):
            table_id = table.get('id') or "data_table"
            self.test_cases['functional'].append({
                'test_id': f"FUNC_TABLE_{self._sanitize_identifier(table_id)}",
                'test_name': f"Verify data table {table_id} renders correctly",
                'description': f'Check table {table_id} row counts and headers',
                'steps': [
                    f"Locate table: {table_id}",
                    'Verify headers are displayed',
                    'Verify row count matches expected data',
                    'Scroll through table content if paginated'
                ],
                'expected_result': 'Table should render rows and headers without layout issues',
                'priority': 'Medium',
                'test_type': 'table_validation',
                'table': table
            })
        
        # Iframe interaction tests
        for frame in self.detected_elements.get('iframes', []):
            frame_label = frame.get('id') or frame.get('name') or frame.get('src') or "iframe"
            self.test_cases['functional'].append({
                'test_id': f"FUNC_IFRAME_{self._sanitize_identifier(frame_label)}",
                'test_name': f"Verify iframe {frame_label} interaction",
                'description': f'Ensure iframe {frame_label} loads and can be switched to',
                'steps': [
                    f"Locate iframe: {frame_label}",
                    'Switch focus to iframe',
                    'Verify iframe content loads',
                    'Switch back to parent context'
                ],
                'expected_result': 'Iframe should be accessible and load content.',
                'priority': 'Low',
                'test_type': 'iframe_validation',
                'iframe': frame
            })
        
        # Page load and performance tests
        self.test_cases['functional'].append({
            'test_id': 'FUNC_PERF_001',
            'test_name': 'Verify page load performance',
            'description': 'Test page load time and performance',
            'steps': [
                f"Navigate to page: {self.website_url}",
                'Measure page load time',
                'Verify page loads within acceptable time',
                'Verify all resources are loaded',
                'Verify no broken images or missing resources'
            ],
            'expected_result': 'Page should load within acceptable time with all resources',
            'priority': 'Medium',
            'test_type': 'performance'
        })
        
        # User workflow tests
        if self.login_id and self.password:
            self.test_cases['functional'].append({
                'test_id': 'FUNC_WORKFLOW_001',
                'test_name': 'Verify complete login workflow',
                'description': 'Test end-to-end login workflow',
                'steps': [
                    f"Navigate to login page: {self.website_url}",
                    'Verify login page is displayed',
                    'Enter valid username',
                    'Enter valid password',
                    'Click login button',
                    'Wait for authentication',
                    'Verify successful login',
                    'Verify user is redirected to appropriate page',
                    'Verify user session is established',
                    'Verify user can access protected resources'
                ],
                'expected_result': 'Complete login workflow should work seamlessly',
                'priority': 'Critical',
                'test_type': 'workflow'
            })
        
        print(f"[SUCCESS] Generated {len(self.test_cases['functional'])} functional test cases")
    
    def _sanitize_identifier(self, text: str) -> str:
        if not text:
            return "FIELD"
        value = re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_')
        return value or "FIELD"
    
    def generate_all_tests(self):
        """Generate all types of test cases"""
        if not self.driver:
            self.initialize_driver()
        
        self.analyze_website()
        
        # Generate all test types
        self.generate_positive_test_cases()
        self.generate_negative_test_cases()
        self.generate_ui_test_cases()
        self.generate_functional_test_cases()
        
        return self.test_cases
    
    def save_report(self):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        report_path = os.path.join('reports', report_file)
        
        report_data = {
            'website_url': self.website_url,
            'generated_at': datetime.now().isoformat(),
            'test_cases': self.test_cases,
            'summary': {
                'total_tests': sum(len(tests) for tests in self.test_cases.values()),
                'positive': len(self.test_cases['positive']),
                'negative': len(self.test_cases['negative']),
                'ui': len(self.test_cases['ui']),
                'functional': len(self.test_cases['functional'])
            },
            'detected_elements': {
                'input_fields': len(self.detected_elements.get('input_fields', [])),
                'buttons': len(self.detected_elements.get('buttons', [])),
                'links': len(self.detected_elements.get('links', [])),
                'forms': len(self.detected_elements.get('forms', []))
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        return report_file
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
