# Start grobid server
# https://grobid.readthedocs.io/en/latest/Run-Grobid/
docker run --rm --init --ulimit core=0 -p 8670:8070 lfoppiano/grobid:0.8.1
