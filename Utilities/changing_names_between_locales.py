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


def replace_proper_nouns(tsv_in, tsv_out, ref_excel, mapout_file, locale='en'):
    """
    This function will change the names in TSV and generate a new file which
    will contains new names
    tsv_in: The TSV file where the names are to be changed
    tsv_out: The TSV file that will be generated which will contains the
            changed name
    ref_excel: Excel file for the map mapping
    map_fname: This file will contains tab separated two values as the mapping
            from the old name to new name
    Example:
        replace_proper_nouns('wordwindow_level_en.tsv', 'wordwindow_level_en_change.tsv', 'mapping.txt')
    """
    # Reading each line from the mapping file and creating a map for the old name and new name
    # column name for the old name
    if locale == 'en':
        locales = ['en']
    elif locale == 'ur':
        locales = ['en_'+locale, locale, 'audio_'+locale]
    else:
        locales = ['en_'+locale, locale]
    names_dict = dict()
    names_not_used = dict()
    for locale in locales:
        src_key = locale+'_old'
        # key of the target that needed to be changed
        target_key = locale+'_new'
        # Read the Excel sheet to create a dictionary
        wb = xlrd.open_workbook(ref_excel)
        sheet = wb.sheet_by_name("Names_Mapping")
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
        print('Locale: ', locale)
        print(src_key + ': ', old_name_index)
        print(target_key + ': ', new_name_index)
        print('Rows count: ', rowCount)
        print('Columns count: ', colCount)
        # Create a dictionary between the identity key and the new value
        for i in range(1, rowCount):
            old_name = sheet.cell_value(i, old_name_index)
            new_name = sheet.cell_value(i, new_name_index)
            old_names = old_name.split(',')
            new_name = new_name.strip()
            for old_name in old_names:
                old_name = old_name.strip()
                new_name = new_name.strip()
                if len(old_name) > 0 and len(new_name) > 0:
                    names_dict[old_name] = new_name
                    names_not_used[old_name] = True
                    if('en' in locale):
                        names_dict[old_name.lower()] = new_name.lower()
                    if(locale == 'bn'):
                        names_dict[old_name+u'র'] = new_name+u'র'
    # Reading the rows from the SRC TSV file and updating the cells and writing the new cells into DEST TSV file
    with open(tsv_in, 'r',  newline='', encoding='utf-8-sig') as fin, open(tsv_out, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.reader(fin, delimiter='\t', quoting=csv.QUOTE_NONE)
        writer = csv.writer(fout, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
        for line in reader:
            for i in range(len(line)):
                for src_word in names_dict:
                    cell = line[i]
                    cell = regex.sub(r'\b'+src_word+r'\b', names_dict[src_word], cell)
                    if (cell != line[i]):
                        names_not_used[src_word] = False
                    line[i] = cell
            writer.writerow(line)
    print(tsv_out+": Created")
    # Create logs for the mapping that were not used
    with open(mapout_file, 'w', newline='', encoding='utf-8') as mapout:
        for src_word in names_not_used:
            # If the name mapping is not used then log them
            if names_not_used[src_word] is True:
                mapout.write(src_word+'\n')


# Excel file that stores the mapping for the names
mapping_file = 'names_mapping.xlsx'
# Locales of TSVs that needed to be udpated
locale_list = ['ur']
# Source path for the TSVs files
src_path = 'ur_old/'
# Destination path where the updated TSVs will be created
dest_path = 'ur_changed/'
# TSVs that needed to be updated
files = ['eggquizliteracy_levels', 'eggquizmath_levels', 'wordwindow_level']
# Path for the log where unused mapping will be stored
log_path = 'log/'
# Logs for the unused mapping
logs = ['egg_lit_map', 'egg_math_map', 'word_map']

for locale in locale_list:
    log_index = 0
    for file in files:
        replace_proper_nouns(src_path + file + '_' + locale + '.tsv',
                             dest_path + file + '_'+locale + '.tsv',
                             mapping_file,
                             log_path+logs[log_index] + '.txt', locale)
        log_index = log_index + 1
