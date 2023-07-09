# Edge cases

**Please note that YAML does not support tuples and sets**, and therefore they
cannot be used in YAML files. If possible, consider using lists instead.

Moreover, YAML does not recognize "None" as a None object, but interprets it as a
string. If you wish to set a None object, you can use "null" or "Null" instead.

"@" is a special character used by the package to identify tags. You can't use it
in your parameters names (but you can use it in your values). It will raise an error
if you try to do so.

"dict" and "process_list" are reserved names of attributes and should not be used
as sub-config or parameter names. It can raise an error if you try to access them
as config attributes (with dots).

In the context of this package, dictionaries are treated as sub-configurations,
which means that modifying or adding keys directly in the additional configs may
not be possible (because only the merge of default configuration allow adding new keys).
If you need to modify or add keys within a dictionary, consider enclosing it in a list.

For instance:

```yaml
# default.yaml
logging:
  metrics: ['train loss', 'val loss']
  styles: [{'train loss': 'red', 'val loss': 'blue'}]
# additional.yaml
logging:
  metrics: ['train loss', 'val loss', 'val acc']
  styles: [{'train loss': 'red', 'val loss': 'blue', 'val acc': 'cyan'}]
```
