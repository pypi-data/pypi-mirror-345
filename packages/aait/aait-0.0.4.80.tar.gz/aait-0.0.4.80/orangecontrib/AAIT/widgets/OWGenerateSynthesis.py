import os
import sys
import re
import copy
import numpy as np
import ntpath

import Orange.data
from Orange.data import StringVariable, Domain, Table
from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from transformers import AutoTokenizer

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.llm import GPT4ALL, lmstudio
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import get_local_store_path
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.llm import GPT4ALL, lmstudio
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
# Remplacement de nltk et GPT2TokenizerFast par une implémentation simple
class BasicTokenizer:
    def encode(self, text):
        # Chemin local vers le modèle all-mpnet-base-v2
        local_store_path = get_local_store_path()
        model_name = "all-mpnet-base-v2"
        model_path = os.path.join(local_store_path, "Models", "NLP", model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        tokens = tokenizer.encode(text,truncation=True,max_length=4096)
        return tokens

    @staticmethod
    def sent_tokenize(text):
        # Découpage des phrases en se basant sur la ponctuation simple.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences
@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWGenerateSynthesis(widget.OWWidget):
    name = "Generate Synthesis"
    description = "Generate Synthesis on the column 'content' of an input table"
    icon = "icons/owgeneratesynthesis.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owgeneratesynthesis.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owembeddings.ui")
    want_control_area = False
    priority = 1060

    class Inputs:
        data = Input("Data for GPT4All", Orange.data.Table)
        data_lmstudio = Input("Data for LMStudio", Orange.data.Table)
        model = Input("Model", str)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        self.data_lmstudio = None
        if self.autorun:
            self.run()

    @Inputs.data_lmstudio
    def set_data_lmstudio(self, in_data):
        self.data_lmstudio = in_data
        self.data = None
        if self.autorun:
            self.run()

    @Inputs.model
    def set_model(self, in_model):
        self.model = in_model
        if self.autorun:
            self.run()

    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        # Data Management
        self.data = None
        self.data_lmstudio = None
        self.model = None
        self.thread = None
        self.autorun = True
        self.result = None
        # Initialisation du context_length avec une valeur par défaut
        self.context_length = 4096
        self.post_initialized()
        self.tokenizer = BasicTokenizer()

    def run(self):
        self.error("")
        # Si un thread est en cours, on quitte
        if self.thread is not None:
            self.thread.safe_quit()
            return

        # Vérification des entrées
        if self.data is None and self.data_lmstudio is None:
            return

        if self.data and self.data_lmstudio:
            self.error('You cannot have both inputs GPT4All and LMStudio.')
            return

        if self.model is None:
            return

        # Si LMStudio est utilisé : vérification des paramètres
        if self.data_lmstudio is not None:
            llm = 'lmstudio'
            data = self.data_lmstudio
            model_list = lmstudio.get_model_lmstudio()
            if isinstance(model_list, str) and model_list == "Error":
                self.error("Please launch the LMStudio app and start the server.")
                return
            # Vérification que le répertoire des modèles est défini dans LMStudio (aait_store)
            if model_list is None:
                self.error("Your models directory in LMStudio is not set properly.")
                return

            # Vérification que le modèle fourni existe dans la liste des modèles de LMStudio
            if not any(ntpath.basename(d["id"]).lower() == ntpath.basename(self.model.lower()) for d in model_list["data"]):
                self.error(f"Model not found in LMStudio. You are trying to use {ntpath.basename(self.model.lower())}, please verify that this model's API identifier exists in LMStudio.")
                return
            for d in model_list["data"]:
                if ntpath.basename(d["id"]).lower() == ntpath.basename(self.model.lower()):
                    self.model = d["id"]

        # Si GPT4All est utilisé
        if self.data is not None:
            llm = 'gpt4all'
            data = self.data
            self.model = ntpath.basename(self.model)

        # Vérification de la présence de la colonne "content"
        try:
            data.domain["content"]
        except KeyError:
            self.error('You need a "content" column in input data')
            return

        if type(data.domain["content"]).__name__ != 'StringVariable':
            self.error('"content" column needs to be a Text')
            return

        # Démarrage de la progress bar
        self.progressBarInit()

        # Lancement du thread avec la fonction principale
        self.thread = thread_management.Thread(self.generate_synthesis_on_table, data, self.model, llm)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, value: float) -> None:
        self.progressBarSet(value)

    def handle_result(self, result):
        try:
            self.result = result
            self.Outputs.data.send(result)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        print("Question generation finished")
        self.progressBarFinished()
        self.thread = None

    def post_initialized(self):
        pass

    def split_text_into_chunks(self, text, max_tokens, safety_margin=1000, tokenizer=None):
        """
        Découpe le texte en chunks en respectant les fins de phrases.
        Chaque chunk contiendra un nombre de tokens inférieur à (max_tokens - safety_margin).

        Args:
            text (str): Texte à découper.
            max_tokens (int): Nombre maximum de tokens du modèle.
            safety_margin (int): Marge de sécurité pour éviter de dépasser la limite.
            tokenizer: Un tokenizer disposant de méthodes encode/decode (ex : celui de HuggingFace).

        Returns:
            list[str]: Liste de chunks respectant la fin des phrases.
        """
        tokens_per_chunk = max_tokens - safety_margin
        chunks = []

        if tokenizer is not None:
            # On découpe d'abord le texte en phrases à l'aide de nltk
            sentences = tokenizer.sent_tokenize(text)
            current_chunk = ""
            current_tokens = 0

            for sentence in sentences:
                # On calcule le nombre de tokens de la phrase courante
                sentence_tokens = len(tokenizer.encode(sentence))
                # Si l'ajout de cette phrase dépasse la limite
                if current_tokens + sentence_tokens > tokens_per_chunk:
                    # On enregistre le chunk actuel s'il n'est pas vide
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # On démarre un nouveau chunk avec la phrase en cours
                    current_chunk = sentence + " "
                    current_tokens = sentence_tokens
                else:
                    # Sinon, on ajoute la phrase au chunk en cours
                    current_chunk += sentence + " "
                    current_tokens += sentence_tokens

            # Ajouter le dernier chunk s'il reste du texte
            if current_chunk:
                chunks.append(current_chunk.strip())
        else:
            # Si aucun tokenizer n'est fourni, on peut utiliser une segmentation approximative par ponctuation.
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = ""
            current_words = 0  # estimation grossière: 1 mot ≈ 1 token

            for sentence in sentences:
                sentence_words = len(sentence.split())
                if current_words + sentence_words > tokens_per_chunk:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
                    current_words = sentence_words
                else:
                    current_chunk += sentence + " "
                    current_words += sentence_words

            if current_chunk:
                chunks.append(current_chunk.strip())

        return chunks

    def generate_synthesis_on_row(self, text, model, max_tokens=None, llm="gpt4all"):
        """
        Découpe le texte en chunks adaptés à la taille maximale en tokens
        et applique directement la synthèse en cascade sur ces chunks pour obtenir un résumé final.
        """
        # Utilisation de la valeur de self.context_length si max_tokens n'est pas spécifié
        if max_tokens is None:
            max_tokens = self.context_length or 4096

        # Découpage du texte en chunks avec marge de sécurité
        chunks = self.split_text_into_chunks(text, max_tokens, safety_margin=1000, tokenizer=self.tokenizer)

        # Application directe de la synthèse en cascade sur les chunks
        final_summary = self.cascade_summary_on_summaries(chunks, model, max_tokens, llm=llm, safety_margin=1000)
        return final_summary

    def cascade_summary_on_summaries(self, texts, model, max_tokens, llm="gpt4all", safety_margin=1000):
        """
        Condense de manière itérative une liste de textes (chunks ou résumés partiels)
        afin d'obtenir un résumé final qui tient dans la limite de tokens autorisée.
        """
        current_texts = texts
        if len(current_texts) == 1:
            return self.generate_synthesis_on_chunk(model, current_texts[0], llm=llm, max_tokens=max_tokens)
        while len(current_texts) > 1:
            new_texts = []
            batch = []
            batch_token_count = 0

            for txt in current_texts:
                token_count = len(self.tokenizer.encode(txt))
                # Si le batch n'est pas vide et que l'ajout de ce texte dépasse la limite,
                # alors on résume le batch actuel
                if batch and (batch_token_count + token_count > max_tokens - safety_margin):
                    batch_text = "\n\n".join(batch)
                    summarized = self.generate_synthesis_on_chunk(model, batch_text, llm=llm, max_tokens=max_tokens, prompt_template=prompt3)
                    new_texts.append(summarized)
                    batch = [txt]
                    batch_token_count = token_count
                else:
                    batch.append(txt)
                    batch_token_count += token_count

            # Résumé du dernier batch s'il n'est pas vide
            if batch:
                batch_text = "\n\n".join(batch)
                summarized = self.generate_synthesis_on_chunk(model, batch_text, llm=llm, max_tokens=max_tokens, prompt_template=prompt4)
                new_texts.append(summarized)

            current_texts = new_texts
        return current_texts[0]


    def generate_synthesis_on_chunk(self, model, text, llm="gpt4all", max_tokens=None, temperature=0, top_p=0,
                                    top_k=50, stop_tokens=None, prompt_template=""):
        """
        Génère une synthèse à partir d'un chunk de texte en appelant le LLM.
        """
        # Utilisation de self.context_length si max_tokens n'est pas précisé
        if max_tokens is None:
            max_tokens = self.context_length or 4096

        prompt = format_prompt(prompt_template, text)

        if llm == "gpt4all":
            try:
                localhost = "localhost:4891"
                response = GPT4ALL.call_completion_api(localhost=localhost, message_content=prompt,model_name=model,temperature=temperature,top_p=top_p,max_tokens=max_tokens)
                answer = GPT4ALL.clean_response(response)
                return answer.strip()
            except Exception as e:
                return f"Error generating synthesis: {e}"

        if llm == "lmstudio":
            try:
                response = lmstudio.appel_lmstudio(prompt, model, max_tokens=max_tokens)
                return response
            except Exception as e:
                return f"Error generating synthesis: {e}"

    def generate_synthesis_on_table(self, table, model, llm="gpt4all", progress_callback=None, argself=None):
        """
        Applique la synthèse sur chaque ligne de la table et ajoute le résumé dans une nouvelle colonne.
        """
        data = copy.deepcopy(table)
        new_metas = list(data.domain.metas) + [StringVariable("Synthesis")]
        new_domain = Domain(data.domain.attributes, data.domain.class_vars, new_metas)
        new_rows = []
        # Utilisation de self.context_length pour la limite de tokens
        max_tokens = self.context_length or 4096
        for i, row in enumerate(data):
            print(f"\n\n -- Working on row {i}")
            content = row["content"].value
            synthesis = self.generate_synthesis_on_row(content, model, max_tokens=max_tokens, llm=llm)
            new_metas_values = list(row.metas) + [synthesis]
            new_instance = Orange.data.Instance(new_domain,
                                                [row[x] for x in data.domain.attributes] +
                                                [row[y] for y in data.domain.class_vars] +
                                                new_metas_values)
            new_rows.append(new_instance)
            if progress_callback is not None:
                progress_value = float(100 * (i + 1) / len(data))
                progress_callback(progress_value)
            if argself:
                if argself.stop:
                    break

        out_data = Table.from_list(domain=new_domain, rows=new_rows)
        return out_data


def format_prompt(template: str, text: str) -> str:
    return template.format(text=text)

prompt1 = """### Contexte : Tu es un assistant de synthèse documentaire. Ton objectif est d'identifier et de lister les points essentiels d'un extrait de document envoyé par un User.


### Instructions :
- Lis le document qui suit.
- Liste les éléments essentiels sous la forme d'une liste avec des tirets.
- Répond dans la langue du document analysé.
- N'ajoute aucun commentaire à ta réponse.


### User : Voici un extrait de document.

{text}




### Assistant:"""

prompt2 = """### Contexte : Tu es un assistant de synthèse documentaire. Un User t'envoie une liste de tous les éléments essentiels contenus dans un document.

### Instructions :
- Lis la liste qui suit.
- Déduis de cette liste le résumé final du document complet.
- Rédige le résumé de façon structurée, en utilisant un format Markdown.
- N'ajoute aucun commentaire à ta réponse.


### User : Voici les éléments de mon document.

{text}



### Assistant :# Résumé du document"""


prompt3 = """### Contexte : Tu es un assistant de synthèse documentaire. Ton objectif est de résumer extrait de document envoyé par un User.


### Instructions :
- Lis l'extrait de document qui suit.
- Rédige un résumé du document.
- Répond dans la langue du document analysé.
- N'ajoute aucun commentaire à ta réponse.


### User : Voici un extrait de document.

{text}




### Assistant: Résumé de l'extrait :"""

prompt4 = """### Contexte : Tu es un assistant de synthèse documentaire. Un User t'envoie un document qui a été résumé par parties. Ton objectif est de produire le résumé global.

### Instructions :
- Lis le texte qui suit.
- Déduis de ce texte le résumé final du document complet.
- Rédige le résumé de façon structurée, en utilisant un format Markdown.
- N'ajoute aucun commentaire à ta réponse.


### User : Voici le résumé par partie de mon document complet.

{text}



### Assistant :# Résumé du document"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWGenerateSynthesis()
    my_widget.show()
    app.exec_()
