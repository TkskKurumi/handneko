import numpy as np
import cv2,time,random
from myGeometry import point
from math import pi
import pic2pic
from pygconverters import *
import pygame.locals as pyglocals
import pygame
from os import path
from PIL import Image
pth=path.dirname(__file__).replace(r'lib\library.zip','')
last_frame=None
cap=cv2.VideoCapture(0)
lastt=time.time()
p1=point(0,0)
p2=point(1,1)
smoothp1=point(0,0)
smoothp2=point(1,1)
width,height=640,None

textures={}
def get_texture(s):												#读取贴图
	global textures	
	ext=path.splitext(s)[1]
	if(ext.lower()=='.gif'):
		if(s not in textures):
			ss=path.join(pth,'textures',s)
			textures[s]=dick({"imgs":extract_gif.extract_gif(ss),"fps":extract_gif.get_fps(ss)})
		frame=int(time.time()*textures[s].fps)%len(textures[s].imgs)
		return textures[s].imgs[frame]
	else:
		if(s not in textures):
			ss=path.join(pth,'textures',s)
			textures[s]=Image.open(ss)
		return textures[s]

def blit_alpha(target,source,location,opacity):					#pygame透明blit
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(),source.get_height())).convert()
    temp.blit(target,(-x,-y))
    temp.blit(source,(0,0))
    temp.set_alpha(opacity)
    target.blit(temp,location)
opt=0	#0:change_bgmode
bg_mode=0	#0:original,1:green
last_shown_hint=''
hint="Welcome"
hints=['改变背景类型']
bg_mode_hints=['原本','绿幕']
hint_duration=2.5
flag=True
while(flag):
	ret,frame=cap.read()
	#frame=cv2.flip(frame,-1)
	framedark=(frame/3).astype(np.uint8)
	dt=time.time()-lastt
	lastt=time.time()
	fps=(1/dt) if dt else 0
	if(last_frame is None):
		last_frame=frame
	delta=frame.astype(np.int32)-last_frame.astype(np.int32)
	delta=np.abs(delta)
	delta_gray=np.sum(delta,axis=2)
	h,w=delta_gray.shape
	if(height is None):
		height=width*h//w
		pygame.init()
		screen=pygame.display.set_mode((width,height),pyglocals.RESIZABLE,32)
		pygame.display.set_caption('handrig')
	for event in pygame.event.get():
		if(event.type==pyglocals.KEYDOWN):
			key=event.key
			if(key==pyglocals.K_q):
				opt=(opt-1)%len(hints)
				hint=hints[opt]
			elif(key==pyglocals.K_e):
				opt=(opt+1)%len(hints)
				hint=hints[opt]
			elif(key==pyglocals.K_DOWN):
				if(opt==0):
					bg_mode=(bg_mode-1)%len(bg_mode_hints)
					hint=bg_mode_hints[bg_mode]
			elif(key==pyglocals.K_UP):
				if(opt==0):
					bg_mode=(bg_mode-1)%len(bg_mode_hints)
					hint=bg_mode_hints[bg_mode]
			elif(key==pyglocals.K_ESCAPE):
				flag=False
	sprites=[]
	screen.fill((0,0,0))
	if(hint!=last_shown_hint):
		print('ln65')
		last_shown_hint=hint
		hint_alpha=hint_duration*255
		hint_image=pic2pic.txt2im(hint,fixedHeight=width//30,bg=(0,)*4,fill=(255,233,0,255))
		#hint_image.show()
		#exit()
	
	if(bg_mode==0):
		p=pic2pic.cv22pil(framedark).resize((width,height))
		sprites.append((p,p.size[0]/2,p.size[1]/2,*p.size,0,255))
	elif(bg_mode==1):
		screen.fill((0,255,0))
		
		
	for p in [smoothp1,smoothp2]:
		p=p*width/w
		if(p.x<width/2):
			pic=get_texture('hand.png')
		else:
			pic=get_texture('hand.png').transpose(Image.FLIP_LEFT_RIGHT)
		pic=pic2pic.fixWidth(pic,width//3)
		sprites.append((pic,p.x,p.y,*pic.size,0,255))
	#sprites.append((pic2pic.cv22pil(frame),233,233,233,233
	hint_alpha-=dt*255
	sprites.append((hint_image,hint_image.size[0]/2,hint_image.size[1]/2,*hint_image.size,0,min(hint_alpha,255)))
	for s,x,y,w,h,rot,alpha in sprites:
		#print(x,y,w,h)
		if(isinstance(s,str)):
			pic=get_texture(s,rot,1)
		elif(isinstance(s,Image.Image)):
			pic=s
		if((w,h)!=pic.size):
			pic=pic.resize((w,h))
		surf=PIL2surface(pic)
		if(alpha<250):
			blit_alpha(screen,surf,(int(x-surf.get_width()/2),int(y-surf.get_height()/2)),alpha)
		else:
			screen.blit(surf,(int(x-surf.get_width()/2),int(y-surf.get_height()/2)))
	pygame.display.flip()
	
	
	#print(delta_gray.shape)
	thresh=delta_gray>300
	#print(thresh.dtype)
	thresh=cv2.erode(thresh.astype(np.uint8), np.ones((3,3),np.uint8))
	#sm=np.sum(thresh)
	ys,xs=np.nonzero(thresh)
	n=ys.shape[0]
	az=list(range(n))
	if(n>=30):
		az=random.sample(az,30)
		n=30
	newp1=point(0,0)
	newp2=point(0,0)
	np1=0
	np2=0
	for idx in az:
		p=point(xs[idx],ys[idx])
		weight=delta_gray[ys[idx],xs[idx]]
		if(p.dist(p1)<p.dist(p2)):
			#p1=p1+(p-p1)/n*2#*dt*10
			newp1+=p*float(weight)
			np1+=weight
		else:
			#p2=p2+(p-p2)/n*2#*dt*10
			newp2+=p*float(weight)
			np2+=weight
	if(np1):
		p1=newp1/np1
	if(np2):
		p2=newp2/np2
	smoothp1+=(p1-smoothp1)*min(dt*10,0.7)
	smoothp2+=(p2-smoothp2)*min(dt*10,0.7)
	
	last_frame=frame.copy()
	#cv2.circle(frame,(int(p1.x),int(p1.y)),10,(0,255,0),3)
	#cv2.circle(frame,(int(p2.x),int(p2.y)),10,(230,170,0),3)
	
	cv2.circle(framedark,(int(smoothp1.x),int(smoothp1.y)),10,(0,255,0),3)
	cv2.circle(framedark,(int(smoothp2.x),int(smoothp2.y)),10,(230,170,0),3)
	print('fps=%.1f'%fps,hint_alpha,end='\r')
	#cv2.imshow("frame",frame)
	cv2.imshow("framedark",framedark)
	cv2.imshow("az",thresh.astype(np.uint8)*255)
	#cv2.imshow("delta_gray",delta_gray.astype(np.uint8))
	k = cv2.waitKey(2) & 0xff
	if k == 27:
		break
cv2.destroyAllWindows()
cap.release()