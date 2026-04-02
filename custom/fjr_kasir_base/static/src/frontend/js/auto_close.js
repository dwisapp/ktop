/** @odoo-module **/
import { Component, markup } from "@odoo/owl";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.auto_close = publicWidget.Widget.extend({
	selector: ".base_auto_close",

	start: function () {
		this._super.apply(this, arguments);
		this.rpc = this.bindService("rpc");

		var message = this.$el.data("value");
		var callback = this.$el.data("callback");
		if (callback) {
			var userInput = window.prompt(message);
			while (!userInput) {
				window.alert("You must enter a value to continue.");
				userInput = window.prompt(message);
			}
			this.rpc(callback, { userInput: userInput });
		} else {
			window.alert(message);
		}
		window.location.href = "about:blank";
	},
});
