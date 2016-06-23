import sys
import subprocess
import numpy as np 
import re
import operator

##################
from  corenlpparse import coreNLP
from  corenlpparse import clsEntity
from  corenlpparse import get_doc_obj


####################################################
__entity_list_map ={}
def build_entity_map( examples_file):
	global __entity_list_map 
	for line in open(examples_file).readlines() :
		fields= {}
		for kv  in line.split("\t") :
		       kv = kv.strip()
		       if len(kv) <=0 : continue

		       tarr	= kv.split(":")
		       key	= tarr[0].strip()
		       val 	= ":".join(tarr[1:] ).strip() #everything after the first : as is
		       fields[key] = val 

		###
		e1 = clsEntity.createEntityFromString( fields["EntityArg1"] )
		e2 = clsEntity.createEntityFromString( fields["EntityArg2"] )
		
		k1 = (e1.documentId, e1.sentenceId)
		k2 = (e2.documentId, e2.sentenceId)
		if k1 not in __entity_list_map : __entity_list_map[k1] = set([])
		if k2 not in __entity_list_map : __entity_list_map[k2] = set([])

		__entity_list_map[k1].add( e1 )
		__entity_list_map[k2].add( e2 )
	
##############
def  get_entities_in_sentence(documentId, sentenceId):
	global __entity_list_map
	return __entity_list_map[ (documentId,sentenceId) ]

################
def prepare_parsetree(e1, e2, pt):
	estr1 = e1.entityDescription 
	estr2 = e2.entityDescription

	pt = pt.replace("SENTENCE_BOUNDARY", "|BT|") 
	#pt = pt.replace( estr1, "ARG1")
	#pt = pt.replace( estr2, "ARG2")
	return pt

############################
def get_entity_semantic_constraints( ) : 
	global all_relations
	entity_types =  set( ["RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain", "Gene","Gene_Family","Box","Promoter","Promoter", "DNA_Product","Hormone", "DNA","Functional_Molecule", "Regulatory_Network","Pathway", "Tissue","Development_Phase","Genotype", "Internal_Factor","Environmental_Factor"] )

	semantic_constraints= {}
	for et1 in entity_types :
		for et2 in entity_types :
			for rt in all_relations :
				if valid_relation_signature( rt, et1, et2 ) :
					if (et1,et2) not in semantic_constraints : semantic_constraints[ (et1,et2) ] = [ rt ]
					else :  semantic_constraints[ (et1,et2) ].append( rt) 
	#print semantic_constraints
	return semantic_constraints 

########################################3		
def get_possible_relations(et1, et2):
	global all_relations
	possible_relations= [ ]
	for rt in all_relations :
		if valid_relation_signature( rt, et1, et2):
			possible_relations.append( rt )
	###
	return possible_relations 
	
###########################
def valid_relation_signature(relation_type, et1, et2): #entitytypes of first and second arguments of relation
#	eg1 	= get_entity_group(et1)
#	eg2	= get_entity_group(et2)

	if relation_type == "Binds_To" :
		if et1 in ["RNA","Protein","Protein_Family", "Protein_Complex", "Protein_Domain", "Hormone"] and  et2 in ["Gene","Gene_Family" ,"Box", "Promoter", "RNA", "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain","Hormone"] : return True
		else: return False

	if relation_type == "Composes_Primary_Structure" :
		if et1 in ["Box", "Promoter"] and et2 in ["Gene","Gene_Family","Box","Promoter"] : return True
		else : return False
	

	if relation_type =="Composes_Protein_Complex" :
		if et1 in ["Protein", "Protein_Family", "Protein_Complex", "Protein_Domain"]  and et2 in ["Protein_Complex"]: return True
		else : return False


	if relation_type=="Exists_At_Stage":
		if et1 in ["RNA", "Protein","Protein_Family","Protein_Complex","Protein_Domain","Hormone"] and et2 in ["Development_Phase"]: return True
		else: return False

	if relation_type =="Exists_In_Genotype" :
		if et1 in ["RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain","Hormone"]  and et2 in ["Genotype"]: return True
		else : return False

	if relation_type =="Has_Sequence_Identical_To" :
		if et1 in ["Gene","Gene_Family"]  and et2 in ["Gene","Gene_Family"]: return True
		elif et1 in ["Protein", "Protein_Family"] and et2 in ["Protein", "Protein_Family"] : return True
		elif et1 == et2 : return True
		else : return False

	if relation_type =="Interacts_With" :
		if et1 in [ "Protein","Protein_Family","Protein_Complex","Protein_Domain" ]  and et2 in  ["Gene","Gene_Family" ,"Box", "Promoter", "RNA", "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain" ]: return True
		elif et1 in ["Gene", "Gene_Family"]  and et2 in  ["Gene","Gene_Family" ,"Box", "Promoter",  "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain" ]: return True
		elif et1 in ["Box","Promoter"]  and et2 in  ["Box", "Promoter",  "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain" ]: return True
		else : return False


	if relation_type=="Is_Functionally_Equivalent_To" :
		if et1 == et2 : return True
		elif et1 in ["Gene", "Gene_Family"] and et2 in ["Gene","Gene_Family"] : return True	 
		elif et1 in ["Protein", "Protein_Family"] and et2 in ["Protein","Protein_Family"] : return True	 
		else: return False

	if relation_type == "Is_Involved_In_Process" :
		if et1 in ["Gene", "Gene_Family","Box","Promoter","RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain","Hormone"]  and et2 in ["Regulatory_Network", "Pathway"] : return True
		else: return False


	if relation_type =="Is_Localized_In" :
		if et1 in ["RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain","Hormone","Regulatory_Network","Pathway"]  and et2 in ["Tissue"]: return True
		else : return False


	if relation_type =="Is_Member_Of_Family" :
		if et1 in ["Gene", "Gene_Family"]  and et2 in ["Gene_Family"]: return True
		elif et1 in ["RNA"]  and et2 in ["RNA"]: return True
		elif et1 in ["Protein", "Protein_Family"]  and et2 in ["Protein_Family"]: return True
		else : return False

	if relation_type =="Is_Protein_Domain_Of" :
		if et1 in ["Protein_Domain"]  and et2 in ["Protein", "Protein_Family","Protein_Complex","Protein_Domain"] : return True
		else : return False


	if relation_type=="Occurs_During":
		if et1 in ["Regulatory_Network","Pathway"] and et2 in ["Development_Phase"]: return True
		else: return False

	if relation_type=="Occurs_In_Genotype":
		if  et1 in ["Regulatory_Network","Pathway"] and et2 in ["Genotype"]: return True
		else: return False
	
	if relation_type =="Regulates_Accumulation" :
		if  et2 in ["RNA","Protein","Protein_Family","Protein_Complex","Hormone"] : return True
		else: return False	

	if relation_type=="Regulates_Development_Phase" :
		if et2 in ["Development_Phase"]: return True
		else: return False

	if relation_type=="Regulates_Expression" : 
		if et2 in ["Gene","Gene_Family","Box","Promoter"] : return True
		else: return False

	if relation_type == "Regulates_Process" :
		if et2 in ["Regulatory_Network",  "Pathway"] : return True
		else: return False

	if relation_type == "Regulates_Tissue_Development" :
		if et2 in ["Tissue"] : return True
		else: return False

	if relation_type =="Regulates_Molecule_Activity" :
		if et2 in ["Protein", "Protein_Family","Protein_Complex","Hormone"]: return True
		else : return False

	if relation_type =="Transcribes_Or_Translates_To" :
		if et1 in ["Gene", "Gene_Family"] and et2 in ["RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain"] : return True
		elif et1 in ["RNA"] and et2 in ["Protein","Protein_Family","Protein_Complex","Protein_Domain"] : return True
		else: return False	

	if relation_type =="Is_Linked_To" :
		if et1 in ["Gene", "Gene_Family", "Box", "Promoter", "RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain", "Hormone", "Regulatory_Network", "Pathway"] and et2 in ["Gene", "Gene_Family", "Box", "Promoter", "RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain", "Hormone", "Regulatory_Network", "Pathway"]  : return True
		elif et1 in ["Environmental_Factor"] and et2 in ["Environmental_Factor"]  : return True
		else : return False

	return False 
	####

###################
___docid_to_nlpobj= {}

def get_nlp_obj(documentId):
	global  ___docid_to_nlpobj 

	if documentId in ___docid_to_nlpobj : 
		return  ___docid_to_nlpobj[ documentId ]
	else:
		nlpObj = coreNLP()
		nlpObj.parse( documentId +".txt.out")
		___docid_to_nlpobj[documentId] = nlpObj
		return nlpObj

###############################
def get_vocabulary_features( features, nlpObj, e1, e2, relation_type):
	vocabulary, vocabulary_lemmas = {} , {}

	vocabulary_lemmas["Exists_In_Genotype"]=["identify","conserve","possess"]
	vocabulary_lemmas["Occurs_In_Genotype"]=["occur","observe","describe","present"]
	vocabulary_lemmas["Exists_At_Stage"]=["express","accumulate","present"]
	vocabulary_lemmas["Occurs_During"]=["implicate","establish","occur","active"]
	vocabulary_lemmas["Is_Localized_In"]=["posses","active"]
	vocabulary_lemmas["Is_Involved_In_Process"]=["involve","include","mediate"]
	vocabulary_lemmas["Transcribes_Or_Translates_To"]=["encode"]
	vocabulary_lemmas["Is_Functionally_Equivalent_To"]=["ortholog","homolog"]
	vocabulary_lemmas["Regulates_Accumulation"]=["activate","induce","enhance","trigger","inhibit","accumulation","steady","concentration"]
	vocabulary_lemmas["Regulates_Expression"]=["activate","induce","enhance","trigger","inhibits","transcription"]
	vocabulary_lemmas["Regulates_Development_Phase"]=["activate","induce","enhance","trigger","inhibits","influence","block"]
	vocabulary_lemmas["Regulates_Molecule_Activity"]=["control","regulate","phosphorylate"]
	vocabulary_lemmas["Regulates_Process"]=["restrict","regulate","induce"]
	vocabulary_lemmas["Regulates_Tissue_Development"]=["produce","generate","developp","repress","possess"]
	vocabulary_lemmas["Composes_Primary_Structure"]=["possess","motif","core","located","sequence"]
	vocabulary_lemmas["Composes_Protein_Complex"]=["presence","associate","complex","detect","component","composition"]
	vocabulary_lemmas["Is_Protein_Domain_Of"]=["contain","presence","characterize"]
	vocabulary_lemmas["Has_Sequence_Identical_To"]=["identical","synonym"]
	vocabulary_lemmas["Binds_To"]=["bind","physical","interact","precipitate","migrate"]
	vocabulary_lemmas["Interacts_With"]=["cooperat","synergistantagonis","counteract","relationship","effect"]
	vocabulary_lemmas["Is_Member_Of_Family"]=["member","family","belong"]
	vocabulary_lemmas["Is_Linked_To"]=[]
	
	
	############for word in ["identified","conserved","possesses", "occurs","observed","described","present", "expressed", "during", "accumulates","implicated","established","active","within","possess","involved","includes","mediating", "encodes","ortholog","homolog","activates","induces","enhances","trigger","inhibits","steady","concentration","increase","gene","expression","transcription","blocks","regulate","phosphorylate","restrict","produce","generate","developed","repress","possess","motif","core","located","sequence","contained"]:

	vocabulary["Exists_At_Stage"] = ["express", "accumulat", "presen"  ]
	vocabulary["Exists_In_Genotype"] = [ "identif", "conserv","possess" ]
	vocabulary["Is_Localized_In"] = ["accumulat","within","possess","presen","activ" ]
	vocabulary["Occurs_During"] = [ "implicat", "establish", "occur", "activ" ]
	vocabulary["Occurs_In_Genotype"] = [ "occur", "observ","descri","presen"  ]
	vocabulary["Is_Functionally_Equivalent_To"] = [ "ortholog","homolog" ]
	vocabulary["Is_Involved_In_Process"] = [ "includ", "mediat", "involv"  ]
	vocabulary["Transcribes_Or_Translates_To"] = [ "encod" ]
	vocabulary["Regulates_Accumulation"] = [ "activat", "induc", "enhanc", "trigger", "inhibit", "accumulat", "steady", "concentrat", "increas" ]
	vocabulary["Regulates_Development_Phase"] = [ "activat", "induc", "enhanc", "trigger", "inhibit", "influenc", "block" ]
	vocabulary["Regulates_Expression"] = [ "activat", "induc", "enhanc", "trigger", "inhibit", "express", "transcript", "gene", "regulat"]
	vocabulary["Regulates_Molecule_Activity"] = [ "control", "regulat", "phosphorylate"]
	vocabulary["Regulates_Process"] = [ "restrict", "regulat", "induc"]
	vocabulary["Regulates_Tissue_Development"] = [ "produc", "generat", "develop", "repress", "possess" ]
	vocabulary["Composes_Primary_Structure"] = ["possess", "motif", "core", "locat", "sequenc", "contain" ]
	vocabulary["Composes_Protein_Complex"] = [ "presen", "associat", "complex", "detect", "component", "compos" ]
	vocabulary["Has_Sequence_Identical_To"] = [ "identical", "synonym" ]
	vocabulary["Is_Member_Of_Family"] = [ "member", "family" , "belong"]
	vocabulary["Is_Protein_Domain_Of"] = [ "contain", "presen", "characterized", "-like"]
	vocabulary["Binds_To"] = [ "bind", "interact", "precipitat", "migrat"]
	vocabulary["Interacts_With"] = [ "cooperat", "synergistic","antagonist", "counteract" ,"relationships", "effect"]
	vocabulary["Is_Linked_To"] = [ "bind", "interact" ]	
	if relation_type not in vocabulary_lemmas :
		return 

	lemma_search_base =  " ".join(nlpObj.lemmas[e1.sentenceId]).lower()
	raw_text_search_base = 	nlpObj.rawText[e1.sentenceId].lower()

	for query  in vocabulary_lemmas[relation_type]:
        	if query in  lemma_search_base :  #nlpObj.rawText[e1.sentenceId]: 
			features["trigger_"+query]=1.0
        	else:
            		features["trigger_"+query]=0.0
	##	
	for query in vocabulary[relation_type] :
	 	if query in raw_text_search_base: 
			features["trigger_"+query]=1.0
        	else:
            		features["trigger_"+query]=0.0


############
from nltk.corpus import stopwords
g_stopwords=  [ str(w) for w in stopwords.words("english")]	
	
######################################
def get_regular_features(fields, e1, e2, relation_type):
	global g_stopwords
	features = {}
	nlpObj = get_nlp_obj( e1.documentId )

	espanstart=  min(e1.start, e2.start)
	espanend =   max(e1.end, e2.end)
	


    	#words of the entities
    	s1=e1.entityDescription
    	for word in s1.split():
        	features["entity1_"+word]=1.0

    	s2=e2.entityDescription
    	for word in s2.split():
        	features["entity2_"+word]=1.0

	
	for (word, wordboundary) in  nlpObj.getLemmas(e1.sentenceId) :  
		word= word.lower()
		#exclusion list
		if relation_type in ["Has_Sequence_Identical_To", "Is_Functionally_Equivalent_To","Regulates_Accumulation","Regulates_Expression"] and (word in  g_stopwords):
			continue 
		if wordboundary <  espanstart :
			word = word+"_before"
		elif wordboundary > espanend :
			word = word+"_after"
		else:
			word = word+"_mid"
		features[word] = features.get(word, 0.0 ) + 1.0


	#feature POS tag sequence
	span1 = e1.getTokenSpan()
	span2 = e2.getTokenSpan()
	p1, p2, p3, p4 =  min(span1), max(span1), min(span2), max(span2)

	features["token_distance"] = abs(p3 -p2)
	
	features["postagseq_before"]= "_".join(  nlpObj.postags[e1.sentenceId][ : p1] )
	features["postagseq_after"] = "_".join(  nlpObj.postags[e1.sentenceId][ p4: ] )
	features["postagseq_middle"]= "_".join(  nlpObj.postags[e1.sentenceId][ p2:p3] )
	features["postagseq_arg1"]  = "_".join(  [nlpObj.postags[e1.sentenceId][i] for i in span1] )
	features["postagseq_arg2"]  = "_".join(  [nlpObj.postags[e1.sentenceId][i] for i in span2] )

	for i in range( len(nlpObj.postags[e1.sentenceId]) ):
		if nlpObj.postags[e1.sentenceId][i].startswith("VB") : 
			if i < p1 :	features["verb_before_"+ nlpObj.lemmas[e1.sentenceId][i] ] = 1.0 
			elif i > p4 :	features["verb_after_"+ nlpObj.lemmas[e1.sentenceId][i] ] = 1.0 
			elif i > p2 and i< p3 :	features["verb_middle_"+ nlpObj.lemmas[e1.sentenceId][i] ] = 1.0 
			else:  	features["verb_within_entity_"+ nlpObj.lemmas[e1.sentenceId][i] ] = 1.0 
 


	get_vocabulary_features(features, nlpObj, e1, e2, relation_type)
	###

	features["entitytype_signature_"+e1.entityType+"_"+e2.entityType]=1.0


		### start of relation specific features
	get_relation_specific_features(features,nlpObj, e1, e2, relation_type)

	return features
##############################################################
def get_relation_specific_features(features, nlpObj, e1, e2, relation_type) :
	sentence = nlpObj.rawText[e1.sentenceId].lower()
	ed1 = e1.entityDescription.lower()
	ed2 = e2.entityDescription.lower()

	if  relation_type in [ "Is_Functionally_Equivalent_To", "Regulates_Development_Phase" ] :
		p1 = ed1+"\s*\(.*"+ed2+".*\)"
		p2 = ed2+"\s*\(.*"+ed1+".*\)"

		if re.search(p1, sentence) or  re.search(p2,sentence):
			features["trigger_pattern_brackets"] = 1.0


########################################
def get_feature_other_entities(features, e1, e2):
	for entity_other  in get_entities_in_sentence(e1.documentId, e1.sentenceId):
		span_other  = entity_other.getTokenSpan()
		postart, poend = min(span_other), max(span_other)
		if poend < p1 :     features["entity_before_"+ entity_other.entityType] =1.0
		elif postart > p4 : features["entity_after_"+ entity_other.entityType] =1.0
		elif postart > p2 and poend< p3 : features["entity_middle_"+ entity_other.entityType] =1.0
	
##########################
def get_candidates(data_file, relation_type, gold_relations, feature_type="BOW"):
	#bag of words feature -- and identifying information -- only for valid (based on entity type signature) candidate entity pairs
	pointSet= []

	import re
	for line in open(data_file).readlines() :
		#if "Bag_Of_Words" not in line  : continue #skip entity pairs without this feature
		if "SENTENCE_BOUNDARY"  in line : continue #skip pairs beyond a sentence

		fields= {}
		for kv  in line.split("\t") :
		       kv = kv.strip()
		       if len(kv) <=0 : continue

		       tarr	= kv.split(":")
		       key	= tarr[0].strip()
		       val 	= ":".join(tarr[1:] ).strip() #everything after the first : as is
		       fields[key] = val 

		###
		label = fields["RelationLabel"]
		e1 = clsEntity.createEntityFromString( fields["EntityArg1"] )
		e2 = clsEntity.createEntityFromString( fields["EntityArg2"] )

		###
		documentId = e1.documentId 

		if (e1,e2,documentId, relation_type) in gold_relations:
			check_label = relation_type
		else:
			check_label = "NOT_RELATED"

		if check_label==relation_type and label!=relation_type  :
		 	print >>sys.stderr, "debug this ", e1.get_display(), e2.get_display(), documentId, relation_type  
		 	print >>sys.stderr, "coming from ", data_file , line 
			sys.exit(-1)	


		#skip this point if...
		if relation_type =="ANY_RELATION" and len(get_possible_relations(e1.entityType, e2.entityType ))<=0 :
			continue
		if relation_type!="ANY_RELATION" and False == valid_relation_signature(relation_type, e1.entityType, e2.entityType):
			continue

		if feature_type=="BOW":
			features = get_regular_features( fields, e1, e2 , relation_type ) #bag of words and other such lexical features	
		elif feature_type == "Parse_Tree" :
			features = fields["Parse_Tree"] #the string parse tree as is
		####
		pointSet.append(  (e1, e2, label, features) ) 
	##### for line in ...

	#dumping candidates for debugging
	ofh= open("tmp.candidates."+ data_file +"."+relation_type, "w") 
	for (e1,e2,label,features) in sorted(pointSet, key=operator.itemgetter(2) ) : #keep it sorted on labels for easy analysis
		print >>ofh, label, e1.get_display(), e2.get_display(), e1.entityDescription,  e2.entityDescription,"|", get_doc_obj(e1,e2).rawText[e1.sentenceId].replace("\n"," ") ,"|", features
	ofh.close()
	
	return pointSet 

#########################
def get_gold_relations(a2dir):
	#assume from dev directory
	goldrelations = set([])	
	import os
	for fname in  os.listdir( a2dir ):
		if fname[-3:] != ".a2" : continue #skip non-a2 files
		
		for line in open(a2dir+fname).readlines():
			arr =  line.split() #[1], l.split()[2], l.split()[3]
			relname = arr[1]

			eid1 = arr[2].split(":")[1]
			eid2 = arr[3].split(":")[1]
			documentId = a2dir+ fname[:-3] # 
			goldrelations.add(  (eid1, eid2, documentId, relname) )
	
	return goldrelations	
		
######################################
def apply_semantic_constraints(test_points, relation_type, classifier_predictions):
	final_labels= []
	for idx in range(len(classifier_predictions)):
		cp = classifier_predictions[idx]
		(e1, e2, true_label, features) = test_points[idx]
		possible_relations = get_possible_relations( e1.entityType, e2.entityType) 
		if relation_type not in possible_relations:
			final_labels.append( "NOT_RELATED" ) 
			continue
			continue

		#default
		final_labels.append(cp)
	
	return final_labels 
###########
dump_predictions={}### collate predictions ( for writing into into .a2 files for evalation)
##########################
def compute_metrics( test_points, classifier_predictions, relation_type , gold_relations):
	#test_points  		= list of tuples of (entity pair information, true labels, features)
	#classifier_predictions = (corresponding) list of predicted labels
	global dump_predictions 

	predictedRelations= set([])
	actualRelations = set([])
	for (eid1,eid2,documentId, rellabel) in gold_relations: 
		if rellabel== relation_type : 
			actualRelations.add( (eid1,eid2,documentId) )

	classifier_predictions = apply_semantic_constraints(test_points, relation_type, classifier_predictions)
	
	ofh= open("tmp.predictions."+relation_type, "w")
	###
	idx = 0
	for predicted_label in classifier_predictions:  #open(svmlight_predictions).readlines() :
		e1, e2, true_label, features = test_points[idx]
		print >>ofh,true_label, predicted_label,"|", e1.get_display(),e2.get_display(),"|", get_doc_obj(e1,e2).rawText[e1.sentenceId]

		if predicted_label == relation_type:
			predictedRelations.add( (e1.entityId, e2.entityId, e1.documentId) )
			if e1.documentId not in dump_predictions : dump_predictions[e1.documentId] = []
			dump_predictions[e1.documentId].append(  (e1, e2, relation_type) )
		idx += 1
	##
	ofh.close()

	correctRelations=   predictedRelations.intersection( actualRelations )
	falseNegatives=     actualRelations - predictedRelations

	print "metrics for ", relation_type, " with ", len(test_points) , " test points"
	print "metrics: actual ",   len(actualRelations) , actualRelations
	print "metrics: predicted", len(predictedRelations), predictedRelations
	print "metrics: false negatives", len(falseNegatives), falseNegatives 
	print "metrics: correct ",  len(correctRelations), correctRelations
	precision, recall, f1 = -1,-1,-1

	if len(predictedRelations) >0  and len(actualRelations)>0 :
		precision = len(correctRelations)*100.0/len(predictedRelations) 
		recall = len(correctRelations)*100.0/ len(actualRelations)
	if len(correctRelations) >0 :
		f1 = 2.0*precision* recall / (precision+recall)

	print  relation_type, "prec, recall, f1 ",  precision, recall, f1, "\n_______________________________________________________________________"
	print  >>sys.stderr, relation_type, "prec, recall, f1 ",  precision, recall, f1, "\n_______________________________________________________________________"
		

def custom_linear_kernel(e1, e2, e3, e4, features1, features2):
	#compute the dot-product of bag of words features
	p= 0 
	for word in features1 :
		p+=  ( features1.get(word,0) * features2.get(word,0) )
	return p
####################################################################################
#globals for custom kernel use
custom_data_points = []
###
############
def scikit_classifier(train_file, test_file, relation_type, method="naive_bayes") :
	global train_gold_relations, test_gold_relations 

	trainPoints = get_candidates(train_file, relation_type, train_gold_relations) 
	testPoints  = get_candidates(test_file, relation_type, test_gold_relations)

	
	#done.. vectorize it now
	from sklearn.feature_extraction.text import CountVectorizer
	from sklearn.feature_extraction import DictVectorizer
	vect = DictVectorizer() #CountVectorizer()

	train_matrix =  vect.fit_transform(  [features for (e1, e2,  label, features)  in trainPoints] )
	test_matrix =   vect.transform	  (  [features for (e1, e2,  label, features)  in testPoints] )	


	train_labels =  [label for (e1, e2, label,features) in trainPoints] #labels to be as strings not numbers
	test_labels  =  [label for (e1, e2, label,features) in testPoints] 

	if method== "naive_bayes" :
		from sklearn.naive_bayes import MultinomialNB
		clf = MultinomialNB().fit( train_matrix, train_labels )
	elif method=="svmsgd":
                from sklearn.linear_model import SGDClassifier
                clf = SGDClassifier(loss='hinge').fit(train_matrix, train_labels)
        elif method=="svmrbf":
                from sklearn import svm
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler( with_mean = False)
                scaler.fit(train_matrix)
                train_matrix = scaler.transform( train_matrix )
                test_matrix = scaler.transform( test_matrix )
                clf= svm.SVC(kernel='rbf')
                clf= clf.fit( train_matrix, train_labels )
        elif method=="logreg":
                from sklearn import linear_model
                clf = linear_model.LogisticRegression( ) #C=regularizationStrength, penalty=regularization, dual=True)
                clf.fit( train_matrix, train_labels )
        elif method=="logregcv":
                from sklearn import linear_model
                clf = linear_model.LogisticRegressionCV( dual=True, solver="liblinear", penalty=regularization) #C=regularizationStrength, penalty=regularization, dual=True)
                clf.fit( train_matrix, train_labels )
        elif method=="svc" :
                from sklearn.svm  import SVC
		train_labels =  [label for (e1, e2, label,features) in trainPoints] #labels to be as strings not numbers
		test_labels  =  [label for (e1, e2, label,features) in testPoints] 

		custom_weights="auto"
			
                clf = SVC(kernel='linear', class_weight= custom_weights)
                clf.fit( train_matrix, train_labels)
	elif method == "svccustom" :
		global custom_data_points
		from sklearn.svm  import SVC
		custom_data_points=[]
		custom_data_points.extend(trainPoints) 
		tempX  =  np.arange( len(trainPoints) ).reshape( -1, 1) #make 1 column matrix of contents 0,1,2,3... (n-1) , where n is no of training points
		clf= SVC( kernel = custom_kernel ) 
		clf.fit( tempX , train_labels ) 
		custom_data_points.extend(  testPoints ) #now load the test points for reference
		indexes_to_predict =  np.arange( len(trainPoints),  len(custom_data_points) ).reshape(-1,1)
		print "custom_data_points are", len(custom_data_points) , " of which train are ", len(trainPoints) 
		print "indexes_to_predict =", indexes_to_predict[0], "..." , indexes_to_predict[-1] 	
		predictions= clf.predict( indexes_to_predict )
	else: 
		print >>sys.stderr, "enter classification method"
		sys.exit(-1)

	if method != "svccustom": #handled above already
		predictions=  clf.predict( test_matrix)

	from sklearn.metrics import confusion_matrix

	print "number of train and test examples", len(trainPoints), len(testPoints)
	print "confusion matrix", set(test_labels)
	print confusion_matrix (test_labels, predictions )

	print >>sys.stderr, method, " compute metrics ", relation_type
	compute_metrics( testPoints, predictions, relation_type , test_gold_relations )

#######################
def dump_predictions_for_submission():	 
	all_predictions= set([] )
	for docid in dump_predictions :
		pred_ofh= open( "predicted_relations/"+ docid.split("/")[-1] + ".a2" , "a")
		relNo= 1
		for (e1,e2, relation_type) in  dump_predictions[docid]  :
			if relation_type== "Binds_To" : role1, role2 = "Functional_Molecule","Molecule"
			elif relation_type== "Composes_Primary_Structure": role1, role2 = "DNA_Part","DNA" 
			elif relation_type== "Composes_Protein_Complex" : role1, role2 =   "Amino_Acid_Sequence", "Protein_Complex"
			elif relation_type== "Exists_At_Stage" : role1, role2 =   "Functional_Molecule", "Development"
			elif relation_type== "Has_Sequence_Identical_To": role1, role2 =   "Element1","Element2"
			elif relation_type== "Interacts_With": role1, role2 =   "Agent","Target"
			elif relation_type== "Is_Functionally_Equivalent_To" : role1, role2 =   "Element1", "Element2"
			elif relation_type== "Is_Involved_In_Process" : role1, role2 = "Participant","Process"
			elif relation_type== "Is_Member_Of_Family" : role1, role2 = "Element", "Family"
			elif relation_type== "Is_Protein_Domain_Of" : role1, role2 =  "Domain","Product" 
			elif relation_type== "Occurs_During" : role1, role2 =   "Process","Development"
			elif relation_type== "Occurs_In_Genotype" : role1, role2 =  "Process","Genotype" 
			elif relation_type== "Regulates_Accumulation": role1, role2 = "Agent","Functional_Molecule"
			elif relation_type== "Regulates_Development_Phase": role1, role2 = "Agent","Development"
			elif relation_type== "Regulates_Expression": role1, role2 = "Agent","DNA"
			elif relation_type== "Regulates_Molecule_Activity": role1, role2 = "Agent","Molecule"
			elif relation_type== "Regulates_Process": role1, role2 = "Agent","Process"
			elif relation_type== "Regulates_Tissue_Development": role1, role2 = "Agent","Target_Tissue"
			elif relation_type== "Transcribes_Or_Translates_To": role1, role2 = "Source","Product"
			elif relation_type== "Is_Linked_To": role1, role2 = "Agent1","Agent2"
			elif relation_type== "Is_Localized_In" :
					if e1.entityType in ["Regulatory_Network", "Pathway" ]   : role1, role2 = "Process", "Target_Tissue"
					else:  role1, role2 =   "Functional_Molecule", "Target_Tissue"
			elif relation_type== "Exists_In_Genotype": 
					if e1.entityType in ["Genotype", "Tissue", "Development_Phase"]: role1, role2 = "Element", "Genotype"
					else: role1, role2 = "Molecule", "Genotype"


			print >>pred_ofh , "E"+str(relNo)+"\t", relation_type, role1+":"+e1.entityId, role2+":"+e2.entityId
			relNo += 1

			all_predictions.add(  (e1.entityId, e2.entityId, docid, relation_type) )
		pred_ofh.close()
	return all_predictions

################################################
def  test_generate_gram_matrix( ifh  ):
	#the pairs comes from a stdin
	while True:
		line = ifh.readline()
		if not line :
			break

		if "custom_kernel_computation_for" not in line : 
			continue 

		line = line.strip()
		try:
			sim_start = line.rfind( " ") 
			sim =  line[ sim_start : ]
			line = line[: sim_start]
			msg, s1, s2, s3, s4 = re.split(" (?=T)", line) #e1A.get_display(), e2A.get_display(), e1B.get_display(), e2B.get_display() ,sim
		except:
			print >>sys.stderr, "check format " , line
			print >>sys.stderr, "check format " , re.split(" (?=T)", line)
			sys.exit(-1)
		e1 = clsEntity.createEntityFromString(s1)	
		e2 = clsEntity.createEntityFromString(s2)	
		e3 = clsEntity.createEntityFromString(s3)	
		e4 = clsEntity.createEntityFromString(s4)	
		
		graph_sim =  graphKernel( e1, e2, e3, e4)
		print "custom_kernel_computation_for", s1, s2, s3, s4, graph_sim




#########################################
all_relations=["Binds_To","Composes_Primary_Structure","Composes_Protein_Complex","Exists_At_Stage","Exists_In_Genotype","Has_Sequence_Identical_To","Interacts_With","Is_Functionally_Equivalent_To","Is_Involved_In_Process","Is_Localized_In","Is_Member_Of_Family","Is_Protein_Domain_Of","Occurs_During","Occurs_In_Genotype","Regulates_Accumulation","Regulates_Development_Phase","Regulates_Expression","Regulates_Process","Regulates_Tissue_Development","Regulates_Molecule_Activity","Transcribes_Or_Translates_To","Is_Linked_To"]
def partitioned_classifier():
	global all_relations, train_examples, test_examples

	print "-----------------------------------------------------------------------------------------------------"
	import time
	print " run at ", time.asctime()
	###test_classification_method = "svmrbf"
	classification_method= {}
	classification_method["Binds_To"] =				"svc"
	classification_method["Composes_Primary_Structure"]=		"naive_bayes"
	classification_method["Composes_Protein_Complex"]=		"naive_bayes"
	classification_method["Exists_At_Stage"]=			"naive_bayes"
	classification_method["Exists_In_Genotype"]=			"svc" 
	classification_method["Has_Sequence_Identical_To"]=		"svc"
	classification_method["Interacts_With"]=			"svc"
	classification_method["Is_Functionally_Equivalent_To"]=		"svc"
	classification_method["Is_Involved_In_Process"]=		"svc"
	classification_method["Is_Localized_In"]=			"svc"
	classification_method["Is_Member_Of_Family"]=			"svc"
	classification_method["Is_Protein_Domain_Of"]=			"svc" 
	classification_method["Occurs_During"]=				"naive_bayes"
	classification_method["Occurs_In_Genotype"]=			"svc" 
	classification_method["Regulates_Accumulation"]=		"svc"
	classification_method["Regulates_Development_Phase"]=		"svc"
	classification_method["Regulates_Expression"]=			"svc"
	classification_method["Regulates_Process"]=			"naive_bayes"
	classification_method["Regulates_Tissue_Development"]=		"naive_bayes"
	classification_method["Regulates_Molecule_Activity"]=		"naive_bayes"
	classification_method["Transcribes_Or_Translates_To"]=		"naive_bayes"
	classification_method["Is_Linked_To"]=				"svc"  


	for relation_type in  all_relations:
		#try :
		     #scikit_classifier( train_examples,  test_examples, relation_type, method=classification_method) 
		     scikit_classifier( train_examples,  test_examples, relation_type, classification_method[relation_type] ) 
		#except Exception, e :
		#	print >>sys.stderr, "classifier", classification_method, " failed for ", relation_type, "exception was", str(e)



#########################################################
if __name__ == "__main__":
	#mode = "test" # 
	mode = "dev" 
	devdir = "data/BioNLP-ST-2016_SeeDev-binary_dev/"
	traindir = "data/BioNLP-ST-2016_SeeDev-binary_train/"

	train_only_gold_relations= get_gold_relations(traindir)
	dev_gold_relations = get_gold_relations(devdir)
	
	if "test" == mode:
		train_gold_relations = train_only_gold_relations.union( dev_gold_relations )
		test_gold_relations = set([]) #empty set - no a2 files
		train_examples, test_examples =  "train_and_dev_examples.txt",  "test_examples.txt"
	else:
		train_gold_relations = train_only_gold_relations
		test_gold_relations = dev_gold_relations
		train_examples, test_examples =  "train_examples.txt",  "dev_examples.txt"

	### get the predictions
	partitioned_classifier()
	
	#dump predictions into a2 files for submission
	all_predictions= dump_predictions_for_submission()
	correct =  len(all_predictions.intersection(test_gold_relations))
	actual = len(test_gold_relations)
	predicted = len(all_predictions)
	print "final: actual , predicted, correct ", actual, predicted , correct
	try :
		p, r = 1.0*correct/predicted , 1.0*correct/actual
		f =  2*p*r/(p+r)
	except :
		p, r, f = 0.0, 0.0 , 0.0

	print "prec, recall, f1 ", p, r,f
