# -*- coding:utf-8 -*-
"""
    实体、实体关系定义，问题，数据库
"""
import json
import platform
import pickle

# 定制换行符
sys_str = platform.system()
if sys_str == "Windows":
    line_break = "\n"
elif sys_str == "Linux":
    line_break = "\r\n"
else:
    print("Other System tasks")

# 改写句子头部信息
add_who = set(['actor', 'director', 'photographer', 'writer', 'editor', 'composer', 'designer', 'producer'
                ,'Actor', 'Director', 'Photographer', 'Writer', 'Editor', 'Composer', 'Designer', 'Producer'])
add_what = set(['movie', 'award', 'compan','Movie', 'Award', 'Compan'])

# 实体和属性的类别设定
# schemazh = ['电影', '人名', '公司']
# transiezh = {
#         '电影':'movie',
#         '人名':'person',
#         '公司':'company'
#     }
# schemaen = ['movie', 'person', 'company']
schemaam = ['average rating','runtimeMinutes','release date','Color',
            'Height','birthday','deathday']
            # 'casts','profession','Nicknames'

#属性名映射词表
re_att_dict = json.load(open("attributes/re_att_dict.json", encoding='utf-8'))

#翻译替换词表
replace_dict = json.load(open("attributes/replace_dict.json", encoding='utf-8'))

# 实体预处理表
person1_list = []
for person in open("entities/person_pre.txt", encoding='utf-8').readlines():
    person = person.strip(line_break)
    person1_list.append(person)
# pz_dict = pickle.load(open("Chinese2English.pkl",'rb'))
# person1_list = list(pz_dict.values())
company1_list = []
for company in open("entities/companies_pre.txt", encoding='utf-8').readlines():
    company = company.strip(line_break)
    company1_list.append(company)

eentity_dict = {"person": person1_list,
                "company": company1_list
               }

# person2_list = []
# for person in open("personz_pre.txt", encoding='utf-8').readlines():
#     person = person.strip(line_break)
#     person2_list.append(person)
pz_dict = pickle.load(open("entities/Chinese2English.pkl",'rb'))
person2_list = list(pz_dict.keys())

company2_list = []
for company in open("entities/companiesz_pre.txt", encoding='utf-8').readlines():
    company = company.strip(line_break)
    company2_list.append(company)

zentity_dict = {"person": person2_list,
                "company": company2_list
               }


# 电影实体预处理表
m_dict = pickle.load(open("entities/movie_Zn2En.pkl",'rb'))
movie1_list = list(m_dict.values())
movie1_list.append('Die Leiden des jungen Werthers')
movie1_list.append('Caught in the Draft')
ementity_dict = {"movie": movie1_list}
movie2_list = list(m_dict.keys())
movie2_list.append('活着')
zmentity_dict = {"movie": movie2_list}


# 实体列表读取
movie_list = []
for movie in open("entities/movie.txt").readlines():
    movie = movie.strip(line_break)
    movie_list.append(movie)
person_list = []
for person in open("entities/person.txt", encoding='utf-8').readlines():
    person = person.strip(line_break)
    person_list.append(person)
company_list = []
for company in open("entities/companies.txt", encoding='utf-8').readlines():
    company = company.strip(line_break)
    company_list.append(company)

entity_dict = {"movie": movie_list,
               "person": person_list,
               "REQU": ['relation', 'relationship'],
            #    "companies": ['what company', 'what companies'],
               "companies": company_list,
               "prop": ["name","rate","rating","Douban rating","average rating","average rate","IMDB rate","IMDB rating","cast","trivia",
                                "time","runtime","running time","length","release date","color","profession","height",
                                "birthday","deathday","nickname","wife","husband","trade mark","portrayal","interview","article"],
               "event": ["award", "awards", "reward", "rewards", "event"]
            #    "QUESTION": ['which', 'who', 'what'],
               }

special_type = ["REQU"]
