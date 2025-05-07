import asyncio
import warnings
import time
import re

from urllib.parse import unquote
from datetime import datetime

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from nanga_ad_library.utils import *

"""
Define MetaAdDownloader class to retrieve ad elements using Playwright.
"""


class MetaRequestInterceptor:
    """
    A class designed to passively intercept network requests from the Meta Ad Library preview while downloading
      ad elements (Title, Body, Description, Image url, Video url and Call to action).
    It blocks direct video requests (to avoid detection) and captures video and image URLs instead.
    These URLs are stored for extracting video links and thumbnails (in __intercepted_videos & __intercepted_images),
      enabling a bypass of Meta's anti-scraping measures.
    """

    def __init__(self, verbose):
        self.__verbose = verbose
        self.__intercepted_videos = []
        self.__intercepted_images = []

    async def intercept(self, route, request):
        # Intercept video requests
        if "video" in request.url:
            await route.abort()
            if self.__verbose:
                print(f"Video request blocked: {request.url}")
            # Store video
            self.__intercepted_videos.append(request.url)

        # Intercept image requests
        elif "scontent" in request.url:
            await route.continue_()
            if self.__verbose:
                print(f"Image request passed: {request.url}")
            # Store image
            self.__intercepted_images.append(request.url)

        else:
            await route.continue_()
            if self.__verbose:
                print(f"Other request passed: {request.url}")

    def get_videos(self):
        return self.__intercepted_videos

    def get_images(self):
        return self.__intercepted_images

    def is_empty(self):
        return bool(self.__intercepted_images or self.__intercepted_videos)


class MetaAdDownloader:
    """
    A class instancing a scraper to retrieve elements from Meta Ad Library previews:
      Body, Title*, Image*, Video*, Description*, Landing page*, CTA caption*
      - "*" tagged elements are retrieved for each creative visual (1 for statics, several for carousels)
    """

    # Store the fields used to store (1) the Meta Ad Library preview url and (2) the ad delivery start date
    PREVIEW_FIELD = "ad_snapshot_url"
    DELIVERY_START_DATE_FIELD = "ad_delivery_start_time"

    # Store the Meta public ad preview base url
    PUBLIC_PREVIEW_URL = "https://www.facebook.com/ads/library/"

    # Store the maximum number of pages that can be open simultaneously in a browser's context
    MAX_BATCH_SIZE = 5

    def __init__(self, start_date=None, end_date=None, verbose=False, proxy=None):
        """

        Args:
            start_date: If not empty: download only ads created after this date,
            end_date: If not empty: download only ads created before this date,
            verbose: Whether to display intermediate logs.
        """

        # Verbose
        self.__verbose = verbose or False

        # Store download start date
        try:
            self.__download_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except:
            self.__download_start_date = datetime.fromtimestamp(0)
            # Raise a warning if the start_date was given but parsing failed
            if start_date and self.__verbose:
                warnings.warn("Provided start date should match the following format '%Y-%m-%d'.")

        # Store download end date
        try:
            self.__download_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            self.__download_end_date = datetime.today()
            # Raise a warning if the start_date was given but parsing failed
            if start_date and self.__verbose:
                warnings.warn("Provided end date should match the following format '%Y-%m-%d'.")

        # Store the proxy url to use for playwright
        proxy = proxy or {}
        if all([x in proxy.keys() for x in ["server", "username", "password"]]):
            self.__proxy = {
                "server": proxy.get("server"),
                "username": proxy.get("username"),
                "password": proxy.get("password")
            }
        else:
            self.__proxy = None

        # Whether Meta has spotted our webdriver and blocked it.
        self.__spotted = False

    @classmethod
    def init(cls, **kwargs):
        """
        Process the provided payload and create a MetaAdDownloader object if everything is fine

        Returns:
            A new MetaAdDownloader object
        """

        # Initiate a playwright downloader
        ad_downloader = cls(
            start_date=kwargs.get("download_start_date"),
            end_date=kwargs.get("download_end_date"),
            verbose=kwargs.get("verbose"),
            proxy=kwargs.get("proxy")
        )

        return ad_downloader

    async def download_from_new_batch(self, ad_library_batch):
        """
        Use parallelized calls to download ad elements for each row of a batch

        Args:
            ad_library_batch: A list of records from a ResponseCursor object.

        Returns:
             The updated batch with new key "ad_elements".
        """

        # Initiate playwright context for this batch
        async with async_playwright() as p:
            # Initiate playwright browser and use it for the whole batch
            if self.__proxy:
                browser = await p.chromium.launch(headless=True, proxy=self.__proxy)
            else:
                browser = await p.chromium.launch(headless=True)

            try:
                # Download ad_elements using smaller batches
                updated_batches = []
                while ad_library_batch:
                    ad_downloader_batch = ad_library_batch[:self.MAX_BATCH_SIZE]
                    ad_library_batch = ad_library_batch[self.MAX_BATCH_SIZE:]

                    # Initiate new context with a randomly generated User Agent
                    user_agent = UserAgent().pick()
                    context = await browser.new_context(user_agent=user_agent)

                    try:
                        for ad_payload in ad_downloader_batch:
                            # Download ad elements 1 by 1
                            updated_batch = await self.__download_ad_elements_from_public(context, ad_payload)
                            updated_batches.append(updated_batch)

                    finally:
                        # Close driver context and wait 1 second before next batch
                        await context.close()
                        time.sleep(1)

            finally:
                await browser.close()

        return updated_batches

    async def __download_ad_elements_from_private(self, context, ad_payload, previous_page=None):
        """ [Hidden method]
        Use scraping to extract all ad elements from the ad preview url.
        The url used is private (needs our access token).

        Args:
            context: A playwright browser's context
            ad_payload: The ad payload (response from Ad Library API)
            previous_page: Playwright page in use when triggering this function.

        Returns:
            A dict with the downloaded ad elements.
        """

        # Prepare payload to return
        ad_elements = {
            "body": None,
            "type": None,
            "carousel": [],
            "spotted": self.__spotted
        }

        # Check that delivery_start_date is between __download_start_date et __download_end_date
        delivery_start_date = datetime.strptime(ad_payload.get(self.DELIVERY_START_DATE_FIELD), "%Y-%m-%d")
        download_needed = (self.__download_start_date <= delivery_start_date <= self.__download_end_date)

        # Go to page and try ad elements extraction (only if needed and not already spotted)
        if download_needed and not self.__spotted:
            # Extract preview url from ad payload
            preview = current_url = ad_payload.get(self.PREVIEW_FIELD)

            # Initiate request interceptor
            interceptor = MetaRequestInterceptor(self.__verbose)

            # Initiate new playwright page
            page = await context.new_page()

            try:
                # Activate page requests interception
                await page.route("**/*", interceptor.intercept)

                # Open Ad Library card and wait until all requests are finished / Increase nav timeout to 5 minutes.
                await page.goto(preview, timeout=300000)
                await page.wait_for_load_state("networkidle")

                # Check if Meta redirected us to a login page
                current_url = page.url
                if "login" in current_url:
                    self.__spotted = True
                    ad_elements["spotted"] = self.__spotted
                    raise Exception(f"Meta detected a non-human behavior and redirected us to '{current_url}'.")

                # Deduplicate blocked videos
                blocked_videos = list(set(interceptor.get_videos()))

                # Store thumbnails from blocked videos
                page_images_locator, page_images = await page.locator("img").all(), []
                if page_images_locator:
                    page_images = [await image.get_attribute("src") for image in page_images_locator]
                blocked_videos_thumbnails = list(set([image for image in interceptor.get_images() if image not in page_images]))

                # Get Body
                body_locator = await page.locator("""//*[@id="content"]/div/div/div/div/div/div/div[2]/div[1]""").all()
                if body_locator:
                    ad_elements["body"] = await body_locator[0].inner_text()

                # Deal with Carousels (several creatives in the ad)
                carousel_path = """//*[@id="content"]/div/div/div/div/div/div/div[3]/div/div[2]/div/div/div"""
                carousel_locator = await page.locator(carousel_path).all()
                if carousel_locator:
                    ad_elements["type"] = "carousel"
                    for k in range(len(carousel_locator)):
                        # Prepare dict
                        creative = {
                            "title": None,
                            "image": None,
                            "video": None,
                            "landing_page": None,
                            "cta": None,
                            "caption": None,
                            "description": None
                        }
                        creative_path = f"""{carousel_path}[{k + 1}]/div/div"""
                        # Image
                        image_locator = await page.locator(f"""{creative_path}/a/div[1]/img""").all()
                        if image_locator:
                            links_path = creative_path + "/a"
                            captions_path = links_path + "/div[2]"
                            creative["image"] = await image_locator[0].get_attribute("src")
                        # Video
                        video_locator = await page.locator(f"""{creative_path}/div[1]//video""").all()
                        if video_locator:
                            links_path = creative_path + "/div[2]/a"
                            captions_path = links_path + "/div"
                            creative["image"] = await video_locator[0].get_attribute("playsinline poster")
                            creative["video"] = await video_locator[0].get_attribute("src")
                        # Undetected video or empty
                        if not (image_locator or video_locator):
                            if blocked_videos:
                                links_path = creative_path + "/div[2]/a"
                                captions_path = links_path + "/div"
                                creative["video"] = blocked_videos.pop(0)
                                if blocked_videos_thumbnails:
                                    creative["image"] = blocked_videos_thumbnails.pop(0)
                            else:
                                links_path = creative_path + "/a"
                                captions_path = links_path + "/div[2]"
                        # Landing page
                        landing_page_locator = await page.locator(links_path).all()
                        if landing_page_locator:
                            creative["landing_page"] = await landing_page_locator[0].get_attribute("href")
                        # Call to action
                        cta_locator = await page.locator(f"""{captions_path}/div[2]/div/div/span/div/div/div""").all()
                        if cta_locator:
                            creative["cta"] = await cta_locator[0].inner_html()
                        # Caption
                        caption_locator = await page.locator(f"""{captions_path}/div[1]/div[1]/div/div""").all()
                        if caption_locator:
                            creative["caption"] = await caption_locator[0].inner_html()
                        # Title
                        title_locator = await page.locator(f"""{captions_path}/div[1]/div[2]/div/div""").all()
                        if title_locator:
                            creative["title"] = await title_locator[0].inner_html()
                        # Description
                        description_locator = await page.locator(f"""{captions_path}/div[1]/div[3]/div/div""").all()
                        if description_locator:
                            creative["description"] = await description_locator[0].inner_html()
                        # Add to list
                        ad_elements["carousel"].append(creative)

                # Deal with ads displaying only one creative
                else:
                    # Prepare dict
                    creative = {
                        "title": None,
                        "image": None,
                        "video": None,
                        "landing_page": None,
                        "cta": None,
                        "caption": None,
                        "description": None
                    }
                    creative_path = f"""//*[@id="content"]/div/div/div/div/div/div/div[2]"""
                    # Image (with title + links)
                    image_locator_1 = await page.locator(f"""{creative_path}/a/div[1]/img""").all()
                    if image_locator_1:
                        ad_elements["type"] = "image"
                        links_path = creative_path + "/a"
                        captions_path = links_path + "/div[2]"
                        creative["image"] = await image_locator_1[0].get_attribute("src")
                    # Image (without title + links)
                    image_locator_2 = await page.locator(f"""{creative_path}/div[2]/img""").all()
                    if image_locator_2:
                        ad_elements["type"] = "image"
                        links_path = None
                        captions_path = None
                        creative["image"] = await image_locator_2[0].get_attribute("src")
                    # Video
                    video_locator = await page.locator(f"""{creative_path}/div[2]//video""").all()
                    if video_locator:
                        ad_elements["type"] = "video"
                        links_path = creative_path + "/div[3]/a"
                        captions_path = links_path + "/div"
                        creative["image"] = await video_locator[0].get_attribute("playsinline poster")
                        creative["video"] = await video_locator[0].get_attribute("src")
                    # Undetected video or empty
                    if not (image_locator_1 or image_locator_2 or video_locator):
                        if blocked_videos:
                            ad_elements["type"] = "video"
                            links_path = creative_path + "/div[3]/a"
                            captions_path = links_path + "/div"
                            creative["video"] = blocked_videos.pop(0)
                            if blocked_videos_thumbnails:
                                creative["image"] = blocked_videos_thumbnails.pop(0)
                        else:
                            ad_elements["type"] = "status"
                            links_path = creative_path + "/a"
                            captions_path = links_path + "/div[2]"
                    if links_path:
                        # Landing page
                        landing_page_locator = await page.locator(links_path).all()
                        if landing_page_locator:
                            meta_landing_page = await landing_page_locator[0].get_attribute("href")
                            creative["landing_page"] = self.__extract_lp_from_meta_url(meta_landing_page)
                    if captions_path:
                        # Call to action
                        cta_locator = await page.locator(f"""{captions_path}/div[2]/div/div/span/div/div/div""").all()
                        if cta_locator:
                            creative["cta"] = await cta_locator[0].inner_html()
                        # Caption
                        caption_locator = await page.locator(f"""{captions_path}/div[1]/div[1]/div/div""").all()
                        if caption_locator:
                            creative["caption"] = await caption_locator[0].inner_html()
                        # Title
                        title_locator = await page.locator(f"""{captions_path}/div[1]/div[2]/div/div""").all()
                        if title_locator:
                            creative["title"] = await title_locator[0].inner_html()
                        # Description
                        description_locator = await page.locator(f"""{captions_path}/div[1]/div[3]/div/div""").all()
                        if description_locator:
                            creative["description"] = await description_locator[0].inner_html()
                    # Add to list
                    ad_elements["carousel"].append(creative)

                # Check that scraping did not fail
                if ad_elements.get("type") == "status" and not interceptor.is_empty():
                    raise ValueError(f"Failed to scrap visuals from Meta Ad Library preview: '{preview}'")

            except PlaywrightTimeoutError:
                print(f"[ERROR] Timeout while loading page '{preview}'")
            except PlaywrightError as e:
                print(f"[ERROR] Scrapping page '{current_url}' failed with error: {e}")
            except Exception as e:
                print(f"[ERROR] Scrapping page '{current_url}' failed with error: {e}")
            finally:
                await page.close()

        # Close previous page
        if previous_page and not previous_page.is_closed():
            await previous_page.close()

        # Update payload
        ad_payload.update({"ad_elements": ad_elements})

        return ad_payload

    async def __download_ad_elements_from_public(self, context, ad_payload):
        """ [Hidden method]
        Use scraping to extract all ad elements from the ad preview url.
        The ad preview url is a public link.

        Args:
            context: A playwright browser's context
            ad_payload: The ad payload (response from Ad Library API).

        Returns:
            A dict with the downloaded ad elements.
        """

        # Prepare payload to return
        ad_elements = {
            "body": None,
            "type": None,
            "carousel": [],
            "spotted": self.__spotted
        }

        # Check that delivery_start_date is between __download_start_date et __download_end_date
        delivery_start_date = datetime.strptime(ad_payload.get(self.DELIVERY_START_DATE_FIELD), "%Y-%m-%d")
        download_needed = (self.__download_start_date <= delivery_start_date <= self.__download_end_date)

        # Go to page and try ad elements extraction (only if needed and not already spotted)
        if download_needed and not self.__spotted:
            # Extract preview url from ad payload
            preview = current_url = f"{self.PUBLIC_PREVIEW_URL}?id={ad_payload.get('id')}"

            # Initiate request interceptor
            interceptor = MetaRequestInterceptor(self.__verbose)

            # Initiate new playwright page
            page = await context.new_page()

            try:
                # Activate page requests interception
                await page.route("**/*", interceptor.intercept)

                # Open Ad Library card and wait until all requests are finished / Increase nav timeout to 5 minutes.
                await page.goto(preview, timeout=300000)
                await page.wait_for_load_state("networkidle")

                # Check if Meta redirected us to a login page
                current_url = page.url
                if "login" in current_url:
                    self.__spotted = True
                    ad_elements["spotted"] = self.__spotted
                    raise Exception(f"Meta detected a non-human behavior and redirected us to '{current_url}'.")

                # Focus on the interesting part of the page
                source_locator = page.get_by_role("dialog").locator("//div[2]/div[1]/div[2]//div[3]")

                # Get Body
                bodies = await source_locator.locator("//div[2]/div").all()
                if bodies:
                    ad_elements["body"] = await bodies[0].inner_text()

                # Deal with Carousels (several creatives in the ad)
                carousel_locator = source_locator.locator("//div[3]//div[2]")
                carousel_elements = await carousel_locator.locator("//a").count()
                if carousel_elements > 1:
                    ad_elements["type"] = "carousel"
                    for k in range(1, carousel_elements):
                        # Prepare dict
                        creative = {
                            "title": None,
                            "image": None,
                            "video": None,
                            "landing_page": None,
                            "cta": None,
                            "caption": None,
                            "description": None
                        }
                        element_locator = carousel_locator.locator(f"//div[{k}]")
                        # Image
                        images = await element_locator.locator("//img").all()
                        if images:
                            links_locator = element_locator.locator("//a/div[2]")
                            creative["image"] = await images[0].get_attribute("src")
                        # Blocked video: call self.__download_ad_elements_from_private
                        else:
                            return await self.__download_ad_elements_from_private(context, ad_payload, page)
                        # Landing page
                        landing_pages = await element_locator.locator("//a").all()
                        if landing_pages:
                            meta_url = await landing_pages[0].get_attribute("href")
                            creative["landing_page"] = self.__extract_lp_from_meta_url(meta_url)
                        # Call to action
                        ctas = await links_locator.locator("""//div[2]//div[@role="button"]/span/div/div/div""").all()
                        if ctas:
                            creative["cta"] = await ctas[0].inner_text()
                        # Caption
                        captions = await links_locator.locator("//div[1]/div[1]/div/div").all()
                        if captions:
                            creative["caption"] = await captions[0].inner_text()
                        # Title
                        titles = await links_locator.locator("//div[1]/div[2]/div/div").all()
                        if titles:
                            creative["title"] = await titles[0].inner_text()
                        # Description
                        descriptions = await links_locator.locator("//div[1]/div[3]/div/div").all()
                        if descriptions:
                            creative["description"] = await descriptions[0].inner_text()
                        # Add to list
                        ad_elements["carousel"].append(creative)

                # Deal with ads displaying only one creative
                else:
                    # Prepare dict
                    creative = {
                        "title": None,
                        "image": None,
                        "video": None,
                        "landing_page": None,
                        "cta": None,
                        "caption": None,
                        "description": None
                    }
                    element_locator = source_locator.locator("//div[2]")
                    # Image
                    images = await element_locator.locator("//img").all()
                    if images:
                        ad_elements["type"] = "image"
                        links_locator = element_locator.locator("//a/div[2]")
                        creative["image"] = await images[0].get_attribute("src")
                    # Blocked videos: call self.__download_ad_elements_from_private
                    else:
                        return await self.__download_ad_elements_from_private(context, ad_payload, page)
                    # Landing page
                    landing_pages = await element_locator.locator("//a").all()
                    if landing_pages:
                        meta_url = await landing_pages[0].get_attribute("href")
                        creative["landing_page"] = self.__extract_lp_from_meta_url(meta_url)
                    # Call to action
                    ctas = await links_locator.locator("""//div[2]//div[@role="button"]/span/div/div/div""").all()
                    if ctas:
                        creative["cta"] = await ctas[0].inner_text()
                    # Caption
                    captions = await links_locator.locator("//div[1]/div[1]/div/div").all()
                    if captions:
                        creative["caption"] = await captions[0].inner_text()
                    # Title
                    titles = await links_locator.locator("//div[1]/div[2]/div/div").all()
                    if titles:
                        creative["title"] = await titles[0].inner_text()
                    # Description
                    descriptions = await links_locator.locator("//div[1]/div[3]/div/div").all()
                    if descriptions:
                        creative["description"] = await descriptions[0].inner_text()
                    # Add to list
                    ad_elements["carousel"].append(creative)

            except PlaywrightTimeoutError as e:
                print(f"[ERROR] Timeout while loading page '{preview}': {e}")
            except PlaywrightError as e:
                print(f"[ERROR] Scrapping page '{current_url}' failed with error: {e}")
            except Exception as e:
                print(f"[ERROR] Scrapping page '{current_url}' failed with error: {e}")
            finally:
                await page.close()

        # Update payload
        ad_payload.update({"ad_elements": ad_elements})

        return ad_payload

    @staticmethod
    def __extract_lp_from_meta_url(url):
        """
        Extract the landing page that is embedded in the Facebook URL

        Args:
            url: The url extracted from the Meta Ad Library preview

        Returns:
            The raw landing page that was "embedded" in the Meta URL.
                We remove utms (all elements after "?" in the landing page).
        """

        pattern = re.compile("https://l\.facebook\.com/l\.php\?u=([^&]+)&.")
        match = re.match(pattern, url)
        landing_page = unquote(match.group(1)).split("?")[0] if match else url

        return landing_page

