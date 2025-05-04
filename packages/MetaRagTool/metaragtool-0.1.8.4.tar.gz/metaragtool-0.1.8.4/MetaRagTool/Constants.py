use_wandb = False
local_mode = True
trust_remote_code_SentenceTransformer = False

# import os
# WandbToken=os.getenv('WandbToken')
# HFToken=os.getenv('HFToken')
# GitHubToken=os.getenv('GitHubToken')


WandbToken = ''
HFToken = ''
GitHubToken = ''
API_KEY_GEMINI = ""
API_KEY_OPENAI = ""


def SetTokens(t_wandb=None, t_hf=None, t_github=None,
              t_gemini=None, t_openai=None):
    global WandbToken, HFToken, GitHubToken
    global API_KEY_GEMINI, API_KEY_OPENAI

    if t_wandb is not None:
        WandbToken = t_wandb
    if t_hf is not None:
        HFToken = t_hf
    if t_github is not None:
        GitHubToken = t_github
    if t_gemini is not None:
        API_KEY_GEMINI = t_gemini
    if t_openai is not None:
        API_KEY_OPENAI = t_openai
