# 🚀 Mobilise - Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the server:**
```bash
# Windows
start.bat

# Linux/Mac
python3 app.py
```

3. **Open your browser:**
Navigate to: `http://localhost:5000`

## How to Use

### Step 1: Enter Website Details
- **Website URL**: Enter the URL of the website you want to test (e.g., `https://example.com`)
- **Login ID** (Optional): Enter username/email if you want to test login
- **Password** (Optional): Enter password if you want to test login

### Step 2: Choose an Action

#### Option A: Analyze Website
Click **"Analyze Website"** to:
- Detect all input fields
- Find all buttons
- Discover links and navigation
- Identify forms
- View page structure

#### Option B: Generate Test Cases
Click **"Generate Test Cases"** to automatically create:
- ✅ **Positive Tests**: Valid login, valid inputs, successful operations
- ❌ **Negative Tests**: Empty fields, invalid credentials, SQL injection, XSS attacks
- 🎨 **UI Tests**: Button visibility, input field UI, responsive design
- ⚙️ **Functional Tests**: Navigation, button functionality, form submissions

#### Option C: Test Login
Click **"Test Login"** to:
- Automatically detect login fields
- Attempt login with provided credentials
- Verify login success/failure

### Step 3: View Results
- Browse test cases by category (tabs)
- View detailed test steps
- Check expected results
- See test priorities

### Step 4: Download Report
Click **"Download Report"** to get:
- Complete test case JSON file
- All test details
- Summary statistics

## Features

### ✨ Automatic Detection
- Smart field detection (username, password, etc.)
- Element identification
- Form analysis
- Button discovery

### 🎯 Comprehensive Testing
- **Positive Tests**: Test valid scenarios
- **Negative Tests**: Test error handling
- **UI Tests**: Test visual elements
- **Functional Tests**: Test workflows

### 📊 Reporting
- JSON format reports
- Detailed test information
- Downloadable files
- Summary statistics

## Example Workflow

1. Enter URL: `https://example.com/login`
2. Enter Login ID: `testuser@example.com`
3. Enter Password: `Test@123`
4. Click **"Generate Test Cases"**
5. Wait for generation (10-30 seconds)
6. View generated test cases
7. Download report

## Troubleshooting

### ChromeDriver Issues
If you see ChromeDriver errors:
- The tool will automatically try to download ChromeDriver
- Make sure Chrome browser is installed
- Check internet connection

### Login Not Working
If login test fails:
- Verify credentials are correct
- Check if website URL is accessible
- Ensure login fields are standard HTML inputs

### No Test Cases Generated
If no test cases are generated:
- Check website URL is correct and accessible
- Verify website loads properly
- Try "Analyze Website" first to see detected elements

## Support

For issues or questions:
- Check the console for error messages
- Verify all requirements are installed
- Ensure website is accessible

---

**Enjoy testing with Mobilise! 🚀**


