import re
import random

import pke
import requests
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize
from pywsd.lesk import adapted_lesk
from pywsd.similarity import max_similarity
from summarizer import Summarizer

from parrot import Parrot

class QuizGenerator:
    """
    The QuizGenerator class is used to generate a quiz from a given text.
    """

    def __init__(self, title, description, text=None, path_to_textfile=None):
        """
        Initializes a QuizGenerator object.

        Args:
            title (str): The title of the quiz.
            description (str): The description of the quiz.
            text (str, optional): The text to generate the quiz from. Defaults to None.
            path_to_textfile (str, optional): The path to a text file to read the text from. Defaults to None.

        Raises:
            ValueError: If text is not provided.
        """
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
     
    def _paraphrase_the_text(self, summary_target_percentage=0.6):
        """
        Paraphrases the text by generating paraphrases for each sentence in the text.
        If the text is too long, it generates an extractive summary and paraphrases the summary instead.
        
        Parameters:
        - summary_target_percentage (float): The target percentage of sentences to include in the extractive summary.
        
        Returns:
        - paraphrased_text (str): The paraphrased text.
        """
        # Tokenize the input text into sentences.
        sentences = self._split_text_to_sentences(self.text)

        # If the text is too long, generate an extractive summary.
        if len(sentences) > 10:
            model = Summarizer()

            # Calculate the number of sentences needed for the target percentage.
            target_sentences = int(len(sentences) * summary_target_percentage)

            # Generate extractive summary with the specified number of sentences.
            summary = model(self.text, num_sentences=target_sentences)

            # Tokenize the summary text into sentences.
            sentences = self._split_text_to_sentences(summary)

        # Create paraphrases for each sentence in the text.
        parrot = Parrot()
        paraphrased_text = ""

        for sentence in sentences:
            print("Original:", sentence)

            paraphrases = parrot.augment(input_phrase=sentence, do_diverse=True)

            if paraphrases:
                # If the paraphrase is sufficiently different from the original sentence, use it.
                if paraphrases[0][1] > 50:
                    paraphrased_sentence = paraphrases[0][0]

                    print("Paraphrased:", paraphrased_sentence, paraphrases[0][1])

                    # Ensure the paraphrased sentence ends with a space.
                    if not paraphrased_sentence.endswith(" "):
                        # Add a period if the sentence doesn't end with one.
                        if not paraphrased_sentence.endswith("."):
                            paraphrased_sentence += ". "
                        else:
                            paraphrased_sentence += " "
                    # Also, ensure the sentence starts with a capital letter.
                    paraphrased_text += paraphrased_sentence.capitalize()
                else:
                    # Ensure the sentence ends with a space.
                    if not sentence.endswith(" "):
                        sentence += " "
                    print("Same as original:", sentence)
                    paraphrased_text += sentence

                print("") 
            else:
                print("No paraphrases found for sentence:", sentence)
                paraphrased_text += sentence

        return paraphrased_text

    def _get_keyphrases(self, text):
        """
        Extracts keyphrases from a given text using MultipartiteRank algorithm.

        Args:
            art (str): The input text.

        Returns:
            list: A list of the 3 most important words extracted from the text.
        """
        # Initialize MultipartiteRank extractor.
        extractor = pke.unsupervised.MultipartiteRank()

        # Load the document into the extractor.
        extractor.load_document(input=text, language='en')

        # Define the part-of-speech tags to consider.
        pos = {'PROPN', 'NOUN'}

        # Select the candidates based on the defined part-of-speech tags.
        extractor.candidate_selection(pos=pos)

        # Weight the candidates.
        extractor.candidate_weighting()

        # Initialize the result list.
        keyphrases = []

        # Get the 3 best keyphrases with score.
        keyphrases_with_score = extractor.get_n_best(n=3)

        # Append each candidate to the result list.
        for keyphrase_with_score in keyphrases_with_score:
            keyphrases.append(keyphrase_with_score[0])

        return keyphrases

    def _split_text_to_sentences(self, text):
        """
        Splits the given text into sentences.

        Args:
            text (str): The text to be split into sentences.

        Returns:
            list: A list of sentences extracted from the text.

        """
        # Split the text into sentences.
        sentences = sent_tokenize(text)

        # Strip whitespace from each sentence.
        sentences = [sentence.strip() for sentence in sentences]  

        # Filter out short sentences e.g. sentences like "Yes.", "No.", "Maybe.", "I see.", etc. 
        # that are technically valid sentences, but they don't provide much context or information.
        sentences = [sentence for sentence in sentences if len(sentence) > 15] 

        return sentences
 
    def _get_word_sense(self, sentence, word):
        """
        Get the WordNet sense of a given word in a sentence.

        Args:
            sentence (str): The sentence containing the word.
            word (str): The word to find the sense for.

        Returns:
            nltk.corpus.reader.wordnet.Synset or None: The WordNet synset with the lowest index
            among the synsets of the word, or None if no synsets are found.
        """
        # Convert the word to lowercase.
        word = word.lower()

        # If the word is a phrase, replace spaces with underscores.
        if len(word.split()) > 0:
            word = word.replace(" ", "_")

        # Get the synsets of the word.
        synsets = wn.synsets(word, 'n')

        # If there are synsets.
        if synsets:
            # Get the synset with the highest similarity to the word using Wu-Palmer Similarity.
            wup = max_similarity(sentence, word, 'wup', pos='n')

            # Get the synset with the highest similarity to the word using Adapted Lesk.
            adapted_lesk_output = adapted_lesk(sentence, word, pos='n')

            # Check if wup and adapted_lesk_output are in synsets before getting their index.
            if wup in synsets and adapted_lesk_output in synsets:
                # Get the index of the synset with the lowest index between wup and adapted_lesk_output.
                lowest_index = min(synsets.index(wup), synsets.index(adapted_lesk_output))
            else:
                # If neither wup nor adapted_lesk_output are in synsets, use the first synset as default.
                lowest_index = 0  # or any default value

            # Return the synset with the lowest index.
            return synsets[lowest_index]
        else:
            # If there are no synsets, return None.
            return None

    def _get_distractors_word_net(self, synset, word):
        """
        Get distractors for a given word using WordNet.

        Args:
            synset (WordNetSynset): The synset object representing the word.
            word (str): The word for which distractors are to be generated.

        Returns:
            list: A list of distractor words.

        """
        # Initialize an empty list for distractors.
        distractors = []

        # Convert the word to lowercase.
        word = word.lower()
        actword = word

        # Replace spaces with underscores if the word is a phrase.
        if len(word.split()) > 0:
            word.replace(" ", "_")

        # Get the hypernyms of the word.
        hypernym = synset.hypernyms()

        # If there are no hypernyms, return an empty list.
        if len(hypernym) == 0:
            return distractors

        # For each hyponym of the first hypernym.
        for each in hypernym[0].hyponyms():
            # Get the name of the first lemma.
            name = each.lemmas()[0].name()

            # If the name is the same as the original word, skip it.
            if name == actword:
                continue

            # Replace underscores with spaces in the name.
            name = name.replace("_", " ")

            # If the name is not None and not already in the list, add it to the list.
            if name is not None and name not in distractors:
                distractors.append(name)

        return distractors

    def _get_distractors_concept_net(self, word):
        """
        Retrieves distractors for a given word using the ConceptNet API.

        Args:
            word (str): The word for which distractors are to be retrieved.

        Returns:
            list: A list of distractor words.

        """
        # Convert the word to lowercase.
        word = word.lower()
        actword = word

        # Replace spaces with underscores if the word is a phrase.
        if len(word.split()) > 0:
            word = word.replace(" ", "_")

        # Initialize an empty list for distractors.
        distractors = []

        # Define the URL for the ConceptNet API request.
        url = f"http://api.conceptnet.io/query?node=/c/en/{word}/n&rel=/r/PartOf&start=/c/en/{word}&limit=5"

        # Send the request and get the response in JSON format.
        obj = requests.get(url).json()

        # For each edge in the response.
        for edge in obj['edges']:
            # Get the term at the end of the edge.
            link = edge['end']['term']

            # Define the URL for the second ConceptNet API request.
            url2 = f"http://api.conceptnet.io/query?node={link}&rel=/r/PartOf&end={link}&limit=10"

            # Send the second request and get the response in JSON format.
            obj2 = requests.get(url2).json()

            # For each edge in the second response.
            for edge in obj2['edges']:
                # Get the label at the start of the edge.
                word2 = edge['start']['label']

                # If the label is not already in the list and the original word is not in the label, add it to the list.
                if word2 not in distractors and actword.lower() not in word2.lower():
                    distractors.append(word2)

        return distractors
    
    def _get_antonym(self, word):
            """
            Retrieves the antonym of a given word using WordNet.

            Parameters:
            word (str): The word for which the antonym is to be retrieved.

            Returns:
            str or None: The antonym of the given word, or None if no antonym is found.
            """
            # Get the sets of synonyms of the word.
            synsets = wn.synsets(word)
            if synsets:
                # Get the first lemma (dictionary form of a word) of the first synset.
                lemmas = synsets[0].lemmas()
                if lemmas:
                    if lemmas[0].antonyms():
                        return lemmas[0].antonyms()[0].name()
            return None
        
    def generate_quiz(self):
            """
            Generates a quiz based on the provided text.

            Returns:
                dict: A dictionary containing the generated quiz.
            Raises:
                ValueError: If the text is not provided.
            """

            if self.text is not None:
                paraphrased_text = self._paraphrase_the_text()
                print("paraphrased_text: ", paraphrased_text)

                sentences = self._split_text_to_sentences(paraphrased_text)

                # Dictionary to map keywords to sentences.
                mapped_sentences = {}

                # Dictionary to map keywords to distractors.
                distractors = {}

                # Extract keywords from each sentence and map them to the sentence.
                iterator = 1
                for sentence in sentences:
                    print(f"sentence {iterator}: {sentence}")
                    keywords = self._get_keyphrases(sentence)
                    print(f"keywords: {keywords}")
                    if keywords:
                        mapped_sentences[keywords[0]] = sentence

                    iterator += 1

                # Find distractors and antonyms for every keyword.
                for keyword, sentence in mapped_sentences.items():
                    # Get the word sense for the keyword.
                    wordsense = self._get_word_sense(sentence, keyword)
                    if wordsense:
                        dists = self._get_distractors_word_net(wordsense, keyword)
                        if len(dists) == 0:
                            dists = self._get_distractors_concept_net(keyword)
                        if len(dists) != 0:
                            # Filter out the correct answer from distractors.
                            dists = [d for d in dists if d.lower() != keyword.lower()]
                            distractors[keyword] = dists
                    else:
                        dists = self._get_distractors_concept_net(keyword)
                        if len(dists) > 0:
                            # Filter out the correct answer from distractors.
                            dists = [d for d in dists if d.lower() != keyword.lower()]
                            distractors[keyword] = dists

                    if len(dists) == 0:
                        distractors[keyword] = "No distractors"
                   
                for keyword, sentence in mapped_sentences.items():
                    print(f"keyword: {keyword}")
                    print(f"sentence: {sentence}")
                    print(f"distractors: {distractors[keyword]}")

                # Generate the quiz. 
                # Formulate the questions and options for those keywords which have at least 2 distractors.
                iterator = 1
                for keyword in distractors:
                    # Get the antonym for the keyword.                   
                    antonym = self._get_antonym(keyword)
                    
                    dists = distractors[keyword]
                    
                    if len(dists) > 1 and isinstance(dists, list):
                        sent = mapped_sentences[keyword]
                        p = re.compile(keyword, re.IGNORECASE)
                        op = p.sub("________", sent)
                        print("Question %s-> " % (iterator), op)  # Prints the question along with a question number.
                        if antonym:
                            print("antonym", antonym)
                            options = [keyword] + [antonym] + dists
                        else:
                            options = [keyword] + dists
                        options = options[:4]

                        question = {
                            "question_text": op,
                            "answer": options[0],
                            "distractors": options[1:]
                        }
                        self.quiz["questions"].append(question)

                        opts = ['a', 'b', 'c', 'd']
                        random.shuffle(options)

                        for i, ch in enumerate(options):
                            print("\t", opts[i], ") ", ch)  # Print the options
                            print()

                        iterator += 1

                return self.quiz
            
            else:
                raise ValueError("Quiz Generation Error", "Quiz not generated. First, you need to provide the text to generate the quiz")

if __name__ == "__main__":
    generator = QuizGenerator("Quiz_1", "Sample quiz", path_to_textfile="text.txt")
    generator.generate_quiz()
