# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import MySQLdb

class erp_mysql(osv.osv):
    _name = "erp.mysql"
    _description = "ERP Mysql configuration"
    _columns = {
        'name': fields.char('Instance Name', size=64, required=True),
        'host': fields.char('Host Name', size=64, required=True),
        'user': fields.char('User Name', size=64, required=True),
        'password': fields.char('Password Name', size=64, required=True),
        'db_name': fields.char('Your Database', size=64, required=True),
        'table_name': fields.char('Table Name', size=64, required=True),

    }
    def action_button_confirm(self, cr, uid, ids, context=None):
        
        import ipdb;ipdb.set_trace()
        account_inv_obj=self.pool.get('account.invoice')
        config_obj=self.browse(cr,uid,ids[0])
        try:
            db = MySQLdb.connect(host=config_obj.host,user=config_obj.user,passwd=config_obj.password)
        except Exception as e:
            print e
        cursor = db.cursor()
        account_inv_ids=account_inv_obj.search(cr,uid,[])
        for i in account_inv_ids:
            account_inv_data=account_inv_obj.browse(cr,uid,i)
            sync_query=str('''INSERT INTO {}.{} (inv_no,customer,product,price,qty,amount,state)'''.format())
            '''INSERT INTO erp.account_inv (inv_no, customer,product,price,qty ,amount,state) VALUES \
            ('{}', '{}','{}', '{}','{}','{}','{}');'''.format(account_inv_data.number,account_inv_data.name,account_inv_data.product)
            
        
            
        
        

erp_mysql()
