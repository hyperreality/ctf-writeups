# Dumb25519: a stupid implementation of ed25519
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

import random
import hashlib
import binascii

# curve parameters
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493
cofactor = 8
b = 256 # bit representation

# Internal helper methods
def exponent(b,e,m):
    return pow(b,e,m)

def invert(x,n):
    return exponent(x,n-2,n)

def xfromy(y):
    temp = (y*y-1) * invert(d*y*y+1,q)
    x = exponent(temp,(q+3)/8,q)
    if (x*x - temp) % q != 0:
        x = (x*I) % q
    if x % 2 != 0:
        x = q-x
    return x

def bit(h,i):
    return (ord(h[i/8]) >> (i%8)) & 1

d = -121665 * invert(121666,q)
I = exponent(2,(q-1)/4,q)

class Scalar:
    def __init__(self,x):
        # Generated from an integer value
        if isinstance(x,int) or isinstance(x,long):
            self.x = x % l
        # Generated from a hex representation
        elif isinstance(x,str):
            try:
                x = binascii.unhexlify(x)
                self.x = sum(2**i * bit(x,i) for i in range(0,b)) % l
            except:
                raise TypeError
        else:
            raise TypeError

    def invert(self):
        if self.x == 0:
            raise ZeroDivisionError
        return Scalar(invert(self.x,l))

    def __add__(self,y):
        if isinstance(y,int):
            return Scalar(self.x + y)
        if isinstance(y,Scalar):
            return Scalar(self.x + y.x)
        return NotImplemented

    def __sub__(self,y):
        if isinstance(y,int):
            return Scalar(self.x - y)
        if isinstance(y,Scalar):
            return Scalar(self.x - y.x)
        return NotImplemented

    def __mul__(self,y):
        if isinstance(y,int):
            return Scalar(self.x * y)
        if isinstance(y,Scalar):
            return Scalar(self.x * y.x)
        return NotImplemented

    def __div__(self,y):
        if isinstance(y,int):
            return Scalar(self.x / y)
        if isinstance(y,Scalar):
            return Scalar(self.x / y.x)
        raise NotImplemented

    def __pow__(self,y):
        if not isinstance(y,int):
            return NotImplemented
        return Scalar(self.x**y)

    def __eq__(self,y):
        if isinstance(y,Scalar):
            return self.x == y.x
        raise TypeError

    def __ne__(self,y):
        if isinstance(y,Scalar):
            return self.x != y.x
        raise TypeError

    def __lt__(self,y):
        if isinstance(y,Scalar):
            return self.x < y.x
        raise TypeError

    def __gt__(self,y):
        if isinstance(y,Scalar):
            return self.x > y.x
        raise TypeError

    def __le__(self,y):
        if isinstance(y,Scalar):
            return self.x <= y.x
        raise TypeError

    def __ge__(self,y):
        if isinstance(y,Scalar):
            return self.x >= y.x
        raise TypeError

    def __repr__(self):
        bits = [(self.x >> i) & 1 for i in range(b)]
        return binascii.hexlify(''.join([chr(sum([bits[i*8+j] << j for j in range(8)])) for i in range(b/8)]))

    def __int__(self):
        return self.x

    def __mod__(self,mod):
        if isinstance(mod,int):
            return Scalar(self.x % mod)
        if isinstance(mod,Scalar):
            return Scalar(self.x % mod.x)
        return NotImplemented

    def __neg__(self):
        return Scalar(-self.x)

class Point:
    def __init__(self,x,y=None):
        # Generated from integer values
        if (isinstance(x,long) or isinstance(x,int)) and (isinstance(y,long) or isinstance(y,int)) and y is not None:
            self.x = x
            self.y = y
        # Generated from a hex representation
        elif isinstance(x,str) and y is None:
            x = binascii.unhexlify(x)
            self.y = sum(2**i * bit(x,i) for i in range(0,b-1))
            self.x = xfromy(self.y)
            if self.x & 1 != bit(x,b-1):
                self.x = q - self.x
        else:
            raise TypeError

    def __eq__(self,Q):
        if not isinstance(Q,Point):
            raise TypeError
        return self.x == Q.x and self.y == Q.y

    def __ne__(self,Q):
        if not isinstance(Q,Point):
            raise TypeError
        return self.x != Q.x or self.y != Q.y

    def __add__(self,Q):
        if not isinstance(Q,Point):
            return NotImplemented
        x1 = self.x
        y1 = self.y
        x2 = Q.x
        y2 = Q.y
        x3 = (x1*y2+x2*y1) * invert(1+d*x1*x2*y1*y2,q)
        y3 = (y1*y2+x1*x2) * invert(1-d*x1*x2*y1*y2,q)
        return Point(x3 % q, y3 % q)

    def __sub__(self,Q):
        if not isinstance(Q,Point):
            return NotImplemented
        x1 = self.x
        y1 = self.y
        x2 = -Q.x
        y2 = Q.y
        x3 = (x1*y2+x2*y1) * invert(1+d*x1*x2*y1*y2,q)
        y3 = (y1*y2+x1*x2) * invert(1-d*x1*x2*y1*y2,q)
        return Point(x3 % q, y3 % q)

    def __mul__(self,y):
        if not isinstance(y,Scalar):
            return NotImplemented
        if y == Scalar(0):
            return Point(0,1)
        Q = self.__mul__(y/Scalar(2))
        Q = Q.__add__(Q)
        if y.x & 1:
            Q = self.__add__(Q)
        return Q

    def __rmul__(self,y):
        if not isinstance(y,Scalar):
            return NotImplemented
        return self*y

    def __repr__(self):
        bits = [(self.y >> i) & 1 for i in range(b-1)] + [self.x & 1]
        return binascii.hexlify(''.join([chr(sum([bits[i*8+j] << j for j in range(8)])) for i in range(b/8)]))

    # determines if the point is on the curve
    def on_curve(self):
        x = self.x
        y = self.y
        return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

class PointVector:
    def __init__(self,points):
        for point in points:
            if not isinstance(point,Point):
                raise TypeError
        self.points = points

    def __add__(self,W):
        if not len(self.points) == len(W.points):
            raise IndexError
        if not isinstance(W,PointVector):
            raise TypeError
        return PointVector([self.points[i] + W.points[i] for i in range(len(self.points))])

    def __sub__(self,W):
        if not len(self.points) == len(W.points):
            raise IndexError
        if not isinstance(W,PointVector):
            raise TypeError
        return PointVector([self.points[i] - W.points[i] for i in range(len(self.points))])

    # multiplying a PointVector by a scalar or ScalarVector or Hadamard
    def __mul__(self,s):
        if isinstance(s,Scalar):
            return PointVector([self.points[i]*s for i in range(len(self.points))])
        if isinstance(s,ScalarVector):
            return multiexp(s,self)
        if isinstance(s,PointVector):
            if not len(self.points) == len(s.points):
                raise IndexError
            return PointVector([self.points[i] + s.points[i] for i in range(len(self.points))])
        raise TypeError

    def __len__(self):
        return len(self.points)

    def __getitem__(self,i):
        if not isinstance(i,slice):
            return self.points[i]
        return PointVector(self.points[i])

    def append(self,item):
        if not isinstance(item,Point):
            raise typeError
        self.points.append(item)

    def extend(self,items):
        for item in items.points:
            if not isinstance(item,Point):
                raise TypeError
            self.points.append(item)

    def __repr__(self):
        return repr(self.points)

class ScalarVector:
    def __init__(self,scalars):
        for scalar in scalars:
            if not isinstance(scalar,Scalar):
                raise TypeError
        self.scalars = scalars

    def __add__(self,s):
        if not len(self.scalars) == len(s.scalars):
            raise IndexError
        if not isinstance(s,ScalarVector):
            raise TypeError
        return ScalarVector([self.scalars[i] + s.scalars[i] for i in range(len(self.scalars))])

    def __sub__(self,s):
        if not len(self.scalars) == len(s.scalars):
            raise IndexError
        if not isinstance(s,ScalarVector):
            raise TypeError
        return ScalarVector([self.scalars[i] - s.scalars[i] for i in range(len(self.scalars))])

    # hadamard product and multiplying a scalar vector by a scalar
    def __mul__(self,s):
        if isinstance(s,Scalar):
            return ScalarVector([self.scalars[i]*s for i in range(len(self.scalars))])
        if not isinstance(s,ScalarVector):
            raise TypeError
        if not len(self.scalars) == len(s.scalars):
            raise IndexError
        return ScalarVector([self.scalars[i]*s.scalars[i] for i in range(len(self.scalars))])

    # running sum
    def sum(self):
        r = Scalar(0)
        for i in range(len(self.scalars)):
            r += self.scalars[i]
        return r

    # inner product
    def __pow__(self,s):
        if not len(self.scalars) == len(s.scalars):
            raise IndexError
        if not isinstance(s,ScalarVector):
            raise TypeError
        r = Scalar(0)
        for i in range(len(self.scalars)):
            r += self.scalars[i]*s.scalars[i]
        return r

    def __len__(self):
        return len(self.scalars)

    def __getitem__(self,i):
        if not isinstance(i,slice):
            return self.scalars[i]
        return ScalarVector(self.scalars[i])

    def __setitem__(self,i,val):
        self.scalars[i] = val

    def append(self,item):
        if not isinstance(item,Scalar):
            raise TypeError
        self.scalars.append(item)

    def extend(self,items):
        for item in items.scalars:
            if not isinstance(item,Scalar):
                raise TypeError
            self.scalars.append(item)

    def __repr__(self):
        return repr(self.scalars)

    # return a vector of inverses
    def invert(self):
        inputs = self.scalars[:]
        n = len(inputs)
        scratch = [Scalar(1)]*n
        acc = Scalar(1)

        for i in range(n):
            if inputs[i] == Scalar(0):
                raise ArithmeticError
            scratch[i] = acc
            acc *= inputs[i]
        acc = Scalar(invert(acc.x,l))
        for i in range(n-1,-1,-1):
            temp = acc*inputs[i]
            inputs[i] = acc*scratch[i]
            acc = temp

        return inputs

# make a point from a given integer y (if it is on the curve)
def make_point(y):
    if not y < q: # stay in the field
        return None
    x = xfromy(y)
    P = Point(x,y)
    if not P.on_curve():
        return None
    return P

# hash data to get a point on the curve in the G subgroup
def hash_to_point(*data):
    result = ''
    for datum in data:
        if datum is None:
            raise TypeError
        result += hashlib.sha256(str(datum)).hexdigest()
    while True:
        result = hashlib.sha256(result).hexdigest()
        if make_point(int(result,16)) is not None:
            return make_point(int(result,16))*Scalar(cofactor)

# hash data to get a scalar
def hash_to_scalar(*data):
    result = ''
    for datum in data:
        if datum is None:
            raise TypeError
        result += hashlib.sha256(str(datum)).hexdigest()

    # ensure we're uniformly in the scalar range
    while True:
        result = hashlib.sha256(result).hexdigest()
        if int(result,16) < l:
            return Scalar(int(result,16))

# generate a random scalar
def random_scalar(zero=True):
    if zero:
        return Scalar(random.randrange(0,l))
    return Scalar(random.randrange(1,l))

# generate a random point in the G subgroup
def random_point():
    return hash_to_point(str(random.random()))

# basepoint
Gy = 4*invert(5,q)
Gx = xfromy(Gy)
G = Point(Gx % q, Gy % q)

# zero point
Z = Point(0,1)

# multiexponention operation using simplified Pippenger
def multiexp(*data):
    if len(data) == 1:
        scalars = ScalarVector([datum[1] for datum in data[0]])
        points = PointVector([datum[0] for datum in data[0]])
    else:
        scalars = ScalarVector(data[0])
        points = PointVector(data[1])

    if not isinstance(scalars,ScalarVector) or not isinstance(points,PointVector):
        raise TypeError
    if len(scalars) != len(points):
        raise IndexError
    if len(scalars) == 0:
        return Z

    buckets = None
    nonzero = False
    result = Z # zero point
   
    c = 4 # window parameter; NOTE: the optimal value actually depends on len(points) empirically

    # really we want to use the max bitlength to compute groups
    maxscalar = int(max(scalars))
    groups = 0
    while maxscalar >= 2**groups:
        groups += 1
    groups = int((groups + c - 1) / c)
    
    # loop is really (groups-1)..0
    for k in range(groups-1,-1,-1):
        if result != Z:
            for i in range(c):
                result += result
        
        buckets = [Z]*(2**c) # clear all buckets
        
        # partition scalars into buckets
        for i in range(len(scalars)):
            bucket = 0
            for j in range(c):
                if int(scalars[i]) & (1 << (k*c+j)): # test for bit
                    bucket |= 1 << j
            
            if bucket == 0: # zero bucket is never used
                continue
            
            if buckets[bucket] != Z:
                buckets[bucket] += points[i]
            else:
                buckets[bucket] = points[i]
        
        # sum the buckets
        pail = Z
        for i in range(len(buckets)-1,0,-1):
            if buckets[i] != Z:
                pail += buckets[i]
            if pail != Z:
                result += pail
    return result
