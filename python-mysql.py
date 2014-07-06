import MySQLdb
db1 = MySQLdb.connect(host="localhost",user="root",passwd="root")
cursor = db1.cursor()
create_db='''CREATE DATABASE erp;'''
cursor.execute(create_db)

create_table_sql='''CREATE TABLE erp.account_inv (
  inv_no INT NOT NULL AUTO_INCREMENT,
  product VARCHAR(45) NOT NULL,
  amount VARCHAR(45) NOT NULL,
  state VARCHAR(45) NOT NULL,
  PRIMARY KEY (`inv_no`));'''

cursor.execute(create_table_sql)

insert_sql='''INSERT INTO erp.account_inv (inv_no, product, amount) VALUES ('SAJ001', 'PEPSI', '12');'''
cursor.execute(insert_sql)

select_sql='''SELECT * FROM erp.account_inv'''

cursor.execute(select_sql)

#fetch values from mysql

for row in cursor.fetchall() :
    print row

db.commit()
db.close()
