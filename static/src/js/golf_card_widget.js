odoo.define('golf.card_widget', function (require) {
    "use strict";

    const { ComponentWrapper, WidgetAdapterMixin } = require('web.OwlCompatibility');
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var core = require('web.core');
    var _t = core._t;

    var GolfCardWidget = AbstractField.extend(WidgetAdapterMixin, {
        tagName: 'div',
        /**
         * @override
         */
        events : {
            "blur input": "_onInputBlur",
            "keydown input": "_onKeyDown",
        },
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this.fields = {};
            this.rows = [];
            this.isDirty = false
            console.debug("GolfCardWidget init",this);
            
        },
        /**
        * @override
        */
        isSet: function () {
            console.debug("GolfCardWidget Siet");
            return !!this.value && this.value.count;
        },

        _onInputBlur: function(ev){
            var $cell = $(ev.currentTarget);
            var next = parseInt($cell.attr('tabIndex'))+1;
            console.debug("blur",next,$cell,ev);
            
            if (this.editable) {
                $cell.parents("o_golf_card").find("input[tabIndex='"+next+"]'").focus();
                this.trigger_up('set_dirty', {dataPointID: this.dataPointID});  
            }
        },
        
        /**
         * Manages the keyboard events on the list. If the list is not editable, when the user navigates to
         * a cell using the keyboard, if he presses enter, enter the model represented by the line
         *
         * @private
         * @param {KeyboardEvent} ev
         */
        _onKeyDown: function (ev) {
            var $cell = $(ev.currentTarget);
            var $tr;
            var $futureCell;
            var colIndex;
            
        },
        
        /**
         * Instanciates or updates the adequate renderer.
         *
         * @override
         * @private
         * @returns {Promise|undefined}
         */
        _render: function () {
            self = this;
            var prm = this._rpc({
                model: this.value.model,
                method: 'search_read',
                args: [[['id',"in",this.value.res_ids]]],
            }).then(function (scores) {
                self.scores = scores;
                self._renderTable(scores);
                return scores;
            });
        },
        _get_golf_field: function(name) {
            var field = this.fields[name];
            if (!field) {
                field = {
                    name: name,
                    holes: $('<tr/>', {class: 'o_golf_holes'}).attr('field_name',name),
                    scores: $('<tr/>', {class: 'o_golf_scores'}).attr('field_name',name),
                };
                this.fields[name]= field;
                this.rows.push(field.holes);
                this.rows.push(field.scores);

            }
            return field;
        },
        _renderTable: function(scores) {
            self = this;
            console.debug("_renderTable",this,scores);
            this.editable = this.$el.parents(".o_form_editable").length > 0;
            
            _.each(scores, function (score,index) {
                var field = self._get_golf_field(score.field_name);
                field.holes.append( $('<td/>', {class: 'o_data_cell o_golf_hole_name'}).html(score.hole_id[1]));
                var input = $('<input/>', {type:'number'}).attr('data-id',score.id).attr("tabIndex",index+1).val(score.score);
                if (!self.editable) {
                    input.attr("readonly",1);
                }
                field.scores.append($('<td/>',{class: 'o_data_cell o_golf_score'}).append(input));
            });
            const $table = $(
                '<table class="o_list_table table table-sm table-hover table-striped o_golf_card"/>'
            );
            
            for (var key in this.fields) {
                var field = this.fields[key];
                field.holes.append($("<td/>", {class:"o_data_cell"}).append(field.name));
                var total = 0;
                field.scores.find("input").each(function() {
                    total += parseInt( $(this).val() );
                });
                field.scores.append($('<td/>',{class: 'o_data_cell o_golf_score'}).append($('<input/>', {type:'number',readonly:1}).val(total) ));
                
            }
            $table.append(this.rows);
            var tableWrapper = Object.assign(document.createElement('div'), {
                className: 'table-responsive',
            });
            tableWrapper.appendChild($table[0]);
            this.el.innerHTML = "";
            this.el.appendChild(tableWrapper);
            console.debug("_renderTable",tableWrapper);         
        },
    });

    fieldRegistry.add('golf_card_widget', GolfCardWidget);

    return GolfCardWidget;
});