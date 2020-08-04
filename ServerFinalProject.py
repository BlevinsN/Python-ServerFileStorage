import hashlib
import socket
from random import seed
from random import randint

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "192.168.1.21" # Local machine address
port = 9998 # Port number for the server
serversocket.bind((ip, port)) # Bind to the port

# SERVER FUNCTIONS

def KeyGenerator():
    KeyInfo = {'n': "NOT SET", 'D': "NOT SET", 'E': "NOT SET"}
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("GENERATE PUBLIC AND PRIVATE KEY PAIR")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    p = int(input("Please enter p value: "))
    q = int(input("Please enter q value: "))
    n = p * q
    KeyInfo['n'] = n
    phi = (p-1) * (q-1)
    DVal = 0
    EVal = 0
    while((EVal * DVal % phi) != 1):
        Test = False
        EVal = 2
        while Test != True:
            prime = True
            EVal = randint(2, 10000)
            for x in range(2, EVal):
                if EVal % x == 0:
                    prime = False
            if prime == True:
                Test = True
        for x in range(2, EVal):
            if (EVal * x % phi) == 1:
                DVal = x
    KeyInfo['E'] = EVal
    KeyInfo['D'] = DVal
    print("The Private Key is [", KeyInfo['n'], ",", KeyInfo['D'],"]")
    print("The Public Key is [", KeyInfo['n'], ",", KeyInfo['E'], "]")
    print("Waiting on Client request...\n")
    return KeyInfo

# Status of Machine
def ServerStatus():
    Command, addr = serversocket.recvfrom(1024)
    return Command.decode()

def RSAEncrypt(File, E, n):
    Encrypted = []
    for byte in File:
        Value = (byte ** E) % n
        Encrypted.append(Value)
    return Encrypted

def RSADecrypt(File, D, n):
    Decrypted = []
    for byte in File:
        Value = (int(byte) ** D) % n
        Decrypted.append(Value)
    return Decrypted

# Uploading a file to server
def SaveFile(Key):

    
    # Get file name
    FileName, addr = serversocket.recvfrom(1024)
    # Get Hash Value
    HashValue, addr = serversocket.recvfrom(1024)

    # Get size of file
    Size, addr = serversocket.recvfrom(2048)
    Size = int(Size.decode())
    
    # Write file to local directory
    FileToSave = open(FileName.decode(), 'wb+')
    WholeFile = []
    print("Recieving File...")
    for Byte in range(Size):
        Value, addr = serversocket.recvfrom(2048)
        WholeFile.append(Value.decode())
    print("Decrypting File...")
    WholeFile = RSADecrypt(WholeFile, int(Key.get('D')), int(Key.get('n')))
    FileToSave.write(bytes(WholeFile))
    FileToSave.close()
    SavedHash = CalculateHash(FileName)

    #Compare Hash Values
    print("Hash of file reveived:", HashValue.decode())
    print("Hash of file saved:", SavedHash)

    return FileName.decode()
        
# Requesting a file from server
def SendFile():
    
    #Get Encryption Information
    print("Client Public Encryption Key: ")
    print("----------------------")
    E = int(input("E: "))
    n = int(input("n: "))
    print("----------------------")

    # Get file name
    FileName, addr = serversocket.recvfrom(1024)

    # Calculate Hash Value of File to send
    Hash = CalculateHash(FileName)
    serversocket.sendto(Hash.encode(), addr)
    
    # Send file
    file = open(FileName.decode(), 'rb')
    WholeFile = file.read()
    serversocket.sendto(str(len(WholeFile)).encode(), addr)
    WholeFile = RSAEncrypt(WholeFile, E, n)
    for byte in WholeFile:
        serversocket.sendto(str(byte).encode(), addr)
    file.close()

    return FileName.decode()

#Calculate Hash Value of File
def CalculateHash(File):
    HashFile = open(File, 'rb')
    TotalBytes = HashFile.read()
    hash_object = hashlib.sha256(TotalBytes)
    HashValue = hash_object.hexdigest()
    HashFile.close()
    return HashValue


# Server Main Code
KeyInfo = KeyGenerator()
while True:

    # Print status of Server
    Command = ServerStatus()

    # User trying to upload file
    if Command == "Sending File":
        print("User is trying to upload file")
        FileName = SaveFile(KeyInfo)
        print("File uploaded:", FileName)

    # User is requesting file
    if Command == "Requesting File":
        print("User is requesting a file")
        FileName = SendFile()
        print("File sent:", FileName)
        
    #User is done with program
    if Command == "Quit":
        print("User is done with program")
        serversocket.close()
        break
    
#Program disconnected
print("Disconnected.")
