# Mobilise - Smart Test Automation Tool

A professional, intelligent test automation platform that automatically generates comprehensive test cases (Positive, Negative, UI, and Functional) by analyzing any website.

## 🚀 Features

- **Automatic Test Generation**: Generate positive, negative, UI, and functional test cases automatically
- **Smart Website Analysis**: Automatically detects forms, buttons, inputs, links, and other elements
- **Login Automation**: Automatically detects and tests login functionality
- **Beautiful UI**: Modern, responsive design with Mobilise branding
- **Test Reports**: Export comprehensive test reports in JSON format
- **Real-time Analysis**: Analyze website structure before generating tests
- **Manual Recording**: Record real browser sessions and generate editable Playwright scripts
- **API Testing Lab**: Import OpenAPI/Swagger specs to auto-generate and execute API suites
- **Run History**: Built-in activity feed to review recent generations/executions across UI and API suites

## 📋 Requirements

- Python 3.8+
- Playwright (browsers are automatically installed)

## 🛠️ Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Playwright browsers:**
```bash
playwright install chromium
```
Or for all browsers:
```bash
playwright install
```

3. **Run the application:**
```bash
python app.py
```

4. **Access the tool:**
Open your browser and navigate to: `http://localhost:5000`

## 📖 Usage

1. **Enter Website URL**: Provide the URL of the website you want to test
2. **Optional Login Credentials**: Enter login ID and password if you want to test login functionality
3. **Choose an action:**
   - **Analyze Website**: Analyze website structure and detect elements
   - **Generate Test Cases**: Generate all test cases automatically
   - **Test Login**: Test login functionality only

4. **View Results**: Browse generated test cases by category
5. **Download Report**: Download comprehensive test report as JSON

### Manual Recording Studio

1. Enter the website URL in the main configuration card
2. Click **Start Recording** to launch a headed Chrome window
3. Perform the desired steps manually—every click, input, and submission is captured
4. Click **Stop & Save** to convert the flow into an editable Playwright Python script
5. Copy or download the script, tweak as needed, and replay it through the executor

### API Testing Lab

1. Paste your API base URL and OpenAPI/Swagger JSON into the API Testing card
2. Click **Generate API Tests** to auto-build positive and negative scenarios
3. Review the generated list, then hit **Execute API Tests** to run live requests
4. Download generation or execution reports for auditing and CI/CD evidence

### Run History

- Open the dashboard to view the latest UI/API generations and executions
- Each entry surfaces timestamp, target URL, totals, and report download shortcuts
- Use it as a lightweight audit trail or to confirm CI jobs finished successfully

## 🎯 Test Types Generated

### Positive Tests
- Valid login tests
- Valid input field tests
- Successful form submissions

### Negative Tests
- Empty field validations
- Invalid credentials
- SQL injection attempts
- XSS attack prevention
- Boundary value tests

### UI Tests
- Button visibility and functionality
- Input field UI checks
- Responsive design tests
- Page title verification

### Functional Tests
- Navigation tests
- Button functionality
- Form submission tests
- End-to-end workflows

## 📁 Project Structure

```
mobilise-test-tool/
├── app.py                  # Flask application
├── smart_test_engine.py    # Test generation engine
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── script.js      # Frontend logic
└── reports/               # Generated test reports
```

## 🔧 Configuration

The tool uses Playwright for browser automation. Playwright browsers are automatically managed and installed on first run.

## 📝 Example

1. Enter URL: `https://example.com`
2. Enter Login ID: `testuser`
3. Enter Password: `testpass`
4. Click "Generate Test Cases"
5. View generated test cases
6. Download report

## 🎨 Features in Detail

### Smart Element Detection
- Automatically detects input fields, buttons, links, forms
- Identifies login fields intelligently
- Detects required fields
- Finds dropdowns and other form elements

### Test Case Generation
- Comprehensive positive test cases
- Extensive negative test scenarios
- UI validation tests
- Functional workflow tests

### Report Generation
- JSON format reports
- Detailed test case information
- Test steps and expected results
- Priority and status tracking

## 🤝 Support

For issues or questions, please contact the Mobilise team.

## 📄 License

Copyright © 2024 Mobilise. All rights reserved.

---

**Built with ❤️ by Mobilise Team**


