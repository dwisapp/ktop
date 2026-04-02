/**
 * Employee Attendance Portal - Camera & GPS Integration
 *
 * Handles:
 * - Camera access and photo capture
 * - GPS location detection
 * - Attendance submission (check-in/check-out)
 */

(function() {
    'use strict';

    console.log('[Attendance Portal] Script loaded');

    // State variables
    let videoStream = null;
    let capturedPhotoData = null;
    let gpsLocation = null;

    // DOM elements
    let videoElement = null;
    let canvasElement = null;
    let photoPreviewElement = null;
    let loadingElement = null;

    // Buttons
    let btnCapture = null;
    let btnRetake = null;
    let btnCheckIn = null;
    let btnCheckOut = null;

    /**
     * Initialize attendance portal
     */
    function initAttendancePortal() {
        console.log('[Attendance Portal] Attempting initialization...');

        // Check if we're on the attendance portal page
        if (!document.getElementById('camera-video')) {
            console.log('[Attendance Portal] Not on attendance page, skipping');
            return; // Not on attendance page
        }

        console.log('[Attendance Portal] Initializing...');

        // Get DOM elements
        videoElement = document.getElementById('camera-video');
        canvasElement = document.getElementById('photo-canvas');
        photoPreviewElement = document.getElementById('photo-preview');
        loadingElement = document.getElementById('camera-loading');

        btnCapture = document.getElementById('btn-capture-photo');
        btnRetake = document.getElementById('btn-retake-photo');
        btnCheckIn = document.getElementById('btn-submit-checkin');
        btnCheckOut = document.getElementById('btn-submit-checkout');

        console.log('[Attendance Portal] DOM elements found:', {
            video: !!videoElement,
            canvas: !!canvasElement,
            loading: !!loadingElement
        });

        // Setup event listeners
        setupEventListeners();

        // Start camera and GPS detection
        startCamera();
        detectGPSLocation();
    }

    /**
     * Initialize on page load - multiple event listeners for compatibility
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAttendancePortal);
    } else {
        // DOM already loaded
        initAttendancePortal();
    }

    // Fallback: also listen to window load
    window.addEventListener('load', function() {
        if (!videoElement) {
            initAttendancePortal();
        }
    });

    /**
     * Setup button event listeners
     */
    function setupEventListeners() {
        if (btnCapture) {
            btnCapture.addEventListener('click', capturePhoto);
        }

        if (btnRetake) {
            btnRetake.addEventListener('click', retakePhoto);
        }

        if (btnCheckIn) {
            btnCheckIn.addEventListener('click', function() {
                submitAttendance('check_in');
            });
        }

        if (btnCheckOut) {
            btnCheckOut.addEventListener('click', function() {
                submitAttendance('check_out');
            });
        }
    }

    /**
     * Start camera stream
     */
    async function startCamera() {
        try {
            console.log('[Camera] Requesting camera access...');

            // Request camera with front-facing preference (for selfie)
            const constraints = {
                video: {
                    facingMode: 'user', // Front camera
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            videoStream = await navigator.mediaDevices.getUserMedia(constraints);

            // Attach stream to video element
            videoElement.srcObject = videoStream;

            // Wait for video to load
            videoElement.onloadedmetadata = function() {
                console.log('[Camera] Camera started successfully');

                // Hide loading, show video and capture button
                if (loadingElement) loadingElement.style.display = 'none';
                videoElement.style.display = 'block';
                if (btnCapture) btnCapture.style.display = 'inline-block';
            };

        } catch (error) {
            console.error('[Camera] Error accessing camera:', error);

            // Show error message
            if (loadingElement) {
                loadingElement.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fa fa-exclamation-triangle"></i>
                        <strong>Camera Access Failed</strong><br/>
                        ${error.message || 'Please allow camera permission in your browser settings.'}
                        <br/><br/>
                        <button class="btn btn-sm btn-primary" onclick="location.reload()">
                            <i class="fa fa-refresh"></i> Try Again
                        </button>
                    </div>
                `;
            }
        }
    }

    /**
     * Detect GPS location
     */
    function detectGPSLocation() {
        const gpsStatusText = document.getElementById('gps-status-text');

        if (!navigator.geolocation) {
            console.warn('[GPS] Geolocation not supported');
            if (gpsStatusText) {
                gpsStatusText.innerHTML = '<span class="text-warning">GPS not supported by browser</span>';
            }
            return;
        }

        console.log('[GPS] Detecting location...');

        navigator.geolocation.getCurrentPosition(
            // Success
            function(position) {
                gpsLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };

                console.log('[GPS] Location detected:', gpsLocation);

                if (gpsStatusText) {
                    gpsStatusText.innerHTML = `
                        <span class="text-success">
                            <i class="fa fa-check-circle"></i>
                            GPS Location Detected: ${gpsLocation.latitude.toFixed(6)}, ${gpsLocation.longitude.toFixed(6)}
                            (±${gpsLocation.accuracy.toFixed(0)}m accuracy)
                        </span>
                    `;
                }
            },
            // Error
            function(error) {
                console.warn('[GPS] Error detecting location:', error);

                if (gpsStatusText) {
                    gpsStatusText.innerHTML = `
                        <span class="text-warning">
                            <i class="fa fa-exclamation-triangle"></i>
                            GPS location not available (${error.message})
                        </span>
                    `;
                }
            },
            // Options
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    }

    /**
     * Capture photo from video stream
     */
    function capturePhoto() {
        if (!videoElement || !canvasElement) {
            console.error('[Camera] Video or canvas element not found');
            return;
        }

        console.log('[Camera] Capturing photo...');

        // Set canvas dimensions to match video
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;

        // Draw current video frame to canvas
        const context = canvasElement.getContext('2d');
        context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

        // Convert canvas to base64 JPEG
        capturedPhotoData = canvasElement.toDataURL('image/jpeg', 0.85);

        console.log('[Camera] Photo captured');

        // Show preview
        showPhotoPreview();
    }

    /**
     * Show captured photo preview
     */
    function showPhotoPreview() {
        // Hide video, show photo preview
        videoElement.style.display = 'none';
        photoPreviewElement.src = capturedPhotoData;
        photoPreviewElement.style.display = 'block';

        // Update buttons
        if (btnCapture) btnCapture.style.display = 'none';
        if (btnRetake) btnRetake.style.display = 'inline-block';
        if (btnCheckIn) btnCheckIn.style.display = 'inline-block';
        if (btnCheckOut) btnCheckOut.style.display = 'inline-block';
    }

    /**
     * Retake photo
     */
    function retakePhoto() {
        console.log('[Camera] Retaking photo...');

        // Clear captured photo
        capturedPhotoData = null;

        // Hide preview, show video
        photoPreviewElement.style.display = 'none';
        videoElement.style.display = 'block';

        // Update buttons
        if (btnCapture) btnCapture.style.display = 'inline-block';
        if (btnRetake) btnRetake.style.display = 'none';
        if (btnCheckIn) btnCheckIn.style.display = 'none';
        if (btnCheckOut) btnCheckOut.style.display = 'none';
    }

    /**
     * Submit attendance to server
     */
    async function submitAttendance(action) {
        console.log('[Attendance] Submitting attendance:', action);

        // Validate photo
        if (!capturedPhotoData) {
            alert('Please capture a photo first!');
            return;
        }

        // Validate GPS (optional)
        if (!gpsLocation) {
            const confirmSubmit = confirm(
                'GPS location not detected. Do you want to continue without location data?'
            );
            if (!confirmSubmit) {
                return;
            }
        }

        // Disable submit buttons
        if (btnCheckIn) btnCheckIn.disabled = true;
        if (btnCheckOut) btnCheckOut.disabled = true;

        // Show loading state
        const originalText = action === 'check_in'
            ? (btnCheckIn ? btnCheckIn.innerHTML : '')
            : (btnCheckOut ? btnCheckOut.innerHTML : '');

        if (action === 'check_in' && btnCheckIn) {
            btnCheckIn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Submitting...';
        } else if (action === 'check_out' && btnCheckOut) {
            btnCheckOut.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Submitting...';
        }

        try {
            // Extract base64 data (remove data:image/jpeg;base64, prefix)
            const photoBase64 = capturedPhotoData.split(',')[1];

            // Prepare data
            const data = {
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    photo_base64: photoBase64,
                    latitude: gpsLocation ? gpsLocation.latitude : null,
                    longitude: gpsLocation ? gpsLocation.longitude : null,
                    action: action
                }
            };

            // Send to server
            const response = await fetch('/my/attendance/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.result && result.result.success) {
                // Success!
                console.log('[Attendance] Submission successful:', result.result);

                // Show success message
                alert(result.result.message || 'Attendance submitted successfully!');

                // Reload page to update status
                window.location.reload();

            } else {
                // Error from server
                const errorMsg = result.result ? result.result.error : 'Unknown error occurred';
                console.error('[Attendance] Submission failed:', errorMsg);
                alert('Error: ' + errorMsg);

                // Re-enable buttons
                if (btnCheckIn) {
                    btnCheckIn.disabled = false;
                    btnCheckIn.innerHTML = originalText;
                }
                if (btnCheckOut) {
                    btnCheckOut.disabled = false;
                    btnCheckOut.innerHTML = originalText;
                }
            }

        } catch (error) {
            console.error('[Attendance] Network error:', error);
            alert('Network error. Please check your connection and try again.');

            // Re-enable buttons
            if (btnCheckIn) {
                btnCheckIn.disabled = false;
                btnCheckIn.innerHTML = originalText;
            }
            if (btnCheckOut) {
                btnCheckOut.disabled = false;
                btnCheckOut.innerHTML = originalText;
            }
        }
    }

    /**
     * Cleanup on page unload
     */
    window.addEventListener('beforeunload', function() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            console.log('[Camera] Stream stopped');
        }
    });

})();
