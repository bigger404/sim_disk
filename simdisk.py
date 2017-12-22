from filesys import *
import json

def initDisk(size=100):
    return Disk(size)

def loadDisk():
    try:
        with open('diskfile') as f:
            print("INIITIALIZE FROM FILE")
            disk=Disk()
            fromDisk=json.load(f)
            disk.size=fromDisk[0]
            disk.freespace=fromDisk[1]
            disk.blocks=fromDisk[2]
            f.close()
            return disk
    except OSError:
        print("File not found\nInitializing New Disk\n")
        disk=initDisk()
        return disk

def saveDisk(disk):
    try:
        with open('diskfile','w') as f:
            todump=[disk.size,disk.freespace,disk.blocks]
            json.dump(todump,f)
            f.close()
    except OSError:
        print("Unable to save disk file")

def quit_sim(disk):
    ans=input("Save file system?<y/n>")
    if ans.lower()=="y":
        saveDisk(disk)
    exit()

def stats(disk):
    print("Size: "+str(disk.size))
    print("blocks array: \n"+str(disk.blocks))
    print("stats....")

def test(disk):
    print("create D dir1")
    disk.create('D','dir1')
    print("create D dir1/dir2")
    disk.create('D','dir1/dir2')
    print("create U dir1/dir2/file1")
    disk.create('U','dir1/dir2/file1')
    print("open O dir1/dir2/file1")
    disk.open('O','dir1/dir2/file1')
    print("write 5 \'chloe!\'")
    disk.write(5,'chloe!')
    print("close")
    disk.close()
    print("open I dir1/dir2/file1")
    disk.open('I','dir1/dir2/file1')
    print("read 6")
    print(disk.read(6))
    print("close")
    disk.close()
    print("create D dir1/dir3")
    disk.create('D','dir1/dir3')
    print("create U dir1/dir3/file2")
    disk.create('U','dir1/dir3/file2')
    print("open O dir1/dir3/file2")
    disk.open('O','dir1/dir3/file2')
    print("read 5")
    print(disk.read(5))
    print("write 5 \'words\'")
    disk.write(5,'words')
    print("close")
    disk.close()
    print("open O dir1/dir3/file2")
    disk.open('O','dir1/dir3/file2')
    print("write 5 \'more \'")
    disk.write(5,'more ')
    print("close")
    disk.close()
    print("open I dir1/dir3/file2")
    disk.open('I','dir1/dir3/file2')
    print("read 12")
    print(disk.read(12))
    print("close")
    disk.close()
    #stats(disk)
    quit_sim(disk)    
    exit()

if __name__ == '__main__':
    myDisk=None
    ans=input("<I>nitialize from file\n<N>ew Disk\n: ")
    if ans.lower()=="i":
        myDisk=loadDisk()
    else:
        try:
            ans=int(input("Enter Disk Size: (100 Default) "))
            myDisk=initDisk(ans)
        except ValueError:
            myDisk=initDisk()
    #ans=input("<T>est or <P>rompt: ")
    #if ans.lower()=="t":
    #    test(myDisk)
    #    exit()#just in case..

    while True:
        fromUser=input("myDisk: ")
        #print(fromUser)
        if(fromUser=="quit"):
            quit_sim(myDisk)
            break
        words = fromUser.split(" ")
        if(words[0]=="create"and len(words)==3):
            myDisk.create(words[1],words[2])
        elif(words[0]=="open"and len(words)==3):
            myDisk.open(words[1],words[2])
        elif(words[0]=="close"and len(words)==1):
            myDisk.close()
        elif(words[0]=="delete"and len(words)==2):
            myDisk.delete(words[1])
        elif(words[0]=="read"and len(words)==2):
            print(myDisk.read(words[1]))
        elif(words[0]=="write"and len(words)>=3):
            #myDisk.write(words[1],words[2])
            #myDisk.write(words[1],words[2][1:len(words[2])-2])
            words[2]=' '.join(words[2:])
            myDisk.write(words[1],words[2].strip("\'"))
        elif(words[0]=="seek"and len(words)==3):
            myDisk.seek(words[1],words[2])
        else:
           print(words)
           print("Bad Input :(")
