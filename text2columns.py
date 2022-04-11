def main():
    
    columns = 4
    n = 1
    origineel = open(r"testtxt2col.txt")
    regel= ''
    zin=''
    #print (origineel)

   

    #xxxx = origineel.readlines()
    for zin in origineel:
        #print (zin)
        
        if n % columns != 0:
            www = zin.rstrip()
            regel = regel + "'" +  www + "'" + ","
        else:
            www = zin.rstrip()
            regel = regel + "'" +  www + "'\n" 
        n=n+1
        

    print (regel)
    #regel = ""
    #print ("xxxxxxxxxxxxxxxxxxxxx")
    #print (regel)



    #File_object.write(str1)
    origineel.close()

    file1 = open("myfile.txt","w")#write mode 
    file1.write(regel) 
    file1.close() 


main()