"""Compare the Tibetan of a source EPUB with the current src/ book, independent of sectioning.

Usage:
  python3 tools/extract_text.py new  resources/<source>.epub  resources/extracted/<source>-text
  python3 tools/extract_text.py ours src                       resources/extracted/current-src-text
  python3 tools/compare_source.py resources/extracted/<source>-text.json resources/extracted/current-src-text.json resources/extracted/comparison-<date>.md

Report-only. Method and conventions are written into the top of the report it produces.
"""
import json, re, sys, collections, unicodedata
new=json.load(open(sys.argv[1],encoding='utf-8')); ours=json.load(open(sys.argv[2],encoding='utf-8'))
K=16
EXCL_OURS={'OPS/titlepage.htm','OPS/zur-yig.htm'}     # editor-supplied, not in any source pecha
def norm(t):
    t=unicodedata.normalize('NFC',t)   # new book: precomposed U+0F75; ours: U+0F71 U+0F74
    t=t.replace('\u0f8e','')             # new book's second ditto sign
    t=re.sub(r'[\s    ]','',t)
    t=re.sub(r'[A-Za-z0-9?=<>\[\]()*_/#\-:.,;!{}|]','',t)
    t=t.replace('༈','')
    t=re.sub(r'་?གསོལ྾','',t)      # new book's ditto for a repeated refrain
    t=t.replace('྾','').replace('༴','')   # remaining abbreviation marks either side
    return t
def text(sec):
    return norm(''.join(t for k,r in sec['blocks'] for s,t in r if s!='r'))   # drop our written-out refrains
def build(secs):
    docs=[]; pos=0; full=[]
    for s in secs:
        if s['src'] in EXCL_OURS: continue
        t=text(s); docs.append((pos,pos+len(t),s)); full.append(t); pos+=len(t)
    return ''.join(full),docs
TN,DN=build(new); TO,DO=build(ours)
def shingle_index(T):
    d=collections.defaultdict(list)
    for i in range(len(T)-K+1): d[T[i:i+K]].append(i)
    return d
IN=shingle_index(TN); IO=shingle_index(TO)
def coverage(T,other_idx):
    cov=bytearray(len(T))
    for i in range(len(T)-K+1):
        if T[i:i+K] in other_idx: cov[i:i+K]=b'\x01'*K
    return cov
CN=coverage(TN,IO); CO=coverage(TO,IN)
def runs(cov):
    out=[];i=0;n=len(cov)
    while i<n:
        if not cov[i]:
            j=i
            while j<n and not cov[j]: j+=1
            out.append((i,j)); i=j
        else: i+=1
    return out
def where(docs,p):
    for a,b,s in docs:
        if a<=p<b: return s
    return docs[-1][2]
def counterpart(T,cov,other_T,other_idx,i,j,maxgap=1500):
    a=i-K
    while a>=0 and not cov[a]: a-=1
    pre=T[a:a+K] if a>=0 and cov[a] else None
    b=j
    while b+K<=len(T) and not all(cov[b:b+K]): b+=1
    post=T[b:b+K] if b+K<=len(T) else None
    if pre is None or post is None: return None
    best=None
    for x in other_idx.get(pre,[]):
        for y in other_idx.get(post,[]):
            if y>=x+K and y-(x+K)<maxgap and (best is None or y-x<best[1]-best[0]): best=(x+K,y)
    return other_T[best[0]:best[1]] if best else None
def label(sec,newbook):
    if newbook: return f"ch {sec['src'].replace('chapter-','').replace('.xhtml','')} · {sec['title'][:36]}"
    return f"{sec['src'].split('/')[-1]} · {sec['title'][:36]}"
def entry(T,cov,other_T,other_idx,docs,i,j,newbook):
    return dict(sec=label(where(docs,i),newbook),seg=T[i:j],cp=counterpart(T,cov,other_T,other_idx,i,j),ctx_a=T[max(0,i-24):i],ctx_b=T[j:j+24],i=i)
newruns=[entry(TN,CN,TO,IO,DN,i,j,True) for i,j in runs(CN)]
ourruns=[entry(TO,CO,TN,IN,DO,i,j,False) for i,j in runs(CO)]
out=[]; P=out.append
P('# Text comparison: new source EPUB (dc:date 2561-06-27) vs current src/\n')
P('**Method.** Both books are reduced to bare Tibetan (no whitespace, page numbers, Latin, ༈). Both are NFC-normalised (the new book encodes ཱུ as the deprecated precomposed U+0F75, ours as U+0F71 U+0F74). Our written-out refrains after `༴` and the new book\'s ditto marks (`གསོལ྾`, `྾` U+0FBE, `ྎ` U+0F8E) are removed, so the two abbreviation conventions do not register as differences. Then every 16-character window of one book is looked up in the other; characters covered by no shared window are *unmatched*, and each run of them is shown with what the other book has between the nearest matching windows. This does not depend on how either book is cut into sections. Our `titlepage.htm` and `c_extra.htm` (ཞབས་རྟེན།, ཟུར་ཡིག) are left out: they are editor-supplied and in no source pecha.\n')
un_n=sum(1 for c in CN if not c); un_o=sum(1 for c in CO if not c)
P(f'- New book: {len(TN)} chars, {un_n} unmatched ({100*un_n/len(TN):.2f}%) in {len(newruns)} runs')
P(f'- Current book: {len(TO)} chars, {un_o} unmatched ({100*un_o/len(TO):.2f}%) in {len(ourruns)} runs\n')
# ---- 0. TOC alignment
P('\n## 0. Table of contents, aligned by content\n')
P('For each chapter of the new book: its NCX title, and the section(s) of ours that hold its text. Share = how much of the chapter\'s text those sections contain.\n')
P('| ch | new NCX title | ours (file · heading) | share |'); P('|---|---|---|---|')
osh=[(a,b,s,{TO[i:i+K] for i in range(a,max(a,b-K+1))}) for a,b,s in DO]
for a,b,s in DN:
    sh={TN[i:i+K] for i in range(a,max(a,b-K+1))}
    if not sh: continue
    hits=[]
    for oa,ob,os_,osh_ in osh:
        c=len(sh&osh_)
        if c/len(sh)>=0.15 or (len(osh_)>=40 and c/len(osh_)>=0.6): hits.append((oa,os_,c/len(sh)))
    hits.sort()
    P(f"| {s['src'].replace('chapter-','').replace('.xhtml','')} | {s['title'][:60]} | " + '<br>'.join(f"{o['src'].split('/')[-1]} · {o['title'][:40]}" for _,o,_ in hits) + ' | ' + ' '.join(f'{100*c:.0f}%' for _,_,c in hits) + ' |')
P('\nSections of ours with no chapter above: ' + ', '.join(sorted({f"{s['src'].split('/')[-1]} · {s['title'][:30]}" for a,b,s in DO if b-a>=200 and sum(1 for i in range(a,b) if CO[i])/(b-a)<0.5})))
def fmt(e,plus,minus):
    cut=lambda s:(s if len(s)<=600 else s[:300]+' […] '+s[-250:])
    cp=e['cp']; cpx=('∅ (nothing there)' if cp=='' else cut(cp)) if cp is not None else '? (no counterpart found within 1500 chars)'
    return f"- **{e['sec']}** · {len(e['seg'])} chars\n  …{e['ctx_a']}⟦{plus} {cut(e['seg'])}⟧{e['ctx_b']}…\n  ⟦{minus} {cpx}⟧"
big=[e for e in newruns if len(e['seg'])>=40]; small=[e for e in newruns if len(e['seg'])<40]
P(f'\n## A. Passages in the NEW book that ours lacks (≥40 chars) — {len(big)}\n\n`+` new book · `−` ours at that spot\n')
for e in sorted(big,key=lambda e:-len(e['seg'])): P(fmt(e,'+','−')); P('')
bigo=[e for e in ourruns if len(e['seg'])>=40]; smallo=[e for e in ourruns if len(e['seg'])<40]
P(f'\n## B. Passages in OUR book that the new one lacks (≥40 chars) — {len(bigo)}\n\n`−` ours · `+` new book at that spot\n')
for e in sorted(bigo,key=lambda e:-len(e['seg'])): P(fmt(e,'−','+')); P('')
P(f'\n## C. Small variants (<40 chars)\n\nSpellings, particles, shad forms, dropped or added syllables. Grouped by (new, ours) pair; most frequent first. `∅` = the other book has nothing there.\n')
grp=collections.defaultdict(list)
for e in small: grp[(e['seg'],e['cp'])].append(e)
P(f'### C1. Seen from the new book ({len(small)} runs, {len(grp)} distinct)\n')
P('| n | new book | ours | where (first) | context (new) |'); P('|---|---|---|---|---|')
for (seg,cp),es in sorted(grp.items(),key=lambda kv:(-len(kv[1]),kv[0][0])):
    e=es[0]; cpx='?' if cp is None else ('∅' if cp=='' else cp)
    P(f"| {len(es)} | {seg} | {cpx} | {e['sec']} | …{e['ctx_a'][-16:]}⟦{seg}⟧{e['ctx_b'][:16]}… |")
newcps=set(e['cp'] for e in small if e['cp'])
rest=[e for e in smallo if e['seg'] not in newcps]
grp2=collections.defaultdict(list)
for e in rest: grp2[(e['seg'],e['cp'])].append(e)
P(f'\n### C2. Seen only from our side ({len(rest)} runs, {len(grp2)} distinct) — usually a syllable ours has and the new book lacks\n')
P('| n | ours | new book | where (first) | context (ours) |'); P('|---|---|---|---|---|')
for (seg,cp),es in sorted(grp2.items(),key=lambda kv:(-len(kv[1]),kv[0][0])):
    e=es[0]; cpx='?' if cp is None else ('∅' if cp=='' else cp)
    P(f"| {len(es)} | {seg} | {cpx} | {e['sec']} | …{e['ctx_a'][-16:]}⟦{seg}⟧{e['ctx_b'][:16]}… |")
open(sys.argv[3],'w',encoding='utf-8').write('\n'.join(out))
print(out[3]);print(out[4]);print('big new',len(big),'big ours',len(bigo),'small new',len(small),'distinct',len(grp),'small ours-only',len(rest),'distinct',len(grp2))
