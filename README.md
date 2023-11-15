#   QA with Data

## Install
```
conda create -n qa_data python=3.7
conda activate qa_transformer
pip install -r requirements.txt
```

安装paddle-NLP

```
python -m pip install paddlepaddle==2.4.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install --upgrade paddlenlp
```

输入请求
```
requests.get('http://910.mivc.top:20000/qa/qa?question=' + question).json()
```
返回数据结构为json文件
```
{
    "q_return: str， #自然语言形式的答案
    "answer": list, #答案列表list，每个元素为一个字典{'text':xxx, 'url': xxx}. 关系类问题url为None
    "cypher": json, #json文件（字典），用于可视化，所有三元组存放于"graph"键值
    "addition": list of json, #所有涉及电影的n个片花和n条评论（目前n=3）
}
```

## Pretrained models
```shell
# en_core_web_sm：
pip --default-timeout=10000 install https://github.com.cnpmjs.org/explosion/spacy-models/releases/download/en_core_web_sm-2.3.0/en_core_web_sm-2.3.0.tar.gz
```

逻辑链生成模型基于Semantic-Parsing-for-KGQA代码训练生成，预训练模型存放在`checkpoint/test_339/`路径下。

