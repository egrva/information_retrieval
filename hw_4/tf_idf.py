import re
import string
import zipfile
from math import log

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

morph = pymorphy2.MorphAnalyzer()


def tokenizator(html):
    page_content = BeautifulSoup(html).get_text()
    result = list(nltk.wordpunct_tokenize(page_content))
    result = minus_znak_prep(result)
    result = list(filter(minus_incorrect_sym, result))
    return result


def minus_znak_prep(values):
    return [i for i in values if all(not j in string.punctuation for j in i)]


def minus_incorrect_sym(word):
    rus = re.compile(r'^[а-яА-Я]{2,}$')
    stop_words = stopwords.words('russian')
    numbers = re.compile(r'^[0-9]+$')
    # signs = re.compile()
    # print(word.lower)
    # if (bool(word.lower() in stop_words)):
    #     print(word.lower())
    res = bool(word.lower() in stop_words) or bool(numbers.match(word)) or not bool(rus.match(word))
    return not res


def get_lemma(word):
    p = morph.parse(word)[0]
    if p.normalized.is_known:
        normal_form = p.normal_form
    else:
        normal_form = word.lower()
    return normal_form


def get_words():
    f = open("/Users/aegorova/Documents/information_retrieval/hw_3/index.txt", "r")
    lines = f.readlines()
    index = dict()
    for line in lines:
        words = re.split('\s+', line)
        index[words[0]] = []
        for i in range(1, len(words) - 1):
            index[words[0]].append(words[i])
    for key, value in index.items():
        index[key] = set(value)
    return index


def get_signs():
    f = open("/Users/aegorova/Documents/information_retrieval/hw_2/lemmas.txt", "r")
    lines = f.readlines()
    signs = set()
    for line in lines:
        words = re.split('\s+', line)
        signs.add(words[0])
    return signs


def get_tf():
    f = open("tf.txt", "r")
    lines = f.readlines()
    tf_dict = dict()
    for line in lines:
        words = re.split('\s+', line)
        ii = words[0]
        for i in range(1, len(words) - 2, 2):
            if ii not in tf_dict:
                tf_dict[ii] = []
            tf_dict[ii].append((words[i], words[i + 1]))
    return tf_dict


def set_tf(tf_dict):
    file = open("tf.txt", "w")
    for word, tf_ in tf_dict.items():
        strings = word + " "
        for tf in tf_:
            strings += " " + tf[0] + " " + str(tf[1])
        strings += "\n"
        file.write(strings)
    file.close()


def compute_tf():
    arch = zipfile.ZipFile('/Users/aegorova/Documents/information_retrieval/hw_1/vykachka.zip', 'r')
    tf_dict = dict()
    for file in arch.filelist:
        tf_dict1 = dict()
        html = arch.open(file.filename)
        html_words = tokenizator(html)
        for word in html_words:
            lemma = get_lemma(word)
            if lemma in tf_dict1.keys():
                tf_dict1[lemma] += 1
            else:
                tf_dict1[lemma] = 1
        for key, value in tf_dict1.items():
            if key not in tf_dict.keys():
                tf_dict[key] = []
            tf = round(value / len(html_words), 6)
            tf_dict[key].append((file.filename, tf))
        print("Done ", file.filename)
    return tf_dict


def get_idf(path):
    f = open(path, "r")
    lines = f.readlines()
    idf_dict = dict()
    for line in lines:
        words = re.split('\s+', line)
        idf_dict[words[0]] = words[1]
    return idf_dict


def set_idf(idf_dict):
    file = open("idf.txt", "w")
    for word, idf in idf_dict.items():
        strings = word + " " + str(idf)
        strings += "\n"
        file.write(strings)
    file.close()


def compute_idf():
    arch = zipfile.ZipFile('/Users/aegorova/Documents/information_retrieval/hw_1/vykachka.zip', 'r')
    num_of_file = len(arch.filelist)
    signs_dict = dict()
    index = get_words()
    for i, j in index.items():
        signs_dict[i] = round(log(num_of_file / len(j)), 6)
    return signs_dict


def set_tfidf(tfidf_dict):
    file = open("tfidf.txt", "w")
    for word, tfidf in tfidf_dict.items():
        # strings = word + " "*(15-len(word))
        strings = word + " "

        for tf in tfidf:
            strings += " " + tf[0] + " " + str(tf[1])
        strings += "\n"
        file.write(strings)
    file.close()


def compute_tfidf():
    arch = zipfile.ZipFile('/Users/aegorova/Documents/information_retrieval/hw_1/vykachka.zip', 'r')
    html_files = list(map(lambda x: x.filename, arch.filelist))
    sort_tf = dict(sorted(get_tf().items()))
    sort_idf = dict(sorted(get_idf("idf.txt").items()))
    tfidf_dict = dict()
    for i, tf_files in sort_tf.items():
        tfidf_dict[i] = []
        tf_files = dict(tf_files)
        for file in html_files:
            if file in tf_files.keys():
                tf = float(tf_files[file])
            else:
                tf = float(0)
            tfidf_dict[i].append((file, tf * float(sort_idf[i])))
    return tfidf_dict


if __name__ == '__main__':
    tf_tf = compute_tf()
    set_tf(tf_tf)
    idf_idf = compute_idf()
    set_idf(idf_idf)
    tfidf_tfidf = compute_tfidf()
    set_tfidf(tfidf_tfidf)