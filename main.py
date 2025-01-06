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



wordlist()
# for i in apilsit:
#     print(i)

