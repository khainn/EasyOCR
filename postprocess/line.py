import numpy as np
from postprocess.util import convert_vi_en,merge_text
from postprocess.bbox import merge_bbox,check_same_line_bbox

def merge_hline(lines):
    same_lines_list={}
    checked=[]
    for i in range(len(lines)-1,-1,-1):
        if i in checked:
            continue
        same_lines_list[i]=[lines[i]]
        for j in range(i-1,-1,-1):
            if check_same_line_bbox(lines[i][1],lines[j][1]):
                same_lines_list[i].append(lines[j])
                checked.append(j)

    new_lines=[]
    for key,same_lines in  same_lines_list.items():
        same_lines = sorted(same_lines, key=lambda x: np.mean(x[1][0]))
        
        m_bbox= merge_bbox([line[1] for line in same_lines])
        m_tex = merge_text([line[0] for line in same_lines])

        new_lines.append([m_tex,m_bbox]) 
    return  new_lines        

def line_postprocess(results,img):
    img_H,img_W=img.shape[:2]
    string_json={'Owners full name':'', 'Address':'', 'Brand':'', 'Color':'', 'NumberPlate': '', \
'Date of first registration': '', 'EngineN': '','Chassis':'', 'Capacity': ''}
    bboxs=[[int(result[0][0][0]),int(result[0][0][1]),  int(result[0][2][0]),int(result[0][2][1])] for result in results]
    texts= [result[1] for result in results]

    line_info=[[text,bbox] for text,bbox in zip(texts,bboxs)]
    line_info=merge_hline(line_info)

    l_info=[[text,bbox] for text,bbox in zip(texts,bboxs)  if np.mean(bbox[::2]) < img_W/2.0 ]
    r_right=[[text,bbox] for text,bbox in zip(texts,bboxs)  if np.mean(bbox[::2]) >= img_W/2.0 ]

    l_info=merge_hline(l_info)
    r_right=merge_hline(r_right)

    l_info = sorted(l_info, key=lambda x: np.mean(x[1][1::2]))
    r_right = sorted(r_right, key=lambda x: np.mean(x[1][1::2]))

    string_json=left_postprocess(l_info,string_json)
    string_json=right_postprocess(r_right,string_json)

    return string_json


def left_postprocess(l_info,string_json):
    for i,(text,bbox) in enumerate(l_info):
        en_text=convert_vi_en(text)
        if 'Ten' in en_text or 'Owner' in en_text:
            if i+1 >=len(l_info) :
                continue 
            if 'Dia' not in l_info[i+1][0] and 'Addr' not in l_info[i+1][0]:
                string_json['Owners full name']= l_info[i+1][0]
        
        if 'Dia' in en_text or 'Addr' in en_text:
            if i+1 >=len(l_info) :
                continue 
            if 'Nhan' not in l_info[i+1][0] and 'Brand' not in l_info[i+1][0] and 'hieu' not in l_info[i+1][0]:
                string_json['Address']= l_info[i+1][0]

        if 'Nhan' in en_text or 'Brand' in en_text or 'hieu' in en_text:
            if ')' in en_text:
                string_json['Brand']=l_info[i][0].split(')')[-1]
            elif 'nd' in en_text:
                string_json['Brand']=l_info[i][0].split('nd')[-1]

        if 'Mau' in en_text or 'son' in en_text or 'Color' in en_text:
            if ')' in en_text:
                string_json['Color']=l_info[i][0].split(')')[-1]
            elif 'or' in en_text:
                string_json['Color']=l_info[i][0].split('or')[-1]

        if 'Bien' in en_text or 'dang' in en_text:
            if i+1 >=len(l_info) :
                continue 
            if len(l_info[i+1][0])< 6:
                if i+2 >=len(l_info) :
                    continue 
                string_json['NumberPlate']= l_info[i+2][0]
            else:
                string_json['NumberPlate']= l_info[i+1][0]

            string_json['NumberPlate']=string_json['NumberPlate'].replace('l','1')
            string_json['NumberPlate']=string_json['NumberPlate'].replace('h','8')

        if 'Date' in en_text or 'firts' in en_text or 'regist' in en_text:
            if i+1 >=len(l_info) :
                continue 
            string_json['Date of first registration']= l_info[i+1][0]

    return string_json

def right_postprocess(r_right,string_json):
    for i,(text,bbox) in enumerate(r_right):
        en_text=convert_vi_en(text)
        if 'Somay' in en_text or 'may' in en_text:
            if i+1 >=len(r_right) :
                continue 
            if 'Sokhung' not in r_right[i+1][0] and 'khung' not in r_right[i+1][0]:
                string_json['EngineN']= r_right[i+1][0]

        if 'Sokhung' in en_text or 'khung' in en_text:
            if i+1 >=len(r_right) :
                continue 
            if 'Model' not in r_right[i+1][0] and 'oai' not in r_right[i+1][0] and 'Model' not in r_right[i+1][0]:
                string_json['Chassis']= r_right[i+1][0]
        
        # if 'Soloai' in en_text or 'loai' in en_text or 'Model' in en_text:
        #     # print('gggggggggggggggggggg')
        #     if string_json['Model'] !='':
        #         continue
        #     if i+1 >=len(r_right) :
        #         continue 
        #     if 'Model' not in r_right[i+1][0] and 'Dung' not in  :
        #         if 'Model' in r_right[i+1][0]:
        #             if i+2 >=len(r_right) :
        #                 continue 
        #             string_json['Model']= r_right[i+2][0]
        #             # print(r_right[i+2][0])
        #         else:
        #             string_json['Model']= r_right[i+1][0]

        if 'Dung' in en_text or 'tich' in en_text or 'Capacity' in en_text:

            if string_json['Capacity'] !='':
                continue

            if ')' in en_text:
                string_json['Capacity']=r_right[i][0].split(')')[-1]
            elif 'ty' in en_text:
                string_json['Capacity']=r_right[i][0].split('ty')[-1]

            string_json['Capacity']=string_json['Capacity'].replace('T','1')
            string_json['Capacity']=string_json['Capacity'].replace(':','')

            if i+1 >=len(r_right) :
                    continue 
            if  string_json['Capacity']=='' and r_right[i+1][0].isnumeric():

                string_json['Capacity']=r_right[i+1][0]

    return string_json
