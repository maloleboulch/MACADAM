#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import argparse
import sys
from collections import defaultdict
import statistics
from operator import itemgetter

########## arguments

#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-tax",dest="tax", help="taxonomy of interest. Carefull with upper case",default=None)
parser.add_argument("-func",dest="func", help="function of interest",default=None)
parser.add_argument("-cpd",dest="cpd", help="compound of interest",default=None)
parser.add_argument("-rxn",dest="rxn", help="reaction of interest",default=None)
parser.add_argument("-enz",dest="enz", help="enzyme of interest",default=None)
parser.add_argument("-rank",dest="rank", help="rank of interest if specified",default=None)
parser.add_argument("-min",dest="min", help="minimal score",default=0.0, type=float)
parser.add_argument("-max",dest="max", help="maximal score",default=1.0, type=float)
parser = parser.parse_args()

#Tax if for the taxonomy
#func is for a particular function
tax=parser.tax
func=parser.func
rank=parser.rank
MiniScore=parser.min
MaxScore=parser.max
MiniScore=float(MiniScore)
MaxScore=float(MaxScore)
cpd=parser.cpd
rxn=parser.rxn
enz=parser.enz


lGoodRank=["species","genus","family","order","class","phylum","superkingdom"]
RankofInterest=[]
if rank:
    rank=rank.split(",")
    for element in rank:
        element=element.strip()
        element=element.lower()
        if element in lGoodRank:
            RankofInterest.append(element)
        else:
            print ("Invalid rank. Set to All rank. Rank must be species,genus,family,order,class or phylum. Separator are comas. Check your input")
            sys.exit()
            #RankofInterest=["species","genus","family","order","class","phylum","superkingdom","no rank"]
else:
    RankofInterest=["all"]

lTemp=[]
if tax:
    tax=tax.split(",")
    for element in tax:
        element=element.strip()
        element=" ".join(element.split())
        lTemp.append(element)
tax=lTemp

lTemp=[]
if func:
    func=func.split(",")
    for item in func:
        item=item.strip()
        item=" ".join(item.split())
        item=item.lower()
        lTemp.append(item)
else:
    func=""

func=lTemp

######### function ###############

#Connection to the DB
def Connection_to_DB(db_file):
    #connect to the db and place the cursor
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def request_a_taxonomy(tax,dbToolsCursor,RankofInterest):
    sLikeoption="(name LIKE \"%"+"%\" OR name LIKE \"%".join(tax)+"%\")"
    # tax="\"%"+tax+"%\""
    lListofInputLine=[]
    if RankofInterest==['all']:
    #Find a taxonomy in the Taxonomy table and generate the lineage.
    #Check if tax exist in our database
        if len(ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+";"))>=1:
            lInputLines=ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+";")
            for line in lInputLines:
                lListofInputLine.append(line)
            if lListofInputLine:
                print (" ".join(tax)+": Exists in our Database")
                return lListofInputLine
        else:
            print (" / ".join(tax)+": Doesn't exists in our database")
            print ("You may consider check your input of the script. Separator are comas")
            print ("Stopping the script")
            lListofInputLine=False
            return lListofInputLine
    else:
        sRankoption="(taxonomicRank IS \""+"\" OR taxonomicRank IS \"".join(RankofInterest)+"\")"
        if len(ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+" AND "+sRankoption+";"))>=1:
            lInputLines=ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+" AND "+sRankoption+";")
            for line in lInputLines:
                lListofInputLine.append(line)
            if lListofInputLine:
                print (" ".join(tax)+" "+" ".join(RankofInterest)+": Exists in our Database")
                return lListofInputLine
        else:
            print (" / ".join(tax)+": Doesn't exists in our database with this rank ("+" / ".join(RankofInterest)+")")
            print ("You may consider check your input of the script. Separator are comas")
            lListofInputLine=False
            return lListofInputLine

def ExecuteCommand(conn,command):
    #print (command)
    conn.execute(command)
    rows = conn.fetchall()
    lOfLines=[]
    for row in rows:
        lOfLines.append(row)
    return lOfLines

def request_pathway_for_a_taxonomy(lLineageRank,MiniScore,MaxScore,func):
    count=0
    #Preprocess func
    sLikeoption="(hierarchy.pathwayName LIKE \"%"+"%\" OR hierarchy.pathwayName LIKE \"%".join(func)+"%\")"
    sLikeFaprotax="(pathwayName LIKE \"%"+"%\" OR pathwayName LIKE \"%".join(func)+"%\")"
    #Find the common ancestor in our database
    #lLineageRank=".".join(str(x) for x in list(reversed(lLineageRank)))+"."

    while count==0:
        if lLineageRank.endswith("NaN."):
            lLineageRank=lLineageRank[:-4]
        else:
            ListofPathway=ExecuteCommand(dbToolsCursor,"SELECT pathway.taxonomy ,pathway.ID, pathway.strainName, pathway.numberOfPGDBInSpecies, pathway.numberOfPathway, pathway.pathwayScore, pathway.pathwayFrequencyScore, pathway.reasonToKeep, hierarchy.pathwayName FROM pathway INNER JOIN hierarchy ON (pathway.pathwayFrameID=hierarchy.pathwayFrameID) WHERE pathwayScore BETWEEN "+str(MiniScore)+" AND "+str(MaxScore)+" AND taxonomy LIKE \""+str(lLineageRank)+"%\" AND "+sLikeoption+";")
            ListofFaprotax=ExecuteCommand(dbToolsCursor,"SELECT * FROM faprotax WHERE taxonomy LIKE \""+str(lLineageRank)+"%\" AND "+sLikeFaprotax+";")
            if ListofPathway and ListofFaprotax:
                count=1
                MatchPoint=lLineageRank.split(".")[-2]
                break
            elif ListofPathway:
                count=1
                MatchPoint=lLineageRank.split(".")[-2]
                break
            elif ListofFaprotax:
                count=1
                MatchPoint=lLineageRank.split(".")[-2]
                break
            elif lLineageRank=="2.":
                print ("Function doesn't exist or your score is too strict! Skip to next taxonomy")
                count=1
                MatchPoint=None
                ListofPathway=None
                ListofFaprotax=None
            else:
                lLineageRank=".".join(lLineageRank.split(".")[0:-1])
                lLineageRank=".".join(lLineageRank.split(".")[0:-1])+"."
    if ListofPathway and ListofFaprotax:
        return ListofPathway,ListofFaprotax,MatchPoint
    elif ListofPathway:
        ListofFaprotax=[]
        return ListofPathway,ListofFaprotax,MatchPoint
    elif ListofFaprotax:
        ListofPathway=[]
        return ListofPathway,ListofFaprotax,MatchPoint
    else:
        return ListofPathway,ListofFaprotax,MatchPoint
######### Script ################

#Connect the DB and put the cursor
dbTools=Connection_to_DB("./DatabaseTSV/PGM.db")
dbToolsCursor=dbTools.cursor()

##### Find metabolite,rxn and enz name and convert it to pathway.

lListofPWYCPD=[]
lListofCPD=[]
if cpd:
    cpd=cpd.split(",")
    for element in cpd:
        element=element.strip()
        element=element.lower()
        lListofCPD=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNCPD ON PWYRXN.RXN = RXNCPD.RXN INNER JOIN CPDName ON RXNCPD.CPD = CPDName.CPD WHERE CPDName.Name LIKE \"%"+element+"%\";")
    for element in lListofCPD:
        for item in element:
            lListofPWYCPD.append(item)

lListofPWYRXN=[]
lListofRXN=[]

if rxn:
    rxn=rxn.split(",")
    for element in rxn:
        element=element.strip()
        element=element.lower()
        lListofRXN=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNName ON PWYRXN.RXN = RXNName.RXN WHERE RXNName.Name LIKE \"%"+element+"%\";")
    for element in lListofRXN:
        for item in element:
            lListofPWYRXN.append(item)

lListofPWYENZ=[]
lListofENZ=[]
if enz:
    enz=enz.split(",")
    for element in enz:
        element=element.strip()
        element=element.lower()
        lListofENZ=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNENZ ON PWYRXN.RXN = RXNENZ.RXN INNER JOIN ENZName ON RXNENZ.ENZ = ENZName.ENZ WHERE ENZName.Name LIKE \"%"+element+"%\";")
    for element in lListofENZ:
        for item in element:
            lListofPWYENZ.append(item)
func=func+lListofCPD+lListofRXN+lListofENZ

print (func)

if tax :
    #request the taxIDs for a string
    lLineofInterest=request_a_taxonomy(tax,dbToolsCursor,RankofInterest)

    #Check if lLineofInterest is false to exit to the next loop

    if lLineofInterest:
        #Keep Only scientific name
        lTemp=[]
        for line in lLineofInterest:
            if line[2]=='scientific name':
                lTemp.append(line)
        lLineofInterest=lTemp

        setOfAllLineage=set()
        dTaxIDtoLineage={}
        for line in lLineofInterest:
            setOfAllLineage.add(line[5])
            dTaxIDtoLineage[line[0]]=line[5]

        dLineagetoPathway={}
        dLineagetoFaprotax={}
        dLineageToMatchingPoint={}

        for item in setOfAllLineage:
            ListofResults=request_pathway_for_a_taxonomy(item,MiniScore,MaxScore,func)
            if ListofResults[0] or ListofResults[1]:
                print ("Trouve!")
                dLineagetoPathway[item]=ListofResults[0]
                dLineagetoFaprotax[item]=ListofResults[1]
                dLineageToMatchingPoint[item]=ListofResults[2]
            else:
                print ("Nope")

        for key in dLineagetoPathway:
            if len(dLineagetoPathway[key])==0:
                ListofPathway=["None"]
        for key in dLineagetoFaprotax:
            if len(dLineagetoFaprotax[key])==0:
                ListofFaprotax=["None"]


        lAllPathway=[]
        lAllTaxIDMatching=[]
        lAllTaxID=[]
        lTaxonomyMatching=[]
        lTaxonomy=[]
        dTaxIDtoTaxonomy={}
        lAllPathwayFaprotax=[]
        with open("./"+"-".join(tax)+"."+"-".join(RankofInterest)+"."+"resultat.tsv","w")as outputfile:
            for key in dTaxIDtoLineage:
                if key!=742887:
                    outputfile.write("##TaxID:"+str(key)+"\n")
                    lAllTaxID.append(str(key))
                    dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(key)+"\" AND typeOfName IS \"scientific name\"")
                    taxonomy = dbToolsCursor.fetchone()
                    outputfile.write("##Taxonomy: "+str(taxonomy[0])+" "+str(taxonomy[1])+"\n")
                    lTaxonomy.append(str(taxonomy[0]))
                    dTaxIDtoTaxonomy[key]=taxonomy[0]
                    outputfile.write("##Matching Point of the Database: "+str(dLineageToMatchingPoint[dTaxIDtoLineage[key]])+"\n")
                    lAllTaxIDMatching.append(str(dLineageToMatchingPoint[dTaxIDtoLineage[key]]))
                    dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(dLineageToMatchingPoint[dTaxIDtoLineage[key]])+"\" AND typeOfName IS \"scientific name\"")
                    taxonomy = dbToolsCursor.fetchone()
                    outputfile.write("##Matching Point Taxonomy: "+str(taxonomy[0])+" "+str(taxonomy[1])+"\n")
                    lTaxonomyMatching.append(str(taxonomy[0]))
                    if dLineagetoPathway[dTaxIDtoLineage[key]]!=[]:
                        outputfile.write("\n#Metacyc:\n")
                        for item in dLineagetoPathway[dTaxIDtoLineage[key]]:
                            outputfile.write("\t".join(str(x) for x in item))
                            outputfile.write("\n")
                            lAllPathway.append([item,key])
                    if dLineagetoFaprotax[dTaxIDtoLineage[key]]!=[]:
                        outputfile.write("\n\n#Faprotax:\n")
                        for item in dLineagetoFaprotax[dTaxIDtoLineage[key]]:
                            dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(item[1])+"\" AND typeOfName IS \"scientific name\"")
                            taxonomy = dbToolsCursor.fetchone()
                            lAllPathwayFaprotax.append([item,key])
                            outputfile.write(str(item[0])+"\t"+str(taxonomy[0])+" "+str(taxonomy[1])+"\t"+str(item[2])+"\t")
                            outputfile.write("\n")
                    outputfile.write("\n")

        ### for metacyc pathway###
        if lAllPathway!=[]:
            dPathwaysInfo={}
            setOfPresentPathwayName=set()
            setOfPresentLineage=set()
            for item in lAllPathway:
                setOfPresentPathwayName.add(item[0][-1])
                setOfPresentLineage.add(item[0][0])
            dPathwaysInfo=dPathwaysInfo.fromkeys(setOfPresentPathwayName,None)
            iNumberofSpeciesMatch=len(setOfPresentLineage)

            #Store all needed information in the following dictionnary: dPathwaysInfo[pathway name]=[number of organism with this pathway,]
            for item in lAllPathway:
                if dPathwaysInfo[item[0][-1]]:
                    dPathwaysInfo[item[0][-1]][0]+=1
                    dPathwaysInfo[item[0][-1]][1].append(float(item[0][5]))
                    dPathwaysInfo[item[0][-1]][2].append(float(item[0][6]))
                    dPathwaysInfo[item[0][-1]][3].append(item[1])

                else:
                    dPathwaysInfo[item[0][-1]]=[1,[float(item[0][5])],[float(item[0][6])],[item[1]]]

            for item in dPathwaysInfo:
                dPathwaysInfo[item][1]=statistics.median(dPathwaysInfo[item][1])
                dPathwaysInfo[item][2]=statistics.median(dPathwaysInfo[item][2])
                dPathwaysInfo[item][3]=set(dPathwaysInfo[item][3])

            with open("./"+"-".join(tax)+"."+"-".join(RankofInterest)+"."+"compact.tsv","w")as outputfile:
                outputfile.write("##TaxID:"+", ".join(lAllTaxID)+"\n")
                outputfile.write("##Taxonomy: "+", ".join(lTaxonomy)+"\n")
                outputfile.write("##Matching Point of the Database: "+", ".join(lAllTaxIDMatching)+"\n")
                outputfile.write("##Matching Point Taxonomy: "+", ".join(lTaxonomyMatching)+"\n")
                outputfile.write("#Metacyc:\n")
                outputfile.write("#Pathway\tPresent in\tMedian of score\tMedian of frequency\tPresent in match\tHierarchy\n")
                ListofMetacyctowrite=[]
                for item in dPathwaysInfo:
                    dbToolsCursor.execute("SELECT PathwayHierarchy from hierarchy where pathwayName is \""+item+"\";")
                    hierarchy=dbToolsCursor.fetchall()
                    hierarchy=[i for sub in hierarchy for i in sub]
                    hierarchy="/".join(hierarchy)
                    hierarchy=hierarchy.replace("Pathways.","")
                    BeginningofLine=[item,str(dPathwaysInfo[item][0])+"/"+str(iNumberofSpeciesMatch),str(round(dPathwaysInfo[item][1],2)),str(round(dPathwaysInfo[item][2],2))]
                    lTemp=[]
                    for item in dPathwaysInfo[item][3]:
                        lTemp.append(dTaxIDtoTaxonomy[item])

                    EndofLine=[", ".join(lTemp),hierarchy+"\n"]
                    LinetoWrite=BeginningofLine+EndofLine
                    ListofMetacyctowrite.append(LinetoWrite)
                ListofMetacyctowrite=sorted(ListofMetacyctowrite,key=itemgetter(5))
                for item in ListofMetacyctowrite:
                    outputfile.write("\t".join(item))
                outputfile.write("\n\n")

        #### For Faprotax ####
        if lAllPathwayFaprotax!=[]:
            dPathwaysInfo={}
            setOfPresentPathwayName=set()
            setOfPresentLineage=set()
            for item in lAllPathwayFaprotax:
                setOfPresentPathwayName.add(item[0][-1])
                setOfPresentLineage.add(item[0][0])

            dPathwaysInfo=dPathwaysInfo.fromkeys(setOfPresentPathwayName,None)
            iNumberofSpeciesMatch=len(setOfPresentLineage)

            for item in lAllPathwayFaprotax:
                if dPathwaysInfo[item[0][-1]]:
                    dPathwaysInfo[item[0][-1]][0]+=1
                    dPathwaysInfo[item[0][-1]][1].append(item[1])
                else:
                    dPathwaysInfo[item[0][-1]]=[1,[item[1]]]

            with open("./"+"-".join(tax)+"."+"-".join(RankofInterest)+"."+"compact.tsv","a")as outputfile:
                outputfile.write("#Faprotax:\n")
                outputfile.write("#Pathway\tPresent in\n")

                for item in sorted(dPathwaysInfo):
                    outputfile.write(item+"\t"+str(round(dPathwaysInfo[item][0],2))+"/"+str(iNumberofSpeciesMatch)+"\t")
                    lTemp=[]
                    for item in dPathwaysInfo[item][1]:
                        lTemp.append(dTaxIDtoTaxonomy[item])
                    lTemp=list(set(lTemp))
                    outputfile.write(", ".join(lTemp)+"\n")
