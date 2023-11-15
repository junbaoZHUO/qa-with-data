# -*- coding:utf-8 -*-
"""
    问句解析的主调模块
"""
import spacy
from spacy_lookup import Entity
from paddlenlp import Taskflow
from infer_ana import *
from answer_module.chain_of_logic import Triplet2Chain
from answer_module.answer_generator import Triplet2Answer
from functools import lru_cache


print("Prepare paddle")
# iezh = Taskflow('information_extraction', schema=schemazh)
# ieen = Taskflow('information_extraction', schema=schemaen, model='uie-base-en')
ieam = Taskflow('information_extraction', schema=schemaam, model='uie-base-en')

print("Prepare entity dictionary")
nlp = spacy.load('en_core_web_sm')
nlp.remove_pipe('ner')
entity_keys = entity_dict.keys()  # 可以提问的实体空间
for key, values in entity_dict.items():
    entity = Entity(keywords_list=values, label=key)
    nlp.add_pipe(entity, name=key)  # 添加确定识别的NER列表

print("Prepare english entity dictionary")
enlp = spacy.load('en_core_web_sm')  # 替换词表的spacy模型
enlp.remove_pipe('ner')
edict_keys = eentity_dict.keys()
for key, values in eentity_dict.items():
    entity = Entity(keywords_list=values, label=key)
    enlp.add_pipe(entity, name=key)

print("Prepare chinese entity dictionary")
znlp = spacy.load('zh_core_web_sm')  # 替换词表的spacy模型
znlp.remove_pipe('ner')
zdict_keys = zentity_dict.keys()
for key, values in zentity_dict.items():
    entity = Entity(keywords_list=values, label=key)
    znlp.add_pipe(entity, name=key)

print("Prepare english movie dictionary")
emnlp = spacy.load('en_core_web_sm')  # 替换词表的spacy模型
emnlp.remove_pipe('ner')
mdict_keys = set(ementity_dict.keys())
for key, values in ementity_dict.items():
    entity = Entity(keywords_list=values, label=key)
    emnlp.add_pipe(entity, name=key)

print("Prepare chinese movie dictionary")
zmnlp = spacy.load('zh_core_web_sm')  # 替换词表的spacy模型
zmnlp.remove_pipe('ner')
mdict_keys.update(set(zmentity_dict.keys()))
for key, values in zmentity_dict.items():
    entity = Entity(keywords_list=values, label=key)
    zmnlp.add_pipe(entity, name=key)

print("Import question pretreatment")
# q_pre = QueryPretreat(iezh,ieen,transiezh)
q_pre = QueryPretreat(emnlp,zmnlp,enlp,znlp,mdict_keys,edict_keys,zdict_keys)
print("Import question spliter")
q_split = QuerySplit(ieam, nlp, entity_keys)

logic_chain_generator = Triplet2Chain()

answer_generator = Triplet2Answer()



@lru_cache()
def answer_inference(question):
    question_components = Qana_forward(question, q_pre, q_split)

    print(question_components)

    if question_components["output"]["id"] == "REQU":
        relation_label = True
        triplet, attr_list = answer_generator.question_com_parser(question_components)
    else:
        # 链式逻辑输出
        question_list, entity_pron = logic_chain_generator.entity_substitute(question_components)
        logic_chain = logic_chain_generator.get_logic_chain(question_list)

        # 逻辑到查询（答案输出）
        relation_label = False
        print(logic_chain)
        triplet, attr_list = answer_generator.chain_parser(logic_chain, question_components, entity_pron)
    answer, visual_ans = answer_generator.get_answer(triplet, attr_list, question_components["logic"],
                                         question_components["neg_label"], relation_label)

    return answer, visual_ans


def addition_info_query(visual_ans):
    if (len(visual_ans["results"]) != 0) and (len(visual_ans["results"][0]["data"]) != 0):
        limitation = 3
        add_visual_ans = answer_generator.get_additional_answer(visual_ans, limitation)
    return add_visual_ans


if __name__ == '__main__':
    print("===============Input quesiton=================")
    for question in open("questions/question1.txt", errors="ignore", encoding='utf-8').readlines():
        question = question.strip(line_break) 
        print("------------------------------------------------------------------------------------")
        print(question)
        results, visual_ans = answer_inference(question)
        print(results)
        add_visual_resluts = addition_info_query(visual_ans)
        print(add_visual_resluts)
        input("------------------------------------------------------------------------------------")