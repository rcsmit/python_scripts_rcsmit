# code adapted from https://stackoverflow.com/questions/67141844/python-how-to-get-face-mesh-landmarks-coordinates-in-mediapipe
# added dataframe as output and an annotated image as output 

import cv2
import mediapipe as mp
import pandas as pd

def generate_df():
  mp_drawing = mp.solutions.drawing_utils
  mp_face_mesh = mp.solutions.face_mesh

  df = pd.DataFrame()
  # file can be found at https://github.com/rcsmit/python_scripts_rcsmit/blob/master/extras/Gal_Gadot_by_Gage_Skidmore_4_5000x5921.jpg
  file_list = [r"C:\Users\rcxsm\Documents\python_scripts\OpenCV scripts\Gal_Gadot_by_Gage_Skidmore_4_5000x5921.jpg"]
  # For static images:
  drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
  with mp_face_mesh.FaceMesh(
      static_image_mode=True,
      min_detection_confidence=0.5) as face_mesh:
    for idx, file in enumerate(file_list):
      image = cv2.imread(file)
      # Convert the BGR image to RGB before processing.
      results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

      # Print and draw face mesh landmarks on the image.
      if not results.multi_face_landmarks:
        continue
      annotated_image = image.copy()
      #for face_landmarks in results.multi_face_landmarks:
        #print('face_landmarks:', face_landmarks)
        # mp_drawing.draw_landmarks(
        #     image=annotated_image,
        #     landmark_list=face_landmarks,
        #     connections=mp_face_mesh.FACEMESH_CONTOURS,
        #     landmark_drawing_spec=drawing_spec,
        #     connection_drawing_spec=drawing_spec)

      for face in results.multi_face_landmarks:
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

              font = cv2.FONT_HERSHEY_SIMPLEX
              font = cv2.FONT_HERSHEY_COMPLEX_SMALL
              cv2.putText(image,str(i),(relative_x, relative_y), font, 1, (255,255,255), 1, cv2.LINE_AA)
      # cv2.imshow('image',image)
      
      # filename = r"C:\Users\rcxsm\Documents\python_scripts\OpenCV scripts\Gal_Gadot_by_Gage_Skidmore_4_5000x5921_annotated_white_letters.jpg"
      # cv2.waitKey(0)
      # cv2.imwrite(filename, image)
      # cv2.destroyAllWindows()
      
      return df

def main():
  name_ = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\extras\landmarks_gal_gadot.csv"
  
  # Generate and save a dataframe with the coordinates
  df = generate_df().set_index(["id"])
  compression_opts = dict(method=None, archive_name=name_)
  df.to_csv(name_, index=False, compression=compression_opts)

  # use a pre-generated dataframe
  # df = pd.read_csv(name_,
  #       comment="#",
  #       delimiter=",",
  #       low_memory=False,
  #   )
  
  print (df)

main()
