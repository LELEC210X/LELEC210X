# Telecommunication Chain Simulation

## Overview

`sim.py` is a Python script designed to run a telecommunication chain simulation. It allows users to configure various parameters for both the simulation process and the chain itself. The results are stored in `.csv` files, and optional graphs can be generated.

## Usage

The script follows the format:

```bash
rye run sim [SIMULATION_PARAMETERS] [CHAIN_PARAMETERS]
```

## Parameters

### Simulation Parameters

These parameters control how the simulation runs and how results are displayed.


| Argument    | Alias                | Description                                                                                      |
| ------------- | ---------------------- | -------------------------------------------------------------------------------------------------- |
| `--basic`   |                      | Uses`BasicChain` instead of `OptimizedChain` (default).                                          |
| `-f`        | `--force_simulation` | Forces simulation execution, even if data already exists.                                        |
| `-s SIM_ID` | `--sim_id SIM_ID`    | Uses a specific precomputed simulation (`simulation_{SIM_ID}`). Skips new execution if provided. |
| `--no_show` | `--dont_show_graphs` | Disables displaying graphs after simulation.                                                     |
| `--no_save` | `--dont_save_graphs` | Disables saving graphs.                                                                          |
| `--FIR`     |                      | Generates the FIR graph of the chain.                                                            |

### Chain Parameters

These parameters define the characteristics of the telecommunication chain.


| Argument         | Alias                       | Description                                    |
| ------------------ | ----------------------------- | ------------------------------------------------ |
| `-p PAYLOAD_LEN` | `--payload_len PAYLOAD_LEN` | Payload length (default: 50).                  |
| `-n N_PACKETS`   | `--n_packets N_PACKETS`     | Number of packets (default: 100).              |
| `-m CFO_MOOSE_N` | `--cfo_Moose_N CFO_MOOSE_N` | `N` parameter in Moose algorithm (default: 4). |
| `-r CFO_RANGE`   | `--cfo_range CFO_RANGE`     | CFO range (default: 1000).                     |
| `-pre`           | `--bypass_preamble_detect`  | Bypasses preamble detection.                   |
| `-cfo`           | `--bypass_cfo_estimation`   | Bypasses CFO estimation.                       |
| `-sto`           | `--bypass_sto_estimation`   | Bypasses STO estimation.                       |

## Examples

### 1. Run a simulation with default parameters:

```bash
rye run sim
```

### 2. Use a precomputed simulation with ID 5:

```bash
rye run sim -s 5
```

### 3. Run a simulation with a specific chain configuration:

```bash
rye run sim -p 100 -n 500 -m 8 -r 5000
```

### 4. Force re-execution of the simulation:

```bash
rye run sim -f
rye run sim -f -s 5
rye run sim -f -p 100 -n 500 -m 8 -r 5000
```

### 5. Run a simulation without displaying or saving graphs:

```bash
rye run sim --no_show --no_save
```

### 6. Generate the FIR graph:

```bash
rye run sim --FIR
```

## Notes

- If `-s SIM_ID` is provided, the script **forces the use of that specific simulation**.
- If `-f` is used, a **new simulation** is executed regardless of existing data.
- All results are stored in `.csv` files, and graphs are optional.
