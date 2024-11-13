import serial
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime 
import matplotlib.pyplot as plt
import random

class MainUnit :

    def plotd(x,y,xl,yl,t,up,lb,l1,l2,l3):
        plt.plot(x,y,color='b',label=l1)
        if(up[0]!=0 and lb[0]!=0) :
            plt.plot(x,up,color='r',label=l2)
            plt.plot(x,lb,color='y',label=l3)
        plt.xlabel(xl)
        plt.ylabel(yl)
        plt.title(t)
        plt.grid(True)
        plt.legend()
        plt.show()


    def mapv(x):
        return (x-645) * (100-0) / (300-645) +0
    
    def mapt(x) :
        return 65
    
    def mapp(x) :
        return 2.22*((5*x/1023)-0.5)



    def exit() :
        obj.space(32)
        print("\033[1m                                  < ",end='')
        obj.sleep(1)
        print("THANX",end='')
        obj.sleep(1)
        print(" FOR",end='')
        obj.sleep(1)
        print(" USING",end='')
        obj.sleep(1)
        print(" >\033[0m")
        obj.space(15)
        obj.sleep(2)


    def analyser(s): #Analyse the recent data
        print()
        con=mysql.connector.connect(host="localhost",user="root",password="abhishek@1604",database="sensordata")
        cursor=con.cursor()
        current_date = datetime.now().date()
        query="select * from {0} WHERE date= %s".format(s)
        cursor.execute(query,(current_date,))
        res=cursor.fetchall()

        mois=0
        temp=0
        phv=0 

        m=[0]*1500
        t=[0]*1500
        p=[0]*1500
        
        times=[]
        mo=[]
        te=[]
        ph=[]

        if res :
            for i in res :
                l=list(i)
                times.append(str(l[1]))
                mo.append(obj.mapv(l[2]))
                te.append(obj.mapt(l[4]))
                ph.append(obj.mapp(l[3]))

                m[l[2]]+=1
                t[l[4]]+=1
                p[l[3]]+=1

            k=0
            for x in range(0,len(m)) : #moisture hashtable
                if(m[x]>k):
                    k=m[x]
                    mois=x
            k=0
            for y in range(0,len(t)) : #pH hashtable
                if(t[y]>k) :
                    k=t[y]
                    temp=y
            k=0
            for z in range(0,len(p)) : #temperature hashtable
                if(p[z]>k):
                    k=p[z]
                    phv=z
            
            mois=obj.mapv(mois)
            temp=obj.mapt(temp)
            phv=obj.mapp(phv)

            print("\033[1mAverage Moisture\033[0m   : {:.2f}%".format(mois))
            print("\033[1mAverage pH Value\033[0m   : {:.2f}".format(phv))
            print("\033[1mAverage Temperature\033[0m: {:.2f}°Fahrenheit".format(temp))

            print("pH Status : ",end='')
            if(phv>7.5 or phv<6.5) :
                if(phv>7.5):
                    print("\033[31m Higher Than Optimal ( {:.2f} units) \033[0m".format(phv-7.5))
                else :
                    print("\033[31mLower Than Optimal ( {:.2f} units)\033[0m".format(6.5-phv))
            else :
                print("\033[32mIn Optimal Range\033[0m")



            print("Temperature Status : ",end='')
            if(temp>75 or temp<50) :
                if(temp>75):
                    print("\033[31mHigher Than Optimal ( {:.2f} units)\033[0m".format(temp-75))
                elif(temp<50) :
                    print("\033[31mLower Than Optimal ( {:.2f} units)\033[0m".format(50-temp))
            else :
                print("\033[32mIn Optimal Range\033[0m")

            print("\033[1mPreferable Crops :\033[0m ")
            query=" select cropname from cropinfo where upperph<{0} and {0}<lowerph".format(phv)
            cursor.execute(query)
            res=cursor.fetchall()
            s=set()
            if res :
                for i in res :
                    s.add(i[0])
                for i in s :
                    print(i,end=',')
                print()
            else :
                print("No Crop Found !!")
            


            obj.sleep(2)
            obj.plotd(times,mo,"Time","Moisture %",str(current_date),[0]*len(times),[0]*len(times),"Moisture Value(%)","","")
            obj.plotd(times,te,"Time","Temperature Fahrenheit",str(current_date),[75]*len(times),[50]*len(times),"Temperature Value","Temp UpperBound","Temp LowerBound")
            obj.plotd(times,ph,"Time","pH Value",str(current_date),[7.5]*len(times),[6.5]*len(times),"pH Value","pH UpperBound","pH LowerBound")

            x=input("Do You Want TO Continue Y/N ? ").lower()
            if(x=='n') :
                obj.exit()
            else :
                obj.interface()
        else :
            print("NO RECORD FOUND !!")
        


    def connectionmaker(farm): #Establishes connection between the arduino and the SQL, pushes data into the SQL
            con=mysql.connector.connect(host="localhost",user="root",password="abhishek@1604",database="sensordata")
            cursor=con.cursor()
            port = 'COM5'  
            rate = 9600       
            ser = None 
            ser = serial.Serial(port,rate)
            i=0
            while(True) :
                    if ser.in_waiting > 0:
                        data = ser.readline().decode().strip()
                        moisture,ph,temperature=map(int, data.split(','))
                        query = "INSERT INTO {0} (date,time,moisture,ph,temp) VALUES (%s,%s,%s,%s,%s)".format(farm)
                        cursor.execute(query,(datetime.now().date(),datetime.now().time(),moisture,ph,temperature))
                        con.commit()
                        i+=1
                        if(i==100):
                            print("Data Collection Complete. ")
                            break
            if con.is_connected():
                cursor.close()
                con.close()
            if ser and ser.is_open:  
                ser.close()
            obj.analyser(farm) 




    def sleep(n): # Makes the system sleep for n-seconds
        time.sleep(n)




    def space(n) : # Useful for interface creations
        for i in range(n) : print(" ")




    def manager() : #Creates the initial starting animation,calles interface function
        obj.space(32)
        print("\033[1m                                  < ",end='')
        obj.sleep(1)
        print("SOIL",end='')
        obj.sleep(1)
        print(" QUALITY",end='')
        obj.sleep(1)
        print(" ANALYSIS ",end='')
        obj.sleep(1)
        print("SYSTEM",end='')
        obj.sleep(1)
        print(" >\033[0m")
        obj.space(15)
        obj.sleep(2)
        obj.interface()


    def interface(): # main interface that deals with everything
        s=""
        obj.space(32)
        print("                                                \033[1m < SOIL QUALITY ANALYSIS SYSTEM > \033[0m")
        obj.space(2)
        print("\033[1mAll The Farm Records -->\033[0m ")
        flag=obj.farms()
        obj.space(2)
        ch=input("\033[1mEnter Farm-Number to choose or 'n' to create new farm :\033[0m").lower()
        obj.space(1)

        if(ch[0]!='n' and len(flag)!=0) :
            s=flag[int(ch[0])-1]
        elif(ch[0]=='n'): 
            print("\033[1mName The New Farm-->\033[0m ",end='')
            s=input()
            con=mysql.connector.connect(host="localhost",user="root",password="abhishek@1604",database="sensordata")
            cursor=con.cursor()
            query="create table {0}(date DATE DEFAULT NULL ,time TIME DEFAULT NULL, moisture int,ph int,temp int)".format(s)
            cursor.execute(query)
        ch=input("\033[1m Enter 's' To Begin Analysis : \033[0m ").lower()
        if(ch=='s') :
            obj.connectionmaker(s)
        else : 
            obj.interface()




    def farms() : #Fetches agvvvvvvvvvvvvlfl the farms present in the MySQL database
        con=mysql.connector.connect(host="localhost",user="root",password="abhishek@1604",database="sensordata")
        cursor=con.cursor()
        query = "show tables"
        cursor.execute(query)
        count=0
        flag=[]
        j=cursor.fetchall()
        for i in j :
            
            if(i[0]!="cropinfo") :
                count+=1
                print("                       ",count,".",i[0])
                flag.append(i[0])
        if(count==0) :
            print("                       No Record !!")
        return flag

        
        




obj=MainUnit
obj.manager()
