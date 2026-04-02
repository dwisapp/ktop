/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { loadJS, loadCSS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

export class FleetMap extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.mapContainer = useRef("mapContainer");
        this.state = useState({
            loading: true,
            vehicles: []
        });

        this.map = null;
        this.markers = {}; // Store markers by vehicle ID
        this.timer = null;
        this.initialFitDone = false;

        onMounted(async () => {
            try {
                // Load Leaflet
                await loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
                await loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js");

                this.initMap();
                this.fetchVehicles();
                // Auto refresh every 30s
                this.timer = setInterval(() => this.fetchVehicles(), 30000);
            } catch (e) {
                console.error("Map init error", e);
            }
        });

        onWillUnmount(() => {
            if (this.timer) clearInterval(this.timer);
            if (this.map) this.map.remove();
        });
    }

    initMap() {
        if (!this.mapContainer.el) return;
        // Default center Indonesia
        this.map = L.map(this.mapContainer.el).setView([-2.5489, 118.0149], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(this.map);
    }

    async fetchVehicles() {
        try {
            const result = await this.rpc("/tracksolid/get_fleet_map_data", {});
            if (result.vehicles) {
                this.updateMap(result.vehicles);
            }
        } catch (e) {
            console.error("Fetch vehicles error", e);
        }
    }

    updateMap(vehicles) {
        if (!this.map) return;

        const bounds = [];

        vehicles.forEach(v => {
            const lat = v.lat;
            const lng = v.lng;

            if (this.markers[v.id]) {
                // Update existing
                this.markers[v.id].setLatLng([lat, lng]);
                this.markers[v.id].setPopupContent(this.getPopupContent(v));
            } else {
                // Create new
                // Check if we can use custom icons for status? Maybe later.
                const marker = L.marker([lat, lng]).addTo(this.map);
                marker.bindPopup(this.getPopupContent(v));
                this.markers[v.id] = marker;
            }
            bounds.push([lat, lng]);
        });

        // Fit bounds if we have points and haven't done it yet
        if (!this.initialFitDone && bounds.length > 0) {
            this.map.fitBounds(bounds);
            this.initialFitDone = true;
        }
    }

    getPopupContent(v) {
        let statusColor = 'grey';
        if (v.status === 'online') statusColor = 'green';
        if (v.status === 'offline') statusColor = 'red';
        if (v.status === 'moving') statusColor = 'green';

        return `
            <div style="min-width: 150px;">
                <h6 style="margin-bottom: 5px;">${v.name}</h6>
                <div><small>Model:</small> <b>${v.model}</b></div>
                <div><small>Driver:</small> <b>${v.driver}</b></div>
                <hr style="margin: 5px 0;"/>
                <div>Speed: <b>${v.speed} km/h</b></div>
                <div>Status: <span style="color:${statusColor}; font-weight:bold;">${v.status || 'unknown'}</span></div>
                <div class="text-muted" style="font-size: 0.8em; margin-top: 5px;">${v.time || ''}</div>
            </div>
        `;
    }
}

FleetMap.template = "fjr_tracksolid_integration.FleetMap";
registry.category("actions").add("tracksolid_fleet_map_client_action", FleetMap);
