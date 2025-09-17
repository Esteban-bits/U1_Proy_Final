import pymysql

def obtener_conexion():
    return pymysql.connect(host='localhost', user='root', password='root', db='purificadoraproduccion')
