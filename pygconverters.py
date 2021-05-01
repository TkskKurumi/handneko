import pygame,mymath,ctypes,pic2pic
from PIL import Image
#杂项
def PIL2surface(im):
	return pygame.image.fromstring(im.tobytes(),im.size,im.mode)
def surface2PIL(surf):
	return Image.frombytes("RGBA",surf.get_size(),pygame.image.tostring(surf, "RGBA",False))
def cv22surface(cv2img):
	return PIL2surface(pic2pic.cv22pil(cv2img))
def blit_alpha(target,source,location,opacity):					#pygame透明blit
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(),source.get_height())).convert()
    temp.blit(target,(-x,-y))
    temp.blit(source,(0,0))
    temp.set_alpha(opacity)
    target.blit(temp,location)
class dick:
	def __init__(self,dic):
		for i in dic:
			exec('self.%s=dic["%s"]'%(i,i))
		self.original_dic=dic
	def get(self,k,default):
		return self.original_dic.get(k,default)
	def __getitem__(self,k):
		return self.original_dic[k]
	def __setitem__(self,i,v):
		self.original_dic[i]=v
		exec('self.%s=eval(v)'%i)
	def __contains__(self,k):
		return k in self.original_dic
def resize_by_ratio(im,r,interpolation=Image.BILINEAR):
	if(mymath.aequal(r,1)):
		return im
	w,h=[int(i*r) for i in im.size]
	return im.resize((w,h),interpolation)

def get_screen_size():
	return [ctypes.windll.user32.GetSystemMetrics(i) for  i in range(2)]
if(__name__=='__main__'):
	print(get_screen_size())