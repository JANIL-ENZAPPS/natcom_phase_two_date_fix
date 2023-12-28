from lxml import etree

from odoo import fields, models
import requests
import json
from datetime import datetime, date
import convert_numbers


class AccountMove(models.Model):
    _inherit = 'account.move'

    def fix_date(self):
        invoicedate = '26/12/2023'
        print(str(self.invoice_datetime))
        print(invoicedate)
        date_obj = datetime.strptime(invoicedate, "%d/%m/%Y")
        date_time_obj = fields.Datetime.from_string(self.invoice_datetime)
        updated_date_time_obj = datetime.combine(date_obj.date(), date_time_obj.time())
        updated_date_time_str = fields.Datetime.to_string(updated_date_time_obj)


        # date_time_obj = fields.Datetime.from_string(self.invoice_datetime)
        # time_part = date_time_obj.strftime("%H:%M:%S")
        # date_obj = datetime.strptime(invoicedate, "%d/%m/%Y")
        # new_date_time_obj = datetime.combine(date_obj.date(), datetime.strptime(time_part, "%H:%M:%S").time())
        # new_date_time_str = new_date_time_obj.strftime("%m/%d/%Y %H:%M:%S")
        # new_date_time_str = date_obj.strftime("%m/%d/%Y") + " " + date_time_obj.strftime("%H:%M:%S")
        # date_time_obj = datetime.strptime(str(self.invoice_datetime), "%Y-%m-%d %H:%M:%S")
        # date_obj = datetime.strptime(invoicedate, "%Y/%m/%d")
        # new_date_time_str = date_obj.strftime("%Y/%m/%d") + " " + date_time_obj.strftime("%H:%M:%S")
        print(updated_date_time_str)
        self.invoice_datetime = updated_date_time_str
        self._onchange_invoice_datetime()


class JsonCalling(models.Model):
    _inherit = 'json.calling'


    def callrequest(self):
        if self.env['json.configuration'].search([]):
            link = self.env['json.configuration'].search([])[0].name
            link_no = self.env['json.configuration'].search([])[-1].no_of_invoices
            import datetime
            responce = requests.get(link)
            json_data = self.env['json.calling'].create({
                'name': 'Invoice Creation on ' + str(datetime.date.today()),
                'date': datetime.date.today(),
            })
            if responce:
                line_data = json.loads(responce.text)
                invoice_no = None
                invoice_date = None
                invoice_length = 0
                line_data.reverse()
                for line in line_data:
                    if invoice_length <= link_no:
                        old_invoice = self.env['account.move'].search([('system_inv_no', '=', line['InvoiceNo'])])
                        if not old_invoice:
                            invoice_length += 1
                            partner_details = self.env['res.partner'].sudo().search(
                                [('name', '=', line['Customer Name'])])
                            if partner_details:
                                partner_id = partner_details
                            else:
                                address_string1 = line['PIN CODE']
                                address_string1key_value_pairs = [item.strip() for item in
                                                                  address_string1.split(",")]
                                address1 = {}
                                if len(address_string1key_value_pairs) == 9:
                                    for pair in address_string1key_value_pairs:
                                        key, value = pair.split(":")
                                        address1[key] = value
                                    partner_id = self.env['res.partner'].sudo().create({
                                        'name': line['Customer Name'],
                                        'ar_name': line['Customer Name Arabic'],
                                        'phone': line['Mobile Number'],
                                        'cust_code': line['CUST_CODE'],
                                        'ar_phone': line['Mobile Number Arabic'],
                                        'street': address1['Street'],
                                        'ar_street': line['STREET_NA'],
                                        'street2': line['Street2 Name'],
                                        'city': address1['City'],
                                        'ar_city': line['CITY_NA'],
                                        'state_id': self.env['res.country.state'].sudo().search(
                                            [('name', '=', address1['State'])]).id,
                                        'zip': address1['Zip'],
                                        'ar_zip': line['PIN CODE ARABIC'],
                                        'country_id': self.env['res.country'].sudo().search(
                                            [('name', '=', line['Country'])]).id,
                                        'ar_country': line['CountryArabic'],
                                        'vat': line['VAT No'],
                                        'ar_tax_id': line['VAT No Arabic'],
                                        'type_of_customer': line['Type of customer'],
                                        'schema_id': 'CRN',
                                        'schema_id_no': line['CR_NUMBER_NA'],
                                        'building_no': address1['Building'],
                                        'plot_id': line['Plot Identification'],
                                        'buyer_identification': 'CRN',
                                        'buyer_identification_no': address1['CR No'],
                                        'additional_no': address1['Addtional No'],
                                        'district': address1['District'],
                                    })
                                else:
                                    partner_id = self.env['res.partner'].sudo().create({
                                        'name': line['Customer Name'],
                                        'ar_name': line['Customer Name Arabic'],
                                        'phone': line['Mobile Number'],
                                        'cust_code': line['CUST_CODE'],
                                        'ar_phone': line['Mobile Number Arabic'],
                                        'street': line['STREET_NA'],
                                        'ar_street': line['STREET_NA'],
                                        'street2': line['Street2 Name'],
                                        'city': line['CITY_NA'],
                                        'ar_city': line['CITY_NA'],
                                        'state_id': self.env['res.country.state'].sudo().search(
                                            [('name', '=', line['State Name'])]).id,
                                        'zip': line['PIN CODE'],
                                        'ar_zip': line['PIN CODE ARABIC'],
                                        'country_id': self.env['res.country'].sudo().search(
                                            [('name', '=', line['Country'])]).id,
                                        'ar_country': line['CountryArabic'],
                                        'vat': line['VAT No'],
                                        'ar_tax_id': line['VAT No Arabic'],
                                        'type_of_customer': line['Type of customer'],
                                        'schema_id': 'CRN',
                                        'schema_id_no': line['CR_NUMBER_NA'],
                                        'building_no': line['BUILDINGNUMBER_NA'],
                                        'plot_id': line['Plot Identification'],
                                        'buyer_identification': 'CRN',
                                        'buyer_identification_no': line['CR_NUMBER_NA'],
                                        'additional_no': line['ADDITIONALNUMBER_NA'],
                                        'district': line['DISTRICT_NA'],
                                    })
                            invoice_list = []
                            for inv_line in line['Invoice lines']:
                                product = self.env['product.product'].sudo().search(
                                    [('name', '=', inv_line['Product Name'])])
                                if not product:
                                    product = self.env['product.template'].sudo().create({
                                        'name': inv_line['Product Name'],
                                        'type': 'service',
                                        'invoice_policy': 'order',
                                    })
                                invoice_list.append((0, 0, {
                                    'name': inv_line['description'],
                                    'price_unit': inv_line['Price'],
                                    'quantity': inv_line['Quantity'],
                                    'discount': inv_line['Discount'],
                                    'product_uom_id': self.env['uom.uom'].sudo().search(
                                        [('name', '=', inv_line['UoM'])]).id,
                                    'vat_category': inv_line['Vat Category'],
                                    'product_id': product.id,
                                    'tax_ids': [(6, 0, self.env['account.tax'].sudo().search(
                                        [('name', '=', inv_line['Taxes']), ('type_tax_use', '=', 'sale')]).ids)]}))
                            invoice_date = (line['InvoiceDate'].split(" ")[0]).split("/")
                            month = invoice_date[0]
                            day = invoice_date[1]
                            year = invoice_date[2]
                            account_move = self.env['account.move'].sudo().create({
                                'partner_id': partner_id[0].id,
                                'invoice_line_ids': invoice_list,
                                'move_type': line['Invoice Type'],
                                'payment_mode': line['Payment Mode'],
                                'contact': line['Address Contact'],
                                'contact_address': line['Address Contact Arabic'],
                                'payment_reference': line['payment reference'],
                                # 'invoice_date': year+'-'+month+'-'+day ,
                                'system_inv_no': line['InvoiceNo'],
                                'a_total_amount': line['A_TOTAL_VALUE'],
                                'a_net_amount': line['A_NET_AMOUNT'],
                                'a_vat_value': line['A_VAT_VALUE'],
                                'a_net_with_value': line['A_NET_WITH_VAT'],
                                'invoice_nat_time': line['INVOICE_DATETIME'],
                                'customer_po': line['PONO'],
                                'compute_test_send_test': True,
                                'ar_amount_untaxed': line['Word without vat'],
                                'amount_in_word_ar': line['Word with vat'],
                                'system_inv_no_ar': line['InvoiceNoArabic'],
                                'invoice_date_time': line['InvoiceDate'],
                                'advance_with_vat': line['ADVANCE_WITH_VAT'],
                                'a_advance_with_vat': line['A_ADVANCE_WITH_VAT'],
                                'invoice_date_time_ar': line['InvoiceDateArabic'],
                                'sales_man': line['Salesman Name'],
                                'so_number': line['SO No'],
                                'curr_code': line['CURR_CODE'],
                                'remarks': line['ANNOTATION'],
                                'advance': line['ADVANCE'],
                                'ar_advance': line['ADVANCE_A'],
                                'exchg_rate': line['EXCHG_RATE'],
                                'discount_value': line['DISCOUNT_VALUE'],
                                'discount_value_a': line['DISCOUNT_VALUE_A'],
                                'word_without_vat_english': line['Word without vat english'],
                                'word_with_vat_english': line['Word with vat english'],
                                'address_contact': line['Address Contact'],
                                'address_contact_ar': line['Address Contact Arabic'],
                            })
                            invoice_no = line['InvoiceNo']
                            invoice_date = line['InvoiceDate']
                            if line['InvoiceDate']:
                                invoicedate = line['InvoiceDate']
                                date_obj = datetime.strptime(invoicedate, "%d/%m/%Y")
                                date_time_obj = fields.Datetime.from_string(account_move.invoice_datetime)
                                updated_date_time_obj = datetime.combine(date_obj.date(), date_time_obj.time())
                                updated_date_time_str = fields.Datetime.to_string(updated_date_time_obj)
                                account_move.invoice_datetime = updated_date_time_str
                                account_move._onchange_invoice_datetime()
                            # account_move.action_post()
                            # if self.env['einvoice.admin'].search([]):
                            #     account_move.admin_mail = self.env['einvoice.admin'].search([])[-1].name.id
                            #     template_id = self.env['mail.template'].sudo().search(
                            #         [('name', '=', 'Invoice: Send by email Information')]).id
                            #     if template_id:
                            #         template = self.env['mail.template'].browse(template_id)
                            #         template.send_mail(account_move.id, force_send=True)
                        if line_data:
                            json_data.system_inv_no = invoice_no
                            json_data.invoice_date_time = invoice_date

    def callrequest1(self):
        if self.env['json.configuration'].search([]):
            link = self.env['json.configuration'].search([])[-1].name
            link_no = self.env['json.configuration'].search([])[-1].no_of_invoices
            responce = requests.get(link)
            if responce:
                line_data = json.loads(responce.text)
                invoice_no = None
                invoice_date = None
                invoice_length = 0
                line_data.reverse()
                for line in line_data:
                    if invoice_length <= link_no:
                        old_invoice = self.env['account.move'].search([('system_inv_no', '=', line['InvoiceNo'])])
                        if not old_invoice:
                            invoice_length += 1
                            partner_details = self.env['res.partner'].sudo().search(
                                [('name', '=', line['Customer Name'])])
                            if partner_details:
                                partner_id = partner_details
                            else:
                                address_string1 = line['PIN CODE']
                                address_string1key_value_pairs = [item.strip() for item in
                                                                  address_string1.split(",")]
                                address1 = {}
                                if len(address_string1key_value_pairs) == 9:
                                    for pair in address_string1key_value_pairs:
                                        key, value = pair.split(":")
                                        address1[key] = value
                                    partner_id = self.env['res.partner'].sudo().create({
                                        'name': line['Customer Name'],
                                        'ar_name': line['Customer Name Arabic'],
                                        'phone': line['Mobile Number'],
                                        'cust_code': line['CUST_CODE'],
                                        'ar_phone': line['Mobile Number Arabic'],
                                        'street': address1['Street'],
                                        'ar_street': line['STREET_NA'],
                                        'street2': line['Street2 Name'],
                                        'city': address1['City'],
                                        'ar_city': line['CITY_NA'],
                                        'state_id': self.env['res.country.state'].sudo().search(
                                            [('name', '=', address1['State'])]).id,
                                        'zip': address1['Zip'],
                                        'ar_zip': line['PIN CODE ARABIC'],
                                        'country_id': self.env['res.country'].sudo().search(
                                            [('name', '=', line['Country'])]).id,
                                        'ar_country': line['CountryArabic'],
                                        'vat': line['VAT No'],
                                        'ar_tax_id': line['VAT No Arabic'],
                                        'type_of_customer': line['Type of customer'],
                                        'schema_id': 'CRN',
                                        'schema_id_no': line['CR_NUMBER_NA'],
                                        'building_no': address1['Building'],
                                        'plot_id': line['Plot Identification'],
                                        'buyer_identification': 'CRN',
                                        'buyer_identification_no': address1['CR No'],
                                        'additional_no': address1['Addtional No'],
                                        'district': address1['District'],
                                    })
                                else:
                                    partner_id = self.env['res.partner'].sudo().create({
                                        'name': line['Customer Name'],
                                        'ar_name': line['Customer Name Arabic'],
                                        'phone': line['Mobile Number'],
                                        'cust_code': line['CUST_CODE'],
                                        'ar_phone': line['Mobile Number Arabic'],
                                        'street': line['Street Name'],
                                        'ar_street': line['STREET_NA'],
                                        'street2': line['Street2 Name'],
                                        'city': line['City'],
                                        'ar_city': line['CITY_NA'],
                                        'state_id': self.env['res.country.state'].sudo().search(
                                            [('name', '=', line['State Name'])]).id,
                                        'zip': line['PIN CODE'],
                                        'ar_zip': line['PIN CODE ARABIC'],
                                        'country_id': self.env['res.country'].sudo().search(
                                            [('name', '=', line['Country'])]).id,
                                        'ar_country': line['CountryArabic'],
                                        'vat': line['VAT No'],
                                        'ar_tax_id': line['VAT No Arabic'],
                                        'type_of_customer': line['Type of customer'],
                                        'schema_id': 'CRN',
                                        'schema_id_no': line['CR_NUMBER_NA'],
                                        'building_no': line['BUILDINGNUMBER_NA'],
                                        'plot_id': line['Plot Identification'],
                                        'buyer_identification': 'CRN',
                                        'buyer_identification_no': line['CR_NUMBER_NA'],
                                        'additional_no': line['ADDITIONALNUMBER_NA'],
                                        'district': line['DISTRICT_NA'],
                                    })
                            invoice_list = []
                            for inv_line in line['Invoice lines']:
                                product = self.env['product.product'].sudo().search(
                                    [('name', '=', inv_line['Product Name'])])
                                if not product:
                                    product = self.env['product.template'].sudo().create({
                                        'name': inv_line['Product Name'],
                                        'type': 'service',
                                        'invoice_policy': 'order',
                                    })
                                invoice_list.append((0, 0, {
                                    'name': inv_line['description'],
                                    'price_unit': inv_line['Price'],
                                    'quantity': inv_line['Quantity'],
                                    'discount': inv_line['Discount'],
                                    'product_uom_id': self.env['uom.uom'].sudo().search(
                                        [('name', '=', inv_line['UoM'])]).id,
                                    'vat_category': inv_line['Vat Category'],
                                    'product_id': product.id,
                                    'tax_ids': [(6, 0, self.env['account.tax'].sudo().search(
                                        [('name', '=', inv_line['Taxes']), ('type_tax_use', '=', 'sale')]).ids)]}))
                            invoice_date = (line['InvoiceDate'].split(" ")[0]).split("/")
                            month = invoice_date[0]
                            day = invoice_date[1]
                            year = invoice_date[2]
                            account_move = self.env['account.move'].sudo().create({
                                'partner_id': partner_id.id,
                                'invoice_line_ids': invoice_list,
                                'move_type': line['Invoice Type'],
                                'payment_mode': line['Payment Mode'],
                                'payment_reference': line['payment reference'],
                                'system_inv_no': line['InvoiceNo'],
                                'customer_po': line['PONO'],
                                'invoice_nat_time': line['INVOICE_DATETIME'],
                                'ar_amount_untaxed': line['Word without vat'],
                                'advance_with_vat': line['ADVANCE_WITH_VAT'],
                                'a_total_amount': line['A_TOTAL_VALUE'],
                                'a_net_amount': line['A_NET_AMOUNT'],
                                'a_vat_value': line['A_VAT_VALUE'],
                                'a_net_with_value': line['A_NET_WITH_VAT'],
                                'a_advance_with_vat': line['A_ADVANCE_WITH_VAT'],
                                'amount_in_word_ar': line['Word with vat'],
                                'system_inv_no_ar': line['InvoiceNoArabic'],
                                'invoice_date_time': line['InvoiceDate'],
                                'invoice_date_time_ar': line['InvoiceDateArabic'],
                                'contact': line['Address Contact'],
                                'contact_address': line['Address Contact Arabic'],
                                'sales_man': line['Salesman Name'],
                                'so_number': line['SO No'],
                                'remarks': line['ANNOTATION'],
                                'curr_code': line['CURR_CODE'],
                                'advance': line['ADVANCE'],
                                'ar_advance': line['ADVANCE_A'],
                                'exchg_rate': line['EXCHG_RATE'],
                                'discount_value': line['DISCOUNT_VALUE'],
                                'discount_value_a': line['DISCOUNT_VALUE_A'],
                                'word_without_vat_english': line['Word without vat english'],
                                'word_with_vat_english': line['Word with vat english'],
                                'address_contact': line['Address Contact'],
                                'address_contact_ar': line['Address Contact Arabic'],
                            })
                            invoice_no = line['InvoiceNo']
                            invoice_date = line['InvoiceDate']
                            if line['InvoiceDate']:
                                invoicedate = line['InvoiceDate']
                                date_obj = datetime.strptime(invoicedate, "%d/%m/%Y")
                                date_time_obj = fields.Datetime.from_string(account_move.invoice_datetime)
                                updated_date_time_obj = datetime.combine(date_obj.date(), date_time_obj.time())
                                updated_date_time_str = fields.Datetime.to_string(updated_date_time_obj)
                                account_move.invoice_datetime = updated_date_time_str
                                account_move._onchange_invoice_datetime()
                            # account_move.action_post()
                            if account_move:
                                import datetime
                                tota = line['INVOICE_DATETIME'].rsplit(' ')[1].rsplit(':')
                                hr = int(tota[0])
                                min = int(tota[1])
                                sec = int(tota[2])
                                import datetime
                                times = datetime.time(hr, min, sec)
                                account_move.invoice_nat_times = datetime.datetime.combine(account_move.invoice_date,
                                                                                           times)
                        if line_data:
                            self.system_inv_no = invoice_no
                            self.invoice_date_time = invoice_date

class JsonCallSales(models.Model):
    _inherit = 'json.call.sales'

    def return_callrequest(self):
        if self.env['return.json.configuration'].search([]):
            link = self.env['return.json.configuration'].search([])[0].name
            responce = requests.get(link)
            from datetime import datetime
            json_data = self.env['json.call.sales'].create({
                'name': 'Invoice Creation on ' + str(datetime.now().date()),
                'date': datetime.now().date(),
            })
            if responce:
                line_data = json.loads(responce.text)
                invoice_no = None
                invoice_date = None
                invoice_length = 0
                for line in line_data:
                    if invoice_length <= 10:
                        old_invoice = self.env['account.move'].search([('system_inv_no', '=', line['InvoiceNo'])])
                        if not old_invoice:
                            invoice_length += 1
                            partner_details = self.env['res.partner'].sudo().search(
                                [('name', '=', line['Customer Name'])])
                            if partner_details:
                                partner_id = partner_details
                            invoice_list = []
                            for inv_line in line['Invoice lines']:
                                product = self.env['product.product'].sudo().search(
                                    [('name', '=', inv_line['Product Name'])])
                                invoice_list.append((0, 0, {
                                    'name': inv_line['description'],
                                    'price_unit': inv_line['Price'],
                                    'quantity': inv_line['Quantity'],
                                    'discount': inv_line['Discount'],
                                    'product_uom_id': self.env['uom.uom'].sudo().search(
                                        [('name', '=', inv_line['UoM'])]).id,
                                    'vat_category': inv_line['Vat Category'],
                                    'product_id': product.id,
                                    'tax_ids': [(6, 0, self.env['account.tax'].sudo().search(
                                        [('name', '=', inv_line['Taxes']), ('type_tax_use', '=', 'sale')]).ids)]}))
                            invoice_date = (line['InvoiceDate'].split(" ")[0]).split("/")
                            day = invoice_date[0]
                            month = invoice_date[1]
                            year = invoice_date[2]
                            account_move = self.env['account.move'].sudo().create({
                                'partner_id': partner_id[0].id,
                                    'invoice_line_ids': invoice_list,
                                    'payment_mode': line['Payment Mode'],
                                    'contact': line['Address Contact'],
                                    'contact_address': line['Address Contact Arabic'],
                                    'payment_reference': line['payment reference'],
                                    'invoice_date': year+'-'+month + '-' + day,
                                    'system_inv_no': line['InvoiceNo'],
                                    'move_type': 'out_refund',
                                    'a_total_amount': line['A_TOTAL_VALUE'],
                                    'a_net_amount': line['A_NET_AMOUNT'],
                                    'a_vat_value': line['A_VAT_VALUE'],
                                    'a_net_with_value': line['A_NET_WITH_VAT'],
                                    'invoice_nat_time': line['INVOICE_DATETIME'],
                                    'customer_po': line['PONO'],
                                    'compute_test_send_test': True,
                                    'ar_amount_untaxed': line['Word without vat'],
                                    'amount_in_word_ar': line['Word with vat'],
                                    'system_inv_no_ar': line['InvoiceNoArabic'],
                                    'invoice_date_time': line['InvoiceDate'],
                                    'advance_with_vat': line['ADVANCE_WITH_VAT'],
                                    'a_advance_with_vat': line['A_ADVANCE_WITH_VAT'],
                                    'invoice_date_time_ar': line['InvoiceDateArabic'],
                                    'sales_man': line['Salesman Name'],
                                    'so_number': line['SO No'],
                                    'curr_code': line['CURR_CODE'],
                                    'remarks': line['ANNOTATION'],
                                    'advance': line['ADVANCE'],
                                    'ar_advance': line['ADVANCE_A'],
                                    'exchg_rate': line['EXCHG_RATE'],
                                    'discount_value': line['DISCOUNT_VALUE'],
                                    'discount_value_a': line['DISCOUNT_VALUE_A'],
                                    'word_without_vat_english': line['Word without vat english'],
                                    'word_with_vat_english': line['Word with vat english'],
                                    'address_contact': line['Address Contact'],
                                    'address_contact_ar': line['Address Contact Arabic'],
                            })
                            invoice_no = line['InvoiceNo']
                            invoice_date = line['InvoiceDate']
                            if line['InvoiceDate']:
                                invoicedate = line['InvoiceDate']
                                date_obj = datetime.strptime(invoicedate, "%d/%m/%Y")
                                date_time_obj = fields.Datetime.from_string(account_move.invoice_datetime)
                                updated_date_time_obj = datetime.combine(date_obj.date(), date_time_obj.time())
                                updated_date_time_str = fields.Datetime.to_string(updated_date_time_obj)
                                account_move.invoice_datetime = updated_date_time_str
                                account_move._onchange_invoice_datetime()
                            if account_move:
                                import datetime
                                date = datetime.date(account_move.invoice_date.year, account_move.invoice_date.month,
                                                     account_move.invoice_date.day)
                                tota = line['INVOICE_DATETIME'].rsplit(' ')[1].rsplit(':')[0]
                                hr = int(tota[0])
                                min = int(tota[1])
                                import datetime
                                times = datetime.time(hr,min)
                                account_move.invoice_nat_times = datetime.datetime.combine(account_move.invoice_date, times)

                            previous_invoice = self.env['account.move'].search([('system_inv_no','=',line['REF_SALES_RETURN'])])
                            if previous_invoice:
                                previous_invoice_name = previous_invoice[-1].name
                                account_move.update({
                                    'ref': 'Reversal of: ' + previous_invoice_name + ',' + line['ANNOTATION']
                                })
                            if account_move.ref_sales_return:
                                reversed_inv = self.env['account.move'].search([('system_inv_no','=',account_move.ref_sales_return)])
                                account_move.reversed_entry_id = reversed_inv
                            # account_move.action_post()
                        if line_data:
                            json_data.system_inv_no = invoice_no
                            json_data.invoice_date_time = invoice_date
