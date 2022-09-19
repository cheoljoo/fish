#/data01/cheoljoo.lee/bin/repo init -u ssh://vgit.lge.com:29420/tiger/manifest/ -b tiger_release -m tiger_desktop_gen12_release.xml
../repo init -u ssh://vgit.lge.com:29420/tiger/manifest/ -b tiger_release -m tiger_desktop_release.xml
../repo sync -cq -j8
../repo start tiger_release --all
echo "cd apps_proc/lge/servicelayer/core/services/"
echo "cd tiger-desktop-gen12/intel-build/poky/meta-tiger/classes"
echo "tiger-feature-common.bbclass"
echo "#do_fetch[nostamp] = 1" 

echo "$ mkdir  my_tiger_src ;     cd  my_tiger_src"
echo "$ repo init -u ssh://vgit.lge.com:29420/tiger/manifest/ -b tiger_release -m  tiger_desktop_gen12_release.xml"
echo "$ repo sync -cqj 8  ;    repo start tiger_release --all"

echo "$  ./run-docker.sh                  # help command"
echo "$  ./run-docker.sh build apps       # build"
echo "$  ./run-docker.sh run              # Run tiger-desktop"
echo "$  ./run-docker.sh committest       # Run commit test"
echo "$  ./run-docker.sh coverity         # Run coverity source code"
echo "$  ./run-docker.sh uts              # Run unit test"

# vi ./intel-build/poky/meta-tiger/classes/tiger-feature-common.bbclass
