export function createItemElement(name, data, type) {
    const itemDiv = document.createElement('div');
    itemDiv.classList.add('bg-zinc-900', 'p-4', type);
    itemDiv.dataset.name = name;
    itemDiv.innerHTML = `
        <div class="flex items-center mb-3">
            <img class="w-6 h-6 mr-3 ${type}-icon" src="${data.icon}" alt="${name}">
            <span class="font-semibold text-lg ${type}-name">${name}</span>
        </div>
        <div class="text-sm text-zinc-300 mb-4 ${type}-prompt line-clamp-3">${data.prompt}</div>
        <div class="flex justify-end space-x-2">
            <button class="bg-blue-700 hover:bg-blue-600 text-white font-medium py-1 px-2 rounded-md text-sm" onclick="edit${type.charAt(0).toUpperCase() + type.slice(1)}(this.parentNode.parentNode)">Edit</button>
            <button class="bg-red-700 hover:bg-red-600 text-white font-medium py-1 px-2 rounded-md text-sm" onclick='delete${type.charAt(0).toUpperCase() + type.slice(1)}("${name}")'>Delete</button>
        </div>
    `;
    return itemDiv;
}

export function createToneElement(name, data) {
    return createItemElement(name, data, 'tone');
}

export function createFormatElement(name, data) {
    return createItemElement(name, data, 'format');
}

let originalToneElement = null;
export function showNewToneForm() {
    const form = document.getElementById('new-tone-form');
    form.classList.remove('hidden');
    
    if (originalToneElement) {
        const tonesList = document.getElementById('tones-list');
        tonesList.appendChild(originalToneElement);
        originalToneElement = null;
    }
}

export function hideNewToneForm() {
    hideNewItemForm('tone');
}

export function addNewTone() {
    addNewItem('tone');
}

export function editTone(toneElement) {
    originalToneElement = toneElement.cloneNode(true);
    const name = toneElement.dataset.name;
    const icon = toneElement.querySelector('.tone-icon').src;
    const prompt = toneElement.querySelector('.tone-prompt').textContent;
    document.getElementById('new-tone-name').value = name;
    document.getElementById('new-tone-icon-preview').src = icon;
    document.getElementById('new-tone-icon-preview').style.display = 'block';
    document.getElementById('new-tone-prompt').value = prompt;
    showNewToneForm();
    toneElement.remove();
}

export function deleteTone(name) {
    if (confirm(`Are you sure you want to delete the tone "${name}"?`)) {
        document.querySelectorAll('.tone').forEach(toneElement => {
            if ( toneElement.dataset.name === name) {
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
    document.getElementById('new-format-icon-preview').src = "";
    document.getElementById('new-format-icon-preview').style.display = 'none';
    document.getElementById('new-format-prompt').value = "";

    if (originalFormatElement) {
        const formatsList = document.getElementById('formats-list');
        formatsList.appendChild(originalFormatElement);
        originalFormatElement = null;
    }
}

function hideNewItemForm(type) {
    const form = document.getElementById(`new-${type}-form`);
    form.classList.add('hidden');
    document.getElementById(`new-${type}-name`).value = "";
    document.getElementById(`new-${type}-icon-preview`).src = "";
    document.getElementById(`new-${type}-icon-preview`).style.display = 'none';
    document.getElementById(`new-${type}-prompt`).value = "";
    if (window[`original${type.charAt(0).toUpperCase() + type.slice(1)}Element`]) {
        const list = document.getElementById(`${type}s-list`);
        list.appendChild(window[`original${type.charAt(0).toUpperCase() + type.slice(1)}Element`]);
        window[`original${type.charAt(0).toUpperCase() + type.slice(1)}Element`] = null;
    }
}

export function hideNewFormatForm() {
    hideNewItemForm('format');
}

function addNewItem(type) {
    const name = document.getElementById(`new-${type}-name`).value;
    const icon = document.getElementById(`new-${type}-icon-preview`).src;
    const prompt = document.getElementById(`new-${type}-prompt`).value;

    if (name && icon && prompt) {
        const newItem = { icon: icon, prompt: prompt };
        const list = document.getElementById(`${type}s-list`);
        const itemDiv = createItemElement(name, newItem, type);
        list.appendChild(itemDiv);
        hideNewItemForm(type);
        saveSettings();
    } else {
        alert(`Please fill in all fields for the new ${type}.`);
    }
}

export function addNewFormat() {
    addNewItem('format');
}

export function editFormat(formatElement) {
    originalFormatElement = formatElement.cloneNode(true);
    const name = formatElement.dataset.name;
    const icon = formatElement.querySelector('.format-icon').src;
    const prompt = formatElement.querySelector('.format-prompt').textContent;
    document.getElementById('new-format-name').value = name;
    document.getElementById('new-format-icon-preview').src = icon;
    document.getElementById('new-format-icon-preview').style.display = 'block';
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
