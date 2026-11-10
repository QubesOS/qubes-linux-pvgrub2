# Qubes PV-GRUB2

This is part of [Qubes OS](https://www.qubes-os.org). It builds GRUB2 for the
Xen PV and PVH platforms. The RPMs (`grub2-xen`, `grub2-xen-pvh`) install two
selectable qube kernels, `pvgrub2` (Xen PV) and `pvgrub2-pvh` (Xen PVH), so a
qube can boot a kernel from inside its own filesystem instead of one provided
by dom0.

GRUB2 runs as the qube's kernel; it then finds and boots the kernel installed
inside the qube, or chainloads the qube's own Xen or GRUB configuration. This
lets a qube manage its own kernel, which a dom0-provided kernel does not allow.

See [Managing qube kernels](https://www.qubes-os.org/doc/managing-vm-kernels/)
for how to use it.
