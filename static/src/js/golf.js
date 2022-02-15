odoo.golf = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.HomePage = instance.Widget.extend({
        start: function() {
            console.log("Golf home page loaded");
            this.$el.append("<div>Golf Module Home Pagina</div>");
            var tournament = new instance.web.Model("golf.tournament");
        },
    });

    instance.web.client_actions.add(
        'golf.homepage', 'instance.golf.HomePage');
    console.log("Golf home page ready");
}