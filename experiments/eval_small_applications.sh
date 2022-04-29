#!/bin/bash

trap "exit" INT

scale=2
threads=4
connections=16
duration=30s

function run_wrk()
{

    echo "Rate: 1"
        ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} #| grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"

    for rate in $rates
    do
        ## TODO: Also check for patterns of non 2xx responses
        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} # | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
    done
}

function set_min_max_scale()
{
    for service in $services
    do
        kn service update "$service" --scale-min ${scale} --scale-max ${scale} --annotation "autoscaling.knative.dev/target=500"
    done
}

function deploy_and_run()
{
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas ${extra_args}
    echo "Running with: ${extra_args}"
    run_wrk
}

function run_single_stateful()
{

    export benchmark="single-stateful"
    ## These are the max rates
    export rates="20 60 100 140 180 220 260 300 340 380"
    export services="backend"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

    echo "Deploying for the first time and running tests (if they exist)..."
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas ${extra_args}
    sleep 15

    echo "Setting scale"
    set_min_max_scale
    sleep 10

    ## mu2sls
    export extra_args="--enable_logging --enable_txn --enable_custom_dict"
    export rates="20 60 100 140 180 220 260 300"
    deploy_and_run

    ## mu2sls (no FT)
    export extra_args="--enable_txn --enable_custom_dict"
    export rates="20 60 100 140 180 220 260 300 340"
    deploy_and_run

    ## mu2sls (w/o OD)
    export extra_args="--enable_logging --enable_txn"
    export rates="20 60 100"
    deploy_and_run

    ## unsage (w/ FT)
    export extra_args="--enable_logging"
    export rates="20 60 100 140 180"
    deploy_and_run

    ## unsage (w/ FT) (seq)
    ## TODO: Add
}

function run_chain()
{
    export benchmark="chain"
    ## These are the max rates
    export rates="10 20 30 40 50 60 70 80 90 100 110 120"
    export services="caller1 caller2 backend"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

    echo "Deploying for the first time and running tests (if they exist)..."
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas ${extra_args}
    sleep 15

    echo "Setting scale"
    set_min_max_scale
    sleep 10

    ## mu2sls
    export extra_args="--enable_logging --enable_txn --enable_custom_dict"
    export rates="10 20 30 40 50 60 70 80 90 100 110 120"
    deploy_and_run

    ## mu2sls (no FT)
    export extra_args="--enable_txn --enable_custom_dict"
    export rates="10 20 30 40 50 60 70 80 90 100 110 120"
    deploy_and_run

    ## mu2sls (w/o OD)
    export extra_args="--enable_logging --enable_txn"
    export rates="10 20 30 40 50 60 70"
    deploy_and_run

    ## unsage (w/ FT)
    export extra_args="--enable_logging"
    export rates="10 20 30 40 50 60 70 80 90 100 110"
    deploy_and_run

    ## unsage (w/ FT) (seq)
    ## TODO: Add
}

function run_tree()
{
    export benchmark="tree"
    ## These are the max rates
    export rates="5 10 15 20 25 30 40 50 60 70 80 90"
    export services="callertxn backend1 backend2"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

    echo "Deploying for the first time and running tests (if they exist)..."
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas ${extra_args}
    sleep 15

    echo "Setting scale"
    set_min_max_scale
    sleep 10

    ## mu2sls
    export extra_args="--enable_logging --enable_txn --enable_custom_dict"
    export rates="5 10 15 20 25 30"
    deploy_and_run

    ## mu2sls (w/o OD)
    export extra_args="--enable_logging --enable_txn"
    export rates="5 10"
    deploy_and_run

    ## unsage (w/ FT)
    export extra_args="--enable_logging"
    export rates="5 10 15 20 25 30 40 50 60 70 80 90"
    deploy_and_run

    ## unsage (w/ FT) (seq)
    ## TODO: Add
}

run_single_stateful | tee single_stateful.log
run_chain | tee chain.log
run_tree | tee tree.log