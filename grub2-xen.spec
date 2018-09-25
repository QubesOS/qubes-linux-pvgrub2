# Prevents fails-to-build-from-source.
%undefine _hardened_build

# Modules always contain just 32-bit code
%define _libdir %{_exec_prefix}/lib

%if 0%{?qubes_builder}
%define _sourcedir %(pwd)
%endif

%global tarversion 2.02
%undefine _missing_build_ids_terminate_build

Name:           grub2-xen
Version:        2.02
Release:        4%{?dist}
Summary:        Bootloader with support for Linux, Multiboot and more, for Xen PV

Group:          System Environment/Base
License:        GPLv3+
URL:            http://www.gnu.org/software/grub/
Source0:        http://ftp.gnu.org/gnu/grub/grub-%{tarversion}.tar.xz
Source1:        grub-bootstrap.cfg
Source2:        grub-xen.cfg
Patch0:         grub-alias-linux16.patch

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

Requires:	gettext os-prober which file

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

%prep
%setup -q -n grub-%{tarversion}
cp %{SOURCE1} %{SOURCE2} ./

%patch0 -p1

%build
./autogen.sh
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

%install
set -e
rm -fr $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install
find $RPM_BUILD_ROOT -iname "*.module" -exec chmod a-x {} \;

install -d $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2
install -m 0644 grub-x86_64-xen.bin $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2/
ln -s grub-x86_64-xen.bin $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2/vmlinuz
# "empty" file file so Qubes tools does not complain
echo -n | gzip > $RPM_BUILD_ROOT/var/lib/qubes/vm-kernels/pvgrub2/initramfs

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

%files tools
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%{_mandir}

%changelog

