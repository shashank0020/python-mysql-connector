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
    def _constrain_check(self,cr,uid,ids):
       # import ipdb;ipdb.set_trace()
        rec=self.browse(cr,uid,ids[0])
        if rec.x_int<0:
            return False
        return True
    
    _columns = {
        'name': fields.char('Instance Name', select=2,size=64, required=False),
        'host': fields.char('Host Name',size=64, required=False),
        'user': fields.char('User Name', size=64, required=False),
        'password': fields.char('Password Name', size=64, required=False),
        'db_name': fields.char('Your Database', size=64, required=False),
        'table_name': fields.char('Table Name', size=64, required=False),
        'type': fields.selection([('sale.order', 'Sale Order'), ('purchase.order', 'Purchase order'),\
                                   ('account.invoice', 'Invoice')], 'Objects'),
        'active_bool': fields.boolean('Create Database /Tables'),
        'inv_no': fields.char('Document Number', size=64, required=False),
        'customer': fields.char('Partner', size=64, required=False),
        'product': fields.char('Product', size=64, required=False),
        'price': fields.char('Price', size=64, required=False),
        'qty': fields.char('Qty', size=64, required=False),
        'states': fields.char('State', size=64, required=False),
        'state': fields.selection([
    ('new','New'),
    ('assigned','Assigned'),
    ('negotiation','Negotiation')
    ], 'Stage', readonly=True),
    'x_int': fields.integer('x_int'),                
        
    }
    _log_access=True
    _order='name'
    _rec_name='host'
    _constraints = [
        (_constrain_check, 'Number should be positive.', ['x_int']),
    ]
    _sql_constraints = [('deduction_registration_name_unique', 'unique(name)', 'Instance name Already exist')]
    _defaults = {'state':'new'
}                     
    

    
    
    def mymod_new(self, cr, uid, ids):
        import ipdb;ipdb.set_trace()
        
        self.write(cr, uid, ids, { 'state' : 'new' })
        return True
    
    def mymod_assigned(self, cr, uid, ids):
        import ipdb;ipdb.set_trace()
        
        self.write(cr, uid, ids, { 'state' : 'assigned' })
        return True
    
    def mymod_negotiation(self, cr, uid, ids):
        import ipdb;ipdb.set_trace()
        
        self.write(cr, uid, ids, { 'state' : 'negotiation' })
        return True
    


    
    def cron_func(self,cr,uid):
        ''' Running scheduler for Sync'''
        context={'cron_job':True}
        
        
        self_id=self.search(cr,uid,[])
        
        for ids in self_id:
            self.sync_data(cr, uid, [ids], context)
        return True

    
    def sync_data(self, cr, uid, ids, context):
        '''Sync between OpenERP -Mysql '''
    
        
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
{} VARCHAR(45) NOT NULL,\
{} VARCHAR(45) NOT NULL,\
{} VARCHAR(45) NOT NULL,\
{} FLOAT NOT NULL,\
{} FLOAT NOT NULL,\
{} VARCHAR(45) NOT NULL\
);'''.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,config_obj.customer,config_obj.product,config_obj.price,\
             config_obj.qty,config_obj.state))
        
        #import ipdb;ipdb.set_trace()
        try: 
            cursor.execute(create_table_sql)
        except Exception as e:
            print e
            
        #fetch records from mysql
        select_query=str('select erp_mysql_map from {}.{} '.format(config_obj.db_name,config_obj.table_name))
        cursor.execute(select_query)
        result=cursor.fetchall()
        
        map_list=[ij[0] for ij in result]
            
        
        #fetch records from erp according to object selected
        
        if config_obj.type=='sale.order':
            order_ids=order_obj.search(cr,uid,[])
            for i in order_ids:
                order_line_ids=order_line_obj.search(cr,uid,[('order_id','=',i)])
                for j in order_line_ids:
                    order_data,order_line_data=order_obj.browse(cr,uid,i),order_line_obj.browse(cr,uid,j)
                    if i in map_list:
                    
                        update_sql=str('''UPDATE {}.{} SET {}='{}', {}='{}' where erp_mysql_map={} '''\
.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,order_data.name,config_obj.state,order_data.state,i))
                        cursor.execute(update_sql)
                    
                    else:
                
                        insert_sql=str('''INSERT INTO {}.{}\
(erp_mysql_map,{}, {},{},{},{},\
{}) \
VALUES ('{}','{}','{}','{}',{},{},'{}');'''\
.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,config_obj.customer,config_obj.product,config_obj.price,\
config_obj.qty,config_obj.state,i,order_data.name,\
order_data.partner_id.name,order_line_data.product_id.name,order_line_data.price_unit,\
order_line_data.product_uom_qty,order_data.state))
                    
                    
                        cursor.execute(insert_sql)
            
            
            
            
        elif config_obj.type=='purchase.order':  
            order_ids=order_obj.search(cr,uid,[])
            for i in order_ids:
                order_line_ids=order_line_obj.search(cr,uid,[('order_id','=',i)])
                for j in order_line_ids:
                    order_data,order_line_data=order_obj.browse(cr,uid,i),order_line_obj.browse(cr,uid,j)
                    if i in map_list:
                    
                        update_sql=str('''UPDATE {}.{} SET {}='{}', {}='{}' where erp_mysql_map={} '''\
.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,order_data.name,config_obj.state,order_data.state,i))
                        cursor.execute(update_sql)
                    
                    else:
                
                        insert_sql=str('''INSERT INTO {}.{}\
(erp_mysql_map,{}, {},{},{},{},\
{}) \
VALUES ('{}','{}','{}','{}',{},{},'{}');'''\
.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,config_obj.customer,config_obj.product,config_obj.price,\
config_obj.qty,config_obj.state,i,order_data.name,\
order_data.partner_id.name,order_line_data.product_id.name,order_line_data.price_unit,\
order_line_data.product_qty,order_data.state))
                    
                    
                        cursor.execute(insert_sql)
        
        
        
        elif config_obj.type=='account.invoice':
            account_inv_ids=order_obj.search(cr,uid,[])
            for i in account_inv_ids:
                account_line_ids=order_line_obj.search(cr,uid,[('invoice_id','=',i)])
                for j in account_line_ids:
                    account_inv_data,account_line_data=order_obj.browse(cr,uid,i),order_line_obj.browse(cr,uid,j)
                    if i in map_list:
                    
                        update_sql=str('''UPDATE {}.{} SET {}='{}', {}='{}' where erp_mysql_map={} '''\
.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,account_inv_data.number,config_obj.state,account_inv_data.state,i))
                        cursor.execute(update_sql)
                    
                    else:
                
                        insert_sql=str('''INSERT INTO {}.{}\
(erp_mysql_map,{}, {},{},{},{},\
{}) \
VALUES ('{}','{}','{}','{}',{},{},'{}');'''\
.format(config_obj.db_name,config_obj.table_name,config_obj.inv_no,config_obj.customer,config_obj.product,config_obj.price,\
config_obj.qty,config_obj.state,i,account_inv_data.number,\
account_inv_data.partner_id.name,account_line_data.product_id.name,account_line_data.price_unit,\
account_line_data.quantity,account_inv_data.state))
                    
                    
                        cursor.execute(insert_sql)
            
        else:
            raise osv.except_osv(
                _('No object or Incorrect object is choosen !'),
                _('Please select object to proceed.')
            )
    
            
            
        
                    
        db.commit()
        db.close()
        
        if context.get('cron_job',False)==True:
            
            print 'Synchronization Completed\n Please check your Mysql Database'
        else:
            
            raise osv.except_osv(
                    _('Synchronization Completed'),
                    _('Please check your Mysql Database')
                )
        return True
             



        
                
erp_mysql()

