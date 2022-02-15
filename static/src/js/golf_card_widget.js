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
            "change input": "_onInputChange",
            "keydown input": "_onKeyDown",
            "blur input": '_onScoreBlur',
            "focus input": '_onScoreFocus',
        },
        resetOnAnyFieldChange: true,
        useSubview: true,
        _focused : null,

        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this.fields = {};
            this.rows = [];
            this.isDirty = false
            console.debug("GolfCardWidget initiated",this);
            
        },
        /**
        * @override
        */
        isSet: function () {
            console.debug("GolfCardWidget Siet");
            return !!this.value && this.value.count;
        },
        _getValue: function(){
            console.debug("_getValue",this);
        },
        _onInputChange: function(ev){
            if (this.__isEditable()) {
                var $cell = $(ev.currentTarget);
                //this._setValue({ operation: 'UPDATE', id: record.id });
                //this.trigger_up('set_dirty', {dataPointID: this.dataPointID});  
                var cell_id = $cell.data("id");
                var changes = { score_ids: { operation: "UPDATE", id: cell_id, data: { score: $cell.val() } } };
                var initialEvent = { dataPointID: cell_id, changes: { score: $cell.val()}, };
                console.debug("changes:",changes);
                //console.debug("ievent:",initialEvent);
                //console.debug("blur val",this._getValue());
                // this._setValue({ operation: "UPDATE", id: cell_id, data: { score: $cell.val() } });
                this.trigger_up('field_changed', {
                    dataPointID: this.record.id,
                    changes: changes,
                    initialEvent: initialEvent, 
                });
            }
        },
        _onScoreBlur: function(ev){
            if (this.__isEditable()) {
                console.debug("blur",$(ev.currentTarget));
                this._focused = null;
            }
        },
        _onScoreFocus: function(ev){
            if (this.__isEditable()) {
                var $cell = $(ev.currentTarget);
                this._focused = parseInt($cell.attr('tabIndex'));
                console.debug("focus", this._focused);
                $cell.select();
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
        __isEditable: function() {
            // Use the widget mode attribute to determine if we are editable
            return this.mode && this.mode == 'edit';
        },
        
        /**
         * Instanciates or updates the adequate renderer.
         *
         * @override
         * @private
         * @returns {Promise|undefined}
         */
        _render: function () {
            console.debug("_render",this.record.data.score_ids.data);
            this._renderTable();
        },
        _renderTable: function(scores) {
            var self = this;
            // re-rendering triggers blur event and we loose the focusable
            var focused = this._focused;
            console.debug("_renderTable",this,scores);
            this.rows=[];
            this.fields = {};
            //const front = this.record.data.score_ids.data.fiter( s => s.number < 10);
            //const back = this.record.data.score_ids.data.fiter( s => s.number > 9);
            

            _.each(this.record.data.score_ids.data,function (score,index) {
                var field = self._get_golf_field(score.data.field_name);
                //field.holes.append( $('<td/>', {class: 'o_data_cell o_golf_hole_name'}).html(score.data.hole_id.data.display_name))
                field.holes.append( $('<td/>', {class: 'o_data_cell o_golf_hole_name'}).html(index+1))                    
                var input = $('<input/>', {type:'number'}).attr('data-id',score.id).attr("tabIndex",index+1).val(score.data.score);
                if (!self.__isEditable()) {
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
            if (this.__isEditable() && focused) {
                var next = focused + 1;
                this.$el.find("input[tabIndex='"+next+"']").focus();
                console.debug("focus to", next);
            }
        },
    });

    fieldRegistry.add('golf_card_widget', GolfCardWidget);

    return GolfCardWidget;
});