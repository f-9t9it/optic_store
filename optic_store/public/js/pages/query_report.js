export function extend_multiselect(ControlMultiSelect) {
  if (ControlMultiSelect.name === 'MultiSelectExtended') {
    return ControlMultiSelect;
  }
  return class MultiSelectExtended extends ControlMultiSelect {
    setup_awesomplete() {
      super.setup_awesomplete();

      this.$input.off('focus');
      this.$input.on('focus', () => {
        if (!this.$input.val()) {
          this.$input.val('');
        }
        this.$input.trigger('input');
      });

      this.$input.on('awesomplete-select', e => {
        e.preventDefault();
        this.awesomplete.replace(e.originalEvent.text);
        this.awesomplete.evaluate();
      });
    }
    get_awesomplete_settings() {
      return Object.assign(super.get_awesomplete_settings(), {
        filter: (text, input) => {
          if (this.get_values().includes(text.value)) {
            return false;
          }

          const item = this.awesomplete.get_item(text.value);
          const match = input.match(/[^,]*$/)[0];
          if (!item) {
            return Awesomplete.FILTER_CONTAINS(text, match);
          }

          const getMatch = value => value && Awesomplete.FILTER_CONTAINS(value, match);
          return (
            getMatch(item.label) || getMatch(item.value) || getMatch(item.description)
          );
        },
      });
    }
  };
}

export default function extend_query_report(QueryReport) {
  return class QueryReportExtended extends QueryReport {
    refresh_report() {
      this.toggle_message(true);

      return frappe.run_serially([
        () => this.setup_filters(),
        () => this.set_route_filters(),
        () => this.report_settings.onload && this.report_settings.onload(this),
        () => {
          try {
            this.get_filter_values(true);
          } catch (e) {
            clearInterval(this.interval);
          }
        },
        () => this.get_user_settings(),
        () => this.refresh(),
      ]);
    }
  };
}
