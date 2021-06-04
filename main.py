"""
Abdelmounaim Hafid axh170730
CS6320.003 NLP
Final Project: Information Extraction
"""
from ner import *

#Task1
outFile_test_buy = open("test_buy.txt",'w')
outFile_test_born = open("test_born.txt", 'w')
outFile_test_part = open("test_part.txt", 'w')
processFile2(outFile_test_buy, outFile_test_born, outFile_test_part)
outFile_test_born.close()
outFile_test_part.close()
outFile_test_part.close()


#Task2,3
outFile_test_buy2 = open("test_buy2.txt",'w')
outFile_test_born2 = open("test_born2.txt", 'w')
outFile_test_part2 = open("test_part2.txt", 'w')
processFile1(outFile_test_buy2, outFile_test_born2, outFile_test_part2)
outFile_test_part2.close()
outFile_test_buy2.close()
outFile_test_born2.close()
