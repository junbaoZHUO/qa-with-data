from tqdm import tqdm
import json
# import pandas as pd
import requests

# def fake_print(*args, **kwargs):
#     pass

# __builtins__.print = fake_print
flask_server = "http://" + "910.mivc.top" + ':20000/qa/qa?question='
answer_dict = {}
question_list = open("test_questions/qa_2.txt").readlines()
# df = pd.read_excel('Q.xlsx')
# question_list = list(df['Question'])

for idx, question in tqdm(enumerate(question_list), ncols=100, total=len(question_list)):
    # answers, visual_answer = answer_inference(question)
    try:
        # answers = requests.get('http://llgpu8.mivc.top:8080/qa?question=' + question).json()["answer"]
        answers = requests.get(flask_server + question).json()["answer"]
        if answers == 'answer cannot be found':
            input("no answer")
            answer_dict[str(idx)] = ["no answer"]
        else:
            answer_dict[str(idx)] = answers
            print(idx, answers)
    except:
        input("error")
        answer_dict[str(idx)] = "error"

with open('./answer_cn.json', 'a') as f:
    json_dump = json.dumps(answer_dict, indent=4, ensure_ascii=False)
    f.write(json_dump)
