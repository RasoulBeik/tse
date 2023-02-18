from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
# from PIL import Image
from io import BytesIO

def simple_get(url, timeout=15, verbose=True):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True, timeout=timeout)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)), verbose=verbose)
        return None

def download_file(url, timeout=15):
    r = get(url, allow_redirects=True)
    # open('xxxxx.csv', 'w').write(r.content)
    return r.content

# def get_image(image_url, output_file_path=None):
#     img_content = simple_get(image_url)
#     if img_content is None:
#         return None

#     try:
#         img = Image.open(BytesIO(img_content))
#         if output_file_path is not None:
#             img.save(output_file_path)
#         return img
#     except IOError as e:
#         log_error('Error during requests to {0} : {1}'.format(image_url, str(e)))
#         return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and (content_type.find('html') > -1 or content_type.find('image') > -1))

def log_error(e, verbose=True):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    if verbose:
        print(e)
    return

if __name__ == "__main__":
    pass
    h = simple_get('https://www.programcreek.com/')
    print(h)