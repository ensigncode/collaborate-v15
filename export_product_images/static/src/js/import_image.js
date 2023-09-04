odoo.define('export_product_images.ImportMenu', function (require) {
    "use strict";

    const DropdownMenuItem = require('web.DropdownMenuItem');
    const FavoriteMenu = require('web.FavoriteMenu');
    const { useModel } = require('web/static/src/js/model.js');

    /**
     * Import Records menu
     *
     * This component is used to import the records for particular model.
     *
     * @extends DropdownMenuItem
     */
    class ImportMenu extends DropdownMenuItem {
        constructor() {
            super(...arguments);
            this.model = useModel('searchModel');
        }

        //---------------------------------------------------------------------
        // Handlers
        //---------------------------------------------------------------------

        /**
         * @private
         */
        _onImportImage() {
            const action = {
                type: 'ir.actions.act_window',
                name: this.env._t("Images Import"),
                res_model: 'import.images',
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                },
            };
            this.env.bus.trigger('do-action', {
                action,
            });
        }

        //---------------------------------------------------------------------
        // Static
        //---------------------------------------------------------------------

        /**
         * @param {Object} env
         * @returns {boolean}
         */
        static shouldBeDisplayed(env) {
            return env.view &&
                ['kanban', 'list'].includes(env.view.type) &&
                !env.device.isMobile &&
                !!JSON.parse(env.view.arch.attrs.import || '1') &&
                !!JSON.parse(env.view.arch.attrs.create || '1');
        }
    }

    ImportMenu.props = {};
    ImportMenu.template = 'base_import.ImportMenu';

    FavoriteMenu.registry.add('import-menu', ImportMenu, 1);

    return ImportMenu;
});
