from django.shortcuts import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse


#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ВХОД"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def enter(request):                                                                                                             
    if request.method=='GET':                                                                                       
        return render(request,'homepage/enter.html')
    else:
        login=request.POST['login']
        password=request.POST['password']
        access=models2().enter(login,password) #модель входа
        if access!=False:
            return redirect(f'select/?id={access}&hello')
        else:
            return render(request,'homepage/enter.html')

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГЛАВНАЯ СТРАНИЦА"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def select(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'name':models2().nickname(request.GET['id']), 
                'hello':('hello' in request.GET),
                'listgroups':models2().listgroups(),
            }
            if models2().access(request.GET['id']): #проверка сессии
                return render(request,'homepage/select.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/500/')
    else:
        if 'quit' in request.POST:
            models2().quit(request.POST['id']) #выход
            return redirect('/')

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ТЕСТЫ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def tests(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'name':models2().nickname(request.GET['id']), 
                'listtests':models2().listtests(),
            }
            if models2().access(request.GET['id']): #проверка сессии
                return render(request,'homepage/tests.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/500/')
    else:
        pass

def test(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'method':'start',
                'test':models2().getinfo(request.GET['test'],'tests'),
                'name':models2().nickname(request.GET['id']), 
                'continue':models2().continuetest(request.GET['id'],request.GET['test']),
            }
            if models2().access(request.GET['id']): #проверка сессии
                return render(request,'homepage/test.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/500/')
    else:
        user=int(request.POST['id'])
        test=int(request.POST['test'])
        method='next'
        question=''
        result=''
        if 'start' in request.POST or 'continue' in request.POST:
            flag='continue' in request.POST
            questions=models2().starttest(user,test,flag)
            if questions[0]=='end':
                method='end'
        else:
            questions=request.POST['questions'].split(',')
        ids=questions[-1]
        if 'endtest' in request.POST:
            models2().endtest(ids,'test')
            return redirect(f'/tests/?id={user}')
        elif 'next' in request.POST:
            idq=request.POST['idq']
            questions.insert(-2,idq)
        elif 'btn' in request.POST or (('end' in request.POST or questions[0]=='end') and 'answer' in request.POST and request.POST['answer']!=''):
            idq=request.POST['idq']
            models2().answertest(ids,idq,request.POST['answer'],'test')
        if 'end' in request.POST or questions[0]=='end':
            result=models2().resulttest(ids,'test')
            method='end'
        else:
            question=models2().question(questions[0])
            del questions[0]
        context={
            'result':result,
            'question':question,
            'questions':','.join(questions),
            'method':method,
            'id':request.POST['id'],
            'test':models2().getinfo(request.POST['test'],'tests'),
            'name':models2().nickname(request.POST['id']), 
        }
        return render(request,'homepage/test.html',context)

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ДОМАШНЕЕ ЗАДАНИЕ"""""""""""""""""""""""""""""""""""""""""""""""""""""""# 
def homeworks(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'name':models2().nickname(request.GET['id']), 
                'listtests':models2().listhomeworks(),
            }
            if models2().access(request.GET['id']): #проверка сессии
                return render(request,'homepage/homeworks.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/500/')
    else:
        pass

def homework(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'method':'start',
                'test':models2().getinfo(request.GET['test'],'homework'),
                'name':models2().nickname(request.GET['id']), 
                'continue':models2().continuehm(request.GET['id'],request.GET['test']),
            }
            if models2().access(request.GET['id']): #проверка сессии
                return render(request,'homepage/homework.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/500/')
    else:
        user=int(request.POST['id'])
        test=int(request.POST['test'])
        method='next'
        question=''
        result=''
        if 'start' in request.POST or 'continue' in request.POST:
            flag='continue' in request.POST
            questions=models2().starthomework(user,test,flag)
            if questions[0]=='end':
                method='end'
        else:
            questions=request.POST['questions'].split(',')
        ids=questions[-1]
        if 'endtest' in request.POST:
            models2().endtest(ids,'homework')
            return redirect(f'/homeworks/?id={user}')
        elif 'next' in request.POST:
            idq=request.POST['idq']
            questions.insert(-2,idq)
        elif 'btn' in request.POST or (('end' in request.POST or questions[0]=='end') and 'answer' in request.POST and request.POST['answer']!=''):
            idq=request.POST['idq']
            models2().answertest(ids,idq,request.POST['answer'],'homework')
        if 'end' in request.POST or questions[0]=='end':
            result=models2().resulttest(ids,'homework')
            method='end'
        else:
            question=models2().question(questions[0])
            del questions[0]
        context={
            'result':result,
            'question':question,
            'questions':','.join(questions),
            'method':method,
            'id':request.POST['id'],
            'test':models2().getinfo(request.POST['test'],'homework'),
            'name':models2().nickname(request.POST['id']), 
        }
        return render(request,'homepage/homework.html',context)

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""ГРУППЫ И ЗАПИСИ"""""""""""""""""""""""""""""""""""""""""""""""""""""""#
def klass(request):
    if request.method=='GET':
        try:
            context={
                'id':request.GET['id'],
                'listrecords':models2().listrecords(request.GET['klass']),
                'group':models2().namegroup(request.GET['klass']),
                'name':models2().nickname(request.GET['id']), 
            }
            if models2().access(request.GET['id']): #проверка сессии
                return render(request,'homepage/klass.html',context)
            else:
                return redirect('/403/')
        except:
            return redirect('/500/')
    else:
        pass