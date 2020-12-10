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


def convert_ratingsum_data(rating_sum):
    rating_sum = int(rating_sum)
    if(rating_sum < 1000):
        return 1
    elif(rating_sum < 5000):
        return 2
    elif(rating_sum < 30000):
        return 3
    elif (rating_sum < 100000):
        return 4
    elif(rating_sum < 250000):
        return 5
    else:
        return 6


# TODO:remove first column
def one_hot_encode(index_num_list, total_num):

    one_hot_list = [0] * (total_num + 1)  # index start from 1

    for index in index_num_list:
        one_hot_list[index] = 1

    return one_hot_list


def dict_data_generator_slash(dataString, dict_cache, data_index):

    if(dataString == ""):
        return []

    reList = []
    temp_places = dataString.split("/")

    for temp_place in temp_places:
        if temp_place in dict_cache:
            reList.append(dict_cache[temp_place])
        else:
            dict_cache[temp_place] = data_index[0]
            data_index[0] += 1
            reList.append(dict_cache[temp_place])

    return reList


def dict_data_generator_comma(dataString, dict_cache, data_index):

    if(len(dataString) < 3):  # TODO:cound have better judge option
        return []
    else:
        dataString = dataString[1:-1]  # remove leading '[' and ending ']'

    reList = []
    temp_places = dataString.split(",")

    for temp_place in temp_places:
        if temp_place in dict_cache:
            reList.append(dict_cache[temp_place])
        else:
            dict_cache[temp_place] = data_index[0]
            data_index[0] += 1
            reList.append(dict_cache[temp_place])

    return reList


# FIXME:archived
# def rm_brackets(raw_str):
#     if(len(raw)<=2):
#         return ""
#     else:
#         return raw_str[1:-1]


def gcn_data_movie_write(node, clayer, flayer, added_node, added_node_info, added_slug_pair,
                         country_dict_cache, country_dict_index,
                         category_dict_cache, category_dict_index,
                         tags_dict_cache, tags_dict_index):

    node_info = node.get_gcn_node_info()

    if(node_info[0] not in added_node):
        added_node_info.append([
            node_info[0],
            dict_data_generator_slash(
                node_info[1], country_dict_cache, country_dict_index),  # country info
            node_info[2],  # year info
            dict_data_generator_slash(
                node_info[3], category_dict_cache, category_dict_index),  # categroy info
            dict_data_generator_comma(
                node_info[4], tags_dict_cache, tags_dict_index),  # tags info
            convert_ratingsum_data(node_info[5]),   # rating_sum info
        ])

        added_node.append(node_info[0])
    else:
        return

    if(clayer >= flayer):  # 超过递归深度直接返回
        return

    rships = node.get_relationship()
    rships = list(rships)
    random.shuffle(rships)

    # TODO
    # the num of node extended from each node is not fixed

    upper_branch_limit = 2  # random.randint(1, 3)
    branch_limit = 2  # random.randint(1, 4)

    for rship in rships[:upper_branch_limit]:
        try:
            relationship_with_movie = rship.get_people().get_relationship()
            relationship_with_movie = list(relationship_with_movie)
            random.shuffle(relationship_with_movie)

            for rship_mv in relationship_with_movie[:branch_limit]:
                try:
                    related_movie = rship_mv.get_movie()
                    related_movie_info = related_movie.get_gcn_node_info()

                    temp_slug_pair = [node_info[0], related_movie_info[0]]
                    temp_slug_pair.sort()
                except Exception:
                    continue

                if(temp_slug_pair not in added_slug_pair):
                    added_slug_pair.append(temp_slug_pair)
                else:
                    pass
                gcn_data_movie_write(
                    related_movie, clayer + 1, flayer, added_node, added_node_info, added_slug_pair,
                    country_dict_cache, country_dict_index,
                    category_dict_cache, category_dict_index,
                    tags_dict_cache, tags_dict_index
                )
        except Exception:
            continue


def check_vailed_node(node_to_check):
    for info_item in node_to_check:
        if(not info_item):
            return False
    return True


def gcn_data_movie(request, slug):
    layer = 5
    current_layer = 0
    root_movie = Item.objects.get(slug=slug)

    added_node = []
    added_slug_pair = []
    added_node_info = []

    country_dict_cache = {}
    country_dict_index = [1]

    category_dict_cache = {}
    category_dict_index = [1]

    tags_dict_cache = {}
    tags_dict_index = [1]

    gcn_data_movie_write(
        root_movie, current_layer, layer, added_node, added_node_info, added_slug_pair,
        country_dict_cache, country_dict_index,
        category_dict_cache, category_dict_index,
        tags_dict_cache, tags_dict_index
    )

    # remove refered nodes that not in partial network
    slug_pair_to_del = []
    for slug_pair in added_slug_pair:
        if((slug_pair[0] not in added_node) or (slug_pair[1] not in added_node)):
            slug_pair_to_del.append(slug_pair)
    new_added_slug_pair = []
    for slug_pair in added_slug_pair:
        if(slug_pair not in slug_pair_to_del):
            new_added_slug_pair.append(slug_pair)
    added_slug_pair = new_added_slug_pair

    node_to_del = []
    new_added_slug_pair = []
    new_added_node_info = []

    for i in added_node_info:
        # TODO filter invailed node
        if(not check_vailed_node(i)):
            node_to_del.append(i[0])
        else:
            new_added_node_info.append(i)

    for i in added_slug_pair:
        if(i[0] in node_to_del or i[1] in node_to_del):
            pass
        else:
            new_added_slug_pair.append(i)  # filter slug pair again

    new_added_node_info.sort()
    new_added_slug_pair.sort()
    added_node_info = new_added_node_info
    added_slug_pair = new_added_slug_pair

    # convert to onehot coding and write to file
    country_num = len(country_dict_cache)
    category_num = len(category_dict_cache)
    tags_num = len(tags_dict_cache)

    with open('./static_in_env/gcn_data/movie_info.txt', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in added_node_info:
            writer.writerow(
                [i[0]] +
                one_hot_encode(i[1], country_num) +
                [i[2]] +
                one_hot_encode(i[3], category_num) +
                one_hot_encode(i[4], tags_num) +
                [i[5]]
            )

    temp_slug_length = len(added_slug_pair)
    for i in range(temp_slug_length):
        temp_list_element = added_slug_pair[i]
        added_slug_pair.append([temp_list_element[1], temp_list_element[0]])

    added_slug_pair.sort()
    with open('./static_in_env/gcn_data/movie_net.txt', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in added_slug_pair:
            writer.writerow(i)

    messages.info(request, "movie gcn data generate successfully")
    return redirect('core:home')  # to be changed
