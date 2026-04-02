/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { loadJS, loadCSS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

export class HistoryMap extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.mapContainer = useRef("mapContainer");

        // Default: Today 00:00 to now
        const now = new Date();
        const start = new Date();
        start.setHours(start.getHours() - 6); // Default 6 hours ago

        this.state = useState({
            loading: false,
            error: null,
            startTime: this.formatDate(start),
            endTime: this.formatDate(now),
            pointCount: 0
        });

        this.vehicleId = this.props.action.context.active_id;

        this.map = null;
        this.polyline = null;
        this.startMarker = null;
        this.endMarker = null;

        onMounted(async () => {
            await this.loadLeaflet();
            this.initMap();
        });
    }

    formatDate(date) {
        // Simple YYYY-MM-DD HH:MM:SS
        const pad = (n) => n.toString().padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }

    async loadLeaflet() {
        try {
            await loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
            await loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js");
        } catch (e) {
            this.state.error = "Failed to load map resources.";
        }
    }

    initMap() {
        if (!this.mapContainer.el) return;
        this.map = L.map(this.mapContainer.el).setView([-2.5489, 118.0149], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        }).addTo(this.map);

        // Auto load on open
        this.onSearch();
    }

    async onSearch() {
        if (!this.vehicleId) return;
        this.state.loading = true;
        this.state.error = null;
        this.state.pointCount = 0;

        // clear old layers
        if (this.polyline) this.map.removeLayer(this.polyline);
        if (this.startMarker) this.map.removeLayer(this.startMarker);
        if (this.endMarker) this.map.removeLayer(this.endMarker);

        try {
            const result = await this.rpc("/tracksolid/get_tracking_history", {
                vehicle_id: this.vehicleId,
                start_time: this.state.startTime,
                end_time: this.state.endTime
            });

            if (result.error) {
                this.state.error = result.error;
            } else if (result.points && result.points.length > 0) {
                const latlngs = result.points.map(p => [parseFloat(p.lat), parseFloat(p.lng)]);
                this.state.pointCount = latlngs.length;

                this.polyline = L.polyline(latlngs, { color: 'blue' }).addTo(this.map);

                // Start & End markers
                this.startMarker = L.marker(latlngs[0]).addTo(this.map).bindPopup("Start");
                this.endMarker = L.marker(latlngs[latlngs.length - 1]).addTo(this.map).bindPopup("End");

                this.map.fitBounds(this.polyline.getBounds());
            } else {
                this.state.error = "No track data found for this period.";
            }

        } catch (e) {
            this.state.error = "Error fetching history: " + e;
        } finally {
            this.state.loading = false;
        }
    }
}

HistoryMap.template = "fjr_tracksolid_integration.HistoryMap";
registry.category("actions").add("tracksolid_history_map_client_action", HistoryMap);
