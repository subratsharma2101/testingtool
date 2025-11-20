# 🚀 Quick Start Guide - Mobilise Test Automation Tool

## Prerequisites

- **Python 3.8+** (Check: `py --version`)
- **Internet connection** (to download dependencies and browsers)

---

## Installation Steps

### 1️⃣ Install Python Dependencies

Open terminal/command prompt in the project folder and run:

```bash
py -m pip install -r requirements.txt
```

**OR** if `pip` works directly:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Playwright (browser automation)
- Other required libraries

---

### 2️⃣ Install Playwright Browsers

After installing dependencies, install the browser:

```bash
playwright install chromium
```

**Note:** This downloads Chromium browser (~150MB) which is needed for automation.

---

### 3️⃣ Run the Application

#### Option A: Using Python directly

```bash
py app.py
```

#### Option B: Using start script (Windows)

Double-click `start.bat` file

#### Option C: Using start script (Linux/Mac)

```bash
chmod +x start.sh
./start.sh
```

---

### 4️⃣ Access the Tool

1. Wait for the message: `Running on http://0.0.0.0:5000` or `Running on http://127.0.0.1:5000`
2. Open your web browser
3. Go to: **http://localhost:5000**

---

## Usage

### Basic Testing

1. **Enter Website URL**: Enter the website URL you want to test
   - Example: `https://formofdifferentlevels.web.app`
   - Example: `https://example.com`

2. **Optional: Login Credentials**
   - If the website requires login, enter username and password

3. **Choose Browser Mode**
   - **Show Chrome (headed)**: Browser window will be visible
   - **Hide Chrome (headless)**: Browser runs in background (faster)

4. **Actions Available**:
   - **🔍 Analyze Website**: Analyze website structure
   - **📝 Generate Test Cases**: Generate all test cases
   - **▶️ Generate & Execute Tests**: Generate and run tests automatically
   - **🔐 Test Login**: Test login functionality only

---

### Advanced Features

#### Manual Recording Studio

1. Enter website URL
2. Click **Start Recording**
3. A Chrome window will open
4. Perform your actions manually (click, type, submit forms)
5. Click **Stop & Save** when done
6. Review the generated Playwright script

#### API Testing Lab

1. Enter API Base URL
2. Paste OpenAPI/Swagger JSON specification
3. Click **Generate API Tests**
4. Review generated test cases
5. Click **Execute API Tests** to run them

#### Run History

- View all past test generations and executions
- Download reports
- Track testing history

---

## Troubleshooting

### Error: "pip is not recognized"

**Solution**: Use `py -m pip` instead of `pip`

```bash
py -m pip install -r requirements.txt
```

---

### Error: "playwright is not recognized"

**Solution**: Install Playwright properly

```bash
py -m pip install playwright
playwright install chromium
```

---

### Error: "Cannot reach website"

**Possible causes**:
1. Website URL is incorrect
2. Internet connection is not working
3. Website is down or blocked

**Solutions**:
- Check the URL is correct (include `http://` or `https://`)
- Check internet connection
- Try a different website first (like `https://example.com`)

---

### Error: "Port 5000 already in use"

**Solution**: Stop the existing server

1. Find the process using port 5000
2. Kill it, or
3. Change port in `app.py` (last line):
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
   ```

---

### Server won't start

**Check**:
1. Python is installed: `py --version`
2. All dependencies installed: `py -m pip list`
3. Playwright installed: `playwright --version`
4. Chromium installed: Check if browser folder exists

---

## Command Summary

```bash
# Install dependencies
py -m pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Run application
py app.py

# Access in browser
# http://localhost:5000
```

---

## Features Overview

✅ **Automatic Test Generation**
- Positive tests
- Negative tests
- UI tests
- Functional tests
- Multi-level form tests

✅ **Manual Recording**
- Record browser sessions
- Generate Playwright scripts
- Edit and replay scripts

✅ **API Testing**
- Generate API tests from OpenAPI spec
- Execute API tests
- View execution results

✅ **Reports & History**
- Download JSON/Excel reports
- View test execution history
- Track all testing activities

---

## Need Help?

1. Check the `README.md` for detailed documentation
2. Review `TEST_EXECUTION_GUIDE.md` for execution details
3. Check console/terminal for error messages

---

**Happy Testing! 🎉**