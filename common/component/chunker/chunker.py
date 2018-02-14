import nltk


class Chunker(nltk.ChunkParserI):
    def shallow_parse(self, sentence):
        return None

    def get_phrases(self, sentence):
        parsed = self.shallow_parse(sentence)
        if isinstance(parsed, list):
            phrases = []
            phrase = []
            for item in parsed:
                if item[1].startswith("B-"):
                    phrases.append(" ".join(phrase))
                    phrase = [item[0]]
                elif item[1].startswith("I-"):
                    phrase.append(item[0])
                elif item[1] == "O":
                    phrases.append(" ".join(phrase))
                    phrase = []
            phrases = [item for item in phrases if len(item) > 1]
            return phrases
        return None
