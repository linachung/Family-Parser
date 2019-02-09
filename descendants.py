"""

Lina Chung
Python Program Assignment 2
CPSC 3400 - Winter Quarter


GEDCOM parser design

Create empty dictionaries of individuals and families
Ask user for a file name and open the gedcom file
Read a line
Skip lines until a FAM or INDI tag is found
    Call functions to process those two types
Print descendant chart when all lines are processed

Processing an Individual
Get pointer string
Make dictionary entry for pointer with ref to Person object
Find name tag and identify parts (surname, given names, suffix)
Find FAMS and FAMC tags; store FAM references for later linkage
Skip other lines

Processing a family
Get pointer string
Make dictionary entry for pointer with ref to Family object
Find HUSB WIFE and CHIL tags
    Add included pointer to Family object
    [Not implemented ] Check for matching references in referenced Person object
        Note conflicting info if found.
Skip other lines

Print info from the collect of Person objects
Read in a person number
Print pedigree chart

"""


#-----------------------------------------------------------------------
class Event():
    # Stores info about a event
    # Created when an event key (DEAT, BIRT, MARR) is processed
    
    def __init__(self, ref):
        # Initializes new Event object, storing char (ref)
        self._event = ref
        self._date = None
        self._place = None
                    
    def addDate(self, dateRef):
        self._date = dateRef

    def addPlace(self, placeRef):
        self._place = placeRef

    def __str__(self):
        eventS = self._event
        if self._date:
            eventS = ' ' + eventS + ' ' + self._date
        if self._place:
            eventS= ' ' + eventS + ' ' + self._place.replace(',','')
        return eventS
        
class Person():
    # Stores info about a single person
    # Created when an Individual (INDI) GEDCOM record is processed.
    #-------------------------------------------------------------------

    def __init__(self,ref):
        # Initializes a new Person object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._asChild = None
        self._asSpouse = []  # use a list to handle multiple families
        self._events = [] # list of events
                
    def addName(self, nameString):
        # Extracts name parts from nameString and stores them
        names = line[6:].split('/')  #surname is surrounded by slashes
        self._given = names[0].strip()
        self._surname = names[1]
        self._suffix = names[2].strip()

    def name(self):
        if self._asChild: # make sure value is not None
            childString = ' asChild: ' + self._asChild
        else: childString = ''
        
        if self._asSpouse != []: # make sure _asSpouse list is not empty
            spouseString = ' asSpouse: ' + str(self._asSpouse)
        else: spouseString = ''
        return self._given + ' ' + self._surname.upper()\
               + ' ' + self._suffix
    
    def addEvent(self, event):
        # Adds event object to events list
        self._events += [event]
        
    def addIsSpouse(self, famRef):
        # Adds the string (famRef) indicating family in which this person
        # is a spouse, to list of any other such families
        self._asSpouse += [famRef]
        
    def addIsChild(self, famRef):
        # Stores the string (famRef) indicating family in which this person
        # is a child
        self._asChild = famRef

    def printDescendants(self, prefix=''):
        # print info for this person and then call method in Family
        print(prefix + self.__str__())
        # recursion stops when self is not a spouse
        for family in self._asSpouse:
            families[family].printFamily(self._id,prefix)

    def isDescendant(self, personID):
        flag = False
        if self._id == personID:
            return True
        for family in self._asSpouse:
                flag = families[family].checkDesecendant(personID)
                if flag:
                    return flag
        return flag
    
    def printAncestors(self, ie = '', height = 0):
        print (space + str(n) + '  ' + self.__str__())
        if self._asChild:
            try:
                # check if father exists
                persons[self.get_father()].printAncestors(ie + '\t' + height+1)
            except KeyError: pass
            print(pre + str(height) + ' ' + self.__str__())
            try: 
                #check if mother exists
                persons[self.get_mother()].printAncestors(height+1)
            except KeyError: pass
        else:
            print(pre + str(height) + ' ' + self.__str__())

    def checkLevel(self, level):
        cArray = []
        if level == 0:#correct level
            return [self.__str__()]
        else:
            for fam in self._asSpouse:
                for child in families[fam]._children:
                    cArray += persons[child].descendantsAtLevel(level-1)
        return cArray

    def lookCousins(self, count, level):
        cArray = []
        # Check grandparents level
        if (count == 0):
            sib = self.siblings()
            for sib in self.siblings():
                cArray += persons[sib].descendantsAtLevel(level)
                #print('\n',self.name(), '\n', c, '\n')        
        if self._asChild:
            cArray += persons[self.get_father()].findCousins(count-1, level+1)
            cArray += persons[self.get_mother()].findCousins(count-1, level+1)
        return cArray

    def printCousins(self, count = 0, level = 0):
        if count == 1:
            print("First cousins for",self.name())
        elif count == 2:
            print("Second cousins for",self.name())
        elif count == 3:
            print("Third cousins for",self.name())
        elif count == 4:
            print("Fourth cousins for",self.name())
        else:
            print(count, "level cousins for",self.name())
        cousins = self.findCousins(n, level)
        if cousins == []:
            print ('\t No cousins')
        else:
            for cousin in cousins:
                print ('\t', cousin)
            
    def __str__(self):
        if self._asChild: # make sure value is not None
            childString = ' asChild: ' + self._asChild
        else: childString = ''
        
        if self._asSpouse != []: # make sure _asSpouse list is not empty
            spouseString = ' asSpouse: ' + str(self._asSpouse)
        else: spouseString = ''

        if self._events != []:
            eventString = ' '
            for event in self._events:
                eventString += str(event) + ', '
            eventString = eventString[:-2]
        else:
            eventString = ' '

        return self._given + ' ' + self._surname.upper()\
               + ' ' + self._suffix + eventString#\
#               + childString + spouseString
                    
    def get_mother(self):
        if self._asChild:
            if families[self._asChild]._wife:
                return families[self._asChild]._wife
    
    def get_father(self):
        if self._asChild:
            if families[self._asChild]._husband:
                return families[self._asChild]._husband

    def get_sibs(self):
        siblings = []
        if self._asChild:
            for child in families[self._asChild]._children:
                if child != self._id:
                    siblings += [child]
        return siblings
 
#-----------------------------------------------------------------------
                    
class Family():
    # Stores info about a family
    # Created when an Family (FAM) GEDCOM record is processed.
    #-------------------------------------------------------------------

    def __init__(self, ref):
        # Initializes a new Family object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._husband = None
        self._wife = None
        self._children = []
        self._events = [] #list of Event objects

    def checkDesecendant(self, personID):
        found = False
        for child in self._children:
            found = persons[child].isDescendant(personID)
            if found:
                return found
        return found
    
    def addHusband(self, personRef):
        # Stores the string (personRef) indicating the husband in this family
        self._husband = personRef

    def addWife(self, personRef):
        # Stores the string (personRef) indicating the wife in this family
        self._wife = personRef

    def addChild(self, personRef):
        # Adds the string (personRef) indicating a new child to the list
        self._children += [personRef]
        
    def addEvent(self, event):
        self._events += [event]
        
    def printFamily(self, firstSpouse, prefix):
        # Used by printDecendants in Person to print spouse
        # and recursively invole printDescendants on children
        if prefix != '': prefix = prefix[:-2]+'  '
        if self._husband == firstSpouse:
            if self._wife:  # make sure value is not None
                print(prefix+ '+' +str(persons[self._wife]))
        else:
            if self._husband:  # make sure value is not None
                print(prefix+ '+' +str(persons[self._husband]))
        for child in self._children:
             persons[child].printDescendants(prefix+'|--')
        
    def __str__(self):
        if self._husband: # make sure value is not None
            husbString = ' Husband: ' + self._husband
        else: husbString = ''

        if self._wife: # make sure value is not None
            wifeString = ' Wife: ' + self._wife
        else: wifeString = ''

        if self._children != []: childrenString = ' Children: ' + str(self._children)
        else: childrenString = ''

        if self._events != []:
            eventString = ' '
            for e in self._events:
                eventString += str(e)
        else: eventString = ''

        return husbString + wifeString + childrenString + eventString


#-----------------------------------------------------------------------
 
def getPointer(line):
    # A helper function used in multiple places in the next two functions
    # Depends on the syntax of pointers in certain GEDCOM elements
    # Returns the string of the pointer without surrounding '@'s or trailing
    return line[8:].split('@')[0]

def processPerson(newPerson):
    global line
    line = f.readline()
    while line[0] != '0': # process all lines until next 0-level
        tag = line[2:6]  # substring where tags are found in 0-level elements
        if tag == 'NAME':
            newPerson.addName(line[7:])
        elif tag == 'FAMS':
            newPerson.addIsSpouse(getPointer(line))
        elif tag == 'FAMC':
            newPerson.addIsChild(getPointer(line))
        ## add code here to look for other fields
        elif tag == 'BIRT':
            event = processEvent('n:')
            newPerson.addEvent(event)
            continue
        elif tag == 'DEAT':
            event = processEvent('d:')
            newPerson.addEvent(event)
            continue
        # read to go to next line
        line = f.readline()
    
def processFamily(newFamily):
    global line
    line = f.readline()
    while line[0] != '0':  # process all lines until next 0-level
        tag = line[2:6]
        if tag == 'HUSB':
            newFamily.addHusband(getPointer(line))
        elif tag == 'WIFE':
            newFamily.addWife(getPointer(line))
        elif tag == 'CHIL':
            newFamily.addChild(getPointer(line))
        ## add code here to look for other fields 
        elif tag == 'MARR':
            newFamily.addEvent(processEvent('m:'))
            continue
        # read to go to next line
        line = f.readline()

def processEvent(e):
    global line
    event = Event(e)
    line = f.readline()
    tag = line[2:6]
    while line[0] != '1':
        if tag == "DATE":
            event.addDate(line[7:].strip('\n'))
        if tag == "PLAC":
            event.addPlace(line[7:].strip('\n'))
        line = f.readline()
        tag = line[2:6]
    return event

## Main program starts here

persons = {}  # to save references to all of the Person objects
families = {} # to save references to all of the Family objects

#filename = "Kennedy.ged"  # Set a default name for the file to be processed

### Uncomment the next line to make the program interactive
filename = input("Type the name of the GEDCOM file:")

f = open (filename)
line = f.readline()
while line != '':  # end loop when file is empty
    fields = line.strip().split(' ')
    # print(fields)
    if line[0] == '0' and len(fields) > 2:
        # print(fields)
        if (fields[2] == "INDI"): 
            ref = fields[1].strip('@')
            persons[ref] = Person(ref)  ## store ref to new Person
            processPerson(persons[ref])
        elif (fields[2] == "FAM"):
            ref = fields[1].strip('@')
            families[ref] = Family(ref) ## store ref to new Family
            processFamily(families[ref])      
        else:    # 0-level line, but not of interest -- skip it
            line = f.readline()
    else:    # skip lines until next candidate 0-level line
        line = f.readline()

# Optionally print out all information stored about individuals
for ref in sorted(persons.keys()):
    print(ref+':', persons[ref])

# Optionally print out all information stored about families
for ref in sorted(families.keys()):
    print(ref+':', families[ref])

##person = "I46"  # Default selection to work with Kennedy.ged file
### Uncomment the next line to make the program interactive

#person = 'I81'#input("Enter person ID for descendants chart:")
#persons['I1'].printDescendants()

# GED test import:

import GEDtest
GEDtest.runtests(persons,families)






