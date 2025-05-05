from impacket.dcerpc.v5 import epm


data = bytes.fromhex("0100000000000000000000000000000000000000020000004b0000004b000000050013000d81bb7a364498f135ad3298f03800100302000200000013000d045d888aeb1cc9119fe808002b10486002000200000001000b020000000100070200008701000904000000000000000000000000000000000000000000000000000004000000")

map_req = epm.ept_map(data)
map_resp = epm.ept_mapResponse()
map_resp["status"] = 0  # success
map_resp["num_towers"] = 1
map_resp["entry_handle"] = map_req["entry_handle"]

req_tower = epm.EPMTower(b"".join(map_req["map_tower"]["tower_octet_string"]))
req_floors = req_tower["Floors"]
resp_tower = epm.EPMTower()
resp_floors = []

# First floor will be the interface
interface = req_floors[0]["InterfaceUUID"]
# Second floor must map to the same syntax -> TODO
# THird floor MUST be TCP
resp_floors.extend(req_floors[:3])

epm_port = epm.EPMPortAddr()
epm_port["IpPort"] = 135# self.rpc_config.epm_port
resp_floors.append(epm_port)

epm_host = epm.EPMHostAddr()
epm_host["Ip4addr"] = "127.0.0.1" # self.config.ipv4
resp_floors.append(epm_host)

resp_tower["NumberOfFloors"] = len(resp_floors)
resp_tower["Floors"] = b"".join([i.getData() for i in resp_floors])

resp_tower_data = epm.twr_p_t()
resp_tower_data["tower_octet_string"] = resp_tower.getData()
resp_tower_data["tower_length"] = len(resp_tower_data["tower_octet_string"])
resp_tower_data["ReferentID"] = 2

map_resp["ITowers"] = [resp_tower_data]
print(map_resp.getData())