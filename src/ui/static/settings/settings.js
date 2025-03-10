import * as IconSelector from './iconSelector.js';
import * as SettingsManager from './settingsManager.js';

// Expose functions to the global namespace
const exportedFunctions = {
  openIconSelector: IconSelector.openIconSelector,
  closeIconSelector: IconSelector.closeIconSelector,
  showSection: SettingsManager.showSection,
  checkStartupStatus: SettingsManager.checkStartupStatus,
  toggleStartup: SettingsManager.toggleStartup,
  loadSettings: SettingsManager.loadSettings,
  saveSettings: SettingsManager.saveSettings,
  addNewTone: SettingsManager.addNewTone,
  hideNewToneForm: SettingsManager.hideNewToneForm,
  showNewToneForm: SettingsManager.showNewToneForm,
  editTone: SettingsManager.editTone,
  deleteTone: SettingsManager.deleteTone,
  addNewFormat: SettingsManager.addNewFormat,
  hideNewFormatForm: SettingsManager.hideNewFormatForm,
  showNewFormatForm: SettingsManager.showNewFormatForm,
  editFormat: SettingsManager.editFormat,
  deleteFormat: SettingsManager.deleteFormat,
  resetToDefaults: SettingsManager.resetToDefaults
};

for (const [name, func] of Object.entries(exportedFunctions)) {
  window[name] = func;
}

document.addEventListener('DOMContentLoaded', () => {
    function initializeSettings() {
        SettingsManager.loadSettings();
        SettingsManager.showSection('openai');
    }

    if (window.pywebview) {
        initializeSettings();
    } else {
        window.addEventListener('pywebviewready', initializeSettings);
    }
});
