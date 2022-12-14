import numpy as np
from postprocess.util import convert_vi_en,merge_text
from postprocess.bbox import Check_bbox_in_group, merge_2_bbox

def merge_hline(lines):
    same_lines_list={}
    checked=[]
    for i in range(len(lines)-1,-1,-1):
        if i in checked:
            continue
        same_lines_list[i]=[lines[i]]
        for j in range(i-1,-1,-1):
            if Check_bbox_in_group(lines[i][1],lines[j][1]):
                same_lines_list[i].append(lines[j])
                checked.append(j)

    new_lines=[]
    for key,same_lines in  same_lines_list.items():
        same_lines = sorted(same_lines, key=lambda x: np.mean(x[1][0]))
        
        m_bbox= merge_2_bbox([line[1] for line in same_lines])
        m_tex = merge_2_bbox([line[0] for line in same_lines])

        new_lines.append([m_tex,m_bbox]) 
    return  new_lines        



def DriverLicense_postprocess(results, StringJson):
    string_json = StringJson.copy()
    string_json["American states"]["bbox"] = results[0][0]
    string_json["American states"]["value"] = results[0][1]

    for i, result in enumerate(results):
        if("DL" in result[1]):
            string_json["DL"]["bbox"] = result[0]
            string_json["DL"]["value"] = result[1].replace("DL ", "")

        if("EXP " in result[1]):
            string_json["EXP"]["bbox"] = result[0]
            string_json["EXP"]["value"] = result[1].replace("EXP ", "")

        if("LN " in result[1]):
            string_json["Last Name"]["bbox"] = result[0]
            string_json["Last Name"]["value"] = result[1].replace("LN ", "")

        if("FN " in result[1]):
            string_json["First Name"]["bbox"] = result[0]
            string_json["First Name"]["value"] = result[1].replace("FN ", "")


            string_json["Address"]["bbox"] = merge_2_bbox(results[i+1][0], results[i+2][0])
            string_json["Address"]["value"] = results[i+1][1] + results[i+2][1]

        if("DOB " in result[1]):
            string_json["Date Of Birth"]["bbox"] = result[0]
            string_json["Date Of Birth"]["value"] = result[1].replace("DOB ", "")

        if("RSTR " in result[1]):
            string_json["RSTR"]["bbox"] = result[0]
            string_json["RSTR"]["value"] = result[1].replace("RSTR ", "")

        if("SEX " in result[1]):
            string_json["SEX"]["bbox"] = result[0]
            string_json["SEX"]["value"] = result[1].replace("SEX ", "")

        if("HAIR " in result[1]):
            string_json["HAIR"]["bbox"] = result[0]
            string_json["HAIR"]["value"] = result[1].replace("HAIR ", "")


        if("EYES " in result[1]):
            string_json["EYES"]["bbox"] = result[0]
            string_json["EYES"]["value"] = result[1].replace("EYES ", "")


        if("HGT " in result[1]):
            string_json["HGT"]["bbox"] = result[0]
            string_json["HGT"]["value"] = result[1].replace("HGT ", "").replace("\\", "")


        if("WGT" in result[1]):
            string_json["WGT"]["bbox"] = results[i+1][0]
            string_json["WGT"]["value"] = results[i+1][1]


        if("DD " in result[1]):
            string_json["DD"]["bbox"] = result[0]
            string_json["DD"]["value"] = result[1].replace("DD ", "")

        
        if("ISS" in result[1]):
            string_json["ISS"]["bbox"] = results[i+2][0]
            string_json["ISS"]["value"] = results[i+2][1]

    return string_json

def CCCD_VN_postprocess(results, StringJson):
    string_json = StringJson.copy()
    for i, result in enumerate(results):
        if("No." in result[1]):
            string_json["Number"]["bbox"] = results[i+1][0]
            string_json["Number"]["value"] = results[i+1][1]

        if("Full name" in result[1]):
            string_json["Full name"]["bbox"] = results[i+1][0]
            string_json["Full name"]["value"] = results[i+1][1]

        if("birth" in result[1]):
            string_json["Date Of Birth"]["bbox"] = results[i+1][0]
            string_json["Date Of Birth"]["value"] = results[i+1][1]

        if("Sex" in result[1]):
            r = result[1].replace(" ", "").split(":")
            if(r[0] == "Sex"):
                bbnew = result[0]
                bbnew[0][0] = bbnew[2][0] - 90
                bbnew[3][0] = bbnew[2][0] - 90
                string_json["Sex"]["bbox"] = bbnew
                string_json["Sex"]["value"] = r[1]
                # string_json["Sex"]["bbox"] = results[i+1][0]
                # string_json["Sex"]["value"] = results[i+1][1]
            # else:
            #     bbnew = result[0]
            #     bbnew[0][0] = bbnew[2][0] - 90
            #     bbnew[3][0] = bbnew[2][0] - 90
            #     string_json["Sex"]["bbox"] = bbnew
            #     string_json["Sex"]["value"] = r[1].split(":")[1]
            if(result[1] == "Sex:"):
                string_json["Sex"]["bbox"] = results[i+1][0]
                string_json["Sex"]["value"] = results[i+1][1]

        if("Nationality" in result[1]):
            r = result[1].split(":")
            if(r[-1] != ""):
                bbnew = result[0]
                bbnew[0][0] = bbnew[2][0] - 175
                bbnew[3][0] = bbnew[2][0] - 175
                string_json["Nationality"]["bbox"] = bbnew
                string_json["Nationality"]["value"] = r[1].lstrip()
            else:
                string_json["Nationality"]["bbox"] = results[i+1][0]
                string_json["Nationality"]["value"] = results[i+1][1]


        if("origin" in result[1]):
            string_json["Place of origin"]["bbox"] = results[i+1][0]
            string_json["Place of origin"]["value"] = results[i+1][1]

        # if("residence" in result[1]):
        #     string_json["Date Of Birth"]["bbox"] = results[i+1][0]
        #     string_json["Date Of Birth"]["value"] = results[i+1][1]

        if("expiry" in result[1]):
            lst = result[1].split(' ')
            for el in lst:
                if(r"/" in el):
                    string_json["Date of expiry"]["bbox"] = result[0]
                    string_json["Date of expiry"]["value"] = el

    return string_json