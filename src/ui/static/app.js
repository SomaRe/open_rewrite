// Global variables
let currentText = '';
let currentResult = '';

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    function checkPyWebView() {
        if (typeof pywebview !== 'undefined') {
            loadOptions();
        } else {
            setTimeout(checkPyWebView, 50); // Check again after 50ms
        }
    }
    checkPyWebView();
});

// Load options from settings
function loadOptions() {
    console.log('Attempting to get settings');
    pywebview.api.get_settings().then(settings => {
        console.log('Settings received:', settings);
        
        // Load tones
        const tonesContainer = document.getElementById('tones-container');
        tonesContainer.innerHTML = '';
        
        Object.entries(settings.tones).forEach(([name, data]) => {
            const button = createOptionButton(name, data.icon, 'tones');
            tonesContainer.appendChild(button);
        });
        
        // Load formats
        const formatsContainer = document.getElementById('formats-container');
        formatsContainer.innerHTML = '';
        
        Object.entries(settings.formats).forEach(([name, data]) => {
            const button = createOptionButton(name, data.icon, 'formats');
            formatsContainer.appendChild(button);
        });
    }).catch(error => {
        console.error('Error getting settings:', error);
    });
}

// Create an option button
function createOptionButton(name, icon, category) {
    const button = document.createElement('button');
    button.className = 'option-btn';
    button.innerHTML = `
        <span class="material-icons-round option-icon">${icon}</span>
        <span class="option-text">${name}</span>
    `;
    
    button.addEventListener('click', () => {
        selectOption(name, category);
    });
    
    return button;
}

// Handle option selection
function selectOption(option, category) {
    document.getElementById('result-title').textContent = option;
    document.getElementById('options-view').classList.add('hidden');
    document.getElementById('result-view').classList.remove('hidden');
    
    showLoading();
    
    // Call the Python API to rewrite the text
    pywebview.api.rewrite_text(currentText, option, category);
}

function openSettings() {
    pywebview.api.open_settings_window();
}

// Show text in the UI
function showText(text) {
    currentText = text;
    document.getElementById('options-view').classList.remove('hidden');
    document.getElementById('result-view').classList.add('hidden');
}

// Show options view
function showOptionsView() {
    document.getElementById('options-view').classList.remove('hidden');
    document.getElementById('result-view').classList.add('hidden');
}

// Show loading indicator
function showLoading() {
    document.getElementById('loading-indicator').classList.remove('hidden');
    document.getElementById('result-text').textContent = '';
}

// Hide loading indicator
function hideLoading() {
    document.getElementById('loading-indicator').classList.add('hidden');
}

// Show result
function showResult(result) {
    currentResult = result;
    document.getElementById('result-text').textContent = result;
    hideLoading();
}

// Show error
function showError(error) {
    document.getElementById('result-text').textContent = `Error: ${error}`;
    hideLoading();
}

// Copy result to clipboard
function copyResult() {
    if (currentResult) {
        pywebview.api.copy_to_clipboard(currentResult);
    }
}

// Replace selected text with result
function replaceResult() {
    if (currentResult) {
        pywebview.api.replace_text(currentResult);
    }
}
