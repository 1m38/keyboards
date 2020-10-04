# usage: `bash elecrow_rename_garber.sh PROJECT_NAME`

ProjectName=$1

set -x

mv ${ProjectName}-F_Cu.gbr ${ProjectName}.GTL
mv ${ProjectName}-B_Cu.gbr ${ProjectName}.GBL
mv ${ProjectName}-F_Mask.gbr ${ProjectName}.GTS
mv ${ProjectName}-B_Mask.gbr ${ProjectName}.GBS
mv ${ProjectName}-F_SilkS.gbr ${ProjectName}.GTO
mv ${ProjectName}-B_SilkS.gbr ${ProjectName}.GBO
mv ${ProjectName}-PTH.drl ${ProjectName}.TXT
mv ${ProjectName}-NPTH.drl ${ProjectName}-NPTH.TXT
mv ${ProjectName}-Edge_Cuts.gbr ${ProjectName}.GML
