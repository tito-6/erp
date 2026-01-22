from tcrm import models, fields, api

class PropertioPrintOptions(models.TransientModel):
    _name = 'propertio.print.options'
    _description = 'Print Options Wizard'

    sale_id = fields.Many2one('propertio.sale', string="Sale Contract", required=True)

    def action_download_pdf(self):
        return self.sale_id.action_download_pdf()

    def action_download_word(self):
        return self.sale_id.action_download_word()

    def action_print_html(self):
        return self.sale_id.action_print_contract_html()

    def action_export_word_batch(self):
        return self.sale_id.action_export_batch_word()
