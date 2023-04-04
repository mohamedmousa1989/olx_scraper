import undetected_chromedriver

from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template

from bs4 import BeautifulSoup

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from scraper.models import OlxAdvertisement

def olx_login():
    """Login to Olx using Selenium."""

    # Setting chrome browser options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = undetected_chromedriver.Chrome(chrome_options=chrome_options, executable_path='/chromedriver')

    browser.get(settings.OLX_SCRAPPING_URL)
    
    try:
        # Get login link
        login_popup_link = browser.find_element(By.CSS_SELECTOR, "button[aria-label*='Login']")
        login_popup_link.click()

        # Handle login modal
        WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.XPATH, "//span[text()='Continue with Email']"))
        )
        continue_with_email_button = browser.find_element(By.XPATH, "//span[text()='Continue with Email']")
        continue_with_email_button.click()

        email_input = browser.find_element(By.ID, "email")
        email_input.send_keys(settings.OLX_ACCOUNT_EMAIL)
        email_input.send_keys(Keys.ENTER)

        WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.ID, "password"))
        )
        password_input = browser.find_element(By.ID, "password")
        password_input.send_keys(settings.OLX_ACCOUNT_PASSWORD)
        password_input.send_keys(Keys.ENTER)

    except (NoSuchElementException, TimeoutException):
        return None
    
    return browser    


def scrap_olx_ads(browser, olx_query):
    """Scrap ads from Olx."""

    ads_urls = []
    page = 1  
    database_bulk_create_index = 50
    while len(ads_urls) < settings.OLX_SCRAPPED_ADS_MIN_LIMIT:
        try:
            # Check if there are results. If so, get links of all ads
            WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CLASS_NAME, "_52497c97")) # This is the div with results
            )
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            result_sets = soup.find_all('ul', {'class': 'ba608fb8 de8df3a3'})

            for result_set in result_sets:
                for list_item in result_set.find_all('li', {'aria-label': 'Listing'}):
                    link = list_item.find('a')
                    ads_urls.append(f'https://www.olx.com.eg{link.get_attribute_list("href")[0]}')

            # Go to next results page
            current_page_url = browser.current_url.split('?page=')[0]
            next_page_url = f'{current_page_url}?page={page+1}'
            browser.get(next_page_url)
            page += 1
        except TimeoutException:
            break

    # Navigate to each ad link, scrap its data and save it to database
    ads_objects = [] 
    for index, ad_url in enumerate(ads_urls):
        browser.get(ad_url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        overview_section = soup.find('div', {'class': 'cf4781f0', 'aria-label': 'Overview'})
        ad_title = overview_section.find('h1', {'class': 'a38b8112'}).text
        price = overview_section.find('span', {'class': '_56dab877'}).text
        location = overview_section.find('span', {'class': '_8918c0a8', 'aria-label': 'Location'}).text

        seller_description_section = soup.find('div', {'class': 'cf4781f0', 'aria-label': 'Seller description'})
        advertiser_name = seller_description_section.find('span', {'class': '_261203a9 _2e82a662'}).text
        ad_olx_id = soup.find('div', {'class': '_171225da'}).text
        try:
            show_number_link = browser.find_element(By.XPATH, "//span[text()='Show number']")
            show_number_link.click()
            WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "span._45d98091._2e82a662"))
            )
            advertiser_number = browser.find_element(By.CSS_SELECTOR, "span._45d98091._2e82a662").text
        except NoSuchElementException:
            advertiser_number = ''
        except TimeoutException:
            continue

        price = price.strip('EGP ').replace(',', '')        
        ads_objects.append(
            OlxAdvertisement(
                title = ad_title,
                price = float(price) if price != '' else 0,
                location = location,
                advertiser_name = advertiser_name,
                advertiser_phone_number = advertiser_number,
                olx_id = ad_olx_id.strip('AD ID '),
                olx_query = olx_query
            )
        )

        # Bulk create ads in database
        if (index == database_bulk_create_index) or (index == len(ads_urls) - 1):  
            OlxAdvertisement.objects.bulk_create(ads_objects)
            database_bulk_create_index += 50

    return ads_urls


def send_email_with_ads_sample(email, email_message_size):
    """Send an email with ads sample data."""

    ads = OlxAdvertisement.objects.filter(
        olx_query__date_created=timezone.now().date()
    ).order_by('price')[:email_message_size] # Sorting data by 'price' in an ascending order


    context = {'data': [ad.__dict__ for ad in ads]}
    template = get_template('email.html').render(context)

    send_mail(
        'Olx ads sample',
        None, # Pass None because it's a HTML mail
        'no-reply@gmail.com',
        [email],
        fail_silently=False,
        html_message = template
    )