#!/usr/bin/python

import subprocess
import os
import time
import keystoneclient.v2_0.client as k_client
from credentials import get_nova_credentials_v2
from credentials import *
from novaclient.client import Client
import ceilometerclient.client

cpuHigh = 70  # Cpu upper bond for sprout nodes
cpuLow = 20   # Cpu lower bond for sprout nodes
ploicyTime =  60 # Plocy time for auto-scaling in seconds.
ceilometerDuration = 30 # Ceilometer polling time duration
waitForScale = 60  # How many seconds to wait for scale process
maxSprout = 2 # Maxiuam deployment for sprout
minSprout = 1 # Minimum deployment for sprout
allSproutId = []
activeSproutId = []
shutOffSproutId = []

keystone = k_client.Client(auth_url=OS_AUTH_URL, username=OS_USERNAME, password=OS_PASSWORD, tenant_name=OS_TENANT_NAME)
#cclient = ceilometerclient.client.get_client(2, os_username=OS_USERNAME, os_password=OS_PASSWORD, os_tenant_name=OS_PROJECT_NAME, os_auth_url=OS_AUTH_URL)

credentials = get_nova_credentials_v2()
nova_client = Client(**credentials)

def getAllInstances():
        return nova_client.servers.list()

def getAllSprout():
        tempList = getAllInstances()
        allSproutList = [elem for elem in tempList if "sprout" in elem.name ]
        return allSproutList

def getAllActiveInstances():
        return nova_client.servers.list(search_opts={'status': 'ACTIVE'})

def getAllSuspendedInstances():
	return nova_client.servers.list(search_opts={'status': 'SUSPENDED'})

def getAllActiveSproutInstance():
	tempList = getAllActiveInstances()
	allActiveSproutList = [elem for elem in tempList if "sprout" in elem.name ]
	return allActiveSproutList

def getAllSuspendedSproutInstance():
	tempList = getAllSuspendedInstances()
	allSuspendedSproutList = [elem for elem in tempList if "sprout" in elem.name ]
	return allSuspendedSproutList

def getActiveSprout():
        tempList = getAllActiveInstances()
        activeSprout = [elem for elem in tempList if "sprout" in elem.name ]
        return activeSprout

def getAllSproutId():
	allSprout = getAllSprout()
	tempList=[]
	for each in allSprout:
		tempList.append(each.id)
	return tempList

def getAllActiveSproutId():
	allActiveSprout = getActiveSprout()
	tempList=[]
	for each in allActiveSprout:
		tempList.append(each.id)
	return tempList

print("----All instances----")
print getAllInstances()
#print(nova_client.servers.list())
#for each in nova_client.servers.list():
#	print each
print("---------------------\n")

print("----All active instances----")
print getAllActiveInstances()
#for each in nova_client.servers.list(search_opts={'status': 'ACTIVE'}):
#	print each
print("----------------------------\n")

print "----All suspended instances------"
print getAllSuspendedInstances()
print "----------------------------------"


print("----Sprout List----")
print getAllSprout()
#tempServerList=nova_client.servers.list()
#SproutList=[elem for elem in tempServerList if "sprout" in elem.name ]
#print(SproutList)
#for each in SproutList:
#	print each
print("--------------------\n")


print("----All Sprout Id List----")
print getAllSproutId()
#for sp in SproutList:
#	print sp.id
#	allSproutId.append(sp.id)
print("----------------------\n")

print("----All Active Sprout Id List----")
print getAllActiveSproutId()
print("---------------------------------")

print "---All Active Sprout List----"
print getAllActiveSproutInstance()
print "-----------------------------\n"


#print("\n----Sprout Cpu Usage----")
#for each in SproutIdList:
#	query = [dict(field='resource_id', op='eq', value=each), dict(field='meter',op='eq',value='cpu_util')]
#	print cclient.new_samples.list(q=query, limit=1)
#print("----Sprout Cpu Usage----\n")

#for spid in SproutIdList:
#	print spid
#	os.system("ceilometer sample-list -m cpu_util "+"-q resource_id="+spid+" -l 1")

#print SproutList

import ceilometerclient.v2 as c_client
auth_token = keystone.auth_token 
ceilometer = c_client.Client(endpoint=CEILOMETER_ENDPOINT, token= lambda : auth_token )

#for each in getAllSproutId():
#	query = [dict(field='resource_id', op='eq', value=each)]
#	cpu_util_sample = ceilometer.samples.list('cpu_util',q=query,limit=1)
#	for each in cpu_util_sample:
#		print each.resource_id, each.counter_volume 
		
def getAllActiveSproutCpu():
	totalCpuUtil = 0;
	for each in getAllActiveSproutId():
		query = [dict(field='resource_id', op='eq', value=each)]
		cpu_util_sample = ceilometer.samples.list('cpu_util',q=query,limit=1)
		for each in cpu_util_sample:
			totalCpuUtil = totalCpuUtil + each.counter_volume
	return totalCpuUtil

def scaleUp(suspendedInstances):
	tempServer = suspendedInstances.pop()
	tempServer.resume()
	print "Wait for scale up complete"
	while True:
		if tempServer in getAllActiveSproutInstance():
			break
		#print tempServer.status

def scaleDown(activeInstances):
	tempServer = activeInstances.pop()
	tempServer.suspend()
	print "Wait for scale down complete"
	while True:
		if tempServer in getAllSuspendedSproutInstance():
			break
		#print tempServer.status

print "Total Active Sprout Number: ", len(getActiveSprout())
print "Total Active Sprout Cpu Usage: ", getAllActiveSproutCpu(), "for ",len(getActiveSprout()), " sprouts"

def autoScaling():
#main auto Scaling function
	print "Start Main Scaling function"
	print "Ctrl + C to close this program"
	while True:
		#do something........
		totalAvgCpuUtil=0
		for i in range(0, ploicyTime/ceilometerDuration, 1):
			time.sleep(ceilometerDuration)
			#allCpuUtil = getAllActiveSproutCpu()
			avgCpuUtil = getAllActiveSproutCpu()/len(getActiveSprout())
			totalAvgCpuUtil = totalAvgCpuUtil + avgCpuUtil
			print "Avg. Cpu Util of active sprouts: ", avgCpuUtil 
			#print("after "+str(ceilometerDuration)+" sec")
			#wait ceilometerDuration time...
			#Get active sprouts' cpu_util from ceilometer
			#get avgCpuUsage 
			#if (avgCpuUsage > cpuHigh && len(activeSproutId) <= maxSprout):
				#do start 1 sprout from shotoffList
			#else if( avgCpuUsage < cpuLow ):
				#stop 1 sprout frome activeList
		print "Avg. Cpu Util of active sprouts in ",ploicyTime," seconds: ", totalAvgCpuUtil/(ploicyTime/ceilometerDuration)
		if totalAvgCpuUtil/(ploicyTime/ceilometerDuration) > cpuHigh and len(getActiveSprout())<maxSprout:
			print "CPU Util is higher than threshold: ", cpuHigh, ". Start sacling up!"
			# start 1 sprout from shotoff Sprout List
			scaleUp( getAllSuspendedSproutInstance() )
			#print "Wait ", waitForScale, " seconds to process scaling"
			#time.sleep(waitForScale)
			print "Scale up done!!!!!"
			print "Back to auto-scaling ploicy...."
		elif totalAvgCpuUtil/(ploicyTime/ceilometerDuration) < cpuLow and len(getActiveSprout())!=minSprout:
			print "CPU Util is lower than threshold: ", cpuLow, ". Start scaling down!"
			# stop 1 sprout from active Sprout List
			scaleDown( getAllActiveSproutInstance() )
			#time.sleep(waitForScale)
			print "Scale down done!!!!!"
			print "Back to auto-scaling ploicy...."
		elif totalAvgCpuUtil/(ploicyTime/ceilometerDuration) > cpuHigh and len(getActiveSprout())==maxSprout:
			print "CPU Util is higher than threshold: ", cpuHigh,". But reach max sprout number."
		elif totalAvgCpuUtil/(ploicyTime/ceilometerDuration) < cpuLow and len(getActiveSprout())==minSprout:
			print "CPU Util is lower than threshold: ", cpuLow,". But reach min sprout number."
		else :
			print "No scaling  up/down triggered....."  # do nothing

try:
	while True:
		autoScaling()
		
except KeyboardInterrupt:
	pass




print "\n\nEnd  :D"
