# barcode-generator
Proof of concept barcode sequence generator

Takes a range of badge numbers from a .yaml file and generates a CSV of barcode-friendly ready to be printed random IDs

We use the OS's urandom() function which returns cryptologically unique numbers.

Generates results like this:

```
1000,N7YXNALRJT82P94MXSSEQG
1001,WEIR1SGE2R+0ODPGFPHETG
1002,EMAEHRPITUPLYOTWU/XA8G
1003,Z3GI/LEEN8SYBRUYEAU4JG
1004,XHR69UBC3ATTZCEISJ+NCA
1005,TDDYB/UNGJURKQR1CKFXLW
1006,8EYVQWGF3YYMTXGLNFWY4G
...snip...
2000,AMLYSZ8SOIOOTYKXODVGWW
2001,U6CNI+PJB9+IBEG8Z/DEBW
2002,AMV396OVEQ/RJLGSOKNEZA
...snip...
```

This whole thing might want to be more carefully thought out inside ubersystem, but for now here's some proof of concept code.
