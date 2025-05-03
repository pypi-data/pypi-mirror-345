# Better-Diff


## The problem we're solving:
Why is my code linting tool telling me there's a difference here?

```diff
--- a
+++ b
@@ -1,6 +1,6 @@
-Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
+Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
 incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
 nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
```

With a normal unified-diff, trailing whitespace that is removed is not highlighted (depending on how the log is saved, may even be removed...)

Similar issues exist with the last line being an empty line or not:

```diff
---a

+++b

@@ -4,4 +4,3 @@

 Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
 fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
 culpa qui officia deserunt mollit anim id est laborum.
-
```

What about that line is getting removed?

## Our solution

Write this module to share a wrapper that calls [`difflib.unified_diff`](https://docs.python.org/3/library/difflib.html#difflib.unified_diff) and augments the formatting output with lines to highlight:
* The difference between the last and the new line is whitespace being removed
* The difference is the absence of line endings at the end.

```diff
--- a
+++ b
@@ -1,3 +1,3 @@
-Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
?                                                                              ^^
+Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
 incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
 nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
\ No newline at end of file (b)
```
