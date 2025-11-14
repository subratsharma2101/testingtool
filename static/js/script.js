// Mobilise Test Automation Tool - Frontend JavaScript

let currentReportFile = null;
let currentExcelReportFile = null;

// DOM Elements
const testForm = document.getElementById('testForm');
const generateBtn = document.getElementById('generateBtn');
const generateAndExecuteBtn = document.getElementById('generateAndExecuteBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const testLoginBtn = document.getElementById('testLoginBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const analysisSection = document.getElementById('analysisSection');
const downloadBtn = document.getElementById('downloadBtn');
const downloadExcelBtn = document.getElementById('downloadExcelBtn');
const headedToggle = document.getElementById('headed_toggle');

// Tab functionality
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.getAttribute('data-tab');
        
        // Remove active class from all buttons and panes
        tabButtons.forEach(b => b.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));
        
        // Add active class to clicked button and corresponding pane
        btn.classList.add('active');
        document.getElementById(`${tabName}Tab`).classList.add('active');
    });
});

// Generate Test Cases
generateBtn.addEventListener('click', async () => {
    const websiteUrl = document.getElementById('website_url').value.trim();
    const loginId = document.getElementById('login_id').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!websiteUrl) {
        alert('Please enter a website URL');
        return;
    }
    
    // Show loading
    showLoading('Generating test cases...', 'This may take a few moments');
    hideResults();
    hideAnalysis();
    
    try {
        const response = await fetch('/api/generate-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                website_url: websiteUrl,
                login_id: loginId,
                password: password,
                headed: headedToggle ? headedToggle.value === 'true' : true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentReportFile = data.report_file;
            displayResults(data);
            hideLoading();
        } else {
            hideLoading();
            alert('Error: ' + (data.error || 'Failed to generate test cases'));
        }
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
        console.error('Error:', error);
    }
});

// Analyze Website
analyzeBtn.addEventListener('click', async () => {
    const websiteUrl = document.getElementById('website_url').value.trim();
    
    if (!websiteUrl) {
        alert('Please enter a website URL');
        return;
    }
    
    showLoading('Analyzing website...', 'Detecting elements and structure');
    hideResults();
    hideAnalysis();
    
    try {
        const response = await fetch('/api/analyze-website', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                website_url: websiteUrl
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAnalysis(data.elements);
            hideLoading();
        } else {
            hideLoading();
            alert('Error: ' + (data.error || 'Failed to analyze website'));
        }
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
        console.error('Error:', error);
    }
});

// Generate and Execute Tests
generateAndExecuteBtn.addEventListener('click', async () => {
    const websiteUrl = document.getElementById('website_url').value.trim();
    const loginId = document.getElementById('login_id').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!websiteUrl) {
        alert('Please enter a website URL');
        return;
    }
    
    // Show loading
    showLoading('Generating and executing tests...', 'This may take a few minutes. Please wait...');
    hideResults();
    hideAnalysis();
    
    try {
        const response = await fetch('/api/generate-and-execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                website_url: websiteUrl,
                login_id: loginId,
                password: password,
                headed: headedToggle ? headedToggle.value === 'true' : true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentReportFile = data.reports.generation_report;
            currentExcelReportFile = data.reports.execution_excel_report;
            displayResultsWithExecution(data);
            hideLoading();
        } else {
            hideLoading();
            alert('Error: ' + (data.error || 'Failed to generate and execute tests'));
        }
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
        console.error('Error:', error);
    }
});

// Test Login
testLoginBtn.addEventListener('click', async () => {
    const websiteUrl = document.getElementById('website_url').value.trim();
    const loginId = document.getElementById('login_id').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!websiteUrl || !loginId || !password) {
        alert('Please enter website URL, login ID, and password');
        return;
    }
    
    showLoading('Testing login...', 'Attempting to login with provided credentials');
    hideResults();
    hideAnalysis();
    
    try {
        const response = await fetch('/api/test-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                website_url: websiteUrl,
                login_id: loginId,
                password: password
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            alert('✅ Login test successful!');
        } else {
            alert('❌ Login test failed: ' + (data.message || 'Invalid credentials or login error'));
        }
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
        console.error('Error:', error);
    }
});

// Download Report (JSON)
downloadBtn.addEventListener('click', () => {
    if (currentReportFile) {
        window.location.href = `/api/download-report/${currentReportFile}`;
    } else {
        alert('No report available to download');
    }
});

// Download Excel Report
if (downloadExcelBtn) {
    downloadExcelBtn.addEventListener('click', () => {
        if (currentExcelReportFile) {
            window.location.href = `/api/download-report/${currentExcelReportFile}`;
        } else {
            alert('No Excel report available to download');
        }
    });
}

// Display Results
function displayResults(data) {
    const summary = data.summary;
    
    // Hide execution summary if not present
    document.getElementById('executionSummary').style.display = 'none';
    
    // Update summary counts
    document.getElementById('totalCount').textContent = summary.total_tests;
    document.getElementById('positiveCount').textContent = summary.positive;
    document.getElementById('negativeCount').textContent = summary.negative;
    document.getElementById('uiCount').textContent = summary.ui;
    document.getElementById('functionalCount').textContent = summary.functional;
    
    // Update badges
    document.getElementById('positiveBadge').textContent = summary.positive;
    document.getElementById('negativeBadge').textContent = summary.negative;
    document.getElementById('uiBadge').textContent = summary.ui;
    document.getElementById('functionalBadge').textContent = summary.functional;
    
    // Display test cases
    displayTestCases('positive', data.test_cases.positive);
    displayTestCases('negative', data.test_cases.negative);
    displayTestCases('ui', data.test_cases.ui);
    displayTestCases('functional', data.test_cases.functional);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display Results with Execution
function displayResultsWithExecution(data) {
    const generationSummary = data.summary.generation;
    const executionSummary = data.summary.execution;
    
    // Show execution summary
    document.getElementById('executionSummary').style.display = 'block';
    document.getElementById('execTotalTests').textContent = executionSummary.total_tests;
    document.getElementById('execPassed').textContent = executionSummary.passed;
    document.getElementById('execFailed').textContent = executionSummary.failed;
    document.getElementById('execSkipped').textContent = executionSummary.skipped;
    document.getElementById('execTime').textContent = executionSummary.execution_time;
    
    // Update summary counts
    document.getElementById('totalCount').textContent = generationSummary.total_tests;
    document.getElementById('positiveCount').textContent = generationSummary.positive;
    document.getElementById('negativeCount').textContent = generationSummary.negative;
    document.getElementById('uiCount').textContent = generationSummary.ui;
    document.getElementById('functionalCount').textContent = generationSummary.functional;
    
    // Update badges
    document.getElementById('positiveBadge').textContent = generationSummary.positive;
    document.getElementById('negativeBadge').textContent = generationSummary.negative;
    document.getElementById('uiBadge').textContent = generationSummary.ui;
    document.getElementById('functionalBadge').textContent = generationSummary.functional;
    
    // Display test cases with execution results
    displayTestCasesWithResults('positive', data.test_cases.positive, data.execution_results.positive);
    displayTestCasesWithResults('negative', data.test_cases.negative, data.execution_results.negative);
    displayTestCasesWithResults('ui', data.test_cases.ui, data.execution_results.ui);
    displayTestCasesWithResults('functional', data.test_cases.functional, data.execution_results.functional);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display Test Cases
function displayTestCases(type, testCases) {
    const container = document.getElementById(`${type}Tests`);
    container.innerHTML = '';
    
    if (testCases.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No test cases generated</p>';
        return;
    }
    
    testCases.forEach(testCase => {
        const card = createTestCaseCard(testCase);
        container.appendChild(card);
    });
}

// Create Test Case Card
function createTestCaseCard(testCase, executionResult = null) {
    const card = document.createElement('div');
    card.className = 'test-case-card';
    
    // Add border color based on execution result
    if (executionResult) {
        if (executionResult.status === 'PASS') {
            card.style.borderLeftColor = '#10b981';
        } else if (executionResult.status === 'FAIL') {
            card.style.borderLeftColor = '#ef4444';
        } else {
            card.style.borderLeftColor = '#64748b';
        }
    }
    
    const stepsHtml = testCase.steps ? `
        <div class="test-case-steps">
            <h4><i class="fas fa-list-ol"></i> Test Steps</h4>
            <ol>
                ${testCase.steps.map(step => `<li>${step}</li>`).join('')}
            </ol>
        </div>
    ` : '';
    
    // Execution result badge
    let executionBadge = '';
    if (executionResult) {
        const statusColor = executionResult.status === 'PASS' ? '#10b981' : 
                           executionResult.status === 'FAIL' ? '#ef4444' : '#64748b';
        executionBadge = `
            <div style="margin-top: 10px; padding: 10px; background: ${statusColor}15; border-radius: 8px; border-left: 3px solid ${statusColor};">
                <strong style="color: ${statusColor};">Execution Status: ${executionResult.status}</strong>
                ${executionResult.execution_time ? `<br><small>Execution Time: ${executionResult.execution_time}s</small>` : ''}
                ${executionResult.error_message ? `<br><small style="color: #ef4444;">Error: ${executionResult.error_message}</small>` : ''}
            </div>
        `;
    }
    
    const statusBadge = testCase.status ? `
        <span class="test-case-priority priority-${testCase.status.toLowerCase()}">
            ${testCase.status}
        </span>
    ` : '';
    
    card.innerHTML = `
        <div class="test-case-header">
            <span class="test-case-id">${testCase.test_id}</span>
            <span class="test-case-name">${testCase.test_name}</span>
            ${statusBadge}
            <span class="test-case-priority priority-${(testCase.priority || 'medium').toLowerCase()}">
                ${testCase.priority || 'Medium'}
            </span>
        </div>
        <div class="test-case-description">
            ${testCase.description || 'No description available'}
        </div>
        ${stepsHtml}
        <div class="test-case-expected">
            <strong><i class="fas fa-check-circle"></i> Expected Result:</strong>
            ${testCase.expected_result || 'Test should pass'}
        </div>
        ${executionBadge}
    `;
    
    return card;
}

// Display Test Cases with Results
function displayTestCasesWithResults(type, testCases, executionResults) {
    const container = document.getElementById(`${type}Tests`);
    container.innerHTML = '';
    
    if (testCases.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No test cases generated</p>';
        return;
    }
    
    // Create a map of execution results by test_id
    const resultsMap = {};
    if (executionResults) {
        executionResults.forEach(result => {
            resultsMap[result.test_id] = result;
        });
    }
    
    testCases.forEach(testCase => {
        const executionResult = resultsMap[testCase.test_id] || null;
        const card = createTestCaseCard(testCase, executionResult);
        container.appendChild(card);
    });
}

// Display Analysis
function displayAnalysis(elements) {
    const container = document.getElementById('analysisGrid');
    container.innerHTML = '';
    
    // Input Fields
    if (elements.input_fields && elements.input_fields.length > 0) {
        const item = createAnalysisItem(
            'Input Fields',
            'fas fa-keyboard',
            elements.input_fields.map(inp => 
                `${inp.name} (${inp.type})${inp.required ? ' *' : ''}`
            )
        );
        container.appendChild(item);
    }
    
    // Buttons
    if (elements.buttons && elements.buttons.length > 0) {
        const item = createAnalysisItem(
            'Buttons',
            'fas fa-mouse-pointer',
            elements.buttons.map(btn => btn.text || 'Button')
        );
        container.appendChild(item);
    }
    
    // Links
    if (elements.links && elements.links.length > 0) {
        const item = createAnalysisItem(
            'Links',
            'fas fa-link',
            elements.links.slice(0, 10).map(link => link.text || link.href)
        );
        container.appendChild(item);
    }
    
    // Forms
    if (elements.forms && elements.forms.length > 0) {
        const item = createAnalysisItem(
            'Forms',
            'fas fa-file-alt',
            elements.forms.map((form, idx) => `Form ${idx + 1} (${form.method})`)
        );
        container.appendChild(item);
    }
    
    // Dropdowns
    if (elements.dropdowns && elements.dropdowns.length > 0) {
        const item = createAnalysisItem(
            'Dropdowns',
            'fas fa-chevron-down',
            elements.dropdowns.map(dd => dd.name || dd.id)
        );
        container.appendChild(item);
    }
    
    // Page Info
    if (elements.page_title) {
        const item = document.createElement('div');
        item.className = 'analysis-item';
        item.innerHTML = `
            <h3><i class="fas fa-info-circle"></i> Page Information</h3>
            <ul>
                <li><strong>Title:</strong> ${elements.page_title}</li>
                <li><strong>URL:</strong> ${elements.current_url}</li>
            </ul>
        `;
        container.appendChild(item);
    }
    
    analysisSection.style.display = 'block';
    analysisSection.classList.add('fade-in');
    analysisSection.scrollIntoView({ behavior: 'smooth' });
}

// Create Analysis Item
function createAnalysisItem(title, icon, items) {
    const item = document.createElement('div');
    item.className = 'analysis-item';
    
    const listItems = items.map(itemText => `<li>${itemText}</li>`).join('');
    
    item.innerHTML = `
        <h3><i class="${icon}"></i> ${title} (${items.length})</h3>
        <ul>
            ${listItems}
        </ul>
    `;
    
    return item;
}

// Show/Hide Functions
function showLoading(text, subtext) {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingSubtext').textContent = subtext;
    loadingSection.style.display = 'block';
    loadingSection.classList.add('fade-in');
}

function hideLoading() {
    loadingSection.style.display = 'none';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function hideAnalysis() {
    analysisSection.style.display = 'none';
}

// Form submission
testForm.addEventListener('submit', (e) => {
    e.preventDefault();
    generateBtn.click();
});

// Enter key support
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
        // Don't submit on Enter, let user choose action
    }
});

// Initialize
console.log('Mobilise Test Automation Tool initialized');
