#!/bin/bash
echo "[+] Waiting for connections"
socat -T 120 tcp-l:1337,reuseaddr,fork EXEC:"./run.sh",pty,stderr
echo "[+] Exiting"
