import spacy
from spacy_lookup import Entity
import numpy as np
import re
from infor_ana import replace_dict,re_att_dict
from infor_ana import eentity_dict, zentity_dict, ementity_dict, zmentity_dict

import requests
import random
import json
from hashlib import md5
import time

# from paddlenlp import Taskflow


class QueryPretreat:
    # def __init__(self,iezh,ieen,transiezh):
        # self.__iezh = iezh
        # self.__ieen = ieen
        # self.__transiezh = transiezh
    
    def __init__(self,emnlp,zmnlp,enlp,znlp,mdict_keys,edict_keys,zdict_keys):
        self.__emnlp = emnlp
        self.__zmnlp = zmnlp
        self.__enlp = enlp
        self.__znlp = znlp
        self.__mdict_keys = mdict_keys
        self.__edict_keys = edict_keys
        self.__zdict_keys = zdict_keys

    def enorzh_question(self, question):
        ch = question[0]
        if ('A'<=ch and ch<='Z')or('a'<=ch and ch<='z'):
            self.__isenglish = True
        else:
            self.__isenglish = False
        if self.__isenglish:
            return 'en'
        else:
            return 'zh'
    
    def getentity(self,question):
        propdict = {}

        # 电影实体
        mnum = 0
        qstr = question
        typenow = 'movie'
        if self.__isenglish:
            typename = 'primaryTitle'
            temp = re.split(r'\"',qstr)
        else:
            typename = 'Chinese_title'
            temp = re.split(r'[“”\"]',qstr)
        ansq = ""
        for i,ch in enumerate(temp):
            if i % 2 == 1:
                mnum +=1
                m = 'M' + str(mnum)
                ansq = ansq + m
                propdict[m] = {
                        'type':typenow,
                        'prop':[[typename,ch]]
                    }
            else:
                ansq = ansq + ch
        if mnum == 0:
            if self.__isenglish:
                qstr = self.__emnlp(ansq)
                ansq = ""
                for token in qstr:
                    if not(ansq == ""):
                        if token.text!=')' and qstr[token.i-1].text!='(':
                            ansq = ansq + " "
                    if token.ent_type_ in self.__mdict_keys:
                        mnum +=1
                        m = 'M' + str(mnum)
                        ansq = ansq + m
                        propdict[m] = {
                                'type':typenow,
                                'prop':[[typename,token.text]]
                            }
                    else:
                        ansq = ansq + token.text
            else:
                qstr = self.__zmnlp(ansq)
                ansq = ""
                for token in qstr:
                    if token.ent_type_ in self.__mdict_keys:
                        mnum +=1
                        m = 'M' + str(mnum)
                        ansq = ansq + m
                        propdict[m] = {
                                'type':typenow,
                                'prop':[[typename,token.text]]
                            }
                    else:
                        ansq = ansq + token.text
        
        # 人&公司实体
        if self.__isenglish:
            entnum = {}
            for key in self.__edict_keys:
                rename = str.upper(key[0])
                entnum[rename] = 0
            doc = self.__enlp(ansq)       
            ansq = ""
            for token in doc:
                if not (ansq == ""):
                    ansq = ansq + " "               
                if token.ent_type_ in self.__edict_keys:
                    typenow = token.ent_type_
                    rename = str.upper(typenow[0])
                    if rename == 'P':
                        typename = 'primaryName'
                    else:
                        typename = 'name'
                    entnum[rename] += 1
                    retext = rename + str(entnum[rename])
                    ansq = ansq + retext
                    propdict[retext] = {
                            'type':typenow,
                            'prop':[[typename,token.text]]
                        }
                else:
                    ansq = ansq + token.text
        else:
            entnum = {}
            for key in self.__zdict_keys:
                rename = str.upper(key[0])
                entnum[rename] = 0
            doc = self.__znlp(ansq)       
            ansq = ""
            for token in doc: 
                if token.ent_type_ in self.__zdict_keys:
                    typenow = token.ent_type_
                    rename = str.upper(typenow[0])
                    if rename == 'P':
                        typename = 'primaryName'
                    else:
                        typename = 'name'
                    entnum[rename] += 1
                    retext = rename + str(entnum[rename])
                    ansq = ansq + retext
                    propdict[retext] = {
                            'type':typenow,
                            'prop':[[typename,token.text]]
                        }
                else:
                    ansq = ansq + token.text
                
        return ansq, propdict

    # def getentity(self,question,entdict):
    #     propdict = {}
    #     newq = question
    #     entnum = {}
    #     for enttype in entdict.keys():
    #         if self.__isenglish:
    #             typenow = enttype
    #             rename = str.upper(typenow[0])
    #             if rename == 'M':
    #                 typename = 'primaryTitle'
    #             elif rename == 'P':
    #                 typename = 'primaryName'
    #             else:
    #                 typename = 'name'
    #         else:
    #             typenow = self.__transiezh[enttype]
    #             rename = str.upper(typenow[0])
    #             if rename == 'M':
    #                 typename = 'Chinese_title'
    #             elif rename == 'P':
    #                 typename = 'primaryName'
    #             else:
    #                 typename = 'name'
    #         entnum[rename] = 0
    #         for ent in entdict[enttype]:
    #             if ent['text'] in newq:
    #                 entnum[rename] += 1
    #                 retext = rename + str(entnum[rename])
    #                 propdict[retext] = {
    #                     'type':typenow,
    #                     'prop':[[typename,ent['text']]]
    #                 }
    #                 newq = newq.replace(ent['text'],retext,1)
    #     return newq, propdict

    def backname(self, triple_set, entlist):
        t = triple_set
        e = entlist
        if len(t)<5:
            for i,name in enumerate(t[1]):
                if name in e.keys():
                    t[1][i] = e[name]
            return t
        for i,name in enumerate(t[1]):
            if name in e.keys():
                t[1][i] = e[name]
        for i,name in enumerate(t[3]):
            if name in e.keys():
                t[3][i] = e[name]
        return t
    
    def atttodict(self, attlist, propdict,la):
        # print("*****************************************")
        a = attlist
        # print(a)
        pd = propdict
        for l in a:
            if l[2] in ['No link','No what','REQU','?']:
                continue
            if l[0] in pd.keys():
                if l[1] in re_att_dict.keys():
                    l[1] = re_att_dict[l[1]]
                pd[l[0]]['prop'].append([l[1],l[2]])
            else:
                if ('person' in l[0]):
                    typenow = 'person'
                elif ('movie' in l[0]):
                    typenow = 'movie'
                elif ('company' in l[0]):
                    typenow = 'company'
                else:
                    typenow = 'NULL'
                if l[1] in re_att_dict.keys():
                    l[1] = re_att_dict[l[1]]
                pd[l[0]] = {
                    'type':typenow,
                    'prop':[[l[1],l[2]]]
                }
            # flag = 'n'
            # if l[0] in e.keys():
            #     k = e[l[0]]
            #     if (l[0][0]=='p')or(l[0][0]=='P'): flag = 'p'
            #     elif (l[0][0]=='m')or(l[0][0]=='M'): flag = 'm'
            # else:
            #     k = l[0]
            #     if ('person' in l[0]): flag = 'p'
            #     elif ('movie' in l[0]): flag = 'm'
            # if l[1] == 'name':
            #     if flag == 'p': l[1] = 'pname'
            #     elif flag == 'm':
            #         if la == 'en': l[1] = 'mnamee'
            #         else: l[1] = 'mnamez'
            # if l[1] in re_att_dict.keys():
            #     l[1] = re_att_dict[l[1]]
            # ad.append([k,l[1],l[2]])
        # print(ad)
        # print("*****************************************")
        return pd


    def make_md5(self, s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    def bdtrans(self,question):
        # Set your own appid/appkey.
        appid = '20210812000914833'
        appkey = 'cm3Sj9cJ6Z2nh3M9rVfR'
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = 'zh'
        to_lang =  'en'
        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path
        query = question
        print(query)
        # Generate salt and sign
        salt = random.randint(32768, 65536)
        sign = self.make_md5(appid + query + str(salt) + appkey)
        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()
        # Show response
        #print(json.dumps(result, indent=4, ensure_ascii=False))
        '''if ('error_code' in result.keys()):
                a=result['error_code']
                if (a == '54003'):
                    访问频繁了'''
        ans = result['trans_result'][0]['dst']
        #print(ans)
        for key in replace_dict.keys():
            ans = ans.replace(key,replace_dict[key])
        # ans = ans.replace(",", " and")
        # ans = ans.replace("prize", "award")
        # ans = ans.replace("film","movie")
        time.sleep(1)
        print(ans)
        return ans
    

    def forward_pre(self, question):
        '''
            前向主调函数
            输入：问题字符串
            返回：语言、预处理后的问句、实体属性字典
        '''
        lang = self.enorzh_question(question)
        # if self.__isenglish:
        #     entdict = self.__ieen(question)[0]
        # else:
        #     entdict = self.__iezh(question)[0]
        # print(entdict)
        newq, propdict = self.getentity(question)
        # newq, movielist, movienum = self.getmovie(question)
        # print(newq)
        # newq, entlist, entnum = self.getentity(newq)
        # print(newq)
        if not(self.__isenglish):
            newq = self.bdtrans(newq)
        return lang, newq, propdict

if __name__=="__main__":


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

    # print("Prepare paddle")
    # schemazh = ['电影', '人名', '公司']
    # transiezh = {
    #     '电影':'movie',
    #     '人名':'person',
    #     '公司':'company'
    # }
    # schemaen = ['movie', 'person', 'company']
    # iezh = Taskflow('information_extraction', schema=schemazh)
    # ieen = Taskflow('information_extraction', schema=schemaen, model='uie-base-en')
    
    # questions = ['Who is actor of "Who is" and director of "The actor" and writer of "She"?'
    #                 ,'What movies is acted by Leonardo DiCaprio and Kate Winslet?'
    #                 ,'What movie is distributed by Tamjeed Elahi Khan Cinema or TC Entertainment (2018) (Japan) (Blu-ray)?']
    # questions = ['戚小波和韩哲参演了什么电影？'
    #                 ,'谁是"谁是"的演员和"演员"的导演以及"她"的编剧？'
    #                 ,'什么电影是刘氏财团或者敬亭文化有限公司发行的？']
    # questions = ['What movies is acted by Leonardo DiCaprio and Kate Winslet?']
    questions = ['吉姆·瑞吉尔和彼得·杰克逊共同导演了什么电影？']
    q_pre = QueryPretreat(emnlp,zmnlp,enlp,znlp,mdict_keys,edict_keys,zdict_keys)
    # q_pre = QueryPretreat(iezh,ieen,transiezh)

    for q in questions:
        print("----------------------------------------------------------------------")
        print(q)
        lang, question, entlist = q_pre.forward_pre(q)
        print(lang)
        print(question)
        print(entlist)
        print()
        triplet_set = ([],['M1','P2','C1'],[],['P1','M2','C2'],[])
        triplet_new = q_pre.backname(triplet_set, entlist)
        print(triplet_new)
        print("----------------------------------------------------------------------")
