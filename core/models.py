from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
import os
import requests

from add_on.SentimentPolarityAnalysis.spa.classifiers import DictClassifier


# TODO: add image cache

# url = 'https://img1.doubanio.com/view/celebrity/s_ratio_celebrity/public/p33988.webp'
# r2 = requests.get(url)
# with open('tupian'+'.jpg', 'wb+') as f:  # 循环写入图片
#     f.write(r2.content)


CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)  # 电影名字
    rating = models.FloatField()  # 电影评分
    img_url = models.CharField(max_length=100, null=True)  # 电影图片
    country = models.CharField(
        max_length=30, default="Unknown", null=True)  # 电影国家
    year = models.CharField(
        max_length=10, default="Unknown", null=True)  # 电影年份

    rating_sum = models.CharField(max_length=20, default="NULL")  # 评分人数

    description = models.TextField(null=True)  # 电影概述
    tags = models.CharField(max_length=100, default="NULL")  # 电影名字
    category = models.CharField(max_length=50, default="NULL")  # 电影类别
    slug = models.SlugField()  # 唯一标识符

    # TODO to be refactored
    def comrate(self, str_to_check):
        ds = DictClassifier()
        result = ds.analyse_sentence(str_to_check)
        return result

    def get_treeview_url(self):
        return f"/relationship_view_movie/{self.slug}"

    def get_node_info(self):
        name = f'{self.title}'
        sex = self.get_img_url()
        url = self.get_absolute_url()
        return [name, sex, url]

    def get_gcn_node_info(self):
        slug = f'{self.slug}'
        country = f'{self.country}'
        year = f'{self.year}'
        category = f'{self.category}'
        tags = f'{self.tags}'
        rating_sum = f'{self.rating_sum}'

        return [slug, country, year, category, tags, rating_sum]

    def get_comments(self):
        comments = Comments.objects.filter(movie_slug=self.slug)
        return comments

    def get_country_label(self):
        return "primary"  # 国家标签颜色

    def get_year_label(self):
        return "secondary"  # 年份标签颜色

    # discount_price = models.FloatField(blank=True, null=True)
    # category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    # label = models.CharField(choices=LABEL_CHOICES, max_length=1)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:movie", kwargs={
            'slug': self.slug
        })

    def get_add_to_bookmark_url(self):
        return reverse("core:add-to-bookmark", kwargs={
            'slug': self.slug
        })

    def get_remove_from_bookmark_url(self):
        return reverse("core:remove-from-bookmark", kwargs={
            'slug': self.slug
        })

    def get_remove_from_bookmark_url_sp(self):
        return reverse("core:remove-from-bookmark-sp", kwargs={
            'slug': self.slug
        })

    def get_relationship(self):
        return MoviePeopleRelationship.objects.filter(movie_slug=self.slug)

    # return true label
    def get_img_url(self):
        # img_url = f"{self.img_url}"
        # img_name = img_url.split('/')[-1]
        # # urllib.request.urlretrieve(img_url, "./static_in_env/img/"+img_name)
        # # return "/static/img/"+img_name
        # r2 = requests.get(img_url)
        # with open("./static_in_env/img/"+img_name, 'wb+') as f:
        #     f.write(r2.content)
        # return "/static/img/"+img_name
        return f"{self.img_url}"


class PeopleItem(models.Model):
    name = models.CharField(max_length=30)  # 影人名字
    img_url = models.CharField(max_length=200, null=True)  # 影人图片

    sex = models.CharField(
        max_length=10, default="Unknown", null=True)  # 影人性别

    birthplace = models.CharField(
        max_length=30, default="Unknown", null=True)  # 影人出生地

    birthday = models.CharField(
        max_length=30, default="Unknown", null=True)  # 影人出生日期

    description = models.TextField(null=True)  # 电影概述

    slug = models.SlugField()  # 唯一标识符

    def get_treeview_url(self):
        return f"/relationship_view_people/{self.slug}"

    def get_node_info(self):
        name = f'{self.name}'
        sex = self.get_img_url()
        url = self.get_absolute_url()

        return [name, sex, url]

    def get_gcn_node_info(self):
        slug = f'{self.slug}'
        sex = f'{self.sex}'
        birthplace = f'{self.birthplace}'
        birthpday = f'{self.birthday}'

        return [slug, sex, birthplace, birthpday]

    def get_country(self):
        raw_str = f'{self.birthplace}'
        country = raw_str.split(',')[0]
        return country

    def get_year_label(self):
        return "secondary"  # 年份标签颜色

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:people-detail", kwargs={
            'slug': self.slug
        })

    # def get_short_des(self):
    #     if(self.description)

    def get_follow_people_url(self):
        return reverse("core:follow-people", kwargs={
            'slug': self.slug
        })

    def get_unfollow_people_url(self):
        return reverse("core:unfollow-people", kwargs={
            'slug': self.slug
        })

    def get_unfollow_people_url_sp(self):
        return reverse("core:unfollow-people-sp", kwargs={
            'slug': self.slug
        })

    def get_relationship(self):
        return MoviePeopleRelationship.objects.filter(people_slug=self.slug)

    def get_img_url(self):
        # img_url = f"{self.img_url}"
        # img_name = img_url.split('/')[-1]
        # # urllib.request.urlretrieve(img_url, "./static_in_env/img/"+img_name)
        # # return "/static/img/"+img_name
        # r2 = requests.get(img_url)
        # with open("./static_in_env/img/"+img_name, 'wb+') as f:
        #     f.write(r2.content)
        # return "/static/img/"+img_name
        return f"{self.img_url}"


class Comments(models.Model):
    user = models.CharField(max_length=20)  # 用户姓名
    content = models.CharField(max_length=300)  # 用户姓名
    movie_slug = models.CharField(max_length=100)  # 关联电影

    def __str__(self):
        return f"{self.user}"


class BookmarkItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item.title} of {self.user}"


class FollowItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    PeopleItem = models.ForeignKey(PeopleItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.PeopleItem.name} of {self.user}"


class FollowList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    items = models.ManyToManyField(FollowItem)


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    items = models.ManyToManyField(BookmarkItem)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    # def get_total(self):
    #     total = 0
    #     for order_item in self.items.all():
    #         total += order_item.get_final_price()
    #     if self.coupon:
    #         total -= self.coupon.amount
    #     return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class MoviePeopleRelationship(models.Model):
    movie_slug = models.CharField(max_length=100)  # 唯一标识符
    people_slug = models.CharField(max_length=100)  # 唯一标识符
    role = models.CharField(max_length=20)

    def get_people(self):
        return PeopleItem.objects.get(slug=self.people_slug)

    def get_movie(self):
        return Item.objects.get(slug=self.movie_slug)


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
