from operationLib.CISCO import CISCO
import argparse
import getpass
import xlsxwriter
def main():
	
	fw_list = [] #ADD YOUR FW NAMES
	fw_dict = { } # ADD FWNAME:FWIP


	parser = argparse.ArgumentParser(prog='PROG',formatter_class=argparse.RawTextHelpFormatter,description="""Extract and filter cisco ACLs.
###########################
Created by Mostafa Soliman
###########################""")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-cmd",help="Open interactive shell",action="store_true")
	group.add_argument("-fwname",help="FW Name")
	group.add_argument("-printfw",help="Print FW Name",action="store_true")

	parser.add_argument("-srcnet",help="Provide source network to filter on")
	parser.add_argument("-dstnet",help="Provide destination network to filter on")
	parser.add_argument("-protocol",help="Provide protocol to filter on")
	parser.add_argument("-port",help="Provide port number to filter on")
	parser.add_argument("-action",help="Provide policy action (permit/deny)")    
	parser.add_argument("-update",help="Update FW Config on the local drive",action="store_true")
	#parser.add_argument("-manip",help="Provide FW Managment IP")
	parser.add_argument("-oT",help="write output to file")
	parser.add_argument("-oX",help="write CSV file")
	args = parser.parse_args()


	if args.printfw:
		for fw in fw_dict:
			print fw
		return


	if args.cmd:
		#
		#TO DO:: CREATE INTERACTIVE SHELL
		#
		pass

	else:
		if args.fwname not in fw_list:
			print 'Bad FW Name , use -printfw'
			return

		fw = CISCO(DeviceName = args.fwname )
		if args.update:
			#UPDATE FW DATA	
			#

			fw.DeviceManIp = fw_dict[args.fwname]

			
			defualt_username=getpass.getuser()
			if '-' in defualt_username:
				defualt_username=defualt_username.split('-')[1]
				defualt_username=defualt_username[0].lower()+'.'+defualt_username.split('.')[1].lower()
			username=raw_input('Username[%s]:'%(defualt_username))
			if(not username):
				username=defualt_username
			password=getpass.getpass()
			fw.username = username
			fw.password = password


			print '[*]Getting Device Type and Version'
			fw.Get_Device_Info()
			print '[*]Devcie Type:',fw.DeviceType,'Device Software Version:',fw.DeviceSoftVersion			
			print '[*]Downloading Device Configurations'
			fw.Update_Device_Data()

		else:
			pass
			#ENSURE THAT DATA EXIST THEN PROCEED
			#
			if not fw.Check_Device_Data_Exist():
				print 'Device Configurations not found, download it by -update.'
				return

		# 
		#EXTRACT THE ACLS
		acl_objects = fw.Get_ACLs(srcnet=args.srcnet,dstnet=args.dstnet,protocol=args.protocol,srcport=None,dstport=args.port,aclname=None,action=args.action,Type=None)
		if args.oT:
			data = '\n'.join([x.config for x in acl_objects] )
			open(args.oT,'w').write(data)
		elif args.oX:
			workbook = xlsxwriter.Workbook(args.oX)
			worksheet = workbook.add_worksheet()
			row = 0
			col = 0
			worksheet.write(row, col,'ACL Name')
			worksheet.write(row, col+1,'Line Number')
			worksheet.write(row, col+2,'ACL Type')
			worksheet.write(row, col+3,'Action')
			worksheet.write(row, col+4,'Protocol Name')
			worksheet.write(row, col+5,'Protocol Value')


			worksheet.write(row, col+6,'Src Name')
			worksheet.write(row, col+7,'Src Networks')
			worksheet.write(row, col+8,'Src Port Name')
			worksheet.write(row, col+9,'Src Port Number')

			worksheet.write(row, col+10,'Dst Name')
			worksheet.write(row, col+11,'Dst Networks')
			worksheet.write(row, col+12,'Dst Port Name')
			worksheet.write(row, col+13,'Dst Port Number')

			worksheet.write(row, col+14,'Time Range')
			worksheet.write(row, col+15,'HitCount')
			worksheet.write(row, col+16,'Hex Indentifier')



			row +=1
			for acl in acl_objects:

				worksheet.write(row, col,acl.Name)
				worksheet.write(row, col+1,acl.LineNo)
				worksheet.write(row, col+2,acl.Type)
				worksheet.write(row, col+3,acl.Action)
				if type(acl.Protocol) ==str : 
					worksheet.write(row, col+4,acl.Protocol)

				else:
					worksheet.write(row, col+4,acl.Protocol.Name)
					if type(acl.Protocol).__name__ == 'ServiceObject':
						worksheet.write(row, col+5,acl.Protocol.ServiceGroup.Name)
					if type(acl.Protocol).__name__ == 'ProtocolObjectGroup':
						worksheet.write(row, col+5,'\n'.join(acl.Protocol.Protocol))
				if type(acl.SrcNet).__name__ == 'IPNetwork' or  type(acl.SrcNet).__name__ == 'IPRange'  :
					worksheet.write(row, col+6,str(acl.SrcNet))
					worksheet.write(row, col+7, str(acl.SrcNet))
				else:
					worksheet.write(row, col+6,acl.SrcNet.Name)
					if type(acl.SrcNet).__name__ == 'NetworkObject':
						worksheet.write(row, col+7, str(acl.SrcNet.Network) )
					elif type(acl.SrcNet).__name__ == 'NetworkObjectGroup':
						net = []
						for n in acl.SrcNet.Network:
							if type(n).__name__  == 'IPNetwork':
								net.append(str(n))
							elif type(n).__name__  == 'NetworkObject':	
								net.append(str(n.Network))						

						worksheet.write(row, col+7,', '.join(net))

				#print acl.config
				#print acl.DstPort
				if acl.Protocol == 'tcp' or acl.Protocol == 'udp':
					worksheet.write(row, col+8,acl.SrcPort.Name)

				#worksheet.write(row, col+9,'Src Port Number')


				if type(acl.DstNet).__name__ == 'IPNetwork' or  type(acl.DstNet).__name__ == 'IPRange'  :
					worksheet.write(row, col+10,str(acl.DstNet))
					worksheet.write(row, col+11, str(acl.DstNet))
				else:
					worksheet.write(row, col+10,acl.DstNet.Name)
					if type(acl.DstNet).__name__ == 'NetworkObject' :
						worksheet.write(row, col+11, str(acl.DstNet.Network) )
					elif type(acl.DstNet).__name__ == 'NetworkObjectGroup':
						net = []
						for n in acl.DstNet.Network:
							if type(n).__name__  == 'IPNetwork':
								net.append(str(n))
							elif type(n).__name__  == 'NetworkObject':	
								net.append(str(n.Network))						

						worksheet.write(row, col+11,', '.join(net))

				if acl.Protocol == 'tcp' or acl.Protocol == 'udp':
					worksheet.write(row, col+12,acl.DstPort.Name)
				
				#worksheet.write(row, col+13,'Src Port Number')



				worksheet.write(row, col+14,acl.TimeRange)
				#worksheet.write(row, col+15,'HitCount')
				#worksheet.write(row, col+16,'Hex Indentifier')

				row+=1
		else:
			print '\n'.join([x.config for x in acl_objects] )

if __name__ == '__main__':
	main()
