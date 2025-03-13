import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

// Global variables
let currentText = '';
let currentResult = '';

function focusInput() {
    const inputField = document.getElementById('custom-input-field');
    if (inputField) {
        inputField.focus();
    }
}
window.focusInput = focusInput;

// Expose functions to pywebview
window.handleSelectedText = handleSelectedText;
window.showResult = showResult;
window.showError = showError;

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    // Function to execute after pywebview is ready
    function initializeApp() {
        loadOptions();
        focusInput();
        
        // Add Enter key handler
        document.getElementById('custom-input-field').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendCustomRequest();
            }
        });
    
        // Close settings menu when clicking outside
        document.addEventListener('click', function(event) {
            const settingsMenu = document.getElementById('settings-menu');
            const settingsButton = document.querySelector('.relative button');
            if (!settingsMenu.contains(event.target) && !settingsButton.contains(event.target)) {
                settingsMenu.classList.add('hidden');
            }
        });
    }


    // Check if pywebview is already ready
    if (window.pywebview) {
        initializeApp();
    } else {
        // Wait for the pywebviewready event
        window.addEventListener('pywebviewready', initializeApp);
    }
});

// Load options from settings
function loadOptions() {
    console.log('Attempting to get settings');
    pywebview.api.get_settings().then(settings => {
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        // Load tones
        Object.entries(settings.tones).forEach(([name, data]) => {
            const button = createOptionButton(name, data.icon, 'tones');
            optionsContainer.appendChild(button);
        });

        // Add separator
        const separator = document.createElement('hr');
        separator.className = 'border-zinc-700 my-2';
        optionsContainer.appendChild(separator);

        // Load formats
        Object.entries(settings.formats).forEach(([name, data]) => {
            const button = createOptionButton(name, data.icon, 'formats');
            optionsContainer.appendChild(button);
        });
    }).catch(error => {
        console.error('Error getting settings:', error);
    });
}

function toggleSettingsMenu() {
    const menu = document.getElementById('settings-menu');
    menu.classList.toggle('hidden');
}

function exitApp() {
    pywebview.api.exit_app();
}


// Create an option button
function createOptionButton(name, icon, category) {
    const button = document.createElement('button');
    button.className = 'flex items-center w-full p-1 hover:bg-zinc-700 transition-colors text-left';
    button.innerHTML = `
        <img class="w-4 h-4 mr-2" src="${icon}" alt="${name}">
        <span class="text-sm">${name}</span>
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

function sendCustomRequest() {
    const customInput = document.getElementById('custom-input-field')?.value.trim();
    if (!customInput) {
        showError('Please enter a custom request');
        return;
    }
    
    document.getElementById('result-title').textContent = "Custom Request";
    document.getElementById('options-view').classList.add('hidden');
    document.getElementById('result-view').classList.remove('hidden');
    
    showLoading();
    
    pywebview.api.handle_custom_request(currentText, customInput);
}

function openSettings() {
    pywebview.api.open_settings_window();
}

// Handle selected text in the UI
function handleSelectedText(text) {
    currentText = text;
    document.getElementById('options-view').classList.remove('hidden');
    document.getElementById('result-view').classList.add('hidden');
    
    // Clear and focus the input field
    const inputField = document.getElementById('custom-input-field');
    if (inputField) {
        inputField.value = '';
        inputField.focus();
    }
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
    // Convert markdown to HTML using marked
    const htmlContent = marked.parse(result);
    document.getElementById('result-text').innerHTML = htmlContent;
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
        showText("");
    }
}
