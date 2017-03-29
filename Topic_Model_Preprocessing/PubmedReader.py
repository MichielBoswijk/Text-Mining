# ------------------------------------------------------------------------------
# PubmedReader class handles the searching of the PubMed database through their
# API (https://www.ncbi.nlm.nih.gov/books/NBK25500/). This class searches
# PubMed using the supplied query, where the placeholders ({}) are replaced 
# by a structure of the supplied list in each iteration. The fetched abstracts  
# are saved in .txt files (one file for each structure) in the supplied location.
# 
# Michiel Boswijk, michiel.boswijk@gmail.com
# University of Amsterdam, Birte Forstmann research group 
# March 2017
# ------------------------------------------------------------------------------

# necessary imports
from Bio import Entrez
import os
import time
import sys
import math
import urllib2

class PubmedReader:

	email = "m.boswijk@uva.nl"     # email necessary to connect with API     
	max_articles = 100000          # number of results returned by PubMed API (100000 covers all) 
	database = "pubmed"            # database accessed
	rettype = "abstract"           # type information retrieved
	retmode = "text"               # format of retrieved info
	url_template =  'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' \
						'db={}&id={}&retmode={}&rettype={}'
	location = "/home/michiel/Desktop/Research Group/MiningProject/Abstracts/"
	batch_size = 100               # number of batches to divide request into

	# --------------------------------------------------------------------------
	# Constructor
	# --------------------------------------------------------------------------

	def __init__(self, query_template, structures, location):
		
		self.pmids =           []
		self.all_abstracts =   []
		self.query_template =  query_template
		self.structures =      structures
		self.location = 	   location
		
		# provide API class with email
		Entrez.email = PubmedReader.email
		
		# calculate progress bar length and increment steps
		n = len(structures)
		progress_format = "[%-" + str(n) + "s] %d%%"
		percentage_step = (1.0 / n) * 100

		# let user know that PubMed is being accessed
		print "Please wait while PubMed is searched and the abstracts are fetched..."

		# iterate the number of structures (one extra time for print statements)
		for idx in range(n + 1):
			# obtain structure and call PubMed as long as index is in range of structure list
			if (idx < n):
				struct = str(structures[idx])
				# build query, search PubMed with query and obtain resulting ids in list
				query = self.query_template.format(struct)
				id_list = self.search(query, PubmedReader.database, PubmedReader.max_articles)
				self.pmids.append(id_list)
				
				# # if results (ids) are found, fetch corresponding abstracts and save them
				# if (len(id_list) > 0):
				# 	structure_abstracts = self.fetch(PubmedReader.url_template, id_list, PubmedReader.database, PubmedReader.retmode, PubmedReader.rettype, PubmedReader.batch_size)
				# 	self.save(struct, structure_abstracts, location)
				# 	self.all_abstracts.append(structure_abstracts)

			# position print writer at beginning of progress bar
			sys.stdout.write('\r')
			# update progress bar each time a result is obtained from PubMed
			sys.stdout.write(progress_format % ('='*idx, round(percentage_step*idx)))
			sys.stdout.flush()
			# add a sleep to avoid overflowing PubMed API service
			time.sleep(1)
		
		# reposition print writer to next line
		print '\nSaved abstracts in ' + location

	# --------------------------------------------------------------------------
	# Helper functions
	# --------------------------------------------------------------------------

	# function searches PubMed with supplied query, returns ids
	def search(self, query, database, max_articles):
		handle = Entrez.esearch(db=database, term=query, retmax=max_articles)
		result = Entrez.read(handle)
		handle.close()
		return result['IdList']

	# function fetches html pages containing abstracts from PubMed  
	def fetch(self, url_template, id_list, database, retmode, rettype, batch_size):
		all_html = ''
		# calculate in how many requests the abstracts are divided based on batch size
		n_divisions = int(math.ceil(len(id_list) / float(PubmedReader.batch_size)))
		# loop number of requests
		for div in range(0, n_divisions):
			# select part of ids, build query and read html    
			id_list_part = ','.join(id_list[(div*batch_size):(div*batch_size) + batch_size])
			query = self.url_template.format(database, id_list_part, retmode, rettype)
			response = urllib2.urlopen(query)
			all_html += response.read()
		return all_html

	# function for saving a file containing all abstracts related to a structure
	def save(self, struct, abstract, location):
		if not os.path.exists(location):
			os.makedirs(location)
		f = open(location + struct + '.txt', 'w+')
		f.write(abstract)
		f.close()

	# function for printing the number of results per structure
	def print_result_count(self):
		total = 0
		for idx, struct in enumerate(self.structures):
			print struct + " : " + str(len(self.pmids[idx])) + " results"
			total += len(self.pmids[idx])
		print str(total) + ' (total)'
