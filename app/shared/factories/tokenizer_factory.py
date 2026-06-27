import tiktoken

import sentencepiece as spm

from threading import Lock

from transformers import AutoTokenizer


class TokenizerFactory:

    def __init__(
        self
    ):

        self._huggingface_cache: dict = {}

        self._lock = Lock()

        self._tiktoken_cache = {}

        self._sentencepiece_cache = {}

    def get_huggingface_tokenizer(
        self,
        model_name: str,
        trust_remote_code: bool
    ):

        cache_key = (
            model_name,
            trust_remote_code
        )

        tokenizer = self._huggingface_cache.get(
            cache_key
        )

        if tokenizer is not None:

            return tokenizer

        with self._lock:

            tokenizer = self._huggingface_cache.get(
                cache_key
            )

            if tokenizer is None:

                tokenizer = AutoTokenizer.from_pretrained(

                    model_name,

                    trust_remote_code=trust_remote_code

                )

                self._huggingface_cache[
                    cache_key
                ] = tokenizer

        return tokenizer
    
    def get_tiktoken_tokenizer(
        self,
        encoding_name: str
    ):

        tokenizer = self._tiktoken_cache.get(
            encoding_name
        )

        if tokenizer is not None:

            return tokenizer

        with self._lock:

            tokenizer = self._tiktoken_cache.get(
                encoding_name
            )

            if tokenizer is None:

                tokenizer = tiktoken.get_encoding(
                    encoding_name
                )

                self._tiktoken_cache[
                    encoding_name
                ] = tokenizer

        return tokenizer
    
    def get_sentencepiece_tokenizer(
        self,
        model_path: str
    ):

        tokenizer = self._sentencepiece_cache.get(
            model_path
        )

        if tokenizer is not None:

            return tokenizer

        with self._lock:

            tokenizer = self._sentencepiece_cache.get(
                model_path
            )

            if tokenizer is None:

                tokenizer = (
                    spm.SentencePieceProcessor()
                )

                tokenizer.load(
                    model_path
                )

                self._sentencepiece_cache[
                    model_path
                ] = tokenizer

        return tokenizer


tokenizer_factory = (
    TokenizerFactory()
)