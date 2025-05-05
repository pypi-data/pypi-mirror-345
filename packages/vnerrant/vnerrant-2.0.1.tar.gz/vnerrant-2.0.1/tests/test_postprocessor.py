import pytest

import vnerrant

annotator = vnerrant.load("en")


def test_postprocessor_single():
    original = "Many writers have drawn inspiration from nature for write their famous works."
    corrected = "Many writers have drawn inspiration from nature to write their famous works."
    edits = annotator.annotate_raw(original, corrected)
    for edit in edits:
        print(edit)


@pytest.mark.parametrize(
    "original, corrected",
    [("Eating junk foods are bad for you're health.", "Eating junk food is bad for your health.")],
)
def test_postprocess_noun_number_to_noun_inflection(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "NOUN:INFL"


@pytest.mark.parametrize(
    "original, corrected",
    [
        (
            "He gotted a new soccer shoes that fit him more better.",
            "He got a new pair of soccer shoes that fit him better.",
        ),
        (
            "In last holiday, we went to a very beautiful beaches and swimmed in the clear blue waters.",
            "In last holiday, we went to a very beautiful beaches and swam in the clear blue waters.",
        ),
    ],
)
def test_postprocess_verb_choice_to_verb_inflection(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "VERB:INFL"


@pytest.mark.parametrize(
    "original, corrected",
    [
        (
            "Eating healthy food can help you live longer and feel more better every day.",
            "Eating healthy food can help you live longer and feel better every day.",
        ),
    ],
)
def test_postprocess_adverb_to_adjective_form(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "ADJ:FORM"


@pytest.mark.parametrize(
    "original, corrected",
    [
        ("The book which I read yesterday is very interesting.", "The book that I read yesterday is very interesting."),
    ],
)
def test_postprocess_determiner_to_pronoun(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "PRON"


@pytest.mark.parametrize(
    "original, corrected",
    [
        (
            "Many species are being endangered due to deforestation.",
            "Many species are becoming endangered due to deforestation.",
        ),
    ],
)
def test_postprocess_verb_tense_to_verb_choice(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "VERB"


@pytest.mark.parametrize(
    "original, corrected",
    [
        (
            "The latest innovations in tech have make our lives much easier than before.",
            "The latest innovations in tech have made our lives much easier than before.",
        ),
        (
            "Eating too much fast food can leaded to health issues like obesity and high blood pressure.",
            "Eating too much fast food can lead to health issues like obesity and high blood pressure.",
        ),
        ("He has work here for two years.", "He has worked here for two years."),
        ("We going to the beach last summer.", "We went to the beach last summer."),
        (
            "The scientist explain that they had discovered a new element.",
            "The scientist explained that they had discovered a new element.",
        ),
    ],
)
def test_postprocess_verb_form_to_verb_tense(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "VERB:TENSE"


@pytest.mark.parametrize(
    "original, corrected",
    [
        (
            "Can I has those blue trousers and this yellow sweater?",
            "Can I have those blue trousers and this yellow sweater?",
        )
    ],
)
def test_postprocess_verb_form_to_verb_sva(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "VERB:SVA"


@pytest.mark.parametrize(
    "original, corrected",
    [
        ("She like the songs of that band.", "She likes the songs of that band."),
        (
            "He like painting, and he has created many beautiful pieces of art.",
            "He likes painting, and he has created many beautiful pieces of art.",
        ),
    ],
)
def test_postprocess_spelling_to_verb_sva(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "VERB:SVA"


@pytest.mark.parametrize(
    "original, corrected",
    [
        (
            "Advanced technologys are changing the face of modern medicine very quickly.",
            "Advanced technologies are changing the face of modern medicine very quickly.",
        ),
        (
            "Recent studys show that eating fewer carbohydrates can be beneficial.",
            "Recent studies show that eating fewer carbohydrates can be beneficial.",
        ),
    ],
)
def test_postprocess_spelling_to_noun_inflection(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    assert edits[0].edit_type[2:] == "NOUN:INFL"
