# Synthetic examples

`cloud_post.txt` is a short, wholly invented creative-production log for an
agent to analyze using [the starter](../../AGENT_STARTER.md). It includes
explicit attempt relationships and decisions, plus a trace with no final
decision. It contains no real person, project or research evidence.

`workflow.py` is a deterministic two-cycle demonstration of the supported
helpers. Run it with `--output /absolute/new-study-path` outside every Git
checkout. It authors its own synthetic input and packet rows without calling
a model; use the text fixture above to exercise agent interpretation instead.

`C001/` is a wholly invented cycle packet that demonstrates the packet
structure and is the fixture the tests copy and mutate. It contains no
empirical evidence, resembles no real creator, project, prompt, transcript, or
source capture, and must never be cited as evidence.

```bash
python3 scripts/validate_analysis_packet.py examples/synthetic/C001
```
