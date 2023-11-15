# -*- coding:utf-8 -*-
"""
    问句解析的主调模块
"""
import spacy
from spacy_lookup import Entity
from paddlenlp import Taskflow
from QAQ import QueryPretreat
from Qsplit import QuerySplit
from infor_ana import line_break, entity_dict
# from infor_ana import schemaen,schemazh,transiezh,schemaam
from infor_ana import eentity_dict, zentity_dict, ementity_dict, zmentity_dict, schemaam

from infor_ana import re_att_dict, add_who, add_what



def addhead(q_in):
    q = q_in
    q = q.replace("What's","What is")
    q = q.replace("what's","what is")
    if 'what is' in q or 'What is' in q:
        return q    
    for item in ['who','Who']:
        if item in q:
            return q.replace(item,'what person')    
    return q_in

def retrive2qa(q_in):
    q = q_in
    if 'what' in q or 'who' in q or 'which' in q or 'What' in q or 'Who' in q or 'Which' in q:
        return q_in
    for item in add_who:
        if item in q:
            q = q.strip(item)
            return 'Who ' + item.lower() + ' ' + q
    for item in add_what:
        if item in q:
            temp = 'what ' + item.lower()
            q = q.replace(item, temp)
            q_temp = q.split(' ')
            if q_temp[0] == 'what':
                return q.replace(q_temp[1], q_temp[1] + ' is')
            else:
                return q
    return q_in

def Qana_forward(q,q_pre,q_split):
    lang, q, propdict = q_pre.forward_pre(q)
    # 输入：问题字符串
    # 返回：语言、预处理后的问句、实体属性字典
    # print(propdict)
    q = retrive2qa(q)
    q = addhead(q)
    # print(q)
    query_splited = q_split.forward_split(q)
    # 输入：问题
    # 返回：logic, question_set, neg_label, proplist
    # print(query_splited['proplist'])
    output = {'id':'NULL'}
    for prop_sep in query_splited["proplist"]:
        # print(prop_sep)
        l = prop_sep[-1]
        if l[2] in ['No link','No what','REQU']:
            output['id']=l[2]
        if l[2] == '?':
            if output['id']=='NULL':
                output['id']=l[0]
                if l[0] in propdict.keys():
                    output['type'] = propdict[l[0]]['type']
                else:
                    if ('person' in l[0]): typenow = 'person'
                    elif ('movie' in l[0]): typenow = 'movie'
                    elif ('company' in l[0]): typenow = 'company'
                    else: typenow = 'event'
                    output['type'] = typenow
                if l[1]=='name':
                    if output['type'] == 'movie':
                        if lang == 'en': l[1]='mnamee'
                        else: l[1]='mnamez'
                    elif output['type'] == 'person': l[1]='pname'
                if l[1] in re_att_dict.keys():
                    l[1] = re_att_dict[l[1]]
                output['prop'] = [l[1],l[2]]

        for l in prop_sep[:-1]:
            # print(l)
            tl = l[1]
            if tl in re_att_dict.keys():tl = re_att_dict[tl]
            if (l[0]==output['id'])and(tl==output['prop'][0])or(l[2] in propdict.keys()):continue
            if l[0] in propdict.keys():
                if l[1] in re_att_dict.keys():
                    l[1] = re_att_dict[l[1]]
                if [l[1],l[2]] not in propdict[l[0]]['prop']:
                    propdict[l[0]]['prop'].append([l[1],l[2]])
            else:
                if ('person' in l[0]): typenow = 'person'
                elif ('movie' in l[0]): typenow = 'movie'
                elif ('company' in l[0]): typenow = 'company'
                else: typenow = 'event'
                if l[1] in re_att_dict.keys():
                    l[1] = re_att_dict[l[1]]
                propdict[l[0]] = {
                    'type':typenow,
                    'prop':[[l[1],l[2]]]
                }
    
    results = {
        'lang': lang,
        'logic':query_splited['logic'],
        'question_set':query_splited['question_set'],
        'neg_label':query_splited['neg_label'],
        'propdict':propdict,
        'output':output
    }
        
    return results


if __name__ == '__main__':

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

    print("===============Input quesiton=================")
    
    for question in open("questions/question1.txt", errors="ignore", encoding='utf-8').readlines():
        question = question.strip(line_break) 
        print("------------------------------------------------------------------------------------")
        print(question)
        results = Qana_forward(question,q_pre,q_split)
        print(results)
        print("------------------------------------------------------------------------------------")

   