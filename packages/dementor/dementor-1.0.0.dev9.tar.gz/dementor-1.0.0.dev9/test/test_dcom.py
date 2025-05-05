import struct
import array

from impacket.dcerpc.v5 import dcom, rpcrt, dcomrt

# resp = dcomrt.ServerAlive2Response(bytes.fromhex("05000700000002002d0000002d00170007004400430030003100000007003100390032002e003100360038002e00350036002e00310031003500000000000900ffff00001e00ffff00001000ffff00000a00ffff00001600ffff00001f00ffff00000e00ffff0000000000000000000000000000"))

# bindings = resp["ppdsaOrBindings"]
# data = bindings["aStringArray"]
# data = array.array("H", data).tobytes()
# data_len = len(data)
# offset = 0
# sec_offset = bindings["wSecurityOffset"] * 2


# print(offset)

# for _ in range():

packet = dcomrt.ServerAlive2Response()
packet["pComVersion"] = dcomrt.COMVERSION()
packet["ErrorCode"] = 0

bindings = dcomrt.DUALSTRINGARRAY()


data = array.array('H')
# Only one stringbinding
binding = dcomrt.STRINGBINDING()
binding["wTowerId"] = 0x07 # ncacn_ip_tcp
binding["aNetworkAddr"] = "127.0.0.1"
data.extend(array.array('H', binding.getData()))

sec_offset = len(data)
if sec_offset % 2 != 0:
    data.append(0x00)
    sec_offset += 1

binding = dcomrt.SECURITYBINDING()
binding["wAuthnSvc"] = rpcrt.RPC_C_AUTHN_WINNT
binding["aPrincName"] = ""
binding["Reserved"] = 0xFFFF
data.extend(array.array('H', binding.getData()))

bindings["wNumEntries"] = len(data)
bindings["wSecurityOffset"] = sec_offset
bindings["aStringArray"] = data

packet["ppdsaOrBindings"] = bindings

print(packet.getData())