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


def one_hot_encode(index_num_list, total_num):

    one_hot_list = [0] * (total_num + 1)  # index start from zero

    for index in index_num_list:
        one_hot_list[index] = 1

    return one_hot_encode


def dict_data_generator_slash(dataString, dict_cache, data_index):
    reList = []
    temp_places = dataString.split("/")

    for temp_place in temp_places:
        if temp_place in dict_cache:
            reList.append(dict_cache[temp_place])
        else:
            dict_cache[temp_place] = data_index[0]
            data_index[0] += 1
            return dict_cache[temp_place]
            reList.append(dict_cache[temp_place])


def dict_data_generator_comma(dataString, dict_cache, birthplace_dict_index):
    reList = []
    temp_places = dataString.split(",")

    for temp_place in temp_places:
        if temp_place in dict_cache:
            reList.append(dict_cache[temp_place])
        else:
            dict_cache[temp_place] = data_index[0]
            data_index[0] += 1
            return dict_cache[temp_place]
            reList.append(dict_cache[temp_place])


def gcn_data_people_write(node, clayer, flayer, added_node, added_node_info, added_slug_pair, birthplace_dict_cache, birthplace_dict_index):
    node_info = node.get_gcn_node_info()
    if(node_info[0] not in added_node):
        added_node_info.append([
            node_info[0],
            convert_people_birthplace(
                node_info[2], birthplace_dict_cache, birthplace_dict_index),
            convert_people_sex(node_info[1]),
            convert_people_birthday(node_info[3])
        ])

        added_node.append(node_info[0])
    else:
        return

    if(clayer >= flayer):  # 超过递归深度直接返回
        return

    rships = node.get_relationship()
    rships = list(rships)

    random.shuffle(rships)
    upper_branch_limit = random.randint(1, 3)
    branch_limit = random.randint(1, 4)

    for rship in rships[:upper_branch_limit]:

        try:
            relationship_with_people = rship.get_movie().get_relationship()
            relationship_with_people = list(relationship_with_people)
            random.shuffle(relationship_with_people)

            for rship_pp in relationship_with_people[:branch_limit]:
                try:
                    related_people = rship_pp.get_people()
                    related_people_info = related_people.get_gcn_node_info()

                    temp_slug_pair = [node_info[0], related_people_info[0]]
                    temp_slug_pair.sort()
                except Exception:
                    continue

                if(temp_slug_pair not in added_slug_pair):
                    added_slug_pair.append(temp_slug_pair)
                else:
                    pass

                # if(related_people_info[0] in added_node):
                #     continue
                gcn_data_people_write(
                    related_people, clayer + 1, flayer, added_node, added_node_info, added_slug_pair, birthplace_dict_cache, birthplace_dict_index)
        except Exception:
            continue


def gcn_data_movie(request, slug):
    layer = 2
    current_layer = 0
    root_people = Item.objects.get(slug=slug)

    added_node = []
    added_slug_pair = []
    added_node_info = []

    country_dict_cache = {}
    country_dict_index = [1]

    category_dict_cache = {}
    category_dict_index = [1]

    tags_dict_cache = {}
    tags_dict_index = [1]

    gcn_data_people_write(
        root_people, current_layer, layer, added_node, added_node_info, added_slug_pair, birthplace_dict_cache, birthplace_dict_index)

    # TODO
    # with open('./static_in_env/gcn_data/people_net.txt', 'w', newline='', encoding='utf-8') as outfile:
    #     writer = csv.writer(outfile, delimiter='/t',
    #                         quotechar='"', quoting=csv.QUOTE_MINIMAL)

    #     # writer.writerow(['slug','sex', 'birthplace','birthday'])

    # TODO:filter node with invailed birthday info
    # TODO:filter invalid slug pair

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
        if(i[3] == 0 or i[2] == 0 or i[1] == 0):
            node_to_del.append(i[0])
        else:
            new_added_node_info.append(i)

    for i in added_slug_pair:
        if(i[0] in node_to_del or i[1] in node_to_del):
            pass
        else:
            new_added_slug_pair.append(i)

    new_added_node_info.sort()
    new_added_slug_pair.sort()

    added_node_info = new_added_node_info
    added_slug_pair = new_added_slug_pair

    # TODO add one hot endoe
    birthplace_num = len(birthplace_dict_cache)
    with open('./static_in_env/gcn_data/people_info.txt', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in added_node_info:
            writer.writerow([i[0]] + one_hot_encode(i[1],
                                                    birthplace_num) + [i[2]] + [i[3]])
        # writer.writerow(['slug','sex', 'birthplace','birthday'])

    temp_slug_length = len(added_slug_pair)
    for i in range(temp_slug_length):
        temp_list_element = added_slug_pair[i]
        added_slug_pair.append([temp_list_element[1], temp_list_element[0]])

    added_slug_pair.sort()

    with open('./static_in_env/gcn_data/people_net.txt', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in added_slug_pair:
            writer.writerow(i)

        # writer.writerow(['slug','sex', 'birthplace','birthday'])

    # TODO:delete place dict cache
    birthplace_dict_cache = {}

    messages.info(request, "gcn data generate successfully")
    return redirect('core:home')
