from django.http import JsonResponse
from django.shortcuts import render
from .forms import UserForm, UserProfileInfoForm
from .models import Sell, UserProfileInfo, Notify, Sold
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from matplotlib import pyplot as plt
from django.conf import settings
import os
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SellForm
import urllib.request
import urllib.parse
from django.contrib.auth.models import User
from .models import UserProfileInfo
import pandas as pd
import numpy as np
import operator
@login_required
def special(request):
    return HttpResponse("You are logged in !")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True
            return HttpResponseRedirect('/user/login/')
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'signup.html',{
                                            'user_form':user_form,
                                            'profile_form':profile_form,
                                            'registered':registered
                                        })


def dashboard(request):

    if request.method == 'GET' and 'notID' in request.GET:
        nid = request.GET.get('notID')
        # retVal = ""
        one_task = Sell.objects.get(add_id=nid)
        if one_task:
            print('task =' ,one_task)

            one_task.delete()  # line 1
            #two_task = Sell.objects.get(id=nid)

            # print(retVal)
            return JsonResponse({
                'id':"Advertisement is deleted."
            })

    if request.method == 'GET' and 'notificationID' in request.GET:
        nid = request.GET.get('notificationID')
        # retVal = ""
        one_task = Notify.objects.get(notify_id=nid)
        if one_task:
            print('task =' ,one_task)

            one_task.delete()  # line 1
            #two_task = Sell.objects.get(id=nid)

            # print(retVal)
            return JsonResponse({
                'id':"Notifiaction is deleted."
            })
    if request.method == 'GET' and 'soldNID' in request.GET:
        nid = request.GET.get('soldNID')
        # retVal = ""
        one_task = Notify.objects.get(notify_id=nid)
        if one_task:
            sellRow = Sell.objects.get(add_id=one_task.add_id_id)

            soldModel = Sold()
            soldModel.title = sellRow.title
            soldModel.price = sellRow.price
            soldModel.save()

            sellRow.delete()
            # print(retVal)
            return JsonResponse({
                'id':"BOOK SOLD !"
            })

    notifications = Notify.objects.filter(seller_id_id=request.user.id)

    notificationList=[]

    for e in notifications:
        pair = {
            'notId': e.notify_id,
            'date': e.datetime,
            'buyer': User.objects.get(id=e.buyer_id_id),
            'prodName':Sell.objects.get(add_id = e.add_id_id)
        }
        notificationList.append(pair)

# ------------------------------------------------------- Advertisements List

    advt = Sell.objects.filter(user_id_id=request.user.id)
    advtList=[]

    for e in advt:
        pair = {
            'notId': e.add_id,
            'date': e.datetime,
            'author': e.author,
            'title':e.title

        }
        advtList.append(pair)

    context = {'pair':notificationList,'advt':advtList}

    return render(request, 'dash.html', context)



class CreatePostView(CreateView): # new
    model = Sell
    form_class = SellForm
    template_name = 'sell2.html'
    success_url = reverse_lazy('home')
    print("Inside Class")

    def form_valid(self, form):
        form.instance.user_id = self.request.user
       # print("Inside Def")
        super().form_valid(form)
        return HttpResponseRedirect('/user/dashboard')



def BuyView(request):
    datalist= []
    if request.method == 'POST' and 'searchForm' in request.POST:
        booknm = request.POST.get('q')
        # gender = request.POST.get('list')
        # print(gender, "-----------------------------------------------")
        datalist = []
        for e in Sell.objects.filter(title__icontains=booknm):
            if e:
                context = {
                    'price':e.price,
                    'title':e.title,
                    'auth':e.author,
                    'descp':e.description,
                    'img':e.bookImage,
                    'add_id': e.add_id
                }
                datalist.append(context)
        return render(request, 'registration/buy.html', {'data':datalist})

    if request.method == 'POST' and 'sortForm' in request.POST:
        sortParam = request.POST.get('list')
        datalist = []
        if sortParam == "az":
            for e in Sell.objects.order_by('title'):
                if e:
                    context = {
                        'price':e.price,
                        'title':e.title,
                        'auth':e.author,
                        'descp':e.description,
                        'img':e.bookImage,
                        'add_id': e.add_id
                    }
                    datalist.append(context)
        elif sortParam == "za":
            for e in Sell.objects.order_by('-title'):
                if e:
                    context = {
                        'price':e.price,
                        'title':e.title,
                        'auth':e.author,
                        'descp':e.description,
                        'img':e.bookImage,
                        'add_id': e.add_id
                    }
                    datalist.append(context)
        elif sortParam == "aPrice":
            for e in Sell.objects.order_by('price'):
                if e:
                    context = {
                        'price':e.price,
                        'title':e.title,
                        'auth':e.author,
                        'descp':e.description,
                        'img':e.bookImage,
                        'add_id': e.add_id
                    }
                    datalist.append(context)
        elif sortParam == "dPrice":
            for e in Sell.objects.order_by('-price'):
                if e:
                    context = {
                        'price':e.price,
                        'title':e.title,
                        'auth':e.author,
                        'descp':e.description,
                        'img':e.bookImage,
                        'add_id': e.add_id
                    }
                    datalist.append(context)


        return render(request, 'registration/buy.html', {'data':datalist})

    if request.method == 'GET':
        id = request.GET.get('id')
        if id:
            buyerid = request.GET.get('user_id')
            prod_data = Sell.objects.get(add_id=id)
            buyer_data = User.objects.get(id=buyerid)
            buyer_data_phone = UserProfileInfo.objects.get(user_id=buyerid)
            seller_data = UserProfileInfo.objects.get(user_id=prod_data.user_id_id)

            print(buyer_data.username)



            #ADDING DATA INTO NOTIFICATION TABLE
            notifyModel = Notify()
            notifyModel.add_id_id =prod_data.add_id
            notifyModel.seller_id_id=seller_data.user_id
            notifyModel.buyer_id_id=buyer_data.id
            notifyModel.save()

            if id:
                return JsonResponse({
                                     'id': prod_data.price
                                     })
            return render(request, 'buy.html', )
        else:

            #Default Sort A - Z
            for e in Sell.objects.order_by('title'):
                if e:
                    context = {
                        'price': e.price,
                        'title': e.title,
                        'auth': e.author,
                        'descp': e.description,
                        'img': e.bookImage,
                        'add_id':e.add_id
                    }
                    datalist.append(context)
            return render(request, 'registration/buy.html', {'data': datalist})

  #  return render(request, 'registration/buy.html', {})




