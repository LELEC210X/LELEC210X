# Telecom Simulation

Only the `sim.py` and `test.py` files should be executed.

When doing so, make sure to run them with Rye, e.g., do:

```bash
rye run python sim.py
```
```bash
rye run python sim.py -h
```

to run the simulation or to see the simulation options, or:

```bash
rye run pytest test.py
```

to test your chain implementation.

Finally, the `chain.py` file contains two classes: `Chain` and `BasicChain`.
You should only change the latter, by filling the missing code lines.

rye run python sim.py --no_show -n 100000
rye run python sim.py --no_show -n 100000 -m 16
rye run python sim.py --no_show -n 100000 -m 16 -r 10000
rye run python sim.py --no_show -n 100000 -d
rye run python sim.py --no_show -n 100000 -d -m 16
rye run python sim.py --no_show -n 100000 -d -m 16 -r 10000
rye run python sim.py --no_show -n 100000 -s
rye run python sim.py --no_show -n 100000 -s -m 16
rye run python sim.py --no_show -n 100000 -s -m 16 -r 10000
rye run python sim.py --no_show -n 100000 -d -s
rye run python sim.py --no_show -n 100000 -d -s -m 16
rye run python sim.py --no_show -n 100000 -d -s -m 16 -r 10000
rye run python sim.py --no_show -n 100000 -c
rye run python sim.py --no_show -n 100000 -c -d
rye run python sim.py --no_show -n 100000 -c -s
rye run python sim.py --no_show -n 100000 -c -d -s