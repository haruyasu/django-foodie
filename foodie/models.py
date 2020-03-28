from django.db import models


class Category(models.Model):
    category_l = models.CharField("大業態コード", max_length=10, blank=False)
    name = models.CharField("カテゴリ名", max_length=30, blank=False)

    def __str__(self):
        return str(self.name)


class Pref(models.Model):
    pref = models.CharField("都道府県コード", max_length=6, blank=False)
    name = models.CharField("都道府県名", max_length=10, blank=False)

    def __str__(self):
        return str(self.name)
