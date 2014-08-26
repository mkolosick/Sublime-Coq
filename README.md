Sublime Coq
===========

Extensions to the Sublime Text 3 editor for use with the Coq programming language.

Highlighting
------------

In order to get nice background highlighting for the proven parts of the file,
add this to your theme (for light backgrounds):

```
<dict>
  <key>name</key>
  <string>Proven by Coq</string>
  <key>scope</key>
  <string>meta.coq.proven</string>
  <key>settings</key>
  <dict>
    <key>background</key>
    <string>#dcffcc</string>
  </dict>
</dict>
```

Mac OS X
--------

On OS X, you may need to use [SublimeFixMacPath package](https://github.com/int3h/SublimeFixMacPath) if coqtop is not present in your system path.
