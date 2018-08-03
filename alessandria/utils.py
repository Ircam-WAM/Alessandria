#-*- encoding:utf-8 *-*
import unicodedata
import uuid
import qrcode
from io import BytesIO
from PIL import ImageTk, Image, Image, ImageFont, ImageDraw
from django.apps import apps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

class IsbnUtils(object):
    @staticmethod
    def author_unpack(author):
        if not author:
            return '', ''
        items = author.split    (' ')
        last_name = items[-1:][0].strip()
        first_name = " ".join(items[:-1]).strip()
        return first_name, last_name
    
    @staticmethod
    def get_country_code(isbn_meta):
        if isbn_meta['Language']:
            return isbn_meta['Language'][:2].upper()
        return None
    
    @staticmethod
    def get_isbn_nb_from_meta(isbn_meta):
        if isbn_meta is not None:
            if isbn_meta.get('ISBN-13'):
                return isbn_meta['ISBN-13']
            if isbn_meta.get('ISBN-10'):
                return isbn_meta['ISBN-10']
        return None

class MyString(object):
    @staticmethod
    def remove_accents(s):
        if s is None:
            return None
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def generate_book_uuid():
    
    Book = apps.get_model('alessandria','Book')
    b_uuid = ""
    while True :
        b_uuid = str(uuid.uuid4())[:5]   
        if not Book.objects.filter(_uuid=b_uuid):
            break;
    return b_uuid

def generate_qrcode(uuid):
    
    bf = BytesIO()

    # Create QRCode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=0,
    )
    qr.add_data(uuid)
    qr.make(fit=True)
    qr_img = qr.make_image()
    
    # Paste QRCode on bigger white image
    background = Image.new('RGBA', (126, 200), (255, 255, 255, 255))
    bg_w, bg_h = background.size
    background.paste(qr_img)
    filename = '%s.png' % (uuid)

    # Draw UUID at the bottom
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype(settings.STATIC_ROOT + "alessandria/layout/font/ABeeZee-Regular.otf", 16)
    draw.text((10, 150), uuid, (0,0,0), font=font)
    background.save(bf, format='PNG')

    filebuffer = InMemoryUploadedFile(bf, None, filename, 'image/png', bf.getbuffer().nbytes, None)
    return filename, filebuffer    