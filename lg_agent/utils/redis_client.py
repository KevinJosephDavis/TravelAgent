import redis
import os
from dotenv import load_dotenv

load_dotenv()

# 本地Redis配置，默认本地6379端口
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,  # 自动把bytes转字符串，不用解码
    password=os.getenv("REDIS_PASSWORD", "")
)

# 缓存过期时间：30分钟（单位：秒），可以根据需要调整
CACHE_EXPIRE_SECONDS = 1800

# 预热连接，Python-redis 的懒加载机制导致 redis-cli 在第一次执行 .get()/.ping() 才真正发起 TCP 握手
# 否则导致 weather_api 耗时较长
# 解决：模块加载时立即ping，提前完成 TCP 初始化
try:
    redis_client.ping()
    print("✅ Redis 连接成功！")
except redis.exceptions.ConnectionError as e:
    print(f"❌ Redis 连接失败：{e}")
    raise e
