class CacheKeys:
    # using short key names to save space in redis
    MAX_PUBLISH_AT = "MXPA"
    MIN_PUBLISH_AT = "MNPA"
    EXPIRY = 10 * 60  # 10 minutes
    LOCK_FOR_EXTERNAL_SYNC = "LFES"
    YOUTUBE_API_KEY = "YAPI"
