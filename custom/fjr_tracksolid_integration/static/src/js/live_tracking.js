/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { loadJS, loadCSS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

export class LiveTrackingMap extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.mapContainer = useRef("mapContainer");
        this.state = useState({
            loading: true,
            error: null,
            vehicleName: "Loading...",
            speed: 0,
            lastUpdate: "-"
        });

        this.vehicleId = this.props.action.context.active_id;
        if (!this.vehicleId) {
            // Fallback if opened directly without context (rare)
            this.state.error = "No Vehicle ID provided.";
            return;
        }

        this.map = null;
        this.marker = null;
        this.timer = null;

        onMounted(async () => {
            try {
                // Load Leaflet
                await loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
                await loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js");

                this.initMap();
                this.startTracking();
            } catch (e) {
                this.state.error = "Failed to load map resources: " + e;
            }
        });

        onWillUnmount(() => {
            if (this.timer) clearInterval(this.timer);
            if (this.map) this.map.remove();
        });
    }

    initMap() {
        if (!this.mapContainer.el) return;

        // Initialize map with default view (Indonesia center approx)
        this.map = L.map(this.mapContainer.el).setView([-2.5489, 118.0149], 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(this.map);
    }

    async startTracking() {
        await this.fetchLocation();
        // Poll every 10 seconds
        this.timer = setInterval(() => this.fetchLocation(), 10000);
    }

    async fetchLocation() {
        try {
            const result = await this.rpc("/tracksolid/get_device_location", {
                vehicle_id: this.vehicleId
            });

            if (result.error) {
                this.state.error = result.error;
                return;
            }

            this.updateMap(result);

        } catch (e) {
            console.error("Tracking Error:", e);
            // Don't show error to user immediately on transient network fail, just log
        }
    }

    updateMap(data) {
        const lat = parseFloat(data.lat);
        const lng = parseFloat(data.lng);

        if (isNaN(lat) || isNaN(lng)) return;

        // Leaflet resize fix
        if (this.map) {
            setTimeout(() => { this.map.invalidateSize(); }, 100);
        }

        this.state.loading = false;
        this.state.vehicleName = data.deviceName || "Vehicle";
        this.state.speed = data.speed || 0;
        this.state.lastUpdate = data.deviceTime || "Just now";

        const position = [lat, lng];

        if (!this.marker) {
            this.marker = L.marker(position).addTo(this.map);
            this.map.setView(position, 15); // Zoom in on first find
        } else {
            this.marker.setLatLng(position);
            this.map.panTo(position); // Follow the car
        }

        this.marker.bindPopup(`
            <b>${this.state.vehicleName}</b><br>
            Speed: ${this.state.speed} km/h<br>
            Time: ${this.state.lastUpdate}
        `).openPopup();
    }
}

LiveTrackingMap.template = "fjr_tracksolid_integration.LiveTrackingMap";
registry.category("actions").add("tracksolid_live_tracking_client_action", LiveTrackingMap);
