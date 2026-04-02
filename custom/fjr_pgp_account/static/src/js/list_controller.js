/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { formatMonetary } from "@web/views/fields/formatters";

patch(ListController.prototype, {
	get amountResidual() {
		let selectedRecords = this.model.root.records.filter(
			(record) => record.selected
		);
		let amountResidual = 0;
		let currency_id = selectedRecords[0].data.company_currency_id;
		for (let record of selectedRecords) {
			amountResidual += record.data.amount_residual_signed;
		}

		return formatMonetary(amountResidual, {
			currencyId: currency_id,
		});
	},

	get displayAmountResidual() {
		return (
			this.props.context.default_move_type &&
			(this.props.context.default_move_type === "in_invoice" ||
				this.props.context.default_move_type === "out_invoice")
		);
	},
});
