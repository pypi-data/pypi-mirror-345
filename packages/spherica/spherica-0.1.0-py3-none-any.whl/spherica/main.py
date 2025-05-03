import math as _math
import re
class Spheric:
 def __init__(self, *args):
  if args == (0,):
   self._t = self._p = self._s = self._x = self._y = self._z = .0
   self._w = 1.0
   return 
  self._t = self._p = self._s = self._w = self._x = self._y = self._z = None
  match len(args):
   case 3:
    self._t = args[0]
    t_rolled = (self._t/_math.pi % 2 >= 1)
    self._t %= _math.pi
    t_invariant = (self._t == 0)
    if t_rolled: self._t = _math.pi-self._t
    if t_invariant:
     self._p = .0
     self._s = .0
     return 
    self._p = args[1]
    if t_rolled: self._p += _math.pi
    p_rolled = (self._p/_math.pi % 2 >= 1)
    self._p %= _math.pi
    p_invariant = (self._p == 0)
    if p_rolled: self._p = _math.pi-self._p
    if p_invariant:
     self._s = .0
     return 
    self._s = args[2]
    if p_rolled: self._s += _math.pi
    self._s %= 2*_math.pi
   case 4:
    self._w, self._x, self._y, self._z = args
    if (s := self._w**2 + self._x**2 + self._y**2 + self._z**2) != 1:
     scale = 1/_math.sqrt(s)
     self._w *= scale
     self._x *= scale
     self._y *= scale
     self._z *= scale
    
   case _: raise ValueError('Provide either 0, (θ, φ, ψ) or (w, x, y, z)')
  
 @property
 def theta(self):
  if self._t is None: self._t = _math.acos(max(min(self._w,1),-1))
  return self._t
 @property
 def phi(self):
  if self._p is None:
   if (self._t is not None and self._t % _math.pi == 0) or abs(self._w) == 1 or (self._y == 0 and self._z == 0): self._p = .0
   else:
    if self._t is not None: s = _math.sin(self._t)
    else: s = _math.sqrt(1-self._w**2)
    self._p = _math.acos(max(min(self._x/s,1),-1))
   
  return self._p
 @property
 def psi(self):
  if self._s is None:
   if (self._p is not None and self._p % _math.pi == 0): self._s = 0
   else: self._s = _math.atan2(self._z,self._y)
  self._s %= 2*_math.pi
  return self._s
 @property
 def w(self):
  if self._w is None: self._w = _math.cos(self._t)
  return self._w
 @property
 def x(self):
  if self._x is None: self._x = _math.sin(self._t)*_math.cos(self._p)
  return self._x
 @property
 def y(self):
  if self._y is None: self._y = _math.sin(self._t)*_math.sin(self._p)*_math.cos(self._s)
  return self._y
 @property
 def z(self):
  if self._z is None: self._z = _math.sin(self._t)*_math.sin(self._p)*_math.sin(self._s)
  return self._z
 def __repr__(self) : return f'{self}'
 def __format__(self, format_spec):
  if re.match(r'^(.\d+)?[GgFf][ca]$', format_spec):
   type = format_spec[-2]
   digits = format_spec[:-2]
   if format_spec[-1] == 'c': return f'Spheric({{:{digits}{type}}}, {{:{digits}{type}}}, {{:{digits}{type}}}, {{:{digits}{type}}})'.format(self.w, self.x, self.y, self.z)
   else : return f'Spheric({{:{digits}{type}}}, {{:{digits}{type}}}, {{:{digits}{type}}})'.format(self.theta, self.phi, self.psi)
  return f'{self:.3ga}'
 def angles(self) : return self.theta, self.phi, self.psi
 def cartesian(self) : return self.w, self.x, self.y, self.z
 def __add__(self, other):
  if not isinstance(other, Spheric): raise ValueError('Both operands must be Spheric')
  return Spheric (self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w)
 def __neg__(self):
  if self._s is None : return Spheric(self.w, -self.x, -self.y, -self.z)
  return Spheric(-self.theta, self.phi, self.psi)
 def __invert__(self):
  if self._s is None : return Spheric(-self.w, -self.x, -self.y, -self.z)
  return Spheric(_math.pi-self.theta, _math.pi-self.phi, self.psi+_math.pi)
 def __sub__(self, other):
  return self + (-other)
 def __or__(self, other):
  if not isinstance(other, Spheric): raise ValueError('Both operands must be Spheric')
  return _math.acos(max(min(self.w*other.w+self.x*other.x+self.y*other.y+self.z*other.z,1.0),-1.0))
 def __matmul__(self, fov):
  if not isinstance(fov, int|float): raise ValueError('FOV must be a float or int')
  scale = _math.tan(self.phi)/_math.tan(fov/2)
  return (_math.cos(self.psi)*scale,_math.sin(self.psi)*scale)
 def __mul__(self, k) : return k*self
 def __truediv__(self, k):
  if not isinstance(k, int|float): raise ValueError('Divisor must be a float or int')
  return 1/k*self
 def __rmul__(self, k):
  if (self._t is not None and self._t == 0) or self.w == 1 : return self
  if not isinstance(k, int|float): raise ValueError('Coefficient must be a float or int')
  if (self._t is not None and self._t == _math.pi) or self.w == -1:
   if k % 1 != 0: raise ValueError('Cannot scale an antipodal Spheric')
   elif k % 2 == 0 : return Spheric(0)
   else : return self
  if self._s is None:
   c = 1/_math.sin(self.theta)
   s = _math.sin(k*self.theta)*c
   return Spheric(_math.sin((1-k)*self.theta)*c+self.w*s,self.x*s,self.y*s,self.z*s)
  else : return Spheric(self.theta * k,self.phi,self.psi)
 def __abs__(self) : return self.theta
 def __eq__(self, other) : return abs((self - other).w-1) < 0.1
 def __rshift__(self, other) : return _SphericInterpolator(self, other)
class _SphericInterpolator:
 def __init__(self, q1, q2):
  if not (isinstance(q1, Spheric) and isinstance(q2, Spheric)): raise ValueError('Both operands must be Spheric')
  self._p1 = q1.cartesian()
  self._p2 = q2.cartesian()
  self._angle = q1 | q2
  self._discrete = self._angle == _math.pi
 @property
 def start(self) : return Spheric(*self._p1)
 @property
 def end(self) : return Spheric(*self._p2)
 def __call__(self, t):
  if self._discrete:
   if t % 1 != 0: raise ValueError('Cannot interpolate between antipodal Spherics')
   if t % 2 == 0 : return Spheric(*self._p1)
   return Spheric(*self._p2)
  if self._angle == 0 : return Spheric(*self._p1)
  c = 1/_math.sin(self._angle)
  o = _math.sin(t*self._angle)*c
  s = _math.sin((1-t)*self._angle)*c
  return Spheric(self._p1[0]*s+self._p2[0]*o,self._p1[1]*s+self._p2[1]*o,self._p1[2]*s+self._p2[2]*o,self._p1[3]*s+self._p2[3]*o)
 def __repr__(self) : return f'SphericInterpolator[({self._p1[0]:.3g}, {self._p1[1]:.3g}, {self._p1[2]:.3g}, {self._p1[3]:.3g}) >> ({self._p2[0]:.3g}, {self._p2[1]:.3g}, {self._p2[2]:.3g}, {self._p2[3]:.3g})]'

