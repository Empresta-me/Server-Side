import redis 

class Redis_interface:

    def __init__(self, host= 'redis', port= 6379, db= 0):

        pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.redis_cli = redis.Redis(connection_pool=pool)

    def set(self, key, value):
        self.redis_cli.set(key, value)
        
        print("[ADDED] " , key + ": " ,  value)
       
    def get(self, key) -> str:
        value = self.redis_cli.get(key)
        print("[GETTED]", key, value)
        return value

    def delete(self, key): 
        value = self.redis_cli.get(key) 
        self.redis_cli.delete(key)
        print("[DELETED] " , key , ": " ,  value)

    def pop(self, key):
        value = self.redis_cli.get(key) 
        self.redis_cli.delete(key)
        print("[POPPED] " , key , ": " ,  value)
        return value

    def keys(self):
        return self.redis_cli.keys()

    def addToSet(self, name, value):
        self.redis_cli.sadd(name, value)
        print("[ADDED TO SET]", name, value)

    def delFromSet(self, name, value):
        self.redis_cli.srem(name, value)
        print("[REMOVED FROM SET]", name, value)

    def isInSet(self, name, value):
        isIn = self.redis_cli.sismember(name, value)
        print("[CHECKED IF PART OF SET]", name, value, isIn)
        return isIn

    def newHashSet(self, key, dic):
        # TODO we may need to convert all keys in dic to String

        self.redis_cli.hset(name= key, mapping= dic)
        print("[CREATE NEW HASHSET] " , key, ": ", dic)


    def getSingleValueFromHashSet(self, set_name, key):
        value = self.redis_cli.hget(set_name, key)
        print("[GETTED SINGLE VALUE FROM HASHSET]", set_name, key, value)
        return value

    def getWholeHashSet(self, set_name):
        dic = self.redis_cli.hgetall(set_name)
        print("[GETTED WHOLE HASHSET]", set_name, dic)
        return dic