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
        document.getElementById('hotkey').value = settings.hotkey || '<ctrl>+r';
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
    pywebview.api.get_current_version().then(version => {
        document.getElementById('current-version-display').textContent = version || '?.?.?';
    });

    // Reset update status on load
    // document.getElementById('update-status').textContent = `Current Version: ${document.getElementById('current-version-display').textContent}`;
    document.getElementById('update-result').textContent = '';
    document.getElementById('release-notes-container').classList.add('hidden');
    document.getElementById('check-update-button').disabled = false;
    document.getElementById('check-update-button').textContent = 'Check for Updates';
}

export function checkForUpdate() {
    const checkButton = document.getElementById('check-update-button');
    const updateResult = document.getElementById('update-result');
    const releaseNotesContainer = document.getElementById('release-notes-container');
    const installButton = document.getElementById('install-update-button');

    checkButton.disabled = true;
    checkButton.textContent = 'Checking...';
    updateResult.textContent = 'Checking for updates...';
    releaseNotesContainer.classList.add('hidden'); // Hide previous notes/button

    pywebview.api.check_for_update().then(result => {
        checkButton.disabled = false;
        checkButton.textContent = 'Check for Updates';

        if (result.update_available) {
            updateResult.textContent = `Update available: Version ${result.latest_version}`;
            document.getElementById('release-notes-content').textContent = result.release_notes || 'No release notes provided.';
            releaseNotesContainer.classList.remove('hidden');

            // Remove previous listener if any, then add new one
            const newInstallButton = installButton.cloneNode(true); // Clone to remove listeners
            installButton.parentNode.replaceChild(newInstallButton, installButton);

            newInstallButton.textContent = `Download & Install v${result.latest_version}`;
            newInstallButton.onclick = () => { // Use arrow function to capture result.download_url
                promptAndUpdate(result.download_url, result.latest_version);
            };

        } else if (result.error) {
            updateResult.textContent = `Error: ${result.error}`;
        } else {
            updateResult.textContent = result.message || 'You are already running the latest version.';
        }
    }).catch(error => {
        console.error("Error calling check_for_update:", error);
        checkButton.disabled = false;
        checkButton.textContent = 'Check for Updates';
        updateResult.textContent = 'Failed to check for updates. See console for details.';
    });
}

function promptAndUpdate(downloadUrl, version) {
    const installButton = document.getElementById('install-update-button'); // Get the potentially new button
    if (confirm(`Are you sure you want to download and install version ${version}? The application will close and restart.`)) {
        installButton.disabled = true;
        installButton.textContent = 'Downloading...';
        document.getElementById('update-result').textContent = 'Downloading update, please wait...';

        pywebview.api.download_and_install_update(downloadUrl).then(installResult => {
            // This part might not be reached if the app exits quickly
            if (installResult.success) {
                // Usually the app closes before this is shown
                document.getElementById('update-result').textContent = 'Update process started. The app will now close.';
            } else {
                document.getElementById('update-result').textContent = `Update failed: ${installResult.error}`;
                installButton.disabled = false;
                installButton.textContent = `Download & Install v${version}`;
            }
        }).catch(error => {
            console.error("Error calling download_and_install_update:", error);
            document.getElementById('update-result').textContent = 'Update initiation failed. See console for details.';
            installButton.disabled = false;
            installButton.textContent = `Download & Install v${version}`;
        });
    }
}

export function saveSettings() {
    const settings = {
        hotkey: document.getElementById('hotkey').value,
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
