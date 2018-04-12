import nltk


class Chunker(nltk.ChunkParserI):
    def shallow_parse(self, sentence):
        return None

    def get_phrases(self, sentence):
        parsed = self.shallow_parse(sentence)
        if isinstance(parsed, list):
            phrases = []
            phrase = []
            current_type = ""
            for item in parsed:
                if item[1].startswith("B-NP"):
                    phrases.append({"chunk": " ".join(phrase), "class": current_type})
                    phrase = [item[0]]
                    current_type = "entity"
                elif item[1].startswith("I-NP"):
                    phrase.append(item[0])
                if item[1].startswith("B-VP"):
                    phrases.append({"chunk": " ".join(phrase), "class": current_type})
                    phrase = [item[0]]
                    current_type = "relation"
                elif item[1].startswith("I-VP"):
                    phrase.append(item[0])
                elif item[1] == "O":
                    phrases.append({"chunk": " ".join(phrase), "class": current_type})
                    phrase = []
            phrases = [item for item in phrases if len(item["chunk"]) > 1]
            return phrases
        return None
