from google.appengine.ext import ndb

class Transaction(ndb.Model):
    type = ndb.StringProperty(required = True)
    amount = ndb.FloatProperty(required = True)
    timestamp = ndb.DateTimeProperty(auto_now_add = True)
    other_user_name = ndb.StringProperty()

class User(ndb.Model):
    balance = ndb.FloatProperty(default = 0)
