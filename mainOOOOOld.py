import random
from difflib import SequenceMatcher

file = open('api.txt', 'r')
apilsit = file.readlines()
print(apilsit)

def wordlist() :
    protocol = [p.strip('\n') for p in open('url_schemas.txt', 'r').readlines()]
    domain = [d.strip('\n') for d in open('localhost.txt', 'r').readlines()]
    path = [p.strip('\n') for p in open('endpoint.txt', 'r').readlines()]

    for pro in protocol :
        for l in domain :
            for p in path :
                print(pro + l + p)

ApiDetail = []
randID = input()
baseurl = f"https://{randID}.web-security-academy.net"
CRUD = [['/product/stock', '/login'], ['/product', '/my-account', '/product/nextProduct', '/'], [], []]
# Create, Read, Update, Delete
FinApi = ['/product/stock', '/login', '/product/nextProduct']
Apidict = {
    "/":[], 
    "/product":['productId'], 
    "/product/stock":['stockApi'], 
    "/product/nextProduct":['currentProductId', 'path'],
    "/my-account":[],
    "/login":['csrf', 'username', 'password']
    }

ArgsBucket = []
ReqSeqBucket = []

def ArgsRatio(PreApi, NextApi) :
    ratio = 0.0
    PreApiArgs = Apidict[PreApi]
    NextApiArgs = Apidict[NextApi]
    for arg in PreApiArgs :
        for arg2 in NextApiArgs :
            ratio += SequenceMatcher(None, arg, arg2).ratio()
    return ratio

def NextScoreCalc(CurrentState, CurrentApi, nextApi) :
    higest = -1
    index = ()
    for i in len(CRUD) :
        score = float(0)
        if CRUD[i] == [] :
            continue
        elif i == 0 :
            if CurrentState == "Read" :
                score += 1
        elif i == 1 :
            if CurrentState == "Create" :
                score += 1
        elif i == 2 :
            if CurrentState == "Read" :
                score += 1
        elif i == 3 :
            if CurrentState == "Read" :
                score += 1
        for apis in CRUD[i] :
            score += ArgsRatio(CurrentApi, apis)
            if apis in FinApi :
                score += 1
            if score > higest :
                higest = score
                index = (i, apis)
    return index
            

def AstarFuzzer() :
    for i in CRUD[0] :
        reqSeq = []
        reqSeq.append(i)
        CurrentStste = ""
        ArgsBucket.append(Apidict[i])
        NextScoreCalc





wordlist()
# for i in apilsit:
#     print(i)

