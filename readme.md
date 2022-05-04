## **LZ4: Compression algorithm**

---

LZ4 is a lossless data compression algorithm that is focused on compression and decompression speed. 
It belongs to the LZ77 family of byte-oriented compression schemes.

In this project, three versions are created that use this algorithm to compress data.
Some files are given to try.

**lz: Normal compressor**

---

This version tries to find between time and compression ratio. 

To compress a file using this version, just run:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python lz4.py -c filename`

To decompress a file using this version, just run:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python lz4.py -d filename`

**lz_T: Fast compressor**

---

This version tries to compress file in the best time possible

To compress a file using this version, just run:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python lz4_T.py -c filename`

To decompress a file using this version, just run:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python lz4_T.py -d filename`

**lz_R: High compressor**

---

This version tries to compress file with highest compression ratio

To compress a file using this version, just run:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python lz4_R.py -c filename`

To decompress a file using this version, just run:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python lz4_R.py -d filename`






