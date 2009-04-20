%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1

%define build_java 1
%define build_autotools 1

# commandline overrides:
# rpm -ba|--rebuild --with 'xxx'
%{?_with_java: %{expand: %%global build_java 1}}
%{?_without_java: %{expand: %%global build_java 0}}
%{?_with_autotools: %{expand: %%global build_autotools 1}}
%{?_without_autotools: %{expand: %%global build_autotools 0}}

Summary:	Extensible modeling tool for MySQL 5.0
Name:		mysql-workbench-oss
Group:		Databases
Version:	5.1.10
Release:	%mkrel 1
License:	GPL
URL:		http://dev.mysql.com/downloads/workbench/
# ftp://ftp.pbone.net/mirror/dev.mysql.com/pub/Downloads/MySQLGUITools/mysql-workbench-5.1.4-1fc9.src.rpm
Source0:	ftp://ftp.mysql.com/pub/mysql/download/gui-tools/%{name}-%{version}.tar.gz
Patch0:		mysql-workbench-5.1.10-fix-str-fmt.patch
Obsoletes:	mysql-workbench < 5.1.6
Provides:	mysql-workbench
BuildRequires:	autoconf2.5
BuildRequires:	cairo-devel
BuildRequires:	ctemplate-devel
BuildRequires:	expat-devel
BuildRequires:	file
BuildRequires:  freetype2-devel >= 2.1.10
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:	glib2-devel
BuildRequires:	glibmm2.4-devel
BuildRequires:	gtk2-devel
BuildRequires:	gtkhtml-3.14-devel
BuildRequires:	gtkmm2.4-devel >= 2.6
BuildRequires:	imagemagick
BuildRequires:	libext2fs-devel
BuildRequires:	libfcgi-devel
BuildRequires:	libfontconfig-devel
BuildRequires:	libglade2.0-devel >= 2.5
BuildRequires:	libgnomeprint-devel >= 2.2.0
BuildRequires:	libpng-devel
BuildRequires:	libsigc++2.0-devel
BuildRequires:	libslang-devel
BuildRequires:	libtool
BuildRequires:  libx11-devel
BuildRequires:  libxext-devel
BuildRequires:	libxml2-devel
BuildRequires:	libxrender-devel
BuildRequires:	libzip-devel
BuildRequires:	lua5.1-devel
BuildRequires:	mesagl-devel
BuildRequires:	mesaglu-devel
BuildRequires:	mysql-devel >= 5.0
BuildRequires:	ncurses-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel >= 5.0
BuildRequires:  pixman-devel >= 0.11.2
BuildRequires:	pkgconfig
BuildRequires:	python-devel
BuildRequires:	readline-devel
BuildRequires:	termcap-devel
%if %{build_java}
BuildRequires:  junit
BuildRequires:	eclipse-ecj
BuildRequires:  java-gcj-compat-devel
BuildRequires:  jpackage-utils
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
MySQL Workbench is modeling tool that allows you to design and generate MySQL
databases graphically.

MySQL Workbench requires OpenGL and a 3D accelerated graphics card with at
least 16MB of memory.

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1

# lib64 fix
perl -pi -e "s|/lib/|/%{_lib}/|g" frontend/linux/workbench/program.cpp

%build

%if %{build_autotools}
NOCONFIGURE=yes ./autogen.sh
%endif

%configure2_5x

# antibork
find -type f -name Makefile | xargs perl -pi -e "s|-Wl,--as-needed||g"

# use the shared libs
find -type f -name Makefile | xargs perl -pi -e "s|%{_libdir}/python%{pyver}/config/libpython%{pyver}.a|-lpython%{pyver}|g"

%make

%install
rm -rf %{buildroot}

%makeinstall_std

# construct a clean and correct wrapper
cat > %{buildroot}%{_bindir}/mysql-workbench << EOF
#!/bin/bash
export LD_LIBRARY_PATH="%{_libdir}/mysql-workbench:\$LD_LIBRARY_PATH"
export MWB_DATA_DIR="%{_datadir}/mysql-workbench"
export MWB_MODULE_DIR="%{_libdir}/mysql-workbench/modules"
export MWB_PLUGIN_DIR="%{_libdir}/mysql-workbench/plugins"
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
Categories=X-MandrivaLinux-MoreApplications-Databases;
EOF

# make some icons
convert %{buildroot}%{_datadir}/mysql-workbench/images/MySQLWorkbench-48.png -resize 16x16 %{buildroot}%{_miconsdir}/mysql-workbench.png
convert %{buildroot}%{_datadir}/mysql-workbench/images/MySQLWorkbench-48.png -resize 32x32 %{buildroot}%{_iconsdir}/mysql-workbench.png
convert %{buildroot}%{_datadir}/mysql-workbench/images/MySQLWorkbench-48.png -resize 48x48 %{buildroot}%{_liconsdir}/mysql-workbench.png

# cleanup
rm -f %{buildroot}%{_libdir}/mysql-workbench/*.*a
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
%attr(0755,root,root) %{_bindir}/mysql-workbench
%attr(0755,root,root) %{_bindir}/mysql-workbench-bin
%attr(0755,root,root) %{_bindir}/grtshell
%attr(0755,root,root) %dir %{_libdir}/mysql-workbench
%attr(0755,root,root) %dir %{_libdir}/mysql-workbench/modules
%attr(0755,root,root) %dir %{_libdir}/mysql-workbench/plugins
%attr(0755,root,root) %{_libdir}/mysql-workbench/*.so*
%attr(0755,root,root) %{_libdir}/mysql-workbench/modules/*.so
%attr(0755,root,root) %{_libdir}/mysql-workbench/modules/*.so.0
%attr(0755,root,root) %{_libdir}/mysql-workbench/modules/*.so.0.0.0
%attr(0755,root,root) %{_libdir}/mysql-workbench/plugins/*.so
%attr(0755,root,root) %{_libdir}/mysql-workbench/plugins/*.so.0
%attr(0755,root,root) %{_libdir}/mysql-workbench/plugins/*.so.0.0.0
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/images
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/data
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/grt
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/libraries
%attr(0644,root,root) %{_datadir}/mysql-workbench/*.glade
%attr(0644,root,root) %{_datadir}/mysql-workbench/workbench.rc
%attr(0644,root,root) %{_datadir}/mysql-workbench/data/*.xml
%attr(0644,root,root) %{_datadir}/mysql-workbench/grt/*.xml
%attr(0644,root,root) %{_datadir}/mysql-workbench/images/*.png
%attr(0644,root,root) %{_datadir}/mysql-workbench/images/*.cur
%attr(0644,root,root) %{_datadir}/mysql-workbench/libraries/*.py
%attr(0644,root,root) %{_datadir}/mysql-workbench/libraries/*.lua
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/db_mysql_catalog_reporting
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/db_mysql_catalog_reporting/Basic_Text.tpl
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/wb_model_reporting
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/HTML_Basic_Frames.tpl
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/HTML_Basic_Single_Page.tpl
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/HTML_Detailed_Frames.tpl
%attr(0755,root,root) %dir %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/Text_Basic.tpl
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/db_mysql_catalog_reporting/Basic_Text.tpl/*
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/HTML_Basic_Frames.tpl/*
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/HTML_Basic_Single_Page.tpl/*
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/HTML_Detailed_Frames.tpl/*
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/wb_model_reporting/Text_Basic.tpl/*
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/*.glade
%attr(0644,root,root) %{_datadir}/mysql-workbench/modules/data/*.xml
%attr(0644,root,root) %{_datadir}/applications/mysql-workbench-oss.desktop
%attr(0644,root,root) %{_iconsdir}/mysql-workbench.png
%attr(0644,root,root) %{_liconsdir}/mysql-workbench.png
%attr(0644,root,root) %{_miconsdir}/mysql-workbench.png
