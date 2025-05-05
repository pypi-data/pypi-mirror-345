from typing import Optional

from vnerrant.components.en.constants import (
    ChildrenErrorType,
    ParentErrorType,
    base_dir,
    language_resources,
)
from vnerrant.components.postprocessor import BasePostprocessor
from vnerrant.constants import Operator, SeparatorTypes
from vnerrant.model.edit import EditCollection
from vnerrant.utils.replacing import ReplacingRule
from vnerrant.utils.wordlist import WordListAdapter


class Postprocessor(BasePostprocessor):

    def __init__(self):
        self.noun_wordlist = self._import(WordListAdapter, "wrong_nouns.txt")
        self.replacing_rule = self._import(ReplacingRule, "replacing.dat")

    @staticmethod
    def _import(obj_class, filename: Optional[str] = None):
        data_path = base_dir / "resources"
        if filename:
            data_path = data_path / filename

        if data_path.exists():
            return obj_class(data_path.absolute().as_posix())
        else:
            return None

    def process(self, edit_collection: EditCollection, **kwargs):
        self._postprocess_noun_number(edit_collection)
        self._postprocess_verb_choice(edit_collection)
        self._postprocess_adverb(edit_collection)
        self._postprocess_determiner(edit_collection)
        self._postprocess_verb_tense(edit_collection)
        self._postprocess_verb_form(edit_collection)
        self._postprocess_spelling(edit_collection)
        self._postprocess_question_tag(edit_collection)

    def _postprocess_noun_number(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for noun number.
        Update NOUN_NUMBER -> NOUN_INFLECTION if the word is in the noun wordlist.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        if self.noun_wordlist is None:
            return

        noun_number = (
            ParentErrorType.NOUN + SeparatorTypes.COLON + ChildrenErrorType.NUMBER
        )
        noun_inflection = (
            ParentErrorType.NOUN + SeparatorTypes.COLON + ChildrenErrorType.INFLECTION
        )

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != noun_number:
                continue

            text = edit.original.text.strip().lower()
            if self.noun_wordlist.check(text):
                edit.edit_type = edit.edit_type[:2] + noun_inflection

            # special case "every days" -> "every day"
            index = edit.original.start_token
            if (
                text == "days"
                and index - 1 >= 0
                and edit_collection.orig_doc[index - 1].lower_ == "every"
            ):
                edit.edit_type = edit.edit_type[:2] + noun_inflection

    def _postprocess_verb_choice(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for verb choice.
        Update VERB_CHOICE -> VERB_INFLECTION if the corrected word is in the replacing rule.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        if self.replacing_rule is None:
            return

        verb_choice = ParentErrorType.VERB
        verb_inflection = (
            ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.INFLECTION
        )

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != verb_choice:
                continue

            text = edit.original.text.strip()
            corrected = edit.corrected.text.strip()
            replacing = self.replacing_rule.suggest(text)
            if corrected in replacing:
                edit.edit_type = edit.edit_type[:2] + verb_inflection

    def _postprocess_adverb(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for adverb.
        Update ADV -> ADJECTIVE_FORM if the word is in {more, most} and place before an adj.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """

        def _is_next_token_adj(doc, index):
            if index < len(doc):
                return doc[index].pos_ == "ADJ"
            return False

        adverb_choice = ParentErrorType.ADVERB
        adjective_form = (
            ParentErrorType.ADJECTIVE + SeparatorTypes.COLON + ChildrenErrorType.FORM
        )

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != adverb_choice:
                continue

            original = edit.original.text.strip().lower()
            corrected = edit.corrected.text.strip().lower()

            if original in ["more", "most"]:
                next_token_index = edit.original.start_token + 1
                if _is_next_token_adj(edit_collection.orig_doc, next_token_index):
                    edit.edit_type = edit.edit_type[:2] + adjective_form

            if corrected in ["more", "most"]:
                next_token_index = edit.corrected.start_token + 1
                if _is_next_token_adj(edit_collection.cor_doc, next_token_index):
                    edit.edit_type = edit.edit_type[:2] + adjective_form

    def _postprocess_determiner(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for determiner.
        Update DET -> PRONOUN because the wrong pos mapping.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        determiner = ParentErrorType.DETERMINER
        pronoun = ParentErrorType.PRONOUN

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != determiner:
                continue

            relative_pronouns = [
                "that",
                "which",
                "who",
                "whom",
                "whose",
                "where",
                "whoever",
                "whomever",
            ]

            if (
                edit.original.end_token - edit.original.start_token == 1
                and edit.original.tokens
            ):
                if (
                    edit.original.tokens[0].pos_ == "PRON"
                    and edit.original.text.strip().lower() in relative_pronouns
                ):
                    edit.edit_type = edit.edit_type[:2] + pronoun

            if (
                edit.corrected.end_token - edit.corrected.start_token == 1
                and edit.corrected.tokens
            ):
                if (
                    edit.corrected.tokens[0].pos_ == "PRON"
                    and edit.corrected.text.strip().lower() in relative_pronouns
                ):
                    edit.edit_type = edit.edit_type[:2] + pronoun

    def _postprocess_verb_tense(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for verb tense.
        Update VERB_TENSE -> VERB_CHOICE if both original and corrected are verb, have same tag and different lemma.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        verb_tense = (
            ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.TENSE
        )
        verb_choice = ParentErrorType.VERB

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != verb_tense:
                continue
            if edit.original.end_token - edit.original.start_token != 1:
                continue
            if edit.corrected.end_token - edit.corrected.start_token != 1:
                continue
            if not edit.original.tokens or not edit.corrected.tokens:
                continue

            o_token = edit.original.tokens[0]
            c_token = edit.corrected.tokens[0]

            if o_token.tag_ == c_token.tag_ and o_token.lemma_ != c_token.lemma_:
                edit.edit_type = edit.edit_type[:2] + verb_choice

    def _postprocess_verb_form(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for verb form.
        Update VERB_FORM -> VERB_TENSE if either original or corrected is verb, and tag is in [VBN, VBD]
        Update VERB_FORM -> SUBJECT_VERB_AGREEMENT because the wrong pos in special case "has/have"

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        verb_form = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.FORM
        verb_tense = (
            ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.TENSE
        )
        subject_verb_agreement = (
            ParentErrorType.VERB
            + SeparatorTypes.COLON
            + ChildrenErrorType.SUBJECT_VERB_AGREEMENT
        )

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != verb_form:
                continue
            if edit.original.end_token - edit.original.start_token != 1:
                continue
            if edit.corrected.end_token - edit.corrected.start_token != 1:
                continue
            if not edit.original.tokens or not edit.corrected.tokens:
                continue

            o_token = edit.original.tokens[0]
            c_token = edit.corrected.tokens[0]

            # VERB_FORM -> VERB_TENSE
            if (
                o_token.tag_ in ["VBN", "VBD"] or c_token.tag_ in ["VBN", "VBD"]
            ) and o_token.tag_ != c_token.tag_:
                edit.edit_type = edit.edit_type[:2] + verb_tense
                continue

            # VERB_FORM -> SUBJECT_VERB_AGREEMENT
            if (
                edit.original.text.strip().lower() in ["has", "have"]
                and edit.corrected.text.strip().lower() in ["has", "have"]
                and c_token.tag_ in ["VB", "VBZ"]
            ):
                edit.edit_type = edit.edit_type[:2] + subject_verb_agreement

    def _postprocess_spelling(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for spelling.
        Update SPELLING -> SUBJECT_VERB_AGREEMENT because the wrong pos in special case "like/likes"
        Update SPELLING -> NOUN_INFLECTION because the wrong lemma of some special wrong nouns (technologys, studys).

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        spelling = ParentErrorType.SPELLING
        subject_verb_agreement = (
            ParentErrorType.VERB
            + SeparatorTypes.COLON
            + ChildrenErrorType.SUBJECT_VERB_AGREEMENT
        )
        noun_inflection = (
            ParentErrorType.NOUN + SeparatorTypes.COLON + ChildrenErrorType.INFLECTION
        )

        for edit in edit_collection.edits:
            if edit.edit_type[2:] != spelling:
                continue
            if edit.original.end_token - edit.original.start_token != 1:
                continue
            if edit.corrected.end_token - edit.corrected.start_token != 1:
                continue
            if not edit.original.tokens or not edit.corrected.tokens:
                continue

            # SPELLING -> SUBJECT_VERB_AGREEMENT
            if (
                edit.original.text.strip().lower() in ["like", "likes"]
                and edit.corrected.text.strip().lower() in ["like", "likes"]
                and edit.corrected.tokens[0].tag_ in ["VB", "VBZ"]
            ):
                edit.edit_type = edit.edit_type[:2] + subject_verb_agreement
                continue

            # SPELLING -> NOUN_INFLECTION
            if (
                edit.original.text.strip().isalpha()
                and edit.original.tokens[0].text not in language_resources.spell
                and edit.original.tokens[0].lower_ not in language_resources.spell
                and edit.corrected.tokens[0].pos_ == "NOUN"
                and edit.corrected.text.strip()
                in self.replacing_rule.suggest(edit.original.text.strip())
            ):
                edit.edit_type = edit.edit_type[:2] + noun_inflection
                continue

    def _postprocess_question_tag(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for contraction.
        Update CONTRACTION -> QUESTION TAG

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        # question have pattern
        # aux[not] + proun + ?
        for edit in edit_collection.edits:
            parent_error = edit.edit_type.split(":")[1]
            operator = edit.edit_type.split(":")[0]
            orig_start = edit.original.start_token
            corr_start = edit.corrected.start_token
            if (
                parent_error == ParentErrorType.CONTRACTION
            ):  # For mising and unnecessary contractions
                # e.g. "Isn't he?" -> "Is he?"
                if operator == Operator.MISSING:
                    if (
                        edit.original.tokens.doc[orig_start + 1].pos_ == "PRON"
                        and edit.original.tokens.doc[orig_start + 2].text == "?"
                        and edit.corrected.tokens.doc[corr_start + 2].pos_ == "PRON"
                        and edit.corrected.tokens.doc[corr_start + 3].text == "?"
                    ):
                        edit.edit_type = (
                            edit.edit_type[:2] + ParentErrorType.QUESTION_TAG
                        )
                elif operator == Operator.UNNECESSARY:
                    if (
                        edit.original.tokens.doc[orig_start + 2].pos_ == "PRON"
                        and edit.original.tokens.doc[orig_start + 3].text == "?"
                        and edit.corrected.tokens.doc[corr_start + 1].pos_ == "PRON"
                        and edit.corrected.tokens.doc[corr_start + 2].text == "?"
                    ):
                        edit.edit_type = (
                            edit.edit_type[:2] + ParentErrorType.QUESTION_TAG
                        )
            if parent_error == ParentErrorType.VERB:
                plus_idx = 0
                if edit.original.tokens.doc[orig_start + 1].text in ["n't", "not"]:
                    plus_idx = 1
                if (
                    edit.original.tokens.doc[orig_start + 1 + plus_idx].pos_ == "PRON"
                    and edit.original.tokens.doc[orig_start + 2 + plus_idx].text == "?"
                    and edit.corrected.tokens.doc[corr_start + 1 + plus_idx].pos_
                    == "PRON"
                    and edit.corrected.tokens.doc[corr_start + 2 + plus_idx].text == "?"
                ):
                    edit.edit_type = edit.edit_type[:2] + ParentErrorType.QUESTION_TAG
