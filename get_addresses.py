from pygdbmi.gdbcontroller import GdbController

gdbmi = GdbController(command=["arm-none-eabi-gdb", "--interpreter=mi3"])

if gdbmi.write(f"file {input("File: ")}")[-1]["message"] == "error":
    print("Error! File Not Found")
    exit()

variables = input("Enter variables seperated by spaces: ").strip().split(" ")

address_dict = {}

for var in variables:
    response = gdbmi.write(f"print &{var}")
    if response[-1]["message"] == "error":
        print(f"Did not find {var}")
    else:
        address_dict[var] = response[1]["payload"].split(" ")[4]

with open("addresses.txt", "w") as f:
    for i in address_dict:
        print(i, address_dict[i], file=f)
