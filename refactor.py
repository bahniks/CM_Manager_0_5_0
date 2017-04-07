import os

search = "wait"

for file in os.listdir(os.getcwd()):
    if file.endswith(".py"):
        with open(file) as f:
            for num, line in enumerate(f, 1):
                if search in line:
                    print(file, "\t", num, "\t", line)



import platform
print(platform.system())
