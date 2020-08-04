import hashlib
import socket
from random import seed
from random import randint

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create socket object
port = 9998 #set port
serverAddr = ('192.168.1.21', port) #set server address



#CLIENT FUNCTIONS:

def FindD(EVal, Phi):
    DVal = 0
    while((EVal * DVal % Phi) != 1):
        print(EVal * DVal % Phi)
        DVal += 1
    return DVal

def FindE():
    seed(1)
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
    return EVal

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
    return KeyInfo
    

def PrintMenu():
    print("\n\n\n")
    print("Welcome to Nathaniel Blevins's Final Project")
    print("--------------------------------------------")
    print("MENU")
    print("1: Upload a file to the server")
    print("2: Download a file from the server")
    print("3: Generate new key pairs")
    print("4: Quit Program")
    print("--------------------------------------------")
    print("\n")

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

def PutFile(Filename):

    #Get Encryption Information
    print("Server Public Encryption Key: ")
    print("----------------------")
    E = int(input("E: "))
    n = int(input("n: "))
    print("----------------------")

    # Tell server what to do
    ServerCommand = "Sending File"
    socket.sendto(ServerCommand.encode(), serverAddr)

    # Send FileName
    socket.sendto(Filename.encode(), serverAddr)
    
    # Send Hash Value of File to send
    Hash = CalculateHash(Filename)
    socket.sendto(Hash.encode(), serverAddr)
    
    # Send file
    file = open(Filename, "rb")
    WholeFile = file.read()
    socket.sendto(str(len(WholeFile)).encode(), serverAddr)
    print("Hash of", Filename, ":", CalculateHash(Filename))
    print("Encrypting File...")
    WholeFile = RSAEncrypt(WholeFile, E, n)
    print("Sending File...")
    for byte in WholeFile:
        socket.sendto(str(byte).encode(), serverAddr)
    file.close()

def GetFile(Filename, Key):

    # Tell server what to do
    ServerCommand = "Requesting File"
    socket.sendto(ServerCommand.encode(), serverAddr)
    
    # Request File
    socket.sendto(Filename.encode(), serverAddr)
    
    # Receive Hash Value
    HashValue, addr = socket.recvfrom(2048)
    HashValue = HashValue.decode()

    # Get size of file
    Size, addr = socket.recvfrom(2048)
    Size = int(Size.decode())
    
    # Receive Message
    file = open(Filename, 'wb+')
    FileToWrite = []
    for Byte in range(Size):
        Value, addr = socket.recvfrom(2048)
        FileToWrite.append(Value.decode())
    FileToWrite = RSADecrypt(FileToWrite, int(Key.get('D')), int(Key.get('n')))
    file.write(bytes(FileToWrite))
    file.close()

    # Compare Hash Values
    print("Hash of received file:", HashValue)
    print("Calculated Hash of Downloaded file:", CalculateHash(Filename))

def QuitProgram():
    ServerCommand = "Quit"
    socket.sendto(ServerCommand.encode(), serverAddr)

#Calculate Hash Value of File
def CalculateHash(File):
    HashFile = open(File, 'rb')
    TotalBytes = HashFile.read()
    hash_object = hashlib.sha256(TotalBytes)
    HashValue = hash_object.hexdigest()
    HashFile.close()
    return HashValue
    
#Client main:
KeyInfo = KeyGenerator()
while True:
    PrintMenu()
    Command = input("Selection: ")
    if Command == '1':
        FileToUpload = input("File to upload: ")
        PutFile(FileToUpload)
    elif Command == '2':   
        FileToDownload = input("File to download: ")
        GetFile(FileToDownload, KeyInfo)
    elif Command == '3':
        KeyInfo = KeyGenerator()
    elif Command == '4':   #Quit program
        print("Exiting Program...")
        QuitProgram()
        socket.close #close connection
        break
    else: print("Command not valid")
        
socket.close #close connection

    
    
    
    
