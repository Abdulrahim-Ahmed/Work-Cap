from datetime import timedelta
from odoo import fields, models, tools, api
from functools import partial
from odoo.http import request
import pytz
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class pos_config(models.Model):
	_inherit = 'pos.config'

	allow_cancel_history = fields.Boolean("Allow POS order cancel with Reason", default=True)


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	allow_cancel_history = fields.Boolean("Allow POS order cancel with Reason", default=True,
										  config_parameter='dps_pos_cancel_order_history.allow_cancel_history')


# Updated for Odoo 18 - Use the new loading pattern
class PosSession(models.Model):
	_inherit = 'pos.session'

	@api.model
	def _load_pos_data_models(self, config_id):
		"""Load the data to the pos.config.models using Odoo 18 pattern"""
		data = super()._load_pos_data_models(config_id)
		data += ['pos.cancel.reason']
		return data


class pos_order_cancel(models.Model):
	_name = 'pos.order.cancel'
	_description = "POS Order Cancel"

	_order = "id desc"

	name = fields.Char(string='Name', required=True, readonly=True, copy=False, default='/')
	product_id = fields.Many2one('product.product', string='Product', required=True, change_default=True)
	price_unit = fields.Float(string='Unit Price', digits=0)
	qty = fields.Float('Quantity', default=1)
	partner_id = fields.Many2one('res.partner', string='Customer')
	user_id = fields.Many2one('res.users', string='Seller')
	session_id = fields.Many2one('pos.session', string='Session')
	config_id = fields.Many2one('pos.config', related='session_id.config_id', string="Point of Sale")
	note = fields.Text(string='Reason')

	@api.model
	def create_new_order(self, orderLines):
		for orderLine in orderLines:
			quotation_obj = self.sudo().create(orderLine)
		return {'result': 'OK'}

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].get('pos.order.cancel')
		return super(pos_order_cancel, self).create(vals)


# Updated for Odoo 18 - Inherit from pos.load.mixin
class POSCancelReason(models.Model):
	_name = 'pos.cancel.reason'
	_description = "POS Cancel Reason"
	_inherit = ['pos.load.mixin']

	name = fields.Char(string='Reason')

	@api.model
	def _load_pos_data_fields(self, config_id):
		"""Return the fields that we want to add inside the POS"""
		return ['id', 'name']


class PosDetails(models.TransientModel):
	_inherit = 'pos.details.wizard'

	# @api.multi
	def generate_cancel_order_report(self):
		data = {'date_start': self.start_date, 'date_stop': self.end_date}
		data.update(self.env['report.dps_pos_cancel_order_history.report_saledetails'].get_sale_details(
			self.start_date, self.end_date, self.pos_config_ids))
		return self.env.ref('dps_pos_cancel_order_history.sale_details_report').report_action([], data=data)
# return self.env['report'].get_action(
#     [], 'dps_pos_cancel_order_history.report_saledetails', data=data)


class ReportSaleDetails(models.AbstractModel):
	_name = 'report.dps_pos_cancel_order_history.report_saledetails'
	_description = "POS Cancel Order Report"

	@api.model
	def get_sale_details(self, date_start=False, date_stop=False, configs=False):
		""" Serialise the orders of the day information

		params: date_start, date_stop string representing the datetime of order
		"""
		if not configs:
			configs = self.env['pos.config'].search([])

		today = fields.Datetime.from_string(fields.Date.context_today(self))
		if date_start:
			date_start = fields.Datetime.from_string(date_start)
		else:
			# start by default today 00:00:00
			date_start = today

		if date_stop:
			# set time to 23:59:59
			date_stop = fields.Datetime.from_string(date_stop)
		else:
			# stop by default today 23:59:59
			date_stop = today + timedelta(days=1, seconds=-1)

		# avoid a date_stop smaller than date_start
		date_stop = max(date_stop, date_start)
		date_start = fields.Datetime.to_string(date_start)
		date_stop = fields.Datetime.to_string(date_stop)

		user_tz = self.env.user.tz or pytz.utc
		local = pytz.timezone(user_tz)

		first_time = datetime.strftime(
			pytz.utc.localize(datetime.strptime(date_start, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),
			DEFAULT_SERVER_DATETIME_FORMAT)
		second_time = datetime.strftime(
			pytz.utc.localize(datetime.strptime(date_stop, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),
			DEFAULT_SERVER_DATETIME_FORMAT)

		orders = self.env['pos.order.cancel'].search([
			('create_date', '>=', date_start),
			('create_date', '<=', date_stop),
			('config_id', 'in', configs.ids)])

		order_list = {}

		for order in orders:
			if order.user_id.name in order_list:
				order_list[order.user_id.name].append({
					'name': order.name,
					'product_name': order.product_id.name,
					'price_unit': order.price_unit,
					'user_id': order.user_id.name,
					'qty': order.qty,
					'note': order.note,
				})
			else:
				order_list[order.user_id.name] = []
				order_list[order.user_id.name].append({
					'name': order.name,
					'product_name': order.product_id.name,
					'price_unit': order.price_unit,
					'user_id': order.user_id.name,
					'qty': order.qty,
					'note': order.note,
				})
		return {
			'order_list': order_list,
			'date_start': first_time,
			'date_stop': second_time
		}

	# @api.multi
	def _get_report_values(self, docids, data=None):
		company = request.env.user.company_id
		date_start = data.get('date_start', False)
		date_stop = data.get('date_stop', False)
		data = dict(data or {})
		# data.update(self.get_sale_details(date_start, date_stop, company))
		return data

	