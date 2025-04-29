VEREDITO

GEMINI 2.5 PRO
GUI - PySide6 (Qt for Python)
Motor de Escaneamento	os.path.getsize + BLAKE3
Manipulação de Arquivos & Sistema	pathlib + shutil + send2trash + concurrent.futures
Descompactação Otimizada	Bindings para libarchive (e.g., libarchive-c)

PERPLEXITY
GUI - PySide6 (Qt for Python)
Motor de Escaneamento    imagededup + BLAKE3 - Pré-filtragem por tamanho (usando os.path.getsize) para otimização inicial
Manipulação de Arquivos & Sistema	pathlib + shutil + send2trash + concurrent.futures
Descompactação Otimizada	zipfile/tarfile (bibliotecas padrão) com opção para libarchive-c

GROK DEEPER SEARCH
GUI - PySide6 (Qt for Python)
Motor de Escaneamento    xxHash
Manipulação de Arquivos & Sistema	shutil + send2trash + xxHash + concurrent.futures
Descompactação Otimizada	 libarchive-c

CLAUD 3.7 SONNET
GUI - PySide6 (Qt for Python)
Motor de Escaneamento    imagehash + BLAKE3 - Pré-filtragem por tamanho (usando os.path.getsize) para otimização inicial
Manipulação de Arquivos & Sistema	pathlib + aiofiles + concurrent.futures
Descompactação Otimizada	PyZstd

gpt o3
GUI - PySide6 (Qt for Python)
Motor de Escaneamento    BLAKE3 (–threads=N) + Faiss + OpenCV/pHash
Manipulação de Arquivos & Sistema	aiofiles (I/O assíncrono) + ThreadPoolExecutor buffered 8 MiB
Descompactação Otimizada	stream-unzip (ZIP) ou python-zstandard (Zstd)



VERIDITO FINAL
GUI - PySide6 
Motor de Escaneamento    BLAKE3 + Pré-filtragem por tamanho (usando os.path.getsize) para otimização inicial
Manipulação de Arquivos & Sistema	pathlib + shutil + send2trash + concurrent.futures
Descompactação Otimizada   stream-unzip (ZIP)