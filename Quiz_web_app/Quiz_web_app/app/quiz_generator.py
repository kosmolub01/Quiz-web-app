import pke
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from nltk.corpus import wordnet as wn
import requests
import re
import random
import string

class QuizGenerator:
    def __init__(self, title, description, text=None, path_to_textfile=None):
        self.title = title
        self.description = description
        self.quiz = {"title": self.title, "description": self.description, "questions": []}

        if path_to_textfile is not None:
            try:
                with open(path_to_textfile, 'r') as file:
                    self.text = file.read()
            except FileNotFoundError:
                print(f"The file {path_to_textfile} was not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
        elif text is not None:
            self.text = text
        else:
            raise ValueError("Provide text to generate the quiz.")

    def _get_important_words(self, art):
        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(input=art, language='en')
        pos = {'PROPN'}
        stops = list(string.punctuation)
        stops += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
        stops += stopwords.words('english')
        extractor.candidate_selection(pos=pos)
        extractor.candidate_weighting()
        result = []
        ex = extractor.get_n_best(n=25)
        for each in ex:
            result.append(each[0])
        return result

    def _split_text_to_sents(self, art):
        s = [sent_tokenize(art)]
        s = [y for x in s for y in x]
        s = [sent.strip() for sent in s if len(sent) > 15]
        return s

    def _map_sents(self, imp_words, sents):
        processor = KeywordProcessor()
        key_sents = {}
        for word in imp_words:
            key_sents[word] = []
            processor.add_keyword(word)
        for sent in sents:
            found = processor.extract_keywords(sent)
            for each in found:
                key_sents[each].append(sent)
        for key in key_sents.keys():
            temp = key_sents[key]
            temp = sorted(temp, key=len, reverse=True)
            key_sents[key] = temp
        return key_sents

    def _get_word_sense(self, sent, word):
        word = word.lower()
        if len(word.split()) > 0:
            word = word.replace(" ", "_")
        synsets = wn.synsets(word, 'n')
        if synsets:
            wup = max_similarity(sent, word, 'wup', pos='n')
            adapted_lesk_output = adapted_lesk(sent, word, pos='n')
            lowest_index = min(synsets.index(wup), synsets.index(adapted_lesk_output))
            return synsets[lowest_index]
        else:
            return None

    def _get_distractors(self, syn, word):
        dists = []
        word = word.lower()
        actword = word
        if len(word.split()) > 0:
            word.replace(" ", "_")
        hypernym = syn.hypernyms()
        if len(hypernym) == 0:
            return dists
        for each in hypernym[0].hyponyms():
            name = each.lemmas()[0].name()
            if name == actword:
                continue
            name = name.replace("_", " ")
            name = " ".join(w.capitalize() for w in name.split())
            if name is not None and name not in dists:
                dists.append(name)
        return dists

    def _get_distractors2(self, word):
        word = word.lower()
        actword = word
        if len(word.split()) > 0:
            word = word.replace(" ", "_")
        dists = []
        url = f"http://api.conceptnet.io/query?node=/c/en/{word}/n&rel=/r/PartOf&start=/c/en/{word}&limit=5"
        obj = requests.get(url).json()
        for edge in obj['edges']:
            link = edge['end']['term']
            url2 = f"http://api.conceptnet.io/query?node={link}&rel=/r/PartOf&end={link}&limit=10"
            obj2 = requests.get(url2).json()
            for edge in obj2['edges']:
                word2 = edge['start']['label']
                if word2 not in dists and actword.lower() not in word2.lower():
                    dists.append(word2)
        return dists

    def generate_quiz(self):
        if self.text is not None:
            imp_words = self._get_important_words(self.text)
            sents = self._split_text_to_sents(self.text)
            mapped_sents = self._map_sents(imp_words, sents)

            mapped_dists = {}
            for each in mapped_sents:
                wordsense = self._get_word_sense(mapped_sents[each][0], each)
                if wordsense:
                    dists = self._get_distractors(wordsense, each)
                    if len(dists) == 0:
                        dists = self._get_distractors2(each)
                    if len(dists) != 0:
                        mapped_dists[each] = dists
                else:
                    dists = self._get_distractors2(each)
                    if len(dists) > 0:
                        mapped_dists[each] = dists

            iterator = 1
            for each in mapped_dists:
                sent = mapped_sents[each][0]
                p = re.compile(each, re.IGNORECASE)
                op = p.sub("________", sent)
                print("Question %s-> "%(iterator),op) #Prints the question along with a question number
                options = [each.capitalize()] + mapped_dists[each]
                options = options[:4]

                question = {
                    "question_text": op,
                    "answer": options[0],
                    "distractors": options[1:]
                }
                self.quiz["questions"].append(question)

                opts = ['a', 'b', 'c', 'd']
                random.shuffle(options)

                for i,ch in enumerate(options):
                    print("\t",opts[i],") ", ch) #Print the options
                    print()

                iterator += 1

            return self.quiz
        else:
            raise ValueError("Quiz Generation Error", "Quiz not generated. First, you need to provide the text to generate the quiz")


if __name__ == "__main__":

    generator = QuizGenerator("Quiz_1", "Sample quiz", path_to_textfile="text.txt")
    generator.generate_quiz()
    print(generator.quiz)
