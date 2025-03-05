document.addEventListener('DOMContentLoaded', () => {
    // Function to execute after pywebview is ready
    function initializeSettings() {
        loadSettings(); // Load settings upon page load
    }

    // Check if pywebview is already ready
    if (window.pywebview) {
        initializeSettings();
    } else {
        // Wait for the pywebviewready event
        window.addEventListener('pywebviewready', initializeSettings);
    }
});

function loadSettings() {

    pywebview.api.get_settings().then(settings => {
        // Load OpenAI settings
        document.getElementById('api_key').value = settings.api_key || '';
        document.getElementById('base_url').value = settings.base_url || 'https://api.openai.com/v1/';
        document.getElementById('model').value = settings.model || 'gpt-4o-mini';

        // Load system message settings
        document.getElementById('system_message').value = settings.system_message || '';

        // Load tones
        const tonesList = document.getElementById('tones-list');
        tonesList.innerHTML = ''; // Clear existing list
        Object.entries(settings.tones || {}).forEach(([name, data]) => {
            const toneDiv = createToneElement(name, data);
            tonesList.appendChild(toneDiv);
        });

        // Load formats
        const formatsList = document.getElementById('formats-list');
        formatsList.innerHTML = ''; // Clear existing list
        Object.entries(settings.formats || {}).forEach(([name, data]) => {
            const formatDiv = createFormatElement(name, data);
            formatsList.appendChild(formatDiv);
        });
    });
}
function createToneElement(name, data) {
    const toneDiv = document.createElement('div');
    toneDiv.classList.add('tone');
    toneDiv.innerHTML = `
        <div class="setting-item">
            <label class="setting-label">Name:</label>
            <input type="text" class="setting-input tone-name" value="${name}">
        </div>
        <div class="setting-item">
            <label class="setting-label">Icon:</label>
            <input type="text" class="setting-input tone-icon" value="${data.icon}">
        </div>
        <div class="setting-item">
            <label class="setting-label">Prompt:</label>
            <textarea class="setting-textarea tone-prompt">${data.prompt}</textarea>
        </div>
        <button class="action-btn" onclick='deleteTone("${name}")'>Delete</button>
        <hr class="divider">
    `;
    return toneDiv;
}

function createFormatElement(name, data) {
    const formatDiv = document.createElement('div');
    formatDiv.classList.add('format');
    formatDiv.innerHTML = `
        <div class="setting-item">
            <label class="setting-label">Name:</label>
            <input type="text" class="setting-input format-name" value="${name}">
        </div>
        <div class="setting-item">
            <label class="setting-label">Icon:</label>
            <input type="text" class="setting-input format-icon" value="${data.icon}">
        </div>
        <div class="setting-item">
            <label class="setting-label">Prompt:</label>
            <textarea class="setting-textarea format-prompt">${data.prompt}</textarea>
        </div>
        <button class="action-btn" onclick='deleteFormat("${name}")'>Delete</button>
        <hr class="divider">
    `;
    return formatDiv;
}
// Function to show the "add new Tone" form
function show_new_tone_form() {
    const form = document.getElementById('new_tone_form');
    form.classList.remove('hidden');  // remove `hidden` class (display: none)
}

// Function to hide the "add new Tone" form
function hide_new_tone_form() {
    const form = document.getElementById('new_tone_form');
    form.classList.add('hidden');  // and add `hidden` class back...hide.

    //clear fields
    document.getElementById('new_tone_name').value   = "";
    document.getElementById('new_tone_icon').value   = "";
    document.getElementById('new_tone_prompt').value = "";

}

//Edit a Tone
function editTone(name){
    console.log("Edit a Tone");

}

//Function deleteTone
function deleteTone(name){
    console.log("Delete Tone");
}


//format new_format_form
function show_new_format_form() {
    const form = document.getElementById('new_format_form');
    form.classList.remove('hidden');  // remove `hidden` class (display: none)
}

// Function to hide the "add new Tone" form
function hide_new_format_form() {
    const form = document.getElementById('new_format_form');
    form.classList.add('hidden');  // and add `hidden` class back...hide.

    //clear fields
    document.getElementById('new_format_name').value   = "";
    document.getElementById('new_format_icon').value   = "";
    document.getElementById('new_format_prompt').value = "";

}

//Edit a format
function editFormat(name){
    console.log("Edit format func");
}

//Function delete Format
function deleteFormat(name){
    console.log("Delete Format");
}

function saveSettings() {
    // Retrieve all settings from input fields
    const settings = {
        api_key: document.getElementById('api_key').value,
        base_url: document.getElementById('base_url').value,
        model: document.getElementById('model').value,
        system_message: document.getElementById('system_message').value,
        tones: {},
        formats: {}
    };

    // Get all tones
    const toneElements = document.querySelectorAll('#tones-list .tone');
    toneElements.forEach(tone => {
        const name = tone.querySelector('input.tone-name').value;
        const icon = tone.querySelector('input.tone-icon').value;
        const prompt = tone.querySelector('textarea.tone-prompt').value;
        settings.tones[name] = { icon, prompt };
    });

    // Get all formats
    const formatElements = document.querySelectorAll('#formats-list .format');
    formatElements.forEach(format => {
        const name = format.querySelector('input.format-name').value;
        const icon = format.querySelector('input.format-icon').value;
        const prompt = format.querySelector('textarea.format-prompt').value;
        settings.formats[name] = { icon, prompt };
    });

    // Call the Python API to save settings
    pywebview.api.save_settings(settings).then(() => {
        console.log("Settings saved successfully");
        loadSettings(); // Reload to confirm changes
    }).catch(error => {
        console.error("Error saving settings:", error);
    });
}

function resetToDefaults() {
    pywebview.api.reset_to_defaults();
    // After reset, reload the settings in the HTML
    loadSettings();
}
