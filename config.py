import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xe6\xf7\xb0\xfeo\x06\xb1k\xefU\x82\xbc|\xa3\xca\xbf'
    MONGODB_SETTINGS = {'db': 'UTA_Enrollment'}
    
 
    