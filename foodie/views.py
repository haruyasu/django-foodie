from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Pref, Category, Review
from .forms import SearchForm, ReviewForm
from django.db.models import Avg
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import requests

# API に渡すパラメータの値の指定
GNAVI_URL = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
GNAVI_KEY = "e69b765feb7e3902bdc22e281874aa97"

class IndexView(TemplateView):
    template_name = 'foodie/index.html'

    def get_context_data(self, *args, **kwargs):
        searchform = SearchForm()

        # おすすめレストラン
        category_l = "RSFST09000" # 居酒屋
        pref = "PREF13" # 東京都
        freeword = "歓送迎会"
        num = 6

        query = get_gnavi_data(
            "",
            category_l,
            pref,
            freeword,
            num
        )

        result = gnavi_api(query)
        pickup_restaurant = get_restaurant_info(result)

        params = {
            'searchform': searchform,
            'pickup_restaurant': pickup_restaurant,
            }
        return params


def Search(request):
    if request.method == 'GET':
        searchform = SearchForm(request.POST)

        if searchform.is_valid():
            category_l = request.GET['category_l']
            pref = request.GET['pref']
            freeword = request.GET['freeword']
            num = 50
            lunch = request.GET['lunch']
            no_smoking = request.GET['no_smoking']
            card = request.GET['card']
            mobilephone = request.GET['mobilephone']
            bottomless_cup = request.GET['bottomless_cup']
            sunday_open = request.GET['sunday_open']
            takeout = request.GET['takeout']
            private_room = request.GET['private_room']
            midnight = request.GET['midnight']
            parking = request.GET['parking']
            memorial_service = request.GET['memorial_service']
            birthday_privilege = request.GET['birthday_privilege']
            betrothal_present = request.GET['betrothal_present']
            kids_menu = request.GET['kids_menu']
            outret = request.GET['outret']
            wifi = request.GET['wifi']
            microphone = request.GET['microphone']
            buffet = request.GET['buffet']
            late_lunch = request.GET['late_lunch']
            sports = request.GET['sports']
            until_morning = request.GET['until_morning']
            lunch_desert = request.GET['lunch_desert']
            projecter_screen = request.GET['projecter_screen']
            with_pet = request.GET['with_pet']
            deliverly = request.GET['deliverly']
            special_holiday_lunch = request.GET['special_holiday_lunch']
            e_money = request.GET['e_money']
            caterling = request.GET['caterling']
            breakfast = request.GET['breakfast']
            desert_buffet = request.GET['desert_buffet']
            lunch_buffet = request.GET['lunch_buffet']
            bento = request.GET['bento']
            lunch_salad_buffet = request.GET['lunch_salad_buffet']
            darts = request.GET['darts']
            web_reserve = request.GET['web_reserve']
            query = get_gnavi_data(
                "",
                category_l,
                pref,
                freeword,
                num,
                lunch,
                no_smoking,
                card,
                mobilephone,
                bottomless_cup,
                sunday_open,
                takeout,
                private_room,
                midnight,
                parking,
                memorial_service,
                birthday_privilege,
                betrothal_present,
                kids_menu,
                outret,
                wifi,
                microphone,
                buffet,
                late_lunch,
                sports,
                until_morning,
                lunch_desert,
                projecter_screen,
                with_pet,
                deliverly,
                special_holiday_lunch,
                e_money,
                caterling,
                breakfast,
                desert_buffet,
                lunch_buffet,
                bento,
                lunch_salad_buffet,
                darts,
                web_reserve
            )
            result = gnavi_api(query)
            total_hit_count = len(result)
            restaurant_list = get_restaurant_info(result)
            page_obj = paginate_queryset(request, restaurant_list, 10)

        context = {
            'total_hit_count': total_hit_count,
            'restaurant_list': page_obj.object_list,
            'page_obj': page_obj,
        }

        return render(request, 'foodie/search.html', context)


def ShopInfo(request, restid):
    query = get_gnavi_data(
        restid,
        "",
        "",
        "",
        1
    )
    result = gnavi_api(query)
    restaurants_info = get_restaurant_info(result)

    if request.method == 'GET':
        review_count = Review.objects.filter(shop_id=restid).count()
        score_ave = Review.objects.filter(shop_id=restid).aggregate(Avg('score'))
        average = score_ave['score__avg']
        if average:
            average_rate = average / 5 * 100
        else:
            average_rate = 0
        review_form = ReviewForm()
        review_list = Review.objects.filter(shop_id=restid)

        params = {
            'review_count': review_count,
            'restaurants_info': restaurants_info,
            'review_form': review_form,
            'review_list': review_list,
            'average': average,
            'average_rate': average_rate,
        }
        return render(request, 'foodie/shop_info.html', params)
    else:
        form = ReviewForm(data=request.POST)

        if form.is_valid():
            review = Review()
            review.shop_id = restid
            review.shop_name = restaurants_info[0][2]
            review.user = request.user
            review.score = request.POST['score']
            review.comment = request.POST['comment']
            is_exist = Review.objects.filter(shop_id = review.shop_id).filter(user = review.user).count()
            
            if is_exist:
                messages.error(request, 'レビューを投稿済みです')
            else:
                review.save()
                messages.success(request, 'レビューを投稿しました')
        else:
            messages.error(request, 'エラーがあります')

        return redirect('shop_info', restid)


def gnavi_api(params):
    result = []
    result_api = requests.get(GNAVI_URL, params).text
    result_json = json.loads(result_api)
    if "error" not in result_json:
        result.extend(result_json["rest"])
    return result


def paginate_queryset(request, queryset, count):
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def get_gnavi_data(
        id,
        category_l,
        pref,
        freeword,
        hit_per_page,
        lunch='0',
        no_smoking='0',
        card='0',
        mobilephone='0',
        bottomless_cup='0',
        sunday_open='0',
        takeout='0',
        private_room='0',
        midnight='0',
        parking='0',
        memorial_service='0',
        birthday_privilege='0',
        betrothal_present='0',
        kids_menu='0',
        outret='0',
        wifi='0',
        microphone='0',
        buffet='0',
        late_lunch='0',
        sports='0',
        until_morning='0',
        lunch_desert='0',
        projecter_screen='0',
        with_pet='0',
        deliverly='0',
        special_holiday_lunch='0',
        e_money='0',
        caterling='0',
        breakfast='0',
        desert_buffet='0',
        lunch_buffet='0',
        bento='0',
        lunch_salad_buffet='0',
        darts='0',
        web_reserve='0'
    ):
    query = {
        "keyid": GNAVI_KEY,
        "id": id,
        "pref": pref,
        "category_l": category_l,
        "freeword": freeword,
        "hit_per_page": hit_per_page,
        "lunch": lunch,
        "no_smoking": no_smoking,
        "card": card,
        "mobilephone": mobilephone,
        "bottomless_cup": bottomless_cup,
        "sunday_open": sunday_open,
        "takeout": takeout,
        "private_room": private_room,
        "midnight": midnight,
        "parking": parking,
        "memorial_service": memorial_service,
        "birthday_privilege": birthday_privilege,
        "betrothal_present": betrothal_present,
        "kids_menu": kids_menu,
        "outret": outret,
        "wifi": wifi,
        "microphone": microphone,
        "buffet": buffet,
        "late_lunch": late_lunch,
        "sports": sports,
        "until_morning": until_morning,
        "lunch_desert": lunch_desert,
        "projecter_screen": projecter_screen,
        "with_pet": with_pet,
        "deliverly": deliverly,
        "special_holiday_lunch": special_holiday_lunch,
        "e_money": e_money,
        "caterling": caterling,
        "breakfast": breakfast,
        "desert_buffet": desert_buffet,
        "lunch_buffet": lunch_buffet,
        "bento": bento,
        "lunch_salad_buffet": lunch_salad_buffet,
        "darts": darts,
        "web_reserve": web_reserve
    }
    query = {k: v for (k, v) in query.items() if v != '0' and v != ''}

    return query


def get_restaurant_info(restaurants):
    restaurant_list = []
    for restaurant in restaurants:
        id = restaurant["id"]
        update_date = restaurant["update_date"]
        name = restaurant["name"]
        name_kana = restaurant["name_kana"]
        latitude = restaurant["latitude"]
        longitude = restaurant["longitude"]
        category = restaurant["category"]
        url = restaurant["url"]
        url_mobile = restaurant["url_mobile"]
        coupon_url_pc = restaurant["coupon_url"]["pc"]
        coupon_url_mobile = restaurant["coupon_url"]["mobile"]
        shop_image1 = restaurant["image_url"]["shop_image1"]
        shop_image2 = restaurant["image_url"]["shop_image2"]
        qrcode = restaurant["image_url"]["qrcode"]
        address = restaurant["address"]
        tel = restaurant["tel"]
        tel_sub = restaurant["tel_sub"]
        fax = restaurant["fax"]
        opentime = restaurant["opentime"]
        holiday = restaurant["holiday"]
        line = restaurant["access"]["line"]
        station = restaurant["access"]["station"]
        station_exit = restaurant["access"]["station_exit"]
        walk = restaurant["access"]["walk"]
        note = restaurant["access"]["note"]
        parking_lots = restaurant["parking_lots"]
        pr_short = restaurant["pr"]["pr_short"]
        pr_long = restaurant["pr"]["pr_long"]
        areaname = restaurant["code"]["areaname"]
        prefname = restaurant["code"]["prefname"]
        areaname_s = restaurant["code"]["areaname_s"]
        category_name_l = " | ".join(filter(lambda a: a != '', restaurant["code"]["category_name_l"]))
        category_name_s = " | ".join(filter(lambda a: a != '', restaurant["code"]["category_name_s"]))
        budget = restaurant["budget"]
        party = restaurant["party"]
        lunch = restaurant["lunch"]
        credit_card = restaurant["credit_card"]
        e_money = restaurant["e_money"]

        restaurant_list.append([
            id, # 0
            update_date, # 1
            name, # 2
            name_kana, # 3
            latitude, # 4
            longitude, # 5
            category, # 6
            url, # 7
            url_mobile, # 8
            coupon_url_pc, # 9
            coupon_url_mobile, # 10
            shop_image1, # 11
            shop_image2, # 12
            qrcode, # 13
            address, # 14
            tel, # 15
            tel_sub, # 16
            fax, # 17
            opentime, # 18
            holiday, # 19
            line, # 20
            station, # 21
            station_exit, # 22
            walk, # 23
            note, # 24
            parking_lots, # 25
            pr_short, # 26
            pr_long, # 27
            areaname, # 28
            prefname, # 29
            areaname_s, # 30
            category_name_l, # 31
            category_name_s, # 32
            budget, # 33
            party, # 34
            lunch, # 35
            credit_card, # 36
            e_money # 37
        ])
    return restaurant_list
