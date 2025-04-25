# Lite version of GROBID can run on assemblix2019
# To check if the container is running, use: `curl asseblix2019:8670` in the terminal
# See documentation: https://grobid.readthedocs.io/en/latest/Run-Grobid/

podman run --rm --ulimit core=0 -p 8670:8070 lfoppiano/grobid:0.8.1
