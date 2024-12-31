docker run -d \
  --name g-r-calendar-api \
  --restart always \
  -e RUNNER_NAME=g-r-calendar-api \
  -e RUNNER_WORKDIR=/tmp/g-r-calendar-api \
  -e RUNNER_GROUP=Default \
  -e RUNNER_TOKEN=ABPLEL2TCPKQTXZFBU555VLHOPUBC \
  -e REPO_URL=https://github.com/asmitul/Google-Calendar-API \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --cpus="0.3" \
  myoung34/github-runner:latest