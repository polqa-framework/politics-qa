from polqa.evaluation.scoring import accumulate_scores, classify

def test_accumulate_and_classify():
    q1 = {"options": {
        "A": {"text":"", "scores":{"economic":-2,"social":-1}},
        "B": {"text":"", "scores":{"economic":0,"social":0}},
        "C": {"text":"", "scores":{"economic":2,"social":1}},
    }}
    q2 = {"options": {
        "A": {"text":"", "scores":{"economic":-1,"social":-2}},
        "B": {"text":"", "scores":{"economic":0,"social":0}},
        "C": {"text":"", "scores":{"economic":1,"social":2}},
    }}
    answers = [(q1, "A"), (q2, "C")]
    scores = accumulate_scores(answers)
    assert scores["economic"] == -1
    assert scores["social"] == 1
    label = classify(scores)
    assert isinstance(label, str)
