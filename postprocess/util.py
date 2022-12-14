def convert_vi_en(string):
    string=string.replace(' ','')
    string=string.replace('ê','e')
    string=string.replace('ư','u')
    string=string.replace('ủ','u')
    string=string.replace('ã','a')
    string=string.replace('ỉ','i')
    string=string.replace('à','a')
    string=string.replace('ý','a')
    string=string.replace('ơ','o')
    string=string.replace('ô','o')
    string=string.replace('ố','o')
    string=string.replace('ệ','e')
    string=string.replace('á','a')
    string=string.replace('ạ','a')
    string=string.replace('í','i')
    string=string.replace('ầ','a')
    string=string.replace('ă','a')
    string=string.replace('ẳ','a')
    string=string.replace('Đ','D')
    string=string.replace('đ','d')
    string=string.replace('đ','d')
    string=string.replace('ể ','e')
    return string


def merge_text(texts):
    m_text=texts[0]
    for text in texts[1:]:
        m_text= m_text +text
    return m_text