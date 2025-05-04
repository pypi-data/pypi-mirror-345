# Evaluation Point Implementation Plan

## Current State of the Problem

The immediate error occurs in `example.py` at line 247 where `truth_value_at()` is called with two arguments:
```python
if not p.proposition.truth_value_at(eval_world, eval_time):
    all_premises_true = False
    break
```

The root issue is a mismatch between different theories' `truth_value_at()` implementations:

1. In `default/semantic.py`, `Proposition.truth_value_at()` only accepts one parameter: `eval_world`
2. In `bimodal/semantic.py`, `BimodalProposition.truth_value_at()` requires two parameters: `eval_world, eval_time`

This is causing a TypeError when running default theory examples through the `BuildExample.print_model()` method, which attempts to call with both parameters.

## Design Philosophy Guidance

From CLAUDE.md, the project follows these key design principles:

- **Fail Fast**: Let errors occur naturally rather than adding conditional logic to handle edge cases
- **Deterministic Behavior**: Avoid default values, fallbacks, or implicit conversions 
- **Required Parameters**: Parameters should be explicitly required with no implicit conversion between types
- **Clear Data Flow**: Keep a consistent approach to passing data between components
- **No Silent Failures**: Don't catch exceptions or provide defaults to avoid errors
- **Explicit References**: World IDs should be explicitly provided rather than attempting conversions

## Analysis of Current Usage

### The `eval_point` Pattern

The codebase already uses an `eval_point` dictionary in many places:

1. In `model.py`, `SemanticDefaults` defines `main_point` as a dictionary:
   ```python
   self.main_point = None  # Later set as a dict with keys specific to the theory
   ```

2. In `default/semantic.py`, it's initialized as:
   ```python
   self.main_point = {
       "world": self.main_world
   }
   ```

3. In `bimodal/semantic.py`, it's initialized as:
   ```python
   self.main_point = {
      "world": self.main_world,
      "time": self.main_time,
   }
   ```

4. Methods that use `eval_point` in operators consistently extract values:
   ```python
   eval_world = eval_point["world"]
   eval_time = eval_point["time"] if "time" in eval_point else None
   ```

5. The `print_proposition` methods already accept `eval_point` as a parameter and extract what they need.

## Implementation Plan

### 1. Modify `truth_value_at()` Signature in All Theory Propositions

Change all implementations to use a consistent dictionary pattern:

**Default theory** (`theory_lib/default/semantic.py`):
```python
def truth_value_at(self, eval_point):
    """Determines the truth value of the proposition at a given evaluation point.
    
    Args:
        eval_point (dict): Dictionary containing evaluation context with at least a "world" key
            
    Returns:
        bool: True if the world contains a verifier, False if it contains a falsifier
    """
    eval_world = eval_point["world"]
    
    # Existing implementation using eval_world
    semantics = self.model_structure.model_constraints.semantics
    z3_model = self.model_structure.z3_model
    # ...rest of implementation unchanged...
```

**Bimodal theory** (`theory_lib/bimodal/semantic.py`):
```python
def truth_value_at(self, eval_point):
    """Checks if the proposition is true at the given evaluation point.
    
    Args:
        eval_point (dict): Dictionary containing evaluation context with "world" and "time" keys
            
    Returns:
        bool: True if the proposition is true at the specified world and time
    """
    eval_world = eval_point["world"]
    eval_time = eval_point["time"]
    
    # Existing implementation using eval_world and eval_time
    # ...rest of implementation unchanged...
```

### 2. Update Caller in `BuildExample.print_model()`

Modify the relevant section in `builder/example.py`:

```python
# Create an eval_point dictionary for consistent usage
eval_point = {"world": eval_world}
if hasattr(self.model_structure, 'main_time'):
    eval_point["time"] = eval_time

# Check premises
for p in self.model_structure.premises:
    if hasattr(p, 'proposition') and hasattr(p.proposition, 'truth_value_at'):
        if not p.proposition.truth_value_at(eval_point):
            all_premises_true = False
            break

# Check conclusions
for c in self.model_structure.conclusions:
    if hasattr(c, 'proposition') and hasattr(c.proposition, 'truth_value_at'):
        if c.proposition.truth_value_at(eval_point):
            all_conclusions_false = False
            break
```

### 3. Update Any Other Direct Callers of `truth_value_at()`

Search for all other direct callers of `truth_value_at()` in the codebase and update them to use the dictionary approach. Known callers include:

- Operator methods defined in `operators.py` files that use propositions' truth values
- Display methods in `jupyter/display.py` if they call this method directly

### 4. Update Tests

Update any tests that directly call `truth_value_at()` to use the new signature.

## Benefits of This Approach

1. **Consistent Interface**: All theories use the same function signature for `truth_value_at()`
2. **Fail-Fast**: Theories requiring specific evaluation parameters will naturally fail if the key is missing
3. **Extensible**: New theories can add evaluation dimensions (like "perspective" or "agent") without changing the interface
4. **Clear Documentation**: The dictionary pattern makes it clear what parameters each theory requires
5. **No Conditional Logic**: No need for try/except or parameter counting
6. **Follows Project Philosophy**: Explicit, deterministic approach rather than defaults or fallbacks

## Implementation Steps Prioritized

1. First update the `truth_value_at()` methods in proposition classes
2. Then update the caller in `BuildExample.print_model()`
3. Find and update any other direct callers
4. Run tests to verify changes
5. Update documentation in code comments

## Testing Plan

1. Run the failing examples first to verify fix
2. Test all example files in all theories
3. Run tests for each theory and component
4. Test interactive Jupyter usage if applicable

## Notes for Reviewers

- This is a breaking change to `truth_value_at()` method signatures
- The project's philosophy explicitly states: "Prioritize Code Quality Over Backward Compatibility"
- The approach eliminates conditional logic like the proposed try/except solution
- The dictionary pattern is already established in the codebase for similar cross-theory interfaces

## Sample Implementation for Initial Fix

For immediate fix of the error, here's a minimal implementation to update just the required methods:

```python
# In default/semantic.py Proposition class
def truth_value_at(self, eval_point):
    """Determines the truth value of the proposition at a given evaluation point.
    
    Args:
        eval_point (dict): Dictionary containing evaluation context with at least a "world" key
            
    Returns:
        bool: True if the world contains a verifier, False if it contains a falsifier
    """
    eval_world = eval_point["world"]
    # Rest of method unchanged
    
# In bimodal/semantic.py BimodalProposition class
def truth_value_at(self, eval_point):
    """Checks if the proposition is true at the given evaluation point.
    
    Args:
        eval_point (dict): Dictionary containing evaluation context with "world" and "time" keys
            
    Returns:
        bool: True if the proposition is true at the specified world and time
    """
    eval_world = eval_point["world"]
    eval_time = eval_point["time"]
    # Rest of method unchanged
    
# In builder/example.py BuildExample.print_model method
# Create an eval_point dictionary for consistent usage
eval_point = {"world": eval_world}
if hasattr(self.model_structure, 'main_time'):
    eval_point["time"] = eval_time

# Check premises
for p in self.model_structure.premises:
    if hasattr(p, 'proposition') and hasattr(p.proposition, 'truth_value_at'):
        if not p.proposition.truth_value_at(eval_point):
            all_premises_true = False
            break
```