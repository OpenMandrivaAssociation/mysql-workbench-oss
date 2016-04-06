%define Werror_cflags -Wformat -fpermissive -Wextra -Wall -Wno-unused -Wno-deprecated
%define _disable_ld_no_undefined 1

%define build_java 0

# Keep internal libraries private
%define __noautoprov 'devel(.*)|_cairo\\.so(.*)|_mforms\\.so(.*)|db(.*)\\.so(.*)|forms\\.grt\\.so(.*)|libantlr3c_wb(.*)|libcdbc\\.so(.*)|libgrt\\.so(.*)|liblinux_utilities\\.so(.*)|libmdcanvas\\.so(.*)|libmdcanvasgtk\\.so(.*)|libmforms\\.so(.*)|libmysqlparser\\.so(.*)|libsqlide\\.so(.*)|libsqlparser\\.so(.*)|libvsqlitepp\\.so(.*)|libwb(.*)\\.so(.*)|wb(.*)\\.so(.*)'
%define __noautoreq '_cairo\\.so(.*)|_mforms\\.so(.*)|db(.*)\\.so(.*)|forms\\.grt\\.so(.*)|libantlr3c_wb(.*)|libcdbc\\.so(.*)|libgrt\\.so(.*)|liblinux_utilities\\.so(.*)|libmdcanvas\\.so(.*)|libmdcanvasgtk\\.so(.*)|libmforms\\.so(.*)|libmysqlparser\\.so(.*)|libsqlide\\.so(.*)|libsqlparser\\.so(.*)|libvsqlitepp\\.so(.*)|libwb(.*)\\.so(.*)|wb(.*)\\.so(.*)'

Summary:	Extensible modeling tool for MySQL 5.x
Name:		mysql-workbench-oss
Version:	6.3.6
Release:	1
License:	GPLv2 and LGPLv2
Group:		Databases
Url:		http://dev.mysql.com/downloads/workbench/
Source0:	http://cdn.mysql.com/Downloads/MySQLGUITools/mysql-workbench-community-%{version}-src.tar.gz
Patch1:		0013-mysql-workbench-no-json.patch
Obsoletes:	mysql-workbench < 5.1.6
Provides:	mysql-workbench = %{EVRD}
BuildRequires:	cmake
BuildRequires:	gettext
BuildRequires:	imagemagick
BuildRequires:	boost-devel
BuildRequires:	gdal-devel
BuildRequires:	gettext-devel
BuildRequires:	mysql-devel >= 5.0
BuildRequires:	mysql-connector-c++-devel
BuildRequires:	readline-devel
BuildRequires:	swig
BuildRequires:	tinyxml-devel
BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(cairomm-1.0)
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(ext2fs)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(glibmm-2.4)
BuildRequires:	pkgconfig(glitz)
BuildRequires:	pkgconfig(gnome-keyring-1)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(gtkmm-2.4)
BuildRequires:	pkgconfig(libctemplate)
BuildRequires:	pkgconfig(libiodbc)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(libzip)
BuildRequires:	pkgconfig(lua)
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(pangoxft)
BuildRequires:	pkgconfig(pixman-1)
BuildRequires:	pkgconfig(python2)
BuildRequires:	pkgconfig(sigc++-2.0)
BuildRequires:	pkgconfig(slang)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xrender)
%if %{build_java}
BuildRequires:	junit
BuildRequires:	eclipse-ecj
BuildRequires:	gcj-tools
BuildRequires:	jpackage-utils
%endif
BuildRequires:	vsqlite++-devel

Requires:	python-paramiko
Requires:	python-pexpect

%description
MySQL Workbench is modeling tool that allows you to design and generate MySQL
databases graphically.

MySQL Workbench requires OpenGL and a 3D accelerated graphics card with at
least 16MB of memory.

%prep
%setup -q -n mysql-workbench-community-%{version}-src
%apply_patches

# make cmake happy with mariadb
sed -i '/^find_package(MySQL /c find_package(MySQL REQUIRED)' \
        CMakeLists.txt


sed -i -e 's:ifconfig:/sbin/ifconfig:' plugins/wb.admin/backend/wb_server_control.py || die

# lib64 fix
perl -pi -e "s|/lib/|/%{_lib}/|g" frontend/linux/workbench/program.cpp

%build
export CXXFLAGS="%{optflags} -fpermissive "
%cmake
%make

%install
%makeinstall_std -C build

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

install -d %{buildroot}%{_datadir}/applications
rm -f %{buildroot}%{_datadir}/applications/MySQLWorkbench.desktop
cat > %{buildroot}%{_datadir}/applications/mysql-workbench.desktop << EOF
[Desktop Entry]
Name=MySQL Workbench
Comment=MySQL Database Design Tool
Exec=%{_bindir}/mysql-workbench
Terminal=false
Type=Application
Icon=mysql-workbench
Categories=Database;Office;
EOF

# More reliable icons
rm -rf %{buildroot}%{_datadir}/icons/hicolor/*/*/mysql-workbench.png
for N in 16 32 48 64 128;
do
convert images/icons/linux/128x128/apps/mysql-workbench.png -resize ${N}x${N} $N.png;
install -D -m 0644 $N.png %{buildroot}%{_iconsdir}/hicolor/${N}x${N}/apps/mysql-workbench.png
done

chmod a+x %{buildroot}%{_datadir}/mysql-workbench/sshtunnel.py

# cleanup
rm -f %{buildroot}%{_libdir}/mysql-workbench/*.*a
rm -f %{buildroot}%{_libdir}/mysql-workbench/modules/*.*a
rm -f %{buildroot}%{_libdir}/mysql-workbench/plugins/*.*a
rm -rf %{buildroot}%{_docdir}/mysql-workbench

%files
%doc COPYING ChangeLog README
%{_bindir}/*
%{_libdir}/mysql-workbench
%{_datadir}/mysql-workbench
%{_datadir}/applications/mysql-workbench.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/mime/packages/mysql-workbench.xml
%{_datadir}/mime-info/mysql-workbench.mime
