export function toggle3dButton()
{
    const threeDButton = document.getElementById('3d');
    const twoDButton = document.getElementById('2d');
    const canvas2d = document.getElementById('game-canvas');
    const canvas3d = document.getElementById('three-canvas');

    // Make sure both canvases exist before proceeding
    if (!canvas2d || !canvas3d) {
        console.error("Canvas elements not found");
        return;
    }

    // Set initial state to 3D
    threeDButton.classList.add('active');
    twoDButton.classList.remove('active');
    canvas2d.style.display = 'none';
    canvas3d.style.display = 'block';

    // Initialize 3D game immediately with a slight delay to ensure DOM is ready
    setTimeout(async () => {
        try {
            const game3dModule = await import('./game_3d.js');
            
            // Make sure gameSettings is properly set before initializing 3D
            if (window.gameSettings) {
                window.gameSettings.contextType = '3d';
                
                // Initialize the 3D game
                game3dModule.initGame3D(canvas3d);
                game3dModule.resizeRenderer(canvas3d.clientWidth, canvas3d.clientHeight);
                game3dModule.animate();
                
                // console.log("3D game initialized successfully");
            } else {
                console.error("gameSettings not available");
            }
        } catch (error) {
            console.error("Error initializing 3D game:", error);
        }
    }, 200);

    // Add 3D button event listener
    threeDButton.addEventListener('click', async () => {
        threeDButton.classList.add('active');
        twoDButton.classList.remove('active');
        canvas2d.style.display = 'none';
        canvas3d.style.display = 'block';
        
        try {
            const game3dModule = await import('./game_3d.js');
            game3dModule.cleanup();
            await new Promise(resolve => setTimeout(resolve, 100));
            
            window.gameSettings.contextType = '3d';
            game3dModule.initGame3D(canvas3d);
            game3dModule.resizeRenderer(canvas3d.clientWidth, canvas3d.clientHeight);
            game3dModule.animate();
        } catch (error) {
            console.error("Error switching to 3D:", error);
        }
    });

    // Add 2D button event listener
    twoDButton.addEventListener('click', async () => {
        twoDButton.classList.add('active');
        threeDButton.classList.remove('active');
        canvas3d.style.display = 'none';
        canvas2d.style.display = 'block';
        
        try {
            window.gameSettings.contextType = '2d';
            
            // Clean up 3D resources
            const game3dModule = await import('./game_3d.js');
            game3dModule.cleanup();
        } catch (error) {
            console.error("Error switching to 2D:", error);
        }
    });

    // Fix the resize handler
    window.addEventListener('resize', resize3d);
}

export function resize3d() {
    let resizeTimeout;
    const canvas3d = document.getElementById('three-canvas');
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(async () => {
        if (gameSettings.contextType === '3d') {
            const game3dModule = await import('./game_3d.js');
            game3dModule.resizeRenderer(canvas3d.clientWidth, canvas3d.clientHeight);
        }
    }, 100);
}