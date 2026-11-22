import sys, glob
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
ps = sorted(glob.glob(d + '/f*.jpg'))
cols = 6; w, h = 270, 480; rows = (len(ps) + cols - 1) // cols
im = Image.new('RGB', (cols * w, rows * h), 'black')
from PIL import ImageDraw
dr = ImageDraw.Draw(im)
for k, p in enumerate(ps):
    x, y = (k % cols) * w, (k // cols) * h
    im.paste(Image.open(p).resize((w, h)), (x, y)); dr.text((x + 6, y + 6), p.split('/')[-1][1:5], fill='yellow')
im.save(out, quality=85)
