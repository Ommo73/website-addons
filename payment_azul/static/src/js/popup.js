/*  Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).*/
odoo.define('payment_azul.popup', function(require) {

"use strict";

var payment_form = require('payment.payment_form');
var session = require('web.session');
var ajax = require('web.ajax');
var core = require('web.core');
var qweb = core.qweb;


payment_form.include({
    getFormData: function ($form) {
        var res = this._super($form);
        var azul_popup_inputs = $('#azul_popup_modal input').serializeArray();
        console.log(res)
        _.map(azul_popup_inputs, function (n, i) {
            res[n.name] = n.value || res[n.name];
        });
        if ($('#azul_popup_modal input#swith_remember_me')[0].checked) {
            res.remember_me = true;
        }
        return res;
    },
})

$(document).ready(function () {

    // update 'Pay Now' handler
    var payment_methods = $('input[name="pm_id"]');
    var azul_checkbox = $('input[name="pm_id"][data-provider="azul"]');
    var non_azul_checkboxes = $('input[name="pm_id"]:not([data-provider="azul"])');
    var pm_button = $('#payment_method button#o_payment_form_pay');
    var toggle_pay_buttons = function(azul) {
        if (azul) {
            pm_button.hide();
            azul_pay_button.show();
        } else {
            azul_pay_button.hide();
            pm_button.show();
        }
    }
    pm_button.parent().parent().parent().append('<button id="azul_pay" class="pull-right btn btn-primary btn-lg mb8 mt8"><i class="fa fa-lock"></i> Payment </button>');
    var azul_pay_button = $('#azul_pay');
    var azul_pm_is_selected = azul_checkbox.prop('checked');
    toggle_pay_buttons(azul_pm_is_selected);
    _.map(payment_methods, function(el) {
        $(el).on('change', function(){
            // for some reason it does not see unchecking the button
            var azul_pm_is_selected = azul_checkbox.prop('checked');
            toggle_pay_buttons(azul_pm_is_selected);
        });
    });



    var data_request = function () {
        return session.rpc("/payment_azul/card_data", {});
    };

    var destroy_stock_modal = function(modal){
        modal.remove();
    };

    var action_close = function (modal) {
        //destroy_stock_modal(modal);
        remove_class_selected(modal);
        modal.hide();
    };

    var request_for_customer_cards = function (partner_id) {
        return;
    };

    var remove_class_selected = function (modal) {
        var $cards = modal.find('.cards');
        _.each($cards.children(), function(c_c) {
            $(c_c).removeClass('selected');
        });
    };

    var create_modal = function () {
        console.log(qweb, session)
        // TODO: request for company_id, SO reference, Company email,

        var modal = $('#azul_popup_modal');
        modal.show()
        data_request().then(function(res) {
            _.chain(res).keys().each(function(k){
                var el = modal.find('.' + k);
                if (el[0] && el[0].tagName === 'SPAN') {
                    el.text(res[k]);
                }
                //else if (el[0] && el[0].tagName === 'INPUT') {
                //    el.val(res[k]);
                //}
            });

            var $add_new_card = modal.find('.add_new_card');
            var $saved_cards = modal.find('.saved_cards');

            if (res.cards && res.cards.length) {
                var $cards = modal.find('.cards');
                $cards[0].innerHTML = '';
                var template = modal.find('.card_template');
                var new_card = false;
                _.each(res.cards, function(c) {
                    new_card = template[0].cloneNode(true);
                    $(new_card).removeClass('card_template').addClass('a_card');
                    $(new_card).attr('cid', c.id);
                    _.each(_.keys(c), function(dk) {
                        $(new_card).find('.' + dk).text(c[dk]);
                    });
                    $cards[0].appendChild(new_card);
                });
                var $cards_children = $cards.children();
                _.each($cards.children(), function(c) {
                    $(c).off().on('click', function (ev) {
                        remove_class_selected(modal);
                        $(c).addClass('selected');
                        var cid = parseInt(c.attributes['cid'].value);
                        modal.find('#card_id').val(cid);
                    });
                });
                $add_new_card.hide();
                $saved_cards.show();
            } else {
                $add_new_card.addClass('hide_saved_btn');
            }

            modal.find('.new_card-btn').off().on('click', function (ev) {
                $add_new_card.show();
                $saved_cards.hide();
                modal.find('#card_id').val();
                remove_class_selected(modal);
            });
            modal.find('.saved_card-btn').off().on('click', function (ev) {
                $add_new_card.hide();
                $saved_cards.show();
            });
        });


        modal.find('.payment-btn').off().on('click', function(ev) {
        //    var payment_widget = new payment_form(window);
        //    payment_widget.payEvent(ev);
            pm_button.click();
            action_close(modal);
        });

        return modal;
    };

    //    var action_add_card_to_modal = function (data) {
    //        console.log(data);
    //    };

    var set_events = function (modal) {
        var close_buttons = modal.find('.close-btn');
        _.map(close_buttons, function (bt) {
            $(bt).on('click', function(ev) {
                action_close(modal);
            });
        });
    };

    var open_azul_modal = function () {
        var modal = create_modal();
        set_events(modal);
    };

    azul_pay_button.on('click', function() {
        open_azul_modal();
    });

    console.log(this);
});

});
