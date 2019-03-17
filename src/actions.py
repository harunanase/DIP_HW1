from PIL import Image, ImageTk
import image_api


def load_imageTk(pilImage):
    return ImageTk.PhotoImage(pilImage)



def do_contrast(img, contrastType, scalarLevel):
    
    imgApi = image_api.ImageAPI()
    if(contrastType == "linear"):
        return imgApi.linear_contrast(img, scalarLevel)
    elif(contrastType == "exp"):
        return imgApi.exp_contrast(img, scalarLevel)
    elif(contrastType == "log"):
        return imgApi.log_contrast(img, scalarLevel)
    else:
        raise AppError('GUI apply button value error')
        return None


def do_zoom(img, rate):
    
    imgApi = image_api.ImageAPI()
    newWidth = int(img.width * rate)
    newHeight = int(img.height * rate)
    return imgApi.bilinear_resize(img, (newWidth, newHeight))
    

def do_histogram(img):
    imgApi = image_api.ImageAPI()
    before, after, adjusted = imgApi.histogram_equalization(img)

    return before, after, adjusted
