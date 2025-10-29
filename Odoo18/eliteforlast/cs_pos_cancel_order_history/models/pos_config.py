from datetime import timedelta
from odoo import fields, models, tools, api
from functools import partial
from odoo.http import request
import pytz
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)


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
	_check_company = True

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
	pos_name = fields.Char(string='POS Name')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
	employee_id = fields.Many2one('hr.employee', string='Employee')

	@api.model
	def search(self, domain=None, offset=0, limit=None, order=None, count=False):
		"""Override search to filter by selected companies from context"""
		domain = domain or []
		
		# Log the context to debug
		_logger.info(f"POS Order Cancel search context: {self.env.context}")
		
		# Get allowed company IDs from context
		allowed_company_ids = self.env.context.get('allowed_company_ids', [])
		
		if allowed_company_ids:
			# User has selected specific companies in the UI
			_logger.info(f"Allowed companies from context: {allowed_company_ids}")
			company_domain = [('company_id', 'in', allowed_company_ids)]
		else:
			# Fallback to current company
			_logger.info(f"No allowed_company_ids in context, using current company: {self.env.company.name} (ID: {self.env.company.id})")
			company_domain = [('company_id', '=', self.env.company.id)]
		
		# Remove any existing company_id domain to avoid conflicts
		domain = [term for term in domain if not (isinstance(term, (list, tuple)) and len(term) >= 1 and term[0] == 'company_id')]
		
		# Prepend company domain
		domain = company_domain + domain
		
		_logger.info(f"Final search domain: {domain}")
		
		return super(pos_order_cancel, self).search(domain=domain, offset=offset, limit=limit, order=order, count=count)

	@api.model
	def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
		"""Override search_read to ensure company filtering"""
		domain = domain or []
		
		# Get allowed company IDs from context
		allowed_company_ids = self.env.context.get('allowed_company_ids', [])
		
		if allowed_company_ids:
			# User has selected specific companies in the UI
			company_domain = [('company_id', 'in', allowed_company_ids)]
		else:
			# Fallback to current company
			company_domain = [('company_id', '=', self.env.company.id)]
		
		# Remove any existing company_id domain to avoid conflicts
		domain = [term for term in domain if not (isinstance(term, (list, tuple)) and len(term) >= 1 and term[0] == 'company_id')]
		
		# Prepend company domain
		domain = company_domain + domain
		
		return super(pos_order_cancel, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

	@api.model
	def create_new_order(self, orderLines):
		for orderLine in orderLines:
			# Fallback for user_id and company_id
			if not orderLine.get('user_id') and orderLine.get('session_id'):
				session = self.env['pos.session'].browse(orderLine['session_id'])
				orderLine['user_id'] = session.user_id.id
			if not orderLine.get('company_id') and orderLine.get('session_id'):
				session = self.env['pos.session'].browse(orderLine['session_id'])
				orderLine['company_id'] = session.company_id.id
			# employee_id is set if present in orderLine
			self.sudo().create(orderLine)
		return {'result': 'OK'}

	# FIXED: Remove @api.model decorator and handle batch creation properly
	def create(self, vals_list):
		"""
		Override create method to handle sequence generation for batch creation.
		This method supports both single record creation and batch creation.
		"""
		# Ensure vals_list is always a list for batch processing
		if not isinstance(vals_list, list):
			vals_list = [vals_list]
		
		# Generate sequence numbers for each record
		for vals in vals_list:
			if not vals.get('name') or vals.get('name') == '/':
				vals['name'] = self.env['ir.sequence'].next_by_code('pos.order.cancel') or '/'
			# Fallback for user_id and company_id
			if not vals.get('user_id') and vals.get('session_id'):
				session = self.env['pos.session'].browse(vals['session_id'])
				vals['user_id'] = session.user_id.id
			if not vals.get('company_id') and vals.get('session_id'):
				session = self.env['pos.session'].browse(vals['session_id'])
				vals['company_id'] = session.company_id.id
			# employee_id is set if present in vals
		return super(pos_order_cancel, self).create(vals_list)


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
