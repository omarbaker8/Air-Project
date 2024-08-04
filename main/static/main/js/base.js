document.addEventListener('DOMContentLoaded', function() {
    const userButton = document.getElementById('toggle-menu-button');
    const dropMenu = document.getElementById('user-drop-down');
    userButton.addEventListener('click', function() {
        dropMenu.classList.toggle('hidden');
    });

    //Mobile navigation
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIconClosed = document.getElementById('menu-icon-closed');
    const menuIconOpen = document.getElementById('menu-icon-open');

    mobileMenuButton.addEventListener('click', function() {
        console.log('Mobile menu button clicked');
        // Toggle the mobile menu visibility
        mobileMenu.classList.toggle('hidden');

        // Toggle the menu icons
        menuIconClosed.classList.toggle('hidden');
        menuIconOpen.classList.toggle('hidden');

        // Update aria-expanded attribute
        const isExpanded = mobileMenu.classList.contains('hidden') ? 'false' : 'true';
        mobileMenuButton.setAttribute('aria-expanded', isExpanded);
    });
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!mobileMenu.contains(event.target) && !mobileMenuButton.contains(event.target)) {
            mobileMenu.classList.add('hidden');
            menuIconClosed.classList.remove('hidden');
            menuIconOpen.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        }
    });
    // Notification panel
    const notificationPanel = document.querySelector('.message');
    const closeButton = notificationPanel.querySelector('button');

    // Function to show the notification
    function showNotification() {
        notificationPanel.classList.remove('translate-y-2', 'opacity-0', 'sm:translate-y-0', 'sm:translate-x-2');
        notificationPanel.classList.add('translate-y-0', 'opacity-100', 'sm:translate-x-0');
        
        // Add the transition classes
        notificationPanel.classList.add('transform', 'ease-out', 'duration-300', 'transition');
    }

    // Function to hide the notification
    function hideNotification() {
        notificationPanel.classList.remove('translate-y-0', 'opacity-100', 'sm:translate-x-0');
        notificationPanel.classList.add('opacity-0');
        
        // Change the transition classes
        notificationPanel.classList.remove('transform', 'ease-out', 'duration-300');
        notificationPanel.classList.add('ease-in', 'duration-100');

        // Remove the panel from the DOM after the transition
        setTimeout(() => {
            notificationPanel.remove();
        }, 100);  // 100ms to match the duration of the exit transition
    }

    // Show the notification when the page loads
    showNotification();

    // Make the close button functional
    closeButton.addEventListener('click', hideNotification);

    // Automatically hide the notification after 5 seconds
    setTimeout(hideNotification, 3000);

});
