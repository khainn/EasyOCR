def check_same_line_bbox(bbox1,bbox2):
    l1,t1,r1,b1=bbox1
    h1=abs(b1-t1)
    l2,t2,r2,b2=bbox2
    h2=abs(b2-t2)

    if abs(t1-t2) < min(h1/2.0,h2/2.0):
        return True
    return False

def merge_bbox(bboxs):

    m_bbox=bboxs[0]
    for bbox2 in bboxs[1:]:
        l1,t1,r1,b1=m_bbox
        l2,t2,r2,b2=bbox2

        l=min(l1,l2)
        t=min(t1,t2)
        r=max(r1,r2)
        b=max(b1,b2)

        m_bbox=[l,t,r,b]
    return m_bbox

# Khainn add
def Check_bbox_in_group(bbox1, bbox2):
    x11, y11 = bbox1[0]
    x21, y21 = bbox1[1]

    x12, y12 = bbox2[0]
    x22, y22 = bbox2[1]

    tx1 = round((x11 + x21)/2)
    ty1 = round((y11 + y21)/2)

    tx2 = round((x12 + x22)/2)
    ty2 = round((y12 + y22)/2)

    if( abs(tx1 - x12) < x22/2 and abs(ty2 - y11) < y22):
        return True
    return False

def merge_2_bbox(bbox1, bbox2):
    l = min(bbox1[0][0], bbox2[0][0])
    t = min(bbox1[0][1], bbox2[0][1])
    r = max(bbox1[2][0], bbox2[2][0])
    b = max(bbox1[2][1], bbox2[2][1])
    
    m_box = [[l, t], [r, t], [r, b], [l, b]]
    return m_box
