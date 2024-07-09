# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import werkzeug


class Main(http.Controller):

    @http.route(['/myorder'], type='http', auth="public", website=True,methods=['GET'])
    def index(self, **kw):
        st=""
        for product in request.env['product.product'].sudo().search([]):
            st+="<option value="+str(product.id)+">"+product.name+"</option>"
        print(">>>>",st)
        values = {'projects': st}
        return request.render('portal_sale_order.create_order', values)

    @http.route('/myorder/submit', type='http', auth='public', methods=['GET','POST'])
    def submit(self, **kw):
        st = ""
        if kw:
            partner_id=request.env.user.partner_id.id
            del kw['submitted']
            del kw['submit']
            lines=[]
            lines2=[]
            for i in range(0,len(kw)):
                if kw.get('item'+str(i)):
                    product_id=kw.get('item'+str(i))
                if kw.get('q'+str(i)):
                    qty=kw.get('q'+str(i))

                if product_id not in lines2:
                    lines2.append(product_id)
                    lines.append((0,0,{
                        'product_id':int(product_id),
                        'name':request.env['product.product'].sudo().search([('id','=',product_id)],limit=1).name,
                        'product_uom_qty':qty,
                    }))

            if partner_id:
                request.env['sale.order'].sudo().create({
                     'partner_id':partner_id,
                    'order_line':lines
                 })
                return werkzeug.utils.redirect('/myorder/thank/')
            else:
                return  self.error("Partner Code Error!")


    @http.route('/myorder/thank/', website=True, auth="public")
    def thank(self, **kw):
        return http.request.render('portal_sale_order.order_thank')

    @http.route('/myorder/error/', auth="public")
    def error(self,error, **kw):
        return http.request.render('portal_sale_order.order_error',{'error':error})



