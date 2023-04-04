from django.http import JsonResponse
from django.utils import timezone

from rest_framework.views import APIView

from bs4 import BeautifulSoup

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from scraper.models import OlxQuery, OlxAdvertisement
from scraper.serializers import OlxQuerySerializer
from scraper.utils import olx_login, scrap_olx_ads, send_email_with_ads_sample


class ScrapOlxView(APIView):
    serializer_class = OlxQuerySerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_keyword = serializer.validated_data['search_keyword']
        email = serializer.validated_data['email']
        email_message_size = serializer.validated_data['size']

        olx_query, olx_query_created = OlxQuery.objects.get_or_create(
            search_keyword=search_keyword, date_created=timezone.now().date()
        )

        if not olx_query_created:
            if not OlxAdvertisement.objects.filter(olx_query=olx_query).exists():
                return JsonResponse(
                    {
                        'message': 'This Olx query is done today before. No results for it.'
                    }
                )

            send_email_with_ads_sample(email, email_message_size)
            return JsonResponse(
                {
                    'message': 'Email sent. This Olx query is done before today. Data sent from DB. Check the console please.'
                }
            )

        browser = olx_login()

        if not browser:
            return JsonResponse({'message': 'Failed to Login to Olx'})

        try:
            # Get the search bar
            WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.XPATH, "//input[@placeholder='Find Cars, Mobile Phones and more...']"))
            )
            search_input = browser.find_element(By.XPATH, "//input[@placeholder='Find Cars, Mobile Phones and more...']")
            # Do the search
            search_input.send_keys(search_keyword)
            search_input.send_keys(Keys.ENTER)
        except (NoSuchElementException, TimeoutException):
            return JsonResponse({'message': 'Failed to locate search bar in Olx'})

        # Scrap Olx ads data
        olx_ads = scrap_olx_ads(browser, olx_query)
        if len(olx_ads) == 0:
            return JsonResponse({'message': 'No ads found for this keyword'})
        
        send_email_with_ads_sample(email, email_message_size)          

        return JsonResponse({'message': 'Olx scrapping is done and email is sent. Check the console please.'})
