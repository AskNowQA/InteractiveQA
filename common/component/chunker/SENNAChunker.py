# Taken from here: https://github.com/AskNowQA/EARL/blob/master/scripts/ShallowParser.py
from practnlptools.tools import Annotator
from chunker import Chunker
import nltk


class SENNAChunker(Chunker):
    def __init__(self):
        print "Shallow Parser Initializing"
        self.annotator = Annotator()
        self.stop_words = ["a", "as", "able", "about", "above", "according", "accordingly", "across", "actually",
                           "after", "afterwards", "again", "against", "aint", "all", "allow", "allows", "almost",
                           "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "an",
                           "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways",
                           "anywhere", "apart", "appear", "appreciate", "appropriate", "are", "arent", "around", "as",
                           "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "be", "became",
                           "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind",
                           "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond",
                           "both", "brief", "but", "by", "cmon", "cs", "came", "can", "cant", "cannot", "cant", "cause",
                           "causes", "certain", "certainly", "changes", "clearly", "co", "com", "come", "comes",
                           "concerning", "consequently", "consider", "considering", "contain", "containing", "contains",
                           "corresponding", "could", "couldnt", "course", "currently", "definitely", "described",
                           "despite", "did", "didnt", "different", "do", "does", "doesnt", "doing", "dont", "done",
                           "down", "downwards", "during", "each", "edu", "eg", "eight", "either", "else", "elsewhere",
                           "enough", "entirely", "especially", "et", "etc", "even", "ever", "every", "everybody",
                           "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "far", "few",
                           "ff", "fifth", "first", "five", "followed", "following", "follows", "for", "former",
                           "formerly", "forth", "four", "from", "further", "furthermore", "get", "gets", "getting",
                           "given", "gives", "go", "goes", "going", "gone", "got", "gotten", "greetings", "had",
                           "hadnt", "happens", "hardly", "has", "hasnt", "have", "havent", "having", "he", "hes",
                           "hello", "help", "hence", "her", "here", "heres", "hereafter", "hereby", "herein",
                           "hereupon", "hers", "herself", "hi", "him", "himself", "his", "hither", "hopefully", "how",
                           "howbeit", "however", "i", "id", "ill", "im", "ive", "ie", "if", "ignored", "immediate",
                           "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar",
                           "instead", "into", "inward", "is", "isnt", "it", "itd", "itll", "its", "its", "itself",
                           "just", "keep", "keeps", "kept", "know", "knows", "known", "last", "lately", "later",
                           "latter", "latterly", "least", "less", "lest", "let", "lets", "like", "liked", "likely",
                           "little", "look", "looking", "looks", "ltd", "mainly", "many", "may", "maybe", "me", "mean",
                           "meanwhile", "merely", "might", "more", "moreover", "most", "mostly", "much", "must", "my",
                           "myself", "name", "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither",
                           "never", "nevertheless", "new", "next", "nine", "no", "nobody", "non", "none", "noone",
                           "nor", "normally", "not", "nothing", "novel", "now", "nowhere", "obviously", "of", "off",
                           "often", "oh", "ok", "okay", "old", "on", "once", "one", "ones", "only", "onto", "or",
                           "other", "others", "otherwise", "ought", "our", "ours", "ourselves", "out", "outside",
                           "over", "overall", "own", "particular", "particularly", "per", "perhaps", "placed", "please",
                           "plus", "possible", "presumably", "probably", "provides", "que", "quite", "qv", "rather",
                           "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively",
                           "respectively", "right", "said", "same", "saw", "say", "saying", "says", "second",
                           "secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves",
                           "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "she", "should",
                           "shouldnt", "since", "six", "so", "some", "somebody", "somehow", "someone", "something",
                           "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify",
                           "specifying", "still", "sub", "such", "sup", "sure", "ts", "take", "taken", "tell", "tends",
                           "th", "than", "thank", "thanks", "thanx", "that", "thats", "thats", "the", "their", "theirs",
                           "them", "themselves", "then", "thence", "there", "theres", "thereafter", "thereby",
                           "therefore", "therein", "theres", "thereupon", "these", "they", "theyd", "theyll", "theyre",
                           "theyve", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three",
                           "through", "throughout", "thru", "thus", "to", "together", "too", "took", "toward",
                           "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", "un", "under",
                           "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used",
                           "useful", "uses", "using", "usually", "value", "various", "very", "via", "viz", "vs", "want",
                           "wants", "was", "wasnt", "way", "we", "wed", "well", "were", "weve", "welcome", "well",
                           "went", "were", "werent", "what", "whats", "whatever", "when", "whence", "whenever", "where",
                           "wheres", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
                           "which", "while", "whither", "who", "whos", "whoever", "whole", "whom", "whose", "why",
                           "will", "willing", "wish", "with", "within", "without", "wont", "wonder", "would", "would",
                           "wouldnt", "yes", "yet", "you", "youd", "youll", "youre", "youve", "your", "yours",
                           "yourself", "yourselves", "zero", "whose", "which", "is", ", ", "\\\\", "?", "\\"]
        print "Shallow Parser Initialized"

    def parse(self, tagged_sent):
        str = " ".join([item[0] for item in tagged_sent]).encode("ascii", "ignore")
        chunks = self.shallowParse(str)
        print chunks
        for i in range(len(chunks)):
            item = chunks[i]
            chunks[i] = (item[0], tagged_sent[i][1] if i < len(tagged_sent) else ".", item[1])

        return nltk.chunk.conlltags2tree(chunks)

    # def shallowParse(self, text):
    #     filterednpchunks = []
    #     result = self.annotator.getAnnotations(text)['chunk']
    #     print result
    #     phrases = []
    #     _phrase = []
    #     for chunk in result:
    #         if chunk[1] == 'S-NP':
    #             phrases.append([chunk[0]])
    #             continue
    #         if chunk[1] == 'B-NP' or chunk[1] == 'I-NP':
    #             _phrase.append(chunk[0])
    #             continue
    #         if chunk[1] == 'E-NP':
    #             _phrase.append(chunk[0])
    #             phrases.append(_phrase)
    #             _phrase = []
    #
    #     for phrase in phrases:
    #         filteredchunk = []
    #         filteredchunkstring = ''
    #         for word in phrase:
    #             if word.lower() not in self.stop_words:
    #                 filteredchunk.append(word)
    #         if len(filteredchunk) > 0:
    #             filteredchunkstring = ' '.join(filteredchunk)
    #             filterednpchunks.append(filteredchunkstring)
    #
    #     return filterednpchunks

    def shallow_parse(self, text):
        result = self.annotator.getAnnotations(text)
        result = result['chunk']
        phrases = []
        for chunk in result:
            if chunk[1] == 'S-NP':
                if chunk[0].lower() in self.stop_words:
                    phrases.append((chunk[0], "O"))
                else:
                    phrases.append((chunk[0], "B-NP"))
            elif chunk[1] == 'B-NP' or chunk[1] == 'I-NP':
                phrases.append((chunk[0], chunk[1]))
            elif chunk[1] == 'E-NP':
                phrases.append((chunk[0], "I-NP"))
            elif chunk[1] == 'S-VP':
                if chunk[0].lower() in self.stop_words:
                    phrases.append((chunk[0], "O"))
                else:
                    phrases.append((chunk[0], "B-VP"))
            elif chunk[1] == 'B-VP' or chunk[1] == 'I-VP':
                phrases.append((chunk[0], chunk[1]))
            elif chunk[1] == 'E-VP':
                phrases.append((chunk[0], "I-VP"))
            else:
                phrases.append((chunk[0], "O"))

        return phrases
