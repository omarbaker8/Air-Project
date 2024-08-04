document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Drawer functionality
    const openDrawerButton = document.getElementById('addNewReading');
    const closeDrawerButton = document.getElementById('close-drawer');
    const drawer = document.getElementById('reading-drawer');
    const noConditionModal = document.getElementById('no-condition-warning');

    openDrawerButton.addEventListener('click', () => {
        if (noConditionModal) {
            noConditionModal.classList.remove('hidden');
            return;
        }
        drawer.classList.remove('hidden');
    });

    closeDrawerButton.addEventListener('click', () => {
        drawer.classList.add('hidden');
    });

    const cancelReading= document.getElementById('cancel-reading');
    cancelReading.addEventListener('click', () => {
        drawer.classList.add('hidden');
    });

    // Condition dropdown functionality
    const dropdownButton = document.getElementById('reading-condition');
    const dropdownList = document.getElementById('condition-list');
    const dropdownOptions = dropdownList.querySelectorAll('li[role="option"]');

    dropdownButton.addEventListener('click', () => {
        dropdownList.classList.toggle('hidden');
    });

    dropdownOptions.forEach(option => {
        option.addEventListener('click', () => {
            dropdownButton.querySelector('span').textContent = option.querySelector('span').textContent;
            dropdownList.classList.add('hidden');
            dropdownOptions.forEach(opt => opt.querySelector('svg').classList.add('hidden'));
            option.querySelector('svg').classList.remove('hidden');
        });
    });

    // Range input functionality
    const rangeInput = document.getElementById('labels-range-input');
    rangeInput.addEventListener('input', function() {
        const value = this.value;
        const percentage = (value / 10) * 100;
        this.style.backgroundImage = `linear-gradient(90deg, rgba(230, 107, 107, 0.5) ${percentage}%, rgba(195, 234, 184, 1) ${percentage}%)`;
    });

    // Add/Remove condition functionality
    const conditionButtons = document.querySelectorAll('#condition-list button');
    conditionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const svg = this.querySelector('svg');
            const isTracked = svg.classList.contains('text-indigo-600');
            const conditionCode = this.id.split('-').pop();

            if (isTracked) {
                showRemoveConditionWarning(conditionCode);
            } else {
                addCondition(conditionCode);
            }
        });
    });

    const goBackButton = document.getElementById('go-back-dashboard');
    if (goBackButton){
        goBackButton.addEventListener('click', () => {
            noConditionModal.classList.add('hidden');
        });
    }


    function showRemoveConditionWarning(conditionCode) {
        const removeConditionWarning = document.getElementById('remove-condition-warning');
        const removeConditionButton = document.getElementById('remove-condition');
        const cancelRemoveConditionButton = document.getElementById('cancel-remove-condition');

        removeConditionWarning.classList.remove('hidden');

        removeConditionButton.onclick = () => removeCondition(conditionCode);
        cancelRemoveConditionButton.onclick = () => removeConditionWarning.classList.add('hidden');
    }

    function addCondition(conditionCode) {
        const url = `/api/add_medical_condition/${conditionCode}/`;
        fetchWithCSRF(url, 'POST', { condition_code: conditionCode })
            .then(() => window.location.reload())
            .catch(error => console.error('Error adding condition:', error));
    }

    function removeCondition(conditionCode) {
        const url = `/api/delete_medical_condition/${conditionCode}/`;
        fetchWithCSRF(url, 'POST', { condition_code: conditionCode })
            .then(() => window.location.reload())
            .catch(error => console.error('Error removing condition:', error));
    }

    // Save reading functionality
    const saveReadingButton = document.getElementById('save-reading');
    saveReadingButton.addEventListener('click', function() {
        const value = rangeInput.value;
        const conditionText = dropdownButton.querySelector('span').textContent;
        const conditionCode = getConditionCode(conditionText);

        const url = `/api/add_daily_condition_rating/${conditionCode}/${value}/`;
        fetchWithCSRF(url, 'POST')
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }
            })
            .catch(error => {
                dropdownButton.classList.add('animate-pulse', 'ring-2', 'ring-red-500');
                setTimeout(() => {
                    dropdownButton.classList.remove('animate-pulse', 'ring-2', 'ring-red-500');
                }, 5000);
                console.error('Error saving reading:', error);
            });
    });

    function getConditionCode(conditionText) {
        const conditions = {
            'Chronic Obstructive Disease': 'COPD',
            'Asthma': 'ASTHMA',
            'Cystic Fibrosis': 'CF',
            'Sleep Apnea': 'SA',
            'Other': 'OTHER'
        };
        return conditions[conditionText] || '';
    }

    function fetchWithCSRF(url, method, body = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: body ? JSON.stringify(body) : null
        };

        return fetch(url, options).then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Network response was not ok');
                });
            }
            return response.json();
        });
    }
});