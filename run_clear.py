#from app import app
from app.xml_import import del_empty_categories
from app import cache
from app.utils import gen_images_list, get_categories

if __name__ == "__main__":
    del_empty_categories()
    cache.clear()
    gen_images_list()
    get_categories()