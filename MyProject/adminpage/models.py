from random import *
import csv,os,sqlite3,re



class models:
#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ВХОД, ВЫХОД, ПРОВЕРКА ДОСТУПА, НИКНЭЙМ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def enter(self,login,password):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        logpass=cur.execute('SELECT login,password FROM users').fetchall()
        if (login,password) in logpass:
            userid=cur.execute('SELECT id FROM users WHERE login=? AND password=?',(login,password)).fetchone()[0]
            session=cur.execute('SELECT * FROM sessionadmin').fetchall()
            if (int(userid),) not in session:
                cur.execute('INSERT INTO sessionadmin VALUES(?)',(userid,))
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
        tf=cur.execute('SELECT * FROM sessionadmin').fetchall()
        conn.commit()
        return ((int(userid),) in tf)
    def quit(self,userid):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM sessionadmin WHERE id=?',(userid,))
        conn.commit()

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ПОЛЬЗОВАТЕЛИ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def listusers(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        users=cur.execute('SELECT * FROM users ORDER BY id').fetchall()
        conn.commit()
        return users
    def newusers(self,users,status):
        for user in users:
            conn = sqlite3.connect('db.sqlite3')
            cur = conn.cursor()
            listusers=cur.execute('SELECT name FROM users').fetchall()
            if len(user.split())!=2 or (user,) in listusers:
                continue
            login,password=generator().login(user),generator().password()
            logpass=cur.execute('SELECT login,password FROM users').fetchall()
            while (login,password) in logpass:
                login,password=generator().login(user),generator().password()
            userid=generator().newid('users')
            cur.execute('INSERT INTO users VALUES(?,?,?,?,?)',(userid,user,login,password,status))
            conn.commit()
    def deluser(self,userid):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id=?',(userid,))
        conn.commit()
    def updateuser(self,userid,name,login,password):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE users SET name=?,login=?,password=? WHERE id=?',(name,login,password,userid))
        conn.commit()
    def searchusers(self,req):
        if len(req.strip())==0:
            return models().listusers()
        else:
            listusers=models().listusers()
            serveranswer=[]
            for user in listusers:
                if req in user or req in user[1] or req==str(user[0]):
                    serveranswer.append(user)
            return serveranswer

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГРУППЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def newgroup(self,name,creator,users,img):
        idg=generator().newid('groups')
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        groups=cur.execute('SELECT name FROM groups').fetchall()
        if (name,) not in groups:
            if img!=None:
                namefile=f'{str(idg)}.{img.name.split(".")[1]}'
                with open(os.path.join('static/avatars',namefile), "wb") as out:
                    out.write(img.read())
            else:
                namefile='none.png'
            users=str(users)[1:-1].replace("'",'').replace('"','')
            cur.execute('INSERT INTO groups VALUES(?,?,?,?,?)',(idg,name,creator,users,namefile))
        conn.commit()
    def listgroups(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        groups=cur.execute('SELECT id,name FROM groups ORDER BY id').fetchall()
        conn.commit()
        return groups
    def listusersing(self,group):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        serveranswer={}
        creator=cur.execute('SELECT creator FROM groups WHERE id=?',(group,)).fetchone()[0]
        users=cur.execute('SELECT users FROM groups WHERE id=?',(group,)).fetchone()[0].split(", ")
        serveranswer[creator]='Учитель'
        for user in users:
            serveranswer[user.replace("'",'')]='Ученик'
        conn.commit()
        return serveranswer
    def delgroup(self,group):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        img=cur.execute('SELECT img FROM groups WHERE id=?',(group,)).fetchone()[0]
        if img!='none.png':
            os.remove('static/avatars/'+img)
        cur.execute('DELETE FROM groups WHERE id=?',(group,))
        conn.commit()
    def newusing(self,user,group):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        users=cur.execute('SELECT users FROM groups WHERE id=?',(group,)).fetchone()[0].split(", ")
        users.append(user)
        users=str(users)[1:-1].replace("'",'').replace('"','')
        cur.execute('UPDATE groups SET users=? WHERE id=?',(users,group))
        conn.commit()
    def delusing(self,user,group):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        users=cur.execute('SELECT users FROM groups WHERE id=?',(group,)).fetchone()[0].split(", ")
        users.remove(user)
        users=str(users)[1:-1].replace("'",'').replace('"','')
        cur.execute('UPDATE groups SET users=? WHERE id=?',(users,group))
        conn.commit()
    def namegroup(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT name FROM groups WHERE id=?',(id,)).fetchone()[0]
        conn.commit()
        return name 

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ТЕМЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def listtopic(self,object):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        topics=cur.execute('SELECT * FROM topics WHERE object=? ORDER BY id',(object,)).fetchall()
        conn.commit()
        return topics
    def newtopic(self,name,object):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        topics=cur.execute('SELECT name FROM topics')
        if (name,) not in topics:
            idtopic=generator().newid('topics')
            cur.execute('INSERT INTO topics VALUES(?,?,?,?)',(idtopic,object,name,0))
            cur.execute('UPDATE objects SET len=len+1 WHERE id=?',(object,))
        conn.commit()
    def deltopic(self,idtopic,object):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM topics WHERE id=?',(idtopic,))
        types=cur.execute('SELECT id FROM types WHERE topic=?',(idtopic,)).fetchall()
        types=[str(i[0]) for i in types]
        cur.execute(f'DELETE FROM questions WHERE type IN ({",".join(types)})')
        cur.execute('DELETE FROM types WHERE topic=?',(idtopic,))
        cur.execute('UPDATE objects SET len=len-1 WHERE id=?',(object,))
        conn.commit()
    def updatetopic(self,idtopic,name):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE topics SET name=? WHERE id=?',(name,idtopic))
        conn.commit()
    def nameobject(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT id,name FROM objects WHERE id=?',(id,)).fetchone()
        conn.commit()
        return name
    def listobandt(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result={}
        objects=cur.execute('SELECT id,name FROM objects').fetchall()
        for ob in objects:
            topics=cur.execute('SELECT id,name FROM topics WHERE object=?',(ob[0],)).fetchall()
            result[ob]=topics
        conn.commit()
        return result
    def nametopic(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT id,name FROM topics WHERE id=?',(id,)).fetchone()
        conn.commit()
        return name

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ТИПЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def listtype(self,topic):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        types=cur.execute('SELECT id,name,len FROM types WHERE topic=? ORDER BY id',(topic,)).fetchall()
        conn.commit()
        return types
    def newtype(self,name,topic):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        idtype=generator().newid('types')
        types=cur.execute('SELECT topic,name FROM types').fetchall()
        if (topic,name) not in types:
            cur.execute('INSERT INTO types VALUES(?,?,?,?)',(idtype,topic,name,0))
            cur.execute('UPDATE topics SET len = len + 1 WHERE id=?',(topic,))
        conn.commit()
    def deltype(self,idtype,topic):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM types WHERE id=?',(idtype,))
        cur.execute('UPDATE topics SET len = len - 1 WHERE id=?',(topic,))
        cur.execute('DELETE FROM questions WHERE type=?',(idtype,))
        conn.commit()
    def updatetype(self,idtype,newname):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE types SET name=? WHERE id=?',(newname,idtype))
        conn.commit()
    def listtt(self,object):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result={}
        topics=cur.execute('SELECT id,name FROM topics WHERE object=?',(object,)).fetchall()
        for t in topics:
            types=list(cur.execute('SELECT id,name FROM types WHERE topic=?',(t[0],)).fetchall())
            result[t]=types
        conn.commit()
        return result
    def nametype(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT id,name FROM types WHERE id=?',(id,)).fetchone()
        conn.commit()
        return name

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ВОПРОСЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def listquestions(self,search=None): #список вопросов(с необязательным поиском)
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions=cur.execute('SELECT * FROM questions ORDER BY id').fetchall()
        result=[]
        for question in questions:
            question=list(question)
            object=cur.execute('SELECT name FROM objects WHERE id=?',(question[1],)).fetchone()[0]
            type=cur.execute('SELECT topic,name FROM types WHERE id=?',(question[2],)).fetchone()
            topic=cur.execute('SELECT name FROM topics WHERE id=?',(type[0],)).fetchone()[0]
            question[1]=object
            question[2]=type[1]
            question.insert(2,topic)
            if search==None:
                result.append(question)
            elif (search in question[1] or search in question[2] or search in question[3] or search==str(question[0])):
                result.append(question)
        conn.commit()
        return result
    def newquestion(self,object,typeq,text,answer,img):
        if typeq=='-' or (len(text.strip())==0 and img==None):
            return 'Ошибка!'
        idq=generator().newid('questions')
        if img!=None:
            namefile=f'{str(idq)}.{img.name.split(".")[1]}'
            with open(os.path.join('static/img',namefile), "wb") as out:
                out.write(img.read())
        else:
            namefile=None
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('INSERT INTO questions VALUES(?,?,?,?,?,?)',(idq,object,typeq,text,answer,namefile))
        cur.execute('UPDATE types SET len=len+1 WHERE id=?',(typeq,))
        conn.commit()
    def delquestion(self,idq):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        typeq=cur.execute('SELECT type FROM questions WHERE id=?',(idq,)).fetchone()[0]
        namefile=cur.execute('SELECT img FROM questions WHERE id=?',(idq,)).fetchone()[0]
        if namefile!=None:
            os.remove('static/img/'+namefile)
        cur.execute('DELETE FROM questions WHERE id=?',(idq,))
        cur.execute('UPDATE types SET len = len - 1 WHERE id=?',(typeq,))
        conn.commit()
    def updatequestion(self,idq,text,answer,delimg,img):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        namefile=cur.execute('SELECT img FROM questions WHERE id=?',(idq,)).fetchone()[0]
        if len(text.strip())==0 and namefile=='None':
            serveranswer='Некоректные данные'
        else:
            if delimg=='on':
                os.remove('static/img/'+namefile)
                namefile=None
            if img!=None:
                namefile=f'{str(idq)}.{img.name.split(".")[1]}'
                with open(os.path.join('static/img',namefile), "wb") as out:
                    out.write(img.read())
            cur.execute('UPDATE questions SET text=?,answer=?,img=? WHERE id=?',(text,answer,namefile,idq))
            serveranswer='Готово!'
        conn.commit()
        return serveranswer

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ТЕСТЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def newtest(self,name,object,dicttypes):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        ids=[]
        idt=generator().newid('tests')
        for i in dicttypes:
            if dicttypes[i]!='0':
                questions=cur.execute('SELECT id FROM questions WHERE type=?',(i,)).fetchall()
                if questions==None: continue
                questions=[str(j[0]) for j in questions]
                k=int(dicttypes[i]) if int(dicttypes[i])<=len(questions) else len(questions)
                ids+=sample(questions,k)
        cur.execute('INSERT INTO tests VALUES(?,?,?,?,?)',(idt,object,name,','.join(ids),'Неактивен'))
        conn.commit()
    def listtests(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result={}
        objects=cur.execute('SELECT id,name FROM objects').fetchall()
        for t in objects:
            tests=list(cur.execute('SELECT id,name FROM tests WHERE object=?',(t[0],)).fetchall())
            result[t]=tests
        conn.commit()
        return result
    def listqint(self,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result=[]
        ids=cur.execute('SELECT questions FROM tests WHERE id=?',(test,)).fetchone()[0].split(',')
        for i in ids:
            question=cur.execute('SELECT * FROM questions WHERE id=?',(i,)).fetchone()
            if question==None: break
            else: question=list(question)
            type=cur.execute('SELECT topic,name FROM types WHERE id=?',(question[2],)).fetchone()
            topic=cur.execute('SELECT name FROM topics WHERE id=?',(type[0],)).fetchone()[0]
            question[2]=type[1]
            question.insert(2,topic)
            result.append(question)
        conn.commit()
        return result
    def updatetest(self,test,questions):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions=','.join([str(i) for i in questions])
        cur.execute('UPDATE tests SET questions=? WHERE id=?',(questions,test))
        conn.commit()
    def deltest(self,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM tests WHERE id=?',(test,))
        conn.commit()
    def getactive(self,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        active=cur.execute('SELECT active FROM tests WHERE id=?',(test,)).fetchone()[0]
        conn.commit()
        return active
    def upactive(self,test,active):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE tests SET active=? WHERE id=?',(active,test))
        conn.commit()
    def nametest(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT id,name FROM tests WHERE id=?',(id,)).fetchone()
        conn.commit()
        return name
    def listquestionsfortest(self,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        object=cur.execute('SELECT object FROM tests WHERE id=?',(test,)).fetchone()[0]
        topics=cur.execute('SELECT id,name FROM topics WHERE object=?',(object,)).fetchall()
        result={}
        for topic in topics:
            types=cur.execute('SELECT id,name FROM types WHERE topic=?',(topic[0],)).fetchall()
            qtypes={}
            for type in types:
                questions=cur.execute('SELECT id,text,answer,img FROM questions WHERE type=?',(type[0],)).fetchall()
                qtypes[type]=questions
            result[topic]=qtypes
        conn.commit()
        return result
    def delqint(self,test,idq):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions=cur.execute('SELECT questions FROM tests WHERE id=?',(test,)).fetchone()[0]
        questions=questions.split(',')
        questions.remove(idq)
        cur.execute('UPDATE tests SET questions=? WHERE id=?',(','.join(questions),test))
        conn.commit()
    def listid(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        ids=cur.execute('SELECT questions FROM tests WHERE id=?',(id,)).fetchone()[0]
        ids=[int(i) for i in ids.split(',')]
        conn.commit()
        return ids
#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ДОМАШНЕЕ ЗАДАНИЕ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#   
    def newhomework(self,name,object,types):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions={}
        for t in types:
            if types[t]!='0':
                question=cur.execute('SELECT id FROM questions WHERE type=?',(t,)).fetchall()
                if question==None: continue
                questions[int(t)]=int(types[t]) if int(types[t])<=len(question) else len(question)
        questions=str(questions).replace(' ','').replace('{','').replace('}','')
        idhm=generator().newid('homework')
        cur.execute('INSERT INTO homework VALUES(?,?,?,?,?)',(idhm,object,name,questions,'Неактивен'))
        conn.commit()
    def listhomework(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        result={}
        objects=cur.execute('SELECT id,name FROM objects').fetchall()
        for t in objects:
            tests=list(cur.execute('SELECT id,name FROM homework WHERE object=?',(t[0],)).fetchall())
            result[t]=tests
        conn.commit()
        return result
    def listqinhm(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        question=cur.execute('SELECT qtypes FROM homework WHERE id=?',(id,)).fetchone()[0]
        if len(question)>0:
            q=[]
            for i in question.split(","):
                try:
                    t,n=i.split(':')
                except:
                    continue
                topic=self.nametopic(cur.execute('SELECT topic FROM types WHERE id=?',(t,)).fetchone()[0])
                t=cur.execute('SELECT id,name FROM types WHERE id=?',(t,)).fetchone()
                q.append((topic[1],t,n))
        else:
            q=None
        conn.commit()
        return q
    def updatehm(self,homework,types):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        typesnow=cur.execute('SELECT qtypes FROM homework WHERE id=?',(homework,)).fetchone()
        typesnow=dict([i.split(':') for i in typesnow[0].split(',')]) if len(typesnow)>0 else {}
        result={}
        for i in types:
            result[int(i)]=int(typesnow[i]) if i in typesnow else 0
        result=str(result).replace(' ','').replace('{','').replace('}','')
        cur.execute('UPDATE homework SET qtypes=? WHERE id=?',(result,homework))
        conn.commit()
    def updatedig(self,homework,types):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        questions={}
        for t in types:
            if types[t]!='0':
                question=cur.execute('SELECT id FROM questions WHERE type=?',(t,)).fetchall()
                if question==None: continue
                questions[int(t)]=int(types[t]) if int(types[t])<=len(question) else len(question)
        questions=str(questions).replace(' ','').replace('{','').replace('}','')
        cur.execute('UPDATE homework SET qtypes=? WHERE id=?',(questions,homework))
        conn.commit()
    def delhomework(self,homework):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM homework WHERE id=?',(homework,))
        conn.commit()
    def getactivehm(self,homework):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        active=cur.execute('SELECT active FROM homework WHERE id=?',(homework,)).fetchone()[0]
        conn.commit()
        return active
    def upactivehm(self,test,active):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE homework SET active=? WHERE id=?',(active,test))
        conn.commit()
    def namehomework(self,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT id,name FROM homework WHERE id=?',(id,)).fetchone()
        conn.commit()
        return name
    def listtypeforhm(self,test):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        object=cur.execute('SELECT object FROM homework WHERE id=?',(test,)).fetchone()
        types=self.listtt(object[0])
        conn.commit()
        return types
    def deltypeinhm(self,test,id):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        qtypes=cur.execute('SELECT qtypes FROM homework WHERE id=?',(test,)).fetchone()[0]
        qtypes=re.sub(f'{id}:\w','',qtypes)
        if qtypes[-1]==',': qtypes=qtypes[:-1]
        elif qtypes[0]==',': qtypes=qtypes[1:]
        print(qtypes)
        cur.execute('UPDATE homework SET qtypes=? WHERE id=?',(qtypes,test))
        conn.commit()

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ЗАПИСИ"""""""""""""""""""""""""""""""""""""""""""""""""""""""# 
    def newrecord(self,idg,date,name,text):
        if idg.isdigit()==False:
            return 'Пожалуйста, выберите группу'
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        idr=generator().newid('records')
        cur.execute('INSERT INTO records VALUES(?,?,?,?,?)',(idr,idg,date,name,text))
        conn.commit()
        return 'Готово!'
    def listrecords(self,idg):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        records=cur.execute('SELECT id,date,name,text FROM records WHERE idgroup=? ORDER BY date',(idg,)).fetchall()
        conn.commit()
        return records
    def namegroup(self,idg):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        name=cur.execute('SELECT id,name FROM groups WHERE id=?',(idg,)).fetchone()
        conn.commit()
        return name
    def delrecord(self,idr):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        idg=cur.execute('SELECT idgroup FROM records WHERE id=?',(idr,)).fetchone()[0]
        name=cur.execute('SELECT id,name FROM groups WHERE id=?',(idg,)).fetchone()
        cur.execute('DELETE FROM records WHERE id=?',(idr,))
        conn.commit()
        return name
    def updaterecord(self,idr,date,name,text):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE records SET date=?,name=?,text=? WHERE id=?',(date,name,text,idr))
        idg=cur.execute('SELECT idgroup FROM records WHERE id=?',(idr,)).fetchone()[0]
        name=cur.execute('SELECT id,name FROM groups WHERE id=?',(idg,)).fetchone()
        conn.commit()
        return name

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ПРЕДМЕТЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
    def listobjects(self):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        objects=cur.execute('SELECT * FROM objects ORDER BY id').fetchall()
        conn.commit()
        return objects
    def newobject(self,name):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        objects=cur.execute('SELECT name FROM objects')
        if (name,) not in objects:
            idobject=generator().newid('objects')
            cur.execute('INSERT INTO objects VALUES(?,?,?)',(idobject,name,0))
        conn.commit()
    def delobject(self,idobject):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('DELETE FROM objects WHERE id=?',(idobject,))
        topics=cur.execute('SELECT id FROM topics WHERE object=?',(idobject,)).fetchall()
        topics=[str(i[0]) for i in topics]
        cur.execute(f'DELETE FROM types WHERE topic IN ({",".join(topics)})')
        cur.execute('DELETE FROM questions WHERE object=?',(idobject,))
        cur.execute('DELETE FROM topics WHERE object=?',(idobject,))
        cur.execute('DELETE FROM tests WHERE object=?',(idobject,))
        cur.execute('DELETE FROM homework WHERE object=?',(idobject,))
        conn.commit()
    def updateobject(self,idobject,newname):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE objects SET name=? WHERE id=?',(newname,idobject))
        conn.commit()








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