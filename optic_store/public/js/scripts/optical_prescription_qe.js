import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';
import { get_all_rx_params } from '../utils/constants';

export default {
  render_dialog: function() {
    this.mandatory = [
      ...this.mandatory,
      ...this.meta.fields.filter(({ fieldname }) =>
        [
          'frame_sec',
          'frame_size',
          'height_col',
          'height_type',
          'height',
          'details_simple_sec',
          'details_html',
        ].includes(fieldname)
      ),
      ...get_all_rx_params().map(fieldname => ({
        fieldname,
        fieldtype: 'Data',
        hidden: 1,
      })),
    ];
    this._super();
    const { $wrapper } = this.dialog.get_field('details_html');
    this.detail_vue = new Vue({
      el: $wrapper.html('<div />').children()[0],
      data: { doc: this.dialog.doc, fields: this.dialog.fields_dict },
      methods: {
        update: (field, value) => this.dialog.set_value(field, value),
      },
      render: function(h) {
        const { doc, update, fields } = this;
        return h(PrescriptionForm, {
          props: { doc, update, fields },
        });
      },
    });
  },
  render_edit_in_full_page_link: function() {
    this._super();
    $(
      `<button class="os-submit btn-warning btn-sm">${__(
        'Save & Submit'
      )}</button>`
    )
      .css('float', 'right')
      .insertAfter(this.dialog.$body.find('.edit-full'))
      .on('click', () => this.submit());
  },

  // copied 'insert' method from /frappe/public/js/frappe/form/quick_entry.js
  submit: async function() {
    try {
      this.update_doc();
      const { message: new_doc } = await frappe.call({
        method: 'optic_store.api.optical_prescription.save_and_submit',
        args: { doc: this.dialog.doc },
        freeze: true,
      });
      if (!new_doc) {
        throw 'x';
      }
      this.dialog.hide();
      frappe.model.clear_doc(this.dialog.doc.doctype, this.dialog.doc.name);
      this.dialog.doc = new_doc;
      if (frappe._from_link) {
        frappe.ui.form.update_calling_link(this.dialog.doc);
      } else {
        if (this.after_insert) {
          this.after_insert(this.dialog.doc);
        } else {
          this.open_form_if_not_list();
        }
      }
    } catch (e) {
      this.open_doc();
    } finally {
      this.dialog.working = false;
      this.dialog.clear_message();
    }
  },
};
