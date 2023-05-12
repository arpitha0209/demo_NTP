import re
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import shlex
import json
import time
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from time import sleep
import pexpect
import subprocess
import ib_utils.common_utilities as common_util
import random
import string



logging.basicConfig(filename='cas.log', filemode='w', level=logging.DEBUG)

def display_msg(msg):
    print(msg)
    logging.info(msg)

def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(20)



class NTP(unittest.TestCase):

    
    @pytest.mark.run(order=1)
    def test_001_generate_SHA1_key_server1(self):

	global server1_key0
	global server1_key1
	global server1_key2

	
	display_msg("Generating SHA1 Key")    
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid2_master_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('ntp-keygen -M')
        child.expect('#')
        child.sendline('grep "11 SHA1" ntpkey_MD5key_master.grid_2.infoblox*')
     	#child.sendline('grep "11 SHA1" ntpkey_MD5key_infoblox*')
        child.expect('#')
        key = child.before
        print(key)

        res=key.split(':')[1]
        print(res)
        x = res.split(' ')
        print(x[0],type(x[0]),x[1],type(x[1]),x[2],type(x[2]))
        server1_key0=x[0]
        print(server1_key0)
        server1_key1=x[1]
        print(server1_key1)
        server1_key2=x[2]
        print(server1_key2)
        child.close()

        display_msg("Enabling ntp on grid master")
        request = ib_NIOS.wapi_request('GET', object_type="grid", params='?_return_fields=ntp_setting',grid_vip=config.grid2_master_vip)
        request = json.loads(request)
        print(request)
        request_ref = request[0]['_ref']
        print(request_ref)
        data = {"ntp_setting": {"ntp_keys": [{"number":int(server1_key0),"type":"SHA1_ASCII","string":str(server1_key2)}]}}
        response = ib_NIOS.wapi_request('PUT', object_type=request_ref, fields=json.dumps(data) ,grid_vip=config.grid2_master_vip)
        print(response)

	if type(response) == tuple:
                display_msg(json.loads(response[1])['text'])
                display_msg("FAIL: Failed to add  NTP key and String, Debug")
                assert False
        else:
                display_msg(response)
                display_msg("PASS: Successfully added NTP Key and String")

	
        display_msg("Validate added NTP key and string")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type="grid", params='?_return_fields=ntp_setting',grid_vip=config.grid2_master_vip)

        display_msg(get_ref1)
        result = server1_key0
        if result in get_ref1:
            display_msg("PASS: Successfully validated NTP Key.")
        else:
            display_msg("FAIL: NTP Key not found.")
            assert False

        result1 = server1_key2
        if result1 in get_ref1:
            display_msg("PASS: Successfully validated NTP String.")
        else:
            display_msg("FAIL: NTP String not found.")
            assert False

      

	request1 = ib_NIOS.wapi_request('GET', object_type="member", params='?_return_fields=ntp_setting',grid_vip=config.grid2_master_vip)
        request1 = json.loads(request1)
        print(request1)
        res_ref1 = request1[0]['_ref']
        print("Grid reference",res_ref1)

        data1 = {"ntp_setting":{"enable_ntp": True }}
        res1 = ib_NIOS.wapi_request('PUT', object_type=res_ref1, fields=json.dumps(data1) ,grid_vip=config.grid2_master_vip)
        print(res1)

	display_msg("Validating if NTP ENABLED on grid member")
        request2 = ib_NIOS.wapi_request('GET', object_type="member", params='?_return_fields=ntp_setting',grid_vip=config.grid2_master_vip)
        print(request2)
        request2 = json.loads(request2)
        display_msg(request2)
        request_ref = request2[0]['_ref']
        display_msg(request_ref)
        res2 = ib_NIOS.wapi_request('GET', object_type=request_ref, params='?_return_fields=ntp_setting' ,grid_vip=config.grid2_master_vip)
        print(res2)
        res2 = json.loads(res2)
        res_enable = res2['ntp_setting']['enable_ntp']
        display_msg(res_enable)
        if res_enable == True:
       		display_msg("NTP is enabled")
                assert True
        else:
                display_msg("NTP is not enabled")
                assert False
        display_msg("TestCase 001 executed successfully")


    @pytest.mark.run(order=2)
    def test_002_generate_SHA1_key_server2(self):

        global server2_key0
        global server2_key1
        global server2_key2

        display_msg("Generating SHA1 Key")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid3_master_vip )
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('ntp-keygen -M')
        child.expect('#')
        child.sendline('grep "12 SHA1" ntpkey_MD5key_master.grid_3.infoblox*')
	    #child.sendline('grep "12 SHA1" ntpkey_MD5key_infoblox*')
        child.expect('#')
        key = child.before
        print(key)
        res=key.split(':')[1]
        print(res)
        x = res.split(' ')
        print(x[0],type(x[0]),x[1],type(x[1]),x[2],type(x[2]))
        server2_key0=x[0]
        print(server2_key0)
        server2_key1=x[1]
        print(server2_key1)
        server2_key2=x[2]
        print(server2_key2)
        child.close()

        display_msg("Enabling ntp on grid master")
        request = ib_NIOS.wapi_request('GET', object_type="grid", params='?_return_fields=ntp_setting',grid_vip=config.grid3_master_vip )
        print(request)
        request = json.loads(request)
        print(request)
        request_ref = request[0]['_ref']
        print(request_ref)
        data = {"ntp_setting": {"ntp_keys": [{"number":int(server2_key0),"type":"SHA1_ASCII","string":str(server2_key2)}]}}
        response = ib_NIOS.wapi_request('PUT', object_type=request_ref, fields=json.dumps(data) ,grid_vip=config.grid3_master_vip )
        print(response)

	if type(response) == tuple:
                display_msg(json.loads(response[1])['text'])
                display_msg("FAIL: Failed to add  NTP key and String, Debug")
                assert False
        else:
                display_msg(response)
                display_msg("PASS: Successfully added NTP Key and String")

	
        display_msg("Validate added NTP key and string")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type="grid", params='?_return_fields=ntp_setting',grid_vip=config.grid3_master_vip )

        display_msg(get_ref1)
        result = server2_key0
        if result in get_ref1:
            display_msg("PASS: Successfully validated NTP Key.")
        else:
            display_msg("FAIL: NTP Key not found.")
            assert False

        result1 = server2_key2
        if result1 in get_ref1:
            display_msg("PASS: Successfully validated NTP String.")
        else:
            display_msg("FAIL: NTP String not found.")
            assert False

      

	request1 = ib_NIOS.wapi_request('GET', object_type="member", params='?_return_fields=ntp_setting',grid_vip=config.grid3_master_vip )
        request1 = json.loads(request1)
        print(request1)
        res_ref1 = request1[0]['_ref']
        print("Grid reference",res_ref1)

        data1 = {"ntp_setting":{"enable_ntp": True }}
        res1 = ib_NIOS.wapi_request('PUT', object_type=res_ref1, fields=json.dumps(data1) ,grid_vip=config.grid3_master_vip )
        print(res1)

	display_msg("Validating if NTP ENABLED on grid member")
        request2 = ib_NIOS.wapi_request('GET', object_type="member", params='?_return_fields=ntp_setting',grid_vip=config.grid3_master_vip )
        print(request2)
        request2 = json.loads(request2)
        display_msg(request2)
        request_ref = request2[0]['_ref']
        display_msg(request_ref)
        res2 = ib_NIOS.wapi_request('GET', object_type=request_ref, params='?_return_fields=ntp_setting' ,grid_vip=config.grid3_master_vip )
        print(res2)
        res2 = json.loads(res2)
        res_enable = res2['ntp_setting']['enable_ntp']
        display_msg(res_enable)
        if res_enable == True:
       		display_msg("NTP is enabled")
                assert True
        else:
                display_msg("NTP is not enabled")
                assert False
        display_msg("TestCase 002 executed successfully")

    
    @pytest.mark.run(order=3)
    def test_003_increase_time_to_120_secs(self):
        display_msg("Getting Time")
        
	try :
	    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('#')
	
	    child.sendline('date')
       	    child.expect('#')
            
            child.sendline('date -s "now + 2 minutes"')
            child.expect('#')

            child.sendline('date')
            child.expect('#')

            child.close()
	    assert True

        except Exception as e:
            child.close()
            print("Failure:")
            print (e)
            assert False

        display_msg("TestCase 003 executed successfully")

        
    @pytest.mark.run(order=4)
    def test_004_adding_ntp_keys_server(self):
        display_msg("Adding NTP Keys and Server")

        display_msg("Starting log capture")
	log("start","/var/log/messages",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
            
	key0 = server1_key0
	print("###########KEY-NUMBER#######",key0)
	key1 = server1_key2
	print("###########KEY-STRING#######",key1)

	request = ib_NIOS.wapi_request('GET' , object_type='grid')
        request = json.loads(request)
        print(request)
        res_ref = request[0]['_ref']
        print("Grid reference",res_ref)
            
	data = {"ntp_setting":{"enable_ntp": True ,"ntp_servers": [{"address": config.grid2_master_vip, "burst": True, "enable_authentication": True,"iburst": True, "ntp_key_number": int(key0), "preferred": False}],"ntp_keys": [{"number":int(key0),"type":"SHA1_ASCII","string":str(key1)}],"use_default_stratum": True }}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
	print("%%%%%%%%%%%%%%%%%%%%",request1)

	if type(request1) == tuple:
        	display_msg(json.loads(request1[1])['text'])
        	display_msg("FAIL: Failed to add  NTP keys and Servers, Debug")
        	assert False
    	else:
        	display_msg(request1)
        	display_msg("PASS: Successfully added NTP Keys and Servers")

	display_msg("Validate added NTP server and key")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting')
        display_msg(get_ref1)
	result = config.grid2_master_vip
        if result in get_ref1:
            display_msg("PASS: Successfully validated NTP server.")
        else:
            display_msg("FAIL: NTP server not found.")
            assert False

	result1 = key0
	if result1 in get_ref1:
            display_msg("PASS: Successfully validated NTP key.")
        else:
            display_msg("FAIL: NTP key not found.")
            assert False
        

        display_msg("Added NTP keys and Server")
	display_msg("Giving sleep time to apply the changes")
	sleep(60)

	display_msg("Ping the Grid ip and check if it is reachable")
	
	
	for i in range(10):
		ping = os.popen("ping -c 5 " + config.grid_vip).read()
		display_msg(ping)
		if "0 received" not in ping:
      			display_msg(config.grid_vip+" is pinging ")
			display_msg("Member restart is successfull")
      			assert True
			break
		else :
			print(config.grid_vip+" is not pinging, Going to sleep for 60 seconds ")
            		sleep(60)
            		if i == 9:    
				assert False

	display_msg("Adding NTP Keys and Server has been completed")
        display_msg("TestCase 004 executed successfully")


    @pytest.mark.run(order=5)
    def test_005_validate_log_keys_server(self):
	display_msg("Validate log NTP Keys and Server")

        display_msg("Stopping log capture")
	log("stop","/var/log/messages",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)



	count = 0

	display_msg("Validate NTP keys added")
        #validate = logv(".*check_ntp_conf.*"+trustedkey  "+server1_key0+".*","/infoblox/var/infoblox.log",config.grid_vip)
        validate = logv(".*check_ntp_conf.*trustedkey  "+server1_key0+".*","/infoblox/var/infoblox.log",config.grid_vip)
	print("VALIDATE",validate)
	if validate != None:
            count +=1
            display_msg("NTP key is added")
        else:
            display_msg("NTP is not added, debug failures")

        display_msg("Validate NTP server added")
        #validate = logv(".*check_ntp_conf.*+server "+server1_key2+" key "+server1_key0+".*","/infoblox/var/infoblox.log",config.grid_vip)
        validate = logv(".*check_ntp_conf.*server "+config.grid2_master_vip+".*key.*"+server1_key0+".*","/infoblox/var/infoblox.log",config.grid_vip)
	print("VALIDATE",validate)
	if validate != None:
            count +=1
            display_msg("NTP server is added")
        else:
            display_msg("NTP server is not added, debug failures")

        display_msg("Validate syslog for NTP server added")
        validate = logv(".*notice ntpdate 4.2.8p15@1.3728-o.*","/var/log/messages",config.grid_vip)
        print("VALIDATE",validate)
	if validate != None:
            count +=1
            display_msg("Syslog validation successful")
        else:
            display_msg("Syslog validation failed")

        display_msg("Validate NTP server reachable in the logs")
        validate = logv(".*Offset between ntp server.*"+config.grid2_master_vip+".*","/infoblox/var/infoblox.log",config.grid_vip)
        print("VALIDATE",validate)
	
	if validate != None:
            count +=1
            display_msg("NTP Server is reachable")
        else:
            display_msg("NTP server is not reachable")
	print("*****TOTAL COUNT****",count)

        display_msg("Validate Offset value is greater than 60 secs")
        validate = logv(".*greater than 60 secs.*","/infoblox/var/infoblox.log",config.grid_vip)
        print("VALIDATE",validate)

        if validate != None:
            count +=1
            display_msg("Offset value is greater than 60 secs")
        else:
            display_msg("Offset value is lesser than 60 secs")
        print("*****TOTAL COUNT****",count)

	if count == 5:
	    assert True
	    display_msg("PASS:Log validation is successful")
	else:
	    display_msg("FAIL:Log validation is failed")
	    assert False
    
	display_msg("Validate NTP Keys and Server is completed")
        display_msg("TestCase 005 executed successfully")


    @pytest.mark.run(order=6)
    def test_006_Validate_ntp_conf(self):
	display_msg("Validate NTP conf")

	count = 0

	logging.info("Validate NTP server is added in ntp.conf")
	ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /tmpfs/ntp.conf | grep burst"'
	ntp_conf_cmd = commands.getoutput(ntp_conf)
	print("Command output",ntp_conf_cmd)

	if re.search(r'.*server '+config.grid2_master_vip+'.*burst.*',ntp_conf_cmd):
	    count +=1
	    display_msg("Server details are present in ntp conf")
	else:
	    display_msg("Server details not present in ntp conf")

        ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /tmpfs/ntp.conf | grep trustedkey"'
        ntp_conf_cmd1 = commands.getoutput(ntp_conf)
        print("Command output",ntp_conf_cmd1)

	if re.search(r'.*trustedkey.*'+server1_key0+'.*',ntp_conf_cmd1):
	    count +=1
	    display_msg("Key detail is present in ntp conf")
	else:
	    display_msg("Key detail is not present in ntp conf")

	if count == 2:
	    assert True
	    display_msg("PASS:All details are present in ntp config file")
	else:
	    display_msg("FAIL:Not all details are present in ntp config file")
	    assert False

	display_msg("Testcase 006 execution completed successfully")

    @pytest.mark.run(order=7)
    def test_007_Validate_ntp_key(self):
        display_msg("Validate NTP key in NTP client")
	
        logging.info("Validate NTP server is added in ntp.conf")
        ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /etc/ntp.keys"'
        ntp_conf_cmd = commands.getoutput(ntp_conf)
        print("Command output",ntp_conf_cmd)
	a = ntp_conf_cmd.split()
	print("$$$$$$$$$$$$$$$$$$",a)
	
	print("KEY STRING",a[-1])
	print("KEY TYPE",a[-2])
	print("KEY NUMBER",a[-3])
	
	if a[-1] == server1_key2 and a[-2] == server1_key1 and a[-3] == server1_key0:
	    assert True
	    display_msg("PASS:Key is added")
	else:
	    display_msg("FAIL:Key is not added")
	    assert False

	sleep(100)
	
	display_msg("Testcase 007 execution completed successfully")

    @pytest.mark.run(order=8)
    def test_008_validate_ntpq_command(self):
	display_msg("Validate NTPQ -P command status")
	

	try:
           child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
	   child.logfile=sys.stdout
    	   child.expect('#')
    	   child.sendline('ntpq -p > note.txt')
           child.expect('#')

    	   child.sendline('grep -e "*"  note.txt')
    	   child.expect('#')
    	   data = child.before
 	   child.close()

    	   print("Before data",data)
    	   n = data.split()
    	   print("########",n)
	
	   count = 0

    	   print("SERVER-IP",n[-11])
    	   a = n[-11]
	   c = a[1:]
	   print("^^^^^^^^^SERVER-IP^^^^^^^^",c)
	   print("////////////////////////",config.grid2_master_vip)
	
       	   if c == config.grid2_master_vip:
	   	count +=1
	    	display_msg("Server IP is reachable")
	   else:
	    	display_msg("Server IP isn't available")

	   print("@@@@@@@@",n[-10])
	   b = n[-10]
    	   if re.search(r'LOCAL.*',b):
	    	count +=1
	    	display_msg("Server reachable, pass")
	   else:
	   	display_msg("Server not reachable, debug")

	   if count == 2:
	    	assert True
	    	display_msg("PASS:NTP server is in Sync")
	   else:
		display_msg("FAIL:NTP server is not in Sync")
	    	assert False

    	   print("Validate ntpq conf is completed")

	except Exception as e:
           child.close()
           print("Failure:")
           print (e)
           assert False

    	display_msg("TestCase 008 executed successfully")


    @pytest.mark.run(order=9)
    def test_009_Validate_ntp_conf_ps_ax(self):
        display_msg("Validate NTP conf ps ax")

        count = 0

        logging.info("Validate /tmpfs/ntp.conf in ntp.conf ps ax")
        ntp_conf_ps_ax = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "  ps ax | grep ntp"'
        ntp_conf_ps_ax_cmd = commands.getoutput(ntp_conf_ps_ax)
        print("Command output",ntp_conf_ps_ax_cmd)
	
	if re.search(r'.*/usr/bin/ntpd -x -a -c /tmpfs/ntp.conf -f /storage/etc/ntp.drift.*',ntp_conf_ps_ax_cmd):
            count +=1
	    assert True
            display_msg("PASS: /tmpfs/ntp.conf are present in ntp conf ps ax")
        else:
	    display_msg("FAIL: /tmpfs/ntp.conf not present in ntp conf ps ax")
	    assert False
           
	
	display_msg("TestCase 009 executed successfully")

    @pytest.mark.run(order=10)
    def test_010_Validate_string_field_length_for_SHA1_algorithm(self):
	
	display_msg("Validate string field length for SHA1 algorithm")
	key = server1_key2
        print("key string",key)

	length = len(key)
	print("string length is",length)
 	
	if length == 40:
		display_msg("PASS : Key field length for SHA-1 algorithm is 40 digits long")
		assert True
	else :
		display_msg("FAIL : Key field length for SHA-1 algorithm is not 40 digits long")
		assert False
	
	display_msg("Validate string field length for SHA-1 algorithm is completed")
	display_msg("TestCase 010 executed successfully")


    @pytest.mark.run(order=11)
    def test_011_Validate_the_key_value_is_between_1_to_65534(self):

	display_msg("Validate the key value is between 1-65534")
	
	key = int(server1_key0)
	
	print("Key value is",key)



	if  1 <= key <= 65534 :
		assert True
		display_msg("PASS : Key value is between 1-65534")
	else :
		display_msg("FAIL : Key value is not in between 1-65534")
		assert False

	display_msg("Validate the key value is between 1-65534 is completed")
	display_msg("TestCase 011 executed successfully")

    
    
  

#Synchronize this member only with other NTP serveres   
    
     
    @pytest.mark.run(order=12)
    def test_012_increase_time_to_120_secs(self):
        display_msg("Getting Time")

        try :
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_member1_vip)
            child.logfile=sys.stdout
            child.expect('#')

            child.sendline('date')
            child.expect('#')

            child.sendline('date -s "now + 2 minutes"')
            child.expect('#')

            child.sendline('date')
            child.expect('#')

            child.close()
            assert True

        except Exception as e:
            child.close()
            print("Failure:")
            print (e)
            assert False

        display_msg("TestCase 012 executed successfully")


    @pytest.mark.run(order=13)
    def test_013_ntp_service_on_memebrs(self):
        display_msg("Adding NTP Keys and Server")

        display_msg("Starting log capture")
        log("start","/var/log/messages",config.grid1_member1_vip)
        log("start","/infoblox/var/infoblox.log",config.grid1_member1_vip)

        key0 = server2_key0
        print("###########KEY-NUMBER#######",key0)
        key1 = server2_key2
        print("###########KEY-STRING#######",key1)

        request = ib_NIOS.wapi_request('GET' , object_type='member',grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)
        res_ref = request[1]['_ref']
        print("Grid reference",res_ref)

        data = {"ntp_setting":{"enable_ntp": False ,"enable_external_ntp_servers": True,"ntp_servers": [{"address": config.grid3_master_vip, "burst": True, "enable_authentication": True,"iburst": True, "ntp_key_number": int(key0), "preferred": False}],"ntp_keys": [{"number":int(key0),"type":"SHA1_ASCII","string":str(key1)}],"use_default_stratum": True }}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        print("%%%%%%%%%%%%%%%%%%%%",request1)

        if type(request1) == tuple:
                display_msg(json.loads(request1[1])['text'])
                display_msg("FAIL: Failed to add  NTP keys and Servers, Debug")
                assert False
        
	else:
                display_msg(request1)
                display_msg("PASS: Successfully added NTP Keys and Servers")

        display_msg("Validate added NTP server and key")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ntp_setting')
        display_msg(get_ref1)
        result = config.grid3_master_vip
        if result in get_ref1:
            display_msg("PASS: Successfully validated NTP server.")
        else:
            display_msg("FAIL: NTP server not found.")
            assert False

        result1 = key0
        if result1 in get_ref1:
            display_msg("PASS: Successfully validated NTP key.")
        else:
            display_msg("FAIL: NTP key not found.")
            assert False


        display_msg("Added NTP keys and Server")
	display_msg("Giving sleep time to apply the changes")
        sleep(260)

        display_msg("Ping the Grid ip and check if it is reachable")


        for i in range(10):
                ping = os.popen("ping -c 5 " + config.grid1_member1_vip).read()
                display_msg(ping)
                if "0 received" not in ping:
                        display_msg(config.grid1_member1_vip+" is pinging ")
                        display_msg("Member restart is successfull")
                        assert True
			break

                else :
                        print(config.grid1_member1_vip+" is not pinging, Going to sleep for 60 seconds ")
                        sleep(60)
                        if i == 9:
                        	assert False



        display_msg("Adding NTP Keys and Server has been completed")
	display_msg("TestCase 013 executed successfully")

    @pytest.mark.run(order=14)
    def test_014_validate_log_keys_server_on_member(self):
        display_msg("Validate log NTP Keys and Server on member")

        display_msg("Stopping log capture")
        log("stop","/var/log/messages",config.grid1_member1_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid1_member1_vip)



        count = 0

        display_msg("Validate NTP keys added")
        #validate = logv(".*check_ntp_conf.*"+trustedkey  "+server1_key0+".*","/infoblox/var/infoblox.log",config.grid1_member1_vip)
        validate = logv(".*check_ntp_conf.*trustedkey  "+server1_key0+".*","/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("NTP key is added")
        else:
            display_msg("NTP is not added, debug failures")

        display_msg("Validate NTP server added")
        #validate = logv(".*check_ntp_conf.*+server "+server1_key2+" key "+server1_key0+".*","/infoblox/var/infoblox.log",config.grid1_member1_vip)
        validate = logv(".*check_ntp_conf.*server "+config.grid3_master_vip+".*key.*"+server1_key0+".*","/infoblox/var/infoblox.log",config.grid1_member1_vip)
	  
	print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("NTP server is added")
        else:
            display_msg("NTP server is not added, debug failures")

        display_msg("Validate syslog for NTP server added")
        validate = logv(".*notice ntpdate 4.2.8p15@1.3728-o.*","/var/log/messages",config.grid1_member1_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("Syslog validation successful")
        else:
            display_msg("Syslog validation failed")

        display_msg("Validate NTP server reachable in the logs")
        validate = logv(".*Offset between ntp server.*"+config.grid3_master_vip+".*","/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("VALIDATE",validate)

        if validate != None:
            count +=1
            display_msg("NTP Server is reachable")
        else:
            display_msg("NTP server is not reachable")
        print("*****TOTAL COUNT****",count)

        display_msg("Validate Offset value is greater than 60 secs")
        validate = logv(".*greater than 60 secs.*","/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("VALIDATE",validate)

        if validate != None:
            count +=1
            display_msg("Offset value is greater than 60 secs")
        else:
            display_msg("Offset value is lesser than 60 secs")
        print("*****TOTAL COUNT****",count)
        
        if count == 5:
            assert True
            display_msg("PASS:Log validation is successful")
        else:
            display_msg("FAIL:Log validation is failed")
            assert False

        display_msg("Validate NTP Keys and Server on member is completed")
        display_msg("TestCase 014 executed successfully")



    @pytest.mark.run(order=15)
    def test_015_Validate_ntp_conf(self):
	display_msg("Validate NTP conf on member")

	count = 0


	logging.info("Validate NTP server is added in ntp.conf")
	ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member1_vip
)+' " cat /tmpfs/ntp.conf | grep burst"'
	ntp_conf_cmd = commands.getoutput(ntp_conf)
	print("Command output",ntp_conf_cmd)

	if re.search(r'.*server '+config.grid3_master_vip+'.*burst.*',ntp_conf_cmd):
	    count +=1
	    display_msg("Server details are present in ntp conf")
	else:
	    display_msg("Server details not present in ntp conf")

        ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member1_vip
)+' " cat /tmpfs/ntp.conf | grep trustedkey"'
        ntp_conf_cmd1 = commands.getoutput(ntp_conf)
        print("Command output",ntp_conf_cmd1)

	if re.search(r'.*trustedkey.*'+server2_key0+'.*',ntp_conf_cmd1):
	    count +=1
	    display_msg("Key detail is present in ntp conf")
	else:
	    display_msg("Key detail is not present in ntp conf")

	if count == 2:
	    assert True
	    display_msg("PASS:All details are present in ntp config file")
	else:
	    display_msg("FAIL:Not all details are present in ntp config file")
	    assert False

	display_msg("Testcase 015 execution completed successfully")


    @pytest.mark.run(order=16)
    def test_016_Validate_ntp_key(self):
        display_msg("Validate NTP key in NTP client on member")
	
        logging.info("Validate NTP server is added in ntp.conf")
        ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_1member1_vip
)+' " cat /etc/ntp.keys"'
        ntp_conf_cmd = commands.getoutput(ntp_conf)
        print("Command output",ntp_conf_cmd)
	a = ntp_conf_cmd.split()
	print("$$$$$$$$$$$$$$$$$$",a)
	
	print("KEY STRING",a[-1])
	print("KEY TYPE",a[-2])
	print("KEY NUMBER",a[-3])
	
	if a[-1] == server2_key2 and a[-2] == server1_key1 and a[-3] == server2_key0:
	    assert True
	    display_msg("PASS:Key is added")
	else:
	    display_msg("FAIL:Key is not added")
	    assert False

	sleep(100)
	
	display_msg("Testcase 016 execution completed successfully")


    @pytest.mark.run(order=17)
    def test_017_validate_ntpq_command(self):
	display_msg("Validate NTPQ -P command status on member")
	

	try:
           child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_member1_vip)
	   child.logfile=sys.stdout
    	   child.expect('#')
    	   child.sendline('ntpq -p > note.txt')
           child.expect('#')

    	   child.sendline('grep -e "*"  note.txt')
    	   child.expect('#')
    	   data = child.before
 	   child.close()

    	   print("Before data",data)
    	   n = data.split()
    	   print("########",n)
	
	   count = 0

    	   print("SERVER-IP",n[-21])
    	   a = n[-21]
	   c = a[1:]
	   print("^^^^^^^^^SERVER-IP^^^^^^^^",c)
	   print("////////////////////////",config.grid3_master_vip)
	
       	   if c == config.grid3_master_vip:
	   	count +=1
	    	display_msg("Server IP is reachable")
	   else:
	    	display_msg("Server IP isn't available")

	   print("@@@@@@@@",n[-20])
	   b = n[-20]
    	   if re.search(r'LOCAL.*',b):
	    	count +=1
	    	display_msg("Server reachable, pass")
	   else:
	   	display_msg("Server not reachable, debug")

	   if count == 2:
	    	assert True
	    	display_msg("PASS:NTP server is in Sync")
	   else:
		display_msg("FAIL:NTP server is not in Sync")
	    	assert False

    	   print("Validate ntpq conf is completed")

	except Exception as e:
           child.close()
           print("Failure:")
           print (e)
           assert False

    	display_msg("TestCase 017 executed successfully")

    @pytest.mark.run(order=18)
    def test_018_Validate_ntp_conf_ps_ax(self):
        display_msg("Validate NTP conf ps ax")

        count = 0

        logging.info("Validate /tmpfs/ntp.conf in ntp.conf ps ax")
        ntp_conf_ps_ax = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member1_vip
)+' "  ps ax | grep ntp"'
        ntp_conf_ps_ax_cmd = commands.getoutput(ntp_conf_ps_ax)
        print("Command output",ntp_conf_ps_ax_cmd)
	
	if re.search(r'.*/usr/bin/ntpd -x -a -c /tmpfs/ntp.conf -f /storage/etc/ntp.drift.*',ntp_conf_ps_ax_cmd):
            count +=1
	    assert True
            display_msg("PASS: /tmpfs/ntp.conf are present in ntp conf ps ax")
        else:
	    display_msg("FAIL: /tmpfs/ntp.conf not present in ntp conf ps ax")
	    assert False
           
	
	display_msg("TestCase 018 executed successfully")

    @pytest.mark.run(order=19)
    def test_019_Validate_string_field_length_for_SHA1_algorithm(self):
	
	display_msg("Validate string field length for SHA1 algorithm")
	key = server2_key2
        print("key string",key)

	length = len(key)
	print("string length is",length)
 	
	if length == 40:
		display_msg("PASS : Key field length for SHA-1 algorithm is 40 digits long")
		assert True
	else :
		display_msg("FAIL : Key field length for SHA-1 algorithm is not 40 digits long")
		assert False
	
	display_msg("Validate string field length for SHA-1 algorithm is completed")
	display_msg("TestCase 019 executed successfully")


    @pytest.mark.run(order=20)
    def test_020_Validate_the_key_value_is_between_1_to_65534(self):

	display_msg("Validate the key value is between 1-65534")
	
	key = int(server2_key0)
	
	print("Key value is",key)



	if  1 <= key <= 65534 :
		assert True
		display_msg("PASS : Key value is between 1-65534")
	else :
		display_msg("FAIL : Key value is not in between 1-65534")
		assert False

	display_msg("Validate the key value is between 1-65534 is completed")
	display_msg("TestCase 020 executed successfully")

    

#Exclude the grid master as an NTP server      

    @pytest.mark.run(order=21)
    def test_021_Validate_Exclude_the_Grid_Master_should_not_sync_with_grid_master(self):

        display_msg("Validate Exclude the Grid Master should not sync with grid master")

        try:
	    cmd = "reboot_system -H "+config.vmid+" -a poweroff"
            print("command is ",cmd)
            result = os.system(cmd)
            assert True
        except:
            assert False
        finally:
            sleep(180)


	display_msg("TestCase 021 executed successfully")
    

    pytest.mark.run(order=22)
    def test_022_ntp_service_on_memebrs(self):
        display_msg("Adding NTP Keys and Server")

        display_msg("Starting log capture")
        log("start","/var/log/messages",config.grid1_member2_vip)
        log("start","/infoblox/var/infoblox.log",config.grid1_member2_vip)

        key0 = server2_key0
        print("###########KEY-NUMBER#######",key0)
        key1 = server2_key2
        print("###########KEY-STRING#######",key1)

        request = ib_NIOS.wapi_request('GET' , object_type='member',grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)
        res_ref = request[2]['_ref']
        print("Grid reference",res_ref)

        data = {"ntp_setting":{"enable_ntp": False ,"enable_external_ntp_servers": True,"exclude_grid_master_ntp_server": True,"ntp_servers": [{"address": config.grid3_master_vip, "burst": True, "enable_authentication": True,"iburst": True, "ntp_key_number": int(key0), "preferred": False}],"ntp_keys": [{"number":int(key0),"type":"SHA1_ASCII","string":str(key1)}],"use_default_stratum": True }}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        print("%%%%%%%%%%%%%%%%%%%%",request1)

        if type(request1) == tuple:
                display_msg(json.loads(request1[1])['text'])
                display_msg("FAIL: Failed to add  NTP keys and Servers, Debug")
                assert False
        
	else:
                display_msg(request1)
                display_msg("PASS: Successfully added NTP Keys and Servers")

        display_msg("Validate added NTP server and key")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ntp_setting')
        display_msg(get_ref1)
        result = config.grid3_master_vip
        if result in get_ref1:
            display_msg("PASS: Successfully validated NTP server.")
        else:
            display_msg("FAIL: NTP server not found.")
            assert False

        result1 = key0
        if result1 in get_ref1:
            display_msg("PASS: Successfully validated NTP key.")
        else:
            display_msg("FAIL: NTP key not found.")
            assert False


        display_msg("Added NTP keys and Server")
	display_msg("Giving sleep time to apply the changes")
        sleep(60)

        display_msg("Ping the Grid ip and check if it is reachable")


        for i in range(10):
                ping = os.popen("ping -c 5 " + config.grid1_member2_vip).read()
                display_msg(ping)
                if "0 received" not in ping:
                        display_msg(config.grid1_member2_vip+" is pinging ")
                        display_msg("Member restart is successfull")
                        assert True
			break

                else :
                        print(config.grid1_member2_vip+" is not pinging, Going to sleep for 60 seconds ")
                        sleep(60)
                        if i == 9:
                        	assert False



        display_msg("Adding NTP Keys and Server has been completed")
     
	display_msg("TestCase 022 executed successfully")

    @pytest.mark.run(order=23)
    def test_023_validate_log_keys_server_on_member(self):
        display_msg("Validate log NTP Keys and Server on member")

        display_msg("Stopping log capture")
        log("stop","/var/log/messages",config.grid1_member2_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid1_member2_vip)



        count = 0

        display_msg("Validate NTP keys added")
        #validate = logv(".*check_ntp_conf.*"+trustedkey  "+server2_key0+".*","/infoblox/var/infoblox.log",config.grid1_member2_vip)
        validate = logv(".*check_ntp_conf.*trustedkey  "+server2_key0+".*","/infoblox/var/infoblox.log",config.grid1_member2_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("NTP key is added")
        else:
            display_msg("NTP is not added, debug failures")

        display_msg("Validate NTP server added")
        #validate = logv(".*check_ntp_conf.*+server "+server2_key2+" key "+server2_key0+".*","/infoblox/var/infoblox.log",config.grid1_member2_vip)
        validate = logv(".*check_ntp_conf.*server "+config.grid3_master_vip+".*key.*"+server2_key0+".*","/infoblox/var/infoblox.log",config.grid1_member2_vip)
	  
	print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("NTP server is added")
        else:
            display_msg("NTP server is not added, debug failures")

        display_msg("Validate syslog for NTP server added")
        validate = logv(".*notice ntpdate 4.2.8p15@1.3728-o.*","/var/log/messages",config.grid1_member2_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("Syslog validation successful")
        else:
            display_msg("Syslog validation failed")

        display_msg("Validate NTP server reachable in the logs")
        validate = logv(".*Offset between ntp server.*"+config.grid3_master_vip+".*","/infoblox/var/infoblox.log",config.grid1_member2_vip)
        print("VALIDATE",validate)

        if validate != None:
            count +=1
            display_msg("NTP Server is reachable")
        else:
            display_msg("NTP server is not reachable")
        print("*****TOTAL COUNT****",count)
        
        if count == 4:
            assert True
            display_msg("PASS:Log validation is successful")
        else:
            display_msg("FAIL:Log validation is failed")
            assert False

        display_msg("Validate NTP Keys and Server on member is completed")
        display_msg("TestCase 023 executed successfully")


    @pytest.mark.run(order=24)
    def test_024_validate_ntpq_command(self):
	display_msg("Validate NTPQ -P command status on member")
	

	try:
           child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_member2_vip)
	   child.logfile=sys.stdout
    	   child.expect('#')
    	   child.sendline('ntpq -p > note.txt')
           child.expect('#')

    	   child.sendline('grep -e ".INIT."  note.txt')
    	   child.expect('#')
    	   data = child.before
 	   child.close()

    	   print("Before data",data)
    	   n = data.split()
    	   print("########",n)
	
	   count = 0

    	   print("SERVER-IP",n[-11])
    	   a = n[-11]
	   c = a[0:]
	   print("^^^^^^^^^SERVER-IP^^^^^^^^",c)
	   print("////////////////////////",config.grid3_master_vip)

	
       	   if c == config.grid3_master_vip:
	   	count +=1
	    	display_msg("Server IP is reachable")
	   else:
	    	display_msg("Server IP isn't available")

	   print("@@@@@@@@",n[-10])
	   b = n[-10]
    	   if re.search(r'.INIT.',b):
	    	count +=1
	    	display_msg("Server not reachable, pass")
	   else:
	   	display_msg("Server reachable, debug")

	   if count == 2:
	    	assert True
	    	display_msg("PASS:NTP server is not in Sync")
	   else:
		display_msg("FAIL:NTP server is in Sync")
	    	assert False

    	   print("Validate ntpq conf is completed")

	except Exception as e:
           child.close()
           print("Failure:")
           print (e)
           assert False

    	display_msg("TestCase 024 executed successfully")


    @pytest.mark.run(order=25)
    def test_025_Validate_Exclude_the_Grid_Master_should_not_sync_with_grid_master(self):

        display_msg("Validate Exclude the Grid Master should not sync with grid master")

        try:
            cmd = "reboot_system -H "+config.vmid+" -a poweron"
            print("command is ",cmd)
            result = os.system(cmd)
            assert True
        except:
            assert False
        finally:
            sleep(300)


        display_msg("TestCase 025 executed successfully")


   

    @pytest.mark.run(order=26)
    def test_026_Validate_ntp_conf(self):
	display_msg("Validate NTP conf on member")

	count = 0

	logging.info("Validate NTP server is added in ntp.conf")
	ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member2_vip
)+' " cat /tmpfs/ntp.conf | grep burst"'
	ntp_conf_cmd = commands.getoutput(ntp_conf)
	print("Command output",ntp_conf_cmd)

	if re.search(r'.*server '+config.grid3_master_vip+'.*burst.*',ntp_conf_cmd):
	    count +=1
	    display_msg("Server details are present in ntp conf")
	else:
	    display_msg("Server details not present in ntp conf")

        ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member2_vip
)+' " cat /tmpfs/ntp.conf | grep trustedkey"'
        ntp_conf_cmd1 = commands.getoutput(ntp_conf)
        print("Command output",ntp_conf_cmd1)

	if re.search(r'.*trustedkey.*'+server2_key0+'.*',ntp_conf_cmd1):
	    count +=1
	    display_msg("Key detail is present in ntp conf")
	else:
	    display_msg("Key detail is not present in ntp conf")

	if count == 2:
	    assert True
	    display_msg("PASS:All details are present in ntp config file")
	else:
	    display_msg("FAIL:Not all details are present in ntp config file")
	    assert False

	display_msg("Testcase 026 execution completed successfully")

    @pytest.mark.run(order=27)
    def test_027_Validate_ntp_key(self):
        display_msg("Validate NTP key in NTP client on member")
	
        logging.info("Validate NTP server is added in ntp.conf")
        ntp_conf = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member2_vip
)+' " cat /etc/ntp.keys"'
        ntp_conf_cmd = commands.getoutput(ntp_conf)
        print("Command output",ntp_conf_cmd)
	a = ntp_conf_cmd.split()
	print("$$$$$$$$$$$$$$$$$$",a)
	
	print("KEY STRING",a[-1])
	print("KEY TYPE",a[-2])
	print("KEY NUMBER",a[-3])
	
	if a[-1] == server2_key2 and a[-2] == server1_key1 and a[-3] == server2_key0:
	    assert True
	    display_msg("PASS:Key is added")
	else:
	    display_msg("FAIL:Key is not added")
	    assert False

	sleep(100)
	
	display_msg("Testcase 027 execution completed successfully")


    @pytest.mark.run(order=28)
    def test_028_validate_ntpq_command(self):
	display_msg("Validate NTPQ -P command status on member")
	

	try:
           child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_member2_vip)
	   child.logfile=sys.stdout
    	   child.expect('#')
    	   child.sendline('ntpq -p > note.txt')
           child.expect('#')

    	   child.sendline('grep -e "*"  note.txt')
    	   child.expect('#')
    	   data = child.before
 	   child.close()

    	   print("Before data",data)
    	   n = data.split()
    	   print("########",n)
	
	   count = 0

    	   print("SERVER-IP",n[-11])
    	   a = n[-11]
	   c = a[1:]
	   print("^^^^^^^^^SERVER-IP^^^^^^^^",c)
	   print("////////////////////////",config.grid3_master_vip)
	
       	   if c == config.grid3_master_vip:
	   	count +=1
	    	display_msg("Server IP is reachable")
	   else:
	    	display_msg("Server IP isn't available")

	   print("@@@@@@@@",n[-10])
	   b = n[-10]
    	   if re.search(r'LOCAL.*',b):
	    	count +=1
	    	display_msg("Server reachable, pass")
	   else:
	   	display_msg("Server not reachable, debug")

	   if count == 2:
	    	assert True
	    	display_msg("PASS:NTP server is in Sync")
	   else:
		display_msg("FAIL:NTP server is not in Sync")
	    	assert False

    	   print("Validate ntpq conf is completed")

	except Exception as e:
           child.close()
           print("Failure:")
           print (e)
           assert False

    	display_msg("TestCase 028 executed successfully")

    @pytest.mark.run(order=29)
    def test_029_Validate_ntp_conf_ps_ax(self):
        display_msg("Validate NTP conf ps ax")

        count = 0

        logging.info("Validate /tmpfs/ntp.conf in ntp.conf ps ax")
        ntp_conf_ps_ax = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid1_member2_vip
)+' "  ps ax | grep ntp"'
        ntp_conf_ps_ax_cmd = commands.getoutput(ntp_conf_ps_ax)
        print("Command output",ntp_conf_ps_ax_cmd)
	
	if re.search(r'.*/usr/bin/ntpd -x -a -c /tmpfs/ntp.conf -f /storage/etc/ntp.drift.*',ntp_conf_ps_ax_cmd):
            count +=1
	    assert True
            display_msg("PASS: /tmpfs/ntp.conf are present in ntp conf ps ax")
        else:
	    display_msg("FAIL: /tmpfs/ntp.conf not present in ntp conf ps ax")
	    assert False
           
	
	display_msg("TestCase 029 executed successfully")

   


    @pytest.mark.run(order=30)
    def test_030_Validate_string_field_length_for_SHA1_algorithm(self):
	
	display_msg("Validate string field length for SHA1 algorithm")
	key = server2_key2
        print("key string",key)

	length = len(key)
	print("string length is",length)
 	
	if length == 40:
		display_msg("PASS : Key field length for SHA-1 algorithm is 40 digits long")
		assert True
	else :
		display_msg("FAIL : Key field length for SHA-1 algorithm is not 40 digits long")
		assert False
	
	display_msg("Validate string field length for SHA-1 algorithm is completed")
	display_msg("TestCase 030 executed successfully")


    @pytest.mark.run(order=31)
    def test_031_Validate_the_key_value_is_between_1_to_65534(self):

	display_msg("Validate the key value is between 1-65534")
	
	key = int(server2_key0)
	
	print("Key value is",key)



	if  1 <= key <= 65534 :
		assert True
		display_msg("PASS : Key value is between 1-65534")
	else :
		display_msg("FAIL : Key value is not in between 1-65534")
		assert False

	display_msg("Validate the key value is between 1-65534 is completed")
	display_msg("TestCase 031 executed successfully")

    
    
    @pytest.mark.run(order=32)
    def test_032_starting_log_capture(self):
	display_msg("Starting log capture")
	log("start","/var/log/messages",config.grid1_master_vip)
        log("start","/infoblox/var/infoblox.log",config.grid1_master_vip)
	display_msg("TestCase 032 executed successfully")

    @pytest.mark.run(order=33)
    def test_033_Taking_Grid_Backup_File(self):
        display_msg("Taking Grid Backup file")
        data = {"type": "BACKUP"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata",grid_vip=config.grid_vip)
        response = json.loads(response)
        print(response)
        token_of_GM = response['token']
        token_of_URL = response['url']
        curl_download='curl -k -u admin:infoblox -H  "content-type: application/force-download" '+token_of_URL+' -o "database.bak"'
        os.system(curl_download)
        print(token_of_GM)
        print(token_of_URL)
        display_msg("TestCase 033 executed successfully")

    @pytest.mark.run(order=34)
    def test_034_Validate_Grid_Backup_File(self):
	display_msg("Validate Grid Backup file")
	
	
        display_msg("Stopping log capture")
        log("stop","/var/log/messages",config.grid1_master_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid1_master_vip)
        
	count = 0

        display_msg("Validate db dump start")
        validate = logv(".*db_dump - start.*","/infoblox/var/infoblox.log",config.grid1_master_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("db dump start")
        else:
            display_msg("db dump not started, debug failures")
       
	display_msg("Validate db dumb done")
        validate = logv(".*db_dump - done.*","/infoblox/var/infoblox.log",config.grid1_master_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("db dump done")
        else:
            display_msg("db dump not done, debug failures")

	display_msg("Validate completed backup")
        validate = logv(".*Completed backup node by user admin at local.*","/infoblox/var/infoblox.log",config.grid1_master_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("Completed Grid Backup")
        else:
            display_msg("Backup failed, debug failures")

	if count == 3:
            assert True
            display_msg("PASS:Log validation is successful")
        else:
            display_msg("FAIL:Log validation is failed")
            assert False

        display_msg("Validate Grid Backup file is completed")
        display_msg("TestCase 034 executed successfully")

	

    @pytest.mark.run(order=35)
    def test_035_cleanup_data(self):
	
	display_msg("Clean all the objects")
        request = ib_NIOS.wapi_request('GET' , object_type='grid',grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)
        res_ref = request[0]['_ref']
        print("Grid reference",res_ref)
	
	data = {"ntp_setting": {"enable_ntp": False, "ntp_servers": [], "ntp_keys": []}}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        display_msg(request1)

	
	if type(request1) == tuple:
        	display_msg(json.loads(request1[1])['text'])
        	display_msg("FAIL: Failed to clean all the objects on grid, Debug")
        	assert False
    	else:
        	display_msg(request1)
        	display_msg("PASS: Successfully cleaned all the objects on grid")	

	display_msg("Validate cleaned objects on grid")
	res = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting')
	display_msg(res)

	string = {"ntp_setting":{"enable_ntp": False,"ntp_keys": [],"ntp_servers": [] }}

	if res == string:
		assert True
		display_msg("Validate : Cleaned all the objects")

        
        request2 = ib_NIOS.wapi_request('GET' , object_type='member')
        request2 = json.loads(request2)
        print(request2)
        res_ref1 = request2[1]['_ref']
        print("Grid reference",res_ref1)
	
	data1 = {"ntp_setting": {"enable_ntp": False,"enable_external_ntp_servers": False, "ntp_servers": [], "ntp_keys": []}}
        request3 = ib_NIOS.wapi_request('PUT', object_type=res_ref1, fields=json.dumps(data1))
        display_msg(request3)

	
	if type(request3) == tuple:
        	display_msg(json.loads(request3[1])['text'])
        	display_msg("FAIL: Failed to clean all the objects on member1, Debug")
        	assert False
    	else:
        	display_msg(request3)
        	display_msg("PASS: Successfully cleaned all the objects on member1")	

	display_msg("Validate cleaned objects on member1")
	res1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ntp_setting')
	display_msg(res1)

	string1 = {"ntp_setting":{"enable_ntp": False,"enable_external_ntp_servers": False,"ntp_keys": [],"ntp_servers": [] }}

	if res1 == string1:
		assert True
		display_msg("Validate : Cleaned all the objects on member1")


        request4 = ib_NIOS.wapi_request('GET' , object_type='member')
        request4 = json.loads(request4)
        print(request4)
        res_ref2 = request4[2]['_ref']
        print("Grid reference",res_ref2)
	
	data2 = {"ntp_setting": {"enable_ntp": False, "enable_external_ntp_servers": False,"exclude_grid_master_ntp_server": False,"ntp_servers": [], "ntp_keys": []}}
        request5 = ib_NIOS.wapi_request('PUT', object_type=res_ref2, fields=json.dumps(data2))
        display_msg(request5)

	
	if type(request5) == tuple:
        	display_msg(json.loads(request5[1])['text'])
        	display_msg("FAIL: Failed to clean all the objects on member2, Debug")
        	assert False
    	else:
        	display_msg(request5)
        	display_msg("PASS: Successfully cleaned all the objects on member2")	

	display_msg("Validate cleaned objects om member2")
	res2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ntp_setting')
	display_msg(res2)

	string2 = {"ntp_setting":{"enable_ntp": False,"enable_external_ntp_servers": False,"exclude_grid_master_ntp_server": False,"ntp_keys": [],"ntp_servers": [] }}

	if res2 == string2:
		assert True
		display_msg("Validate : Cleaned all the objects on member1")
        


	display_msg("Cleanup data is completed")
	display_msg("TestCase 035 executed successfully")


    @pytest.mark.run(order=36)
    def test_036_starting_log_capture(self):
	display_msg("Starting log capture")
        log("start","/var/log/messages",config.grid1_master_vip)
        log("start","/infoblox/var/infoblox.log",config.grid1_master_vip)
        display_msg("TestCase 036 executed successfully")


    @pytest.mark.run(order=37)
    def test_037_Restore_Grid_Backup_File(self):
        display_msg("Restore_Grid_Backup_File")
        log("start","/infoblox/var/infoblox.log", config.grid_vip)
        response = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit",grid_vip=config.grid_vip)
        response = json.loads(response)
        print(response)
        token_of_GM = response['token']
        token_of_URL = response['url']
        curl_upload='curl -k -u admin:infoblox -H "content-typemultipart-formdata" '+token_of_URL+' -F file=@database.bak'
        os.system(curl_upload)
        print(curl_upload)
        data = {"mode": "FORCED", "token": token_of_GM}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredatabase",grid_vip=config.grid_vip)
        sleep(60)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        check_master=commands.getoutput(" grep -cw \".*restore_node complete.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
        if (int(check_master)!=0):
                assert True
        else:
                assert False
        sleep(60)
        display_msg("TestCase 037 executed successfully")

    @pytest.mark.run(order=38)
    def test_038_Validate_Restore_Grid_Backup_File(self):
        display_msg("Validate Restore Grid Backup File")


        display_msg("Stopping log capture")
        log("stop","/var/log/messages",config.grid1_master_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid1_master_vip)

        count = 0

        display_msg("Validate Grid Restore started")
        validate = logv(".*Grid Restore started.*","/infoblox/var/infoblox.log",config.grid1_master_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("Grid Restore started")
        else:
            display_msg("Grid Restore is not started, debug failures")

	display_msg("Validate db import complete")
        validate = logv(".*db_import complete.*","/infoblox/var/infoblox.log",config.grid1_master_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("db import completed")
        else:
            display_msg("db import is not completed, debug failures")

	
	display_msg("Validate Restore complete")
        validate = logv(".*restore_node complete.*","/infoblox/var/infoblox.log",config.grid1_master_vip)
        print("VALIDATE",validate)
        if validate != None:
            count +=1
            display_msg("Grid Restore complete")
        else:
            display_msg("Grid Restore is not completed, debug failures")


	if count == 3:
            assert True
            display_msg("PASS:Log validation is successful")
        else:
            display_msg("FAIL:Log validation is failed")
            assert False

        display_msg("Validate Restore Grid Backup File is Completed")
        display_msg("TestCase 038 executed successfully")


    @pytest.mark.run(order=39)
    def test_039_Add_IPv4_Network_ACL_with_Alow_Permission_in_Named_ACLs(self):
                
	display_msg("Adding IPv4 Named ACL with Allow Permission")
                
        data = {"name": "test","access_list": [{"_struct": "addressac","address": config.network_address,"permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type="namedacl",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20) #wait for 20 secs for the member to get started
        display_msg("TestCase 039 executed successfully")

    @pytest.mark.run(order=40)
    def test_040_Validate_Created_IPv4_Address_Named_ACL(self):
                
        display_msg("Validating added ipv4 named acl ")
                
        data = ('"name": "test"','"_struct": "addressac"','"address": "'+config.network_address+'"','"permission": "ALLOW"')
        response = ib_NIOS.wapi_request('GET', "namedacl?name=test&_return_fields=access_list,name&_return_as_object=1",grid_vip=config.grid_vip)
        print(response)
        for i in data:
            if i in response:
                assert True
            else:
            	assert False
        print(data)
        display_msg("TestCase 040 executed successfully")

    @pytest.mark.run(order=41)
    def test_041_Validate_NTP_SHA_1_authentication_works_with_Access_Control(self):
        display_msg("Validate NTP SHA-1 authentication works fine with Access Control enabled")
        try:
           child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_member1_vip)
           child.logfile=sys.stdout
           child.expect('#')
           #child.sendline('ntpdate -d -a 12 -k /etc/ntp.keys config.grid3_master_vip > note.txt')
           child.sendline("ntpdate -d -a "+server2_key0+" -k /etc/ntp.keys "+config.grid3_master_vip+"  > note.txt")
           child.expect('#')
           child.sendline('grep -e "authentication passed"  note.txt')
           child.expect('#')
           data = child.before
           child.close()
           print("Before data",data)
           if re.search(r'receive: authentication passed.*',data):
                assert True
                display_msg("PASS : Authentication passed")
           else:
                display_msg("FAIL : Authentication failed , debug")
                assert False

	except Exception as e:
           child.close()
           print("Failure:")
           print (e)
           assert False


	display_msg("TestCase 041 executed successfully")

    ''' 
    @pytest.mark.run(order=42)
    def test_042_convert_member_to_Master_candidate(self):
        print("Make the member as Master candidate")
        #get_ref = ib_NIOS.wapi_request('GET', object_type='member?host_name='+config.grid_vip)
        request = ib_NIOS.wapi_request('GET' , object_type='member',grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)
        get_ref = request[1]['_ref']
        print("Grid reference",get_ref)
	#get_ref = json.loads(get_ref)[0]['_ref']
        data = {"master_candidate":True}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        print(response)
        if response[0] == 400 or response[0] == 401:
            print("Failure: Make the member as Master candidate")
            assert False
        else:
            print("Success: Make the member as Master candidate")
            assert True
        sleep(120)
	display_msg("Test case 042 execution completed")

    @pytest.mark.run(order=43)
    def test_043_Promote_GMC(self):
        display_msg("Promoting Grid Master Candidate...")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("set promote_master")
            child.expect("Do you want a delay between notification to grid members*")
            child.sendline("n")
            child.expect(":")
            child.sendline("c")
            child.expect("Are you sure you want to do this*")
            child.sendline("n")
            print("Grid Master Candidate NOT promoted!")
            assert True
        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...")
            assert False
        finally:
            child.close()

	display_msg("TestCase 043 executed successfully")



    @pytest.mark.run(order=44)
    def test_44_Promote_GMC(self):
        display_msg("Promoting Grid Master Candidate...")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("set promote_master")
            child.expect("Do you want a delay between notification to grid members*")
            child.sendline("n")
            # prom = child.expect("Infoblox > ")
            # val = child.before
            # print(val)
            child.expect(":")
            child.sendline("2")
            child.expect("Are you sure you want to do this*")
            child.sendline("y")
            child.expect("Are you really sure you want to do this*")
            child.sendline("y")
            print("System restart...")
            sleep(300)
            print("Grid Master Candidate promoted!")
            assert True
        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...")
            assert False
        finally:
            child.close()

	display_msg("TestCase 044 executed successfully")

 

    @pytest.mark.run(order=45)
    def test_045_after_GMC_promotion_grid_is_alive(self): 
	
	display_msg("After GMC promotion check grid is alive")
	
	display_msg("Ping the Grid ip and check if it is reachable")
	
	
	for i in range(10):
                ping = os.popen("ping -c 5 " + config.grid1_member1_vip).read()
                display_msg(ping)
                if "0 received" not in ping:
                        display_msg(config.grid1_member1_vip+" is pinging ")
                        display_msg("Member restart is successfull")
                        assert True
                        break

                else :
                        print(config.grid1_member1_vip+" is not pinging, Going to sleep for 60 seconds ")
                        sleep(60)
                        if i == 9:
                                display_msg("Grid is not pinging")
                                assert False


	display_msg("TestCase 045 executed successfully")

    @pytest.mark.run(order=46)
    def test_046_validate_ntpq_command(self):
	display_msg("After GMC promotion Validate NTPQ -P command status on member")
	

	try:
           child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
	   child.logfile=sys.stdout
    	   child.expect('#')
    	   child.sendline('ntpq -p > note.txt')
           child.expect('#')

    	   child.sendline('grep -e "*"  note.txt')
    	   child.expect('#')
    	   data = child.before
 	   #child.close()

    	   print("Before data",data)
    	   n = data.split()
    	   print("########",n)
	
	   count = 0

    	   print("SERVER-IP",n[-10])
    	   a = n[-10]
	   c = a[0:]
	   print("^^^^^^^^^SERVER-IP^^^^^^^^",c)
	   print("////////////////////////",config.grid1_member2_vip)
	
       	   if c == config.grid1_member2_vip:
	   	count +=1
	    	display_msg("Server IP is reachable")
	   else:
	    	display_msg("Server IP isn't available")

           child.sendline('ntpq -p > note1.txt')
           child.expect('#')

           child.sendline('grep -e "LOCAL(1)"  note1.txt')
           child.expect('#')
           data = child.before
           child.close()

           print("Before data",data)
           p = data.split()
           print("########",p)

	   print("@@@@@@@@",p[-11])
	   p = p[-11]
	   

    	   if re.search(r'LOCAL.*',p):
	    	count +=1
	    	display_msg("Server reachable, pass")
	   else:
	   	display_msg("Server not reachable, debug")

	   if count == 2:
	    	assert True
	    	display_msg("PASS:NTP server is in Sync")
	   else:
		display_msg("FAIL:NTP server is not in Sync")
	    	assert False

    	   print("Validate ntpq conf is completed")

	except Exception as e:
           child.close()
           print("Failure:")
           print (e)
           assert False

    	display_msg("TestCase 046 executed successfully")

    '''

