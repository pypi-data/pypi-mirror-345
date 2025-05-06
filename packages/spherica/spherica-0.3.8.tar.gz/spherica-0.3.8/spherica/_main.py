import math as _math
from copy import copy as _copy
class Spheric:
 def __init__(self, *args: int|float):
  if args == (0,):
   self.__t = self.__p = self.__s = self.__x = self.__y = self.__z = .0
   self.__w = 1.
   return 
  self.__t = self.__p = self.__s = self.__w = self.__x = self.__y = self.__z = None
  match len(args):
   case 3:
    for n, i in enumerate(args):
     if not isinstance(i, int|float): raise TypeError(f'Angles must be numerical, but got {["θ","φ","ψ"][n]} of type \'{type(i).__name__}\'')
     if _math.isnan(i) or _math.isinf(i): raise ValueError(f'Angles cannot be ±inf or NaN, but got {["θ","φ","ψ"][n]} = {i}')
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
    for n, i in enumerate(args):
     if not isinstance(i, int|float): raise TypeError(f'Coordinates must be numerical, but got {["w","x","y","z"][n]} of type \'{type(i).__name__}\'')
     if _math.isnan(i) or _math.isinf(i): raise ValueError(f'Coordinates cannot be ±inf or NaN, but got {["w","x","y","z"][n]} = {i}')
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
 def theta(self, val): self.__init__(val, self.phi, self.psi)
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
 def phi(self, val): self.__init__(self.theta, val, self.psi)
 @property
 def psi(self):
  if self.__s is None:
   if self.__p is not None and self.__p % _math.pi == 0: self.__s = 0
   else: self.__s = _math.atan2(self.__z,self.__y)
  self.__s %= 2*_math.pi
  return self.__s
 @psi.setter
 def psi(self, val): self.__init__(self.theta, self.phi, val)
 @property
 def w(self):
  if self.__w is None: self.__w = _math.cos(self.__t)
  return self.__w
 @w.setter
 def w(self, val): self.__init__(val, self.x, self.y, self.z)
 @property
 def x(self):
  if self.__x is None: self.__x = _math.sin(self.__t)*_math.cos(self.__p)
  return self.__x
 @x.setter
 def x(self, val): self.__init__(self.w, val, self.y, self.z)
 @property
 def y(self):
  if self.__y is None: self.__y = _math.sin(self.__t)*_math.sin(self.__p)*_math.cos(self.__s)
  return self.__y
 @y.setter
 def y(self, val): self.__init__(self.w, self.x, val, self.z)
 @property
 def z(self):
  if self.__z is None: self.__z = _math.sin(self.__t)*_math.sin(self.__p)*_math.sin(self.__s)
  return self.__z
 @z.setter
 def z(self, val): self.__init__(self.w, self.x, self.z, val)
 def __repr__(self) : return f'{self}'
 def __format__(self, format_spec):
  floatform = '.3g' if ((s := format_spec.rstrip('cAa')) == '') else s
  style = s if len(format_spec) != 0 and ((s := format_spec[-1]) in 'cAa') else 'a'
  match style:
   case 'c' : return f'Spheric({{:{floatform}}}, {{:{floatform}}}, {{:{floatform}}}, {{:{floatform}}})'.format(self.w, self.x, self.y, self.z)
   case 'a' : return f'Spheric({{:{floatform}}}, {{:{floatform}}}, {{:{floatform}}})'.format(self.theta, self.phi, self.psi)
   case _:
    scale = 1/_math.pi
    return f'Spheric({{:{floatform}}}π, {{:{floatform}}}π, {{:{floatform}}}π)'.format(self.theta*scale, self.phi*scale, self.psi*scale)
   
  
 def angles(self) : return self.theta, self.phi, self.psi
 def cartesian(self) : return self.w, self.x, self.y, self.z
 def __add__(self, other):
  if not isinstance(other, Spheric) : return NotImplemented
  return Spheric (self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w)
 def __neg__(self):
  if self.__use_c() : return Spheric(self.w, -self.x, -self.y, -self.z)
  return Spheric(-self.theta, self.phi, self.psi)
 def __invert__(self):
  if self.__use_c() : return Spheric(-self.w, -self.x, -self.y, -self.z)
  return Spheric(_math.pi-self.theta, _math.pi-self.phi, self.psi+_math.pi)
 def __sub__(self, other) : return self + (-other)
 def __or__(self, other):
  if not isinstance(other, Spheric) : return NotImplemented
  
  return _math.acos(self * other)
 def __matmul__(self, fov):
  if not isinstance(fov, int|float) : return NotImplemented
  scale = _math.tan(self.phi)/_math.tan(fov/2)
  return _math.cos(self.psi)*scale, _math.sin(self.psi)*scale
 def __mul__(self, other):
  if isinstance(other, int|float) : return other*self
  if not isinstance(other, Spheric) : return NotImplemented
  return max(min(self.w*other.w+self.x*other.x+self.y*other.y+self.z*other.z,1.),-1.)
 def __truediv__(self, k):
  if not isinstance(k, int|float) : return NotImplemented
  return 1/k*self
 def __rmul__(self, k):
  if not isinstance(k, int|float) : return NotImplemented
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
 def __eq__(self, other) : return self * other == 1
 def __rshift__(self, other):
  if not (isinstance(self, Spheric) and isinstance(other, Spheric)) : return NotImplemented
  return _SphericInterpolator(self, other)
 def __xor__(self, other):
  if not (isinstance(self, Spheric) and isinstance(other, Spheric)) : return NotImplemented
  return _AngleConstructor(self, other)
 def __pos__(self) : return _copy(self)
 
class _SphericInterpolator:
 def __init__(self, q1, q2):
  self.start = q1
  self.end = q2
  self.distance = q1 | q2
  self.__discrete = self.distance == _math.pi
 def __call__(self, t):
  if not isinstance(t, int|float): raise TypeError('t-value must be numerical')
  if self.__discrete:
   if t % 1 != 0: raise ValueError('Cannot interpolate between antipodal Spherics')
   if t % 2 == 0 : return self.start
   return self.end
  if self.distance == 0 : return self.start
  c = 1/_math.sin(self.distance)
  o = _math.sin(t*self.distance)*c
  s = _math.sin((1-t)*self.distance)*c
  p1 = self.start.cartesian()
  p2 = self.end.cartesian()
  return Spheric(p1[0]*s+p2[0]*o,p1[1]*s+p2[1]*o,p1[2]*s+p2[2]*o,p1[3]*s+p2[3]*o)
 def __format__(self, format_spec) : return f'SphericInterpolator[({f"{{:{format_spec}}}".format(self.start)[8:-1]}) >> ({f"{{:{format_spec}}}".format(self.end)[8:-1]})]'
 def __repr__(self) : return f'{self}'
class _AngleConstructor:
 def __init__(self, q1, q2):
  if not (isinstance(q1, Spheric) and isinstance(q2, Spheric)): raise TypeError('Both operands must be Spheric')
  self.__dot = q1 * q2
  self.__eq = self.__dot == 1
  self.endpoints = (q1, q2)
  
 def __call__(self, q):
  if not isinstance(q, Spheric): raise TypeError('Angle vertex must be Spheric')
  if self.__eq : return .0
  a = self.endpoints[0] * q
  b = self.endpoints[1] * q
  sa = _math.sqrt(1-a**2)
  sb = _math.sqrt(1-b**2)
  S = sa*sb
  if S == 0: raise ValueError('Angle vertex cannot be equal to endpoint')
  return _math.acos(max(min((self.__dot-a*b)/S,1.),-1.))
 def __format__(self, format_spec) : return f'AngleConstructor[({f"{{:{format_spec}}}".format(self.endpoints[0])[8:-1]}) ^ ({f"{{:{format_spec}}}".format(self.endpoints[1])[8:-1]})]'
 def __repr__(self) : return f'{self}'

