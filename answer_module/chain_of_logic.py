from transformers import AutoTokenizer, T5ForConditionalGeneration, pipeline
from sentence_transformers import SentenceTransformer
import pandas as pd
import torch
import heapq


class Triplet2Chain:
    def __init__(self):
        # 加载预训练模型
        print("Loading pretrained model for triplet to chain")
        checkpoint_path = "checkpoint/test_339/"
        tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        model = T5ForConditionalGeneration.from_pretrained(checkpoint_path)
        self.summarizer = pipeline(task="summarization", model=model, tokenizer=tokenizer)
        self.sim_model = SentenceTransformer('hiiamsid/sentence_similarity_hindi')

        # 加载逻辑链groundtruth
        print("Loading targets for chain of logic")
        df = pd.read_csv("chain/example_train.csv")
        df = df.drop_duplicates(subset=['summary'])
        self.path_targets = df["summary"].to_list()
        self.path_target_embedding = self.sim_model.encode(self.path_targets)

    @staticmethod
    def cos_sim(a: torch.Tensor, b: torch.Tensor):
        """
        Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
        :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
        """
        if not isinstance(a, torch.Tensor):
            a = torch.tensor(a)

        if not isinstance(b, torch.Tensor):
            b = torch.tensor(b)

        if len(a.shape) == 1:
            a = a.unsqueeze(0)

        if len(b.shape) == 1:
            b = b.unsqueeze(0)

        a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
        b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
        return torch.mm(a_norm, b_norm.transpose(0, 1))

    @staticmethod
    def entity_substitute(question_component):
        """
        替换查询问句中的实体指代词，如：P1, P2 ——> Person; M1, M2 ——> Movie
        """
        query = []
        entity_pron = []
        for question in question_component["question_set"]:
            question = question.text
            pron = []
            for k, v in question_component["propdict"].items():
                sub_question = question.replace(k, v["type"].title())
                if sub_question != question:
                    pron.append(k)
                question = sub_question
            entity_pron.append(pron)
            query.append(question)
        return query, entity_pron

    def get_logic_chain(self, query):
        # 获取查询问句的嵌入表示
        output_query = self.summarizer(query, max_length=23, min_length=8)
        output_query_list = []
        for i in range(len(output_query)):
            output_query_list.append(output_query[i]["summary_text"])
        output_query_embedding = self.sim_model.encode(output_query_list)

        # 对比groundtruth相似性，筛选最相近的逻辑链作为输出
        hop_number = 1
        transfer_output = []
        for i in range(len(output_query_list)):
            score_list = []
            for j in range(len(self.path_targets)):
                score = self.cos_sim(output_query_embedding[i], self.path_target_embedding[j]).item()
                score_list.append(score)
            max_score_l = heapq.nlargest(hop_number, score_list)
            max_score_index = []
            for k in max_score_l:
                max_score_index.append(score_list.index(k))
            transfer_output.append([self.path_targets[max_score_index[i]] for i in range(len(max_score_index))])
        return transfer_output
