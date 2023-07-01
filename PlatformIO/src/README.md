Code here will be uploaded to the microcontroller depending on the environment.

- `main.cpp` will always be compiled first.
- `main-uno.cpp` will be loaded if 'env:uno' is selected as the working environment.
- `main-esp.cpp` will be loaded if 'env:esp' is selected as the working environment.