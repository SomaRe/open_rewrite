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
    toneDiv.classList.add('bg-zinc-900', 'border', 'border-zinc-700', 'rounded-lg', 'p-4', 'tone');
    toneDiv.dataset.name = name;
    toneDiv.innerHTML = `
        <div class="flex items-center mb-3">
            <img class="w-8 h-8 mr-3 tone-icon" src="${data.icon}" alt="${name}">
            <span class="font-semibold text-lg tone-name">${name}</span>
        </div>
        <div class="text-sm text-zinc-300 mb-4 tone-prompt">${data.prompt}</div>
        <div class="flex justify-end space-x-2">
            <button class="text-blue-400 hover:text-blue-300 font-medium" onclick="editTone(this.parentNode.parentNode)">Edit</button>
            <button class="text-red-400 hover:text-red-300 font-medium" onclick='deleteTone("${name}")'>Delete</button>
        </div>
    `;
    return toneDiv;
}

function createFormatElement(name, data) {
    const formatDiv = document.createElement('div');
    formatDiv.classList.add('bg-zinc-900', 'border', 'border-zinc-700', 'rounded-lg', 'p-4', 'format');
    formatDiv.dataset.name = name;
    formatDiv.innerHTML = `
        <div class="flex items-center mb-3">
            <img class="w-8 h-8 mr-3 format-icon" src="${data.icon}" alt="${name}">
            <span class="font-semibold text-lg format-name">${name}</span>
        </div>
        <div class="text-sm text-zinc-300 mb-4 format-prompt">${data.prompt}</div>
        <div class="flex justify-end space-x-2">
            <button class="text-blue-400 hover:text-blue-300 font-medium" onclick="editFormat(this.parentNode.parentNode)">Edit</button>
            <button class="text-red-400 hover:text-red-300 font-medium" onclick='deleteFormat("${name}")'>Delete</button>
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
function editTone(toneElement) {
    const name = toneElement.dataset.name;
    const icon = toneElement.querySelector('.tone-icon').src;
    const prompt = toneElement.querySelector('.tone-prompt').textContent;

    // Populate the new tone form with existing data
    document.getElementById('new-tone-name').value = name;
    document.getElementById('new-tone-icon').value = icon;
    document.getElementById('new-tone-prompt').value = prompt;

    // Show the form
    showNewToneForm();

    // Remove the original tone
    toneElement.remove();
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
