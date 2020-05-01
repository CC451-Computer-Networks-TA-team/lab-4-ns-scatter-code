import fcntl
import struct
import os
import errno

# https://github.com/firecracker-microvm/firecracker/blob/ebc15f2eacaa4c26782a05f8e0cebe4c47512553/src/vmm/src/default_syscalls/mod.rs#L64
# https://gist.github.com/glacjay/585369#file-tun-ping-linux-py-L9
TUNSETIFF = 0x400454ca

# https://chromium.googlesource.com/chromiumos/platform/flimflam/+/refs/heads/0.11.257.B90/tools/tap-test.c#101
# https://elixir.bootlin.com/linux/latest/source/include/uapi/linux/if_tun.h#L37
TUNSETLINK = 0x400454cd

# https://github.com/torvalds/linux/blob/bd2463ac7d7ec51d432f23bf0e893fb371a908cd/include/uapi/linux/if.h#L33
IFNAMSIZ = 16

# https://github.com/torvalds/linux/blob/80f232121b69cc69a31ccb2b38c1665d770b0710/include/uapi/linux/if_tun.h#L65
IFF_TUN = 0x0001
IFF_TAP = 0x0002

# Ignore packet data added by the Linux kernel.
IFF_NO_PI = 0x1000

# https://unix.superglobalmegacorp.com/BSD4.4/newsrc/net/if_arp.h.html
ARPHRD_ETHER = 1

def print_sys_err(e):
    # The errno variable is pretty interesting, check it out.
    # that's why C functions return -1 only. Because they set errno.
    print(f"Error [{errno.errorcode[e.errno]}]: {os.strerror(e.errno)}")


dev_name = "tap0"
# https://docs.python.org/3/library/io.html#raw-i-o
fd = open("/dev/net/tun", "r+b", buffering=0)

# https://github.com/torvalds/linux/blob/bd2463ac7d7ec51d432f23bf0e893fb371a908cd/include/uapi/linux/if.h#L233
# Convert an ifreq to bytes, to pass it to ioctl.
dev_name_bytes = bytes(dev_name, "ascii")
ifreq = struct.pack("{}sH".format(IFNAMSIZ),
                    dev_name_bytes, IFF_TAP | IFF_NO_PI)
try:
    fcntl.ioctl(fd, TUNSETIFF, ifreq)
    fcntl.ioctl(fd, TUNSETLINK, ARPHRD_ETHER)
    # Now you have a dead device that you need to give an IP and "up"
except Exception as e:
    print_sys_err(e)
    exit(-1)
