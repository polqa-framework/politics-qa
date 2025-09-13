from polqa.evaluation.prompt_builder import build_prompt

def test_force_instruction():
    q = {"prompt":"Q?","options":{"A":{"text":"ta","scores":{"economic":0,"social":0}},
                                  "B":{"text":"tb","scores":{"economic":0,"social":0}}}}
    p = build_prompt(q, force=True)
    assert "Respond only with the letter of your choice" in p
