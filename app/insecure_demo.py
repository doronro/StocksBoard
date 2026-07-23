import hashlib
API_KEY = "sk_live_"
def h(p): return hashlib.md5(p.encode()).hexdigest()
