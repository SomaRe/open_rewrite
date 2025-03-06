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
        const name = toneElement.dataset.name;
        const icon = toneElement.querySelector('.tone-icon').src;
        const prompt = toneElement.querySelector('.tone-prompt').textContent;
        settings.tones[name] = { icon: icon, prompt: prompt };
    });
    
    // Save formats
    document.querySelectorAll('.format').forEach(formatElement => {
        const name = formatElement.dataset.name;
        const icon = formatElement.querySelector('.format-icon').src;
        const prompt = formatElement.querySelector('.format-prompt').textContent;
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
    toneDiv.dataset.name = name;
    toneDiv.innerHTML = `
        <div class="flex items-center justify-between mb-2">
            <div class="flex items-center">
                <img class="w-6 h-6 mr-2 tone-icon" src="${data.icon}" alt="${name}">
                <span class="font-medium tone-name">${name}</span>
            </div>
            <div>
                <button class="edit-button bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onclick="editTone(this.parentNode.parentNode.parentNode)">Edit</button>
                <button class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded" onclick='deleteTone("${name}")'>
                    <img class="w-6" src="static/material_icons_round/content/round_clear_black_48dp_white.png" alt="Delete">
                </button>
            </div>
        </div>
        <div class="mb-2">
            <label class="block mb-1 font-medium">Prompt:</label>
            <div class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded tone-prompt">${data.prompt}</div>
        </div>
    `;
    return toneDiv;
}

function createFormatElement(name, data) {
    const formatDiv = document.createElement('div');
    formatDiv.classList.add('mb-4', 'pb-4', 'border-b', 'border-zinc-700', 'format');
    formatDiv.dataset.name = name;
    formatDiv.innerHTML = `
        <div class="flex items-center justify-between mb-2">
            <div class="flex items-center">
                <img class="w-6 h-6 mr-2 format-icon" src="${data.icon}" alt="${name}">
                <span class="font-medium format-name">${name}</span>
            </div>
            <div>
                <button class="edit-button bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onclick="editFormat(this.parentNode.parentNode.parentNode)">Edit</button>
                <button class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded" onclick='deleteFormat("${name}")'>
                    <img class="w-6" src="static/material_icons_round/content/round_clear_black_48dp_white.png" alt="Delete">
                </button>
            </div>
        </div>
        <div class="mb-2">
            <label class="block mb-1 font-medium">Prompt:</label>
            <div class="w-full p-2 bg-zinc-900 border border-zinc-700 rounded format-prompt">${data.prompt}</div>
        </div>
    `;
    return formatDiv;
}

// Function to show the "add new Tone" form
function showNewToneForm() {
    const form = document.getElementById('new-tone-form');
    form.classList.remove('hidden');  // remove `hidden` class
}

// Function to hide the "add new Tone" form
function hideNewToneForm() {
    const form = document.getElementById('new-tone-form');
    form.classList.add('hidden');  // and add `hidden` class back...hide.

    //clear fields
    document.getElementById('new-tone-name').value   = "";
    document.getElementById('new-tone-icon').value   = "";
    document.getElementById('new-tone-prompt').value = "";

}

// Function to add a new tone
function addNewTone() {
    const name = document.getElementById('new-tone-name').value;
    const icon = document.getElementById('new-tone-icon').value;
    const prompt = document.getElementById('new-tone-prompt').value;

    if (name && icon && prompt) {
        const newTone = { icon: icon, prompt: prompt };
        // Dynamically add the new tone to the tones-list
        const tonesList = document.getElementById('tones-list');
        const toneDiv = createToneElement(name, newTone);
        tonesList.appendChild(toneDiv);
        hideNewToneForm();
    } else {
        alert('Please fill in all fields for the new tone.');
    }
}

//Edit a Tone
function editTone(toneElement){
    console.log("Edit a Tone");

}

// Function to delete a tone
function deleteTone(name) {
    document.querySelectorAll('.tone').forEach(toneElement => {
        if (toneElement.dataset.name === name) {
            toneElement.remove();
        }
    });
}

// Function to show the "add new Format" form
function showNewFormatForm() {
    const form = document.getElementById('new-format-form');
    form.classList.remove('hidden');
}

// Function to hide the "add new Format" form
function hideNewFormatForm() {
    const form = document.getElementById('new-format-form');
    form.classList.add('hidden');

    // Clear fields
    document.getElementById('new-format-name').value = "";
    document.getElementById('new-format-icon').value = "";
    document.getElementById('new-format-prompt').value = "";
}

// Function to add a new format
function addNewFormat() {
    const name = document.getElementById('new-format-name').value;
    const icon = document.getElementById('new-format-icon').value;
    const prompt = document.getElementById('new-format-prompt').value;

    if (name && icon && prompt) {
        const newFormat = { icon: icon, prompt: prompt };

        // Dynamically add the new format to the formats-list
        const formatsList = document.getElementById('formats-list');
        const formatDiv = createFormatElement(name, newFormat);
        formatsList.appendChild(formatDiv);
        hideNewFormatForm();
    } else {
        alert('Please fill in all fields for the new format.');
    }
}

// Function to delete a format
function deleteFormat(name) {
    document.querySelectorAll('.format').forEach(formatElement => {
        if (formatElement.dataset.name === name) {
            formatElement.remove();
        }
    });
}
