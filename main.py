file = open('api.txt', 'r')
apilsit = file.readlines()
print(apilsit)

ApiDetail = []

create = ['https://web-security-academy.net/product/stock?stockApi=/product/stock/check?productId=2&storeId=1',
          'https://web-security-academy.net/login?csrf=&username=&password='          
          ]

read = ['https://web-security-academy.net/product?productId=2',
        'https://web-security-academy.net/my-account',
        'https://web-security-academy.net/product/nextProduct?currentProductId=3&path=/product?productId=4',
        'https://web-security-academy.net'
        ]

FinApi = ['https://web-security-academy.net/product/stock?stockApi=/product/stock/check?productId=2&storeId=1',
          'https://web-security-academy.net/login?csrf=&username=&password=',
          'https://web-security-academy.net/product/nextProduct?currentProductId=3&path=/product?productId=4'
          ]

ArgsBucket = []
ReqSeqBucket = []

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

