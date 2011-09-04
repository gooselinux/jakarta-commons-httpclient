# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define short_name httpclient

Name:           jakarta-commons-httpclient
Version:        3.1
Release:        0.6%{?dist}
Epoch:          1
Summary: Jakarta Commons HTTPClient implements the client side of HTTP standards
License:        ASL 2.0
Source0:        http://archive.apache.org/dist/httpcomponents/commons-httpclient/source/commons-httpclient-3.1-src.tar.gz
Patch0:         %{name}-disablecryptotests.patch
# Add OSGi MANIFEST.MF bits
Patch1:         %{name}-addosgimanifest.patch
URL:            http://jakarta.apache.org/commons/httpclient/
Group:          Development/Libraries/Java
%if ! %{gcj_support}
Buildarch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:  ant
BuildRequires:  jakarta-commons-codec
BuildRequires:  jakarta-commons-logging >= 0:1.0.3
BuildRequires:  jce >= 0:1.2.2
BuildRequires:  jsse >= 0:1.0.3.01
#BuildRequires:  java-javadoc
BuildRequires:  jakarta-commons-logging-javadoc
BuildRequires:  junit
#BuildRequires:  jaxp = 1.3

Requires:       jakarta-commons-logging >= 0:1.0.3

Provides:       commons-httpclient = %{epoch}:%{version}-%{release}
Obsoletes:      commons-httpclient < %{epoch}:%{version}-%{release}
Provides:       jakarta-commons-httpclient3 = %{epoch}:%{version}-%{release}
Obsoletes:      jakarta-commons-httpclient3 < %{epoch}:%{version}-%{release}

%if %{gcj_support}
BuildRequires:       java-gcj-compat-devel
Requires(post):      java-gcj-compat
Requires(postun):    java-gcj-compat
%endif

%description
The Hyper-Text Transfer Protocol (HTTP) is perhaps the most significant
protocol used on the Internet today. Web services, network-enabled
appliances and the growth of network computing continue to expand the
role of the HTTP protocol beyond user-driven web browsers, and increase
the number of applications that may require HTTP support.
Although the java.net package provides basic support for accessing
resources via HTTP, it doesn't provide the full flexibility or
functionality needed by many applications. The Jakarta Commons HTTP
Client component seeks to fill this void by providing an efficient,
up-to-date, and feature-rich package implementing the client side of the
most recent HTTP standards and recommendations.
Designed for extension while providing robust support for the base HTTP
protocol, the HTTP Client component may be of interest to anyone
building HTTP-aware client applications such as web browsers, web
service clients, or systems that leverage or extend the HTTP protocol
for distributed communication.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Documentation
# for /bin/rm and /bin/ln
Requires(post):   coreutils
Requires(postun): coreutils

%description    javadoc
%{summary}.

%package        demo
Summary:        Demos for %{name}
Group:          Development/Testing
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description    demo
%{summary}.

%package        manual
Summary:        Manual for %{name}
Group:          Development/Documentation
Requires:       %{name}-javadoc = %{epoch}:%{version}-%{release}

%description    manual
%{summary}.


%prep
%setup -q -n commons-httpclient-%{version}
mkdir lib # duh
rm -rf docs/apidocs docs/*.patch docs/*.orig docs/*.rej

%patch0

pushd src/conf
%{__sed} -i 's/\r//' MANIFEST.MF
%patch1
popd

# Use javax classes, not com.sun ones
# assume no filename contains spaces
pushd src
    for j in $(find . -name "*.java" -exec grep -l 'com\.sun\.net\.ssl' {} \;); do
        sed -e 's|com\.sun\.net\.ssl|javax.net.ssl|' $j > tempf
        cp tempf $j
    done
    rm tempf
popd

# FIXME: These tests fail due to absence of jks in libgcj. Disable them for now.
rm -f src/test/org/apache/commons/httpclient/TestProxy.java
rm -f src/test/org/apache/commons/httpclient/params/TestSSLTunnelParams.java

%{__sed} -i 's/\r//' RELEASE_NOTES.txt
%{__sed} -i 's/\r//' README.txt
%{__sed} -i 's/\r//' LICENSE.txt

%build
export CLASSPATH=%(build-classpath jsse jce jakarta-commons-codec jakarta-commons-logging junit)
ant \
  -Dbuild.sysclasspath=first \
  -Djavadoc.j2sdk.link=%{_javadocdir}/java \
  -Djavadoc.logging.link=%{_javadocdir}/jakarta-commons-logging \
  -Dtest.failonerror=false \
  dist test


%install
rm -rf $RPM_BUILD_ROOT

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p dist/commons-httpclient.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)
# compat symlink
pushd $RPM_BUILD_ROOT%{_javadir}
ln -s commons-httpclient.jar commons-httpclient3.jar
popd

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}
mv dist/docs/api $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

# demo
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pr src/examples src/contrib $RPM_BUILD_ROOT%{_datadir}/%{name}

# manual and docs
rm -f dist/docs/{BUILDING,TESTING}.txt
ln -s %{_javadocdir}/%{name}-%{version} dist/docs/apidocs


%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt README.txt RELEASE_NOTES.txt
%{_javadir}/*

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc dist/docs/*


%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1:3.1-0.6
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-0.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-0.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jul 24 2008 Andrew Overholt <overholt@redhat.com> 1:3.1-0.3
- Update OSGi MANIFEST.MF

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:3.1-0.2
- drop repotag
- fix license tag

* Fri Apr 04 2008 Deepak Bhole <dbhole@redhat.com> - 0:3.1-0jpp.1
- Update to 3.1

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:3.0.1-2jpp.2
- Autorebuild for GCC 4.3

* Thu Sep 06 2007 Andrew Overholt <overholt@redhat.com> 1:3.0.1-1jpp.2
- Add OSGi MANIFEST.MF information.

* Fri Mar 16 2007 Permaine Cheung <pcheung@redhat.com> - 1:3.0.1-1jpp.1
- Merge with upstream and more rpmlint cleanup.

* Thu Feb 15 2007 Fernando Nasser <fnasser@redhat.com> - 1:3.0.1-1jpp
- Upgrade to 3.0.1

* Fri Jan 26 2007 Permaine Cheung <pcheung@redhat.com> - 1:3.0-8jpp
- Added versions for provides and obsoletes and rpmlint cleanup.

* Thu Aug 10 2006 Deepak Bhole <dbhole@redhat.com> - 1:3.0-7jpp.1
- Added missing requirements.
- Added missing postun section for javadoc.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 1:3.0-6jpp_2fc
- Rebuilt

* Thu Jul 20 2006 Deepak Bhole <dbhole@redhat.com> - 1:3.0-6jpp_1fc
- Added conditional native compilation.
- Disable certain ssl related tests that are known to fail with libgcj.

* Thu Apr 06 2006 Fernando Nasser <fnasser@redhat.com> - 1:3.0-5jpp
- Improve backwards compatibility and force removal of older versioned
  packages

* Thu Apr 06 2006 Fernando Nasser <fnasser@redhat.com> - 1:3.0-4jpp
- Remove duplicate release definition
- Require simply a jaxp 1.3

* Thu Apr 06 2006 Fernando Nasser <fnasser@redhat.com> - 1:3.0-3jpp
- BR xml-commons-jaxp-1.3-apis

* Thu Apr 06 2006 Ralph Apel <r.apel@r-apel.de> - 1:3.0-2jpp
- Fix tarball typo
- assure javax classes are used instead of com.sun. ones

* Wed Apr 05 2006 Ralph Apel <r.apel@r-apel.de> - 1:3.0-1jpp
- 3.0 final, drop main version in name

* Thu Oct 20 2005 Jason Corley <jason.corley@gmail.com> - 1:3.0-0.rc4.1jpp
- 3.0rc4

* Thu May 05 2005 Fernando Nasser <fnasser@redhat.com> - 1:3.0-0.rc2.1jpp
- Update to 3.0 rc2.

* Thu Nov  4 2004 Ville Skyttä <ville.skytta at iki.fi> - 1:2.0.2-1jpp
- Update to 2.0.2.
- Fix Group tag in -manual.

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:2.0-2jpp
- Rebuild with ant-1.6.2

* Mon Feb 16 2004 Kaj J. Niemi <kajtzu@fi.basen.net> - 0:2.0-1jpp
- 2.0 final

* Thu Jan 22 2004 David Walluck <david@anti-microsoft.org> 0:2.0-0.rc3.1jpp
- 2.0-rc3
- bump epoch

* Tue Oct 14 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-3.rc2.1jpp
- Update to 2.0rc2.
- Manual subpackage.
- Crosslink with local J2SE javadocs.
- Own unversioned javadoc dir symlink.

* Fri Aug 15 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-3.rc1.1jpp
- Update to 2.0rc1.
- Include "jakarta-"-less jar symlinks for consistency with other packages.
- Exclude example and contrib sources from main package, they're in -demo.

* Wed Jul  9 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-2.beta2.1jpp
- Update to 2.0 beta 2.
- Demo subpackage.
- Crosslink with local commons-logging javadocs.

* Wed Jun  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-2.beta1.1jpp
- Update to 2.0 beta 1.
- Non-versioned javadoc symlinking.

* Fri Apr  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-1.alpha3.2jpp
- Rebuild for JPackage 1.5.

* Wed Feb 26 2003 Ville Skyttä <ville.skytta at iki.fi> - 2.0-1.alpha3.1jpp
- Update to 2.0 alpha 3.
- Fix Group tags.
- Run standalone unit tests during build.

* Thu Sep 12 2002 Ville Skyttä <ville.skytta at iki.fi> 2.0-0.cvs20020909.1jpp
- Tune the rpm release number tag so rpm2html doesn't barf on it.

* Mon Sep  9 2002 Ville Skyttä <ville.skytta at iki.fi> 2.0-0.20020909alpha1.1jpp
- 2.0alpha1 snapshot 20020909.
- Use sed instead of bash extensions when symlinking jars during build.
- Add distribution tag.
- Require commons-logging instead of log4j.

* Sat Jan 19 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-4jpp
- renamed to jakarta-commons-httpclient
- additional sources in individual archives
- versioned dir for javadoc
- no dependencies for javadoc package
- dropped j2ee package
- adapted to new jsse package
- section macro

* Fri Dec 7 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-3jpp
- javadoc into javadoc package

* Sat Nov 3 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-2jpp
- fixed jsse subpackage

* Fri Nov 2 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-1jpp
- first JPackage release
