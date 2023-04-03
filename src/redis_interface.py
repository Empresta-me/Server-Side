import redis 

class Redis_interface:

    def __init__(self, host= 'localhost', port= 6379):

        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.redis_cli = redis.Redis(connection_pool=pool)

    def set(self, key, value):
        self.redis_cli.set(key, value)
        
        print("[ADDED] " + key + ": " +  value)
       
    def get(self, key) -> str:

        return self.redis_cli.get(key) 

    def delete(self, key, value): 
        value = self.redis_cli.get(key) 
        self.redis_cli.delete(key)
        print("[DELETED] " + key + ": " +  value)