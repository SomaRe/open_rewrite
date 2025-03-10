export function showSection(section) {
    document.querySelectorAll('[id$="-section"]').forEach(el => {
        el.classList.add('hidden');
    });
    document.getElementById(`${section}-section`).classList.remove('hidden');

    document.querySelectorAll('nav button').forEach(button => {
        button.classList.remove('bg-zinc-700');
    });
    document.querySelector(`nav button[onclick="showSection('${section}')"]`).classList.add('bg-zinc-700');
}

export function checkStartupStatus() {
    pywebview.api.check_startup_status().then(status => {
        const toggle = document.getElementById('startup-toggle');
        const statusText = document.getElementById('startup-status');
        
        if (status === 'enabled') {
            toggle.checked = true;
            statusText.textContent = 'App will launch at startup';
        } else {
            toggle.checked = false;
            statusText.textContent = 'App will not launch at startup';
        }
    });
}

export function toggleStartup() {
    pywebview.api.toggle_startup().then(result => {
        if (result.success) {
            checkStartupStatus();
        } else {
            alert(result.message || 'Failed to update startup settings');
        }
    });
}

export function loadSettings() {
    pywebview.api.get_settings().then(settings => {
        checkStartupStatus();
        document.getElementById('api_key').value = settings.api_key || '';
        document.getElementById('base_url').value = settings.base_url || 'https://api.openai.com/v1';
        document.getElementById('model').value = settings.model || 'gpt-4o-mini';
        document.getElementById('system_message').value = settings.system_message || '';

        const tonesList = document.getElementById('tones-list');
        tonesList.innerHTML = '';
        Object.entries(settings.tones || {}).forEach(([name, data]) => {
            const toneDiv = createToneElement(name, data);
            tonesList.appendChild(toneDiv);
        });

        const formatsList = document.getElementById('formats-list');
        formatsList.innerHTML = '';
        Object.entries(settings.formats || {}).forEach(([name, data]) => {
            const formatDiv = createFormatElement(name, data);
            formatsList.appendChild(formatDiv);
        });
    });
}

export function saveSettings() {
    const settings = {
        api_key: document.getElementById('api_key').value,
        base_url: document.getElementById('base_url').value,
        model: document.getElementById('model').value,
        system_message: document.getElementById('system_message').value,
        tones: {},
        formats: {}
    };

    document.querySelectorAll('.tone').forEach(toneElement => {
        const name = toneElement.dataset.name;
        const fullIconPath = toneElement.querySelector('.tone-icon').src;
        const staticIndex = fullIconPath.indexOf('static/');
        const icon = staticIndex !== -1 ? fullIconPath.substring(staticIndex) : '';
        const prompt = toneElement.querySelector('.tone-prompt').textContent;
        settings.tones[name] = { icon: icon, prompt: prompt };
    });
    
    document.querySelectorAll('.format').forEach(formatElement => {
        const name = formatElement.dataset.name;
        const fullIconPath = formatElement.querySelector('.format-icon').src;
        const staticIndex = fullIconPath.indexOf('static/');
        const icon = staticIndex !== -1 ? fullIconPath.substring(staticIndex) : '';
        const prompt = formatElement.querySelector('.format-prompt').textContent;
        settings.formats[name] = { icon: icon, prompt: prompt };
    });

    pywebview.api.save_settings(settings).then(() => {
        if (!document.getElementById('new-tone-form').classList.contains('hidden') || 
            !document.getElementById('new-format-form').classList.contains('hidden')) {
            return;
        }
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
            <img class="w-6 h-6 mr 3 format-icon" src="${data.icon}" alt="${name}">
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

let originalToneElement = null;
export function showNewToneForm() {
    const form = document.getElementById('new-tone-form');
    form.classList.remove('hidden');
}

export function hideNewToneForm() {
    const form = document.getElementById('new-tone-form');
    form.classList.add('hidden');
    document.getElementById('new-tone-name').value   = "";
    document.getElementById('new-tone-icon').value   = "";
    document.getElementById('new-tone-prompt').value = "";
    if (originalToneElement) {
        const tonesList = document.getElementById('tones-list');
        tonesList.appendChild(originalToneElement);
        originalToneElement = null;
    }
}

export function addNewTone() {
    const name = document.getElementById('new-tone-name').value;
    const icon = document.getElementById('new-tone-icon').value;
    const prompt = document.getElementById('new-tone-prompt').value;

    if (name && icon && prompt) {
        const newTone = { icon: icon, prompt: prompt };
        const tonesList = document.getElementById('tones-list');
        const toneDiv = createToneElement(name, newTone);
        tonesList.appendChild(toneDiv);
        hideNewToneForm();
        saveSettings();
    } else {
        alert('Please fill in all fields for the new tone.');
    }
}

export function editTone(toneElement) {
    originalToneElement = toneElement.cloneNode(true);
    const name = toneElement.dataset.name;
    const icon = toneElement.querySelector('.tone-icon').src;
    const prompt = toneElement.querySelector('.tone-prompt').textContent;
    document.getElementById('new-tone-name').value = name;
    document.getElementById('new-tone-icon').value = icon;
    document.getElementById('new-tone-prompt').value = prompt;
    showNewToneForm();
    toneElement.remove();
}

export function deleteTone(name) {
    if (confirm(`Are you sure you want to delete the tone "${name}"?`)) {
        document.querySelectorAll('.tone').forEach(toneElement => {
            if (toneElement.dataset.name === name) {
                toneElement.remove();
                saveSettings();
            }
        });
    }
}

let originalFormatElement = null;
export function showNewFormatForm() {
    const form = document.getElementById('new-format-form');
    form.classList.remove('hidden');
    document.getElementById('new-format-name').value = "";
    document.getElementById('new-format-icon').value = "";
    document.getElementById('new-format-prompt').value = "";

    if (originalFormatElement) {
        const formatsList = document.getElementById('formats-list');
        formatsList.appendChild(originalFormatElement);
        originalFormatElement = null;
    }
}

export function hideNewFormatForm() {
    const form = document.getElementById('new-format-form');
    form.classList.add('hidden');
    document.getElementById('new-format-name').value = "";
    document.getElementById('new-format-icon'). value = "";
    document.getElementById('new-format-prompt').value = "";
    if (originalFormatElement) {
        const formatsList = document.getElementById('formats-list');
        formatsList.appendChild(originalFormatElement);
        originalFormatElement = null;
    }
}

export function addNewFormat() {
    const name = document.getElementById('new-format-name').value;
    const icon = document.getElementById('new-format-icon').value;
    const prompt = document.getElementById('new-format-prompt').value;

    if (name && icon && prompt) {
        const newFormat = { icon: icon, prompt: prompt };
        const formatsList = document.getElementById('formats-list');
        const formatDiv = createFormatElement(name, newFormat);
        formatsList.appendChild(formatDiv);
        hideNewFormatForm();
        saveSettings();
    } else {
        alert('Please fill in all fields for the new format.');
    }
}

export function editFormat(formatElement) {
    originalFormatElement = formatElement.cloneNode(true);
    const name = formatElement.dataset.name;
    const icon = formatElement.querySelector('.format-icon').src;
    const prompt = formatElement.querySelector('.format-prompt').textContent;
    document.getElementById('new-format-name').value = name;
    document.getElementById('new-format-icon').value = icon;
    document.getElementById('new-format-prompt').value = prompt;
    showNewFormatForm();
    formatElement.remove();
}

export function deleteFormat(name) {
    if (confirm(`Are you sure you want to delete the format "${name}"?`)) {
        document.querySelectorAll('.format').forEach(formatElement => {
            if (formatElement.dataset.name === name) {
                formatElement.remove();
                saveSettings();
            }
        });
    }
}

export function resetToDefaults() {
    if (confirm('Are you sure you want to reset all settings to default values? This cannot be undone.')) {
        pywebview.api.reset_to_defaults().then(() => {
            alert('Settings have been reset to defaults');
            loadSettings();
        }).catch(error => {
            console.error("Error resetting settings:", error);
            alert('Failed to reset settings');
        });
    }
}
