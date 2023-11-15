# -*- coding:utf-8 -*-
"""
    主调模块
"""
from flask import Flask, request, jsonify
import json
from flask_cors import CORS, cross_origin
from infer_main import answer_inference, addition_info_query
import time
import re

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/qa', methods=['GET', 'POST'])
def qa():
    t1 = time.time()
    print(request)
    if request.method == 'GET':
        question = request.args.get("question")
        print(question)
        try:
            answer, cypher = answer_inference(question)
        except:
            answer, cypher = answer_inference(question)

        if len(answer) == 0:
            print('answer cannot be found')
            return app.response_class(
            response=json.dumps({
                "answer": ["answer cannot be found"],
                "cypher": cypher}),
            mimetype='application/json'
        )
        else:

            add_visual = addition_info_query(cypher)
            for v in answer:
                print(v)
                # q_return = q_return + ' ' + v['text'] + ','
            print(time.time() - t1)
            return app.response_class(
                response=json.dumps({
                    # "q_return": q_return,
                    "answer": answer,
                    "cypher": cypher,
                    "addition": add_visual}),
                mimetype='application/json'
            )

    return '{}'


app.run(host='0.0.0.0', port=8203, debug=True)
