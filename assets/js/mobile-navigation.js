const mobileNavigation = document.querySelector('.mobile-navigation');

if (mobileNavigation) {
    mobileNavigation.addEventListener('click', (event) => {
        if (event.target.closest('a[href]')) {
            mobileNavigation.open = false;
        }
    });

    document.addEventListener('click', (event) => {
        if (!mobileNavigation.contains(event.target)) {
            mobileNavigation.open = false;
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && mobileNavigation.open) {
            mobileNavigation.open = false;
            mobileNavigation.querySelector('summary').focus();
        }
    });

    window.matchMedia('(max-width: 700px)').addEventListener('change', () => {
        mobileNavigation.open = false;
    });
}
