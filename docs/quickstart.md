# Quick start

First create a default config that can be split in multiple files that will be merged
(from left to right in `make_config` function):

```yaml
# default1.yaml
param1: 1
param2: 0
letters:
  letter1: a
  letter2: b
```

```yaml
# default2.yaml
param1: 1
param2: 2  # will override param2 from default1.yaml
letters.letter3: c  # add a new parameter
```

Now you can set up your program to use the config:

```python
# main.py
from cliconfig import make_config, show_config

config = make_config('default1.yaml', 'default2.yaml')
show_config(config)
```

Then add one or multiple additional config files that will override the default values.
**Be careful, the additional config files cannot bring new parameters by default**.
If you want to add new parameters (not advised for retro-compatibility, readability
and security), you can add `allow_new_keys=True` in `make_config` function.

```yaml
# exp1.yaml
letters:
  letter3: C
```

```yaml
# exp2.yaml
param1: -1
letters.letter1: A
```

Now you can launch the program with additional configurations and parameters.
The additional configurations are indicated with `--config` (separate with comma,
without space) and the parameters with `--<param_name>`. The default configuration
will be merged with the additional configurations (from left to right), then the
parameters will be set.

```bash
python main.py --config exp1.yaml,exp2.yaml --param2=-2 --letters.letter2='B'
```

Will show:

```text
[CONFIG] Merge 2 default configs, 2 additional configs and 2 CLI parameter(s).

Config:
    param1: -1
    param2: -2
    letters:
        letter1: A
        letter2: B
        letter3: C
```

Note that the configurations are native python dicts.
