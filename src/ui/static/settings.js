document.addEventListener('DOMContentLoaded', () => {
    function initializeSettings() {
        loadSettings();
    }

    if (window.pywebview) {
        initializeSettings();
    } else {
        window.addEventListener('pywebviewready', initializeSettings);
    }
});

function loadSettings() {

    pywebview.api.get_settings().then(settings => {
        console.log("settings: ", settings)
        // Load OpenAI settings
        document.getElementById('api_key').value = settings.api_key || '';
        document.getElementById('base_url').value = settings.base_url || 'https://api.openai.com/v1';
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

function saveSettings() {
    const settings = {
        api_key: document.getElementById('api_key').value,
        base_url: document.getElementById('base_url').value,
        model: document.getElementById('model').value,
        system_message: document.getElementById('system_message').value,
        tones: {},
        formats: {}
    };

    // Save tones
    document.querySelectorAll('.tone').forEach(toneElement => {
        const name = toneElement.querySelector('.tone-name').value;
        const icon = toneElement.querySelector('.tone-icon').value;
        const prompt = toneElement.querySelector('.tone-prompt').value;
        settings.tones[name] = { icon: icon, prompt: prompt };
    });
    
    // Save formats
    document.querySelectorAll('.format').forEach(formatElement => {
        const name = formatElement.querySelector('.format-name').value;
        const icon = formatElement.querySelector('.format-icon').value;
        const prompt = formatElement.querySelector('.format-prompt').value;
        settings.formats[name] = { icon: icon, prompt: prompt };
    });

    pywebview.api.save_settings(settings).then(() => {
        alert('Settings saved!');
        loadSettings();
    }).catch(error => {
        console.error("Error saving settings:", error);
    });
}
function createToneElement(name, data) {
    const toneDiv = document.createElement('div');
    toneDiv.classList.add('mb-4', 'pb-4', 'border-b', 'border-zinc-700', 'tone');
    toneDiv.innerHTML = `
        <div class="mb-2">
            <label class="block mb-1 font-medium">Name:</label>
            <input type="text" class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded tone-name" value="${name}">
        </div>
        <div class="mb-2">
            <label class="block mb-1 font-medium">Icon:</label>
            <input type="text" class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded tone-icon" value="${data.icon}">
        </div>
        <div class="mb-2">
            <label class="block mb-1 font-medium">Prompt:</label>
            <textarea class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded tone-prompt">${data.prompt}</textarea>
        </div>
        <button class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded" onclick='deleteTone("${name}")'>
            <img class="w-6" src="static/material_icons_round/content/round_clear_black_48dp_white.png" alt="Delete">
        </button>
    `;
    return toneDiv;
}

function createFormatElement(name, data) {
    const formatDiv = document.createElement('div');
    formatDiv.classList.add('mb-4', 'pb-4', 'border-b', 'border-zinc-700', 'format');
    formatDiv.innerHTML = `
        <div class="mb-2">
            <label class="block mb-1 font-medium">Name:</label>
            <input type="text" class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded format-name" value="${name}">
        </div>
        <div class="mb-2">
            <label class="block mb-1 font-medium">Icon:</label>
            <input type="text" class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded format-icon" value="${data.icon}">
        </div>
        <div class="mb-2">
            <label class="block mb-1 font-medium">Prompt:</label>
            <textarea class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded format-prompt">${data.prompt}</textarea>
        </div>
        <button class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded" onclick='deleteFormat("${name}")'>
            <img class="w-6" src="static/material_icons_round/content/round_clear_black_48dp_white.png" alt="Delete">
        </button>
    `;
    return formatDiv;
}

// Function to show the "add new Tone" form
function show_new_tone_form() {
    const form = document.getElementById('new_tone_form');
    form.classList.remove('hidden');  // remove `hidden` class
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

// Function to add a new tone
function add_new_tone() {
    const name = document.getElementById('new_tone_name').value;
    const icon = document.getElementById('new_tone_icon').value;
    const prompt = document.getElementById('new_tone_prompt').value;

    if (name && icon && prompt) {
        const newTone = { icon: icon, prompt: prompt };
        // Dynamically add the new tone to the tones-list
        const tonesList = document.getElementById('tones-list');
        const toneDiv = createToneElement(name, newTone);
        tonesList.appendChild(toneDiv);
        hide_new_tone_form();
    } else {
        alert('Please fill in all fields for the new tone.');
    }
}

//Edit a Tone
function editTone(name){
    console.log("Edit a Tone");

}

// Function to delete a tone
function deleteTone(name) {
    document.querySelectorAll('.tone').forEach(toneElement => {
        const toneName = toneElement.querySelector('.tone-name').value;
        if (toneName === name) {
            toneElement.remove();
        }
    });
}

// Function to show the "add new Format" form
function show_new_format_form() {
    const form = document.getElementById('new_format_form');
    form.classList.remove('hidden');
}

// Function to hide the "add new Format" form
function hide_new_format_form() {
    const form = document.getElementById('new_format_form');
    form.classList.add('hidden');

    // Clear fields
    document.getElementById('new_format_name').value = "";
    document.getElementById('new_format_icon').value = "";
    document.getElementById('new_format_prompt').value = "";
}

// Function to add a new format
function add_new_format() {
    const name = document.getElementById('new_format_name').value;
    const icon = document.getElementById('new_format_icon').value;
    const prompt = document.getElementById('new_format_prompt').value;

    if (name && icon && prompt) {
        const newFormat = { icon: icon, prompt: prompt };

        // Dynamically add the new format to the formats-list
        const formatsList = document.getElementById('formats-list');
        const formatDiv = createFormatElement(name, newFormat);
        formatsList.appendChild(formatDiv);
        hide_new_format_form();
    } else {
        alert('Please fill in all fields for the new format.');
    }
}

// Function to delete a format
function deleteFormat(name) {
    document.querySelectorAll('.format').forEach(formatElement => {
        const formatName = formatElement.querySelector('.format-name').value;
        if (formatName === name) {
            formatElement.remove();
        }
    });
}
