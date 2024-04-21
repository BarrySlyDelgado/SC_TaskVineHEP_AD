for num_jobs in  1 4
do
	for run in 1 2 3 
	do
		vine_factory -M rstri-test --cores 4 --memory 64000 --disk 100000 --timeout 600 -T sge --min-workers 0 --max-workers  $num_jobs --workers-per-cycle $num_jobs  --python-env=rstri-env.tar.gz --scratch-dir="$PWD"/scratch & 
		factory_pid=$!
		python skim.py -d GJets -dv --optimize  
		kill $factory_pid
		cp vine-run-info/most-recent/vine-logs/transactions ../logs/rst_"$num_jobs"j_run-"$run"_tr
		cp vine-run-info/most-recent/vine-logs/debug ../logs/rst_"$num_jobs"j_run-"$run"_db
		cp vine-run-info/most-recent/vine-logs/performance ../logs/rst_"$num_jobs"j_run-"$run"_perf
		sleep 5
	done

	for run in 1 2 3 
	do
		vine_factory -M rstri-test --cores 4 --memory 64000 --disk 100000 --timeout 600 -T sge --min-workers 0 --max-workers  $num_jobs --workers-per-cycle $num_jobs  --python-env=rstri-env.tar.gz --scratch-dir="$PWD"/scratch & 
		factory_pid=$!
		python skim_o.py -d GJets -dv --optimize  
		kill $factory_pid
		cp vine-run-info/most-recent/vine-logs/transactions ../logs/rst_o_"$num_jobs"j_run-"$run"_tr
		cp vine-run-info/most-recent/vine-logs/debug ../logs/rst_o_"$num_jobs"j_run-"$run"_db
		cp vine-run-info/most-recent/vine-logs/performance ../logs/rst_o_"$num_jobs"j_run-"$run"_perf
		sleep 5
	done
done
