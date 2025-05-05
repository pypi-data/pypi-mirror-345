from MetaRagTool.Encoders.MyEncoder import MyEncoder,models_path,OneByOneEncoder
from transformers import XLMRobertaModel
from transformers import AutoConfig, AutoTokenizer, AutoModel

class AutoModelEncoder(MyEncoder):
    class ModelName:
        jinaaiJina_embeddings_v3 = models_path + "\jinaaiJina-embeddings-v3"

    def __init__(self, model_name: str = ModelName.jinaaiJina_embeddings_v3, verbose=False):
        super().__init__(model_name, verbose)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        print("Model loaded successfully")

    def encode(self, sentences, isQuery=True):
        embeddings = self.model.encode(sentences,
                                       show_progress_bar=not isQuery,
                                       )

        return embeddings


class XLMRobertaEncoder(OneByOneEncoder):
    class ModelName:
        MEXMA = models_path + "\MEXMA"

    def __init__(self, model_name: str = ModelName.MEXMA, verbose=False):
        super().__init__(model_name, verbose)
        self.tokenizer = AutoTokenizer.from_pretrained(models_path + "\Xlm-roberta-large")
        self.model = XLMRobertaModel.from_pretrained(model_name, add_pooling_layer=False).to('cuda')

        print("Model loaded successfully")

    def _encode_str(self, sentences: str):
        tokenized_input = self.tokenizer(sentences, return_tensors='pt').to('cuda')
        outputs = self.model(**tokenized_input)
        sentence_representation = outputs.last_hidden_state[:, 0]
        sentence_representation = sentence_representation.detach().cpu().numpy()
        return sentence_representation


class BertEncoder(OneByOneEncoder):
    class ModelName:
        parsBertV3 = models_path + "\HooshvareLab-bert-fa-zwnj-base"
        FaBert = models_path + "\FaBert"

    def __init__(self, model_name: str = ModelName.parsBertV3, verbose=False):
        super().__init__(model_name, verbose)
        self.config = AutoConfig.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to('cuda')
        print("Model loaded successfully")

    def _encode_str(self, sentences: str):
        tokens = self.tokenizer(sentences, return_tensors='pt').to('cuda')
        output = self.model(**tokens)
        pooler_output = output.pooler_output
        return pooler_output.detach().cpu().numpy()
