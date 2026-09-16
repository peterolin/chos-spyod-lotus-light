# A7 — large shad hard against yig chung

Rule (Peter, 2026-09-16): a tibnormal span that ENDS in a shad, followed by a yig chung span with NO whitespace
between the two tags, is a mismatch — that shad belongs to the small letters. This list is exactly those.

Regex, for VS Code Find in Files with `.*` on:

```
<span class="tibnormal">[^<]*[།༔]</span><span class="tibyigchungH?">
```

Fix: move the shad from the end of the large span to the start of the small one. The search string below is the
end of the large span, tag included — paste it into Find (regex OFF) in the file named.

21 rows.

| done | page | file | line | large span ends | small span begins | search string |
|---|---|---|---|---|---|---|
| [ ] | 220 | p219_220_247.htm | 66 | …ཨོཾ་པདྨ་དྷཱ་རི་ཧཱུྃ། |  བཻཌཱུརྻའི་གཟུངས་རིང… | `་ཧཱུྃ།</span>` |
| [ ] | 257 | p257_leu_bdun_ma.htm | 16 | …གུ་རུ་ན་མོ༔ | ཨོ་རྒྱན་རིན་པོ་ཆེའི་… | `་ན་མོ༔</span>` |
| [ ] | 362 | p362.htm | 56 | …འབེབས་བདག་ལ་གཟིགས། ། | བསོད་ནམས་དང་ཡེ་ཤེས་ཀ… | `ིགས།
།</span>` |
| [ ] | 362 | p362.htm | 62 | …ན་པའི་དོན་དུ་བསྔོ། ། | ཡོན་ཏན་རྗེས་སུ་དྲན་ཞ… | `སྔོ།
།</span>` |
| [ ] | 362 | p362.htm | 69 | …་གྲུབ་སྩལ་དུ་གསོལ། ། | རྡོ་རྗེའི་ཚིག་རྐང་གི… | `སོལ།
།</span>` |
| [ ] | 362 | p362.htm | 82 | …ཀྱི་རྡོ་རྗེར་གྱུར། ། | བསྡུ་རིམ་ནི། … | `ྱུར།
།</span>` |
| [ ] | 395 | p378_.htm | 148 | …འ་ཡས་ལ་ཕྱག་འཚལ་ལོ། ། | འདའ་ཁའི་གདམས་པ་བྱིན་… | `་ལོ།
།</span>` |
| [ ] | 395 | p378_.htm | 150 | …་མེད་ཀ་དག་ངང་ལ་བཞག ། | ཅེས་བསྲེ་བ་གསུམ་གྱི་… | `་བཞག
།</span>` |
| [ ] | 425 | c_53.htm | 50 | …དམ་ཚིག་ཉམས་པ་བཤགས། ། | ཞེས་དང་། … | `ཤགས།
།</span>` |
| [ ] | 425 | c_53.htm | 63 | …་གྲུབ་སྩལ་དུ་གསོལ། ། | ཞེས་དྲི་མེད་བཤགས་རྒྱ… | `སོལ།
།</span>` |
| [ ] | 445 | c_59.htm | 38 | …ི་ནམ་མཁར་བཛྲ་ས་མཱ་ཛ༔ | ས་སྤྱན་དྲངས་པར་བསམས་… | `་མཱ་ཛ༔</span>` |
| [ ] | 450 | c_59.htm | 154 | …ཨོཾ་ཨཱཿཧཱུྃ་ཧོ༔ | ས་བརླབ། … | `ུྃ་ཧོ༔</span>` |
| [ ] | 450 | c_59.htm | 172 | …མས་ཅན་དོན་ཀུན་མཛད། ། | སོགས། … | `མཛད།
།</span>` |
| [ ] | 546 | c_78.htm | 18 | …འི་བླ་མ་རིན་པོ་ཆེ། ། | སོགས་དང་། … | `་ཆེ།
།</span>` |
| [ ] | 546 | c_78.htm | 38 | …མས་ཅན་སྙིང་རེ་རྗེ། ། | རྐང་གླིང་ཁ་བརྡབ་དང་།… | `རྗེ།
།</span>` |
| [ ] | 546 | c_78.htm | 41 | …ྲིན་ཅན་ཕ་མའི་ཚོགས། ། | དེ་ནས་མཆོག་གསུམ་གྱི་… | `ོགས།
།</span>` |
| [ ] | 557 | c_79.htm | 17 | …ོ་འཕང་མྱུར་ཐོབ་ཤོག ། | ཅེས་པའང་དགེ་སྦྱོང་ཀར… | `་ཤོག
།</span>` |
| [ ] | 558 | c_80.htm | 18 | …ན་པོ་ལ་ཕྱག་འཚལ་ལོ། ། | འདིར་ཐུགས་རྗེ་ཆེན་པོ… | `་ལོ།
།</span>` |
| [ ] | 558 | c_80.htm | 66 | …ཨོཾ་ཨཱཿཧཱུྃ༔ | ལན་གསུམ། … | `ཿཧཱུྃ༔</span>` |
| [ ] | 723 | c_105.htm | 146 | …ན་རིང་གནས་གྱུར་ཅིག ། | ཅེས་དང་། … | `་ཅིག
།</span>` |
| [ ] | 735 | c_106.htm | 79 | …ྒྱན་དུ་ཡུན་གནས་ཤོག ། | བདུད་འཇོམས་པས་སོ།།… | `་ཤོག
།</span>` |
