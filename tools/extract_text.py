"""Extract plain Tibetan text (with yigchung marked) from an EPUB source or from src/.

Usage:
  python3 tools/extract_text.py new  <path/to/source.epub | unpacked dir>  <out-basename>
  python3 tools/extract_text.py ours src                                    <out-basename>
Writes <out-basename>.md (readable, yigchung as «…») and <out-basename>.json (runs with styles n/y/r).
Style r = our written-out refrain after ༴ (class repeatNextOcc); the JSON keeps it apart so
tools/compare_source.py can ignore it. Report-only: never edits the book.

Extract plain Tibetan text (with yigchung marked) from the two EPUB sources.
Output: list of sections; each section = dict(title, src, blocks=[ (kind, [(style,text),...]) ])
kind in {'h','p'}; style in {'n','y'} (normal / yigchung)."""
import re, os, sys, glob, json
from html.parser import HTMLParser

Y_OPEN, Y_CLOSE = '«', '»'

class Walker(HTMLParser):
    def __init__(self, yig_classes, tiny_classes, drop_classes, drop_tags, heading_test, rep_classes=frozenset()):
        super().__init__(convert_charrefs=True)
        self.rep=rep_classes
        self.yig=yig_classes; self.tiny=tiny_classes; self.drop=drop_classes; self.drop_tags=drop_tags
        self.heading_test=heading_test
        self.stack=[]   # (tag, classes, is_block_start)
        self.blocks=[]  # (kind, runs)
        self.cur=None
        self.depth_drop=0
    def classes(self,attrs):
        return set((dict(attrs).get('class') or '').split())
    def handle_starttag(self,tag,attrs):
        cls=self.classes(attrs)
        if self.depth_drop or tag in self.drop_tags or (cls & self.drop):
            self.depth_drop+=1; self.stack.append((tag,cls)); return
        # block start?
        parent=self.stack[-1][0] if self.stack else None
        is_block = tag in ('p','h1','h2','h3','h4','h5','h6','li') or (tag in ('span','a') and parent in (None,'body','div','html'))
        if is_block or tag=='br':
            kind='h' if (tag[0]=='h' and tag!='html') or self.heading_test(tag,cls) else 'p'
            if tag=='br':
                if self.cur: self.cur[1].append(('n','\n'))
            else:
                self.cur=(kind,[]); self.blocks.append(self.cur)
        self.stack.append((tag,cls))
    def handle_endtag(self,tag):
        if self.stack: t,cls=self.stack.pop()
        else: return
        if self.depth_drop: self.depth_drop-=1; return
        parent=self.stack[-1][0] if self.stack else None
        if t in ('p','h1','h2','h3','h4','h5','h6','li') or (t in ('span','a') and parent in (None,'body','div','html')):
            self.cur=None
    def handle_data(self,data):
        if self.depth_drop: return
        if not data.strip():  # whitespace only
            if self.cur is not None and self.cur[1]: self.cur[1].append(('n',' '))
            return
        style='n'
        for t,cls in reversed(self.stack):
            if cls & self.tiny: return
            if cls & self.rep: style='r'; break
            if cls & self.yig: style='y'; break
        if self.cur is None:
            self.cur=('p',[]); self.blocks.append(self.cur)
        self.cur[1].append((style,data))

def norm_runs(runs):
    """merge adjacent same-style runs, collapse whitespace"""
    out=[]
    for s,t in runs:
        t=re.sub(r'[ \t\r\n    ]+',' ',t)
        if out and out[-1][0]==s: out[-1]=(s,out[-1][1]+t)
        else: out.append((s,t))
    out=[(s,t) for s,t in out if t.strip()]
    if out: out[0]=(out[0][0],out[0][1].lstrip()); out[-1]=(out[-1][0],out[-1][1].rstrip())
    return out

def block_text(runs, mark=True):
    parts=[]
    for s,t in runs:
        parts.append(f'{Y_OPEN}{t.strip()}{Y_CLOSE}' if (s=='y' and mark) else t)
    return ' '.join(p for p in parts if p).strip()

def parse(path, **kw):
    w=Walker(**kw)
    s=open(path,encoding='utf-8').read()
    s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    m=re.search(r'<body[^>]*>(.*)</body>',s,re.S)
    w.feed(m.group(1) if m else s)
    blocks=[]
    for kind,runs in w.blocks:
        r=norm_runs(runs)
        if r: blocks.append((kind,r))
    return blocks

def opf_items(opf):
    out={}
    for tag in re.findall(r'<item\b[^>]*>',opf):
        a=dict(re.findall(r'(\w[\w:-]*)="([^"]*)"',tag))
        if 'id' in a and 'href' in a: out[a['id']]=a['href']
    return out

# ---------- NEW book (Pages export) ----------
def unpack(epub):
    """unzip to a temp dir; the zip has a non-UTF-8 flagged filename that trips `unzip`"""
    import zipfile, tempfile
    out=tempfile.mkdtemp(prefix='epub_')
    z=zipfile.ZipFile(epub)
    for i in z.infolist():
        if i.is_dir(): continue
        name=i.filename
        if not (i.flag_bits & 0x800):
            try: name=name.encode('cp437').decode('utf-8')
            except Exception: pass
        safe=re.sub(r'[^\x20-\x7e/]', lambda m:'U%04x'%ord(m.group()), name)
        dst=os.path.join(out,safe); os.makedirs(os.path.dirname(dst),exist_ok=True)
        open(dst,'wb').write(z.read(i))
    return out

def extract_new(root):
    if root.lower().endswith('.epub'): root=unpack(root)
    opf=open(glob.glob(root+'/*/*.opf')[0],encoding='utf-8').read()
    items=opf_items(opf)
    spine=re.findall(r'<itemref idref="([^"]+)"',opf)
    ncx=open(glob.glob(root+'/*/*.ncx')[0],encoding='utf-8').read()
    titles={m.group(2):re.sub(r'\s+',' ',m.group(1)).strip() for m in re.finditer(r'<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src="([^"]*)"',ncx,re.S)}
    yig={'c9','c10','c15','c17','c22'}; tiny={'c16','c13','c7','c6','c19'}
    secs=[]
    for idref in spine:
        href=items[idref]
        if not href.startswith('chapter-'): continue
        p=os.path.join(root,'OPS',href)
        blocks=parse(p,yig_classes=yig,tiny_classes=tiny,drop_classes=set(),drop_tags={'img','style','script'},heading_test=lambda t,c:False)
        secs.append(dict(title=titles.get(href,''),src=href,blocks=blocks))
    return secs

# ---------- OUR book ----------
def extract_ours(root):
    opf=open(root+'/content.opf',encoding='utf-8').read()
    items=opf_items(opf)
    spine=re.findall(r'<itemref[^>]*idref="([^"]+)"',opf)
    yig={'tibyigchung','tibyigchungH'}
    drop={'pageno','lpn','ppnp','invisible','caption','jumpDown','jumpUp','jumpTODO','jumpRepeat','jumpRepeat3','imagebox','imageframe','image','tocpage2','wrap','left','right','ipnpx'}
    secs=[]
    for idref in spine:
        href=items.get(idref)
        if not href or not href.startswith('OPS/'): continue
        p=os.path.join(root,href)
        if not os.path.exists(p): continue
        blocks=parse(p,yig_classes=yig,tiny_classes=set(),drop_classes=drop,drop_tags={'img','style','script','a'},heading_test=lambda t,c:'tocpage1' in c,rep_classes={'repeatNextOcc','invisibleRepeat'})
        # split into sections at headings
        cur=dict(title='(start of file)',src=href,blocks=[])
        for kind,runs in blocks:
            if kind=='h':
                if cur['blocks'] or cur['title']!='(start of file)': secs.append(cur)
                cur=dict(title=block_text(runs,mark=False),src=href,blocks=[])
            else: cur['blocks'].append((kind,runs))
        secs.append(cur)
    return secs

def to_md(secs, header):
    out=[header,'']
    for s in secs:
        out.append(f"# {s['title']}  ⟨{s['src']}⟩"); out.append('')
        first=True
        for kind,runs in s['blocks']:
            t=block_text(runs)
            if not t: continue
            if kind=='h':
                if first and re.sub(r'\s','',block_text(runs,False))==re.sub(r'\s','',s['title']): first=False; continue
                out.append('## '+block_text(runs,False))
            else: out.append(t)
            out.append(''); first=False
    return '\n'.join(out)

if __name__=='__main__':
    which,root,out=sys.argv[1:4]
    secs=extract_new(root) if which=='new' else extract_ours(root)
    json.dump(secs,open(out+'.json','w',encoding='utf-8'),ensure_ascii=False)
    hdr = ('<!-- Plain Tibetan text extracted from resources/བཀའ་རྙིང་ཆོས་སྤྱོད་ཞལ་འདོན།.epub (Pages 6.2 export, dc:date 2561-06-27).\n'
           '     Source of truth for the Tibetan only; no navigation. Yigchung (small annotation script) is marked «…».\n'
           '     Generated by tools/extract_text.py — do not hand-edit. -->') if which=='new' else '<!-- Plain text of the current src/ book, same conventions. -->'
    open(out+'.md','w',encoding='utf-8').write(to_md(secs,hdr))
    n=sum(len(s['blocks']) for s in secs); ch=sum(len(t) for s in secs for k,r in s['blocks'] for st,t in r)
    print(f"{which}: {len(secs)} sections, {n} blocks, {ch} chars")
