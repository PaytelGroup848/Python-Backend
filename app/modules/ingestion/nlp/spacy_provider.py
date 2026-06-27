from app.modules.ingestion.nlp.base_nlp_provider import (
    BaseNLPProvider
)

from app.modules.ingestion.schemas.nlp_document import (
    NLPDocument,
    NLPSentence
)

from app.modules.pipeline_runtime.schemas.nlp_configuration import (
    NLPConfiguration
)

from app.shared.factories.nlp_model_factory import (
    nlp_model_factory
)


class SpaCyProvider(
    BaseNLPProvider
):

    @property
    def provider_code(
        self
    ) -> str:

        return "SPACY"

    async def parse(
        self,
        text: str,
        configuration: NLPConfiguration
    ) -> NLPDocument:

        model = (
            nlp_model_factory.get_model(
                configuration.model_name
            )
        )

        document = model(
            text
        )

        sentences = []

        for sentence in document.sents:

            sentences.append(

                NLPSentence(

                    text=sentence.text,

                    start_offset=sentence.start_char,

                    end_offset=sentence.end_char

                )

            )

        return NLPDocument(

            text=text,

            language=document.lang_,

            metadata={

                "provider_code": self.provider_code,

                "model_name": configuration.model_name

            },

            sentences=sentences

        )


spacy_provider = (
    SpaCyProvider()
)