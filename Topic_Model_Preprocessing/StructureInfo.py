# ------------------------------------------------------------------------------
# StructureInfo class handles reading in the .xlsx file containing all
# subcortical structures to research. Using this class, one is able to
# extract specific types of information from the .xlsx file. Specifically:
# the name of the structure, its abbreviations, the scan_type used for the 
# structure, the type of data available using this scan_type, synonyms, and  
# some extra unstructured information.
#
# Michiel Boswijk, michiel.boswijk@gmail.com
# University of Amsterdam, Birte Forstmann research group 
# March 2017
# ------------------------------------------------------------------------------

# necessary imports
from openpyxl import load_workbook
import pandas as pd

class StructureInfo:

    # load data from excel file with all information
    wb = load_workbook(filename = 'SubcorticalStructures.xlsx')
    sheet_ranges = wb['Sheet1']

    # define cell-range with relevant data in the excel file
    first_index = 2
    last_index = 34

    # --------------------------------------------------------------------------
    # Constructor
    # --------------------------------------------------------------------------

    def __init__(self):
        
        self.structures =        []
        self.abbreviations =     []
        self.scan_types =        []
        self.available_data =    []
        self.synonyms =          []
        self.extra_info =        []

        # obtain select specific data from the excel file
        for i in range(StructureInfo.first_index, StructureInfo.last_index + 1):
            cell_id = 'A' + str(i)
            struct =    StructureInfo.sheet_ranges[cell_id].value
            cell_id = 'B' + str(i)
            abbr =      StructureInfo.sheet_ranges[cell_id].value
            cell_id = 'C' + str(i)
            scan_type = StructureInfo.sheet_ranges[cell_id].value
            cell_id = 'D' + str(i)
            data =      StructureInfo.sheet_ranges[cell_id].value
            cell_id = 'E' + str(i)
            syn =       StructureInfo.sheet_ranges[cell_id].value
            cell_id = 'F' + str(i)
            info =      StructureInfo.sheet_ranges[cell_id].value

            # save selected date in lists as string (instead of unicode)
            self.structures.append(str(struct))
            self.abbreviations.append(str(abbr))
            self.scan_types.append(str(scan_type))
            self.available_data.append(str(data))
            self.synonyms.append(str(syn))
            self.extra_info.append(str(info))

        # create dataframe from selection
        data = {'structure':        self.structures,
                'abbreviation':     self.abbreviations,
                'scan type':        self.scan_types,
                'available data':   self.available_data,
                'synonyms':         self.synonyms,
                'extra info':       self.extra_info}
        structure_df = pd.DataFrame(data)

    # def get_structures(self):
    #     return structures

    # def get_abbreviations(self):
    #     return abbreviations

    # def get_scan_types(self):
    #     return scan_types

    # def get_structures(self):
    #     return structures

    # def get_structures(self):
    #     return structures