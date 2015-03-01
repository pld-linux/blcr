# NOTE: probably doesn't work with kernel address space randomization(?)
#
# Conditional build:
%bcond_without	static_libs	# static library
%bcond_without	kernel		# kernel modules
%bcond_without	userspace	# userspace library and utilities
%bcond_with	verbose		# verbose build (V=1) of kernel modules
#
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define	pname	blcr
%define	rel	5
Summary:	Berkeley Lab Checkpoint/Restart for Linux
Summary(pl.UTF-8):	Berkeley Lab Checkpoint/Restart dla Linuksa
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	0.8.5
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	LGPL v2+ (library), GPL v2+ (utilities and modules)
Group:		Libraries
#Source0Download: http://crd.lbl.gov/departments/computer-science/CLaSS/research/BLCR/berkeley-lab-checkpoint-restart-for-linux-blcr-downloads/
Source0:	http://crd.lbl.gov/assets/Uploads/FTG/Projects/CheckpointRestart/downloads/%{pname}-%{version}.tar.gz
# Source0-md5:	e0e6d3f6c117d820eaafabf2599ad37b
# extract from diff against https://upc-bugs.lbl.gov/blcr-dist/blcr-0.8.6_b4.tar.gz
Patch0:		%{pname}-update.patch
Patch1:		%{pname}-am.patch
URL:		http://crd.lbl.gov/departments/computer-science/CLaSS/research/BLCR/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	perl-base
%if %{with userspace}
BuildRequires:	ftb-devel
BuildRequires:	glibc-devel >= 5:2.4
%endif
%if %{with kernel}
BuildRequires:	rpmbuild(macros) >= 1.701
# for System.map symbol lookups
%{expand:%buildrequires_kernel kernel%%{_alt_kernel} = %%{kernel_version}}
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build = %%{kernel_version}}
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6}
%endif
ExclusiveArch:	%{ix86} %{x8664} x32 arm ppc ppc64 sparc sparcv9 sparc64
ExcludeArch:	i386
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Berkeley Lab Checkpoint/Restart (BLCR) for Linux is a project of
Future Technologies Group researchers to develop a hybrid kernel/user
implementation of checkpoint/restart. Their goal is to provide a
robust, production quality implementation that checkpoints a wide
range of applications, without requiring changes to be made to
application code. This work focuses on checkpointing parallel
applications that communicate through MPI, and on compatibility with
the software suite produced by the SciDAC Scalable Systems Software
ISIC.

%description -l pl.UTF-8
Berkeley Lab Checkpoint/Restart (BLCR) dla Linuksa to projekt badaczy
Future Technologies Group polegający na stworzeniu hybrydowej
(działającej w jądrze i przestrzeni użytkownika) implementacji
mechanizmu checkpoint/restart (punktów kontrolnych i restartów
programów). Celem jest dostarczenie bogatej, mającej produkcyjną
jakość implementacji potrafiącej wykonać migawki stanu szerokiej gamy
aplikacji bez potrzeby wykonywania zmian w ich kodzie. Praca skupia
się na aplikacjach równoległych komunikujących się poprzez MPI oraz
zgodności z oprogramowaniem tworzonym przez SciDAC Scalable Systems
Software ISIC.

%package devel
Summary:	Header files for BLCR library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki BLCR
License:	LGPL v2+
Group:		Development/Libraries
Requires:	%{pname} = %{version}-%{release}

%description devel
Header files for BLCR library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki BLCR.

%package static
Summary:	Static BLCR library
Summary(pl.UTF-8):	Statyczna biblioteka BLCR
License:	LGPL v2+
Group:		Development/Libraries
Requires:	%{pname}-devel = %{version}-%{release}

%description static
Static BLCR library.

%description static -l pl.UTF-8
Statyczna biblioteka BLCR.

%define kernel_pkg()\
%package -n kernel%{_alt_kernel}-misc-blcr\
Summary:	BLCR modules for Linux kernel\
Summary(pl.UTF-8):	Moduły BLCR dla jądra Linuksa\
Release:	%{rel}@%{_kernel_ver_str}\
License:	GPL v2+\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-misc-blcr\
BLCR modules for Linux kernel.\
\
%description -n kernel%{_alt_kernel}-misc-blcr -l pl.UTF-8\
Moduły BLCR dla jądra Linuksa.\
\
%files -n kernel%{_alt_kernel}-misc-blcr\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/misc/blcr.ko*\
/lib/modules/%{_kernel_ver}/misc/blcr_imports.ko*\
\
%post	-n kernel%{_alt_kernel}-misc-blcr\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-misc-blcr\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%configure \\\
	%{?with_verbose:--enable-kbuild-verbose} \\\
	--with-linux=%{_kernel_ver} \\\
	--with-linux-src=%{_kernelsrcdir} \\\
	--with-kmod-dir=/lib/modules/%{_kernel_ver}/misc \\\
	--with-system-map=/boot/System.map-%{_kernel_ver} \\\
	--with-components="%{?with_kernel:modules}"\
\
%{__make} clean\
%{__make}\
p=`pwd`\
%{__make} install DESTDIR=$p/installed\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}

%{?with_kernel:%{expand:%build_kernel_packages}}

%if %{with userspace}
%configure \
	%{?with_static_libs:--enable-static} \
	--with-components="%{?with_userspace:util libcr include tests examples contrib}"

%{__make} clean
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc LICENSE.txt NEWS README.FTB doc/{README,html}
%attr(755,root,root) %{_bindir}/cr_checkpoint
%attr(755,root,root) %{_bindir}/cr_restart
%attr(755,root,root) %{_bindir}/cr_run
%attr(755,root,root) %{_libdir}/libcr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcr.so.0
%attr(755,root,root) %{_libdir}/libcr_omit.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcr_omit.so.0
%attr(755,root,root) %{_libdir}/libcr_run.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcr_run.so.0
%{_mandir}/man1/cr_checkpoint.1*
%{_mandir}/man1/cr_restart.1*
%{_mandir}/man1/cr_run.1*

%files devel
%defattr(644,root,root,755)
%doc README.devel
%attr(755,root,root) %{_libdir}/libcr.so
%attr(755,root,root) %{_libdir}/libcr_omit.so
%attr(755,root,root) %{_libdir}/libcr_run.so
%{_libdir}/libcr.la
%{_libdir}/libcr_omit.la
%{_libdir}/libcr_run.la
%{_includedir}/blcr_*.h
%{_includedir}/libcr.h

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libcr.a
%{_libdir}/libcr_omit.a
%{_libdir}/libcr_run.a
%endif
%endif
