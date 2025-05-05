import math as _math
import re
from copy import copy as _copy
class Spheric:
 def __init__(self, *args):
  if args == (0,):
   self.__t = self.__p = self.__s = self.__x = self.__y = self.__z = .0
   self.__w = 1.
   return 
  self.__t = self.__p = self.__s = self.__w = self.__x = self.__y = self.__z = None
  match len(args):
   case 3:
    for i in args:
     if not isinstance(i, int|float): raise TypeError('Angles must be numerical')
     if _math.isnan(i) or _math.isinf(i): raise ValueError('Angles cannot be ±inf or NaN')
     
    self.__t = args[0]
    t_rolled = (self.__t/_math.pi % 2 >= 1)
    self.__t %= _math.pi
    t_invariant = (self.__t == 0)
    if t_rolled: self.__t = _math.pi-self.__t
    if t_invariant:
     self.__p = .0
     self.__s = .0
     return 
    self.__p = args[1]
    if t_rolled: self.__p += _math.pi
    p_rolled = (self.__p/_math.pi % 2 >= 1)
    self.__p %= _math.pi
    p_invariant = (self.__p == 0)
    if p_rolled: self.__p = _math.pi-self.__p
    if p_invariant:
     self.__s = .0
     return 
    self.__s = args[2]
    if p_rolled: self.__s += _math.pi
    self.__s %= 2*_math.pi
   case 4:
    for i in args:
     if not isinstance(i, int|float): raise TypeError('Coordinates must be numerical')
     if _math.isnan(i) or _math.isinf(i): raise ValueError('Coordinates cannot be ±inf or NaN')
     
    self.__w, self.__x, self.__y, self.__z = args
    if (s := self.__w**2 + self.__x**2 + self.__y**2 + self.__z**2) != 1:
     if s == 0: raise ValueError('(0, 0, 0, 0) is not normalizable')
     scale = 1/_math.sqrt(s)
     self.__w *= scale
     self.__x *= scale
     self.__y *= scale
     self.__z *= scale
    
   case _: raise ValueError('Provide either 0, (θ, φ, ψ) or (w, x, y, z)')
  
 def __use_c(self) : return (self.__t is None) + (self.__p is None) + (self.__s is None) > 1
 @property
 def theta(self):
  if self.__t is None: self.__t = _math.acos(max(min(self.__w,1),-1))
  return self.__t
 @theta.setter
 def theta(self, val):
  a = list(self.angles())
  a[0] = val
  self.__init__(*a)
 @property
 def phi(self):
  if self.__p is None:
   if (self.__t is not None and self.__t % _math.pi == 0) or abs(self.__w) == 1 or (self.__y == 0 and self.__z == 0): self.__p = .0
   else:
    if self.__t is not None: s = _math.sin(self.__t)
    else: s = _math.sqrt(1-self.__w**2)
    self.__p = _math.acos(max(min(self.__x/s,1.),-1.))
   
  return self.__p
 @phi.setter
 def phi(self, val):
  a = list(self.angles())
  a[1] = val
  self.__init__(*a)
 @property
 def psi(self):
  if self.__s is None:
   if (self.__p is not None and self.__p % _math.pi == 0): self.__s = 0
   else: self.__s = _math.atan2(self.__z,self.__y)
  self.__s %= 2*_math.pi
  return self.__s
 @psi.setter
 def psi(self, val):
  a = list(self.angles())
  a[2] = val
  self.__init__(*a)
 @property
 def w(self):
  if self.__w is None: self.__w = _math.cos(self.__t)
  return self.__w
 @w.setter
 def w(self, val):
  c = list(self.cartesian())
  c[0] = val
  self.__init__(*c)
 @property
 def x(self):
  if self.__x is None: self.__x = _math.sin(self.__t)*_math.cos(self.__p)
  return self.__x
 @x.setter
 def x(self, val):
  c = list(self.cartesian())
  c[1] = val
  self.__init__(*c)
 @property
 def y(self):
  if self.__y is None: self.__y = _math.sin(self.__t)*_math.sin(self.__p)*_math.cos(self.__s)
  return self.__y
 @y.setter
 def y(self, val):
  c = list(self.cartesian())
  c[2] = val
  self.__init__(*c)
 @property
 def z(self):
  if self.__z is None: self.__z = _math.sin(self.__t)*_math.sin(self.__p)*_math.sin(self.__s)
  return self.__z
 @z.setter
 def z(self, val):
  c = list(self.cartesian())
  c[3] = val
  self.__init__(*c)
 def __repr__(self) : return f'{self}'
 def __format__(self, format_spec):
  if re.match(r'^(.\d+)?[GgFf][cAa]$', format_spec):
   type = format_spec[-2]
   digits = format_spec[:-2]
   match format_spec[-1]:
    case 'c' : return f'Spheric({{:{digits}{type}}}, {{:{digits}{type}}}, {{:{digits}{type}}}, {{:{digits}{type}}})'.format(self.w, self.x, self.y, self.z)
    case 'a' : return f'Spheric({{:{digits}{type}}}, {{:{digits}{type}}}, {{:{digits}{type}}})'.format(self.theta, self.phi, self.psi)
    case _ : return f'Spheric({{:{digits}{type}}}π, {{:{digits}{type}}}π, {{:{digits}{type}}}π)'.format(self.theta/_math.pi, self.phi/_math.pi, self.psi/_math.pi)
   
  return f'{self:.3ga}'
 def angles(self) : return self.theta, self.phi, self.psi
 def cartesian(self) : return self.w, self.x, self.y, self.z
 def __add__(self, other):
  if not isinstance(other, Spheric): raise TypeError('Both operands must be Spheric')
  return Spheric (self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w)
 def __neg__(self):
  if self.__use_c() : return Spheric(self.w, -self.x, -self.y, -self.z)
  return Spheric(-self.theta, self.phi, self.psi)
 def __invert__(self):
  if self.__use_c() : return Spheric(-self.w, -self.x, -self.y, -self.z)
  return Spheric(_math.pi-self.theta, _math.pi-self.phi, self.psi+_math.pi)
 def __sub__(self, other) : return self + (-other)
 def __or__(self, other):
  if not isinstance(other, Spheric): raise TypeError('Both operands must be Spheric')
  return _math.acos(self & other)
 def __matmul__(self, fov):
  if not isinstance(fov, int|float): raise TypeError('FOV must be numerical')
  scale = _math.tan(self.phi)/_math.tan(fov/2)
  return (_math.cos(self.psi)*scale,_math.sin(self.psi)*scale)
 def __and__(self, other):
  if not isinstance(other, Spheric): raise TypeError('Both operands must be Spheric')
  return max(min(self.w*other.w+self.x*other.x+self.y*other.y+self.z*other.z,1.),-1.)
 def __mul__(self, k) : return k*self
 def __truediv__(self, k):
  if not isinstance(k, int|float): raise TypeError('Divisor must be numerical')
  return 1/k*self
 def __rmul__(self, k):
  if not isinstance(k, int|float): raise TypeError('Coefficient must be numerical')
  if (self.__t is not None and self.__t == 0) or self.w == 1 : return self
  if (self.__t is not None and self.__t == _math.pi) or self.w == -1:
   if k % 1 != 0: raise ValueError('Cannot scale an antipodal Spheric')
   elif k % 2 == 0 : return Spheric(0)
   else : return self
  if self.__use_c():
   c = 1/_math.sin(self.theta)
   s = _math.sin(k*self.theta)*c
   return Spheric(_math.sin((1-k)*self.theta)*c+self.w*s,self.x*s,self.y*s,self.z*s)
  else : return Spheric(self.theta * k,self.phi,self.psi)
 def __abs__(self) : return self.theta
 def __eq__(self, other) : return self & other == 1
 def __rshift__(self, other) : return _SphericInterpolator(self, other)
 def __xor__(self, other) : return _AngleConstructor(self, other)
 def __pos__(self) : return _copy(self)
 
class _SphericInterpolator:
 def __init__(self, q1, q2):
  if not (isinstance(q1, Spheric) and isinstance(q2, Spheric)): raise TypeError('Both operands must be Spheric')
  self.__p1 = q1.cartesian()
  self.__p2 = q2.cartesian()
  self.__angle = q1 | q2
  self.__discrete = self.__angle == _math.pi
 @property
 def start(self) : return Spheric(*self.__p1)
 @property
 def end(self) : return Spheric(*self.__p2)
 def __call__(self, t):
  if not isinstance(t, int|float): raise TypeError('t-value must be numerical')
  if self.__discrete:
   if t % 1 != 0: raise ValueError('Cannot interpolate between antipodal Spherics')
   if t % 2 == 0 : return Spheric(*self.__p1)
   return Spheric(*self.__p2)
  if self.__angle == 0 : return Spheric(*self.__p1)
  c = 1/_math.sin(self.__angle)
  o = _math.sin(t*self.__angle)*c
  s = _math.sin((1-t)*self.__angle)*c
  return Spheric(self.__p1[0]*s+self.__p2[0]*o,self.__p1[1]*s+self.__p2[1]*o,self.__p1[2]*s+self.__p2[2]*o,self.__p1[3]*s+self.__p2[3]*o)
 def __repr__(self) : return f'SphericInterpolator[({self.__p1[0]:.3g}, {self.__p1[1]:.3g}, {self.__p1[2]:.3g}, {self.__p1[3]:.3g}) >> ({self.__p2[0]:.3g}, {self.__p2[1]:.3g}, {self.__p2[2]:.3g}, {self.__p2[3]:.3g})]'
class _AngleConstructor:
 def __init__(self, q1, q2):
  if not (isinstance(q1, Spheric) and isinstance(q2, Spheric)): raise TypeError('Both operands must be Spheric')
  self.__dot = q1 & q2
  self.__eq = self.__dot == 1
  self.__p1 = q1.cartesian()
  self.__p2 = q2.cartesian()
 @property
 def start(self) : return Spheric(*self.__p1)
 @property
 def end(self) : return Spheric(*self.__p2)
 def __call__(self, q):
  if not isinstance(q, Spheric): raise TypeError('Angle vertex must be Spheric')
  if self.__eq : return .0
  q = q.cartesian()
  dot = lambda a,b: a[0]*b[0]+a[1]*b[1]+a[2]*b[2]+a[3]*b[3]
  a = dot(self.__p1,q)
  b = dot(self.__p2,q)
  sa = _math.sqrt(1-a**2)
  sb = _math.sqrt(1-b**2)
  S = sa*sb
  if S == 0: raise ValueError('Angle vertex cannot be equal to endpoint')
  return _math.acos(max(min((self.__dot-a*b)/S,1.),-1.))
 def __repr__(self) : return f'AngleConstructor[({self.__p1[0]:.3g}, {self.__p1[1]:.3g}, {self.__p1[2]:.3g}, {self.__p1[3]:.3g}) ^ ({self.__p2[0]:.3g}, {self.__p2[1]:.3g}, {self.__p2[2]:.3g}, {self.__p2[3]:.3g})]'

