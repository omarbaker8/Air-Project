document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('location-dropdown');
    const dropdownMenu = document.getElementById('location-list');
    const options = dropdownMenu.querySelectorAll('[role="option"]');
    let myChart = null;

    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "; expires=" + date.toUTCString();
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let c of ca) {
            while (c.charAt(0) == ' ') c = c.substring(1);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length);
        }
        return null;
    }

    function toggleDropdown() {
        dropdownMenu.classList.toggle('hidden');
        button.setAttribute('aria-expanded', !dropdownMenu.classList.contains('hidden'));
    }

    button.addEventListener('click', toggleDropdown);

    document.addEventListener('click', (event) => {
        if (!button.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.add('hidden');
            button.setAttribute('aria-expanded', 'false');
        }
    });

    options.forEach(option => {
        option.addEventListener('click', () => selectOption(option));
    });

    function selectOption(option) {
        const uid = option.dataset.uid;
        const stationName = option.querySelector('span').textContent;
        
        button.querySelector('span').textContent = stationName;
        toggleDropdown();

        options.forEach(opt => opt.querySelector('svg').classList.add('hidden'));
        option.querySelector('svg').classList.remove('hidden');

        setCookie('selectedStation', uid, 30);
        updateChart(uid);
    }

    function updateChart(uid) {
        const chartData = window.stationData[uid];
        if (!chartData || chartData.length === 0) {
            console.error('No data available for the selected location');
            return;
        }

        chartData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        const data = {
            labels: chartData.map(item => formatTimestamp(item.timestamp)),
            datasets: [{
                label: 'Air Quality Index',
                data: chartData.map(item => parseInt(item.aqi)),
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: chartData[0].station
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `AQI: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Air Quality Index'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date and Time'
                        }
                    }
                }
            }
        };

        if (myChart) {
            myChart.destroy();
        }

        myChart = new Chart(document.getElementById('aqi-chart'), config);
    }

    function formatTimestamp(dateString) {
        const date = new Date(dateString);
        return `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    }

    function setDefaultOption() {
        const savedUid = getCookie('selectedStation');
        if (savedUid) {
            const savedOption = document.querySelector(`[data-uid="${savedUid}"]`);
            if (savedOption) {
                selectOption(savedOption);
            } else {
                setFirstOptionAsDefault();
            }
        } else {
            setFirstOptionAsDefault();
        }
    }
    
    function setFirstOptionAsDefault() {
        const firstOption = options[0];
        if (firstOption) {
            selectOption(firstOption);
        } else {
            button.querySelector('span').textContent = "Select a location";
        }
    }

    setDefaultOption();
});