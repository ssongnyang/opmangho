from sentence_transformers import SentenceTransformer, util
from stock.crawler import news_title

import random


async def similarity(keyword: str):
    # stock_kr = "이 기업은 좋은 평가를 받는다"
    sum = 0
    for _ in range(10):
        # 원래는 뉴스 기사를 가져와 문장 간 유사도를 이용하려 했으나, 시간이 너무 많이 걸려 런타임 경고가 나서 폐기
        # model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        # emb1 = model.encode(title)
        # emb2 = model.encode(stock_kr)

        # cos_sim = util.cos_sim(emb1, emb2)
        # value = cos_sim.item()

        # random.seed(title)
        value = random.random()
        sum += value

    return sum
