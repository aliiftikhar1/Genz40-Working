// main.js
document.addEventListener('DOMContentLoaded', function () {
    // Tab switching logic
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = {
        roller: document.getElementById('roller-content'),
        'roller-plus': document.getElementById('roller-plus-content'),
        'turnkey-minus': document.getElementById('turnkey-minus-content')
    };

    // Hide all tab contents initially
    Object.values(tabContents).forEach(content => {
        if (content) content.classList.add('hidden');
    });

    // Show the default tab (e.g., "roller")
    if (tabContents.roller) {
        tabContents.roller.classList.remove('hidden');
    }

    // Add click event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');

            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active-tab'));
            // Add active class to the clicked button
            button.classList.add('active-tab');

            // Hide all tab contents
            Object.values(tabContents).forEach(content => {
                if (content) content.classList.add('hidden');
            });

            // Show the selected tab content
            const targetContent = tabContents[tabId];
            if (targetContent) {
                targetContent.classList.remove('hidden');
            }
        });
    });

    // Initialize forms
    if (document.getElementById('rollerForm')) {
        initRollerForm(); // Defined in rollerForm.js
    }
    
    if (document.getElementById('rollerPlusForm')) {
        initRollerPlusForm(); // Defined in rollerplusform.js
    }
});