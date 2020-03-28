from django.views.generic import TemplateView

# API に渡すパラメータの値の指定
GNAVI_URL = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
GNAVI_KEY = "e69b765feb7e3902bdc22e281874aa97"

class IndexView(TemplateView):
    template_name = 'foodie/index.html'
