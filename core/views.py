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


def get_similar_rate(rate_str):
    try:
        rate_num = int(rate_str)
        if(rate_num < 20):
            rate_num = random.randint(3, 20)
        elif(rate_num > 80):
            rate_num = random.randint(80, 98)
        return rate_num
    except Exception:
        return random.randint(20, 80)


area_view_deepest_layer = 10


# TODO make branch num more robust

def recurse_write_queue_people_area(node, clayer, flayer, outfile, added_node):

    rate = get_similar_rate(node.get_node_info()[2][-4:-2])

    temp_rate = round(rate * random.uniform(0.8, 1.2))

    rate1 = get_similar_rate(temp_rate)

    temp_rate = round(rate * random.uniform(0.8, 1.2))

    rate2 = get_similar_rate(temp_rate)

    if(clayer > 0):
        outfile.writerow(
            [clayer, node.get_node_info()[0], node.get_node_info()[1], node.get_node_info()[2], rate, rate1, rate2])

    if(clayer >= flayer):
        return

    rships = node.get_relationship()

    rships = list(rships)
    random.shuffle(rships)

    leaf_num = 1

    if(clayer == 0):
        leaf_num = 24

    add_num = 0

    for rship in rships:
        if(add_num < leaf_num):
            if(clayer % 2 == 0):
                temp_node = rship.get_movie()
            else:
                temp_node = rship.get_people()

            if(temp_node.get_node_info()[0] in added_node):
                continue
            else:
                added_node.append(temp_node.get_node_info()[0])

            recurse_write_queue_people_area(
                temp_node, clayer + 1, flayer, outfile, added_node)
            add_num += 1
        else:
            break


def relationship_area_view_people(request, slug):
    layer = area_view_deepest_layer
    current_layer = 0
    root_people = PeopleItem.objects.get(slug=slug)

    # id_list = [1]
    added_node = []

    with open('./static_in_env/csv/relationship_area_view_people.csv', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['layer', 'name',
                         'img_url', 'url', 'rate', 'rate1', 'rate2'])

        added_node.append(root_people.get_node_info()[0])

        recurse_write_queue_people_area(
            root_people, current_layer, layer, writer, added_node)

        context = {
            'item': root_people
        }

    return render(request, 'relationship_area_view_people.html', context=context)


# TODO:
# random shuffle(✔)
# random number(✔)
# text link(✔)
# expected value of leaf number(✔)
# image ratate(✔)


def one_hot_encode(index_num, total_num):
    one_hot_list = [0] * index_num + [1] + [0] * (total_num - index_num)
    return one_hot_list


def convert_people_sex(people_sex):
    if(people_sex == "男"):
        return 1
    if(people_sex == "女"):
        return 2

    return 0


def convert_people_birthday(people_birthday):
    if "/" in people_birthday:
        year = people_birthday.split("/")[0]
        year = int(year)
        # dacade = year//10-190
        # return dacade
        return (2020-year)//10

    else:
        return 0


# TODO
# birthplace_dict_index = 1
# birthplace_dict_cache = {}


def convert_people_birthplace(people_birthplace, birthplace_dict_cache, birthplace_dict_index):

    # TODO
    # if("," in people_birthplace):
    #     temp_place = people_birthplace.split(",")[1]
    #     if temp_place in birthplace_dict_cache:
    #         return birthplace_dict_cache[temp_place] % 20-10
    #     else:
    #         birthplace_dict_cache[temp_place] = birthplace_dict_index[0]
    #         birthplace_dict_index[0] += 1
    #         return birthplace_dict_cache[temp_place] % 20-10
    # else:
    #     return 0

    if("," in people_birthplace):
        temp_place = people_birthplace.split(",")[1]
        if temp_place in birthplace_dict_cache:
            return birthplace_dict_cache[temp_place]
        else:
            birthplace_dict_cache[temp_place] = birthplace_dict_index[0]
            birthplace_dict_index[0] += 1
            return birthplace_dict_cache[temp_place]
    else:
        return 0


# def gcn_data_people_write(node, id, pid, clayer, flayer, outfile, added_node):
def gcn_data_people_write(node, clayer, flayer, added_node, added_node_info, added_slug_pair, birthplace_dict_cache, birthplace_dict_index):
    node_info = node.get_gcn_node_info()
    if(node_info[0] not in added_node):
        # write info to add_node_info
        # added_node_info.append(node_info)
        added_node_info.append([node_info[0], convert_people_birthplace(
            node_info[2], birthplace_dict_cache, birthplace_dict_index), convert_people_sex(node_info[1]), convert_people_birthday(node_info[3])])
        added_node.append(node_info[0])
    else:
        return

    if(clayer >= flayer):  # 超过递归深度直接返回
        return

    rships = node.get_relationship()
    rships = list(rships)

    # TODO
    random.shuffle(rships)

    # TODO
    # branch_limit
    upper_branch_limit = random.randint(1, 3)  # random.randint(1, 5)

    # TODO
    # branch_limit = int(random.randint(1, 30)/100 * len(rships))  # 随机选取1%---->20%的数量
    branch_limit = random.randint(1, 4)  # random.randint(1, 5)

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


def gcn_data_people(request, slug):
    layer = 9
    current_layer = 0
    root_people = PeopleItem.objects.get(slug=slug)

    # id_list = [1]

    added_node = []
    added_slug_pair = []
    added_node_info = []

    # added_node.append(root_people.get_gcn_node_info()[0])  # 加入根节点ID
    # TODO
    # add root node info

    birthplace_dict_cache = {}

    birthplace_dict_index = [1]

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


deepest_layer = 5


def recurse_write_queue_people(node, id, pid, clayer, flayer, outfile, added_node):

    if(pid is None):
        outfile.writerow([str(id[0]), "", node.get_node_info()
                          [0][:5], node.get_node_info()[1], node.get_node_info()[2]])
    else:
        outfile.writerow([str(id[0]), str(pid), node.get_node_info()[
                         0][:5], node.get_node_info()[1], node.get_node_info()[2]])

    if(clayer > flayer):
        return

    origin_id = id[0]
    id[0] += 1
    rships = node.get_relationship()

    add_num = 0

    leaf_num = flayer-clayer

    if(clayer != 0 and flayer-clayer > 1):
        leaf_num += random.randint(-leaf_num+1, leaf_num-1)

    rships = list(rships)

    random.shuffle(rships)

    for rship in rships:
        if(add_num < leaf_num):
            if(clayer % 2 == 0):
                # write movie
                temp_node = rship.get_movie()
            else:
                temp_node = rship.get_people()

            if(temp_node.get_node_info()[0] in added_node):
                continue
            else:
                added_node.append(temp_node.get_node_info()[0])

            recurse_write_queue_people(
                temp_node, id, origin_id, clayer + 1, flayer, outfile, added_node)
            id[0] += 1
            add_num += 1
        else:
            break


def recurse_write_queue_movie(node, id, pid, clayer, flayer, outfile, added_node):

    # added_node.append(node.get_node_info()[0])
    if(pid is None):
        outfile.writerow([str(id[0]), "", node.get_node_info()
                          [0][:5], node.get_node_info()[1], node.get_node_info()[2]])
    else:
        outfile.writerow([str(id[0]), str(pid), node.get_node_info()[
                         0][:5], node.get_node_info()[1], node.get_node_info()[2]])

    if(clayer > flayer):
        return

    origin_id = id[0]
    id[0] += 1
    rships = node.get_relationship()

    add_num = 0

    leaf_num = flayer-clayer

    if(clayer != 0 and flayer-clayer > 1):
        leaf_num += random.randint(-leaf_num+1, leaf_num-1)

    rships = list(rships)

    random.shuffle(rships)

    for rship in rships:
        if(add_num < leaf_num):
            if(clayer % 2 == 1):
                # write movie
                temp_node = rship.get_movie()
            else:
                temp_node = rship.get_people()

            if(temp_node.get_node_info()[0] in added_node):
                continue
            else:
                added_node.append(temp_node.get_node_info()[0])

            recurse_write_queue_movie(
                temp_node, id, origin_id, clayer + 1, flayer, outfile, added_node)
            id[0] += 1
            add_num += 1
        else:
            break


def relationship_view_people(request, slug):
    layer = deepest_layer
    current_layer = 0
    root_people = PeopleItem.objects.get(slug=slug)

    id_list = [1]

    added_node = []

    with open('./static_in_env/csv/relationship_view_people.csv', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['id', 'parentId', 'name',
                         'description', 'url'])

        added_node.append(root_people.get_node_info()[0])
        recurse_write_queue_people(
            root_people, id_list, None, current_layer, layer, writer, added_node)
        context = {
            'item': root_people
        }
        return render(request, "relationship_view_people.html", context)


def relationship_view_movie(request, slug):
    layer = deepest_layer
    current_layer = 0
    root_people = Item.objects.get(slug=slug)
    id_list = [1]
    added_node = []
    with open('./static_in_env/csv/relationship_view_movie.csv', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['id', 'parentId', 'name',
                         'description', 'url'])

        added_node.append(root_people.get_node_info()[0])
        recurse_write_queue_movie(
            root_people, id_list, None, current_layer, layer, writer, added_node)

        context = {
            'item': root_people
        }
        return render(request, "relationship_view_movie.html", context)


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def movie_year_view_1(request):

    return render(request, "movie_year_view_people.html")


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = Item
    paginate_by = 20
    template_name = "home.html"


class PeopleView(ListView):
    model = PeopleItem
    paginate_by = 20
    template_name = "people.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            bookmark = Bookmark.objects.get(user=self.request.user)

            # if(bookmark.exists() is False):
            #     messages.warning(self.request, "您还未收藏任何电影")
            #     return redirect("/")

            context = {
                'object': bookmark
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "您还未收藏任何电影")
            return redirect(self.request.META.get('HTTP_REFERER', '/'))


@login_required
def follow_list(request):
    try:
        followlist = FollowList.objects.get(
            user=request.user)

        context = {
            'object': followlist
        }
        return render(request, 'follow_list.html', context)
    except ObjectDoesNotExist:
        messages.warning(request, "您还未关注任何影人")
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

    # def get(self, *args, **kwargs):
    #     form = RefundForm()
    #     context = {
    #         'object': model
    #     }
    #     return render(self.request, "product.html", context)


class PeopleItemDetailView(DetailView):
    model = PeopleItem
    template_name = "people_detail.html"


@login_required
def add_comment(request, slug):
    if(request.POST.get("anonymous")):
        new_comment = Comments.objects.create(user="匿名用户",
                                              content=request.POST.get(
                                                  "content"),
                                              movie_slug=request.POST.get("slug"))
    else:
        new_comment = Comments.objects.create(user=request.user,
                                              content=request.POST.get(
                                                  "content"),
                                              movie_slug=request.POST.get("slug"))
    return redirect("core:movie", slug=slug)


@login_required
def add_to_bookmark(request, slug):
    item = get_object_or_404(Item, slug=slug)
    bookmark_item, created = BookmarkItem.objects.get_or_create(
        item=item,
        user=request.user
    )

    bookmark_qs = Bookmark.objects.filter(user=request.user)

    if bookmark_qs.exists():
        bookmark = bookmark_qs[0]
        # check if the order item is in the order
        if bookmark.items.filter(item__slug=item.slug).exists():
            # order_item.quantity += 1
            # order_item.save()
            messages.info(request, "该电影已在收藏夹中")
            return redirect("core:movie", slug=slug)

        else:
            bookmark.items.add(bookmark_item)
            messages.info(request, "收藏成功")
            return redirect("core:movie", slug=slug)
    else:
        # ordered_date = timezone.now()
        bookmark = Bookmark.objects.create(
            user=request.user)  # , ordered_date=ordered_date)
        bookmark.items.add(bookmark_item)
        messages.info(request, "收藏成功")
        return redirect("core:movie", slug=slug)


@login_required
def remove_from_bookmark(request, slug):
    item = get_object_or_404(Item, slug=slug)
    bookmark_qs = Bookmark.objects.filter(
        user=request.user
    )
    if bookmark_qs.exists():
        bookmark = bookmark_qs[0]
        # check if the order item is in the order
        if bookmark.items.filter(item__slug=item.slug).exists():
            bookmark_item = BookmarkItem.objects.filter(
                item=item,
                user=request.user,
            )[0]

            bookmark.items.remove(bookmark_item)
            bookmark_item.delete()

            if(bookmark.items.count() == 0):
                bookmark.delete()

            messages.info(request, "已移出收藏夹")
            return redirect("core:movie", slug=slug)
        else:
            messages.info(request, "您未收藏该电影")
            return redirect("core:movie", slug=slug)
    else:
        messages.info(request, "您未收藏该电影")
        return redirect("core:movie", slug=slug)


@login_required
def remove_from_bookmark_sp(request, slug):
    item = get_object_or_404(Item, slug=slug)
    bookmark_qs = Bookmark.objects.filter(
        user=request.user
    )
    if bookmark_qs.exists():
        bookmark = bookmark_qs[0]
        # check if the order item is in the order
        if bookmark.items.filter(item__slug=item.slug).exists():
            bookmark_item = BookmarkItem.objects.filter(
                item=item,
                user=request.user,
            )[0]

            bookmark.items.remove(bookmark_item)
            bookmark_item.delete()

            if(bookmark.items.count() == 0):
                bookmark.delete()
                return redirect("/")

            messages.info(request, "已移出收藏夹")
            return redirect("core:order-summary")
        else:
            messages.info(request, "您未收藏该电影")
            return redirect("core:order-summary")
    else:
        messages.info(request, "您未收藏该电影")
        return redirect("core:order-summary")


@login_required
def follow_people(request, slug):
    item = get_object_or_404(PeopleItem, slug=slug)
    follow_item, created = FollowItem.objects.get_or_create(
        PeopleItem=item,
        user=request.user
    )

    followList_qs = FollowList.objects.filter(user=request.user)

    if followList_qs.exists():
        followList = followList_qs[0]
        # check if the order item is in the order
        if followList.items.filter(PeopleItem__slug=item.slug).exists():
            messages.info(request, "您已关注过该影人")
            return redirect("core:people-detail", slug=slug)

        else:
            followList.items.add(follow_item)
            messages.info(request, "关注成功")
            return redirect("core:people-detail", slug=slug)
    else:
        followList = FollowList.objects.create(user=request.user)
        followList.items.add(follow_item)
        messages.info(request, "关注成功")
        return redirect("core:people-detail", slug=slug)


@login_required
def unfollow_people(request, slug):
    item = get_object_or_404(PeopleItem, slug=slug)
    followList_qs = FollowList.objects.filter(
        user=request.user
    )
    if followList_qs.exists():
        followList = followList_qs[0]
        if followList.items.filter(PeopleItem__slug=item.slug).exists():
            follow_item = FollowItem.objects.filter(
                PeopleItem=item,
                user=request.user,
            )[0]

            followList.items.remove(follow_item)
            follow_item.delete()

            if(followList.items.count() == 0):
                followList.delete()

            messages.info(request, "成功取消关注")
            return redirect("core:people-detail", slug=slug)
        else:
            messages.info(request, "您未关注该影人")
            return redirect("core:people-detail", slug=slug)
    else:
        messages.info(request, "您未关注该影人")
        return redirect("core:people-detail", slug=slug)


@login_required
def unfollow_people_sp(request, slug):
    item = get_object_or_404(PeopleItem, slug=slug)
    followList_qs = FollowList.objects.filter(
        user=request.user
    )
    if followList_qs.exists():
        followList = followList_qs[0]
        if followList.items.filter(PeopleItem__slug=item.slug).exists():
            follow_item = FollowItem.objects.filter(
                PeopleItem=item,
                user=request.user,
            )[0]

            followList.items.remove(follow_item)
            follow_item.delete()

            if(followList.items.count() == 0):
                followList.delete()
                return redirect("/people")

            messages.info(request, "成功取消关注")
            return redirect("core:follow-list")
        else:
            messages.info(request, "您未关注该影人")
            return redirect("core:follow-list")
    else:
        messages.info(request, "您未关注该影人")
        return redirect("core:follow-list")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")
