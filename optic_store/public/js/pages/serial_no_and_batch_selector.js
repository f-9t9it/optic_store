export default function extend_batch_selector(SerialNoBatchSelectorClass) {
  class SerialNoBatchSelectorExtended extends SerialNoBatchSelectorClass {
    get_batch_fields() {
      const fields = super.get_batch_fields();
      if (fields) {
        const batches = fields.find(({ fieldname }) => fieldname === 'batches');
        if (batches) {
          const batch_no = batches.fields.find(
            ({ fieldname }) => fieldname === 'batch_no'
          );
          if (batch_no) {
            batch_no.get_query = () => ({
              filters: { item: this.item_code },
            });
          }
        }
      }
      return fields;
    }
  }
  return SerialNoBatchSelectorExtended;
}
