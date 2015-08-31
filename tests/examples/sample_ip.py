#from common import *
import switch
#import pytest
from switch.CLI import *
from switch.CLI.lldp import *
from switch.CLI.interface import *
from lib import *

topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,lnk02:dut01:wrkston02",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston02:system-category:workstation"}

def switch_reboot(dut01):
    # Reboot switch
    LogOutput('info', "Reboot switch") 
    dut01.Reboot()
    rebootRetStruct = returnStruct(returnCode=0)
    return rebootRetStruct

def ping_to_switch(dut01, wrkston01):
    # Switch config
    LogOutput('info', "Configuring Switch to be an IPv4 router")
    retStruct = InterfaceEnable(deviceObj=dut01, enable=True,
                             interface=dut01.linkPortMapping['lnk01'])
    if retStruct.returnCode() != 0:
        assert("Failed to enable port on switch")
    else:
        LogOutput('info', "Successfully enabled port on switch")

    retStruct = InterfaceIpConfig(deviceObj=dut01,
                                  interface=dut01.linkPortMapping['lnk01'],
                                  addr="140.1.1.1", mask=24, config=True)
    # Workstation config
    LogOutput('info', "Configuring workstations")
    retStruct = wrkston01.NetworkConfig(ipAddr="140.1.1.10", netMask="255.255.255.0", broadcast="140.1.1.255", 
                                        interface=wrkston01.linkPortMapping['lnk01'], config=True)
    if retStruct.returnCode() != 0:
        assert("Failed to configure IP on workstation")
    
    cmdOut = wrkston01.cmd("ifconfig "+ wrkston01.linkPortMapping['lnk01'])
    LogOutput('info', "Ifconfig info for workstation 1:\n" + cmdOut)

# 
    cmdOut = dut01.cmdVtysh(command="show run")
    LogOutput('info', "Running config of the switch:\n" + cmdOut)
    
    LogOutput('info', "Pinging between workstation1 and dut01")
    retStruct = wrkston01.Ping(ipAddr="140.1.1.1")
    if retStruct.returnCode() != 0:
        assert("Failed to ping switch")
    else:
        LogOutput('info', "IPv4 Ping from workstation 1 to dut01 return JSON:\n" + str(retStruct.retValueString()))
        packet_loss = retStruct.valueGet(key='packet_loss')
        packets_sent = retStruct.valueGet(key='packets_transmitted')
        packets_received = retStruct.valueGet(key='packets_received')
        LogOutput('info', "Packets Sent:\t"+ str(packets_sent))
        LogOutput('info', "Packets Recv:\t"+ str(packets_received))
        LogOutput('info', "Packet Loss %:\t"+str(packet_loss))
        
    ptosRetStruct = returnStruct(returnCode=0)
    return ptosRetStruct

def ping_through_switch(dut01, wrkston01, wrkston02):
    # Configure other switch port
    retStruct = InterfaceEnable(deviceObj=dut01, enable=True,
                             interface=dut01.linkPortMapping['lnk02'])
    if retStruct.returnCode() != 0:
        assert("Failed to enable port on switch")
    else:
        LogOutput('info', "Successfully enabled port on switch")
        
    retStruct = InterfaceIpConfig(deviceObj=dut01,
                                  interface=dut01.linkPortMapping['lnk02'],
                                  addr="140.1.2.1", mask=24, config=True)
    if retStruct.returnCode() != 0:
        assert("Failed to configure IP on switchport")
    else:
        LogOutput('info', "Successfully configured ip on switch port")
        
    LogOutput('info', "Configuring workstations")
    retStruct = wrkston02.NetworkConfig(ipAddr="140.1.2.10", netMask="255.255.255.0", broadcast="140.1.2.255", 
                                        interface=wrkston02.linkPortMapping['lnk02'], config=True)
    if retStruct.returnCode() != 0:
        assert("Failed to configure IP on workstation")
    
    cmdOut = wrkston02.cmd("ifconfig "+ wrkston02.linkPortMapping['lnk02'])
    LogOutput('info', "Ifconfig info for workstation 2:\n" + cmdOut)
        
    
    retStruct = wrkston01.IPRoutesConfig(config=True, destNetwork="140.1.2.0", netMask=24, gateway="140.1.1.1")
    if retStruct.returnCode() != 0:
        assert("Failed to configure IP route on workstation 1")
        
    cmdOut = wrkston01.cmd("netstat -rn")
    LogOutput('info', "IPv4 Route table for workstation 1:\n" + cmdOut)
 
    retStruct = wrkston02.IPRoutesConfig(config=True, destNetwork="140.1.1.0", netMask=24, gateway="140.1.2.1")
    if retStruct.returnCode() != 0:
        assert("Failed to configure IP route on workstation 2")
        
    cmdOut = wrkston02.cmd("netstat -rn")
    LogOutput('info', "IPv4 Route table for workstation 2:\n" + cmdOut)
# 
    LogOutput('info', "Pinging between workstation1 and workstation2")
    retStruct = wrkston01.Ping(ipAddr="140.1.2.10")
    if retStruct.returnCode() != 0:
        assert("Failed to ping from workstation 1 to workstation2 through the switch")
    else:
        LogOutput('info', "IPv4 Ping from workstation 1 to workstation 2 return JSON:\n" + str(retStruct.retValueString()))
        packet_loss = retStruct.valueGet(key='packet_loss')
        packets_sent = retStruct.valueGet(key='packets_transmitted')
        packets_received = retStruct.valueGet(key='packets_received')
        LogOutput('info', "Packets Sent:\t"+ str(packets_sent))
        LogOutput('info', "Packets Recv:\t"+ str(packets_received))
        LogOutput('info', "Packet Loss %:\t"+str(packet_loss))
    ptosRetStruct = returnStruct(returnCode=0)
    return ptosRetStruct
# 

def deviceCleanup(dut01, wrkston01, wrkston02):
    LogOutput('info', "Unonfiguring workstations")
    retStruct = wrkston01.IPRoutesConfig(config=False, destNetwork="140.1.2.0", netMask=24, gateway="140.1.1.1")
    if retStruct.returnCode() != 0:
        assert("Failed to remove IP route on workstation 1")
    cmdOut = wrkston01.cmd("netstat -rn")
    LogOutput('info', "IPv4 Route table for workstation 1:\n" + cmdOut)
# 
    retStruct = wrkston02.IPRoutesConfig(config=False, destNetwork="140.1.1.0", netMask=24, gateway="140.1.2.1")
    if retStruct.returnCode() != 0:
        assert("Failed to remove IP route on workstation 2")

    cmdOut = wrkston02.cmd("netstat -rn")
    LogOutput('info', "IPv4 Route table for workstation 1:\n" + cmdOut)
# 
    retStruct = wrkston01.NetworkConfig(ipAddr="140.1.1.10", netMask="255.255.255.0", broadcast="140.1.1.255", 
                                           interface=wrkston01.linkPortMapping['lnk01'], config=False)
    if retStruct.returnCode() != 0:
        assert("Failed to unconfigure IP address on workstation 1")
    cmdOut = wrkston01.cmd("ifconfig "+ wrkston01.linkPortMapping['lnk01'])
    LogOutput('info', "Ifconfig info for workstation 1:\n" + cmdOut)
    
    retStruct = wrkston02.NetworkConfig(ipAddr="140.1.2.10", netMask="255.255.255.0", broadcast="140.1.2.255", 
                                        interface=wrkston02.linkPortMapping['lnk02'], config=False)
    if retStruct.returnCode() != 0:
        assert("Failed to unconfigure IP address on workstation 2")
    cmdOut = wrkston02.cmd("ifconfig "+ wrkston02.linkPortMapping['lnk02'])
    LogOutput('info', "Ifconfig info for workstation 2:\n" + cmdOut)
# 
    # LogOutput('info', "Unconfigure switch")
    retStruct = InterfaceIpConfig(deviceObj=dut01,
                               interface=dut01.linkPortMapping['lnk01'],
                               addr="140.1.1.1", mask=24, config=False)
    if retStruct.returnCode() != 0:
        assert("Failed to unconfigure IP address on dut01 port " + str(dut01.linkPortMapping['lnk01']))
    else:
        LogOutput('info', "Unconfigure IP address on dut01 port " + str(dut01.linkPortMapping['lnk01']))
        
    retStruct = InterfaceIpConfig(deviceObj=dut01,
                               interface=dut01.linkPortMapping['lnk02'],
                               addr="140.1.2.1", mask=24, config=False)
    if retStruct.returnCode() != 0:
        assert("Failed to unconfigure IP address on dut01 port " + str(dut01.linkPortMapping['lnk02']))
    else:
        LogOutput('info', "Unconfigure IP address on dut01 port " + str(dut01.linkPortMapping['lnk02']))
 
    retStruct = InterfaceEnable(deviceObj=dut01, enable=False,
                             interface=dut01.linkPortMapping['lnk01'])
    if retStruct.returnCode() != 0:
        assert("Failed to shutdown dut01 interface " + str(dut01.linkPortMapping['lnk01']))
    else:
        LogOutput('info', "Shutdown dut01 interface " + str(dut01.linkPortMapping['lnk01']))

    retStruct = InterfaceEnable(deviceObj=dut01, enable=False,
                                interface=dut01.linkPortMapping['lnk02'])
    if retStruct.returnCode() != 0:
        assert("Failed to shutdown dut01 interface " + str(dut01.linkPortMapping['lnk02']))
    else:
        LogOutput('info', "Shutdown dut01 interface " + str(dut01.linkPortMapping['lnk02']))

    cmdOut = dut01.cmdVtysh(command="show run")
    LogOutput('info', "Running config of the switch:\n" + cmdOut)
    cleanupRetStruct = returnStruct(returnCode=0)
    return cleanupRetStruct

#class Test_ft_framework_basics:
#    def setup_class(cls):
        # Create Topology object and connect to devices
testObj = testEnviron(topoDict=topoDict)
topoObj = testObj.topoObjGet()
dut01Obj = topoObj.deviceObjGet(device="dut01")
wrkston01Obj = topoObj.deviceObjGet(device="wrkston01")
wrkston02Obj = topoObj.deviceObjGet(device="wrkston02")
#    def teardown_class(cls):
#        # Terminate all nodes
#        Test_ft_framework_basics.topoObj.terminate_nodes()
        
#   def test_reboot_switch(self):
LogOutput('info', "############################################")
LogOutput('info', "Reboot the switch")
LogOutput('info', "############################################")
#dut01Obj = topoObj.deviceObjGet(device="dut01")
devRebootRetStruct = switch_reboot(dut01Obj)
if devRebootRetStruct.returnCode() != 0:
    assert("Failed to reboot Switch")
else:
    LogOutput('info', "Passed Switch Reboot piece")
    
    #def test_ping_to_switch(self):
LogOutput('info', "############################################")
LogOutput('info', "Configure and ping to switch")
LogOutput('info', "############################################")
        #dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        #wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
pingSwitchRetStruct = ping_to_switch(dut01Obj, wrkston01Obj)
if pingSwitchRetStruct.returnCode() != 0:
    assert("Failed to ping to the switch")
else:
    LogOutput('info', "Passed ping to switch test")
    
#    def test_ping_through_switch(self):
LogOutput('info', "############################################")
LogOutput('info', "Additional configuration and ping through switch")
LogOutput('info', "############################################")
#        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
#        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        #wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
pingSwitchRetStruct = ping_through_switch(dut01Obj, wrkston01Obj, wrkston02Obj)
if pingSwitchRetStruct.returnCode() != 0:
    assert("Failed to ping through the switch")
else:
    LogOutput('info', "Passed ping to switch test")
    
#    def test_clean_up_devices(self):
LogOutput('info', "############################################")
LogOutput('info', "Device Cleanup - rolling back config")
LogOutput('info', "############################################")
#        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
#        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
#        wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
cleanupRetStruct = deviceCleanup(dut01Obj, wrkston01Obj, wrkston02Obj)
if cleanupRetStruct.returnCode() != 0:
    assert("Failed to cleanup device")
else:
    LogOutput('info', "Cleaned up devices")

topoObj.terminate_nodes()