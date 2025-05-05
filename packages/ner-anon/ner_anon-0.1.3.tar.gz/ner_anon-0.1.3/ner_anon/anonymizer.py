import random
from transformers import pipeline, BertTokenizerFast, BertForTokenClassification


class EntityAnonymizer:
    """
    A class to anonymize named entities in text using a pre-trained NER model.
        
        Initialize the anonymizer with a chosen entity context and language setting.

        Args:
            context (dict): A dictionary containing mappings of sensitive data to their anonymized forms.
                
                Required keys in the dictionary:
                    - 'LABEL_1': list of person names.
                    - 'LABEL_3': list of organization names.
                    - 'LABEL_5': list of location names.
            multilingua (bool): Use multilingual model if True, else monolingual.

        Example:
        >>> anonymizer = EntityAnonymizer(context=MARVEL_ENTITIES)
        >>> anonymizer.anonymize("Angela Merkel visited Microsoft headquarters.")
        """
    def __init__(self, context: dict = None, multilingual: bool = False):
        
        if context is None:
            context = {
                'LABEL_1': ["[PERSON]"],
                'LABEL_3': ["[ORGANIZATION]"],
                'LABEL_5': ["[LOCATION]"]
            }
        self.context = context

        model_name = (
            'aimarbp02/ner-bert-base-multilingual-cased' if multilingual
            else 'aimarbp02/ner-bert-base-cased'
        )
        model = BertForTokenClassification.from_pretrained(model_name)
        tokenizer = BertTokenizerFast.from_pretrained(model_name)

        self.ner_pipeline = pipeline(
            "token-classification",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple"
        )

    def anonymize(self, text: str) -> str:
        """
        Anonymize named entities in the text based on the loaded context.

        Args:
            text (str): Text to anonymize.

        Returns:
            str: Anonymized text.
        """
        predictions = self.ner_pipeline(text)
        new_text = ""

        for ent in predictions:
            if ent["entity_group"] in self.context:
                new_text += random.choice(self.context[ent["entity_group"]]) + " "
            elif ent["entity_group"] in ['LABEL_0', 'LABEL_7', 'LABEL_8']:
                new_text += ent["word"] + " "

        return new_text.strip()