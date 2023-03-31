# Please keep this package in sync with FC

%global major   4
%define libname %mklibname capstone %major
%define devname %mklibname capstone -d

# don't provide libcapstone.so.3 with py2/3 pkgs
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{python_sitelib}/.*\.so
%bcond_with java

Name:           capstone
Version:        4.0.2
Release:        2
Summary:        A lightweight multi-platform, multi-architecture disassembly framework
Group:          System/Libraries

%global         gituser         aquynh
%global         gitname         capstone

License:        BSD
URL:            http://www.capstone-engine.org/
#               https://github.com/aquynh/capstone/releases
#Source0:        https://github.com/%{gituser}/%{gitname}/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
Source0:        https://github.com/%{gituser}/%{gitname}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

%global srcname distribute

BuildRequires:  git
%if %{with java}
BuildRequires:  jna
BuildRequires:  java-devel
%endif
BuildRequires:  python-devel
BuildRequires:  python-setuptools
%global _hardened_build 1


%description
Capstone is a disassembly framework with the target of becoming the ultimate
disasm engine for binary analysis and reversing in the security community.

%package        -n %libname
Summary:        A lightweight multi-platform, multi-architecture disassembly framework
Group:          System/Libraries
Obsoletes:      %{_lib}capstone0 < 3.0.4-3

%description    -n %libname
Capstone is a disassembly framework with the target of becoming the ultimate
disasm engine for binary analysis and reversing in the security community.

%package        -n %devname
Summary:        Development files for %{name}
Group:		Development/Other
Requires:       %{libname}%{?_isa} = %{version}-%{release}
Provides:	capstone-devel = %{version}-%{release}

%description    -n %devname
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package	-n python-capstone
Summary:	Python3 bindings for %{name}
Group:		Development/Python
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description	-n python-capstone
The python-%{name} package contains python3 bindings for %{name}.

%if %{with java}
%package        java
Summary:        Java bindings for %{name}
Group:          Development/Java
Requires:       %{name} >= %{version}-%{release}
BuildArch:      noarch

%description    java
The %{name}-java package contains java bindings for %{name}.
%endif

%prep
# autosetup -n %{gitname}-%{commit} -S git
%autosetup -n %{gitname}-%{version} -S git

%build
DESTDIR="%{buildroot}" 	V=1 CFLAGS="%{optflags}" \
LIBDIRARCH="%{_lib}" INCDIR="%{_includedir}" \
make PYTHON3=%{__python} %{?_smp_mflags}

# Fix pkgconfig file
sed -i 's;%{buildroot};;' capstone.pc
grep -v archive capstone.pc > capstone.pc.tmp
mv capstone.pc.tmp capstone.pc

# build python bindings
pushd bindings/python
%py3_build
popd

%if %{with java}
# build java bindings
pushd bindings/java
make PYTHON3=%{__python} CFLAGS="%{optflags}" # %{?_smp_mflags} parallel seems broken
popd
%endif

%install
DESTDIR=%{buildroot} LIBDIRARCH=%{_lib} \
INCDIR="%{_includedir}" make install
find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'

# install python bindings
pushd bindings/python
%py3_install
popd

%if %{with java}
# install java bindings
install -D -p -m 0644 bindings/java/%{name}.jar  %{buildroot}/%{_javadir}/%{name}.jar
%endif

%files
%{_bindir}/cstool

%files -n %libname
%license LICENSE.TXT LICENSE_LLVM.TXT
%doc CREDITS.TXT ChangeLog README.md SPONSORS.TXT
%{_libdir}/*.so.%{major}{,.*}

%files -n %devname
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%files -n python-capstone
%{python_sitelib}/*egg-info
%{python_sitelib}/%{name}

%if %{with java}
%files java
%{_javadir}/
%endif
