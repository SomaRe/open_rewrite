// Icon Selector Functions
let currentIconField = null;

function openIconSelector(fieldId) {
    currentIconField = fieldId;
    loadIcons();
    document.getElementById('icon-selector-modal').classList.remove('hidden');
}

function closeIconSelector() {
    document.getElementById('icon-selector-modal').classList.add('hidden');
    currentIconField = null;
}

async function loadIcons() {
    try {
        const icons = await pywebview.api.get_available_icons();
        const iconGrid = document.getElementById('icon-grid');
        iconGrid.innerHTML = '';

        icons.forEach(icon => {
            const iconDiv = document.createElement('div');
            iconDiv.className = 'flex flex-col items-center p-2 cursor-pointer hover:bg-zinc-700 rounded';
            iconDiv.innerHTML = `
                <img class="w-8 h-8" src="static/${icon}" alt="${icon}">
                <span class="text-xs mt-1 text-center">${icon.split('/').pop()}</span>
            `;
            iconDiv.addEventListener('click', () => {
                document.getElementById(currentIconField).value = icon;
                closeIconSelector();
            });
            iconGrid.appendChild(iconDiv);
        });
    } catch (error) {
        console.error('Error loading icons:', error);
    }
}

// Close modal when clicking outside
document.addEventListener('click', (event) => {
    const modal = document.getElementById('icon-selector-modal');
    if (event.target === modal) {
        closeIconSelector();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    function initializeSettings() {
        loadSettings();
        showSection('general');
    }

    if (window.pywebview) {
        initializeSettings();
    } else {
        window.addEventListener('pywebviewready', initializeSettings);
    }
});

function showSection(section) {
    // Hide all sections
    document.querySelectorAll('[id$="-section"]').forEach(el => {
        el.classList.add('hidden');
    });
    
    // Show the selected section
    document.getElementById(`${section}-section`).classList.remove('hidden');
    
    // Update active state in sidebar
    document.querySelectorAll('nav button').forEach(button => {
        button.classList.remove('bg-zinc-700');
    });
    document.querySelector(`nav button[onclick="showSection('${section}')"]`).classList.add('bg-zinc-700');
}

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
    toneDiv.classList.add('bg-zinc-900', 'p-4', 'tone');
    toneDiv.dataset.name = name;
    toneDiv.innerHTML = `
        <div class="flex items-center mb-3">
            <img class="w-6 h-6 mr-3 tone-icon" src="${data.icon}" alt="${name}">
            <span class="font-semibold text-lg tone-name">${name}</span>
        </div>
        <div class="text-sm text-zinc-300 mb-4 tone-prompt line-clamp-3">${data.prompt}</div>
        <div class="flex justify-end space-x-2">
            <button class="bg-blue-700 hover:bg-blue-600 text-white font-medium py-1 px-2 rounded-md text-sm" onclick="editTone(this.parentNode.parentNode)">Edit</button>
            <button class="bg-red-700 hover:bg-red-600 text-white font-medium py-1 px-2 rounded-md text-sm" onclick='deleteTone("${name}")'>Delete</button>
        </div>
    `;
    return toneDiv;
}

function createFormatElement(name, data) {
    const formatDiv = document.createElement('div');
    formatDiv.classList.add('bg-zinc-900', 'p-4', 'format');
    formatDiv.dataset.name = name;
    formatDiv.innerHTML = `
        <div class="flex items-center mb-3">
            <img class="w-6 h-6 mr-3 format-icon" src="${data.icon}" alt="${name}">
            <span class="font-semibold text-lg format-name">${name}</span>
        </div>
        <div class="text-sm text-zinc-300 mb-4 format-prompt line-clamp-3">${data.prompt}</div>
        <div class="flex justify-end space-x-2">
            <button class="bg-blue-700 hover:bg-blue-600 text-white font-medium py-1 px-2 rounded-md text-sm" onclick="editFormat(this.parentNode.parentNode)">Edit</button>
            <button class="bg-red-700 hover:bg-red-600 text-white font-medium py-1 px-2 rounded-md text-sm" onclick='deleteFormat("${name}")'>Delete</button>
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

    // Restore original tone if it exists
    if (originalToneElement) {
        const tonesList = document.getElementById('tones-list');
        tonesList.appendChild(originalToneElement);
        originalToneElement = null;
    }
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

// Store original tone element when editing
let originalToneElement = null;

//Edit a Tone
function editTone(toneElement) {
    // Store the original element
    originalToneElement = toneElement.cloneNode(true);
    
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

//Edit a Format
function editFormat(formatElement) {
    // Store the original element
    originalFormatElement = formatElement.cloneNode(true);
    
    const name = formatElement.dataset.name;
    const icon = formatElement.querySelector('.format-icon').src;
    const prompt = formatElement.querySelector('.format-prompt').textContent;

    // Populate the new format form with existing data
    document.getElementById('new-format-name').value = name;
    document.getElementById('new-format-icon').value = icon;
    document.getElementById('new-format-prompt').value = prompt;

    // Show the form
    showNewFormatForm();

    // Remove the original format
    formatElement.remove();
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

// Store original format element when editing
let originalFormatElement = null;

// Function to hide the "add new Format" form
function hideNewFormatForm() {
    const form = document.getElementById('new-format-form');
    form.classList.add('hidden');

    // Clear fields
    document.getElementById('new-format-name').value = "";
    document.getElementById('new-format-icon').value = "";
    document.getElementById('new-format-prompt').value = "";

    // Restore original format if it exists
    if (originalFormatElement) {
        const formatsList = document.getElementById('formats-list');
        formatsList.appendChild(originalFormatElement);
        originalFormatElement = null;
    }
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
