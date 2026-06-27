import pytest
from flask import Flask, jsonify, request
import uuid
import multiprocessing



jobs = None
app = Flask(__name__)

def serve(port):
    
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@app.route("/run", methods=["POST"])
def run():
    global jobs
    data=request.json
    pytest_args=data.get("args",[])
    id=str(uuid.uuid4())
    if isinstance(pytest_args, str):
        pytest_args = [pytest_args]
    job={"id":id,"status":"running"}
    jobs[id]=job
    pytest_process = multiprocessing.Process(
        target=execute,
        args=(pytest_args, id,jobs), 
        daemon=True  # Allows the main Flask app to shut down cleanly and kill this process
    )

    # Start the process
    pytest_process.start()
    return jsonify(dict(jobs[id]))

def execute(args,id,shared_jobs):
    exit_code=pytest.main(args)
    code_val = int(exit_code)
    
    # This will now successfully sync back to the main Flask process!
    shared_jobs[id] = {
        "id": id, 
        "status": "done", 
        "results": code_val
    }


@app.route("/status/<id>", methods=["GET"])
def get_job(id):
    if jobs is None:
        return jsonify({"error": "Not initialized"}), 500
    job = jobs.get(id)
    return jsonify(dict(job) if job else None)

@app.route("/status/all", methods=["GET"])
def get_jobs():
    if jobs is None:
        return jsonify({})
    return jsonify(dict(jobs))

def pytest_addoption(parser):
    parser.addoption("--serve",default=False,action="store_true")
    parser.addoption("--serve-port",default=8000,action="store",type=int)


def pytest_cmdline_main(config):
    global jobs
    if config.getoption("--serve"):

        manager=multiprocessing.Manager()
        jobs=manager.dict()
        try:
            serve(config.getoption("--serve-port"))
        except KeyboardInterrupt:
            print("\n Stopping API Gateway server...")
        return 0
    return None