for num_jobs in 1 4
do
	# TaskVine Function Calls
	for run in 1 2 3
	do 
		vine_factory -M dv3-tv-fcs --cores 4 --memory 64000 --disk 100000 --timeout 600 -T sge --min-workers 0 --max-workers  $num_jobs --workers-per-cycle $num_jobs --python-env=dv3-env.tar.gz --scratch-dir="$PWD"/scratch &
                factory_pid=$!
                python dv3_tv_fcs.py 4
                kill $factory_pid
                cp vine-run-info/most-recent/vine-logs/transactions ../logs/tv_fcs_"$num_jobs"j_run-"$run"_tr
                cp vine-run-info/most-recent/vine-logs/debug ../logs/tv_fcs_"$num_jobs"j_run-"$run"_db
                cp vine-run-info/most-recent/vine-logs/performance ../logs/tv_fcs_"$num_jobs"j_run-"$run"_perf
                sleep 5
	done

	# TaskVine Tasks
	for run in 1 2 3
	do 
		vine_factory -M dv3-tv-tasks --cores 4 --memory 64000 --disk 100000 --timeout 600 -T sge --min-workers 0 --max-workers  $num_jobs --workers-per-cycle $num_jobs --python-env=dv3-env.tar.gz --scratch-dir="$PWD"/scratch &
                factory_pid=$!
                python dv3_tv_tasks.py 1
                kill $factory_pid
                cp vine-run-info/most-recent/vine-logs/transactions ../logs/tv_tasks_"$num_jobs"j_run-"$run"_tr
                cp vine-run-info/most-recent/vine-logs/debug ../logs/tv_tasks_"$num_jobs"j_run-"$run"_db
                cp vine-run-info/most-recent/vine-logs/performance ../logs/tv_tasks_"$num_jobs"j_run-"$run"_perf
                sleep 5

	done
	# Work Queue
	for run in 1 2 3
	do 
		work_queue_factory -M dv3-wq --cores 4 --memory 64000 --disk 100000  --timeout 600 -T sge --min-workers 0 --max-workers  $num_jobs --workers-per-cycle $num_jobs --python-env=dv3-env.tar.gz --scratch-dir="$PWD"/scratch &
                factory_pid=$!
                python dv3_wq.py 1
                kill $factory_pid
                cp tr ../logs/wq_"$num_jobs"j_run-"$run"_tr
                cp db ../logs/wq_"$num_jobs"j_run-"$run"_db
                cp perf ../logs/wq_"$num_jobs"j_run-"$run"_perf
                sleep 5

	done
	# Dask
	for run in 1 2 3
	do 
        	python dv3_dask.py $num_jobs 4 $run
		sleep 5

	done


done
