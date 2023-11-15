"""
    问题拆分
    
"""
from os import replace
from unittest import result
from sklearn.cross_decomposition import PLSCanonical
import spacy
from spacy_lookup import Entity
import numpy as np
import re
# from sentence_transformers import SentenceTransformer, util
# import torch
# from termcolor import colored
# import itertools
from infor_ana import entity_dict
# from information import val_dict


# from information import remodel_dict
# import QperML

class QuerySplit:
    '''def __init__(self):
        """
        初始化
        question: 待处理问句
        """
        self.__ynlp = spacy.load('en_core_web_sm')  # 原版spacy模型
        self.__nlp = spacy.load('en_core_web_sm')  # 替换词表的spacy模型

        self.__nlp.remove_pipe('ner')

        self.__dict_keys = entity_dict.keys()

        for key, values in entity_dict.items():
            entity = Entity(keywords_list=values, label=key)
            self.__nlp.add_pipe(entity, name=key)

        self.__amod = set()  # 形容词类型集合
        for key, values in val_dict.items():
            self.__amod.add(key)
            entity = Entity(keywords_list=values, label=key)
            self.__nlp.add_pipe(entity, name=key)
        
        # self.__replace_num = {}
        # self.__replace_dict = {}
        # for key in self.__dict_keys:
        #     self.__replace_num[key] = 0

        self.__qnum = 1  # 问句数目
        self.__qs = []  # 问句列表（替换实体表浅）
        self.__qsy = []  # 问句列表（原词）
        self.__logic = []  # 逻辑词表
        self.__neg = []  # 问句列表中每个句子的否定状态'''
    
    def __init__(self, ieam, nlp, entity_keys):
        """
        初始化
        question: 待处理问句
        """
        
        self.__nlp = nlp  # 替换词表的spacy模型
        self.__ieam = ieam

        self.__dict_keys = entity_keys

        self.__qnum = 1  # 问句数目
        self.__qs = []  # 问句列表（替换实体表浅）
        self.__qsy = []  # 问句列表（原词）
        self.__logic = []  # 逻辑词表
        self.__neg = []  # 问句列表中每个句子的否定状态
        self.__a = [] #属性三元组表
        self.__ampos = {} #以首字母位置为关键字的属性字典
        self.__amdict = {} #以属性类型为关键字的属性字典


    def encode_question(self, question):
        self.__docy = question
        self.__docy = self.__nlp(self.__docy)  # 原词的问句
        #self.__replace_num = {}
        #self.__replace_dict = {}
        #for key in self.__dict_keys:
        #    self.__replace_num[key] = 0

        self.__doc = ""
        for token in self.__docy:
            if not (self.__doc == ""):
                self.__doc = self.__doc + " "
            
            if token.ent_type_ in self.__dict_keys:
                #self.__replace_num[token.ent_type_] += 1
                #retext = token.ent_type_ + str(self.__replace_num[token.ent_type_])
                #self.__doc = self.__doc + retext
                self.__doc = self.__doc + token.ent_type_
                #self.__replace_dict[retext] = token.text
            else:
                self.__doc = self.__doc + token.text
        self.__doc = self.__nlp(self.__doc)  # 替换电影实体标签的问句
        amdict = self.__ieam(question)[0]
        # input(amdict)
        ampos = {}
        for amtype in amdict.keys():
            for i in amdict[amtype]:
                if amtype=='average rating' and (i['text'][0]<'0' or i['text'][0]>'9'):
                    continue
                ampos[i['start']] = {'type':amtype, 'text':i['text'], 'len':i['end']-i['start']}
        self.__ampos = ampos
        self.__amdict = amdict

    def find(self, node):
        """
        找到连词点
        """
        for child in node.children:
            deep = self.find(child)
            if not (deep == None):
                return deep
        for child in node.children:
            if child.dep_ == "cc":
                return node
        return None

    def downtag(self, now):
        """
            深度搜索需copy的子节点
        """
        # print(now.i)
        tag = set()
        for child in now.children:
            tag = tag.union(self.downtag(child))
        # print(tag)
        tag.add(now.i)
        # print(tag)
        return tag

    
    
    def split(self, sen, seny, node):
        #print('       split*****************************')
        """
            拆掉node点的逻辑连词
            返回拆分后的两个句子和中间的逻辑词
        """
        #print()
        #print(sen,len(sen))
        #print(seny,len(seny))

        

        for child in node.children:
            if child.dep_ == "cc":
                cc = child
            if child.dep_ == "conj":
                cnode = child

        deltag = set([node.i, cc.i])
        cdeltag = set([cnode.i, cc.i])
        # print(deltag,cdeltag)
        for child in node.children:
            if (child.text == "not") or (child.dep_ == "amod"):
                deltag.add(child.i)
            elif not (child == cc or child == cnode):
                for cchild in cnode.children:
                    if child.dep_ == cchild.dep_:
                        # print(child.i,cchild.i)
                        # t = self.downtag(child)
                        # print(t)
                        deltag = deltag.union(self.downtag(child))
                        cdeltag = cdeltag.union(self.downtag(cchild))
        for cchild in cnode.children:
            if (cchild.text == "not") or (cchild.dep_ == "amod"):
                cdeltag.add(cchild.i)
        # print(deltag,cdeltag)
        i = 0
        while i in cdeltag:
            i = i + 1
        doct = sen[i].text
        docty = seny[i].text
        for j in range(i + 1, len(sen)):
            if not (j in cdeltag):
                doct = doct + ' ' + sen[j].text
                docty = docty + ' ' + seny[j].text
        doct = self.__nlp(doct)
        docty = self.__nlp(docty)
        sq = [list(doct.sents)[0]]
        sqy = [docty]
        #print(sq,len(sq[0]))
        #print(sqy,len(sqy[0]))
        # print("sen1: ",sq)

        i = 0
        while i in deltag:
            i = i + 1
        doct = sen[i].text
        docty = seny[i].text
        for j in range(i + 1, len(sen)):
            if not (j in deltag):
                doct = doct + ' ' + sen[j].text
                docty = docty + ' ' + seny[j].text
        doct = self.__nlp(doct)
        docty = self.__nlp(docty)
        sq.append(list(doct.sents)[0])
        sqy.append(docty)
        # print("sen2: ",sq)
        #print('       *****************************')

        return sq, sqy, [cc.text]

    def splitcc(self):
        #print('splitcc---------------------------------------')
        """
            拆分问句，返回问句列表和逻辑词列表（逻辑词合并顺序对应二叉树形状）
        """
        logic = []
        sent = [list(self.__doc.sents)[0]]
        #print(sent)
        senty = [self.__docy]
        #senty = [list(self.__docy.sents)[0]]
        #print(senty)
        # sent = self.__doc
        # print(sent)
        # senty = self.__docy
        # print(senty)
        # print(sent.root)
        # input(senty.root)

        num = 0
        for token in self.__doc:
            if token.dep_ == "cc":
                num = num + 1
        # print(num)

        for i in range(num):
            temp = []
            tempy = []
            for sen,seny in zip(sent,senty):
                #print()
                #print(sen,len(sen))
                #print(seny,len(seny))
                root = sen.root
                sq, sqy, cc = self.split(sen, seny, self.find(root))
                temp.extend(sq)
                tempy.extend(sqy)
                logic.extend(cc)
            sent = temp
            senty = tempy

        self.__qs = sent
        self.__qsy = senty
        self.__qnum = len(sent)
        self.__logic = logic

        #print('---------------------------------------')
        return sent, senty, logic

    def negjudge(self):
        """
            拆掉句子中的所有not
            返回陈述句列表和每个句子最终的否定情况（not或者none）
        """
        neg = []
        for index, q in enumerate(self.__qs):
            num = 0
            for token in q:
                if token.text == "not":
                    num = num + 1
            if num % 2 == 0:
                neg.append(None)
            else:
                neg.append("not")
            if num > 0:
                qy = self.__qsy[index]
                i = 0
                while q[i].text == "not":
                    i = i + 1
                doct = q[i].text
                docty = qy[i].text
                for j in range(i + 1, len(q)):
                    if not (q[j].text == "not"):
                        doct = doct + ' ' + q[j].text
                        docty = docty + ' ' + qy[j].text
                doct = self.__nlp(doct)
                docty = self.__nlp(docty)
                self.__qs[index] = list(doct.sents)[0]
                self.__qsy[index] = docty

        self.__neg = neg
        return self.__qs, self.__qsy, neg
    
    def cut(self,qu,plist):
        pfa = plist.copy()
        pch = plist.copy()
        chpath = []
        for _ in range(len(pch)):
            chpath.append(set())
        flag = -1
        father = True
        repath = set()
        while (flag == -1) and (len(pfa)>0 or len(pch)>0):
            num = len(pfa)
            for _ in range(num):
                idx = pfa.pop(0)
                for token in qu[idx].children:
                    pfa.append(token.i)
                    if token.ent_type_ in ["movie","person","companies","event"]:
                        flag = token.i
                        break
                if flag>-1: break
            if flag>-1: break
            num = len(pch)
            for _ in range(num):
                idx = pch.pop(0)
                path = chpath.pop(0)
                token=qu[idx].head
                if idx == token.i: continue
                pch.append(token.i)
                path.add(idx)
                chpath.append(path)
                if token.ent_type_ in ["movie","person","companies","event"]:
                    flag = token.i
                    father = False
                    repath = path
                    break
        if flag == -1:
            newdoc = ""
            for token in qu:
                if token.ent_type_ != 'prop':
                    if newdoc == "":
                        newdoc = token.text
                    else:
                        newdoc = newdoc + ' ' + token.text 
            return newdoc,[]
        enti = flag
        if father:
            propset = set()
            flag = qu[flag].head.i
            while qu[flag].ent_type_ != 'prop':
                propset.add(flag)
                flag = qu[flag].head.i
            propset.add(flag)
        else:
            propset = repath
        newdoc = ""
        newpro = [qu[enti].text]
        for token in qu:
            if token.i in propset:
                if token.ent_type_ == 'prop':
                    newpro.append(token.text)
            else:
                if newdoc == "":
                    newdoc = token.text
                else:
                    newdoc = newdoc + ' ' + token.text            
        return newdoc,newpro

    def findprop_old(self,qu):
        result = []
        plist = []
        for token in qu:
            if token.ent_type_ == 'prop':
                plist.append(token.i)
        while len(plist)>0:
            qu,pro = self.cut(qu,plist)
            # print(qu)
            qu = self.__nlp(qu)
            plist = []
            for token in qu:
                if token.ent_type_ == 'prop':
                    plist.append(token.i)
            if len(pro)>0 : result.append(pro)

        return result
    
    def proptoent(self,qu,now,amod):
        falist = [now]
        ch = now
        flag = -1
        while (flag == -1) and (len(falist)>0 or ch != qu[ch].head.i):
            num = len(falist)
            for _ in range(num):
                idx = falist.pop(0)
                for token in qu[idx].children:
                    falist.append(token.i)
                    if token.ent_type_ in ["movie","person","companies","event"]:
                        flag = token.i
                        break
                if flag>-1: break
            if flag>-1: break
            token = qu[ch].head
            ch = token.i
            if token.ent_type_ in ["movie","person","companies","event"]:
                flag = token.i
                break
        if flag>-1:
            return [qu[flag].text,amod['type'],amod['text']]
        else:
            if ch == qu[ch].head.i:
                return ['ROOT',amod['type'],amod['text']]
            else:
                return []

    
    def findprop(self,qu):
        r = list(qu.sents)[0].root.i
        if qu[r].ent_type_ in ["movie","person","companies","event"]:
            firstent = qu[r].text
        else:
            rlist = [r]
            flag = -1
            while (flag == -1) and (len(rlist)>0):
                num = len(rlist)
                for _ in range(num):
                    idx = rlist.pop(0)
                    for token in qu[idx].children:
                        rlist.append(token.i)
                        if token.ent_type_ in ["movie","person","companies","event"]:
                            flag = token.i
                            break
                    if flag>-1: break
                if flag>-1: break
            if flag>-1:
                firstent = qu[flag].text
            else:
                return []
        result = []
        for token in qu:
            if token.idx in self.__ampos.keys():
                pro = self.proptoent(qu,token.i,self.__ampos[token.idx])
                if len(pro)>0:
                    if pro[0]=='ROOT':
                        pro[0] = firstent
                    result.append(pro)
        # print(result)
        # print()
        return result

    def splitamod(self):
        self.__a = []
        for q in self.__qsy:
            temp = self.findprop(q)
            fwhat = [-1]
            flag = {}
            num = len(q)
            for token in q:
                flag[token.i] = False
                if token.text in ['what','What','which','Which']:
                    fwhat[0] = token.i
                    flag[token.i] = True
                    num = num - 1
            if fwhat[0] == -1:
                temp.append(['No what','No what','No what'])
            else:
                new = {}
                while num > 0 and len(fwhat) > 0:
                    n = len(fwhat)
                    for _ in range(n):
                        idx = fwhat.pop(0)
                        # print('------------------------------------------')
                        # print(idx)
                        for child in q[idx].children:
                            if not(flag[child.i]):
                                fwhat.append(child.i)
                                flag[child.i] = True
                                num = num - 1
                                if child.ent_type_ in ["movie","person","companies","event"]:
                                    new['ent'] = child.text
                                    if not('att' in new.keys()):
                                        new['att'] = 'name'
                                    break
                                elif child.ent_type_ == 'prop':
                                    if not('att' in new.keys()):
                                        new['att'] = child.text
                        if 'ent' in new.keys(): break
                        child = q[idx].head
                        if not(flag[child.i]):
                            fwhat.append(child.i)
                            flag[child.i] = True
                            num = num - 1
                            if child.ent_type_ in ["movie","person","companies","event"]:
                                new['ent'] = child.text
                                if not('att' in new.keys()):
                                    new['att'] = 'name'
                                break
                            elif child.ent_type_ == 'prop':
                                if not('att' in new.keys()):
                                    new['att'] = child.text
                    if 'ent' in new.keys(): break
                if 'ent' in new.keys():
                    # print(new)
                    # print(temp)
                    # for iii,_ in enumerate(temp):
                    #     if (new['ent'] == _[0]) and (new['att'] == _[1]):
                    #         temp.pop(iii)
                    #         break
                    temp.append([new['ent'],new['att'],'?'])
                else:
                    temp.append(['No link','No link','No link'])

            self.__a.append(temp)
        return self.__a

    def triplet(self, q):
        """
        可接入获取三元组的接口
        这里直接返回句子文本了
        """
        return "(" + q + ")"

    def Qpro(self, ques):
        """
            处理每一个拆分后的句子
            返回处理结果
        """
        ans = ""
        for q in ques:
            if ans == "":
                ans = self.triplet(q.text)
            else:
                ans = ans + "/" + self.triplet(q.text)
        return ans

    def search(self, now):
        """
            按逻辑列表合并句子列表
            返回拆分问句的逻辑结构
        """
        ans = ""
        if now < self.__qnum:
            ans = "(" + self.search(now * 2) + ")" + self.__logic[now - 1] + "(" + self.search(now * 2 + 1) + ")"
        else:
            if self.__neg[now - self.__qnum] == None:
                # ans = self.qpro(self.__qs[now-self.__qnum])
                ans = self.Qpro(self.__qsy[now - self.__qnum])
            else:
                # ans = "not(" + self.qpro(self.__qs[now-self.__qnum]) + ")"
                ans = "not(" + self.Qpro(self.__qsy[now - self.__qnum]) + ")"

        return ans
    
    def spflag(self):

        special_type = {'REQU'}
        flag = False

        for token in self.__docy:
            if token.ent_type_ in special_type:
                flag = True
                break       

        return flag

    '''def reback(self):
        self.__rqs = []
        #print(self.__replace_dict)
        for i,q in enumerate(self.__qs):
            #print(q)
            rq = []
            for j,text in enumerate(q):
                doc = ""
                #print(text)
                for k,token in enumerate(text):
                    if not(doc == ""):
                        doc = doc + ' '
                    if token.text in self.__replace_dict.keys():
                        #print('reback')
                        doc = doc + self.__replace_dict[token.text]
                    else:
                        doc = doc + token.text
                rq.append(self.__nlp(doc))
            self.__rqs.append(rq)
        return self.__rqs'''

    def solve(self):
        if self.spflag():
            self.__qs = list(self.__doc.sents)[0]
            self.__qsy = [self.__docy]
            self.__a = [[['REQU','REQU','REQU']]]
            # for token in self._qsy[-1]:
            #     print(token.text)
            self.__qnum = 1
        else:
            #self.print_dict()
            #print(list(self.__doc.sents))
            #print(list(self.__docy.sents))
            q, qy, l = self.splitcc()  # 拆分and/or
            self.negjudge()  # 判断每个句子肯定/否定
            self.splitamod()  # 拆分形容词短语
        #self.reback()

    def print_dict(self):
        print(self.__docy)
        print()
        for token in self.__doc:
            print(token.text, token._.is_entity, token.ent_type_, token.dep_)
        print()
        for token in self.__docy:
            print(token.text, token._.is_entity, token.ent_type_, token.dep_)
        print()
        print(self.__logic)
        print(self.__qs)
        print(self.__qsy)
        #print(self.__rqs)
        print(self.__neg)
        print(self.__a)
        print()

    def forward_split(self, question):
        '''
            前向主调函数
            输入：问题字符串
            返回：
                logic {"and"/"or"}: 逻辑连接词表示子句之间的逻辑关系
                question_set: 个拆分子问题, size[n]
                neg_label {"not"/None}: 否定标志表示子句是否否定not表示否定，None表示没有否定，size[n]

            解析形式为树形结构
                       logic[0]
                       /       \
                logic[1]       logic[2]
                /     \          /     \
           q_set[0] q_set[1] q_set[2] q_set[3]
           neg_f[0] neg_f[1] neg_f[2] neg_f[3]
        '''

        self.encode_question(question)
        #self.print_dict()
        self.solve()
        return {
            "logic": self.__logic,
            "question_set": self.__qsy,
            "neg_label": self.__neg,
            "proplist":self.__a
        }

if __name__=="__main__":
    #question = "What movies are directed by Stephen Chow and acted by Leonardo DiCaprio and Kate Winslet?"
    # question = "What companies are acted by Leonardo DiCaprio and Kate Winslet?"
    # question = "What colored movie is directed or acted by Barack Obama and qi?"
    #question = "who direct or act gone with the wind and colored Poison?"
    # question = "What movie is directed by han and not acted by Barack Obama?"
    question = "What color is the movie starred and directed by P1?"
    # question = "What colored movie is directed by Barack Obama?"
    #question = "What movies is acted by Leonardo DiCaprio and Kate Winslet?"
    #question = "What is not the relationship between colored Titanic and Leonardo DiCaprio?"
    #question = "What movie is distributed by Tamjeed Elahi Khan Cinema or TC Entertainment (2018) (Japan) (Blu-ray)?"

    print("===============Model initialize=================")
    print("Prepare entity dictionary")
    nlp = spacy.load('en_core_web_sm')
    nlp.remove_pipe('ner')
    entity_keys = entity_dict.keys()  # 可以提问的实体空间
    for key, values in entity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        nlp.add_pipe(entity, name=key)   # 添加确定识别的NER列表

    test = QuerySplit(nlp, entity_keys)
    test.forward_split(question)
    test.print_dict()
