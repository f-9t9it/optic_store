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
