# TODO: multi-kernels build?
# NOTE: probably doesn't work with kernel address space randomization(?)
#
# Conditional build:
%bcond_without	static_libs	# static library
%bcond_without	kernel		# kernel modules
%bcond_without	userspace	# userspace library and utilities
%bcond_with	verbose		# verbose build (V=1) of kernel modules
#
Summary:	Berkeley Lab Checkpoint/Restart for Linux
Summary(pl.UTF-8):	Berkeley Lab Checkpoint/Restart dla Linuksa
%define	pname	blcr
Name:		%{pname}
Version:	0.8.5
%define	rel	1
Release:	%{rel}
License:	LGPL v2+ (library), GPL v2+ (utilities and modules)
Group:		Libraries
#Source0Download: http://crd.lbl.gov/departments/computer-science/CLaSS/research/BLCR/berkeley-lab-checkpoint-restart-for-linux-blcr-downloads/
Source0:	http://crd.lbl.gov/assets/Uploads/FTG/Projects/CheckpointRestart/downloads/%{pname}-%{version}.tar.gz
# Source0-md5:	e0e6d3f6c117d820eaafabf2599ad37b
URL:		http://crd.lbl.gov/departments/computer-science/CLaSS/research/BLCR/
%if %{with userspace}
BuildRequires:	ftb-devel
BuildRequires:	glibc-devel >= 5:2.4
%endif
BuildRequires:	perl-base
%if %{with kernel}
# for System.map and vmlinux symbol lookups
BuildRequires:	kernel%{_alt_kernel} = 3:%{_kernel_ver}
BuildRequires:	kernel%{_alt_kernel}-module-build = 3:%{_kernel_ver}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6
%endif
ExclusiveArch:	%{ix86} %{x8664} arm ppc ppc64 sparc sparcv9 sparc64
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

%package -n kernel%{_alt_kernel}-extra-blcr
Summary:	BLCR modules for Linux kernel
Summary(pl.UTF-8):	Moduły BLCR dla jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2+
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%requires_releq_kernel
Requires(postun):	%releq_kernel

%description -n kernel%{_alt_kernel}-extra-blcr
BLCR modules for Linux kernel.

%description -n kernel%{_alt_kernel}-extra-blcr -l pl.UTF-8
Moduły BLCR dla jądra Linuksa.

%prep
%setup -q

%build
%configure \
	%{?with_static_libs:--enable-static} \
%if %{with kernel}
	%{?with_verbose:--enable-kbuild-verbose} \
	--with-linux=%{_kernel_ver} \
	--with-linux-src=%{_kernelsrcdir} \
	--with-system-map=/boot/System.map-%{_kernel_ver} \
	--with-vmlinux=/boot/vmlinuz-%{_kernel_ver} \
%endif
	--with-components="%{?with_kernel:modules} %{?with_userspace:util libcr include tests examples contrib}"

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel%{_alt_kernel}-extra-blcr
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-extra-blcr
%depmod %{_kernel_ver}

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

%if %{with kernel}
%files -n kernel%{_alt_kernel}-extra-blcr
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/extra/blcr.ko*
/lib/modules/%{_kernel_ver}/extra/blcr_imports.ko*
%endif
