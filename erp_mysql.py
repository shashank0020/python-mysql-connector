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
        'type': fields.selection([('sale.order', 'Sale Order'), ('purchase.order', 'Purchase order'),\
                                   ('account.invoice', 'Invoice')], 'Objects'),
        'active_bool': fields.boolean('Create Database /Tables'),
    }
    def sync_data(self, cr, uid, ids, context=None):
        
        
        map_ids=[]
        config_obj=self.browse(cr,uid,ids[0])        
        if config_obj.type=='sale.order':
            order_obj=self.pool.get(config_obj.type)
            order_line_obj=self.pool.get('sale.order.line')
            
        elif config_obj.type=='purchase.order':
            order_obj=self.pool.get(config_obj.type)
            order_line_obj=self.pool.get('purchase.order.line')
            
        elif config_obj.type=='account.invoice':
            order_obj=self.pool.get(config_obj.type)
            order_line_obj=self.pool.get('account.invoice.line')
            
        else:
            raise osv.except_osv(
                _('No object is choosen !'),
                _('Please select object to proceed.')
            )
            
            

#conenct to mysql        
        try:
            db = MySQLdb.connect(host=config_obj.host,user=config_obj.user,passwd=config_obj.password)
        except Exception as e:
            print e
            raise osv.except_osv(
                _('Incorrect Mysql connection Settings!'),
                _('Please check and correct the Mysql connection Settings on instance.')
            )
        cursor = db.cursor()
#create new database
        
        create_db=str('''CREATE DATABASE {};'''.format(config_obj.db_name))
          
        try:
            cursor.execute(create_db)
        except Exception as e:
            print e      
#create a new table in Mysql
        create_table_sql=str('''CREATE TABLE {}.{}\
(erp_mysql_map INT NOT NULL,\
inv_no VARCHAR(45) NOT NULL,\
customer VARCHAR(45) NOT NULL,\
product VARCHAR(45) NOT NULL,\
price FLOAT NOT NULL,\
qty FLOAT NOT NULL,\
state VARCHAR(45) NOT NULL\
);'''.format(config_obj.db_name,config_obj.table_name))
        
        try: 
            cursor.execute(create_table_sql)
        except Exception as e:
            print e
            
        #fetch records from mysql
        select_query=str('select erp_mysql_map from {}.{} '.format(config_obj.db_name,config_obj.table_name))
        cursor.execute(select_query)
        result=cursor.fetchall()
        
        map_list=[ij[0] for ij in result]
            
        
        
        account_inv_ids=order_obj.search(cr,uid,[])
        for i in account_inv_ids:
            account_line_ids=order_line_obj.search(cr,uid,[('invoice_id','=',i)])
            for j in account_line_ids:
                account_inv_data,account_line_data=order_obj.browse(cr,uid,i),order_line_obj.browse(cr,uid,j)
                if i in map_list:
                    import ipdb;ipdb.set_trace()
                    update_sql=str('''update {}.{} set state='{}' where erp_mysql_map={} '''\
.format(config_obj.db_name,config_obj.table_name,account_inv_data.state,i))
                    cursor.execute(update_sql)
                else:
                
                    insert_sql=str('''INSERT INTO {}.{}\
    (erp_mysql_map,inv_no, customer,product,price,qty,\
    state) \
    VALUES ('{}','{}','{}','{}',{},{},'{}');'''\
    .format(config_obj.db_name,config_obj.table_name,i,account_inv_data.number,\
    account_inv_data.partner_id.name,account_line_data.product_id.name,account_line_data.price_unit,\
    account_line_data.quantity,account_inv_data.state))
                    
                     
                    cursor.execute(insert_sql)
            db.commit()
            db.close()
        
        raise osv.except_osv(
                _('Synchronization Completed'),
                _('Please check your Mysql Database')
            )
        return True
             



        
                
erp_mysql()
