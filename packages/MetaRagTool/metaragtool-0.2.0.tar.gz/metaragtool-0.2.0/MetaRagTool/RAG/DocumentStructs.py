from enum import Enum

class ChunkingMethod(Enum):
    SENTENCE_MERGER_CROSS_PARAGRAPH = 'sentence_merger_cross_paragraph'
    SENTENCE = 'sent'
    PARAGRAPH = 'paragraph'
    DOCUMENT = 'document'
    RECURSIVE = 'recursive'
    SENTENCE_MERGER = 'sentence_merger'

class MyDocument:
    def __init__(self,text=""):
        self.MyParagraphs = []
        self.MySentences = []
        self.Text = text
        self.isChunked = False

    def AddParagraph(self, paragraph):
        self.MyParagraphs.append(paragraph)

    def AddSentence(self, sentence):
        self.MySentences.append(sentence)



class MyParagraph:
    def __init__(self,document,text=""):
        self.MyDocument = document
        self.MySentences = []
        self.Prev = None
        self.Next = None
        self.Text = text
        self.Embeddings = None

    def AddSentence(self, sentence):
        self.MySentences.append(sentence)

    def SetPrev(self, prev):
        self.Prev = prev

    def SetNext(self, nextParagraph):
        self.Next = nextParagraph


class MySentence:
    def __init__(self ,document,paragraph,text=""):
        self.MyDocument = document
        self.MyParagraph = paragraph
        self.Prev = None
        self.Next = None
        self.Text = text

    def SetPrev(self, prev):
        self.Prev = prev

    def SetNext(self, nextSentence):
        self.Next = nextSentence

class MyChunk:
    def __init__(self,document, text=""):
        self.Text = text
        self.Paragraphs = []
        self.Sentences = []
        self.Document = document
        self.PrevRelated = None
        self.NextRelated = None
        self.Embeddings = None
        self.Length = -1

    def AddParagraph(self, paragraph):
        if paragraph not in self.Paragraphs:
            self.Paragraphs.append(paragraph)

    def AddSentence(self, sentence):
        self.Sentences.append(sentence)



    def __str__(self):
        return self.Text

    def __repr__(self):
        return self.Text


