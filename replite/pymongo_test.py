import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')

dblist = myclient.list_database_names()
# dblist = myclient.database_names()
if "admin" in dblist:
    print("数据库已存在！")
else:
    print("不存在")