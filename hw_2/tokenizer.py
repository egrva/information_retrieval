import re
import string
import zipfile

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

morph = pymorphy2.MorphAnalyzer()


def read_file(zip_file, f):
    html = zip_file.open(f)
    return html


def set_tokenizer_result(result):
    index_html = open("tokens.txt", "a")
    pattern = "%s\n"
    for word in result:
        index_html.write(pattern % word)
    index_html.close()


def tokenizer(html):
    page_content = BeautifulSoup(html).get_text()
    result = list(nltk.wordpunct_tokenize(page_content))
    result = minus_sign_prep(result)
    result = list(filter(minus_incorrect_symbol, result))
    return result


def minus_sign_prep(values):
    return [i for i in values if all(not j in string.punctuation for j in i)]


def minus_incorrect_symbol(word):
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


def lemmatizer(tokenizer_res):
    lemmatizer_arr = dict()
    for word in tokenizer_res:
        normal_form = get_lemma(word)
        if not normal_form in lemmatizer_arr:
            lemmatizer_arr[normal_form] = []
        lemmatizer_arr[normal_form].append(word)
    return lemmatizer_arr


def set_lemmatizer_res(lemmatizer_res):
    f_lemma = open("lemmas.txt", "a")
    for lemma, tokens in lemmatizer_res.items():
        f_words = lemma + " "
        for token in tokens:
            f_words += token + " "
        f_words += "\n"
        f_lemma.write(f_words)
    f_lemma.close()


if __name__ == '__main__':
    zip = zipfile.ZipFile('/Users/aegorova/Documents/information_retrieval/hw_1/vykachka.zip', 'r')
    tokenizer_res = set()
    for f in zip.filelist:
        page_html = read_file(zip, f.filename)
        token_file = set(tokenizer(page_html))
        tokenizer_res = tokenizer_res | token_file
        print(f.filename, "finished")
    set_tokenizer_result(tokenizer_res)
    lemmatizer_res = lemmatizer(tokenizer_res)
    set_lemmatizer_res(lemmatizer_res)
    # print(stopwords.words('russian'))




