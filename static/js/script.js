// Mobilise Test Automation Tool - Frontend JavaScript

let currentReportFile = null;
let currentExcelReportFile = null;
let recordingPollInterval = null;
let recordingActive = false;
let currentApiTests = [];
let currentApiResults = [];
let currentApiBaseUrl = '';
let currentApiReportFile = null;
let currentApiExecutionReportFile = null;

// Helper function for safe API calls
async function safeFetch(url, options = {}) {
    const response = await fetch(url, options);
    
    // Check if response is OK
    if (!response.ok) {
        const contentType = response.headers.get('content-type');
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        // Try to parse JSON error if available
        if (contentType && contentType.includes('application/json')) {
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If JSON parse fails, use status text
            }
        } else {
            // If not JSON, try to get text
            try {
                const errorText = await response.text();
                if (errorText && errorText.length < 200) {
                    errorMessage = errorText;
                }
            } catch (e) {
                // Use default error message
            }
        }
        
        const error = new Error(errorMessage);
        error.status = response.status;
        throw error;
    }
    
    // Check content type before parsing
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned non-JSON response. Please check the server logs.');
    }
    
    // Parse and return JSON
    return await response.json();
}

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
const startRecordingBtn = document.getElementById('startRecordingBtn');
const stopRecordingBtn = document.getElementById('stopRecordingBtn');
const recordingStatusChip = document.getElementById('recordingStatusChip');
const recordedStepsList = document.getElementById('recordedStepsList');
const recordedStepsCount = document.getElementById('recordedStepsCount');
const recordedScriptArea = document.getElementById('recordedScript');
const copyScriptBtn = document.getElementById('copyScriptBtn');
const downloadScriptBtn = document.getElementById('downloadScriptBtn');
const apiBaseUrlInput = document.getElementById('api_base_url');
const apiSpecInput = document.getElementById('apiSpecInput');
const generateApiBtn = document.getElementById('generateApiBtn');
const executeApiBtn = document.getElementById('executeApiBtn');
const clearApiBtn = document.getElementById('clearApiBtn');
const apiSummaryCard = document.getElementById('apiSummary');
const apiTestsList = document.getElementById('apiTestsList');
const downloadApiReportBtn = document.getElementById('downloadApiReportBtn');
const downloadApiExecutionBtn = document.getElementById('downloadApiExecutionBtn');
const apiTotalCount = document.getElementById('apiTotalCount');
const apiPositiveCount = document.getElementById('apiPositiveCount');
const apiNegativeCount = document.getElementById('apiNegativeCount');
const runHistoryList = document.getElementById('runHistoryList');

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
        const data = await safeFetch('/api/generate-tests', {
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
        
        if (data.success) {
            currentReportFile = data.report_file;
            currentExcelReportFile = data.excel_report_file || null;
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
        const data = await safeFetch('/api/analyze-website', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                website_url: websiteUrl
            })
        });
        
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
        const data = await safeFetch('/api/generate-and-execute', {
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
        const data = await safeFetch('/api/test-login', {
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

// Recording Controls
if (startRecordingBtn && stopRecordingBtn) {
    startRecordingBtn.addEventListener('click', () => {
        if (!recordingActive) {
            startRecording();
        }
    });

    stopRecordingBtn.addEventListener('click', () => {
        if (recordingActive) {
            stopRecording();
        }
    });
}

if (copyScriptBtn) {
    copyScriptBtn.addEventListener('click', () => {
        if (!recordedScriptArea) {
            return;
        }
        const scriptText = recordedScriptArea.value.trim();
        if (!scriptText) {
            alert('No script available to copy');
            return;
        }
        navigator.clipboard.writeText(scriptText)
            .then(() => alert('Script copied to clipboard'))
            .catch(() => alert('Unable to copy script'));
    });
}

if (downloadScriptBtn) {
    downloadScriptBtn.addEventListener('click', () => {
        if (!recordedScriptArea) {
            return;
        }
        const scriptText = recordedScriptArea.value.trim();
        if (!scriptText) {
            alert('No script available to download');
            return;
        }
        const blob = new Blob([scriptText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        link.download = `mobilise_recording_${timestamp}.py`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    });
}

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

// API Testing controls
if (generateApiBtn) {
    generateApiBtn.addEventListener('click', generateApiTests);
}

if (executeApiBtn) {
    executeApiBtn.addEventListener('click', executeApiTests);
}

if (clearApiBtn) {
    clearApiBtn.addEventListener('click', resetApiBuilder);
}

if (downloadApiReportBtn) {
    downloadApiReportBtn.addEventListener('click', () => downloadApiReport(currentApiReportFile));
}

if (downloadApiExecutionBtn) {
    downloadApiExecutionBtn.addEventListener('click', () => downloadApiReport(currentApiExecutionReportFile));
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
    refreshRunHistory();
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
    refreshRunHistory();
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

// Recording functions
async function startRecording() {
    if (!startRecordingBtn || !stopRecordingBtn) {
        return;
    }

    const websiteUrl = document.getElementById('website_url').value.trim();
    if (!websiteUrl) {
        alert('Please enter a website URL before recording');
        return;
    }

    setRecordingStatus('starting', 'Starting...');
    startRecordingBtn.disabled = true;
    stopRecordingBtn.disabled = true;
    try {
        const data = await safeFetch('/api/recording/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ website_url: websiteUrl })
        });
        if (data.success) {
            recordingActive = true;
            stopRecordingBtn.disabled = false;
            setRecordingStatus('recording', 'Recording');
            renderRecordedSteps([]);
            if (recordedScriptArea) {
                recordedScriptArea.value = '';
            }
            startRecordingPolling();
        } else {
            alert('Error: ' + (data.error || 'Unable to start recording'));
            resetRecordingControls();
        }
    } catch (error) {
        console.error(error);
        alert('Error: ' + error.message);
        resetRecordingControls();
    }
}

async function stopRecording() {
    if (!stopRecordingBtn || !startRecordingBtn) {
        return;
    }

    setRecordingStatus('stopping', 'Stopping...');
    stopRecordingBtn.disabled = true;
    try {
        const data = await safeFetch('/api/recording/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (data.success) {
            recordingActive = false;
            stopRecordingPolling();
            startRecordingBtn.disabled = false;
            const recording = data.recording || {};
            updateRecordingUI(recording);
            setRecordingStatus('idle', 'Idle');
        } else {
            alert('Error: ' + (data.error || 'Unable to stop recording'));
            stopRecordingBtn.disabled = false;
        }
    } catch (error) {
        console.error(error);
        alert('Error: ' + error.message);
        stopRecordingBtn.disabled = false;
    }
}

function startRecordingPolling() {
    fetchRecordingStatus();
    if (recordingPollInterval) {
        clearInterval(recordingPollInterval);
    }
    recordingPollInterval = setInterval(fetchRecordingStatus, 2000);
}

function stopRecordingPolling() {
    if (recordingPollInterval) {
        clearInterval(recordingPollInterval);
        recordingPollInterval = null;
    }
}

async function fetchRecordingStatus() {
    try {
        const data = await safeFetch('/api/recording/status', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (data.success && data.recording) {
            updateRecordingUI(data.recording);
            if (!data.recording.active) {
                stopRecordingPolling();
            }
        }
    } catch (error) {
        console.error('Recording status error', error);
    }
}

function updateRecordingUI(recording) {
    if (!recording) {
        return;
    }
    if (Array.isArray(recording.steps)) {
        renderRecordedSteps(recording.steps);
    }
    if (typeof recording.python_script === 'string' && recordedScriptArea) {
        if (recordingActive || !recordedScriptArea.value.trim()) {
            recordedScriptArea.value = recording.python_script;
        }
    }
}

function renderRecordedSteps(steps) {
    if (!recordedStepsList || !recordedStepsCount) {
        return;
    }
    recordedStepsList.innerHTML = '';
    recordedStepsCount.textContent = steps.length;

    if (!steps.length) {
        recordedStepsList.innerHTML = '<p class="muted-text">No steps captured yet.</p>';
        return;
    }

    steps.forEach(step => {
        const selector = escapeHtml(step.selector || '');
        const value = escapeHtml(step.value || '');
        const card = document.createElement('div');
        card.className = 'recording-step-card';
        card.innerHTML = `
            <div class="step-header">
                <span class="step-id">${step.step_id}</span>
                <span class="step-action">${step.action}</span>
            </div>
            <p><strong>Selector:</strong> ${selector}</p>
            ${step.value ? `<p><strong>Value:</strong> ${value}</p>` : ''}
        `;
        recordedStepsList.appendChild(card);
    });
}

function setRecordingStatus(state, label) {
    if (!recordingStatusChip) {
        return;
    }
    const icons = {
        idle: '<i class="fas fa-circle"></i>',
        recording: '<i class="fas fa-dot-circle"></i>',
        starting: '<i class="fas fa-sync fa-spin"></i>',
        stopping: '<i class="fas fa-sync fa-spin"></i>'
    };
    recordingStatusChip.innerHTML = `${icons[state] || icons.idle} ${label}`;
    recordingStatusChip.className = `status-chip status-${state}`;
}

function resetRecordingControls() {
    recordingActive = false;
    if (startRecordingBtn) {
        startRecordingBtn.disabled = false;
    }
    if (stopRecordingBtn) {
        stopRecordingBtn.disabled = true;
    }
    setRecordingStatus('idle', 'Idle');
    stopRecordingPolling();
}

// API Testing functions
async function generateApiTests() {
    if (!apiBaseUrlInput || !apiSpecInput) {
        return;
    }
    const baseUrl = apiBaseUrlInput.value.trim();
    const specText = apiSpecInput.value.trim();

    if (!baseUrl || !specText) {
        alert('Please provide API Base URL and OpenAPI JSON before generating tests');
        return;
    }

    showLoading('Generating API tests...', 'Parsing specification and preparing cases');
    try {
        const data = await safeFetch('/api/api-tests/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                base_url: baseUrl,
                spec: specText
            })
        });
        hideLoading();

        if (data.success) {
            currentApiTests = data.test_cases || [];
            currentApiResults = [];
            currentApiBaseUrl = baseUrl;
            currentApiReportFile = data.report_file || null;
            currentApiExecutionReportFile = null;

            renderApiTests(currentApiTests);
            updateApiSummaryCard(data.summary);
            if (executeApiBtn) {
                executeApiBtn.disabled = currentApiTests.length === 0;
            }
            if (downloadApiReportBtn) {
                downloadApiReportBtn.disabled = !currentApiReportFile;
            }
            if (downloadApiExecutionBtn) {
                downloadApiExecutionBtn.disabled = true;
            }
            refreshRunHistory();
        } else {
            alert('Error: ' + (data.error || 'Unable to generate API tests'));
        }
    } catch (error) {
        hideLoading();
        console.error(error);
        alert('Error: ' + error.message);
    }
}

async function executeApiTests() {
    if (!currentApiTests.length) {
        alert('Generate API tests before execution');
        return;
    }
    const baseUrl = currentApiBaseUrl || (apiBaseUrlInput ? apiBaseUrlInput.value.trim() : '');
    if (!baseUrl) {
        alert('API Base URL is required to execute tests');
        return;
    }

    showLoading('Executing API tests...', 'Sending HTTP requests');
    try {
        const data = await safeFetch('/api/api-tests/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                base_url: baseUrl,
                test_cases: currentApiTests
            })
        });
        hideLoading();

        if (data.success) {
            currentApiResults = (data.results && data.results.tests) || [];
            currentApiExecutionReportFile = data.report_file || null;
            renderApiTests(currentApiTests, currentApiResults);
            updateApiSummaryCard(data.results ? data.results.summary : null);
            if (downloadApiExecutionBtn) {
                downloadApiExecutionBtn.disabled = !currentApiExecutionReportFile;
            }
            refreshRunHistory();
        } else {
            alert('Error: ' + (data.error || 'Unable to execute API tests'));
        }
    } catch (error) {
        hideLoading();
        console.error(error);
        alert('Error: ' + error.message);
    }
}

function renderApiTests(tests, executionResults = []) {
    if (!apiTestsList) {
        return;
    }

    apiTestsList.innerHTML = '';
    if (!tests.length) {
        apiTestsList.innerHTML = '<p class="muted-text">API test cases will appear here after generation.</p>';
        return;
    }

    const resultsMap = {};
    executionResults.forEach(result => {
        resultsMap[result.test_id] = result;
    });

    tests.forEach(test => {
        const card = document.createElement('div');
        const categoryClass = test.category || '';
        card.className = `api-test-card ${categoryClass}`;
        const status = resultsMap[test.test_id];
        let statusHtml = '';
        if (status) {
            const badgeClass = status.status === 'PASS' ? 'api-status-pass' : 'api-status-fail';
            statusHtml = `<span class="api-status-badge ${badgeClass}">${status.status}</span>`;
        }

        const urlText = escapeHtml(test.url || test.path || '');
        const description = escapeHtml(test.description || '');

        card.innerHTML = `
            <div class="api-test-header">
                <span class="api-method">${test.method}</span>
                <span class="api-url">${urlText}</span>
                ${statusHtml}
            </div>
            <p><strong>Expected:</strong> ${test.expected_status}</p>
            <p>${description || 'No description supplied.'}</p>
        `;
        apiTestsList.appendChild(card);
    });
}

function updateApiSummaryCard(summary) {
    if (!apiSummaryCard || !apiTotalCount || !apiPositiveCount || !apiNegativeCount) {
        return;
    }
    if (!summary) {
        apiSummaryCard.style.display = 'none';
        return;
    }

    apiSummaryCard.style.display = 'block';
    const total = summary.total || 0;
    const positive = summary.positive ?? summary.passed ?? 0;
    const negative = summary.negative ?? summary.failed ?? 0;
    apiTotalCount.textContent = total;
    apiPositiveCount.textContent = positive;
    apiNegativeCount.textContent = negative;
}

function resetApiBuilder() {
    if (apiSpecInput) {
        apiSpecInput.value = '';
    }
    if (apiBaseUrlInput) {
        apiBaseUrlInput.value = '';
    }
    currentApiTests = [];
    currentApiResults = [];
    currentApiBaseUrl = '';
    currentApiReportFile = null;
    currentApiExecutionReportFile = null;
    renderApiTests([]);
    updateApiSummaryCard(null);
    if (executeApiBtn) {
        executeApiBtn.disabled = true;
    }
    if (downloadApiReportBtn) {
        downloadApiReportBtn.disabled = true;
    }
    if (downloadApiExecutionBtn) {
        downloadApiExecutionBtn.disabled = true;
    }
}

function downloadApiReport(fileName) {
    if (!fileName) {
        alert('No report available to download');
        return;
    }
    window.location.href = `/api/download-report/${fileName}`;
}

async function refreshRunHistory() {
    if (!runHistoryList) {
        return;
    }
    try {
        const data = await safeFetch('/api/run-history', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (data.success) {
            renderRunHistory(data.history || []);
        }
    } catch (error) {
        console.error('History fetch failed', error);
    }
}

function renderRunHistory(items) {
    if (!runHistoryList) {
        return;
    }
    runHistoryList.innerHTML = '';
    if (!items.length) {
        runHistoryList.innerHTML = '<p class="muted-text align-left">No runs logged yet.</p>';
        return;
    }
    const typeLabels = {
        ui_generation: 'UI Test Generation',
        ui_execution: 'UI Execution',
        api_generation: 'API Test Generation',
        api_execution: 'API Execution',
        recording_session: 'Recording Session'
    };
    items.forEach(item => {
        const wrapper = document.createElement('div');
        wrapper.className = 'history-item';
        const badgeClass = item.type && item.type.startsWith('api')
            ? 'api'
            : (item.type && item.type.startsWith('ui') ? 'ui' : 'recording');
        const label = typeLabels[item.type] || item.type || 'Activity';
        const timestamp = item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A';
        wrapper.innerHTML = `
            <div class="meta">
                <strong>${label}</strong>
                <span>${item.website_url || 'N/A'}</span>
            </div>
            <div class="meta" style="text-align: right;">
                <span>${timestamp}</span>
                <span class="history-badge ${badgeClass}">${badgeClass.toUpperCase()}</span>
            </div>
        `;
        runHistoryList.appendChild(wrapper);
    });
}

function escapeHtml(value) {
    if (typeof value !== 'string') {
        return '';
    }
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
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
refreshRunHistory();
console.log('Mobilise Test Automation Tool initialized');
