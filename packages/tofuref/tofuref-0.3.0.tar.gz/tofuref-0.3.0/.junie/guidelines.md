# Guidelines for AI coding assistant Junie

* This application is interactive terminal application, meaning it can't be just ran by an AI assistant in order to check its functionality.
* Tests should be written in pytest
* Every change should be checked by running tests
* Code should be split between presentation and business logic/data layer.
* `uv` is used to manage python dependencies, they should not be installed through any other means
* README should be updated with every change, but it doesn't need to fill the role of documentation
* `gh` CLI can be used as a subprocess, but keep in mind that by default its outputs are opened in `less`-like application, not printed to stdout
* Anytime something is fixed, test should be added for that
