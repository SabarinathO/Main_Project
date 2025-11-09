document.addEventListener('DOMContentLoaded', function () {
    // Theme button & modal
    const themeBtn = document.querySelector('#theme'); 
    const themeModal = document.querySelector('.customize-theme');

    // Font size selection
    const fontSizes = document.querySelectorAll('.choose-size span');
    const root = document.documentElement; 

    // Color selection
    const colorPalette = document.querySelectorAll('.choose-color span');

    // Background selection
    const Bg1 = document.querySelector('.bg-1');
    const Bg2 = document.querySelector('.bg-2');
    const Bg3 = document.querySelector('.bg-3');

    // ========== OPEN & CLOSE THEME MODAL ==========
    const openThemeModal = () => {
        themeModal.style.display = 'grid';
    };

    const closeThemeModal = (e) => {
        if (e.target.classList.contains('customize-theme')) {
            themeModal.style.display = 'none';
        }
    };

    // Add event listeners
    themeBtn.addEventListener('click', openThemeModal);
    themeModal.addEventListener('click', closeThemeModal);

    // ========== CHANGE FONT SIZE ==========
    fontSizes.forEach(size => {
        size.addEventListener('click', () => {
            document.querySelector('.choose-size .active')?.classList.remove('active');
            size.classList.add('active');

            let fontSize;
            if (size.classList.contains('font-size-1')) {
                fontSize = '12px';
            } else if (size.classList.contains('font-size-2')) {
                fontSize = '13px';
            } else if (size.classList.contains('font-size-3')) {
                fontSize = '15px';
            } else if (size.classList.contains('font-size-4')) {
                fontSize = '17px';
            } else if (size.classList.contains('font-size-5')) {
                fontSize = '18px';
            }

            document.querySelector('html').style.fontSize = fontSize;

            // Save to localStorage
            localStorage.setItem('fontSize', fontSize);
            localStorage.setItem('activeFontSize', size.classList[0]);
        });
    });

    // ========== CHANGE PRIMARY COLOR ==========
    colorPalette.forEach(color => {
        color.addEventListener('click', () => {
            document.querySelector('.choose-color .active')?.classList.remove('active');
            color.classList.add('active');

            let primaryColor;
            if (color.classList.contains('color-1')) {
                primaryColor = "hsl(255,75%,60%)";
            } else if (color.classList.contains('color-2')) {
                primaryColor = "hsl(52,75%,60%)";
            } else if (color.classList.contains('color-3')) {
                primaryColor = "hsl(352,75%,60%)";
            } else if (color.classList.contains('color-4')) {
                primaryColor = "hsl(152,75%,60%)";
            } else if (color.classList.contains('color-5')) {
                primaryColor = "hsl(202,75%,60%)";
            }

            root.style.setProperty('--color-primary', primaryColor);

            // Save to localStorage
            localStorage.setItem('primaryColor', primaryColor);
            localStorage.setItem('activeColor', color.classList[0]);
        });
    });

    // ========== CHANGE BACKGROUND THEME ==========
    let lightColorLightness;
    let darkColorLightness;
    let whiteColorLightness;

    const changeBg = () => {
        root.style.setProperty('--light-color-lightness', lightColorLightness);
        root.style.setProperty('--dark-color-lightness', darkColorLightness);
        root.style.setProperty('--white-color-lightness', whiteColorLightness);
    };

    Bg2.addEventListener('click', () => {
        darkColorLightness = '95%';
        lightColorLightness = '15%';
        whiteColorLightness = '20%';

        Bg2.classList.add('active');
        Bg1.classList.remove('active');
        Bg3.classList.remove('active');
        changeBg();

        // Save to localStorage
        localStorage.setItem('background', 'bg-2');
    });

    Bg3.addEventListener('click', () => {
        darkColorLightness = '95%';
        lightColorLightness = '10%';
        whiteColorLightness = '0%';

        Bg2.classList.remove('active');
        Bg1.classList.remove('active');
        Bg3.classList.add('active');
        changeBg();

        // Save to localStorage
        localStorage.setItem('background', 'bg-3');
    });

    Bg1.addEventListener('click', () => {
        darkColorLightness = '17%';
        lightColorLightness = '95%';
        whiteColorLightness = '100%';
    
        Bg1.classList.add('active');
        Bg2.classList.remove('active');
        Bg3.classList.remove('active');
        changeBg();
    
        // Save to localStorage
        localStorage.setItem('background', 'bg-1');
    });
    

    // ========== LOAD USER SETTINGS FROM LOCAL STORAGE ==========
    function loadSettings() {
        // Load font size
        if (localStorage.getItem('fontSize')) {
            document.querySelector('html').style.fontSize = localStorage.getItem('fontSize');
        }

        if (localStorage.getItem('activeFontSize')) {
            document.querySelectorAll('.choose-size span').forEach(size => {
                size.classList.remove('active');
                if (size.classList.contains(localStorage.getItem('activeFontSize'))) {
                    size.classList.add('active');
                }
            });
        }

        // Load primary color
        if (localStorage.getItem('primaryColor')) {
            root.style.setProperty('--color-primary', localStorage.getItem('primaryColor'));
        }

        if (localStorage.getItem('activeColor')) {
            document.querySelectorAll('.choose-color span').forEach(color => {
                color.classList.remove('active');
                if (color.classList.contains(localStorage.getItem('activeColor'))) {
                    color.classList.add('active');
                }
            });
        }

        // Load background
        const savedBg = localStorage.getItem('background');
        if (savedBg) {
            if (savedBg === 'bg-2') {
                Bg2.click();
            } else if (savedBg === 'bg-3') {
                Bg3.click();
            } else {
                Bg1.click();
            }
        }
    }

    loadSettings(); // Load user preferences on page load
});