#!/usr/bin/env python

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF, RDF

g = Graph()
g.parse("semantic_map4Simple.owl")

#print len(g)

chair = URIRef("http://www.semanticweb.org/ontologies/2016/1/semantic_mapping_domain_model#Chair")

table = URIRef("http://www.semanticweb.org/ontologies/2016/1/semantic_mapping_domain_model#Table")

lexicalRef = URIRef("http://www.semanticweb.org/ontologies/2016/1/semantic_mapping_domain_model#lexicalReference")


numOfChairs = 0
numOfTables = 0

for subj, pred, obj in g:
	#print("\n New object\n")
	print((subj,pred,obj))
 	if (subj, pred, obj) not in g:
		raise Exception("Iterator / Container Protocols are Broken!!")

print("\n\nChairs:\n\n")

# Find Triples in which an instance of the type Chair is defined
for chairs in g.subjects(RDF.type,chair):
	print("Found a Chair\n"+ chairs +"\n\n")
	numOfChairs += 1
	
	# Search all predicates of this instance
	print("Looking for predicates...\n\n")
	for pred,obj in g.predicate_objects(chairs):
		print("Predicate:\n " + pred)
		print("Object:\n " + obj + "\n\n")
		for o in g.objects(obj,None):
			print("\nFuther Infos:\n")
			print("Oggetto: \n" + o+ "\n\n")
	print("\n\n")

for tables in g.subjects(RDF.type,table):
	print("Found a table",tables)
	numOfTables += 1

print("Total Number of Chairs:",numOfChairs) 
print("Total Number of Tables:",numOfTables) 


#print("--- printing mboxes ---")
for person in g.subjects(RDF.type, FOAF.Person):
    for mbox in g.objects(person, FOAF.mbox):
        #print(mbox)
	pass


#s = g.serialize(format='n3')
#print s
