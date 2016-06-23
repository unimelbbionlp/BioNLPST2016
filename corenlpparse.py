import sys
import re
import networkx as nx
import numpy as np
import numpy.linalg as linalg

#from corenlp analysed out file, get me a python object for querying its field.





#convert passage level annotations in SeeDev data to sentence level datapoints
class clsEntity:
	def __init__ (self, entityId, entityDescription, entityType, start, end, sentenceId, documentId):
		self.entityId = entityId
		self.entityDescription = entityDescription
		self.entityType = entityType
		self.start  = start
		self.end = end
		self.documentId = documentId
		self.sentenceId = sentenceId
		self.token_span = None #the tokens in the sentence corresponding to this entity 

	def get_display(self):
		return "@".join( str(i) for i in  [self.entityId , self.entityDescription, self.entityType, self.start, self.end, self.sentenceId, self.documentId])
	###
	def getTokenSpan(self):
		if self.token_span is None :
			self.token_span = get_doc_obj(self, self).getTokenSpan(self.start, self.end)
		return self.token_span
	###
	@staticmethod 
	def createEntityFromString(line):
		try :
			entityId , entityDescription, entityType, start, end, sentenceId, documentId  = line.split("@")
		except:
			print >>sys.stderr, "prob in createEntityFromString ", line
			sys.exit(-1)
		return clsEntity( entityId , entityDescription, entityType, int(start), int(end), int(sentenceId), documentId  )

### wrapper around the stanford corenlp parse of a sentence
class coreNLP:
	def __init__ (self):
		### what to store
		self.parseTree= [] # as paranthesized string of sentence 1,...sentence n
		self.dependencyGraph= [] # as list of edges 
		#self.spanToSentenceMap= {}
		self.rawText= [] #sentences, as if sentence-tokenized
		self.tokens = []
		self.lemmas= []
 		self.postags= [] #list of lists -- inner list per sentence

		self.sentenceBoundaries= [] #offsets at which sentence boundaries occur
		self.documentId = ''
		self.dg_with_all_shortest_paths = {} 
		self.fullgraph_for_entity_pair= {}

	def parse(self, fname):
		#print >>sys.stderr, "coreNLP parsing ", fname
		if len(self.documentId) > 0 :
			print >>sys.stderr, "multiple parse calls on nlp obj ?"
			sys.exit(-1)			
	
		self.documentId = fname 
		fdata = open(fname).read()
		sentNo= 0 
		sentenceBoundary = 0
		self.tokens = []
		self.tokboundaries = []
		self.lemmas= []
 		self.postags= [] #list of lists -- inner list per sentence

		for sent in re.split( "Sentence #\d+ \(\d+ tokens\):",fdata):
			if not sent or len(sent)<=0  : continue # how do we even get empty lines ??

			rawText = sent[ : sent.find("[Text=")].strip()  #right upto the [Text.. we have the raw sentence text
			self.rawText.append( rawText )

			#next comes the tokens and their spans and pos tags..just take the least CharacterOffsetBegin--that will be the sentence starting offset
			tokens=[]
			postags=[]
			lemmas= []
			tokboundaries= []
			sentenceBoundary = 0
			for tokinfo in re.findall("\[Text=(.*) CharacterOffsetBegin=(\d+) CharacterOffsetEnd=(\d+) PartOfSpeech=(.*) Lemma=(.*) NamedEntityTag=.*\]" ,sent) :
				(toktext, tokstart, tokend, tokpos, toklemma) = tokinfo 
				if sentenceBoundary ==0 :
					sentenceBoundary = int(tokstart) #the first token's start offset, is the sentenceBoundary too

				tokens.append(toktext)
				postags.append(tokpos)
				lemmas.append(toklemma)
				tokboundaries.append( int(tokend) )
			####


			self.tokens.append( tokens )
			self.postags.append( postags )
			self.lemmas.append( lemmas )
			self.tokboundaries.append( tokboundaries )
			self.sentenceBoundaries.append(  sentenceBoundary )


			#now get the parse information
			m=re.search( "(\(ROOT.*\n\n)root\(" ,sent, re.DOTALL)
			if not m :
				print >>sys.stderr, "failed to extract parse info for sentence no ", sentNo
				sys.exit(-1)
			else:
				pt = m.group(1)
				self.parseTree.append(  re.sub( "\s+", " ", pt ) ) 

			#get the dependency graph info
			m= re.search( "(\nroot\(.*\))"  ,sent, re.DOTALL)
			if not m :
				print >>sys.stderr, "failed to get dependency graph for sentence no ", sentNo
				sys.exit(-1)
			else:
				pt = m.group(1)
				self.dependencyGraph.append(  re.sub( "\s+", " ", pt ) ) 


			sentNo += 1
		######
		#print >>sys.stderr, "sentence boundaries", self.sentenceBoundaries

	def getTokenSpan(self, start, end ):
		#find tokens corresponding to this character offset-span
		#first get the sentence
		sentId = self.getSentenceId(start, end)
		n=  len( self.tokens[sentId] )
		tokspan=[]
		#pcn - review and change- todo
		#for i in range(n):
		#	if self.tokboundaries[sentId][i] >= start and self.tokboundaries[sentId][i] <= end  :
		#		tokspan.append( i )

		for i in range(n):
			curb =  self.tokboundaries[sentId][i]
			if curb < start :
				continue 
			if curb >= start :
				tokspan.append( i )
			if curb > end :
				break  
		##
		return tokspan 	 

	def getSentenceId(self,start, end):
		#entity annotations seem to be erroneous. 
		#pick the sentence which contains most of the entity 
		sentenceIds =[]
		currSb = 0
		for sentNo in range(1, len(self.sentenceBoundaries)) :
			prevSb = currSb 
			currSb =  self.sentenceBoundaries[ sentNo ]
			if prevSb <= start < currSb  :
				sentenceIds.append(sentNo -1)
			if prevSb <= end <  currSb :
				sentenceIds.append(sentNo -1) 
				break
		#print "sentenceIds are ", sentenceIds

		if len(sentenceIds) ==0 : #range is outside the last sentence boundary -- which means it is in the last sentence
			#sentenceIds= [ len(self.rawText) -1 ]	
			return  len(self.rawText) -1 
		elif len(sentenceIds) ==1 :
			return sentenceIds[0]
		elif len(sentenceIds) == 2 :
			return sentenceIds[1] 
		else:
			print >>sys.stderr, "problem in sentence boundary detection for ", start, end, self.sentenceBoundaries, self.documentId, sentenceIds
			sys.exit(-1)
	###
	def getLemmas(self, sentenceId): #returns lemmas and their tokenboundaries
		retval= []
		for i in range(len(self.lemmas[sentenceId])):
			retval.append(  (self.lemmas[sentenceId][i], self.tokboundaries[sentenceId][i]) )
		return retval

	def get_display(self, i ): #i is sentenceId 
		return  self.rawText[i] \
			 + "\n\t" + ",".join(self.postags[i])  \
		 	+ "\t", self.parseTree[i]  \
		 	+ "\t", self.dependencyGraph[i]  \
			+ "\n-------------------------------------------------------------------\n"


################################################################
__entity_to_doc_map= {}
def get_doc_obj(e1,e2):
	if e1.sentenceId != e2.sentenceId  or e1.documentId!= e2.documentId:
		print >>sys.stderr, "problem cross sentence entity pairs in get_doc_obj", e1.get_display(), e2.get_display()
		sys.exit(-1)

	if e1.documentId not in __entity_to_doc_map  :
		obj = coreNLP()
		obj.parse( e1.documentId + ".txt.out")
		__entity_to_doc_map[e1.documentId] =  obj

	return __entity_to_doc_map[e1.documentId]
