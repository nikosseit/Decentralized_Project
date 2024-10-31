import hashlib
import math
import pandas as pd
import ipaddress

pd.options.display.max_rows = 9999

df = pd.read_csv('computer_scientists.csv',encoding= 'unicode_escape') #Dhmiourgia dataframe me vasei to csv poy exei Surname, #ofAwards
                                                               #kai education gia tous computer scientists.

csv_list = df[[df.columns[0],df.columns[1],df.columns[2]]].values.tolist()

class Node:
    def __init__(self, ip, port, id, k, prev = None): #Arxikopoihsh node stigmiotypoy me ip, prot, kai hashed id poy prokyptei apo ip:port
        self.ip = ip
        self.port = port
        self.id = id
        self.data = []
        self.prev = prev
        self.finger_table = [0]*k 

    def update_finger_table(self,ring,k): #Sinartisi poy kanei update to finger table toy komvoy xrhsimopoiontas gia kathe thesh thn find succesor sinartisi
        for i in range(k):
            table_id = self.id + 2**i 
            if table_id > 2**k: #An o arithmos einai megalyteros toy megethoys toy ring afairese to megethos gia na paraxthei to swsto apotelesma gia ton find_successor(p.x. An megethos 128 kai komvos 113 to 113 + 32(=2^5) = 17 kai oxi 145)
                table_id -= 2**k
            self.finger_table[i] = ring.find_successor(ring.start_node, table_id)

    def print_finger(self): #Sinartisi poy emfanizei to finger table enos komvoy
        print("Finger table of node: ", self.id)
        k = len(self.finger_table)
        for i in range(k):
            print("--Position: ", i," Node id: ", self.finger_table[i].id)

class Key: #Klash key poy afora antikeimena kleidiwn
    def __init__(self,key,awards,surname,id):
        self.key = key
        self.awards = awards 
        self.surname = surname
        self.id = id
        self.succ = None


class Chord:
    def __init__(self,k): #Arxikopoihsh toy ring chord me to k na einai to megethos se bit gia ta diathesima id apo to opoio prokyptei to 2^(k) megethos toy ring
        self.k = k
        self.size = 2 ** k
        self.start_node = None
        self.num_of_nodes = 0

    def join_node(self,ip,port): #Sinartisi gia thn eisagwgi komvwn sto ring
        self.num_of_nodes += 1
        id = self.hash_id(ip,port) #Paragwgi toy id mesw hash toy ip:port
        n = Node(ip,port,id,k) #Dhmiourgia toy komvou n

        if not self.start_node: #An den yparxei arxikos komvos sto ring tote o n ginetai o arxikos
            self.start_node = n
            n.finger_table[0] = n
            n.prev = n
        
        succ = self.find_successor(self.start_node, id) #Vres ton successor tou komvoy n

        prev_node = succ.prev #Stabilize tis times gia previous kai successor twn komvwn poy ephreazontai apo thn eisagwgh toy neoy
        n.finger_table[0] = succ
        n.prev = prev_node
        succ.prev = n
        prev_node.finger_table[0] = n
        
        n.update_finger_table(self,self.k) #Update to finger table toy neoy komvoy
        self.update_all_fingers() #Update ta ypoloipa finger tables

        for key in succ.data: #Gia kathe kleidi toy succ elegxe an prepei na metaferthei ston neo komvo
            if self.distance(key.id,n.id) <= self.distance(key.id,succ.id): 
                n.data.append(key)
                succ.data.remove(key)

    def find_successor(self, start, node_id): #Sinartisi poy vriskei ton successor enos komvoy 
        if self.start_node is None: #An to ring einai keno emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring!")
            return 
        curr = start
        while True:
            if curr.id == node_id: #An o komvos exei idio id me ton dwsmeno tote o komvos einai successor toy eautoy toy
                return curr
            if self.distance(curr.id, node_id) <= self.distance(curr.finger_table[0].id, node_id): #An h apostash toy komvoy apo ton curr einai mikroterh apo thn apostash apo ton successor toy curr tote epestrepse ton successor
                return curr.finger_table[0]
            i = 0
            next_node = curr.finger_table[-1]
            while i < self.k - 1: #Ypologise ton neo komvo gia na sygkrithei me ton dwsmeno mesa apo ena while loop poy elegxei thn apostash toy dwsmenoy me toys komvoys sto finger table toy curr
                if self.distance(curr.finger_table[i].id, node_id) < self.distance(curr.finger_table[i+1].id, node_id):
                    next_node = curr.finger_table[i]
                i += 1
            curr = next_node

    def leave_node(self,node):
        if self.start_node is None: #An to ring einai keno emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring for one to leave!")
            return 0
        if(node.finger_table[0] == node): #An o komvos einai o monadikos sto ring
            self.start_node = None
        else:
            succ = node.finger_table[0] #An den einai o monadikos anethese ton succ toy node ws successor toy prohgoymenoy kai ton predecessor toy epomenoy ws ton prev toy node
            pred = node.prev
            succ.prev = node.prev
            pred.finger_table[0] = succ

            for key in node.data: #Gia kathe kleidi toy komvoy prostese to ston succ kai diegrapse to apo ton komvo poy diagrafetai
                succ.data.append(key)
                node.data.remove(key)
            

            if self.start_node == node: #An o komvos htan entry point allaxe to me ton successor
                self.start_node = node.finger_table[0]
        
        node.id = 1000 #Megalo id gia prosomoiwsh toy oti o komvos feygei mias kai den ginetai na ginei kanoniko delete node
        self.update_all_fingers()
        return 1

    def update_all_fingers(self): #Sinartisi poy kanei update ta finger table kathe komvoy sto ring
        self.start_node.update_finger_table(self,self.k)
        curr = self.start_node.finger_table[0]
        while curr != self.start_node:
            curr.update_finger_table(self,self.k)
            curr = curr.finger_table[0]
        
    def print_prev(self): #Sinartisi poy emfanizei ton previous komvo gia kathe enan komvo sto ring
        if self.start_node is None:
            print("\nThere are no nodes in the ring!")
            return
        print("Start node: ",self.start_node.id, " Previous of start node: ",self.start_node.prev.id)
        curr = self.start_node.finger_table[0]
        while curr != self.start_node:
            x = str(curr.id)
            print("--Node: " + x + " Previous node: ",curr.prev.id)
            curr = curr.finger_table[0]

    def hash_id(self,ip,port): #Sinartisi poy pairnei ip, port ta enwnei se ena string ip:port, ta hasharei me sha1 kai paragei to id me thn xrhsh toy % 2^(k) sth hashed timh
        h_input = ip+':'+port
        h_input = h_input.encode('utf-8')
        id = int(hashlib.sha1(h_input).hexdigest(), 16) % 2 ** self.k
        return id
    
    def distance(self,n1,n2): #Sinartisi poy ypologizei thn apostash dyo komvwn sto ring 
        if n1 == n2:
            return 0
        if n1 < n2:
            return n2 - n1
        return self.size - n1 + n2
    
    def print_nodes(self): #Sinartisi poy emfanizei ta id olwn twn komvwn 
        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring!")
            return
        else:
            print("\nHere are the nodes that are part of the chord ring: ")
            print("Start node: ", self.start_node.id)
            succ = self.start_node.finger_table[0]
            while succ != self.start_node:
                print("Node id: ", succ.id)
                succ = succ.finger_table[0]
        

    def search_node(self,id): #Sinartisi poy anazhtei enan komvo mesw toy id toy kai ton epistrefei
        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring to search for!")
            return
        if self.start_node.id == id: #An o komvos einai o arxikos epestrepse ton
            print("\nNode found.")
            return self.start_node
        
        succ = self.start_node.finger_table[0] #Orise ws succ ton successor toy arxikoy
        while succ != self.start_node: #Oso o succ den einai o arxikos
            if succ.id == id: #An vrethike o komvos epestrepse ton
                print("\nNode found.")
                return succ
            succ = succ.finger_table[0] #Orise ws succ ton successor toy twrinoy komvoy
        
        print("\nNode you searched for is not in the ring!") #An den exei vrethei o komvos tote emfanise mhnyma lathoys

    def insert_key(self,key,awards,surname): #Sinartisi poy eisagei ena kleidi sto ring
        exists = 0
        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nCan not insert a key without a node in the ring!")
            return
        key = key.encode('utf-8')
        id = int(hashlib.sha1(key).hexdigest(), 16) % 2 ** self.k #Vres to id toy kleidioy hasharontas to key
        value = Key(key,awards,surname,id)

        succ = self.find_successor(self.start_node,id) #Vres ton komvo ston opoio prepei na antistoixei to kleidi
        
        value.succ = succ #Orise ws successor toy key ton komvo ston opoio antistoixei to kleidi
        if not succ.data: #An o komvos den exei alla kleidia prosthese to kleidi kai epestrepese epityxia 
            succ.data.append(value)
            return 1
        else:   #Alliws an o komvos exei kleidia elegxe mhpws to kleidi yparxei hdh
            for x in succ.data:
                if(x.id == value.id) & (x.surname == value.surname): #An yparxei to kleidi orise exists = 1
                    exists = 1

        if not exists: #An den yparxei to kleidi prosthese to kai epestrepese epityxia
            succ.data.append(value)
            return 1
        else: #Alliws emfanise mhnyma lathous
            print("\nKey already exists!")
            return 
        

    def lookup_key(self,start,key): #Sinartisi poy psaxnei kleidia me sygkekrimeno id
        found = 0
        key = key.encode('utf-8')
        id = int(hashlib.sha1(key).hexdigest(), 16) % 2 ** self.k

        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring so there are no keys to search for either.")
            return

        node = self.find_successor(start,id) #Vres ton successor toy kleidioy sto ring
        
        if node.data: #An yparxoyn kleidia ston successor elegxe an einai to id idio me ayto poy anazhtyome kai an einai emfanise to
            for x in node.data:
                if x.id == id:
                    print("--Key id: ", x.id, " Key value: ", x.key," Key awards: ", x.awards, " Key surname: ", x.surname)
                    found = 1
        else: #Alliws emfanise pws den yparxei to kleidia poy anazhtame
            print("\nKey ", key," does not exist or entered invalid input.")
            return
        
        if not found:
            print("\nKey ", key," does not exist.")
            return
        
    def update_key(self,start,key, awards, surname,old_a,old_s): #Sinartisi poy vrhskei ena kleidi kai to kanei update
        found = 0
        key = key.encode('utf-8')
        id = int(hashlib.sha1(key).hexdigest(), 16) % 2 ** self.k
 
        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring so there are no keys to update either.")
            return

        node = self.find_successor(start,id) #Vres ton successor toy kleidioy sto ring
        
        if node.data: #An exei kleidia o successor elegxe an kapoio einai ayto poy anazhtoyme
            for x in node.data: #An vrethike to kleidi me ths times poy dwsame enhmerwse to 
                if (x.id == id) & (x.awards == int(old_a)) & (x.surname == old_s):
                    if awards:
                        x.awards = awards
                    if surname:
                        x.surname = surname
                    found = 1
        else: #An den eixe kleidia o successor emfanise pws den yparxei to kleidi
            print("\nKey ", key," does not exist.")
            return
        
        if not found: #An den vrethike to kleidi 
            print("\nKey ", key," does not exist.")
            return
        else: #An egine epityxhs enhmerwsh
            print("\nKey was updated.")
            return

    def delete_key(self,start,key, awards, surname): #Sinartisi poy diagrafei ena sygkekrimeno kleidi
        found = 0
        key = key.encode('utf-8')
        id = int(hashlib.sha1(key).hexdigest(), 16) % 2 ** self.k

        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring so there are no keys to delete either.")
            return

        node = self.find_successor(start,id) #Vres successor toy kleidioy
        
        if node.data: #An exei kleidia o successor elegxe an kapoio einai ayto poy anazhtoyme
            for x in node.data:
                if (x.id == id) & (x.awards == int(awards)) & (x.surname == surname): #An vrethike to kleidi me ths times poy dwsame diegrapse to 
                    node.data.remove(x)
                    found = 1
        else: #An den eixe kleidia o successor emfanise pws den yparxei to kleidi
            print("\nKey ", key," does not exist.")
            return
        
        if not found: #An den vrethike to kleidi 
            print("\nKey ", key," does not exist.")
            return
        else: #An egine epityxhs diagrafh
            print("\nKey was removed.")
            return
    
    def range_search(self,start,key,min_number,max_number,min_letter,max_letter,s_list): #Sinartisi poy kanei range search gia kleidi vasei awards kai prwtoy grammatos onomatos kai epistrefei mia lista me ta kleidia poy throyn thn anazhthsh
        key = key.encode('utf-8')
        id = int(hashlib.sha1(key).hexdigest(), 16) % 2 ** self.k

        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring so there are no keys  to search for either.")
            return
        
        if min_number > max_number: #Allaxe toys arithmous gia na threitai to min ws elaxisto kai to max ws megisto se periptwsh poy einai anapoda
            temp = min_number
            min_number = max_number
            max_number = temp
        
        if min_letter > max_letter: #Allaxe ta grammata gia na threitai to min ws elaxisto kai to max ws megisto se periptwsh poy einai anapoda
            temp = min_letter
            min_letter = max_letter
            max_letter = temp
        
        node = self.find_successor(start,id) #Vres ton successor toy kleidioy sto ring

        if node.data: #An exei kleidia o successor
            for x in node.data:
                if(x.id == id) & (int(x.awards) >= min_number) & (int(x.awards) <= max_number) & (x.surname[0].lower() >= min_letter.lower()) & (x.surname[0].lower() <= max_letter.lower()): #An to kleidi threi to range search prosthese to sth lista apotelesmatwn
                    s_list.append(x)
        else: #An den exei kleidia o successor
            print("\nKey ", key," does not exist.")

    def print_keys(self): #Sinartisi poy emfanizei kathe komvo mazi me ta kleidia toy
        if self.start_node is None: #An den yparxei komvos sto ring emfanise mhnyma lathoys
            print("\nThere are no nodes in the ring so there are no keys either.")
            return
        print("\nHere are the keys that are part of each node: ")
        print("Start node: ", self.start_node.id)
        for key in self.start_node.data: #Gia kathe kleidi toy start node emfanise to
            print("--Key id: ", key.id, " Key value: ", key.key," Key awards: ", key.awards, " Key surname: ", key.surname)
        succ = self.start_node.finger_table[0] #Orise ws succ ton successor toy arxikoy komvoy
        while succ != self.start_node: #Oso o succ den einai o start komvos emfanise to id toy komvoy kai ta kleidia toy
            print("Node id: ", succ.id)
            for key in succ.data:
                print("--Key id: ", key.id, " Key value: ", key.key," Key awards: ", key.awards, " Key surname: ", key.surname)
            succ = succ.finger_table[0] #Orise ws succ ton epomeno komvo apo ton twrino

    def create_ring(self): #Sinartisi poy dhmiourgei 5 komvoys kai eisagei prokathorismena kleidia apo to arxeio .csv sto ring
        Flag = True
        self.join_node("1.1.1.1","1000")
        self.join_node("1.1.1.2","1000")
        self.join_node("2.1.1.2","1000")
        self.join_node("2.1.1.3","1000")
        self.join_node("4.1.1.2","1000")
        for x in csv_list: #Gia kathe grammh sto csv arxeio 
            self.insert_key(x[2],int(x[1]),x[0])

        print("\nChord ring was created succesfully!")
        return False
    
    def check_for_duplicate_node(self,ip,port): #Sinartisi poy elegxei an enas neos komvos me ip,port yparxei hdh sto ring kai epistrefei true an yparxei false an den yparxei
        id = self.hash_id(ip,port) #Paragwgi toy id mesw hash toy ip:port
        if self.start_node is None: #An den yparxei komvos sto ring den yparxoyn kai duplicates opote epestrepse false
            return False
        
        if self.start_node.id == id: #An o komvos einai idios me ton arxiko epestrepse true
            return True
    
        succ = self.start_node.finger_table[0] 
        while(succ != self.start_node): #Gia oso o succ den einai o arxikos komvos elegxe kathe fora ton epomeno komvo vasei twn finger tables
            if succ.id == id:
                return True
            succ = succ.finger_table[0]
        
        return False


def validate_ip(ip): #Sinartisi poy dexetai ws orisma ena string kai elegxei an einai IPv4 h IPv6 address
    try:
        ip_object = ipaddress.ip_address(ip) #An einai egkyro address epestrepse true
        return True
    except ValueError: #Alliws false
        return False
        
def validate_port(port): #Sinartisi poy dexetai ws orisma ena string kai elegxei an einai egkyro ws port value(Dhladh na einai arithmos apo to 0 ews to 65535)
    if port.isnumeric() and int(port) >= 0 and int(port) <= 65535:
        return True
    else:
        return False
    
def validate_alnum_spaces(text): #Sinartisi poy dexetai ws orisma ena string kai elegxei an einai alfarithmitiko kai me kena
    return all(c.isalnum() or c.isspace() for c in text)

def validate_alpha_with_spaces(text): #Sinartisi poy dexetai ws orisma ena string kai elegxei an apoteleitai mono apo xarakthres toy alfavhtoy kai me kena
    return all(c.isalpha() or c.isspace() for c in text) 




#####-----MAIN-----#####
    
k = 7 #Arxikopoihsh ring 
ring = Chord(7)
custom_ring_create=True #flag pou diasfalizei oti to create_ring sta choices tha ginei mono mia fora

while True:
    print("\nMenu:") #Menoy efarmoghs
    print("0. Create a ring with pre determined values of keys based on a list of computer scientists")
    print("1. Add a new node")
    print("2. Delete a node")
    print("3. Print nodes")
    print("4. Search node and print its finger table")
    print("5. Insert a key")
    print("6. Print keys")
    print("7. Lookup key")
    print("8. Update key")
    print("9. Delete key")
    print("10. Range query")
    print("11. Exit")

    choice = input("Enter your choice (0/1/2/3/4/5/6/7/8/9/10/11): \n").lower()
    
    if choice == "0":
        if custom_ring_create: 
            custom_ring_create = ring.create_ring()
        else:
            print("\nRing has already been created! ")
            
    elif choice == "1":
        new_ip = input("\nPlease enter the ip address of the new node(x.x.x.x format): ")
        new_port = input("\nPlease enter the port of the new node(dddd format): ")
        if validate_ip(new_ip) and validate_port(new_port) and not ring.check_for_duplicate_node(new_ip,new_port):
            ring.join_node(new_ip,new_port)
            print("\nNode joined the ring succesfully.")   
        elif ring.check_for_duplicate_node(new_ip,new_port):
            print("\nNode already exists in the ring.") 
        else:
            print("\nYou did not enter a correct ip or port number. Please try again.")

    elif choice == "2":
        ring.print_nodes()
        id = input("\nPlease enter the id of a node to delete(Positive integer): ")

        if not id.isnumeric():
            print("\nYou did not enter a correct node id to delete. Please try again.")
        else:
            node = ring.search_node(int(id))
            x = ring.leave_node(node)
            if x:
                print("\nNode deleted succesfully.")
            else:
                print("\nNode to delete was not found.")

    elif choice == "3":
        ring.print_nodes()

    elif choice == "4":
        ring.print_nodes()
        node_input = input("\nEnter a node id to search for(Positive integer): ")
        
        if node_input.isnumeric():
            n= ring.search_node(int(node_input))
            if n != None:
                n.print_finger()
            else:
                print("\nNode you searched is not in the ring and does not have a finger table to show!")
        else:
            print("\nYou did not enter a valid key to search for!")

    elif choice == "5":
        new_key = input("\nPlease enter the value of the new key: ")
        new_awards = input("\nPlease enter the number of awards of the new key(Positive integer): ") 
        new_surname = input("\nPlease enter the surname of the new key(Only letters): ")
        
        if new_key and new_surname and validate_alnum_spaces(new_key) and validate_alpha_with_spaces(new_surname) and new_awards.isnumeric():
            success = ring.insert_key(new_key,int(new_awards),new_surname)
            if success:
                print("\nKey inserted succesfully!")
            else:
                print("\nKey was not inserted.")
        else:
            print("You did not enter valid values for each of the key elemets!")

    elif choice == "6":
        ring.print_keys()

    elif choice == "7":
        search = input("\nPlease enter key value to search for: ")
        
        if search and validate_alnum_spaces(search):
            ring.lookup_key(ring.start_node,search)
        else:
            print("\nYou did not enter a valid key to search for!")

    elif choice == "8":
        update = input("\nPlease enter key value to update: ")
        old_awards = input("\nPlease enter old awards value to update(Positive integer): ")
        old_sname = input("\nPlease enter old surname value to update(Only letters): ")
        
        awards = input("\nPlease enter new awards value to update to(Positive integer or blank to not change): ") or None
        
        sname = input("\nPlease enter new surname to update to(Only letter or blank to not change): ") or None

        if sname and not validate_alpha_with_spaces(sname):
            sname = None
            print("\nNew name was not valid so it will not change.")
        if awards and not awards.isnumeric():
            awards = None
            print("\nNew awards value was not valid so it will not change.")
        
        if update and old_sname and validate_alnum_spaces(update) and validate_alpha_with_spaces(old_sname) and old_awards.isnumeric():
            ring.update_key(ring.start_node,update,awards,sname,old_awards,old_sname)
        else:
            print("\nYou did not enter a valid key, or valid awards number or a valid surname!")
    
    elif choice == "9":
        delete = input("\nPlease enter key value to delete: ") 
        old_awards = input("\nPlease enter awards value(Positive integer): ") 
        old_sname = input("\nPlease enter surname value(Only letters): ") 
         
        if delete and old_sname and validate_alnum_spaces(delete) and validate_alpha_with_spaces(old_sname) and old_awards.isnumeric():
            ring.delete_key(ring.start_node,delete,old_awards,old_sname)
        else:
            print("\nYou did not enter a valid key, or valid awards number or a valid surname!")

    elif choice == "10":
        key = input("\nPlease enter key value for the range search: ")
        min_a = input("\nPlease enter minimum awards value(Positive integer with blank for no limit): ") or "0"
        max_a = input("\nPlease enter maximum awards value(Positive integer with blank for no limit): ") or "10000"
        min_l = input("\nPlease enter minimum letter value(From A to Z with blank for no limit): ") or "A"
        max_l = input("\nPlease enter maximum letter value(From A to Z with blank for no limit): ") or "Z"
        
        search_list = []
        if validate_alnum_spaces(key) and min_a.isnumeric() and max_a.isnumeric() and validate_alpha_with_spaces(min_l) and validate_alpha_with_spaces(max_l):
            ring.range_search(ring.start_node,key,int(min_a),int(max_a),min_l,max_l,search_list)
            if search_list:
                for x in search_list:
                    print("--Key id: ", x.id, " Key value: ", x.key," Key awards: ", x.awards, " Key surname: ", x.surname)
            else:
                print("\nThere were no keys in that range!")
        else:
            print("\nYou did not enter a valid key!")

    elif choice == "11":
        print("\nExiting the program. Thank you!")
        exit()
    
    else:
        print("Invalid choice number. Please try again.")



