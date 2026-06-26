import pytest
from flask import Flask, jsonify, request
import uuid
from threading import Thread
jobs={}
app = Flask(__name__)
def serve(port):
    
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@app.route("/run", methods=["POST"])
def run():
    data=request.json
    pytest_args=data.get("args",[])
    id=str(uuid.uuid4())
    if isinstance(pytest_args, str):
        pytest_args = [pytest_args]
    job={"id":id,"status":"running"}
    jobs[id]=job
    pytest_thread = Thread(
        target=execute,
        args=(pytest_args,id), 
        daemon=True  # Allows Flask to shut down cleanly even if a test is running
    )
    pytest_thread.start()
    return jsonify(job)

def execute(args,id):
    exit_code=pytest.main(args)
    jobs[id]={"id":id,"status":"done","results":exit_code}


@app.route("/status/<id>",methods=["GET"])
def get_job(id):
    job=jobs.get(id)
    return jsonify(job)

@app.route("/status/all",methods=["GET"])
def get_jobs():
    print(jobs)
    return jsonify(jobs)

def pytest_addoption(parser):
    parser.addoption("--serve",default=False,action="store_true")
    parser.addoption("--serve-port",default=8000,action="store",type=int)


def pytest_configure(config):
    if hasattr(config, "_api_gateway_running"):
        return
    if config.getoption("--serve"):
        config._api_gateway_running = True
        try:
            # Start Flask directly on the main thread
            serve(config.getoption("--serve-port"))
        except KeyboardInterrupt:
            pass
        finally:
            pytest.exit("API Gateway server stopped.", returncode=0)