import csv
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import nltk
import codecs,cStringIO
import io

def getProperNouns(fin_fname, fout_fname):
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    propernouns = set()
    with open(fin_fname) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            isSentence = False
            for cell in row:
                    sentence = cell.replace('^',' ')
                    sentence = sentence.replace('_','')
                    token = word_tokenize(sentence)
                    #print sentence
                    #tagged_sent = pos_tag(sentence.split())
                    tagged_sent = pos_tag(token)
                    for word,pos in tagged_sent:
                        if pos == 'NNP':
                            word = word.replace("'s",'')
                            if word.isalpha():
                                propernouns.add(word)
        print propernouns
        with open(fout_fname, 'w') as f:
            for item in propernouns:
                print >> f, item

def mergeProperNounsFiles(fin_files, fout_file):
    propernouns = set()
    for file in fin_files:
        f = open(file,"r").readlines()
        for line in f:
            word = line.strip()
            propernouns.add(word)
    print propernouns
    with open(fout_file, 'w') as f:
        for item in propernouns:
            print >> f, item

def replaceProperNouns(tsv_in, tsv_out, map_fname):
    f_indian =  io.open(map_fname,'r',encoding='utf-8').readlines()
    names_dict = dict()
    for line in f_indian:
        src_word, dst_word = line.split('\t')
        src_word = src_word.strip()
        dst_word = dst_word.strip()
        names_dict[src_word]=dst_word
    #print names_dict

    class UTF8Recoder:
        def __init__(self, f, encoding):
            self.reader = codecs.getreader(encoding)(f)
        def __iter__(self):
            return self
        def next(self):
            return self.reader.next().encode("utf-8")

    class UnicodeReader:
        def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
            f = UTF8Recoder(f, encoding)
            self.reader = csv.reader(f, dialect=dialect, **kwds)
        def next(self):
            '''next() -> unicode
            This function reads and returns the next line as a Unicode string.
            '''
            row = self.reader.next()
            return [unicode(s, "utf-8") for s in row]
        def __iter__(self):
            return self

    class UnicodeWriter:
        def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
            self.queue = cStringIO.StringIO()
            self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()
        def writerow(self, row):
            '''writerow(unicode) -> None
            This function takes a Unicode string and encodes it to the output.
            '''
            self.writer.writerow([s.encode("utf-8") for s in row])
            data = self.queue.getvalue()
            data = data.decode("utf-8")
            data = self.encoder.encode(data)
            self.stream.write(data)
            self.queue.truncate(0)

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)

    with open(tsv_in,'rb') as fin, open(tsv_out,'wb') as fout:
        reader = UnicodeReader(fin,delimiter='\t',quoting=csv.QUOTE_NONE)
        writer = UnicodeWriter(fout,delimiter='\t',quotechar='',quoting=csv.QUOTE_NONE)
        for line in reader:
            length= len(line)
            if length> 0:
                for i in range(length):
                    for src_word in names_dict:
                        cell = line[i].replace(src_word, names_dict[src_word])
                        line[i]=cell.strip()
                #print line
                #print length
                writer.writerow(line)

#getProperNouns('eggquizliteracy_levels_en.tsv','propernouns3.txt')
#mergeProperNounsFiles(["propernouns.txt", "propernouns2.txt"], 'merged_names2.txt')
#replaceProperNouns('wordwindow_level_en.tsv', 'wordwindow_level_en_change.tsv', 'mapping.txt')