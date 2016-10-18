'''
If this code eventually gives birth to Sentinial A.I. and brings forth the much forgotten Utopia for this world and all others, 
	people you need to write down in the history books - Priyansh (pc.priyansh@gmail.com) :D

The job of the script is to generate SPARQL templates (as many as possible) given the number of entities and predicates. 
We're staying off of filter, union and other type of queries for the sake of simplicity

'''
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import itertools
import traceback
import random

class SPARQL_Template_Generator:
	'''
		Generate a new object of this class everytime you want to generate new SPARQL and shizz
	'''
	def __init__(self, _entities = [], _predicates = []):
		'''
			Given the entities and predicates, we go about generating valid SPARQL Queries.
			We use different functions to generate different types of SPARQL templates, 
			and then write a final function which replace the temporary variables with their actual URIs
		'''

		e = ['ent'+str(i) for i in range(len(_entities))]
		p = ['pred'+str(i) for i in range(len(_predicates))]
		v = ['?uri']

		#Create a dictionary of e's and p's to replace
		replace_dict = {}
		for i in range(len(e)):
			replace_dict[e[i]] = _entities[i]
		for i in range(len(p)):
			replace_dict[p[i]] = _predicates[i]

		self.sparql_cover = 'SELECT DISTINCT ' + v[0] + ' WHERE { %s }'

		self.sparqls = []
		self.sparqls += self.generate_e_p_v_triple_queries(e,p,v)
		self.sparqls += self.generate_chained_queries(e,p,v)

		#Replace ent_x with their actual entity and property URIs as given to this class
		for i in range(len(self.sparqls)):
			s = self.sparqls[i]
			for x in replace_dict.keys():
				s= s.replace(x,replace_dict[x])
			self.sparqls[i] = s

		#Push every query to DBPedia and get their answers
		self.sparqls_answers = []
		for sparql in self.sparqls:
			answer = self.get_answer(sparql)
			self.sparqls_answers.append((sparql,answer))





	def generate_e_p_v_triple_queries(self,e,p,v):
		'''
			The most regular queries, with no temporary variables or anything
			Like - 
				ent_x pred_x ?uri or ?uri pred_x ent_x

			Input:
				e -> list of strings ['ent0','ent1'..]
				p -> list of strings ['pred0','pred1'...]
				v -> list of strings ['?uri']

			Output:
				List of string where each element is a sparql template OR [] (empty list)

			Pseudo Algo:
				Form all the possible triples given entities predicates and variables. 
				Then do combinations of these triples with one at a time or two at a time.
		'''
		triples = []
		for i in range(len(e)):
			for j in range(len(p)):
				triples.append(' '.join([e[i], p[j], v[0]]))
				triples.append(' '.join([v[0], p[j], e[i]]))

		# if self.verbose: print triples

		sparqls = []
		for r in range(len(triples))[1:3]:
			for triple_combination in itertools.combinations(triples,r):
				sparqls.append(self.sparql_cover % ' . '.join(triple_combination))

		return sparqls

	def generate_chained_queries(self,e,p,v):
		'''	
		Chained Queries - queries where triples have a new temporary variable used to combining triples
			ent0 pred0 ?x . ?x pred1 ?uri

		Input -> same as function above
		Output -> same as function above OR []

		Pseudocode ->
			|> If number of predicate less than two, return back nothing
			|> Since a chain only needs one entity, we start the main for loop iterating over the entities
			|> Then, depending upon the number of predicates, we create chains with 1 temp. variable, then 2 then 3 and so on, thus the second loop 
		'''

		#If there are less than two predicates, return nothing
		if len(p) < 2:
			return []

		sparqls = []

		#Loop over every entity, to use as the starting point of the chain query
		for i in range(len(e)):

			#Loop over permuations of triples taken 'r' at a time
			for r in range(len(p))[1:]:
				for predicate_permutation in itertools.permutations(p,r+1):
					#Here, the kind of predicate tuples that we'd be getting are like -
					#(p0,p1),(p1,p0),(p0,p2),(p2,p0),(p1,p2),(p2,p1),(p0,p1,p2),(p1,p0,p2).....

					#Create temporary variables for this one query. For 3 pred. we need 2 temp. vars. For n pred, need n-1 vars
					temp_vars = ['?var'+str(i) for i in range(len(predicate_permutation)-1)]

					#So now we have predicates, starting entity and temporary variables. Let's start making the query no
					first_triple = ' '.join([e[i],predicate_permutation[0],temp_vars[0]])
					last_triple = ' '.join([temp_vars[-1],predicate_permutation[-1],v[0]])

					middle_triple_list = []
					for j in range(len(predicate_permutation))[1:-1]:
						middle_triple_list.append(' '.join([temp_vars[j-1],predicate_permutation[j],temp_vars[j]]))

					query_triples = ' . '.join([first_triple]+middle_triple_list+[last_triple])
					sparqls.append(self.sparql_cover % query_triples)

		return sparqls

	def get_answer(self, _sparql_query):
		'''
			Function used to shoot a query and get the answers back. Easy peasy.

			Return - array of values of first variable of query
			NOTE: Only give it queries with one variable
		'''
		print _sparql_query
		#sparql = SPARQLWrapper('http://dbpedia.org/sparql/')
		sparql = SPARQLWrapper('http://131.220.153.66:8900/sparql/')
		sparql.setQuery(_sparql_query)
		sparql.setReturnFormat(JSON)
		try:
			response = sparql.query().convert()
		except:
			print "Whoops!"
			print traceback.print_exc()

		#Now to parse the response
		variables = [x for x in response[u'head'][u'vars']]

		#NOTE: Assuming that there's only one variable
		value = [ x[variables[0]][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings'] ]

		return value	

if __name__ == '__main__':

	e = ['<http://dbpedia.org/resource/Barack_Obama>', '<http://dbpedia.org/resource/India>']
	p = ['<http://dbpedia.org/ontology/region>','<http://dbpedia.org/ontology/largestCity>']
	sparqlgen = SPARQL_Template_Generator(e,p)

	#Results
	print "Number of generated SPARQL templates: ",len(set(sparqlgen.sparqls))
	pprint(sparqlgen.sparqls_answers)
	while True:
		raw_input("Press Enter to see generated SPARQLs at random. Ctrl+C to quit.")
		pprint(random.choice(sparqlgen.sparqls_answers))
