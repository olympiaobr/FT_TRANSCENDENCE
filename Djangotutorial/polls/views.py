from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def detail(request, question_id):
    return HttpResponse("You are looking at question nr. %s."% question_id)

def results(request, question_id):
    return HttpResponse("You are looking at the results of Question nr. %s" % question_id)

def vote(request, question_id):
    return HttpResponse ("you are voting on question nr. %s." %question_id)