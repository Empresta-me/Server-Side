import redis 

class RedisInterface:

    def __init__(self, host= 'redis', port= 6379, db= 0):

        pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.redis_cli = redis.Redis(connection_pool=pool)

    # HASHSET

    def hdel(self, key : str, field : str):
        self.redis_cli.hdel(key, field)

    def hexists(self, key : str, field : str):
        return self.redis_cli.hexists(key, field)

    def hget(self, key : str, field : str):
        return self.redis_cli.hget(key, field)

    def hset(self, key : str, field : str, value : str):
        self.redis_cli.hset(key, field, value)

    # SET

    def sismember(self, key : str, member : str):
        return self.redis_cli.sismember(key, member)

    def sadd(self, key : str, member : str):
        self.redis_cli.sadd(key, member)

    def srem(self, key : str, member : str):
        self.redis_cli.srem(key, member)

    '''
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
        """ stores a dictionary (account) referenced by "key\" """
        # NOTE we may need to convert all keys in dic to String

        self.redis_cli.hset(name= key, mapping= dic)
        print("[CREATE NEW HASHSET] " , key, ": ", dic)


    def getSingleValueFromHashSet(self, key, key_in_dic):
        """ returns a single value from a dictionary (account)\n 
        uses "key" to identify the dictionary, \n
        and "key_in_dic" to locate the desired value within it"""

        value = self.redis_cli.hget(key, key_in_dic)
        print("[GETTED SINGLE VALUE FROM HASHSET]", key, key_in_dic, value)
        return value

    def getWholeHashSet(self, key):
        """ returns a dictionary (account) referenced by "key\" """

        dic = self.redis_cli.hgetall(key)
        print("[GETTED WHOLE HASHSET]", key, dic)
        return dic
    '''
