%define build_java 1
%define build_autotools 1

# commandline overrides:
# rpm -ba|--rebuild --with 'xxx'
%{?_with_java: %{expand: %%global build_java 1}}
%{?_without_java: %{expand: %%global build_java 0}}
%{?_with_autotools: %{expand: %%global build_autotools 1}}
%{?_without_autotools: %{expand: %%global build_autotools 0}}

Summary:	Extensible modeling tool for MySQL 5.x
Name:		mysql-workbench-oss
Group:		Databases
Version:	5.2.31
Release:	%mkrel 1
License:	GPL
URL:		http://dev.mysql.com/downloads/workbench/
# ftp://ftp.pbone.net/mirror/dev.mysql.com/pub/Downloads/MySQLGUITools/mysql-workbench-5.1.4-1fc9.src.rpm
Source0:	ftp://ftp.mysql.com/pub/mysql/download/gui-tools/mysql-workbench-gpl-%{version}a-src.tar.gz
Patch0:		mysql-workbench-oss-5.1.16_buildfix_gcc-4_4.patch
Patch1:		mysql-workbench-oss-5.1.16_remove-internal-ext.patch
Patch2:		mysql-workbench-gpl-5.2.27-use_-avoid-version_for_plugins.patch
Patch3:		mysql-workbench-gpl-5.2.27-linkage.patch
Obsoletes:	mysql-workbench < 5.1.6
Provides:	mysql-workbench
BuildRequires:	autoconf2.5
BuildRequires:	boost-devel >= 1.35.0
BuildRequires:	cairo-devel
BuildRequires:	cairomm-devel
BuildRequires:	ctemplate-devel >= 0.91
BuildRequires:	expat-devel
BuildRequires:	fdupes
BuildRequires:	file
BuildRequires:  freetype2-devel >= 2.1.10
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:	glib2-devel
BuildRequires:	glibmm2.4-devel
BuildRequires:	glitz-devel
BuildRequires:	gtk2-devel
BuildRequires:	gtkhtml-3.14-devel
BuildRequires:	gtkmm2.4-devel >= 2.6
BuildRequires:	imagemagick
BuildRequires:	libext2fs-devel
BuildRequires:	libfcgi-devel
BuildRequires:	libfontconfig-devel
BuildRequires:	libglade2.0-devel >= 2.5
BuildRequires:	libgnome2-devel
BuildRequires:	libgnomeprint-devel >= 2.2.0
BuildRequires:	libpng-devel
BuildRequires:	libsigc++2.0-devel
BuildRequires:	libslang-devel
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:  libx11-devel
BuildRequires:  libxext-devel
BuildRequires:	libxml2-devel
BuildRequires:	libxrender-devel
BuildRequires:	libzip-devel
BuildRequires:	lua5.1-devel
BuildRequires:	mesagl-devel
BuildRequires:	mesaglu-devel
BuildRequires:	mysql-connector-c++-devel
BuildRequires:	mysql-devel >= 5.0
BuildRequires:	ncurses-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel >= 5.0
BuildRequires:  pixman-devel >= 0.11.2
BuildRequires:	pkgconfig
BuildRequires:	python-devel
BuildRequires:	readline-devel
BuildRequires:	scintilla-devel
BuildRequires:	termcap-devel
BuildRequires:	sqlite3-devel
BuildRequires:	libgnome-keyring-devel
%if %{build_java}
BuildRequires:  junit
BuildRequires:	eclipse-ecj
BuildRequires:  gcj-tools
BuildRequires:  jpackage-utils
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
MySQL Workbench is modeling tool that allows you to design and generate MySQL
databases graphically.

MySQL Workbench requires OpenGL and a 3D accelerated graphics card with at
least 16MB of memory.

%prep

%setup -q -n mysql-workbench-gpl-%{version}-src
#%patch0 -p1
#%patch1 -p1
%patch2 -p1 -b .module
%patch3 -p1 -b .link

# lib64 fix
perl -pi -e "s|/lib/|/%{_lib}/|g" frontend/linux/workbench/program.cpp

# other small fixes
#touch po/POTFILES.in

# ctemplete is now ctemplate and not google anymore
for i in `grep -Rl google .`; do
    sed -i 's/google/ctemplate/g' $i;
done

%build
#export CPPFLAGS="$CPPFLAGS `pkg-config --cflags scintilla`"

%if %{build_autotools}
NOCONFIGURE=yes ./autogen.sh
%endif
%define _disable_ld_no_undefined 1
%configure2_5x --disable-static

# antibork
#find -type f -name Makefile | xargs perl -pi -e "s|-Wl,--as-needed||g"

# use the shared libs
#find -type f -name Makefile | xargs perl -pi -e "s|%{_libdir}/python%{pyver}/config/libpython%{pyver}.a|-lpython%{pyver}|g"

%make

%install
rm -rf %{buildroot}

%makeinstall_std

# construct a clean and correct wrapper
cat > %{buildroot}%{_bindir}/mysql-workbench << EOF
#!/bin/bash
export LD_LIBRARY_PATH="%{_libdir}/mysql-workbench:\$LD_LIBRARY_PATH"
export MWB_DATA_DIR="%{_datadir}/mysql-workbench"
export MWB_LIBRARY_DIR="%{_datadir}/mysql-workbench/libraries"
export MWB_MODULE_DIR="%{_libdir}/mysql-workbench/modules"
export MWB_PLUGIN_DIR="%{_libdir}/mysql-workbench/plugins"
export DBC_DRIVER_PATH="%{_libdir}/mysql-workbench"
%{_bindir}/mysql-workbench-bin \$*
EOF

# fix some menu entries and stuff...
install -d %{buildroot}%{_miconsdir}
install -d %{buildroot}%{_iconsdir}
install -d %{buildroot}%{_liconsdir}

install -d %{buildroot}%{_datadir}/applications
rm -f %{buildroot}%{_datadir}/applications/MySQLWorkbench.desktop
cat > %{buildroot}%{_datadir}/applications/mysql-workbench-oss.desktop << EOF
[Desktop Entry]
Name=MySQL Workbench
Comment=MySQL Database Design Tool
Exec=%{_bindir}/mysql-workbench
Terminal=false
Type=Application
Icon=mysql-workbench
Categories=Database;Office;
EOF

# make some icons
convert %{buildroot}%{_datadir}/mysql-workbench/images/MySQLWorkbench-48.png -resize 16x16 %{buildroot}%{_miconsdir}/mysql-workbench.png
convert %{buildroot}%{_datadir}/mysql-workbench/images/MySQLWorkbench-48.png -resize 32x32 %{buildroot}%{_iconsdir}/mysql-workbench.png
convert %{buildroot}%{_datadir}/mysql-workbench/images/MySQLWorkbench-48.png -resize 48x48 %{buildroot}%{_liconsdir}/mysql-workbench.png

# cleanup
rm -f %{buildroot}%{_libdir}/mysql-workbench/*.*a
rm -f %{buildroot}%{_libdir}/mysql-workbench/lib*.so
rm -f %{buildroot}%{_libdir}/mysql-workbench/modules/*.*a
rm -f %{buildroot}%{_libdir}/mysql-workbench/plugins/*.*a

%if %mdkversion < 200900
%post
%update_menus
%endif

%if %mdkversion < 200900
%postun
%clean_menus
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc COPYING ChangeLog README
%{_bindir}/*
%{_libdir}/mysql-workbench/lib*.so.*
%{_libdir}/mysql-workbench/mysqlcppconn.so
%{_libdir}/mysql-workbench/modules
%{_libdir}/mysql-workbench/plugins
%{_datadir}/mysql-workbench
%{_datadir}/applications/mysql-workbench-oss.desktop
%{_iconsdir}/mysql-workbench.png
%{_liconsdir}/mysql-workbench.png
%{_miconsdir}/mysql-workbench.png
