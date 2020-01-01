Summary: Similar Image Finder
Name: python3-simimg
Version: 0.6.1
Epoch: 6
Release: 1%{?dist}
Url: https://pypi.python.org/pypi/simimg
License: MIT
Group: Development/Languages/Python
Source0: simimg-%{version}.tar.bz2
BuildArch: noarch
Requires: python3-pillow
Requires: python3-imagehash

%description
This is a python GUI for displaying pictures grouped according to
similarity. The main aim of the program is to help identify groups of
holiday snaps that resemble each-other and efficiently inspect those
groups. It allows to easily keep only the best photos.


%prep
%setup -qn simimg-%{version}

%install
%{__python3} setup.py install --root=%{buildroot}

%files
%{_bindir}/*
%{python3_sitelib}/*
