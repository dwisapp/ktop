/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

export class JasaErpSalesOrderListController extends ListController {
	setup() {
		super.setup();
		this.orm = useService("orm");
		this.notificationService = useService("notification");
	}

	onClickGetSalesOrder() {
		var self = this;
		self.orm
			.call("jasa.erp.sales.order", "generate_sales_order", [])
			.then((res) => {
				if (res.status == "success") {
					self.actionService.doAction({
						type: "ir.actions.client",
						tag: "reload",
					});
				} else {
					let message = res.message;

					self.notificationService.add(
						"Gagal mengambil data sales order " + message,
						{
							type: "danger",
						}
					);
				}
			});
	}
}

registry.category("views").add("jasa_erp_sales_order", {
	...listView,
	Controller: JasaErpSalesOrderListController,
	buttonTemplate: "JasaErpSalesOrderListView.buttons",
});
