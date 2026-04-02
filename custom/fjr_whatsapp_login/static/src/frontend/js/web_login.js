odoo.define("fjr_whatsapp_login.WebLogin", function (require) {
	"use strict";

	const dom = require("web.dom");
	var publicWidget = require("web.public.widget");
	var utils = require("web.utils");
	var core = require("web.core");
	const { Markup } = require("web.utils");
	var _t = core._t;
	publicWidget.registry.WhatsappWebLogin = publicWidget.Widget.extend({
		selector: "form.oe_login_form",
		events: {
			"click .send-otp-button": "_sendOtp",
		},
		start: function () {
			// this.disabledLoginButton();
			return this._super.apply(this, arguments);
		},

		_sendOtp: function (ev) {
			var self = this;
			var $button = $(ev.currentTarget);
			var originalText = $button.text();
			var $whatsappNumber = self.$("#whatsapp_number").val().trim();
			// Disable button and show loading
			if (!$whatsappNumber) {
				self.displayNotification({
					title: _t("Error"),
					message: _t("Please Insert your Whatsapp Number."),
					type: "danger",
				});
				this.$("#whatsapp_number").focus();
				return;
			}

			$button
				.prop("disabled", true)
				.html('<i class="fa fa-spinner fa-spin"></i> Sending OTP...');

			this._rpc({
				route: "/otp-verification/whatsapp",
				params: {
					phone_number: self.$("#whatsapp_number").val(),
					type: "login",
				},
			})
				.then(function (result) {
					// Animasi sukses
					if (result.status == "success") {
						$button.html('<i class="fa fa-check"></i> Success Sending OTP!');
						setTimeout(function () {
							$button.html("Resend OTP").prop("disabled", false);
							self.$("div.field-otp").css("display", "block");
							self.$("#otp").focus();
							self.$("button[type='submit']").show();
						}, 1000);
					} else {
						self.displayNotification({
							title: _t("Error"),
							message: _t(result.message),
							type: "danger",
						});
						setTimeout(function () {
							$button.html("Send OTP").prop("disabled", false);
						}, 1000);
					}
				})
				.guardedCatch(function (error) {
					// Animasi gagal
					$button.html('<i class="fa fa-times"></i> Failed Sending OTP');
					setTimeout(function () {
						$button.html(originalText).prop("disabled", false);
					}, 2000);
					// Handle error (e.g., show error message)
				});
		},
	});
});
