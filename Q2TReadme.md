# Question Analysis 3月18日更新

解决属性重复提取冲突&提取拆分debug

## 更新的文件

Q2TReadme.md : 本文档

infer_ana.py : 构建属性表时先录入output，判别重复时跳过属性录入

QAQ.py、Qsplit.py : debug

replace_dict.json、companies_pre.txt : 词表语料问题更新

question1.txt : 上半部分是之前测试有问题的样例

## 接口

接口保持原状

## 结果示例

解决了属性在属性表和问题输出中重复提取的冲突，修复了一些实体属性提取、问句拆分中的bug
```
输入 : 泰坦尼克号是什么颜色的？
输出 ：
{
        'lang': 'zh',
        'logic': [], 
        'question_set': [What color is M1?], 
        'neg_label': [None], 
        'propdict': {
                'M1': {
                        'type': 'movie', 
                        'prop': [['Chinese_title', '泰坦尼克号']]
                }
        }, 
        'output': {
                'id': 'M1', 
                'type': 'movie', 
                'prop': ['Color', '?']
        }
}

输入 : Who is the actor of The Phantom of the Opera at the Royal Albert Hall?
输出 ：
{
        'lang': 'en',
        'logic': [], 
        'question_set': [what person is the actor of M1 at C1 ?], 
        'neg_label': [None], 
        'propdict': {
                'M1': {
                        'type': 'movie', 
                        'prop': [['primaryTitle', 'The Phantom of the Opera']]
                }, 
                'C1': {
                        'type': 'company', 
                        'prop': [['name', 'the Royal Albert Hall']]
                }
        }, 
        'output': {
                'id': 'person', 
                'type': 'person', 
                'prop': ['primaryName', '?']
        }
}

输入 : 吉姆·瑞吉尔和彼得·杰克逊共同导演了什么电影？
输出 ：
{
        'lang': 'zh',
        'logic': ['and'], 
        'question_set': [What movie did P1 direct ?, What movie did P2 direct ?], 
        'neg_label': [None, None], 
        'propdict': {
                'P1': {
                        'type': 'person', 
                        'prop': [['primaryName', '吉姆·瑞吉尔']]
                }, 
                'P2': {
                        'type': 'person', 
                        'prop': [['primaryName', '彼得·杰克逊']]
                }
        }, 
        'output': {
                'id': 'movie', 
                'type': 'movie', 
                'prop': ['Chinese_title', '?']
        }
}
```

## 未解决问题

```
deathday存在时提取情况可能有点混乱
```

# Question Analysis 2月1日更新

实体预处理改为词典检索提取

## 更新的文件

Q2TReadme.md : 本文档

infer_ana.py : 添加spacy实体词典准备，删除paddle实体准备

infor_ana.py : 添加spacy实体词典准备，删除paddle实体准备

QAQ.py : 初始化接收spacy，getentity改成词典检索式提取

movie_Zn2En.pkl : 电影实体中英词典

person_pre.txt : 人名实体英文词典

Chinese2English.pkl ：人名实体中文词典

companies_pre.txt : 公司实体英文词典

companiesz_pre.txt : 公司实体中文词典

## 接口

接口保持原状，模型预载和实例化有改动（参见infer_ana.py）

## 结果示例

实体预提取精度提升，解决了人名、电影不全和公司名不带括号的问题。
```
输入 : what movies are distributed by GGG (2018) (Germany) (DVD)？
输出 ：
{
        'lang': 'en',
        'logic': [], 
        'question_set': [what movies are distributed by C1 ？], 
        'neg_label': [None], 
        'propdict': {
                'C1': {
                        'type': 'company', 
                        'prop': [['name', 'GGG (2018) (Germany) (DVD)']]
                }
        }, 
        'output': {
                'id': 'movies', 
                'type': 'movie', 
                'prop': ['primaryTitle', '?']
        }
}
```

## 未解决问题

```
color在提问时也会提取一遍作为属性值的color本词

runtimeMinutes容易提取多种内容（P1、deathday等）

release date会提取类似“the deathday of P1”

birthday会提取birthday本词
```
 ——都不好完全补丁，建议搜一遍作为参考，搜不到条件的放弃

```
casts会提取cast本词，且人名表会变成代号人名表提取有误差
Nicknames不准，有时提取不到有时会提取P1之类的 
```
——不常用已删除该项


# Question Analysis 12月22日更新

新版问句解析方案

## 更新的文件
Q2TReadme.md : 本文档

question1.txt : 本次测试问题列表

infer_ana.py : 问句解析主调程序

QAQ.py : 问句预处理

Qsplit.py : 问句拆解 

infor_ana.py : 预定义信息

movie.txt : 电影实体

person.txt : 人名实体

companies.txt : 公司实体

re_att_dict.json : 属性名映射

replace_dict.json : 翻译映射

## 安装环境

安装spacy工具、paddle工具paddlepaddle、paddlenlp

参考
```
https://spacy.io/usage
https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/conda/linux-conda.html
https://github.com/PaddlePaddle/PaddleNLP/blob/develop/docs/get_started/installation.rst
```

## 接口

调用程序：
```
# Import需要
import spacy
from spacy_lookup import Entity
from paddlenlp import Taskflow
from QAQ import QueryPretreat
from Qsplit import QuerySplit
from infor_ana import line_break, entity_dict
from infor_ana import schemaen,schemazh,transiezh,schemaam

from infer_ana import Qana_forward # 主调函数

# 先加载模型、实例化两个对象
    print("Prepare paddle")
    iezh = Taskflow('information_extraction', schema=schemazh)
    ieen = Taskflow('information_extraction', schema=schemaen, model='uie-base-en')
    ieam = Taskflow('information_extraction', schema=schemaam, model='uie-base-en')

    print("Prepare entity dictionary")
    nlp = spacy.load('en_core_web_sm')
    nlp.remove_pipe('ner')
    entity_keys = entity_dict.keys()  # 可以提问的实体空间
    for key, values in entity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        nlp.add_pipe(entity, name=key)  # 添加确定识别的NER列表

    print("Import question pretreatment")
    q_pre = QueryPretreat(iezh,ieen,transiezh)
    print("Import question spliter")
    q_split = QuerySplit(ieam, nlp, entity_keys)

# 向主调函数中输入问题question

    print("===============Input quesiton=================")
    results = Qana_forward(question,q_pre,q_split)

```

输入：
```
question(问题),q_pre,q_split(两个实例)
```

输出：
```
result字典{
        "lang"：语种，
        "logic"：拆分子句的逻辑结构，
        "question_set": 拆分的句子列表，
        "neg_label"：每个子句的肯定/否定标记，
        "propdict": 属性列表字典{
                句中实体：实体信息字典{
                        "type":实体类型
                        "prop":实体属性列表
                },
                ......
        },
        "output": 问题指示字典{
                'id':提问的实体,
                'type':实体类型,
                'prop':提问的实体属性
        }

*注意，"output"问题提示，在特殊情形时仅有关键字'id'，可能的特殊值为：
        'REQU' : 询问关系
        'No link' : 找不到与what连接的实体
        'No what' : 找不到what
        'NULL' : 提取失败
```

## 结果示例
```
输入 : 什么电影由陈凯歌导演或出演？
输出 ：
{
        'lang': 'zh',
        'logic': ['or'], 
        'question_set': [What movie is directed by P1 ?, What movie is acted by P1 ?], 
        'neg_label': [None, None], 
        'propdict': {
                'P1': {
                        'type': 'person', 
                        'prop': [['primaryName', '陈凯歌']]
                }
        }, 
        'output': {
                'id': 'movie', 
                'type': 'movie', 
                'prop': ['Chinese_title', '?']
        }
}
```
```
输入 : What colored movie are acted by James Cameron and Leonardo DiCaprio?
输出 ：
{
        'lang': 'en', 
        'logic': ['and'], 
        'question_set': [What colored movie are acted by P2 ?, What colored movie are acted by P1 ?], 
        'neg_label': [None, None], 
        'propdict': {
                'P1': {
                        'type': 'person', 
                        'prop': [['primaryName', 'Leonardo DiCaprio']]
                }, 
                'P2': {
                        'type': 'person', 
                        'prop': [['primaryName', 'James Cameron']]
                }, 
                'movie': {
                        'type': 'movie', 
                        'prop': [['Color', 'colored']]
                }
        }, 
        'output': {
                'id': 'movie', 
                'type': 'movie', 
                'prop': ['primaryTitle', '?']
        }
}
```



## 一些未解决问题

```
人名三个以上会有提取遗漏(电影也有少数遗漏情况)

有时电影名只能识别一半
（例如“The Phantom of the Opera at the Royal Albert Hall”只识别“The Phantom of the Opera”）

公司名无法连带我们词表重后面的括号识别
（例如“Twentieth Century Fox (2018) (USA) (TV)”只识别“Twentieth Century Fox”）
```
——暂时解决不了

```
color在提问时也会提取一遍作为属性值的color本词

runtimeMinutes容易提取多种内容（P1、deathday等）

release date会提取类似“the deathday of P1”

birthday会提取birthday本词
```
 ——都不好完全补丁，建议搜一遍作为参考，搜不到条件的放弃

```
casts会提取cast本词，且人名表会变成代号人名表提取有误差
Nicknames不准，有时提取不到有时会提取P1之类的 
```
——不常用已删除该项

