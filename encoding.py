s = "python"
b_ascii = s.encode("ascii")
b_utf8 = s.encode("utf-8")
print(b_ascii, b_ascii.hex())
print(b_utf8, b_utf8.hex())

s = "питон"
#b_ascii = s.encode("ascii")
b_utf8 = s.encode("utf-8")
#print(b_ascii, b_ascii.hex())
print(b_utf8, b_utf8.hex())

b = b"\x10\x26\x35\x46\x73"
s_ascii = b.decode("ascii")
s_utf8 = b.decode("utf-8")
print(b, s_ascii)
print(b, s_utf8)