# RTL Verilog Block Diagrams

Use `scripts/verilog_to_visio.py` for top-level RTL integration diagrams. It
parses Verilog module instances and emits a deterministic, editable Visio
diagram without requiring the agent to hand-author coordinates.

## Command

```bash
python "<skill>/scripts/verilog_to_visio.py" "<verilog-dir-or-top.v>" "<output.vsdx>" \
  --top top_module \
  --json "<output.json>" \
  --preview "<preview.png>"
```

`--top` is optional when the script can infer the module that instantiates the
other modules. `--json` keeps the generated intermediate spec. `--preview`
exports a PNG through Visio COM for a quick visual check.

## Deterministic Layout

The generator recognizes common RTL roles from module names:

| Role | Keywords | Position |
| --- | --- | --- |
| Clock | `clk`, `clock`, `pll`, `divider` | upper left |
| Input conditioning | `debounce`, `key`, `button`, `config` | lower left |
| Receive/source | `rx`, `receiver`, `source` | left datapath |
| Storage | `fifo`, `ram`, `mem`, `buffer`, `bram` | center datapath |
| Transmit/sink | `tx`, `transmit`, `sink` | right datapath |
| Control | `ctrl`, `control`, `fsm`, `arbiter` | above datapath |
| Status | `led`, `indicator`, `status`, `debug` | lower right |

The main datapath is horizontal. Multi-bit data signals are blue and thick.
Control lines are orange. Status lines are slate gray. External ports are
black. Clock fanout and reset are intentionally summarized so a top-level
diagram remains readable rather than becoming a port-level wiring report.

## Scope

Use this generator for module-level architecture diagrams. It does not attempt
to draw internal registers, combinational equations, individual FSM states, or
gate-level netlists. Keep the original Verilog as the detailed port-level
authority.

If the generated role classification is unusual for a project, use the emitted
JSON as an editable starting point or add project-specific keywords to
`role_for()` in `scripts/verilog_to_visio.py`.
