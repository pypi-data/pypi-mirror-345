from tqdm import tqdm
import wandb




def god_eval(encoder_name, sample_size, qa_sample_ratio, local_mode=False, multi_hop_hardness_factor=0,
             judged=False, top_k=None, useTool=False, llm=None):
    import MetaRagTool.Evaluations.TestManager as TestManager
    import MetaRagTool.Utils.MyUtils as MyUtils

    ragConfig = MyUtils.Init(encoder_name=encoder_name, top_k=top_k, sample_size=sample_size,
                             qa_sample_ratio=qa_sample_ratio, local_mode=local_mode,
                             multi_hop_hardness_factor=multi_hop_hardness_factor, judged=judged, useTool=useTool,
                             multi_hop=True,llm=llm)

    eval_k_base = [1, 5, 10, 15, 20, 30, 40, 50, 70, 100, 140, 180, 230, 300, 400, 500]
    eval_k_half = [1, 3, 7, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250]
    eval_k_quarter = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 77, 90, 100, 120, 125, 150]
    eval_k_low_res = [1, 3, 5, 7, 10, 20, 30, 50, 200]
    if top_k is not None:
        eval_k_base = [top_k]
        eval_k_half = [top_k]
        eval_k_quarter = [top_k]
        eval_k_low_res = [top_k]

    ragConfig.fine_grain_progressbar = top_k is not None

    encoder_name = f"s{sample_size}_{encoder_name}"
    if multi_hop_hardness_factor != 0:
        encoder_name += f"_hard{multi_hop_hardness_factor}"
    if top_k is not None:
        encoder_name += f"_k{top_k}"

    ragConfig.encoder_name = encoder_name

    def run_test(ks, ragConfig0, rag0):

        loop = tqdm(ks, desc='Evaluating', total=len(ks), disable=ragConfig.fine_grain_progressbar)
        for k0 in loop:
            ragConfig0.top_k = k0
            rag0, results = TestManager.test_retrival(ragConfig=ragConfig0, rag=rag0)
            loop.set_postfix({'K': k0, 'Run': ragConfig0.run_name})
        wandb.finish()
        return rag0

    rag = None
    ragConfig.reset_rag_attributes()
    ragConfig.run_name = encoder_name
    rag = run_test(eval_k_base, ragConfig, rag)

    ragConfig.reset_rag_attributes()
    ragConfig.run_name = f"{encoder_name}_enhanced"
    ragConfig.add_neighbor_chunks_smart = True
    ragConfig.replace_retrieved_chunks_with_parent_paragraph = True
    rag = run_test(eval_k_quarter, ragConfig, rag)

    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_add_neighbor_smart"
    # ragConfig.add_neighbor_chunks_smart=True
    # rag=run_test(eval_k_quarter,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_replace_with_paragraph"
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # rag=run_test(eval_k_quarter,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_depth_first_retrival"
    # ragConfig.depth_first_retrival = True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_enhanced_depth_first_retrival"
    # ragConfig.depth_first_retrival = True
    # ragConfig.add_neighbor_chunks_smart=True
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_breath_first_retrival"
    # ragConfig.breath_first_retrival = True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_enhanced_breath_first_retrival"
    # ragConfig.breath_first_retrival = True
    # ragConfig.add_neighbor_chunks_smart=True
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_weighted_bfs_retrival"
    # ragConfig.weighted_bfs = True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_enhanced_weighted_bfs_retrival"
    # ragConfig.weighted_bfs = True
    # ragConfig.add_neighbor_chunks_smart=True
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_reflections"
    # ragConfig.include_reflections = True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_refractions"
    # ragConfig.include_refractions = True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_sentence"
    # ragConfig.splitting_method=ChunkingMethod.SENTENCE
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_recursive"
    # ragConfig.splitting_method=ChunkingMethod.RECURSIVE
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_PARAGRAPH"
    # ragConfig.splitting_method=ChunkingMethod.PARAGRAPH
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_SENTENCE_MERGER_CROSS_PARAGRAPH"
    # ragConfig.splitting_method=ChunkingMethod.SENTENCE_MERGER_CROSS_PARAGRAPH
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_use_parentParagraph_embeddings"
    # ragConfig.use_parentParagraph_embeddings=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_use_parentParagraph_embeddings_enhanced"
    # ragConfig.use_parentParagraph_embeddings=True
    # ragConfig.add_neighbor_chunks_smart=True
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_use_neighbor_embeddings"
    # ragConfig.use_neighbor_embeddings=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_use_neighbor_embeddings_enhanced"
    # ragConfig.use_neighbor_embeddings=True
    # ragConfig.add_neighbor_chunks_smart=True
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name= f"{encoder_name}_enriched_embeddings"
    # ragConfig.use_neighbor_embeddings=True
    # ragConfig.use_parentParagraph_embeddings=True
    # ragConfig.embedding_steering_influence_factor=0.2
    # rag=run_test(eval_k_base,ragConfig,rag)
    #
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name=f"{encoder_name}_enriched_embeddings_enhanced"
    # ragConfig.use_neighbor_embeddings=True
    # ragConfig.use_parentParagraph_embeddings=True
    # ragConfig.embedding_steering_influence_factor=0.2
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # ragConfig.add_neighbor_chunks_smart=True
    # rag=run_test(eval_k_quarter,ragConfig,rag)
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name=f"{encoder_name}_Normalized_text"
    # ragConfig.normalize_text=True
    # rag=run_test(eval_k_quarter,ragConfig,rag)
    #
    #
    #
    # rag=None
    # ragConfig.reset_rag_attributes()
    # ragConfig.run_name=f"{encoder_name}_godMode"
    # ragConfig.normalize_text=True
    # ragConfig.use_neighbor_embeddings=True
    # ragConfig.use_parentParagraph_embeddings=True
    # ragConfig.embedding_steering_influence_factor=0.2
    # ragConfig.replace_retrieved_chunks_with_parent_paragraph=True
    # ragConfig.add_neighbor_chunks_smart=True
    # rag=run_test(eval_k_quarter,ragConfig,rag)


def all_encoders(sample_size=200, qa_sample_ratio=0.5, local_mode=False, multi_hop_hardness_factor=0,
                 judged=False, top_k=20):
    names = [
        'sentence-transformers/LaBSE',
        'codersan/FaLaBSE-v3',
        'sentence-transformers/all-MiniLM-L6-v2',
        'codersan/all-MiniLM-L6-v2-Fa',
        'codersan/all-MiniLM-L6-v2-Fa-v2',
        'intfloat/multilingual-e5-base',
        'codersan/multilingual-e5-base-Fa',
        'codersan/multilingual-e5-base-Fa-v2',
        'sentence-transformers/use-cmlm-multilingual',
        'HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1',
        'myrkur/sentence-transformer-parsbert-fa',
        'BAAI/bge-m3',
        'codersan/all-MiniLM-L6-v2-Fa-v3',
        'codersan/multilingual-e5-base-Fa-v3'
    ]

    for n in names:
        god_eval(encoder_name=n, sample_size=sample_size, qa_sample_ratio=qa_sample_ratio,
                 multi_hop_hardness_factor=multi_hop_hardness_factor,
                 local_mode=local_mode, judged=judged, top_k=top_k)

#
# def embedding_steering_influence_factor(encoder_name, sample_size=250, qa_sample_ratio=0.35, local_mode=False):
#     Constants.local_mode = local_mode
#     Constants.use_wandb = True
#     contexts, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, qa_sample_ratio=qa_sample_ratio, multi_hop=True, )
#     encoder = SentenceTransformerEncoder(encoder_name)
#     gc.collect()
#     rag = None
#
#     for embedding_steering_influence_factor_value in [0.1, 0.2, 0.3, 0.4]:
#
#         eval_ks = [1, 3, 5, 7, 10, 13, 16, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300]
#         rag = None
#         MyUtils.init_wandb(project_name="embedding_steering_influence_factor",
#                            run_name=f"{encoder_name}_enriched_embeddings_{embedding_steering_influence_factor_value}")
#         for k in eval_ks:
#             rag, results = TestManager.test_retrival(encoder, contexts, qas, rag=rag, llm=None,
#                                                      splitting_method=ChunkingMethod.SENTENCE_MERGER, top_k=k,
#                                                      use_neighbor_embeddings=True, use_parentParagraph_embeddings=True,
#                                                      embedding_steering_influence_factor=embedding_steering_influence_factor_value,
#                                                      multi_hop=True,
#                                                      log_chunking_report=False, )
#         wandb.finish()
#         gc.collect()
#
#         eval_ks = [1, 3, 5, 7, 10, 13, 16, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180]
#         # rag = None
#         MyUtils.init_wandb(project_name="embedding_steering_influence_factor",
#                            run_name=f"{encoder_name}_enriched_embeddings_enhanced_{embedding_steering_influence_factor_value}")
#         for k in eval_ks:
#             rag, results = TestManager.test_retrival(encoder, contexts, qas, rag=rag, llm=None,
#                                                      splitting_method=ChunkingMethod.SENTENCE_MERGER, top_k=k,
#                                                      use_neighbor_embeddings=True, use_parentParagraph_embeddings=True,
#                                                      embedding_steering_influence_factor=embedding_steering_influence_factor_value,
#                                                      replace_retrieved_chunks_with_parent_paragraph=True,
#                                                      add_neighbor_chunks_smart=True,
#                                                      multi_hop=True,
#                                                      log_chunking_report=False, )
#         wandb.finish()
#         gc.collect()
#
#         # eval_ks = [1, 3, 5, 7, 10, 13, 16, 20,  30,  40,  50, 60, 80 , 100, 150 , 200,250,300]
#         # rag = None
#         # MyUtils.init_wandb(project_name="embedding_steering_influence_factor", run_name=f"{encoder_name}_use_neighbor_embeddings_enhanced_{embedding_steering_influence_factor_value}")
#         # for k in eval_ks:
#         #     rag, results = TestManager.test_retrival(encoder, contexts, qas, rag=rag, llm=None,
#         #                                              splitting_method=ChunkingMethod.SENTENCE_MERGER, top_k=k,use_neighbor_embeddings=True,
#         #                                              embedding_steering_influence_factor=embedding_steering_influence_factor_value,
#         #                                              replace_retrieved_chunks_with_parent_paragraph=True,add_neighbor_chunks_smart=True,
#         #                                              multi_hop=True,
#         #                                              log_chunking_report=False, )
#         # wandb.finish()
#         # gc.collect()
#
#         # eval_ks = [1, 3, 5, 7, 10, 13, 16, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300]
#         # rag = None
#         # MyUtils.init_wandb(project_name="embedding_steering_influence_factor", run_name=f"{encoder_name}_use_parentParagraph_embeddings_{embedding_steering_influence_factor_value}")
#         # for k in eval_ks:
#         #     rag, results = TestManager.test_retrival(encoder, contexts, qas, rag=rag, llm=None,
#         #                                              splitting_method=ChunkingMethod.SENTENCE_MERGER, top_k=k,
#         #                                              use_parentParagraph_embeddings=True,
#         #                                              embedding_steering_influence_factor=embedding_steering_influence_factor_value,
#         #                                              multi_hop=True,
#         #                                              log_chunking_report=False, )
#         # wandb.finish()
#         # gc.collect()
#
#
# def qa_ratio_impact(encoder_name="sentence-transformers/LaBSE", local_mode=False):
#     Constants.local_mode = local_mode
#     Constants.use_wandb = True
#     encoder = SentenceTransformerEncoder(encoder_name)
#     sample_size = -1
#     rag = None
#     contexts, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, multi_hop=True, qa_sample_ratio=1)
#     qa_ratios = [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1]
#
#     MyUtils.init_wandb(project_name="qa_sample_ratio", run_name=encoder_name)
#     for qa_ratio in qa_ratios:
#         _, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, multi_hop=True, qa_sample_ratio=qa_ratio)
#         rag, res = TestManager.test_retrival(encoder, contexts, qas, rag=rag,
#                                              splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                              log_chunking_report=False, top_k=20, multi_hop=True)
#     wandb.finish()
#
#     MyUtils.init_wandb(project_name="qa_sample_ratio", run_name=f"{encoder_name}_enhanced")
#     for qa_ratio in qa_ratios:
#         _, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, multi_hop=True, qa_sample_ratio=qa_ratio)
#         rag, res = TestManager.test_retrival(encoder, contexts, qas, rag=rag,
#                                              splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                              log_chunking_report=False, top_k=20, multi_hop=True,
#                                              add_neighbor_chunks_smart=True,
#                                              replace_retrieved_chunks_with_parent_paragraph=True)
#     wandb.finish()
#
#
# def encoder_on_chunk_size(encoder_name, sample_size=500, qa_sample_ratio=0.5, local_mode=False):
#     Constants.local_mode = local_mode
#     Constants.use_wandb = True
#     contexts, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, qa_sample_ratio=qa_sample_ratio, multi_hop=True)
#     encoder = SentenceTransformerEncoder(encoder_name)
#
#     chunk_size_eval_range = range(3, 15)
#     chunk_size_eval_step = 10
#
#     MyUtils.init_wandb(project_name="testingChunkingSizeFair", run_name=f"not_fair_{encoder_name}")
#     for i in chunk_size_eval_range:
#         size = i * chunk_size_eval_step
#         TestManager.test_retrival(encoder, contexts, qas, llm=None, splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                   top_k=20, multi_hop=True, log_chunking_report=False, chunk_size=size)
#         gc.collect()
#
#     wandb.finish()
#
#     MyUtils.init_wandb(project_name="testingChunkingSizeFair", run_name=f"not_fair_{encoder_name}_enhanced")
#     for i in chunk_size_eval_range:
#         size = i * chunk_size_eval_step
#         TestManager.test_retrival(encoder, contexts, qas, llm=None, splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                   top_k=20, multi_hop=True, log_chunking_report=False, chunk_size=size,
#                                   add_neighbor_chunks_smart=True,
#                                   replace_retrieved_chunks_with_parent_paragraph=True)
#         gc.collect()
#
#     wandb.finish()
#
#
# def encoder_on_chunk_size_fair(encoder_name, sample_size=500, qa_sample_ratio=0.5, local_mode=False):
#     Constants.local_mode = local_mode
#     Constants.use_wandb = True
#     contexts, qas = DataLoader.loadWikiFaQa(sample_size=sample_size, qa_sample_ratio=qa_sample_ratio, multi_hop=True)
#     encoder = SentenceTransformerEncoder(encoder_name)
#
#     constant_k_chunk_size = 900
#     chunk_size_eval_range = range(3, 15)
#     chunk_size_eval_step = 10
#
#     MyUtils.init_wandb(project_name="testingChunkingSizeFair", run_name=encoder_name)
#     for i in chunk_size_eval_range:
#         size = i * chunk_size_eval_step
#         k = constant_k_chunk_size // size
#         TestManager.test_retrival(encoder, contexts, qas, llm=None, splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                   top_k=k, multi_hop=True, log_chunking_report=False, chunk_size=size)
#         gc.collect()
#
#     wandb.finish()
#
#     MyUtils.init_wandb(project_name="testingChunkingSizeFair", run_name=f"{encoder_name}_enhanced")
#     for i in chunk_size_eval_range:
#         size = i * chunk_size_eval_step
#         k = constant_k_chunk_size // size
#         TestManager.test_retrival(encoder, contexts, qas, llm=None, splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                   top_k=k, multi_hop=True, log_chunking_report=False, chunk_size=size,
#                                   add_neighbor_chunks_smart=True,
#                                   replace_retrieved_chunks_with_parent_paragraph=True)
#         gc.collect()
#
#     wandb.finish()
#
#
# def corpus_size(encoder_name, local_mode=False):
#     llm = None
#     Constants.local_mode = local_mode
#     Constants.use_wandb = True
#
#     contexts, qas = DataLoader.loadWikiFaQa(sample_size=50, multi_hop=True, qa_sample_ratio=0.5)
#     all_contexts, all_qas = DataLoader.loadWikiFaQa(multi_hop=True)
#
#     # remove contexts from all_contexts (contexts is a list of strings)
#     all_contexts = [context for context in all_contexts if context not in contexts]
#     encoder = SentenceTransformerEncoder(encoder_name)
#
#     MyUtils.init_wandb(project_name="CorpusSize", run_name=encoder_name)
#     rag, res = TestManager.test_retrival(encoder, contexts, qas, llm=llm,
#                                          splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                          log_chunking_report=False, top_k=20, multi_hop=True)
#     batch_size = 100
#     for i in range(0, len(all_contexts), batch_size):
#         batch = all_contexts[i:i + batch_size]
#         rag.add_corpus(batch)
#         TestManager.test_retrival(encoder, contexts, qas, llm=llm, rag=rag,
#                                   splitting_method=ChunkingMethod.SENTENCE_MERGER,
#                                   log_chunking_report=False, top_k=20, multi_hop=True)
#
#     wandb.finish()
#
