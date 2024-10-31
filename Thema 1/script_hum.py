import re
import csv

f = open("hum.txt",'r')
headers_list = [] #Create lists for the csv file to be created
rows_list = []
headers_list.append("Date")
headers_list.append("Value")
lines = f.readlines() #Read line of txt file
for line in lines:
    line = re.sub('[{""}]','',line) #Erase from the line the following characters: ", {, }
    entry = line.partition(', ')[0] #Keep as entry the line until the character comma
    rest = line.partition(', ')[2] #Keep everything after the comma as rest
    lastchar = entry[-1] #Get last character of entry


    while lastchar != "\n": #Until the last character of entry is the last character of the line that was read from the txt
        row = []
        remains = entry.partition('T') #Seperate the date value of each entry from the date,time,temperature\humidity struct
        date = remains[0]
        temp = remains[2].partition(': ') #Seperate the time and temperature\humidity values that remain
        value = temp[2]
        
        
        row.append(date) #Make a row of the date and value to be added to the csv rows list
        row.append(value)
        
        entry = rest #Make the entry as the next one in line after comma
        rest_line = entry.partition(', ')
        entry = rest_line[0]
        rest = rest_line[2]
        lastchar = entry[-1]
        
        if(lastchar == "\n"): #If the entry is the last one calculate the date time and temperature once for it because the while won't execute
            rows_list.append(row)
            row = []
            entry = entry.replace("\n","")
            remains = entry.partition('T')
            date = remains[0]
            temp = remains[2].partition(': ')
            value = temp[2]
            
            row.append(date) #Make a row of the date and value to be added to the csv rows list
            row.append(value)

        rows_list.append(row)
    
file_name = "hum.csv" #Name of csv file to be created

with open(file_name, 'w', newline='') as csvfile:  #Open the csv file with write priveleges

    csvwriter = csv.writer(csvfile)  #Make a writer instance
                 
    csvwriter.writerow(headers_list) #Write the headers to the csv file
                
    csvwriter.writerows(rows_list) #Write all rows to the csv
