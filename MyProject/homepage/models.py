from random import *
import csv,os,sqlite3
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ВХОД, ВЫХОД, ПРОВЕРКА ДОСТУПА, НИКНЭЙМ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
class models2:
    def enter(self,login,password):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        logpass=cur.execute('SELECT login,password FROM users').fetchall()
        if (login,password) in logpass:
            userid=cur.execute('SELECT id FROM users WHERE login=? AND password=?',(login,password)).fetchone()[0]
            session=cur.execute('SELECT * FROM sessionuser').fetchall()
            if (int(userid),) not in session:
                cur.execute('INSERT INTO sessionuser VALUES(?)',(userid,))
                answer=str(userid)
            else:
                answer=False
        else:
            answer=False
        conn.commit()
        return answer
    def nickname(self,userid):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        nickname=cur.execute('SELECT name FROM users WHERE id=?',(userid)).fetchone()[0]
        conn.commit()
        return nickname
    def access(self,userid):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        tf=cur.execute('SELECT * FROM sessionuser').fetchall()
        conn.commit()
        return ((int(userid),) in tf)
    def quit(self,userid):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM sessionuser WHERE id=?',(userid,))
        conn.commit()

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ТЕСТЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#  
    def listtests(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result={} 
        objects=cur.execute('SELECT id,name FROM objects').fetchall()
        for i in objects:
            tests=cur.execute('SELECT id,name FROM tests WHERE object=? AND active="Активен"',(i[0],)).fetchall()
            result[i]=tests
        conn.commit()
        return result
    def getinfo(self,testid,table):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        test=cur.execute(f'SELECT id,name FROM {table} WHERE id=?',(testid,)).fetchone()
        conn.commit()
        return test
    def starttest(self,user,test,flag):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions=cur.execute('SELECT questions FROM tests WHERE id=?',(test,)).fetchone()[0]
        session=cur.execute('SELECT user,test FROM sessiontest').fetchall()
        if (user,test) in session:
            id=cur.execute('SELECT id FROM sessiontest WHERE user=? AND test=?',(user,test)).fetchone()[0]
            if flag:
                questions=cur.execute('SELECT questions FROM sessiontest WHERE id=?',(id,)).fetchone()[0]
            cur.execute('DELETE FROM sessiontest WHERE user=? AND test=?',(user,test))
        else:
            id=generator().newid('sessiontest')
        cur.execute('INSERT INTO sessiontest VALUES(?,?,?,?,?,?)',(id,user,test,questions,0,0))
        questions=questions.split(',') if ',' in questions else []
        questions=sample(questions,len(questions)) if (user,test) not in session else questions
        questions.append('end')
        questions.append(str(id))
        conn.commit()
        return questions
    def question(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        question=cur.execute('SELECT id,img,text FROM questions WHERE id=?',(id,)).fetchone()
        conn.commit()
        return question
    def resulttest(self,id,table):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        res=cur.execute(f'SELECT allq,trueq FROM session{table} WHERE id=?',(id,)).fetchone()
        if res[0]!=0:
            res=round(res[1]/res[0],2)
            if res>=0.8:
                score=5
            elif res>=0.6:
                score=4
            elif res>=0.4:
                score=3
            else:
                score=2
            res=f'<br>Ваш результат - {res*100}%<br>Ваша оценка - {score}' 
        else:
            res='Вы не ответили ни на один вопрос'
        conn.commit()
        return res
    def answertest(self,ids,idq,answer,table):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions=cur.execute(f'SELECT questions FROM session{table} WHERE id=?',(ids,)).fetchone()[0].split(',')
        if str(idq) in questions:
            trueanswer=cur.execute('SELECT answer FROM questions WHERE id=?',(idq,)).fetchone()[0]
            cur.execute(f'UPDATE session{table} SET allq=allq+1 WHERE id=?',(ids,))
            if answer==trueanswer:
                cur.execute(f'UPDATE session{table} SET trueq=trueq+1 WHERE id=?',(ids,))
            questions.remove(str(idq))
            cur.execute(f'UPDATE session{table} SET questions=? WHERE id=?',(','.join(questions),ids))
        conn.commit()
    def continuetest(self,user,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        session=cur.execute(f'SELECT user,test FROM sessiontest').fetchall()
        conn.commit()
        flag=(int(user),int(test)) in session
        return flag
    def endtest(self,ids,table):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute(f'DELETE FROM session{table} WHERE id=?',(ids,))
        conn.commit()
#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ДОМАШНЕЕ ЗАДАНИЕ"""""""""""""""""""""""""""""""""""""""""""""""""""""""# 
    def listhomeworks(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result={} 
        objects=cur.execute('SELECT id,name FROM objects').fetchall()
        for i in objects:
            tests=cur.execute('SELECT id,name FROM homework WHERE object=? AND active="Активен"',(i[0],)).fetchall()
            result[i]=tests
        conn.commit()
        return result
    def starthomework(self,user,test,flag):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        qtypes=cur.execute('SELECT qtypes FROM homework WHERE id=?',(test,)).fetchone()[0]
        session=cur.execute('SELECT user,test FROM sessionhomework').fetchall()
        if (user,test) in session:
            id=cur.execute('SELECT id FROM sessionhomework WHERE user=? AND test=?',(user,test)).fetchone()[0]
            if flag:
                questions=cur.execute('SELECT questions FROM sessionhomework WHERE id=?',(id,)).fetchone()[0]
                questions=questions.split(',') if ',' in questions else []
            cur.execute('DELETE FROM sessionhomework WHERE user=? AND test=?',(user,test))
        else:
            id=generator().newid('sessionhomework')
        if not(flag):
            qtypes=dict([i.split(':') for i in qtypes.split(',')]) if ',' in qtypes else {}
            questions=[]
            for type in qtypes:
                allq=cur.execute('SELECT id FROM questions WHERE type=?',(type,)).fetchall()
                allq=[str(i[0]) for i in allq]
                questions+=sample(allq,int(qtypes[type]))
        cur.execute('INSERT INTO sessionhomework VALUES(?,?,?,?,?,?)',(id,user,test,','.join(questions),0,0))
        questions=sample(questions,len(questions)) if (user,test) not in session else questions
        questions.append('end')
        questions.append(str(id))
        conn.commit()
        return questions
    def continuehm(self,user,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        session=cur.execute(f'SELECT user,test FROM sessionhomework').fetchall()
        conn.commit()
        flag=(int(user),int(test)) in session
        return flag

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГРУППЫ И ЗАПИСИ"""""""""""""""""""""""""""""""""""""""""""""""""""""""# 
    def listgroups(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        groups=cur.execute('SELECT id,name,img FROM groups ORDER BY id').fetchall()
        conn.commit()
        return groups
    def listrecords(self,idg):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        records=cur.execute('SELECT id,date,name,text FROM records WHERE idgroup=? ORDER BY date',(idg,)).fetchall()
        conn.commit()
        return records
    def namegroup(self,idgroup):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT name FROM groups WHERE id=?',(idgroup,)).fetchone()[0]
        conn.commit()
        return name

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГЕНЕРАТОР"""""""""""""""""""""""""""""""""""""""""""""""""""""""#        
class generator:
    def login(self,user):
        slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
        'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
        'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
        'ц':'c','ч':'ch','ш':'sh','щ':'scz','ъ':'','ы':'y','ь':'','э':'e',
        'ю':'u','я':'ya', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E',
        'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
        'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
        'Ц':'C','Ч':'CH','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'y','Ь':'','Э':'E',
        'Ю':'U','Я':'YA'}
        name,last_name=user.split()
        login=[]
        for i in last_name:
            if i in slovar:
                login.append(slovar[i])
            else:
                login.append(i)
        if name[0] in slovar:
            login.append(slovar[name[0]])
        else:
            login.append(name[0])
        login[0]=login[0].upper()
        return ''.join(login)
    def password(self):
        stock='111222333444555666777888999'
        password=sample(stock,5)
        return ''.join(password)
    def newid(self,table):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        newid=cur.execute(f"SELECT id FROM {table} ORDER BY id DESC").fetchmany(1)
        conn.commit()
        if newid==[]:
            newid=0
        else:
            newid=int(newid[0][0])
        return str(newid+1)