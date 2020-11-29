import json
import random
import string

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import *

import csv

stripe.api_key = settings.STRIPE_SECRET_KEY


def marked_item_net_view(request):
    data = {}
    link_list = []
    people_list = []
    movie_list = []  # json object prepare

    bookmark = Bookmark.objects.filter(user=request.user)[0]
    all_marked_movie = bookmark.items.all()
    for movie_item in all_marked_movie:
        loc_info = movie_item.item.get_node_info_sp()
        movie_list.append({
            "id": loc_info[0],
            "name": loc_info[1],
            "img_url": loc_info[2],
            "type": "location"
        })

    followList = FollowList.objects.filter(user=request.user)[0]
    all_marked_people = followList.items.all()
    for people_item in all_marked_people:
        cha_info = people_item.PeopleItem.get_node_info_sp()
        people_list.append({
            "id": cha_info[0],
            "name": cha_info[1],
            "img_url": cha_info[2],
            "type": "character"
        })

    for people in people_list:
        for movie in movie_list:
            people_slug = people["id"]
            movie_slug = movie["id"]

            rsItem = MoviePeopleRelationship.objects.filter(
                movie_slug=movie_slug,
                people_slug=people_slug
            )

            if(rsItem.exists()):
                link_list.append({
                    "source": "c_"+people_slug,
                    "target": "l_"+movie_slug
                })

    for i in movie_list:
        i["id"] = "l_"+i["id"]

    for i in people_list:
        i["id"] = "c_"+i["id"]

    data["links"] = link_list
    data["characters"] = people_list
    data["locations"] = movie_list  # finish json

    with open('./static_in_env/visualization_data/graph.json', 'w') as outfile:
        # write json to file
        json.dump(data, outfile, indent=2)  # , ensure_ascii=False)

    return render(request, "marked_item_net_view.html")
