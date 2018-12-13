#!/bin/bash
declare -a projects
declare -a locales
declare -a dates

# Load files into arrays.
readarray projects < projects.txt
readarray locales < wikilocale.txt
readarray dates < dates.txt

success_records="pass.txt"
failure_records="fail.txt"
results_records="AutomationTestResuls.txt"
if [ -f $success_records ] ; then
    rm $success_records 
fi

if [ -f $failure_records ] ; then
    rm $failure_records
fi

if [ -f $failure_records ] ; then
    rm $results_records
fi

numberOfTrials=0
for ((m = 1; m < 2; m++))
do
for ((j = 0; j < 1; j++))
do
for ((k = 1; k < 2; k++))
do
for ((l = 0; l < 50; l++))
do
((numberOfTrials+=1)) 
python wdcli.py -m $m -d ${dates[j]} -p ${projects[k]} -l ${locales[l]} -r 1 -s
done
done
done
done

successfulTrials=$(cat ${success_records} | wc -l)
failedTrials=$(cat ${failure_records} | wc -l)
accuracy=$(awk -v a="$successfulTrials" -v b="$numberOfTrials"  'BEGIN{print a / b * 100}')

printf "Number of Test Trials is : $numberOfTrials\n"
printf "Number of Successful Test Trials is : $successfulTrials\n"
printf "Number of Failed Test Trials is : $failedTrials\n"
printf "Accuracy Rate is : $accuracy %%\n"

printf "Number of Test Trials is : $numberOfTrials\n" >> AutomationTestResuls.txt
printf "Number of Successful Test Trials is : $successfulTrials\n" >> AutomationTestResuls.txt
printf "Number of Failed Test Trials is : $failedTrials\n" >> AutomationTestResuls.txt
printf "Accuracy Rate is : $accuracy %%\n" >> AutomationTestResuls.txt

if [ $failedTrials -gt 0 ] ; then
    printf "Reason of Failure: The links for the failed combinations do not exist"
    printf "Reason of Failure: The links for the failed combinations do not exist" >> AutomationTestResuls.txt
fi

printf "Open pass.txt to view successful test cases and fail.txt to view failed test cases"
