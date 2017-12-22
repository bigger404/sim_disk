
#To read data blocks: 
#disk.blocks[blk#][0] back
#disk.blocks[blk#][1] frwd
#disk.blocks[blk#][2][data index #(0-504)]

#To read directory blocks
#disk.blocks[blk#][0] back
#disk.blocks[blk#][1] frwd
#disk.blocks[blk#][2] free
#disk.blocks[blk#][3] 'fill'
#disk.blocks[blk#][4] arr of entries
#disk.blocks[blk#][4][0] 1st directory entry =['U', 'filename', blk#, size]

#free space list:
#self.freespace         1s are free, 0s are used. index corresponds to block number

#Open file info found in:
#self.open_files                                Open?/dirblk/direntry/fileblk/IOU Mode/byteptr
#self.fileblks[first][lastsize][blk list]      Gives the list of blocks for the current open file

#Disk Class
class Disk():
    #Constructor
    def __init__(self,size=100):    #create 100 block disk by default
        ##defaults        
        self.size=size                                  #Disk size
        self.freespace=[1]*size                         #Disk freespace list
        self.data_template=[None,None,[None]*504]       #back,frwd,data*504

        self.dir=['F','',0,0]                           #dir=[type,name,link,size]
        self.dirs=[self.dir]*31                         #31 deep
        self.dir_template=[0,0,0,'fill',self.dirs]      #back,frwd,free,filler,[dirs]
        
        self.open_file=[False,0,0,0,'I',0]              #Open?/dirblk/direntry/fileblk/IOU Mode/byteptr
        self.file_blks=[0,0,[]]                         #first/last size/list of blks
        self.blocks=[None]*self.size                    #Build blocks array
        
        self.freespace[0]=0                             #Setup Block Zero
        self.blocks[0]=self.dir_template[:]

    #Create function
    def create(self,typ,name):
        if(self.isFull()):
            print("Disk Full")
            return
        if typ.lower()=='d':                                    #create dir entry
            self.createDir(name)
            return
        elif typ.lower()=='u':
            self.createFile(name)
            return
        return

    #Create directory block
    def createDir(self,name):
        if self.isFull():
            print("Disk full")
            return
        path,dirname=self.getPath(name)
        dirblk=self.getDirblk(path)
        newdirblk=self.nextFree()   #new directory block #
        searching=True
        while searching:
            for x, entry in enumerate(self.blocks[dirblk][4]):
                if entry[1]==name and entry[0]=='D':        #same name directory exists here!
                    print("Directory exists!")
                    searching = False
                    return
                elif entry[0]=='F':                         #find free entry
                    self.blocks[dirblk][4][x]=['D',dirname,newdirblk,0]
                    d=['F','',0,0]                    
                    ds=[d]*31                         
                    temp=[0,0,0,None,ds[:]]
                    self.blocks[newdirblk]=[0,0,0,'fill',ds[:]]
                    self.blocks[newdirblk][0]=dirblk                
                    self.freespace[newdirblk]=0
                    searching=False
                    break
            if self.blocks[dirblk][2] != 0 and searching:   #check next directory block
                dirblk=self.blocks[dirblk][2]
            elif searching:
                self.freespace[newdirblk]=0                 #need to create one
                if self.isFull():
                    print("Disk full")
                    return
                nextdirblk=self.nextFree()
                self.freespace[nextdirblk]=0
                self.blocks[dirblk][2]=nextdirblk           #set next blk to the new one
                prevblk=self.blocks[dirblk][0]
                #dirblk=nextdirblk                          #switch to the new one
                d=['F','',0,0]                              #build new one
                ds=[d]*31                         
                self.blocks[nextdirblk]=[prevblk,0,0,'fill',ds[:]]
                self.blocks[nextdirblk][4][0]=['D',dirname,newdirblk,0]
                #now build the new dir blk                
                d=['F','',0,0]                    
                ds=[d]*31                         
                temp=[0,0,0,None,ds[:]]
                self.blocks[newdirblk]=[0,0,0,'fill',ds[:]]
                self.blocks[newdirblk][0]=dirblk 
                searching=False
 
    #Create file block
    def createFile(self,name):
        if self.isFull():
            print("Disk full")
            return
        path,filename=self.getPath(name)                #split the path and filename
        dirblk=self.getDirblk(path)                     #get the correct directory file
        newblk=self.nextFree()                          #get next free block
        self.freespace[newblk]=0                        #update freespace
        self.blocks[newblk]=[0,0,[None]*504]            #create file block
        direntry=['U',filename,newblk,0]                #create a directory entry
        searching = True        
        while searching:
            for x, entry in enumerate(self.blocks[dirblk][4]):
                if entry[1]==filename:                  #file exists, zero it
                    self.freespace[newblk]=1            #free the new block created for this
                    self.blocks[dirblk][4][x][3]=0      #set the space to zero
                    searching=False
                    break
                elif entry[0]=='F':                     #found a free entry
                    self.blocks[dirblk][4][x]=direntry  #swap in new entry
                    searching=False
                    break
            if self.blocks[dirblk][2] != 0 and searching:#STILL searching, check next directory block
                dirblk=self.blocks[dirblk][2]
            elif searching:                             #STILL searching, no more blocks to check
                if self.isFull():
                    print("Disk full")
                    return
                nextdirblk=self.nextFree()
                self.freespace[nextdirblk]=0
                self.blocks[dirblk][2]=nextdirblk       #set next blk to the new one
                prevblk=self.blocks[dirblk][0]
                d=['F','',0,0]                          #build new one
                ds=[d]*31                         
                self.blocks[nextdirblk]=[prevblk,0,0,'fill',ds[:]]
                self.blocks[nextdirblk][4][0]=direntry
                searching=False                       


    #Open function
    def open(self,mode,name):
        if self.open_file[0]:
            print("File is already open")
            return
        path,filename=self.getPath(name)
        dirblk=self.getDirblk(path)
        files=None
        fileblk=None
        direntry=None
        end=0
        found=False
        searching=True
        while(searching):
            files=self.getFiles(dirblk)
            for ea in files:
                if ea[1][1]==filename:
                    found=True
                    searching=False
                    fileblk=ea[1][2]
                    direntry=ea[0]
                    self.file_blks[0]=fileblk   #filblk
                    self.file_blks[1]=ea[1][3]  #last byte
                    if mode.lower()=='o':
                        end=ea[1][3]
            if not found:
                dirblk=self.blocks[dirblk][2]
            if dirblk==0:
                searching=False
            
        self.open_file=[found,dirblk,direntry,fileblk,mode.upper(),end]#Open?/dirblk/direntry/fileblk/IOU Mode/byteptr
        if not found:
            print("not found")
            return
        #traverse the file blocks
        tblk=self.blocks[self.open_file[3]][1]
        self.file_blks[2].append(fileblk)
        while tblk > 0:
            self.file_blks[2].append(tblk)
            tblk=self.blocks[tblk][1]
        if mode.lower()=='o':
            self.open_file[5]+=((len(self.file_blks[2])-1)*504)

    #Close function
    def close(self):
        self.open_file=[False,0,0,0,'I',0]               #Reset the open_file flags
        self.file_blks=[0,0,[]]                          #Reset the file_blks: first/last size/list of blks

    #Delete function
    def delete(self,name):
        path,filename=self.getPath(name)
        dirblk=self.getDirblk(path)
        files=self.getFiles(dirblk)
        fileblk=None
        direntry=None
        
        for ea in files:
            if ea[1][1]==filename:
                fileblk=ea[1][2]
                direntry=ea[0]
        if not fileblk:
            print("not found")
            return
        more=True
        self.blocks[dirblk][4][direntry][0]='F'
        while(more):
            self.freespace[fileblk]=1
            if self.blocks[fileblk][1]==0:
                more=False
            else:
                fileblk=self.blocks[fileblk][1]

    #Read function        
    def read(self,n):
        if self.open_file[4]=='O' or not self.open_file[0]:         #check open
            print("File not open for read operations")
            return
        filesize=((len(self.file_blks[2])-1)*504)+self.file_blks[1] #total file size
        #numblks=int(filesize/504)                                   #total number of blocks
        n=int(n)                                                    #fix n
        data=""        
        eof=False                                                   #end of file flag
        dirblk=self.open_file[1]                                    #dir blk with this entry
        direntry=self.open_file[2]                                  #entry in the dir
        fileblk=self.open_file[3]                                   #this file block
        bptr=self.open_file[5]                                      #current byte pointer
        if bptr+n > filesize:
            eof=True
            n = filesize-bptr                                       #give a safe n
        tblk=self.file_blks[2][int((bptr-1)/504)]
        for op in range(n):                                         #safe n operations
            tptr=(bptr+op)%504                                      #
            if tptr==0 and (bptr+n)>504:                            #time to switch to the next block
                tblk=self.file_blks[2][int((bptr+op)/504)]           #next block
            data+=self.blocks[tblk][2][tptr]                        #read byte
        self.open_file[5]=bptr+n                                    #update the open_file bptr (bptr + safe n)
        if eof:
            data+='EOF'
        return data

    def write(self,n,data):
        if self.open_file[4]=='I' or not self.open_file[0]:         #check file open
            print("File not open for write operations")
            return
        n=int(n)                                                    #fix n
        dirblk=self.open_file[1]
        direntry=self.open_file[2]
        byte_ptr=self.open_file[5]                                  #set the byte pointer
        temp_ptr=byte_ptr%504                                       #in block pointer
        page_num=0                                                  #start at the first page
        current_blk=self.file_blks[2][page_num]                     #get the first blk in the file
        if(n<len(data)):
            data=data[:n]                                           #shrink data to n
        data=data.ljust(n)                                          #add padding to the data to size n

        for op in range(n):
            byte_ptr=self.open_file[5]
            temp_ptr=byte_ptr%504
            page_num = int(byte_ptr/504)                            #calculate the page_num
            if (len(self.file_blks[2])-1) < page_num:                
                if self.isFull():                                   #check disk full
                    print("Disk full")
                    return
                lastblk=self.file_blks[2][len(self.file_blks[2])-1] #get last block number
                newblk=self.nextFree()                              #get next block
                self.freespace[newblk]=0                            #update freespace
                self.blocks[lastblk][1]=newblk                      #set forward pointer
                self.blocks[newblk]=[lastblk,0,[None]*504]          #create file block
                self.file_blks[2].append(newblk)                    #add blk to page list
            current_blk=self.file_blks[2][page_num]                 #calculate the current_blk
            self.blocks[current_blk][2][temp_ptr]=data[op]          #write byte
            self.open_file[5]+=1                                    #update byte pointer
            self.updateSize(dirblk, direntry, (temp_ptr+1))         #update dir entry and size
            self.file_blks[1]=temp_ptr+1                            #update file_blk size

    #Seek function
    def seek(self,base,offset):
        if self.open_file[4].lower()=='O' or not self.open_file[0]:
            print("File not open for seek operations")
            return
        current=self.open_file[5]
        byte_ptr=0
        base=int(base)
        offset=int(offset)
        if base == -1:
            byte_ptr=offset
        if base == 0:
            byte_ptr=current+offset
        if base == 1:
            byte_ptr=((len(self.file_blks[2])-1)*504)+self.file_blks[1]
        self.open_file[5]=byte_ptr                #set the new file pointer

    #Returns True if the disk is full
    def isFull(self):
        if(self.nextFree()):
            return False
        else:
            return True

    #NextFree function
    def nextFree(self):                           #find next available block.. return False on full
        if 1 in self.freespace:
            return self.freespace.index(1)
        else:
            return False

    def isDirListFull(self,dirblk):
    #Return True if the Directory list is full
    #Pass in the block number of the directory to check
        if self.blocks[dirblk][1]:               #This dir has a child
            return True
        x=0
        for entry in self.blocks[dirblk][4]:
            if entry[0]=='F':
                x+=1
        return x==0

    def getDirblk(self,path):
        #pass in path WITHOUT filename
        #WITHOUT starting or trailing slashes
        #returns the block number to the directory file for this path
        fix = -1
        dirblk = 0                              #start in blk zero
        parts = path.split('/')                 #split the path into parts
        try:
            fix=parts.index("")
        except:
            fix=-1
        if fix>-1:
            parts.pop(fix)                      #fix leading slash..
        for ea in parts:                        #follow each part
            dirs=self.getDirs(dirblk)           #get dir listings
            for dir in dirs:
                if dir[1]==ea:                  #name==ea found the dir
                    dirblk=dir[2]               #update dirblk
        #dirblk should now have the dir blk number for the folder's dir file
        return dirblk

    def getFiles(self,dirblk):                  #return an array of files from this list [index,[file]]
        files=[]                                #return an array of directories from this list
        for x,entry in enumerate(self.blocks[dirblk][4]):
            if entry[0]=='U':
                f=[x,entry[:]]
                files.append(f)
        return files


    def getDirs(self,dirblk):
        dirs=[]                                 #return an array of directories from this list
        more=True
        while more:
            for entry in self.blocks[dirblk][4]:
                if entry[0]=='D':
                    dirs.append(entry)
            if self.blocks[dirblk][2] !=0:
                dirblk= self.blocks[dirblk][2]
            else:
                more = False        
        return dirs

    def getPath(self,name):
        #splits name into path,filename
        if '/' not in name:                     #it's just a filename
            return '',name
        ind=name.rfind('/')
        filename=name[(ind+1):]
        path=name[:ind]
        if name[0]=='/':                        #fix front slashes..
            path=path[1:]
        return path,filename

    def updateSize(self, dirBlk, pos, size):
        self.blocks[dirBlk][4][pos][3]=size
        
