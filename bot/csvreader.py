from pandas import *
import sys
sys.path.insert(1,'../')
from orm.ormvideo import session , User
a=read_csv('csva.csv')

names=a['نام'].to_list()
names = list(dict.fromkeys(names))
for i in names:
    new_user = User(pname=i)
    session.add(new_user)
    session.commit()