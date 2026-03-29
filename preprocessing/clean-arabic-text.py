# import section

import pyarabic.araby as araby
import re
def convert_ind_arabic_to_latin(text):
    return text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789'))

         #text from user input 
def Arabic_trans(text):

    text = araby.normalize_alef(text) 
    text = araby.strip_tatweel(text)
    text = re.sub(r'([ء-ي])\1+', r'\1', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    text = convert_ind_arabic_to_latin(text)
    text = araby.tokenize(text)
   

return text


