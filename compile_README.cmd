@echo for testing the README.md.  
@echo the outpout is not used for publishing.  it is only so you know your README.md will
@echo compile ok before publishing with flit.

python -m markdown README.md > README.html
