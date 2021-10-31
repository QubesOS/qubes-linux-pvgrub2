# This package calls binutils components directly and would need to pass
# in flags to enable the LTO plugins
# Disable LTO
%global _lto_cflags %{nil}

# Prevents fails-to-build-from-source.
%undefine _hardened_build

# Modules always contain just 32-bit code
%define _libdir %{_exec_prefix}/lib

%global tarversion 2.06
%undefine _missing_build_ids_terminate_build

%global _configure ../configure

Name:           grub2-xen
Version:        2.06
Release:        1%{?dist}
Summary:        Bootloader with support for Linux, Multiboot and more, for Xen PV

Group:          System Environment/Base
License:        GPLv3+
URL:            https://www.gnu.org/software/grub/
Source0:        https://ftp.gnu.org/gnu/grub/grub-%{tarversion}.tar.xz
Source1:        grub-bootstrap.cfg
Source2:        grub-xen.cfg
Patch0:         grub-alias-linux16.patch

BuildRequires:  gcc
BuildRequires:  flex bison binutils python
BuildRequires:  ncurses-devel xz-devel
BuildRequires:  freetype-devel libusb-devel
%ifarch %{sparc} x86_64
# sparc builds need 64 bit glibc-devel - also for 32 bit userland
BuildRequires:  /usr/lib64/crt1.o glibc-static
%else
# ppc64 builds need the ppc crt1.o
BuildRequires:  /usr/lib/crt1.o glibc-static
%endif
BuildRequires:  autoconf automake autogen device-mapper-devel
BuildRequires:	freetype-devel gettext-devel git
BuildRequires:	texinfo
BuildRequires:	dejavu-sans-fonts
BuildRequires:	help2man
BuildRequires:	xen-devel

Requires:	gettext which file

ExcludeArch:	s390 s390x %{arm}

%description
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for PC BIOS systems.

%package tools
Summary:	Support tools for GRUB.
Group:		System Environment/Base
Requires:	gettext which file system-logos

%description tools
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides tools for support of all platforms.

%package pvh
Summary:	Bootloader with support for Linux, Multiboot and more, for Xen PVH
Group:		System Environment/Base
Requires:	gettext which file

%description pvh
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for Xen PVH.

%prep
%autosetup -p1 -n grub-%{tarversion}
mkdir grub-xen-x86_64
cp %{SOURCE1} %{SOURCE2} grub-xen-x86_64/
mkdir grub-xen_pvh-i386
cp %{SOURCE1} %{SOURCE2} grub-xen_pvh-i386/

%build
./autogen.sh
cd grub-xen-x86_64
%configure							\
	CFLAGS="$(echo $RPM_OPT_FLAGS | sed			\
		-e 's/-O.//g'					\
		-e 's/-fstack-protector\(-[[:alnum:]]\+\)*//g'	\
		-e 's/-Wp,-D_FORTIFY_SOURCE=[[:digit:]]//g'	\
		-e 's/--param=ssp-buffer-size=4//g'		\
		-e 's/-mregparm=3/-mregparm=4/g'		\
		-e 's/-fexceptions//g'				\
		-e 's/-fasynchronous-unwind-tables//g' )"	\
	TARGET_LDFLAGS=-static					\
	--with-platform=xen					\
	--with-grubdir=%{name}					\
	--program-transform-name=s,grub,%{name},		\
	--disable-grub-mount					\
	--disable-werror
make %{?_smp_mflags}
tar cf memdisk.tar grub-xen.cfg
./grub-mkimage -O x86_64-xen -o grub-x86_64-xen.bin \
		-c grub-bootstrap.cfg -m memdisk.tar -d grub-core grub-core/*.mod
cd ..
cd grub-xen_pvh-i386
%configure							\
	CFLAGS="$(echo $RPM_OPT_FLAGS | sed			\
		-e 's/-m64//g'					\
		-e 's/-O.//g'					\
		-e 's/-fstack-protector\(-[[:alnum:]]\+\)*//g'	\
		-e 's/-Wp,-D_FORTIFY_SOURCE=[[:digit:]]//g'	\
		-e 's/--param=ssp-buffer-size=4//g'		\
		-e 's/-mregparm=3/-mregparm=4/g'		\
		-e 's/-fexceptions//g'				\
		-e 's/-fasynchronous-unwind-tables//g' )"	\
	TARGET_LDFLAGS=-static					\
    --target=i386-redhat-linux-gnu				\
	--with-platform=xen_pvh	    				\
	--with-grubdir=%{name}-pvh				\
	--program-transform-name=s,grub,%{name}-pvh,		\
	--disable-grub-mount					\
	--disable-werror
make %{?_smp_mflags}
tar cf memdisk.tar grub-xen.cfg
./grub-mkimage -O i386-xen_pvh -o grub-i386-xen_pvh.bin \
		-c grub-bootstrap.cfg -m memdisk.tar -d grub-core grub-core/*.mod
cd ..

%install
set -e
rm -fr $RPM_BUILD_ROOT

for dir in grub-xen-x86_64 grub-xen_pvh-i386; do
    make -C $dir DESTDIR=$RPM_BUILD_ROOT install
done
find $RPM_BUILD_ROOT -iname "*.module" -exec chmod a-x {} \;

install -d $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2
install -m 0644 grub-xen-x86_64/grub-x86_64-xen.bin $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2/
ln -s grub-x86_64-xen.bin $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2/vmlinuz
# "empty" file file so Qubes tools does not complain
echo -n | gzip > $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2/initramfs

install -d $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2-pvh
install -m 0644 grub-xen_pvh-i386/grub-i386-xen_pvh.bin $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2-pvh/
ln -s grub-i386-xen_pvh.bin $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2-pvh/vmlinuz
# "empty" file file so Qubes tools does not complain
echo -n | gzip > $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2-pvh/initramfs

# Install ELF files modules and images were created from into
# the shadow root, where debuginfo generator will grab them from
find $RPM_BUILD_ROOT -name '*.mod' -o -name '*.img' |
while read MODULE
do
        BASE=$(echo $MODULE |sed -r "s,.*/([^/]*)\.(mod|img),\1,")
        # Symbols from .img files are in .exec files, while .mod
        # modules store symbols in .elf. This is just because we
        # have both boot.img and boot.mod ...
        EXT=$(echo $MODULE |grep -q '.mod' && echo '.elf' || echo '.exec')
        TGT=$(echo $MODULE |sed "s,$RPM_BUILD_ROOT,.debugroot,")
#        install -m 755 -D $BASE$EXT $TGT
done

rm $RPM_BUILD_ROOT%{_infodir}/grub.info
rm $RPM_BUILD_ROOT%{_infodir}/grub-dev.info
rm $RPM_BUILD_ROOT%{_infodir}/dir

rm -r $RPM_BUILD_ROOT%{_sysconfdir}
rm -r $RPM_BUILD_ROOT%{_datarootdir}/grub
rm -r $RPM_BUILD_ROOT%{_datarootdir}/locale

%clean    
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_libdir}/grub/*-xen/
/var/lib/qubes/vm-kernels/pvgrub2/grub-x86_64-xen.bin
/var/lib/qubes/vm-kernels/pvgrub2/vmlinuz
/var/lib/qubes/vm-kernels/pvgrub2/initramfs
%doc COPYING

%files pvh
%defattr(-,root,root,-)
%{_libdir}/grub/*-xen_pvh/
/var/lib/qubes/vm-kernels/pvgrub2-pvh/grub-i386-xen_pvh.bin
/var/lib/qubes/vm-kernels/pvgrub2-pvh/vmlinuz
/var/lib/qubes/vm-kernels/pvgrub2-pvh/initramfs
%doc COPYING


%files tools
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%{_mandir}

%changelog

