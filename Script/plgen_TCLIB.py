# -*- coding: cp1252 -*-
#Stephen Friederichs
#CSV parts list -> TinyCAD MDB Library

#TODO - add code to remove illegal characters
#TODO - figure out how to keep the names from being visible in TinyCAD
#TODO - check price outputs - not showing up correctly, always '1'

#DONE - ha HA!  No more win32 crap!
import sys, string, csv, os.path,os,sqlite3

#testing
project_path = "." + "\\Libraries"
output_path = project_path + "\\TCLib"
CSV_path = project_path + "\\CSV\\parts_list.csv"
symbol_mdb_path = project_path + "\\Symbols\\symbols.mdb"
symbol_tclib_path = project_path + "\\Symbols\\symbols.TCLib"

lib_extension = ".TCLib"
#lib_extension = ".mdb"

#Characters not allowed in XML to be stripped
illegal_chars = '�'

#Column Definitions -parts list file structure 
library_desc = {'Name':1}

#Part description - required fields
part_desc = {'Markup':0,
             'Name':1,           #Part Name 
             'PPP':2,            #Parts/Package
             'Ref':3,            #Reference Designator
             'Description':6,    #Description
             'Symbol':4,
             'Package': 5}        #Symbol

desc_part = {0:'Markup',
             1:'Name',
             2:'PPP',
             3:'Ref',
             4:'Symbol',
             5:'Package',
             6:'Description'}

#const = win32com.client.constants
#daoEngine = win32com.client.Dispatch('DAO.DBEngine.36')
fields = {}
db_conn = None
dtbs=None

#This will be the database connection to the symbol library
symbol_db = None

#This is a dictionary that will containt information about what ID a symbol name has
symbol_id = {0:'None'}

#Needs to be set to something to avoid some exceptions, it just works better this way

def safe_quit(row,msg,db):
    global symbol_db
    
    print >>sys.stderr, "On row " + str(row) +" of " + CSV_path + ":\n"+str(msg)
    try:
        #db.Close()
        db.close()
    except Exception,msg:
        pass
    try:
        #symbol_db.Close()
        symbol_db.close()
    except Exception,msg:
        pass

    try:
        #symbol_db.Close()
        symbol_db.close()
    except Exception,msg:
        pass
    
    sys.exit(1)
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
       
    row_num = -1

    try:
        parts = csv.reader(file(CSV_path))
    except Exception:
        safe_quit(row_num,"Could not open CSV parts file " + CSV_path,None) 

    #Open Symbol Library
    try:
 #       symbol_db = daoEngine.OpenDatabase(symbol_mdb_path)
         symbol_db = sqlite3.connect(symbol_tclib_path)
    except Exception,msg:
        safe_quit(0,msg,None)
        

    for row in parts:

        row_num = row_num+1
        
        #Check for special cases
        
        try:
            if row[part_desc['Markup']] == 'header':                #Check for header information
                first_field_num = 99
                fields = {}
                fields_new = {}
                colnum = 0                                              
                for column in row:
                    if colnum == 0:                             #Ignore markup column
                        pass
                    elif colnum <= part_desc['Description']:    #Check required column names
                        try:
                            part_desc[column.strip()]
                        except Exception,msg:
                            safe_quit(row_num,"Header error: Column " + str(colnum) + " does not equal required column header of " + desc_part[colnum] +"!",dtbs)
                            
                    elif colnum > first_field_num and column:   #Header after required columns, if it exists, add it to fields
                        fields_new[colnum] = column.strip()     
                    elif not column:                            #Look for first blank row after required columns
                        first_field_num = colnum
                    else:
                        pass
                        
                    colnum=colnum+1
                fields = fields_new
                
                if first_field_num == 99:                       #No field marker found
                    safe_quit(row_num,"Markup error: No field marker found!\nReason: Do you have at least one blank column after the required columns?",dtbs)
                    
                continue
            elif row[part_desc['Markup']].lower() == 'library':       #New library marker
                                                                    #close out current library if it's open
                                                                    #and start a new one
                #close the database
                #Need a conditional to determine if the database is closed or open
                try:
                    #dtbs.Close()
                    dtbs.close()
                except Exception,msg:
                    pass

                #Reset PKEY variables and symbol ID table for new file
                NameID = 1
                SymbolID = 1
                SymbolID_PKey = 1
                AttributeID = 1
                symbol_id = {}
                
                #Generate new library file name
                library_file = output_path + "\\" + row[library_desc['Name']].strip() + lib_extension
                
                print "Starting new library: " + library_file

                #delete files with the same name in the output directory

                print "\tSearching for old library files....."
                if os.path.isfile(library_file):
                    print "\tFound old library file!"
                    try:
                        os.remove(library_file)
                    except Exception:
                        try:
                            safe_quit(row_num,"Unable to remove old library file: " + library_file + " !\n",dtbs)
                        except Exception,msg:
                            safe_quit(row_num,"Unable to remove old library file: " + library_file + " !\n",None)
                        
                    print "\tOld library file removed!"
                else:
                    print "\tNo old library file found"
                        
                #create the new MDB file
                try:
                    #dtbs=daoEngine.CreateDatabase(library_file,win32com.client.constants.dbLangGeneral)
                    dtbs=sqlite3.connect(library_file,isolation_level=None);
                except Exception:
                    safe_quit(row_num, "Creation of new database file (" + library_file + ") failed!\n",None)

                print "\tNew MDB library file created successfully!"        

                #create the tables within the new MDB file
                try:
                    #dtbs.Execute("CREATE TABLE Name (NameID long NOT NULL PRIMARY KEY,Name Text(128),SymbolID long,Type long,Reference Text(255),ppp long,Description Text(255),ShowName long,ShowRef long)")
                    #dtbs.Execute("CREATE TABLE Attribute (AttributeID long NOT NULL PRIMARY KEY, NameID long, AttName Text(64), AttValue Memo, ShowAtt long)")
                    #dtbs.Execute("CREATE TABLE Symbol (SymbolID long NOT NULL PRIMARY KEY, Data LongBinary,DrawRotate long, DefRotate long, Type long)")
                    #dtbs.Execute("CREATE TABLE Property (PropertyID long NOT NULL PRIMARY KEY, Name Text(64),'Value' Text(255))")
					
                    dtbs.execute("CREATE TABLE Name (NameID INTEGER PRIMARY KEY,Name TEXT,SymbolID INTEGER,Type INTEGER,Reference TEXT,ppp INTEGER,Description TEXT,ShowName INTEGER,ShowRef INTEGER, DefRotate INTEGER)")
                    dtbs.execute("CREATE TABLE Attribute (AttributeID INTEGER PRIMARY KEY, NameID INTEGER, AttName TEXT, AttValue TEXT, ShowAtt INTEGER)")
                    dtbs.execute("CREATE TABLE Symbol (SymbolID INTEGER PRIMARY KEY, Data TEXT)")
                    dtbs.execute("CREATE INDEX [idx_NameID] ON [Attribute] ( [NameID] )")

                except Exception,msg:
                    safe_quit(row_num,"Create tables in file " + library_file + " failed!",dtbs)
                    
                print "\tTables created successfully!\n"

                #continue to the next row
                continue 

            elif row[part_desc['Markup']] == 'end':           #end of file
                break
            elif row[part_desc['Markup']] == '':              #Blank row
                pass

            elif row[part_desc['Markup']].lower() == 'part':   #Regular part 

                if row[part_desc['Symbol']] == '':            #Non-schematic part
                    print"\t\t\tIgnoring non-schematic part " + row[part_desc['Name']] #+ " on row " +str(row_num)
                    continue
                
                symbol_name = row[part_desc['Symbol']].strip()
              
                
                try:
                    #If the symbol has already been added to the library then it will be in this dictionary
                    #and this will return its symbol ID for the new part record
                    
                    SymbolID = symbol_id[symbol_name]
                    
                except Exception, msg:
                    
                    #If not, then we need to find the symbol in the symbol library and insert it into the new
                    #library, create a SymbolID for it and pass that SymbolID back
                    
                    #Symbol table
                    #SymbolID - primary key for symbol table
                    #Data - symbol data
                    #DrawRotate - long angle to rotate the drawing
                    #DefRotate - long ???
                    #Type - long ???

                    #Correctly inserting the BLOB for the symbol
                    #the buffer command does the magic
                    #You can't just put the symbol into the query up there because buffers and strings
                    #don't mix, so you find the record you just inserted then update it
                    #with apparently an entirely different set of commands.
                    
                    sqlQuery = "SELECT SymbolID FROM Name WHERE Name = \'" + symbol_name +"\'"
                    #print sqlQuery
                    
                    try:
                        rsp = symbol_db.execute(sqlQuery)
                    except Exception, msg:
                        safe_quit(row_num,"Error: Unable to execute SQL query on database " + symbol_tclib_path + " of: " + sqlQuery +"\nReason: Unknown!",dtbs)


                    
                    #Should select all and insert all but SymbolID
                    #SymbolID should be unique to this library file and is based on SymbolID_PKey variable
                    #row = rsp.next()
                    #Field order is: SymbolID, Data, DrawRotate, DefRotate, Type

                    try:
                        result = rsp.next()
                        #print result
                        sqlQuery = "SELECT * FROM Symbol WHERE SymbolID = " + str(result[0])
                        #print sqlQuery
                        rsp = symbol_db.execute(sqlQuery)
                        result = rsp.next()
                    except Exception,msg:
                        print "\t\t\tError: No symbol present for " + symbol_name
                        continue
                    
                    symbol = str(result[1]).strip()
                    symbol = sqlite3.Binary(symbol)
                    ##symbol = buffer(symbol)
                    #print symbol
                    
                    try:
                        sqlQuery = "INSERT INTO Symbol VALUES (" + str(SymbolID_PKey) + ",?)"# + sqlite3.Binary(symbol)+"\")" #+"," + str(result[3]) +"," + str(result[4]) + ")"
                    except Exception,msg:
                        safe_quit(row_num,"Markup Error! Part before library!\n" +str(msg),None)
                        #print sqlQuery

                    try:
                        #dtbs.Execute(sqlQuery)
                        dtbs.execute(sqlQuery,(symbol,) )
                    except Exception,msg:
                        safe_quit(row_num,"Unable to execute query: " + sqlQuery +"\nError: " + str(msg) +"\nReason: Unknown",dtbs)

#                    sqlQuery = "SELECT * FROM Symbol WHERE SymbolID = " + str(SymbolID_PKey)
#                    #print sqlQuery

#                    try:
#                        #rsp = dtbs.OpenRecordset(sqlQuery)
#                        rsp = dtbs.execute(sqlQuery)
#                    except Exception, msg:
#                            safe_quit(row_num,"Error: Unable to execute SQL query on database " + library_file + " of: " + sqlQuery +"\nReason: Is a library open?",dtbs)
#                    try:
                            
#                        #rsp.Edit()
#                        rsp.edit()
#                    except Exception,msg:
#                        safe_quit(0,"Edit symbol field failed! " + str(msg),dtbs)
#
#                    try:
#                        rsp.Fields[1].Value = buffer(symbol) 
#                    except Exception,msg:
#                        safe_quit(0,"Unable to set new symbol data! " + str(msg),dtbs)
#
                    try:
                        #rsp.Update()
#                        rsp.update()
                        SymbolID = SymbolID_PKey #Set the symbol ID for this part to the newly inserted symbol
                        
                        symbol_id[symbol_name] = SymbolID #Add the new symbol to the dictionary
                        SymbolID_PKey = SymbolID_PKey+1 #and increment the PKey for the next symbol
                    except Exception,msg:
                        safe_quit(0,"Unable to update symbol field for symbol " + symbol_name + "\n" + str(msg),dtbs)

                    print "\t\tNew symbol: " + symbol_name + " added to library as symbol #" +str(SymbolID_PKey-1)

                #Insert the part into Name table
                    
                #Table Name contains fields:
                #NameID - UID long
                #Name - Text(128)
                #SymbolID - symbol ID from symbol table - long
                #Type - ?? long?
                #Reference - Text(255)
                #ppp - parts/package long
                #Description
                #ShowName - long
                #ShowRef - long
                
                sqlQuery = "INSERT INTO Name VALUES (" + str(NameID) + ",'" + row[part_desc['Name']] + "'," + str(SymbolID) + ",0,'" + row[part_desc['Ref']] + "'," + row[part_desc['PPP']] + ",'" + row[part_desc['Description']] + "',0,0,0)"
                #print sqlQuery
                
                try:
                    #dtbs.Execute(sqlQuery)
                    dtbs.execute(sqlQuery)
                except Exception,msg:
                    safe_quit(row_num,"Unable to execute query: " + sqlQuery +"\nError: " + str(msg) +"\nReason: Is a library open?",dtbs)

                #Table Attribute
                #AttributeID - long UID
                #NameID - long UID from Name table
                #AttName - text(64) attribute name
                #Attvalue - text/memo - attribute value
                #ShowAtt - long - show attribute or not

                #TODO - insert package - it's an attribute but it seems a necessary one
                sqlQuery = "INSERT INTO Attribute VALUES (" +str(AttributeID) + "," +str(NameID) +",'Package','" +row[part_desc['Package']]+"',1)"
                AttributeID = AttributeID + 1
                #print sqlQuery
                
                try:            
                    #dtbs.Execute(sqlQuery)
                    dtbs.execute(sqlQuery)
                except Exception,msg:
                    safe_quit(row_num,"Header error: Undefined field information!\nReason: Is there at least one header row in the file? Is a library open?",dtbs)
                    
                #loop through attributes for each part 
                try:
                    for column,field in fields.iteritems(): #error occurs here - list index out of range for row - solution: exception catching
                        try:
                            if( not row[column]):
                                row[column] = ".."
                            sqlQuery = "INSERT INTO Attribute VALUES (" +str(AttributeID) + "," +str(NameID) +",'" + fields[column] +"','" +row[column]+"',1)"
                        except Exception,msg:
                            sqlQuery = "INSERT INTO Attribute VALUES (" +str(AttributeID) + "," +str(NameID) +",'" + fields[column] +"','..',1)"

                        AttributeID = AttributeID + 1
                        #print sqlQuery
                        

                        try:
                            #dtbs.Execute(sqlQuery)
                            dtbs.execute(sqlQuery)
                        except Exception,msg:
                            safe_quit(row_num,"Error: Unable to execute SQL query on database " + library_file + " of: " + sqlQuery +"\nReason: Is a library open?",dtbs)
                            
                        continue
                except Exception,msg:
                    print "On line " + str(row_num) + " WARNING:  No header information present!  Relying on built-in format rules!  No part attributes will be included!"
                
                NameID = NameID + 1 #Update PKey for Name, but not Symbol (it's handled above)
                print "\t\tAdded part: " + row[part_desc['Name']] 
                continue

            else:
                pass
        except IndexError: #I forget what this is fixing
            pass   

    #dtbs.Close()
    #symbol_db.Close()
    dtbs.close()
    symbol_db.close()
    os.system('pause');
    return


if __name__=="__main__":
    try:
        main()
    except SystemExit:
        print "A fatal error ocurred"


	
        

        
