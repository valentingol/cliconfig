"""Test show.py."""

from cliconfig.show import show_config


def test_show_config() -> None:
    """Test show_config."""
    config = {
        'model': {
            's1_ae_config': {
                'in_dim': 2,
                'out_dim': 1,
                'layer_channels': [16, 32, 64],
                'conv_per_layer': 1,
                'residual': False,
                'dropout_rate': 0.0,
            },
            'mask_module_dim': [6, 2],
            'glob_module_dims': [2, 8, 2],
            'conv_block_dims': [32, 64, 128],
        },
        'train': {
            'n_epochs': 100,
            'optimizer': {
                'name': 'Adam',
                'lr': 0.001,
                'weight_decay': 0.0,
                'warmup_steps': 0,
            },
        },
        'data': {
            'dataset': 'mnist',
            'batch_size': 128,
            'num_workers': 6,
        },
    }
    show_config(config)
