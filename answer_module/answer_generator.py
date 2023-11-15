# -*- coding:utf-8 -*-
"""
    答案生成，可视化cypher语句生成模块
"""
import re
import json
import requests
import platform
from post_cypher import QueryCypher

sys_str = platform.system()
if sys_str == "Windows":
    line_break = "\n"
elif sys_str == "Linux":
    line_break = "\r\n"
else:
    print("Other System tasks")


class Triplet2Answer:
    def __init__(self):
        try:
            # 使用本地ip
            requests.get("http://" + "192.168.1.4" + ":8201", timeout=3.)
            print("local connection")
            self.url = "http://" + "localhost" + ':20000/base_services/neo4j?query='
        except:
            # 使用远程ip
            print("remote connetion")
            self.url = "http://910.mivc.top:20000/base_services/neo4j?query="
        self.login = "neo4j:123456"
        self.entity_query_dict = json.load(open("attributes/entity_query_dict.json", encoding='utf-8'))
        self.property_entity_name = json.load(open("attributes/property_entity_name_dict.json", encoding='utf-8'))
        self.chain_entity_dict = json.load(open("attributes/chain_entity_dict.json", encoding='utf-8'))

    @staticmethod
    def __conj_based_appender__(match_line_list, where_line_list, return_line_list, logic):
        where_line_appender = []
        if logic == "and":
            match_line_list[0].extend(match_line_list[1])
            return_line_list[0].extend(return_line_list[1])
            where_line_appender = where_line_list[1]
        elif logic == "or":
            where_line_appender = []
            for dict_cnt in range(len(where_line_list[0])):
                k = next(iter(where_line_list[0][dict_cnt].keys()))
                v = next(iter(where_line_list[1][dict_cnt].values()))
                where_line_appender.append({k: v})
            for i in range(len(match_line_list[0])):
                k = next(iter(match_line_list[0][i].keys()))
                if match_line_list[0][i][k] == "":
                    match_line_list[0][i][k] = match_line_list[1][i][k]
                    return_line_list[0][i][k] = return_line_list[1][i][k]

        k = next(iter(where_line_list[0][0].keys()))
        v = next(iter(where_line_list[0][0].values()))
        where_line_list[0][0][k] = "(" + v
        k = next(iter(where_line_list[0][-1].keys()))
        v = next(iter(where_line_list[0][-1].values()))
        where_line_list[0][-1][k] = v + ") " + logic

        k = next(iter(where_line_appender[0].keys()))
        v = next(iter(where_line_appender[0].values()))
        where_line_appender[0][k] = " (" + v
        k = next(iter(where_line_appender[-1].keys()))
        v = next(iter(where_line_appender[-1].values()))
        where_line_appender[-1][k] = v + ")"

        where_line_list[0].extend(where_line_appender)
        return match_line_list[0], where_line_list[0], return_line_list[0]

    @staticmethod
    def __relation_where_plus_conj__(where_line_list, logic):
        """
        逻辑连词组装
        :param where_line_list: 待组装的where
        :param logic: 逻辑连词
        :return: 组装好的where语句
        """
        where_queue = []
        logic_i = len(logic)
        if logic_i > 0:
            for i in range(len(logic), 0, -2):
                logic_i = logic_i - 1
                where_line = ""
                if where_line_list[i] == "" and where_line_list[i - 1] != "":
                    where_line = "(" + where_line_list[i - 1] + ")"
                elif where_line_list[i] != "" and where_line_list[i - 1] == "":
                    where_line = "(" + where_line_list[i] + ")"
                elif where_line_list[i] != "" and where_line_list[i - 1] != "":
                    where_line = "((" + where_line_list[i] + ") " + logic[logic_i] + " (" + where_line_list[
                        i - 1] + "))"
                where_queue.append(where_line)
            if logic_i > 0:
                queue_i = 0
                for i in range(logic_i - 1, 0, -1):
                    where_line = "(" + where_queue[queue_i] + " " + logic[i] + " " + where_queue[queue_i + 1] + ")"
                    where_queue.append(where_line)
                    queue_i = queue_i + 2
                where_line = "(" + where_queue[-2] + " " + logic[0] + " " + where_queue[-1] + ")"
            else:
                where_line = where_queue[0]
        else:
            where_line = ""
            for phrase in where_line_list:
                if phrase != "":
                    where_line = where_line + "AND (" + phrase + ")"
            where_line = where_line[4:]
        return where_line

    def __match_where_plus_conj__(self, match_line_list, where_line_list, return_line_list, logic):
        """
        逻辑连词组装
        :param match_line_list: 待组装的match
        :param where_line_list: 待组装的where
        :param return_line_list: 待组装的return
        :param logic: 逻辑连词
        :return: 组装好的where语句
        """
        match_queue = []
        where_queue = []
        return_queue = []
        match_line = ""
        where_line = ""
        return_line = ""
        logic_i = len(logic)
        if logic_i > 0:
            for i in range(len(logic), 0, -2):
                logic_i = logic_i - 1
                match_phrase, where_phrase, return_phrase = self.__conj_based_appender__([match_line_list[i - 1],
                                                                                          match_line_list[i]],
                                                                                         [where_line_list[i - 1],
                                                                                          where_line_list[i]],
                                                                                         [return_line_list[i - 1],
                                                                                          return_line_list[i]],
                                                                                         logic[logic_i])
                match_queue.append(match_phrase)
                where_queue.append(where_phrase)
                return_queue.append(return_phrase)
            if logic_i > 0:
                queue_i = 0
                for i in range(logic_i - 1, 0, -1):
                    match_phrase, where_phrase, return_phrase = self.__conj_based_appender__([match_queue[queue_i],
                                                                                              match_queue[queue_i + 1]],
                                                                                             [where_queue[queue_i],
                                                                                              where_queue[queue_i + 1]],
                                                                                             [return_queue[queue_i],
                                                                                              return_queue[
                                                                                                  queue_i + 1]],
                                                                                             logic[i])
                    match_queue.append(match_phrase)
                    where_queue.append(where_phrase)
                    return_queue.append(return_phrase)
                    queue_i = queue_i + 2
                match_phrase, where_phrase, return_phrase = self.__conj_based_appender__([match_queue[-2],
                                                                                          match_queue[-1]],
                                                                                         [where_queue[-2],
                                                                                          where_queue[-1]],
                                                                                         [return_queue[-2],
                                                                                          return_queue[-1]],
                                                                                         logic[0])
            else:
                match_phrase = match_queue[0]
                where_phrase = where_queue[0]
                return_phrase = return_queue[0]
            for line in match_phrase:
                a, b, t = next(iter(line.keys())).split(".")
                match_line = match_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
            for line in where_phrase:
                a, b, t = next(iter(line.keys())).split(".")
                where_line = where_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
            for line in return_phrase:
                a, b, t = next(iter(line.keys())).split(".")
                return_line = return_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
        else:
            for i in range(0, len(where_line_list)):
                for line in match_line_list[i]:
                    a, b, t = next(iter(line.keys())).split(".")
                    match_line = match_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
                for line in where_line_list[i]:
                    a, b, t = next(iter(line.keys())).split(".")
                    where_line = where_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
                for line in return_line_list[i]:
                    a, b, t = next(iter(line.keys())).split(".")
                    return_line = return_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
        return match_line, where_line, return_line

    def __query_templates_match__(self, entity_name, property_type, property_value, neg, loc, attr_idx, info):
        """
        属性查询语句模板匹配
        :param entity_name: 实体类型
        :param property_type: 实体属性类型
        :param property_value: 实体属性值
        :param neg：否定词
        :param loc: 头实体or尾实体
        :return:
            match_phrase: 参与match语句组装
            where_phrase: 非查询对象的限定语句，参与where语句的组装
            where_for_return: 查询对象的限定语句，参与where语句的组装
            return_phrase：参与return语句的组装
            long_type_match： (c)-[r1]-(a)-[r]-(b)-[r2]-(d) or (a)-[r]-(b)
            r_prop_flag：匹配为第二种模板时为True
        """
        type_name = ['a', 'b', 'c' + attr_idx + '{cnt1}', 'b{cnt2}', 'a{cnt1}',
                     'd' + attr_idx + '{cnt2}', 'c' + attr_idx, 'd' + attr_idx]
        entity_name_list = [':{label})-[rr', ':' + entity_name + ')-[rrr', ':' + entity_name + ')', ':{label})']
        cnt_name = ["{cnt1}", "{cnt2}"]
        return_special_prop_phrase = ""
        match_special_prop_phrase = ""
        if property_type != "":
            try:
                entity_query_idx = self.entity_query_dict[entity_name + '.' + property_type]
            except:
                print("Mismatch entity and property: " + entity_name + '.' + property_type)
                entity_query_idx = 1
        else:
            entity_query_idx = 1
        if entity_query_idx == 1:
            '''
            where_phrase = {type_name}{cntk}.{property_type}='{property_value}'
            return_phrase = {type_name}{cntk}.{property_type} (for parsing, query stage: id({type_name}{cntk}))
            '''
            if neg is not None:
                if property_value == "":
                    where_phrase = "none(x in nodes(p{cnt0}) WHERE EXISTS(x." + property_type + "))"
                else:
                    where_phrase = "none(x in nodes(p{cnt0}) WHERE x." + property_type + "='" + property_value + "')"
            else:
                if property_value == "":
                    where_phrase = "EXISTS(" + type_name[loc] + cnt_name[loc] + "." + property_type + ")"
                else:
                    where_phrase = type_name[loc] + cnt_name[loc] + "." + property_type + "='" + property_value + "'"
            return_phrase = ",id(" + type_name[loc] + "{idx})"
            return_type = "nodes$" + property_type + "$" + info
            where_for_return = ""
        elif entity_query_idx == 2:
            '''
            where_phrase = r{cntk}.{property_type}='{property_value}'
            return_phrase = r{cntk}.{property_type} (for parsing, query stage: id(r{cntk}))
            '''
            if neg is not None:
                if property_value == "":
                    where_phrase = "none(x in relationships(p{cnt0}) WHERE EXISTS(x." + property_type + "))"
                else:
                    where_phrase = "none(x in relationships(p{cnt0}) WHERE x." + property_type + "='" + property_value + "')"
            else:
                if property_value == "":
                    where_phrase = "EXISTS(r" + cnt_name[loc] + "." + property_type + ")"
                else:
                    where_phrase = "r" + cnt_name[loc] + "." + property_type + "='" + property_value + "'"
            return_phrase = ",id(r{idx})"
            return_type = "relationships$" + property_type + "$" + info
            where_for_return = ""
        else:
            entity_name_list_sub = entity_name_list
            entity_name_list_sub[0] = entity_name_list_sub[0].format(label=self.property_entity_name[property_type])
            entity_name_list_sub[3] = entity_name_list_sub[3].format(label=self.property_entity_name[property_type])
            type_name_sub = type_name[2: 6]
            '''
            match_special_prop_phrase = 
            p{cnt0}_{cntk}=(c{cntk}:{entity_label})-[rr{cnt0}_{cntk}]-(a{cntk}:{entity_name}),
            or 
            p{cnt0}_{cntk}=(b{cntk}:{entity_name})-[rrr{cnt0}_{cntk}]-(d{cntk}:{entity_label}),
            '''
            match_special_prop_phrase = "p{cnt0}_" + cnt_name[loc] + "=(" + type_name_sub[loc] + \
                                        entity_name_list_sub[loc] + "{cnt0}_" + cnt_name[loc] + \
                                        "]-(" + type_name_sub[loc + 2] + entity_name_list_sub[loc + 2] + ","
            return_special_prop_phrase = "p{cnt0}_" + cnt_name[loc] + ","
            if entity_query_idx == 3:
                '''
                where_phrase = {type_name}{cntk}.{property_type}='{property_value}'
                return_phrase = {type_name}{cntk}.{property_type} (for parsing, query stage: id({type_name}{cntk}))
                '''
                if property_type == "release_date":  # TODO，命名缺乏一般规律
                    property_type = "date"
                if neg is not None:
                    if property_value == "":
                        where_phrase = "none(x in nodes(p{cnt0}) WHERE EXISTS(x." + property_type + "))"
                    else:
                        where_phrase = "none(x in nodes(p{cnt0}) WHERE x." + property_type + "='" + property_value + "')"
                else:
                    if property_value == "":
                        where_phrase = "EXISTS(" + type_name[loc + 6] + cnt_name[loc] + "." + property_type + ")"
                    else:
                        where_phrase = type_name[loc + 6] + cnt_name[loc] + "." + property_type + "='" + property_value + "'"
                where_for_return = ""
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$" + property_type + "$" + info
            elif entity_query_idx == 4:
                '''
                where_phrase = {type_name}{cntk}.label='{property_type}' AND {type_name}{cntk}.value='{property_value}'
                where_for_return = {type_name}{cntk}.label='{property_type}'
                return_phrase = {type_name}{cntk}.value (for parsing, query stage: id({type_name}{cntk}))
                '''
                if neg is not None:
                    where_for_return = " AND none(x in nodes(p{cnt0}) WHERE x.label='" + property_type + "')"
                    if property_value == "":
                        where_phrase = where_for_return
                    else:
                        where_phrase = "none(x in nodes(p{cnt0}) WHERE x.label='" + property_type + \
                                       "' AND x.value='" + property_value + "')"
                else:
                    where_for_return = " AND " + type_name[loc + 6] + cnt_name[loc] + ".label='" + property_type + "'"
                    if property_value == "":
                        where_phrase = where_for_return
                    else:
                        where_phrase = type_name[loc + 6] + cnt_name[loc] + ".label='" + property_type + \
                                       "' AND " + type_name[loc + 6] + cnt_name[loc] + ".value='" + property_value + "'"
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$1value" + "$" + info
            elif entity_query_idx == 5:
                '''
                where_phrase = {type_name}{cntk}.cate='{property_type}' AND {type_name}{cntk}.value='{property_value}'
                where_for_return = {type_name}{cntk}.cate='{property_type}'
                return_phrase = {type_name}{cntk}.value (for parsing, query stage: id({type_name}{cntk}))
                '''
                if neg is not None:
                    where_for_return = " AND none(x in nodes(p{cnt0}) WHERE x.cate='" + property_type + "')"
                    if property_value == "":
                        where_phrase = where_for_return
                    else:
                        where_phrase = "none(x in nodes(p{cnt0}) WHERE x.cate='" + property_type + \
                                       "' AND x.value='" + property_value + "')"
                else:
                    where_for_return = " AND " + type_name[loc + 6] + cnt_name[loc] + ".cate='" + property_type + "'"
                    if property_value == "":
                        where_phrase = where_for_return
                    else:
                        where_phrase = type_name[loc + 6] + cnt_name[loc] + ".cate='(" + property_type + \
                                       "' AND " + type_name[loc + 6] + cnt_name[loc] + ".value='" + property_value + "'"
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$1value" + "$" + info
            elif entity_query_idx == 6:
                '''
                where_for_return = {type_name}{cntk}.cate='{property_type}'
                return_phrase = {type_name}{cntk}.label (for parsing, query stage: id({type_name}{cntk}))
                '''
                where_phrase = ""
                if neg is not None:
                    where_for_return = " AND none(x in nodes(p{cnt0}) WHERE x.cate='" + property_type + "')"
                else:
                    where_for_return = " AND " + type_name[loc + 6] + cnt_name[loc] + ".cate='" + property_type + "'"
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$1label" + "$" + info
        where_phrase = " AND " + where_phrase if where_phrase[:5] != " AND "  else where_phrase

        return match_special_prop_phrase, where_phrase, where_for_return, \
               return_phrase, return_type, return_special_prop_phrase

    # TODO：
    def __match_relation__(self, triplet_set, attlist_set, logic, neg):
        """
        查询符合要求的头尾实体关系
        :param triplet_set: 三元组 [ ([entity_a1], [entity_a_property1], [entity_b1], [entity_b_property1], [relation1]),
                                    ([entity_a2], [entity_a_property2], [entity_b2], [entity_b_property2], [relation2]),
                                    ...]
        :param attlist_set: 属性列表 [<逻辑词连接> [<头实体尾实体>[<同实体不同属性>[entity1_name, 1_property_type, 1_property],
                                                 [entity1_name, 1_property_type, 1_property]
        :param logic: 逻辑连接词
        :param neg: 条件否定词
        :return: 查询结果，即头尾实体关系（头指向尾）
        """
        print("----enter relation match section----")
        match_line = "MATCH "
        where_line_list = []
        return_line = "RETURN DISTINCT "
        return_word = ""
        return_cnt = 0
        unwind_word = ""

        match_cmp_list = {0: [], 1: []}
        where_cmp_list = {0: [], 1: []}
        cnt_list = {0: [], 1: []}
        where_list = {0: [], 1: []}

        triplet_key = [0, 2]
        cnt = [0, 0]
        cypher_name = ["a", "b"]
        if len(neg) < len(triplet_set):
            for _ in range(len(neg), len(triplet_set)):
                neg.append(None)
        for i in range(0, len(triplet_set)):
            where_line_i = ""
            for j in range(0, len(triplet_set[0][0])):
                cnt_plus_counter = 0
                t = i * len(triplet_set[0][0]) + j
                match_special_template_j = ""
                for k in range(0, 2):
                    entity_name = triplet_set[i][triplet_key[k]][j]
                    cnt[k] = t
                    for w in range(0, len(attlist_set[t][k])):
                        property_type, entity_property = attlist_set[t][k][w][1:3]
                        cmp_str = entity_name + property_type[k] + entity_property
                        match_special_template, where_phrase_template, \
                        _, _, _, _ = self.__query_templates_match__(entity_name, property_type,
                                                                    entity_property, neg[i], k,
                                                                    str(i) + str(w),
                                                                    attlist_set[t][k][w][0])
                        # 目前没考虑多跳条件的情况，所以special也不会重复，如果考虑更一般，需要改写
                        match_special_template_j = match_special_template_j + match_special_template
                        if entity_property != "":
                            if (cmp_str + triplet_set[i][4][j]) in where_cmp_list[k]:
                                where_line_i = where_line_i + where_list[k][
                                    where_cmp_list[k].index(cmp_str + triplet_set[i][4][j])]
                            else:
                                where_cmp_list[k].append(cmp_str + triplet_set[i][4][j])
                                if cmp_str not in match_cmp_list[k]:
                                    cnt_list[k].append(cnt[k])
                                    match_cmp_list[k].append(cmp_str)
                                else:
                                    cnt[k] = cnt_list[k][match_cmp_list[k].index(cmp_str)]
                                cnt_plus_counter = cnt_plus_counter + 1
                                where_phrase = where_phrase_template
                                # if neg[i] is not None:
                                #     where_phrase = " AND none(x" + str(cnt[k]) + " in nodes(p" + str(t) + \
                                #                    ") WHERE x" + str(cnt[k]) + "." + property_type[k] + \
                                #                    "='" + entity_property + "')"
                                # else:
                                #     where_phrase = " AND " + cypher_name[k] + str(cnt[k]) + "." + property_type[k] + \
                                #                    "='" + entity_property + "'"
                                if entity_name == "movie":
                                    where_phrase += " AND " + cypher_name[k] + str(cnt[k]) + ".douban_movie_id<>'nan'"
                                where_list[k].append(where_phrase)
                                where_line_i = where_line_i + where_phrase
                # relation
                if cnt_plus_counter != 0:
                    if triplet_set[i][4][j] != "REQU":
                        where_line_i += " AND type(r{t})=~'{relation}.*'" if neg[1] is None \
                                        else " AND none(z{t} in relationships(p{t}) WHERE type(z{t})=~'{relation}.*')"
                        where_line_i = where_line_i.format(t=str(t), relation=triplet_set[i][4][j])
                        match_line = match_line + "p{t}=(a{cnt0}:{e_type0})-[r{t}]-(b{cnt1}:{e_type1}),"
                    else:
                        match_line = match_line + "p{t}=(a{cnt0}:{e_type0})-[r{t}*{hop}]-(b{cnt1}:{e_type1}),"
                        where_line_i += " AND all(x{t} in nodes(p{t}) " \
                                        "WHERE none(label{t} in labels(x{t}) " \
                                        "WHERE label{t} in ['user','keywords','videos', 'imgs']))" \
                                        " AND all(x{t} in relationships(p{t}) " \
                                        "WHERE type(x{t})<>'actor2actor' and " \
                                        "type(x{t})<>'other' and type(x{t})<>'bothlike')".format(t=str(t))
                        unwind_word = unwind_word + ",r" + str(t) + " as rr" + str(t)
                        return_word = return_word + ",type(rr" + str(t) + ")"
                        return_cnt = return_cnt + 1
                    match_line = match_line.format(t=str(t), cnt0=str(cnt[0]), cnt1=str(cnt[1]), hop="{hop}",
                                                   e_type0=triplet_set[i][0][j], e_type1=triplet_set[i][2][j])
                    return_line = return_line + "p" + str(t) + ","
                    where_line_list.append(where_line_i[5:])
        if len(where_line_list) > 1:
            where_line = "WHERE " + self.__relation_where_plus_conj__(where_line_list, logic)
        else:
            where_line = "WHERE " + where_line_list[0]
        return_todo_cypher = match_line[:-1] + " " + where_line + " " + \
                             "UNWIND " + unwind_word[1:] + " " + return_line + "{return_w}{limit}"
        ans = []
        for i in range(1, 5):  # TODO: 只考虑一对，多跳条件不支持
            if i == 1:
                cypher = return_todo_cypher.format(hop=i, return_w=return_word[1:], limit="", cnt1=0, cnt2=0)
            elif i == 2:
                cypher = return_todo_cypher.format(hop=i, return_w="null", limit=" LIMIT 5", cnt1=0, cnt2=0)
            else:
                cypher = return_todo_cypher.format(hop=i, return_w="null", limit=" LIMIT 1", cnt1=0, cnt2=0)
            print("----jump = " + str(i))
            print("生成的cypher查询语句：")
            print(cypher)
            print("Querying Remote Database: It may take some time")
            res = QueryCypher(self.url, self.login, cypher)
            ans_list = []
            if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
                if return_cnt > 0:
                    for j in range(-1, -return_cnt - 1, -1):
                        res_type = res["results"][0]["columns"][j]
                        if res_type == "null":
                            ans.append({"text": '多跳关系', "url": None})
                            continue
                        for k in range(0, len(res["results"][0]["data"])):
                            if res["results"][0]["data"][k]["row"][j] not in ans_list:
                                ans.append({"text": res["results"][0]["data"][k]["row"][j], "url": None})
                                ans_list.append(res["results"][0]["data"][k]["row"][j])
                break
        return ans, res

    def __match_node__(self, triplet_set, attlist_set, logic, neg):
        """
        查询符合要求的实体属性值
        :param triplet_set: 三元组 [ ([entity_a1], [entity_a_property1], [entity_b1], [entity_b_property1], [relation1]),
                                    ([entity_a2], [entity_a_property2], [entity_b2], [entity_b_property2], [relation2]),
                                    ...]
        :param attlist_set: 属性列表 [<逻辑词连接> [<头实体尾实体>[<同实体不同属性>[entity1_name, 1_property_type, 1_property],
                                                                             [entity1_name, 1_property_type, 1_property]
        :param logic: 逻辑连接词
        :param neg: 条件否定词
        :return: 返回查询结果，即尾实体属性值
        """
        print("----enter node match section----")
        match_cmp_list = []
        match_cmp_cnt_list = []
        return_where_list = []
        return_words = []
        return_idx_list = []
        return_property_list = []
        return_cnt = 0

        match_line_list = []
        where_line_list = []
        return_line_list = []

        cmp_list = {0: [], 1: []}
        cnt_list = {0: [], 1: []}
        where_list = {0: [], 1: []}

        triplet_key = [0, 2]
        cnt = [0, 0]
        cypher_name = ["a", "b"]
        for i in range(len(triplet_set)):
            where_line_i = []
            match_line_i = []
            return_line_i = []
            len_rel_flag = len(triplet_set[i])
            where_movie_cmp_list = []
            for j in range(len(triplet_set[0][0])):
                match_line_j = ""
                match_special_template_j = ""
                where_line_j = ""
                return_line_j = ""
                return_special_j = ""
                t = i * len(triplet_set[0][0]) + j
                k_len = 1 if len_rel_flag < 3 else 2
                match_cmp_str = ""
                key = ""
                # entity: head (and tail)
                for k in range(0, k_len):
                    cnt[k] = t
                    movie_thres_phrase = " AND " + cypher_name[k] + "{cnt" + str(k + 1) + "}.douban_movie_id<>'nan'"
                    entity_name = triplet_set[i][triplet_key[k]][j]
                    # property
                    for w in range(0, len(attlist_set[t][k])):
                        entity_property = attlist_set[t][k][w][2]
                        property_type = attlist_set[t][k][w][1]
                        match_special_template, where_phrase_template, \
                        where_for_return_template, return_word_template, \
                        return_type, return_special = self.__query_templates_match__(entity_name, property_type,
                                                                                     entity_property, neg[i], k,
                                                                                     str(i) + str(w),
                                                                                     attlist_set[t][k][w][0])
                        cmp_str = entity_name + property_type + entity_property
                        if cmp_str in cmp_list[k]:
                            where_line_j = where_line_j + where_list[k][cmp_list[k].index(cmp_str)]
                            cnt[k] = cnt_list[k][cmp_list[k].index(cmp_str)]
                        else:
                            match_special_template_j = match_special_template_j + match_special_template
                            return_special_j = return_special_j + return_special
                            cmp_list[k].append(cmp_str)
                            cnt_list[k].append(cnt[k])
                            # 不是疑问词或空，设置where语句
                            if re.match("^(what|$)", attlist_set[t][k][w][3], re.I) is None:
                                where_phrase = where_phrase_template
                            # 是疑问词，设置return语句
                            elif re.match("^(what)", attlist_set[t][k][w][3], re.I):
                                return_word = return_word_template.format(idx=str(cnt[k]))
                                if return_word in return_words:
                                    return_idx_list.append(return_idx_list[return_words.index(return_word)])
                                else:
                                    return_words.append(return_word)
                                    return_idx_list.append(return_cnt)
                                return_property_list.append(return_type)
                                return_cnt = return_cnt + 1
                                where_phrase = where_for_return_template
                            else:
                                where_phrase = ""
                            where_list[k].append(where_phrase)
                            where_line_j = where_line_j + where_phrase
                    if movie_thres_phrase + str(cnt[k]) not in where_movie_cmp_list and entity_name == "movie":
                        where_movie_cmp_list.append(movie_thres_phrase + str(cnt[k]))
                        where_line_j = where_line_j + movie_thres_phrase
                    key = key + str(cnt[k]) + "." if k_len == 2 else key + str(cnt[k]) + ".."
                    match_cmp_str = match_cmp_str + cmp_str
                # 拼接
                path_format = ['', triplet_set[i][(k_len - 1) * 4][j], "),",
                               ")-[r{cnt0}]-(b{cnt2}:" + triplet_set[i][k_len][j] + "),"]
                match_cmp_str = match_cmp_str + path_format[k_len - 1]
                if match_cmp_str not in match_cmp_list:
                    return_line_j = "p{cnt0}," + return_special_j
                    match_line_j = "p" + str(t) + "=(a{cnt1}:" + triplet_set[i][0][j] + \
                                   path_format[k_len + 1] + match_special_template_j
                    match_cmp_list.append(match_cmp_str)
                    where_phrase = " AND type(r{cnt0})=~'{relation}.*'" if neg[i] is None \
                        else " AND none(z{cnt0} in relationships(p{cnt0}) WHERE type(z{cnt0})=~'{relation}.*')"
                    match_cmp_cnt_list.append(t)
                    if len_rel_flag < 5:
                        return_line_j = "a{cnt1}," + return_special_j
                        match_line_j = "(a{cnt1}:" + triplet_set[i][0][j] + \
                                    path_format[k_len + 1] + match_special_template_j
                        where_phrase = ""
                    return_where_list.append(where_phrase)
                else:
                    where_phrase = return_where_list[match_cmp_list.index(match_cmp_str)]
                    t = match_cmp_cnt_list[match_cmp_list.index(match_cmp_str)]
                key = key + str(t)
                match_line_i.append({key: match_line_j})
                where_line_i.append({key: where_line_j + where_phrase.format(relation=path_format[k_len - 1], cnt0="{cnt0}")})
                return_line_i.append({key: return_line_j})

            where_line_i[0][next(iter(where_line_i[0].keys()))] = next(iter(where_line_i[0].values()))[5:]
            match_line_list.append(match_line_i)
            where_line_list.append(where_line_i)
            return_line_list.append(return_line_i)

        match_line, \
        where_line, \
        return_line = self.__match_where_plus_conj__(match_line_list, where_line_list, return_line_list, logic)
        if where_line[:5] == " AND ":
            where_line = where_line[5:]
        cypher = "MATCH " + match_line[:-1] + line_break + \
                 "WHERE " + where_line + line_break + \
                 "RETURN DISTINCT " + return_line + ''.join(return_words)[1:]
        cypher += " LIMIT 20"
        print("----生成的cypher查询语句：" + line_break + cypher)
        print("----Querying Remote Database: It may take some time")
        res = QueryCypher(self.url, self.login, cypher)
        ans = self.__node_match_ans_parse__(res, return_cnt, return_idx_list, return_property_list)
        return ans, res

    @staticmethod
    def __node_match_ans_parse__(res, return_cnt, return_idx_list, return_property_list):
        ans = []
        info_dict = {}
        unk_dict = {}
        cnt = 0
        if return_cnt > 0:
            if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
                for i in range(-1, -return_cnt - 1, -1):
                    for j in range(0, len(res["results"][0]["data"])):
                        entity_id = res["results"][0]["data"][j]["row"][return_idx_list[i] - max(return_idx_list) - 1]
                        ans_url = "nan"
                        return_prop = return_property_list[i].split("$")
                        for part in res["results"][0]["data"][j]["graph"][return_prop[0]]:
                            if part["id"] == str(entity_id):
                                if return_prop[1] in ["1label", "1value"]:
                                    text = part["properties"][return_prop[1][1:]]
                                elif return_prop[1] in part["properties"].keys():
                                    text = part["properties"][return_prop[1]]
                                    if "labels" in part.keys():
                                        if "person" in part["labels"] and "website" in part["properties"].keys():
                                            ans_url = part["properties"]["website"]
                                        elif "movie" in part["labels"] and "url" in part["properties"].keys():
                                            ans_url = part["properties"]["url"]
                                else:
                                    continue
                                if ans_url == "nan":
                                    ans_url = "https://www.baidu.com/s?wd=" + text
                                if return_prop[2] != "INFO":
                                    ans.append({"text": text, "url": ans_url})
                                    # print("attention!! this is the dataset generation verion! for qa, use the other append line")
                                    # ans.append(text)

                                    if return_prop[2] == "UNK":
                                        unk_dict[len(ans) - 1] = j
                                    cnt = cnt + 1
                                else:
                                    info_dict[j] = text + ": "
                if len(info_dict) > 0:
                    for k, v in unk_dict.items():
                        ans[k]["text"] = info_dict[v] + ans[k]["text"]
        ans_list = []
        for i in range(len(ans)):
            if ans[i] not in ans_list:
                ans_list.append(ans[i])

        return ans_list

    def get_additional_answer(self, json_res, limitation):
        # cypher_img = "MATCH (a:movie)-[r]-(b:imgs)" + line_break + \
        #              "WHERE id(a)={id}" + line_break + "RETURN b LIMIT {limitation}"
        cypher_review = "MATCH (a:movie)-[r]-(b:reviews)" + line_break + \
                        "WHERE id(a)={id}" + line_break + "RETURN b LIMIT {limitation}"
        add_visual_ans = []
        movie_id_list = []
        for data in json_res["results"][0]["data"]:
            for node in data["graph"]["nodes"]:
                if "movie" in node["labels"]:
                    movie_id = int(node["id"])
                    if movie_id not in movie_id_list:
                        movie_id_list.append(movie_id)
                        # query_res = QueryCypher(url, login, cypher_img.format(limitation=limitation, id=movie_id))
                        # add_visual_ans.append(query_res)
                        query_res = QueryCypher(self.url, self.login,
                                                cypher_review.format(limitation=limitation, id=movie_id))
                        add_visual_ans.append(query_res)
        return add_visual_ans

    def get_answer(self, triplet_set, attlist_set, logic, neg, relate_flag):
        """
        获得问题的查询结果
        :param relate_flag:
        :param triplet_set: 三元组
        :param attlist_set: 属性列表
        :param logic: 逻辑连接词
        :param neg: 条件否定词
        :return: 返回输入问题的答案
        """

        if relate_flag:
            # self.__match_relation__(triplet_set, attlist_set, logic, neg)
            ans, visual_ans = self.__match_relation__(triplet_set, attlist_set, logic, neg)
        else:
            # self.__match_node__(triplet_set, attlist_set, logic, neg)
            ans, visual_ans = self.__match_node__(triplet_set, attlist_set, logic, neg)
        # return None, None
        return ans, visual_ans

    @staticmethod
    def question_com_parser(question_components):
        attr_list = []
        triplet = tuple()
        for k, v in question_components["propdict"].items():
            v["type"] = "companies" if v["type"] == "company" else v["type"]
            triplet = triplet + ([v["type"]], [k])
            entity_property = []
            for p in v["prop"]:
                if question_components["lang"] == "zh":
                    if v["type"] == "person" and p[0] == "primaryName":
                        p[0] = "Chinese_name"
                    elif v["type"] == "movie" and p[0] == "primaryTitle":
                        p[0] = "Chinese_title"
                entity_property.append(["INFO", p[0], p[1], "cond"])
            attr_list.append(entity_property)
        attr_list = [attr_list]
        triplet_list = [triplet + ([question_components["output"]["id"]],)]

        return triplet_list, attr_list

    def chain_parser(self, logic_chain, question_components, entity_pron):
        triplet_list = []
        attr_list = []
        # logic_list = []
        for i in range(len(logic_chain)):
            chain = logic_chain[i][0].split('_')
            pron = entity_pron[i]
            # logic = []
            entity_repost = []
            triplet = tuple()
            for j in range(int((len(chain) - 1) / 2)):
                # 初始化
                head = self.chain_entity_dict[chain[j * 2]].split("$")
                head_entity_property = [["INFO", "", "", ""]]
                head_entity_value = ""
                tail = self.chain_entity_dict[chain[j * 2 + 2]].split("$")
                tail_entity_property = [["INFO", "", "", ""]]
                tail_entity_value = ""
                if len(head) > 1:
                    head, relation = head[0], head[1]
                    tail = tail[0]
                elif len(tail) > 1:
                    tail, relation = tail[0], tail[1]  # 假设person不与person直接关联，因此不会出现head tail同时给出关系的情况
                    head = head[0]
                else:
                    head, tail = head[0], tail[0]
                    relation = ""
                if j == 0:
                    overall_head_type = head
                # # 若产生多跳实体链，添加logic关联
                # if j > 1:
                #     logic.append("and")
                # 实体链 总头实体 属性关联
                for k, v in question_components["propdict"].items():
                    flag = (k in pron) and (v["type"] == overall_head_type)
                    if (flag or (head in k)) and (k not in entity_repost):
                        head_entity_property = []
                        for p in v["prop"]:
                            # 中文double check
                            if question_components["lang"] == "zh":
                                if v["type"] == "person" and p[0] == "primaryName":
                                    p[0] = "Chinese_name"
                                elif v["type"] == "movie" and p[0] == "primaryTitle":
                                    p[0] = "Chinese_title"
                            head_entity_property.append(["INFO", p[0], p[1], "cond"])
                        head_entity_value = k
                        entity_repost.append(k)
                # 实体链 总尾实体 属性关联
                if (j * 2 + 2) == (len(chain) - 1):
                    # 中文double check
                    if question_components["lang"] == "zh":
                        if question_components["output"]["type"] == "person" and \
                                question_components["output"]["prop"][0] == "primaryName":
                            question_components["output"]["prop"][0] = "Chinese_name"
                        elif question_components["output"]["type"] == "movie" and \
                                question_components["output"]["prop"][0] == "primaryTitle":
                            question_components["output"]["prop"][0] = "Chinese_title"
                    tail_entity_property = [["UNK", question_components["output"]["prop"][0], "?", "what"]]
                    tail_entity_value = question_components["output"]["id"]

                # wrong name sub
                head = "companies" if head == "company" else head
                tail = "companies" if tail == "company" else tail
                sub_dict = {"DoubanRating": "rating", "IMDBRating": "averageRating",
                            "release-date": "release_date", "trade-mark": "trade_mark",
                            "production-designer": "production_designer"}
                for i in range(len(head_entity_property)):
                    for k, v in sub_dict.items():
                        if k in head_entity_property[i][2]:
                            head_entity_property[i][2] = v
                for i in range(len(tail_entity_property)):
                    for k, v in sub_dict.items():
                        if k in tail_entity_property[i][2]:
                            tail_entity_property[i][2] = v

                # 三元组 实体、属性
                if head_entity_value == tail_entity_value and head_entity_value != "":
                    if len(triplet) == 0:
                        triplet = ([head], [head_entity_value])
                        attr = [head_entity_property + tail_entity_property]
                    elif len(triplet[0]) % 2 == 0:
                        attr_list[-1][0] = attr_list[-1][0] + head_entity_property + tail_entity_property
                        continue
                    else:
                        attr_list[-1][1] = attr_list[-1][1] + head_entity_property + tail_entity_property
                        continue
                else:
                    if len(triplet) == 0:
                        triplet = ([head], [head_entity_value], [tail], [tail_entity_value], [relation])
                        attr = [head_entity_property, tail_entity_property]
                    # 衔尾存储
                    elif len(triplet[0]) % 2 == 0:
                        tup = (head, head_entity_value, tail, tail_entity_value, relation)
                        for t in range(len(triplet)):
                            triplet[t].append(tup[t])
                        attr = [head_entity_property, tail_entity_property]
                    else:
                        tup = (tail, tail_entity_value, head, head_entity_value, relation)
                        for t in range(len(triplet)):
                            triplet[t].append(tup[t])
                        attr = [tail_entity_property, head_entity_property]
                attr_list.append(attr)
            triplet_list.append(triplet)
            # logic_list = logic_list + logic
            # if i < len(question_components["logic"]):
            #     logic_list.append(question_components["logic"][i])
        return triplet_list, attr_list
