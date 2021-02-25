from django.shortcuts import render
from django.conf import settings
from accounts.models import CatalogItem, SponsorCatalogItem, CatalogItemImage, SponsorCompany, UserInformation
from catalog.serializers import ItemSerializer, SponsorCatalogItemSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ItemSerializer
from rest_framework import generics
import json
import requests

# Create your views here.


base_url = settings.ETSY_BASE_URL
key = settings.ETSY_API_KEY


def shop(request):

    if request.method == 'POST':
        add_ID = request.POST['ID']
        user = UserInformation.objects.get(user=request.user)
        company = user.sponsor_company
        catalog_item = CatalogItem.objects.filter(api_item_Id=add_ID)[0]

        # add to sponsor database
        if request.POST['change'] == 'Add':
            
            # check not already in sponsor
            if not SponsorCatalogItem.objects.filter(sponsor_company=company, catalog_item=catalog_item).exists():
                # calculate points
                ratio = company.company_point_ratio 
                cents = (int)(catalog_item.retail_price * 100)
                points = (int)(cents/ratio)

                # create new sponspor item and add to database
                new_sponsor_item = SponsorCatalogItem(sponsor_company=company, catalog_item=catalog_item, point_value=points, is_available_to_drivers=True)
                new_sponsor_item.save()

        elif request.POST['change'] == 'Remove':
            SponsorCatalogItem.objects.filter(sponsor_company=company, catalog_item=catalog_item).delete()
    else:
        # get all database instances for items and update all listings
        for listing in CatalogItem.objects.all():
            url = base_url + '/listings/{}?api_key={}'.format(listing.api_item_Id, key)
            response = requests.request("GET", url)
            search_was_successful = (response.status_code == 200)
            data = response.json()
            listing_data = data['results'][0]

            # check if the modfied time has been changed 
            listing.item_name = listing_data['title']
            listing.item_description = listing_data['description']
            # ignore foreign currency for now
            listing.retail_price = float(listing_data['price'])
            if listing_data['state'] == "active":
                listing.is_available = True
            else:
                listing.is_available = False
            listing.save()

            # create new catalog item image instance if one doesnt exist
            if not CatalogItemImage.objects.filter(catalog_item = listing).exists():
                url = base_url + '/listings/{}/images?api_key={}'.format(listing.api_item_Id, key)
                response = requests.request("GET", url)
                search_was_successful = (response.status_code == 200)
                image_data = response.json()
                images = image_data['results']
                for image in images:
                    if image['rank'] == 1:
                        main_image = image['url_170x135']
                CatalogItemImage.objects.create(catalog_item = listing, image_link = main_image)

    # gather objects to be used in html 
    items = CatalogItem.objects.all()
    images = CatalogItemImage.objects.all()
    listings = zip(items, images)
    return render(request, "catalog/shop.html", context = {'listings' : listings})
    
# need some kind of additional inheritance so CatalogItemImage can be accessed through CatalogItem
# zip relies on the listings always being in order which may not always be the case
    
def my_catalog(request):
    user = UserInformation.objects.get(user=request.user)
    company = user.sponsor_company
    items = CatalogItem.objects.filter(sponsorcatalogitem__in=SponsorCatalogItem.objects.filter(sponsor_company=company)).order_by('pk')
    sponsors = SponsorCatalogItem.objects.filter(catalog_item__in=items).order_by('catalog_item')
    images = CatalogItemImage.objects.filter(catalog_item__in=items).order_by('catalog_item')
    listings = zip(items, sponsors, images)
    return render(request, "catalog/my-catalog.html", context = {'listings' : listings})

# trying to use django-restframework & django-filters 
class Get_Items(APIView):
    def get(self, request):
        items = CatalogItem.objects.all()
        serialized = ItemSerializer(items, many=True)
        return Response(serialized.data)

class Get_Sponsor_Items(APIView):
    def get(self, request):
        user = UserInformation.objects.get(user=request.user)
        company = user.sponsor_company
        sponsor_items = SponsorCatalogItem.objects.filter(sponsor_company=company)
        serialized = SponsorCatalogItemSerializer(sponsor_items, many=True)
        return Response(serialized.data)

def listings(request):
    return render(request, "catalog/listings.html")