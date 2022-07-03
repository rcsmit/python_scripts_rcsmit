# code adapted from https://stackoverflow.com/questions/67141844/python-how-to-get-face-mesh-landmarks-coordinates-in-mediapipe
# added dataframe as output and an annotated image as output 

import cv2
import mediapipe as mp
import pandas as pd

def generate_df(file, show_image, save_image, img_out):
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh

    df = pd.DataFrame()
    file_list = [file]
    # For static images:
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        min_detection_confidence=0.5) as face_mesh:
        image = cv2.imread(file)
        # Convert the BGR image to RGB before processing.
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Print and draw face mesh landmarks on the image.
        # if not results.multi_face_landmarks:
        #     continue
        annotated_image = image.copy()
        for face in results.multi_face_landmarks:
            # print('face_landmarks:', face_landmarks)
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec)

        #for face in results.multi_face_landmarks:
            for i, landmark in enumerate(face.landmark):
                x = landmark.x
                y = landmark.y
                #print (i,x,y)
                df_ =pd.DataFrame([ {
                                    "id": i,
                                    "x": x*10000,
                                    "y": y * 10000
                
                                    }]
                                )           

                df = pd.concat([df, df_],axis = 0)   
                
                shape = image.shape 
                relative_x = int(x * shape[1])
                relative_y = int(y * shape[0])

                cv2.circle(image, (relative_x, relative_y), radius=1, color=(225, 0, 100), thickness=1)

              
                font = cv2.FONT_HERSHEY_COMPLEX_SMALL
                # cv2.putText(image,str(i),(relative_x, relative_y), font, 1, (255,255,255), 1, cv2.LINE_AA)
               
        if show_image == True:
            cv2.imshow('image',image)
            cv2.waitKey(0)
            if save_image== True:
                cv2.imwrite(img_out, image)
    #cv2.destroyAllWindows()
    
    return df

def transform_to_value_vertical(y_,ih):
    # transforms the calculated value to pixels on image
    y = int(y_/10000*ih)
    return y
def transform_to_value_horizontal(x_,iw):
    # transforms the calculated value to pixels on image
    x = int(x_/10000*iw)
    return x

def calculate_beauty(df, url):
    # https://www.goldennumber.net/meisner-beauty-guide-golden-ratio-facial-analysis/
    # top of head wordt niet gemeten #1

    center_face_top =  (df.iloc[10,0],df.iloc[10,1]) #2
  
    top_arc_eyebrows_l =  (df.iloc[105,0],df.iloc[105,1]) #3
    top_arc_eyebrows_r =  (df.iloc[334,0],df.iloc[334,1]) #4
    top_arc_eyebrows_c = (((top_arc_eyebrows_l[0]+top_arc_eyebrows_r[0])/2), ((top_arc_eyebrows_l[1]+top_arc_eyebrows_r[1])/2))

    inside_arc_eyebrows_l =  (df.iloc[55,0],df.iloc[55,1]) #5
    inside_arc_eyebrows_r =  (df.iloc[285,0],df.iloc[285,1]) #6
    outside_arc_eyebrows_l =  (df.iloc[156,0],df.iloc[156,1]) #7
    outside_arc_eyebrows_r =  (df.iloc[383,0],df.iloc[383,1]) #8

    top_of_eyes_l =  (df.iloc[159,0],df.iloc[159,1]) #9
    top_of_eyes_r =  (df.iloc[368,0],df.iloc[368,1]) #10
    top_of_eyes_c = (((top_of_eyes_l[0]+top_of_eyes_r[0])/2), ((top_of_eyes_l[1]+top_of_eyes_r[1])/2))

    center_pupil_l = ((df.iloc[159,0] + df.iloc[160,0] + df.iloc[145,0]+ df.iloc[144,0])/4, 
                    (df.iloc[159,1] + df.iloc[160,1] + df.iloc[145,1]+ df.iloc[144,1])/4) #11
    center_pupil_r = ((df.iloc[385,0] + df.iloc[380,0] + df.iloc[386,0]+ df.iloc[374,0])/4, 
                    (df.iloc[385,1] + df.iloc[380,1] + df.iloc[386,1]+ df.iloc[374,1])/4) #12

    center_pupil_c = (((center_pupil_l[0]+center_pupil_r[0])/2), 
                    ((center_pupil_l[1]+center_pupil_r[1])/2))

    outside_eye_l =  (df.iloc[130,0],df.iloc[226,1]) #13 was 130
    outside_eye_r =  (df.iloc[359,0],df.iloc[359,1]) #14
 
    inside_eye_l =  (df.iloc[133,0],df.iloc[133,1]) #15
    inside_eye_r =  (df.iloc[463,0],df.iloc[463,1]) #16
    inside_eye_c =  ( (inside_eye_l[0] + inside_eye_r[0]/2) , ((inside_eye_l[1] + inside_eye_r[1])/2))

    bottom_of_eyes_l =  (df.iloc[145,0],df.iloc[145,1]) #17
    bottom_of_eyes_r =  (df.iloc[374,0],df.iloc[374,1]) #18
    bottom_of_eyes_c = (((bottom_of_eyes_l[0]+bottom_of_eyes_r[0])/2), ((bottom_of_eyes_l[1]+bottom_of_eyes_r[1])/2))
    side_of_face_l =  (df.iloc[127,0],df.iloc[127,1]) #19
    side_of_face_r =  (df.iloc[447,0],df.iloc[447,1]) #20

    nose_flair_top_l =  (df.iloc[198,0],df.iloc[198,1]) #21
    nose_flair_top_r =  (df.iloc[420,0],df.iloc[420,1]) #22
    nose_flair_top_c = (((nose_flair_top_l[0]+nose_flair_top_r[0])/2), ((nose_flair_top_l[1]+nose_flair_top_r[1])/2))
    nose_nostril_l =  (df.iloc[64,0],df.iloc[64,1])  #23
    nose_nostril_r =  (df.iloc[294,0],df.iloc[294,1])  #24
    nose_nostril_c = (((nose_nostril_l[0]+nose_nostril_r[0])/2), ((nose_nostril_l[1]+nose_nostril_r[1])/2))

    nose_base_l =  (df.iloc[240,0],df.iloc[240,1]) #25
    nose_base_r =  (df.iloc[460,0],df.iloc[460,1]) #26
    nose_base_c = (((nose_base_l[0]+nose_base_r[0])/2), ((nose_base_l[1]+nose_base_r[1])/2))

    
    top_of_lips_l =  (df.iloc[37,0],df.iloc[37,1]) # cupids bow #27
    top_of_lips_r =  (df.iloc[267,0],df.iloc[267,1]) # cupids bow #28
    top_of_lips_c = (((top_of_lips_l[0]+top_of_lips_r[0])/2), ((top_of_lips_l[1]+top_of_lips_r[1])/2))

    middle_of_lips_l =  (df.iloc[57,0],df.iloc[57,1]) #29 mondhoek l
    middle_of_lips_r =  (df.iloc[287,0],df.iloc[287,1]) #30 mondhoek r
    middle_of_lips_c = (((middle_of_lips_l[0]+middle_of_lips_r[0])/2), ((middle_of_lips_l[1]+middle_of_lips_r[1])/2))

    
    center_of_lips =  (df.iloc[14,0],df.iloc[14,1]) #31
    bottom_of_lips =  (df.iloc[17,0],df.iloc[17,1]) #32
    bottom_of_chin = (df.iloc[152,0],df.iloc[152,1]) #33
  
    hoogte_gezicht =  bottom_of_chin[1]-center_face_top[1]
    breedte_gezicht = side_of_face_r[0] -  side_of_face_l[0] 

    nose_zijkant_neusvleugel_l =  (df.iloc[129,0],df.iloc[129,1]) #21
    nose_zijkant_neusvleugel_r =  (df.iloc[331,0],df.iloc[331,1]) #22
    nose_zijkant_neusvleugel_c = (((nose_zijkant_neusvleugel_l[0]+nose_zijkant_neusvleugel_r[0])/2), ((nose_zijkant_neusvleugel_l[1]+nose_zijkant_neusvleugel_r[1])/2))

    v0 = hoogte_gezicht/breedte_gezicht
    width_of_nose = nose_base_r[0]-nose_base_l[0]
    width_of_mouth = middle_of_lips_r[0]-middle_of_lips_l[0]
    print (f"center face top  {center_face_top[1]}, inside eye {inside_eye_c[1]}, nose base {nose_base_c[1]},bottom chin {bottom_of_chin[1]}" )
    A =  inside_eye_c[1] -  center_face_top[1]
    B =  nose_zijkant_neusvleugel_c[1] -   center_pupil_c[1] 
    C =   middle_of_lips_c[1]  - nose_zijkant_neusvleugel_c[1] 
  
    #B =  nose_base_c[1] -   center_pupil_c[1] 
    #C =   middle_of_lips_c[1]  - nose_base_c[1] 
    D = bottom_of_chin[1] - middle_of_lips_c[1]

    score1 = (B+C)/D
    score2 = (A+B)/(C+D)
    score3a = width_of_mouth / width_of_nose #geeft geen goede resultaten
    score3 = ((score1+score2)/2)/1.618*100
    if score3>100:
        score3=1/score3*10000
    txtx = (f"Score 1 {score1} - Score2 {score2}- score3 {round(score3,1)} % ")
    print (txtx)
   
    
    # print (A,B,C)
    # import numpy as np
    # data = [A,B,C]
    # mean2 = np.mean(data) 
    # std2 = np.std(data) 
    # print (std2)
    # score1 = 1-(std2/mean2)
    # print (f"Score op basis van de drie proporties =  {round(score1*100,1)} %" )

            #   B -  A / C - B
    v1 = ((center_of_lips[1] - center_pupil_c[1] )) / ( bottom_of_chin[1] - (center_of_lips[1]))
    v2 = ((nose_nostril_c[1] - center_pupil_c[1] )) / ( bottom_of_chin[1] - (nose_nostril_c[1]))  # ??? Just B is different compared to v1
    v3 = (nose_flair_top_c[1] - center_pupil_c[1] ) / ( nose_base_c[1] - (nose_flair_top_c[1]))
    v4 = ( top_of_eyes_c[1] - top_arc_eyebrows_c [1] ) / ( bottom_of_eyes_c[1] - ( top_of_eyes_c[1]))
    v5 = ((nose_nostril_c[1] - center_pupil_c[1] )) / ( center_of_lips[1] - (nose_nostril_c[1]))
    v6 = ((middle_of_lips_c[1] - top_of_lips_c[1] )) / ( bottom_of_lips[1] - (middle_of_lips_c[1]))
    v7 = ((top_of_lips_c[1] - nose_nostril_c[1] )) / ( center_of_lips[1] - (top_of_lips_c[1])) 
 
            #   B -  A / C - B
    h1 =( side_of_face_r[0]-inside_eye_l[0])/ (inside_eye_l[0] - side_of_face_l[0]) 
    h2 = (inside_eye_l[0] - side_of_face_l[0]) /( inside_eye_r[0]-inside_eye_l[0])
    center_of_face =( ((side_of_face_r[0]-side_of_face_l[0])/2)  +     center_face_top[0]+    bottom_of_chin[0])/3
    h3l = (outside_eye_l[0] - center_of_face ) / (side_of_face_l[0] - outside_eye_l[0])
    h3r = (outside_eye_r[0] - center_of_face ) / (side_of_face_r[0] - outside_eye_r[0])
    h4 = (inside_eye_l[0] - outside_eye_l[0]) /(outside_eye_l[0] - side_of_face_l[0])

    h5 = (outside_eye_l[0]-outside_arc_eyebrows_l[0]) / (outside_arc_eyebrows_l[0] - side_of_face_l[0])

    h6a = (width_of_nose - center_of_face )/ (width_of_mouth-center_of_face)
    h6b = ((width_of_nose/2) - center_of_face )/ ((width_of_mouth/2)-center_of_face)
  
    a0 = (((nose_nostril_l[1] + nose_nostril_r[1])/2) - center_face_top[1]) / (bottom_of_chin[1]  - ((nose_nostril_l[1] + nose_nostril_r[1])/2) )
    a1 = (middle_of_lips_c[1] -(( outside_eye_l[1]+outside_eye_r[1])/2) )/ (bottom_of_chin[1] -middle_of_lips_c[1] )
    outputx=False
    if outputx:
        print  (outside_eye_l[1],outside_eye_r[1])
        #print (f"a0 {a0}")
        print (f"a1 {a1}")
        #print (f"v0 {v0}") # klopt niet omdat de hoogte van het gezicht onjuist is
        print (f"v1 {v1}")
        #print (f"v2 {v2} ????")
        print (f"v3 {v3}")
        print (f"v4 {v4}")
        print (f"v5 {v5}")
        #print (f"v6 {v6}")
        print (f"v7 {v7}")

        
        print (f"h1 {h1}")
        print (f"h2 {h2}")
        #print (f"h3l {h3l}")
        #print (f"h3r {h3r}")
        #print (f"h4 {h4}")
        #print (f"h5 {h5}")
        #print (f"h6a {h6a}")
        #print (f"h6b {h6b}")
        
    gemiddelde = (a1+v1+v3+v4+v5+v7+h1+h2 )/ 8
    score = (gemiddelde / 1.61803398875)
    
    if score>1:
        score = 1/(score)
    
    print (f"Score : {round (score*100,1)} %")
    # draw on photo
    txt = (f"{round(score3,1)} % ")
    ####
    draw_horizontal_lines (url, center_face_top, center_pupil_c, middle_of_lips_c, bottom_of_chin, nose_zijkant_neusvleugel_c, score1, score2, txt)

    draw_vertical_lines(url, outside_eye_l, inside_eye_l, inside_eye_r, outside_eye_r, side_of_face_l, side_of_face_r)

    cv2.destroyAllWindows()

def draw_vertical_lines(url, outside_eye_l, inside_eye_l, inside_eye_r, outside_eye_r, side_of_face_l, side_of_face_r):
    img = cv2.imread(url,cv2.IMREAD_COLOR)
    #font = cv2.FONT_HERSHEY_SIMPLEX
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    ih, iw, ic = img.shape
    

    lv1 = transform_to_value_horizontal(side_of_face_l[0], ih)
    lv2 = transform_to_value_horizontal(outside_eye_l[0] , ih)
    lv3 = transform_to_value_horizontal(inside_eye_l[0], ih)
    lv4 = transform_to_value_horizontal(inside_eye_r[0], ih)
    lv5 = transform_to_value_horizontal(outside_eye_r[0] , ih)
    lv6 = transform_to_value_horizontal(side_of_face_r[0], ih)

    tot = lv6-lv1
    p1 = str(round((lv2-lv1)/tot*100,1))
    p2 = str(round((lv3-lv2)/tot*100,1))
    p3 = str(round((lv4-lv3)/tot*100,1))
    p4 = str(round((lv5-lv4)/tot*100,1))
    p5 = str(round((lv6-lv5)/tot*100,1))

    verh1 = str(round(((lv3-lv2)/(lv2-lv1)),4))
    lines = [lv1,lv2,lv3,lv4,lv5, lv6]
    for l in lines:
        cv2.line(img,(l,0),(l,ih),(255,255,255),1)

    cv2.putText(img,p1,( int(lv1+((lv2-lv1)/4)) , 20), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.putText(img,"1",( int(lv1+((lv2-lv1)/4)) , 50), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.line(img,(lv1,60),(lv3,60),(0,255,255),1)
    cv2.putText(img,p2,( int(lv2+((lv3-lv2)/4)) , 30), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.putText(img,verh1,( int(lv2+((lv3-lv2)/4)) , 50), font, 1, (200,255,155), 1, cv2.LINE_AA)
    
    cv2.putText(img,p3,( int(lv3+((lv4-lv3)/4)) , 20), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.putText(img,p4,( int(lv4+((lv5-lv4)/4)) , 30), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.putText(img,p5,( int(lv5+((lv6-lv5)/4)) , 20), font, 1, (200,255,155), 1, cv2.LINE_AA)
    
    
    cv2.imshow('image',img)
    cv2.waitKey(0)

def draw_horizontal_lines(url, center_face_top, center_pupil_c, middle_of_lips_c, bottom_of_chin, nose_zijkant_neusvleugel_c, score1, score2, txt):
    img = cv2.imread(url,cv2.IMREAD_COLOR)
    #font = cv2.FONT_HERSHEY_SIMPLEX
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    ih, iw, ic = img.shape
    l1 = transform_to_value_vertical(center_face_top[1], ih)
    l2 = transform_to_value_vertical(center_pupil_c[1], ih)
    #l3 = transform_to_value_vertical(nose_base_c[1],ih)
    l3 = transform_to_value_vertical(nose_zijkant_neusvleugel_c[1],ih)
    
    l4 = transform_to_value_vertical(middle_of_lips_c[1],ih)
    l5 = transform_to_value_vertical(bottom_of_chin[1],ih)
    lines = [l1,l2,l3,l4,l5]
    for l in lines:
        cv2.line(img,(0,l),(iw,l),(255,255,255),1)
    cv2.line(img,(10,l2),(10,l4),(255,255,255),1)
    cv2.line(img,(20,l4),(20,l5),(255,255,255),1)
    cv2.putText(img,str(round(score1,3)),(30,int((l2+l4)/2)), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.putText(img,"1",(30,int((l5+l4)/2)), font, 1, (200,255,155), 1, cv2.LINE_AA)

    cv2.putText(img,str(round(score2,3)),(iw-70,int((l1+l3)/2)), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.putText(img,"1",(iw-70,int((l3+l5)/2)), font, 1, (200,255,155), 1, cv2.LINE_AA)

    cv2.line(img,(iw-10,l5),(iw-10,l3),(255,255,255),1)
    cv2.line(img,(iw-20,l1),(iw-20,l3),(255,255,255),1)
            
 
    cv2.putText(img,txt,(100,20), font, 1, (200,255,155), 1, cv2.LINE_AA)
    cv2.imshow('image',img)
    cv2.waitKey(0)
def main():
    #action = "use_already_generated"
    action = "generate"
    if action == "generate":

        img_in1 = r"C:\Users\rcxsm\Documents\python_scripts\OpenCV scripts\Gal_Gadot_by_Gage_Skidmore_4_5000x5921.jpg"
        img_in2 = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\2022c\190378998_10160208309133514_3407449812052869166_n.jpg" #rachel lewins
        img_in3 = r"C:\Users\rcxsm\Pictures\foto vacansoleil2021 vierkant.jpg"
        img_in5 = r"C:\Users\rcxsm\Pictures\pasfoto vierkant.jpg"
        img_in6 = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\gal gadot\FB_IMG_1653833806145.jpg"
        img_in7 =r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\2022c\190378998_10160208309133514_3407449812052869166_n.jpg" #rachel
    
        img_in8 = r"C:\Users\rcxsm\Downloads\FB_IMG_1656775269766.jpg"
        img_in9 = r"C:\Users\rcxsm\Downloads\Screenshot_20220702-145255_Gallery.jpg" #galgadot

        img_in10=r"C:\Users\rcxsm\Downloads\Screenshot_20220702-143356_Chrome.jpg"
        img_in11=r"C:\Users\rcxsm\Downloads\Lengths-of-the-face-and-set-of-ideal-proportions.png"
        img_in12=r"C:\Users\rcxsm\Downloads\florence-colgate-perfect-beautiful-face-golden-ratio.jpg"
        img_in13=r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\extras\images.jpg" #1.618 perfect model
        images_in = [img_in13]#,img_in7, img_in2,img_in12, ] #,img_in4,img_in5, img_in6,img_in7,img_in8,img_in9,img_in10, img_in11,img_in12]
        show_image =True
        save_image = False
        save_csv = False
        img_out =  r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\extras\florence_colgate2_annotated.jpg"
        csv_out = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\extras\florence2.csv"
        
        for img_in in images_in:
            print (f"-------------({img_in})-----------")
            df = generate_df(img_in, show_image, save_image, img_out).set_index(["id"])
            
            if save_csv == True:
                compression_opts = dict(method=None, archive_name=csv_out)
                df.to_csv(csv_out, index=False, compression=compression_opts)
            calculate_beauty(df, img_in)
    elif action == "use_already_generated":
        csv_in = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\extras\landmarks_gal_gadot.csv"
        csv_in = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\extras\landmarks_florence_colgate.csv"
        df = pd.read_csv(csv_in,
                comment="#",
                delimiter=",",
                low_memory=False,
            )
        calculate_beauty(df)
    else:
        print("Error in /action/")
    # print (df)
    

main()
