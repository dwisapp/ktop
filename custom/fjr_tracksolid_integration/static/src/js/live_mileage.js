/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LiveMileage extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            error: null,
            mileage: 0
        });

        this.vehicleId = this.props.action.context.active_id;

        onMounted(async () => {
            await this.fetchMileage();
        });
    }

    async fetchMileage() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const result = await this.rpc("/tracksolid/get_live_mileage", {
                vehicle_id: this.vehicleId
            });

            if (result.error) {
                this.state.error = result.error;
            } else {
                this.state.mileage = result.mileage_km;
            }
        } catch (e) {
            this.state.error = "Connection failed";
        } finally {
            this.state.loading = false;
        }
    }
}

LiveMileage.template = "fjr_tracksolid_integration.LiveMileage";
registry.category("actions").add("tracksolid_live_mileage_client_action", LiveMileage);
