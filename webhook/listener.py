import subprocess, logging
from flask import Flask, request, jsonify

logging.basicConfig(filename="healing.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")

app = Flask(__name__)

PLAYBOOKS = {
    "NginxDown": "ansible/restart_nginx.yml",
    "HighCPU": "ansible/high_cpu.yml",
}

@app.route("/alert", methods=["POST"])
def alert():
    data = request.get_json()
    for a in data.get("alerts", []):
        name = a["labels"].get("alertname")
        status = a["status"]
        logging.info(f"Received {name} ({status})")
        if status == "firing" and name in PLAYBOOKS:
            logging.info(f"Running {PLAYBOOKS[name]}")
            r = subprocess.run(["ansible-playbook", PLAYBOOKS[name]],
                               capture_output=True, text=True)
            logging.info(r.stdout)
            if r.returncode != 0:
                logging.error(r.stderr)
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
