# MineBot

Python 모듈로 제공되는 MineBot의 주식 데이터 API입니다.

## 설치

pip install minebot

## 사용법

```python
from minebot import getapi

data = getapi()
print(data)


## 출력 예시


[
  {
    "date": "2025-05-01",
    "stock": "MINE",
    "price": 120
  },
  {
    "date": "2025-05-02",
    "stock": "MINE",
    "price": 135
  }
]

