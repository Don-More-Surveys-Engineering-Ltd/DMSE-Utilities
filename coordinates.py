import math

class NB_coord:
	def __init__(self):
		self.easting=0
		self.northing=0
		self.lat_ddd=0
		self.long_ddd=0
		self.lat_deg=0
		self.lat_min=0
		self.lat_sec=0
		self.long_deg=0
		self.long_min=0
		self.long_sec=0
		self.elev_ellip=0
		self.elev_ortho=0
		self.undulation=0
		
	def __get_grid(self):
		return [self.easting, self.northing]
		
	def __set_grid(self, east, north):
		self.easting=east
		self.northing=north
		return [True]
	
	#def __get_lat_long_ddd
		
	
	
	
# convert Easting and Northing to Latitude and Longitude	
'''def grid_2_geocentric_function(east, north):
	#
	# Need to write this 
	#
	return [lat, lon]
'''
# convert Latitude and Longitude to Easting and Northing
def geocentric2grid(lat, lon):
	east0=2500000
	north0=7500000
	r=6379222.285
	k0=0.999912
	lon0=-66.5
	a_grs80=6378137
	b_grs80=6356752.3141
	ee=(a_grs80*a_grs80-b_grs80*b_grs80)/(a_grs80*a_grs80)
	e=math.sqrt(ee)
	phi0=46.5
	c1=(1+(ee*(math.cos(phi0*math.pi/180))**4)/(1-ee))**0.5
	chi0=math.asin(math.sin(phi0*math.pi/180)/c1)*180/math.pi
	c2=math.tan((45+chi0/2)*math.pi/180)*(math.tan((45+phi0/2)*math.pi/180)*((1-e*math.sin(phi0*math.pi/180))/(1+e*math.sin(phi0*math.pi/180)))**(e/2))**(c1*-1)
	a1=math.sin(lat*math.pi/180)
	a2=((1-e*a1)/(1+e*a1))**(e/2)
	a4=math.tan((45+lat/2)*math.pi/180)
	chi=c2*(a2*a4)**c1
	chi=(math.atan(chi)*180/math.pi-45)*2
	lamda=c1*lon
	lamda0=c1*lon0
	delta_lamda=lamda-lamda0
	sin_delta_lamda=math.sin(delta_lamda*math.pi/180)
	cos_delta_lamda=math.cos(delta_lamda*math.pi/180)
	sin_chi=math.sin(chi*math.pi/180)
	cos_chi=math.cos(chi*math.pi/180)
	sin_chi0=math.sin(chi0*math.pi/180)
	cos_chi0=math.cos(chi0*math.pi/180)
	east=east0+(2*k0*r*cos_chi*sin_delta_lamda)/(1+sin_chi*sin_chi0+cos_chi*cos_chi0*cos_delta_lamda)
	north=north0+(2*k0*r*(sin_chi*cos_chi0-cos_chi*sin_chi0*cos_delta_lamda))/(1+sin_chi*sin_chi0+cos_chi*cos_chi0*cos_delta_lamda)
	return [east, north]

def ddd2dms(ddd):
	"""Converts decimal format to degrees-minutes-seconds"""
	deg=int(ddd)
	mins=int((ddd-deg)*60)
	sec=((ddd-deg)*60-mins)*60
	if ddd>0:
		return [deg, mins, sec]
	else:
		return [deg, mins*-1, sec*-1]

def dms2ddd(deg, mins, sec):
	"""Convert degrees-minutes-seconds to decimal format"""
	if deg>0:
		return deg+mins/60+sec/3600
	else:
		return deg-mins/60-sec/3600
		
		
	
