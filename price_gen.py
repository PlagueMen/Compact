from zipfile import ZipFile, ZIP_DEFLATED
import os.path

from app.price_gen import generate_price


if __name__ == "__main__":
    if os.path.exists("app/static/img/logo.bmp"):
        img_path = "app/static/img/logo.bmp"
        path = "app/static/upload/"
    else:
        img_path = "/home/alex/cmpt_shop/app/static/img/logo.bmp"
        path = "/home/alex/cmpt_shop/app/static/upload/"
    generate_price(img_path, os.path.join(path, "price_cmpt.xls"))
    print ("Compressing...")
    with ZipFile(os.path.join(path, "price_cmpt.zip"), "w", ZIP_DEFLATED) as myzip:
        myzip.write(os.path.join(path, "price_cmpt.xls"), "price_cmpt.xls")
