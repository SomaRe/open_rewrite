let currentIconField = null;
let currentCategory = null;

export function openIconSelector(type) {
    currentIconField = type;
    loadIcons();
    document.getElementById('icon-selector-modal').classList.remove('hidden');
}

export function closeIconSelector() {
    document.getElementById('icon-selector-modal').classList.add('hidden');
    currentIconField = null;
}

export async function loadIcons() {
    try {
        const iconsByCategory = await pywebview.api.get_available_icons();
        const categories = Object.keys(iconsByCategory);
        
        // Load category tabs
        const categoryTabs = document.getElementById('icon-categories');
        const tabsContainer = categoryTabs.querySelector('div');
        tabsContainer.innerHTML = '';
        categories.forEach(category => {
            const tab = document.createElement('button');
            tab.className = 'px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap';
            tab.textContent = category;
            tab.addEventListener('click', () => showCategoryIcons(category, iconsByCategory[category]));
            
            if (!currentCategory) {
                tab.classList.add('bg-zinc-700', 'text-white');
                currentCategory = category;
            } else {
                tab.classList.add('text-zinc-400', 'hover:text-white');
            }
            tabsContainer.appendChild(tab);
        });

        if (categories.length > 0) {
            showCategoryIcons(currentCategory, iconsByCategory[currentCategory]);
        }
    } catch (error) {
        console.error('Error loading icons:', error);
    }
}

export function showCategoryIcons(category, icons) {
    const iconGrid = document.getElementById('icon-grid');
    iconGrid.innerHTML = '';
    
    // Add click handler for icons
    const handleIconClick = (iconSrc) => {
        if (currentIconField === 'tone') {
            const preview = document.getElementById('new-tone-icon-preview');
            preview.src = iconSrc;
            preview.style.display = 'block';
        } else if (currentIconField === 'format') {
            const preview = document.getElementById('new-format-icon-preview');
            preview.src = iconSrc;
            preview.style.display = 'block';
        }
        closeIconSelector();
    };

    const categoryTabs = document.getElementById('icon-categories');
    categoryTabs.querySelectorAll('button').forEach(tab => {
        if (tab.textContent === category) {
            tab.classList.add('bg-zinc-700', 'text-white');
            tab.classList.remove('text-zinc-400', 'hover:text-white');
        } else {
            tab.classList.remove('bg-zinc-700', 'text-white');
            tab.classList.add('text-zinc-400', 'hover:text-white');
        }
    });

    icons.forEach(icon => {
        const iconDiv = document.createElement('div');
        iconDiv.className = 'flex flex-col items-center p-2 cursor-pointer hover:bg-zinc-700 rounded';
        iconDiv.innerHTML = `
            <img class="w-8 h-8" src="static/${icon}" alt="${icon}">
        `;
        iconDiv.addEventListener('click', () => handleIconClick("static/" + icon));
        iconGrid.appendChild(iconDiv);
    });

    currentCategory = category;
}

// Close modal when clicking outside
document.addEventListener('click', (event) => {
    const modal = document.getElementById('icon-selector-modal');
    if (event.target === modal) {
        closeIconSelector();
    }
});
