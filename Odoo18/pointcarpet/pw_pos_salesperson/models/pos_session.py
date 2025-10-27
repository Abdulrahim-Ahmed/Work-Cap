# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _load_pos_data_models(self, config_id):
        """Override to load employee data."""
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info("=== POS SALESPERSON DEBUG: _load_pos_data_models called ===")
        _logger.info(f"=== POS SALESPERSON DEBUG: config_id: {config_id}")
        _logger.info(f"=== POS SALESPERSON DEBUG: config_id type: {type(config_id)}")
        
        result = super()._load_pos_data_models(config_id)
        _logger.info(f"=== POS SALESPERSON DEBUG: Parent result type: {type(result)}")
        _logger.info(f"=== POS SALESPERSON DEBUG: Parent result: {result}")
        
        # Add employee data if salesperson feature is enabled
        try:
            _logger.info(f"=== POS SALESPERSON DEBUG: Checking allow_salesperson...")
            _logger.info(f"=== POS SALESPERSON DEBUG: hasattr(config_id, 'allow_salesperson'): {hasattr(config_id, 'allow_salesperson')}")
            if hasattr(config_id, 'allow_salesperson'):
                _logger.info(f"=== POS SALESPERSON DEBUG: config_id.allow_salesperson: {config_id.allow_salesperson}")
            
            if hasattr(config_id, 'allow_salesperson') and config_id.allow_salesperson:
                _logger.info("=== POS SALESPERSON DEBUG: Loading employee data via _load_pos_data_models...")
                
                employee_fields = ['id', 'name', 'write_date', 'image_128']
                employees = self.env['hr.employee'].search_read(
                    [('active', '=', True)],
                    employee_fields
                )
                
                _logger.info(f"=== POS SALESPERSON DEBUG: Found {len(employees)} employees: {[e.get('name') for e in employees]}")
                
                # If result is a list (Odoo 18), we need to add employee model differently
                if isinstance(result, list):
                    _logger.info("=== POS SALESPERSON DEBUG: Result is a list, appending hr.employee model")
                    result.append({
                        'model': 'hr.employee',
                        'fields': employee_fields,
                        'domain': [('active', '=', True)],
                    })
                else:
                    # If result is a dict (fallback for older versions)
                    _logger.info("=== POS SALESPERSON DEBUG: Result is a dict, adding hr.employee data")
                    result['hr.employee'] = {
                        'data': employees,
                        'fields': employee_fields
                    }
                _logger.info("=== POS SALESPERSON DEBUG: Added hr.employee to result")
            else:
                _logger.info(f"=== POS SALESPERSON DEBUG: Salesperson not enabled. hasattr: {hasattr(config_id, 'allow_salesperson')}, value: {getattr(config_id, 'allow_salesperson', 'NOT_FOUND')}")
        except Exception as e:
            _logger.error(f"=== POS SALESPERSON DEBUG: Error in _load_pos_data_models: {e}")
            import traceback
            _logger.error(traceback.format_exc())
        
        _logger.info(f"=== POS SALESPERSON DEBUG: Final result type: {type(result)}")
        _logger.info(f"=== POS SALESPERSON DEBUG: Final result: {result}")
        return result
