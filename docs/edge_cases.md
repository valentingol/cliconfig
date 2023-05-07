# Edge cases

**Be careful, tuples and sets are not supported by YAML and cannot be used in configs.**
Use lists instead if possible

`None` is not recognized as a None object by YAML but as a string, you may use `null`
or `Null` instead if you want to
set a None object.

Dicts are considered as sub-configs and so you may not be able to change the keys if
`allow_new_keys=False` (default). If you want to modify a dict keys, you should
enclose it in a list.

For instance:

```yaml
--- default.yaml
logging:
  metrics: ['train loss', 'val loss']
  styles: [{'train loss': 'red', 'val loss': 'blue'}]
--- experiment.yaml
logging:
  metrics: ['train loss', 'val loss', 'val acc']
  styles: [{'train loss': 'red', 'val loss': 'blue', 'val acc': 'cyan'}]
```
