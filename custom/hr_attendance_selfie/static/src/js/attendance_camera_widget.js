/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Attendance Camera Widget
 * Handles camera capture for check-in/check-out selfies
 */
export class AttendanceCameraWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.state = useState({
            cameraActive: false,
            photoCapture: null,
            showPreview: false,
            gpsLocation: null,
            error: null,
        });

        this.videoRef = useRef("video");
        this.canvasRef = useRef("canvas");
        this.stream = null;
    }

    /**
     * Start camera stream
     */
    async startCamera() {
        try {
            // Request camera permission dengan preferensi front camera
            const constraints = {
                video: {
                    facingMode: "user", // front camera untuk selfie
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);

            if (this.videoRef.el) {
                this.videoRef.el.srcObject = this.stream;
                this.state.cameraActive = true;
                this.state.error = null;
            }

            // Auto-detect GPS location
            this.getGPSLocation();

        } catch (error) {
            console.error("Camera error:", error);
            this.state.error = "Failed to access camera. Please check permissions.";
            this.notification.add(
                "Camera permission denied or not available",
                { type: "danger" }
            );
        }
    }

    /**
     * Stop camera stream
     */
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.state.cameraActive = false;
    }

    /**
     * Capture photo from video stream
     */
    capturePhoto() {
        if (!this.videoRef.el || !this.canvasRef.el) {
            return;
        }

        const video = this.videoRef.el;
        const canvas = this.canvasRef.el;
        const context = canvas.getContext('2d');

        // Set canvas size to video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw current video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to base64 JPEG
        const photoData = canvas.toDataURL('image/jpeg', 0.85);

        this.state.photoCapture = photoData;
        this.state.showPreview = true;

        // Stop camera after capture
        this.stopCamera();

        this.notification.add("Photo captured successfully!", { type: "success" });
    }

    /**
     * Retake photo
     */
    retakePhoto() {
        this.state.photoCapture = null;
        this.state.showPreview = false;
        this.startCamera();
    }

    /**
     * Get GPS location using Geolocation API
     */
    async getGPSLocation() {
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

            this.state.gpsLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };

        } catch (error) {
            console.warn("GPS error:", error);
            this.state.gpsLocation = null;
        }
    }

    /**
     * Submit attendance with photo and GPS
     */
    async submitAttendance(isCheckIn = true) {
        if (!this.state.photoCapture) {
            this.notification.add("Please capture a photo first!", { type: "warning" });
            return;
        }

        try {
            // Prepare data
            const attendanceData = {};

            if (isCheckIn) {
                attendanceData.check_in_image = this.state.photoCapture.split(',')[1]; // Remove data:image/jpeg;base64,

                if (this.state.gpsLocation) {
                    attendanceData.in_latitude = this.state.gpsLocation.latitude;
                    attendanceData.in_longitude = this.state.gpsLocation.longitude;
                }
            } else {
                attendanceData.check_out_image = this.state.photoCapture.split(',')[1];

                if (this.state.gpsLocation) {
                    attendanceData.out_latitude = this.state.gpsLocation.latitude;
                    attendanceData.out_longitude = this.state.gpsLocation.longitude;
                }
            }

            // Call backend to save attendance
            await this.props.onSubmit(attendanceData);

            this.notification.add(
                isCheckIn ? "Check-in successful!" : "Check-out successful!",
                { type: "success" }
            );

            // Close modal/dialog
            this.props.close();

        } catch (error) {
            console.error("Submit error:", error);
            this.notification.add("Failed to submit attendance", { type: "danger" });
        }
    }

    /**
     * Lifecycle: Cleanup on unmount
     */
    onWillUnmount() {
        this.stopCamera();
    }
}

AttendanceCameraWidget.template = "hr_attendance_selfie.CameraWidget";

// Register the widget
registry.category("fields").add("attendance_camera", AttendanceCameraWidget);
