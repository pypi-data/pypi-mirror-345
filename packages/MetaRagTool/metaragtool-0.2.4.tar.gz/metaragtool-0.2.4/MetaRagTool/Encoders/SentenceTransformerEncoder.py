from sentence_transformers import SentenceTransformer
from MetaRagTool.Encoders.MyEncoder import MyEncoder,models_path
import MetaRagTool.Constants as Constants




class SentenceTransformerEncoder(MyEncoder):
    class ModelName :
        bge_m3 = models_path + "\Bge-m3"
        LaBSE = models_path + "/LaBSE"
        allMiniLML6v2 = models_path + "\AllMiniLML6v2"
        parsbert_fa = models_path + "\MyrkurSentence-transformer-parsbert-fa"
        Multilingual_e5_base = models_path + "\Multilingual-e5-base"
        Use_cmlm_multilingual = models_path + "\\Use-cmlm-multilingual"
        mixedbread_ai_mxbai_embed_large_v1 = models_path + "\mixedbread-ai-mxbai-embed-large-v1"

        # slow models
        HIT_TMGKaLM_embedding_multilingual_mini_instruct_v1 = models_path + "\HIT-TMGKaLM-embedding-multilingual-mini-instruct-v1"



    def __init__(self, model_name: str = ModelName.LaBSE, verbose=False):
        super().__init__(model_name, verbose)
        if Constants.trust_remote_code_SentenceTransformer:
            self.model = SentenceTransformer(model_name,trust_remote_code=True)
        else:
            self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")

    def encode(self, sentences, isQuery=True):
        embeddings = self.model.encode(sentences,
                                       # normalize_embeddings=True,
                                       # batch_size=256,
                                       show_progress_bar=not isQuery,

                                       convert_to_tensor=False)
        return embeddings
