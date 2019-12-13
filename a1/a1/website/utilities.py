import os
import cv2

def list_tupples(a,b):
    list_tupple=[]
    temp=[]
    count=0
    for i in a:
        temp.append(i)
        count+=1
        if count==b:
            count=0
            list_tupple.append(temp)
            temp=[]
            
    if (temp not in list_tupple) and temp != []:
        list_tupple.append(temp)

    return list_tupple
        

def create_thumbnail(image_path, thumbnail_path, s3):
    temp=image_path.split('/')
    img_name=temp[-1]
    image = cv2.imread(image_path)
    try:
        image2 = cv2.resize(image,(100,100))
    except:
        image = cv2.imread('sample.png')
        image2 = cv2.resize(image,(100,100))
        
    output_file = thumbnail_path + img_name
    
    cv2.imwrite(output_file,image2)
    #Store in S3 instead of local filesystem
    s3.upload_file(output_file, 'my-test-bucket-ece1779', 'thumbnails/{}'.format(img_name))

    # Remove file from temporary local storage
    if os.path.isfile(output_file):
        #os.remove(output_file)
        pass
    return


def load_html_page(file_path):
    with open(file_path,'r') as fp:
        web_content= fp.read()

    return web_content




