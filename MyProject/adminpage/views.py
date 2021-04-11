from django.shortcuts import render,redirect
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse


#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ВХОД"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def enter(request):                                                                                                             
    if request.method=='GET':                                                                                       
        return render(request,'admin/enter.html')
    else:
        login=request.POST['login']
        password=request.POST['password']
        access=models().enter(login,password) #модель входа
        if access!=False:
            return redirect(f'select/?id={access}&hello')
        else:
            return render(request,'admin/enter.html',context={'k':access})

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГЛАВНАЯ СТРАНИЦА"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def select(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'name':models().nickname(request.GET['id']), 
                'hello':('hello' in request.GET),
            }
            if models().access(request.GET['id']): #проверка сессии
                return render(request,'admin/select.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/404/')
    else:
        if 'quit' in request.POST:
            models().quit(request.POST['id']) #выход
            return redirect('/admin/')

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ПОЛЬЗОВАТЕЛИ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def users(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'name':models().nickname(request.GET['id']),
                'listusers':models().listusers(), #список пользователей
                'search':'',
            }
            if models().access(request.GET['id']):
                return render(request,'admin/users.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/404/')
    else:
        if 'new' in request.POST or 'newmany' in request.POST: #новый(ые) пользователи
            users=request.POST['users'].split('\r\n')
            status=request.POST['status']
            models().newusers(users,status) #модель добавления пользователей
        elif 'del' in request.POST:
            userid=request.POST['iduser']
            models().deluser(userid) #модель удаления пользователей
        elif 'up' in request.POST:
            userid=request.POST['iduser']
            name=request.POST['name']
            login=request.POST['login']
            password=request.POST['password']
            models().updateuser(userid,name,login,password) #можель изменения данных пользователей
        listusers=models().listusers()
        req=''
        if 'search' in request.POST:
            req=request.POST['search']
            listusers=models().searchusers(req)
        context={
            'search':req,
            'open':str('newmany' in request.POST),
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listusers':listusers,
        }
        return render(request,'admin/users.html',context)

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГРУППЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def groups(request):
    if request.method=='GET':
        try:
            context={
                'creator':models().nickname(request.GET['id']),
                'id':request.GET['id'],
                'name':models().nickname(request.GET['id']),
                'listgroups':models().listgroups(),
                'group':('-','Выберите группу'),
                'listusersing':'',
            }
            if models().access(request.GET['id']):
                return render(request,'admin/groups.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/404/')
    else:
        creator=models().nickname(request.POST['id'])
        group=('-','Выберите группу')
        listusersing=''
        if 'newg' in request.POST:
            creator=request.POST['creator']
            users=request.POST['users'].replace(',','').split('\r\n')
            namegroup=request.POST['namegroup']
            img=request.FILES['img'] if len(request.FILES)!=0 else None
            models().newgroup(namegroup,creator,users,img)
        else:
            if 'newus' in request.POST:
                models().newusing(request.POST['user'],request.POST['group'])
            elif 'delus' in request.POST:
                models().delusing(request.POST['user'],request.POST['group'])
            if 'delg' in request.POST:
                models().delgroup(request.POST['group'])
            else:
                group=models().namegroup(request.POST['group'])
                listusersing=models().listusersing(request.POST['group'])
        context={
            'group':group,
            'listusersing':listusersing,
            'open':str('newg' in request.POST),
            'creator':creator,
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listgroups':models().listgroups(),
        }
        return render(request,'admin/groups.html',context)  

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ПРЕДМЕТЫ,ТЕМЫ И ТИПЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def tt(request):
    if request.method=='GET':
       
            context={
                'id':request.GET['id'],
                'name':models().nickname(request.GET['id']),
                'topic':('-','Тема'),
                'object':('-','Предмет'),
                'list':models().listobandt(),
                'listobjects':models().listobjects(),
            }
            if models().access(request.GET['id']):
                return render(request,'admin/tt.html',context)
            else:
                return redirect('/403/')
        
            return redirect('/404/')
    else:
        opentopic='True' if 'object' in request.POST else 'False'
        openobject='False'
        opentype='True' if 'topic' in request.POST else 'False'
        object=models().nameobject(request.POST['object']) if 'object' in request.POST else ('-','Предмет')
        topic=models().nametopic(request.POST['topic']) if 'topic' in request.POST else ('-','Тема')
        if 'newobject' in request.POST:
            models().newobject(request.POST['name'])
            openobject='True'
        elif 'delobject' in request.POST:
            models().delobject(request.POST['idobject'])
            openobject='True'
            object=('-','Предмет')
        elif 'upobject' in request.POST:
            models().updateobject(request.POST['idobject'],request.POST['name'])
            openobject='True'
        elif 'newtopic' in request.POST:
            models().newtopic(request.POST['name'],object[0])
        elif 'deltopic' in request.POST:
            models().deltopic(request.POST['idtopic'],object[0])
        elif 'uptopic' in request.POST:
            models().updatetopic(request.POST['idtopic'],request.POST['name'])
        elif 'newtype' in request.POST:
            models().newtype(request.POST['name'],topic[0])
        elif 'deltype' in request.POST:
            models().deltype(request.POST['idtype'],topic[0])
        elif 'uptype' in request.POST:
            models().updatetype(request.POST['idtype'],request.POST['name'])
        context={
            'topic':topic,
            'object':object,
            'openobject':openobject,
            'opentopic':opentopic,
            'opentype':opentype,
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listtopic':models().listtopic(object[0]),
            'listtypes':models().listtype(topic[0]),
            'list':models().listobandt(),
            'listobjects':models().listobjects(),
            }
        return render(request,'admin/tt.html',context)

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ВОПРОСЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def questions(request):
    if request.method=='GET':
        #try:
            context={
                'id':request.GET['id'],
                'object':('-','Предмет'),
                'opt':'off',
                'opq':'off',
                'name':models().nickname(request.GET['id']),
                'listquestions':models().listquestions(),
                'listobjects':models().listobjects(),
            }
            if models().access(request.GET['id']):
                return render(request,'admin/questions.html',context)
            else:
                return redirect('/403/')
       # except:
            return redirect('/404/')
    else:
        search=request.POST['search'] if 'search' in request.POST else None
        object=models().nameobject(request.POST['object']) if 'object' in request.POST and request.POST['object'][0]!='-' else ('-','Предмет')
        listtt=models().listtt(request.POST['object'][0]) if 'object' in request.POST else ''
        opq=request.POST['opq'] if 'opq' in request.POST else 'off'
        opt=request.POST['opt'] if 'opt' in request.POST else 'off'
        type=models().nametype(request.POST['type']) if 'type' in request.POST   else ('-','Тип')
        if 'new' in request.POST:
            text=request.POST['text']
            answer=request.POST['answer']
            img=request.FILES['img'] if len(request.FILES)!=0 else None
            models().newquestion(object[0],type[0],text,answer,img)
        elif 'del' in request.POST:
            idq=request.POST['idq']
            models().delquestion(idq)
        elif 'up' in request.POST:
            idq=request.POST['idq']
            text=request.POST['text']
            answer=request.POST['answer']
            img=request.FILES['img'] if len(request.FILES)!=0 else None
            delimg=request.POST['delimg'] if 'delimg' in request.POST else None
            models().updatequestion(idq,text,answer,delimg,img)
        context={
            'search':search,
            'type':type,
            'listtt':listtt,
            'object':object,
            'opq':opq,
            'opt':opt,
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listobjects':models().listobjects(),
            'listquestions':models().listquestions(search),
        }
        return render(request,'admin/questions.html',context)

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ТЕСТЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def tests(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'name':models().nickname(request.GET['id']),
                'listobjects':models().listobjects(),
                'object':('-','Предмет'),
                'objectlist':('-','Предмет'),
                'test':'-',
                'listtests':models().listtests(),
            }
            if models().access(request.GET['id']):
                return render(request,'admin/tests.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/404/')
    else:
        object=models().nameobject(request.POST['object']) if 'object' in request.POST else ('-','Предмет')
        models().upactive(request.POST['test'],request.POST['active']) if 'active' in request.POST else None
        opennew=('object' in request.POST) 
        openlist=('test' in request.POST)
        test=models().nametest(request.POST['test']) if 'test' in request.POST else '-'
        listtt=models().listtt(request.POST['object']) if 'object' in request.POST else ''
        if 'new' in request.POST:
            types=request.POST.getlist('types[]')
            dig=request.POST.getlist('dig[]')
            dicttypes=dict(zip(types,dig))
            name=request.POST['name']
            models().newtest(name,object[0],dicttypes)
        if 'update' in request.POST:
            ids=request.POST.getlist('idq[]')
            models().updatetest(request.POST['test'],ids)
        if 'delq' in request.POST:
            idq=request.POST['idq']
            models().delqint(request.POST['test'],idq)
        testinfo=models().listqint(request.POST['test']) if 'test' in request.POST else ''
        active=models().getactive(request.POST['test']) if 'test' in request.POST else ''
        listquestions=models().listquestionsfortest(request.POST['test']) if 'test' in request.POST else ''
        if 'deltest' in request.POST:
            models().deltest(request.POST['test'])
            test='-'
        context={
            'listid':models().listid(test[0]),
            'listquestions':listquestions,
            'active':active,
            'testinfo':testinfo,
            'openlist':openlist,
            'opennew':opennew,
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listobjects':models().listobjects(),
            'object':object,
            'listtt':listtt,
            'test':test,
            'listtests':models().listtests(),
        }
        return render(request,'admin/tests.html',context)

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ДОМАШНЕЕ ЗАДАНИЕ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def homework(request):
    if request.method=='GET':
        #try:
            context={
                'id':request.GET['id'],
                'name':models().nickname(request.GET['id']),
                'listobjects':models().listobjects(),
                'object':('-','Предмет'),
                'objectlist':('-','Предмет'),
                'test':'-',
                'listhomework':models().listhomework(),
            }
            if models().access(request.GET['id']):
                return render(request,'admin/homework.html',context)
            else:
                return redirect('/403/')
        #except:
            return redirect('/404/')
    else:
        object=models().nameobject(request.POST['object']) if 'object' in request.POST else ('-','Предмет')
        models().upactivehm(request.POST['test'],request.POST['active']) if 'active' in request.POST else None
        opennew=('object' in request.POST) 
        openlist=('test' in request.POST)
        test=models().namehomework(request.POST['test']) if 'test' in request.POST else '-'
        listtt=models().listtt(request.POST['object']) if 'object' in request.POST else ''
        if 'new' in request.POST:
            types=request.POST.getlist('types[]')
            dig=request.POST.getlist('dig[]')
            dicttypes=dict(zip(types,dig))
            name=request.POST['name']
            models().newhomework(name,object[0],dicttypes)
        if 'update' in request.POST:
            types=request.POST.getlist('nums[]')
            models().updatehm(request.POST['test'],types)
        if 'updatehm' in request.POST:
            types=request.POST.getlist('types[]')
            dig=request.POST.getlist('dig[]')
            dicttypes=dict(zip(types,dig))
            models().updatedig(request.POST['test'],dicttypes)
        if 'deltype' in request.POST:
            models().deltypeinhm(request.POST['test'],request.POST['deltype'])
        testinfo=models().listqinhm(request.POST['test']) if 'test' in request.POST else ''
        ids=[i[1] for i in testinfo] if testinfo!=None else None
        active=models().getactivehm(request.POST['test']) if 'test' in request.POST else ''
        listtypes=models().listtypeforhm(request.POST['test']) if 'test' in request.POST else ''
        if 'deltest' in request.POST:
            models().delhomework(request.POST['test'])
            test='-'
        context={
            'listids':ids,
            'listtypes':listtypes,
            'active':active,
            'testinfo':testinfo,
            'openlist':openlist,
            'opennew':opennew,
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listobjects':models().listobjects(),
            'object':object,
            'listtt':listtt,
            'test':test,
            'listhomework':models().listhomework(),
        }
        return render(request,'admin/homework.html',context)
def writing(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'group':('','Выберте группу'),
                'name':models().nickname(request.GET['id']),
                'listgroups':models().listgroups(),
            }
            if models().access(request.GET['id']):
                return render(request,'admin/writing.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/404/')
    else:
        serveranswer=''
        listrecords=''
        if 'new' in request.POST:
            group=request.POST['group']
            date=request.POST['date']
            name=request.POST['name']
            text=request.POST['text']
            serveranswer=models().newrecord(group,date,name,text)
            group=models().namegroup(request.POST['group'])
        elif 'del' in request.POST:
            idr=request.POST['idr']
            group=models().delrecord(idr)
        elif 'up' in request.POST:
            idr=request.POST['idr']
            date=request.POST['date']
            name=request.POST['name']
            text=request.POST['text']
            group=models().updaterecord(idr,date,name,text)
        else:
            group=models().namegroup(request.POST['group'])
        listrecords=models().listrecords(group[0])
        context={
            'listrecords':listrecords,
            'serveranswer':serveranswer,
            'group':group,
            'id':request.POST['id'],
            'name':models().nickname(request.POST['id']),
            'listgroups':models().listgroups(),
        }
        return render(request,'admin/writing.html',context)