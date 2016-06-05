FACE_TRACES = 'face_traces'
FRAMES = 'frames'
''' EXAMPLE
mc = MC({'serverUrl': 'ds****.mlab.com', port: 21343, 'userName': '****', 'password': '****',
'dbName': '****'})
'''
class MC:
    from pymongo import MongoClient

    def __init__(self, prms):
        userName = None
        password = None
        print prms
        serverUrl = prms['serverUrl']
        port = prms['port']
        try:
            prms['userName']
        except AttributeError:
            userName = None
        else:
            userName = prms['userName']
        try:
            prms['password']
        except AttributeError:
            password = None
        else:
            password = prms['password']
        dbName = prms['dbName']
        if userName is not None and password is not None:
            print 'with credentials'
            self.client = self.MongoClient(serverUrl, port)
            self.db = self.client[dbName]
            self.db.authenticate(userName, password)
        else:
            print 'without credentials'
            self.client = self.MongoClient("mongodb://" + serverUrl + ":" + port)
            self.db = self.client[dbName]

    def getFrameByName(self, name):
        return self.db[FRAMES].find_one({ 'name': name })

    def addFrame(self, doc):
        return self.db[FRAMES].insert_one(doc).inserted_id

    def addMultipleFrames(self, docs):
        return self.db[FRAMES].insert_many(docs, ordered = False)

    def getFaceTraceByTraceId(self, id):
        return self.db[FACE_TRACES].find_one({ 'id': id })

    def addFaceTrace(self, doc):
        return self.db[FACE_TRACES].insert_one(doc).inserted_id

    def updateFaceTrace(self, doc):
        return self.db[FACE_TRACES].update_one({'_id':doc['_id']}, {'$set': doc}, upsert=False)

    def existsFaceTraceField(self, field):
        expression = {}
        expression[field] = {"$exists":False}
        return self.db[FACE_TRACES].find(expression)
