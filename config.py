class Config:
    ENV = 'LOCAL'
    JWT_SECRET_KEY = 'test-password'
    SESSION_SECRET = 'session-secrey'
    MONGODB_HOST = 'localhost:27017'
    MONGODB_DB = 'blog'
    MONGODB_USER = 'blog-admin'
    MONGODB_PWD = 'un1bl0g$'
    MONGODB_URL = 'mongodb://%s:%s@%s/%s?retryWrites=true&w=majority' % (MONGODB_USER,
                                                                         MONGODB_PWD,
                                                                         MONGODB_HOST,
                                                                         MONGODB_DB)
    origins = [
        "http://localhost:5000"
    ]
