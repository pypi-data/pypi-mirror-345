# ACEcalc

> This is beta version.

> the code is not complete.

Fast calculate the cyclone ACE.

## Library description

**add_knot**:

Add the knots.

**_example_**:

```py
import ACE_calc
ACE_calc.set_mode(ACE_calc.TROPICAL)
ACE_calc.add_knot(50)
ACE_calc.add_knot(45, 2)
ACE_calc.add_knot(35, 2, 1)
ACE_calc.output_knot()
```

**output**:

```index = 1, knots = 50, mode = tropical
index = 2, knots = 35, mode = subtropical
index = 3, knots = 45, mode = subtropical
```

**_parameters_**:

knots:int: The knots you want to add.

mode=now_mode: The mode you want to add.

index:int=len(ACE_list): The index you want to insert in the after.

**_raises_**:

**ValueError**: Your input or mode is invalid.

---

### add_knots

Add the some knots.

**_example_**:

```py
import ACE_calc
ACE_calc.set_mode(ACE_calc.TROPICAL)
ACE_calc.add_knots(50, 3)
ACE_calc.output_knot()
```

**output**:

```index = 1, knots = 50, mode = tropical
index = 2, knots = 50, mode = subtropical
index = 3, knots = 50, mode = subtropical
```

**_parameters_**:

knots:int: The knots you want to add.
mode=now_mode: The mode you want to add.
index=len(ACE_list): The index you want to insert in the after.

**_raises_**:

**ValueError**: Your input or mode is invalid.

---

### output_knots

Format print your knot list.

**_exmanple_**:
```py
import ACE_calc
ACE_calc.set_mode(ACE_calc.TROPICAL)
ACE_calc.add_knot(50)
ACE_calc.output_knot()
```

### output:

```
index = 1, knots = 50, mode = tropical
```

---
### get_konts_indexed

Get all the ACE indexes (index starts from 1).

**_exmanple_**:
```py
ACE_calc.add_knot(50)
ACE_calc.add_knot(45, 2)
ACE_calc.add_knot(50, 2, 1)
get_ACE_indexes(50)
```

**output**:

```
"[1, 2]"
```

**_parameters_**:

knots:int: The knots you want to search.

**_returns_**:

**list[int]**:

All the knots list.