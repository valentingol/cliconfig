# Hyperparameter search with Weights&Biases

Making hyperparameter search easier and more effective with
[Weights&Biases sweeps](https://wandb.ai/site)! This example shows you how to combine them
with cliconfig supporting nested configuration:

```python
# main.py
from cliconfig.config_routines import update_config
from cliconfig.dict_routines import flatten
import wandb

def main() -> None:
    """Main function."""
    # Create a cliconfig based on CLI
    config = make_config('default.yaml')
    # Initialize wandb to create wandb.config eventually modified by sweep
    # Note that the config is flattened because wandb sweep does not support
    # nested config (yet)
    wandb.init(config=flatten(config.dict))
    # Sync the cliconfig with wandb.config
    config = update_config(config, wandb.config)
    # Now the config is eventually updated with the sweep,
    # unflattened and ready to be used

    run(config)

if __name__ == '__main__':
    main()
```

Now you can create your sweep configuration use wandb sweep either from CLI or
from python following the [wandb tutorial](https://docs.wandb.ai/guides/sweeps).

For instance with a configuration containing train and data sub-configurations:

```yaml
# sweep.yaml
program: main.py
method: bayes
metric:
  name: val_loss
  goal: minimize
parameters:
    train.learning_rate:
        distribution: log_uniform_values
        min: 0.0001
        max: 0.1
    train.optimizer.name:
        values: ["adam", "sgd"]
    data.batch_size:
        values: [32, 64, 128]
```

```bash
$ wandb sweep sweep.yaml
sweep_id: ...
$ wandb agent <sweep_id>
```

This makes a bayesian search over the learning rate, the optimizer and the batch size to minimize the final validation loss.
