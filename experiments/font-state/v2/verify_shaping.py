"""Verify shaping with local system HarfBuzz through ctypes (no pip dependency)."""
import ctypes as C
from pathlib import Path
LIB=C.CDLL('libharfbuzz.so.0')

def setup(name, restype, args):
 f=getattr(LIB,name); f.restype=restype; f.argtypes=args; return f
P=C.c_void_p
hb_blob_create=setup('hb_blob_create',P,[P,C.c_uint,C.c_int,P,P])
hb_face_create=setup('hb_face_create',P,[P,C.c_uint]); hb_font_create=setup('hb_font_create',P,[P]); hb_ot_font_set_funcs=setup('hb_ot_font_set_funcs',None,[P]); hb_font_set_scale=setup('hb_font_set_scale',None,[P,C.c_int,C.c_int]);hb_font_set_var_coords_design=setup('hb_font_set_var_coords_design',None,[P,C.POINTER(C.c_float),C.c_uint]);hb_buffer_create=setup('hb_buffer_create',P,[]);hb_buffer_add_utf8=setup('hb_buffer_add_utf8',None,[P,P,C.c_int,C.c_uint,C.c_int]);hb_buffer_guess_segment_properties=setup('hb_buffer_guess_segment_properties',None,[P]);hb_shape=setup('hb_shape',None,[P,P,P,C.c_uint]); hb_buffer_get_length=setup('hb_buffer_get_length',C.c_uint,[P]);
class GlyphPos(C.Structure):
 _fields_=[('x_advance',C.c_int),('y_advance',C.c_int),('x_offset',C.c_int),('y_offset',C.c_int),('var',C.c_uint)]
hb_buffer_get_glyph_positions=setup('hb_buffer_get_glyph_positions',C.POINTER(GlyphPos),[P,P]); hb_buffer_destroy=setup('hb_buffer_destroy',None,[P]); hb_font_destroy=setup('hb_font_destroy',None,[P]);hb_face_destroy=setup('hb_face_destroy',None,[P]);hb_blob_destroy=setup('hb_blob_destroy',None,[P])

def shape(font_file, text, addr=None):
 data=Path(font_file).read_bytes(); buf=C.create_string_buffer(data); blob=hb_blob_create(C.cast(buf,P),len(data),0,None,None)
 face=hb_face_create(blob,0); font=hb_font_create(face); hb_ot_font_set_funcs(font);hb_font_set_scale(font,1000,1000)
 if addr is not None:
  coords=(C.c_float * 1)(addr); hb_font_set_var_coords_design(font,coords,1)
 shaped=hb_buffer_create(); t=text.encode(); textbuf=C.create_string_buffer(t)
 hb_buffer_add_utf8(shaped,C.cast(textbuf,P),len(t),0,len(t)); hb_buffer_guess_segment_properties(shaped)
 hb_shape(font,shaped,None,0)
 length=hb_buffer_get_length(shaped); glyphs=hb_buffer_get_glyph_positions(shaped,None)
 advances=[glyphs[i].x_advance for i in range(length)]; total=sum(advances)
 hb_buffer_destroy(shaped);hb_font_destroy(font);hb_face_destroy(face);hb_blob_destroy(blob)
 return total/1000,advances

if __name__=='__main__':
 d=Path(__file__).parent/'generated'
 for fn,text,ax in [('ProbeToken.ttf','ALICE',None),('ProbeTokenContext.ttf','ALICE',None),('ProbeContext.ttf','^AB',None),('ProbeAddress.ttf','^ABC',0),('ProbeAddress.ttf','^ABC',1),('ProbeAddress.ttf','^ABC',2),('ProbeAddress.ttf','^ABC',3)]:
  try: print(fn,text,ax,shape(d/fn,text,ax))
  except Exception as e: print('ERR',fn,e)
