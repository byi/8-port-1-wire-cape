#!/usr/bin/python

# Beginnings of Boiler Monitoring Program

import string
import pyowfs
import datetime
import time
import mysql.connector

def setup_database_connection():
  db = mysql.connector.Connect(host="localhost", user="dummy", password="", database="demo", buffered=True)
  return db

def setup_connection (host, port) :
  x = ''
  from pyowfs import Connection
  root = Connection (x.join([host, ':', port]))
  #root = Connection ("localhost:4304")
  return root

def print_something():
  print "Print Something"

def dont_use_cache(root):
  root.use_cache (0)

def build_sensor_dict(root):
  port_map_dict = {}
  port = 1
  port_max = 8
    
  for z in range(port_max) :
      
  #for z in root.find(type="DS18S20") : 
    
    #for e in z.iter_entries () : print e

    sensor_address = '/bus.0/bus.' + str(port - 1)
    address = str(root.capi.get (sensor_address))[11:26]
    
#    type = (z.get ("type"))
#    family = (z.get ("family"))
#    id = (z.get ("id"))
#    locator = (z.get ("locator"))
#    
#    temp = (z.get ("temperature"))
#    #intf = (z.get ("i2c"))
#    tuple = (type, family, id, locator, temp)
#    print tuple
#    port_map_dict[port_key] = (family + '.' + id + '/')
#    port_map_dict[port_key] = str(address[0:2]) + '.' + str(address[2:14]+ '/')

    port_key = 'Port-' + str(port)
    family = address[0:2]
    
    if ((family == '28') or (family == '10')) :
        port_map_dict[port_key] = (address + '/')
        #print port_key
    else :
        port_map_dict[port_key] = ('' + '/')
    
    port += 1

  return(port_map_dict)

def print_temp2(root):
    for z in root.find(type="temperature") : 
        print (z.get ("type")),
        print (z.get ("address")),
        print (z.get ("id")),
        print (z.get ("temperature"))


def iterroot(root):
  for e in root.get("bus.0").iter_entries () : 
    print e
    for p in root.iter_entries () : 
      print p	

def fullpath(root):
#  print (root.capi.get ("/bus.0/bus.1/10.3B18A6010800/templow"))
   print (root.capi.put ("/bus.0/bus.1/10.3B18A6010800/templow", "10"))
#  print (root.capi.get ("/bus.0/bus.1/10.3B18A6010800/templow"))
#  print (root.capi.get ("/bus.0/bus.1/10.3B18A6010800/temphigh"))

def print_port_temps(root, port_map_dict):

  for port_number, ow_address in sorted(port_map_dict.iteritems()):
      if ow_address != '/' :
          temperature_deg_C = float(root.capi.get (ow_address + "temperature"))
          temperature_deg_F = 1.8 * temperature_deg_C + 32.0
          print "%s %s %5.1f" % (port_number, ow_address, temperature_deg_F)
      else :
          print "%s %s" % (port_number, "No Sensors Found")
        
          
def logtodb_port_map(root, port_map_dict, db):
    
  port = 1
  
  for port_number, ow_address in sorted(port_map_dict.iteritems()):
      
    one_port = []
    
    one_port.append("%s" % (port_number))
    
    if ow_address != '/' :

        one_port.append("%s" % (str(ow_address[0:15])))
 
        one_port.append("%s" % (root.capi.get (ow_address + "type")))
        
        stmt_update = "UPDATE port_map SET physical_name = %s, sensor_id = %s, sensor_type = %s WHERE id = %s"

    else :

        one_port.append("%s" % ("No Sensor"))
        one_port.append("%s" % (""))
    
    one_port.append("%s" % (port))
    
    #print one_port
    cursor = db.cursor()
    cursor.execute(stmt_update, one_port)
    db.commit()   
    port += 1   


def logtodb_port_temps(root, port_map_dict, db):
  all_temps = []
  #now = datetime.datetime.now()
  #print str(now),

  for port_number, ow_address in sorted(port_map_dict.iteritems()):
    if ow_address != '/' :
        #temperature_deg_C = float(root.capi.get ("/uncached/" + ow_address + "temperature"))
        temperature_deg_C = float(root.capi.get (ow_address + "temperature"))
        temperature_deg_F = 1.8 * temperature_deg_C + 32.0
        all_temps.append("%5.1f" % (temperature_deg_F))
        #print ("%5.1f" % (temperature_deg_F)),
    elif ow_address == '/':
        all_temps.append("%5.1f" % (0))
    else :
        print "No Sensors Found"

  #print all_temps


  stmt_insert = "INSERT INTO boilerdb (datetime, temp1, temp2, temp3, temp4, temp5, temp6, temp7, temp8) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s)"

  cursor = db.cursor()
  cursor.execute(stmt_insert, all_temps)
  db.commit()

def main():

  root = setup_connection('localhost', '4304')
  db = setup_database_connection()
  #dont_use_cache(root)
  #fullpath(root)
  #iterroot(root)
  port_map_dict = build_sensor_dict(root)

#  for key in sorted(port_map_dict.keys()):
#	print key, port_map_dict[key]

  print_port_temps(root, port_map_dict)
  logtodb_port_map(root, port_map_dict, db)
  
  print "Begin logging sensor data to demo database"

  while True: 
    logtodb_port_temps(root, port_map_dict, db)
    time.sleep(30)

  #iterroot(root)
  #for s in root.path : print s
  #fullpath(root)

  # Command line args are in sys.argv[1], sys.argv[2] ..
  # sys.argv[0] is the script name itself and can be ignored

if __name__ == '__main__':
  main()

