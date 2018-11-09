##############################################################
# colors.py
#
# Defines colors and operations on them

# Copyright 2018 Taras Zakharko (taras.zakharko)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



import collections
from UIToolkit.Drawing import Context

def makecolor(value):
    if value is not None and value.__class__ is not Color:
        return Color(value)
    else:
        return value

class Color(collections.namedtuple('Color', 'red,green,blue,alpha')):
    __namedcolors = dict(
        indigo = (0.294117647059, 0.0, 0.509803921569, 1.0),
        gold = (1.0, 0.843137254902, 0.0, 1.0),
        hotpink = (1.0, 0.411764705882, 0.705882352941, 1.0),
        firebrick = (0.698039215686, 0.133333333333, 0.133333333333, 1.0),
        indianred = (0.803921568627, 0.360784313725, 0.360784313725, 1.0),
        yellow = (1.0, 1.0, 0.0, 1.0),
        mistyrose = (1.0, 0.894117647059, 0.882352941176, 1.0),
        darkolivegreen = (0.333333333333, 0.419607843137, 0.18431372549, 1.0),
        olive = (0.501960784314, 0.501960784314, 0.0, 1.0),
        darkseagreen = (0.560784313725, 0.737254901961, 0.560784313725, 1.0),
        pink = (1.0, 0.752941176471, 0.796078431373, 1.0),
        tomato = (1.0, 0.388235294118, 0.278431372549, 1.0),
        lightcoral = (0.941176470588, 0.501960784314, 0.501960784314, 1.0),
        orangered = (1.0, 0.270588235294, 0.0, 1.0),
        navajowhite = (1.0, 0.870588235294, 0.678431372549, 1.0),
        lime = (0.0, 1.0, 0.0, 1.0),
        palegreen = (0.596078431373, 0.98431372549, 0.596078431373, 1.0),
        darkslategrey = (0.18431372549, 0.309803921569, 0.309803921569, 1.0),
        greenyellow = (0.678431372549, 1.0, 0.18431372549, 1.0),
        burlywood = (0.870588235294, 0.721568627451, 0.529411764706, 1.0),
        seashell = (1.0, 0.960784313725, 0.933333333333, 1.0),
        mediumspringgreen = (0.0, 0.980392156863, 0.603921568627, 1.0),
        fuchsia = (1.0, 0.0, 1.0, 1.0),
        papayawhip = (1.0, 0.937254901961, 0.835294117647, 1.0),
        blanchedalmond = (1.0, 0.921568627451, 0.803921568627, 1.0),
        chartreuse = (0.498039215686, 1.0, 0.0, 1.0),
        dimgray = (0.411764705882, 0.411764705882, 0.411764705882, 1.0),
        black = (0.0, 0.0, 0.0, 1.0),
        peachpuff = (1.0, 0.854901960784, 0.725490196078, 1.0),
        springgreen = (0.0, 1.0, 0.498039215686, 1.0),
        aquamarine = (0.498039215686, 1.0, 0.83137254902, 1.0),
        white = (1.0, 1.0, 1.0, 1.0),
        orange = (1.0, 0.647058823529, 0.0, 1.0),
        lightsalmon = (1.0, 0.627450980392, 0.478431372549, 1.0),
        darkslategray = (0.18431372549, 0.309803921569, 0.309803921569, 1.0),
        brown = (0.647058823529, 0.164705882353, 0.164705882353, 1.0),
        ivory = (1.0, 1.0, 0.941176470588, 1.0),
        dodgerblue = (0.117647058824, 0.564705882353, 1.0, 1.0),
        peru = (0.803921568627, 0.521568627451, 0.247058823529, 1.0),
        lawngreen = (0.486274509804, 0.988235294118, 0.0, 1.0),
        chocolate = (0.823529411765, 0.411764705882, 0.117647058824, 1.0),
        crimson = (0.862745098039, 0.078431372549, 0.235294117647, 1.0),
        forestgreen = (0.133333333333, 0.545098039216, 0.133333333333, 1.0),
        darkgrey = (0.662745098039, 0.662745098039, 0.662745098039, 1.0),
        lightseagreen = (0.125490196078, 0.698039215686, 0.666666666667, 1.0),
        cyan = (0.0, 1.0, 1.0, 1.0),
        mintcream = (0.960784313725, 1.0, 0.980392156863, 1.0),
        silver = (0.752941176471, 0.752941176471, 0.752941176471, 1.0),
        antiquewhite = (0.980392156863, 0.921568627451, 0.843137254902, 1.0),
        mediumorchid = (0.729411764706, 0.333333333333, 0.827450980392, 1.0),
        skyblue = (0.529411764706, 0.807843137255, 0.921568627451, 1.0),
        gray = (0.501960784314, 0.501960784314, 0.501960784314, 1.0),
        darkturquoise = (0.0, 0.807843137255, 0.819607843137, 1.0),
        goldenrod = (0.854901960784, 0.647058823529, 0.125490196078, 1.0),
        darkgreen = (0.0, 0.392156862745, 0.0, 1.0),
        floralwhite = (1.0, 0.980392156863, 0.941176470588, 1.0),
        darkviolet = (0.580392156863, 0.0, 0.827450980392, 1.0),
        darkgray = (0.662745098039, 0.662745098039, 0.662745098039, 1.0),
        moccasin = (1.0, 0.894117647059, 0.709803921569, 1.0),
        saddlebrown = (0.545098039216, 0.270588235294, 0.0745098039216, 1.0),
        grey = (0.501960784314, 0.501960784314, 0.501960784314, 1.0),
        darkslateblue = (0.282352941176, 0.239215686275, 0.545098039216, 1.0),
        lightskyblue = (0.529411764706, 0.807843137255, 0.980392156863, 1.0),
        lightpink = (1.0, 0.713725490196, 0.756862745098, 1.0),
        mediumvioletred = (0.780392156863, 0.0823529411765, 0.521568627451, 1.0),
        slategrey = (0.439215686275, 0.501960784314, 0.564705882353, 1.0),
        red = (1.0, 0.0, 0.0, 1.0),
        deeppink = (1.0, 0.078431372549, 0.576470588235, 1.0),
        limegreen = (0.196078431373, 0.803921568627, 0.196078431373, 1.0),
        darkmagenta = (0.545098039216, 0.0, 0.545098039216, 1.0),
        palegoldenrod = (0.933333333333, 0.909803921569, 0.666666666667, 1.0),
        plum = (0.866666666667, 0.627450980392, 0.866666666667, 1.0),
        turquoise = (0.250980392157, 0.878431372549, 0.81568627451, 1.0),
        lightgrey = (0.827450980392, 0.827450980392, 0.827450980392, 1.0),
        lightgoldenrodyellow = (0.980392156863, 0.980392156863, 0.823529411765, 1.0),
        darkgoldenrod = (0.721568627451, 0.525490196078, 0.043137254902, 1.0),
        lavender = (0.901960784314, 0.901960784314, 0.980392156863, 1.0),
        maroon = (0.501960784314, 0.0, 0.0, 1.0),
        yellowgreen = (0.603921568627, 0.803921568627, 0.196078431373, 1.0),
        sandybrown = (0.956862745098, 0.643137254902, 0.376470588235, 1.0),
        thistle = (0.847058823529, 0.749019607843, 0.847058823529, 1.0),
        violet = (0.933333333333, 0.509803921569, 0.933333333333, 1.0),
        navy = (0.0, 0.0, 0.501960784314, 1.0),
        magenta = (1.0, 0.0, 1.0, 1.0),
        dimgrey = (0.411764705882, 0.411764705882, 0.411764705882, 1.0),
        tan = (0.823529411765, 0.705882352941, 0.549019607843, 1.0),
        rosybrown = (0.737254901961, 0.560784313725, 0.560784313725, 1.0),
        olivedrab = (0.419607843137, 0.556862745098, 0.137254901961, 1.0),
        blue = (0.0, 0.0, 1.0, 1.0),
        lightblue = (0.678431372549, 0.847058823529, 0.901960784314, 1.0),
        ghostwhite = (0.972549019608, 0.972549019608, 1.0, 1.0),
        honeydew = (0.941176470588, 1.0, 0.941176470588, 1.0),
        cornflowerblue = (0.392156862745, 0.58431372549, 0.929411764706, 1.0),
        slateblue = (0.41568627451, 0.352941176471, 0.803921568627, 1.0),
        linen = (0.980392156863, 0.941176470588, 0.901960784314, 1.0),
        darkblue = (0.0, 0.0, 0.545098039216, 1.0),
        powderblue = (0.690196078431, 0.878431372549, 0.901960784314, 1.0),
        seagreen = (0.180392156863, 0.545098039216, 0.341176470588, 1.0),
        darkkhaki = (0.741176470588, 0.717647058824, 0.419607843137, 1.0),
        snow = (1.0, 0.980392156863, 0.980392156863, 1.0),
        sienna = (0.627450980392, 0.321568627451, 0.176470588235, 1.0),
        mediumblue = (0.0, 0.0, 0.803921568627, 1.0),
        royalblue = (0.254901960784, 0.411764705882, 0.882352941176, 1.0),
        lightcyan = (0.878431372549, 1.0, 1.0, 1.0),
        green = (0.0, 0.501960784314, 0.0, 1.0),
        mediumpurple = (0.576470588235, 0.439215686275, 0.847058823529, 1.0),
        midnightblue = (0.0980392156863, 0.0980392156863, 0.439215686275, 1.0),
        cornsilk = (1.0, 0.972549019608, 0.862745098039, 1.0),
        paleturquoise = (0.686274509804, 0.933333333333, 0.933333333333, 1.0),
        bisque = (1.0, 0.894117647059, 0.76862745098, 1.0),
        slategray = (0.439215686275, 0.501960784314, 0.564705882353, 1.0),
        darkcyan = (0.0, 0.545098039216, 0.545098039216, 1.0),
        khaki = (0.941176470588, 0.901960784314, 0.549019607843, 1.0),
        wheat = (0.960784313725, 0.870588235294, 0.701960784314, 1.0),
        teal = (0.0, 0.501960784314, 0.501960784314, 1.0),
        darkorchid = (0.6, 0.196078431373, 0.8, 1.0),
        deepskyblue = (0.0, 0.749019607843, 1.0, 1.0),
        salmon = (0.980392156863, 0.501960784314, 0.447058823529, 1.0),
        darkred = (0.545098039216, 0.0, 0.0, 1.0),
        steelblue = (0.274509803922, 0.509803921569, 0.705882352941, 1.0),
        palevioletred = (0.847058823529, 0.439215686275, 0.576470588235, 1.0),
        lightslategray = (0.466666666667, 0.533333333333, 0.6, 1.0),
        aliceblue = (0.941176470588, 0.972549019608, 1.0, 1.0),
        lightslategrey = (0.466666666667, 0.533333333333, 0.6, 1.0),
        lightgreen = (0.564705882353, 0.933333333333, 0.564705882353, 1.0),
        orchid = (0.854901960784, 0.439215686275, 0.839215686275, 1.0),
        gainsboro = (0.862745098039, 0.862745098039, 0.862745098039, 1.0),
        mediumseagreen = (0.235294117647, 0.701960784314, 0.443137254902, 1.0),
        lightgray = (0.827450980392, 0.827450980392, 0.827450980392, 1.0),
        mediumturquoise = (0.282352941176, 0.819607843137, 0.8, 1.0),
        lemonchiffon = (1.0, 0.980392156863, 0.803921568627, 1.0),
        cadetblue = (0.372549019608, 0.619607843137, 0.627450980392, 1.0),
        cadetblue1 = (0.59, 0.96, 1, 1.0),
        cadetblue2 = (0.55, 0.89, 0.93, 1.0),
        lightyellow = (1.0, 1.0, 0.878431372549, 1.0),
        lavenderblush = (1.0, 0.941176470588, 0.960784313725, 1.0),
        coral = (1.0, 0.498039215686, 0.313725490196, 1.0),
        purple = (0.501960784314, 0.0, 0.501960784314, 1.0),
        aqua = (0.0, 1.0, 1.0, 1.0),
        whitesmoke = (0.960784313725, 0.960784313725, 0.960784313725, 1.0),
        mediumslateblue = (0.482352941176, 0.407843137255, 0.933333333333, 1.0),
        darkorange = (1.0, 0.549019607843, 0.0, 1.0),
        mediumaquamarine = (0.4, 0.803921568627, 0.666666666667, 1.0),
        darksalmon = (0.913725490196, 0.588235294118, 0.478431372549, 1.0),
        beige = (0.960784313725, 0.960784313725, 0.862745098039, 1.0),
        blueviolet = (0.541176470588, 0.16862745098, 0.886274509804, 1.0),
        azure = (0.941176470588, 1.0, 1.0, 1.0),
        lightsteelblue = (0.690196078431, 0.76862745098, 0.870588235294, 1.0),
        oldlace = (0.992156862745, 0.960784313725, 0.901960784314, 1.0)
    )
    
    
    def __new__(cls, *args, **kwargs):
        # 1. construct from provided color name or color
        if len(args) == 1:
            if args[0] is None: return None
            
            if isinstance(args[0], basestring):
                try:
                    s = args[0]
                    if s.startswith('#'):
                        val = [int(s[1:3], 16)/255.0, int(s[3:5], 16)/255.0, int(s[5:7], 16)/255.0, 1.0]
                    else:
                        val = list(Color.__namedcolors[s.lower()])
                except KeyError, ValueError:
                    raise ValueError('Unknown color \'%s\'' % args[0])    
            elif isinstance(args[0], Color):
                return args[0]
            else:
                raise ValueError('Not a color: %s' % (args[0], ))    
        # 2. construct from provided rgb tripple        
        elif len(args) == 3:
            val = [args[0], args[1], args[2], 1.0]
        # 3. construct from provided rgba quadruple
        elif len(args) == 4:
            val = list(args)
        else:
            raise ValueError('Don\'t know how to construct a color from %s' % (args, ))
            
        # now, override the color information (if provided)
        for k, v in kwargs.iteritems():
            if k == 'red':
                val[0] = v
            elif k =='green':
                val[1] = v
            elif k =='blue':
                val[2] = v
            elif k =='alpha':
                val[3] = v
            else:
                raise ValueError('Unknown color component \'%s\'' % k)
        # clamp the color values 
                
        return tuple.__new__(Color, val)
            
    def makeDrawcolor(self):
        Context.color = self        

    def makeFillcolor(self):
        Context.fillcolor = self    
                    
    def blend(self, target, t):
        invt = 1-t
        return tuple.__new__(Color, (self[0]*invt + target[0]*t, 
                    self[1]*invt + target[1]*t,
                    self[2]*invt + target[2]*t,
                    self[3]*invt + target[3]*t))
                    
    __interpolate__ = blend
    
    
