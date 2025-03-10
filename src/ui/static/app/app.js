// Global variables
let currentText = '';
let currentResult = '';

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    // Function to execute after pywebview is ready
    function initializeApp() {
        loadOptions();
    
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
        showText("");
    }
}