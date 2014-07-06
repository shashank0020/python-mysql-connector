# -*- coding: UTF-8 -*-
'''
    magento-integration

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) LTD
    :license: AGPLv3, see LICENSE for more details
'''
import MySQLdb
import socket

from openerp.osv import osv
from openerp.tools.translate import _
import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _



class erp_mysqltest(osv.TransientModel):
    "Test erp-mysql Connection"
    _name = 'erp.mysqltest'
    _description = __doc__

    def default_get(self, cursor, user, fields, context):
        """Set a default state

        :param cursor: Database cursor
        :param user: ID of current user
        :param fields: List of fields on wizard
        :param context: Application context
        """
        
        self.test_connection(cursor, user, context)
        return {}

    def test_connection(self, cursor, user, context):
        """Test the connection to mysql instance(s)

        :param cursor: Database cursor
        :param user: ID of current user
        :param context: Application context
        """
        Pool = self.pool
        

        instance_obj = Pool.get('erp.mysql')

        instance = instance_obj.browse(
            cursor, user, context.get('active_id'), context
        )
        try:
            db = MySQLdb.connect(host=instance.host,user=instance.user,passwd=instance.password)
        except Exception as e:
            
            raise osv.except_osv(
                _('Incorrect Mysql connection Settings!'),
                _('Please check and correct the Mysql connection Settings on instance.')
            )

erp_mysqltest()
