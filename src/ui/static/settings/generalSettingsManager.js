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
        
        if (status === 'enabled') {
            toggle.checked = true;
        } else {
            toggle.checked = false;
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
