import * as IconSelector from './iconSelector.js';
import * as GeneralSettings from './generalSettingsManager.js';
import * as ToneFormatManager from './toneFormatManager.js';

// Expose functions to the global namespace
const exportedFunctions = {
  openIconSelector: IconSelector.openIconSelector,
  closeIconSelector: IconSelector.closeIconSelector,
  ...GeneralSettings,
  ...ToneFormatManager
};

for (const [name, func] of Object.entries(exportedFunctions)) {
  window[name] = func;
}

document.addEventListener('DOMContentLoaded', () => {
    function initializeSettings() {
        GeneralSettings.loadSettings();
        GeneralSettings.showSection('openai');
    }

    if (window.pywebview) {
        initializeSettings();
    } else {
        window.addEventListener('pywebviewready', initializeSettings);
    }
});
