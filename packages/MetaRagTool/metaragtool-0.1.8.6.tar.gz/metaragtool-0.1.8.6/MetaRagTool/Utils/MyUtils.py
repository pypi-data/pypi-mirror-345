import gc
import weave
from hazm import sent_tokenize, word_tokenize as persian_word_tokenize
from nltk.tokenize import word_tokenize as english_word_tokenize
import numpy as np
import re
import wandb
from collections import OrderedDict
import MetaRagTool.Constants as Constants

from MetaRagTool.LLM.GoogleGemini import Gemini

has_logged_in_to_wandb = False


def init_wandb(project_name, run_name, config=None):
    global has_logged_in_to_wandb
    if not has_logged_in_to_wandb:
        api_key = Constants.WandbToken
        wandb.login(key=api_key)
        has_logged_in_to_wandb = True

    wandb.init(project=project_name, name=run_name, config=config)


def init_hf():
    from huggingface_hub import login
    hf_token = Constants.HFToken
    login(token=hf_token, add_to_git_credential=False)


def listToString(listOfStrings, separator="\n"):
    output = ""
    for s in listOfStrings:
        output += str(s) + separator
    return output


def capped_sent_tokenize(text, max_length=500, sentence_tokenizer=sent_tokenize,
                         custom_word_tokenizer=persian_word_tokenize):
    sentences = sentence_tokenizer(text)
    capped_sentences = []
    for sentence in sentences:
        while token_len(sentence) > max_length:
            tokens = custom_word_tokenizer(sentence)
            capped_sentences.append(" ".join(tokens[:max_length]))
            sentence = " ".join(tokens[max_length:])
        capped_sentences.append(sentence)
    return capped_sentences


def token_len(text, custom_word_tokenizer=persian_word_tokenize):
    return len(custom_word_tokenizer(text))


def token_len_en(text):
    return len(english_word_tokenize(text))


def reflect_vector(q, v):
    proj = np.dot(v, q) / np.dot(q, q) * q
    reflection = 2 * proj - v

    return reflection


def read_pdf(pdf_path, ignore_line_breaks=True):
    import PyPDF2

    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            if page.extract_text():
                page_text = page.extract_text()
                if ignore_line_breaks:
                    # Replace single line breaks with space
                    page_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', page_text)
                    text += page_text + '\n'
                else:
                    text += page_text

    return text.strip()


def Init(encoder_name, top_k, sample_size, qa_sample_ratio, local_mode=False, multi_hop_hardness_factor=0,
         judged=False, useTool=False, llm_name:str=Gemini.GEMINI_2_FLASH,multi_hop=True):
    from MetaRagTool.Utils.MetaRagConfig import MetaRagConfig
    from MetaRagTool.Encoders.SentenceTransformerEncoder import SentenceTransformerEncoder
    from MetaRagTool.LLM.JudgeLLM import JudgeLLM
    from MetaRagTool.Utils import DataLoader

    gc.collect()

    Constants.local_mode = local_mode
    Constants.use_wandb = True
    contexts, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, qa_sample_ratio=qa_sample_ratio, multi_hop=multi_hop,
                                            multi_hop_hardness_factor=multi_hop_hardness_factor)
    encoder = SentenceTransformerEncoder(encoder_name)
    llm = None
    judge = None

    # wandb_config = {
    #     'model_name': llm_name,
    #     'multi_hop': True,
    #     'sample_size': sample_size,
    #     'qa_sample_ratio': qa_sample_ratio,
    #     'hardness_factor': multi_hop_hardness_factor,
    #     'top_k': top_k,
    #     'useTool': useTool
    # }

    if judged:
        llm = Gemini(has_memory=False, RequestPerMinute_limit=15, model_name=llm_name)
        judge = JudgeLLM(model_name=Gemini.GEMINI_2_FLASH_LIGHT, RequestPerMinute_limit=30)
        project_name = "fullRag"
        weave.init(project_name)

    else:
        project_name = 'retrival'

    ragConfig = MetaRagConfig(encoder_name=encoder_name, top_k=top_k, sample_size=sample_size,
                              qa_sample_ratio=qa_sample_ratio, local_mode=local_mode,
                              multi_hop_hardness_factor=multi_hop_hardness_factor, judged=judged, useTool=useTool,
                              llm_name=llm_name,
                              encoder=encoder, contexts=contexts, qas=qas, llm=llm, judge=judge,
                              project_name=project_name,multi_hop=multi_hop)

    return ragConfig


def remove_duplicates(l):
    return list(OrderedDict.fromkeys(l))
