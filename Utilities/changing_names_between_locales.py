""""
This script contains functions which help in creating txt file which contains
proper nouns from tsv, merging proper nouns txt files, and to rename names in TSVs
"""
import csv
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import nltk
import io
import regex
import xlrd

def get_proper_nouns(fin_fname, fout_fname):
    """
    This function get all the possible proper nouns from the TSV file and list
    them in the the output file.
    fin_fname: TSV file for the proper nouns
    fout_fname: output file for the listing proper nouns(not in append mode)
                [*.txt file]
    Example:
        get_proper_nouns('eggquizliteracy_levels_en.tsv','propernouns3.txt')
    """
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    proper_nouns = set()
    # Read the sentences from the TSV and use NLTK Tagger to tag each of the word
    with open(fin_fname, encoding="utf8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            for cell in row:
                    sentence = cell.replace('^', ' ').replace('_', '')
                    token = word_tokenize(sentence)
                    # tagged_sent = pos_tag(sentence.split())
                    tagged_sent = pos_tag(token)
                    for word, pos in tagged_sent:
                        if pos == 'NNP':
                            word = word.replace("'s", '')
                            if word.isalpha():
                                propernouns.add(word)
        # List of proper nouns
        print(propernouns)
        # Creating a new file named fout_fname to store proper nouns
        with open(fout_fname, 'w', encoding="utf8") as f:
            for item in propernouns:
                print(item, file=f)


def merge_proper_nouns_files(fin_files, fout_file):
    """
    This function get all the  proper nouns and generate fout_file file which
    will contains all the unique proper nouns
    fin_files: List of the files which contains proper nouns
    fout_file: Output file which will finally contains proper nouns(not opened
    in append mode)[*.txt file]
    Example:
        merge_proper_nouns_files(["propernouns.txt", "propernouns2.txt"], 'merged_names2.txt')
    """
    proper_nouns = set()
    # Reading each of the proper nouns from the each of the txt file
    for file in fin_files:
        f = open(file, "r", encoding="utf8").readlines()
        for line in f:
            word = line.strip()
            propernouns.add(word)
    # Creating a new file which stores all the unique proper nouns
    print(propernouns)
    with open(fout_file, 'w', encoding="utf8") as f:
        for item in propernouns:
            print(item, file=f)


def replace_proper_nouns(tsv_in, tsv_out, ref_excel, sheet_name="Sheet1"):
    """
    This function will change the names in TSV and generate a new file which
    will contains new names
    tsv_in: The TSV file where the names are to be changed
    tsv_out: The TSV file that will be generated which will contains the
            changed name
    map_fname: This file will contains tab separated two values as the mapping
            from the old name to new name
    Example:
        replace_proper_nouns('wordwindow_level_en.tsv', 'wordwindow_level_en_change.tsv', 'mapping.txt')
    """
    # Reading each line from the mapping file and creating a map for the old name and new name
    # column name for the old name
    locales = ['en', 'hi']
    names_dict = dict()
    for locale in locales:
        src_key = locale+'_old'
        # key of the target that needed to be changed
        target_key = locale+'_new'
        # Read the Excel sheet to create a dictionary
        wb = xlrd.open_workbook(ref_excel)
        sheet = wb.sheet_by_name(sheet_name)
        rowCount = sheet.nrows
        colCount = sheet.ncols
        # Get the column index of identity and new title column in Excel
        old_name_index = -1
        new_name_index = -1
        for i in range(colCount):
            if old_name_index == -1 and src_key == sheet.cell_value(0, i):
                old_name_index = i
            if new_name_index == -1 and target_key == sheet.cell_value(0, i):
                new_name_index = i
            if old_name_index != -1 and new_name_index != -1:
                break
        print('Sheet: ', sheet_name)
        print('old_name_index: ', old_name_index)
        print('new_name_index: ', new_name_index)
        print('Rows count: ', rowCount)
        print('Columns count: ', colCount)
        # Create a dictionary between the identity key and the new value
        for i in range(1, rowCount):
            old_name = sheet.cell_value(i, old_name_index)
            new_name = sheet.cell_value(i, new_name_index)
            old_name = old_name.strip()
            new_name = new_name.strip()
            if len(old_name) > 0 and len(new_name):
                names_dict[old_name] = new_name
                if(locale == 'en'):
                    names_dict[old_name.lower()] = new_name.lower()

    # Reading the rows from the SRC TSV file and updating the cells and writing the new cells into DEST TSV file
    with open(tsv_in, 'r',  newline='', encoding='utf-8-sig') as fin, open(tsv_out, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.reader(fin, delimiter='\t', quoting=csv.QUOTE_NONE)
        writer = csv.writer(fout, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
        for line in reader:
            for i in range(len(line)):
                if(line[i] == u"image_word" or line[i] == u"soundonly_word"):
                    break
                for src_word in names_dict:
                    cell = line[i]
                    cell = regex.sub(r'(?u)\b'+src_word+r'(?u)\b', names_dict[src_word], cell)
                    line[i] = cell
            writer.writerow(line)


mapping_file = 'ProposedNames.xlsx'
locale_list = ['en', 'hi']
for locale in locale_list:
    replace_proper_nouns('original/eggquizliteracy_levels_' + locale + '.tsv', 'test_changed/eggquizliteracy_levels_' + locale + '.tsv', mapping_file)
    replace_proper_nouns('original/eggquizmath_levels_' + locale + '.tsv', 'test_changed/eggquizmath_levels_' + locale + '.tsv', mapping_file)
    replace_proper_nouns('original/wordwindow_level_' + locale + '.tsv', 'test_changed/wordwindow_level_' + locale + '.tsv',  mapping_file)
