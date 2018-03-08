import csv
import ipaddress

# #########################################################################
# CSV File Format
# Filename must be vlans.csv
#
# VLAN = VLAN Number
# IP_Addr = IP Subnet
# Subnet_Mask = Subnet mask in numeric format ex: 24
# VLAN_Name = Name of VLAN to be used in VLAN configuration
# Description = Description to be used in interface
# VRF = name of VRF, can be blank or default if part of default VRF
# HI_Low = Use 'hi' for upper range of subnet, use 'low' for lower part of subnet for Gateway addresses
# Interface_Type = gateway, p2p, ICMP_ONLY, VLAN_ONLY
# OSPF_Instance = name of the OSPF instance, if not part of OSPF leave blank or 'none'
# OSPF_Area = Area of the OSPF Instance
# OSPF_Key = Key number for point to point networks
# OSPF_Phrase = OSPF password phrase in unencrypted format
# #########################################################################


def Primary_VLAN_Gateway(row):
	IP_NETWORK = (row['IP_Addr'] + '/' + row['Subnet_Mask'])
	IP_BROADCAST = ipaddress.IPv4Network(IP_NETWORK).broadcast_address
	
	if row['Hi_Low'].upper() == 'LOW':
		ip_address = str(ipaddress.IPv4Address(row['IP_Addr']) + 2)
		gw_address = str(ipaddress.IPv4Address(row['IP_Addr']) + 1)
	else:
		ip_address = str(IP_BROADCAST - 3)
		gw_address = str(IP_BROADCAST - 1)
		
	if (row['OSPF_Instance'].upper() == 'NONE') or (len(row['OSPF_Instance']) == 0):
		OSPF_String = ''
	else:
		OSPF_String = ( 
		'  ip ospf passive-interface' + '\n' + 
		'  ip router ospf ' + row['OSPF_Instance'] + ' area ' + row['OSPF_AREA'] + '\n'
		)

	if (row['VRF'].upper() == 'DEFAULT') or (len(row['VRF']) == 0):
		VRF_String = ''
	else:
		VRF_String = ('  vrf member ' + row['VRF'] + '\n')
	
	return (
		'interface vlan ' + row['VLAN'] + '\n' + 
		'  description ' + row['Description'] + '\n' + 
		VRF_String +
		'  ip address ' + ip_address + '/' + row['Subnet_Mask'] + '\n' + 
		OSPF_String + 
		'  no ip redirects' + '\n' +
		'  ip pim sparse-mode' + '\n' +
		'  ip pim dr-priority 50' + '\n' +
		'  hsrp version 2' + '\n' +
		'  hsrp 1' + '\n' +
		'    authentication md5 key-chain hsrp1' + '\n' +
		'    preempt delay minimum 180' + '\n' +
		'    priority 130' + '\n' +
		'    ip ' + gw_address + '\n'
		)

def Secondary_VLAN_Gateway(row):
	IP_NETWORK = (row['IP_Addr'] + '/' + row['Subnet_Mask'])
	IP_BROADCAST = ipaddress.IPv4Network(IP_NETWORK).broadcast_address

	if row['Hi_Low'].upper() == 'LOW':
		ip_address = str(ipaddress.IPv4Address(row['IP_Addr']) + 3)
		gw_address = str(ipaddress.IPv4Address(row['IP_Addr']) + 1)
	else:
		ip_address = str(IP_BROADCAST - 2)
		gw_address = str(IP_BROADCAST - 1)
	
	if (row['OSPF_Instance'].upper() == 'NONE') or (len(row['OSPF_Instance']) == 0):
		OSPF_String = ''
	else:
		OSPF_String = ( 
		'  ip ospf passive-interface' + '\n' + 
		'  ip router ospf ' + row['OSPF_Instance'] + ' area ' + row['OSPF_AREA'] + '\n'
		)

	if (row['VRF'].upper() == 'DEFAULT') or (len(row['VRF']) == 0):
		VRF_String = ''
	else:
		VRF_String = ('  vrf member ' + row['VRF'] + '\n')
	
	return (
		'interface vlan' + row['VLAN'] + '\n' + 
		'  description ' + row['Description'] + '\n' + 
		VRF_String +
		'  ip address ' + ip_address + '/' + row['Subnet_Mask'] + '\n' + 
		OSPF_String + 
		'  no ip redirects' + '\n' +
		'  ip pim sparse-mode' + '\n' +
		'  hsrp version 2\n  hsrp 1' + '\n' +
		'    authentication md5 key-chain hsrp1' + '\n' +
		'    preempt' + '\n' +
		'    priority 110' + '\n' +
		'    ip ' + gw_address + '\n'
		)

def VLAN_Configuration(row):
	return (
	'vlan ' + row['VLAN'] + '\n' + 
	'  name ' + row['VLAN_Name'] + '\n'
	)
	
def Primary_VLAN_NOT_Gateway(row):
	if row['VRF'] != '':
		VRF_String = ('  vrf member ' + row['VRF'] + '\n')
	else:
		VRF_String = ''

	return (
	'interface vlan' + row['VLAN'] + '\n' +
	'  description ' + row['Description'] + '\n' + 
	VRF_String +
	'  ip address ' + str(ipaddress.IPv4Address(row['IP_Addr']) + 7) + '/' + row['Subnet_Mask'] + '\n' +
	'  no ip redirects' + '\n' +
	'  ip pim sparse-mode' + '\n' +
	'  ip access-group ICMP_ONLY in' + '\n'
	)
	
def Secondary_VLAN_NOT_Gateway(row):
	if row['VRF'] != '':
		VRF_String = ('  vrf member ' + row['VRF'] + '\n')
	else:
		VRF_String = ''

	return (
	'interface vlan' + row['VLAN'] + '\n' +
	'  description ' + row['Description'] + '\n' +
	VRF_String +
	'  ip address ' + str(ipaddress.IPv4Address(row['IP_Addr']) + 8) + '/' + row['Subnet_Mask'] + '\n' +
	'  no ip redirects' + '\n' +
	'  ip pim sparse-mode' + '\n' +
	'  ip access-group ICMP_ONLY in' + '\n'
	)
	
def Point_to_Point_VLAN(row):
	OSPF_String = (
		'  ip ospf message-digest-key ' + row['OSPF_Key'] + ' md5 ' + row['OSPF_Phrase'] + '\n' +
		'  ip router ospf ' + row['OSPF_Instance'] + ' area ' + row['OSPF_AREA'] + '\n'
	)
	
	if row['Hi_Low'].upper() == 'LOW':
		ip_address = str(ipaddress.IPv4Address(row['IP_Addr']) + 1)
		dr_priority = '  ip pim dr-priority 50' + '\n'
	else:
		ip_address = str(ipaddress.IPv4Address(row['IP_Addr']) + 2)
		dr_priority = ''

	return (
		'interface vlan' + row['VLAN'] + '\n' + 
		'  description ' + row['Description'] + '\n' + 
		'  ip address ' + ip_address + '/' + row['Subnet_Mask'] + '\n'  + 
		OSPF_String + 
		'  no ip redirects' + '\n' +
		'  ip pim sparse-mode' + '\n' +
		dr_priority
		)
		
#def no longer needed nor used but leaving for reference
def allcaps(word):
    return "".join([i.title() for i in list(word)])

# This is the main code
# Open the CSV file for reading and open all of the files to write out to

# name of the file to open
F_Name = 'vlans.csv'

with open(F_Name, newline='') as csvfile:
#with csvfile = open('vlans.csv', newline=''):
	#open('vlans1.csv', newline='') as csvfile
	read_dict = csv.DictReader(csvfile)
	F_ConfigP = open('configpri.txt', 'w')
	F_ConfigS = open('configsec.txt', 'w')
	F_ConfigV = open('configvlan.txt', 'w')
	F_ConfigE = open('configError.txt', 'w')
	F_ConfigP2P = open('configp2p.txt', 'w')
	F_ConfigV.write('!  VLAN Configuration for both devices\n!\n')
	F_ConfigP.write('!  Interface VLAN Configuration for primary device\n!\n')
	F_ConfigS.write('!  Interface VLAN Configuration for secondary device\n!\n')
	F_ConfigP2P.write('!  Interface VLAN Configuration for Point to Point Interfaces\n!\n')
	for row in read_dict:
		#VLAN Configuration
		F_ConfigV.write(VLAN_Configuration(row))
		#Int_Type = allcaps(row['Interface_Type'])
		Int_Type = row['Interface_Type'].upper()
		#print (Int_Type)
		if Int_Type == 'GATEWAY':
			#Primary Interface Configuration
			F_ConfigP.write(Primary_VLAN_Gateway(row))
			F_ConfigP.write('   no shutdown\n!!!!!!!!!\n')
			#Secondary Interface Configuration
			F_ConfigS.write(Secondary_VLAN_Gateway(row))
			F_ConfigS.write('   no shutdown\n!!!!!!!!!\n')
		elif Int_Type == 'ICMP_ONLY':
			F_ConfigP.write(Primary_VLAN_NOT_Gateway(row))
			F_ConfigP.write('  no shutdown\n!!!!!!!!!\n')
			F_ConfigS.write(Secondary_VLAN_NOT_Gateway(row))
			F_ConfigS.write('  no shutdown\n!!!!!!!!!\n')
		elif Int_Type == 'P2P':
			F_ConfigP2P.write(Point_to_Point_VLAN(row))
			F_ConfigP2P.write('  no shutdown\n!!!!!!!!!\n')
		elif Int_Type == 'VLAN_ONLY':
			F_ConfigE.write('I created only a Layer 2 VLAN\n')
			F_ConfigE.write(str(row.keys()))
			F_ConfigE.write('\n')
			F_ConfigE.write(str(row.values()))
			F_ConfigE.write('\n')
		else:
			F_ConfigE.write('Not an Interface I recognize\n')
			F_ConfigE.write(str(row.keys()))
			F_ConfigE.write('\n')
			F_ConfigE.write(str(row.values()))
			F_ConfigE.write('\n')

	F_ConfigP.close
	F_ConfigS.close
	F_ConfigV.close
	F_ConfigE.close
	F_ConfigP2P.close

print('We are done!')
