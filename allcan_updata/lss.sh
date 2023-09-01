###################xxxxxxxx######
cansend can0 7E5#4043480000000000 # Vendor-ID
cansend can0 7E5#4132006500000000 # Product Code
cansend can0 7E5#4204504142000000 # Revision Version
cansend can0 7E5#4335353320000000 # Serial Number
sleep 0.5
# 配置节点
cansend can0 7E5#11$*000000000000
sleep 0.5
cansend can0 7E5#1700000000000000
sleep 0.5
cansend can0 7E5#0400000000000000

cansend can0 000#8100



