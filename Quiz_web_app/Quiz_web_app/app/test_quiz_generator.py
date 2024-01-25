import unittest
from quiz_generator import QuizGenerator

class QuizGeneratorTests(unittest.TestCase):

    def setUp(self):
        self.quiz_generator = QuizGenerator("Test Quiz", "This is a test quiz", text="This is a test text.")

    def test_quiz_generator_initialization(self):
        self.assertEqual(self.quiz_generator.title, "Test Quiz")
        self.assertEqual(self.quiz_generator.description, "This is a test quiz")
        self.assertEqual(self.quiz_generator.text, "This is a test text.")

    def test_quiz_generator_paraphrase_the_text(self):
        paraphrased_text = self.quiz_generator._paraphrase_the_text()
        self.assertIsInstance(paraphrased_text, str)

    def test_quiz_generator_get_keyphrases(self):
        keyphrases = self.quiz_generator._get_keyphrases("This is a test text.")
        self.assertIsInstance(keyphrases, list)

    def test_quiz_generator_split_text_to_sentences(self):
        sentences = self.quiz_generator._split_text_to_sentences("This is a test sentence. This is another test sentence.")
        self.assertIsInstance(sentences, list)
        self.assertEqual(len(sentences), 2)

    def test_quiz_generator_get_word_sense(self):
        sentence = "This is a test sentence."
        word = "test"
        word_sense = self.quiz_generator._get_word_sense(sentence, word)
        self.assertIsNotNone(word_sense)

    def test_quiz_generator_get_distractors_word_net(self):
        synset = self.quiz_generator._get_word_sense("This is a test sentence.", "test")
        distractors = self.quiz_generator._get_distractors_word_net(synset, "test")
        self.assertIsInstance(distractors, list)

    def test_quiz_generator_get_distractors_concept_net(self):
        distractors = self.quiz_generator._get_distractors_concept_net("test")
        self.assertIsInstance(distractors, list)

if __name__ == '__main__':
    unittest.main()