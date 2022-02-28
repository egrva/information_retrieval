import re
import string
import zipfile
from functools import cmp_to_key
import pymorphy2
import nltk
from bs4 import BeautifulSoup


class WordsCount:
    def __init__(self):
        self.documents = []
        self.general_count = 0

    def append_document_info(self, document_number, document_word_count):
        self.documents.append(document_number)
        self.general_count += document_word_count


def tokenizator(html):
    page_content = BeautifulSoup(html, features="html.parser").get_text()
    result = list(nltk.wordpunct_tokenize(page_content))
    return result


def minus_znak_prep(values):
    return [i for i in values if all(not j in string.punctuation for j in i)]


def minus_incorrect_sym(word):
    rus = re.compile(r'^[а-яА-Я]{2,}$')
    numbers = re.compile(r'^[0-9]+$')
    res = bool(rus.match(word)) or bool(numbers.match(word))
    return res


def get_lemma(word):
    p = pymorphy2.MorphAnalyzer().parse(word)[0]
    if p.normalized.is_known:
        normal_form = p.normal_form
    else:
        normal_form = word.lower()
    return normal_form


def get_lemmatizator():
    f = open("/Users/aegorova/Documents/information_retrieval/hw_2/lemmas.txt", "r")
    lines = f.readlines()
    map = dict()
    for line in lines:
        key = None
        words = re.split('\s+', line)
        for i in range(len(words) - 1):
            if i == 0:
                key = words[i]
                map[key] = []
            else:
                map[key].append(words[i])
    return map


def get_doc_id(filename):
    id = ""
    for letter in filename:
        if letter.isdigit():
            id += letter
    return int(id)


def sort_id(id):
    def comparator(x, y):
        return x[1].general_count - y[1].general_count

    return dict(sorted(id.items(), key=cmp_to_key(comparator), reverse=True))


def find_word_f(map):
    arch = zipfile.ZipFile('/Users/aegorova/Documents/information_retrieval/hw_1/vykachka.zip', 'r')
    index = dict()
    for file in arch.filelist:
        html = arch.open(file.filename)
        html_word_list = tokenizator(html)
        word_used = set()
        for word in html_word_list:
            lemma = get_lemma(word)
            if lemma in map.keys() and lemma not in word_used:
                word_used.add(lemma)
                similar_words = map[lemma]
                count = 0
                for similar_word in similar_words:
                    count += html_word_list.count(similar_word)
                if lemma not in index.keys():
                    index[lemma] = WordsCount()
                index[lemma].append_document_info(file.filename, count)
        print(file.filename, "finished")
    return dict(sorted(index.items()))


def set_answers(index):
    file = open("index.txt", "w")
    for word, doc_info in index.items():
        file_string = word + " "
        for doc in doc_info.documents:
            file_string += " " + str(doc)
        file_string += "\n"
        file.write(file_string)
    file.close()


def create_index():
    map = get_lemmatizator()
    index = find_word_f(map)
    sorted_index = sort_id(index)
    set_answers(sorted_index)


def read_index():
    f = open("index.txt", "r")
    lines = f.readlines()
    map = dict()
    for line in lines:
        words = re.split('\s+', line)
        key = words[0]
        if not key in map.keys():
            map[key] = set()
        for i in range(1, len(words) - 1):
            map[key].add(words[i])
    return map


def boolean_search(query, index):
    query_words = re.split('\s+', query)
    page_crossing = set()
    token_query = set(map(lambda x: get_lemma(x), query_words))
    for word in token_query:
        page_crossing = page_crossing | index[word]
    print(page_crossing)


if __name__ == '__main__':
    create_index()
    boolean_search("изумрудные", read_index())
