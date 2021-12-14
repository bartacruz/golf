odoo.define('golf.cardo2m', (require) => {

    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');

    var GolfCardListRenderer = ListRenderer.extend({
        fields : {},
        rows: [],
        events: {
            "mousedown": "_onMouseDown",
            "click .o_optional_columns_dropdown .dropdown-item": "_onToggleOptionalColumn",
            "click .o_optional_columns_dropdown_toggle": "_onToggleOptionalColumnDropdown",
            'click tbody td': '_onRowClicked',
            'change tbody .o_list_record_selector': '_onSelectRecord',
            'click thead th.o_column_sortable': '_onSortColumn',
            'click .o_list_record_selector': '_onToggleCheckbox',
            'click .o_group_header': '_onToggleGroup',
            'change thead .o_list_record_selector input': '_onToggleSelection',
            'keypress thead tr td': '_onKeyPress',
            'keydown td': '_onKeyDown',
            'keydown th': '_onKeyDown',
        },
        _get_golf_field: function(name) {
            field = this.fields[name];
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
        /**
         * Render all rows. This method should only called when the view is not
         * grouped.
         *
         * @private
         * @returns {jQueryElement[]} a list of <tr>
         */
        _renderRows: function () {
            var self = this;
            this.fields = {};
            this.rows = [];

            this.state.data.forEach(function (record, index) {
                self.columns.forEach(function (node,index) {
                    $cell = self._renderBodyCell(record, node, index, { mode: 'readonly' });
                    $cell.attr('data-id', record.id)
                    field = self._get_golf_field(record.data.field_name);
                    if (index % 2 == 0) {
                        field.holes.append($cell);
                    } else {
                        field.scores.append($cell);
                    }
                });
            });

            for (var key in this.fields) {
                var field = this.fields[key];
                field.holes.append($("<td/>", {class:"o_data_cell"}).append("Total"));
                var total = 0;
                field.scores.children().each(function() {
                    total += parseInt( $(this).html() );
                });
                field.scores.append($("<td/>", {class:"o_data_cell"}).append(total));
            }
            return this.rows;
            //return this.state.data.map(this._renderRow.bind(this));
        },

        _renderEmptyRow: function() {},
        _renderHeader: function () {},
        _renderFooter: function () {},

        /**
         * We want to add .o_section_and_note_list_view on the table to have stronger CSS.
         *
         * @override
         * @private
         */
        _renderView: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$('.o_list_table').addClass('o_golf_card_list_view');
            });
        }
    });

    var GolfCardOne2Many = FieldOne2Many.extend({
        /**
         * We want to use our custom renderer for the list.
         *
         * @override
         */
        _getRenderer: function () {
            return GolfCardListRenderer;
            
        },
    });
    fieldRegistry.add('golf_card_o2m', GolfCardOne2Many);

    return GolfCardListRenderer;
});