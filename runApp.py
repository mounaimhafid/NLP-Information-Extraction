"""
Abdelmounaim Hafid axh170730
CS6320.003 NLP
Final Project: Information Extraction
"""
from ner import *

"""
    This program was written by Abdelmounaim Hafid as part of the CS6320 NLP Course.
    It reads in articles from a directory and extracts three relationship templates 
    from the text, with respect to the entities extracted from the text:
        BORN(Person/Organization, Date, Location)
        ACQUIRE(Organization, Organization, Date)
        PART_OF(Organization, Organization)
        PART_OF(Location, Location)
        
        
    In order to run this program call:
        python runApp.py

    There are no arguments required, however, there should be a directory in the same
    directory the file is located called 'articles2'. This directory should have the 
    .txt files that wish to be processed. The program will output json files in a 
    directory called json that shows what has been extracted. The program will also
    output 3 text files, one for each relationship, that shows the relationships and
    the arguments line by line. These .txt files are there for convenience. 
"""

outFile_test_buy2 = open("test_buy2.txt",'w')
outFile_test_born2 = open("test_born2.txt", 'w')
outFile_test_part2 = open("test_part2.txt", 'w')
processFile1(outFile_test_buy2, outFile_test_born2, outFile_test_part2)
outFile_test_part2.close()
outFile_test_buy2.close()
outFile_test_born2.close()
