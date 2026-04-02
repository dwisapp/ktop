/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Component, useState } from "@odoo/owl";

/**
 * Kiosk Camera Integration for Selfie Attendance
 *
 * This module patches the kiosk attendance app to integrate camera selfie capture
 * before creating attendance records.
 */

// Import kiosk app (will be patched)
import { kioskAttendanceApp } from "@hr_attendance/public_kiosk/public_kiosk_app";

// Patch the kiosk attendance app
patch(kioskAttendanceApp.prototype, {

    setup() {
        super.setup(...arguments);

        // Add camera state
        this.cameraState = useState({
            showModal: false,
            cameraActive: false,
            capturedPhoto: null,
            gpsLocation: null,
            pendingEmployeeId: null,
            isCheckIn: true,
        });
    },

    /**
     * Override onManualSelection to capture photo first
     */
    async onManualSelection(employeeId, pincode) {
        // Store employee ID for later
        this.cameraState.pendingEmployeeId = employeeId;

        // Show camera modal
        this.cameraState.showModal = true;

        // Start camera
        await this.startSelfieCamera();
    },

    /**
     * Override onBarcodeScanned to capture photo first
     */
    async onBarcodeScanned(barcode) {
        if (this.lockScanner) return;

        this.lockScanner = true;

        try {
            // Get employee data from barcode
            const employee = await this.rpc('attendance_barcode_scanned', {
                'barcode': barcode,
                'token': this.props.token,
            });

            if (employee && employee.employee_id) {
                // Store for photo capture
                this.cameraState.pendingEmployeeId = employee.employee_id;

                // Check if using PIN
                if (employee.use_pin) {
                    this.employeeData = employee;
                    this.switchDisplay('pin');
                } else {
                    // Show camera modal
                    this.cameraState.showModal = true;
                    await this.startSelfieCamera();
                }
            }
        } catch (error) {
            console.error("Barcode scan error:", error);
            this.displayNotification(_t("Badge scan failed. Please try again."));
        } finally {
            // Reset lock after delay
            setTimeout(() => { this.lockScanner = false; }, 1000);
        }
    },

    /**
     * Start camera for selfie capture
     */
    async startSelfieCamera() {
        try {
            // Request camera permission with front camera
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: "user", // front camera
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            });

            this.cameraStream = stream;
            this.cameraState.cameraActive = true;

            // Auto-detect GPS in background
            this.detectGPSLocation();

        } catch (error) {
            console.error("Camera error:", error);

            // Fallback: allow check-in without photo (with warning)
            this.notification.add(
                _t("Camera not available. Proceeding without photo."),
                { type: "warning" }
            );

            // Proceed without photo
            await this.submitAttendanceWithoutPhoto();
        }
    },

    /**
     * Capture photo from video stream
     */
    capturePhotoFromCamera() {
        if (!this.cameraStream) {
            console.error("No camera stream available");
            return null;
        }

        try {
            // Create canvas to capture frame
            const video = document.querySelector('#kiosk-camera-video');
            if (!video) return null;

            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert to base64 JPEG
            const photoData = canvas.toDataURL('image/jpeg', 0.85);

            this.cameraState.capturedPhoto = photoData;

            return photoData;

        } catch (error) {
            console.error("Photo capture error:", error);
            return null;
        }
    },

    /**
     * Stop camera stream
     */
    stopCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        this.cameraState.cameraActive = false;
    },

    /**
     * Detect GPS location
     */
    async detectGPSLocation() {
        if (!navigator.geolocation) {
            console.warn("Geolocation not supported");
            return;
        }

        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            });

            this.cameraState.gpsLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };

        } catch (error) {
            console.warn("GPS detection failed:", error);
            this.cameraState.gpsLocation = null;
        }
    },

    /**
     * Submit attendance with photo and GPS
     */
    async submitAttendanceWithPhoto() {
        const employeeId = this.cameraState.pendingEmployeeId;
        const photo = this.cameraState.capturedPhoto;
        const gps = this.cameraState.gpsLocation;

        if (!employeeId) {
            console.error("No employee ID for attendance");
            return;
        }

        try {
            // Prepare attendance data
            const attendanceData = {
                'token': this.props.token,
                'employee_id': employeeId,
            };

            // Add photo (remove data:image/jpeg;base64, prefix)
            if (photo) {
                attendanceData.check_in_image = photo.split(',')[1];
            }

            // Add GPS coordinates
            if (gps) {
                attendanceData.latitude = gps.latitude;
                attendanceData.longitude = gps.longitude;
            }

            // Submit to backend
            const result = await this.rpc('kiosk_attendance', attendanceData);

            // Stop camera
            this.stopCamera();

            // Close modal
            this.cameraState.showModal = false;
            this.cameraState.capturedPhoto = null;
            this.cameraState.pendingEmployeeId = null;

            // Show greeting screen
            if (result && result.employee_name) {
                this.employeeData = result;
                this.switchDisplay('greet');
            }

            // Auto-return to main screen
            setTimeout(() => {
                this.kioskReturn();
            }, 3000);

        } catch (error) {
            console.error("Attendance submission error:", error);
            this.notification.add(
                _t("Failed to submit attendance. Please try again."),
                { type: "danger" }
            );

            // Close modal
            this.stopCamera();
            this.cameraState.showModal = false;
            this.kioskReturn();
        }
    },

    /**
     * Submit attendance without photo (fallback)
     */
    async submitAttendanceWithoutPhoto() {
        const employeeId = this.cameraState.pendingEmployeeId;

        if (!employeeId) return;

        try {
            const result = await this.rpc('kiosk_attendance', {
                'token': this.props.token,
                'employee_id': employeeId,
            });

            this.cameraState.showModal = false;
            this.cameraState.pendingEmployeeId = null;

            if (result && result.employee_name) {
                this.employeeData = result;
                this.switchDisplay('greet');
            }

            setTimeout(() => {
                this.kioskReturn();
            }, 3000);

        } catch (error) {
            console.error("Attendance submission error:", error);
            this.notification.add(_t("Failed to submit attendance."), { type: "danger" });
            this.kioskReturn();
        }
    },

    /**
     * Cancel camera capture
     */
    cancelCameraCapture() {
        this.stopCamera();
        this.cameraState.showModal = false;
        this.cameraState.capturedPhoto = null;
        this.cameraState.pendingEmployeeId = null;
        this.kioskReturn();
    },

    /**
     * Retake photo
     */
    retakePhoto() {
        this.cameraState.capturedPhoto = null;
        this.startSelfieCamera();
    },
});
