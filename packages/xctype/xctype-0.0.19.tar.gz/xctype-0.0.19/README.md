# xctype
Explicit C types for Python

This is a proof of concept / work in progress for now, see [roadmap](#roadmap).

## Installation
````
python3 -m pip install xctype-***.whl
````

## Known limitations

- When two consecutive bitfields do not have the same storage (like uint32_t followed bu uint16_t), offsets are wrong.

## Roadmap

- to_asciidoc
    - raw_bytes option: display values as hexstr 
- support for enums
- support for user specified alignement
- support for unions ?
- better support for bitfields:
  - fix the known limitation or at least detect it and issue an error
  - optional arg to auto create padding bitfield -> may need an entirely new approach to bitfields to have a container object
- doc: think about how to attach a doc to each member, preferably in a python/sphinx friendly way to leverage IDEs
- replace make_struct by a decorator ?
- think about way for user to add code to the struct to manipulate it / validate it (struct with CRCs for example)
- replace sympy by plain python eval ? allows to size stuff based on other stuff size for example. maybe no point making this more flexible than C...
- replace sympy with z3 ?

