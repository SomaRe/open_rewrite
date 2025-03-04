document.addEventListener('DOMContentLoaded', () => {
    loadSettings(); // Load settings upon page load
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
        <div>${name}</div>
        <div>(Icon: ${data.icon}, Prompt: ${data.prompt})</div>
        <button onclick='editTone("${name}")'>Edit</button>
        <button onclick='deleteTone("${name}")'>Delete</button>
        <hr class="divider">
    `;
    return toneDiv;
}

function createFormatElement(name, data) {
    const formatDiv = document.createElement('div');
    formatDiv.classList.add('format');
    formatDiv.innerHTML = `
        <div>${name}</div>
        <div>(Icon: ${data.icon}, Prompt: ${data.prompt})</div>
        <button onclick='editFormat("${name}")'>Edit</button>
        <button onclick='deleteFormat("${name}")'>Delete</button>
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
    // Retrieve settings from input fields
    const apiKey = document.getElementById('api_key').value;
    const baseUrl = document.getElementById('base_url').value;
    const model = document.getElementById('model').value;
    const systemMessage = document.getElementById('system_message').value;
    // Retrieve tones

    // Retrieve Formats
    // Call the Python API to save settings
    pywebview.api.save_settings({ // call Python API with settings object.
        api_key: apiKey,
        base_url: baseUrl,
        model: model,
        system_message: systemMessage
    }).then(()=>{
        console.log("Saved ok");
    });
}

function resetToDefaults() {
    pywebview.api.reset_to_defaults();
    // After reset, reload the settings in the HTML
    loadSettings();
}