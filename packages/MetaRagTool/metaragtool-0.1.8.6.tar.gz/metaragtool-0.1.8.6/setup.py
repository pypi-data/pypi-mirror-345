from setuptools import setup, find_packages
setup(
  name = 'MetaRagTool',
  packages = find_packages(),
  version = '0.1.8.6',
  license='MIT',
  description = 'TYPE YOUR DESCRIPTION HERE',
  author = 'Ali Mobarekati',
  author_email = 'ali7919mb@yhaoo.com',
  url = 'https://github.com/user/ali7919',
  download_url = 'https://github.com/ali7919/MetaRAG/archive/refs/tags/v0.1.8.6.tar.gz',
  keywords = ['Ai', 'RAG', 'LLM'],
  install_requires=[
    'faiss-cpu',
    'hazm',
    'PyPDF2',
    'datasets',
    'huggingface_hub',
    'gradio',
    'weave'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)