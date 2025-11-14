# Mobilise - Smart Test Automation Tool

A professional, intelligent test automation platform that automatically generates comprehensive test cases (Positive, Negative, UI, and Functional) by analyzing any website.

## 🚀 Features

- **Automatic Test Generation**: Generate positive, negative, UI, and functional test cases automatically
- **Smart Website Analysis**: Automatically detects forms, buttons, inputs, links, and other elements
- **Login Automation**: Automatically detects and tests login functionality
- **Beautiful UI**: Modern, responsive design with Mobilise branding
- **Test Reports**: Export comprehensive test reports in JSON format
- **Real-time Analysis**: Analyze website structure before generating tests

## 📋 Requirements

- Python 3.8+
- Chrome Browser
- ChromeDriver (automatically managed)

## 🛠️ Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the tool:**
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

The tool automatically uses ChromeDriver from the cache directory. If not found, it will download automatically using webdriver-manager.

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


