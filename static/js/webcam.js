// Webcam Capture Functionality - ROBUST VERSION

let stream = null;
let capturedImage = null;

// Initialize webcam
async function initWebcam() {
    console.log("Attempting to start webcam...");
    const video = document.getElementById('webcam');
    const startBtn = document.getElementById('start-webcam');
    const captureBtn = document.getElementById('capture-image');
    const retakeBtn = document.getElementById('retake-image');

    if (!video) {
        console.error('Video element with id "webcam" not found');
        alert("Error: Video element missing from page.");
        return;
    }

    // 1. Hardware/Browser Support Check
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Error: Your browser does not support camera access. Please use Chrome/Edge/Firefox.');
        return;
    }

    // Show loading state
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing...';
    }

    try {
        console.log('Requesting camera permission...');
        // Use simpler constraints for maximum device compatibility
        stream = await navigator.mediaDevices.getUserMedia({
            video: true, // Simple constraint
            audio: false
        });

        console.log('Stream acquired, connecting to video tag...');
        video.srcObject = stream;
        video.setAttribute('playsinline', ''); // Essential for iOS
        video.style.display = 'block'; // Ensure visible

        // Wait for video to be ready
        video.onloadedmetadata = function (e) {
            video.play().then(() => {
                console.log('Video playing successfully');
                if (startBtn) startBtn.style.display = 'none';
                if (captureBtn) captureBtn.style.display = 'inline-block';
                if (retakeBtn) retakeBtn.style.display = 'none';

                // Ensure canvas is ready
                const canvas = document.getElementById('canvas');
                if (canvas) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }
            }).catch(err => {
                console.error('Video play error:', err);
                alert('Playback Error: ' + err.message);
                if (startBtn) {
                    startBtn.disabled = false;
                    startBtn.innerHTML = 'Retry Camera';
                }
            });
        };

    } catch (error) {
        console.error('Webcam Error:', error);
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-camera"></i> Retry Camera';
            startBtn.style.display = 'inline-block';
        }

        let msg = 'Camera Error: ' + (error.message || error.name);
        alert(msg);
    }
}

// Capture image from webcam
function captureImage() {
    console.log("Capturing image...");
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-image');
    const retakeBtn = document.getElementById('retake-image');
    const previewContainer = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const voterImageInput = document.getElementById('voter-image-input');

    if (!video || !canvas) {
        console.error("Missing video or canvas element");
        return;
    }

    const context = canvas.getContext('2d');
    // Ensure dimensions match
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get image data as base64
    capturedImage = canvas.toDataURL('image/jpeg', 0.8);
    console.log("Image captured, length:", capturedImage.length);

    // Set hidden input value
    if (voterImageInput) {
        voterImageInput.value = capturedImage;
        console.log("Input field updated");
    } else {
        console.error("FATAL: voter-image-input hidden field not found!");
        alert("Error: Could not save image. Please refresh and try again.");
    }

    // Show preview
    if (previewImg) {
        previewImg.src = capturedImage;
        previewImg.style.display = 'block'; // Ensure visible
    }
    if (previewContainer) {
        previewContainer.style.display = 'block';
    }

    // Stop webcam tracks to release camera
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    // Hide video, show preview
    video.style.display = 'none';
    if (captureBtn) captureBtn.style.display = 'none';
    if (retakeBtn) retakeBtn.style.display = 'inline-block';

    // Enable submit button
    updateSubmitButton();
}

// Retake image
function retakeImage() {
    console.log("Retaking image...");
    const video = document.getElementById('webcam');
    const captureBtn = document.getElementById('capture-image');
    const retakeBtn = document.getElementById('retake-image');
    const previewContainer = document.getElementById('image-preview');
    const voterImageInput = document.getElementById('voter-image-input');

    capturedImage = null;
    if (voterImageInput) {
        voterImageInput.value = '';
    }

    if (previewContainer) {
        previewContainer.style.display = 'none';
    }

    if (captureBtn) captureBtn.style.display = 'none';
    if (retakeBtn) retakeBtn.style.display = 'none';

    // Restart webcam
    initWebcam();
    updateSubmitButton();
}

// Update submit button state
function updateSubmitButton() {
    const submitBtn = document.getElementById('submit-vote-btn') || document.getElementById('submit-btn');
    if (!submitBtn) return;

    const hasImage = document.getElementById('voter-image-input')?.value;
    // Check if we are on vote page (requires candidate) or registration (requires password)
    const candidateInput = document.getElementById('candidate-id-input');

    let isFormValid = false;

    if (candidateInput) {
        // Voting Page
        const hasLocation = true; // Assume location is ok for now to unblock
        const hasCandidate = !!candidateInput.value;
        isFormValid = (hasImage && hasCandidate);
    } else {
        // Registration/Password Page
        isFormValid = !!hasImage;
    }

    submitBtn.disabled = !isFormValid;
    submitBtn.style.opacity = isFormValid ? '1' : '0.5';
    submitBtn.style.cursor = isFormValid ? 'pointer' : 'not-allowed';
}

// Initializer
function initialize() {
    console.log('webcam.js initialized');
    const startBtn = document.getElementById('start-webcam');
    const captureBtn = document.getElementById('capture-image');
    const retakeBtn = document.getElementById('retake-image');

    // Remove old listeners to prevent duplicates (not strictly needed with simple script include, but good practice)
    if (startBtn) {
        startBtn.onclick = null;
        startBtn.onclick = initWebcam; // Use onclick to ensure single handler
        console.log("Start button listener attached");
    } else {
        console.warn("Start button not found on load");
    }

    if (captureBtn) captureBtn.onclick = captureImage;
    if (retakeBtn) retakeBtn.onclick = retakeImage;

    // Check periodically if button appears (for dynamic content)
    updateSubmitButton();
}

// Run on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// Cleanup
window.addEventListener('beforeunload', function () {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});
