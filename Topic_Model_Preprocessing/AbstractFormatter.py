# ------------------------------------------------------------------------------
# AbstractFormatter class handles the formatting of the abstracts obtained
# by PubMed. Initially, the abstracts are in a single text file per structure.
# The class can be used to extract specific information from the abstracts
# (like headers, titles, authors, etc), and will return the abstracts in 3
# possible ways: with all information, only the abstract text, or N-words 
# surrounding the structure keyword.
#
# Michiel Boswijk, michiel.boswijk@gmail.com
# University of Amsterdam, Birte Forstmann research group 
# March 2017
# ------------------------------------------------------------------------------

class AbstractFormatter:

    empty_placeholder = '-1'    # placeholder for all empty elements
    abstract_threshold = 100    # minimum number of characters for an abstract

    # --------------------------------------------------------------------------
	# Constructor
	# --------------------------------------------------------------------------

    def __init__(self, location, structure):

        f = open(location + structure + '.txt')
        # split abstracts (all abstract information) individually in a local variable list
        self.abstracts = f.read().split(' [Indexed for MEDLINE]\n\n')[:-1]
        # save structure into local variable
        self.structure = structure
        f.close()

    # --------------------------------------------------------------------------
	# Getter functions
	# --------------------------------------------------------------------------

    # function for obtaining headers
    def get_headers(self):
        # header is cleaned version of 1st paragraph
        return [self.clean_text(a.split('\n\n')[0]) for a in self.abstracts]

    # function for obtaining titles
    def get_titles(self):
        # first clean title section (2nd paragraph), then handle titles between brackets
        titles_raw = [self.clean_text(a.split('\n\n')[1]) for a in self.abstracts]
        return [a[1:-2] + '.' if (a[0] == '[' and a[-2] == ']') else a for a in titles_raw]

    # function for obtianing dois
    def get_dois(self):
        # if DOI is in the text, it will be the first line of the last paragraph
        return [a.split('\n\n')[-1].split('\n')[0] if 'DOI:' in a else AbstractFormatter.empty_placeholder for a in self.abstracts]

    # function for obtaining pmcids
    def get_pmcids(self):
        pmcids = []
        for a in self.abstracts:
            id_section = a.split('\n\n')[-1] # last paragraph contains IDs
            if 'PMCID:' in id_section:
                # extract until PMID (PMID always follows PMCID)
                pmcids.append(id_section[id_section.find('PMCID:'):id_section.find('\nPMID:')])
            else:
                pmcids.append(AbstractFormatter.empty_placeholder)
        return pmcids

    # function for obtaining pmids
    def get_pmids(self):
        pmids = []
        for a in self.abstracts:
            id_section = a.split('\n\n')[-1] # last paragraph contains IDs
            if 'PMID:' in id_section:
                # extract until [Indexed for MEDLINE] (it always follows PMID)
                pmids.append(id_section[id_section.find('PMID:'):id_section.find('[Indexed for MELDINE]')])
            else:
                pmids.append(AbstractFormatter.empty_placeholder)
        return pmids

    # function for obtaining author information
    def get_author_info(self):
        author_info = []
        for a in self.abstracts:
            if 'Author information' in a:
                a = a[a.find('Author information:'):]
                # extract until next paragraph
                author_info.append(a[a.find('Author information:'):a.find('\n\n')].replace('\n', ' '))
            else:
                author_info.append(AbstractFormatter.empty_placeholder)
        return author_info

    # function for obtaining authors
    def get_authors(self):
        authors = []
        for a in self.abstracts:
            if '[Article in' in a:
                # remove everything above the [Article in .. achor
                a = a[a.find('[Article in'):]
                # authors are now 2nd paragraph from the top
                authors.append(a.split('\n\n')[1].replace('\n', ' '))
            elif 'Author information' in a:
                # extract everything until author info
                a = a[0:a.find('Author information')]
                # authors are now the paragraph before the last one
                authors.append(a.split('\n\n')[-2].replace('\n', ' '))
            else:
                authors.append(a.split('\n\n')[2].replace('\n', ' '))
        return authors

    # function for obtaining abstracts
    def get_abstracts(self, mode, word_list):

        abstract_texts = []
        if mode == -1:
            for abstract in self.abstracts:
                # initialize variables for max text length and the final abstract
                max_len = 0
                single_abstract = ''
                # split into paragraphs
                sections = abstract.split('\n\n')
                # select the section with the maximum length (exclude author info and doi sections)
                for sec in sections:
                    if ((len(sec) > max_len) and (not ('Author information:' in sec)) and (not ('PMID:' in sec))):
                        max_len = len(sec)
                        single_abstract = sec
                # if the abstract is too short, replace with empty indicatpr
                if max_len < AbstractFormatter.abstract_threshold:
                    single_abstract = AbstractFormatter.empty_placeholder
                abstract_texts.append(single_abstract)
        else:
            abstract_texts = []

        return abstract_texts

    # --------------------------------------------------------------------------
	# Helper functions
	# --------------------------------------------------------------------------

    # function for formatting the texts so it can be used by the word2vec method
    def word2vec_format(self, abstracts, structure):
        sentences = []
        if(len(abstracts) > 0):
            for abstr in abstracts:
                # convert to lower case and replace structure keyword with a version with underscores for spaces
                abstr = abstr.lower().replace(structure.lower(), structure.lower().replace(' ', '_'))
                # one sentence is an abstract/text split into individual words
                sentences.append(abstr.split(' '))
        return sentences

    # function for cleaning text from newline characters and spaces
    def clean_text(self, text):
        junk = ['\n\n', '\n', '   ', '  ']
        for j in junk:
            text = text.replace(j, ' ')
        return text.strip()

    # function for printing a comparison between number of valid options versus empty/invalid ones
    def print_result_info(self, mode):
        print '<Total Count> / <Invalid Count>\n----------\nHeaders:'
        print str(len(self.get_headers()))      + ' / ' + str(len([header for header in self.get_headers() if header == AbstractFormatter.empty_placeholder]))
        print '----------\nTitles: '
        print str(len(self.get_titles()))       + ' / ' + str(len([title for title in self.get_titles() if title == AbstractFormatter.empty_placeholder]))
        print '----------\nDOIs: '
        print str(len(self.get_dois()))         + ' / ' + str(len([doi for doi in self.get_dois() if doi == AbstractFormatter.empty_placeholder]))
        print '----------\nPMCIDS: '
        print str(len(self.get_pmcids()))       + ' / ' + str(len([pmcid for pmcid in self.get_pmcids() if pmcid == AbstractFormatter.empty_placeholder]))
        print '----------\nPMIDS: '
        print str(len(self.get_pmids()))        + ' / ' + str(len([pmid for pmid in self.get_pmids() if pmid == AbstractFormatter.empty_placeholder]))
        print '----------\nAuthor info: '
        print str(len(self.get_author_info()))  + ' / ' + str(len([info for info in self.get_author_info() if info == AbstractFormatter.empty_placeholder]))
        print '----------\nAuthors: '
        print str(len(self.get_authors()))      + ' / ' + str(len([author for author in self.get_authors() if author == AbstractFormatter.empty_placeholder]))
        print '----------\nAbstracts: '
        print str(len(self.get_abstracts(mode, False)))   + ' / ' + str(len([abstract for abstract in self.get_abstracts(mode, False) if len(abstract) < AbstractFormatter.abstract_threshold]))
        print '----------'
