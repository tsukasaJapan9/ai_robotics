# gob_GC0308 の依存ライブラリ（quirc）が古いCコードを使っているため、Cコンパイラのみに警告抑制フラグを適用する
Import("env")
env.Append(CFLAGS=["-Wno-implicit-function-declaration", "-Wno-int-conversion"])
