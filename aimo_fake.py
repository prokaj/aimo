import pandas as pd
import json 
import postprocess

cleaned_problems = '../input/aimo-script/cleaned_problems.json'

class FakeEnv:

    def __init__(self, questions):
        self.questions = questions
        self.answers = []
        
    def iter_test(self):
        for i, (q, a) in enumerate(self.questions):
            yield (
                pd.DataFrame([{'id':i, 'problem': q}]).set_index('id'), 
                pd.DataFrame([{'id':i, 'answer':0, 'true answer': a}]).set_index('id')
            )
        
        
    def predict(self, submission):
        self.answers.append(submission)

def make_env():
    with open(cleaned_problems) as f:
        data = json.load(f) 
    numeric_problems = []
    for problem in data:
        ans = postprocess.get_answers(problem['solutions'])
        if len(ans)==1:
            problem['answer'] = next(iter(ans.keys()))
            numeric_problems.append(problem)
            
    questions = [
        ("What is 1 + 1?", 2),
        ("What is 2 + 2?", 4),
        ("What is 3 + 3?", 6),
        ("What is 4 + 4?", 8),
        ("What is 5 + 5?", 10),
    ]
    questions.extend([(d['problem'], d['answer']) for d in numeric_problems]) 
    return FakeEnv(questions)        
