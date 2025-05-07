from fasthtml.common import *
from monsterui.all import * 

# add some custom md stylings based on my css
cck_class_map = franken_class_map.copy()
cck_class_map['h1'] = cck_class_map['h1'] + ' cck-heading'
for i in range(2,5):
    cck_class_map[f'h{i}'] = cck_class_map[f'h{i}'] + ' cck-subheading'
cck_class_map['blockquote'] = cck_class_map['blockquote'] + ' cck-blockquote'


